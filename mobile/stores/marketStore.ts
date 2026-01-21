import { create } from 'zustand';
import { Ticker, OHLCV } from '@/types';
import { marketService } from '@/services';
import { API_CONFIG } from '@/constants/api';

interface MarketState {
  ticker: Ticker | null;
  ohlcv: OHLCV[];
  isLoading: boolean;
  error: string | null;
  lastUpdated: Date | null;
  wsConnected: boolean;

  // Actions
  fetchTicker: (symbol?: string) => Promise<void>;
  fetchOHLCV: (symbol?: string, timeframe?: string, limit?: number) => Promise<void>;
  connectWebSocket: () => void;
  disconnectWebSocket: () => void;
  clearError: () => void;
}

let ws: WebSocket | null = null;

export const useMarketStore = create<MarketState>((set, get) => ({
  ticker: null,
  ohlcv: [],
  isLoading: false,
  error: null,
  lastUpdated: null,
  wsConnected: false,

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

  connectWebSocket: () => {
    if (ws) return;

    try {
      // Determine correct WS URL based on platform/config
      const wsUrl = API_CONFIG.WS_URL + '/prices';
      console.log('Connecting to WS:', wsUrl);
      
      ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        console.log('WS Connected');
        set({ wsConnected: true, error: null });
      };

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          
          if (message.type === 'ticker_update') {
            const newTicker = message.data;
            set({ 
              ticker: newTicker, 
              lastUpdated: new Date() 
            });

            // Update latest candle in real-time
            const currentOhlcv = get().ohlcv;
            if (currentOhlcv.length > 0) {
              const lastCandle = { ...currentOhlcv[currentOhlcv.length - 1] };
              
              // Simple update: update close price
              // In a real app, we'd check if a new candle needs to be created based on time
              lastCandle.close = newTicker.price;
              
              if (newTicker.price > lastCandle.high) lastCandle.high = newTicker.price;
              if (newTicker.price < lastCandle.low) lastCandle.low = newTicker.price;
              
              const newOhlcv = [...currentOhlcv.slice(0, -1), lastCandle];
              set({ ohlcv: newOhlcv });
            }
          }
        } catch (e) {
          console.error('WS Message Parse Error', e);
        }
      };

      ws.onerror = (e) => {
        console.error('WS Error', e);
        set({ error: 'Error de conexión WebSocket' });
      };

      ws.onclose = () => {
        console.log('WS Closed');
        set({ wsConnected: false });
        ws = null;
      };
    } catch (e) {
      console.error('WS Connection Error', e);
      set({ error: 'No se pudo conectar al WebSocket' });
    }
  },

  disconnectWebSocket: () => {
    if (ws) {
      ws.close();
      ws = null;
      set({ wsConnected: false });
    }
  },

  clearError: () => set({ error: null }),
}));

export default useMarketStore;
