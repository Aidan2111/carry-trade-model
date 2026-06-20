import React from 'react';
import { PerformanceMetrics } from '../types';

interface Props {
  data?: PerformanceMetrics;
}

const PerformanceCard: React.FC<Props> = ({ data }) => {
  if (!data) {
    return (
      <div className="trading-card p-6">
        <h3 className="text-xl font-bold text-gray-100 mb-4">Performance Metrics</h3>
        <div className="text-center py-8 text-gray-400">
          No performance data available
        </div>
      </div>
    );
  }

  const metrics = [
    {
      label: 'Total Return',
      value: `${data.totalReturn > 0 ? '+' : ''}${data.totalReturn.toFixed(2)}%`,
      color: data.totalReturn >= 0 ? 'text-emerald-400' : 'text-red-400',
      icon: data.totalReturn >= 0 ? 'UP' : 'DN',
    },
    {
      label: 'Sharpe Ratio',
      value: data.sharpeRatio.toFixed(2),
      color: data.sharpeRatio >= 1 ? 'text-emerald-400' : data.sharpeRatio >= 0.5 ? 'text-yellow-400' : 'text-red-400',
      icon: 'SR',
    },
    {
      label: 'Max Drawdown',
      value: `${data.maxDrawdown.toFixed(2)}%`,
      color: data.maxDrawdown >= -10 ? 'text-emerald-400' : data.maxDrawdown >= -20 ? 'text-yellow-400' : 'text-red-400',
      icon: 'DD',
    },
    {
      label: 'Win Rate',
      value: `${data.winRate.toFixed(1)}%`,
      color: data.winRate >= 60 ? 'text-emerald-400' : data.winRate >= 50 ? 'text-yellow-400' : 'text-red-400',
      icon: 'WR',
    },
    {
      label: 'Volatility',
      value: `${data.volatility.toFixed(2)}%`,
      color: data.volatility <= 15 ? 'text-emerald-400' : data.volatility <= 25 ? 'text-yellow-400' : 'text-red-400',
      icon: 'VOL',
    },
    {
      label: 'vs Benchmark',
      value: `${data.totalReturn - data.benchmark > 0 ? '+' : ''}${(data.totalReturn - data.benchmark).toFixed(2)}%`,
      color: data.totalReturn - data.benchmark >= 0 ? 'text-emerald-400' : 'text-red-400',
      icon: 'BM',
    },
  ];

  return (
    <div className="trading-card p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-bold text-gray-100">Performance Metrics</h3>
        <div className="text-sm text-gray-400">
          {new Date(data.timestamp).toLocaleDateString()}
        </div>
      </div>
      
      <div className="grid grid-cols-2 gap-4">
        {metrics.map((metric) => (
          <div key={metric.label} className="bg-gray-800/50 border border-gray-700/50 rounded-lg p-3">
            <div className="flex items-center justify-between mb-1">
              <span className="text-sm text-gray-400">{metric.label}</span>
              <span className="flex h-7 min-w-7 items-center justify-center rounded-md border border-gray-600 bg-gray-700 px-1 text-[10px] font-bold text-gray-300">
                {metric.icon}
              </span>
            </div>
            <div className={`text-xl font-bold ${metric.color}`}>
              {metric.value}
            </div>
          </div>
        ))}
      </div>
      
      <div className="mt-4 pt-4 border-t border-gray-700">
        <div className="flex justify-between text-sm text-gray-400">
          <span>Avg Daily Return:</span>
          <span className={data.avgDailyReturn >= 0 ? 'text-emerald-400' : 'text-red-400'}>
            {data.avgDailyReturn > 0 ? '+' : ''}{(data.avgDailyReturn * 100).toFixed(3)}%
          </span>
        </div>
      </div>
    </div>
  );
};

export default PerformanceCard;
