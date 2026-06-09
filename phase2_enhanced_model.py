"""
Phase 2 Enhanced Carry Trade Model
==================================

This module implements advanced improvements including:
1. Risk Management Framework
2. Advanced Feature Engineering  
3. Data Infrastructure
4. Advanced Model Architectures
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Core ML libraries
from sklearn.model_selection import TimeSeriesSplit
from sklearn.ensemble import StackingRegressor, RandomForestRegressor
from sklearn.preprocessing import RobustScaler
from sklearn.feature_selection import SelectKBest, f_regression
from sklearn.linear_model import Ridge, RidgeCV
from sklearn.metrics import mean_squared_error, r2_score
import lightgbm as lgb
import xgboost as xgb

# Advanced ML for Phase 2
from sklearn.neural_network import MLPRegressor
from sklearn.ensemble import VotingRegressor
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans

# Risk management
from scipy import stats
from scipy.optimize import minimize

class Phase2EnhancedModel:
    """Enhanced carry trade model with Phase 2 improvements"""
    
    def __init__(self, risk_tolerance=0.05, max_positions=3):
        """
        Initialize enhanced model with risk management
        
        Args:
            risk_tolerance: Maximum acceptable VaR (default 5%)
            max_positions: Maximum number of concurrent positions
        """
        self.risk_tolerance = risk_tolerance
        self.max_positions = max_positions
        
        # Model components
        self.models = {}
        self.scalers = {}
        self.feature_selectors = {}
        self.selected_features = []
        
        # Risk management components
        self.position_sizes = {}
        self.stop_losses = {}
        self.take_profits = {}
        self.risk_metrics = {}
        
        # Advanced features
        self.regime_detector = None
        self.stress_indicators = {}
        
        print("📈 Phase 2 Enhanced Model initialized with risk management")
        
    def load_and_prepare_data(self):
        """Load and prepare data with enhanced validation"""
        try:
            # Load data files
            fx_data = pd.read_csv('logs/fx/fx_log.csv')
            macro_data = pd.read_csv('logs/macro/macro_log.csv')
            sentiment_data = pd.read_csv('logs/news_log.csv')
            
            # Convert dates
            fx_data['date'] = pd.to_datetime(fx_data['date'])
            macro_data['date'] = pd.to_datetime(macro_data['date'])
            sentiment_data['date'] = pd.to_datetime(sentiment_data['date'])
            
            # Aggregate sentiment by date (pivot and average)
            sentiment_pivot = sentiment_data.pivot_table(
                index='date', 
                columns='Region', 
                values='Sentiment', 
                aggfunc='mean'
            ).reset_index()
            
            # Flatten column names
            sentiment_pivot.columns = ['date'] + [f'Sentiment_{col}' for col in sentiment_pivot.columns[1:]]
            
            # Merge all data
            data = fx_data.merge(macro_data, on='date', how='inner')
            data = data.merge(sentiment_pivot, on='date', how='left')
            
            # Fill any remaining NaN values
            data = data.ffill().bfill()
            
            # Data quality validation
            if len(data) < 100:
                raise ValueError(f"Insufficient data: {len(data)} rows (need 100+)")
                
            print(f"✅ Enhanced data loaded: {data.shape}")
            return data
            
        except Exception as e:
            print(f"❌ Enhanced data loading failed: {e}")
            return None
    
    def detect_market_regimes(self, data):
        """Detect market regimes using clustering"""
        print("🔍 Detecting market regimes...")
        
        # Calculate regime features
        regime_features = []
        
        # Volatility regime
        for currency in ['USD_UAH', 'EUR_UAH']:
            if currency in data.columns:
                returns = data[currency].pct_change().rolling(20).std()
                regime_features.append(returns)
        
        # Interest rate regime  
        if 'US_FedFunds' in data.columns and 'EU_Rate' in data.columns:
            rate_spread = data['US_FedFunds'] - data['EU_Rate']
            regime_features.append(rate_spread)
            
        # Create regime matrix
        regime_matrix = pd.concat(regime_features, axis=1).fillna(0)
        
        # Convert to numpy array to avoid sklearn column name issues
        regime_array = regime_matrix.values
        
        # Use KMeans clustering for regime detection
        self.regime_detector = KMeans(n_clusters=3, random_state=42)
        regimes = self.regime_detector.fit_predict(regime_array)
        
        # Add regime labels
        data['market_regime'] = regimes
        data['regime_volatility'] = regime_matrix.iloc[:, 0] if len(regime_matrix.columns) > 0 else 0
        data['regime_rates'] = regime_matrix.iloc[:, -1] if len(regime_matrix.columns) > 1 else 0
        
        print(f"✅ Market regimes detected: {len(np.unique(regimes))} regimes")
        return data
    
    def calculate_stress_indicators(self, data):
        """Calculate market stress indicators"""
        print("⚠️ Calculating stress indicators...")
        
        stress_indicators = {}
        
        # VIX-like volatility stress
        for currency in ['USD_UAH', 'EUR_UAH']:
            if currency in data.columns:
                returns = data[currency].pct_change()
                vol_stress = returns.rolling(20).std() / returns.rolling(60).std()
                stress_indicators[f'{currency}_vol_stress'] = vol_stress
        
        # Interest rate stress
        if 'US_FedFunds' in data.columns:
            rate_change = data['US_FedFunds'].diff().abs()
            rate_stress = rate_change.rolling(10).mean()
            stress_indicators['rate_stress'] = rate_stress
            
        # Sentiment stress
        sentiment_cols = [col for col in data.columns if 'Sentiment_' in col]
        if sentiment_cols:
            sentiment_vol = data[sentiment_cols].std(axis=1)
            stress_indicators['sentiment_stress'] = sentiment_vol
        
        # Add stress indicators to data
        for name, indicator in stress_indicators.items():
            data[name] = indicator.fillna(0)
            
        self.stress_indicators = stress_indicators
        print(f"✅ Calculated {len(stress_indicators)} stress indicators")
        return data
    
    def advanced_feature_engineering(self, data):
        """Enhanced feature engineering with regime and stress features"""
        print("🔬 Advanced feature engineering...")
        
        # Start with regime detection and stress indicators
        data = self.detect_market_regimes(data)
        data = self.calculate_stress_indicators(data)
        
        features = {}
        feature_names = []
        
        # Basic features (from Phase 1)
        for col in data.columns:
            if col not in ['date']:
                features[col] = data[col].values
                feature_names.append(col)
        
        # Advanced technical indicators
        for currency in ['USD_UAH', 'EUR_UAH']:
            if currency in data.columns:
                prices = data[currency]
                
                # Multiple timeframe analysis
                for window in [5, 10, 20, 50]:
                    # Moving averages
                    sma = prices.rolling(window).mean()
                    features[f'{currency}_sma_{window}'] = sma.values
                    feature_names.append(f'{currency}_sma_{window}')
                    
                    # Bollinger Bands
                    std = prices.rolling(window).std()
                    bb_upper = sma + (2 * std)
                    bb_lower = sma - (2 * std)
                    bb_position = (prices - bb_lower) / (bb_upper - bb_lower)
                    features[f'{currency}_bb_position_{window}'] = bb_position.values
                    feature_names.append(f'{currency}_bb_position_{window}')
                
                # Momentum indicators
                returns = prices.pct_change()
                
                # RSI with multiple periods
                for period in [14, 30]:
                    rsi = self.calculate_rsi(prices, period)
                    features[f'{currency}_rsi_{period}'] = rsi.values
                    feature_names.append(f'{currency}_rsi_{period}')
                
                # MACD
                macd, macd_signal = self.calculate_macd(prices)
                features[f'{currency}_macd'] = macd.values
                features[f'{currency}_macd_signal'] = macd_signal.values
                feature_names.extend([f'{currency}_macd', f'{currency}_macd_signal'])
                
                # Volatility features
                for window in [10, 20, 30]:
                    vol = returns.rolling(window).std()
                    features[f'{currency}_volatility_{window}'] = vol.values
                    feature_names.append(f'{currency}_volatility_{window}')
        
        # Cross-asset correlations
        currency_cols = [col for col in data.columns if 'UAH' in col]
        if len(currency_cols) >= 2:
            for window in [20, 60]:
                corr = data[currency_cols[0]].rolling(window).corr(data[currency_cols[1]])
                features[f'currency_correlation_{window}'] = corr.values
                feature_names.append(f'currency_correlation_{window}')
        
        # Interest rate differentials and derived features
        if 'US_FedFunds' in data.columns and 'EU_Rate' in data.columns and 'UAH_Rate' in data.columns:
            # Multiple rate differentials
            features['usd_uah_rate_diff'] = (data['US_FedFunds'] - data['UAH_Rate']).values
            features['eur_uah_rate_diff'] = (data['EU_Rate'] - data['UAH_Rate']).values
            features['usd_eur_rate_diff'] = (data['US_FedFunds'] - data['EU_Rate']).values
            feature_names.extend(['usd_uah_rate_diff', 'eur_uah_rate_diff', 'usd_eur_rate_diff'])
            
            # Rate momentum
            for rate in ['US_FedFunds', 'EU_Rate', 'UAH_Rate']:
                rate_momentum = data[rate].diff(5)  # 5-day momentum
                features[f'{rate}_momentum'] = rate_momentum.values
                feature_names.append(f'{rate}_momentum')
        
        # Economic indicators
        if 'US_CPI' in data.columns:
            cpi_change = data['US_CPI'].pct_change(12)  # YoY inflation
            features['inflation_change'] = cpi_change.values
            feature_names.append('inflation_change')
            
        if 'US_YieldCurve' in data.columns:
            yield_momentum = data['US_YieldCurve'].diff(10)
            features['yield_curve_momentum'] = yield_momentum.values
            feature_names.append('yield_curve_momentum')
        
        # Sentiment features
        sentiment_cols = [col for col in data.columns if 'Sentiment_' in col]
        if sentiment_cols:
            # Sentiment momentum
            for col in sentiment_cols:
                momentum = data[col].diff(5)
                features[f'{col}_momentum'] = momentum.values
                feature_names.append(f'{col}_momentum')
            
            # Sentiment spread
            if len(sentiment_cols) >= 2:
                sentiment_spread = data[sentiment_cols[0]] - data[sentiment_cols[1]]
                features['sentiment_spread'] = sentiment_spread.values
                feature_names.append('sentiment_spread')
        
        # Create feature matrix
        feature_matrix = pd.DataFrame(features)
        feature_matrix = feature_matrix.ffill().fillna(0)
        
        print(f"✅ Advanced features created: {len(feature_names)} features")
        return feature_matrix, feature_names
    
    def calculate_rsi(self, prices, period=14):
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_macd(self, prices, fast=12, slow=26, signal=9):
        """Calculate MACD indicator"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        macd_signal = macd.ewm(span=signal).mean()
        return macd, macd_signal
    
    def prepare_features_and_targets(self, data):
        """Prepare features and targets with advanced engineering"""
        # Advanced feature engineering
        X, feature_names = self.advanced_feature_engineering(data)
        
        # Create targets (next day returns)
        y_usd = data['USD_UAH'].pct_change().shift(-1)
        y_eur = data['EUR_UAH'].pct_change().shift(-1)
        dates = data['date']
        
        # Remove last row (no target available)
        X = X[:-1]
        y_usd = y_usd[:-1]
        y_eur = y_eur[:-1]
        dates = dates[:-1]
        
        # Remove any remaining NaN values
        valid_idx = ~(np.isnan(y_usd) | np.isnan(y_eur) | np.isnan(X).any(axis=1))
        X = X[valid_idx]
        y_usd = y_usd[valid_idx]
        y_eur = y_eur[valid_idx]
        dates = dates[valid_idx]
        
        print(f"✅ Advanced features and targets prepared: {X.shape}")
        return X, y_usd, y_eur, dates, feature_names
    
    def calculate_position_size(self, predictions, confidence_intervals, currency):
        """Calculate position size based on Kelly Criterion and risk management"""
        pred = predictions[f'{currency}_predictions']
        ci = confidence_intervals[f'{currency}_confidence_intervals']
        
        # Calculate expected return and volatility
        expected_return = np.mean(pred)
        volatility = np.std(pred)
        
        # Kelly Criterion for position sizing
        if volatility > 0:
            # Win probability (assume 50% base, adjust for confidence)
            ci_width = np.mean(ci[:, 1] - ci[:, 0])
            confidence_adj = max(0.4, min(0.6, 0.5 + (0.1 / ci_width) if ci_width > 0 else 0.5))
            
            # Kelly fraction
            kelly_fraction = (confidence_adj * expected_return) / (volatility ** 2)
            
            # Apply risk constraints
            max_position = 0.25  # Maximum 25% of capital per position
            kelly_fraction = max(-max_position, min(max_position, kelly_fraction))
        else:
            kelly_fraction = 0.0
        
        # Apply additional risk adjustments
        if currency in self.stress_indicators:
            stress_level = np.mean(list(self.stress_indicators.values()))
            kelly_fraction *= (1 - min(0.5, stress_level))  # Reduce position in high stress
        
        self.position_sizes[currency] = kelly_fraction
        return kelly_fraction
    
    def calculate_stop_loss_take_profit(self, predictions, confidence_intervals, currency):
        """Calculate dynamic stop-loss and take-profit levels"""
        pred = predictions[f'{currency}_predictions']
        ci = confidence_intervals[f'{currency}_confidence_intervals']
        
        # Calculate volatility-based stops
        volatility = np.std(pred)
        
        # Stop-loss: 2x volatility or lower confidence bound
        stop_loss = max(2 * volatility, np.mean(ci[:, 0] - pred))
        
        # Take-profit: 3x volatility or upper confidence bound  
        take_profit = min(3 * volatility, np.mean(ci[:, 1] - pred))
        
        self.stop_losses[currency] = abs(stop_loss)
        self.take_profits[currency] = abs(take_profit)
        
        return abs(stop_loss), abs(take_profit)
    
    def calculate_portfolio_risk_metrics(self, predictions, confidence_intervals):
        """Calculate comprehensive portfolio risk metrics"""
        metrics = {}
        
        # Value at Risk (VaR) calculation
        all_predictions = []
        for currency in ['usd', 'eur']:
            if f'{currency}_predictions' in predictions:
                preds = predictions[f'{currency}_predictions']
                position_size = self.position_sizes.get(currency, 0)
                all_predictions.extend(preds * position_size)
        
        if all_predictions:
            portfolio_returns = np.array(all_predictions)
            var_95 = np.percentile(portfolio_returns, 5)
            var_99 = np.percentile(portfolio_returns, 1)
            
            metrics['VaR_95'] = abs(var_95)
            metrics['VaR_99'] = abs(var_99)
            metrics['expected_return'] = np.mean(portfolio_returns)
            metrics['volatility'] = np.std(portfolio_returns)
            
            # Sharpe ratio (assuming risk-free rate of 3%)
            risk_free_rate = 0.03 / 252  # Daily risk-free rate
            if metrics['volatility'] > 0:
                metrics['sharpe_ratio'] = (metrics['expected_return'] - risk_free_rate) / metrics['volatility']
            else:
                metrics['sharpe_ratio'] = 0
                
            # Maximum drawdown (simplified)
            cumulative_returns = np.cumsum(portfolio_returns)
            running_max = np.maximum.accumulate(cumulative_returns)
            drawdown = cumulative_returns - running_max
            metrics['max_drawdown'] = abs(np.min(drawdown))
        
        self.risk_metrics = metrics
        return metrics
    
    def build_advanced_ensemble(self):
        """Build advanced ensemble with neural networks and voting"""
        base_models = [
            ('rf', RandomForestRegressor(n_estimators=50, random_state=42)),
            ('xgb', xgb.XGBRegressor(n_estimators=50, random_state=42, verbosity=0)),
            ('lgb', lgb.LGBMRegressor(n_estimators=50, random_state=42, verbosity=-1)),
            ('mlp', MLPRegressor(hidden_layer_sizes=(50,), random_state=42, max_iter=200))
        ]
        
        # Create stacking ensemble with simple CV split
        stacking_model = StackingRegressor(
            estimators=base_models,
            final_estimator=RidgeCV(alphas=np.logspace(-8, 2, 30)),
            cv=3  # Use simple integer instead of TimeSeriesSplit for training
        )
        
        return stacking_model
    
    def train_advanced_models(self, X, y_usd, y_eur, feature_names):
        """Train advanced models with enhanced architecture"""
        print("🚀 Training advanced ensemble models...")
        
        # Feature selection
        selector_usd = SelectKBest(f_regression, k=min(30, X.shape[1]))
        selector_eur = SelectKBest(f_regression, k=min(30, X.shape[1]))
        
        X_selected_usd = selector_usd.fit_transform(X, y_usd)
        X_selected_eur = selector_eur.fit_transform(X, y_eur)
        
        # Get selected feature names
        selected_features_usd = [feature_names[i] for i in selector_usd.get_support(indices=True)]
        selected_features_eur = [feature_names[i] for i in selector_eur.get_support(indices=True)]
        
        # Robust scaling
        scaler_usd = RobustScaler()
        scaler_eur = RobustScaler()
        
        X_scaled_usd = scaler_usd.fit_transform(X_selected_usd)
        X_scaled_eur = scaler_eur.fit_transform(X_selected_eur)
        
        # Build and train advanced models
        model_usd = self.build_advanced_ensemble()
        model_eur = self.build_advanced_ensemble()
        
        model_usd.fit(X_scaled_usd, y_usd)
        model_eur.fit(X_scaled_eur, y_eur)
        
        # Store models and preprocessors
        self.models = {'usd': model_usd, 'eur': model_eur}
        self.scalers = {'usd': scaler_usd, 'eur': scaler_eur}
        self.feature_selectors = {'usd': selector_usd, 'eur': selector_eur}
        self.selected_features = {
            'usd': selected_features_usd,
            'eur': selected_features_eur
        }
        
        print(f"✅ Advanced models trained successfully")
        print(f"   USD features: {len(selected_features_usd)}")
        print(f"   EUR features: {len(selected_features_eur)}")
        
        return self.selected_features
    
    def predict_with_risk_management(self, X):
        """Generate predictions with comprehensive risk management"""
        predictions = {}
        
        for currency in ['usd', 'eur']:
            if currency in self.models:
                # Prepare features
                X_selected = self.feature_selectors[currency].transform(X)
                X_scaled = self.scalers[currency].transform(X_selected)
                
                # Generate predictions
                pred = self.models[currency].predict(X_scaled)
                predictions[f'{currency}_predictions'] = pred
                
                # Bootstrap confidence intervals
                n_bootstrap = 100
                bootstrap_preds = []
                
                for _ in range(n_bootstrap):
                    # Bootstrap sample
                    indices = np.random.choice(len(X_scaled), size=len(X_scaled), replace=True)
                    X_bootstrap = X_scaled[indices]
                    pred_bootstrap = self.models[currency].predict(X_bootstrap)
                    bootstrap_preds.append(pred_bootstrap)
                
                # Calculate confidence intervals
                bootstrap_preds = np.array(bootstrap_preds)
                ci_lower = np.percentile(bootstrap_preds, 2.5, axis=0)
                ci_upper = np.percentile(bootstrap_preds, 97.5, axis=0)
                
                predictions[f'{currency}_confidence_intervals'] = np.column_stack([ci_lower, ci_upper])
        
        # Calculate risk management components
        for currency in ['usd', 'eur']:
            if f'{currency}_predictions' in predictions:
                # Position sizing
                position_size = self.calculate_position_size(
                    predictions, predictions, currency
                )
                
                # Stop-loss and take-profit
                stop_loss, take_profit = self.calculate_stop_loss_take_profit(
                    predictions, predictions, currency
                )
                
                # Add to predictions
                predictions[f'{currency}_position_size'] = position_size
                predictions[f'{currency}_stop_loss'] = stop_loss
                predictions[f'{currency}_take_profit'] = take_profit
        
        # Portfolio risk metrics
        risk_metrics = self.calculate_portfolio_risk_metrics(predictions, predictions)
        predictions['risk_metrics'] = risk_metrics
        
        return predictions
    
    def time_series_cross_validation(self, X, y_usd, y_eur, dates):
        """Enhanced cross-validation with risk metrics"""
        print("📊 Advanced time series cross-validation...")
        
        tscv = TimeSeriesSplit(n_splits=5)
        
        results = {
            'usd_scores': [],
            'eur_scores': [],
            'risk_metrics': [],
            'position_sizes': []
        }
        
        for fold, (train_idx, test_idx) in enumerate(tscv.split(X)):
            print(f"   Fold {fold + 1}/5...")
            
            # Split data
            X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
            y_usd_train, y_usd_test = y_usd.iloc[train_idx], y_usd.iloc[test_idx]
            y_eur_train, y_eur_test = y_eur.iloc[train_idx], y_eur.iloc[test_idx]
            
            # Train fold-specific models
            selected_features = self.train_advanced_models(X_train, y_usd_train, y_eur_train, X.columns.tolist())
            
            # Generate predictions with risk management
            predictions = self.predict_with_risk_management(X_test)
            
            # Calculate scores
            usd_score = r2_score(y_usd_test, predictions['usd_predictions'])
            eur_score = r2_score(y_eur_test, predictions['eur_predictions'])
            
            results['usd_scores'].append(usd_score)
            results['eur_scores'].append(eur_score)
            results['risk_metrics'].append(predictions.get('risk_metrics', {}))
            
            # Aggregate position sizes
            position_info = {
                'usd_position': predictions.get('usd_position_size', 0),
                'eur_position': predictions.get('eur_position_size', 0)
            }
            results['position_sizes'].append(position_info)
        
        print("✅ Advanced cross-validation completed")
        return results

# Example usage and testing functions
def test_phase2_improvements():
    """Test Phase 2 improvements"""
    print("🧪 Testing Phase 2 Enhanced Model")
    print("=" * 50)
    
    # Initialize enhanced model
    model = Phase2EnhancedModel(risk_tolerance=0.05, max_positions=3)
    
    # Test data loading
    data = model.load_and_prepare_data()
    if data is None:
        print("❌ Data loading failed")
        return False
    
    # Test feature preparation
    X, y_usd, y_eur, dates, feature_names = model.prepare_features_and_targets(data)
    print(f"✅ Advanced features: {X.shape}")
    print(f"   Feature count: {len(feature_names)}")
    
    # Test model training
    if len(X) >= 100:
        selected_features = model.train_advanced_models(X, y_usd, y_eur, feature_names)
        print(f"✅ Advanced models trained")
        
        # Test predictions with risk management
        test_X = X[-10:]
        predictions = model.predict_with_risk_management(test_X)
        
        print(f"✅ Risk-managed predictions generated")
        print(f"   Prediction keys: {list(predictions.keys())}")
        
        # Show risk metrics
        if 'risk_metrics' in predictions:
            print(f"   Portfolio VaR (95%): {predictions['risk_metrics'].get('VaR_95', 0):.4f}")
            print(f"   Expected return: {predictions['risk_metrics'].get('expected_return', 0):.4f}")
            print(f"   Sharpe ratio: {predictions['risk_metrics'].get('sharpe_ratio', 0):.4f}")
        
        return True
    else:
        print("❌ Insufficient data for training")
        return False

if __name__ == "__main__":
    test_phase2_improvements()
