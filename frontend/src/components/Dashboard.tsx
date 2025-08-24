import React, { useState, useEffect } from 'react';
import { DashboardData } from '../types';
// import { ApiService } from '../services/api';
import FXRatesCard from './FXRatesCard';
import SentimentCard from './SentimentCard';
import ModelPredictionsCard from './ModelPredictionsCard';
import PerformanceCard from './PerformanceCard';
import CarryTradeSignalsCard from './CarryTradeSignalsCard';
import MacroDataCard from './MacroDataCard';
import NewsCard from './NewsCard';

const Dashboard: React.FC = () => {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  // Mock data for development
  const mockData: DashboardData = {
    fxRates: [
      {
        pair: 'USD/UAH',
        rate: 36.85,
        change: 0.12,
        changePercent: 0.33,
        timestamp: new Date().toISOString(),
      },
      {
        pair: 'EUR/UAH',
        rate: 40.12,
        change: -0.08,
        changePercent: -0.20,
        timestamp: new Date().toISOString(),
      },
    ],
    sentiment: [
      {
        region: 'USD',
        score: 0.25,
        label: 'positive',
        confidence: 0.75,
        timestamp: new Date().toISOString(),
      },
      {
        region: 'EUR',
        score: -0.15,
        label: 'negative',
        confidence: 0.68,
        timestamp: new Date().toISOString(),
      },
      {
        region: 'UAH',
        score: 0.05,
        label: 'neutral',
        confidence: 0.55,
        timestamp: new Date().toISOString(),
      },
    ],
    macroData: [
      {
        indicator: 'US Fed Funds',
        value: 5.25,
        previousValue: 5.00,
        change: 0.25,
        timestamp: new Date().toISOString(),
      },
      {
        indicator: 'US CPI',
        value: 3.2,
        previousValue: 3.0,
        change: 0.2,
        timestamp: new Date().toISOString(),
      },
    ],
    predictions: [
      {
        pair: 'USD/UAH',
        predictedReturn: 2.5,
        confidence: 0.82,
        horizon: 30,
        timestamp: new Date().toISOString(),
      },
      {
        pair: 'EUR/UAH',
        predictedReturn: -1.2,
        confidence: 0.75,
        horizon: 30,
        timestamp: new Date().toISOString(),
      },
    ],
    signals: [
      {
        pair: 'USD/UAH',
        action: 'BUY',
        strength: 85,
        expectedReturn: 2.5,
        risk: 15,
        timestamp: new Date().toISOString(),
      },
      {
        pair: 'EUR/UAH',
        action: 'HOLD',
        strength: 45,
        expectedReturn: -1.2,
        risk: 25,
        timestamp: new Date().toISOString(),
      },
    ],
    performance: {
      totalReturn: 12.5,
      sharpeRatio: 1.35,
      maxDrawdown: -8.2,
      winRate: 65,
      avgDailyReturn: 0.08,
      volatility: 12.5,
      benchmark: 8.2,
      timestamp: new Date().toISOString(),
    },
    news: [
      {
        headline: 'Federal Reserve signals potential rate adjustment',
        source: 'Reuters',
        sentiment: 0.2,
        timestamp: new Date(Date.now() - 3600000).toISOString(),
        region: 'USD',
      },
      {
        headline: 'ECB maintains dovish stance on monetary policy',
        source: 'Bloomberg',
        sentiment: -0.1,
        timestamp: new Date(Date.now() - 7200000).toISOString(),
        region: 'EUR',
      },
    ],
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        // For now, use mock data
        // const dashboardData = await ApiService.getDashboardData();
        setData(mockData);
        setLastUpdate(new Date());
        setError(null);
      } catch (err) {
        setError('Failed to fetch dashboard data');
        console.error('Dashboard data fetch error:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    
    // Set up auto-refresh every 30 seconds
    const interval = setInterval(fetchData, 30000);
    
    return () => clearInterval(interval);
  }, []);

  const handleRefresh = async () => {
    setLoading(true);
    try {
      // const dashboardData = await ApiService.getDashboardData();
      setData(mockData);
      setLastUpdate(new Date());
      setError(null);
    } catch (err) {
      setError('Failed to refresh data');
    } finally {
      setLoading(false);
    }
  };

  if (loading && !data) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error && !data) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-500 text-xl mb-4">⚠️</div>
          <p className="text-red-600 mb-4">{error}</p>
          <button 
            onClick={handleRefresh}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">
                Carry Trade Dashboard
              </h1>
              <div className="ml-4 flex items-center">
                <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                <span className="ml-2 text-sm text-gray-600">Live</span>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-500">
                Last updated: {lastUpdate.toLocaleTimeString()}
              </span>
              <button
                onClick={handleRefresh}
                disabled={loading}
                className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white px-4 py-2 rounded-lg transition-colors"
              >
                {loading ? 'Refreshing...' : 'Refresh'}
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex">
              <div className="text-red-400">⚠️</div>
              <div className="ml-3">
                <p className="text-red-800">{error}</p>
              </div>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* FX Rates */}
          <FXRatesCard data={data?.fxRates || []} />
          
          {/* Sentiment */}
          <SentimentCard data={data?.sentiment || []} />
          
          {/* Performance Metrics */}
          <PerformanceCard data={data?.performance} />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Model Predictions */}
          <ModelPredictionsCard data={data?.predictions || []} />
          
          {/* Carry Trade Signals */}
          <CarryTradeSignalsCard data={data?.signals || []} />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Macro Data */}
          <MacroDataCard data={data?.macroData || []} />
          
          {/* News */}
          <NewsCard data={data?.news || []} />
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
