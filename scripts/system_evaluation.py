"""Deterministic end-to-end system evaluation for the API contract."""

from __future__ import annotations

import json
import pathlib
import sys
from typing import Any, Dict


REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))


class EvaluationDataProvider:
    """Small fixture provider for no-network API system checks."""

    def get_latest_fx_rates(self):
        return [{
            "pair": "USD/UAH",
            "rate": 41.25,
            "change": 0.15,
            "changePercent": 0.36,
            "timestamp": "2026-06-20T12:00:00",
        }]

    def get_sentiment_data(self):
        return [{
            "region": "USD",
            "score": 0.12,
            "label": "positive",
            "confidence": 0.62,
            "timestamp": "2026-06-20T12:00:00",
        }]

    def get_macro_data(self):
        return [{
            "indicator": "US Fed Funds Rate",
            "value": 5.25,
            "previousValue": 5.0,
            "change": 0.25,
            "timestamp": "2026-06-20T12:00:00",
        }]

    def get_performance_metrics(self):
        return None

    def get_model_predictions(self, fx_rates=None, sentiment=None, macro_data=None):
        if not fx_rates or not sentiment:
            return []
        return [{
            "pair": fx_rates[0]["pair"],
            "predictedReturn": 1.8,
            "confidence": 0.76,
            "horizon": 30,
            "timestamp": "2026-06-20T12:00:00",
        }]

    def get_trading_signals(self, predictions=None):
        if not predictions:
            return []
        return [{
            "pair": predictions[0]["pair"],
            "action": "BUY",
            "strength": 86,
            "expectedReturn": predictions[0]["predictedReturn"],
            "risk": 14,
            "timestamp": "2026-06-20T12:00:00",
        }]

    def get_news_headlines(self):
        return [{
            "headline": "Central bank holds rates steady",
            "source": "Fixture",
            "sentiment": 0.12,
            "timestamp": "2026-06-20T12:00:00",
            "region": "USD",
        }]


def _key_style(row: Dict[str, Any], camel_key: str, snake_key: str) -> str:
    if camel_key in row and snake_key not in row:
        return "camelCase"
    if snake_key in row:
        return "snake_case"
    return "missing"


def run_system_evaluation() -> Dict[str, Any]:
    """Run deterministic API checks and return a structured report."""
    from carry_trade.api.app import create_app

    app = create_app(data_provider=EvaluationDataProvider())
    client = app.test_client()

    health_response = client.get("/health")
    dashboard_response = client.get("/api/dashboard")
    update_response = client.post("/api/update-model")
    dashboard_payload = dashboard_response.get_json() or {}
    predictions = dashboard_payload.get("predictions") or [{}]
    signals = dashboard_payload.get("signals") or [{}]

    checks = {
        "health": {
            "status_code": health_response.status_code,
            "status": (health_response.get_json() or {}).get("status"),
        },
        "dashboard": {
            "status_code": dashboard_response.status_code,
            "data_source": dashboard_payload.get("dataSource"),
            "required_keys_present": {
                key: key in dashboard_payload
                for key in (
                    "fxRates",
                    "sentiment",
                    "macroData",
                    "predictions",
                    "signals",
                    "performance",
                    "news",
                    "lastUpdate",
                    "dataSource",
                )
            },
            "prediction_key_style": _key_style(predictions[0], "predictedReturn", "predicted_return"),
            "signal_key_style": _key_style(signals[0], "expectedReturn", "expected_return"),
        },
        "model_update_disabled": {
            "status_code": update_response.status_code,
            "status": (update_response.get_json() or {}).get("status"),
        },
    }

    failures = []
    if checks["health"]["status_code"] != 200 or checks["health"]["status"] != "healthy":
        failures.append("health")
    if checks["dashboard"]["status_code"] != 200:
        failures.append("dashboard_status")
    if not all(checks["dashboard"]["required_keys_present"].values()):
        failures.append("dashboard_keys")
    if checks["dashboard"]["data_source"] != "REAL_DATA":
        failures.append("dashboard_data_source")
    if checks["dashboard"]["prediction_key_style"] != "camelCase":
        failures.append("prediction_key_style")
    if checks["dashboard"]["signal_key_style"] != "camelCase":
        failures.append("signal_key_style")
    if checks["model_update_disabled"]["status_code"] != 403:
        failures.append("model_update_gate")

    return {
        "status": "fail" if failures else "pass",
        "failures": failures,
        "checks": checks,
    }


def main() -> int:
    report = run_system_evaluation()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
