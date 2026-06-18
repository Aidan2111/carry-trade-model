"""Compatibility wrapper for the packaged real-data API server."""

from pathlib import Path
import sys


SRC_DIR = Path(__file__).resolve().parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from carry_trade.api.server import app, run_dev_server  # noqa: E402


if __name__ == "__main__":
    run_dev_server()
