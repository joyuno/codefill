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

    # === 필터링 ===
    filtered_results: List[ProblemInfo]

    # === 선택 ===
    selection_index: Optional[int]  # intent_tool에서 감지한 선택 인덱스 (1-based)
    selected_problem: Optional[ProblemInfo]
    problem_type: Optional[str]  # blank, puzzle, guided
    is_confirmed: bool  # 문제 확정 여부

    # === 응답 ===
    response_message: str
    action_trigger: Optional[str]  # search_problems, select_problem_type, generate_problem
    action_data: Optional[Dict[str, Any]]

    # === 플로우 제어 ===
    next_node: Optional[str]
    route_to: Optional[str]  # solving, respond

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
