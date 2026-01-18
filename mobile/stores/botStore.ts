import { create } from 'zustand';
import { BotStatus, BotPerformance, Trade } from '@/types';
import { botService, StartBotParams } from '@/services/bot';

interface BotState {
  status: BotStatus | null;
  performance: BotPerformance | null;
  trades: Trade[];
  isLoading: boolean;
  error: string | null;

  // Actions
  fetchStatus: () => Promise<void>;
  fetchPerformance: () => Promise<void>;
  fetchTrades: (limit?: number) => Promise<void>;
  startBot: (params?: StartBotParams) => Promise<boolean>;
  stopBot: () => Promise<boolean>;
  pauseBot: () => Promise<boolean>;
  resumeBot: () => Promise<boolean>;
  clearError: () => void;
}

export const useBotStore = create<BotState>((set) => ({
  status: null,
  performance: null,
  trades: [],
  isLoading: false,
  error: null,

  fetchStatus: async () => {
    try {
      const status = await botService.getStatus();
      set({ status });
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : 'Error al obtener estado';
      set({ error: message });
    }
  },

  fetchPerformance: async () => {
    try {
      const performance = await botService.getPerformance();
      set({ performance });
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : 'Error al obtener rendimiento';
      set({ error: message });
    }
  },

  fetchTrades: async (limit = 50) => {
    try {
      const trades = await botService.getTrades(limit);
      set({ trades });
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : 'Error al obtener trades';
      set({ error: message });
    }
  },

  startBot: async (params?: StartBotParams) => {
    set({ isLoading: true, error: null });
    try {
      await botService.start(params);
      const status = await botService.getStatus();
      set({ status, isLoading: false });
      return true;
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : 'Error al iniciar bot';
      set({ error: message, isLoading: false });
      return false;
    }
  },

  stopBot: async () => {
    set({ isLoading: true, error: null });
    try {
      await botService.stop();
      const status = await botService.getStatus();
      set({ status, isLoading: false });
      return true;
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : 'Error al detener bot';
      set({ error: message, isLoading: false });
      return false;
    }
  },

  pauseBot: async () => {
    set({ isLoading: true, error: null });
    try {
      await botService.pause();
      const status = await botService.getStatus();
      set({ status, isLoading: false });
      return true;
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : 'Error al pausar bot';
      set({ error: message, isLoading: false });
      return false;
    }
  },

  resumeBot: async () => {
    set({ isLoading: true, error: null });
    try {
      await botService.resume();
      const status = await botService.getStatus();
      set({ status, isLoading: false });
      return true;
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : 'Error al resumir bot';
      set({ error: message, isLoading: false });
      return false;
    }
  },

  clearError: () => set({ error: null }),
}));

export default useBotStore;
