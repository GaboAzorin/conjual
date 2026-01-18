import api from './api';
import { API_CONFIG } from '@/constants/api';
import { Ticker, OHLCV } from '@/types';

export const marketService = {
  async getTicker(symbol: string = 'BTC-CLP'): Promise<Ticker> {
    const response = await api.get<Ticker>(API_CONFIG.ENDPOINTS.TICKER, {
      params: { symbol },
    });
    return response.data;
  },

  async getOHLCV(
    symbol: string = 'BTC-CLP',
    timeframe: string = '1h',
    limit: number = 100
  ): Promise<OHLCV[]> {
    const response = await api.get<OHLCV[]>(API_CONFIG.ENDPOINTS.OHLCV, {
      params: { symbol, timeframe, limit },
    });
    return response.data;
  },
};

export default marketService;
