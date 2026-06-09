"""Shared NewsAPI client factory.

The repository is public-facing, so API keys must come from environment
variables or a local .env file that is not committed.
"""

import os
from typing import Optional

from dotenv import load_dotenv
from newsapi import NewsApiClient


def get_newsapi_client() -> Optional[NewsApiClient]:
    """Return a NewsAPI client when NEWS_API_KEY is configured."""
    load_dotenv()
    api_key = os.getenv("NEWS_API_KEY")
    if not api_key:
        return None
    return NewsApiClient(api_key=api_key)
