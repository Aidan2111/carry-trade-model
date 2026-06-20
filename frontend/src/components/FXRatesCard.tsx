import React from 'react';
import { FXRate } from '../types';

interface Props {
  data: FXRate[];
}

const FXRatesCard: React.FC<Props> = ({ data }) => {
  const formatChange = (change: number, changePercent: number) => {
    const sign = change >= 0 ? '+' : '';
    const color = change >= 0 ? 'text-emerald-400' : 'text-red-400';
    const bgColor = change >= 0 ? 'bg-emerald-500/10' : 'bg-red-500/10';
    return (
      <span className={`${color} ${bgColor} px-2 py-1 rounded text-xs font-medium`}>
        {sign}{change.toFixed(4)} ({sign}{changePercent.toFixed(2)}%)
      </span>
    );
  };

  const getStrengthIndicator = (changePercent: number) => {
    const abs = Math.abs(changePercent);
    if (abs > 1) return 'High move';
    if (abs > 0.5) return 'Firm';
    if (abs > 0.1) return 'Active';
    return 'Stable';
  };

  return (
    <div className="trading-card group p-4 sm:p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-xl font-bold text-gray-100 flex items-center gap-2">
            <span className="flex h-7 w-7 items-center justify-center rounded-md border border-blue-500/30 bg-blue-500/15 text-xs font-bold text-blue-300">
              FX
            </span>
            FX Rates
          </h3>
          <p className="text-gray-400 text-sm">Currency rates from the API</p>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-emerald-500 rounded-full animate-pulse shadow-lg shadow-emerald-500/50"></div>
          <span className="text-xs text-emerald-400 font-medium">DATA</span>
        </div>
      </div>
      
      <div className="space-y-4">
        {data.map((rate, index) => (
          <div key={rate.pair} className="bg-gray-800/50 rounded-lg p-4 border border-gray-700/50 hover:border-blue-500/50 transition-all duration-300 group/rate">
            <div className="flex justify-between items-center">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center text-white font-bold text-sm">
                  {rate.pair.split('/')[0]}
                </div>
                <div>
                  <div className="font-bold text-gray-100 text-lg">{rate.pair}</div>
                  <div className="text-xs text-gray-400">
                    {new Date(rate.timestamp).toLocaleTimeString()} • {getStrengthIndicator(rate.changePercent)}
                  </div>
                </div>
              </div>
              <div className="text-right">
                <div className="text-2xl font-mono font-bold text-gray-100 mb-1 group-hover/rate:text-blue-400 transition-colors">
                  {rate.rate.toFixed(4)}
                </div>
                <div>
                  {formatChange(rate.change, rate.changePercent)}
                </div>
              </div>
            </div>
            
            {/* Micro trend line */}
            <div className="mt-3 h-1 bg-gray-700 rounded-full overflow-hidden">
              <div 
                className={`h-full rounded-full transition-all duration-1000 ${
                  rate.changePercent >= 0 ? 'bg-emerald-500' : 'bg-red-500'
                }`}
                style={{ width: `${Math.min(Math.abs(rate.changePercent) * 20, 100)}%` }}
              ></div>
            </div>
          </div>
        ))}
      </div>
      
      {data.length === 0 && (
        <div className="text-center py-12">
          <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-lg border border-blue-500/30 bg-blue-500/10 text-sm font-bold text-blue-300">FX</div>
          <div className="text-gray-400 font-medium">No FX data available</div>
          <div className="text-gray-500 text-sm mt-2">Start the backend or run data collection</div>
        </div>
      )}
    </div>
  );
};

export default FXRatesCard;
