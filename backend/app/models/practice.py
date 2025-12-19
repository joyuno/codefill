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
    """XP configuration for different problem types."""
    BLANK_CORRECT = 50     # 빈칸 채우기 정답
    PUZZLE_CORRECT = 70    # 퍼즐(Parsons) 정답 - 더 복잡하므로 XP 높음
    HINT_PENALTY = 10      # 힌트 사용시 페널티
