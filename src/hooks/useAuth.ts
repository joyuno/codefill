'use client';

import { useState, useEffect, useCallback } from 'react';
import { createClient } from '@/lib/supabase/client';
import type { User, Session } from '@supabase/supabase-js';

/**
 * 인증 상태를 관리하는 커스텀 훅
 * - Supabase 세션 상태 실시간 감지
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

export function useAuth() {
  const [authState, setAuthState] = useState<AuthState>({
    user: null,
    profile: null,
    session: null,
    isLoading: true,
    isAuthenticated: false,
  });

  const supabase = createClient();

  // 사용자 프로필 조회
  const fetchProfile = useCallback(async (userId: string): Promise<UserProfile | null> => {
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
        username: data.username || data.email?.split('@')[0] || 'User',
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

  // 초기 세션 확인 및 세션 변경 감지
  useEffect(() => {
    // 현재 세션 확인
    const initializeAuth = async () => {
      try {
        const { data: { session } } = await supabase.auth.getSession();
        
        if (session?.user) {
          const profile = await fetchProfile(session.user.id);
          setAuthState({
            user: session.user,
            profile,
            session,
            isLoading: false,
            isAuthenticated: true,
          });
        } else {
          setAuthState({
            user: null,
            profile: null,
            session: null,
            isLoading: false,
            isAuthenticated: false,
          });
        }
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

    // 세션 변경 리스너
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event, session) => {
        console.log('Auth state changed:', event);
        
        if (event === 'SIGNED_IN' && session?.user) {
          const profile = await fetchProfile(session.user.id);
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

    return () => {
      subscription.unsubscribe();
    };
  }, [supabase, fetchProfile]);

  // 로그아웃
  const signOut = useCallback(async () => {
    try {
      await supabase.auth.signOut();
      // 캐릭터 데이터도 삭제
      localStorage.removeItem('codefill_character');
      localStorage.removeItem('codefill_farm_level');
    } catch (error) {
      console.error('로그아웃 오류:', error);
    }
  }, [supabase]);

  // 프로필 새로고침
  const refreshProfile = useCallback(async () => {
    if (authState.user) {
      const profile = await fetchProfile(authState.user.id);
      setAuthState(prev => ({ ...prev, profile }));
    }
  }, [authState.user, fetchProfile]);

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

