# 🏦 Advanced Carry Trade Forecasting Model

A sophisticated financial trading system that combines machine learning ensemble models with real-time data collection and a modern React TypeScript dashboard for carry trade strategy analysis and forecasting.

## 🎯 Features

### 🤖 Machine Learning Models
- **Ensemble Models**: RandomForest, XGBoost, LightGBM, Ridge Regression
- **Advanced Feature Engineering**: Technical indicators, sentiment analysis, macro data
- **Backtesting Framework**: Comprehensive performance evaluation and validation
- **Real-time Predictions**: Live model inference with continuous learning

### 📊 Real-Time Data Collection
- **Multi-Source FX Data**: 4 different API sources with automatic fallbacks
- **Enhanced News Collection**: RSS feeds + NewsAPI for comprehensive coverage
- **Macro Economic Data**: Fed rates, inflation, yield curves, consumer prices
- **Sentiment Analysis**: VADER sentiment analysis on financial news
- **Smart Error Handling**: Automatic fallback systems for 100% uptime

### 🎨 Modern Dashboard
- **React TypeScript Frontend**: Professional UI with Tailwind CSS
- **Real-time Updates**: Live data visualization and model predictions
- **Multiple Card Views**: FX rates, news sentiment, macro data, performance metrics
- **Responsive Design**: Works on desktop and mobile devices

## 🏗️ Architecture

```
├── 🐍 Python Backend
│   ├── ML Models (ensemble_backtest_carry_*.py)
│   ├── Data Collection (enhanced_scraper_simple.py, real_time_data_engine.py)
│   ├── API Server (api_server_*.py)
│   └── Data Processing (process_headlines_real.py, get_historical_data.py)
├── ⚛️ React Frontend
│   ├── TypeScript Components
│   ├── Tailwind CSS Styling
│   └── API Integration
└── 📁 Data Storage
    ├── CSV Logs (FX, News, Macro)
    ├── Performance Metrics
    └── Historical Data
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Aidan2111/carry-trade-model.git
   cd carry-trade-model
   ```

2. **Set up Python environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   pip install -r requirements.txt
   ```

3. **Set up frontend**
   ```bash
   cd frontend
   npm install
   ```

4. **Configure API keys** (optional for enhanced features)
   - NewsAPI key for news data
   - Yahoo Finance (free tier)
   - ExchangeRate-API (free tier)

### Running the System

1. **Start data collection**
   ```bash
   # Enhanced multi-source data collection
   python enhanced_scraper_simple.py
   
   # OR advanced async data engine
   python real_time_data_engine.py
   ```

2. **Start backend API**
   ```bash
   python api_server_live.py
   ```

3. **Start frontend dashboard**
   ```bash
   cd frontend
   npm start
   ```

4. **Access the dashboard**
   - Open http://localhost:3000 in your browser
   - Backend API runs on http://localhost:8000

## 📈 Data Sources

### FX Data (4 sources with automatic fallback)
- Yahoo Finance API
- ExchangeRate-API
- Fixer.io
- CurrencyAPI

### News Sources (6+ sources)
- Reuters Business & Markets
- CNBC World News
- Bloomberg Markets
- Financial Times
- BBC Business
- NewsAPI integration

### Macro Economic Data
- US Federal Reserve rates
- US CPI and inflation expectations
- EU consumer prices
- US Treasury yield curves

## 🎛️ Configuration

### Data Collection Intervals
- **FX Rates**: Every 1-3 minutes
- **News Data**: Every 5-15 minutes  
- **Macro Data**: Every 1 hour

### Model Parameters
- Configurable ensemble weights
- Feature selection options
- Risk management parameters
- Backtesting periods

## 📊 Performance Metrics

The system tracks and displays:
- Model prediction accuracy
- Portfolio returns and Sharpe ratio
- News sentiment trends
- Data collection reliability
- API response times

## 🔧 Batch Scripts (Windows)

Convenient batch files for easy system management:
- `start_dashboard.bat` - Start complete system
- `run_enhanced_scraper.bat` - Data collection only
- `run_backend.bat` - API server only
- `run_frontend.bat` - Dashboard only

## 📁 Project Structure

```
carry_trade_model/
├── 📊 ML Models & Backtesting
│   ├── ensemble_backtest_carry_advanced_*.py
│   ├── carry_model_*.py
│   └── Carry_Trade_Model_*.py
├── 🔄 Data Collection
│   ├── enhanced_scraper_simple.py
│   ├── real_time_data_engine.py
│   ├── get_historical_data.py
│   └── process_headlines_real.py
├── 🌐 API & Backend
│   ├── api_server_live.py
│   ├── api_server_real_data.py
│   └── dashboard_integration.py
├── ⚛️ Frontend Dashboard
│   └── frontend/
│       ├── src/components/
│       ├── src/services/
│       └── src/types/
├── 📈 Data & Logs
│   └── logs/
│       ├── fx/
│       ├── macro/
│       └── *.csv files
└── 🔧 Utilities
    ├── *.bat (Windows batch files)
    └── requirements.txt
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This software is for educational and research purposes only. Not financial advice. Trading carries risk of financial loss. Use at your own risk.

## 🙏 Acknowledgments

- Yahoo Finance API for market data
- NewsAPI for news aggregation
- ExchangeRate-API for FX data
- Federal Reserve Economic Data (FRED)
- Open source ML libraries: scikit-learn, XGBoost, LightGBM

---

**Built with ❤️ for quantitative finance and algorithmic trading**