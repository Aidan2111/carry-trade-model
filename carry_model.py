
# AI-Enhanced USD/UAH & EUR/UAH Carry Trade Model with Live News Sentiment & Inflation Prediction

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sklearn.ensemble import RandomForestRegressor
from newsapi import NewsApiClient

# Initialize sentiment analyzer and news API client
analyzer = SentimentIntensityAnalyzer()
newsapi = NewsApiClient(api_key='[REDACTED_NEWS_API_KEY]')  # Replace with your NewsAPI key

# Function to fetch headlines for a query using NewsAPI
def fetch_headlines(query, language='en', max_articles=10):
    try:
        articles = newsapi.get_everything(q=query, language=language, sort_by='relevancy', page_size=max_articles)
        return [article['title'] for article in articles['articles']]
    except Exception as e:
        print(f"NewsAPI error for {query}: {e}")
        return []

# Function to compute sentiment score from headlines
def get_sentiment_score_from_news(query):
    headlines = fetch_headlines(query)
    if not headlines:
        return 0  # Neutral fallback
    scores = [analyzer.polarity_scores(h)['compound'] for h in headlines]
    return np.mean(scores)

# Live sentiment scores
sentiment_scores = {
    'USD': get_sentiment_score_from_news("Federal Reserve OR US economy"),
    'EUR': get_sentiment_score_from_news("ECB OR European Union economy"),
    'UAH': get_sentiment_score_from_news("Ukraine OR Zelensky OR hryvnia")
}

# Simulated monthly data (24 months)
np.random.seed(42)
dates = pd.date_range(start="2022-01-01", periods=24, freq='M')

# Simulated nominal interest rates (%)
usd_nominal = np.random.uniform(4.0, 5.0, 24)
eur_nominal = np.random.uniform(3.0, 4.5, 24)
uah_nominal = np.random.uniform(15.0, 20.0, 24)

# Simulated historical inflation data (used to train AI model)
usd_inflation_hist = np.random.uniform(2.0, 3.0, 24)
eur_inflation_hist = np.random.uniform(1.5, 2.5, 24)
uah_inflation_hist = np.random.uniform(20.0, 30.0, 24)

# AI: Predict next period inflation using RandomForest
def train_predict_inflation_model(inflation_series):
    X = np.arange(len(inflation_series)).reshape(-1, 1)
    y = inflation_series
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    return model.predict(X)

usd_predicted_inflation = train_predict_inflation_model(usd_inflation_hist)
eur_predicted_inflation = train_predict_inflation_model(eur_inflation_hist)
uah_predicted_inflation = train_predict_inflation_model(uah_inflation_hist)

# Real interest rates = nominal - AI-predicted inflation
df = pd.DataFrame({
    'Date': dates,
    'r_usd': usd_nominal - usd_predicted_inflation,
    'r_eur': eur_nominal - eur_predicted_inflation,
    'r_uah': uah_nominal - uah_predicted_inflation,
})
df.set_index('Date', inplace=True)

# Simulated FX spot returns (UAH depreciates slightly on avg)
df['usd_uah_return'] = np.random.normal(-0.01, 0.03, 24)
df['eur_uah_return'] = np.random.normal(-0.008, 0.025, 24)

# Carry calculations (real interest differential)
df['carry_usd_uah'] = (df['r_usd'] - df['r_uah']) / 12
df['carry_eur_uah'] = (df['r_eur'] - df['r_uah']) / 12

# Add sentiment adjustment
alpha = 0.5  # weight on sentiment
sent_diff_usd = sentiment_scores['USD'] - sentiment_scores['UAH']
sent_diff_eur = sentiment_scores['EUR'] - sentiment_scores['UAH']
df['adj_carry_usd_uah'] = df['carry_usd_uah'] + alpha * sent_diff_usd
df['adj_carry_eur_uah'] = df['carry_eur_uah'] + alpha * sent_diff_eur

# Strategy return = carry + FX return (unhedged)
df['strategy_return_usd'] = df['adj_carry_usd_uah'] + df['usd_uah_return']
df['strategy_return_eur'] = df['adj_carry_eur_uah'] + df['eur_uah_return']
df['cumulative_return_usd'] = (1 + df['strategy_return_usd']).cumprod()
df['cumulative_return_eur'] = (1 + df['strategy_return_eur']).cumprod()

# Plot
plt.figure(figsize=(12,6))
plt.plot(df.index, df['cumulative_return_usd'], label='USD/UAH Carry Trade (Live News + AI Inflation)')
plt.plot(df.index, df['cumulative_return_eur'], label='EUR/UAH Carry Trade (Live News + AI Inflation)')
plt.title("Live Sentiment-Enhanced Carry Trade Strategy")
plt.xlabel("Date")
plt.ylabel("Cumulative Return")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# Display table
print(df[['r_usd', 'r_eur', 'r_uah', 'carry_usd_uah', 'carry_eur_uah',
          'adj_carry_usd_uah', 'adj_carry_eur_uah',
          'usd_uah_return', 'eur_uah_return',
          'strategy_return_usd', 'strategy_return_eur',
          'cumulative_return_usd', 'cumulative_return_eur']])
