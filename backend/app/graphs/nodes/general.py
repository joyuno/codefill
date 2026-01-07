"""
General Chat Nodes

인사, 감사, 기타 일반 대화 처리
"""
from typing import Dict, Any
from ..state import ChatState


async def handle_greeting(state: ChatState) -> Dict[str, Any]:
    """
    인사 처리 - 개인화된 추천 포함

    user_context["personalization"]에서 사용자 히스토리 기반 추천 생성
    """
    message = state.get("message", "").lower()
    user_context = state.get("user_context", {})
    personalization = user_context.get("personalization", {})

    # 시간대별 인사
    if any(word in message for word in ["아침", "morning"]):
        greeting = "좋은 아침이에요! "
    elif any(word in message for word in ["저녁", "evening", "밤"]):
        greeting = "좋은 저녁이에요! "
    else:
        greeting = "안녕하세요! "

    # ============================================================
    # 개인화된 추천 메시지 생성
    # ============================================================
    suggested_actions = []
    recommendation_msg = ""

    if personalization.get("has_history"):
        recommendations = personalization.get("recommendations", [])
        recent_problems = personalization.get("recent_problems", [])
        skill_summary = personalization.get("skill_summary", {})

        # 최근 풀이 기반 추천
        if recommendations:
            rec = recommendations[0]  # 첫 번째 추천 사용
            rec_type = rec.get("type")
            rec_topics = rec.get("topics", [])
            rec_difficulty = rec.get("difficulty")
            rec_reason = rec.get("reason", "")

            if rec_type == "level_up" and rec_topics:
                topic = rec_topics[0]
                diff_display = {
                    "easy": "쉬움", "medium": "보통",
                    "medium_hard": "중상", "hard": "어려움", "very_hard": "매우 어려움"
                }.get(rec_difficulty, rec_difficulty)

                recommendation_msg = f"\n\n💡 **추천**: {rec_reason}, **{diff_display}** 난이도로 도전해볼까요?"
                suggested_actions.append({
                    "label": f"{topic} {diff_display}",
                    "value": f"{topic}_{rec_difficulty}",
                    "recommended": True
                })

            elif rec_type == "retry" and rec_topics:
                topic = rec_topics[0]
                recommendation_msg = f"\n\n💪 **추천**: {topic} 문제를 좀 더 연습해볼까요?"
                suggested_actions.append({
                    "label": f"{topic} 연습",
                    "value": f"{topic}_{rec_difficulty or 'medium'}",
                    "recommended": True
                })

            elif rec_type == "weak_topic" and rec_topics:
                topic = rec_topics[0]
                recommendation_msg = f"\n\n📚 **추천**: {topic}은(는) 연습이 더 필요해 보여요!"
                suggested_actions.append({
                    "label": f"{topic} 연습",
                    "value": f"{topic}_easy",
                    "recommended": True
                })

        # 최근 풀이 정보 추가
        if recent_problems and not recommendation_msg:
            last = recent_problems[0]
            last_name = last.get("name", "문제")
            last_topics = last.get("topics", [])
            was_solved = last.get("solved", False)

            if was_solved:
                recommendation_msg = f"\n\n지난번에 '{last_name}'을(를) 잘 풀었네요! 오늘도 화이팅! 🔥"
            else:
                recommendation_msg = f"\n\n지난번 '{last_name}'에서 고생하셨죠? 다시 도전해볼까요?"
                if last_topics:
                    suggested_actions.append({
                        "label": f"{last_topics[0]} 다시 도전",
                        "value": f"{last_topics[0]}_retry"
                    })

    # 기본 액션 추가
    if not suggested_actions:
        suggested_actions = [
            {"label": "쉬운 문제", "value": "easy"},
            {"label": "중간 문제", "value": "medium"},
            {"label": "어려운 문제", "value": "hard"},
        ]
    else:
        # 추천 외에 기본 옵션도 추가
        suggested_actions.extend([
            {"label": "다른 주제", "value": "other_topic"},
            {"label": "랜덤 문제", "value": "random"},
        ])

    response = f"{greeting}오늘은 어떤 코딩 연습을 해볼까요?{recommendation_msg}"

    return {
        "response_message": response,
        "action_data": {
            "suggested_actions": suggested_actions,
            "personalization": personalization if personalization.get("has_history") else None,
        },
        "next_node": "respond",
    }


async def handle_thanks(state: ChatState) -> Dict[str, Any]:
    """감사 인사 처리"""
    responses = [
        "천만에요! 더 도움이 필요하시면 말씀해주세요 😊",
        "별말씀을요! 열심히 하시는 모습이 멋져요!",
        "도움이 됐다니 기뻐요! 다른 문제도 풀어볼까요?",
    ]

    import random
    response = random.choice(responses)

    return {
        "response_message": response,
        "next_node": "respond",
    }


async def handle_general(state: ChatState) -> Dict[str, Any]:
    """
    일반적인 대화 처리 (분류되지 않은 의도)
    """
    from ...services.openrouter import OpenRouterService

    message = state.get("message", "")
    conversation_history = state.get("conversation_history", [])
    intent_result = state.get("intent_result", {})

    openrouter = OpenRouterService()

    system_prompt = """당신은 CodeFill의 친근한 코딩 학습 도우미입니다.
사용자와 자연스럽게 대화하면서 코딩 학습으로 유도해주세요.

규칙:
- 친근하고 격려하는 톤
- 코딩/알고리즘 관련 대화로 자연스럽게 유도
- 범위를 벗어난 질문은 정중히 거절하고 학습으로 돌아오게 유도
- 이모지 적절히 사용
"""

    messages = [{"role": "system", "content": system_prompt}]
    for msg in conversation_history[-4:]:
        messages.append({
            "role": msg.get("role", "user"),
            "content": msg.get("content", "")
        })
    messages.append({"role": "user", "content": message})

    try:
        response_data = await openrouter.chat_completion(
            messages=messages,
            model="gpt-4o-mini",
        )
        response = openrouter.get_content(response_data)
    except Exception as e:
        print(f"[HandleGeneral] Error: {e}")
        response = "죄송해요, 잠시 문제가 있었어요. 코딩 문제를 풀어볼까요?"

    return {
        "response_message": response,
        "next_node": "respond",
    }


async def handle_context_missing(state: ChatState) -> Dict[str, Any]:
    """
    컨텍스트가 필요한데 없을 때 처리

    예: 힌트 요청인데 현재 문제가 없는 경우
    """
    intent_result = state.get("intent_result", {})
    intent = intent_result.get("intent", "")

    if intent == "hint_request":
        response = "힌트를 드리려면 먼저 문제를 선택해야 해요! 어떤 문제를 풀어볼까요?"
        action_trigger = "search_problems"
    elif intent in ["code_review", "error_help", "submit_code"]:
        response = "코드를 확인하려면 먼저 코드가 필요해요! 코드 에디터에서 코드를 작성해주세요."
        action_trigger = None
    elif intent in ["skip_problem", "retry_problem"]:
        response = "현재 풀고 있는 문제가 없어요! 먼저 문제를 선택해볼까요?"
        action_trigger = "search_problems"
    else:
        response = "먼저 문제를 선택해주세요! 어떤 문제를 풀어볼까요?"
        action_trigger = "search_problems"

    return {
        "response_message": response,
        "action_trigger": action_trigger,
        "next_node": "respond",
    }


async def handle_out_of_scope(state: ChatState) -> Dict[str, Any]:
    """범위 밖 질문 처리"""
    response = "저는 코딩 학습 도우미라서 그 부분은 도움드리기 어려워요 😅 대신 재밌는 알고리즘 문제를 풀어볼까요?"

    return {
        "response_message": response,
        "action_data": {
            "suggested_actions": [
                {"label": "쉬운 문제 풀기", "value": "easy"},
                {"label": "랜덤 문제", "value": "random"},
            ]
        },
        "next_node": "respond",
    }


async def handle_affirmation(state: ChatState) -> Dict[str, Any]:
    """긍정 응답 처리 (네, 좋아요 등)"""
    # 이전 제안이 있었는지 확인
    search_results = state.get("search_results", [])
    generated_problem = state.get("generated_problem")

    if search_results or generated_problem:
        # 문제가 있으면 선택으로 처리
        return await handle_problem_selection_internal(state)
    else:
        response = "좋아요! 어떤 문제를 풀어볼까요?"
        return {
            "response_message": response,
            "next_node": "respond",
        }


async def handle_negation(state: ChatState) -> Dict[str, Any]:
    """부정 응답 처리 (아니요, 다른 거 등)"""
    response = "알겠어요! 다른 걸로 해볼까요? 어떤 주제나 난이도를 원하세요?"

    return {
        "response_message": response,
        "next_node": "respond",
    }


async def handle_problem_selection_internal(state: ChatState) -> Dict[str, Any]:
    """내부적으로 문제 선택 처리"""
    from .problem import handle_problem_selection
    return await handle_problem_selection(state)
