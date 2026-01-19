"""
Ask Topic Node

주제를 물어보는 노드
사용자의 레벨에 따라 다른 추천 제공 (동적 태그 기반)
"""
import json
import os
import random
from typing import Dict, Any, List
from ..state import CollectionState


# ============================================================
# 동적 태그 로드
# ============================================================

_ASK_TOPIC_TAG_CACHE = None

def _load_available_tags() -> List[str]:
    """JSON 파일에서 사용 가능한 태그 목록 로드"""
    global _ASK_TOPIC_TAG_CACHE

    if _ASK_TOPIC_TAG_CACHE is not None:
        return _ASK_TOPIC_TAG_CACHE

    # JSON 파일 경로 (nodes/ → collection/ → graphs/ → app/)
    json_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
        "data", "tag_normalization.json"
    )

    default_tags = ["구현", "수학", "자료구조", "그리디", "DP", "정렬", "문자열",
                    "완전탐색", "그래프", "BFS/DFS", "트리", "이분탐색"]

    try:
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                _ASK_TOPIC_TAG_CACHE = data.get("available_tags", default_tags)
                return _ASK_TOPIC_TAG_CACHE
    except Exception:
        pass

    _ASK_TOPIC_TAG_CACHE = default_tags
    return default_tags


def _get_dynamic_topic_message(user_level: str) -> str:
    """레벨에 맞는 동적 메시지 생성"""
    tags = _load_available_tags().copy()
    random.shuffle(tags)

    # 레벨별 추천 태그 수
    if user_level in ["beginner", "elementary"]:
        sample_tags = tags[:4]
        intro = "코딩 학습을 시작하셨군요!"
    elif user_level == "intermediate":
        sample_tags = tags[:5]
        intro = "어떤 알고리즘을 연습하고 싶으세요?"
    else:  # advanced
        sample_tags = tags[:6]
        intro = "어떤 알고리즘을 연습하시겠어요?"

    tag_list = ", ".join([f"**{t}**" for t in sample_tags])
    more_tags = ", ".join(tags[len(sample_tags):len(sample_tags)+3])

    return (
        f"{intro}\n\n"
        f"**추천 주제:** {tag_list}\n\n"
        f"**기타:** {more_tags} 등\n\n"
        f"어떤 주제로 해볼까요?"
    )


def ask_topic(state: CollectionState) -> Dict[str, Any]:
    """
    주제를 물어보는 응답 생성

    사용자 레벨에 따라 적절한 추천 제공 (동적 태그 기반)
    """
    # 이미 주제가 있으면 다음 단계로
    if state.get("topic"):
        return {
            "current_step": "difficulty",
        }

    # 사용자 레벨 확인
    user_context = state.get("user_context", {})
    user_level = user_context.get("level", "beginner")

    # 동적 메시지 생성
    message = _get_dynamic_topic_message(user_level)

    return {
        "response_message": message,
        "current_step": "topic",
    }
