import { create } from 'zustand';
import { User, LoginCredentials, RegisterCredentials } from '@/types';
import { authService, tokenStorage } from '@/services';

interface AuthState {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  error: string | null;

  // Actions
  login: (credentials: LoginCredentials) => Promise<boolean>;
  register: (credentials: RegisterCredentials) => Promise<boolean>;
  logout: () => Promise<void>;
  checkAuth: () => Promise<void>;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isLoading: false,
  isAuthenticated: false,
  error: null,

  login: async (credentials: LoginCredentials) => {
    set({ isLoading: true, error: null });
    try {
      await authService.login(credentials);
      const user = await authService.getCurrentUser();
      set({ user, isAuthenticated: true, isLoading: false });
      return true;
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : 'Error al iniciar sesion';
      set({ error: message, isLoading: false });
      return false;
    }
  },

  register: async (credentials: RegisterCredentials) => {
    set({ isLoading: true, error: null });
    try {
      await authService.register(credentials);
      // Auto-login after registration
      await authService.login({
        username: credentials.email,
        password: credentials.password,
      });
      const user = await authService.getCurrentUser();
      set({ user, isAuthenticated: true, isLoading: false });
      return true;
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : 'Error al registrarse';
      set({ error: message, isLoading: false });
      return false;
    }
  },

  logout: async () => {
    set({ isLoading: true });
    try {
      await authService.logout();
    } finally {
      set({ user: null, isAuthenticated: false, isLoading: false });
    }
  },

  checkAuth: async () => {
    set({ isLoading: true });
    try {
      const hasToken = await tokenStorage.getAccessToken();
      if (hasToken) {
        const user = await authService.getCurrentUser();
        set({ user, isAuthenticated: true, isLoading: false });
      } else {
        set({ isAuthenticated: false, isLoading: false });
      }
    } catch {
      await tokenStorage.clearTokens();
      set({ user: null, isAuthenticated: false, isLoading: false });
    }
  },

  clearError: () => set({ error: null }),
}));

export default useAuthStore;
