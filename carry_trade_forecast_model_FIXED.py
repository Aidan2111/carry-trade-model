
# === Carry Trade Model with Forecasting and CSV Export ===

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import VotingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
import lightgbm as lgb
from datetime import datetime
import yfinance as yf

# --- Load Data ---
macro = pd.read_csv("macro_data.csv")
sentiment = pd.read_csv("sentiment_data.csv")
macro["date"] = pd.to_datetime(macro["date"])
sentiment["date"] = pd.to_datetime(sentiment["date"])

# Load FX data
symbols = ["USDUAH=X", "EURUAH=X"]
fx_data = {}
for sym in symbols:
    fx = yf.download(sym, start="2010-01-01", end=datetime.today().strftime("%Y-%m-%d"), progress=False)["Close"]
    fx.name = sym
    fx_data[sym] = fx.reset_index().rename(columns={"Date": "date"})

fx_merged = pd.merge(fx_data["USDUAH=X"], fx_data["EURUAH=X"], on="date", how="outer")
fx_merged.rename(columns={"USDUAH=X": "USD_UAH", "EURUAH=X": "EUR_UAH"}, inplace=True)

# Merge all
data = pd.merge(fx_merged, macro, on="date", how="inner")
data = pd.merge(data, sentiment, on="date", how="left")
data = data.sort_values("date")
data["usd_return"] = data["USD_UAH"].pct_change().fillna(0)
data["eur_return"] = data["EUR_UAH"].pct_change().fillna(0)
data = data.ffill().fillna(0)

# --- Feature Engineering ---
data["interest_diff_usd"] = data["USD_FedFunds"] - data["UAH_Rate"]
data["interest_diff_eur"] = data["EU_Rate"] - data["UAH_Rate"]

# Keep full feature list for future prediction
all_features = [
    "USD_FedFunds", "US_YieldCurve", "EU_ConsumerPrices",
    "US_InflationExpectations", "US_CPI", "interest_diff_usd",
    "interest_diff_eur", "sentiment_usd", "sentiment_eur", "sentiment_uah"
]
features_present = [f for f in all_features if f in data.columns]
X = data[features_present]
y_usd = data["usd_return"]
y_eur = data["eur_return"]

# --- Train/Test Split ---
split = int(len(data) * 0.8)
X_train, X_test = X.iloc[:split], X.iloc[split:]
y_usd_train, y_usd_test = y_usd.iloc[:split], y_usd.iloc[split:]
y_eur_train, y_eur_test = y_eur.iloc[:split], y_eur.iloc[split:]

# --- Ensemble Models ---
model_usd = VotingRegressor([
    ('lr', LinearRegression()),
    ('rf', RandomForestRegressor(n_estimators=100)),
    ('lgbm', lgb.LGBMRegressor())
])
model_eur = VotingRegressor([
    ('lr', LinearRegression()),
    ('rf', RandomForestRegressor(n_estimators=100)),
    ('lgbm', lgb.LGBMRegressor())
])
model_usd.fit(X_train, y_usd_train)
model_eur.fit(X_train, y_eur_train)

# --- Backtest Strategy ---
data_test = data.iloc[split:].copy()
data_test["pred_usd"] = model_usd.predict(X_test)
data_test["pred_eur"] = model_eur.predict(X_test)
data_test["carry_usd"] = data_test["interest_diff_usd"] * data_test["pred_usd"]
data_test["carry_eur"] = data_test["interest_diff_eur"] * data_test["pred_eur"]
capital = 1_000_000
data_test["strategy_usd"] = (1 + data_test["carry_usd"]).cumprod() * capital
data_test["strategy_eur"] = (1 + data_test["carry_eur"]).cumprod() * capital
data_test["benchmark_usd"] = (1 + data_test["usd_return"]).cumprod() * capital
data_test["benchmark_eur"] = (1 + data_test["eur_return"]).cumprod() * capital

# --- Export to CSV ---
export_cols = ["date", "strategy_usd", "strategy_eur", "benchmark_usd", "benchmark_eur"]
export_path = r"carry-trade-model\logs\performance_log.csv"
data_test[export_cols].to_csv(export_path, index=False)

# --- Forecast Future ---
latest_data = data.iloc[-1:].copy()
future_days = [7, 30, 60, 90]
forecast_rows = []

for days in future_days:
    pred_usd_ret = model_usd.predict(latest_data[features_present])[0] * days
    pred_eur_ret = model_eur.predict(latest_data[features_present])[0] * days
    usd_next = latest_data["USD_UAH"].values[0] * (1 + pred_usd_ret)
    eur_next = latest_data["EUR_UAH"].values[0] * (1 + pred_eur_ret)
    forecast_rows.append({
        "horizon": f"{days}_day",
        "predicted_usd_return": pred_usd_ret,
        "predicted_eur_return": pred_eur_ret,
        "predicted_usd_uah": usd_next,
        "predicted_eur_uah": eur_next
    })

forecast_df = pd.DataFrame(forecast_rows)
forecast_df.to_csv(r"carry-trade-model\logs\forecast_log.csv", index=False)

# --- Plotting ---
plt.figure(figsize=(12, 6))
plt.plot(data_test["date"], data_test["strategy_usd"], label="Model USD/UAH Carry")
plt.plot(data_test["date"], data_test["benchmark_usd"], label="Benchmark USD/UAH", linestyle="--")
plt.plot(data_test["date"], data_test["strategy_eur"], label="Model EUR/UAH Carry")
plt.plot(data_test["date"], data_test["benchmark_eur"], label="Benchmark EUR/UAH", linestyle="--")
plt.legend()
plt.title("Carry Trade Strategy vs Benchmark")
plt.xlabel("Date")
plt.ylabel("Portfolio Value")
plt.grid(True)
plt.tight_layout()
plt.show()

# --- Trade Logic ---
rec_usd = "LONG USD/UAH" if forecast_df.loc[0, "predicted_usd_return"] > 0.001 else "HOLD"
rec_eur = "SHORT EUR/UAH" if forecast_df.loc[0, "predicted_eur_return"] < -0.001 else "HOLD"
print("
--- Trade Recommendation ---")
print(f"→ USD Strategy: {rec_usd}")
print(f"→ EUR Strategy: {rec_eur}")
