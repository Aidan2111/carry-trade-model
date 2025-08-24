"""
Simple validation script to test basic functionality
"""
import sys
print(f"Python version: {sys.version}")

try:
    import pandas as pd
    print("✅ Pandas imported successfully")
except ImportError as e:
    print(f"❌ Pandas import failed: {e}")

try:
    import numpy as np
    print("✅ NumPy imported successfully")
except ImportError as e:
    print(f"❌ NumPy import failed: {e}")

try:
    from sklearn.ensemble import RandomForestRegressor
    print("✅ Scikit-learn imported successfully")
except ImportError as e:
    print(f"❌ Scikit-learn import failed: {e}")

try:
    import xgboost as xgb
    print("✅ XGBoost imported successfully")
except ImportError as e:
    print(f"❌ XGBoost import failed: {e}")

try:
    import lightgbm as lgb
    print("✅ LightGBM imported successfully")
except ImportError as e:
    print(f"❌ LightGBM import failed: {e}")

print("\n🧪 Testing basic functionality...")

# Test basic data creation
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Create simple test data
dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
test_data = pd.DataFrame({
    'date': dates,
    'price': np.random.randn(len(dates)).cumsum() + 100,
    'volume': np.random.randint(1000, 10000, len(dates))
})

print(f"✅ Test data created: {test_data.shape}")
print(f"📅 Date range: {test_data['date'].min()} to {test_data['date'].max()}")

print("\n🎉 Basic functionality test completed successfully!")
