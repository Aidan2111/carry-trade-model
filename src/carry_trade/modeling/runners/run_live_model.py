"""
Deterministic model-output runner for dashboard integration.

This script reads local FX, sentiment, and macro logs. It writes research
predictions and performance metrics only from available local data, without
randomized or fabricated fallback values.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from carry_trade.paths import PROJECT_ROOT


def run_ensemble_model(base_dir: Optional[str] = None) -> Dict[str, Any]:
    """Run deterministic log-backed research calculations."""
    base_dir = base_dir or str(PROJECT_ROOT)
    try:
        fx_data = load_latest_fx_data(base_dir)
        sentiment_data = load_latest_sentiment_data(base_dir)
        macro_data = load_latest_macro_data(base_dir)

        predictions = generate_predictions(fx_data, sentiment_data, macro_data)
        performance = calculate_performance_metrics(fx_data)

        write_prediction_logs(base_dir, predictions)
        if performance:
            update_performance_log(base_dir, performance)

        return {
            "status": "success",
            "message": "Generated deterministic research outputs from available logs.",
            "predictions": predictions,
            "performance": performance,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as exc:
        return {
            "status": "error",
            "error": str(exc),
            "timestamp": datetime.now().isoformat(),
        }


def load_latest_fx_data(base_dir: str) -> Dict[str, pd.DataFrame]:
    """Load latest FX data from local files."""
    fx_dir = os.path.join(base_dir, "logs", "fx")
    paths = {
        "USD_UAH": os.path.join(fx_dir, "USD_UAH Historical Data.csv"),
        "EUR_UAH": os.path.join(fx_dir, "EUR_UAH Historical Data.csv"),
    }

    fx_data: Dict[str, pd.DataFrame] = {}
    for pair, path in paths.items():
        if not os.path.exists(path):
            continue
        df = pd.read_csv(path)
        if df.empty or "Price" not in df.columns:
            continue
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
            df = df.sort_values("Date")
        fx_data[pair] = df.tail(90).copy()

    return fx_data


def load_latest_sentiment_data(base_dir: str) -> Dict[str, float]:
    """Load latest sentiment data from local news logs."""
    news_path = os.path.join(base_dir, "logs", "news_log.csv")
    if not os.path.exists(news_path):
        return {}

    df = pd.read_csv(news_path)
    if df.empty or not {"Region", "Sentiment"}.issubset(df.columns):
        return {}

    sentiment_data: Dict[str, float] = {}
    for region in ("USD", "EUR", "UAH"):
        region_df = df[df["Region"] == region]
        if not region_df.empty:
            sentiment_data[region] = float(region_df.tail(50)["Sentiment"].mean())

    return sentiment_data


def load_latest_macro_data(base_dir: str) -> Dict[str, float]:
    """Load latest macro data from local macro logs."""
    macro_dir = os.path.join(base_dir, "logs", "macro")
    macro_files = {
        "US_FedFunds.csv": "fed_funds",
        "US_CPI.csv": "us_cpi",
        "US_InflationExpectations.csv": "us_inflation_expectations",
        "EU_ConsumerPrices.csv": "eu_cpi",
    }

    macro_data: Dict[str, float] = {}
    for filename, key in macro_files.items():
        path = os.path.join(macro_dir, filename)
        if not os.path.exists(path):
            continue
        df = pd.read_csv(path)
        if df.empty:
            continue
        for value_col in ("Value", "Price", "Close", "Rate", key):
            if value_col in df.columns:
                macro_data[key] = float(df.iloc[-1][value_col])
                break

    return macro_data


def generate_predictions(
    fx_data: Dict[str, pd.DataFrame],
    sentiment_data: Dict[str, float],
    macro_data: Dict[str, float],
) -> List[Dict[str, Any]]:
    """Generate deterministic research predictions from observed inputs."""
    predictions: List[Dict[str, Any]] = []

    for pair, df in fx_data.items():
        prices = pd.to_numeric(df["Price"], errors="coerce").dropna().to_numpy()
        if len(prices) < 6:
            continue

        returns = np.diff(prices) / prices[:-1]
        recent_returns = returns[-20:] if len(returns) >= 20 else returns
        short_momentum = float(np.mean(returns[-5:]))
        medium_momentum = float(np.mean(recent_returns))
        volatility = float(np.std(recent_returns))

        base_currency = pair.split("_")[0]
        quote_currency = pair.split("_")[1]
        sentiment_spread = (
            sentiment_data.get(base_currency, 0.0) - sentiment_data.get(quote_currency, 0.0)
        )

        macro_tilt = 0.0
        if base_currency == "USD" and "fed_funds" in macro_data:
            macro_tilt += min(max(macro_data["fed_funds"] / 10000, -0.002), 0.002)
        if base_currency == "EUR" and "eu_cpi" in macro_data:
            macro_tilt -= min(max(macro_data["eu_cpi"] / 10000, -0.002), 0.002)

        predicted_return = (
            0.45 * short_momentum
            + 0.35 * medium_momentum
            + 0.15 * sentiment_spread
            + macro_tilt
        )
        predicted_return = float(np.clip(predicted_return * 100, -10.0, 10.0))

        confidence = 0.45
        confidence += min(len(prices), 90) / 90 * 0.25
        confidence += max(0.0, 0.20 - min(volatility, 0.20))
        confidence = float(np.clip(confidence, 0.1, 0.9))

        predictions.append({
            "pair": pair.replace("_", "/"),
            "predicted_return": predicted_return,
            "confidence": confidence,
            "horizon_days": 30,
            "features": {
                "short_momentum": short_momentum,
                "medium_momentum": medium_momentum,
                "volatility": volatility,
                "sentiment_spread": sentiment_spread,
                "macro_tilt": macro_tilt,
            },
            "model": "deterministic_research_heuristic",
            "timestamp": datetime.now().isoformat(),
        })

    return predictions


def calculate_performance_metrics(fx_data: Dict[str, pd.DataFrame]) -> Dict[str, float]:
    """Calculate deterministic performance-style metrics from recent FX data."""
    pair_returns: List[np.ndarray] = []
    total_returns: List[float] = []
    volatilities: List[float] = []
    drawdowns: List[float] = []

    for df in fx_data.values():
        prices = pd.to_numeric(df["Price"], errors="coerce").dropna().to_numpy()
        if len(prices) < 2:
            continue
        returns = np.diff(prices) / prices[:-1]
        if len(returns) == 0:
            continue
        equity = np.cumprod(1 + returns)
        peak = np.maximum.accumulate(equity)
        drawdown = equity / peak - 1

        pair_returns.append(returns)
        total_returns.append(float((prices[-1] / prices[0] - 1) * 100))
        volatilities.append(float(np.std(returns) * np.sqrt(252) * 100))
        drawdowns.append(float(np.min(drawdown) * 100))

    if not pair_returns:
        return {}

    combined_returns = np.concatenate(pair_returns)
    avg_return = float(np.mean(total_returns))
    avg_volatility = float(np.mean(volatilities))
    sharpe_ratio = float(avg_return / max(avg_volatility, 0.01))
    win_rate = float((combined_returns > 0).mean() * 100)

    return {
        "total_return": avg_return,
        "sharpe_ratio": sharpe_ratio,
        "max_drawdown": float(min(drawdowns)),
        "volatility": avg_volatility,
        "win_rate": win_rate,
    }


def write_prediction_logs(base_dir: str, predictions: List[Dict[str, Any]]) -> None:
    """Write prediction outputs for the dashboard when data is available."""
    if not predictions:
        return

    logs_dir = os.path.join(base_dir, "logs")
    os.makedirs(logs_dir, exist_ok=True)

    json_path = os.path.join(logs_dir, "model_predictions.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(predictions, f, indent=2)

    forecast_rows = [{
        "timestamp": pred["timestamp"],
        "pair": pred["pair"],
        "predicted_return": pred["predicted_return"],
        "confidence": pred["confidence"],
        "horizon_days": pred["horizon_days"],
        "model": pred["model"],
    } for pred in predictions]
    pd.DataFrame(forecast_rows).to_csv(os.path.join(logs_dir, "forecast_log.csv"), index=False)


def update_performance_log(base_dir: str, performance_data: Dict[str, float]) -> None:
    """Append deterministic performance metrics to the local performance log."""
    logs_dir = os.path.join(base_dir, "logs")
    os.makedirs(logs_dir, exist_ok=True)
    perf_path = os.path.join(logs_dir, "performance_log.csv")

    perf_entry = {
        "timestamp": datetime.now().isoformat(),
        "date": datetime.now().strftime("%Y-%m-%d"),
        **performance_data,
    }
    df = pd.DataFrame([perf_entry])
    if os.path.exists(perf_path):
        df.to_csv(perf_path, mode="a", header=False, index=False)
    else:
        df.to_csv(perf_path, index=False)


def main() -> None:
    print("Running deterministic carry trade research model for dashboard...")
    print("=" * 60)
    result = run_ensemble_model()

    if result["status"] == "success":
        predictions = result.get("predictions", [])
        print("Model run completed.")
        print(f"Generated {len(predictions)} prediction rows from available logs.")
        for pred in predictions:
            print(
                f"   {pred['pair']}: {pred['predicted_return']:.2f}% "
                f"(confidence: {pred['confidence']:.2f})"
            )
    else:
        print("Model run failed.")
        print(f"Error: {result.get('error')}")

    print("=" * 60)


if __name__ == "__main__":
    main()
