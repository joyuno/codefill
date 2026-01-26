'use client';

import { useState, useCallback } from 'react';
import type { CallBackProps } from 'react-joyride';
import { STATUS, EVENTS, ACTIONS } from 'react-joyride';
import { TUTORIAL_STORAGE_KEYS, type ProblemType } from '@/lib/tutorial/constants';

interface UseTutorialReturn {
  isRunning: boolean;
  stepIndex: number;
  problemType: ProblemType | null;
  startTutorial: (type: ProblemType) => void;
  stopTutorial: () => void;
  shouldShowTutorial: (type: ProblemType) => boolean;
  markTutorialSeen: (type: ProblemType) => void;
  resetTutorial: (type: ProblemType) => void;
  handleJoyrideCallback: (data: CallBackProps) => void;
}

export function useTutorial(): UseTutorialReturn {
  const [isRunning, setIsRunning] = useState(false);
  const [stepIndex, setStepIndex] = useState(0);
  const [problemType, setProblemType] = useState<ProblemType | null>(null);

  // localStorage에서 튜토리얼 완료 여부 확인
  const shouldShowTutorial = useCallback((type: ProblemType): boolean => {
    if (typeof window === 'undefined') return false;
    const key = TUTORIAL_STORAGE_KEYS[type];
    return localStorage.getItem(key) !== 'true';
  }, []);

  // 튜토리얼 완료 표시
  const markTutorialSeen = useCallback((type: ProblemType) => {
    if (typeof window === 'undefined') return;
    const key = TUTORIAL_STORAGE_KEYS[type];
    localStorage.setItem(key, 'true');
  }, []);

  // 튜토리얼 리셋 (다시 보기용)
  const resetTutorial = useCallback((type: ProblemType) => {
    if (typeof window === 'undefined') return;
    const key = TUTORIAL_STORAGE_KEYS[type];
    localStorage.removeItem(key);
  }, []);

  // 튜토리얼 시작
  const startTutorial = useCallback((type: ProblemType) => {
    setProblemType(type);
    setStepIndex(0);
    setIsRunning(true);
  }, []);

  // 튜토리얼 중지
  const stopTutorial = useCallback(() => {
    setIsRunning(false);
    setStepIndex(0);
    // 중지 시 현재 타입 완료 표시
    if (problemType) {
      markTutorialSeen(problemType);
    }
    setProblemType(null);
  }, [problemType, markTutorialSeen]);

  // Joyride 콜백 핸들러
  const handleJoyrideCallback = useCallback((data: CallBackProps) => {
    const { status, index, type, action } = data;

    // 종료 처리 함수 (스크롤 위치 유지)
    const finishTutorial = () => {
      // 현재 스크롤 위치 저장
      const scrollY = window.scrollY;
      const scrollX = window.scrollX;

      setIsRunning(false);
      setStepIndex(0);
      if (problemType) {
        markTutorialSeen(problemType);
      }
      setProblemType(null);

      // 스크롤 위치 복원 (다음 프레임에서)
      requestAnimationFrame(() => {
        window.scrollTo(scrollX, scrollY);
      });
    };

    // 완료 또는 스킵 시 종료
    if (status === STATUS.FINISHED || status === STATUS.SKIPPED) {
      finishTutorial();
      return;
    }

    // 닫기 버튼 클릭 시 종료
    if (action === ACTIONS.CLOSE) {
      finishTutorial();
      return;
    }

    // 투어 종료 이벤트
    if (type === EVENTS.TOUR_END) {
      finishTutorial();
      return;
    }

    // 다음/이전 스텝
    if (type === EVENTS.STEP_AFTER) {
      if (action === ACTIONS.NEXT) {
        setStepIndex(index + 1);
      } else if (action === ACTIONS.PREV) {
        setStepIndex(Math.max(0, index - 1));
      }
    }
  }, [problemType, markTutorialSeen]);

  return {
    isRunning,
    stepIndex,
    problemType,
    startTutorial,
    stopTutorial,
    shouldShowTutorial,
    markTutorialSeen,
    resetTutorial,
    handleJoyrideCallback,
  };
}
