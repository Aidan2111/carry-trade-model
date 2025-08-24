import React from 'react';
import { MacroData } from '../types';

interface Props {
  data: MacroData[];
}

const MacroDataCard: React.FC<Props> = ({ data }) => {
  const getChangeColor = (change: number) => {
    return change >= 0 ? 'text-green-600' : 'text-red-600';
  };

  const getChangeIcon = (change: number) => {
    return change >= 0 ? '📈' : '📉';
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Macro Indicators</h3>
        <div className="text-sm text-gray-500">Economic Data</div>
      </div>
      
      <div className="space-y-3">
        {data.map((indicator, index) => (
          <div key={`${indicator.indicator}-${index}`} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
            <div className="flex items-center space-x-3">
              <div className="text-xl">{getChangeIcon(indicator.change)}</div>
              <div>
                <div className="font-semibold text-gray-900">{indicator.indicator}</div>
                <div className="text-sm text-gray-500">
                  Previous: {indicator.previousValue.toFixed(2)}
                </div>
              </div>
            </div>
            <div className="text-right">
              <div className="text-lg font-bold text-gray-900">
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
        <div className="text-center py-8 text-gray-500">
          No macro data available
        </div>
      )}
    </div>
  );
};

export default MacroDataCard;
