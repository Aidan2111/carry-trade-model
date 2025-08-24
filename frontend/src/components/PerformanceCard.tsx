import React from 'react';
import { PerformanceMetrics } from '../types';

interface Props {
  data?: PerformanceMetrics;
}

const PerformanceCard: React.FC<Props> = ({ data }) => {
  if (!data) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance Metrics</h3>
        <div className="text-center py-8 text-gray-500">
          No performance data available
        </div>
      </div>
    );
  }

  const metrics = [
    {
      label: 'Total Return',
      value: `${data.totalReturn > 0 ? '+' : ''}${data.totalReturn.toFixed(2)}%`,
      color: data.totalReturn >= 0 ? 'text-green-600' : 'text-red-600',
      icon: data.totalReturn >= 0 ? '📈' : '📉',
    },
    {
      label: 'Sharpe Ratio',
      value: data.sharpeRatio.toFixed(2),
      color: data.sharpeRatio >= 1 ? 'text-green-600' : data.sharpeRatio >= 0.5 ? 'text-yellow-600' : 'text-red-600',
      icon: '📊',
    },
    {
      label: 'Max Drawdown',
      value: `${data.maxDrawdown.toFixed(2)}%`,
      color: data.maxDrawdown >= -10 ? 'text-green-600' : data.maxDrawdown >= -20 ? 'text-yellow-600' : 'text-red-600',
      icon: '📉',
    },
    {
      label: 'Win Rate',
      value: `${data.winRate.toFixed(1)}%`,
      color: data.winRate >= 60 ? 'text-green-600' : data.winRate >= 50 ? 'text-yellow-600' : 'text-red-600',
      icon: '🎯',
    },
    {
      label: 'Volatility',
      value: `${data.volatility.toFixed(2)}%`,
      color: data.volatility <= 15 ? 'text-green-600' : data.volatility <= 25 ? 'text-yellow-600' : 'text-red-600',
      icon: '📈',
    },
    {
      label: 'vs Benchmark',
      value: `${data.totalReturn - data.benchmark > 0 ? '+' : ''}${(data.totalReturn - data.benchmark).toFixed(2)}%`,
      color: data.totalReturn - data.benchmark >= 0 ? 'text-green-600' : 'text-red-600',
      icon: '🏆',
    },
  ];

  return (
    <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Performance Metrics</h3>
        <div className="text-sm text-gray-500">
          {new Date(data.timestamp).toLocaleDateString()}
        </div>
      </div>
      
      <div className="grid grid-cols-2 gap-4">
        {metrics.map((metric) => (
          <div key={metric.label} className="bg-gray-50 rounded-lg p-3">
            <div className="flex items-center justify-between mb-1">
              <span className="text-sm text-gray-600">{metric.label}</span>
              <span className="text-lg">{metric.icon}</span>
            </div>
            <div className={`text-xl font-bold ${metric.color}`}>
              {metric.value}
            </div>
          </div>
        ))}
      </div>
      
      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="flex justify-between text-sm text-gray-600">
          <span>Avg Daily Return:</span>
          <span className={data.avgDailyReturn >= 0 ? 'text-green-600' : 'text-red-600'}>
            {data.avgDailyReturn > 0 ? '+' : ''}{(data.avgDailyReturn * 100).toFixed(3)}%
          </span>
        </div>
      </div>
    </div>
  );
};

export default PerformanceCard;
