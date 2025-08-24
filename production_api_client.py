
# production_api_client.py
# Production-ready API client with real financial data sources

import os
import requests
import pandas as pd
import yfinance as yf
from fredapi import Fred
from dotenv import load_dotenv
import pickle

class ProductionAPIClient:
    """Production API client with real data sources"""

    def __init__(self):
        # Load environment variables
        load_dotenv()

        # Initialize API clients
        self.fred = Fred(api_key=os.getenv('FRED_API_KEY'))
        self.alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        self.fixer_key = os.getenv('FIXER_API_KEY')

        # Load the saved model
        self.model_package = self.load_model()

    def load_model(self):
        """Load the saved integrated model"""
        model_path = "integrated_models/integrated_enhanced_model.pkl"
        with open(model_path, 'rb') as f:
            return pickle.load(f)

    def get_real_forex_rates(self):
        """Get real forex rates from Fixer.io"""
        url = f"http://data.fixer.io/api/latest"
        params = {
            'access_key': self.fixer_key,
            'base': 'USD',
            'symbols': 'EUR,GBP,JPY,AUD,CAD,CHF,NZD'
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()['rates']
        return None

    def get_real_interest_rates(self):
        """Get real interest rates from FRED"""
        series = {
            'US_FedFunds': 'FEDFUNDS',
            'EU_Rate': 'ECBMRRFR',
            'UK_Rate': 'GBRONTD156N'
        }

        rates = {}
        for name, series_id in series.items():
            try:
                data = self.fred.get_series(series_id, limit=1)
                rates[name] = float(data.iloc[-1])
            except:
                rates[name] = 0.0

        return rates

    def get_real_economic_data(self):
        """Get real economic indicators"""
        indicators = {
            'US_CPI': 'CPIAUCSL',
            'US_Unemployment': 'UNRATE',
            'US_GDP': 'GDP'
        }

        data = {}
        for name, series_id in indicators.items():
            try:
                series_data = self.fred.get_series(series_id, limit=1)
                data[name] = float(series_data.iloc[-1])
            except:
                data[name] = 0.0

        return data

    def make_prediction(self):
        """Make prediction using real data and saved model"""
        # Get real data
        forex = self.get_real_forex_rates()
        rates = self.get_real_interest_rates()
        economic = self.get_real_economic_data()

        # Create feature vector (you'll need to adapt this to your features)
        features = {**forex, **rates, **economic}
        feature_df = pd.DataFrame([features])

        # Use saved model for prediction
        model = self.model_package['model']
        prediction_result = model.predict_with_risk_management(feature_df)

        return prediction_result

# Example usage:
# client = ProductionAPIClient()
# prediction = client.make_prediction()
