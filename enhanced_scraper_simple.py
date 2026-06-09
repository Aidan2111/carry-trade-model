"""
Enhanced Auto-Scraper for Carry Trade Model
==========================================

This script improves local data collection by:
1. Adding multiple FX data sources with fallbacks
2. Enhancing news collection with free RSS feeds
3. Implementing real-time macro data
4. Adding automatic scheduling and error handling
5. Maintaining the expected CSV file formats

USAGE:
- Run once: python enhanced_scraper_simple.py --once
- Run continuously: python enhanced_scraper_simple.py --auto
"""

import pandas as pd
import numpy as np
import requests
import yfinance as yf
import time
import os
import json
import sys
from datetime import datetime, timedelta
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from news_client import get_newsapi_client
import logging
from typing import Dict, List, Optional
import threading

class SimpleEnhancedScraper:
    def __init__(self):
        # Use current project directory
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.log_dir = os.path.join(self.base_dir, "logs")
        self.fx_dir = os.path.join(self.log_dir, "fx")
        self.macro_dir = os.path.join(self.log_dir, "macro")
        
        # Create directories if they don't exist
        os.makedirs(self.log_dir, exist_ok=True)
        os.makedirs(self.fx_dir, exist_ok=True)
        os.makedirs(self.macro_dir, exist_ok=True)
        
        # Initialize optional NewsAPI client from NEWS_API_KEY
        self.newsapi = get_newsapi_client()
        self.analyzer = SentimentIntensityAnalyzer()
        
        # FX pairs from local CSV files
        self.fx_pairs = {
            'USD_UAH': 'USDUAH=X',
            'EUR_UAH': 'EURUAH=X'
        }
        
        # Status tracking
        self.running = False
        self.last_update = {}
        
        print("Enhanced Scraper initialized - ready for local data collection.")
    
    def get_multi_source_fx_data(self):
        """Enhanced FX collection with multiple sources"""
        print(f"\n💱 Collecting FX data at {datetime.now().strftime('%H:%M:%S')}")
        
        for pair_name, yahoo_symbol in self.fx_pairs.items():
            print(f"   Processing {pair_name}...")
            
            # Try multiple sources in order
            rate = self._get_fx_rate_multi_source(pair_name, yahoo_symbol)
            
            if rate:
                self._update_fx_historical_csv(pair_name, rate)
                print(f"   ✅ {pair_name}: {rate:.4f} (updated CSV)")
            else:
                print(f"   ❌ {pair_name}: All sources failed")
    
    def _get_fx_rate_multi_source(self, pair_name: str, yahoo_symbol: str) -> Optional[float]:
        """Try multiple sources for FX rates"""
        
        # Source 1: Yahoo Finance
        try:
            ticker = yf.Ticker(yahoo_symbol)
            # Try recent data first
            hist = ticker.history(period='1d', interval='1m')
            if not hist.empty:
                rate = float(hist['Close'].iloc[-1])
                print(f"     🎯 Yahoo Finance: {rate:.4f}")
                return rate
        except Exception as e:
            print(f"     ⚠️ Yahoo Finance failed: {str(e)[:50]}...")
        
        # Source 2: ExchangeRate-API (free tier)
        try:
            if '_' in pair_name:
                base, quote = pair_name.split('_')
                url = f"https://api.exchangerate-api.com/v4/latest/{base}"
                
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if quote in data.get('rates', {}):
                        rate = float(data['rates'][quote])
                        print(f"     🎯 ExchangeRate-API: {rate:.4f}")
                        return rate
        except Exception as e:
            print(f"     ⚠️ ExchangeRate-API failed: {str(e)[:50]}...")
        
        # Source 3: CurrencyAPI (optional free/paid key)
        try:
            currency_api_key = os.getenv('CURRENCY_API_KEY')
            if currency_api_key and '_' in pair_name:
                base, quote = pair_name.split('_')
                url = f"https://api.currencyapi.com/v3/latest"
                params = {
                    'apikey': currency_api_key,
                    'base_currency': base,
                    'currencies': quote
                }
                
                response = requests.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    rates = data.get('data', {})
                    if quote in rates:
                        rate = float(rates[quote]['value'])
                        print(f"     🎯 CurrencyAPI: {rate:.4f}")
                        return rate
            elif not currency_api_key:
                print("     ℹ️ CurrencyAPI skipped: CURRENCY_API_KEY not configured")
        except Exception as e:
            print(f"     ⚠️ CurrencyAPI failed: {str(e)[:50]}...")
        
        return None
    
    def _update_fx_historical_csv(self, pair_name: str, rate: float):
        """Update local historical CSV files."""
        try:
            # Convert pair name to match the CSV filename format.
            csv_name = pair_name.replace('_', '/') + " Historical Data.csv"
            csv_path = os.path.join(self.fx_dir, csv_name)
            
            # Create a new row in the expected CSV format.
            now = datetime.now()
            new_row = {
                'Date': now.strftime('%m/%d/%Y'),
                'Price': f"{rate:.4f}",
                'Open': f"{rate:.4f}",
                'High': f"{rate:.4f}",
                'Low': f"{rate:.4f}",
                'Vol.': "",
                'Change %': "0.00%"
            }
            
            # Calculate change % from previous day
            if os.path.exists(csv_path):
                existing_df = pd.read_csv(csv_path)
                if not existing_df.empty:
                    prev_price = float(existing_df.iloc[0]['Price'])
                    change_pct = ((rate - prev_price) / prev_price) * 100
                    new_row['Change %'] = f"{change_pct:+.2f}%"
                
                # Add new row at top with most recent data first.
                updated_df = pd.concat([pd.DataFrame([new_row]), existing_df], ignore_index=True)
            else:
                updated_df = pd.DataFrame([new_row])
            
            # Save updated CSV
            updated_df.to_csv(csv_path, index=False)
            
        except Exception as e:
            print(f"     ❌ CSV update failed: {e}")
    
    def get_enhanced_news_data(self):
        """Enhanced news collection using free RSS feeds and optional NewsAPI."""
        print(f"\n📰 Collecting enhanced news at {datetime.now().strftime('%H:%M:%S')}")
        
        all_articles = []
        
        # Method 1: Free RSS feeds (unlimited)
        rss_articles = self._get_rss_news()
        all_articles.extend(rss_articles)
        print(f"   📡 RSS feeds: {len(rss_articles)} articles")
        
        # Method 2: Optional NewsAPI with smart rate limiting
        try:
            api_articles = self._get_smart_newsapi()
            all_articles.extend(api_articles)
            print(f"   🔑 NewsAPI: {len(api_articles)} articles")
        except Exception as e:
            print(f"   ⚠️ NewsAPI limited: {str(e)[:50]}...")
        
        # Process and update news_log.csv
        if all_articles:
            processed = self._process_news_for_local_csv(all_articles)
            print(f"   ✅ Saved {len(processed)} articles to news_log.csv")
    
    def _get_rss_news(self) -> List[Dict]:
        """Get news from free RSS feeds"""
        articles = []
        
        # Free RSS feeds (no rate limits)
        feeds = {
            'reuters': 'http://feeds.reuters.com/reuters/businessNews',
            'bbc': 'http://feeds.bbci.co.uk/news/business/rss.xml',
            'cnbc': 'https://www.cnbc.com/id/100727362/device/rss/rss.html'
        }
        
        for source, url in feeds.items():
            try:
                # Simple RSS parsing without external libraries
                response = requests.get(url, timeout=15)
                if response.status_code == 200:
                    # Basic XML parsing for RSS
                    content = response.text
                    
                    # Extract titles using simple string operations
                    titles = []
                    lines = content.split('\n')
                    for line in lines:
                        if '<title>' in line and '</title>' in line:
                            start = line.find('<title>') + 7
                            end = line.find('</title>')
                            if start > 6 and end > start:
                                title = line[start:end].strip()
                                if len(title) > 10 and 'RSS' not in title:
                                    titles.append(title)
                    
                    # Take latest 5 titles from each source
                    for title in titles[:5]:
                        articles.append({
                            'title': title,
                            'source': source,
                            'published': datetime.now().strftime('%Y-%m-%d'),
                            'url': url
                        })
                        
            except Exception as e:
                print(f"     ⚠️ RSS {source} failed: {str(e)[:30]}...")
        
        return articles
    
    def _get_smart_newsapi(self) -> List[Dict]:
        """Use optional NewsAPI with smart rate limiting."""
        if self.newsapi is None:
            return []

        articles = []
        
        # Rotate queries to maximize coverage within daily limits
        queries = [
            'currency exchange OR forex',
            'Federal Reserve OR interest rates',
            'Ukraine economy OR hryvnia',
            'inflation OR central bank'
        ]
        
        # Use different query each hour to spread usage
        query_index = datetime.now().hour % len(queries)
        query = queries[query_index]
        
        try:
            response = self.newsapi.get_everything(
                q=query,
                language='en',
                sort_by='publishedAt',
                page_size=10  # Small size to conserve quota
            )
            
            for article in response.get('articles', []):
                articles.append({
                    'title': article.get('title', ''),
                    'source': f"api_{article.get('source', {}).get('name', 'unknown')}",
                    'published': article.get('publishedAt', ''),
                    'url': article.get('url', '')
                })
                
        except Exception as e:
            print(f"     ⚠️ NewsAPI error: {str(e)[:50]}...")
        
        return articles
    
    def _process_news_for_local_csv(self, articles: List[Dict]) -> List[Dict]:
        """Process news using local sentiment and region classification."""
        processed = []
        
        for article in articles:
            title = article.get('title', '')
            if len(title) < 10:
                continue
            
            # Use the project region classification logic
            region = self._classify_region_for_project(title)
            if not region:
                continue
            
            # Calculate headline sentiment for the local CSV schema
            sentiment = self.analyzer.polarity_scores(title)['compound']
            
            processed.append({
                'Date': datetime.now().strftime('%Y-%m-%d'),
                'Region': region,
                'Headline': title,
                'Sentiment': sentiment
            })
        
        # Update news_log.csv in the expected format
        if processed:
            self._update_local_news_csv(processed)
        
        return processed
    
    def _classify_region_for_project(self, text: str) -> Optional[str]:
        """Use the project region classification logic."""
        text = text.lower()
        
        # Keywords adapted from process_headlines_real.py
        if any(w in text for w in ["fed", "us", "dollar", "powell", "america"]):
            return "USD"
        elif any(w in text for w in ["euro", "ecb", "eu", "germany", "france", "europa"]):
            return "EUR"
        elif any(w in text for w in ["ukraine", "zelensky", "hryvnia", "kyiv"]):
            return "UAH"
        
        return None
    
    def _update_local_news_csv(self, news_items: List[Dict]):
        """Update the local news_log.csv file."""
        try:
            news_csv = os.path.join(self.log_dir, 'news_log.csv')
            
            new_df = pd.DataFrame(news_items)
            
            if os.path.exists(news_csv):
                existing_df = pd.read_csv(news_csv)
                combined_df = pd.concat([new_df, existing_df], ignore_index=True)
                
                # Remove duplicates by headline
                combined_df.drop_duplicates(subset=['Headline'], inplace=True)
                
                # Keep reasonable size (last 20,000 entries)
                if len(combined_df) > 20000:
                    combined_df = combined_df.head(20000)
            else:
                combined_df = new_df
            
            # Save in the expected format.
            combined_df[['Date', 'Region', 'Headline', 'Sentiment']].to_csv(news_csv, index=False)
            
        except Exception as e:
            print(f"     ❌ News CSV update failed: {e}")
    
    def get_real_time_macro_data(self):
        """Get real-time macro data to update local CSV files."""
        print(f"\n📊 Collecting macro data at {datetime.now().strftime('%H:%M:%S')}")
        
        # Get Treasury yields
        treasury_data = self._get_live_treasury_yields()
        
        # Get Fed Funds estimate
        fed_data = self._get_fed_funds_estimate()
        
        # Update local macro CSV files.
        all_macro = {**treasury_data, **fed_data}
        if all_macro:
            self._update_local_macro_csvs(all_macro)
            print(f"   ✅ Updated {len(all_macro)} macro indicators")
    
    def _get_live_treasury_yields(self) -> Dict:
        """Get live Treasury yields"""
        yields = {}
        
        treasury_symbols = {
            '^TNX': 'US_10Y_Treasury',
            '^FVX': 'US_5Y_Treasury'
        }
        
        for symbol, name in treasury_symbols.items():
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period='1d')
                
                if not hist.empty:
                    current_yield = float(hist['Close'].iloc[-1])
                    yields[name] = {
                        'date': datetime.now().strftime('%Y-%m-%d'),
                        'value': current_yield
                    }
                    print(f"   📈 {name}: {current_yield:.2f}%")
                    
            except Exception as e:
                print(f"   ⚠️ {name} failed: {str(e)[:30]}...")
        
        return yields
    
    def _get_fed_funds_estimate(self) -> Dict:
        """Get current Fed Funds rate estimate"""
        fed_data = {}
        
        try:
            # Method 1: Try to get from Fed Funds futures
            ticker = yf.Ticker('ZQ=F')  # Fed Funds futures
            hist = ticker.history(period='1d')
            
            if not hist.empty:
                # Fed Funds futures price converts to rate
                futures_price = float(hist['Close'].iloc[-1])
                fed_rate = 100 - futures_price  # Approximate conversion
                
                fed_data['US_FedFunds'] = {
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'value': fed_rate
                }
                print(f"   🏦 Fed Funds (est): {fed_rate:.2f}%")
            else:
                print("   ℹ️ Fed Funds unavailable from free futures proxy")
                
        except Exception as e:
            print(f"   ⚠️ Fed Funds failed: {str(e)[:30]}...")
        
        return fed_data
    
    def _update_local_macro_csvs(self, macro_data: Dict):
        """Update local macro CSV files."""
        try:
            for indicator, data in macro_data.items():
                csv_path = os.path.join(self.macro_dir, f"{indicator}.csv")
                
                # Create new row
                new_row = {
                    'date': data['date'],
                    indicator: data['value']
                }
                
                # Update CSV in the expected format
                if os.path.exists(csv_path):
                    existing_df = pd.read_csv(csv_path)
                    updated_df = pd.concat([pd.DataFrame([new_row]), existing_df], ignore_index=True)
                else:
                    updated_df = pd.DataFrame([new_row])
                
                updated_df.to_csv(csv_path, index=False)
                
        except Exception as e:
            print(f"   ❌ Macro CSV update failed: {e}")
    
    def run_enhanced_collection(self, mode='once'):
        """Run the enhanced data collection"""
        
        if mode == 'once':
            print("\n🔄 Running ENHANCED single collection...")
            print("=" * 60)
            
            # Run all collections
            self.get_multi_source_fx_data()
            time.sleep(1)
            self.get_enhanced_news_data()
            time.sleep(1) 
            self.get_real_time_macro_data()
            
            print("\n✅ Enhanced collection completed!")
            print("📁 Check local CSV files for newly collected data.")
            
        elif mode == 'auto':
            print("\n🔄 Starting CONTINUOUS enhanced collection...")
            print("=" * 60)
            print("⏰ Schedule:")
            print("   💱 FX: Every 3 minutes")
            print("   📰 News: Every 15 minutes")
            print("   📊 Macro: Every 1 hour")
            print("   🛑 Press Ctrl+C to stop")
            print("=" * 60)
            
            self.running = True
            
            # Run initial collection
            self.get_multi_source_fx_data()
            self.get_enhanced_news_data()
            self.get_real_time_macro_data()
            
            # Schedule future collections
            fx_interval = 180    # 3 minutes
            news_interval = 900  # 15 minutes  
            macro_interval = 3600 # 1 hour
            
            last_fx = time.time()
            last_news = time.time()
            last_macro = time.time()
            
            try:
                while self.running:
                    current_time = time.time()
                    
                    # Check if it's time for each collection
                    if current_time - last_fx >= fx_interval:
                        self.get_multi_source_fx_data()
                        last_fx = current_time
                    
                    if current_time - last_news >= news_interval:
                        self.get_enhanced_news_data()
                        last_news = current_time
                    
                    if current_time - last_macro >= macro_interval:
                        self.get_real_time_macro_data()
                        last_macro = current_time
                    
                    time.sleep(10)  # Check every 10 seconds
                    
            except KeyboardInterrupt:
                print("\n🛑 Stopping enhanced scraper...")
                self.running = False
                print("✅ Enhanced scraper stopped")

def main():
    """Main function"""
    scraper = SimpleEnhancedScraper()
    
    print("ENHANCED AUTO-SCRAPER FOR CARRY TRADE MODEL")
    print("=" * 60)
    print("This collects configured real data with:")
    print("✅ Multi-source FX rates (3+ sources per pair)")
    print("✅ Enhanced news (free RSS + optional NewsAPI)")
    print("✅ Real-time macro data (Treasury yields, Fed Funds)")
    print("✅ Automatic fallbacks and error handling")
    print("✅ Updates local CSV files")
    print("=" * 60)
    
    # Check command line arguments
    if len(sys.argv) > 1:
        if '--once' in sys.argv:
            scraper.run_enhanced_collection('once')
        elif '--auto' in sys.argv:
            scraper.run_enhanced_collection('auto')
        else:
            print("Usage: python enhanced_scraper_simple.py [--once|--auto]")
    else:
        # Interactive mode
        mode = input("\nChoose mode:\n1. Test run (collect once)\n2. Continuous (keep running)\nEnter 1 or 2: ").strip()
        
        if mode == "1":
            scraper.run_enhanced_collection('once')
        elif mode == "2":
            scraper.run_enhanced_collection('auto')
        else:
            print("Invalid choice. Running test mode...")
            scraper.run_enhanced_collection('once')

if __name__ == "__main__":
    main()
