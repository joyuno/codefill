"""
LangGraph Intent Graph Definition (Stage 1)

1단계: 의도 파악 그래프

역할:
- 사용자 메시지의 의도 분류
- 다음 단계로 라우팅 결정

플로우:
    START → classify_intent → route_request → END (with route_to)

Note: collect_info 노드는 삭제됨 (V3에서는 InfoCollectionGraph로 분리)
"""
from typing import Dict, Any
from langgraph.graph import StateGraph, END

from .intent_state import (
    IntentState,
    INTENT_TO_ROUTE,
    CONTEXT_REQUIRED_INTENTS,
)


# ============================================================
# Node Functions
# ============================================================

async def classify_intent_node(state: IntentState) -> Dict[str, Any]:
    """
    사용자 메시지의 의도를 분류합니다.
    """
    from ..intents import intent_classifier  # 전역 싱글톤 사용

    message = state.get("message", "")
    conversation_history = state.get("conversation_history", [])
    user_context = state.get("user_context", {})

    # session_context 구성
    session_context = {
        **(user_context or {}),
        "conversation_history": conversation_history,
        "message": message,
    }

    # 의도 분류 (전역 싱글톤 사용 - 임베딩 캐싱됨)
    result = await intent_classifier.classify(
        message=message,
        session_context=session_context
    )

    intent_result = {
        "intent": result.intent.value,
        "confidence": result.confidence,
        "method": result.method,
        "requires_context": result.requires_context,
        "next_action": result.next_action,
    }

    # 컨텍스트 체크
    intent = result.intent.value
    if intent in CONTEXT_REQUIRED_INTENTS:
        required = CONTEXT_REQUIRED_INTENTS[intent]
        has_context = False

        if required == "problem":
            has_context = bool(user_context.get("current_problem"))
        elif required == "code":
            has_context = bool(user_context.get("current_code") or "```" in message)

        if not has_context:
            # 컨텍스트 부족 → 직접 응답
            context_type = "문제" if required == "problem" else "코드"
            return {
                "intent_result": intent_result,
                "response_message": f"이 기능을 사용하려면 {context_type}가 필요해요! 먼저 문제를 선택해주세요.",
                "route_to": "respond",
                "next_node": "route_request",
            }

    # 다음 노드 결정 (V3에서는 항상 route_request로 이동, collect_info는 InfoCollectionGraph에서 처리)
    return {
        "intent_result": intent_result,
        "next_node": "route_request",
    }


# collect_info_node 삭제됨 - V3에서는 InfoCollectionGraph에서 처리


async def route_request_node(state: IntentState) -> Dict[str, Any]:
    """
    최종 라우팅을 결정합니다.
    """
    intent_result = state.get("intent_result", {})
    intent = intent_result.get("intent", "unknown")

    # 이미 route_to가 설정되어 있으면 그대로 사용
    existing_route = state.get("route_to")
    if existing_route:
        return {}

    # 의도에 따라 라우팅
    route_to = INTENT_TO_ROUTE.get(intent, "respond")

    # 응답 메시지 생성 (route_to가 respond인 경우)
    response_message = state.get("response_message", "")
    if route_to == "respond" and not response_message:
        response_message = _generate_simple_response(intent)

    return {
        "route_to": route_to,
        "response_message": response_message,
    }


def _generate_simple_response(intent: str) -> str:
    """간단한 응답 메시지 생성"""
    responses = {
        "greeting": "안녕하세요! 코딩 공부 도와드릴게요. 어떤 문제를 풀어볼까요?",
        "thanks": "도움이 됐다니 기뻐요! 더 필요한 게 있으면 말씀해주세요.",
        "goodbye": "수고하셨어요! 다음에 또 만나요. 화이팅!",
        "confusion": "헷갈리시는군요! 어떤 부분이 어려우신가요?\n1. 문제 이해 → 설명 요청\n2. 풀이 방향 → 힌트 요청\n3. 코드 에러 → 에러 도움 요청",
        "affirmation": "좋아요! 진행할게요.",
        "negation": "알겠어요! 다른 걸로 해볼까요?",
        "out_of_scope": "저는 코딩 학습 도우미예요! 알고리즘 문제 풀이, 코드 리뷰, 힌트 제공 등을 도와드릴 수 있어요.",
        "clarification_needed": "죄송해요, 요청을 이해하기 어려워요. 더 구체적으로 말씀해주실 수 있나요?",
        "progress_check": "진행 상황을 확인할게요!",
        "weak_point": "약점을 분석할게요. 잠시만요...",
        "study_plan": "맞춤 학습 계획을 세워드릴게요!",
    }
    return responses.get(intent, "무엇을 도와드릴까요?")


# ============================================================
# Graph Builder
# ============================================================

def create_intent_graph() -> StateGraph:
    """
    Intent 그래프를 생성합니다.

    V3 플로우: START → classify_intent → route_request → END
    (collect_info는 InfoCollectionGraph에서 처리)
    """
    workflow = StateGraph(IntentState)

    # 노드 추가
    workflow.add_node("classify_intent", classify_intent_node)
    workflow.add_node("route_request", route_request_node)

    # 시작점
    workflow.set_entry_point("classify_intent")

    # classify_intent → route_request
    workflow.add_edge("classify_intent", "route_request")

    # route_request → END
    workflow.add_edge("route_request", END)

    return workflow


# ============================================================
# Compiled Graph Singleton
# ============================================================

_compiled_intent_graph = None


def get_intent_graph():
    """컴파일된 그래프 싱글톤 반환"""
    global _compiled_intent_graph
    if _compiled_intent_graph is None:
        workflow = create_intent_graph()
        _compiled_intent_graph = workflow.compile()
    return _compiled_intent_graph


# ============================================================
# Graph Wrapper Class
# ============================================================

class IntentGraph:
    """
    Intent 그래프 래퍼 클래스
    """

    def __init__(self):
        self.graph = get_intent_graph()

    async def invoke(
        self,
        message: str,
        conversation_history: list = None,
        user_context: dict = None,
        collected_info: dict = None,
    ) -> Dict[str, Any]:
        """
        그래프를 실행합니다.

        Args:
            message: 사용자 메시지
            conversation_history: 대화 히스토리
            user_context: 사용자 컨텍스트
            collected_info: 이미 수집된 정보

        Returns:
            {
                intent_result: 의도 분류 결과,
                collected_info: 수집된 정보,
                route_to: 다음 그래프 (discovery, solving, respond),
                response_message: 응답 메시지 (route_to가 respond인 경우),
            }
        """
        initial_state: IntentState = {
            "message": message,
            "conversation_history": conversation_history or [],
            "user_context": user_context or {},
            "collected_info": collected_info or {},
        }

        result = await self.graph.ainvoke(initial_state)

        return result

    def get_mermaid_diagram(self) -> str:
        """그래프를 Mermaid 다이어그램으로 반환"""
        try:
            return self.graph.get_graph().draw_mermaid()
        except Exception:
            return "Mermaid diagram not available"
