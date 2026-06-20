"""Flask route registration for the carry trade API."""

from __future__ import annotations

from datetime import datetime
from typing import Callable, Optional

from flask import jsonify

from carry_trade.api.service import DashboardService


def register_routes(app, data_provider, model_update_runner: Optional[Callable[[], dict]] = None) -> None:
    """Register API routes against an app and injected dependencies."""
    dashboard_service = DashboardService(data_provider)

    @app.route("/health")
    def health_check():
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "data_source": "REAL_DATA",
        })

    @app.route("/api/fx-rates")
    def get_fx_rates():
        return jsonify(data_provider.get_latest_fx_rates())

    @app.route("/api/sentiment")
    def get_sentiment():
        return jsonify(data_provider.get_sentiment_data())

    @app.route("/api/macro")
    def get_macro():
        return jsonify(data_provider.get_macro_data())

    @app.route("/api/predictions")
    def get_predictions():
        return jsonify(data_provider.get_model_predictions())

    @app.route("/api/signals")
    def get_signals():
        return jsonify(data_provider.get_trading_signals())

    @app.route("/api/performance")
    def get_performance():
        performance = data_provider.get_performance_metrics()
        if performance:
            return jsonify(performance)
        return jsonify({"error": "No performance data available"}), 404

    @app.route("/api/news")
    def get_news():
        return jsonify(data_provider.get_news_headlines())

    @app.route("/api/dashboard")
    def get_dashboard_data():
        try:
            return jsonify(dashboard_service.get_dashboard_data())
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    @app.route("/api/update-model", methods=["POST"])
    def update_model():
        if not app.config.get("ENABLE_MODEL_UPDATE_ENDPOINT", False):
            return jsonify({
                "status": "disabled",
                "message": (
                    "Model updates are disabled by default. Set "
                    "ENABLE_MODEL_UPDATE_ENDPOINT=true for local research use."
                ),
                "timestamp": datetime.now().isoformat(),
            }), 403

        try:
            runner = model_update_runner
            if runner is None:
                from carry_trade.dashboard.integration import scheduled_model_run

                runner = scheduled_model_run
            return jsonify(runner())
        except Exception as exc:
            return jsonify({
                "status": "error",
                "message": str(exc),
                "timestamp": datetime.now().isoformat(),
            }), 500
