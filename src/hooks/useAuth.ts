'use client';

import { useState, useEffect, useCallback, useRef } from 'react';

/**
 * 인증 상태를 관리하는 커스텀 훅
 * - localStorage JWT 토큰 기반 인증
 * - 백엔드 API를 통한 프로필 조회
 * - 로그인/로그아웃 함수 제공
 */

interface UserProfile {
  id: string;
  email: string;
  username: string;
  avatar_url?: string;
  level: number;
  current_xp: number;
  required_xp: number;
  solved_count: number;
  streak: number;
  max_streak: number;
  subscription_tier: 'free' | 'basic' | 'pro';
  subscription_expires_at?: string;
  created_at: string;
}

interface AuthState {
  user: {
    id: string;
    email: string;
    aud?: string;
    role?: string;
    created_at?: string;
  } | null;
  profile: UserProfile | null;
  isLoading: boolean;
  isAuthenticated: boolean;
}

// JWT 토큰에서 사용자 ID 추출
function getUserIdFromToken(token: string): string | null {
  try {
    const payload = token.split('.')[1];
    const decoded = JSON.parse(atob(payload));
    return decoded.sub || null;
  } catch {
    return null;
  }
}

// JWT 토큰 만료 확인
function isTokenExpired(token: string): boolean {
  try {
    const payload = token.split('.')[1];
    const decoded = JSON.parse(atob(payload));
    if (!decoded.exp) return false;
    return decoded.exp * 1000 < Date.now();
  } catch {
    return true;
  }
}

export function useAuth() {
  const [authState, setAuthState] = useState<AuthState>({
    user: null,
    profile: null,
    isLoading: true,
    isAuthenticated: false,
  });

  const initializedRef = useRef(false);

  // 백엔드 API로 프로필 조회 (JWT 토큰 사용)
  const fetchProfileFromBackend = useCallback(async (token: string): Promise<UserProfile | null> => {
    try {
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${API_BASE_URL}/users/me/profile`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        console.error('프로필 조회 실패:', response.status);
        return null;
      }

      const data = await response.json();
      return {
        id: data.id,
        email: data.email,
        username: data.username || data.name || data.email?.split('@')[0] || 'User',
        avatar_url: data.avatar_url || data.avatarColor,
        level: data.level || 1,
        current_xp: data.current_xp || data.currentXP || 0,
        required_xp: data.required_xp || data.requiredXP || 100,
        solved_count: data.solved_count || data.solvedCount || 0,
        streak: data.streak || data.currentStreak || 0,
        max_streak: data.max_streak || data.maxStreak || 0,
        subscription_tier: data.subscription_tier || data.subscription || 'free',
        subscription_expires_at: data.subscription_expires_at,
        created_at: data.created_at || data.joinedAt,
      };
    } catch (error) {
      console.error('프로필 조회 중 오류:', error);
      return null;
    }
  }, []);

  // 인증 초기화
  useEffect(() => {
    // 중복 실행 방지
    if (initializedRef.current) return;
    initializedRef.current = true;

    const initializeAuth = async () => {
      // 브라우저 환경 체크
      if (typeof window === 'undefined') {
        setAuthState(prev => ({ ...prev, isLoading: false }));
        return;
      }

      const accessToken = localStorage.getItem('access_token');

      // 토큰 없거나 만료됨
      if (!accessToken || isTokenExpired(accessToken)) {
        // 만료된 토큰 정리
        if (accessToken) {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
        }
        setAuthState({
          user: null,
          profile: null,
          isLoading: false,
          isAuthenticated: false,
        });
        return;
      }

      // 프로필 조회
      const userId = getUserIdFromToken(accessToken);
      const profile = await fetchProfileFromBackend(accessToken);

      if (profile) {
        setAuthState({
          user: {
            id: userId || profile.id,
            email: profile.email,
            aud: 'authenticated',
            role: 'authenticated',
            created_at: profile.created_at,
          },
          profile,
          isLoading: false,
          isAuthenticated: true,
        });
      } else {
        // 프로필 조회 실패 시 토큰 정리
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        setAuthState({
          user: null,
          profile: null,
          isLoading: false,
          isAuthenticated: false,
        });
      }
    };

    initializeAuth();

    // localStorage 변경 감지 (다른 탭에서 로그인/로그아웃 시)
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'access_token') {
        initializedRef.current = false;
        initializeAuth();
      }
    };

    window.addEventListener('storage', handleStorageChange);

    return () => {
      window.removeEventListener('storage', handleStorageChange);
    };
  }, [fetchProfileFromBackend]);

  // 로그아웃
  const signOut = useCallback(async () => {
    try {
      // localStorage 토큰 삭제
      if (typeof window !== 'undefined') {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('codefill_character');
        localStorage.removeItem('codefill_farm_level');
      }

      setAuthState({
        user: null,
        profile: null,
        isLoading: false,
        isAuthenticated: false,
      });
    } catch (error) {
      console.error('로그아웃 오류:', error);
    }
  }, []);

  // 프로필 새로고침
  const refreshProfile = useCallback(async () => {
    if (typeof window !== 'undefined') {
      const accessToken = localStorage.getItem('access_token');
      if (accessToken && !isTokenExpired(accessToken)) {
        const profile = await fetchProfileFromBackend(accessToken);
        if (profile) {
          setAuthState(prev => ({ ...prev, profile }));
        }
      }
    }
  }, [fetchProfileFromBackend]);

  return {
    ...authState,
    signOut,
    refreshProfile,
  };
}

// 구독 티어별 기능 정의
export const SUBSCRIPTION_FEATURES = {
  free: {
    name: '무료',
    price: 0,
    features: [
      '하루 5문제 풀이',
      '기본 힌트 제공',
      '커뮤니티 접근',
    ],
    limits: {
      dailyProblems: 5,
      hints: 3,
      aiChat: false,
    },
  },
  basic: {
    name: '베이직',
    price: 9900,
    features: [
      '하루 20문제 풀이',
      '무제한 힌트',
      'AI 튜터 기본 기능',
      '진도 분석',
    ],
    limits: {
      dailyProblems: 20,
      hints: Infinity,
      aiChat: true,
    },
  },
  pro: {
    name: '프로',
    price: 19900,
    features: [
      '무제한 문제 풀이',
      '무제한 힌트',
      'AI 튜터 고급 기능',
      '1:1 코드 리뷰',
      '우선 지원',
      '모든 뱃지 언락',
    ],
    limits: {
      dailyProblems: Infinity,
      hints: Infinity,
      aiChat: true,
    },
  },
};
