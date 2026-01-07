"""
Handle Question Node (Structured Output)

사용자가 질문을 할 때 LLM으로 답변 생성
Structured output으로 안정적인 추천값 추출

Tool 기반 개인화:
- get_user_profile: DB에서 사용자 프로필 조회
- get_personalized_recommendations: 프로필 기반 추천 생성
"""
import json
from typing import Dict, Any, Optional
from ..state import CollectionState, DIFFICULTY_TO_TIER


# ============================================================
# Tool 호출 함수
# ============================================================

async def fetch_user_profile_and_recommendations(user_id: Optional[str], user_context: dict) -> dict:
    """
    사용자 프로필을 DB에서 조회하고 개인화 추천 생성

    Args:
        user_id: 사용자 UUID (없으면 user_context에서 추출 시도)
        user_context: 프론트엔드에서 전달된 컨텍스트

    Returns:
        {
            "profile": UserProfileResult.to_dict(),
            "recommendations": RecommendationResult.to_dict(),
            "from_db": bool  # DB에서 조회했는지 여부
        }
    """
    from app.tools.user_tools import get_user_tools

    tools = get_user_tools()

    # user_id 추출 (여러 소스에서)
    if not user_id:
        user_id = user_context.get("user_id") or user_context.get("id")

    profile_data = None
    from_db = False

    # 1. DB에서 프로필 조회 시도
    if user_id:
        profile = await tools.get_user_profile(user_id)
        if profile.success:
            profile_data = profile
            from_db = True
            print(f"[handle_question] Fetched profile from DB: {profile.experience_level}, {profile.learning_goal}")

    # 2. 프로필 기반 추천 생성
    if profile_data:
        recommendations = tools.get_personalized_recommendations(profile=profile_data)
    else:
        # DB 조회 실패 시 user_context에서 추출
        recommendations = tools.get_personalized_recommendations(
            experience_level=user_context.get("experience_level"),
            learning_goal=user_context.get("learning_goal"),
            strong_algorithms=user_context.get("strong_algorithms"),
            preferred_difficulty=user_context.get("preferred_difficulty"),
        )

    return {
        "profile": profile_data.to_dict() if profile_data else None,
        "recommendations": recommendations.to_dict(),
        "from_db": from_db,
    }


# 현재 단계별 추천 옵션 (UI 표시용)
STEP_RECOMMENDATIONS = {
    "topic": {
        "options": ["DP", "그래프", "정렬", "구현", "기초"],
        "default": "DP",
        "display_name": "주제",
    },
    "difficulty": {
        "options": ["실버", "골드", "플래티넘", "다이아", "마스터"],
        "options_db": ["easy", "medium", "medium_hard", "hard", "very_hard"],
        "default": "실버",
        "display_name": "티어",
    },
    "language": {
        "options": ["Python", "Java", "C++"],
        "default": "Python",
        "display_name": "언어",
    },
}

# NOTE: 개인화 추천 로직은 user_tools.py의 UserTools 클래스로 이전됨
# - EXPERIENCE_TO_DIFFICULTY → user_tools.LEVEL_TO_DIFFICULTY
# - EXPERIENCE_TO_TOPICS → user_tools.BIG_TECH_TOP_ALGORITHMS 등
# - GOAL_TO_TOPICS → user_tools.COMPANY_ALGORITHM_FREQUENCY
# - get_personalized_recommendations → UserTools.get_personalized_recommendations

# 티어명 → DB값 매핑
TIER_TO_DB = {
    "실버": "easy", "골드": "medium", "플래티넘": "medium_hard",
    "다이아": "hard", "마스터": "very_hard",
}

# 난이도 순서 (인덱스로 상대적 조정 가능)
DIFFICULTY_ORDER = ["easy", "medium", "medium_hard", "hard", "very_hard"]


# 질문 유형별 프롬프트 (추천값 생성 포함)
QUESTION_PROMPTS = {
    "recommendation": """
사용자가 주제/난이도/언어 추천을 요청했습니다.

현재 수집 단계: {current_step}
수집된 정보:
- 주제: {topic}
- 난이도: {difficulty}
- 언어: {language}

사용자 메시지: "{message}"

친절하게 추천해주세요. 반드시 아래 형식으로 답변하세요:

1. 먼저 질문에 대한 짧은 답변 (1-2문장)
2. 그 다음 구체적인 추천값 제안

중요: 답변 마지막에 반드시 하나의 구체적인 값을 추천하세요.
예시:
- topic 단계: "DP로 해볼까요?"
- difficulty 단계: "골드로 할까요?"
- language 단계: "Python으로 할까요?"

현재 단계에 맞는 추천:
- topic: 기초, DP, 그래프, 정렬, 구현, 문자열 중 하나
- difficulty: 실버, 골드, 플래티넘, 다이아, 마스터 중 하나
- language: Python, Java, C++ 중 하나
""",
    "explanation": """
사용자가 알고리즘/용어에 대한 설명을 요청했습니다.

현재 수집 단계: {current_step}
수집된 정보:
- 주제: {topic}
- 난이도: {difficulty}
- 언어: {language}

사용자 메시지: "{message}"

1. 간단하게 설명해주세요 (2-3문장)
2. 그리고 현재 단계({current_step})에 맞는 값을 하나 추천하세요

중요: 답변 마지막에 반드시 구체적인 값을 추천하세요.
예: "DP로 시작해볼까요?" 또는 "골드로 할까요?"
""",
    "comparison": """
사용자가 비교/차이점을 물어봤습니다.

현재 수집 단계: {current_step}
수집된 정보:
- 주제: {topic}
- 난이도: {difficulty}
- 언어: {language}

사용자 메시지: "{message}"

1. 간단히 비교해주세요 (2-3문장)
2. 그리고 현재 단계({current_step})에 맞는 값을 하나 추천하세요

중요: 답변 마지막에 반드시 구체적인 값을 추천하세요.
예: "그래프로 해볼까요?" 또는 "플래티넘으로 할까요?"
""",
    "general": """
사용자가 질문을 했습니다.

현재 수집 단계: {current_step}
수집된 정보:
- 주제: {topic}
- 난이도: {difficulty}
- 언어: {language}

사용자 메시지: "{message}"

1. 친절하게 답변하세요 (1-2문장)
2. 그리고 현재 단계({current_step})에 맞는 값을 하나 추천하세요

중요: 답변 마지막에 반드시 구체적인 값을 추천하세요.
예: "DP로 해볼까요?" 또는 "Python으로 할까요?"
""",
    "rejection": """
사용자가 이전 추천을 거절했거나 추천을 요청했습니다.

현재 수집 단계: {current_step}
수집된 정보:
- 주제: {topic}
- 난이도: {difficulty}
- 언어: {language}

사용자 메시지: "{message}"
이전에 거절된 값들: {rejected_values}
거절 이유 힌트: {rejection_reason}

중요 지침:
1. 거절된 값들({rejected_values})은 절대 다시 추천하지 마세요!
2. 거절 이유에 맞게 추천하세요:
   - "too_hard" → 더 낮은 티어 추천
   - "too_easy" → 더 높은 티어 추천
   - "already_done" → 완전히 다른 주제 추천
   - "unknown/beginner" → 사용자 프로필 기반 추천 (개인화 힌트 참고!)
   - "not_interested" → 다른 계열의 주제 추천
3. 공감하는 말로 시작하세요 (예: "알겠어요!", "그럼 다른 걸로!", "좋아요!")
4. 새로운 추천을 자연스럽게 제시하고 "~로 해볼까요?" 형식으로 마무리
5. **개인화 힌트가 있으면 그것을 우선 참고하세요!**

현재 단계에 맞는 선택지:
- topic: DP, 그래프, 정렬, 구현, 문자열, 이분탐색, 백트래킹, 기초
- difficulty: 실버, 골드, 플래티넘, 다이아, 마스터
- language: Python, Java, C++
""",
}

# 거절 이유별 메시지 (하드코딩된 topic/difficulty 제거 - Tool 기반 개인화 사용)
REJECTION_SUGGESTIONS = {
    "too_hard": {
        "message_prefix": "더 쉬운 난이도로 추천해드릴게요! ",
        "difficulty_adjustment": "lower",  # 난이도 낮추기
    },
    "too_easy": {
        "message_prefix": "도전적인 난이도를 원하시는군요! ",
        "difficulty_adjustment": "higher",  # 난이도 높이기
    },
    "already_done": {
        "message_prefix": "이미 해보셨군요! 다른 주제로 ",
    },
    "unknown": {
        # 하드코딩된 "기초" 제거 - 사용자 프로필 기반 추천 사용
        "message_prefix": "잘 모르시겠군요! 회원님께 맞는 추천을 해드릴게요. ",
        "use_profile_recommendation": True,
    },
    "beginner": {
        # 하드코딩된 "기초" 제거 - 사용자 프로필 기반 추천 사용
        "message_prefix": "입문자시군요! 회원님께 맞는 추천을 해드릴게요. ",
        "use_profile_recommendation": True,
    },
    "not_interested": {
        "message_prefix": "그럼 완전히 다른 걸로! ",
    },
    "want_choose": {
        "message_prefix": "직접 선택하고 싶으시군요! 선택지를 보여드릴게요:\n",
        "show_options": True,
    },
}

# 현재 단계별 선택 유도 메시지 (사용하지 않음 - LLM이 직접 추천)
STEP_GUIDANCE = {
    "topic": "\n\n어떤 알고리즘 주제로 해볼까요?",
    "difficulty": "\n\n어떤 난이도로 할까요? (실버/골드/플래티넘/다이아/마스터)",
    "language": "\n\n어떤 언어로 풀어볼까요? (Python/Java/C++)",
}


async def handle_question(state: CollectionState) -> Dict[str, Any]:
    """
    질문에 대한 답변 생성

    LLM을 사용하여 친절한 답변 + 추천값 생성
    "네/아니오" 칩과 함께 awaiting_confirmation 상태로 전환

    rejection 타입일 때는 거절 맥락을 활용한 스마트 추천
    Tool 기반 사용자 프로필 조회 및 개인화 추천 적용
    """
    # Import inside function to avoid circular imports
    from app.services.openrouter import openrouter_service
    import re

    question_type = state.get("question_type", "general")
    current_step = state.get("current_step", "topic")
    message = state.get("message", "")
    rejected_values = state.get("rejected_values", [])
    rejection_reason = state.get("rejection_reason")

    # ============================================================
    # Tool 호출: DB에서 사용자 프로필 조회 및 개인화 추천 생성
    # ============================================================
    user_context = state.get("user_context", {}) or {}
    user_id = user_context.get("user_id") or user_context.get("id")

    # DB에서 프로필 조회 시도 (user_id가 있을 때)
    tool_result = await fetch_user_profile_and_recommendations(user_id, user_context)
    personalized = tool_result["recommendations"]

    # DB 프로필을 user_context에 병합 (LLM 프롬프트에서 사용)
    if tool_result["from_db"] and tool_result["profile"]:
        profile = tool_result["profile"]
        user_context = {
            **user_context,
            "experience_level": profile.get("experience_level") or user_context.get("experience_level"),
            "learning_goal": profile.get("learning_goal") or user_context.get("learning_goal"),
            "strong_algorithms": profile.get("strong_algorithms") or user_context.get("strong_algorithms", []),
            "preferred_difficulty": profile.get("preferred_difficulty") or user_context.get("preferred_difficulty"),
            "problems_solved": profile.get("problems_solved", 0),
            "level": profile.get("level", 1),
        }
        print(f"[handle_question] Using DB profile: {profile.get('experience_level')}, {profile.get('learning_goal')}")

    # ============================================================
    # 애매한 응답 재확인 처리
    # "음... 그래", "글쎄... 좋아" 등 confidence가 낮은 긍정
    # ============================================================
    if state.get("needs_reconfirmation"):
        suggested = state.get("suggested_value", "")
        display_value = _get_display_value(suggested, current_step)

        reconfirm_message = f"혹시 {display_value}{_get_particle(display_value)} 하시는 게 맞을까요? 한번 더 확인해주세요!"

        return {
            "response_message": reconfirm_message,
            "awaiting_confirmation": True,
            "suggested_value": suggested,
            "needs_reconfirmation": False,
            "chips": [
                {"label": "네, 맞아요", "value": "yes", "category": "confirmation"},
                {"label": "아니요, 다시", "value": "no", "category": "confirmation"},
            ],
        }

    # rejection 타입일 때 특별 처리
    if question_type == "rejection":
        # "want_choose" 이유면 옵션 목록 보여주기 (Tool 기반 칩 UI)
        if rejection_reason == "want_choose":
            return await _handle_show_options(state, current_step, user_context)

        # difficulty 단계에서 too_hard/too_easy면 유동적으로 난이도 조정
        suggested_difficulty_hint = ""
        if current_step == "difficulty" and rejection_reason in ["too_hard", "too_easy"]:
            # 이전에 추천된 난이도 (rejected_values의 마지막 값 또는 suggested_value)
            previous_difficulty = state.get("suggested_value") or (rejected_values[-1] if rejected_values else "medium")
            adjusted_difficulty = _get_adjusted_difficulty(previous_difficulty, rejection_reason, rejected_values)
            adjusted_display = _get_display_value(adjusted_difficulty, "difficulty")
            suggested_difficulty_hint = f"\n\n추천 힌트: {adjusted_display}({adjusted_difficulty})로 추천하세요."

        prompt_template = QUESTION_PROMPTS.get("rejection", QUESTION_PROMPTS["general"])
        prompt = prompt_template.format(
            current_step=current_step,
            topic=state.get("topic") or "미선택",
            difficulty=state.get("difficulty") or "미선택",
            language=state.get("language") or "미선택",
            message=message,
            rejected_values=", ".join(rejected_values) if rejected_values else "없음",
            rejection_reason=rejection_reason or "없음",
        ) + suggested_difficulty_hint
    else:
        # 일반 질문 처리
        prompt_template = QUESTION_PROMPTS.get(question_type, QUESTION_PROMPTS["general"])
        prompt = prompt_template.format(
            current_step=current_step,
            topic=state.get("topic") or "미선택",
            difficulty=state.get("difficulty") or "미선택",
            language=state.get("language") or "미선택",
            message=message,
        )

    try:
        # ============================================================
        # Structured Output으로 LLM 호출
        # JSON 형식으로 message + suggested_value 동시에 받기
        # ============================================================
        existing_topic = state.get("topic")
        existing_difficulty = state.get("difficulty")
        existing_language = state.get("language")

        # 현재 단계에 따른 추천 대상 결정 (개인화된 순서 사용)
        if current_step == "topic":
            # 개인화된 주제 옵션 사용
            valid_values = personalized.get("topic_options", []) + ["DP", "그래프", "정렬", "구현", "기초", "문자열", "이분탐색", "백트래킹", "BFS/DFS", "스택/큐"]
            # 중복 제거
            seen = set()
            valid_values = [v for v in valid_values if not (v in seen or seen.add(v))]
        elif current_step == "difficulty":
            valid_values = ["easy", "medium", "medium_hard", "hard", "very_hard"]
        else:
            valid_values = ["python", "java", "cpp"]

        # 거절된 값 제외
        available_values = [v for v in valid_values if v.lower() not in [r.lower() for r in rejected_values]]

        # 이미 선택된 정보 텍스트
        selected_info_text = ""
        if existing_topic:
            selected_info_text += f"\n- 이미 선택된 주제: {existing_topic}"
        if existing_difficulty:
            selected_info_text += f"\n- 이미 선택된 난이도: {existing_difficulty}"
        if existing_language:
            selected_info_text += f"\n- 이미 선택된 언어: {existing_language}"

        # ============================================================
        # 사용자 프로필 기반 개인화 정보 구성 (Tool에서 가져온 정보 사용)
        # ============================================================
        user_profile_text = ""

        # Tool에서 생성한 user_summary 사용 (DB 프로필 기반)
        user_summary = personalized.get("user_summary", "")
        if user_summary and user_summary != "프로필 미설정":
            user_profile_text += f"\n- 사용자 요약: {user_summary}"

        experience_level = user_context.get("experience_level")
        learning_goal = user_context.get("learning_goal")
        strong_algorithms = user_context.get("strong_algorithms", [])
        problems_solved = user_context.get("problems_solved", 0)

        if experience_level:
            level_names = {
                "beginner": "입문자",
                "elementary": "초급자",
                "intermediate": "중급자",
                "advanced": "고급자",
            }
            user_profile_text += f"\n- 사용자 레벨: {level_names.get(experience_level, experience_level)}"

        if learning_goal:
            goal_names = {
                "big_tech": "대기업 취업",
                "mid_startup": "스타트업 취업",
                "skill_up": "실력 향상",
            }
            user_profile_text += f"\n- 학습 목표: {goal_names.get(learning_goal, learning_goal)}"

        if strong_algorithms:
            user_profile_text += f"\n- 이미 잘하는 알고리즘: {', '.join(strong_algorithms)}"

        if problems_solved > 0:
            user_profile_text += f"\n- 푼 문제 수: {problems_solved}개"

        # 개인화 추천 이유 (Tool에서 생성)
        personalization_hint = ""
        personalization_reason = personalized.get("personalization_reason", "")

        # 개인화된 기본 추천값
        if current_step == "topic":
            default_suggestion = personalized.get("recommended_topic", available_values[0] if available_values else "기초")
            if personalization_reason:
                personalization_hint = f"\n\n개인화 힌트: 이 사용자에게는 {personalization_reason} 주제를 추천하세요."
        elif current_step == "difficulty":
            # difficulty 단계: get_difficulty_recommendations로 구체적인 추천 생성
            from app.tools.user_tools import get_user_tools
            tools = get_user_tools()
            diff_result = tools.get_difficulty_recommendations(
                experience_level=experience_level or "unknown",
                selected_topic=state.get("topic"),
            )
            default_suggestion = diff_result.recommended_difficulty
            recommended_display = diff_result.recommended_display
            # 더 구체적인 개인화 힌트 (한글 티어명 포함)
            level_names = {"beginner": "입문자", "elementary": "초급자", "intermediate": "중급자", "advanced": "고급자"}
            level_name = level_names.get(experience_level, "")
            if level_name:
                personalization_hint = f"\n\n개인화 힌트: {level_name}에게 적합한 난이도는 **{recommended_display}**입니다. '{recommended_display}로 해볼까요?' 형식으로 추천하세요."
            else:
                personalization_hint = f"\n\n개인화 힌트: 추천 난이도는 **{recommended_display}**입니다."
        else:
            default_suggestion = personalized.get("recommended_language", available_values[0] if available_values else "python")
            personalization_hint = ""

        # default_suggestion이 거절된 값이면 다른 값 사용
        if default_suggestion.lower() in [r.lower() for r in rejected_values]:
            default_suggestion = available_values[0] if available_values else valid_values[0]

        system_prompt = f"""당신은 CodeFill 알고리즘 학습 도우미입니다.
사용자 질문에 답변하고, 현재 단계에 맞는 값을 추천하세요.

컨텍스트:
- 알고리즘 문제 풀이 학습 플랫폼
- 실버/골드/플래티넘/다이아/마스터 = 난이도 티어 (금융/게임 아님)
{selected_info_text}
{user_profile_text}

현재 단계: {current_step}
선택 가능한 값: {available_values}
거절된 값 (추천 금지): {rejected_values}
추천 기본값: {default_suggestion}{personalization_hint}

반드시 JSON 형식으로 응답하세요:
{{
  "message": "사용자에게 보낼 친근한 답변 (2-3문장). 마지막에 '~로 해볼까요?' 형식으로 추천",
  "suggested_value": "{default_suggestion}"
}}

중요:
- suggested_value는 반드시 선택 가능한 값 중 하나여야 합니다
- 거절된 값은 절대 추천하지 마세요
- 사용자 프로필이 있으면 그에 맞는 추천을 하세요
- difficulty일 때: easy/medium/medium_hard/hard/very_hard 중 하나 (한글 X)
- language일 때: python/java/cpp 중 하나 (한글 X)"""

        response = await openrouter_service.chat_completion(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=400,
            response_format={"type": "json_object"},
        )

        content = openrouter_service.get_content(response)
        result = json.loads(content)

        answer = result.get("message", "")
        suggested_value = result.get("suggested_value", "")

        # 추천값 검증 및 정규화
        suggested_value = _normalize_suggested_value(suggested_value, current_step)

        # 추천값이 없거나 거절된 값이면 개인화된 옵션에서 선택
        if not suggested_value or suggested_value.lower() in [r.lower() for r in rejected_values]:
            personalized_options = personalized.get("topic_options") if current_step == "topic" else None
            suggested_value = _get_non_rejected_default(current_step, rejected_values, personalized_options)
            step_info = STEP_RECOMMENDATIONS.get(current_step, {})
            display_value = _get_display_value(suggested_value, current_step)
            answer += f"\n\n{display_value}{_get_particle(display_value)} 해볼까요?"

        return {
            "response_message": answer,
            "suggested_value": suggested_value,
            "awaiting_confirmation": True,
            "is_question": False,
        }

    except Exception as e:
        # LLM 호출 실패 시 기본 메시지 (개인화 추천 사용)
        print(f"[handle_question] LLM error: {e}")

        # rejection 타입이고 difficulty 단계면 유동적 조정
        if question_type == "rejection" and current_step == "difficulty" and rejection_reason in ["too_hard", "too_easy"]:
            previous_difficulty = state.get("suggested_value") or (rejected_values[-1] if rejected_values else "medium")
            default_value = _get_adjusted_difficulty(previous_difficulty, rejection_reason, rejected_values)
            display_value = _get_display_value(default_value, current_step)
        elif current_step == "difficulty":
            # difficulty 단계: 개인화된 추천 사용
            from app.tools.user_tools import get_user_tools
            tools = get_user_tools()
            diff_result = tools.get_difficulty_recommendations(
                experience_level=user_context.get("experience_level") or "unknown",
                selected_topic=state.get("topic"),
            )
            default_value = diff_result.recommended_difficulty
            display_value = diff_result.recommended_display
        else:
            # 개인화된 추천값 우선 사용 (하드코딩 fallback 제거)
            if current_step == "topic":
                default_value = personalized.get("recommended_topic") or personalized.get("topic_options", ["DP"])[0]
            else:
                default_value = personalized.get("recommended_language") or "python"

            # 거절된 값이면 개인화된 옵션에서 다른 값 선택
            if default_value.lower() in [r.lower() for r in rejected_values]:
                personalized_options = personalized.get("topic_options") if current_step == "topic" else None
                default_value = _get_non_rejected_default(current_step, rejected_values, personalized_options)

            display_value = _get_display_value(default_value, current_step)

        # rejection 타입이면 공감 메시지 추가
        if question_type == "rejection":
            if rejection_reason == "too_hard":
                prefix = "알겠어요! 더 쉬운 걸로 추천해드릴게요.\n\n"
            elif rejection_reason == "too_easy":
                prefix = "알겠어요! 더 도전적인 걸로 추천해드릴게요.\n\n"
            else:
                prefix = "알겠어요! 회원님 레벨에 맞게 추천해드릴게요.\n\n"
        else:
            prefix = ""

        # 난이도 단계에서 개인화 메시지 사용
        level_names = {"beginner": "입문자", "elementary": "초급자", "intermediate": "중급자", "advanced": "고급자"}
        level_name = level_names.get(user_context.get("experience_level", ""), "")

        if current_step == "difficulty" and level_name:
            difficulty_msg = f"{prefix}{level_name}에게 적합한 난이도를 추천해드려요!\n\n{display_value}{_get_particle(display_value)} 해볼까요?"
        else:
            fallback_messages = {
                "topic": f"{prefix}알고리즘 주제를 선택해볼까요?\n\n{display_value}{_get_particle(display_value)} 해볼까요?",
                "difficulty": f"{prefix}난이도를 선택해볼까요?\n\n{display_value}{_get_particle(display_value)} 할까요?",
                "language": f"{prefix}프로그래밍 언어를 선택해볼까요?\n\n{display_value}{_get_particle(display_value)} 할까요?",
            }
            difficulty_msg = fallback_messages.get(
                current_step, f"{prefix}{display_value}{_get_particle(display_value)} 해볼까요?"
            )

        return {
            "response_message": difficulty_msg,
            "suggested_value": default_value,  # DB 값 저장
            "awaiting_confirmation": True,
            "is_question": False,
        }


def _normalize_suggested_value(value: str, current_step: str) -> str:
    """
    추천값 정규화 (DB 저장 형식으로 변환)

    - topic: 그대로 유지
    - difficulty: easy/medium/medium_hard/hard/very_hard
    - language: python/java/cpp
    """
    if not value:
        return ""

    value_lower = value.lower().strip()

    if current_step == "difficulty":
        # 티어명 → DB값 변환
        DIFF_MAP = {
            "실버": "easy", "silver": "easy", "easy": "easy", "쉬움": "easy",
            "골드": "medium", "gold": "medium", "medium": "medium", "중간": "medium",
            "플래티넘": "medium_hard", "platinum": "medium_hard", "medium_hard": "medium_hard",
            "다이아": "hard", "diamond": "hard", "hard": "hard", "어려움": "hard",
            "마스터": "very_hard", "master": "very_hard", "very_hard": "very_hard",
        }
        return DIFF_MAP.get(value_lower, value)

    elif current_step == "language":
        LANG_MAP = {
            "파이썬": "python", "python": "python", "py": "python",
            "자바": "java", "java": "java",
            "씨플플": "cpp", "c++": "cpp", "cpp": "cpp",
        }
        return LANG_MAP.get(value_lower, value)

    # topic은 그대로
    return value


def _get_display_value(value: str, current_step: str) -> str:
    """
    DB 값을 사용자 표시용 값으로 변환

    - difficulty: easy → 실버
    - language: python → Python
    """
    if current_step == "difficulty":
        return DIFFICULTY_TO_TIER.get(value, value)
    elif current_step == "language":
        LANG_DISPLAY = {"python": "Python", "java": "Java", "cpp": "C++"}
        return LANG_DISPLAY.get(value, value)
    return value


def _get_non_rejected_default(
    current_step: str,
    rejected_values: list = None,
    personalized_options: list = None,
) -> str:
    """
    rejected_values를 피해서 기본값 반환 (DB 저장 형식)
    개인화된 옵션이 있으면 그것을 우선 사용
    """
    rejected_lower = [v.lower() for v in (rejected_values or [])]

    # 개인화된 옵션이 있으면 우선 사용
    if personalized_options:
        for option in personalized_options:
            if option.lower() not in rejected_lower:
                return option

    # 각 단계별 DB 값 리스트 (대기업 빈출 순서로 정렬)
    if current_step == "topic":
        # 대기업 빈출 순서: DP > 그래프 > 구현 > 이분탐색 > 문자열 > 정렬 > 기초
        options = ["DP", "그래프", "구현", "이분탐색", "문자열", "정렬", "기초"]
    elif current_step == "difficulty":
        options = ["easy", "medium", "medium_hard", "hard", "very_hard"]
    else:  # language
        options = ["python", "java", "cpp"]

    for option in options:
        if option.lower() not in rejected_lower:
            return option

    # 모든 옵션이 거절됐으면 첫 번째 옵션 반환
    return options[0]


def _get_adjusted_difficulty(
    previous_difficulty: str,
    rejection_reason: str,
    rejected_values: list = None
) -> str:
    """
    이전 추천 난이도와 거절 이유에 따라 유동적으로 난이도 조정

    - too_hard: 한 단계 아래로
    - too_easy: 한 단계 위로

    Args:
        previous_difficulty: 이전에 추천된 난이도 (DB값: easy/medium/medium_hard/hard/very_hard)
        rejection_reason: 거절 이유 (too_hard, too_easy, etc.)
        rejected_values: 이미 거절된 값들

    Returns:
        조정된 난이도 (DB값)
    """
    rejected_lower = [v.lower() for v in (rejected_values or [])]

    # 이전 난이도의 인덱스 찾기
    try:
        current_idx = DIFFICULTY_ORDER.index(previous_difficulty.lower())
    except ValueError:
        # 찾을 수 없으면 중간값(medium)으로 시작
        current_idx = 1

    if rejection_reason == "too_hard":
        # 한 단계 아래로 (인덱스 감소)
        new_idx = max(0, current_idx - 1)
    elif rejection_reason == "too_easy":
        # 한 단계 위로 (인덱스 증가)
        new_idx = min(len(DIFFICULTY_ORDER) - 1, current_idx + 1)
    else:
        # 기타 이유면 그냥 다른 값 선택
        new_idx = current_idx

    # 새 난이도가 이미 거절됐으면 다른 방향으로 탐색
    new_difficulty = DIFFICULTY_ORDER[new_idx]

    if new_difficulty.lower() in rejected_lower:
        # 거절된 값이면 반대 방향 또는 다른 값 탐색
        if rejection_reason == "too_hard":
            # 더 쉬운 방향으로 계속 탐색
            for idx in range(new_idx - 1, -1, -1):
                if DIFFICULTY_ORDER[idx].lower() not in rejected_lower:
                    return DIFFICULTY_ORDER[idx]
            # 쉬운 방향에 없으면 어려운 방향 탐색
            for idx in range(new_idx + 1, len(DIFFICULTY_ORDER)):
                if DIFFICULTY_ORDER[idx].lower() not in rejected_lower:
                    return DIFFICULTY_ORDER[idx]
        else:
            # 더 어려운 방향으로 계속 탐색
            for idx in range(new_idx + 1, len(DIFFICULTY_ORDER)):
                if DIFFICULTY_ORDER[idx].lower() not in rejected_lower:
                    return DIFFICULTY_ORDER[idx]
            # 어려운 방향에 없으면 쉬운 방향 탐색
            for idx in range(new_idx - 1, -1, -1):
                if DIFFICULTY_ORDER[idx].lower() not in rejected_lower:
                    return DIFFICULTY_ORDER[idx]

    return new_difficulty


async def _handle_show_options(state: CollectionState, current_step: str, user_context: dict = None) -> Dict[str, Any]:
    """
    사용자가 직접 선택하고 싶을 때 옵션 목록 보여주기
    Tool 기반 칩 UI 사용 (DB 태그 분석 + 대기업 빈출 유형)
    """
    from app.tools.user_tools import get_user_tools

    tools = get_user_tools()
    user_context = user_context or {}
    rejected_values = state.get("rejected_values", [])
    rejected_lower = [v.lower() for v in rejected_values]

    if current_step == "topic":
        # Tool로 주제 추천 가져오기 (DB 태그 분석 + 빈출 유형)
        learning_goal = user_context.get("learning_goal", "unknown")
        experience_level = user_context.get("experience_level", "unknown")
        strong_algorithms = user_context.get("strong_algorithms", [])

        topic_result = await tools.get_topic_recommendations(
            learning_goal=learning_goal,
            experience_level=experience_level,
            strong_algorithms=strong_algorithms,
            limit=8,  # 더 많은 옵션 제공
        )

        # 거절된 값 제외
        chips = [
            c.to_dict()
            for c in topic_result.topic_chips
            if c.value.lower() not in rejected_lower
        ][:6]

        message = topic_result.message
        if topic_result.personalization_context:
            message = f"[{topic_result.personalization_context}]\n\n{message}"

    elif current_step == "difficulty":
        # Tool로 난이도 추천 가져오기
        experience_level = user_context.get("experience_level", "unknown")
        selected_topic = state.get("topic")

        difficulty_result = tools.get_difficulty_recommendations(
            experience_level=experience_level,
            selected_topic=selected_topic,
        )

        # 거절된 값 제외
        chips = [
            c.to_dict()
            for c in difficulty_result.difficulty_chips
            if c.value.lower() not in rejected_lower
        ]

        message = difficulty_result.message

    else:
        # language 단계
        step_info = STEP_RECOMMENDATIONS.get(current_step, {})
        options = step_info.get("options", [])
        available_options = [opt for opt in options if opt.lower() not in rejected_lower]
        chips = [
            {"label": opt, "value": opt.lower(), "category": current_step}
            for opt in available_options
        ]
        message = "어떤 언어로 풀어볼까요?"

    return {
        "response_message": message,
        "suggested_value": None,  # 선택 대기
        "awaiting_confirmation": False,  # 목록에서 직접 선택
        "is_question": False,
        "chips": chips,
    }


def _get_particle(word: str) -> str:
    """
    한국어 조사 결정 (으로/로)
    """
    if not word:
        return "으로"

    # 마지막 글자의 받침 여부 확인
    last_char = word[-1]

    # 영어인 경우
    if last_char.isascii():
        # 자음으로 끝나면 "으로", 모음으로 끝나면 "로"
        vowels = 'aeiouAEIOU'
        return "로" if last_char in vowels else "으로"

    # 한글인 경우
    if '가' <= last_char <= '힣':
        # 유니코드로 받침 여부 확인
        code = ord(last_char) - ord('가')
        jong = code % 28  # 종성 (0이면 받침 없음)
        return "으로" if jong > 0 else "로"

    return "으로"
