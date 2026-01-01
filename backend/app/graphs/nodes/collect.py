"""
Info Collection Node

사용자 메시지에서 문제 검색에 필요한 정보를 추출합니다.
(주제, 난이도, 언어 등)
"""
import json
from typing import Dict, Any
from ..state import ChatState, CollectedInfo


async def collect_info(state: ChatState) -> Dict[str, Any]:
    """
    사용자 메시지에서 정보를 추출하고,
    필요한 정보가 부족하면 추가 질문을 생성합니다.

    Returns:
        업데이트된 상태:
        - collected_info: 수집된 정보
        - is_info_complete: 검색 가능 여부
        - response_message: 응답 메시지 (추가 질문 또는 검색 안내)
        - next_node: 다음 노드
    """
    from ...services.openrouter import openrouter_service
    from ...prompts.free_chat_agent import FREE_CHAT_SYSTEM_PROMPT

    message = state.get("message", "")
    conversation_history = state.get("conversation_history", [])
    intent_result = state.get("intent_result", {})
    existing_info = state.get("collected_info", {})

    # 현재 상태 정보 구성
    context_info = _build_context_info(state)
    collected_str = json.dumps(existing_info, ensure_ascii=False, default=str)

    # 시스템 프롬프트 구성
    system_prompt = FREE_CHAT_SYSTEM_PROMPT.format(
        intent=intent_result.get("intent", "unknown"),
        confidence=intent_result.get("confidence", 0),
        requires_context=intent_result.get("requires_context"),
        context_info=context_info,
        collected_info=collected_str,
    )

    # LLM 호출
    messages = [
        {"role": "system", "content": system_prompt},
    ]

    # 대화 히스토리 추가
    for msg in conversation_history[-6:]:  # 최근 6개만
        messages.append({
            "role": msg.get("role", "user"),
            "content": msg.get("content", "")
        })

    messages.append({"role": "user", "content": message})

    try:
        response = await openrouter_service.chat_completion(
            messages=messages,
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
        )

        # API 응답에서 content 추출 및 JSON 파싱
        content = openrouter_service.get_content(response)
        result = openrouter_service.parse_json_response(content)

        # JSON 파싱 성공했는지 확인
        if not result or not isinstance(result, dict):
            raise ValueError("Invalid JSON response")

    except Exception as e:
        print(f"[CollectInfo] Error: {e}")
        # 스마트 폴백: 현재 상태에 따라 적절한 안내 메시지 제공
        if not existing_info.get("topics"):
            fallback_message = (
                "코딩 테스트에서 가장 자주 출제되는 유형은 **구현(Implementation)**, **그리디**, **DFS/BFS** 예요!\n\n"
                "초보자라면 **기초**부터 시작하는 걸 추천드려요. 어떤 주제로 해볼까요?"
            )
        elif not existing_info.get("difficulty"):
            fallback_message = "난이도를 선택해주세요! 실버, 골드, 플래티넘, 다이아, 마스터 중에 어떤 게 좋을까요?"
        elif not existing_info.get("language"):
            fallback_message = "어떤 프로그래밍 언어로 풀어볼까요? (Python, Java, C++)"
        else:
            fallback_message = "죄송해요, 잠시 문제가 있었어요. 다시 말씀해주시겠어요?"

        result = {
            "message": fallback_message,
            "collected_info": existing_info,
            "is_complete": False,
            "action_trigger": None,
        }

    # collected_info 업데이트 (기존 정보와 병합)
    new_info = result.get("collected_info") or {}  # None 방지
    merged_info: CollectedInfo = {
        "topics": new_info.get("topics") or existing_info.get("topics", []),
        "difficulty": new_info.get("difficulty") or existing_info.get("difficulty"),
        "language": new_info.get("language") or existing_info.get("language"),
        "specific_needs": new_info.get("specific_needs") or existing_info.get("specific_needs"),
        "time_available": new_info.get("time_available") or existing_info.get("time_available"),
        "selected_problem": new_info.get("selected_problem") or existing_info.get("selected_problem"),
        "selected_problem_index": new_info.get("selected_problem_index") or existing_info.get("selected_problem_index"),
    }

    is_complete = result.get("is_complete", False)
    action_trigger = result.get("action_trigger")
    intent = intent_result.get("intent", "")
    response_message = result.get("message", "")

    # 문제 검색 의도일 때 필수 필드 검증
    search_intents = {"new_problem", "topic_specific", "difficulty_change", "language_change"}
    if intent in search_intents and (is_complete or action_trigger == "search_problems"):
        # 언어가 없으면 물어봐야 함
        if not merged_info.get("language"):
            is_complete = False
            action_trigger = None
            response_message = "어떤 프로그래밍 언어로 풀어볼까요? (Python, Java, C++)"

    # 다음 노드 결정
    if action_trigger == "search_problems" or is_complete:
        next_node = "search_problems"
    elif action_trigger == "select_problem_type":
        next_node = "handle_problem_selection"
    else:
        next_node = "respond"  # 추가 질문 응답

    # random_recommend 의도도 단계별로 정보 수집
    if intent == "random_recommend":
        user_context = state.get("user_context", {})
        user_level = user_context.get("level", "beginner")

        # 1. 주제가 없으면 추천
        if not merged_info.get("topics"):
            is_complete = False
            response_message = (
                "어떤 알고리즘을 연습해볼까요?\n\n"
                "• **기초** - 조건문, 반복문, 배열\n"
                "• **정렬** - 버블, 퀵, 병합 정렬\n"
                "• **탐색** - 이분탐색, BFS, DFS\n"
                "• **DP** - 동적 프로그래밍\n"
                "• **그리디** - 탐욕 알고리즘\n\n"
                "잘 모르겠으면 '기초'로 시작해볼까요?"
            )
            next_node = "respond"
        # 2. 난이도가 없으면 유저 레벨 기반 추천
        elif not merged_info.get("difficulty"):
            is_complete = False
            # 유저 레벨에 따른 난이도 추천
            recommended = "easy" if user_level in ["beginner", "elementary"] else "medium"
            # 유저 레벨에 따른 추천 난이도 변환
            tier_recommended = {"easy": "실버", "medium": "골드"}.get(recommended, "실버")
            response_message = (
                f"난이도는 어떻게 할까요?\n\n"
                f"• **실버** - 기본 개념 익히기\n"
                f"• **골드** - 응용 문제\n"
                f"• **플래티넘** - 심화 문제\n"
                f"• **다이아** - 도전 문제\n"
                f"• **마스터** - 최상위 난이도\n\n"
                f"회원님 레벨 기준으로 **{tier_recommended}** 추천드려요!"
            )
            next_node = "respond"
        # 3. 언어가 없으면 물어보기
        elif not merged_info.get("language"):
            is_complete = False
            response_message = "어떤 프로그래밍 언어로 풀어볼까요? (Python, Java, C++)"
            next_node = "respond"
        # 4. 모두 있으면 검색
        else:
            next_node = "search_problems"
            is_complete = True

    return {
        "collected_info": merged_info,
        "is_info_complete": is_complete,
        "response_message": response_message,
        "action_trigger": action_trigger,
        "next_node": next_node,
    }


async def free_chat(state: ChatState) -> Dict[str, Any]:
    """
    자유 대화 처리 (의도가 명확하지 않을 때)

    Returns:
        업데이트된 상태:
        - response_message: 응답 메시지
    """
    from ...services.openrouter import openrouter_service

    message = state.get("message", "")
    conversation_history = state.get("conversation_history", [])
    intent_result = state.get("intent_result", {})

    system_prompt = """당신은 CodeFill의 친근한 코딩 학습 도우미입니다.
사용자와 자연스럽게 대화하면서 코딩 학습을 도와주세요.

현재 의도: {intent}

규칙:
- 친근하게 대화하세요
- 코딩 학습으로 자연스럽게 유도하세요
- 이모지는 적절히 사용하세요
""".format(intent=intent_result.get("intent", "unknown"))

    messages = [{"role": "system", "content": system_prompt}]
    for msg in conversation_history[-4:]:
        messages.append({
            "role": msg.get("role", "user"),
            "content": msg.get("content", "")
        })
    messages.append({"role": "user", "content": message})

    try:
        response = await openrouter_service.chat_completion(
            messages=messages,
            model="gpt-4o-mini",
        )
        content = openrouter_service.get_content(response)
    except Exception as e:
        print(f"[FreeChat] Error: {e}")
        content = "죄송해요, 잠시 문제가 있었어요. 다시 말씀해주세요!"

    return {
        "response_message": content,
        "next_node": "respond",
    }


def _build_context_info(state: ChatState) -> str:
    """현재 상태 정보를 문자열로 구성"""
    user_context = state.get("user_context", {})
    collected_info = state.get("collected_info", {})
    search_results = state.get("search_results", [])

    parts = []

    if user_context.get("current_problem"):
        parts.append(f"현재 문제: {user_context['current_problem'].get('title', 'Unknown')}")

    if collected_info.get("topics"):
        parts.append(f"선택한 주제: {', '.join(collected_info['topics'])}")

    if collected_info.get("difficulty"):
        parts.append(f"난이도: {collected_info['difficulty']}")

    if collected_info.get("language"):
        parts.append(f"언어: {collected_info['language']}")

    if search_results:
        problem_names = [p.get("name") or p.get("title", "Unknown") for p in search_results[:5]]
        parts.append(f"검색된 문제: {', '.join(problem_names)}")

    return "\n".join(parts) if parts else "없음"
