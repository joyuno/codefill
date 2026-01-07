"""
Agentic RAG State for Guided Tutor

1대1 대화형 문제 풀이를 위한 상태 정의
- 문제/정답 컨텍스트
- 학생 이해도 추적
- RAG 검색 결과
- 튜터 행동 결정
"""

from typing import TypedDict, Optional, List, Dict, Any, Literal, Annotated
from langgraph.graph import add_messages


class ProblemContext(TypedDict, total=False):
    """문제 컨텍스트"""
    id: str
    title: str
    description: str
    difficulty: str
    topics: List[str]
    solution_code: str
    key_concepts: List[str]
    input_output: Dict[str, Any]


class StudentProgress(TypedDict, total=False):
    """학생 진행 상황"""
    understanding_score: float  # 0.0 ~ 1.0
    concepts_mastered: List[str]  # 이해한 개념
    concepts_struggling: List[str]  # 어려워하는 개념
    current_focus: str  # 현재 다루는 개념
    hints_received: int  # 받은 힌트 수
    attempts: int  # 시도 횟수


class RetrievedDoc(TypedDict, total=False):
    """RAG 검색 문서"""
    content: str
    metadata: Dict[str, Any]
    relevance_score: float


class AgenticRAGState(TypedDict, total=False):
    """
    Agentic RAG State for Guided Tutor

    핵심 구성요소:
    1. messages: 대화 히스토리 (add_messages reducer)
    2. problem_context: 문제/정답 정보
    3. student_progress: 학생 이해도
    4. retrieved_docs: RAG 검색 결과
    5. tutor_action: 다음 행동 결정
    """

    # === 대화 히스토리 ===
    # add_messages reducer로 메시지 누적
    messages: Annotated[List[Dict[str, str]], add_messages]

    # === 문제 컨텍스트 ===
    problem_context: ProblemContext
    solution_code: str  # 정답 코드 (튜터만 알고 있음)
    key_concepts: List[str]  # 학습해야 할 핵심 개념

    # === 학생 상태 ===
    student_progress: StudentProgress
    current_student_code: Optional[str]  # 학생이 작성 중인 코드

    # === RAG 검색 ===
    search_query: Optional[str]  # 검색 쿼리
    retrieved_docs: List[RetrievedDoc]  # 검색된 문서
    retrieval_grade: Literal["relevant", "not_relevant", "pending"]

    # === 튜터 행동 ===
    tutor_action: Literal[
        "explain",       # 개념 설명
        "ask_question",  # 이해 확인 질문
        "give_hint",     # 힌트 제공
        "give_example",  # 예제 제공
        "guide_code",    # 코드 작성 유도
        "celebrate",     # 정답 축하
        "encourage",     # 격려
    ]

    # === 출력 ===
    response: str  # 튜터 응답
    suggested_next_step: Optional[str]  # 다음 단계 제안

    # === 플로우 제어 ===
    next_node: Optional[str]
    is_complete: bool  # 문제 풀이 완료 여부


# 튜터 행동별 프롬프트 힌트
TUTOR_ACTION_PROMPTS = {
    "explain": "개념을 간단히 설명해주세요. 2줄 이내로.",
    "ask_question": "이해도를 확인하는 질문을 하세요. 1줄로.",
    "give_hint": "정답 코드의 관련 부분을 암시하세요. 직접 보여주지 마세요.",
    "give_example": "비슷한 간단한 예제를 보여주세요.",
    "guide_code": "다음에 작성할 코드 방향을 제시하세요.",
    "celebrate": "정답을 축하하고 핵심을 요약해주세요. 2줄 이내.",
    "encourage": "격려하고 다시 시도하도록 유도하세요. 1줄로.",
}

# 이해도에 따른 기본 행동
UNDERSTANDING_TO_ACTION = {
    (0.0, 0.3): "explain",      # 낮은 이해도 → 설명
    (0.3, 0.5): "give_hint",    # 중간 이해도 → 힌트
    (0.5, 0.7): "ask_question", # 괜찮은 이해도 → 확인 질문
    (0.7, 0.9): "guide_code",   # 높은 이해도 → 코드 유도
    (0.9, 1.0): "celebrate",    # 완전 이해 → 축하
}
