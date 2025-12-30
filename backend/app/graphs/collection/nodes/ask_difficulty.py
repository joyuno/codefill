"""
Ask Difficulty Node

난이도를 물어보는 노드
선택된 주제에 따라 적절한 난이도 추천
"""
from typing import Dict, Any
from ..state import CollectionState


# 주제별 난이도 추천
TOPIC_DIFFICULTY_HINTS = {
    "기초": "기초 문제는 **쉬움**부터 시작하는 걸 추천해요!",
    "DP": "DP는 처음이라면 **쉬움**으로, 익숙하다면 **중간**으로!",
    "그래프": "그래프 탐색은 **중간** 난이도가 연습하기 좋아요.",
    "정렬": "정렬은 개념 정리에 **쉬움**, 응용은 **중간**!",
    "구현": "구현 문제는 난이도에 따라 복잡도가 달라요.",
}

DEFAULT_HINT = "자신의 실력에 맞는 난이도를 선택해주세요!"


def ask_difficulty(state: CollectionState) -> Dict[str, Any]:
    """
    난이도를 물어보는 응답 생성

    선택된 주제에 따라 적절한 힌트 제공
    """
    # 이미 난이도가 있으면 다음 단계로
    if state.get("difficulty"):
        return {
            "current_step": "language",
        }

    # 주제가 없으면 topic 단계로
    topic = state.get("topic")
    if not topic:
        return {
            "current_step": "topic",
        }

    # 주제에 맞는 힌트 선택
    topic_hint = TOPIC_DIFFICULTY_HINTS.get(topic, DEFAULT_HINT)

    message = (
        f"좋아요! **{topic}** 주제로 할게요.\n\n"
        f"난이도는 어떻게 할까요?\n"
        f"- **쉬움** (easy): 기본 개념 연습\n"
        f"- **중간** (medium): 응용 문제\n"
        f"- **어려움** (hard): 도전적인 문제\n\n"
        f"💡 {topic_hint}"
    )

    return {
        "response_message": message,
        "current_step": "difficulty",
    }
