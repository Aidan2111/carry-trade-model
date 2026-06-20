import pathlib
import sys
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))


class StubDataProvider:
    def __init__(self):
        self.calls = []

    def get_latest_fx_rates(self):
        self.calls.append("fx")
        return [
            {
                "pair": "USD/UAH",
                "rate": 41.25,
                "change": 0.15,
                "changePercent": 0.36,
                "timestamp": "2026-06-20T12:00:00",
            }
        ]

    def get_sentiment_data(self):
        self.calls.append("sentiment")
        return [
            {
                "region": "USD",
                "score": 0.12,
                "label": "positive",
                "confidence": 0.62,
                "timestamp": "2026-06-20T12:00:00",
            }
        ]

    def get_macro_data(self):
        self.calls.append("macro")
        return [
            {
                "indicator": "US Fed Funds Rate",
                "value": 5.25,
                "previousValue": 5.0,
                "change": 0.25,
                "timestamp": "2026-06-20T12:00:00",
            }
        ]

    def get_performance_metrics(self):
        self.calls.append("performance")
        return None

    def get_model_predictions(self, fx_rates=None, sentiment=None, macro_data=None):
        self.calls.append("predictions")
        self.prediction_inputs = {
            "fx_rates": fx_rates,
            "sentiment": sentiment,
            "macro_data": macro_data,
        }
        return [
            {
                "pair": "USD/UAH",
                "predictedReturn": 1.8,
                "confidence": 0.76,
                "horizon": 30,
                "timestamp": "2026-06-20T12:00:00",
            }
        ]

    def get_trading_signals(self, predictions=None):
        self.calls.append("signals")
        self.signal_inputs = predictions
        return [
            {
                "pair": "USD/UAH",
                "action": "BUY",
                "strength": 86,
                "expectedReturn": 1.8,
                "risk": 14,
                "timestamp": "2026-06-20T12:00:00",
            }
        ]

    def get_news_headlines(self):
        self.calls.append("news")
        return [
            {
                "headline": "Central bank holds rates steady",
                "source": "Fixture",
                "sentiment": 0.12,
                "timestamp": "2026-06-20T12:00:00",
                "region": "USD",
            }
        ]


class ApiContractE2ETests(unittest.TestCase):
    def test_dashboard_contract_uses_injected_provider_and_canonical_keys(self):
        from carry_trade.api.app import create_app

        provider = StubDataProvider()
        app = create_app(data_provider=provider)
        client = app.test_client()

        response = client.get("/api/dashboard")

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(
            set(payload),
            {
                "fxRates",
                "sentiment",
                "macroData",
                "predictions",
                "signals",
                "performance",
                "news",
                "lastUpdate",
                "dataSource",
            },
        )
        self.assertEqual(payload["dataSource"], "REAL_DATA")
        self.assertIn("predictedReturn", payload["predictions"][0])
        self.assertNotIn("predicted_return", payload["predictions"][0])
        self.assertIn("expectedReturn", payload["signals"][0])
        self.assertNotIn("expected_return", payload["signals"][0])
        self.assertEqual(provider.calls.count("fx"), 1)
        self.assertEqual(provider.prediction_inputs["fx_rates"], payload["fxRates"])
        self.assertEqual(provider.signal_inputs, payload["predictions"])

    def test_model_update_endpoint_is_disabled_by_default(self):
        from carry_trade.api.app import create_app

        app = create_app(data_provider=StubDataProvider())
        client = app.test_client()

        response = client.post("/api/update-model")

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.get_json()["status"], "disabled")

    def test_model_update_endpoint_can_use_injected_runner_when_enabled(self):
        from carry_trade.api.app import create_app

        def runner():
            return {"status": "success", "message": "fixture update"}

        app = create_app(data_provider=StubDataProvider(), model_update_runner=runner)
        app.config["ENABLE_MODEL_UPDATE_ENDPOINT"] = True
        client = app.test_client()

        response = client.post("/api/update-model")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "success")


if __name__ == "__main__":
    unittest.main()
