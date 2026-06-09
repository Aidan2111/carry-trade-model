import axios from 'axios';
import { DashboardData } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export class ApiService {
  static async getDashboardData(): Promise<DashboardData> {
    try {
      const response = await api.get('/api/dashboard');
      return response.data;
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      throw error;
    }
  }

  static async getFXRates() {
    try {
      const response = await api.get('/api/fx-rates');
      return response.data;
    } catch (error) {
      console.error('Error fetching FX rates:', error);
      throw error;
    }
  }

  static async getSentimentData() {
    try {
      const response = await api.get('/api/sentiment');
      return response.data;
    } catch (error) {
      console.error('Error fetching sentiment data:', error);
      throw error;
    }
  }

  static async getMacroData() {
    try {
      const response = await api.get('/api/macro');
      return response.data;
    } catch (error) {
      console.error('Error fetching macro data:', error);
      throw error;
    }
  }

  static async getModelPredictions() {
    try {
      const response = await api.get('/api/predictions');
      return response.data;
    } catch (error) {
      console.error('Error fetching model predictions:', error);
      throw error;
    }
  }

  static async getCarryTradeSignals() {
    try {
      const response = await api.get('/api/signals');
      return response.data;
    } catch (error) {
      console.error('Error fetching carry trade signals:', error);
      throw error;
    }
  }

  static async getPerformanceMetrics() {
    try {
      const response = await api.get('/api/performance');
      return response.data;
    } catch (error) {
      console.error('Error fetching performance metrics:', error);
      throw error;
    }
  }

  static async getNewsData() {
    try {
      const response = await api.get('/api/news');
      return response.data;
    } catch (error) {
      console.error('Error fetching news data:', error);
      throw error;
    }
  }

  static async triggerModelUpdate() {
    try {
      const response = await api.post('/api/update-model');
      return response.data;
    } catch (error) {
      console.error('Error triggering model update:', error);
      throw error;
    }
  }
}
