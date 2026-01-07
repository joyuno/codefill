"""
LangGraph State Definitions for CodeFill Chat Agent

상태 정의:
- 사용자 입력 및 대화 히스토리
- 의도 분류 결과
- 수집된 정보 (주제, 난이도, 언어)
- 검색/생성된 문제
- 응답 메시지
"""
from typing import TypedDict, Optional, List, Dict, Any, Annotated
from operator import add


class CollectedInfo(TypedDict, total=False):
    """수집된 문제 검색 정보"""
    topics: List[str]
    difficulty: Optional[str]  # easy, medium, hard
    language: Optional[str]  # python, java, cpp
    specific_needs: Optional[str]
    time_available: Optional[int]
    selected_problem: Optional[str]
    selected_problem_index: Optional[int]


class IntentResult(TypedDict, total=False):
    """의도 분류 결과"""
    intent: str
    confidence: float
    method: str  # embedding, llm, llm_verified
    requires_context: Optional[str]
    next_action: Optional[str]


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


class ChatState(TypedDict, total=False):
    """
    LangGraph Chat State

    그래프를 통해 흐르는 모든 상태 정보
    """
    # === 입력 ===
    message: str  # 현재 사용자 메시지
    conversation_history: List[Dict[str, str]]  # 대화 히스토리
    user_context: Optional[Dict[str, Any]]  # 사용자 컨텍스트 (현재 문제, 코드 등)

    # === 의도 분류 ===
    intent_result: Optional[IntentResult]

    # === 정보 수집 ===
    collected_info: CollectedInfo
    is_info_complete: bool  # 검색에 필요한 정보가 다 모였는지

    # === 문제 검색/생성 ===
    search_results: List[ProblemInfo]  # RAG 검색 결과
    generated_problem: Optional[ProblemInfo]  # CodeGen 생성 문제
    should_generate: bool  # CodeGen fallback 필요 여부

    # === 문제 선택 ===
    selected_problem: Optional[ProblemInfo]
    problem_type: Optional[str]  # blank, puzzle, guided

    # === 생성된 문제 콘텐츠 ===
    problem_content: Optional[Dict[str, Any]]  # Blank/Puzzle/Guided 생성 결과

    # === 응답 ===
    response_message: str
    action_trigger: Optional[str]  # search_problems, select_problem_type, generate_hint 등
    action_data: Optional[Dict[str, Any]]  # 프론트엔드에 전달할 액션 데이터
    suggested_actions: Optional[List[Dict[str, str]]]  # 🚀 동적 선택지 [{label, value, description}]

    # === 플로우 제어 ===
    next_node: Optional[str]  # 다음으로 이동할 노드 (조건부 라우팅용)
    error: Optional[str]  # 에러 메시지


# 상태 병합을 위한 리듀서 (리스트 append 등)
def merge_search_results(existing: List[ProblemInfo], new: List[ProblemInfo]) -> List[ProblemInfo]:
    """검색 결과 병합 (중복 제거)"""
    if not existing:
        return new
    existing_ids = {p.get("id") for p in existing if p.get("id")}
    merged = existing.copy()
    for p in new:
        if p.get("id") not in existing_ids:
            merged.append(p)
    return merged


# Intent별 다음 노드 매핑
INTENT_TO_NODE = {
    # 문제 검색/추천
    "new_problem": "collect_info",
    "topic_specific": "collect_info",
    "random_recommend": "collect_info",  # 주제/난이도/언어 수집 후 검색
    "difficulty_change": "collect_info",
    "language_change": "collect_info",
    "similar_code_problem": "search_similar",

    # 문제 선택
    "problem_selection": "handle_problem_selection",

    # 문제 풀이 중
    "hint_request": "provide_hint",
    "solution_request": "provide_solution",
    "explanation_request": "provide_explanation",
    "code_review": "review_code",
    "error_help": "help_error",

    # 진행 관련
    "skip_problem": "skip_problem",
    "retry_problem": "retry_problem",
    "submit_code": "submit_code",

    # 학습/통계
    "progress_check": "show_progress",
    "weak_point": "analyze_weakness",
    "study_plan": "create_plan",

    # 일반 대화
    "greeting": "handle_greeting",
    "thanks": "handle_thanks",
    "goodbye": "handle_goodbye",
    "confusion": "handle_confusion",
    "affirmation": "handle_affirmation",
    "negation": "handle_negation",
    "out_of_scope": "handle_out_of_scope",
    "clarification_needed": "request_clarification",
}

# 컨텍스트가 필요한 의도
CONTEXT_REQUIRED_INTENTS = {
    "hint_request": "problem",
    "solution_request": "problem",
    "code_review": "code",
    "error_help": "code",
    "similar_code_problem": "code",
    "skip_problem": "problem",
    "retry_problem": "problem",
    "submit_code": "code",
}
