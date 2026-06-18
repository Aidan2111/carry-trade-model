import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor, VotingRegressor
from sklearn.linear_model import Ridge
from lightgbm import LGBMRegressor
from xgboost import XGBRegressor
import matplotlib.pyplot as plt
import os
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import yfinance as yf

# === Setup directories and date range ===
os.makedirs("logs/fx", exist_ok=True)
os.makedirs("logs/macro", exist_ok=True)
os.makedirs("logs", exist_ok=True)  # for news_log.csv

start_date = "2010-01-01"
end_date = datetime.today().strftime("%Y-%m-%d")

# === Load historical FX data from CSVs ===
usd_hist = pd.read_csv("logs/fx/USD_UAH Historical Data.csv")
eur_hist = pd.read_csv("logs/fx/EUR_UAH Historical Data.csv")

usd_hist["date"] = pd.to_datetime(usd_hist["Date"])
eur_hist["date"] = pd.to_datetime(eur_hist["Date"])

usd_hist = usd_hist[["date", "Price"]].rename(columns={"Price": "USD_UAH"})
eur_hist = eur_hist[["date", "Price"]].rename(columns={"Price": "EUR_UAH"})

# === Fetch new FX data from Yahoo Finance ===
def fetch_new_fx(symbol, last_date):
    new_start = last_date + timedelta(days=1)
    if new_start >= datetime.today():
        print(f"No new data needed for {symbol}")
        return pd.DataFrame(columns=["date", symbol])
    try:
        df = yf.download(symbol, start=new_start, end=datetime.today())
        if df.empty:
            print(f"No new data fetched for {symbol}.")
            return pd.DataFrame(columns=["date", symbol])
        df = df.reset_index()
        df["date"] = pd.to_datetime(df["Date"]).dt.date
        if isinstance(df.columns, pd.MultiIndex):
            if ("Close", symbol) in df.columns:
                df = df[[("Close", symbol)]]
                df.columns = [symbol]
                df = df.reset_index().rename(columns={"Date": "date"})
                return df
            else:
                print(f"Unexpected data format for {symbol}: {df.columns}")
                return pd.DataFrame(columns=["date", symbol])
        elif "Adj Close" in df.columns:
            return df[["Adj Close"]].reset_index().rename(columns={"Date": "date", "Adj Close": symbol})
        elif "Close" in df.columns:
            return df[["Close"]].reset_index().rename(columns={"Date": "date", "Close": symbol})
        else:
            print(f"Unexpected data format for {symbol}: {df.columns}")
    except Exception as e:
        print(f"Failed to fetch {symbol}: {e}")
    return pd.DataFrame(columns=["date", symbol])

usd_fx = fetch_new_fx("USDUAH=X", usd_hist["date"].max())
eur_fx = fetch_new_fx("EURUAH=X", eur_hist["date"].max())

if not usd_fx.empty:
    usd_fx.rename(columns={"USDUAH=X": "USD_UAH"}, inplace=True)
if not eur_fx.empty:
    eur_fx.rename(columns={"EURUAH=X": "EUR_UAH"}, inplace=True)

usd_all = pd.concat([usd_hist, usd_fx], ignore_index=True).drop_duplicates(subset="date").sort_values("date")
eur_all = pd.concat([eur_hist, eur_fx], ignore_index=True).drop_duplicates(subset="date").sort_values("date")
fx_data = pd.merge(usd_all, eur_all, on="date", how="outer").sort_values("date").dropna(subset=["USD_UAH", "EUR_UAH"])
fx_data.to_csv("logs/fx/fx_log.csv", index=False)

# === Load macroeconomic data from CSV ===
macro_data = pd.read_csv("logs/macro/macro_log.csv")
macro_data.rename(columns={"US_FedFunds": "USD_FedFunds", "EU_Rate": "EU_Rate"}, inplace=True)
macro_data["date"] = pd.to_datetime(macro_data["date"])

# Add placeholders if missing
if "UAH_Rate" not in macro_data.columns:
    macro_data["UAH_Rate"] = 0.1
if "USD_FedFunds" not in macro_data.columns:
    macro_data["USD_FedFunds"] = 0.05
if "EU_Rate" not in macro_data.columns:
    macro_data["EU_Rate"] = 0.02

# === Load sentiment data from news_log.csv ===
sentiment_path = "logs/news_log.csv"
sentiment_data = pd.read_csv(sentiment_path)
possible_date_cols = ["date", "Date", "timestamp", "Timestamp"]
date_col = next((col for col in possible_date_cols if col in sentiment_data.columns), None)
if not date_col:
    raise ValueError("No recognizable date column found in sentiment data")
sentiment_data["date"] = pd.to_datetime(sentiment_data[date_col])
analyzer = SentimentIntensityAnalyzer()
def compute_sentiment(group):
    scores = group["Headline"].astype(str).apply(lambda x: analyzer.polarity_scores(x)["compound"])
    return scores.mean()
pivoted_sentiment = sentiment_data.groupby(["date", "Region"]).apply(compute_sentiment).unstack(fill_value=0).reset_index()
pivoted_sentiment.rename(columns={"USD": "sentiment_usd", "EUR": "sentiment_eur", "UAH": "sentiment_uah"}, inplace=True)

# === Merge all data ===
print("Before merge:")
print("FX data:", fx_data.shape)
print("Macro data:", macro_data.shape)
print("Sentiment data:", pivoted_sentiment.shape)

# Align date formatting (using date only)
fx_data["date"] = pd.to_datetime(fx_data["date"]).dt.date
macro_data["date"] = pd.to_datetime(macro_data["date"]).dt.date
pivoted_sentiment["date"] = pd.to_datetime(pivoted_sentiment["date"]).dt.date

data = fx_data.merge(macro_data, on="date", how="inner")
print("After FX + Macro merge:", data.shape)
data = data.merge(pivoted_sentiment, on="date", how="left")
print("After adding sentiment:", data.shape)
data["date"] = pd.to_datetime(data["date"])

# Auto-fill missing sentiment columns with 0s
for col in ["sentiment_usd", "sentiment_eur", "sentiment_uah"]:
    if col not in data.columns:
        data[col] = 0.0

data = data.sort_values("date")
data = data.ffill().fillna(0)

# === Feature engineering ===
data["interest_diff_usd"] = data["USD_FedFunds"] - data["UAH_Rate"]
data["interest_diff_eur"] = data["EU_Rate"] - data["UAH_Rate"]
data["usd_return"] = data["USD_UAH"].pct_change().shift(-7)
data["eur_return"] = data["EUR_UAH"].pct_change().shift(-7)

features = [
    "USD_FedFunds", "US_InflationExpectations", "US_YieldCurve", "US_CPI",
    "EU_ConsumerPrices", "interest_diff_usd", "interest_diff_eur",
    "sentiment_usd", "sentiment_eur", "sentiment_uah"
]

data.dropna(subset=features + ["usd_return", "eur_return"], inplace=True)

X = data[features]
y_usd = data["usd_return"]
y_eur = data["eur_return"]

print("Final merged data shape:", data.shape)
print("First few rows:\n", data.head())

train_size = int(0.8 * len(data))
X_train, X_test = X[:train_size], X[train_size:]
y_usd_train, y_usd_test = y_usd[:train_size], y_usd[train_size:]
y_eur_train, y_eur_test = y_eur[:train_size], y_eur[train_size:]

if X_train.empty or y_usd_train.empty:
    print("Training data is empty. Check earlier data merging or filtering.")
    print("X_train shape:", X_train.shape)
    print("y_usd_train shape:", y_usd_train.shape)
    print("Recent rows in merged data:")
    print(data.tail())
    raise ValueError("Training set is empty. Cannot proceed with model fitting.")

# === Data cleaning and feature validation ===
low_variance_cols = [col for col in X.columns if X[col].nunique() <= 1]
if low_variance_cols:
    print("Dropping low-variance features:", low_variance_cols)
    X = X.drop(columns=low_variance_cols)
non_numeric = X.select_dtypes(exclude=[np.number]).columns.tolist()
if non_numeric:
    print("Dropping non-numeric features:", non_numeric)
    X = X.drop(columns=non_numeric)
print("\n=== Feature Summary ===")
print(X.describe().T[["mean", "std", "min", "max"]])
# Store the final features used for training
features_trained = X.columns.tolist()
features = features_trained

# === Modeling ===
models_usd = [
    ("rf", RandomForestRegressor(n_estimators=100)),
    ("xgb", XGBRegressor(n_estimators=100, verbosity=0)),
    ("lgbm", LGBMRegressor(n_estimators=100, min_data_in_leaf=1, min_data_in_bin=1)),
    ("ridge", Ridge(alpha=1.0))
]
ensemble_usd = VotingRegressor(estimators=models_usd)
ensemble_usd.fit(X_train, y_usd_train)

models_eur = [
    ("rf", RandomForestRegressor(n_estimators=100)),
    ("xgb", XGBRegressor(n_estimators=100, verbosity=0)),
    ("lgbm", LGBMRegressor(n_estimators=100, min_data_in_leaf=1, min_data_in_bin=1)),
    ("ridge", Ridge(alpha=1.0))
]
ensemble_eur = VotingRegressor(estimators=models_eur)
ensemble_eur.fit(X_train, y_eur_train)

pred_usd = ensemble_usd.predict(X_test)
pred_eur = ensemble_eur.predict(X_test)

capital = 1_000_000
data_test = data.iloc[train_size:].copy()
data_test["pred_usd"] = pred_usd
data_test["pred_eur"] = pred_eur
data_test["carry_usd"] = data_test["interest_diff_usd"] * data_test["pred_usd"]
data_test["carry_eur"] = data_test["interest_diff_eur"] * data_test["pred_eur"]
data_test["strategy_usd"] = (1 + data_test["carry_usd"]).cumprod() * capital
data_test["strategy_eur"] = (1 + data_test["carry_eur"]).cumprod() * capital
# === Add Market Benchmarks ===
data_test["benchmark_usd"] = (1 + data_test["usd_return"]).cumprod() * capital
data_test["benchmark_eur"] = (1 + data_test["eur_return"]).cumprod() * capital

# === Export Selected Columns to CSV ===
export_cols = ["date", "strategy_usd", "benchmark_usd", "strategy_eur", "benchmark_eur"]
data_test[export_cols].to_csv(os.path.join("logs", "performance_log.csv"), index=False)

# === Unified Plot (Single Graph for Both Pairs) ===
plt.figure(figsize=(14, 7))
plt.plot(data_test["date"], data_test["strategy_usd"], label="Model USD/UAH Carry", linewidth=2)
plt.plot(data_test["date"], data_test["benchmark_usd"], label="Market USD/UAH", linestyle="--")
plt.plot(data_test["date"], data_test["strategy_eur"], label="Model EUR/UAH Carry", linewidth=2)
plt.plot(data_test["date"], data_test["benchmark_eur"], label="Market EUR/UAH", linestyle="--")
plt.title("Carry Trade Strategy vs Market Benchmark")
plt.xlabel("Date")
plt.ylabel("Portfolio Value")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# === Forecast Exchange Rates and Carry ===
forecast_horizons = [7, 30, 60, 90]
# Use the cleaned training features to ensure consistency
latest_features = X.iloc[-1:].copy()
latest_data = data.iloc[-1:].copy()
forecast_results = []

for days in forecast_horizons:
    future_date = latest_data["date"].values[0] + np.timedelta64(days, 'D')
    
    # Use features_trained to ensure we include the same columns as used during training
    pred_usd_ret = ensemble_usd.predict(latest_data[features_trained])[0] * days
    pred_eur_ret = ensemble_eur.predict(latest_data[features_trained])[0] * days

    pred_usd_rate = latest_data["USD_UAH"].values[0] * (1 + pred_usd_ret)
    pred_eur_rate = latest_data["EUR_UAH"].values[0] * (1 + pred_eur_ret)

    carry_usd = latest_data["interest_diff_usd"].values[0] * pred_usd_ret
    carry_eur = latest_data["interest_diff_eur"].values[0] * pred_eur_ret

    trade_usd = "LONG USD/UAH" if carry_usd > 0.001 else "HOLD/EXIT"
    trade_eur = "SHORT EUR/UAH" if carry_eur < -0.001 else "HOLD/EXIT"

    forecast_results.append({
        "horizon_days": days,
        "forecast_date": str(future_date)[:10],
        "pred_usd_return": pred_usd_ret,
        "pred_eur_return": pred_eur_ret,
        "pred_usd_rate": pred_usd_rate,
        "pred_eur_rate": pred_eur_rate,
        "carry_usd": carry_usd,
        "carry_eur": carry_eur,
        "trade_usd": trade_usd,
        "trade_eur": trade_eur
    })

# === Save Forecasts to CSV ===
forecast_df = pd.DataFrame(forecast_results)
forecast_path = os.path.join("logs", "performance_log.csv")

try:
    existing_log = pd.read_csv(forecast_path)
    updated_log = pd.concat([existing_log, forecast_df], ignore_index=True)
except FileNotFoundError:
    updated_log = forecast_df

updated_log.to_csv(forecast_path, index=False)

print("\n=== Forecasts Exported ===")
print(forecast_df.to_string(index=False))



