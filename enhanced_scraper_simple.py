"""Compatibility wrapper for the packaged enhanced data scraper."""

from pathlib import Path
import sys


SRC_DIR = Path(__file__).resolve().parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from carry_trade.data.collectors.enhanced_scraper_simple import main  # noqa: E402


if __name__ == "__main__":
    main()
