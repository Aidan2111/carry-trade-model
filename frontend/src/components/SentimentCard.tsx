import React from 'react';
import { SentimentData } from '../types';

interface Props {
  data: SentimentData[];
}

const SentimentCard: React.FC<Props> = ({ data }) => {
  const getSentimentColor = (score: number) => {
    if (score > 0.1) return 'text-emerald-400 bg-emerald-500/20 border-emerald-500/30';
    if (score < -0.1) return 'text-red-400 bg-red-500/20 border-red-500/30';
    return 'text-yellow-400 bg-yellow-500/20 border-yellow-500/30';
  };

  const getSentimentIcon = (label: string) => {
    switch (label) {
      case 'positive': return 'POS';
      case 'negative': return 'NEG';
      default: return 'NEU';
    }
  };

  const getSentimentGradient = (score: number) => {
    if (score > 0.1) return 'from-emerald-500/20 to-green-500/10';
    if (score < -0.1) return 'from-red-500/20 to-orange-500/10';
    return 'from-yellow-500/20 to-amber-500/10';
  };

  const getRegionFlag = (region: string) => {
    const flags: { [key: string]: string } = {
      'USD': 'USD',
      'EUR': 'EUR',
      'GBP': 'GBP',
      'JPY': 'JPY',
      'AUD': 'AUD',
      'CAD': 'CAD',
      'CHF': 'CHF',
      'NZD': 'NZD',
      'Global': 'GLB',
      'Asia': 'ASI',
      'Europe': 'EUR',
      'Americas': 'AMR'
    };
    return flags[region] || 'REG';
  };

  const averageSentiment = data.length > 0 
    ? data.reduce((sum, item) => sum + item.score, 0) / data.length 
    : 0;

  return (
    <div className="trading-card group p-4 sm:p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-xl font-bold text-gray-100 flex items-center gap-2">
            <span className="flex h-7 w-7 items-center justify-center rounded-md border border-purple-500/30 bg-purple-500/15 text-xs font-bold text-purple-300">
              SI
            </span>
            Market Sentiment
          </h3>
          <p className="text-gray-400 text-sm">AI-powered news analysis</p>
        </div>
        <div className="text-right">
          <div className={`px-3 py-1 rounded-lg border text-sm font-medium ${getSentimentColor(averageSentiment)}`}>
            Overall: {averageSentiment > 0.1 ? 'BULLISH' : averageSentiment < -0.1 ? 'BEARISH' : 'NEUTRAL'}
          </div>
          <div className="text-xs text-gray-400 mt-1">
            Score: {averageSentiment > 0 ? '+' : ''}{averageSentiment.toFixed(3)}
          </div>
        </div>
      </div>
      
      <div className="space-y-4">
        {data.map((sentiment, index) => (
          <div key={sentiment.region} className="group/sentiment">
            <div className={`bg-gradient-to-r ${getSentimentGradient(sentiment.score)} p-4 rounded-lg border border-gray-700/50 hover:border-blue-500/30 transition-all duration-300`}>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="flex items-center justify-center w-12 h-12 bg-gray-800 rounded-lg border border-gray-600">
                    <span className="text-xs font-bold text-gray-300">{getRegionFlag(sentiment.region)}</span>
                  </div>
                  <div>
                    <div className="font-bold text-gray-100 text-lg">{sentiment.region}</div>
                    <div className="flex items-center gap-2 text-sm text-gray-400">
                      <span>Confidence: {(sentiment.confidence * 100).toFixed(0)}%</span>
                      <div className="w-16 h-2 bg-gray-700 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-blue-500 rounded-full transition-all duration-500"
                          style={{ width: `${sentiment.confidence * 100}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="text-right flex items-center gap-3">
                  <div className="flex h-9 min-w-9 items-center justify-center rounded-md border border-gray-600 bg-gray-700 px-2 text-[10px] font-bold text-gray-200">
                    {getSentimentIcon(sentiment.label)}
                  </div>
                  <div>
                    <div className={`px-3 py-2 rounded-lg border text-sm font-bold ${getSentimentColor(sentiment.score)}`}>
                      {sentiment.label.toUpperCase()}
                    </div>
                    <div className="text-sm text-gray-300 mt-1 font-mono">
                      {sentiment.score > 0 ? '+' : ''}{sentiment.score.toFixed(3)}
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Sentiment strength bar */}
              <div className="mt-4 h-2 bg-gray-700 rounded-full overflow-hidden">
                <div 
                  className={`h-full rounded-full transition-all duration-1000 ${
                    sentiment.score > 0.1 ? 'bg-emerald-500' : 
                    sentiment.score < -0.1 ? 'bg-red-500' : 'bg-yellow-500'
                  }`}
                  style={{ 
                    width: `${50 + (sentiment.score * 50)}%`,
                    marginLeft: sentiment.score < 0 ? `${50 + (sentiment.score * 50)}%` : '0'
                  }}
                ></div>
              </div>
            </div>
          </div>
        ))}
      </div>
      
      {data.length === 0 && (
        <div className="text-center py-12">
          <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-lg border border-purple-500/30 bg-purple-500/10 text-sm font-bold text-purple-300">SI</div>
          <div className="text-gray-400 font-medium">No sentiment data available</div>
          <div className="text-gray-500 text-sm mt-2">Configure news collection or add sentiment logs</div>
        </div>
      )}
    </div>
  );
};

export default SentimentCard;
