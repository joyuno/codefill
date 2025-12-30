"""
Intent Classification Node

사용자 메시지의 의도를 분류합니다.
전역 싱글톤 intent_classifier를 재사용합니다 (main.py에서 초기화됨).
"""
from typing import Dict, Any
from ..state import ChatState, IntentResult, INTENT_TO_NODE, CONTEXT_REQUIRED_INTENTS
from ...intents import intent_classifier  # 전역 싱글톤 사용


async def classify_intent(state: ChatState) -> Dict[str, Any]:
    """
    사용자 메시지의 의도를 분류합니다.

    Returns:
        업데이트된 상태:
        - intent_result: 의도 분류 결과
        - next_node: 다음으로 이동할 노드
    """
    message = state.get("message", "")
    conversation_history = state.get("conversation_history", [])
    user_context = state.get("user_context", {})

    # session_context 구성 (IntentClassifier가 기대하는 형태)
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

    intent_result: IntentResult = {
        "intent": result.intent.value,
        "confidence": result.confidence,
        "method": result.method,
        "requires_context": result.requires_context,
        "next_action": result.next_action,
    }

    # 다음 노드 결정
    intent = result.intent.value
    next_node = INTENT_TO_NODE.get(intent, "handle_general")

    # 컨텍스트가 필요한 의도인데 컨텍스트가 없으면 처리
    if intent in CONTEXT_REQUIRED_INTENTS:
        required = CONTEXT_REQUIRED_INTENTS[intent]
        has_context = False

        if required == "problem":
            has_context = bool(user_context.get("current_problem"))
        elif required == "code":
            has_context = bool(user_context.get("current_code"))

        if not has_context:
            next_node = "handle_context_missing"

    return {
        "intent_result": intent_result,
        "next_node": next_node,
    }
