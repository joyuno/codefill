"""
Problem Solving Intent Classification Node

문제 풀이 중 사용자 의도 분류
"""
from typing import Dict, Any
from ..solving_state import SolvingState, SolvingIntentResult, SOLVING_INTENT_TO_NODE


async def classify_solving_intent(state: SolvingState) -> Dict[str, Any]:
    """
    문제 풀이 중 의도를 분류합니다.

    의도 종류:
    - hint_request: 힌트 요청
    - code_review: 코드 리뷰 요청
    - answer_check: 정답 확인 요청
    - feedback_request: 피드백 요청
    - explain_concept: 개념 설명 요청
    - give_up: 포기/정답 보기
    - next_step: 다음 단계 (guided 전용)
    - question: 일반 질문
    """
    from ...services.openrouter import openrouter_service

    message = state.get("message", "").lower()
    problem_context = state.get("problem_context", {})
    user_progress = state.get("user_progress", {})

    # 키워드 기반 빠른 분류
    intent = _classify_by_keywords(message)
    confidence = 0.9 if intent else 0.0

    # 키워드로 분류 안 되면 LLM 사용
    if not intent:
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


def _classify_by_keywords(message: str) -> str:
    """키워드 기반 빠른 분류"""
    # 문제 요약 요청
    if any(kw in message for kw in ["요약", "summary", "간단히", "정리", "문제 설명"]):
        return "summarize_problem"

    # 힌트 요청
    if any(kw in message for kw in ["힌트", "hint", "도움", "모르겠", "어려워", "막혔"]):
        return "hint_request"

    # 코드 리뷰
    if any(kw in message for kw in ["리뷰", "review", "코드 봐", "이 코드", "맞아?"]):
        return "code_review"

    # 정답 확인
    if any(kw in message for kw in ["제출", "submit", "정답", "확인", "채점", "실행"]):
        return "answer_check"

    # 피드백 요청
    if any(kw in message for kw in ["피드백", "feedback", "어때", "괜찮", "개선"]):
        return "feedback_request"

    # 개념 설명
    if any(kw in message for kw in ["설명", "explain", "뭐야", "무슨", "어떻게", "왜"]):
        return "explain_concept"

    # 포기
    if any(kw in message for kw in ["포기", "정답 보", "답 보", "give up", "모르겠어"]):
        return "give_up"

    # 다음 단계 (guided)
    if any(kw in message for kw in ["다음", "next", "진행", "계속"]):
        return "next_step"

    return ""


async def _classify_by_llm(
    message: str,
    problem_context: dict,
    user_progress: dict
) -> tuple:
    """LLM 기반 분류"""
    from ...services.openrouter import openrouter_service

    system_prompt = """사용자가 코딩 문제를 풀고 있습니다. 메시지의 의도를 분류하세요.

가능한 의도:
- hint_request: 힌트나 도움 요청
- code_review: 작성한 코드 검토 요청
- answer_check: 정답 제출/확인 요청
- feedback_request: 피드백 요청
- explain_concept: 개념이나 알고리즘 설명 요청
- give_up: 포기하고 정답 보기
- question: 일반적인 질문

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

    if intent == "explain_concept":
        if any(kw in message for kw in ["시간복잡도", "복잡도", "O("]):
            return "explain_complexity"
        elif any(kw in message for kw in ["왜", "이유"]):
            return "explain_why"
        return "explain_general"

    return ""
