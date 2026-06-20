"""Compatibility module for the packaged Flask API server."""

from carry_trade.api.app import app, create_app, run_dev_server


if __name__ == "__main__":
    run_dev_server()
