"""
Complete Node

모든 정보 수집 완료 후 다음 단계로 라우팅
"""
from typing import Dict, Any
from ..state import CollectionState


# DB값 → 티어 표시명
DIFFICULTY_TO_TIER = {
    "easy": "실버",
    "medium": "골드",
    "medium_hard": "플래티넘",
    "hard": "다이아",
    "very_hard": "마스터",
}


def complete_collection(state: CollectionState) -> Dict[str, Any]:
    """
    정보 수집 완료 처리

    모든 정보가 수집되었음을 확인하고
    문제 검색 단계로 라우팅
    """
    topic = state.get("topic")
    difficulty = state.get("difficulty")
    language = state.get("language")

    # 모든 정보가 있는지 확인
    if not all([topic, difficulty, language]):
        # 누락된 정보가 있으면 해당 단계로
        if not topic:
            return {"current_step": "topic"}
        if not difficulty:
            return {"current_step": "difficulty"}
        if not language:
            return {"current_step": "language"}

    # 티어 이름
    tier_name = DIFFICULTY_TO_TIER.get(difficulty, difficulty)

    # 언어 표시명
    language_display = {
        "python": "Python",
        "java": "Java",
        "cpp": "C++",
    }.get(language, language)

    # 완료 메시지
    message = (
        f"좋아요! {topic} 주제의 {tier_name} 문제를 "
        f"{language_display}로 찾아볼게요!"
    )

    return {
        "response_message": message,
        "is_complete": True,
        "current_step": "complete",
        "route_to": "discovery",  # 다음 단계: 문제 검색
    }
