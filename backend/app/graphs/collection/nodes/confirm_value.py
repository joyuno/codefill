"""
Confirm Value Node (Unified)

choose_topic, choose_difficulty, choose_language를 하나로 통합
사용자가 직접 값을 선택했을 때 확정하고 다음 단계로 이동
"""
import re
from typing import Dict, Any, List, Optional
from ..state import CollectionState, DIFFICULTY_TO_TIER


# ============================================================
# Tier Question Detection & Answering
# ============================================================

# DB값 → 티어명 + 설명
TIER_INFO = {
    "easy": ("실버", "기본 개념 연습"),
    "medium": ("골드", "응용 문제"),
    "medium_hard": ("플래티넘", "심화 응용"),
    "hard": ("다이아", "도전적인 문제"),
    "very_hard": ("마스터", "최상위 난이도"),
}


def _detect_tier_question(message: str) -> Optional[str]:
    """
    메시지에서 티어 관련 질문 감지

    Returns:
        티어 설명 문자열 or None
    """
    message_lower = message.lower()

    # 티어 질문 패턴 감지
    tier_question_patterns = [
        r"티어로\s*따지면",
        r"티어가\s*뭐",
        r"어떤\s*티어",
        r"무슨\s*티어",
        r"난이도가\s*뭐",
    ]

    has_tier_question = any(re.search(p, message_lower) for p in tier_question_patterns)

    if not has_tier_question:
        return None

    # 어떤 난이도에 대해 물어보는지 감지
    difficulty_mentions = {
        "easy": ["easy", "이지"],
        "medium": ["medium", "미디엄", "중간"],
        "medium_hard": ["medium_hard", "플래티넘"],
        "hard": ["hard", "하드"],
        "very_hard": ["very_hard", "베리하드"],
    }

    for db_val, keywords in difficulty_mentions.items():
        for keyword in keywords:
            if keyword in message_lower:
                tier_name, tier_desc = TIER_INFO.get(db_val, (db_val, ""))
                return f"참고로 {keyword}은 **{tier_name}** 티어예요! ({tier_desc})"

    # 특정 값 언급 없으면 전체 티어 설명
    return ("참고로 난이도 티어는 이렇게 돼요:\n"
            "• easy = 실버 (기본 개념)\n"
            "• medium = 골드 (응용)\n"
            "• medium_hard = 플래티넘 (심화)\n"
            "• hard = 다이아 (도전적)\n"
            "• very_hard = 마스터 (최상위)")


# ============================================================
# Shared Chip Definitions
# ============================================================

TOPIC_CHIPS: List[Dict[str, str]] = [
    {"label": "기초", "value": "기초", "category": "topic"},
    {"label": "정렬", "value": "정렬", "category": "topic"},
    {"label": "DP", "value": "DP", "category": "topic"},
    {"label": "그래프", "value": "그래프", "category": "topic"},
    {"label": "구현", "value": "구현", "category": "topic"},
    {"label": "탐색", "value": "탐색", "category": "topic"},
]

DIFFICULTY_CHIPS: List[Dict[str, str]] = [
    {"label": "실버", "value": "easy", "category": "difficulty"},
    {"label": "골드", "value": "medium", "category": "difficulty"},
    {"label": "플래티넘", "value": "medium_hard", "category": "difficulty"},
    {"label": "다이아", "value": "hard", "category": "difficulty"},
    {"label": "마스터", "value": "very_hard", "category": "difficulty"},
]

LANGUAGE_CHIPS: List[Dict[str, str]] = [
    {"label": "Python", "value": "python", "category": "language"},
    {"label": "Java", "value": "java", "category": "language"},
    {"label": "C++", "value": "cpp", "category": "language"},
]

# Display mappings
LANGUAGE_DISPLAY = {
    "python": "Python",
    "java": "Java",
    "cpp": "C++",
}


# ============================================================
# Unified Confirm Value Node
# ============================================================

def confirm_value(state: CollectionState) -> Dict[str, Any]:
    """
    통합 값 확정 노드

    현재 단계(current_step)에 따라:
    - 값이 있으면 확정하고 다음 단계로 이동
    - 값이 없으면 해당 단계 질문 표시

    Returns:
        current_step, response_message, chips, (is_complete if done)
    """
    topic = state.get("topic")
    difficulty = state.get("difficulty")
    language = state.get("language")
    current_step = state.get("current_step", "topic")
    message = state.get("message", "")

    # 티어 관련 질문 감지
    tier_answer = _detect_tier_question(message) if message else None

    # ============================================================
    # Topic Stage
    # ============================================================
    if current_step == "topic":
        if not topic:
            return {
                "current_step": "topic",
                "response_message": (
                    "어떤 알고리즘 주제로 연습할까요?\n\n"
                    "기초, DP, 그래프, 정렬, 구현, 문자열 등 원하는 주제를 말씀해주세요!"
                ),
                "chips": TOPIC_CHIPS,
            }

        # Topic confirmed → move to difficulty
        return {
            "current_step": "difficulty",
            "response_message": (
                f"{topic} 주제로 할게요.\n\n"
                f"난이도를 선택해주세요!\n"
                f"실버 - 기본 개념 연습\n"
                f"골드 - 응용 문제\n"
                f"플래티넘 - 심화 응용\n"
                f"다이아 - 도전적인 문제\n"
                f"마스터 - 최상위 난이도"
            ),
            "chips": DIFFICULTY_CHIPS,
        }

    # ============================================================
    # Difficulty Stage
    # ============================================================
    if current_step == "difficulty":
        if not topic:
            return {
                "current_step": "topic",
                "response_message": "먼저 주제를 선택해주세요!",
                "chips": TOPIC_CHIPS,
            }

        if not difficulty:
            return {
                "current_step": "difficulty",
                "response_message": (
                    f"{topic} 주제로 할게요.\n\n"
                    f"난이도를 선택해주세요!\n"
                    f"실버 - 기본 개념 연습\n"
                    f"골드 - 응용 문제\n"
                    f"플래티넘 - 심화 응용\n"
                    f"다이아 - 도전적인 문제\n"
                    f"마스터 - 최상위 난이도"
                ),
                "chips": DIFFICULTY_CHIPS,
            }

        # Difficulty confirmed → move to language
        tier_name = DIFFICULTY_TO_TIER.get(difficulty, difficulty)

        # 기본 응답
        response = f"좋아요! {topic} 주제의 {tier_name} 문제로 할게요.\n\n"

        # 티어 관련 질문이 있었으면 답변 추가
        if tier_answer:
            response += f"{tier_answer}\n\n"

        response += "어떤 프로그래밍 언어로 풀어볼까요?"

        return {
            "current_step": "language",
            "response_message": response,
            "chips": LANGUAGE_CHIPS,
        }

    # ============================================================
    # Language Stage
    # ============================================================
    if current_step == "language":
        if not topic:
            return {
                "current_step": "topic",
                "response_message": "먼저 주제를 선택해주세요!",
                "chips": TOPIC_CHIPS,
            }

        if not difficulty:
            return {
                "current_step": "difficulty",
                "response_message": f"{topic} 주제로 할게요. 난이도를 선택해주세요!",
                "chips": DIFFICULTY_CHIPS,
            }

        if not language:
            tier_name = DIFFICULTY_TO_TIER.get(difficulty, difficulty)

            # 기본 응답
            response = f"{topic} 주제의 {tier_name} 문제로 할게요.\n\n"

            # 티어 관련 질문이 있었으면 답변 추가
            if tier_answer:
                response += f"{tier_answer}\n\n"

            response += "어떤 언어로 풀어볼까요?"

            return {
                "current_step": "language",
                "response_message": response,
                "chips": LANGUAGE_CHIPS,
            }

        # Language confirmed → complete!
        tier_name = DIFFICULTY_TO_TIER.get(difficulty, difficulty)
        language_display = LANGUAGE_DISPLAY.get(language.lower(), language)

        return {
            "current_step": "complete",
            "is_complete": True,
            "response_message": (
                f"좋아요! {topic} 주제의 {tier_name} 문제를 {language_display}로 풀어볼게요!\n\n"
                f"문제를 찾고 있어요..."
            ),
        }

    # ============================================================
    # Complete Stage (shouldn't reach here normally)
    # ============================================================
    return {
        "current_step": "complete",
        "is_complete": True,
        "response_message": "모든 정보가 수집되었어요! 문제를 찾고 있어요...",
    }


# ============================================================
# Legacy Compatibility Wrappers
# ============================================================

def choose_topic(state: CollectionState) -> Dict[str, Any]:
    """Legacy wrapper for confirm_value (topic stage)"""
    return confirm_value(state)


def choose_difficulty(state: CollectionState) -> Dict[str, Any]:
    """Legacy wrapper for confirm_value (difficulty stage)"""
    return confirm_value(state)


def choose_language(state: CollectionState) -> Dict[str, Any]:
    """Legacy wrapper for confirm_value (language stage)"""
    return confirm_value(state)
