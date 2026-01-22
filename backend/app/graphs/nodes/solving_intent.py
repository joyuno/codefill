"""
Problem Solving Intent Classification Node

문제 풀이 중 사용자 의도 분류
"""
from typing import Dict, Any
from ..solving_state import SolvingState, SolvingIntentResult, SOLVING_INTENT_TO_NODE
from ...services.langsmith_tracker import track_intent_node


@track_intent_node("classify_solving_intent", tags=["solving", "intent"])
async def classify_solving_intent(state: SolvingState) -> Dict[str, Any]:
    """
    문제 풀이 중 의도를 분류합니다.

    우선순위:
    1. orchestrator에서 LLM으로 분류한 pre_classified_intent 사용
    2. pre_classified_intent가 없으면 LLM fallback (직접 호출 시)

    의도 종류:
    - hint_request: 힌트 요청 (힌트 버튼용, 레벨 증가)
    - code_review: 코드 리뷰 요청
    - answer_check: 정답 확인 요청
    - feedback_request: 피드백 요청
    - give_up: 포기/정답 보기
    - question: 일반 질문
    - chat_assist: 채팅 기반 간접 도움
    - concept_explain: 개념 설명 요청
    - approach_hint: 접근법 힌트
    - validate_direction: 방향 확인
    - summarize_problem: 문제 요약
    """
    message = state.get("message", "")
    problem_context = state.get("problem_context", {})
    user_progress = state.get("user_progress", {})

    # 1. orchestrator에서 분류한 의도가 있으면 사용 (LLM 기반)
    pre_classified_intent = state.get("pre_classified_intent")
    if pre_classified_intent:
        intent = pre_classified_intent
        confidence = 0.95  # orchestrator LLM에서 분류됨

    # 2. pre_classified_intent가 없으면 LLM fallback (직접 호출 시)
    else:
        intent, confidence = await _classify_by_llm(
            message, problem_context, user_progress
        )

    # 결과 구성
    intent_result: SolvingIntentResult = {
        "intent": intent,
        "confidence": confidence,
        "sub_intent": _detect_sub_intent(message, intent),
    }

    # 다음 노드 결정
    next_node = SOLVING_INTENT_TO_NODE.get(intent, "answer_question")

    return {
        "intent_result": intent_result,
        "next_node": next_node,
    }


# _classify_by_keywords 함수 제거됨 - orchestrator에서 LLM 기반으로 통합 분류


async def _classify_by_llm(
    message: str,
    problem_context: dict,
    user_progress: dict
) -> tuple:
    """LLM 기반 분류"""
    from ...services.openrouter import openrouter_service

    system_prompt = """사용자가 코딩 문제를 풀고 있습니다. 메시지의 의도를 분류하세요.

가능한 의도:
- summarize_problem: 문제 요약/설명 요청 ("문제 설명해줘", "요약해줘")
- chat_assist: 채팅으로 간접 도움 요청 (정답 노출 없이 개념/방향 설명)
- concept_explain: 개념이나 원리 설명 요청 ("이게 뭐야?", "왜 이렇게?")
- approach_hint: 접근법/방법 질문 ("어떻게 시작해?", "어떻게 접근?")
- validate_direction: 방향 확인 ("이렇게 하면 맞아?", "이 방향이 맞나?")
- hint_request: 명시적 힌트 요청 ("힌트 줘", 힌트 버튼)
- code_review: 작성한 코드 검토 요청
- answer_check: 정답 제출/확인 요청 ("제출", "채점해줘")
- feedback_request: 피드백 요청 ("어때?", "개선할 점?")
- give_up: 포기하고 정답 보기 ("답 보여줘", "포기")
- question: 일반적인 질문

참고: 이 함수는 orchestrator에서 분류 실패 시 fallback으로만 사용됩니다.

JSON으로 응답: {"intent": "의도", "confidence": 0.0~1.0}"""

    context = f"""
현재 문제: {problem_context.get('title', 'Unknown')}
문제 유형: {problem_context.get('problem_type', 'unknown')}
시도 횟수: {user_progress.get('attempt_count', 0)}
힌트 사용: {user_progress.get('hint_count', 0)}회
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"{context}\n\n사용자 메시지: {message}"},
    ]

    try:
        response = await openrouter_service.chat_completion(
            messages=messages,
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
        )
        content = openrouter_service.get_content(response)
        result = openrouter_service.parse_json_response(content)

        return result.get("intent", "question"), result.get("confidence", 0.7)

    except Exception as e:
        print(f"[SolvingIntent] LLM error: {e}")
        return "question", 0.5


def _detect_sub_intent(message: str, intent: str) -> str:
    """세부 의도 감지"""
    if intent == "hint_request":
        if any(kw in message for kw in ["알고리즘", "접근", "방법"]):
            return "hint_algorithm"
        elif any(kw in message for kw in ["문법", "syntax", "어떻게 써"]):
            return "hint_syntax"
        elif any(kw in message for kw in ["에러", "오류", "버그"]):
            return "hint_debug"
        return "hint_general"

    # chat_assist 계열 세부 의도
    if intent in ["chat_assist", "concept_explain", "approach_hint", "validate_direction"]:
        if any(kw in message for kw in ["개념", "원리", "뭐야", "무슨"]):
            return "concept_explain"
        elif any(kw in message for kw in ["맞아", "맞나", "방향", "틀렸"]):
            return "validate_direction"
        elif any(kw in message for kw in ["어떻게", "시작", "접근", "방법"]):
            return "approach_hint"
        return "general_help"

    if intent == "explain_concept":
        if any(kw in message for kw in ["시간복잡도", "복잡도", "O("]):
            return "explain_complexity"
        elif any(kw in message for kw in ["왜", "이유"]):
            return "explain_why"
        return "explain_general"

    return ""
