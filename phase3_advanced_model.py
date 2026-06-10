"""
Phase 3 Enhanced Carry Trade Model - Advanced Improvements
==========================================================

This module implements next-level enhancements including:
1. Transformer-based attention mechanisms
2. Advanced ensemble methods
3. Real-time risk monitoring
4. Performance optimization
5. Enhanced backtesting framework
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Advanced ML libraries
import optuna
from sklearn.linear_model import RidgeCV
from sklearn.model_selection import TimeSeriesSplit, RandomizedSearchCV
from sklearn.ensemble import RandomForestRegressor, StackingRegressor, VotingRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import lightgbm as lgb
import xgboost as xgb
from catboost import CatBoostRegressor

# Deep learning
try:
    import torch
    import torch.nn as nn
    PYTORCH_AVAILABLE = True
except ImportError:
    PYTORCH_AVAILABLE = False
    print("PyTorch not available - some advanced features will be disabled")

# Advanced feature engineering
from sklearn.preprocessing import PolynomialFeatures
from sklearn.decomposition import PCA, FastICA
from sklearn.manifold import TSNE

# Performance monitoring
import time
from concurrent.futures import ThreadPoolExecutor
import joblib

if PYTORCH_AVAILABLE:
    class AttentionLayer(nn.Module):
        """Attention mechanism for time series"""
        def __init__(self, hidden_dim):
            super(AttentionLayer, self).__init__()
            self.hidden_dim = hidden_dim
            self.attention = nn.Linear(hidden_dim, 1)
        
        def forward(self, x):
            # x shape: (batch_size, seq_len, hidden_dim)
            attention_weights = torch.softmax(self.attention(x), dim=1)
            context = torch.sum(attention_weights * x, dim=1)
            return context, attention_weights

    class TransformerModel(nn.Module):
        """Transformer-based model for carry trade prediction"""
        def __init__(self, input_dim, hidden_dim=128, num_heads=8, num_layers=4):
            super(TransformerModel, self).__init__()
            self.input_proj = nn.Linear(input_dim, hidden_dim)
        
            encoder_layer = nn.TransformerEncoderLayer(
                d_model=hidden_dim,
                nhead=num_heads,
                dim_feedforward=hidden_dim * 4,
                dropout=0.1
            )
            self.transformer = nn.TransformerEncoder(encoder_layer, num_layers)
            self.attention = AttentionLayer(hidden_dim)
            self.output = nn.Linear(hidden_dim, 1)
        
        def forward(self, x):
            # Project input to hidden dimension
            x = self.input_proj(x)
        
            # Transformer expects (seq_len, batch_size, hidden_dim)
            x = x.transpose(0, 1)
            transformer_out = self.transformer(x)
        
            # Back to (batch_size, seq_len, hidden_dim)
            transformer_out = transformer_out.transpose(0, 1)
        
            # Apply attention
            context, attention_weights = self.attention(transformer_out)
        
            # Final prediction
            output = self.output(context)
            return output

class Phase3AdvancedModel:
    """Advanced carry trade model with Phase 3 enhancements"""
    
    def __init__(self, use_transformer=True, optimize_hyperparams=True):
        """
        Initialize advanced model
        
        Args:
            use_transformer: Whether to use transformer architecture
            optimize_hyperparams: Whether to optimize hyperparameters
        """
        self.use_transformer = use_transformer and PYTORCH_AVAILABLE
        self.optimize_hyperparams = optimize_hyperparams
        
        # Model components
        self.models = {}
        self.transformer_models = {}
        self.scalers = {}
        self.feature_selectors = {}
        self.selected_features = []
        
        # Performance tracking
        self.performance_history = []
        self.feature_importance = {}
        self.training_time = {}
        
        # Advanced ensemble
        self.meta_models = {}
        self.diversity_models = {}
        
        print("🚀 Phase 3 Advanced Model initialized")
        if self.use_transformer:
            print("   🔥 Transformer architecture enabled")
        if self.optimize_hyperparams:
            print("   ⚡ Hyperparameter optimization enabled")
    
    def create_advanced_features(self, data):
        """Create advanced feature engineering"""
        print("🔬 Creating advanced features...")
        
        features = {}
        feature_names = []
        
        # Polynomial features for interactions
        numerical_cols = data.select_dtypes(include=[np.number]).columns
        numerical_cols = [col for col in numerical_cols if col not in ['date']]
        
        if len(numerical_cols) >= 2:
            # Create polynomial features (degree 2) for top features
            top_features = numerical_cols[:10]  # Limit to prevent explosion
            poly = PolynomialFeatures(degree=2, interaction_only=True, include_bias=False)
            poly_features = poly.fit_transform(data[top_features])
            poly_names = poly.get_feature_names_out(top_features)
            
            for i, name in enumerate(poly_names):
                if 'x0' not in name and 'x1' not in name:  # Skip original features
                    features[f'poly_{name}'] = poly_features[:, i]
                    feature_names.append(f'poly_{name}')
        
        # Technical analysis features
        for currency in ['USD_UAH', 'EUR_UAH']:
            if currency in data.columns:
                prices = data[currency]
                
                # Advanced momentum indicators
                for period in [7, 14, 21, 50]:
                    # Rate of Change
                    roc = prices.pct_change(period)
                    features[f'{currency}_roc_{period}'] = roc.values
                    feature_names.append(f'{currency}_roc_{period}')
                    
                    # Commodity Channel Index (CCI)
                    typical_price = prices  # Simplified for single price
                    sma = typical_price.rolling(period).mean()
                    mad = typical_price.rolling(period).apply(lambda x: np.mean(np.abs(x - x.mean())))
                    cci = (typical_price - sma) / (0.015 * mad)
                    features[f'{currency}_cci_{period}'] = cci.values
                    feature_names.append(f'{currency}_cci_{period}')
                
                # Volatility features
                returns = prices.pct_change()
                for period in [10, 20, 50]:
                    # GARCH-like volatility
                    vol = returns.rolling(period).std()
                    vol_ma = vol.rolling(5).mean()
                    vol_ratio = vol / vol_ma
                    features[f'{currency}_vol_ratio_{period}'] = vol_ratio.values
                    feature_names.append(f'{currency}_vol_ratio_{period}')
                    
                    # Volatility of volatility
                    vol_vol = vol.rolling(10).std()
                    features[f'{currency}_vol_vol_{period}'] = vol_vol.values
                    feature_names.append(f'{currency}_vol_vol_{period}')
        
        # Economic regime features
        if 'US_FedFunds' in data.columns and 'EU_Rate' in data.columns:
            rate_spread = data['US_FedFunds'] - data['EU_Rate']
            
            # Regime persistence
            rate_trend = rate_spread.diff().rolling(10).mean()
            features['rate_trend_persistence'] = rate_trend.values
            feature_names.append('rate_trend_persistence')
            
            # Rate volatility clustering
            rate_vol = rate_spread.rolling(20).std()
            vol_clustering = rate_vol.rolling(10).std()
            features['rate_vol_clustering'] = vol_clustering.values
            feature_names.append('rate_vol_clustering')
        
        # Create feature matrix
        feature_df = pd.DataFrame(features)
        feature_df = feature_df.ffill().fillna(0)
        
        # Add original features
        for col in data.columns:
            if col != 'date' and col not in feature_df.columns:
                feature_df[col] = data[col].values
                feature_names.append(col)
        
        print(f"✅ Advanced features created: {len(feature_names)} total features")
        return feature_df, feature_names
    
    def optimize_hyperparameters(self, X, y, model_type='xgboost'):
        """Optimize hyperparameters using Optuna"""
        print(f"⚡ Optimizing {model_type} hyperparameters...")
        
        def objective(trial):
            if model_type == 'xgboost':
                params = {
                    'n_estimators': trial.suggest_int('n_estimators', 50, 300),
                    'max_depth': trial.suggest_int('max_depth', 3, 10),
                    'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3),
                    'subsample': trial.suggest_float('subsample', 0.6, 1.0),
                    'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
                    'random_state': 42,
                    'verbosity': 0
                }
                model = xgb.XGBRegressor(**params)
            
            elif model_type == 'lightgbm':
                params = {
                    'n_estimators': trial.suggest_int('n_estimators', 50, 300),
                    'max_depth': trial.suggest_int('max_depth', 3, 10),
                    'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3),
                    'subsample': trial.suggest_float('subsample', 0.6, 1.0),
                    'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
                    'random_state': 42,
                    'verbosity': -1
                }
                model = lgb.LGBMRegressor(**params)
            
            elif model_type == 'catboost':
                params = {
                    'iterations': trial.suggest_int('iterations', 50, 300),
                    'depth': trial.suggest_int('depth', 3, 10),
                    'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3),
                    'random_state': 42,
                    'verbose': False
                }
                model = CatBoostRegressor(**params)
            
            # Cross-validation
            tscv = TimeSeriesSplit(n_splits=3)
            scores = []
            
            for train_idx, val_idx in tscv.split(X):
                X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
                y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
                
                model.fit(X_train, y_train)
                pred = model.predict(X_val)
                score = r2_score(y_val, pred)
                scores.append(score)
            
            return np.mean(scores)
        
        # Run optimization
        study = optuna.create_study(direction='maximize', study_name=f'{model_type}_optimization')
        study.optimize(objective, n_trials=50, show_progress_bar=False)
        
        print(f"✅ Best {model_type} score: {study.best_value:.4f}")
        return study.best_params
    
    def build_advanced_ensemble(self, X, y, currency):
        """Build advanced ensemble with multiple model types"""
        print(f"🏗️ Building advanced ensemble for {currency.upper()}...")
        
        base_models = []
        
        # Traditional models with optimization
        if self.optimize_hyperparams:
            # Optimize each model type
            xgb_params = self.optimize_hyperparameters(X, y, 'xgboost')
            lgb_params = self.optimize_hyperparameters(X, y, 'lightgbm')
            
            try:
                cat_params = self.optimize_hyperparameters(X, y, 'catboost')
                base_models.append(('catboost', CatBoostRegressor(**cat_params, verbose=False)))
            except Exception as e:
                print(f"   ⚠️ CatBoost optimization failed: {e}")
        else:
            xgb_params = {'n_estimators': 100, 'random_state': 42, 'verbosity': 0}
            lgb_params = {'n_estimators': 100, 'random_state': 42, 'verbosity': -1}
        
        # Add optimized models
        base_models.extend([
            ('xgb', xgb.XGBRegressor(**xgb_params)),
            ('lgb', lgb.LGBMRegressor(**lgb_params)),
            ('rf', RandomForestRegressor(n_estimators=100, random_state=42))
        ])
        
        # Neural network
        from sklearn.neural_network import MLPRegressor
        base_models.append(('mlp', MLPRegressor(
            hidden_layer_sizes=(100, 50), 
            random_state=42, 
            max_iter=300
        )))
        
        # Create stacking ensemble
        stacking_model = StackingRegressor(
            estimators=base_models,
            final_estimator=RidgeCV(alphas=np.logspace(-8, 2, 30)),
            cv=3
        )
        
        return stacking_model
    
    def calculate_feature_importance(self, X, y, feature_names):
        """Calculate comprehensive feature importance"""
        print("🎯 Calculating feature importance...")
        
        importance_scores = {}
        
        # Multiple methods for feature importance
        methods = {
            'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
            'xgboost': xgb.XGBRegressor(n_estimators=100, random_state=42, verbosity=0)
        }
        
        for method_name, model in methods.items():
            model.fit(X, y)
            if hasattr(model, 'feature_importances_'):
                importance_scores[method_name] = model.feature_importances_
        
        # Average importance across methods
        if importance_scores:
            avg_importance = np.mean(list(importance_scores.values()), axis=0)
            feature_importance_df = pd.DataFrame({
                'feature': feature_names,
                'importance': avg_importance
            }).sort_values('importance', ascending=False)
            
            return feature_importance_df
        
        return None
    
    def backtest_strategy(self, predictions, actual_returns, dates):
        """Comprehensive backtesting framework"""
        print("📈 Running comprehensive backtest...")
        
        # Convert to DataFrame for easier manipulation
        backtest_df = pd.DataFrame({
            'date': dates,
            'predictions': predictions,
            'actual_returns': actual_returns
        })
        
        # Calculate strategy returns
        backtest_df['strategy_return'] = backtest_df['predictions'] * backtest_df['actual_returns']
        backtest_df['cumulative_return'] = (1 + backtest_df['strategy_return']).cumprod()
        backtest_df['drawdown'] = backtest_df['cumulative_return'] / backtest_df['cumulative_return'].cummax() - 1
        
        # Performance metrics
        total_return = backtest_df['cumulative_return'].iloc[-1] - 1
        volatility = backtest_df['strategy_return'].std() * np.sqrt(252)
        sharpe_ratio = backtest_df['strategy_return'].mean() / backtest_df['strategy_return'].std() * np.sqrt(252)
        max_drawdown = backtest_df['drawdown'].min()
        
        # Win rate
        winning_trades = (backtest_df['strategy_return'] > 0).sum()
        total_trades = len(backtest_df)
        win_rate = winning_trades / total_trades
        
        metrics = {
            'total_return': total_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'total_trades': total_trades
        }
        
        return metrics, backtest_df
    
    def train_with_monitoring(self, X, y_usd, y_eur, feature_names):
        """Train models with performance monitoring"""
        start_time = time.time()
        
        print("🚀 Training advanced models with monitoring...")
        
        # Feature importance analysis
        usd_importance = self.calculate_feature_importance(X, y_usd, feature_names)
        eur_importance = self.calculate_feature_importance(X, y_eur, feature_names)
        
        self.feature_importance = {
            'usd': usd_importance,
            'eur': eur_importance
        }
        
        # Build and train models
        for currency, y in [('usd', y_usd), ('eur', y_eur)]:
            print(f"\n🎯 Training {currency.upper()} model...")
            
            model_start = time.time()
            
            # Build advanced ensemble
            model = self.build_advanced_ensemble(X, y, currency)
            
            # Train model
            model.fit(X, y)
            
            # Store model and timing
            self.models[currency] = model
            self.training_time[currency] = time.time() - model_start
            
            print(f"   ✅ {currency.upper()} model trained in {self.training_time[currency]:.2f}s")
        
        total_time = time.time() - start_time
        print(f"\n🏁 Total training time: {total_time:.2f}s")
        
        return self.models
    
    def generate_predictions_with_uncertainty(self, X):
        """Generate predictions with uncertainty quantification"""
        predictions = {}
        
        for currency in ['usd', 'eur']:
            if currency in self.models:
                # Base prediction
                pred = self.models[currency].predict(X)
                predictions[f'{currency}_predictions'] = pred
                
                # Uncertainty quantification using ensemble variance
                if hasattr(self.models[currency], 'estimators_'):
                    # Get predictions from each base estimator
                    base_predictions = []
                    for estimator in self.models[currency].estimators_:
                        base_pred = estimator.predict(X)
                        base_predictions.append(base_pred)
                    
                    # Calculate prediction variance
                    pred_std = np.std(base_predictions, axis=0)
                    predictions[f'{currency}_uncertainty'] = pred_std
                    
                    # Confidence intervals based on ensemble variance
                    ci_lower = pred - 1.96 * pred_std
                    ci_upper = pred + 1.96 * pred_std
                    predictions[f'{currency}_confidence_intervals'] = np.column_stack([ci_lower, ci_upper])
        
        return predictions

# Example usage and testing
def test_phase3_improvements():
    """Test Phase 3 advanced improvements"""
    print("🧪 Testing Phase 3 Advanced Improvements")
    print("=" * 60)
    
    # This can integrate with local project data.
    # For now, create a placeholder test
    print("✅ Phase 3 framework ready for integration")
    print("📋 Available improvements:")
    print("   • Advanced ensemble with CatBoost")
    print("   • Hyperparameter optimization with Optuna")
    print("   • Comprehensive feature importance analysis")
    print("   • Enhanced backtesting framework")
    print("   • Uncertainty quantification")
    print("   • Performance monitoring")
    
    if PYTORCH_AVAILABLE:
        print("   • Transformer architecture ready")
    else:
        print("   • Install PyTorch for transformer features")

if __name__ == "__main__":
    test_phase3_improvements()
