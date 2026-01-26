"""
LangGraph State for Problem Discovery Phase (Stage 2)

2단계: 문제 탐색 그래프의 상태 정의

역할:
- RAG 기반 문제 검색
- 검색 결과 필터링
- 사용자 문제 선택 처리
- 문제 확정 및 유형 선택

입력: IntentGraph 결과 (collected_info 포함)
출력: 선택된 문제 + 문제 유형 (blank, puzzle, guided)
"""
from typing import TypedDict, Optional, List, Dict, Any


class CollectedInfo(TypedDict, total=False):
    """수집된 문제 검색 정보 (IntentGraph에서 전달)"""
    topics: List[str]
    difficulty: Optional[str]
    language: Optional[str]
    specific_needs: Optional[str]
    time_available: Optional[int]
    selected_problem: Optional[str]
    selected_problem_index: Optional[int]
    # 출처 및 생성 관련
    source: Optional[str]  # 문제 출처 (baekjoon, leetcode) - 검색 필터용
    wants_generation: bool  # 새 문제 생성 요청 여부
    generation_details: Optional[str]  # 선택적 4단계: 어떤 문제 원하는지 자유 양식
    is_corporate_test: bool  # 대기업 코테 관련 여부 (programmers RAG 포함)


class ProblemInfo(TypedDict, total=False):
    """문제 정보"""
    id: Optional[str]
    name: Optional[str]
    title: Optional[str]
    question: Optional[str]
    description: Optional[str]
    difficulty: str
    tags: Optional[List[str]]
    topics: Optional[List[str]]
    solutions: Optional[List[Dict[str, str]]]
    code: Optional[Dict[str, str]]
    similarity: Optional[float]


class DiscoveryState(TypedDict, total=False):
    """
    2단계 LangGraph State: 문제 탐색

    입력: IntentGraph 결과 (collected_info)
    출력: 선택된 문제 + 문제 유형
    """
    # === 입력 (IntentGraph에서 전달) ===
    message: str
    conversation_history: List[Dict[str, str]]
    user_context: Optional[Dict[str, Any]]
    collected_info: CollectedInfo
    intent: str  # 현재 의도 (problem_selection, new_problem 등)

    # === 검색 결과 ===
    search_results: List[ProblemInfo]
    generated_problem: Optional[ProblemInfo]  # CodeGen fallback
    should_generate: bool  # CodeGen 필요 여부
    awaiting_selection: bool  # 선택 대기 상태
    search_offset: int  # 검색 오프셋 (더 찾아보기용)
    force_generate: bool  # 강제 생성 (새 문제 생성 버튼)
    search_method: Optional[str]  # 🚀 Agentic RAG: metadata | semantic | hybrid
    retry_info: Optional[Dict[str, Any]]  # 🔄 조건 완화 재시도 정보

    # === 동적 페이지 크기 ===
    requested_limit: Optional[int]  # 🔢 사용자 요청 개수
    per_page: int  # 🔢 실제 적용된 페이지당 개수
    limit_exceeded: bool  # 🔢 최대 개수 초과 여부
    original_request: Optional[int]  # 🔢 원래 요청한 개수 (초과 시)

    # === 필터링 ===
    filtered_results: List[ProblemInfo]

    # === 선택 ===
    selection_index: Optional[int]  # intent_tool에서 감지한 선택 인덱스 (1-based)
    selected_problem: Optional[ProblemInfo]
    problem_type: Optional[str]  # blank, puzzle, guided
    is_confirmed: bool  # 문제 확정 여부

    # === 문제 질문 (inquire_problem) ===
    inquiry_target: Optional[str]  # 질문 대상 (인덱스 또는 문제명)
    inquiry_question: Optional[str]  # 원본 질문

    # === 응답 ===
    response_message: str
    action_trigger: Optional[str]  # search_problems, select_problem_type, generate_problem
    action_data: Optional[Dict[str, Any]]

    # === 플로우 제어 ===
    next_node: Optional[str]
    route_to: Optional[str]  # solving, respond
    fallback_reason: Optional[str]  # 의도 파악 실패 사유

    # === 에러 ===
    error: Optional[str]


# 문제 탐색 관련 의도
DISCOVERY_INTENTS = {
    "new_problem",
    "topic_specific",
    "random_recommend",
    "difficulty_change",
    "language_change",
    "similar_code_problem",
    "problem_selection",
    "more_search",
    "generate_new",
    "inquire_problem",  # 검색 결과 문제에 대한 질문
}

# 검색 후 바로 문제 목록을 보여주는 의도
IMMEDIATE_SEARCH_INTENTS = {
    "random_recommend",
    "new_problem",
    "topic_specific",
    "more_search",
}

# 문제 선택 관련 의도
SELECTION_INTENTS = {
    "problem_selection",
}

# 강제 생성 의도
GENERATE_INTENTS = {
    "generate_new",
}
