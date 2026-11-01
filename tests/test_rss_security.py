"""Offline transport and parser-boundary regressions for news collectors."""

import ast
import asyncio
import io
from pathlib import Path
import unittest
from unittest.mock import Mock, patch

import feedparser
import requests

from carry_trade.data.collectors import enhanced_auto_scraper, enhanced_scraper_simple
from carry_trade.data.runtime import real_time_data_engine


FEED_URL = "https://feeds.example.test/news.xml"
VALID_FEED = b"""<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0"><channel><title>Research fixture</title>
<item><title>Dollar research headline</title><description>Fixture description</description>
<link>https://example.test/article</link><pubDate>Tue, 01 Sep 2026 12:00:00 GMT</pubDate>
</item></channel></rss>"""


def default_feed_map(module, class_name, attribute):
    """Read literal constructor configuration without starting a collector."""
    tree = ast.parse(Path(module.__file__).read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef) or node.name != class_name:
            continue
        for assignment in ast.walk(node):
            if not isinstance(assignment, ast.Assign):
                continue
            if any(
                isinstance(target, ast.Attribute) and target.attr == attribute
                for target in assignment.targets
            ):
                return ast.literal_eval(assignment.value)
    raise AssertionError(f"No {class_name}.{attribute} default feed map")


def collector(kind, feeds=None):
    """Avoid constructor filesystem, credential, and sentiment setup effects."""
    if kind == "simple":
        return enhanced_scraper_simple.SimpleEnhancedScraper.__new__(
            enhanced_scraper_simple.SimpleEnhancedScraper
        )
    if kind == "enhanced":
        result = enhanced_auto_scraper.EnhancedDataScraper.__new__(
            enhanced_auto_scraper.EnhancedDataScraper
        )
        result.news_feeds = feeds if feeds is not None else default_feed_map(
            enhanced_auto_scraper, "EnhancedDataScraper", "news_feeds"
        )
    else:
        result = real_time_data_engine.NewsDataCollector.__new__(
            real_time_data_engine.NewsDataCollector
        )
        result.rss_feeds = feeds if feeds is not None else default_feed_map(
            real_time_data_engine, "NewsDataCollector", "rss_feeds"
        )
    result.logger = Mock()
    return result


class RssSecurityTests(unittest.TestCase):
    def collect(self, kind, *, body=VALID_FEED, status=200, feeds=None):
        subject = collector(kind, feeds)
        requested = []

        def get_response(url, **kwargs):
            requested.append((url, kwargs))
            response = requests.Response()
            response.status_code = status
            response.url = url
            response._content = body
            response._content_consumed = True
            if 300 <= status < 400:
                response.headers["Location"] = "http://attacker.example.test/news.xml"
            return response

        # An unguarded parser URL branch simulates following a redirect and
        # reaching an attacker feed. No test can perform a real network read.
        with patch("requests.get", side_effect=get_response), patch(
            "feedparser.http.get", return_value=body
        ) as parser_http, patch(
            "builtins.open", side_effect=AssertionError("secondary local file read")
        ) as parser_open, patch("feedparser.parse", wraps=feedparser.parse) as parse:
            if kind == "simple":
                items = subject._get_rss_news()
            elif kind == "enhanced":
                items = subject._collect_rss_news()
            else:
                items = asyncio.run(subject._collect_rss_news())
        return items, requested, parser_http, parser_open, parse

    def test_valid_feeds_preserve_headline_and_source_fields(self):
        for kind in ("simple", "enhanced", "runtime"):
            with self.subTest(collector=kind):
                items, _, _, _, _ = self.collect(kind)
                self.assertTrue(items)
                self.assertTrue(any(item["title"] == "Dollar research headline" for item in items))
                self.assertTrue(all(item["source"] for item in items))

    def test_default_feeds_are_retrieved_only_over_https(self):
        for kind in ("simple", "enhanced", "runtime"):
            with self.subTest(collector=kind):
                items, requested, parser_http, _, _ = self.collect(kind)
                self.assertTrue(items)
                urls = [url for url, _ in requested]
                urls.extend(call.args[0] for call in parser_http.call_args_list)
                self.assertTrue(urls, "collector made no feed retrieval")
                self.assertTrue(all(url.startswith("https://") for url in urls), urls)

    def test_redirect_responses_are_skipped_instead_of_parsed(self):
        for kind in ("simple", "enhanced", "runtime"):
            with self.subTest(collector=kind):
                items, _, _, _, _ = self.collect(kind, status=302)
                self.assertEqual(items, [])

    def test_failed_http_responses_are_skipped_instead_of_parsed(self):
        for kind in ("simple", "enhanced", "runtime"):
            with self.subTest(collector=kind):
                items, _, _, _, _ = self.collect(kind, status=503)
                self.assertEqual(items, [])

    def test_http_and_malformed_feed_locations_never_reach_resource_readers(self):
        for kind in ("enhanced", "runtime"):
            for url in (
                "http://feeds.example.test/news.xml",
                "file:///tmp/private-research.xml",
                "https:///missing-host.xml",
                "https://",
            ):
                with self.subTest(collector=kind, url=url):
                    items, requested, parser_http, parser_open, _ = self.collect(
                        kind, feeds={"fixture": url}
                    )
                    self.assertEqual(items, [])
                    self.assertEqual(requested, [])
                    parser_http.assert_not_called()
                    parser_open.assert_not_called()

    def test_transport_disables_redirects_and_bounds_request_time(self):
        for kind in ("simple", "enhanced", "runtime"):
            with self.subTest(collector=kind):
                items, requested, parser_http, _, _ = self.collect(kind)
                self.assertTrue(items)
                self.assertTrue(requested, "collector bypassed guarded HTTP transport")
                for _, options in requested:
                    self.assertEqual(options.get("allow_redirects"), False)
                    self.assertEqual(options.get("timeout"), 15)
                parser_http.assert_not_called()

    def test_url_and_path_looking_bodies_remain_data_without_secondary_reads(self):
        for kind in ("enhanced", "runtime"):
            for body in (
                b"https://attacker.example.test/stolen-feed.xml",
                b"/tmp/private-research.xml",
                b"\xff\xfe malformed feed bytes",
            ):
                with self.subTest(collector=kind, body=body):
                    items, requested, parser_http, parser_open, parse = self.collect(
                        kind, body=body, feeds={"fixture": FEED_URL}
                    )
                    self.assertEqual(items, [])
                    self.assertEqual(len(requested), 1)
                    parser_http.assert_not_called()
                    parser_open.assert_not_called()
                    self.assertEqual(parse.call_count, 1)
                    self.assertIsInstance(parse.call_args.args[0], io.BytesIO)


if __name__ == "__main__":
    unittest.main()
