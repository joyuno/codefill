"""
LangGraph State for Problem Solving Phase

문제 풀이 중 힌트/피드백/정답 체크를 위한 상태 정의
"""
from typing import TypedDict, Optional, List, Dict, Any


class ProblemContext(TypedDict, total=False):
    """현재 풀고 있는 문제 정보"""
    id: str
    name: str
    title: str
    description: str
    difficulty: str
    topics: List[str]
    problem_type: str  # blank, puzzle, guided

    # 문제 유형별 데이터
    blanks: Optional[List[Dict[str, Any]]]  # blank 문제의 빈칸들
    puzzle_blocks: Optional[List[Dict[str, Any]]]  # puzzle 문제의 블록들
    guided_steps: Optional[List[Dict[str, Any]]]  # guided 문제의 단계들

    # 정답 정보
    solution_code: Optional[str]
    expected_output: Optional[str]


class UserProgress(TypedDict, total=False):
    """사용자 진행 상황"""
    current_code: str  # 현재 작성 중인 코드
    filled_blanks: Dict[str, str]  # blank 문제: 채운 빈칸들
    arranged_blocks: List[int]  # puzzle 문제: 배치한 블록 순서
    completed_steps: List[int]  # guided 문제: 완료한 단계들

    attempt_count: int  # 시도 횟수
    hint_count: int  # 받은 힌트 수
    last_error: Optional[str]  # 마지막 에러 메시지


class SolvingIntentResult(TypedDict, total=False):
    """풀이 중 의도 분류 결과"""
    intent: str  # hint_request, code_review, answer_check, feedback_request, question, give_up
    confidence: float
    sub_intent: Optional[str]  # 세부 의도 (e.g., hint_algorithm, hint_syntax)


class SolvingState(TypedDict, total=False):
    """
    문제 풀이 LangGraph State

    문제가 화면에 표시된 후, 사용자가 풀이 중일 때 사용
    """
    # === 입력 ===
    message: str
    conversation_history: List[Dict[str, str]]

    # === 컨텍스트 ===
    problem_context: ProblemContext  # 현재 문제 정보
    user_progress: UserProgress  # 사용자 진행 상황

    # === 의도 분류 ===
    intent_result: Optional[SolvingIntentResult]

    # === 힌트 ===
    hint_level: int  # 1~4 (점진적 힌트)
    previous_hints: List[str]  # 이전에 준 힌트들

    # === 피드백 ===
    code_analysis: Optional[Dict[str, Any]]  # 코드 분석 결과
    is_correct: Optional[bool]  # 정답 여부
    feedback_type: Optional[str]  # praise, correction, suggestion

    # === 응답 ===
    response_message: str
    action_trigger: Optional[str]  # show_hint, highlight_error, show_solution, next_step
    action_data: Optional[Dict[str, Any]]

    # === 플로우 제어 ===
    next_node: Optional[str]


# 풀이 중 의도 → 노드 매핑
SOLVING_INTENT_TO_NODE = {
    "hint_request": "provide_hint",
    "code_review": "review_code",
    "answer_check": "check_answer",
    "feedback_request": "provide_feedback",
    "explain_concept": "explain_concept",
    "give_up": "show_solution",
    "next_step": "guide_next_step",  # guided 문제 전용
    "question": "answer_question",  # 일반 질문
}
