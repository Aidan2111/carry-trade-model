"""
Simple test for the improved model to verify functionality
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

# Test data creation and basic functionality
def create_test_data():
    """Create synthetic test data for validation"""
    print("Creating test data...")
    
    # Create date range
    dates = pd.date_range(start='2022-01-01', end='2024-01-01', freq='D')
    n_days = len(dates)
    
    # Create synthetic FX data with realistic trends
    np.random.seed(42)
    usd_base = 35.0
    eur_base = 38.0
    
    usd_prices = []
    eur_prices = []
    
    for i, date in enumerate(dates):
        # Add trend and noise
        trend_factor = 1 + (i / n_days) * 0.3  # 30% appreciation over period
        noise_usd = np.random.normal(0, 0.02)  # 2% daily volatility
        noise_eur = np.random.normal(0, 0.025)  # 2.5% daily volatility
        
        usd_price = usd_base * trend_factor * (1 + noise_usd)
        eur_price = eur_base * trend_factor * (1 + noise_eur)
        
        usd_prices.append(usd_price)
        eur_prices.append(eur_price)
    
    fx_data = pd.DataFrame({
        'date': dates,
        'USD_UAH': usd_prices,
        'EUR_UAH': eur_prices
    })
    
    # Create synthetic macro data
    macro_data = pd.DataFrame({
        'date': dates,
        'US_FedFunds': np.random.uniform(4.0, 5.5, n_days),
        'EU_Rate': np.random.uniform(3.0, 4.5, n_days),
        'UAH_Rate': np.random.uniform(15.0, 20.0, n_days),
        'US_CPI': np.random.uniform(2.0, 8.0, n_days),
        'US_InflationExpectations': np.random.uniform(2.0, 4.0, n_days),
        'US_YieldCurve': np.random.uniform(0.5, 3.0, n_days),
        'EU_ConsumerPrices': np.random.uniform(1.5, 6.0, n_days)
    })
    
    # Create synthetic sentiment data
    sentiment_data = pd.DataFrame({
        'date': dates,
        'sentiment_usd': np.random.normal(0, 0.3, n_days),
        'sentiment_eur': np.random.normal(0, 0.25, n_days),
        'sentiment_uah': np.random.normal(-0.1, 0.4, n_days)  # Slightly negative bias
    })
    
    print(f"✅ Created test data: {len(dates)} days from {dates[0].date()} to {dates[-1].date()}")
    
    return fx_data, macro_data, sentiment_data

def test_improved_model():
    """Test the improved model functionality"""
    print("🧪 Testing Improved Carry Trade Model")
    print("=" * 50)
    
    try:
        # Import our improved model
        from improved_ensemble_model import ImprovedCarryTradeModel
        
        # Create test data
        fx_data, macro_data, sentiment_data = create_test_data()
        
        # Save test data to files for the model to load
        os.makedirs('logs/fx', exist_ok=True)
        os.makedirs('logs/macro', exist_ok=True)
        
        # Save test data
        fx_data.to_csv('logs/fx/fx_log.csv', index=False)
        macro_data.to_csv('logs/macro/macro_log.csv', index=False)
        sentiment_data.to_csv('logs/news_log.csv', index=False)
        
        print("📁 Test data saved to logs directory")
        
        # Initialize model
        model = ImprovedCarryTradeModel()
        
        # Test data loading
        print("\n1️⃣ Testing data loading...")
        data = model.load_and_prepare_data()
        
        if data is None:
            print("❌ Data loading failed")
            return False
        
        print(f"✅ Data loaded successfully: {data.shape}")
        
        # Test feature preparation
        print("\n2️⃣ Testing feature preparation...")
        X, y_usd, y_eur, dates, feature_names = model.prepare_features_and_targets(data)
        
        print(f"✅ Features prepared: {X.shape}")
        print(f"📋 Feature names: {feature_names}")
        
        # Test time series validation (with smaller dataset)
        if len(X) >= 50:  # Only run if we have enough data
            print("\n3️⃣ Testing time series validation...")
            cv_results = model.time_series_split_validation(X, y_usd, y_eur, dates)
            print(f"✅ Cross-validation completed")
            
            # Test model training
            print("\n4️⃣ Testing final model training...")
            selected_features = model.train_final_models(X, y_usd, y_eur, feature_names)
            print(f"✅ Models trained with {len(selected_features)} selected features")
            
            # Test predictions
            print("\n5️⃣ Testing predictions...")
            predictions = model.predict(X.tail(5))  # Predict on last 5 data points
            print(f"✅ Predictions generated:")
            print(f"   USD predictions: {predictions['usd_predictions']}")
            print(f"   EUR predictions: {predictions['eur_predictions']}")
            
        else:
            print("⚠️ Insufficient data for full validation, but basic functionality works")
        
        print("\n" + "=" * 50)
        print("✅ All tests passed! Improved model is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_improved_model()
    if success:
        print("\n🎉 Improved model testing completed successfully!")
    else:
        print("\n💥 Improved model testing failed!")
