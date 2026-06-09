import React, { useCallback, useEffect, useState } from 'react';
import { DashboardData } from '../types';
import { ApiService } from '../services/api';
import FXRatesCard from './FXRatesCard';
import SentimentCard from './SentimentCard';
import ModelPredictionsCard from './ModelPredictionsCard';
import PerformanceCard from './PerformanceCard';
import CarryTradeSignalsCard from './CarryTradeSignalsCard';
import MacroDataCard from './MacroDataCard';
import NewsCard from './NewsCard';

const formatPercent = (value?: number) => {
  if (value === undefined || value === null || Number.isNaN(value)) {
    return 'N/A';
  }

  const sign = value > 0 ? '+' : '';
  return `${sign}${value.toFixed(2)}%`;
};

const formatNumber = (value?: number) => {
  if (value === undefined || value === null || Number.isNaN(value)) {
    return 'N/A';
  }

  return value.toFixed(2);
};

const Dashboard: React.FC = () => {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      const dashboardData = await ApiService.getDashboardData();
      setData(dashboardData);
      setLastUpdate(new Date());
      setError(null);
      setIsConnected(true);
    } catch (err) {
      setError('Backend API unavailable. Start api_server_real_data.py or set VITE_API_URL.');
      setIsConnected(false);
      console.error('Dashboard data fetch error:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000);

    return () => clearInterval(interval);
  }, [fetchData]);

  const performance = data?.performance;

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
          <p className="mt-2 text-gray-500 text-sm">Requesting backend market data</p>
        </div>
      </div>
    );
  }

  if (error && !data) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center max-w-md mx-auto px-6">
          <div className="w-16 h-16 bg-red-500/20 rounded-full flex items-center justify-center mx-auto mb-6">
            <svg className="w-8 h-8 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.313 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <h2 className="text-xl font-semibold text-red-400 mb-4">Connection Error</h2>
          <p className="text-gray-400 mb-6">{error}</p>
          <button
            onClick={fetchData}
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
                    CarryTrade Research
                  </h1>
                  <p className="text-gray-400 text-sm">Currency carry research dashboard</p>
                </div>
              </div>

              <div className="flex items-center space-x-2 px-3 py-1 bg-gray-800 rounded-lg">
                <div className={`status-indicator ${isConnected ? 'status-live' : 'status-error'}`}></div>
                <span className="text-sm text-gray-300">
                  {isConnected ? 'API connected' : 'API disconnected'}
                </span>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <div className="text-right">
                <p className="text-sm text-gray-400">Last updated</p>
                <p className="text-sm font-mono text-gray-200">
                  {lastUpdate ? lastUpdate.toLocaleTimeString() : 'N/A'}
                </p>
              </div>

              <button
                onClick={fetchData}
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

      {error && (
        <div className="bg-red-500/10 border-l-4 border-red-500 p-4 mx-6 mt-4 rounded-r-lg">
          <div className="flex items-center">
            <svg className="w-5 h-5 text-red-400 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-2.5 0L4.313 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
            <p className="text-red-200">{error}</p>
          </div>
        </div>
      )}

      <main className="max-w-8xl mx-auto px-6 py-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
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
              {formatPercent(performance?.totalReturn)}
            </div>
            <p className="text-gray-400 text-sm mt-2">From performance log or recent FX calculation</p>
          </div>

          <div className="trading-card p-6 fade-in-up" style={{ animationDelay: '0.1s' }}>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-200">Sharpe Ratio</h3>
              <div className="w-10 h-10 bg-blue-500/20 rounded-lg flex items-center justify-center">
                <svg className="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
            </div>
            <div className="number-large text-blue-400">
              {formatNumber(performance?.sharpeRatio)}
            </div>
            <p className="text-gray-400 text-sm mt-2">Risk-adjusted return</p>
          </div>

          <div className="trading-card p-6 fade-in-up" style={{ animationDelay: '0.2s' }}>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-200">Max Drawdown</h3>
              <div className="w-10 h-10 bg-red-500/20 rounded-lg flex items-center justify-center">
                <svg className="w-5 h-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" />
                </svg>
              </div>
            </div>
            <div className="number-large text-red-400">
              {formatPercent(performance?.maxDrawdown)}
            </div>
            <p className="text-gray-400 text-sm mt-2">Peak-to-trough loss</p>
          </div>

          <div className="trading-card p-6 fade-in-up" style={{ animationDelay: '0.3s' }}>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-200">Win Rate</h3>
              <div className="w-10 h-10 bg-purple-500/20 rounded-lg flex items-center justify-center">
                <svg className="w-5 h-5 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
            <div className="number-large text-purple-400">
              {formatPercent(performance?.winRate)}
            </div>
            <p className="text-gray-400 text-sm mt-2">Only shown when calculated</p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6 mb-8">
          <div className="lg:col-span-1">
            <FXRatesCard data={data?.fxRates || []} />
          </div>

          <div className="lg:col-span-1">
            <CarryTradeSignalsCard data={data?.signals || []} />
          </div>

          <div className="lg:col-span-1 xl:col-span-1">
            <ModelPredictionsCard data={data?.predictions || []} />
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6 mb-8">
          <div className="lg:col-span-1">
            <MacroDataCard data={data?.macroData || []} />
          </div>

          <div className="lg:col-span-1">
            <SentimentCard data={data?.sentiment || []} />
          </div>

          <div className="lg:col-span-1">
            <PerformanceCard data={performance || undefined} />
          </div>
        </div>

        <div className="grid grid-cols-1 gap-6">
          <NewsCard data={data?.news || []} />
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
