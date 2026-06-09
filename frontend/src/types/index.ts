export interface FXRate {
  pair: string;
  rate: number;
  change: number;
  changePercent: number;
  timestamp: string;
}

export interface SentimentData {
  region: 'USD' | 'EUR' | 'UAH';
  score: number;
  label: 'positive' | 'negative' | 'neutral';
  confidence: number;
  timestamp: string;
}

export interface MacroData {
  indicator: string;
  value: number;
  previousValue: number;
  change: number;
  timestamp: string;
}

export interface ModelPrediction {
  pair: string;
  predictedReturn: number;
  confidence: number;
  horizon: number; // days
  timestamp: string;
}

export interface CarryTradeSignal {
  pair: string;
  action: 'BUY' | 'SELL' | 'HOLD';
  strength: number; // 0-100
  expectedReturn: number;
  risk: number;
  timestamp: string;
}

export interface PerformanceMetrics {
  totalReturn: number;
  sharpeRatio: number;
  maxDrawdown: number;
  winRate: number;
  avgDailyReturn: number;
  volatility: number;
  benchmark: number;
  timestamp: string;
}

export interface NewsHeadline {
  headline: string;
  source: string;
  sentiment: number;
  timestamp: string;
  region: 'USD' | 'EUR' | 'UAH';
}

export interface DashboardData {
  fxRates: FXRate[];
  sentiment: SentimentData[];
  macroData: MacroData[];
  predictions: ModelPrediction[];
  signals: CarryTradeSignal[];
  performance?: PerformanceMetrics | null;
  news: NewsHeadline[];
  lastUpdate?: string;
  dataSource?: string;
}
