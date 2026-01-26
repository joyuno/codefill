'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Code2 } from 'lucide-react';
import { Header } from '@/components/layout/Header';
import { TopNav } from '@/components/layout/TopNav';
import { SidebarProfile } from '@/components/dashboard/SidebarProfile';
import { SessionExpiredModal } from '@/components/auth/SessionExpiredModal';
import { useAuth } from '@/hooks/useAuth';
import { usersApi } from '@/lib/api/users';
import type { Badge } from '@/lib/types';
import { LandingPage } from '@/components/landing/LandingPage';

// 뱃지 캐시 설정
const BADGES_CACHE_KEY = 'codefill_badges_cache';
const BADGES_CACHE_TTL = 1000 * 60 * 10; // 10분

interface BadgesCache {
  data: Badge[];
  timestamp: number;
}

function getBadgesFromCache(): Badge[] | null {
  try {
    const cached = sessionStorage.getItem(BADGES_CACHE_KEY);
    if (!cached) return null;
    const parsed: BadgesCache = JSON.parse(cached);
    if (Date.now() - parsed.timestamp > BADGES_CACHE_TTL) {
      sessionStorage.removeItem(BADGES_CACHE_KEY);
      return null;
    }
    return parsed.data;
  } catch {
    return null;
  }
}

function setBadgesToCache(data: Badge[]): void {
  try {
    sessionStorage.setItem(BADGES_CACHE_KEY, JSON.stringify({
      data,
      timestamp: Date.now(),
    }));
    // StatCards에서 재사용하도록 카운트도 캐싱
    sessionStorage.setItem('codefill_badge_count', data.length.toString());
  } catch {
    // 캐시 실패 무시
  }
}

export default function MainLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { isLoading, isAuthenticated } = useAuth();
  // 캐시에서 초기값 로드 (즉시 표시)
  const [badges, setBadges] = useState<Badge[]>(() => {
    if (typeof window === 'undefined') return [];
    return getBadgesFromCache() || [];
  });

  // 뱃지 로드 (캐시 우선, API는 백그라운드)
  useEffect(() => {
    if (!isAuthenticated) return;

    // 캐시가 있으면 이미 초기값으로 설정됨, 백그라운드에서 갱신
    const cached = getBadgesFromCache();
    if (cached) {
      // 이미 badges state에 설정되어 있으므로 API만 백그라운드 호출
      usersApi.getBadges()
        .then((data) => {
          setBadges(data);
          setBadgesToCache(data);
        })
        .catch(() => {});
      return;
    }

    // 캐시 없으면 API 호출
    usersApi.getBadges()
      .then((data) => {
        setBadges(data);
        setBadgesToCache(data);
      })
      .catch(() => setBadges([]));
  }, [isAuthenticated]);

  // 로딩 중
  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
        >
          <Code2 className="h-8 w-8 text-primary" />
        </motion.div>
      </div>
    );
  }

  // 비로그인: 랜딩페이지 표시 (레이아웃 없이)
  if (!isAuthenticated) {
    return <LandingPage />;
  }

  // 로그인: 공통 레이아웃 적용
  return (
    <div className="min-h-screen bg-background">
      <Header />
      <TopNav />
      <div className="flex">
        <aside className="hidden w-72 shrink-0 border-r border-border lg:block">
          <SidebarProfile badges={badges} />
        </aside>
        <main className="flex-1 p-6">
          {children}
        </main>
      </div>
      {/* 세션 만료 팝업 */}
      <SessionExpiredModal />
    </div>
  );
}
