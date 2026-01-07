"""
Info Collection Node

사용자 메시지에서 문제 검색에 필요한 정보를 추출합니다.
(주제, 난이도, 언어 등)

🚀 Agentic 추천 시스템:
- 하드코딩 → LLM 기반 동적 suggested_actions 생성
- 사용자 컨텍스트 (약점, 최근 풀이, 목표) 기반 개인화

🚀 협업 필터링:
- 사용자 상호작용 로깅
- 유사 사용자 기반 추천
"""
import json
from typing import Dict, Any, List, Optional
from ..state import ChatState, CollectedInfo


# ============================================================
# 🚀 협업 필터링: 상호작용 로깅
# ============================================================

async def _log_collection_interaction(
    user_id: Optional[str],
    session_id: Optional[str],
    interaction_type: str,
    data: Dict[str, Any],
    user_context: Dict[str, Any],
):
    """
    정보 수집 단계에서 사용자 상호작용 로깅 (비차단)
    """
    if not user_id:
        return

    try:
        from ...services.collaborative_filtering import get_collaborative_service
        service = get_collaborative_service()

        user_metadata = {
            "goal": user_context.get("goal"),
            "level": user_context.get("level"),
        }

        await service.log_interaction(
            user_id=user_id,
            session_id=session_id,
            interaction_type=interaction_type,
            data=data,
            user_metadata=user_metadata,
        )
    except Exception as e:
        print(f"[CollaborativeFiltering] Log error (non-blocking): {e}")


# ============================================================
# 🚀 Agentic 추천 시스템: 동적 선택지 생성
# ============================================================

async def _generate_dynamic_topic_suggestions(
    user_context: dict,
    personalization: dict,
) -> tuple[str, List[dict]]:
    """
    LLM 기반 동적 주제 선택지 생성

    하드코딩 대신 사용자 컨텍스트를 분석하여 개인화된 추천을 생성합니다.

    Args:
        user_context: 사용자 온보딩 데이터
        personalization: 개인화 데이터 (weak_topics, recent_problems 등)

    Returns:
        (message, suggested_actions)
        - message: 응답 메시지
        - suggested_actions: [{label, value, description}]
    """
    from ...services.openrouter import openrouter_service

    # 컨텍스트 추출
    goal = user_context.get("goal", "")
    level = user_context.get("level", "beginner")
    weak_topics = personalization.get("skill_summary", {}).get("weak_topics", [])
    recent_problems = personalization.get("recent_problems", [])
    recommendations = personalization.get("recommendations", [])

    # 최근 학습 주제
    recent_topics = []
    for p in recent_problems[:3]:
        tags = p.get("tags") or p.get("topics") or []
        recent_topics.extend(tags[:2])
    recent_topics = list(set(recent_topics))[:3]

    # 추천에서 주제 추출
    recommended_topics = []
    for rec in recommendations[:2]:
        rec_topics = rec.get("topics", [])
        recommended_topics.extend(rec_topics)

    context_info = {
        "goal": goal,
        "level": level,
        "weak_topics": weak_topics[:3],
        "recent_topics": recent_topics,
        "recommended_topics": recommended_topics[:2],
        "has_history": personalization.get("has_history", False),
    }

    # LLM 프롬프트
    system_prompt = """당신은 코딩 교육 플랫폼의 개인화 추천 엔진입니다.
사용자 컨텍스트를 분석하여 맞춤형 주제 선택지를 생성하세요.

## 사용자 컨텍스트
{context}

## 규칙
1. 3-4개의 주제 선택지를 생성하세요
2. 각 선택지는 사용자 상황에 맞게 개인화된 설명을 포함하세요
3. 약점 주제가 있으면 우선 추천하세요
4. 최근 학습 주제가 있으면 "이어서" 학습 옵션을 포함하세요
5. 목표(대기업 코테 등)에 맞는 중요 주제를 포함하세요

## 응답 형식 (JSON)
{{
  "message": "친근한 질문 메시지 (1-2문장)",
  "suggested_actions": [
    {{
      "label": "주제명 (짧게)",
      "value": "topic_value",
      "description": "개인화된 이유 설명 (10자 이내)"
    }}
  ]
}}

## 가능한 주제 값 (value)
- dp: 동적 프로그래밍
- graph: 그래프 (BFS, DFS)
- implementation: 구현/시뮬레이션
- sorting: 정렬
- binary_search: 이분탐색
- string: 문자열
- greedy: 그리디
- data_structure: 자료구조 (스택, 큐, 해시)
- tree: 트리
- recursion: 재귀
- math: 수학
""".format(context=json.dumps(context_info, ensure_ascii=False, indent=2))

    try:
        response = await openrouter_service.chat_completion(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "사용자 컨텍스트에 맞는 주제 선택지를 생성해주세요."},
            ],
            temperature=0.7,
            max_tokens=500,
            response_format={"type": "json_object"},
        )

        content = openrouter_service.get_content(response)
        result = openrouter_service.parse_json_response(content)

        message = result.get("message", "어떤 주제로 연습해볼까요?")
        suggested_actions = result.get("suggested_actions", [])

        # 값 정규화 (한글 → 영어 값)
        topic_value_map = {
            "DP": "dp", "동적 프로그래밍": "dp", "dp": "dp",
            "그래프": "graph", "graph": "graph",
            "구현": "implementation", "implementation": "implementation",
            "정렬": "sorting", "sorting": "sorting",
            "이분탐색": "binary_search", "binary_search": "binary_search",
            "문자열": "string", "string": "string",
            "그리디": "greedy", "greedy": "greedy",
            "자료구조": "data_structure", "data_structure": "data_structure",
            "트리": "tree", "tree": "tree",
            "재귀": "recursion", "recursion": "recursion",
            "수학": "math", "math": "math",
        }

        for action in suggested_actions:
            value = action.get("value", "")
            action["value"] = topic_value_map.get(value, value)

        print(f"[Agentic:TopicSuggestion] Generated {len(suggested_actions)} suggestions")
        return message, suggested_actions

    except Exception as e:
        print(f"[Agentic:TopicSuggestion] LLM error, using fallback: {e}")
        # 폴백: 기본 선택지
        return _get_fallback_topic_suggestions(user_context, personalization)


def _get_fallback_topic_suggestions(
    user_context: dict,
    personalization: dict,
) -> tuple[str, List[dict]]:
    """
    LLM 실패 시 폴백 선택지 (규칙 기반)
    """
    goal = user_context.get("goal", "")
    weak_topics = personalization.get("skill_summary", {}).get("weak_topics", [])

    suggested_actions = []

    # 약점 주제 우선
    if weak_topics:
        weak = weak_topics[0]
        suggested_actions.append({
            "label": f"{weak} (약점 보완)",
            "value": weak.lower().replace(" ", "_"),
            "description": "연습 필요"
        })

    # 대기업 목표면 필수 주제
    if "대기업" in goal or "코테" in goal:
        if not any(a.get("value") == "dp" for a in suggested_actions):
            suggested_actions.append({
                "label": "DP",
                "value": "dp",
                "description": "대기업 필수"
            })
        if not any(a.get("value") == "graph" for a in suggested_actions):
            suggested_actions.append({
                "label": "그래프",
                "value": "graph",
                "description": "빈출 유형"
            })

    # 기본 추가
    default_topics = [
        {"label": "구현", "value": "implementation", "description": "기본기 연습"},
        {"label": "정렬", "value": "sorting", "description": "정석 알고리즘"},
    ]

    for topic in default_topics:
        if len(suggested_actions) >= 4:
            break
        if not any(a.get("value") == topic["value"] for a in suggested_actions):
            suggested_actions.append(topic)

    message = "어떤 알고리즘을 연습해볼까요?"
    return message, suggested_actions[:4]


async def _generate_dynamic_difficulty_suggestions(
    user_context: dict,
    personalization: dict,
    selected_topic: str = None,
) -> tuple[str, List[dict]]:
    """
    동적 난이도 선택지 생성

    사용자 실력과 선택 주제를 고려하여 적절한 난이도를 추천합니다.
    """
    level = user_context.get("level", "beginner")
    skill_summary = personalization.get("skill_summary", {})
    preferred_difficulty = skill_summary.get("preferred_difficulty", "easy")

    # 난이도 순서
    diff_order = ["easy", "medium", "medium_hard", "hard", "very_hard"]
    diff_display = {
        "easy": ("실버", "기본 개념 익히기"),
        "medium": ("골드", "응용력 키우기"),
        "medium_hard": ("플래티넘", "심화 문제 도전"),
        "hard": ("다이아", "고급 알고리즘"),
        "very_hard": ("마스터", "최상위 난이도"),
    }

    suggested_actions = []

    # 1. 추천 난이도 (가장 먼저)
    if preferred_difficulty in diff_display:
        name, desc = diff_display[preferred_difficulty]
        suggested_actions.append({
            "label": f"{name} (추천)",
            "value": preferred_difficulty,
            "description": "실력에 맞춰요"
        })

    # 2. 한 단계 높은 난이도 (도전)
    try:
        curr_idx = diff_order.index(preferred_difficulty)
        if curr_idx < len(diff_order) - 1:
            next_diff = diff_order[curr_idx + 1]
            name, desc = diff_display[next_diff]
            suggested_actions.append({
                "label": f"{name} (도전)",
                "value": next_diff,
                "description": "한 단계 업!"
            })
    except ValueError:
        pass

    # 3. 한 단계 낮은 난이도 (복습)
    try:
        curr_idx = diff_order.index(preferred_difficulty)
        if curr_idx > 0:
            prev_diff = diff_order[curr_idx - 1]
            name, desc = diff_display[prev_diff]
            suggested_actions.append({
                "label": name,
                "value": prev_diff,
                "description": "기초 다지기"
            })
    except ValueError:
        pass

    # 4. 레벨 기반 기본 추천
    if not suggested_actions:
        if level in ["beginner", "elementary"]:
            suggested_actions = [
                {"label": "실버 (추천)", "value": "easy", "description": "기본부터"},
                {"label": "골드", "value": "medium", "description": "도전해볼까요?"},
            ]
        else:
            suggested_actions = [
                {"label": "골드 (추천)", "value": "medium", "description": "적당한 난이도"},
                {"label": "플래티넘", "value": "medium_hard", "description": "도전!"},
            ]

    message = "난이도를 선택해주세요!"
    return message, suggested_actions[:4]


async def collect_info(state: ChatState) -> Dict[str, Any]:
    """
    사용자 메시지에서 정보를 추출하고,
    필요한 정보가 부족하면 추가 질문을 생성합니다.

    히스토리 기반 추천:
    - new_problem intent일 때 user_context["personalization"]에서 추천 정보 확인
    - 추천이 있으면 자동으로 topic/difficulty 설정하고 확인 질문
    - 추천이 없으면 기존 로직 (LLM 기반 정보 수집)

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
    user_context = state.get("user_context", {})
    intent = intent_result.get("intent", "")

    # ============================================================
    # 히스토리 기반 개인화 추천 (new_problem intent)
    # ============================================================
    if intent in ["new_problem", "random_recommend"] and not existing_info.get("topics"):
        personalized = _generate_personalized_recommendation(user_context)

        if personalized.get("has_recommendation"):
            # 개인화 추천이 있으면 자동으로 정보 설정
            rec_topics = personalized.get("topics", [])
            rec_difficulty = personalized.get("difficulty")
            rec_message = personalized.get("message", "")
            rec_type = personalized.get("recommendation_type", "")

            # 언어가 있으면 바로 검색, 없으면 언어만 물어보기
            language = existing_info.get("language")

            merged_info = {
                "topics": rec_topics,
                "difficulty": rec_difficulty,
                "language": language,
                "specific_needs": None,
                "time_available": None,
                "selected_problem": None,
                "selected_problem_index": None,
            }

            if language:
                # 언어까지 있으면 추천 메시지 + 바로 검색
                return {
                    "collected_info": merged_info,
                    "is_info_complete": True,
                    "response_message": rec_message,
                    "action_trigger": "search_problems",
                    "next_node": "search_problems",
                }
            else:
                # 언어 선택 필요
                return {
                    "collected_info": merged_info,
                    "is_info_complete": False,
                    "response_message": f"{rec_message}\n\n어떤 언어로 풀어볼까요? (Python, Java, C++)",
                    "action_trigger": None,
                    "next_node": "respond",
                }

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
                "대기업 코테에서 가장 자주 출제되는 유형은 **DP**, **그래프**, **구현** 이에요!\n\n"
                "어떤 주제로 해볼까요? 회원님의 목표에 맞게 추천해드릴게요."
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

    # 🚀 협업 필터링: 새로운 선택 로깅 (비차단)
    user_id = user_context.get("user_id")
    session_id = state.get("session_id")

    if new_info.get("topics") and new_info.get("topics") != existing_info.get("topics"):
        await _log_collection_interaction(
            user_id=user_id,
            session_id=session_id,
            interaction_type="topic_select",
            data={"topic": new_info["topics"][0] if new_info["topics"] else None},
            user_context=user_context,
        )

    if new_info.get("difficulty") and new_info.get("difficulty") != existing_info.get("difficulty"):
        await _log_collection_interaction(
            user_id=user_id,
            session_id=session_id,
            interaction_type="difficulty_select",
            data={"difficulty": new_info["difficulty"]},
            user_context=user_context,
        )

    if new_info.get("language") and new_info.get("language") != existing_info.get("language"):
        await _log_collection_interaction(
            user_id=user_id,
            session_id=session_id,
            interaction_type="language_select",
            data={"language": new_info["language"]},
            user_context=user_context,
        )

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
    suggested_actions = None  # 🚀 동적 선택지

    if intent == "random_recommend":
        user_context = state.get("user_context", {})
        personalization = user_context.get("personalization", {})

        # 1. 주제가 없으면 🚀 동적 선택지 생성
        if not merged_info.get("topics"):
            is_complete = False
            response_message, suggested_actions = await _generate_dynamic_topic_suggestions(
                user_context=user_context,
                personalization=personalization,
            )
            next_node = "respond"

        # 2. 난이도가 없으면 🚀 동적 난이도 선택지
        elif not merged_info.get("difficulty"):
            is_complete = False
            selected_topic = merged_info.get("topics", [None])[0]
            response_message, suggested_actions = await _generate_dynamic_difficulty_suggestions(
                user_context=user_context,
                personalization=personalization,
                selected_topic=selected_topic,
            )
            next_node = "respond"

        # 3. 언어가 없으면 물어보기 (간단한 선택지)
        elif not merged_info.get("language"):
            is_complete = False
            response_message = "어떤 프로그래밍 언어로 풀어볼까요?"
            suggested_actions = [
                {"label": "Python", "value": "python", "description": "인기 1위"},
                {"label": "Java", "value": "java", "description": "기업 선호"},
                {"label": "C++", "value": "cpp", "description": "성능 최적화"},
            ]
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
        "suggested_actions": suggested_actions,  # 🚀 동적 선택지 포함
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
    personalization = user_context.get("personalization", {})

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

    # 개인화 정보 추가 (히스토리 기반 추천에 활용)
    if personalization.get("has_history"):
        recent = personalization.get("recent_problems", [])
        if recent:
            recent_names = [p.get("name", "") for p in recent[:3]]
            parts.append(f"최근 풀이: {', '.join(recent_names)}")

        recommendations = personalization.get("recommendations", [])
        if recommendations:
            rec = recommendations[0]
            rec_type = rec.get("type", "")
            rec_topics = rec.get("topics", [])
            rec_reason = rec.get("reason", "")
            if rec_topics:
                parts.append(f"추천 주제: {rec_topics[0]} ({rec_type}: {rec_reason})")

    return "\n".join(parts) if parts else "없음"


def _generate_personalized_recommendation(user_context: dict) -> dict:
    """
    사용자 히스토리 기반 개인화 추천 생성

    Returns:
        {
            "has_recommendation": bool,
            "topics": list[str],
            "difficulty": str,
            "message": str,
            "recommendation_type": str,  # level_up, retry, weak_topic
        }
    """
    personalization = user_context.get("personalization", {})

    if not personalization.get("has_history"):
        return {"has_recommendation": False}

    recommendations = personalization.get("recommendations", [])
    recent_problems = personalization.get("recent_problems", [])
    skill_summary = personalization.get("skill_summary", {})

    if not recommendations:
        return {"has_recommendation": False}

    # 첫 번째 추천 사용
    rec = recommendations[0]
    rec_type = rec.get("type")
    rec_topics = rec.get("topics", [])
    rec_difficulty = rec.get("difficulty")
    rec_reason = rec.get("reason", "")

    # 난이도 한글 변환
    diff_display = {
        "easy": "쉬움", "medium": "보통",
        "medium_hard": "중상", "hard": "어려움", "very_hard": "매우 어려움"
    }.get(rec_difficulty, rec_difficulty)

    # 추천 타입별 동적 메시지 생성
    if rec_type == "level_up" and rec_topics:
        topic = rec_topics[0]
        message = (
            f"💡 지난번에 **{topic}** 문제를 잘 푸셨네요!\n"
            f"이번엔 **{diff_display}** 난이도로 도전해볼까요?\n\n"
            f"바로 검색할까요, 아니면 다른 주제를 원하시나요?"
        )
    elif rec_type == "retry" and rec_topics:
        topic = rec_topics[0]
        message = (
            f"💪 **{topic}** 연습이 더 필요해 보여요!\n"
            f"같은 난이도로 비슷한 문제 찾아볼까요?"
        )
    elif rec_type == "weak_topic" and rec_topics:
        topic = rec_topics[0]
        weak_topics = skill_summary.get("weak_topics", [])
        message = (
            f"📚 **{topic}**은(는) 아직 연습이 더 필요해요!\n"
            f"쉬운 문제부터 차근차근 풀어볼까요?"
        )
        rec_difficulty = "easy"
    else:
        return {"has_recommendation": False}

    return {
        "has_recommendation": True,
        "topics": rec_topics[:1],  # 첫 번째 주제만
        "difficulty": rec_difficulty,
        "message": message,
        "recommendation_type": rec_type,
    }
