"""
LangGraph State for Intent Classification Phase (Stage 1)

1단계: 의도 파악 그래프의 상태 정의

역할:
- 사용자 메시지 의도 분류
- 다음 단계로 라우팅 결정

출력:
- intent_result: 분류된 의도
- route_to: 다음 그래프 (discovery, solving, respond)

Note: 정보 수집은 InfoCollectionGraph (별도)에서 처리
"""
from typing import TypedDict, Optional, List, Dict, Any


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
    method: str  # embedding, llm, llm_verified, rule
    requires_context: Optional[str]  # code, problem, previous_suggestion
    next_action: Optional[str]


class IntentState(TypedDict, total=False):
    """
    1단계 LangGraph State: 의도 파악

    입력: 사용자 메시지 + 대화 히스토리
    출력: 의도 + 수집된 정보 + 라우팅 결정
    """
    # === 입력 ===
    message: str
    conversation_history: List[Dict[str, str]]
    user_context: Optional[Dict[str, Any]]  # 온보딩 데이터, 현재 상태 등

    # === 의도 분류 ===
    intent_result: Optional[IntentResult]

    # === 정보 수집 ===
    collected_info: CollectedInfo
    is_info_complete: bool  # 다음 단계로 진행 가능 여부

    # === 응답 (추가 질문 시) ===
    response_message: str

    # === 라우팅 ===
    route_to: Optional[str]  # discovery, solving, respond, greeting, general
    next_node: Optional[str]  # 그래프 내 다음 노드

    # === 에러 ===
    error: Optional[str]


# 의도별 라우팅 대상 매핑
INTENT_TO_ROUTE = {
    # Discovery Graph로 라우팅 (문제 탐색)
    "new_problem": "discovery",
    "topic_specific": "discovery",
    "random_recommend": "discovery",
    "difficulty_change": "discovery",
    "language_change": "discovery",
    "similar_code_problem": "discovery",
    "problem_selection": "discovery",

    # Solving Graph로 라우팅 (문제 풀이)
    "hint_request": "solving",
    "solution_request": "solving",
    "explanation_request": "solving",
    "code_review": "solving",
    "error_help": "solving",
    "skip_problem": "solving",
    "retry_problem": "solving",
    "submit_code": "solving",

    # 직접 응답 (별도 그래프 불필요)
    "greeting": "respond",
    "thanks": "respond",
    "goodbye": "respond",
    "confusion": "respond",
    "affirmation": "respond",
    "negation": "respond",
    "out_of_scope": "respond",
    "clarification_needed": "respond",

    # 통계/학습 (직접 응답)
    "progress_check": "respond",
    "weak_point": "respond",
    "study_plan": "respond",
}

# 정보 수집이 필요한 의도
NEEDS_INFO_COLLECTION = {
    "new_problem",
    "topic_specific",
    "random_recommend",  # 주제/난이도/언어 수집
    "difficulty_change",
    "language_change",
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
