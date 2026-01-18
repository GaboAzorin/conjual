import { create } from 'zustand';
import { Ticker, OHLCV } from '@/types';
import { marketService } from '@/services';

interface MarketState {
  ticker: Ticker | null;
  ohlcv: OHLCV[];
  isLoading: boolean;
  error: string | null;
  lastUpdated: Date | null;

  // Actions
  fetchTicker: (symbol?: string) => Promise<void>;
  fetchOHLCV: (symbol?: string, timeframe?: string, limit?: number) => Promise<void>;
  clearError: () => void;
}

export const useMarketStore = create<MarketState>((set) => ({
  ticker: null,
  ohlcv: [],
  isLoading: false,
  error: null,
  lastUpdated: null,

  fetchTicker: async (symbol = 'BTC-CLP') => {
    set({ isLoading: true });
    try {
      const ticker = await marketService.getTicker(symbol);
      set({ ticker, isLoading: false, lastUpdated: new Date() });
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : 'Error al obtener precio';
      set({ error: message, isLoading: false });
    }
  },

  fetchOHLCV: async (symbol = 'BTC-CLP', timeframe = '1h', limit = 100) => {
    set({ isLoading: true });
    try {
      const ohlcv = await marketService.getOHLCV(symbol, timeframe, limit);
      set({ ohlcv, isLoading: false, lastUpdated: new Date() });
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : 'Error al obtener OHLCV';
      set({ error: message, isLoading: false });
    }
  },

  clearError: () => set({ error: null }),
}));

export default useMarketStore;
