/**
 * Authentication API functions
 */

import { api, apiClient } from './client';

// Types
export interface OnboardingData {
  status: 'student' | 'job_seeker' | 'employed' | 'career_change';
  goal: 'big_tech' | 'mid_startup' | 'skill_up' | 'unknown';
  level: 'beginner' | 'elementary' | 'intermediate' | 'advanced' | 'unknown';
  solved_ac_id?: string;
  strong_algorithms?: string[];
  desired_job?: string;  // 희망 직무 (자유 텍스트)
}

export interface SignupData {
  email: string;
  password: string;
  name: string;
  // Legacy fields (deprecated)
  experience_level?: 'non_major' | 'lt_6m' | '6m_2y' | 'gt_2y';
  learning_goal?: 'coding_test' | 'work_skills' | 'framework' | 'fun';
  preferred_language?: string;
  preferred_framework?: string;
  // New onboarding data
  onboarding_data?: OnboardingData;
}

export interface LoginData {
  email: string;
  password: string;
}

export interface AuthResponse {
  success: boolean;
  message: string;
  data?: {
    user_id?: string;
  };
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

// API Functions
export const authApi = {
  /**
   * Register a new user
   */
  signup: async (data: SignupData): Promise<{ data?: AuthResponse; error?: { code: string; message: string } }> => {
    const result = await api.post<AuthResponse>('/auth/signup', data, false);
    return result;
  },

  /**
   * Login with email and password
   */
  login: async (data: LoginData): Promise<{ data?: TokenResponse; error?: { code: string; message: string } }> => {
    const result = await api.post<TokenResponse>('/auth/login', data, false);

    if (result.data) {
      // Store tokens on successful login
      apiClient.setTokens(result.data.access_token, result.data.refresh_token);
    }

    return result;
  },

  /**
   * Logout current user
   */
  logout: async (): Promise<void> => {
    await api.post('/auth/logout', undefined, true);
    apiClient.clearTokens();
  },

  /**
   * Request password reset email
   */
  requestPasswordReset: async (email: string): Promise<{ data?: AuthResponse; error?: { code: string; message: string } }> => {
    return api.post<AuthResponse>('/auth/password/reset', { email }, false);
  },

  /**
   * Confirm password reset with token
   */
  confirmPasswordReset: async (token: string, newPassword: string): Promise<{ data?: AuthResponse; error?: { code: string; message: string } }> => {
    return api.put<AuthResponse>('/auth/password/reset', {
      token,
      new_password: newPassword,
    }, false);
  },

  /**
   * Check if user is authenticated
   */
  isAuthenticated: (): boolean => {
    return apiClient.isAuthenticated();
  },

  /**
   * Get current access token
   */
  getToken: (): string | null => {
    return apiClient.getAccessToken();
  },
};
