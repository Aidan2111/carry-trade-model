import React from 'react';
import { NewsHeadline } from '../types';

interface Props {
  data: NewsHeadline[];
}

const NewsCard: React.FC<Props> = ({ data }) => {
  const getSentimentColor = (sentiment: number) => {
    if (sentiment > 0.1) return 'text-green-600';
    if (sentiment < -0.1) return 'text-red-600';
    return 'text-gray-600';
  };

  const getSentimentIcon = (sentiment: number) => {
    if (sentiment > 0.1) return '😊';
    if (sentiment < -0.1) return '😟';
    return '😐';
  };

  const getRegionColor = (region: string) => {
    switch (region) {
      case 'USD': return 'bg-blue-100 text-blue-800';
      case 'EUR': return 'bg-purple-100 text-purple-800';
      case 'UAH': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Market News</h3>
        <div className="text-sm text-gray-500">Latest Headlines</div>
      </div>
      
      <div className="space-y-4 max-h-96 overflow-y-auto">
        {data.map((news, index) => (
          <div key={index} className="border-l-4 border-gray-200 pl-4 py-2">
            <div className="flex justify-between items-start mb-2">
              <div className={`px-2 py-1 rounded text-xs font-medium ${getRegionColor(news.region)}`}>
                {news.region}
              </div>
              <div className="flex items-center space-x-2">
                <span className="text-lg">{getSentimentIcon(news.sentiment)}</span>
                <span className={`text-sm font-medium ${getSentimentColor(news.sentiment)}`}>
                  {news.sentiment > 0 ? '+' : ''}{news.sentiment.toFixed(2)}
                </span>
              </div>
            </div>
            
            <h4 className="font-medium text-gray-900 mb-2 line-clamp-2">
              {news.headline}
            </h4>
            
            <div className="flex justify-between items-center text-sm text-gray-500">
              <span className="font-medium">{news.source}</span>
              <span>{new Date(news.timestamp).toLocaleString()}</span>
            </div>
          </div>
        ))}
      </div>
      
      {data.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          No news data available
        </div>
      )}
    </div>
  );
};

export default NewsCard;
