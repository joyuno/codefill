import type { Step } from 'react-joyride';
import { TUTORIAL_TARGETS } from '@/lib/tutorial/constants';

/**
 * Guided(가이드 코딩) 문제 튜토리얼 스텝
 * 7단계: 번역 -> 테스트 케이스 -> 코드 에디터 -> AI 채팅 -> 힌트 -> 테스트 실행 -> 제출
 */
export const guidedSteps: Step[] = [
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
    content: '테스트 탭에서 입력값과 예상 출력값을 확인하세요. 이 테스트를 모두 통과하면 정답입니다!',
    placement: 'right',
    disableBeacon: true,
  },
  {
    target: TUTORIAL_TARGETS.codeEditor,
    title: '💻 코드 작성 영역',
    content: '여기에 문제를 해결하는 코드를 직접 작성하세요. 시작 코드가 제공되어 있으니 로직만 채우면 됩니다.',
    placement: 'right',
    disableBeacon: true,
  },
  {
    target: TUTORIAL_TARGETS.chatInputArea,
    title: '💬 AI 튜터와 대화하기',
    content: '막히면 자유롭게 질문하세요! "힌트 줘", "문제 요약해줘", "에러가 나는데 뭐가 문제야?" 등 뭐든 물어볼 수 있어요.',
    placement: 'top',
    disableBeacon: true,
  },
  {
    target: TUTORIAL_TARGETS.submitBtn,
    title: '✅ 최종 제출',
    content: '모든 테스트가 통과하면 "제출" 버튼을 눌러 최종 제출하세요. 숨겨진 테스트도 함께 검증됩니다!',
    placement: 'top',
    disableBeacon: true,
  },
];
