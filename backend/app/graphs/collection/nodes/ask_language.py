"""
Ask Language Node

프로그래밍 언어를 물어보는 노드
"""
from typing import Dict, Any
from ..state import CollectionState


def ask_language(state: CollectionState) -> Dict[str, Any]:
    """
    프로그래밍 언어를 물어보는 응답 생성
    """
    # 이미 언어가 있으면 complete 단계로
    if state.get("language"):
        return {
            "current_step": "complete",
            "is_complete": True,
        }

    # 난이도가 없으면 difficulty 단계로
    difficulty = state.get("difficulty")
    if not difficulty:
        return {
            "current_step": "difficulty",
        }

    # 주제가 없으면 topic 단계로
    topic = state.get("topic")
    if not topic:
        return {
            "current_step": "topic",
        }

    # 난이도 한글 변환
    difficulty_korean = {
        "easy": "쉬운",
        "medium": "중간",
        "hard": "어려운",
    }.get(difficulty, difficulty)

    message = (
        f"**{topic}** 주제의 **{difficulty_korean}** 문제로 할게요!\n\n"
        f"어떤 프로그래밍 언어로 풀어볼까요?\n"
        f"- **Python** (파이썬)\n"
        f"- **Java** (자바)\n"
        f"- **C++** (씨플플)"
    )

    return {
        "response_message": message,
        "current_step": "language",
    }
