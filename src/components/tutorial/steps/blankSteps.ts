import type { Step } from 'react-joyride';
import { TUTORIAL_TARGETS } from '@/lib/tutorial/constants';

/**
 * Blank(빈칸 채우기) 문제 튜토리얼 스텝
 * 6단계: 번역 -> 테스트 케이스 -> 빈칸 입력 -> 빈칸 힌트 -> AI 채팅 -> 정답 확인
 */
export const blankSteps: Step[] = [
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
    content: '테스트 탭에서 입력값과 예상 출력값을 확인하세요. 코드가 어떻게 동작해야 하는지 힌트를 얻을 수 있어요!',
    placement: 'right',
    disableBeacon: true,
  },
  {
    target: TUTORIAL_TARGETS.blankInput0,
    title: '✏️ 빈칸에 정답 입력',
    content: '코드의 빈칸에 알맞은 답을 입력하세요. 변수명, 함수명, 연산자 등 정확한 코드를 넣어야 해요.',
    placement: 'bottom',
    disableBeacon: true,
  },
  {
    target: TUTORIAL_TARGETS.blankHintBtn,
    title: '💡 빈칸별 힌트',
    content: '각 빈칸 옆의 💡 버튼을 누르면 해당 빈칸의 정답 힌트를 볼 수 있어요!',
    placement: 'bottom',
    disableBeacon: true,
  },
  {
    target: TUTORIAL_TARGETS.chatInputArea,
    title: '💬 AI 튜터와 대화하기',
    content: '막히면 자유롭게 질문하세요! "힌트 줘", "문제 요약해줘", "이 코드가 뭐하는 거야?" 등 뭐든 물어볼 수 있어요.',
    placement: 'top',
    disableBeacon: true,
  },
  {
    target: TUTORIAL_TARGETS.submitBtn,
    title: '✅ 정답 확인',
    content: '모든 빈칸을 채웠다면 "정답 확인" 버튼을 눌러 제출하세요. 맞으면 XP 획득, 틀리면 다시 시도!',
    placement: 'top',
    disableBeacon: true,
  },
];
