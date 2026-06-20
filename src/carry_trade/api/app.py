"""Flask app factory for the carry trade dashboard API."""

from __future__ import annotations

import os
from typing import Callable, Optional

from flask import Flask
from flask_cors import CORS

from carry_trade.api.data_provider import RealDataProvider
from carry_trade.api.routes import register_routes
from carry_trade.paths import LOGS_DIR as PROJECT_LOGS_DIR, PROJECT_ROOT


def parse_cors_origins(raw_origins: str):
    """Return explicit dashboard origins; use CORS_ORIGINS=* only if intentional."""
    if raw_origins.strip() == "*":
        return "*"
    return [origin.strip() for origin in raw_origins.split(",") if origin.strip()]


def default_cors_origins():
    raw_origins = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000,"
        "http://localhost:5173,http://127.0.0.1:5173",
    )
    return parse_cors_origins(raw_origins)


def create_app(data_provider=None, model_update_runner: Optional[Callable[[], dict]] = None) -> Flask:
    """Create a Flask app with injectable data and model-update dependencies."""
    app = Flask(__name__)
    app.config["DATA_PROVIDER"] = data_provider or RealDataProvider()
    app.config["ENABLE_MODEL_UPDATE_ENDPOINT"] = os.getenv(
        "ENABLE_MODEL_UPDATE_ENDPOINT", ""
    ).lower() in {"1", "true", "yes"}

    CORS(app, resources={
        r"/api/*": {"origins": default_cors_origins()},
        r"/health": {"origins": default_cors_origins()},
    })
    register_routes(app, app.config["DATA_PROVIDER"], model_update_runner)
    return app


app = create_app()


def run_dev_server(app_instance: Optional[Flask] = None) -> None:
    """Run the local development API server with safe public-release defaults."""
    server_app = app_instance or app
    host = os.getenv("FLASK_HOST", "127.0.0.1")
    port = int(os.getenv("FLASK_PORT", "8000"))
    debug_enabled = os.getenv("FLASK_DEBUG", "").lower() in {"1", "true", "yes"}

    print("\n" + "=" * 50)
    print("CARRY TRADE API SERVER - REAL DATA MODE")
    print("=" * 50)
    print(f"Data Source: local log files in {PROJECT_LOGS_DIR}")
    print(f"Base directory: {PROJECT_ROOT}")
    print(f"FX Data: {PROJECT_LOGS_DIR / 'fx'}")
    print(f"News Data: {PROJECT_LOGS_DIR / 'news_log.csv'}")
    print(f"Macro Data: {PROJECT_LOGS_DIR / 'macro'}")
    print(f"Host: {host}:{port}")
    print("=" * 50)
    server_app.run(host=host, port=port, debug=debug_enabled)
