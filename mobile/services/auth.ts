import api, { tokenStorage } from './api';
import { API_CONFIG } from '@/constants/api';
import { User, AuthTokens, LoginCredentials, RegisterCredentials } from '@/types';

export const authService = {
  async login(credentials: LoginCredentials): Promise<AuthTokens> {
    // FastAPI OAuth2 expects form data
    const formData = new URLSearchParams();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);

    const response = await api.post<AuthTokens>(
      API_CONFIG.ENDPOINTS.LOGIN,
      formData.toString(),
      {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      }
    );

    const tokens = response.data;
    await tokenStorage.setTokens(tokens.access_token, tokens.refresh_token);
    return tokens;
  },

  async register(credentials: RegisterCredentials): Promise<User> {
    const response = await api.post<User>(
      API_CONFIG.ENDPOINTS.REGISTER,
      credentials
    );
    return response.data;
  },

  async logout(): Promise<void> {
    await tokenStorage.clearTokens();
  },

  async getCurrentUser(): Promise<User> {
    const response = await api.get<User>(API_CONFIG.ENDPOINTS.ME);
    return response.data;
  },

  async refreshToken(): Promise<AuthTokens> {
    const refreshToken = await tokenStorage.getRefreshToken();
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    const response = await api.post<AuthTokens>(API_CONFIG.ENDPOINTS.REFRESH, {
      refresh_token: refreshToken,
    });

    const tokens = response.data;
    await tokenStorage.setTokens(tokens.access_token, tokens.refresh_token);
    return tokens;
  },

  async isAuthenticated(): Promise<boolean> {
    const token = await tokenStorage.getAccessToken();
    return !!token;
  },
};

export default authService;
