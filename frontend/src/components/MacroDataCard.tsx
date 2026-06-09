import React from 'react';
import { MacroData } from '../types';

interface Props {
  data: MacroData[];
}

const MacroDataCard: React.FC<Props> = ({ data }) => {
  const getChangeColor = (change: number) => {
    return change >= 0 ? 'text-emerald-400' : 'text-red-400';
  };

  const getChangeIcon = (change: number) => {
    return change >= 0 ? '📈' : '📉';
  };

  return (
    <div className="trading-card p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-xl font-bold text-gray-100">Macro Indicators</h3>
          <p className="text-gray-400 text-sm">Economic data from local logs</p>
        </div>
        <div className="px-3 py-1 bg-blue-500/20 text-blue-400 text-xs rounded-lg border border-blue-500/30 font-medium">
          Data
        </div>
      </div>
      
      <div className="space-y-3">
        {data.map((indicator, index) => (
          <div key={`${indicator.indicator}-${index}`} className="flex justify-between items-center p-3 bg-gray-800/50 border border-gray-700/50 rounded-lg">
            <div className="flex items-center space-x-3">
              <div className="text-xl">{getChangeIcon(indicator.change)}</div>
              <div>
                <div className="font-semibold text-gray-100">{indicator.indicator}</div>
                <div className="text-sm text-gray-400">
                  Previous: {indicator.previousValue.toFixed(2)}
                </div>
              </div>
            </div>
            <div className="text-right">
              <div className="text-lg font-bold text-gray-100">
                {indicator.value.toFixed(2)}
              </div>
              <div className={`text-sm ${getChangeColor(indicator.change)}`}>
                {indicator.change > 0 ? '+' : ''}{indicator.change.toFixed(2)}
              </div>
            </div>
          </div>
        ))}
      </div>
      
      {data.length === 0 && (
        <div className="text-center py-8 text-gray-400">
          No macro data available
        </div>
      )}
    </div>
  );
};

export default MacroDataCard;
