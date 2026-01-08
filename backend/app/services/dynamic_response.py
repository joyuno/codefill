"""
Dynamic Response Generator Service

LLM 기반 동적 응답 생성 서비스
- 하드코딩된 응답 대신 LLM이 상황에 맞는 응답 생성
- 모든 예측 불가능한 입력에 대응
- 대화 컨텍스트 기반 자연스러운 응답

핵심 원칙:
- 절대 하드코딩된 응답 사용 금지
- LLM이 상황 판단하여 적절한 응답 생성
- 코딩 학습 도우미로서의 역할 유지
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass

from ..config import get_settings
from ..services.openrouter import openrouter_service

settings = get_settings()


@dataclass
class DynamicResponse:
    """동적 응답 결과"""
    message: str
    suggested_action: Optional[str] = None  # 다음 추천 액션
    redirect_to: Optional[str] = None  # 리다이렉트 대상 (discovery, solving 등)


class DynamicResponseGenerator:
    """
    LLM 기반 동적 응답 생성기

    어떤 입력이든 LLM이 컨텍스트를 이해하고 적절한 응답을 생성합니다.
    - 욕설/비속어 → 부드럽게 학습으로 유도
    - 거부/싫다 표현 → 대안 제시
    - 의미 불명 입력 → 친절하게 재질문
    - 감정 표현 → 공감 후 학습 연결
    """

    SYSTEM_PROMPT = """당신은 친근하고 똑똑한 코딩 학습 AI 튜터입니다.
사용자의 모든 메시지에 자연스럽고 적절하게 응답하세요.

핵심 원칙:
1. 절대 "무엇을 도와드릴까요?" 같은 기계적인 응답 금지
2. 사용자의 감정과 의도를 이해하고 공감
3. 부드럽게 코딩 학습으로 연결
4. 거부나 부정적 표현에는 대안 제시
5. 대화체로 자연스럽게 (반말 OK, 이모지 최소화)

응답 스타일:
- 짧고 간결하게 (1-3문장)
- 다음 행동을 자연스럽게 제안
- 사용자가 거부한 것은 다시 제안하지 않음

예시:
- 욕설/짜증 → "알겠어, 다른 걸로 해볼까? 어떤 주제가 끌려?"
- "기초 싫어" → "그래, 기초 말고 다른 거 할까? 관심 있는 주제 있어?"
- 의미불명 → "음, 뭘 원하는지 잘 모르겠어. 문제 풀기? 개념 설명? 코드 리뷰?"
- 감정표현 → "그렇구나. 뭐 할래? 쉬운 문제로 가볍게 풀어볼까?"

당신의 역할:
- 알고리즘 문제 추천 및 풀이 도움
- 코드 리뷰 및 디버깅
- 개념 설명 및 힌트 제공"""

    async def generate(
        self,
        message: str,
        intent: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        user_context: Optional[Dict[str, Any]] = None,
    ) -> DynamicResponse:
        """
        상황에 맞는 동적 응답 생성

        Args:
            message: 사용자 메시지
            intent: 분류된 의도
            conversation_history: 대화 히스토리
            user_context: 사용자 컨텍스트 (현재 문제, 온보딩 정보 등)

        Returns:
            DynamicResponse: LLM이 생성한 응답
        """
        conversation_history = conversation_history or []
        user_context = user_context or {}

        # 컨텍스트 정보 구성
        context_info = self._build_context_info(user_context, intent)

        # 최근 대화 요약 (최대 3턴)
        recent_history = conversation_history[-6:] if conversation_history else []
        history_text = "\n".join([
            f"{'사용자' if msg.get('role') == 'user' else 'AI'}: {msg.get('content', '')[:100]}"
            for msg in recent_history
        ])

        prompt = f"""현재 상황:
- 사용자 메시지: "{message}"
- 분류된 의도: {intent}
{context_info}

최근 대화:
{history_text if history_text else "(없음)"}

위 상황에 맞는 자연스러운 응답을 생성하세요.
응답만 출력하세요 (부가 설명 없이)."""

        try:
            response = await openrouter_service.chat_completion(
                model=settings.llm_model_intent,  # 빠른 모델 사용
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,  # 약간의 창의성
                max_tokens=150,  # 짧은 응답
            )

            generated_message = openrouter_service.get_content(response).strip()

            # 다음 액션 추론
            suggested_action = self._infer_action(intent, message)

            return DynamicResponse(
                message=generated_message,
                suggested_action=suggested_action,
            )

        except Exception as e:
            print(f"[DynamicResponseGenerator] Error: {e}")
            # 폴백 (하지만 이것도 동적으로)
            return DynamicResponse(
                message="잠깐 문제가 있었어. 다시 말해줄래?",
                suggested_action="retry"
            )

    def _build_context_info(self, user_context: Dict, intent: str) -> str:
        """컨텍스트 정보 문자열 생성"""
        lines = []

        if user_context.get("current_problem"):
            lines.append(f"- 현재 문제: {user_context['current_problem'].get('title', '있음')}")

        if user_context.get("onboarding"):
            onboard = user_context["onboarding"]
            if onboard.get("preferred_topics"):
                lines.append(f"- 선호 주제: {', '.join(onboard['preferred_topics'][:3])}")
            if onboard.get("skill_level"):
                lines.append(f"- 실력: {onboard['skill_level']}")

        if user_context.get("last_suggestion"):
            lines.append(f"- 최근 제안: {user_context['last_suggestion']}")

        # 거부된 것들
        if user_context.get("rejected_topics"):
            lines.append(f"- 거부한 주제: {', '.join(user_context['rejected_topics'])}")

        return "\n".join(lines) if lines else "- 추가 정보 없음"

    def _infer_action(self, intent: str, message: str) -> Optional[str]:
        """의도에 따른 다음 액션 추론"""
        # 액션 매핑 (단순 힌트용)
        action_hints = {
            "negation": "offer_alternatives",
            "confusion": "clarify_and_help",
            "inappropriate_message": "redirect_to_learning",
            "clarification_needed": "ask_specific_question",
            "greeting": "welcome_and_suggest",
            "thanks": "acknowledge_and_continue",
            "out_of_scope": "redirect_to_coding",
        }
        return action_hints.get(intent)


# 싱글톤 인스턴스
dynamic_response_generator = DynamicResponseGenerator()
