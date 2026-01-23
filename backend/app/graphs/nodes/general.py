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

    문제 풀이 중일 때는 현재 상황 정보를 포함하여 관련 질문에 대답할 수 있도록 함
    """
    from ...services.openrouter import OpenRouterService
    import json

    message = state.get("message", "")
    conversation_history = state.get("conversation_history", [])
    intent_result = state.get("intent_result", {})
    current_practice_state = state.get("current_practice_state", {})

    openrouter = OpenRouterService()

    # 기본 시스템 프롬프트
    system_prompt = """당신은 CodeFill의 친근한 코딩 학습 도우미입니다.
사용자와 자연스럽게 대화하면서 코딩 학습으로 유도해주세요.

규칙:
- 친근하고 격려하는 톤
- 코딩/알고리즘 관련 대화로 자연스럽게 유도
- 범위를 벗어난 질문은 정중히 거절하고 학습으로 돌아오게 유도
- 이모지 적절히 사용
"""

    # 문제 풀이 중일 때 현재 상황 정보 추가
    if current_practice_state and current_practice_state.get("problem_id"):
        problem_type = current_practice_state.get("problem_type", "")
        problem_title = current_practice_state.get("problem_title", "")
        previous_hints = current_practice_state.get("previous_hints", [])

        practice_context = f"""

## 현재 문제 풀이 상황
- **문제**: {problem_title}
- **유형**: {problem_type}
"""

        # 빈칸 문제일 때
        if problem_type == "blank":
            blank_answers = current_practice_state.get("blank_answers", {})
            used_hint_indices = current_practice_state.get("used_hint_indices", [])

            if blank_answers:
                answers_info = ", ".join([f"{k}: '{v}'" for k, v in blank_answers.items() if v])
                practice_context += f"- **현재 입력한 답변**: {answers_info}\n"

            if used_hint_indices:
                practice_context += f"- **힌트 사용한 빈칸**: {used_hint_indices}\n"

        # 퍼즐 문제일 때
        elif problem_type == "puzzle":
            puzzle_user_order = current_practice_state.get("puzzle_user_order", [])
            used_hint_indices = current_practice_state.get("used_hint_indices", [])

            if puzzle_user_order:
                practice_context += f"- **현재 블록 배치 순서**: {len(puzzle_user_order)}개 블록 배치됨\n"

            if used_hint_indices:
                practice_context += f"- **힌트 사용한 블록 위치**: {used_hint_indices}\n"

        # guided 모드일 때
        elif problem_type == "guided":
            current_code = current_practice_state.get("current_code", "")
            if current_code:
                # 코드가 너무 길면 축약
                code_preview = current_code[:500] + "..." if len(current_code) > 500 else current_code
                practice_context += f"- **현재 작성 중인 코드**:\n```\n{code_preview}\n```\n"

        # 이전 힌트 정보
        if previous_hints:
            hints_summary = previous_hints[-3:]  # 최근 3개 힌트만
            practice_context += f"- **이전에 받은 힌트** ({len(previous_hints)}개):\n"
            for i, hint in enumerate(hints_summary, 1):
                hint_preview = hint[:100] + "..." if len(hint) > 100 else hint
                practice_context += f"  {i}. {hint_preview}\n"

        practice_context += """
## 추가 규칙
- 사용자가 현재 풀고 있는 문제와 관련된 질문을 하면 위 정보를 참고하여 도움을 주세요
- 이미 제공된 힌트 내용을 참고하여 중복되지 않는 도움을 주세요
- 직접적인 정답은 알려주지 않고, 사고 과정을 돕는 방향으로 안내하세요
- 사용자가 입력한 답변이 있으면 그것을 바탕으로 피드백을 줄 수 있어요
"""

        system_prompt += practice_context

    messages = [{"role": "system", "content": system_prompt}]
    for msg in conversation_history[-6:]:  # 꼬리 질문 맥락 유지
        messages.append({
            "role": msg.get("role", "user"),
            "content": msg.get("content", "")
        })
    messages.append({"role": "user", "content": message})

    try:
        response_data = await openrouter.chat_completion(
            messages=messages,
            model="gpt-4o-mini",
            max_tokens=180,  # 2-3문장으로 간결하게
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


async def handle_inappropriate_message(state: ChatState) -> Dict[str, Any]:
    """
    부적절한 메시지 처리 (욕설, 비속어, 의미없는 입력)

    공격적이지 않게 코딩 학습으로 자연스럽게 유도
    """
    response = "저는 코딩 학습을 도와드리는 AI예요. 함께 알고리즘 문제를 풀면서 실력을 키워볼까요? 💻"

    return {
        "response_message": response,
        "action_data": {
            "suggested_actions": [
                {"label": "쉬운 문제부터", "value": "easy"},
                {"label": "추천받기", "value": "recommend"},
                {"label": "주제 선택", "value": "topic"},
            ]
        },
        "next_node": "respond",
    }


async def handle_affirmation(state: ChatState) -> Dict[str, Any]:
    """
    긍정 응답 처리 (네, 좋아요 등)

    - 문제 검색 결과가 있으면 → 문제 선택
    - 추천 주제/난이도가 있으면 → 언어 확인 후 검색 진행
    - 🚀 CF 추천 수락 시 클릭 이벤트 트래킹
    """
    search_results = state.get("search_results", [])
    generated_problem = state.get("generated_problem")
    collected_info = state.get("collected_info", {})
    user_context = state.get("user_context", {})

    if search_results or generated_problem:
        # 문제가 있으면 선택으로 처리
        return await handle_problem_selection_internal(state)

    # 추천을 수락한 경우: topics와 difficulty가 있으면 검색 진행
    if collected_info.get("topics") and collected_info.get("difficulty"):
        # 🚀 CF 추천 수락 시 클릭 이벤트 트래킹
        rec_type = collected_info.get("recommendation_type", "")
        if rec_type.startswith("cf_"):
            try:
                from ...services.collaborative_filtering import get_collaborative_service
                cf_service = get_collaborative_service()
                user_id = user_context.get("user_id")
                if user_id:
                    await cf_service.track_recommendation_click(
                        user_id=user_id,
                        topic=collected_info["topics"][0],
                        difficulty=collected_info["difficulty"],
                    )
            except Exception as e:
                print(f"[HandleAffirmation] CF tracking error (non-blocking): {e}")

        if collected_info.get("language"):
            # 모든 정보가 있으면 바로 검색
            return {
                "response_message": "좋아요! 문제를 찾아볼게요!",
                "collected_info": collected_info,
                "is_info_complete": True,
                "action_trigger": "search_problems",
                "next_node": "search_problems",
            }
        else:
            # 언어만 물어보기
            return {
                "response_message": "좋아요! 어떤 프로그래밍 언어로 풀어볼까요?",
                "collected_info": collected_info,
                "is_info_complete": False,
                "suggested_actions": [
                    {"label": "Python", "value": "python", "description": "인기 1위"},
                    {"label": "Java", "value": "java", "description": "기업 선호"},
                    {"label": "C++", "value": "cpp", "description": "성능 최적화"},
                ],
                "next_node": "respond",
            }

    # 기본 응답
    response = "좋아요! 어떤 문제를 풀어볼까요?"
    return {
        "response_message": response,
        "next_node": "respond",
    }


async def handle_negation(state: ChatState) -> Dict[str, Any]:
    """
    부정 응답 처리 (아니요, 다른 거 등)

    핵심: 현재 추천된 topics를 rejected_topics에 추가하고 초기화
    → 다음 추천에서 rejected_topics 제외
    """
    from .collect import _generate_dynamic_topic_suggestions

    collected_info = state.get("collected_info", {})
    user_context = state.get("user_context", {})
    personalization = user_context.get("personalization", {})

    # 현재 topics를 rejected_topics에 추가
    current_topics = collected_info.get("topics", [])
    rejected_topics = list(collected_info.get("rejected_topics", []))

    for topic in current_topics:
        if topic and topic not in rejected_topics:
            rejected_topics.append(topic)

    # 새로운 collected_info 생성 (topics, difficulty 초기화)
    new_collected_info = {
        "topics": [],  # 초기화
        "difficulty": None,  # 초기화
        "language": collected_info.get("language"),  # 언어는 유지
        "specific_needs": None,
        "time_available": None,
        "selected_problem": None,
        "selected_problem_index": None,
        "rejected_topics": rejected_topics,  # 거부된 주제들 누적
    }

    # 새로운 주제 선택지 생성 (rejected_topics 제외)
    try:
        # personalization에 rejected_topics 정보 추가
        enriched_personalization = dict(personalization)
        enriched_personalization["rejected_topics"] = rejected_topics

        message, suggested_actions = await _generate_dynamic_topic_suggestions(
            user_context=user_context,
            personalization=enriched_personalization,
        )

        # rejected_topics에 있는 주제는 제외
        filtered_actions = [
            action for action in suggested_actions
            if action.get("value") not in rejected_topics
        ]

        if not filtered_actions:
            # 모든 추천이 거부됨 - 기본 선택지 제공
            filtered_actions = [
                {"label": "구현", "value": "implementation", "description": "기본기 연습"},
                {"label": "문자열", "value": "string", "description": "문자열 처리"},
                {"label": "수학", "value": "math", "description": "수학 문제"},
            ]
            # rejected에 없는 것만 필터
            filtered_actions = [
                a for a in filtered_actions if a.get("value") not in rejected_topics
            ]

        response = f"알겠어요! {message if filtered_actions else '다른 주제를 직접 입력해주세요!'}"

    except Exception as e:
        print(f"[HandleNegation] Error generating suggestions: {e}")
        response = "알겠어요! 다른 주제로 해볼까요? 어떤 알고리즘을 연습하고 싶으세요?"
        filtered_actions = [
            {"label": "DP", "value": "dp", "description": "동적 프로그래밍"},
            {"label": "그래프", "value": "graph", "description": "BFS/DFS"},
            {"label": "구현", "value": "implementation", "description": "시뮬레이션"},
        ]
        filtered_actions = [
            a for a in filtered_actions if a.get("value") not in rejected_topics
        ]

    return {
        "response_message": response,
        "collected_info": new_collected_info,
        "suggested_actions": filtered_actions[:4] if filtered_actions else None,
        "next_node": "respond",
    }


async def handle_problem_selection_internal(state: ChatState) -> Dict[str, Any]:
    """내부적으로 문제 선택 처리"""
    from .problem import handle_problem_selection
    return await handle_problem_selection(state)
