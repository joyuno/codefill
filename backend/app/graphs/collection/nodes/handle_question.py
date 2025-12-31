"""
Handle Question Node (Structured Output)

사용자가 질문을 할 때 LLM으로 답변 생성
Structured output으로 안정적인 추천값 추출
"""
import json
from typing import Dict, Any
from ..state import CollectionState, DIFFICULTY_TO_TIER


# 현재 단계별 추천 옵션
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

# 티어명 → DB값 매핑
TIER_TO_DB = {
    "실버": "easy", "골드": "medium", "플래티넘": "medium_hard",
    "다이아": "hard", "마스터": "very_hard",
}


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
사용자가 이전 추천을 거절했습니다. 새로운 추천을 해주세요.

현재 수집 단계: {current_step}
수집된 정보:
- 주제: {topic}
- 난이도: {difficulty}
- 언어: {language}

사용자의 거절 메시지: "{message}"
이전에 거절된 값들: {rejected_values}
거절 이유 힌트: {rejection_reason}

중요 지침:
1. 거절된 값들({rejected_values})은 절대 다시 추천하지 마세요!
2. 거절 이유에 맞게 추천하세요:
   - "too_hard" → 더 낮은 티어 추천 (예: 실버)
   - "too_easy" → 더 높은 티어 추천 (예: 다이아, 마스터)
   - "already_done" → 완전히 다른 주제 추천
   - "unknown/beginner" → 기초적인 주제 추천
   - "not_interested" → 다른 계열의 주제 추천
   - "want_choose" → 선택지 목록 보여주기
3. 공감하는 말로 시작하세요 (예: "알겠어요!", "그럼 다른 걸로!", "좋아요!")
4. 새로운 추천을 자연스럽게 제시하고 "~로 해볼까요?" 형식으로 마무리

예시 응답:
- "알겠어요! 그럼 그래프는 어떠세요? 탐색 알고리즘의 기초를 배울 수 있어요!"
- "좋아요! 더 도전적인 걸 원하시는군요. 다이아로 해볼까요?"
- "그럼 실버부터 차근차근 시작해볼까요? 입문자에게 딱이에요!"

현재 단계에 맞는 선택지:
- topic: 기초, DP, 그래프, 정렬, 구현, 문자열, 이분탐색, 백트래킹
- difficulty: 실버, 골드, 플래티넘, 다이아, 마스터
- language: Python, Java, C++
""",
}

# 거절 이유별 추천 가이드
REJECTION_SUGGESTIONS = {
    "too_hard": {
        "topic": ["기초", "구현", "정렬"],
        "difficulty": ["실버"],
        "message_prefix": "더 쉬운 난이도로 추천해드릴게요! ",
    },
    "too_easy": {
        "topic": ["DP", "그래프", "백트래킹"],
        "difficulty": ["다이아", "마스터"],
        "message_prefix": "도전적인 난이도를 원하시는군요! ",
    },
    "already_done": {
        "message_prefix": "이미 해보셨군요! 다른 주제로 ",
    },
    "unknown": {
        "topic": ["기초"],
        "difficulty": ["실버"],
        "message_prefix": "처음이시군요! 실버부터 ",
    },
    "beginner": {
        "topic": ["기초"],
        "difficulty": ["실버"],
        "message_prefix": "입문자시군요! ",
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
        # "want_choose" 이유면 옵션 목록 보여주기
        if rejection_reason == "want_choose":
            return _handle_show_options(state, current_step)

        prompt_template = QUESTION_PROMPTS.get("rejection", QUESTION_PROMPTS["general"])
        prompt = prompt_template.format(
            current_step=current_step,
            topic=state.get("topic") or "미선택",
            difficulty=state.get("difficulty") or "미선택",
            language=state.get("language") or "미선택",
            message=message,
            rejected_values=", ".join(rejected_values) if rejected_values else "없음",
            rejection_reason=rejection_reason or "없음",
        )
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

        # 현재 단계에 따른 추천 대상 결정
        if current_step == "topic":
            valid_values = ["DP", "그래프", "정렬", "구현", "기초", "문자열", "이분탐색", "백트래킹", "BFS/DFS", "스택/큐"]
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

        system_prompt = f"""당신은 CodeFill 알고리즘 학습 도우미입니다.
사용자 질문에 답변하고, 현재 단계에 맞는 값을 추천하세요.

컨텍스트:
- 알고리즘 문제 풀이 학습 플랫폼
- 실버/골드/플래티넘/다이아/마스터 = 난이도 티어 (금융/게임 아님)
{selected_info_text}

현재 단계: {current_step}
선택 가능한 값: {available_values}
거절된 값 (추천 금지): {rejected_values}

반드시 JSON 형식으로 응답하세요:
{{
  "message": "사용자에게 보낼 친근한 답변 (2-3문장). 마지막에 '~로 해볼까요?' 형식으로 추천",
  "suggested_value": "{available_values[0] if available_values else valid_values[0]}"
}}

중요:
- suggested_value는 반드시 선택 가능한 값 중 하나여야 합니다
- 거절된 값은 절대 추천하지 마세요
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

        # 추천값이 없거나 거절된 값이면 다른 값 사용
        if not suggested_value or suggested_value.lower() in [r.lower() for r in rejected_values]:
            suggested_value = _get_non_rejected_default(current_step, rejected_values)
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
        # LLM 호출 실패 시 기본 메시지
        print(f"[handle_question] LLM error: {e}")

        # rejected_values를 피해서 기본값 선택
        default_value = _get_non_rejected_default(current_step, rejected_values)
        display_value = _get_display_value(default_value, current_step)

        # rejection 타입이면 공감 메시지 추가
        if question_type == "rejection":
            prefix = "알겠어요! 다른 걸로 추천해드릴게요.\n\n"
        else:
            prefix = ""

        fallback_messages = {
            "topic": f"{prefix}알고리즘 주제를 선택해볼까요?\n\n{display_value}{_get_particle(display_value)} 해볼까요?",
            "difficulty": f"{prefix}난이도를 선택해볼까요?\n\n{display_value}{_get_particle(display_value)} 할까요?",
            "language": f"{prefix}프로그래밍 언어를 선택해볼까요?\n\n{display_value}{_get_particle(display_value)} 할까요?",
        }

        return {
            "response_message": fallback_messages.get(
                current_step, f"{prefix}{display_value}{_get_particle(display_value)} 해볼까요?"
            ),
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


def _get_non_rejected_default(current_step: str, rejected_values: list = None) -> str:
    """
    rejected_values를 피해서 기본값 반환 (DB 저장 형식)
    """
    rejected_lower = [v.lower() for v in (rejected_values or [])]

    # 각 단계별 DB 값 리스트
    if current_step == "topic":
        options = ["DP", "그래프", "정렬", "구현", "기초", "문자열"]
    elif current_step == "difficulty":
        options = ["easy", "medium", "medium_hard", "hard", "very_hard"]
    else:  # language
        options = ["python", "java", "cpp"]

    for option in options:
        if option.lower() not in rejected_lower:
            return option

    # 모든 옵션이 거절됐으면 첫 번째 옵션 반환
    return options[0]


def _handle_show_options(state: CollectionState, current_step: str) -> Dict[str, Any]:
    """
    사용자가 직접 선택하고 싶을 때 옵션 목록 보여주기
    """
    step_info = STEP_RECOMMENDATIONS.get(current_step, {})
    options = step_info.get("options", [])
    display_name = step_info.get("display_name", "값")
    rejected_values = state.get("rejected_values", [])

    # 거절된 값 제외한 옵션 목록
    available_options = [opt for opt in options if opt not in rejected_values]

    if current_step == "topic":
        # 주제는 더 많은 옵션 제공
        all_topics = ["기초", "DP", "그래프", "정렬", "구현", "문자열", "이분탐색", "백트래킹", "스택/큐", "트리"]
        available_options = [t for t in all_topics if t not in rejected_values]
        options_text = "\n".join([f"• {opt}" for opt in available_options])
        chips = [
            {"label": opt, "value": opt, "category": current_step}
            for opt in available_options[:6]
        ]
    elif current_step == "difficulty":
        # 난이도 옵션 (프론트엔드에서 아이콘 렌더링)
        tier_options = [
            ("실버", "easy"),
            ("골드", "medium"),
            ("플래티넘", "medium_hard"),
            ("다이아", "hard"),
            ("마스터", "very_hard"),
        ]
        available_options = [t for t in tier_options if t[0] not in rejected_values]
        options_text = "\n".join([f"• {opt[0]}" for opt in available_options])
        chips = [
            {"label": opt[0], "value": opt[1], "category": "difficulty"}
            for opt in available_options
        ]
    else:
        options_text = "\n".join([f"• {opt}" for opt in available_options])
        chips = [
            {"label": opt, "value": opt, "category": current_step}
            for opt in available_options[:6]
        ]

    message = f"직접 선택하고 싶으시군요! 아래 {display_name} 중에서 골라주세요:\n\n{options_text}\n\n어떤 걸로 할까요?"

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
