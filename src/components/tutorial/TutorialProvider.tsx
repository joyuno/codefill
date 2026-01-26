'use client';

import React, { createContext, useContext, useCallback, useMemo } from 'react';
import dynamic from 'next/dynamic';
import type { Step } from 'react-joyride';
import { useTutorial } from '@/hooks/useTutorial';
import { TutorialTooltip } from './TutorialTooltip';
import { blankSteps } from './steps/blankSteps';
import { puzzleSteps } from './steps/puzzleSteps';
import { guidedSteps } from './steps/guidedSteps';
import { JOYRIDE_STYLES, JOYRIDE_DEFAULT_OPTIONS, type ProblemType } from '@/lib/tutorial/constants';

// Joyride 동적 임포트 (SSR 비활성화)
const Joyride = dynamic(() => import('react-joyride'), {
  ssr: false,
});

// Context 타입
interface TutorialContextType {
  isRunning: boolean;
  stepIndex: number;
  problemType: ProblemType | null;
  startTutorial: (type: ProblemType) => void;
  stopTutorial: () => void;
  shouldShowTutorial: (type: ProblemType) => boolean;
  resetTutorial: (type: ProblemType) => void;
}

const TutorialContext = createContext<TutorialContextType | null>(null);

// 문제 유형별 스텝 매핑
const stepsByType: Record<ProblemType, Step[]> = {
  blank: blankSteps,
  puzzle: puzzleSteps,
  guided: guidedSteps,
};

interface TutorialProviderProps {
  children: React.ReactNode;
}

export function TutorialProvider({ children }: TutorialProviderProps) {
  const {
    isRunning,
    stepIndex,
    problemType,
    startTutorial,
    stopTutorial,
    shouldShowTutorial,
    resetTutorial,
    handleJoyrideCallback,
  } = useTutorial();

  // 현재 문제 유형에 맞는 스텝 선택
  const currentSteps = useMemo(() => {
    if (!problemType) return [];
    return stepsByType[problemType] || [];
  }, [problemType]);

  const contextValue = useMemo(
    () => ({
      isRunning,
      stepIndex,
      problemType,
      startTutorial,
      stopTutorial,
      shouldShowTutorial,
      resetTutorial,
    }),
    [isRunning, stepIndex, problemType, startTutorial, stopTutorial, shouldShowTutorial, resetTutorial]
  );

  return (
    <TutorialContext.Provider value={contextValue}>
      {children}
      <Joyride
        steps={currentSteps}
        run={isRunning}
        stepIndex={stepIndex}
        callback={handleJoyrideCallback}
        continuous={JOYRIDE_DEFAULT_OPTIONS.continuous}
        showProgress={JOYRIDE_DEFAULT_OPTIONS.showProgress}
        showSkipButton={JOYRIDE_DEFAULT_OPTIONS.showSkipButton}
        disableOverlayClose={JOYRIDE_DEFAULT_OPTIONS.disableOverlayClose}
        spotlightPadding={JOYRIDE_DEFAULT_OPTIONS.spotlightPadding}
        scrollOffset={JOYRIDE_DEFAULT_OPTIONS.scrollOffset}
        disableScrolling={JOYRIDE_DEFAULT_OPTIONS.disableScrolling}
        disableScrollParentFix={true}
        styles={JOYRIDE_STYLES}
        tooltipComponent={TutorialTooltip}
        floaterProps={{
          disableAnimation: false,
          offset: 15,
        }}
        locale={{
          back: '이전',
          close: '닫기',
          last: '완료',
          next: '다음',
          skip: '건너뛰기',
        }}
      />
    </TutorialContext.Provider>
  );
}

// Hook to use tutorial context
export function useTutorialContext(): TutorialContextType {
  const context = useContext(TutorialContext);
  if (!context) {
    throw new Error('useTutorialContext must be used within a TutorialProvider');
  }
  return context;
}
