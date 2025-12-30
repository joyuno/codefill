"""
Info Collection State Definition

LangGraph 상태 정의 - 노드 간에 전달되는 데이터 구조
"""
from typing import TypedDict, Optional, List, Dict, Any, Literal


# 수집 단계 정의
CollectionStep = Literal["topic", "difficulty", "language", "complete"]


class CollectionState(TypedDict, total=False):
    """
    정보 수집 그래프의 상태

    이 상태는 모든 노드를 통해 전달되며,
    각 노드는 필요한 부분만 업데이트합니다.
    """

    # ============================================================
    # 입력 (매 턴마다 새로 설정)
    # ============================================================
    message: str                          # 현재 사용자 메시지
    conversation_history: List[Dict[str, str]]  # 대화 히스토리
    user_context: Optional[Dict[str, Any]]      # 사용자 컨텍스트 (레벨 등)

    # ============================================================
    # 수집된 정보 (턴 간 유지)
    # ============================================================
    topic: Optional[str]                  # 선택된 주제 (기초, DP, 그래프 등)
    difficulty: Optional[str]             # 선택된 난이도 (easy, medium, hard)
    language: Optional[str]               # 선택된 언어 (python, java, cpp)

    # ============================================================
    # 현재 턴 분석 결과
    # ============================================================
    current_step: CollectionStep          # 현재 수집 단계
    is_question: bool                     # 사용자가 질문을 했는지
    extracted_value: Optional[str]        # 메시지에서 추출한 값
    question_type: Optional[str]          # 질문 유형 (recommendation, explanation, comparison)

    # ============================================================
    # 출력
    # ============================================================
    response_message: str                 # 사용자에게 보낼 메시지
    is_complete: bool                     # 모든 정보 수집 완료 여부
    route_to: Optional[str]               # 다음 그래프 (discovery, solving, respond)

    # ============================================================
    # 에러 처리
    # ============================================================
    error: Optional[str]                  # 에러 메시지


# ============================================================
# 유효한 값 정의
# ============================================================

VALID_TOPICS = {
    # 한글
    "기초", "정렬", "탐색", "dp", "그리디", "구현",
    "문자열", "그래프", "브루트포스", "이분탐색",
    "bfs", "dfs", "다이나믹", "동적",
    # 영어
    "basic", "sort", "search", "greedy", "implementation",
    "string", "graph", "bruteforce",
}

VALID_DIFFICULTIES = {
    # 한글
    "쉬움", "쉬운", "쉽", "중간", "보통", "어려움", "어려운", "어렵",
    # 영어
    "easy", "medium", "hard",
}

VALID_LANGUAGES = {
    # 한글
    "파이썬", "자바", "씨플플",
    # 영어
    "python", "java", "cpp", "c++",
}

# 난이도 정규화 매핑
DIFFICULTY_NORMALIZE = {
    "쉬움": "easy", "쉬운": "easy", "쉽": "easy", "easy": "easy",
    "중간": "medium", "보통": "medium", "medium": "medium",
    "어려움": "hard", "어려운": "hard", "어렵": "hard", "hard": "hard",
}

# 언어 정규화 매핑
LANGUAGE_NORMALIZE = {
    "파이썬": "python", "python": "python",
    "자바": "java", "java": "java",
    "씨플플": "cpp", "cpp": "cpp", "c++": "cpp",
}

# 주제 정규화 매핑
TOPIC_NORMALIZE = {
    "기초": "기초", "basic": "기초",
    "정렬": "정렬", "sort": "정렬",
    "탐색": "탐색", "search": "탐색",
    "dp": "DP", "다이나믹": "DP", "동적": "DP",
    "그리디": "그리디", "greedy": "그리디",
    "구현": "구현", "implementation": "구현",
    "문자열": "문자열", "string": "문자열",
    "그래프": "그래프", "graph": "그래프",
    "브루트포스": "브루트포스", "bruteforce": "브루트포스",
    "이분탐색": "이분탐색",
    "bfs": "BFS/DFS", "dfs": "BFS/DFS",
}

# 질문 패턴 정의
QUESTION_PATTERNS = [
    # 추천 요청
    "추천", "뭐가 좋", "뭘 해", "뭘해", "알아서", "골라", "정해",
    # 모름 표현
    "모르", "몰라", "모름", "잘 모", "하나도",
    # 질문
    "뭐야", "뭔데", "뭐지", "어떤 거", "어떤거", "무슨",
    # 비교/설명 요청
    "차이", "뭐가 다", "설명", "알려",
]

# 추천 요청 패턴 (질문 중에서도 추천을 원하는 경우)
RECOMMENDATION_PATTERNS = [
    "추천", "뭐가 좋", "알아서", "골라", "정해", "아무", "랜덤",
]


def get_initial_state(
    message: str,
    conversation_history: List[Dict[str, str]] = None,
    user_context: Dict[str, Any] = None,
    existing_topic: str = None,
    existing_difficulty: str = None,
    existing_language: str = None,
) -> CollectionState:
    """초기 상태 생성"""

    # 현재 단계 결정
    if not existing_topic:
        current_step = "topic"
    elif not existing_difficulty:
        current_step = "difficulty"
    elif not existing_language:
        current_step = "language"
    else:
        current_step = "complete"

    return CollectionState(
        message=message,
        conversation_history=conversation_history or [],
        user_context=user_context or {},
        topic=existing_topic,
        difficulty=existing_difficulty,
        language=existing_language,
        current_step=current_step,
        is_question=False,
        extracted_value=None,
        question_type=None,
        response_message="",
        is_complete=False,
        route_to=None,
        error=None,
    )
