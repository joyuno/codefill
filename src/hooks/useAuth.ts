'use client';

import { useState, useEffect, useCallback } from 'react';
import { createClient } from '@/lib/supabase/client';
import type { User, Session } from '@supabase/supabase-js';

/**
 * 인증 상태를 관리하는 커스텀 훅
 * - Supabase 세션 상태 실시간 감지
 * - 백엔드 JWT 토큰 지원 (카카오/구글 OAuth)
 * - 로그인/로그아웃 함수 제공
 * - 사용자 정보 제공
 */

interface UserProfile {
  id: string;
  email: string;
  username: string;
  avatar_url?: string;
  level: number;
  current_xp: number;
  required_xp: number;
  subscription_tier: 'free' | 'basic' | 'pro';
  subscription_expires_at?: string;
  created_at: string;
}

interface AuthState {
  user: User | null;
  profile: UserProfile | null;
  session: Session | null;
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
    session: null,
    isLoading: true,
    isAuthenticated: false,
  });

  const supabase = createClient();

  // 사용자 프로필 조회 (Supabase 직접 조회)
  const fetchProfileFromSupabase = useCallback(async (userId: string): Promise<UserProfile | null> => {
    try {
      const { data, error } = await supabase
        .from('users')
        .select('*')
        .eq('id', userId)
        .single();

      if (error) {
        console.error('프로필 조회 오류:', error);
        return null;
      }

      return {
        id: data.id,
        email: data.email,
        username: data.username || data.name || data.email?.split('@')[0] || 'User',
        avatar_url: data.avatar_url,
        level: data.level || 1,
        current_xp: data.current_xp || 0,
        required_xp: data.required_xp || 100,
        subscription_tier: data.subscription_tier || 'free',
        subscription_expires_at: data.subscription_expires_at,
        created_at: data.created_at,
      };
    } catch (error) {
      console.error('프로필 조회 중 오류:', error);
      return null;
    }
  }, [supabase]);

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
        console.error('백엔드 프로필 조회 실패:', response.status);
        return null;
      }

      const data = await response.json();
      return {
        id: data.id,
        email: data.email,
        username: data.username || data.name || data.email?.split('@')[0] || 'User',
        avatar_url: data.avatar_url,
        level: data.level || 1,
        current_xp: data.current_xp || data.currentXP || 0,
        required_xp: data.required_xp || data.requiredXP || 100,
        subscription_tier: data.subscription_tier || data.subscription || 'free',
        subscription_expires_at: data.subscription_expires_at,
        created_at: data.created_at || data.joinedAt,
      };
    } catch (error) {
      console.error('백엔드 프로필 조회 중 오류:', error);
      return null;
    }
  }, []);

  // 초기 세션 확인 및 세션 변경 감지
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        // 1. Supabase 세션 확인
        const { data: { session } } = await supabase.auth.getSession();

        if (session?.user) {
          const profile = await fetchProfileFromSupabase(session.user.id);
          setAuthState({
            user: session.user,
            profile,
            session,
            isLoading: false,
            isAuthenticated: true,
          });
          return;
        }

        // 2. localStorage JWT 토큰 확인 (카카오/구글 로그인)
        if (typeof window !== 'undefined') {
          const accessToken = localStorage.getItem('access_token');

          if (accessToken && !isTokenExpired(accessToken)) {
            const userId = getUserIdFromToken(accessToken);
            const profile = await fetchProfileFromBackend(accessToken);

            if (profile) {
              // JWT 기반 인증 상태 설정
              setAuthState({
                user: {
                  id: userId || profile.id,
                  email: profile.email,
                  aud: 'authenticated',
                  role: 'authenticated',
                  created_at: profile.created_at,
                } as User,
                profile,
                session: null,
                isLoading: false,
                isAuthenticated: true,
              });
              return;
            }
          }

          // 만료된 토큰 정리
          if (accessToken && isTokenExpired(accessToken)) {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
          }
        }

        // 인증되지 않음
        setAuthState({
          user: null,
          profile: null,
          session: null,
          isLoading: false,
          isAuthenticated: false,
        });
      } catch (error) {
        console.error('인증 초기화 오류:', error);
        setAuthState({
          user: null,
          profile: null,
          session: null,
          isLoading: false,
          isAuthenticated: false,
        });
      }
    };

    initializeAuth();

    // Supabase 세션 변경 리스너
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event, session) => {
        console.log('Auth state changed:', event);

        if (event === 'SIGNED_IN' && session?.user) {
          const profile = await fetchProfileFromSupabase(session.user.id);
          setAuthState({
            user: session.user,
            profile,
            session,
            isLoading: false,
            isAuthenticated: true,
          });
        } else if (event === 'SIGNED_OUT') {
          setAuthState({
            user: null,
            profile: null,
            session: null,
            isLoading: false,
            isAuthenticated: false,
          });
        }
      }
    );

    // localStorage 변경 감지 (다른 탭에서 로그인/로그아웃 시)
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'access_token') {
        initializeAuth();
      }
    };

    if (typeof window !== 'undefined') {
      window.addEventListener('storage', handleStorageChange);
    }

    return () => {
      subscription.unsubscribe();
      if (typeof window !== 'undefined') {
        window.removeEventListener('storage', handleStorageChange);
      }
    };
  }, [supabase, fetchProfileFromSupabase, fetchProfileFromBackend]);

  // 로그아웃
  const signOut = useCallback(async () => {
    try {
      // Supabase 로그아웃
      await supabase.auth.signOut();

      // localStorage 토큰 삭제 (백엔드 JWT)
      if (typeof window !== 'undefined') {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('codefill_character');
        localStorage.removeItem('codefill_farm_level');
      }

      setAuthState({
        user: null,
        profile: null,
        session: null,
        isLoading: false,
        isAuthenticated: false,
      });
    } catch (error) {
      console.error('로그아웃 오류:', error);
    }
  }, [supabase]);

  // 프로필 새로고침
  const refreshProfile = useCallback(async () => {
    if (authState.session?.user) {
      const profile = await fetchProfileFromSupabase(authState.session.user.id);
      setAuthState(prev => ({ ...prev, profile }));
    } else if (typeof window !== 'undefined') {
      const accessToken = localStorage.getItem('access_token');
      if (accessToken) {
        const profile = await fetchProfileFromBackend(accessToken);
        setAuthState(prev => ({ ...prev, profile }));
      }
    }
  }, [authState.session, fetchProfileFromSupabase, fetchProfileFromBackend]);

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
