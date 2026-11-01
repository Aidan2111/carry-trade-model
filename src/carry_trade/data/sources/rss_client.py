"""Authenticated, non-redirecting retrieval for public research RSS feeds."""

from urllib.parse import urlsplit

import requests


def fetch_rss_bytes(url: str) -> bytes:
    """Fetch an HTTPS feed without allowing redirects or parser resource reads."""
    parsed = urlsplit(url)
    if parsed.scheme != "https" or not parsed.hostname:
        raise ValueError("RSS feeds require an HTTPS URL with a hostname.")

    with requests.get(url, timeout=15, allow_redirects=False) as response:
        if response.status_code != 200:
            raise ValueError(f"RSS request returned HTTP {response.status_code}.")
        return response.content
