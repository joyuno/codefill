/**
 * Google Analytics 4 분석 도구
 *
 * 기능:
 * - 페이지뷰 추적
 * - 커스텀 이벤트
 * - 전환 퍼널
 * - 사용자 속성
 *
 * 설정: https://analytics.google.com
 */

declare global {
  interface Window {
    gtag: (...args: unknown[]) => void;
    dataLayer: unknown[];
  }
}

export const GA_MEASUREMENT_ID = process.env.NEXT_PUBLIC_GA_ID;

/**
 * GA4 초기화 확인
 * 스크립트는 layout.tsx의 next/script로 로드됨
 */
export function initGA4(): void {
  if (typeof window === 'undefined') return;
  if (!GA_MEASUREMENT_ID) {
    console.warn('[GA4] NEXT_PUBLIC_GA_ID not set');
    return;
  }
  // 스크립트는 layout.tsx에서 로드됨
  // 여기서는 초기화 확인만 수행
  if (window.gtag) {
    console.log('[GA4] Ready');
  }
}

/**
 * 페이지뷰 추적
 * Next.js router 이벤트에서 호출
 */
export function pageview(url: string, title?: string): void {
  if (typeof window === 'undefined' || !window.gtag || !GA_MEASUREMENT_ID) return;

  window.gtag('config', GA_MEASUREMENT_ID, {
    page_path: url,
    page_title: title,
  });
}

/**
 * 커스텀 이벤트 전송
 */
export function event(
  action: string,
  params?: Record<string, string | number | boolean>
): void {
  if (typeof window === 'undefined' || !window.gtag) return;

  window.gtag('event', action, params);
}

/**
 * 사용자 속성 설정
 */
export function setUserProperties(properties: Record<string, string | number>): void {
  if (typeof window === 'undefined' || !window.gtag || !GA_MEASUREMENT_ID) return;

  window.gtag('config', GA_MEASUREMENT_ID, {
    user_properties: properties,
  });
}

/**
 * 사용자 ID 설정 (로그인 후)
 */
export function setUserId(userId: string): void {
  if (typeof window === 'undefined' || !window.gtag || !GA_MEASUREMENT_ID) return;

  window.gtag('config', GA_MEASUREMENT_ID, {
    user_id: userId,
  });
}

// ============================================================
// CodeFill 전용 이벤트
// ============================================================

export const ga4Events = {
  // 온보딩 퍼널
  onboardingStart: () => event('onboarding_start'),
  onboardingStep: (step: number, stepName: string) =>
    event('onboarding_step', { step, step_name: stepName }),
  onboardingComplete: (timeSpent: number) =>
    event('onboarding_complete', { time_spent_seconds: timeSpent }),
  onboardingDrop: (lastStep: number) =>
    event('onboarding_drop', { last_step: lastStep }),

  // 문제 풀이 퍼널
  problemView: (problemId: string, difficulty: string, topics: string[]) =>
    event('problem_view', {
      problem_id: problemId,
      difficulty,
      topics: topics.join(','),
    }),
  problemStart: (problemId: string, source: string) =>
    event('problem_start', { problem_id: problemId, source }),
  problemSubmit: (problemId: string, attemptCount: number) =>
    event('problem_submit', { problem_id: problemId, attempt_count: attemptCount }),
  problemSolve: (
    problemId: string,
    isCorrect: boolean,
    timeSpent: number,
    hintUsed: number
  ) =>
    event('problem_solve', {
      problem_id: problemId,
      is_correct: isCorrect,
      time_spent_seconds: timeSpent,
      hint_used_count: hintUsed,
    }),
  problemSkip: (problemId: string, timeSpent: number) =>
    event('problem_skip', { problem_id: problemId, time_spent_seconds: timeSpent }),

  // 힌트
  hintRequest: (problemId: string, hintLevel: number) =>
    event('hint_request', { problem_id: problemId, hint_level: hintLevel }),
  hintView: (problemId: string, hintLevel: number) =>
    event('hint_view', { problem_id: problemId, hint_level: hintLevel }),

  // 챗봇
  chatStart: () => event('chat_start'),
  chatMessage: (messageType: 'user' | 'bot') =>
    event('chat_message', { message_type: messageType }),
  chatRecommendation: (recommendationType: string, count: number) =>
    event('chat_recommendation', { type: recommendationType, count }),
  chatProblemSelect: (problemId: string, source: string) =>
    event('chat_problem_select', { problem_id: problemId, source }),

  // 검색
  searchQuery: (query: string, resultCount: number) =>
    event('search', { search_term: query, result_count: resultCount }),
  searchResultClick: (problemId: string, position: number) =>
    event('search_result_click', { problem_id: problemId, position }),

  // 추천
  recommendationView: (source: string, count: number) =>
    event('recommendation_view', { source, count }),
  recommendationClick: (problemId: string, source: string, position: number) =>
    event('recommendation_click', { problem_id: problemId, source, position }),

  // 에러
  error: (errorType: string, errorMessage: string) =>
    event('error', { error_type: errorType, error_message: errorMessage }),

  // 전환 이벤트 (GA4 전환으로 설정)
  signUp: (method: string) => event('sign_up', { method }),
  login: (method: string) => event('login', { method }),
  firstProblemSolved: () => event('first_problem_solved'),
  tenProblemsSolved: () => event('ten_problems_solved'),
};

// ============================================================
// Next.js App Router용 Hook
// ============================================================

import { useEffect } from 'react';
import { usePathname, useSearchParams } from 'next/navigation';

export function useGA4PageView(): void {
  const pathname = usePathname();
  const searchParams = useSearchParams();

  useEffect(() => {
    if (!pathname) return;

    const url = searchParams?.toString()
      ? `${pathname}?${searchParams.toString()}`
      : pathname;

    pageview(url);
  }, [pathname, searchParams]);
}

export default {
  init: initGA4,
  pageview,
  event,
  setUserProperties,
  setUserId,
  events: ga4Events,
  usePageView: useGA4PageView,
};
