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
    question_info: Optional[Dict[str, Any]]  # 질문 상세 정보 (question_type, question_target, question_subjects)
    is_off_topic: bool                    # 관련 없는 메시지인지
    extracted_with_question: Optional[Dict[str, str]]  # 질문과 함께 추출된 값 (동시 처리용)

    # ============================================================
    # 추천/확인 관련 (handle_question 용)
    # ============================================================
    suggested_value: Optional[str]        # LLM이 추천한 값 (예: "DP")
    awaiting_confirmation: bool           # "네/아니오" 응답 대기 상태
    is_positive_response: bool            # 긍정 응답인지 ("네")
    is_negative_response: bool            # 부정 응답인지 ("아니오")

    # ============================================================
    # 거절 히스토리 및 맥락 (부정 응답 처리용)
    # ============================================================
    rejected_values: List[str]            # 거절된 값 리스트 (예: ["정렬", "DP"])
    rejection_reason: Optional[str]       # 거절 이유 힌트 (예: "too_hard", "already_done")
    alternative_value: Optional[str]      # 부정과 함께 제시된 대안 (예: "DP 말고 그래프" → "그래프")

    # ============================================================
    # 출력
    # ============================================================
    response_message: str                 # 사용자에게 보낼 메시지
    is_complete: bool                     # 모든 정보 수집 완료 여부
    route_to: Optional[str]               # 다음 그래프 (discovery, solving, respond)
    chips: Optional[List[Dict[str, str]]] # 빠른 선택용 칩 리스트
    needs_reconfirmation: bool            # 애매한 응답 → 재확인 필요

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
    # 티어 (한글)
    "실버", "골드", "플래티넘", "플레티넘", "다이아", "다이아몬드", "마스터",
    # 티어 (영어)
    "silver", "gold", "platinum", "diamond", "master",
    # 기존 호환성 (한글)
    "쉬움", "쉬운", "쉽", "중간", "보통", "어려움", "어려운", "어렵",
    # 기존 호환성 (영어)
    "easy", "medium", "medium_hard", "hard", "very_hard",
}

VALID_LANGUAGES = {
    # 한글
    "파이썬", "자바", "씨플플",
    # 영어
    "python", "java", "cpp", "c++",
}

# 난이도 정규화 매핑 (티어 시스템)
# DB 값: easy, medium, medium_hard, hard, very_hard
DIFFICULTY_NORMALIZE = {
    # 티어명 → DB값
    "실버": "easy", "silver": "easy",
    "골드": "medium", "gold": "medium",
    "플래티넘": "medium_hard", "플레티넘": "medium_hard", "platinum": "medium_hard",
    "다이아": "hard", "다이아몬드": "hard", "diamond": "hard",
    "마스터": "very_hard", "master": "very_hard",
    # 기존 호환성
    "쉬움": "easy", "쉬운": "easy", "쉽": "easy", "easy": "easy",
    "중간": "medium", "보통": "medium", "medium": "medium",
    "medium_hard": "medium_hard",
    "어려움": "hard", "어려운": "hard", "어렵": "hard", "hard": "hard",
    "very_hard": "very_hard",
}

# DB값 → 티어 표시명
DIFFICULTY_TO_TIER = {
    "easy": "실버",
    "medium": "골드",
    "medium_hard": "플래티넘",
    "hard": "다이아",
    "very_hard": "마스터",
}

# 티어 설명
TIER_DESCRIPTIONS = {
    "easy": "기본 개념 연습",
    "medium": "응용 문제",
    "medium_hard": "심화 응용",
    "hard": "도전적인 문제",
    "very_hard": "최상위 난이도",
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

# ============================================================
# 패턴/키워드 상수들은 collection_tools.py의 LLM 프롬프트로 이동됨
# (Tool 기반 리팩토링으로 인해 더 이상 사용하지 않음)
# ============================================================


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
        extracted_with_question=None,  # 질문과 함께 추출된 값
        suggested_value=None,
        awaiting_confirmation=False,
        is_positive_response=False,
        is_negative_response=False,
        # 거절 히스토리 및 맥락
        rejected_values=[],
        rejection_reason=None,
        alternative_value=None,
        # 출력
        response_message="",
        is_complete=False,
        route_to=None,
        error=None,
    )
