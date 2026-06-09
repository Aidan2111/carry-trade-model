import os
import pandas as pd
import requests
from datetime import datetime
from news_client import get_newsapi_client
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import yfinance as yf

# --- Setup directories using absolute paths ---
base_dir = r"carry-trade-model"
log_dir = os.path.join(base_dir, "logs")
macro_dir = os.path.join(log_dir, "macro")
fx_dir = os.path.join(log_dir, "fx")

os.makedirs(log_dir, exist_ok=True)
os.makedirs(macro_dir, exist_ok=True)
os.makedirs(fx_dir, exist_ok=True)

# --- Paths for saving files ---
news_log_path = os.path.join(log_dir, "news_log.csv")

# --- Initialize NewsAPI client from NEWS_API_KEY when available ---
newsapi = get_newsapi_client()

# --- Define date range for new articles ---
# We fetch articles from 2020-01-01 up to today.
from_date = "2020-01-01"
to_date = datetime.today().strftime('%Y-%m-%d')

# --- Fetch articles using NewsAPI ---
all_articles = []
page = 1
page_size = 100  # maximum page size supported
while newsapi is not None:
    response = newsapi.get_everything(
        q="finance OR economics OR news",  # adjust query keywords as needed
        from_param=from_date,
        to=to_date,
        language="en",
        sort_by="publishedAt",
        page=page,
        page_size=page_size
    )
    articles = response.get("articles", [])
    if not articles:
        break
    all_articles.extend(articles)
    # Break if fewer than page_size articles were returned (end of results)
    if len(articles) < page_size:
        break
    page += 1

if newsapi is None:
    print("NEWS_API_KEY is not configured; skipping NewsAPI historical fetch.")

print(f"Fetched {len(all_articles)} articles from NewsAPI.")

# --- Convert articles to DataFrame ---
if all_articles:
    # Choose the fields you want to keep
    news_df = pd.DataFrame(all_articles)
    # Convert publishedAt to datetime and extract date
    news_df["date"] = pd.to_datetime(news_df["publishedAt"]).dt.date
    # Rename 'title' to 'Headline'
    news_df = news_df.rename(columns={"title": "Headline"})
    # Select desired columns; adjust as needed
    news_df = news_df[["date", "Headline", "description", "url"]]
else:
    news_df = pd.DataFrame(columns=["date", "Headline", "description", "url"])

# --- Append or merge with existing news log ---
if os.path.exists(news_log_path):
    existing_news = pd.read_csv(news_log_path)
    # Combine and drop duplicates (e.g. by URL)
    combined_news = pd.concat([existing_news, news_df], ignore_index=True)
    combined_news.drop_duplicates(subset="url", inplace=True)
else:
    combined_news = news_df

# --- Save updated news log ---
combined_news.to_csv(news_log_path, index=False)
print(f"Updated news log saved to {news_log_path}")

