import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import os

from carry_trade.paths import PROJECT_ROOT


logs_dir = PROJECT_ROOT / "logs"
os.makedirs(logs_dir, exist_ok=True)
analyzer = SentimentIntensityAnalyzer()

def load_and_tag(filepath, source_name):
    df = pd.read_csv(filepath)
    filepath_text = str(filepath)

    if "cnbc" in filepath_text.lower():
        df["date"] = pd.to_datetime(df["Time"].str.replace("ET", "").str.strip(), errors="coerce").dt.date
        df["title"] = df["Headlines"]
    else:
        for col in ["date", "published", "datetime", "Date", "Time"]:
            if col in df.columns:
                df["date"] = pd.to_datetime(df[col], errors="coerce").dt.date
                break
        else:
            raise ValueError(f"No recognizable date column found in {source_name}")
        
        for title_col in ["title", "Headline", "headlines", "Headlines"]:
            if title_col in df.columns:
                df["title"] = df[title_col]
                break
        else:
            raise ValueError(f"No recognizable title column found in {source_name}")

    df = df.dropna(subset=["date"])
    df["source"] = source_name
    return df

cnbc = load_and_tag(PROJECT_ROOT / "cnbc_headlines.csv", "CNBC")
guardian = load_and_tag(PROJECT_ROOT / "guardian_headlines.csv", "Guardian")
reuters = load_and_tag(PROJECT_ROOT / "reuters_headlines.csv", "Reuters")

df = pd.concat([cnbc, guardian, reuters], ignore_index=True)
df = df.dropna(subset=["title"])

def classify_region(text):
    text = text.lower()
    if any(w in text for w in ["fed", "us", "dollar", "powell", "america"]):
        return "USD"
    elif any(w in text for w in ["euro", "ecb", "eu", "germany", "france", "europa"]):
        return "EUR"
    elif any(w in text for w in ["ukraine", "zelensky", "hryvnia", "kyiv"]):
        return "UAH"
    else:
        return None

df["Region"] = df["title"].apply(classify_region)
df = df.dropna(subset=["Region"])
df["Sentiment"] = df["title"].apply(lambda t: analyzer.polarity_scores(t)["compound"])

df = df.rename(columns={"date": "Date", "title": "Headline"})
df[["Date", "Region", "Headline", "Sentiment"]].to_csv(logs_dir / "news_log.csv", index=False)

print("✅ Cleaned historical news data saved to logs/news_log.csv.")
