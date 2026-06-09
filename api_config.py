# api_config.py
# Helper script to configure API connections

import os
from dotenv import load_dotenv

class APIConfig:
    """Centralized API configuration"""
    
    def __init__(self):
        load_dotenv()
        self.validate_keys()
    
    def validate_keys(self):
        """Report optional API keys that are not configured."""
        optional_keys = [
            'NEWS_API_KEY',
            'ALPHA_VANTAGE_API_KEY',
            'FRED_API_KEY',
            'FIXER_API_KEY'
        ]
        
        missing_keys = []
        for key in optional_keys:
            if not os.getenv(key):
                missing_keys.append(key)
        
        if missing_keys:
            print(f"Optional API keys not configured: {missing_keys}")
            print("Add them to your .env file to enable those data sources.")
            return False

        print("All optional API keys configured successfully")
        return True

    def get_newsapi_key(self):
        return os.getenv('NEWS_API_KEY')
    
    def get_alpha_vantage_key(self):
        return os.getenv('ALPHA_VANTAGE_API_KEY')
    
    def get_fred_key(self):
        return os.getenv('FRED_API_KEY')
    
    def get_fixer_key(self):
        return os.getenv('FIXER_API_KEY')

# Test configuration
if __name__ == "__main__":
    config = APIConfig()
