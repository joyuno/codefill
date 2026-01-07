'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Code2 } from 'lucide-react';
import { Header } from '@/components/layout/Header';
import { TopNav } from '@/components/layout/TopNav';
import { SidebarProfile } from '@/components/dashboard/SidebarProfile';
import { useAuth } from '@/hooks/useAuth';
import { usersApi } from '@/lib/api/users';
import type { Badge } from '@/lib/types';
import { LandingPage } from '@/components/landing/LandingPage';

export default function MainLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { isLoading, isAuthenticated } = useAuth();
  const [badges, setBadges] = useState<Badge[]>([]);

  // 뱃지 로드 (로그인 사용자만)
  useEffect(() => {
    if (isAuthenticated) {
      usersApi.getBadges()
        .then(setBadges)
        .catch(() => setBadges([]));
    }
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
    </div>
  );
}
