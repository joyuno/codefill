import type { Step } from 'react-joyride';
import { TUTORIAL_TARGETS } from '@/lib/tutorial/constants';

/**
 * Puzzle(코드 블록 정렬) 문제 튜토리얼 스텝
 * 7단계: 번역 -> 테스트 케이스 -> 블록 정렬 -> 드래그 -> AI 채팅 -> 힌트 -> 정답 확인
 */
export const puzzleSteps: Step[] = [
  {
    target: TUTORIAL_TARGETS.translateBtn,
    title: '🌐 번역 기능',
    content: '문제가 영어로 되어 있다면 여기서 한국어, 일본어 등 원하는 언어로 번역할 수 있어요!',
    placement: 'bottom',
    disableBeacon: true,
  },
  {
    target: TUTORIAL_TARGETS.sidebarTestTab,
    title: '📋 테스트 케이스 확인',
    content: '테스트 탭에서 입출력 예시를 확인하세요. 코드가 어떤 순서로 실행되어야 하는지 파악하는 데 도움이 돼요!',
    placement: 'right',
    disableBeacon: true,
  },
  {
    target: TUTORIAL_TARGETS.puzzleBlocksArea,
    title: '🧩 코드 블록 정렬',
    content: '이 영역의 코드 블록들을 올바른 순서로 정렬하세요. 위에서 아래로 논리적인 순서대로 배치하면 됩니다.',
    placement: 'bottom',
    disableBeacon: true,
  },
  {
    target: TUTORIAL_TARGETS.puzzleGrip,
    title: '✋ 드래그로 이동',
    content: '왼쪽의 손잡이 아이콘을 드래그하여 블록 위치를 변경할 수 있어요.',
    placement: 'right',
    disableBeacon: true,
  },
  {
    target: TUTORIAL_TARGETS.chatInputArea,
    title: '💬 AI 튜터와 대화하기',
    content: '순서가 헷갈리면 질문하세요! "힌트 줘", "문제 요약해줘", "이 블록은 뭐하는 코드야?" 등 자유롭게 물어볼 수 있어요.',
    placement: 'top',
    disableBeacon: true,
  },
  {
    target: TUTORIAL_TARGETS.submitBtn,
    title: '✅ 정답 확인',
    content: '블록 배치가 완료되면 "정답 확인" 버튼을 누르세요. 틀린 블록은 빨간색으로 표시됩니다.',
    placement: 'top',
    disableBeacon: true,
  },
];
