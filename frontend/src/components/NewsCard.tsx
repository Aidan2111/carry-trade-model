import React from 'react';
import { NewsHeadline } from '../types';

interface Props {
  data: NewsHeadline[];
}

const NewsCard: React.FC<Props> = ({ data }) => {
  const getSentimentColor = (sentiment: number) => {
    if (sentiment > 0.1) return 'text-emerald-400 bg-emerald-500/20';
    if (sentiment < -0.1) return 'text-red-400 bg-red-500/20';
    return 'text-gray-400 bg-gray-500/20';
  };

  const getSentimentIcon = (sentiment: number) => {
    if (sentiment > 0.3) return '🚀';
    if (sentiment > 0.1) return '�';
    if (sentiment < -0.3) return '💥';
    if (sentiment < -0.1) return '�';
    return '➡️';
  };

  const getRegionColor = (region: string) => {
    switch (region) {
      case 'USD': return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
      case 'EUR': return 'bg-purple-500/20 text-purple-400 border-purple-500/30';
      case 'GBP': return 'bg-red-500/20 text-red-400 border-red-500/30';
      case 'JPY': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      case 'AUD': return 'bg-green-500/20 text-green-400 border-green-500/30';
      case 'CAD': return 'bg-orange-500/20 text-orange-400 border-orange-500/30';
      default: return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
    }
  };

  const getSourceIcon = (source: string) => {
    const sourceMap: { [key: string]: string } = {
      'Reuters': '📰',
      'Bloomberg': '📊',
      'BBC': '🌍',
      'CNBC': '💼',
      'Financial Times': '📈',
      'MarketWatch': '📉',
      'Yahoo Finance': '🏛️',
      'WSJ': '📋'
    };
    return sourceMap[source] || '📃';
  };

  const getTimeAgo = (timestamp: string) => {
    const now = new Date();
    const time = new Date(timestamp);
    const diffInHours = Math.floor((now.getTime() - time.getTime()) / (1000 * 60 * 60));
    
    if (diffInHours < 1) return 'Just now';
    if (diffInHours < 24) return `${diffInHours}h ago`;
    return `${Math.floor(diffInHours / 24)}d ago`;
  };

  return (
    <div className="trading-card group">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-xl font-bold text-gray-100 flex items-center gap-2">
            📈 Market News
          </h3>
          <p className="text-gray-400 text-sm">Financial headlines from configured sources</p>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-blue-500 rounded-full animate-pulse shadow-lg shadow-blue-500/50"></div>
          <span className="text-xs text-blue-400 font-medium">DATA FEED</span>
        </div>
      </div>
      
      <div className="space-y-4 max-h-96 overflow-y-auto custom-scrollbar">
        {data.map((news, index) => (
          <div key={index} className="group/news">
            <div className="bg-gray-800/30 rounded-lg p-4 border border-gray-700/50 hover:border-blue-500/30 transition-all duration-300 hover:bg-gray-800/50">
              {/* Header with region and sentiment */}
              <div className="flex justify-between items-start mb-3">
                <div className="flex items-center gap-2">
                  <div className={`px-2 py-1 rounded-lg text-xs font-bold border ${getRegionColor(news.region)}`}>
                    {news.region}
                  </div>
                  <div className="flex items-center gap-1">
                    <span className="text-lg">{getSourceIcon(news.source)}</span>
                    <span className="text-xs text-gray-400 font-medium">{news.source}</span>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xl">{getSentimentIcon(news.sentiment)}</span>
                  <div className={`px-2 py-1 rounded-lg text-xs font-mono ${getSentimentColor(news.sentiment)}`}>
                    {news.sentiment > 0 ? '+' : ''}{news.sentiment.toFixed(2)}
                  </div>
                </div>
              </div>
              
              {/* Headline */}
              <h4 className="font-semibold text-gray-100 mb-3 line-clamp-2 text-sm leading-relaxed group-hover/news:text-blue-300 transition-colors">
                {news.headline}
              </h4>
              
              {/* Sentiment bar */}
              <div className="mb-3">
                <div className="h-1 bg-gray-700 rounded-full overflow-hidden">
                  <div 
                    className={`h-full rounded-full transition-all duration-1000 ${
                      news.sentiment > 0.1 ? 'bg-emerald-500' : 
                      news.sentiment < -0.1 ? 'bg-red-500' : 'bg-gray-500'
                    }`}
                    style={{ 
                      width: `${50 + (news.sentiment * 50)}%`,
                      marginLeft: news.sentiment < 0 ? `${50 + (news.sentiment * 50)}%` : '0'
                    }}
                  ></div>
                </div>
              </div>
              
              {/* Footer */}
              <div className="flex justify-between items-center text-xs">
                <div className="flex items-center gap-2 text-gray-400">
                  <span className="font-medium">{news.source}</span>
                  <span>•</span>
                  <span>{getTimeAgo(news.timestamp)}</span>
                </div>
                <div className="text-gray-500">
                  Impact: {Math.abs(news.sentiment) > 0.3 ? 'HIGH' : Math.abs(news.sentiment) > 0.1 ? 'MED' : 'LOW'}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
      
      {data.length === 0 && (
        <div className="text-center py-12">
          <div className="text-6xl mb-4">📰</div>
          <div className="text-gray-400 font-medium">No market news available</div>
          <div className="text-gray-500 text-sm mt-2">Configure news sources or add a news log</div>
        </div>
      )}
    </div>
  );
};

export default NewsCard;
