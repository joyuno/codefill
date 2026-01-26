/**
 * 튜토리얼 시스템 상수 및 타입 정의
 */

import type { Styles as JoyrideStyles } from 'react-joyride';

// Partial Styles 타입 (모든 속성이 optional)
type PartialJoyrideStyles = Partial<JoyrideStyles>;

// 문제 유형
export type ProblemType = 'blank' | 'puzzle' | 'guided';

// localStorage 키
export const TUTORIAL_STORAGE_KEYS = {
  blank: 'codefill_tutorial_seen_blank',
  puzzle: 'codefill_tutorial_seen_puzzle',
  guided: 'codefill_tutorial_seen_guided',
} as const;

// Joyride 기본 설정
export const JOYRIDE_DEFAULT_OPTIONS = {
  spotlightPadding: 8,
  scrollOffset: 100,
  disableOverlayClose: false,
  hideCloseButton: false,
  showProgress: true,
  showSkipButton: true,
  continuous: true,
  disableScrolling: false,
} as const;

// Joyride 스타일 (다크 테마)
export const JOYRIDE_STYLES: PartialJoyrideStyles = {
  options: {
    primaryColor: 'hsl(142, 76%, 36%)', // primary green
    backgroundColor: 'hsl(240, 10%, 10%)', // card background
    textColor: 'hsl(0, 0%, 95%)', // foreground
    arrowColor: 'hsl(240, 10%, 10%)',
    overlayColor: 'rgba(0, 0, 0, 0.75)',
    zIndex: 10000,
  },
  spotlight: {
    borderRadius: '0.75rem',
    boxShadow: '0 0 0 9999px rgba(0, 0, 0, 0.85), 0 0 30px rgba(34, 197, 94, 0.8), 0 0 60px rgba(34, 197, 94, 0.4)',
    backgroundColor: 'rgba(255, 255, 255, 0.05)',
  },
  overlay: {
    backgroundColor: 'transparent',
  },
  tooltipContainer: {
    textAlign: 'left' as const,
  },
  tooltip: {
    borderRadius: '0.75rem',
    padding: 0, // 커스텀 Tooltip에서 처리
  },
  tooltipContent: {
    padding: '0',
  },
  buttonNext: {
    backgroundColor: 'hsl(142, 76%, 36%)',
    borderRadius: '0.5rem',
    color: '#fff',
    fontSize: '14px',
    padding: '8px 16px',
  },
  buttonBack: {
    color: 'hsl(0, 0%, 64%)',
    marginRight: '8px',
  },
  buttonSkip: {
    color: 'hsl(0, 0%, 50%)',
    fontSize: '13px',
  },
  buttonClose: {
    display: 'none', // 커스텀 Tooltip에서 처리
  },
};

// data-tutorial 속성 매핑
export const TUTORIAL_TARGETS = {
  // 사이드바
  sidebarProblemTab: '[data-tutorial="sidebar-problem-tab"]',
  sidebarTestTab: '[data-tutorial="sidebar-test-tab"]',

  // Blank 문제
  blankInput0: '[data-tutorial="blank-input-0"]',
  blankHintBtn: '[data-tutorial="blank-hint-btn"]',
  blankProgress: '[data-tutorial="blank-progress"]',

  // Puzzle 문제
  puzzleBlocksArea: '[data-tutorial="puzzle-blocks-area"]',
  puzzleGrip: '[data-tutorial="puzzle-grip"]',
  puzzlePreview: '[data-tutorial="puzzle-preview"]',
  puzzleFixedArea: '[data-tutorial="puzzle-fixed-area"]',

  // Guided 문제
  codeEditor: '[data-tutorial="code-editor"]',
  testCard: '[data-tutorial="test-card"]',
  addTestBtn: '[data-tutorial="add-test-btn"]',

  // 채팅 패널
  chatInputArea: '[data-tutorial="chat-input-area"]',
  keyConceptsBtn: '[data-tutorial="key-concepts-btn"]',

  // 공통
  translateBtn: '[data-tutorial="translate-btn"]',
  submitBtn: '[data-tutorial="submit-btn"]',
  runTestsBtn: '[data-tutorial="run-tests-btn"]',
  hintBtn: '[data-tutorial="hint-btn"]',
} as const;
