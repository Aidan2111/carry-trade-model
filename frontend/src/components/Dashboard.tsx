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
  const [isConnected, setIsConnected] = useState(true);

  // Mock data for development with more realistic trading data
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
      {
        pair: 'EUR/USD',
        rate: 1.0892,
        change: 0.0023,
        changePercent: 0.21,
        timestamp: new Date().toISOString(),
      },
      {
        pair: 'GBP/USD',
        rate: 1.2654,
        change: -0.0045,
        changePercent: -0.35,
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
      {
        indicator: 'US 10Y Treasury',
        value: 4.26,
        previousValue: 4.18,
        change: 0.08,
        timestamp: new Date().toISOString(),
      },
      {
        indicator: 'EUR CPI',
        value: 2.8,
        previousValue: 2.9,
        change: -0.1,
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
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="relative">
            <div className="animate-spin rounded-full h-16 w-16 border-4 border-gray-600 border-t-blue-500 mx-auto"></div>
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-8 h-8 bg-blue-500 rounded-full animate-pulse"></div>
            </div>
          </div>
          <p className="mt-6 text-gray-300 text-lg">Loading trading dashboard...</p>
          <p className="mt-2 text-gray-500 text-sm">Fetching real-time market data</p>
        </div>
      </div>
    );
  }

  if (error && !data) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center max-w-md mx-auto">
          <div className="w-16 h-16 bg-red-500/20 rounded-full flex items-center justify-center mx-auto mb-6">
            <svg className="w-8 h-8 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.313 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <h2 className="text-xl font-semibold text-red-400 mb-4">Connection Error</h2>
          <p className="text-gray-400 mb-6">{error}</p>
          <button 
            onClick={handleRefresh}
            className="btn-primary"
          >
            Retry Connection
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900">
      {/* Modern Trading Header */}
      <header className="navbar sticky top-0 z-50">
        <div className="max-w-8xl mx-auto px-6">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-6">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-xl flex items-center justify-center">
                  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                  </svg>
                </div>
                <div>
                  <h1 className="text-2xl font-bold gradient-text">
                    CarryTrade Pro
                  </h1>
                  <p className="text-gray-400 text-sm">Advanced Trading Analytics</p>
                </div>
              </div>
              
              <div className="flex items-center space-x-2 px-3 py-1 bg-gray-800 rounded-lg">
                <div className={`status-indicator ${isConnected ? 'status-live' : 'status-error'}`}></div>
                <span className="text-sm text-gray-300">
                  {isConnected ? 'Live Market Data' : 'Disconnected'}
                </span>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <p className="text-sm text-gray-400">Last updated</p>
                <p className="text-sm font-mono text-gray-200">
                  {lastUpdate.toLocaleTimeString()}
                </p>
              </div>
              
              <button
                onClick={handleRefresh}
                disabled={loading}
                className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <svg className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                {loading ? 'Syncing...' : 'Refresh'}
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Error Banner */}
      {error && (
        <div className="bg-red-500/10 border-l-4 border-red-500 p-4 mx-6 mt-4 rounded-r-lg">
          <div className="flex items-center">
            <svg className="w-5 h-5 text-red-400 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.313 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
            <p className="text-red-200">{error}</p>
          </div>
        </div>
      )}

      {/* Main Trading Dashboard */}
      <main className="max-w-8xl mx-auto px-6 py-6">
        {/* Top Row - Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Portfolio Performance */}
          <div className="trading-card p-6 fade-in-up">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-200">Portfolio Return</h3>
              <div className="w-10 h-10 bg-green-500/20 rounded-lg flex items-center justify-center">
                <svg className="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
              </div>
            </div>
            <div className="number-large text-green-400">
              +{data?.performance?.totalReturn || 12.5}%
            </div>
            <p className="text-gray-400 text-sm mt-2">
              <span className="text-green-400">↗ +2.3%</span> this week
            </p>
          </div>

          {/* Sharpe Ratio */}
          <div className="trading-card p-6 fade-in-up" style={{animationDelay: '0.1s'}}>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-200">Sharpe Ratio</h3>
              <div className="w-10 h-10 bg-blue-500/20 rounded-lg flex items-center justify-center">
                <svg className="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
            </div>
            <div className="number-large text-blue-400">
              {data?.performance?.sharpeRatio || 1.35}
            </div>
            <p className="text-gray-400 text-sm mt-2">Risk-adjusted return</p>
          </div>

          {/* Max Drawdown */}
          <div className="trading-card p-6 fade-in-up" style={{animationDelay: '0.2s'}}>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-200">Max Drawdown</h3>
              <div className="w-10 h-10 bg-red-500/20 rounded-lg flex items-center justify-center">
                <svg className="w-5 h-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" />
                </svg>
              </div>
            </div>
            <div className="number-large text-red-400">
              {data?.performance?.maxDrawdown || -8.2}%
            </div>
            <p className="text-gray-400 text-sm mt-2">Peak to trough loss</p>
          </div>

          {/* Win Rate */}
          <div className="trading-card p-6 fade-in-up" style={{animationDelay: '0.3s'}}>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-200">Win Rate</h3>
              <div className="w-10 h-10 bg-purple-500/20 rounded-lg flex items-center justify-center">
                <svg className="w-5 h-5 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
            <div className="number-large text-purple-400">
              {data?.performance?.winRate || 65}%
            </div>
            <p className="text-gray-400 text-sm mt-2">Successful trades</p>
          </div>
        </div>

        {/* Second Row - Trading Cards */}
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6 mb-8">
          {/* FX Rates with enhanced design */}
          <div className="lg:col-span-1">
            <FXRatesCard data={data?.fxRates || []} />
          </div>
          
          {/* Trading Signals */}
          <div className="lg:col-span-1">
            <CarryTradeSignalsCard data={data?.signals || []} />
          </div>
          
          {/* Model Predictions */}
          <div className="lg:col-span-1 xl:col-span-1">
            <ModelPredictionsCard data={data?.predictions || []} />
          </div>
        </div>

        {/* Third Row - Analysis Cards */}
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6 mb-8">
          {/* Macro Data */}
          <div className="lg:col-span-1">
            <MacroDataCard data={data?.macroData || []} />
          </div>
          
          {/* Sentiment Analysis */}
          <div className="lg:col-span-1">
            <SentimentCard data={data?.sentiment || []} />
          </div>
          
          {/* Performance Details */}
          <div className="lg:col-span-1">
            <PerformanceCard data={data?.performance} />
          </div>
        </div>

        {/* Bottom Row - News Feed */}
        <div className="grid grid-cols-1 gap-6">
          <NewsCard data={data?.news || []} />
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
