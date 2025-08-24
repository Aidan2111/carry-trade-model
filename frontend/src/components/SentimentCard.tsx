import React from 'react';
import { SentimentData } from '../types';

interface Props {
  data: SentimentData[];
}

const SentimentCard: React.FC<Props> = ({ data }) => {
  const getSentimentColor = (score: number) => {
    if (score > 0.1) return 'text-green-600 bg-green-100';
    if (score < -0.1) return 'text-red-600 bg-red-100';
    return 'text-yellow-600 bg-yellow-100';
  };

  const getSentimentIcon = (label: string) => {
    switch (label) {
      case 'positive': return '📈';
      case 'negative': return '📉';
      default: return '➡️';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Market Sentiment</h3>
        <div className="text-sm text-gray-500">Real-time</div>
      </div>
      
      <div className="space-y-3">
        {data.map((sentiment) => (
          <div key={sentiment.region} className="flex items-center justify-between p-3 rounded-lg border border-gray-100">
            <div className="flex items-center space-x-3">
              <div className="text-2xl">
                {getSentimentIcon(sentiment.label)}
              </div>
              <div>
                <div className="font-semibold text-gray-900">{sentiment.region}</div>
                <div className="text-sm text-gray-500">
                  Confidence: {(sentiment.confidence * 100).toFixed(0)}%
                </div>
              </div>
            </div>
            <div className="text-right">
              <div className={`px-3 py-1 rounded-full text-sm font-medium ${getSentimentColor(sentiment.score)}`}>
                {sentiment.label.toUpperCase()}
              </div>
              <div className="text-sm text-gray-600 mt-1">
                {sentiment.score > 0 ? '+' : ''}{sentiment.score.toFixed(3)}
              </div>
            </div>
          </div>
        ))}
      </div>
      
      {data.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          No sentiment data available
        </div>
      )}
    </div>
  );
};

export default SentimentCard;
