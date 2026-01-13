/**
 * API Client for CodeFill Backend
 *
 * Handles all HTTP requests to the FastAPI backend with
 * authentication token management.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface ApiResponse<T> {
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: unknown;
  };
}

interface RequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  body?: unknown;
  headers?: Record<string, string>;
  requireAuth?: boolean;
  timeout?: number;  // 타임아웃 (ms), 기본값 30초
}

class ApiClient {
  private baseUrl: string;
  private accessToken: string | null = null;
  private refreshToken: string | null = null;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
    // Load tokens from localStorage on init (client-side only)
    if (typeof window !== 'undefined') {
      this.accessToken = localStorage.getItem('access_token');
      this.refreshToken = localStorage.getItem('refresh_token');
    }
  }

  /**
   * Set authentication tokens
   */
  setTokens(accessToken: string, refreshToken: string) {
    this.accessToken = accessToken;
    this.refreshToken = refreshToken;
    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', accessToken);
      localStorage.setItem('refresh_token', refreshToken);
    }
  }

  /**
   * Clear authentication tokens
   */
  clearTokens() {
    this.accessToken = null;
    this.refreshToken = null;
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    }
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    return !!this.accessToken;
  }

  /**
   * Get current access token
   */
  getAccessToken(): string | null {
    return this.accessToken;
  }

  /**
   * Refresh access token using refresh token
   */
  async refreshAccessToken(): Promise<boolean> {
    if (!this.refreshToken) return false;

    try {
      const response = await fetch(`${this.baseUrl}/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: this.refreshToken }),
      });

      if (response.ok) {
        const data = await response.json();
        this.setTokens(data.access_token, data.refresh_token);
        return true;
      }

      this.clearTokens();
      return false;
    } catch {
      this.clearTokens();
      return false;
    }
  }

  /**
   * Make an API request with timeout support
   */
  async request<T>(
    endpoint: string,
    options: RequestOptions = {}
  ): Promise<ApiResponse<T>> {
    const { method = 'GET', body, headers = {}, requireAuth = true, timeout = 30000 } = options;

    const requestHeaders: Record<string, string> = {
      'Content-Type': 'application/json',
      ...headers,
    };

    if (requireAuth && this.accessToken) {
      requestHeaders['Authorization'] = `Bearer ${this.accessToken}`;
    }

    // AbortController를 사용한 타임아웃 설정
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        method,
        headers: requestHeaders,
        body: body ? JSON.stringify(body) : undefined,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      // Handle 401 Unauthorized - try to refresh token
      if (response.status === 401 && requireAuth && this.refreshToken) {
        const refreshed = await this.refreshAccessToken();
        if (refreshed) {
          // Retry the request with new token (새로운 타임아웃 적용)
          const retryController = new AbortController();
          const retryTimeoutId = setTimeout(() => retryController.abort(), timeout);

          try {
            requestHeaders['Authorization'] = `Bearer ${this.accessToken}`;
            const retryResponse = await fetch(`${this.baseUrl}${endpoint}`, {
              method,
              headers: requestHeaders,
              body: body ? JSON.stringify(body) : undefined,
              signal: retryController.signal,
            });
            clearTimeout(retryTimeoutId);
            return this.handleResponse<T>(retryResponse);
          } catch (retryError) {
            clearTimeout(retryTimeoutId);
            if (retryError instanceof DOMException && retryError.name === 'AbortError') {
              return {
                error: {
                  code: 'TIMEOUT_ERROR',
                  message: `Request timeout after ${timeout}ms`,
                },
              };
            }
            throw retryError;
          }
        }
      }

      return this.handleResponse<T>(response);
    } catch (error) {
      clearTimeout(timeoutId);

      // 타임아웃 에러 처리
      if (error instanceof DOMException && error.name === 'AbortError') {
        return {
          error: {
            code: 'TIMEOUT_ERROR',
            message: `Request timeout after ${timeout}ms`,
          },
        };
      }

      return {
        error: {
          code: 'NETWORK_ERROR',
          message: error instanceof Error ? error.message : 'Network error',
        },
      };
    }
  }

  private async handleResponse<T>(response: Response): Promise<ApiResponse<T>> {
    try {
      const data = await response.json();

      if (!response.ok) {
        // Handle FastAPI validation errors (detail is array of objects)
        let errorMessage = 'Request failed';
        if (data.error?.message) {
          errorMessage = data.error.message;
        } else if (data.detail) {
          if (typeof data.detail === 'string') {
            errorMessage = data.detail;
          } else if (Array.isArray(data.detail)) {
            // FastAPI validation error format: [{type, loc, msg, input}, ...]
            errorMessage = data.detail.map((e: { msg?: string }) => e.msg || 'Validation error').join(', ');
          }
        }

        return {
          error: {
            code: data.error?.code || `HTTP_${response.status}`,
            message: errorMessage,
            details: data.error?.details,
          },
        };
      }

      return { data };
    } catch {
      if (!response.ok) {
        return {
          error: {
            code: `HTTP_${response.status}`,
            message: response.statusText || 'Request failed',
          },
        };
      }
      return { data: undefined as T };
    }
  }
}

// Export singleton instance
export const apiClient = new ApiClient(API_BASE_URL);

// Export convenience methods
export const api = {
  get: <T>(endpoint: string, requireAuth = true, timeout?: number) =>
    apiClient.request<T>(endpoint, { method: 'GET', requireAuth, timeout }),

  post: <T>(endpoint: string, body?: unknown, requireAuth = true, timeout?: number) =>
    apiClient.request<T>(endpoint, { method: 'POST', body, requireAuth, timeout }),

  put: <T>(endpoint: string, body?: unknown, requireAuth = true, timeout?: number) =>
    apiClient.request<T>(endpoint, { method: 'PUT', body, requireAuth, timeout }),

  patch: <T>(endpoint: string, body?: unknown, requireAuth = true, timeout?: number) =>
    apiClient.request<T>(endpoint, { method: 'PATCH', body, requireAuth, timeout }),

  delete: <T>(endpoint: string, body?: unknown, requireAuth = true, timeout?: number) =>
    apiClient.request<T>(endpoint, { method: 'DELETE', body, requireAuth, timeout }),
};
