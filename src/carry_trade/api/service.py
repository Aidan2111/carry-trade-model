"""Application services for the carry trade API."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict


class DashboardService:
    """Build dashboard payloads without binding to Flask route code."""

    def __init__(self, data_provider):
        self.data_provider = data_provider

    def get_dashboard_data(self) -> Dict[str, Any]:
        fx_rates = self.data_provider.get_latest_fx_rates()
        sentiment = self.data_provider.get_sentiment_data()
        macro_data = self.data_provider.get_macro_data()
        predictions = self.data_provider.get_model_predictions(
            fx_rates=fx_rates,
            sentiment=sentiment,
            macro_data=macro_data,
        )
        signals = self.data_provider.get_trading_signals(predictions=predictions)

        return {
            "fxRates": fx_rates,
            "sentiment": sentiment,
            "macroData": macro_data,
            "predictions": predictions,
            "signals": signals,
            "performance": self.data_provider.get_performance_metrics(),
            "news": self.data_provider.get_news_headlines(),
            "lastUpdate": datetime.now().isoformat(),
            "dataSource": "REAL_DATA",
        }
