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

export interface CheckResponse {
  available: boolean;
  message: string;
}

export interface RecoveryRequiredResponse {
  recovery_required: boolean;
  message: string;
  email: string;
  deleted_at: string;
  days_remaining: number;
}

export interface RecoverData {
  email: string;
  password: string;
}

export interface RecoverOAuthData {
  provider: string;
  provider_id: string;
}

// API Functions
export const authApi = {
  /**
   * Register a new user
   * Returns JWT tokens for automatic login after signup
   */
  signup: async (data: SignupData): Promise<{ data?: TokenResponse; error?: { code: string; message: string } }> => {
    const result = await api.post<TokenResponse>('/auth/signup', data, false);

    if (result.data) {
      // Store tokens on successful signup (auto-login)
      apiClient.setTokens(result.data.access_token, result.data.refresh_token);
    }

    return result;
  },

  /**
   * Login with email and password
   * Returns TokenResponse on success, or RecoveryRequiredResponse if account needs recovery
   */
  login: async (data: LoginData): Promise<{
    data?: TokenResponse | RecoveryRequiredResponse;
    error?: { code: string; message: string }
  }> => {
    const result = await api.post<TokenResponse | RecoveryRequiredResponse>('/auth/login', data, false);

    if (result.data && 'access_token' in result.data) {
      // Store tokens on successful login (not recovery required)
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

  /**
   * Change password (for logged-in user)
   */
  changePassword: async (currentPassword: string, newPassword: string): Promise<{ data?: AuthResponse; error?: { code: string; message: string } }> => {
    return api.put<AuthResponse>('/auth/password/change', {
      current_password: currentPassword,
      new_password: newPassword,
    }, true);
  },

  /**
   * Delete account (회원 탈퇴) - Legacy, 비밀번호 방식
   * @deprecated Use withdraw() instead
   */
  deleteAccount: async (password: string): Promise<{ data?: AuthResponse; error?: { code: string; message: string } }> => {
    const result = await api.delete<AuthResponse>('/auth/account', { password }, true);
    if (result.data) {
      apiClient.clearTokens();
    }
    return result;
  },

  /**
   * 회원탈퇴 (확인 문구 방식)
   * - 일반 가입자, 소셜 가입자 모두 동일하게 사용
   * - '탈퇴합니다' 확인 문구 입력 필요
   * - TODO: 이메일 인증 기능 추가 예정
   */
  withdraw: async (confirmation: string): Promise<{ data?: AuthResponse; error?: { code: string; message: string } }> => {
    const result = await api.delete<AuthResponse>('/auth/withdraw', { confirmation }, true);
    if (result.data?.success) {
      apiClient.clearTokens();
    }
    return result;
  },

  /**
   * Check email availability (for signup)
   */
  checkEmail: async (email: string): Promise<{ data?: CheckResponse; error?: { code: string; message: string } }> => {
    return api.post<CheckResponse>('/auth/check-email', { email }, false);
  },

  /**
   * Check nickname availability
   */
  checkNickname: async (nickname: string): Promise<{ data?: CheckResponse; error?: { code: string; message: string } }> => {
    return api.post<CheckResponse>('/auth/check-nickname', { nickname }, false);
  },

  /**
   * Recover withdrawn account (email login)
   * - For users who signed up with email/password
   * - Requires password verification
   */
  recover: async (data: RecoverData): Promise<{ data?: TokenResponse; error?: { code: string; message: string } }> => {
    const result = await api.post<TokenResponse>('/auth/recover', data, false);

    if (result.data) {
      // Store tokens on successful recovery
      apiClient.setTokens(result.data.access_token, result.data.refresh_token);
    }

    return result;
  },

  /**
   * Recover withdrawn account (OAuth login)
   * - For users who signed up with Kakao/Google
   * - No password required, verified by OAuth provider
   */
  recoverOAuth: async (data: RecoverOAuthData): Promise<{ data?: TokenResponse; error?: { code: string; message: string } }> => {
    const result = await api.post<TokenResponse>('/auth/recover-oauth', data, false);

    if (result.data) {
      // Store tokens on successful recovery
      apiClient.setTokens(result.data.access_token, result.data.refresh_token);
    }

    return result;
  },
};
