"""
Ask Topic Node

주제를 물어보는 노드
사용자의 레벨에 따라 다른 추천 제공
"""
from typing import Dict, Any
from ..state import CollectionState


# 레벨별 추천 주제
TOPIC_RECOMMENDATIONS = {
    "beginner": {
        "recommended": ["기초", "구현"],
        "message": "코딩 학습을 시작하셨군요! 어떤 알고리즘을 연습하고 싶으세요?\n\n"
                   "**추천 주제:**\n"
                   "- **기초**: 입출력, 조건문, 반복문 등 기본기\n"
                   "- **구현**: 문제를 코드로 옮기는 연습\n\n"
                   "**더 도전적인 주제:**\n"
                   "- 정렬, 탐색, DP, 그래프 등\n\n"
                   "어떤 주제로 해볼까요?",
    },
    "intermediate": {
        "recommended": ["DP", "그래프", "정렬"],
        "message": "어떤 알고리즘을 연습하고 싶으세요?\n\n"
                   "**인기 주제:**\n"
                   "- **DP (동적 프로그래밍)**: 코딩테스트 단골!\n"
                   "- **그래프**: BFS/DFS 탐색\n"
                   "- **정렬**: 다양한 정렬 알고리즘\n\n"
                   "**기타:**\n"
                   "- 탐색, 그리디, 문자열, 구현 등\n\n"
                   "어떤 걸로 할까요?",
    },
    "advanced": {
        "recommended": ["DP", "그래프", "이분탐색"],
        "message": "어떤 알고리즘을 연습하시겠어요?\n\n"
                   "주제: 기초, 정렬, 탐색, DP, 그리디, 구현, 문자열, 그래프, BFS/DFS, 이분탐색 등\n\n"
                   "원하는 주제를 말씀해주세요!",
    },
}


def ask_topic(state: CollectionState) -> Dict[str, Any]:
    """
    주제를 물어보는 응답 생성

    사용자 레벨에 따라 적절한 추천 제공
    """
    # 이미 주제가 있으면 다음 단계로
    if state.get("topic"):
        return {
            "current_step": "difficulty",
        }

    # 사용자 레벨 확인
    user_context = state.get("user_context", {})
    user_level = user_context.get("level", "beginner")

    # 레벨에 맞는 메시지 선택
    if user_level in TOPIC_RECOMMENDATIONS:
        recommendation = TOPIC_RECOMMENDATIONS[user_level]
    else:
        recommendation = TOPIC_RECOMMENDATIONS["beginner"]

    return {
        "response_message": recommendation["message"],
        "current_step": "topic",
    }
