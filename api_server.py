from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import json
import os
from datetime import datetime, timedelta
import numpy as np
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize sentiment analyzer
analyzer = SentimentIntensityAnalyzer()

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGS_DIR = os.path.join(BASE_DIR, 'logs')

def load_fx_data():
    """Load FX rates from log files"""
    try:
        fx_log_path = os.path.join(LOGS_DIR, 'fx', 'fx_log.csv')
        if os.path.exists(fx_log_path):
            df = pd.read_csv(fx_log_path)
            if not df.empty:
                # Get latest rates for each pair
                latest_data = []
                for pair in ['USD/UAH', 'EUR/UAH']:
                    pair_data = df[df['pair'] == pair].tail(1)
                    if not pair_data.empty:
                        row = pair_data.iloc[0]
                        latest_data.append({
                            'pair': pair,
                            'rate': float(row.get('rate', 0)),
                            'change': float(row.get('change', 0)),
                            'changePercent': float(row.get('change_percent', 0)),
                            'timestamp': datetime.now().isoformat()
                        })
                return latest_data
    except Exception as e:
        print(f"Error loading FX data: {e}")
    
    # Return mock data if file doesn't exist
    return [
        {
            'pair': 'USD/UAH',
            'rate': 36.85,
            'change': 0.12,
            'changePercent': 0.33,
            'timestamp': datetime.now().isoformat()
        },
        {
            'pair': 'EUR/UAH',
            'rate': 40.12,
            'change': -0.08,
            'changePercent': -0.20,
            'timestamp': datetime.now().isoformat()
        }
    ]

def load_sentiment_data():
    """Load sentiment data from news logs"""
    try:
        news_log_path = os.path.join(LOGS_DIR, 'news_log.csv')
        if os.path.exists(news_log_path):
            df = pd.read_csv(news_log_path)
            if not df.empty:
                # Get latest sentiment for each region
                sentiment_data = []
                for region in ['USD', 'EUR', 'UAH']:
                    region_data = df[df['region'] == region].tail(1)
                    if not region_data.empty:
                        row = region_data.iloc[0]
                        score = float(row.get('sentiment_score', 0))
                        sentiment_data.append({
                            'region': region,
                            'score': score,
                            'label': 'positive' if score > 0.1 else 'negative' if score < -0.1 else 'neutral',
                            'confidence': float(row.get('confidence', 0.5)),
                            'timestamp': datetime.now().isoformat()
                        })
                return sentiment_data
    except Exception as e:
        print(f"Error loading sentiment data: {e}")
    
    # Return mock data
    return [
        {
            'region': 'USD',
            'score': 0.25,
            'label': 'positive',
            'confidence': 0.75,
            'timestamp': datetime.now().isoformat()
        },
        {
            'region': 'EUR',
            'score': -0.15,
            'label': 'negative',
            'confidence': 0.68,
            'timestamp': datetime.now().isoformat()
        },
        {
            'region': 'UAH',
            'score': 0.05,
            'label': 'neutral',
            'confidence': 0.55,
            'timestamp': datetime.now().isoformat()
        }
    ]

def load_macro_data():
    """Load macro economic data"""
    try:
        macro_data = []
        macro_files = {
            'US Fed Funds': 'US_FedFunds.csv',
            'US CPI': 'US_CPI.csv',
            'US Inflation Expectations': 'US_InflationExpectations.csv',
            'EU Consumer Prices': 'EU_ConsumerPrices.csv'
        }
        
        for indicator_name, filename in macro_files.items():
            file_path = os.path.join(LOGS_DIR, 'macro', filename)
            if os.path.exists(file_path):
                df = pd.read_csv(file_path)
                if not df.empty and len(df) >= 2:
                    latest = df.iloc[-1]
                    previous = df.iloc[-2]
                    value = float(latest.iloc[1]) if len(latest) > 1 else 0
                    prev_value = float(previous.iloc[1]) if len(previous) > 1 else 0
                    macro_data.append({
                        'indicator': indicator_name,
                        'value': value,
                        'previousValue': prev_value,
                        'change': value - prev_value,
                        'timestamp': datetime.now().isoformat()
                    })
        
        if macro_data:
            return macro_data
    except Exception as e:
        print(f"Error loading macro data: {e}")
    
    # Return mock data
    return [
        {
            'indicator': 'US Fed Funds',
            'value': 5.25,
            'previousValue': 5.00,
            'change': 0.25,
            'timestamp': datetime.now().isoformat()
        },
        {
            'indicator': 'US CPI',
            'value': 3.2,
            'previousValue': 3.0,
            'change': 0.2,
            'timestamp': datetime.now().isoformat()
        }
    ]

def load_performance_data():
    """Load performance metrics"""
    try:
        perf_log_path = os.path.join(LOGS_DIR, 'performance_log.csv')
        if os.path.exists(perf_log_path):
            df = pd.read_csv(perf_log_path)
            if not df.empty:
                latest = df.iloc[-1]
                return {
                    'totalReturn': float(latest.get('total_return', 0)),
                    'sharpeRatio': float(latest.get('sharpe_ratio', 0)),
                    'maxDrawdown': float(latest.get('max_drawdown', 0)),
                    'winRate': float(latest.get('win_rate', 0)),
                    'avgDailyReturn': float(latest.get('avg_daily_return', 0)),
                    'volatility': float(latest.get('volatility', 0)),
                    'benchmark': float(latest.get('benchmark', 0)),
                    'timestamp': datetime.now().isoformat()
                }
    except Exception as e:
        print(f"Error loading performance data: {e}")
    
    # Return mock data
    return {
        'totalReturn': 12.5,
        'sharpeRatio': 1.35,
        'maxDrawdown': -8.2,
        'winRate': 65,
        'avgDailyReturn': 0.08,
        'volatility': 12.5,
        'benchmark': 8.2,
        'timestamp': datetime.now().isoformat()
    }

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard_data():
    """Get all dashboard data"""
    try:
        dashboard_data = {
            'fxRates': load_fx_data(),
            'sentiment': load_sentiment_data(),
            'macroData': load_macro_data(),
            'predictions': [
                {
                    'pair': 'USD/UAH',
                    'predictedReturn': 2.5,
                    'confidence': 0.82,
                    'horizon': 30,
                    'timestamp': datetime.now().isoformat()
                },
                {
                    'pair': 'EUR/UAH',
                    'predictedReturn': -1.2,
                    'confidence': 0.75,
                    'horizon': 30,
                    'timestamp': datetime.now().isoformat()
                }
            ],
            'signals': [
                {
                    'pair': 'USD/UAH',
                    'action': 'BUY',
                    'strength': 85,
                    'expectedReturn': 2.5,
                    'risk': 15,
                    'timestamp': datetime.now().isoformat()
                },
                {
                    'pair': 'EUR/UAH',
                    'action': 'HOLD',
                    'strength': 45,
                    'expectedReturn': -1.2,
                    'risk': 25,
                    'timestamp': datetime.now().isoformat()
                }
            ],
            'performance': load_performance_data(),
            'news': [
                {
                    'headline': 'Federal Reserve signals potential rate adjustment',
                    'source': 'Reuters',
                    'sentiment': 0.2,
                    'timestamp': (datetime.now() - timedelta(hours=1)).isoformat(),
                    'region': 'USD'
                },
                {
                    'headline': 'ECB maintains dovish stance on monetary policy',
                    'source': 'Bloomberg',
                    'sentiment': -0.1,
                    'timestamp': (datetime.now() - timedelta(hours=2)).isoformat(),
                    'region': 'EUR'
                }
            ]
        }
        return jsonify(dashboard_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/fx-rates', methods=['GET'])
def get_fx_rates():
    """Get FX rates"""
    return jsonify(load_fx_data())

@app.route('/api/sentiment', methods=['GET'])
def get_sentiment():
    """Get sentiment data"""
    return jsonify(load_sentiment_data())

@app.route('/api/macro', methods=['GET'])
def get_macro():
    """Get macro data"""
    return jsonify(load_macro_data())

@app.route('/api/performance', methods=['GET'])
def get_performance():
    """Get performance metrics"""
    return jsonify(load_performance_data())

@app.route('/api/predictions', methods=['GET'])
def get_predictions():
    """Get model predictions"""
    # This would integrate with your actual model
    predictions = [
        {
            'pair': 'USD/UAH',
            'predictedReturn': np.random.normal(2.0, 1.0),
            'confidence': np.random.uniform(0.6, 0.9),
            'horizon': 30,
            'timestamp': datetime.now().isoformat()
        },
        {
            'pair': 'EUR/UAH',
            'predictedReturn': np.random.normal(-0.5, 1.5),
            'confidence': np.random.uniform(0.5, 0.8),
            'horizon': 30,
            'timestamp': datetime.now().isoformat()
        }
    ]
    return jsonify(predictions)

@app.route('/api/signals', methods=['GET'])
def get_signals():
    """Get trading signals"""
    # This would integrate with your actual trading logic
    signals = [
        {
            'pair': 'USD/UAH',
            'action': np.random.choice(['BUY', 'SELL', 'HOLD']),
            'strength': np.random.randint(30, 100),
            'expectedReturn': np.random.normal(2.0, 2.0),
            'risk': np.random.randint(10, 30),
            'timestamp': datetime.now().isoformat()
        },
        {
            'pair': 'EUR/UAH',
            'action': np.random.choice(['BUY', 'SELL', 'HOLD']),
            'strength': np.random.randint(20, 90),
            'expectedReturn': np.random.normal(-0.5, 2.5),
            'risk': np.random.randint(15, 35),
            'timestamp': datetime.now().isoformat()
        }
    ]
    return jsonify(signals)

@app.route('/api/news', methods=['GET'])
def get_news():
    """Get news headlines"""
    # Load from your news files
    news_data = []
    try:
        news_files = [
            ('cnbc_headlines.csv', 'CNBC'),
            ('reuters_headlines.csv', 'Reuters'),
            ('guardian_headlines.csv', 'Guardian')
        ]
        
        for filename, source in news_files:
            file_path = os.path.join(BASE_DIR, filename)
            if os.path.exists(file_path):
                df = pd.read_csv(file_path)
                for _, row in df.head(5).iterrows():  # Get latest 5 headlines
                    headline = row.get('Headlines', row.get('headline', ''))
                    if headline:
                        sentiment_score = analyzer.polarity_scores(headline)['compound']
                        news_data.append({
                            'headline': headline,
                            'source': source,
                            'sentiment': sentiment_score,
                            'timestamp': datetime.now().isoformat(),
                            'region': 'USD'  # Default, could be improved with NLP
                        })
    except Exception as e:
        print(f"Error loading news data: {e}")
    
    return jsonify(news_data)

@app.route('/api/update-model', methods=['POST'])
def update_model():
    """Trigger model update"""
    try:
        # This would trigger your actual model update process
        # For now, just return success
        return jsonify({
            'status': 'success',
            'message': 'Model update triggered',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

if __name__ == '__main__':
    print(f"Starting Carry Trade API server...")
    print(f"Base directory: {BASE_DIR}")
    print(f"Logs directory: {LOGS_DIR}")
    app.run(debug=True, host='0.0.0.0', port=8000)
