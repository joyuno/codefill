from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Any
from datetime import datetime
from enum import Enum
from uuid import UUID
import json


class ProblemType(str, Enum):
    """Problem types for MVP v1."""
    BLANK = "blank"         # 빈칸 채우기 - Fill in the blanks
    PUZZLE = "puzzle"       # 퍼즐 (Parsons Problem) - 드래그앤드롭 코드 블록 정렬


class Difficulty(str, Enum):
    """Difficulty levels."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class Framework(str, Enum):
    """Supported programming languages for algorithm problems."""
    PYTHON = "python"
    JAVA = "java"
    CPP = "cpp"
    JAVASCRIPT = "javascript"  # For basic algorithm problems only


class BlankInfo(BaseModel):
    """Information about a blank in blank-fill problems."""
    id: str
    position: int  # character position in code
    answer: str
    hints: List[str] = []


class PuzzleBlock(BaseModel):
    """Code block for Parsons Problem (puzzle type)."""
    id: str
    code: str
    indentation: int = 0
    position: Optional[int] = None  # correct position (1-based)


class PuzzleData(BaseModel):
    """Answer data structure for puzzle problems."""
    blocks: List[PuzzleBlock]
    correct_order: List[str]  # List of block IDs in correct order
    distractors: Optional[List[PuzzleBlock]] = None  # Wrong blocks to confuse


class Code(BaseModel):
    """Base code model."""
    id: UUID
    framework: Framework
    category: Optional[str] = None
    tags: List[str] = []
    title: str
    description: Optional[str] = None
    code: str
    difficulty: Difficulty = Difficulty.MEDIUM
    source: Optional[str] = None
    source_url: Optional[str] = None
    created_at: datetime


class Problem(BaseModel):
    """Problem model."""
    id: UUID
    code_id: UUID
    problem_type: ProblemType
    problem_code: str
    difficulty: Difficulty = Difficulty.MEDIUM
    times_attempted: int = 0
    times_solved: int = 0
    avg_solve_time: Optional[int] = None  # seconds
    created_at: datetime

    # Type-specific data (populated based on problem_type)
    blanks: Optional[List[BlankInfo]] = None      # for BLANK
    puzzle_data: Optional[PuzzleData] = None      # for PUZZLE (Parsons Problems)


class ProblemDetail(BaseModel):
    """Detailed problem for practice."""
    problem: Problem
    code: Code
    hints: List[str] = []
    key_concepts: List[str] = []
    related_docs: List[dict] = []


class ProblemListItem(BaseModel):
    """Problem item for list view."""
    id: UUID
    title: str
    framework: Framework
    difficulty: Difficulty
    problem_type: ProblemType
    topics: List[str] = []
    times_solved: int = 0
    avg_solve_time: Optional[int] = None


class ProblemFilter(BaseModel):
    """Filter for problem search."""
    framework: Optional[Framework] = None
    difficulty: Optional[Difficulty] = None
    problem_type: Optional[ProblemType] = None
    search: Optional[str] = None
    tags: Optional[List[str]] = None
    page: int = 1
    limit: int = 20


class HintRequest(BaseModel):
    """Request for hint."""
    problem_id: UUID
    hint_level: int = Field(..., ge=1, le=3)


class HintResponse(BaseModel):
    """Response with hint."""
    hint: str
    level: int
    xp_cost: int = 10
    docs_reference: Optional[str] = None


# ===========================================
# base_problems 테이블용 모델
# ===========================================

class BaseProblemListItem(BaseModel):
    """base_problems 목록 조회용 모델."""
    id: UUID
    original_id: str
    name: str
    difficulty: str
    tags: List[str] = []
    source: Optional[str] = None
    input_output: Optional[dict] = None
    solve_count: int = 0  # 풀이 수 (유저당 1회만)
    like_count: int = 0  # 좋아요 수

    @field_validator('input_output', mode='before')
    @classmethod
    def parse_input_output(cls, v):
        """JSON 문자열을 dict로 파싱"""
        if v is None:
            return None
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return None
        return v


class SolutionItem(BaseModel):
    """솔루션 코드 아이템."""
    code: str
    language: str


class BaseProblemDetail(BaseModel):
    """base_problems 상세 조회용 모델 (Preview)."""
    id: UUID
    original_id: str
    name: str
    question: str
    difficulty: str
    tags: List[str] = []
    source: Optional[str] = None
    url: Optional[str] = None
    input_output: Optional[dict] = None
    explanation: Optional[str] = None
    solutions: List[SolutionItem] = []  # 솔루션 코드 목록

    @field_validator('input_output', mode='before')
    @classmethod
    def parse_input_output(cls, v):
        """JSON 문자열을 dict로 파싱"""
        if v is None:
            return None
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return None
        return v


class BaseProblemListResponse(BaseModel):
    """base_problems 목록 응답."""
    items: List[BaseProblemListItem]
    total: int
    page: int
    limit: int
    has_more: bool
