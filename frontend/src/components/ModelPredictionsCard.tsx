import React from 'react';
import { ModelPrediction } from '../types';

interface Props {
  data: ModelPrediction[];
}

const ModelPredictionsCard: React.FC<Props> = ({ data }) => {
  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30';
    if (confidence >= 0.6) return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
    return 'bg-red-500/20 text-red-400 border-red-500/30';
  };

  const getReturnColor = (predictedReturn: number) => {
    return predictedReturn >= 0 ? 'text-emerald-400' : 'text-red-400';
  };

  const getConfidenceGradient = (confidence: number) => {
    if (confidence >= 0.8) return 'from-emerald-500 to-green-500';
    if (confidence >= 0.6) return 'from-yellow-500 to-orange-500';
    return 'from-red-500 to-rose-500';
  };

  const getPredictionIcon = (predictedReturn: number, confidence: number) => {
    if (confidence < 0.5) return '❓';
    if (predictedReturn > 2) return '🚀';
    if (predictedReturn > 0.5) return '📈';
    if (predictedReturn < -2) return '💥';
    if (predictedReturn < -0.5) return '📉';
    return '➡️';
  };

  return (
    <div className="trading-card group">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-xl font-bold text-gray-100 flex items-center gap-2">
            🤖 Model Outputs
          </h3>
          <p className="text-gray-400 text-sm">Research forecasts from backend data</p>
        </div>
        <div className="flex items-center gap-2">
          <div className="px-3 py-1 bg-blue-500/20 text-blue-400 text-xs rounded-lg border border-blue-500/30 font-medium">
            API Output
          </div>
        </div>
      </div>
      
      <div className="space-y-4">
        {data.map((prediction, index) => (
          <div key={`${prediction.pair}-${index}`} className="bg-gray-800/50 rounded-lg border border-gray-700/50 hover:border-purple-500/50 transition-all duration-300 overflow-hidden group/prediction">
            <div className="p-6">
              <div className="flex justify-between items-start mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-blue-600 rounded-lg flex items-center justify-center text-white font-bold text-sm">
                    {prediction.pair.split('/')[0]}
                  </div>
                  <div>
                    <div className="font-bold text-gray-100 text-lg">{prediction.pair}</div>
                    <div className="flex items-center gap-2 text-sm text-gray-400">
                      <span>Backend forecast</span>
                      <span>•</span>
                      <span>{prediction.horizon}-day forecast</span>
                    </div>
                  </div>
                </div>
                <div className="text-right flex items-center gap-3">
                  <div className="text-3xl">
                    {getPredictionIcon(prediction.predictedReturn, prediction.confidence)}
                  </div>
                  <div className={`px-3 py-2 rounded-lg border text-xs font-bold ${getConfidenceColor(prediction.confidence)}`}>
                    {(prediction.confidence * 100).toFixed(0)}% CONFIDENCE
                  </div>
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4 mb-4">
                <div className="bg-gray-700/50 rounded-lg p-3">
                  <div className="text-xs text-gray-400 mb-1">Predicted Return</div>
                  <div className={`text-2xl font-bold font-mono ${getReturnColor(prediction.predictedReturn)}`}>
                    {prediction.predictedReturn > 0 ? '+' : ''}{prediction.predictedReturn.toFixed(2)}%
                  </div>
                </div>
                <div className="bg-gray-700/50 rounded-lg p-3">
                  <div className="text-xs text-gray-400 mb-1">Risk Level</div>
                  <div className="text-lg font-bold text-gray-100">
                    {prediction.confidence >= 0.8 ? 'LOW' : prediction.confidence >= 0.6 ? 'MEDIUM' : 'HIGH'}
                  </div>
                </div>
              </div>
              
              {/* Confidence visualization */}
              <div className="mb-3">
                <div className="flex justify-between text-xs text-gray-400 mb-1">
                  <span>Model Confidence</span>
                  <span>{(prediction.confidence * 100).toFixed(1)}%</span>
                </div>
                <div className="h-3 bg-gray-700 rounded-full overflow-hidden">
                  <div 
                    className={`h-full bg-gradient-to-r ${getConfidenceGradient(prediction.confidence)} rounded-full transition-all duration-1000 shadow-lg`}
                    style={{ width: `${prediction.confidence * 100}%` }}
                  ></div>
                </div>
              </div>
              
              {/* Return magnitude visualization */}
              <div className="mb-4">
                <div className="flex justify-between text-xs text-gray-400 mb-1">
                  <span>Return Magnitude</span>
                  <span>{Math.abs(prediction.predictedReturn).toFixed(2)}%</span>
                </div>
                <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                  <div 
                    className={`h-full rounded-full transition-all duration-1000 ${
                      prediction.predictedReturn >= 0 ? 'bg-emerald-500' : 'bg-red-500'
                    }`}
                    style={{ width: `${Math.min(Math.abs(prediction.predictedReturn) * 10, 100)}%` }}
                  ></div>
                </div>
              </div>
              
              <div className="text-xs text-gray-500 border-t border-gray-700 pt-3">
                Last updated: {new Date(prediction.timestamp).toLocaleString()}
              </div>
            </div>
          </div>
        ))}
      </div>
      
      {data.length === 0 && (
        <div className="text-center py-12">
          <div className="text-6xl mb-4">🤖</div>
          <div className="text-gray-400 font-medium">Training AI models...</div>
          <div className="text-gray-500 text-sm mt-2">Generating predictions from market data</div>
        </div>
      )}
    </div>
  );
};

export default ModelPredictionsCard;
