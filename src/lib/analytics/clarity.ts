/**
 * Microsoft Clarity 분석 도구
 *
 * 기능:
 * - 세션 리플레이: 사용자 행동 녹화
 * - 히트맵: 클릭/스크롤 패턴 시각화
 * - 인사이트: 자동 UX 문제 감지
 *
 * 설정: https://clarity.microsoft.com
 */

declare global {
  interface Window {
    clarity: (command: string, ...args: unknown[]) => void;
  }
}

const CLARITY_ID = process.env.NEXT_PUBLIC_CLARITY_ID;

/**
 * Clarity 초기화 확인
 * 스크립트는 layout.tsx의 next/script로 로드됨
 */
export function initClarity(): void {
  if (typeof window === 'undefined') return;
  if (!CLARITY_ID) {
    console.warn('[Clarity] NEXT_PUBLIC_CLARITY_ID not set');
    return;
  }
  // 스크립트는 layout.tsx에서 로드됨
  // 여기서는 초기화 확인만 수행
  if (window.clarity) {
    console.log('[Clarity] Ready');
  }
}

/**
 * 사용자 식별 (로그인 후 호출)
 * Clarity 대시보드에서 특정 사용자 세션 필터링 가능
 */
export function identifyUser(userId: string, sessionId?: string): void {
  if (typeof window === 'undefined' || !window.clarity) return;

  window.clarity('identify', userId, sessionId);
}

/**
 * 커스텀 태그 설정
 * 세션에 메타데이터 추가 (필터링용)
 */
export function setTag(key: string, value: string | string[]): void {
  if (typeof window === 'undefined' || !window.clarity) return;

  window.clarity('set', key, value);
}

/**
 * 이벤트 추적
 * 중요 사용자 행동 마킹
 */
export function trackEvent(eventName: string): void {
  if (typeof window === 'undefined' || !window.clarity) return;

  window.clarity('event', eventName);
}

/**
 * 업그레이드 (중요 세션 마킹)
 * 결제, 전환 등 중요 세션을 우선 저장
 */
export function upgradeSession(reason: string): void {
  if (typeof window === 'undefined' || !window.clarity) return;

  window.clarity('upgrade', reason);
}

// ============================================================
// CodeFill 전용 이벤트
// ============================================================

export const clarityEvents = {
  // 온보딩
  onboardingStart: () => trackEvent('onboarding_start'),
  onboardingComplete: () => {
    trackEvent('onboarding_complete');
    upgradeSession('onboarding_complete');
  },

  // 문제 풀이
  problemStart: (problemId: string) => {
    setTag('current_problem', problemId);
    trackEvent('problem_start');
  },
  problemSolve: (isCorrect: boolean) => {
    trackEvent(isCorrect ? 'problem_correct' : 'problem_incorrect');
    if (isCorrect) upgradeSession('problem_solved');
  },
  problemSkip: () => trackEvent('problem_skip'),
  hintRequest: (level: number) => {
    setTag('hint_level', String(level));
    trackEvent('hint_request');
  },

  // 챗봇
  chatMessage: () => trackEvent('chat_message'),
  chatRecommendation: () => trackEvent('chat_recommendation'),

  // 에러
  errorOccurred: (errorType: string) => {
    setTag('error_type', errorType);
    trackEvent('error_occurred');
  },
};

export default {
  init: initClarity,
  identify: identifyUser,
  setTag,
  trackEvent,
  upgradeSession,
  events: clarityEvents,
};
