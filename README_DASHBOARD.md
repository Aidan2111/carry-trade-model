# Carry Trade Dashboard

A comprehensive real-time dashboard for carry trade modeling and analysis, featuring machine learning predictions, sentiment analysis, and FX market monitoring.

## Architecture Overview

### Frontend (React TypeScript)
- **Dashboard**: Real-time data visualization
- **Components**: Modular cards for different data types
- **Styling**: Tailwind CSS for responsive design
- **API Integration**: Axios for backend communication

### Backend (Python Flask)
- **API Server**: RESTful endpoints serving JSON data
- **Data Integration**: Connects to existing Python models
- **Real-time Updates**: Live data from logs and files
- **CORS Enabled**: Cross-origin requests supported

## Features

### 📊 FX Rates Card
- Real-time USD/UAH and EUR/UAH exchange rates
- Change indicators with color-coded trends
- Live status indicator

### 📈 Sentiment Analysis Card
- Regional sentiment scores (USD, EUR, UAH)
- Confidence levels and sentiment labels
- Real-time news sentiment processing

### 🎯 Performance Metrics Card
- Total return and Sharpe ratio
- Maximum drawdown and win rate
- Volatility measurements
- Benchmark comparisons

### 🤖 Model Predictions Card
- ML-generated return forecasts
- Confidence levels with visual indicators
- Multi-horizon predictions (7, 30, 60, 90 days)

### 🚀 Trading Signals Card
- BUY/SELL/HOLD recommendations
- Signal strength indicators
- Expected returns and risk assessments

### 📰 Market News Card
- Latest financial headlines
- Sentiment-analyzed news stories
- Regional news categorization

### 📊 Macro Data Card
- Economic indicators (Fed Funds, CPI, etc.)
- Change tracking from previous values
- Visual trend indicators

## Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js 20.19+ for the Vite dashboard
- Virtual environment (recommended)

### Backend Setup

1. **Activate virtual environment**:
   ```bash
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the backend server**:
   ```bash
   python api_server.py
   # Or use the batch file:
   run_backend.bat
   ```

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install Node.js dependencies**:
   ```bash
   npm install
   ```

3. **Start the development server**:
   ```bash
   npm start
   # Or use the batch file:
   run_frontend.bat
   ```

## API Endpoints

### Core Data Endpoints
- `GET /api/dashboard` - Complete dashboard data
- `GET /api/fx-rates` - Real-time FX rates
- `GET /api/sentiment` - Market sentiment analysis
- `GET /api/macro` - Macroeconomic indicators
- `GET /api/predictions` - ML model predictions
- `GET /api/signals` - Trading signals
- `GET /api/performance` - Performance metrics
- `GET /api/news` - Market news headlines

### Utility Endpoints
- `GET /health` - API health check
- `POST /api/update-model` - Trigger model update

## Data Sources

### Real-time Data
- **FX Rates**: `logs/fx/fx_log.csv`
- **News Sentiment**: `logs/news_log.csv`
- **Performance**: `logs/performance_log.csv`

### Historical Data
- **Macro Data**: `logs/macro/*.csv`
- **Headlines**: `*_headlines.csv` files
- **FX History**: `logs/fx/*_Historical_Data.csv`

## Configuration

### Environment Variables
Create `.env` file in frontend directory:
```
VITE_API_URL=http://localhost:8000
REACT_APP_VERSION=1.0.0
REACT_APP_ENVIRONMENT=development
```

### Backend Configuration
- Default port: 8000
- CORS enabled for all origins
- Debug mode enabled in development

## Technology Stack

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Axios** - HTTP client
- **Recharts** - Data visualization (ready for charts)

### Backend
- **Flask** - Web framework
- **Flask-CORS** - Cross-origin support
- **Pandas** - Data manipulation
- **NumPy** - Numerical computing
- **VADER Sentiment** - Sentiment analysis

### Machine Learning Integration
- **Scikit-learn** - ML models
- **LightGBM/XGBoost** - Ensemble models
- **SHAP** - Model explainability

## Development

### Adding New Components
1. Create component in `frontend/src/components/`
2. Add TypeScript interface in `types/index.ts`
3. Import and use in `Dashboard.tsx`

### Adding New API Endpoints
1. Add route in `api_server.py`
2. Update API service in `frontend/src/services/api.ts`
3. Add data loading function if needed

### Styling Guidelines
- Use Tailwind utility classes
- Follow component-based structure
- Maintain responsive design patterns

## Deployment

### Production Build
```bash
# Frontend
cd frontend
npm run build

# Backend
python api_server.py --host=0.0.0.0 --port=8000
```

### Docker Support (Optional)
Ready for containerization - Dockerfile can be added for production deployment.

## Monitoring & Logging

### Backend Logs
- API request/response logging
- Error tracking and handling
- Performance monitoring

### Frontend Monitoring
- Real-time status indicators
- Error boundaries for graceful failures
- Auto-refresh capabilities

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes with proper TypeScript typing
4. Test both frontend and backend
5. Submit pull request

## License

MIT License - See LICENSE file for details

## Support

For issues or questions:
1. Check the logs directory for data availability
2. Verify API endpoints are responding
3. Check browser console for frontend errors
4. Ensure all dependencies are installed

---

**Dashboard URL**: http://localhost:3000  
**API URL**: http://localhost:8000  
**Health Check**: http://localhost:8000/health
