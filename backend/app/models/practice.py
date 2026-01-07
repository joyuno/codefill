from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict
from datetime import datetime
from enum import Enum
from uuid import UUID

from .problem import ProblemType


class SubmissionResult(str, Enum):
    """Submission result types."""
    CORRECT = "correct"
    INCORRECT = "incorrect"
    PARTIAL = "partial"
    ERROR = "error"


class TestResult(BaseModel):
    """Result of a single test case."""
    test_id: str
    passed: bool
    input: str
    expected: str
    actual: Optional[str] = None
    error: Optional[str] = None


class BlankSubmission(BaseModel):
    """Submission for blank-fill problems."""
    problem_id: UUID
    answers: Dict[str, str]  # blank_id -> answer


class PuzzleBlockSubmission(BaseModel):
    """Single block in puzzle submission."""
    id: str
    indentation: int


class PuzzleSubmission(BaseModel):
    """Submission for puzzle (Parsons) problems."""
    problem_id: UUID
    block_order: List[PuzzleBlockSubmission]  # Blocks in user's arranged order with indentation


class SubmissionResponse(BaseModel):
    """Response for problem submission."""
    result: SubmissionResult
    is_correct: bool
    score: Optional[int] = None
    xp_earned: int = 0
    feedback: Optional[str] = None

    # Type-specific results
    blank_results: Optional[Dict[str, bool]] = None  # blank_id -> correct
    puzzle_results: Optional[Dict[str, bool]] = None  # block_id -> correct position/indentation


class CodeExecutionRequest(BaseModel):
    """Request for code execution."""
    code: str
    language: str = "javascript"
    test_input: Optional[str] = None


class CodeExecutionResponse(BaseModel):
    """Response from code execution."""
    success: bool
    output: Optional[str] = None
    error: Optional[str] = None
    execution_time: Optional[int] = None  # ms


class PracticeSession(BaseModel):
    """Practice session model."""
    id: UUID
    user_id: UUID
    problem_id: UUID
    problem_type: ProblemType
    started_at: datetime
    completed_at: Optional[datetime] = None
    is_correct: Optional[bool] = None
    score: Optional[int] = None
    hints_used: int = 0
    xp_earned: int = 0


class AttemptCreate(BaseModel):
    """Model for creating an attempt record."""
    user_id: UUID
    problem_id: UUID
    is_correct: bool
    score: Optional[int] = None
    submitted_code: Optional[str] = None
    submitted_answer: Optional[str] = None
    time_spent: Optional[int] = None
    hints_used: int = 0
    xp_earned: int = 0


class Attempt(BaseModel):
    """Attempt record model."""
    id: UUID
    user_id: UUID
    problem_id: UUID
    is_correct: bool
    score: Optional[int] = None
    submitted_code: Optional[str] = None
    submitted_answer: Optional[str] = None
    started_at: Optional[datetime] = None
    submitted_at: datetime
    time_spent: Optional[int] = None
    hints_used: int = 0
    xp_earned: int = 0


class XPConfig:
    """XP configuration for different problem types and difficulties."""

    # 난이도별 XP 획득량
    DIFFICULTY_XP = {
        "easy": 20,
        "medium": 40,
        "medium_hard": 70,
        "hard": 100,
        "very_hard": 150,
    }

    # 문제 유형별 기본 XP (난이도 없을 때 fallback)
    BLANK_CORRECT = 40     # 빈칸 채우기 기본
    PUZZLE_CORRECT = 40    # 퍼즐(Parsons) 기본
    GUIDED_CORRECT = 60    # 가이드 문제 기본

    # 힌트 페널티
    HINT_COST = 5          # 힌트 사용 시 -5 XP

    @classmethod
    def get_xp_for_difficulty(cls, difficulty: str, problem_type: str = "blank") -> int:
        """난이도에 따른 XP 반환, 없으면 문제 유형별 기본값"""
        if difficulty in cls.DIFFICULTY_XP:
            return cls.DIFFICULTY_XP[difficulty]
        # fallback to problem type default
        type_defaults = {
            "blank": cls.BLANK_CORRECT,
            "puzzle": cls.PUZZLE_CORRECT,
            "guided": cls.GUIDED_CORRECT,
        }
        return type_defaults.get(problem_type, 40)


class RecordSubmission(BaseModel):
    """Simple submission for recording problem solve (XP & grass)."""
    problem_id: str  # UUID or generated problem ID
    base_problem_id: Optional[str] = None  # base_problems 테이블의 UUID (잔디 클릭 시 문제 정보 표시용)
    problem_type: str = "blank"  # blank, puzzle, guided
    difficulty: Optional[str] = None  # easy, medium, medium_hard, hard, very_hard
    is_correct: bool = True
    xp_earned: Optional[int] = None  # None이면 난이도 기반 자동 계산
    problem_name: Optional[str] = None  # 문제 이름 (잔디 클릭 시 표시용)
    hints_used: Optional[int] = None  # 힌트 사용 횟수 (기록용)
    topics: Optional[List[str]] = None  # 문제 주제/태그 (예: ["DP", "그래프"])
    attempt_id: Optional[str] = None  # 기존 pending attempt ID (attempt_details 기록용)


class RecordResponse(BaseModel):
    """Response for record submission."""
    success: bool
    xp_earned: int
    message: str


class HintCheckResponse(BaseModel):
    """Response for hint availability check."""
    can_use: bool
    current_xp: int
    hint_cost: int
    message: str


class HintUseResponse(BaseModel):
    """Response after using hint."""
    success: bool
    xp_deducted: int
    remaining_xp: int
    message: str


# ============================================================
# Start Practice (Attempt Tracking)
# ============================================================

class StartPracticeRequest(BaseModel):
    """문제 풀이 시작 요청 - attempt 생성"""
    problem_id: str  # UUID or generated problem ID
    problem_type: str = "blank"  # blank, puzzle, guided
    difficulty: Optional[str] = None
    problem_name: Optional[str] = None
    topics: Optional[List[str]] = None


class StartPracticeResponse(BaseModel):
    """문제 풀이 시작 응답"""
    attempt_id: str
    started_at: str
    message: str


# ============================================================
# Attempt Detail Recording
# ============================================================

class AttemptDetailAction(str, Enum):
    """attempt_details action types"""
    BLANK_SUBMIT = "blank_submit"
    BLANK_HINT_REQUEST = "blank_hint_request"
    BLANK_HINT_REVEAL = "blank_hint_reveal"
    PUZZLE_SUBMIT = "puzzle_submit"
    PUZZLE_HINT_REQUEST = "puzzle_hint_request"
    GUIDED_MESSAGE = "guided_message"
    GUIDED_STEP_COMPLETE = "guided_step_complete"
    GIVE_UP = "give_up"


class RecordAttemptDetailRequest(BaseModel):
    """attempt_details 기록 요청 (내부용)"""
    attempt_id: str
    action_type: str
    step_number: Optional[int] = None

    # Blank specific
    blank_index: Optional[int] = None
    blank_user_answer: Optional[str] = None
    blank_correct_answer: Optional[str] = None
    blank_is_correct: Optional[bool] = None
    blank_hint_level: Optional[int] = None
    blank_hint_content: Optional[str] = None

    # Puzzle specific
    puzzle_user_order: Optional[List[int]] = None
    puzzle_correct_order: Optional[List[int]] = None
    puzzle_wrong_positions: Optional[List[Dict]] = None
    puzzle_hint_content: Optional[str] = None

    # Guided specific
    guided_step: Optional[int] = None
    guided_user_message: Optional[str] = None
    guided_tutor_response: Optional[str] = None
    guided_understanding_score: Optional[float] = None

    # Hint tracking
    hint_was_requested: bool = False
