"""
Improved Carry Trade Model with Proper Time Series Validation
This implements the key improvements identified in the analysis
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Core ML imports
from sklearn.ensemble import RandomForestRegressor, StackingRegressor
from sklearn.linear_model import Ridge, RidgeCV
from sklearn.model_selection import TimeSeriesSplit, GridSearchCV
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.feature_selection import SelectKBest, f_regression, RFE
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
def _optional_model_error(exc):
    message = str(exc)
    if 'libomp' in message:
        return 'OpenMP runtime libomp is not installed; run `brew install libomp` on macOS to enable this model.'
    return message.splitlines()[0] if message else exc.__class__.__name__


try:
    import lightgbm as lgb
except Exception as exc:
    lgb = None
    LIGHTGBM_IMPORT_ERROR = _optional_model_error(exc)
else:
    LIGHTGBM_IMPORT_ERROR = None

try:
    import xgboost as xgb
except Exception as exc:
    xgb = None
    XGBOOST_IMPORT_ERROR = _optional_model_error(exc)
else:
    XGBOOST_IMPORT_ERROR = None

# Technical analysis (simplified without TA-Lib)
from scipy import stats

# Visualization
import matplotlib.pyplot as plt

# Utilities
import os
import sys
from pathlib import Path

from carry_trade.paths import PROJECT_ROOT

class ImprovedCarryTradeModel:
    """
    Enhanced carry trade model with proper validation and advanced features
    """
    
    def __init__(self, base_dir=None):
        self.base_dir = base_dir or str(PROJECT_ROOT)
        self.logs_dir = os.path.join(self.base_dir, 'logs')
        self.models = {}
        self.scalers = {}
        self.feature_selectors = {}
        self.performance_metrics = {}
        self._optional_model_warnings_printed = set()
        
        # Ensure logs directory exists
        os.makedirs(self.logs_dir, exist_ok=True)
        os.makedirs(os.path.join(self.logs_dir, 'fx'), exist_ok=True)
        os.makedirs(os.path.join(self.logs_dir, 'macro'), exist_ok=True)

    def _build_base_models(self, n_estimators=100):
        """Build the ensemble with optional boosted-tree models when available."""
        models = [
            ('rf', RandomForestRegressor(n_estimators=n_estimators, random_state=42, n_jobs=-1))
        ]

        if xgb is not None:
            models.append((
                'xgb',
                xgb.XGBRegressor(
                    n_estimators=n_estimators,
                    random_state=42,
                    n_jobs=-1,
                    verbosity=0
                )
            ))
        else:
            if 'xgboost' not in self._optional_model_warnings_printed:
                print(f"⚠️ Skipping XGBoost: {XGBOOST_IMPORT_ERROR}")
                self._optional_model_warnings_printed.add('xgboost')

        if lgb is not None:
            models.append((
                'lgb',
                lgb.LGBMRegressor(
                    n_estimators=n_estimators,
                    random_state=42,
                    n_jobs=-1,
                    verbosity=-1
                )
            ))
        else:
            if 'lightgbm' not in self._optional_model_warnings_printed:
                print(f"⚠️ Skipping LightGBM: {LIGHTGBM_IMPORT_ERROR}")
                self._optional_model_warnings_printed.add('lightgbm')

        return models

    def _build_meta_model(self):
        """Meta-learner for stacking with a data-driven regularization scale."""
        return RidgeCV(alphas=np.logspace(-8, 2, 30))

    def load_and_prepare_data(self):
        """
        Load and prepare data with enhanced feature engineering
        """
        print("📊 Loading and preparing data...")
        
        # Load FX data
        try:
            fx_data = self._load_fx_data()
        except Exception as e:
            print(f"⚠️ Error loading FX data: {e}")
            return None
        
        # Load macro data
        try:
            macro_data = self._load_macro_data()
        except Exception as e:
            print(f"⚠️ Error loading macro data: {e}")
            return None
        
        # Load sentiment data
        try:
            sentiment_data = self._load_sentiment_data()
        except Exception as e:
            print(f"⚠️ Error loading sentiment data: {e}")
            return None
        
        # Merge all data
        data = self._merge_data(fx_data, macro_data, sentiment_data)
        
        if data is None or data.empty:
            print("❌ No data available after merging")
            return None
        
        # Enhanced feature engineering
        data = self._enhanced_feature_engineering(data)
        
        # Data quality checks
        data = self._data_quality_checks(data)
        
        print(f"✅ Data preparation complete. Shape: {data.shape}")
        print(f"📅 Date range: {data['date'].min()} to {data['date'].max()}")
        
        return data
    
    def _load_fx_data(self):
        """Load FX data with fallback options"""
        fx_files = [
            'logs/fx/fx_log.csv',
            'logs/fx/USD_UAH Historical Data.csv',
            'logs/fx/EUR_UAH Historical Data.csv'
        ]
        
        # Try to load combined FX data first
        fx_path = os.path.join(self.base_dir, fx_files[0])
        if os.path.exists(fx_path):
            fx_data = pd.read_csv(fx_path)
            fx_data['date'] = pd.to_datetime(fx_data['date'])
            return fx_data
        
        # Fallback: load individual files
        usd_path = os.path.join(self.base_dir, fx_files[1])
        eur_path = os.path.join(self.base_dir, fx_files[2])
        
        if os.path.exists(usd_path) and os.path.exists(eur_path):
            usd_data = pd.read_csv(usd_path)
            eur_data = pd.read_csv(eur_path)
            
            # Standardize column names
            usd_data['date'] = pd.to_datetime(usd_data.get('Date', usd_data.get('date')))
            eur_data['date'] = pd.to_datetime(eur_data.get('Date', eur_data.get('date')))
            
            usd_data = usd_data[['date', 'Price']].rename(columns={'Price': 'USD_UAH'})
            eur_data = eur_data[['date', 'Price']].rename(columns={'Price': 'EUR_UAH'})
            
            fx_data = pd.merge(usd_data, eur_data, on='date', how='outer')
            return fx_data.sort_values('date')
        
        raise FileNotFoundError("No FX data files found")
    
    def _load_macro_data(self):
        """Load macro economic data"""
        macro_path = os.path.join(self.base_dir, 'logs/macro/macro_log.csv')
        
        if os.path.exists(macro_path):
            macro_data = pd.read_csv(macro_path)
            macro_data['date'] = pd.to_datetime(macro_data['date'])
            
            # Standardize column names
            if 'US_FedFunds' not in macro_data.columns and 'USD_FedFunds' in macro_data.columns:
                macro_data.rename(columns={'USD_FedFunds': 'US_FedFunds'}, inplace=True)
            
            # Add missing columns with default values
            default_values = {
                'US_FedFunds': 0.05,
                'EU_Rate': 0.02,
                'UAH_Rate': 0.1,
                'US_CPI': 3.0,
                'US_InflationExpectations': 2.5,
                'US_YieldCurve': 1.5,
                'EU_ConsumerPrices': 2.0
            }
            
            for col, default_val in default_values.items():
                if col not in macro_data.columns:
                    macro_data[col] = default_val
            
            return macro_data
        
        # Create default macro data if file doesn't exist
        print("⚠️ Creating default macro data")
        dates = pd.date_range(start='2020-01-01', end=datetime.now(), freq='D')
        macro_data = pd.DataFrame({
            'date': dates,
            'US_FedFunds': 0.05,
            'EU_Rate': 0.02,
            'UAH_Rate': 0.1,
            'US_CPI': 3.0,
            'US_InflationExpectations': 2.5,
            'US_YieldCurve': 1.5,
            'EU_ConsumerPrices': 2.0
        })
        
        return macro_data
    
    def _load_sentiment_data(self):
        """Load sentiment data"""
        sentiment_path = os.path.join(self.base_dir, 'logs/news_log.csv')
        
        if os.path.exists(sentiment_path):
            sentiment_data = pd.read_csv(sentiment_path)
            
            # Find date column
            date_cols = ['date', 'Date', 'timestamp', 'Timestamp']
            date_col = None
            for col in date_cols:
                if col in sentiment_data.columns:
                    date_col = col
                    break
            
            if date_col:
                sentiment_data['date'] = pd.to_datetime(sentiment_data[date_col])

                wide_sentiment_cols = ['sentiment_usd', 'sentiment_eur', 'sentiment_uah']
                if all(col in sentiment_data.columns for col in wide_sentiment_cols):
                    return sentiment_data[['date', *wide_sentiment_cols]]

                if not {'Region', 'Sentiment'}.issubset(sentiment_data.columns):
                    print("⚠️ Sentiment log missing Region/Sentiment columns; using neutral sentiment")
                    return pd.DataFrame({
                        'date': sentiment_data['date'],
                        'sentiment_usd': 0.0,
                        'sentiment_eur': 0.0,
                        'sentiment_uah': 0.0
                    })
                
                # Aggregate sentiment by date and region
                sentiment_agg = sentiment_data.groupby(['date', 'Region']).agg({
                    'Sentiment': 'mean'
                }).reset_index()
                
                # Pivot to get sentiment columns
                sentiment_pivot = sentiment_agg.pivot(index='date', columns='Region', values='Sentiment')
                sentiment_pivot.columns = [f'sentiment_{col.lower()}' for col in sentiment_pivot.columns]
                sentiment_pivot = sentiment_pivot.reset_index()
                
                # Fill missing sentiment columns
                for col in ['sentiment_usd', 'sentiment_eur', 'sentiment_uah']:
                    if col not in sentiment_pivot.columns:
                        sentiment_pivot[col] = 0.0
                
                return sentiment_pivot
        
        # Create default sentiment data
        print("⚠️ Creating default sentiment data")
        dates = pd.date_range(start='2020-01-01', end=datetime.now(), freq='D')
        sentiment_data = pd.DataFrame({
            'date': dates,
            'sentiment_usd': 0.0,
            'sentiment_eur': 0.0,
            'sentiment_uah': 0.0
        })
        
        return sentiment_data
    
    def _merge_data(self, fx_data, macro_data, sentiment_data):
        """Merge all data sources"""
        print("🔄 Merging data sources...")
        
        # Align date formats
        for df in [fx_data, macro_data, sentiment_data]:
            df['date'] = pd.to_datetime(df['date']).dt.date
        
        # Start with FX data as base
        data = fx_data.copy()
        
        # Merge macro data
        data = data.merge(macro_data, on='date', how='inner')
        print(f"After macro merge: {data.shape}")
        
        # Merge sentiment data
        data = data.merge(sentiment_data, on='date', how='left')
        print(f"After sentiment merge: {data.shape}")
        
        # Convert date back to datetime
        data['date'] = pd.to_datetime(data['date'])
        data = data.sort_values('date')
        
        # Forward fill missing values
        data = data.ffill().fillna(0)
        
        return data
    
    def _enhanced_feature_engineering(self, data):
        """
        Create enhanced features including technical indicators
        """
        print("🛠️ Creating enhanced features...")
        
        # Basic carry trade features
        data['interest_diff_usd'] = data['US_FedFunds'] - data['UAH_Rate']
        data['interest_diff_eur'] = data['EU_Rate'] - data['UAH_Rate']
        
        # Returns (7-day forward looking)
        data['usd_return'] = data['USD_UAH'].pct_change(7).shift(-7)
        data['eur_return'] = data['EUR_UAH'].pct_change(7).shift(-7)
        
        # Technical indicators for USD_UAH
        if len(data) > 50:  # Need enough data for technical indicators
            try:
                # Price-based indicators
                data['usd_sma_10'] = data['USD_UAH'].rolling(10).mean()
                data['usd_sma_20'] = data['USD_UAH'].rolling(20).mean()
                data['usd_sma_30'] = data['USD_UAH'].rolling(30).mean()
                data['usd_ema_10'] = data['USD_UAH'].ewm(span=10).mean()
                
                # Volatility
                data['usd_volatility'] = data['USD_UAH'].pct_change().rolling(20).std()
                data['eur_volatility'] = data['EUR_UAH'].pct_change().rolling(20).std()
                
                # Momentum indicators
                data['usd_momentum'] = data['USD_UAH'] / data['USD_UAH'].shift(10) - 1
                data['eur_momentum'] = data['EUR_UAH'] / data['EUR_UAH'].shift(10) - 1
                
                # RSI (Relative Strength Index)
                if len(data) > 14:
                    delta = data['USD_UAH'].diff()
                    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                    rs = gain / loss
                    data['usd_rsi'] = 100 - (100 / (1 + rs))
                
                # Bollinger Bands
                data['usd_bb_upper'] = data['usd_sma_20'] + (data['USD_UAH'].rolling(20).std() * 2)
                data['usd_bb_lower'] = data['usd_sma_20'] - (data['USD_UAH'].rolling(20).std() * 2)
                data['usd_bb_position'] = (data['USD_UAH'] - data['usd_bb_lower']) / (data['usd_bb_upper'] - data['usd_bb_lower'])
                
            except Exception as e:
                print(f"⚠️ Error creating technical indicators: {e}")
        
        # Macro feature engineering
        data['yield_curve_slope'] = data.get('US_YieldCurve', 0)
        data['real_rate_usd'] = data['US_FedFunds'] - data.get('US_CPI', 0)
        data['real_rate_eur'] = data['EU_Rate'] - data.get('EU_ConsumerPrices', 0)
        
        # Sentiment features
        data['sentiment_momentum'] = data['sentiment_usd'].rolling(5).mean()
        data['sentiment_volatility'] = data['sentiment_usd'].rolling(10).std()
        
        # Cross-asset features
        data['fx_correlation'] = data['USD_UAH'].rolling(30).corr(data['EUR_UAH'])
        
        print(f"✅ Feature engineering complete. New shape: {data.shape}")
        return data
    
    def _data_quality_checks(self, data):
        """
        Perform data quality checks and cleaning
        """
        print("🔍 Performing data quality checks...")
        
        # Remove rows with all NaN in key columns
        key_columns = ['USD_UAH', 'EUR_UAH']
        data = data.dropna(subset=key_columns, how='all')
        
        # Outlier detection on daily moves. Levels are deliberately not capped:
        # clipping a trending FX series with full-sample quantiles leaks future
        # information into past rows and erases genuine regime shifts.
        for col in ['USD_UAH', 'EUR_UAH']:
            if col in data.columns:
                daily_move = data[col].pct_change().abs()
                suspicious = daily_move > 0.25
                if suspicious.any():
                    print(
                        f"⚠️ {col}: {suspicious.sum()} daily moves above 25%; "
                        "verify these against the raw source"
                    )
        
        # Check for data gaps
        data = data.sort_values('date')
        date_diff = data['date'].diff().dt.days
        large_gaps = date_diff > 7
        if large_gaps.any():
            print(f"⚠️ Found {large_gaps.sum()} large data gaps (>7 days)")
        
        print(f"✅ Data quality checks complete. Final shape: {data.shape}")
        return data
    
    def prepare_features_and_targets(self, data):
        """
        Prepare feature matrix and target variables
        """
        print("🎯 Preparing features and targets...")
        
        # Define feature columns
        feature_columns = [
            # Basic carry trade features
            'interest_diff_usd', 'interest_diff_eur',
            
            # Macro features
            'US_FedFunds', 'EU_Rate', 'UAH_Rate',
            'US_CPI', 'US_InflationExpectations', 'US_YieldCurve', 'EU_ConsumerPrices',
            'yield_curve_slope', 'real_rate_usd', 'real_rate_eur',
            
            # Sentiment features
            'sentiment_usd', 'sentiment_eur', 'sentiment_uah',
            'sentiment_momentum', 'sentiment_volatility',
            
            # Technical features
            'usd_volatility', 'eur_volatility',
            'usd_momentum', 'eur_momentum',
            'fx_correlation'
        ]
        
        # Only include features that exist in the data
        available_features = [col for col in feature_columns if col in data.columns]
        print(f"📊 Using {len(available_features)} features out of {len(feature_columns)} possible")
        
        # Prepare feature matrix
        X = data[available_features].copy()
        
        # Prepare targets
        y_usd = data['usd_return'].copy()
        y_eur = data['eur_return'].copy()
        
        # Remove rows with missing targets
        valid_indices = ~(y_usd.isna() | y_eur.isna())
        X = X[valid_indices]
        y_usd = y_usd[valid_indices]
        y_eur = y_eur[valid_indices]
        dates = data['date'][valid_indices]
        
        # Handle remaining NaN values in features
        X = X.ffill().fillna(0)
        
        print(f"✅ Feature preparation complete:")
        print(f"   📈 Features shape: {X.shape}")
        print(f"   🎯 USD targets: {len(y_usd)} samples")
        print(f"   🎯 EUR targets: {len(y_eur)} samples")
        print(f"   📅 Date range: {dates.min()} to {dates.max()}")
        
        return X, y_usd, y_eur, dates, available_features
    
    def time_series_split_validation(self, X, y_usd, y_eur, dates):
        """
        Perform proper time series cross-validation
        """
        print("⏰ Starting time series cross-validation...")
        
        # Use TimeSeriesSplit with a purge gap matching the 7-day forward
        # target so train-set targets cannot overlap the validation window.
        tscv = TimeSeriesSplit(n_splits=5, gap=7)
        
        results = {
            'usd_scores': [],
            'eur_scores': [],
            'fold_dates': []
        }
        
        for fold, (train_idx, val_idx) in enumerate(tscv.split(X)):
            print(f"🔄 Processing fold {fold + 1}/5...")
            
            X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
            y_usd_train, y_usd_val = y_usd.iloc[train_idx], y_usd.iloc[val_idx]
            y_eur_train, y_eur_val = y_eur.iloc[train_idx], y_eur.iloc[val_idx]
            
            # Record fold dates
            train_dates = dates.iloc[train_idx]
            val_dates = dates.iloc[val_idx]
            results['fold_dates'].append({
                'fold': fold + 1,
                'train_start': train_dates.min(),
                'train_end': train_dates.max(),
                'val_start': val_dates.min(),
                'val_end': val_dates.max()
            })
            
            # Scale features
            scaler = RobustScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_val_scaled = scaler.transform(X_val)
            
            # Train models for this fold
            fold_results = self._train_fold_models(
                X_train_scaled, X_val_scaled, 
                y_usd_train, y_usd_val,
                y_eur_train, y_eur_val,
                fold
            )
            
            results['usd_scores'].append(fold_results['usd_score'])
            results['eur_scores'].append(fold_results['eur_score'])
        
        # Calculate average performance
        avg_usd_score = np.mean(results['usd_scores'])
        avg_eur_score = np.mean(results['eur_scores'])
        
        print(f"✅ Time series validation complete:")
        print(f"   📊 Average USD R²: {avg_usd_score:.4f} (±{np.std(results['usd_scores']):.4f})")
        print(f"   📊 Average EUR R²: {avg_eur_score:.4f} (±{np.std(results['eur_scores']):.4f})")
        
        return results
    
    def _train_fold_models(self, X_train, X_val, y_usd_train, y_usd_val, y_eur_train, y_eur_val, fold):
        """
        Train models for a single fold
        """
        # Create improved ensemble with stacking
        base_models = self._build_base_models(n_estimators=100)

        # A fixed alpha=1.0 over-shrinks meta coefficients because FX returns
        # have tiny variance; let RidgeCV pick a scale-appropriate penalty.
        meta_model = self._build_meta_model()
        
        # Stacking ensemble
        stacked_usd = StackingRegressor(
            estimators=base_models,
            final_estimator=meta_model,
            cv=3,
            n_jobs=-1
        )
        
        stacked_eur = StackingRegressor(
            estimators=base_models,
            final_estimator=meta_model,
            cv=3,
            n_jobs=-1
        )
        
        # Train models
        stacked_usd.fit(X_train, y_usd_train)
        stacked_eur.fit(X_train, y_eur_train)
        
        # Make predictions
        usd_pred = stacked_usd.predict(X_val)
        eur_pred = stacked_eur.predict(X_val)
        
        # Calculate scores
        usd_score = r2_score(y_usd_val, usd_pred)
        eur_score = r2_score(y_eur_val, eur_pred)
        
        return {
            'usd_score': usd_score,
            'eur_score': eur_score,
            'usd_model': stacked_usd,
            'eur_model': stacked_eur
        }
    
    def train_final_models(self, X, y_usd, y_eur, feature_names):
        """
        Train final models on all available data
        """
        print("🎓 Training final models...")
        
        # Feature scaling
        self.scalers['features'] = RobustScaler()
        X_scaled = self.scalers['features'].fit_transform(X)
        
        # Feature selection
        selector = SelectKBest(score_func=f_regression, k=min(15, X.shape[1]))
        X_selected = selector.fit_transform(X_scaled, y_usd)
        self.feature_selectors['selector'] = selector
        
        selected_features = [feature_names[i] for i in selector.get_support(indices=True)]
        print(f"📋 Selected {len(selected_features)} features: {selected_features}")
        
        # Create final ensemble models
        base_models = self._build_base_models(n_estimators=200)

        meta_model = self._build_meta_model()
        
        # Train USD model
        self.models['usd'] = StackingRegressor(
            estimators=base_models,
            final_estimator=meta_model,
            cv=3,
            n_jobs=-1
        )
        self.models['usd'].fit(X_selected, y_usd)
        
        # Train EUR model
        self.models['eur'] = StackingRegressor(
            estimators=base_models,
            final_estimator=meta_model,
            cv=3,
            n_jobs=-1
        )
        self.models['eur'].fit(X_selected, y_eur)
        
        print("✅ Final models trained successfully!")
        
        return selected_features
    
    def predict(self, X_new):
        """
        Make predictions with confidence intervals
        """
        if not self.models:
            raise ValueError("Models not trained yet!")
        
        # Scale features
        X_scaled = self.scalers['features'].transform(X_new)
        
        # Select features
        X_selected = self.feature_selectors['selector'].transform(X_scaled)
        
        # Make predictions
        usd_pred = self.models['usd'].predict(X_selected)
        eur_pred = self.models['eur'].predict(X_selected)
        
        # Calculate prediction intervals using bootstrap approach
        usd_intervals = self._calculate_prediction_intervals(self.models['usd'], X_selected, confidence=0.95)
        eur_intervals = self._calculate_prediction_intervals(self.models['eur'], X_selected, confidence=0.95)
        
        return {
            'usd_predictions': usd_pred,
            'eur_predictions': eur_pred,
            'usd_confidence_intervals': usd_intervals,
            'eur_confidence_intervals': eur_intervals,
            'usd_confidence': np.mean(usd_intervals[:, 1] - usd_intervals[:, 0]),
            'eur_confidence': np.mean(eur_intervals[:, 1] - eur_intervals[:, 0])
        }
    
    def _calculate_prediction_intervals(self, model, X, confidence=0.95, n_bootstrap=100):
        """
        Calculate prediction intervals using bootstrap sampling
        """
        predictions = []
        
        # For ensemble models, we can use the prediction variance from base estimators
        if hasattr(model, 'estimators_'):
            # Get predictions from all base estimators
            base_predictions = []
            for estimator in model.estimators_:
                pred = estimator.predict(X)
                base_predictions.append(pred)
            base_predictions = np.array(base_predictions)
            
            # Calculate mean and std across base estimators
            mean_pred = np.mean(base_predictions, axis=0)
            std_pred = np.std(base_predictions, axis=0)
            
            # Calculate confidence intervals using normal approximation
            alpha = 1 - confidence
            z_score = 1.96  # For 95% confidence interval
            
            lower_bound = mean_pred - z_score * std_pred
            upper_bound = mean_pred + z_score * std_pred
            
            return np.column_stack([lower_bound, upper_bound])
        
        else:
            # Fallback: use simple standard deviation estimate
            pred = model.predict(X)
            std_estimate = np.std(pred) * 0.1  # 10% of prediction std as uncertainty
            
            alpha = 1 - confidence
            z_score = 1.96
            
            lower_bound = pred - z_score * std_estimate
            upper_bound = pred + z_score * std_estimate
            
            return np.column_stack([lower_bound, upper_bound])
    
    def run_full_pipeline(self):
        """
        Run the complete improved modeling pipeline
        """
        print("🚀 Starting Improved Carry Trade Model Pipeline...")
        print("=" * 60)
        
        # Step 1: Load and prepare data
        data = self.load_and_prepare_data()
        if data is None:
            print("❌ Pipeline failed: No data available")
            return None
        
        # Step 2: Prepare features and targets
        X, y_usd, y_eur, dates, feature_names = self.prepare_features_and_targets(data)
        
        if len(X) < 100:
            print("⚠️ Warning: Limited data available, results may not be reliable")
        
        # Step 3: Time series cross-validation
        cv_results = self.time_series_split_validation(X, y_usd, y_eur, dates)
        
        # Step 4: Train final models
        selected_features = self.train_final_models(X, y_usd, y_eur, feature_names)
        
        # Step 5: Save results
        self._save_results(cv_results, selected_features)
        
        print("=" * 60)
        print("✅ Improved pipeline completed successfully!")
        
        return {
            'cv_results': cv_results,
            'selected_features': selected_features,
            'data_shape': X.shape,
            'date_range': (dates.min(), dates.max())
        }
    
    def _save_results(self, cv_results, selected_features):
        """Save model results and performance metrics"""
        results_dir = os.path.join(self.logs_dir, 'model_results')
        os.makedirs(results_dir, exist_ok=True)
        
        # Save CV results
        cv_df = pd.DataFrame({
            'fold': range(1, len(cv_results['usd_scores']) + 1),
            'usd_r2': cv_results['usd_scores'],
            'eur_r2': cv_results['eur_scores']
        })
        cv_df.to_csv(os.path.join(results_dir, 'cv_results.csv'), index=False)
        
        # Save selected features
        features_df = pd.DataFrame({'feature': selected_features})
        features_df.to_csv(os.path.join(results_dir, 'selected_features.csv'), index=False)
        
        print(f"📁 Results saved to {results_dir}")


if __name__ == "__main__":
    # Initialize and run the improved model
    model = ImprovedCarryTradeModel()
    results = model.run_full_pipeline()
    
    if results:
        print(f"\n📊 Final Results Summary:")
        print(f"   🎯 Data points: {results['data_shape'][0]}")
        print(f"   📈 Features: {results['data_shape'][1]}")
        print(f"   📅 Date range: {results['date_range'][0]} to {results['date_range'][1]}")
        print(f"   🏆 Selected features: {len(results['selected_features'])}")
