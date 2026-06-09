import React from 'react';
import { CarryTradeSignal } from '../types';

interface Props {
  data: CarryTradeSignal[];
}

const CarryTradeSignalsCard: React.FC<Props> = ({ data }) => {
  const getActionColor = (action: string) => {
    switch (action) {
      case 'BUY': return 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30';
      case 'SELL': return 'bg-red-500/20 text-red-300 border-red-500/30';
      default: return 'bg-gray-700 text-gray-200 border-gray-600';
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
    <div className="trading-card p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-xl font-bold text-gray-100">Trading Signals</h3>
          <p className="text-gray-400 text-sm">Derived from backend forecasts</p>
        </div>
        <div className="px-3 py-1 bg-blue-500/20 text-blue-400 text-xs rounded-lg border border-blue-500/30 font-medium">
          API Output
        </div>
      </div>
      
      <div className="space-y-4">
        {data.map((signal, index) => (
          <div key={`${signal.pair}-${index}`} className="bg-gray-800/50 border border-gray-700/50 rounded-lg p-4">
            <div className="flex justify-between items-start mb-3">
              <div className="flex items-center space-x-3">
                <div className="text-2xl">{getActionIcon(signal.action)}</div>
                <div>
                  <div className="font-semibold text-gray-100">{signal.pair}</div>
                  <div className="text-sm text-gray-400">
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
                <div className="text-gray-400">Signal Strength</div>
                <div className="font-semibold text-gray-100">{signal.strength}%</div>
              </div>
              <div>
                <div className="text-gray-400">Expected Return</div>
                <div className={`font-semibold ${signal.expectedReturn >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                  {signal.expectedReturn > 0 ? '+' : ''}{signal.expectedReturn.toFixed(2)}%
                </div>
              </div>
            </div>
            
            <div className="mt-3">
              <div className="flex justify-between text-xs text-gray-400 mb-1">
                <span>Strength</span>
                <span>{signal.strength}%</span>
              </div>
              <div className="bg-gray-700 rounded-full h-2">
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
        <div className="text-center py-8 text-gray-400">
          No trading signals available
        </div>
      )}
    </div>
  );
};

export default CarryTradeSignalsCard;
