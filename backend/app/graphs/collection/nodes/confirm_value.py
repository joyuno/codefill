"""
Confirm Value Node (Unified)

choose_topic, choose_difficulty, choose_language를 하나로 통합
사용자가 직접 값을 선택했을 때 확정하고 다음 단계로 이동
"""
from typing import Dict, Any, List, Optional
from ..state import CollectionState, DIFFICULTY_TO_TIER


# ============================================================
# Tier Question Detection & Answering (LLM 기반)
# ============================================================

# DB값 → 티어명 + 설명
TIER_INFO = {
    "easy": ("실버", "기본 개념 연습"),
    "medium": ("골드", "응용 문제"),
    "medium_hard": ("플래티넘", "심화 응용"),
    "hard": ("다이아", "도전적인 문제"),
    "very_hard": ("마스터", "최상위 난이도"),
}


async def _detect_tier_question_async(message: str, analysis_result=None) -> Optional[str]:
    """
    메시지에서 티어 관련 질문 감지 (LLM 기반)

    Args:
        message: 사용자 메시지
        analysis_result: 이미 분석된 UnifiedAnalysisResult (있으면 재사용)

    Returns:
        티어 설명 문자열 or None
    """
    from app.tools.collection_tools import collection_tool

    # 이미 분석된 결과가 있으면 재사용
    if analysis_result is None:
        analysis_result = await collection_tool.analyze(message)

    # 질문이 아니면 None
    if analysis_result.intent != "question":
        return None

    # question_info에서 티어/난이도 관련 질문인지 확인
    question_info = analysis_result.question_info
    if not question_info:
        return None

    # 난이도 관련 질문인지 확인
    is_tier_question = (
        question_info.question_target == "difficulty" or
        question_info.question_type == "difficulty_inquiry" or
        any(subj in ["실버", "골드", "플래티넘", "다이아", "마스터", "티어", "난이도",
                     "easy", "medium", "hard", "very_hard"]
            for subj in (question_info.question_subjects or []))
    )

    if not is_tier_question:
        return None

    # 특정 난이도 언급 확인
    subjects = [s.lower() for s in (question_info.question_subjects or [])]

    difficulty_map = {
        "실버": "easy", "silver": "easy", "easy": "easy", "쉬움": "easy",
        "골드": "medium", "gold": "medium", "medium": "medium", "보통": "medium",
        "플래티넘": "medium_hard", "platinum": "medium_hard",
        "다이아": "hard", "diamond": "hard", "hard": "hard", "어려움": "hard",
        "마스터": "very_hard", "master": "very_hard",
    }

    for subj in subjects:
        if subj in difficulty_map:
            db_val = difficulty_map[subj]
            tier_name, tier_desc = TIER_INFO.get(db_val, (db_val, ""))
            return f"참고로 {subj}은 **{tier_name}** 티어예요! ({tier_desc})"

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
    {"label": "구현", "value": "구현", "category": "topic"},
    {"label": "정렬", "value": "정렬", "category": "topic"},
    {"label": "문자열", "value": "문자열", "category": "topic"},
    {"label": "이분탐색", "value": "이분탐색", "category": "topic"},
    {"label": "그리디", "value": "그리디", "category": "topic"},
    {"label": "기초", "value": "기초", "category": "topic"},
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

async def confirm_value(state: CollectionState) -> Dict[str, Any]:
    """
    통합 값 확정 노드 (async - LLM 기반 질문 감지)

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

    # 자동 추천 여부 확인
    auto_recommended = state.get("auto_recommended", False)
    auto_recommended_value = state.get("auto_recommended_value")

    # 티어 관련 질문 감지 (LLM 기반)
    tier_answer = await _detect_tier_question_async(message) if message else None

    # ============================================================
    # Topic Stage
    # ============================================================
    if current_step == "topic":
        if not topic:
            return {
                "current_step": "topic",
                "response_message": (
                    "어떤 알고리즘 주제로 연습할까요?\n\n"
                    "구현, 정렬, 문자열, 이분탐색, 그리디 등 원하는 주제를 말씀해주세요!"
                ),
                "chips": TOPIC_CHIPS,
            }

        # Topic confirmed → move to difficulty
        # 자동 추천이면 메시지 조정
        if auto_recommended and auto_recommended_value == topic:
            topic_msg = f"제가 추천드리는 **{topic}** 주제로 할게요!"
        else:
            topic_msg = f"{topic} 주제로 할게요."

        return {
            "current_step": "difficulty",
            "response_message": (
                f"{topic_msg}\n\n"
                f"난이도를 선택해주세요!\n"
                f"실버 - 기본 개념 연습\n"
                f"골드 - 응용 문제\n"
                f"플래티넘 - 심화 응용\n"
                f"다이아 - 도전적인 문제\n"
                f"마스터 - 최상위 난이도"
            ),
            "chips": DIFFICULTY_CHIPS,
            "auto_recommended": False,  # 플래그 리셋
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

        # 자동 추천이면 메시지 조정
        if auto_recommended and auto_recommended_value == difficulty:
            difficulty_msg = f"제가 추천드리는 **{tier_name}** 난이도로 할게요!"
        else:
            difficulty_msg = f"좋아요! {topic} 주제의 {tier_name} 문제로 할게요."

        # 기본 응답
        response = f"{difficulty_msg}\n\n"

        # 티어 관련 질문이 있었으면 답변 추가
        if tier_answer:
            response += f"{tier_answer}\n\n"

        response += "어떤 프로그래밍 언어로 풀어볼까요?"

        return {
            "current_step": "language",
            "response_message": response,
            "chips": LANGUAGE_CHIPS,
            "auto_recommended": False,  # 플래그 리셋
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

        # 자동 추천이면 메시지 조정
        if auto_recommended and auto_recommended_value == language:
            complete_msg = (
                f"제가 추천드리는 **{language_display}**로 할게요!\n\n"
                f"{topic} 주제의 {tier_name} 문제를 {language_display}로 풀어볼게요!\n\n"
                f"문제를 찾고 있어요..."
            )
        else:
            complete_msg = (
                f"좋아요! {topic} 주제의 {tier_name} 문제를 {language_display}로 풀어볼게요!\n\n"
                f"문제를 찾고 있어요..."
            )

        return {
            "current_step": "complete",
            "is_complete": True,
            "response_message": complete_msg,
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
# Legacy Compatibility Wrappers (async)
# ============================================================

async def choose_topic(state: CollectionState) -> Dict[str, Any]:
    """Legacy wrapper for confirm_value (topic stage)"""
    return await confirm_value(state)


async def choose_difficulty(state: CollectionState) -> Dict[str, Any]:
    """Legacy wrapper for confirm_value (difficulty stage)"""
    return await confirm_value(state)


async def choose_language(state: CollectionState) -> Dict[str, Any]:
    """Legacy wrapper for confirm_value (language stage)"""
    return await confirm_value(state)
