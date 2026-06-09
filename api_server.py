"""Compatibility wrapper for the canonical real-data API server.

Older docs and scripts referenced `api_server.py`. Keep that entry point working
without reintroducing mock dashboard data or unsafe debug defaults.
"""

from api_server_real_data import app, run_dev_server


if __name__ == "__main__":
    run_dev_server()
