"""Data provider for the carry trade dashboard API."""

from __future__ import annotations

import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import pandas as pd

from carry_trade.paths import LOGS_DIR as PROJECT_LOGS_DIR, PROJECT_ROOT


class RealDataProvider:
    """Read dashboard data from local logs and configured market sources."""

    def __init__(self, base_dir: Optional[str] = None, logs_dir: Optional[str] = None, cache_ttl_seconds: int = 30):
        self.base_dir = base_dir or str(PROJECT_ROOT)
        self.logs_dir = logs_dir or str(PROJECT_LOGS_DIR)
        self.cache_ttl_seconds = cache_ttl_seconds
        self._cache: Dict[str, tuple[datetime, Any]] = {}

    def _get_cached(self, key: str):
        cached = self._cache.get(key)
        if not cached:
            return None
        created_at, value = cached
        if datetime.now() - created_at > timedelta(seconds=self.cache_ttl_seconds):
            self._cache.pop(key, None)
            return None
        return value

    def _set_cached(self, key: str, value):
        self._cache[key] = (datetime.now(), value)
        return value

    def get_latest_fx_rates(self) -> List[Dict[str, Any]]:
        """Get FX rates from local historical data and live sources."""
        cached = self._get_cached("fx_rates")
        if cached is not None:
            return cached

        try:
            fx_rates: List[Dict[str, Any]] = []
            usd_path = os.path.join(self.logs_dir, "fx", "USD_UAH Historical Data.csv")
            eur_path = os.path.join(self.logs_dir, "fx", "EUR_UAH Historical Data.csv")

            if os.path.exists(usd_path):
                usd_df = pd.read_csv(usd_path)
                if not usd_df.empty:
                    latest_usd = usd_df.iloc[-1]
                    prev_usd = usd_df.iloc[-2] if len(usd_df) > 1 else latest_usd
                    change = float(latest_usd["Price"]) - float(prev_usd["Price"])
                    change_percent = (change / float(prev_usd["Price"])) * 100
                    fx_rates.append({
                        "pair": "USD/UAH",
                        "rate": float(latest_usd["Price"]),
                        "change": change,
                        "changePercent": change_percent,
                        "timestamp": datetime.now().isoformat(),
                    })

            if os.path.exists(eur_path):
                eur_df = pd.read_csv(eur_path)
                if not eur_df.empty:
                    latest_eur = eur_df.iloc[-1]
                    prev_eur = eur_df.iloc[-2] if len(eur_df) > 1 else latest_eur
                    change = float(latest_eur["Price"]) - float(prev_eur["Price"])
                    change_percent = (change / float(prev_eur["Price"])) * 100
                    fx_rates.append({
                        "pair": "EUR/UAH",
                        "rate": float(latest_eur["Price"]),
                        "change": change,
                        "changePercent": change_percent,
                        "timestamp": datetime.now().isoformat(),
                    })

            try:
                import yfinance as yf

                for symbol, pair in (("USDUAH=X", "USD/UAH"), ("EURUAH=X", "EUR/UAH")):
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period="2d")
                    if hist.empty or len(hist) < 2:
                        continue
                    current = float(hist["Close"].iloc[-1])
                    previous = float(hist["Close"].iloc[-2])
                    change = current - previous
                    change_percent = (change / previous) * 100
                    existing = next((rate for rate in fx_rates if rate["pair"] == pair), None)
                    payload = {
                        "rate": current,
                        "change": change,
                        "changePercent": change_percent,
                        "timestamp": datetime.now().isoformat(),
                    }
                    if existing:
                        existing.update(payload)
                    else:
                        fx_rates.append({"pair": pair, **payload})
            except Exception as exc:
                print(f"Yahoo Finance error: {exc}")

            return self._set_cached("fx_rates", fx_rates)
        except Exception as exc:
            print(f"Error loading FX data: {exc}")
            return []

    def get_sentiment_data(self) -> List[Dict[str, Any]]:
        """Get sentiment data from local news logs."""
        try:
            news_path = os.path.join(self.logs_dir, "news_log.csv")
            if not os.path.exists(news_path):
                return []

            df = pd.read_csv(news_path)
            if df.empty or not {"Region", "Sentiment"}.issubset(df.columns):
                return []

            sentiment_data = []
            for region in ("USD", "EUR", "UAH"):
                region_data = df[df["Region"] == region]
                if region_data.empty:
                    continue
                recent_data = region_data.tail(50)
                avg_sentiment = recent_data["Sentiment"].mean()
                confidence = min(abs(avg_sentiment) + 0.5, 0.95)
                label = "positive" if avg_sentiment > 0.1 else "negative" if avg_sentiment < -0.1 else "neutral"
                sentiment_data.append({
                    "region": region,
                    "score": float(avg_sentiment),
                    "label": label,
                    "confidence": float(confidence),
                    "timestamp": datetime.now().isoformat(),
                })

            return sentiment_data
        except Exception as exc:
            print(f"Error loading sentiment data: {exc}")
            return []

    def get_macro_data(self) -> List[Dict[str, Any]]:
        """Get macro data from local logs."""
        try:
            macro_data = []
            macro_dir = os.path.join(self.logs_dir, "macro")
            macro_files = {
                "US_FedFunds.csv": "US Fed Funds Rate",
                "US_CPI.csv": "US CPI",
                "US_InflationExpectations.csv": "US Inflation Expectations",
                "US_YieldCurve.csv": "US Yield Curve",
                "EU_ConsumerPrices.csv": "EU Consumer Prices",
            }

            for filename, indicator_name in macro_files.items():
                file_path = os.path.join(macro_dir, filename)
                if not os.path.exists(file_path):
                    continue
                df = pd.read_csv(file_path)
                if df.empty or len(df) < 2:
                    continue
                latest = df.iloc[-1]
                previous = df.iloc[-2]
                value_col = next((col for col in ("Value", "Price", "Rate", "Close") if col in df.columns), None)
                if not value_col:
                    continue
                current_val = float(latest[value_col])
                prev_val = float(previous[value_col])
                macro_data.append({
                    "indicator": indicator_name,
                    "value": current_val,
                    "previousValue": prev_val,
                    "change": current_val - prev_val,
                    "timestamp": datetime.now().isoformat(),
                })

            return macro_data
        except Exception as exc:
            print(f"Error loading macro data: {exc}")
            return []

    def get_performance_metrics(self) -> Optional[Dict[str, Any]]:
        """Get performance metrics from local logs."""
        try:
            perf_path = os.path.join(self.logs_dir, "performance_log.csv")
            if not os.path.exists(perf_path):
                return None

            df = pd.read_csv(perf_path)
            if df.empty:
                return None
            latest = df.iloc[-1]
            return {
                "totalReturn": float(latest.get("total_return", 0)),
                "sharpeRatio": float(latest.get("sharpe_ratio", 0)),
                "maxDrawdown": float(latest.get("max_drawdown", 0)),
                "winRate": float(latest.get("win_rate", 0)),
                "avgDailyReturn": float(latest.get("avg_daily_return", 0)),
                "volatility": float(latest.get("volatility", 0)),
                "benchmark": float(latest.get("benchmark", 0)),
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as exc:
            print(f"Error loading performance data: {exc}")
            return None

    def get_model_predictions(
        self,
        fx_rates: Optional[List[Dict[str, Any]]] = None,
        sentiment: Optional[List[Dict[str, Any]]] = None,
        macro_data: Optional[List[Dict[str, Any]]] = None,
    ) -> List[Dict[str, Any]]:
        """Generate dashboard predictions from available observed inputs."""
        del macro_data
        try:
            fx_data = fx_rates if fx_rates is not None else self.get_latest_fx_rates()
            sentiment_data = sentiment if sentiment is not None else self.get_sentiment_data()
            predictions = []

            for fx in fx_data:
                momentum = fx["changePercent"]
                base_currency = fx["pair"].split("/")[0]
                sentiment_score = 0.0
                for sent in sentiment_data:
                    if sent["region"] == base_currency:
                        sentiment_score = sent["score"]
                        break

                predicted_return = (momentum * 0.7) + (sentiment_score * 10 * 0.3)
                confidence = min(0.5 + abs(sentiment_score), 0.9)
                predictions.append({
                    "pair": fx["pair"],
                    "predictedReturn": float(predicted_return),
                    "confidence": float(confidence),
                    "horizon": 30,
                    "timestamp": datetime.now().isoformat(),
                })

            return predictions
        except Exception as exc:
            print(f"Error generating predictions: {exc}")
            return []

    def get_trading_signals(self, predictions: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """Generate dashboard trading signals from predictions."""
        try:
            prediction_rows = predictions if predictions is not None else self.get_model_predictions()
            signals = []

            for pred in prediction_rows:
                predicted_return = pred["predictedReturn"]
                confidence = pred["confidence"]
                if predicted_return > 1.5 and confidence > 0.7:
                    action = "BUY"
                    strength = min(100, int(confidence * 100 + abs(predicted_return) * 5))
                elif predicted_return < -1.5 and confidence > 0.7:
                    action = "SELL"
                    strength = min(100, int(confidence * 100 + abs(predicted_return) * 5))
                else:
                    action = "HOLD"
                    strength = int(confidence * 60)

                signals.append({
                    "pair": pred["pair"],
                    "action": action,
                    "strength": strength,
                    "expectedReturn": predicted_return,
                    "risk": max(5, 100 - strength),
                    "timestamp": datetime.now().isoformat(),
                })

            return signals
        except Exception as exc:
            print(f"Error generating trading signals: {exc}")
            return []

    def get_news_headlines(self) -> List[Dict[str, Any]]:
        """Get recent news headlines from local logs."""
        try:
            news_path = os.path.join(self.logs_dir, "news_log.csv")
            if not os.path.exists(news_path):
                return []

            df = pd.read_csv(news_path)
            if df.empty or not {"Headline", "Sentiment", "Date", "Region"}.issubset(df.columns):
                return []

            headlines = []
            for _, row in df.tail(20).iterrows():
                headlines.append({
                    "headline": str(row["Headline"]),
                    "source": "Financial News",
                    "sentiment": float(row["Sentiment"]),
                    "timestamp": str(row["Date"]),
                    "region": str(row["Region"]),
                })

            return headlines
        except Exception as exc:
            print(f"Error loading news headlines: {exc}")
            return []
