"""Optional premium data client for higher-quality research inputs.

The main project can run without this file. Use it when you have paid or
premium API credentials and a trained model artifact available locally.
"""

import os
import pickle
from typing import Dict, Optional

import pandas as pd
import requests
from dotenv import load_dotenv
from fredapi import Fred


class ProductionAPIClient:
    """Premium API client with real financial data sources."""

    def __init__(self, model_path: str = "integrated_models/integrated_enhanced_model.pkl"):
        load_dotenv()
        self.fred_key = os.getenv("FRED_API_KEY")
        self.fixer_key = os.getenv("FIXER_API_KEY")
        self.model_path = model_path
        self.fred = Fred(api_key=self.fred_key) if self.fred_key else None
        self.model_package = self.load_model()

    def load_model(self):
        """Load a local model artifact when one exists."""
        if not os.path.exists(self.model_path):
            return None

        with open(self.model_path, "rb") as f:
            return pickle.load(f)

    def get_real_forex_rates(self) -> Optional[Dict[str, float]]:
        """Get real forex rates from Fixer over HTTPS when configured."""
        if not self.fixer_key:
            return None

        url = "https://data.fixer.io/api/latest"
        params = {
            "access_key": self.fixer_key,
            "base": "USD",
            "symbols": "EUR,GBP,JPY,AUD,CAD,CHF,NZD",
        }
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        payload = response.json()
        return payload.get("rates")

    def get_real_interest_rates(self) -> Dict[str, float]:
        """Get real interest rates from FRED when configured."""
        if not self.fred:
            return {}

        series = {
            "US_FedFunds": "FEDFUNDS",
            "EU_Rate": "ECBMRRFR",
            "UK_Rate": "GBRONTD156N",
        }

        rates = {}
        for name, series_id in series.items():
            try:
                data = self.fred.get_series(series_id, limit=1)
                rates[name] = float(data.iloc[-1])
            except Exception:
                continue

        return rates

    def get_real_economic_data(self) -> Dict[str, float]:
        """Get real economic indicators from FRED when configured."""
        if not self.fred:
            return {}

        indicators = {
            "US_CPI": "CPIAUCSL",
            "US_Unemployment": "UNRATE",
            "US_GDP": "GDP",
        }

        data = {}
        for name, series_id in indicators.items():
            try:
                series_data = self.fred.get_series(series_id, limit=1)
                data[name] = float(series_data.iloc[-1])
            except Exception:
                continue

        return data

    def make_prediction(self):
        """Make a prediction when real inputs and a local model are available."""
        if not self.model_package:
            return None

        forex = self.get_real_forex_rates() or {}
        rates = self.get_real_interest_rates()
        economic = self.get_real_economic_data()
        features = {**forex, **rates, **economic}
        if not features:
            return None

        feature_df = pd.DataFrame([features])
        model = self.model_package["model"]
        return model.predict_with_risk_management(feature_df)


if __name__ == "__main__":
    client = ProductionAPIClient()
    print(client.make_prediction())
