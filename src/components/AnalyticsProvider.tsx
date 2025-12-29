'use client';

/**
 * Analytics Provider
 *
 * 분석 도구 초기화 및 페이지뷰 추적을 담당하는 컴포넌트
 * 앱의 최상위에 배치하여 모든 페이지에서 분석 가능
 */

import { useEffect, Suspense } from 'react';
import { usePathname, useSearchParams } from 'next/navigation';
import { initAnalytics, identifyUser } from '@/lib/analytics';
import { pageview } from '@/lib/analytics/ga4';
import { useAuth } from '@/hooks/useAuth';

function AnalyticsPageView() {
  const pathname = usePathname();
  const searchParams = useSearchParams();

  useEffect(() => {
    if (!pathname) return;

    const url = searchParams?.toString()
      ? `${pathname}?${searchParams.toString()}`
      : pathname;

    // GA4 페이지뷰
    pageview(url);
  }, [pathname, searchParams]);

  return null;
}

export function AnalyticsProvider({ children }: { children: React.ReactNode }) {
  const { user, profile } = useAuth();

  // 분석 도구 초기화 (앱 시작 시 한 번)
  useEffect(() => {
    initAnalytics();
  }, []);

  // 사용자 식별 (로그인 상태 변경 시)
  useEffect(() => {
    if (user?.id) {
      identifyUser(user.id, {
        userLevel: String(profile?.level ?? 'beginner'),
        signupDate: user.created_at,
        problemsSolved: (profile as { stats?: { problemsSolved?: number } })?.stats?.problemsSolved || 0,
      });
    }
  }, [user, profile]);

  // 페이지 이탈 시 로그 flush (beforeunload)
  useEffect(() => {
    const handleBeforeUnload = () => {
      // CF 로그 flush는 useInteractionLog에서 처리
      // 여기서는 추가 cleanup 필요 시 처리
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => window.removeEventListener('beforeunload', handleBeforeUnload);
  }, []);

  return (
    <>
      <Suspense fallback={null}>
        <AnalyticsPageView />
      </Suspense>
      {children}
    </>
  );
}

export default AnalyticsProvider;
