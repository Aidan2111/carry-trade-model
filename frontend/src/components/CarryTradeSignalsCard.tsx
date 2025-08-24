import React from 'react';
import { CarryTradeSignal } from '../types';

interface Props {
  data: CarryTradeSignal[];
}

const CarryTradeSignalsCard: React.FC<Props> = ({ data }) => {
  const getActionColor = (action: string) => {
    switch (action) {
      case 'BUY': return 'bg-green-100 text-green-800 border-green-200';
      case 'SELL': return 'bg-red-100 text-red-800 border-red-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getActionIcon = (action: string) => {
    switch (action) {
      case 'BUY': return '📈';
      case 'SELL': return '📉';
      default: return '⏸️';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Trading Signals</h3>
        <div className="text-sm text-gray-500">Live</div>
      </div>
      
      <div className="space-y-4">
        {data.map((signal, index) => (
          <div key={`${signal.pair}-${index}`} className="border border-gray-200 rounded-lg p-4">
            <div className="flex justify-between items-start mb-3">
              <div className="flex items-center space-x-3">
                <div className="text-2xl">{getActionIcon(signal.action)}</div>
                <div>
                  <div className="font-semibold text-gray-900">{signal.pair}</div>
                  <div className="text-sm text-gray-500">
                    Risk: {signal.risk.toFixed(1)}%
                  </div>
                </div>
              </div>
              <div className={`px-3 py-1 rounded border ${getActionColor(signal.action)}`}>
                {signal.action}
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <div className="text-gray-600">Signal Strength</div>
                <div className="font-semibold">{signal.strength}%</div>
              </div>
              <div>
                <div className="text-gray-600">Expected Return</div>
                <div className={`font-semibold ${signal.expectedReturn >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {signal.expectedReturn > 0 ? '+' : ''}{signal.expectedReturn.toFixed(2)}%
                </div>
              </div>
            </div>
            
            <div className="mt-3">
              <div className="flex justify-between text-xs text-gray-500 mb-1">
                <span>Strength</span>
                <span>{signal.strength}%</span>
              </div>
              <div className="bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-blue-500 h-2 rounded-full transition-all"
                  style={{ width: `${signal.strength}%` }}
                ></div>
              </div>
            </div>
          </div>
        ))}
      </div>
      
      {data.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          No trading signals available
        </div>
      )}
    </div>
  );
};

export default CarryTradeSignalsCard;
