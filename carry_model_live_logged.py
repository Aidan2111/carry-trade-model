
# AI-Enhanced Carry Trade with Logging and Real-Time Sentiment/FX

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sklearn.ensemble import RandomForestRegressor
from newsapi import NewsApiClient
import yfinance as yf
import os
from datetime import datetime

# Initialize
analyzer = SentimentIntensityAnalyzer()
newsapi = NewsApiClient(api_key='[REDACTED_NEWS_API_KEY]')
today = datetime.today().strftime('%Y-%m-%d')

# Create log folders if they don't exist
os.makedirs('logs', exist_ok=True)

# Fetch headlines and sentiment
def fetch_and_log_headlines(query, region):
    try:
        articles = newsapi.get_everything(q=query, language='en', sort_by='relevancy', page_size=10)
        data = []
        for article in articles['articles']:
            headline = article['title']
            score = analyzer.polarity_scores(headline)['compound']
            data.append([today, region, headline, score])
            print(f"{region} Headline: {headline} | Score: {score}")
        df = pd.DataFrame(data, columns=["Date", "Region", "Headline", "Sentiment"])
        df.to_csv("logs/news_log.csv", mode='a', header=not os.path.exists("logs/news_log.csv"), index=False)
        return np.mean([row[3] for row in data]) if data else 0
    except Exception as e:
        print(f"News error ({region}):", e)
        return 0

# Live sentiment
sentiment_scores = {
    'USD': fetch_and_log_headlines("Federal Reserve OR US economy", "USD"),
    'EUR': fetch_and_log_headlines("ECB OR European Union economy", "EUR"),
    'UAH': fetch_and_log_headlines("Ukraine OR Zelensky OR hryvnia", "UAH")
}

# Get FX rates and log
def get_fx_rate(ticker):
    try:
        fx = yf.Ticker(ticker)
        data = fx.history(period='1d')
        price = data['Close'].iloc[-1]
        return price
    except:
        return None

usd_uah = get_fx_rate('USDUAH=X')
eur_uah = get_fx_rate('EURUAH=X')
prev_usd = usd_uah * 1.01 if usd_uah else None
prev_eur = eur_uah * 1.01 if eur_uah else None
fx_return_usd = (usd_uah - prev_usd) / prev_usd if usd_uah else 0
fx_return_eur = (eur_uah - prev_eur) / prev_eur if eur_uah else 0

fx_log = pd.DataFrame([{
    "Date": today,
    "USD_UAH": usd_uah,
    "EUR_UAH": eur_uah,
    "USD_UAH_Return": fx_return_usd,
    "EUR_UAH_Return": fx_return_eur
}])
fx_log.to_csv("logs/fx_log.csv", mode='a', header=not os.path.exists("logs/fx_log.csv"), index=False)

# Simulated macro data
np.random.seed(42)
dates = pd.date_range(start="2022-01-01", periods=24, freq='M')
usd_nom = np.random.uniform(4.0, 5.0, 24)
eur_nom = np.random.uniform(3.0, 4.5, 24)
uah_nom = np.random.uniform(15.0, 20.0, 24)
usd_inf = np.random.uniform(2.0, 3.0, 24)
eur_inf = np.random.uniform(1.5, 2.5, 24)
uah_inf = np.random.uniform(20.0, 30.0, 24)

def predict_inflation(series):
    X = np.arange(len(series)).reshape(-1,1)
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, series)
    return model.predict(X)

usd_pi = predict_inflation(usd_inf)
eur_pi = predict_inflation(eur_inf)
uah_pi = predict_inflation(uah_inf)

df = pd.DataFrame({
    'Date': dates,
    'r_usd': usd_nom - usd_pi,
    'r_eur': eur_nom - eur_pi,
    'r_uah': uah_nom - uah_pi,
})
df.set_index('Date', inplace=True)

df['usd_uah_return'] = [fx_return_usd] * len(df)
df['eur_uah_return'] = [fx_return_eur] * len(df)
df['carry_usd_uah'] = (df['r_usd'] - df['r_uah']) / 12
df['carry_eur_uah'] = (df['r_eur'] - df['r_uah']) / 12

alpha = 0.5
sd_usd = sentiment_scores['USD'] - sentiment_scores['UAH']
sd_eur = sentiment_scores['EUR'] - sentiment_scores['UAH']
df['adj_carry_usd_uah'] = df['carry_usd_uah'] + alpha * sd_usd
df['adj_carry_eur_uah'] = df['carry_eur_uah'] + alpha * sd_eur
df['strategy_return_usd'] = df['adj_carry_usd_uah'] + df['usd_uah_return']
df['strategy_return_eur'] = df['adj_carry_eur_uah'] + df['eur_uah_return']
df['cumulative_return_usd'] = (1 + df['strategy_return_usd']).cumprod()
df['cumulative_return_eur'] = (1 + df['strategy_return_eur']).cumprod()

plt.figure(figsize=(12,6))
plt.plot(df.index, df['cumulative_return_usd'], label='USD/UAH Strategy')
plt.plot(df.index, df['cumulative_return_eur'], label='EUR/UAH Strategy')
plt.title("Carry Trade Strategy - Real-Time FX & Sentiment")
plt.xlabel("Date")
plt.ylabel("Cumulative Return")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
