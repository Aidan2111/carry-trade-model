import React from 'react';
import { ModelPrediction } from '../types';

interface Props {
  data: ModelPrediction[];
}

const ModelPredictionsCard: React.FC<Props> = ({ data }) => {
  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'bg-green-100 text-green-800';
    if (confidence >= 0.6) return 'bg-yellow-100 text-yellow-800';
    return 'bg-red-100 text-red-800';
  };

  const getReturnColor = (predictedReturn: number) => {
    return predictedReturn >= 0 ? 'text-green-600' : 'text-red-600';
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Model Predictions</h3>
        <div className="text-sm text-gray-500">ML Forecast</div>
      </div>
      
      <div className="space-y-4">
        {data.map((prediction, index) => (
          <div key={`${prediction.pair}-${index}`} className="border border-gray-200 rounded-lg p-4">
            <div className="flex justify-between items-start mb-3">
              <div>
                <div className="font-semibold text-gray-900">{prediction.pair}</div>
                <div className="text-sm text-gray-500">{prediction.horizon}-day horizon</div>
              </div>
              <div className={`px-2 py-1 rounded-full text-xs font-medium ${getConfidenceColor(prediction.confidence)}`}>
                {(prediction.confidence * 100).toFixed(0)}% confidence
              </div>
            </div>
            
            <div className="flex justify-between items-center">
              <div className="text-sm text-gray-600">Predicted Return:</div>
              <div className={`text-lg font-bold ${getReturnColor(prediction.predictedReturn)}`}>
                {prediction.predictedReturn > 0 ? '+' : ''}{prediction.predictedReturn.toFixed(2)}%
              </div>
            </div>
            
            <div className="mt-2 bg-gray-100 rounded-full h-2">
              <div 
                className={`h-2 rounded-full ${prediction.confidence >= 0.8 ? 'bg-green-500' : prediction.confidence >= 0.6 ? 'bg-yellow-500' : 'bg-red-500'}`}
                style={{ width: `${prediction.confidence * 100}%` }}
              ></div>
            </div>
            
            <div className="text-xs text-gray-500 mt-2">
              Updated: {new Date(prediction.timestamp).toLocaleString()}
            </div>
          </div>
        ))}
      </div>
      
      {data.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          No predictions available
        </div>
      )}
    </div>
  );
};

export default ModelPredictionsCard;
