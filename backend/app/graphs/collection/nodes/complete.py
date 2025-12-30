"""
Complete Node

모든 정보 수집 완료 후 다음 단계로 라우팅
"""
from typing import Dict, Any
from ..state import CollectionState


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

    # 난이도 한글 변환
    difficulty_korean = {
        "easy": "쉬운",
        "medium": "중간",
        "hard": "어려운",
    }.get(difficulty, difficulty)

    # 언어 표시명
    language_display = {
        "python": "Python",
        "java": "Java",
        "cpp": "C++",
    }.get(language, language)

    # 완료 메시지
    message = (
        f"좋아요! **{topic}** 주제의 **{difficulty_korean}** 난이도 문제를 "
        f"**{language_display}**으로 찾아볼게요!"
    )

    return {
        "response_message": message,
        "is_complete": True,
        "current_step": "complete",
        "route_to": "discovery",  # 다음 단계: 문제 검색
    }
