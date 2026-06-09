"""Compatibility wrapper for the canonical real-data API server.

This project is public research software, not a production trading service.
Use `api_server_real_data.py` for the maintained API implementation.
"""

from api_server_real_data import app, run_dev_server


if __name__ == "__main__":
    run_dev_server()
