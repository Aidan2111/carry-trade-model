import React from 'react';
import { FXRate } from '../types';

interface Props {
  data: FXRate[];
}

const FXRatesCard: React.FC<Props> = ({ data }) => {
  const formatChange = (change: number, changePercent: number) => {
    const sign = change >= 0 ? '+' : '';
    const color = change >= 0 ? 'text-green-600' : 'text-red-600';
    return (
      <span className={color}>
        {sign}{change.toFixed(4)} ({sign}{changePercent.toFixed(2)}%)
      </span>
    );
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">FX Rates</h3>
        <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
      </div>
      
      <div className="space-y-4">
        {data.map((rate) => (
          <div key={rate.pair} className="flex justify-between items-center">
            <div>
              <div className="font-semibold text-gray-900">{rate.pair}</div>
              <div className="text-sm text-gray-500">
                {new Date(rate.timestamp).toLocaleTimeString()}
              </div>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-gray-900">
                {rate.rate.toFixed(4)}
              </div>
              <div className="text-sm">
                {formatChange(rate.change, rate.changePercent)}
              </div>
            </div>
          </div>
        ))}
      </div>
      
      {data.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          No FX data available
        </div>
      )}
    </div>
  );
};

export default FXRatesCard;
