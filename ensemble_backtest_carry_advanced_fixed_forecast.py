# === Full Carry Trade Model with Forecasts ===
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import lightgbm as lgb
from datetime import datetime, timedelta
import yfinance as yf
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from newsapi import NewsApiClient

# === Load or Fetch FX Data ===
fx_symbols = ["USDUAH=X", "EURUAH=X"]
fx_data = {}
for symbol in fx_symbols:
    fx = yf.download(symbol, start="2010-01-01", end=datetime.today().strftime("%Y-%m-%d"), progress=False)["Close"]
    fx.name = symbol
    fx_data[symbol] = fx.reset_index().rename(columns={"Date": "date"})

fx_merged = pd.merge(fx_data["USDUAH=X"], fx_data["EURUAH=X"], on="date", how="outer")
fx_merged.rename(columns={"USDUAH=X": "USD_UAH", "EURUAH=X": "EUR_UAH"}, inplace=True)

# === Load Macro Data ===
macro = pd.read_csv("macro_data.csv")
macro["date"] = pd.to_datetime(macro["date"])

# === Load Sentiment Data ===
sentiment = pd.read_csv("sentiment_data.csv")
sentiment["date"] = pd.to_datetime(sentiment["date"])

# === Merge All Data ===
data = pd.merge(fx_merged, macro, on="date", how="inner")
data = pd.merge(data, sentiment, on="date", how="left")
data = data.sort_values("date")
data = data.ffill().fillna(0)

# === Compute Returns ===
data["usd_return"] = data["USD_UAH"].pct_change().fillna(0)
data["eur_return"] = data["EUR_UAH"].pct_change().fillna(0)

# === Feature Engineering ===
data["interest_diff_usd"] = data["USD_FedFunds"] - data["UAH_Rate"]
data["interest_diff_eur"] = data["EU_Rate"] - data["UAH_Rate"]

# === Feature Selection ===
features = [
    "USD_FedFunds", "US_YieldCurve", "EU_ConsumerPrices", "US_InflationExpectations", 
    "US_CPI", "interest_diff_usd", "interest_diff_eur", "sentiment_usd", "sentiment_eur", "sentiment_uah"
]
target_usd = "usd_return"
target_eur = "eur_return"

# === Train/Test Split ===
train_size = int(len(data) * 0.8)
X = data[features]
y_usd = data[target_usd]
y_eur = data[target_eur]

X_train, X_test = X.iloc[:train_size], X.iloc[train_size:]
y_usd_train, y_usd_test = y_usd.iloc[:train_size], y_usd.iloc[train_size:]
y_eur_train, y_eur_test = y_eur.iloc[:train_size], y_eur.iloc[train_size:]

# === Model Training ===
model_usd = lgb.LGBMRegressor(n_estimators=100, learning_rate=0.1)
model_usd.fit(X_train, y_usd_train)

model_eur = lgb.LGBMRegressor(n_estimators=100, learning_rate=0.1)
model_eur.fit(X_train, y_eur_train)

# === Predictions ===
pred_usd = model_usd.predict(X_test)
pred_eur = model_eur.predict(X_test)

# === Strategy Backtest ===
capital = 1_000_000
data_test = data.iloc[train_size:].copy()
data_test["pred_usd"] = pred_usd
data_test["pred_eur"] = pred_eur
data_test["carry_usd"] = data_test["interest_diff_usd"] * data_test["pred_usd"]
data_test["carry_eur"] = data_test["interest_diff_eur"] * data_test["pred_eur"]
data_test["strategy_usd"] = (1 + data_test["carry_usd"]).cumprod() * capital
data_test["strategy_eur"] = (1 + data_test["carry_eur"]).cumprod() * capital
data_test["benchmark_usd"] = (1 + data_test["usd_return"]).cumprod() * capital
data_test["benchmark_eur"] = (1 + data_test["eur_return"]).cumprod() * capital

# === Export Results to CSV ===
export_cols = ["date", "USD_UAH", "EUR_UAH", "strategy_usd", "benchmark_usd", "strategy_eur", "benchmark_eur"]
data_test[export_cols].to_csv(r"carry-trade-model\logs\performance_log.csv", index=False)

# === Plotting ===
plt.figure(figsize=(12, 6))
plt.plot(data_test["date"], data_test["strategy_usd"], label="Model USD/UAH Carry")
plt.plot(data_test["date"], data_test["benchmark_usd"], label="Market USD/UAH", linestyle="--")
plt.plot(data_test["date"], data_test["strategy_eur"], label="Model EUR/UAH Carry")
plt.plot(data_test["date"], data_test["benchmark_eur"], label="Market EUR/UAH", linestyle="--")
plt.legend()
plt.title("Carry Trade Strategy vs Market Benchmark (Full Test Range)")
plt.xlabel("Date")
plt.ylabel("Portfolio Value")
plt.grid(True)
plt.tight_layout()
plt.show()

# === Multi-Horizon Forecasts ===
horizons = [7, 30, 60, 90]
latest_data = data.iloc[-1:].copy()
outlook_results = []

for days in horizons:
    usd_ret = model_usd.predict(latest_data[features])[0] * days
    eur_ret = model_eur.predict(latest_data[features])[0] * days
    usd_fx = latest_data["USD_UAH"].values[0] * (1 + usd_ret)
    eur_fx = latest_data["EUR_UAH"].values[0] * (1 + eur_ret)
    usd_carry = latest_data["interest_diff_usd"].values[0] * usd_ret
    eur_carry = latest_data["interest_diff_eur"].values[0] * eur_ret
    outlook_results.append([days, usd_ret, usd_fx, usd_carry, eur_ret, eur_fx, eur_carry])

forecast_df = pd.DataFrame(outlook_results, columns=[
    "Days", "USD_Return", "USD_FX_Rate", "USD_Carry", 
    "EUR_Return", "EUR_FX_Rate", "EUR_Carry"
])
forecast_df.to_csv(r"carry-trade-model\logs\forecast_log.csv", index=False)

# === Trade Logic ===
recommendation = forecast_df.copy()
recommendation["USD_Trade"] = recommendation["USD_Carry"].apply(lambda x: "LONG USD/UAH" if x > 0.001 else "HOLD/EXIT")
recommendation["EUR_Trade"] = recommendation["EUR_Carry"].apply(lambda x: "SHORT EUR/UAH" if x < -0.001 else "HOLD/EXIT")
print(recommendation)

