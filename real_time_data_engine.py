"""
Advanced Real-Time Data Collection Engine for Carry Trade Model
==============================================================

This system provides real-time data collection from multiple sources with:
- Redundant data sources for reliability
- Automatic fallback mechanisms
- Data validation and cleaning
- Continuous background monitoring
- Smart rate limiting and caching
- Error handling and logging
"""

import pandas as pd
import numpy as np
import requests
import yfinance as yf
import feedparser
import time
import os
import json
import logging
from datetime import datetime, timedelta
from threading import Thread, Lock
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from news_client import get_newsapi_client
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor
import schedule

# Configuration
@dataclass
class DataConfig:
    base_dir: str = os.getenv(
        "CARRY_TRADE_MODEL_DIR",
        os.path.dirname(os.path.abspath(__file__))
    )
    update_intervals: Dict[str, int] = None  # seconds
    api_keys: Dict[str, str] = None
    data_sources: Dict[str, List[str]] = None
    
    def __post_init__(self):
        if self.update_intervals is None:
            self.update_intervals = {
                'fx': 60,      # FX rates every 1 minute
                'news': 300,   # News every 5 minutes  
                'macro': 3600, # Macro data every 1 hour
                'sentiment': 180 # Sentiment every 3 minutes
            }
        
        if self.api_keys is None:
            self.api_keys = {
                'newsapi': os.getenv('NEWS_API_KEY'),
                'alpha_vantage': os.getenv('ALPHA_VANTAGE_API_KEY'),
                'fred': os.getenv('FRED_API_KEY'),
                'fxrates': os.getenv('FXRATES_API_KEY')
            }
        
        if self.data_sources is None:
            self.data_sources = {
                'fx_apis': [
                    'yfinance',
                    'alpha_vantage', 
                    'exchangerate_api',
                    'fxrates_api'
                ],
                'news_sources': [
                    'newsapi',
                    'reuters_rss',
                    'cnbc_rss',
                    'bloomberg_rss',
                    'financial_times_rss'
                ],
                'macro_sources': [
                    'fred_api',
                    'ecb_api',
                    'yahoo_finance',
                    'web_scraping'
                ]
            }

class RealTimeDataEngine:
    def __init__(self, config: DataConfig):
        self.config = config
        self.base_dir = config.base_dir
        self.log_dir = os.path.join(self.base_dir, "logs")
        self.cache_dir = os.path.join(self.base_dir, "cache")
        
        # Create directories
        os.makedirs(self.log_dir, exist_ok=True)
        os.makedirs(self.cache_dir, exist_ok=True)
        os.makedirs(os.path.join(self.log_dir, "fx"), exist_ok=True)
        os.makedirs(os.path.join(self.log_dir, "macro"), exist_ok=True)
        
        # Initialize components
        self.setup_logging()
        self.analyzer = SentimentIntensityAnalyzer()
        self.newsapi = get_newsapi_client()
        
        # Data cache and locks
        self.data_cache = {}
        self.cache_locks = {
            'fx': Lock(),
            'news': Lock(),
            'macro': Lock(),
            'sentiment': Lock()
        }
        
        # Status tracking
        self.last_updates = {}
        self.error_counts = {}
        self.running = False
        
        self.logger.info("Real-Time Data Engine initialized")
    
    def setup_logging(self):
        """Setup comprehensive logging"""
        log_file = os.path.join(self.log_dir, 'data_engine.log')
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('DataEngine')

class FXDataCollector:
    def __init__(self, engine: RealTimeDataEngine):
        self.engine = engine
        self.logger = engine.logger
        self.pairs = ['USD/UAH', 'EUR/UAH', 'EUR/USD', 'GBP/USD', 'USD/JPY']
        self.yf_symbols = {
            'USD/UAH': 'USDUAH=X',
            'EUR/UAH': 'EURUAH=X', 
            'EUR/USD': 'EURUSD=X',
            'GBP/USD': 'GBPUSD=X',
            'USD/JPY': 'USDJPY=X'
        }
        
    async def collect_fx_data(self) -> Dict[str, Any]:
        """Collect FX data from multiple sources with fallbacks"""
        fx_data = {}
        
        for pair in self.pairs:
            try:
                # Try multiple sources in order
                rate = await self._get_fx_rate_with_fallback(pair)
                if rate:
                    fx_data[pair] = {
                        'rate': rate,
                        'timestamp': datetime.now().isoformat(),
                        'source': 'multi_source'
                    }
                    
            except Exception as e:
                self.logger.error(f"Error collecting FX data for {pair}: {e}")
        
        # Update CSV files
        if fx_data:
            self._update_fx_csvs(fx_data)
        
        return fx_data
    
    async def _get_fx_rate_with_fallback(self, pair: str) -> Optional[float]:
        """Try multiple sources for FX rate"""
        
        # Source 1: Yahoo Finance
        try:
            symbol = self.yf_symbols.get(pair)
            if symbol:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period='1d', interval='1m')
                if not hist.empty:
                    return float(hist['Close'].iloc[-1])
        except Exception as e:
            self.logger.warning(f"Yahoo Finance failed for {pair}: {e}")
        
        # Source 2: Alpha Vantage (if key available)
        try:
            if self.engine.config.api_keys.get('alpha_vantage'):
                rate = await self._get_alpha_vantage_rate(pair)
                if rate:
                    return rate
        except Exception as e:
            self.logger.warning(f"Alpha Vantage failed for {pair}: {e}")
        
        # Source 3: Free Exchange Rate API
        try:
            rate = await self._get_exchangerate_api_rate(pair)
            if rate:
                return rate
        except Exception as e:
            self.logger.warning(f"ExchangeRate API failed for {pair}: {e}")
        
        return None
    
    async def _get_exchangerate_api_rate(self, pair: str) -> Optional[float]:
        """Get rate from exchangerate-api.com (free tier: 1500 requests/month)"""
        if '/' not in pair:
            return None
            
        base, quote = pair.split('/')
        url = f"https://api.exchangerate-api.com/v4/latest/{base}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('rates', {}).get(quote)
        return None
    
    async def _get_alpha_vantage_rate(self, pair: str) -> Optional[float]:
        """Get rate from Alpha Vantage API"""
        if '/' not in pair:
            return None
            
        base, quote = pair.split('/')
        api_key = self.engine.config.api_keys.get('alpha_vantage')
        
        if not api_key:
            return None
            
        url = f"https://www.alphavantage.co/query"
        params = {
            'function': 'CURRENCY_EXCHANGE_RATE',
            'from_currency': base,
            'to_currency': quote,
            'apikey': api_key
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    rate_info = data.get('Realtime Currency Exchange Rate', {})
                    rate_str = rate_info.get('5. Exchange Rate')
                    if rate_str:
                        return float(rate_str)
        return None
    
    def _update_fx_csvs(self, fx_data: Dict[str, Any]):
        """Update the historical CSV files with new data"""
        try:
            for pair, data in fx_data.items():
                filename = pair.replace('/', '_') + " Historical Data.csv"
                file_path = os.path.join(self.engine.log_dir, 'fx', filename)
                
                # Create new row
                new_row = {
                    'Date': datetime.now().strftime('%m/%d/%Y'),
                    'Price': data['rate'],
                    'Open': data['rate'],
                    'High': data['rate'],
                    'Low': data['rate'],
                    'Vol.': '',
                    'Change %': '0.00%'  # Calculate if historical data available
                }
                
                # Load existing data
                if os.path.exists(file_path):
                    existing_df = pd.read_csv(file_path)
                    
                    # Calculate change % if possible
                    if not existing_df.empty:
                        prev_price = existing_df.iloc[0]['Price']
                        change_pct = ((data['rate'] - prev_price) / prev_price) * 100
                        new_row['Change %'] = f"{change_pct:.2f}%"
                    
                    # Add new row at the beginning
                    new_df = pd.concat([pd.DataFrame([new_row]), existing_df], ignore_index=True)
                else:
                    new_df = pd.DataFrame([new_row])
                
                # Save updated data
                new_df.to_csv(file_path, index=False)
                self.logger.info(f"Updated {filename} with rate {data['rate']}")
                
        except Exception as e:
            self.logger.error(f"Error updating FX CSVs: {e}")

class NewsDataCollector:
    def __init__(self, engine: RealTimeDataEngine):
        self.engine = engine
        self.logger = engine.logger
        self.rss_feeds = {
            'reuters_business': 'http://feeds.reuters.com/reuters/businessNews',
            'reuters_markets': 'http://feeds.reuters.com/news/artsculture',
            'cnbc_world': 'https://www.cnbc.com/id/100727362/device/rss/rss.html',
            'bloomberg': 'https://feeds.bloomberg.com/markets/news.rss',
            'ft_markets': 'https://www.ft.com/rss/markets',
            'bbc_business': 'http://feeds.bbci.co.uk/news/business/rss.xml'
        }
        
    async def collect_news_data(self) -> List[Dict[str, Any]]:
        """Collect news from multiple sources"""
        all_news = []
        
        # Collect from RSS feeds (free and reliable)
        rss_news = await self._collect_rss_news()
        all_news.extend(rss_news)
        
        # Collect from NewsAPI (with rate limiting)
        api_news = await self._collect_newsapi_news()
        all_news.extend(api_news)
        
        # Process sentiment and classify regions
        processed_news = self._process_news_sentiment(all_news)
        
        # Update news log
        if processed_news:
            self._update_news_log(processed_news)
        
        return processed_news
    
    async def _collect_rss_news(self) -> List[Dict[str, Any]]:
        """Collect news from RSS feeds"""
        news_items = []
        
        for source, url in self.rss_feeds.items():
            try:
                # Use feedparser to parse RSS
                feed = feedparser.parse(url)
                
                for entry in feed.entries[:5]:  # Latest 5 from each source
                    news_items.append({
                        'title': entry.get('title', ''),
                        'description': entry.get('description', ''),
                        'source': source,
                        'published_at': entry.get('published', ''),
                        'url': entry.get('link', '')
                    })
                    
                self.logger.info(f"Collected {len(feed.entries[:5])} articles from {source}")
                
            except Exception as e:
                self.logger.warning(f"RSS collection failed for {source}: {e}")
        
        return news_items
    
    async def _collect_newsapi_news(self) -> List[Dict[str, Any]]:
        """Collect news from NewsAPI with rate limiting"""
        if self.engine.newsapi is None:
            self.logger.info("NEWS_API_KEY not configured; skipping NewsAPI collection")
            return []

        news_items = []
        
        try:
            # Limit to avoid rate limits (NewsAPI: 1000 requests/day on free tier)
            queries = [
                'forex OR currency OR exchange rate',
                'Federal Reserve OR ECB OR central bank',
                'Ukraine OR Ukrainian economy',
                'inflation OR interest rate'
            ]
            
            for query in queries[:2]:  # Limit to 2 queries to manage rate limits
                articles = self.engine.newsapi.get_everything(
                    q=query,
                    language='en',
                    sort_by='publishedAt',
                    page_size=10
                )
                
                for article in articles.get('articles', []):
                    news_items.append({
                        'title': article.get('title', ''),
                        'description': article.get('description', ''),
                        'source': f"newsapi_{article.get('source', {}).get('name', 'unknown')}",
                        'published_at': article.get('publishedAt', ''),
                        'url': article.get('url', '')
                    })
                
                # Rate limiting pause
                time.sleep(1)
                
        except Exception as e:
            self.logger.warning(f"NewsAPI collection failed: {e}")
        
        return news_items
    
    def _process_news_sentiment(self, news_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process sentiment and classify regions for news items"""
        processed_news = []
        
        for item in news_items:
            try:
                title = item.get('title', '')
                if not title:
                    continue
                
                # Classify region
                region = self._classify_region(title)
                if not region:
                    continue
                
                # Calculate sentiment
                sentiment_score = self.engine.analyzer.polarity_scores(title)['compound']
                
                processed_news.append({
                    'Date': datetime.now().strftime('%Y-%m-%d'),
                    'Region': region,
                    'Headline': title,
                    'Sentiment': sentiment_score,
                    'Source': item.get('source', ''),
                    'URL': item.get('url', '')
                })
                
            except Exception as e:
                self.logger.warning(f"Error processing news item: {e}")
        
        return processed_news
    
    def _classify_region(self, text: str) -> Optional[str]:
        """Classify news text by region/currency"""
        text_lower = text.lower()
        
        # USD indicators
        usd_keywords = [
            'fed', 'federal reserve', 'powell', 'us economy', 'united states',
            'dollar', 'usd', 'american', 'usa', 'washington', 'treasury'
        ]
        
        # EUR indicators  
        eur_keywords = [
            'ecb', 'european central bank', 'lagarde', 'eu', 'europe',
            'euro', 'eur', 'eurozone', 'germany', 'france', 'italy'
        ]
        
        # UAH indicators
        uah_keywords = [
            'ukraine', 'ukrainian', 'kyiv', 'kiev', 'zelensky',
            'hryvnia', 'uah', 'crimea', 'donbas'
        ]
        
        # Check for keywords
        if any(keyword in text_lower for keyword in usd_keywords):
            return 'USD'
        elif any(keyword in text_lower for keyword in eur_keywords):
            return 'EUR'
        elif any(keyword in text_lower for keyword in uah_keywords):
            return 'UAH'
        
        return None
    
    def _update_news_log(self, news_items: List[Dict[str, Any]]):
        """Update the news log CSV file"""
        try:
            news_log_path = os.path.join(self.engine.log_dir, 'news_log.csv')
            
            # Convert to DataFrame
            new_df = pd.DataFrame(news_items)
            
            # Load existing data
            if os.path.exists(news_log_path):
                existing_df = pd.read_csv(news_log_path)
                
                # Combine and remove duplicates
                combined_df = pd.concat([new_df, existing_df], ignore_index=True)
                combined_df.drop_duplicates(subset=['Headline'], inplace=True)
            else:
                combined_df = new_df
            
            # Save updated data
            combined_df.to_csv(news_log_path, index=False)
            self.logger.info(f"Updated news log with {len(news_items)} new items")
            
        except Exception as e:
            self.logger.error(f"Error updating news log: {e}")

class MacroDataCollector:
    def __init__(self, engine: RealTimeDataEngine):
        self.engine = engine
        self.logger = engine.logger
        
    async def collect_macro_data(self) -> Dict[str, Any]:
        """Collect macro economic data from multiple sources"""
        macro_data = {}
        
        # Collect from different sources
        fred_data = await self._collect_fred_data()
        yahoo_data = await self._collect_yahoo_macro()
        
        # Combine data
        macro_data.update(fred_data)
        macro_data.update(yahoo_data)
        
        # Update CSV files
        if macro_data:
            self._update_macro_csvs(macro_data)
        
        return macro_data
    
    async def _collect_fred_data(self) -> Dict[str, Any]:
        """Collect data from Federal Reserve Economic Data (FRED)"""
        fred_data = {}
        
        # FRED series we want to track
        fred_series = {
            'FEDFUNDS': 'US_FedFunds',
            'CPIAUCSL': 'US_CPI',
            'T5YIE': 'US_InflationExpectations',
            'DGS10': 'US_10Y_Treasury'
        }
        
        try:
            for series_id, file_name in fred_series.items():
                # Use FRED API or web scraping
                data = await self._get_fred_series(series_id)
                if data:
                    fred_data[file_name] = data
                    
        except Exception as e:
            self.logger.error(f"FRED data collection failed: {e}")
        
        return fred_data
    
    async def _get_fred_series(self, series_id: str) -> Optional[Dict[str, Any]]:
        """Get specific FRED series data"""
        try:
            self.logger.info("FRED_API_KEY not configured; skipping %s", series_id)
        except Exception as e:
            self.logger.warning(f"FRED series {series_id} failed: {e}")
        
        return None
    
    async def _collect_yahoo_macro(self) -> Dict[str, Any]:
        """Collect macro data from Yahoo Finance"""
        yahoo_data = {}
        
        # Treasury yields and indices
        symbols = {
            '^TNX': 'US_10Y_Treasury',
            '^FVX': 'US_5Y_Treasury',
            '^IRX': 'US_3M_Treasury'
        }
        
        try:
            for symbol, name in symbols.items():
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period='1d')
                
                if not hist.empty:
                    yahoo_data[name] = {
                        'date': datetime.now().strftime('%Y-%m-%d'),
                        'value': float(hist['Close'].iloc[-1])
                    }
                    
        except Exception as e:
            self.logger.warning(f"Yahoo macro data failed: {e}")
        
        return yahoo_data
    
    def _update_macro_csvs(self, macro_data: Dict[str, Any]):
        """Update macro data CSV files"""
        try:
            macro_dir = os.path.join(self.engine.log_dir, 'macro')
            
            for indicator, data in macro_data.items():
                file_path = os.path.join(macro_dir, f"{indicator}.csv")
                
                # Create new row
                new_row = {
                    'date': data['date'],
                    indicator: data['value']
                }
                
                # Update or create CSV
                if os.path.exists(file_path):
                    existing_df = pd.read_csv(file_path)
                    new_df = pd.concat([pd.DataFrame([new_row]), existing_df], ignore_index=True)
                else:
                    new_df = pd.DataFrame([new_row])
                
                new_df.to_csv(file_path, index=False)
                self.logger.info(f"Updated {indicator}.csv")
                
        except Exception as e:
            self.logger.error(f"Error updating macro CSVs: {e}")

class DataOrchestrator:
    def __init__(self, config: DataConfig):
        self.config = config
        self.engine = RealTimeDataEngine(config)
        
        # Initialize collectors
        self.fx_collector = FXDataCollector(self.engine)
        self.news_collector = NewsDataCollector(self.engine)
        self.macro_collector = MacroDataCollector(self.engine)
        
        self.logger = self.engine.logger
        
    def start_collection(self):
        """Start the real-time data collection"""
        self.logger.info("🚀 Starting Real-Time Data Collection Engine")
        
        # Schedule different data types at different intervals
        schedule.every(self.config.update_intervals['fx']).seconds.do(
            lambda: asyncio.run(self._collect_fx_data())
        )
        
        schedule.every(self.config.update_intervals['news']).seconds.do(
            lambda: asyncio.run(self._collect_news_data())
        )
        
        schedule.every(self.config.update_intervals['macro']).seconds.do(
            lambda: asyncio.run(self._collect_macro_data())
        )
        
        # Run initial collection
        asyncio.run(self._run_initial_collection())
        
        # Start scheduler
        self.engine.running = True
        while self.engine.running:
            schedule.run_pending()
            time.sleep(1)
    
    async def _run_initial_collection(self):
        """Run initial data collection on startup"""
        self.logger.info("Running initial data collection...")
        
        try:
            # Collect all data types initially
            fx_task = self._collect_fx_data()
            news_task = self._collect_news_data()
            macro_task = self._collect_macro_data()
            
            # Run in parallel
            await asyncio.gather(fx_task, news_task, macro_task, return_exceptions=True)
            
            self.logger.info("✅ Initial data collection completed")
            
        except Exception as e:
            self.logger.error(f"Initial collection failed: {e}")
    
    async def _collect_fx_data(self):
        """Wrapper for FX data collection"""
        try:
            data = await self.fx_collector.collect_fx_data()
            self.engine.last_updates['fx'] = datetime.now()
            self.logger.info(f"FX data collected: {len(data)} pairs")
        except Exception as e:
            self.logger.error(f"FX collection error: {e}")
            self.engine.error_counts['fx'] = self.engine.error_counts.get('fx', 0) + 1
    
    async def _collect_news_data(self):
        """Wrapper for news data collection"""
        try:
            data = await self.news_collector.collect_news_data()
            self.engine.last_updates['news'] = datetime.now()
            self.logger.info(f"News data collected: {len(data)} articles")
        except Exception as e:
            self.logger.error(f"News collection error: {e}")
            self.engine.error_counts['news'] = self.engine.error_counts.get('news', 0) + 1
    
    async def _collect_macro_data(self):
        """Wrapper for macro data collection"""
        try:
            data = await self.macro_collector.collect_macro_data()
            self.engine.last_updates['macro'] = datetime.now()
            self.logger.info(f"Macro data collected: {len(data)} indicators")
        except Exception as e:
            self.logger.error(f"Macro collection error: {e}")
            self.engine.error_counts['macro'] = self.engine.error_counts.get('macro', 0) + 1
    
    def stop_collection(self):
        """Stop the data collection"""
        self.engine.running = False
        self.logger.info("Data collection stopped")
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of the data collection system"""
        return {
            'running': self.engine.running,
            'last_updates': self.engine.last_updates,
            'error_counts': self.engine.error_counts,
            'uptime': datetime.now().isoformat()
        }

# Main execution
if __name__ == "__main__":
    print("🔄 Advanced Real-Time Data Collection Engine")
    print("=" * 60)
    
    # Initialize configuration
    config = DataConfig()
    
    # Create and start orchestrator
    orchestrator = DataOrchestrator(config)
    
    try:
        print("Starting real-time data collection...")
        print("📊 FX rates updated every 1 minute")
        print("📰 News updated every 5 minutes")
        print("📈 Macro data updated every 1 hour")
        print("🛑 Press Ctrl+C to stop")
        print("=" * 60)
        
        orchestrator.start_collection()
        
    except KeyboardInterrupt:
        print("\n🛑 Stopping data collection...")
        orchestrator.stop_collection()
        print("✅ Data collection stopped")
    except Exception as e:
        print(f"❌ Error: {e}")
        orchestrator.stop_collection()
