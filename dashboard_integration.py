"""
Dashboard Integration Module
Connects existing carry trade models to the dashboard API
"""

import pandas as pd
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any

class DashboardIntegrator:
    """Integrates carry trade models with dashboard data"""
    
    def __init__(self, base_dir: str = None):
        self.base_dir = base_dir or os.path.dirname(os.path.abspath(__file__))
        self.logs_dir = os.path.join(self.base_dir, 'logs')
        
    def run_model_and_update_logs(self) -> Dict[str, Any]:
        """
        Run the deterministic log-backed model runner and update dashboard logs.
        """
        try:
            from run_live_model import run_ensemble_model

            result = run_ensemble_model(base_dir=self.base_dir)
            return {
                'status': result.get('status', 'error'),
                'timestamp': datetime.now().isoformat(),
                'results': {
                    'fx_rates': self.get_latest_fx_data(),
                    'sentiment': self.get_latest_sentiment_data(),
                    'performance': self.calculate_performance_metrics(),
                    'predictions': self.get_latest_predictions(),
                    'signals': self.get_trading_signals(),
                },
                'model_output': result.get('message', ''),
                'error': result.get('error')
            }

        except Exception as e:
            return {
                'status': 'error',
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def get_latest_fx_data(self) -> Dict[str, Any]:
        """Get latest FX data from local log files."""
        try:
            # Check historical data files
            usd_path = os.path.join(self.logs_dir, 'fx', 'USD_UAH Historical Data.csv')
            eur_path = os.path.join(self.logs_dir, 'fx', 'EUR_UAH Historical Data.csv')
            
            fx_data = {}
            
            if os.path.exists(usd_path):
                df = pd.read_csv(usd_path)
                if not df.empty:
                    latest = df.iloc[-1]
                    fx_data['USD_UAH'] = {
                        'rate': float(latest['Price']),
                        'date': latest['Date'],
                        'pair': 'USD/UAH'
                    }
            
            if os.path.exists(eur_path):
                df = pd.read_csv(eur_path)
                if not df.empty:
                    latest = df.iloc[-1]
                    fx_data['EUR_UAH'] = {
                        'rate': float(latest['Price']),
                        'date': latest['Date'],
                        'pair': 'EUR/UAH'
                    }
            
            return fx_data
            
        except Exception as e:
            print(f"Error loading FX data: {e}")
            return {}
    
    def get_latest_sentiment_data(self) -> Dict[str, Any]:
        """Get latest sentiment data from news logs"""
        try:
            news_path = os.path.join(self.logs_dir, 'news_log.csv')
            if not os.path.exists(news_path):
                return {}
            
            df = pd.read_csv(news_path)
            if df.empty:
                return {}
            
            sentiment_data = {}
            for region in ['USD', 'EUR', 'UAH']:
                region_data = df[df['Region'] == region]
                if not region_data.empty:
                    recent_sentiment = region_data.tail(10)['Sentiment'].mean()
                    sentiment_data[f'{region.lower()}_sentiment'] = float(recent_sentiment)
                    sentiment_data[f'{region.lower()}_confidence'] = min(abs(recent_sentiment) + 0.5, 0.9)
                    sentiment_data[f'{region.lower()}_news_count'] = len(region_data)
            
            return sentiment_data
            
        except Exception as e:
            print(f"Error loading sentiment data: {e}")
            return {}
    
    def calculate_performance_metrics(self) -> Dict[str, Any]:
        """Load performance metrics from the performance log when available."""
        try:
            perf_log_path = os.path.join(self.logs_dir, 'performance_log.csv')
            if os.path.exists(perf_log_path):
                df = pd.read_csv(perf_log_path)
                if not df.empty:
                    latest = df.iloc[-1]
                    return {
                        'total_return': float(latest.get('total_return', 0)),
                        'sharpe_ratio': float(latest.get('sharpe_ratio', 0)),
                        'max_drawdown': float(latest.get('max_drawdown', 0)),
                        'win_rate': float(latest.get('win_rate', 0)),
                        'avg_daily_return': float(latest.get('avg_daily_return', 0)),
                        'volatility': float(latest.get('volatility', 0)),
                        'benchmark': float(latest.get('benchmark', 0))
                    }
            return {}

        except Exception as e:
            print(f"Error loading performance metrics: {e}")
            return {}
    
    def update_fx_logs(self, fx_data: Dict[str, Any]):
        """Update FX rate logs"""
        try:
            fx_log_path = os.path.join(self.logs_dir, 'fx', 'fx_log.csv')
            os.makedirs(os.path.dirname(fx_log_path), exist_ok=True)
            
            # Create new FX log entry
            fx_entry = {
                'timestamp': datetime.now().isoformat(),
                'pair': fx_data.get('pair', 'USD/UAH'),
                'rate': fx_data.get('rate', 0),
                'change': fx_data.get('change', 0),
                'change_percent': fx_data.get('change_percent', 0)
            }
            
            # Append to log file
            df = pd.DataFrame([fx_entry])
            if os.path.exists(fx_log_path):
                existing_df = pd.read_csv(fx_log_path)
                df = pd.concat([existing_df, df], ignore_index=True)
            
            df.to_csv(fx_log_path, index=False)
            
        except Exception as e:
            print(f"Error updating FX logs: {e}")
    
    def update_performance_logs(self, performance_data: Dict[str, Any]):
        """Update performance metrics logs"""
        try:
            perf_log_path = os.path.join(self.logs_dir, 'performance_log.csv')
            os.makedirs(os.path.dirname(perf_log_path), exist_ok=True)
            
            # Create performance log entry
            perf_entry = {
                'timestamp': datetime.now().isoformat(),
                'total_return': performance_data.get('total_return', 0),
                'sharpe_ratio': performance_data.get('sharpe_ratio', 0),
                'max_drawdown': performance_data.get('max_drawdown', 0),
                'win_rate': performance_data.get('win_rate', 0),
                'avg_daily_return': performance_data.get('avg_daily_return', 0),
                'volatility': performance_data.get('volatility', 0),
                'benchmark': performance_data.get('benchmark', 0)
            }
            
            # Append to log file
            df = pd.DataFrame([perf_entry])
            if os.path.exists(perf_log_path):
                existing_df = pd.read_csv(perf_log_path)
                df = pd.concat([existing_df, df], ignore_index=True)
            
            df.to_csv(perf_log_path, index=False)
            
        except Exception as e:
            print(f"Error updating performance logs: {e}")
    
    def update_news_logs(self, sentiment_data: Dict[str, Any]):
        """Update news sentiment logs"""
        try:
            news_log_path = os.path.join(self.logs_dir, 'news_log.csv')
            os.makedirs(os.path.dirname(news_log_path), exist_ok=True)
            
            # Create news log entries for each region
            for region in ['USD', 'EUR', 'UAH']:
                news_entry = {
                    'timestamp': datetime.now().isoformat(),
                    'region': region,
                    'sentiment_score': sentiment_data.get(f'{region.lower()}_sentiment', 0),
                    'confidence': sentiment_data.get(f'{region.lower()}_confidence', 0.5),
                    'news_count': sentiment_data.get(f'{region.lower()}_news_count', 0)
                }
                
                # Append to log file
                df = pd.DataFrame([news_entry])
                if os.path.exists(news_log_path):
                    existing_df = pd.read_csv(news_log_path)
                    df = pd.concat([existing_df, df], ignore_index=True)
                else:
                    df = pd.DataFrame([news_entry])
                
                df.to_csv(news_log_path, index=False)
                
        except Exception as e:
            print(f"Error updating news logs: {e}")
    
    def get_latest_predictions(self) -> List[Dict[str, Any]]:
        """Get latest model predictions from model output files when available."""
        try:
            json_path = os.path.join(self.logs_dir, 'model_predictions.json')
            if os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    predictions = json.load(f)
                return predictions if isinstance(predictions, list) else []

            forecast_path = os.path.join(self.logs_dir, 'forecast_log.csv')
            if os.path.exists(forecast_path):
                df = pd.read_csv(forecast_path)
                if df.empty:
                    return []

                predictions = []
                for _, row in df.tail(20).iterrows():
                    pair = row.get('pair') or row.get('Pair')
                    predicted_return = row.get('predicted_return', row.get('predictedReturn'))
                    if pair is None or predicted_return is None:
                        continue
                    predictions.append({
                        'pair': str(pair),
                        'predicted_return': float(predicted_return),
                        'confidence': float(row.get('confidence', 0)),
                        'horizon': int(row.get('horizon', row.get('horizon_days', 30))),
                        'model': str(row.get('model', 'research_model')),
                        'timestamp': str(row.get('timestamp', datetime.now().isoformat()))
                    })
                return predictions

            return []

        except Exception as e:
            print(f"Error getting predictions: {e}")
            return []
    
    def get_trading_signals(self) -> List[Dict[str, Any]]:
        """Get current trading signals"""
        try:
            signals = []
            predictions = self.get_latest_predictions()
            
            for pred in predictions:
                # Simple signal logic; replace with a project-specific strategy if needed.
                predicted_return = pred['predicted_return']
                confidence = pred['confidence']
                
                if predicted_return > 1.5 and confidence > 0.7:
                    action = 'BUY'
                    strength = min(100, int(confidence * 100 + abs(predicted_return) * 10))
                elif predicted_return < -1.5 and confidence > 0.7:
                    action = 'SELL'
                    strength = min(100, int(confidence * 100 + abs(predicted_return) * 10))
                else:
                    action = 'HOLD'
                    strength = int(confidence * 50)
                
                signals.append({
                    'pair': pred['pair'],
                    'action': action,
                    'strength': strength,
                    'expected_return': predicted_return,
                    'risk': max(5, 100 - strength),
                    'timestamp': datetime.now().isoformat()
                })
            
            return signals
            
        except Exception as e:
            print(f"Error getting trading signals: {e}")
            return []
    
    def cleanup_old_logs(self, days_to_keep: int = 30):
        """Clean up old log entries to prevent files from getting too large"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            log_files = [
                os.path.join(self.logs_dir, 'fx', 'fx_log.csv'),
                os.path.join(self.logs_dir, 'performance_log.csv'),
                os.path.join(self.logs_dir, 'news_log.csv')
            ]
            
            for log_file in log_files:
                if os.path.exists(log_file):
                    df = pd.read_csv(log_file)
                    if 'timestamp' in df.columns:
                        df['timestamp'] = pd.to_datetime(df['timestamp'])
                        df = df[df['timestamp'] >= cutoff_date]
                        df.to_csv(log_file, index=False)
                        
        except Exception as e:
            print(f"Error cleaning up logs: {e}")

def scheduled_model_run():
    """
    Function to be called by local scheduled tasks (cron, task scheduler, etc.).
    This updates all the data that the dashboard displays
    """
    integrator = DashboardIntegrator()
    
    print(f"Running scheduled model update at {datetime.now()}")
    
    # Run model and update logs
    result = integrator.run_model_and_update_logs()
    
    # Cleanup old logs
    integrator.cleanup_old_logs()
    
    print(f"Model update completed: {result['status']}")
    
    return result

if __name__ == "__main__":
    # Run the scheduled model update
    scheduled_model_run()
