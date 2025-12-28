/**
 * Analytics Module
 *
 * 통합 분석 도구 모듈
 * - Microsoft Clarity: 세션 리플레이, 히트맵
 * - Google Analytics 4: 이벤트 추적, 퍼널 분석
 */

export { default as clarity, clarityEvents } from './clarity';
export { default as ga4, ga4Events, useGA4PageView, GA_MEASUREMENT_ID } from './ga4';

import { initClarity, identifyUser as clarityIdentify, setTag } from './clarity';
import { initGA4, setUserId as ga4SetUserId, setUserProperties } from './ga4';

/**
 * 모든 분석 도구 초기화
 * 앱 시작 시 한 번 호출
 */
export function initAnalytics(): void {
  initClarity();
  initGA4();
}

/**
 * 사용자 식별 (로그인 후 호출)
 * 모든 분석 도구에 사용자 정보 전달
 */
export function identifyUser(
  userId: string,
  properties?: {
    userLevel?: string;
    signupDate?: string;
    problemsSolved?: number;
  }
): void {
  // Clarity
  clarityIdentify(userId);
  if (properties?.userLevel) {
    setTag('user_level', properties.userLevel);
  }

  // GA4
  ga4SetUserId(userId);
  if (properties) {
    setUserProperties({
      user_level: properties.userLevel || 'unknown',
      signup_date: properties.signupDate || '',
      problems_solved: properties.problemsSolved || 0,
    });
  }
}

/**
 * 분석 이벤트 일괄 전송
 * Clarity와 GA4 모두에 이벤트 전송
 */
export { clarityEvents, ga4Events };
