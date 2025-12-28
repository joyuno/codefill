"""
Agent Models
Request/Response models for AI agents

출력 형식: data/examples/ 폴더의 JSON 형식과 일치
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from uuid import UUID


# ============================================================
# Enums
# ============================================================

class ProblemTypeEnum(str, Enum):
    """Problem generation types."""
    BLANK = "blank"
    PUZZLE = "puzzle"
    GUIDED = "guided"


class LanguageEnum(str, Enum):
    """Supported programming languages."""
    PYTHON = "python"
    JAVA = "java"
    CPP = "cpp"


class DifficultyEnum(str, Enum):
    """Difficulty levels."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class UserLevelEnum(str, Enum):
    """User skill levels."""
    BEGINNER = "beginner"
    ELEMENTARY = "elementary"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


# ============================================================
# Chat Agent Models
# ============================================================

class ChatAgentMessage(BaseModel):
    """Single message in chat history."""
    role: str  # "user" or "assistant"
    content: str


class ChatAgentRequest(BaseModel):
    """Request to Chat Agent for info collection."""
    message: str
    conversation_history: List[ChatAgentMessage] = []
    user_context: Optional[Dict[str, Any]] = None  # onboarding data


class CollectedInfo(BaseModel):
    """Information collected by Chat Agent."""
    topics: List[str] = []
    difficulty: Optional[str] = None
    language: Optional[str] = None
    specific_needs: Optional[str] = None
    time_available: Optional[int] = None


class ChatAgentResponse(BaseModel):
    """Response from Chat Agent."""
    message: str
    collected_info: CollectedInfo
    is_complete: bool = False
    search_query: Optional[str] = None


# ============================================================
# Problem Generation Models
# ============================================================

class BaseProblemInfo(BaseModel):
    """Base problem information for generation."""
    id: Optional[str] = None
    title: str
    description: str
    code: str
    language: LanguageEnum = LanguageEnum.PYTHON
    difficulty: DifficultyEnum = DifficultyEnum.MEDIUM
    topics: List[str] = []
    time_complexity: Optional[str] = None
    space_complexity: Optional[str] = None


class ProblemGenerationRequest(BaseModel):
    """Request to generate a problem."""
    base_problem: BaseProblemInfo
    problem_type: ProblemTypeEnum
    user_level: UserLevelEnum = UserLevelEnum.INTERMEDIATE
    language: LanguageEnum = LanguageEnum.PYTHON


# --- Blank Problem (data/examples/problems_blank.json 형식) ---

class BlankProblemResponse(BaseModel):
    """
    Generated blank-fill problem.
    형식: {original_id, language, code_template, answers[]}
    """
    original_id: str
    language: str
    code_template: str  # _0_, _1_, _2_ 형식의 빈칸
    answers: List[str]  # 순서대로 정답 배열


# --- Puzzle Problem (data/examples/problems_puzzle.json 형식) ---

class PuzzleBlock(BaseModel):
    """Code block for puzzle problem."""
    id: int  # 정답 순서 (1, 2, 3, ...)
    code: str


class PuzzleProblemResponse(BaseModel):
    """
    Generated puzzle (Parsons) problem.
    형식: {original_id, language, fixed_start?, fixed_end?, blocks[]}
    """
    original_id: str
    language: str
    fixed_start: Optional[str] = None  # 고정된 시작 코드
    fixed_end: Optional[str] = None    # 고정된 끝 코드
    blocks: List[PuzzleBlock]          # id 순서가 정답


# --- Guided Problem (data/examples/problems_guided.json 형식) ---

class GuidedProblemResponse(BaseModel):
    """
    Generated guided (1:1) problem.
    형식: {original_id, language, concepts[], flow[], checkpoints[]}
    """
    original_id: str
    language: str
    concepts: List[str]     # 핵심 개념 목록
    flow: List[str]         # 학습 흐름 단계
    checkpoints: List[str]  # 체크포인트/확인 사항


# ============================================================
# Code Generation Models
# ============================================================

class CodeGenerationRequest(BaseModel):
    """Request to generate new educational code."""
    user_request: Dict[str, Any]  # collected_info from Chat Agent
    similar_problems: List[Dict[str, Any]] = []  # RAG results
    user_status: Optional[str] = None
    user_goal: Optional[str] = None
    user_level: UserLevelEnum = UserLevelEnum.INTERMEDIATE
    strong_algorithms: List[str] = []


class CodeGenerationResponse(BaseModel):
    """Generated educational code."""
    title: str
    title_en: str
    description: str
    code: Dict[str, str]  # language -> code
    input_format: str
    output_format: str
    examples: List[Dict[str, str]]
    constraints: List[str]
    difficulty: str
    topics: List[str]
    time_complexity: str
    space_complexity: str
    key_concepts: List[str]
    common_mistakes: List[str]
    hints_for_problem_gen: Dict[str, List[str]]


# ============================================================
# Hint Agent Models
# ============================================================

class HintAgentRequest(BaseModel):
    """Request for AI-generated hint."""
    problem_id: str
    problem_info: Dict[str, Any]
    user_code: Optional[str] = None
    attempt_count: int = 0
    hint_level: int = Field(1, ge=1, le=4)
    previous_hints: List[str] = []
    user_level: UserLevelEnum = UserLevelEnum.INTERMEDIATE


class RelatedConcept(BaseModel):
    """Related concept for hint."""
    name: str
    brief: str
    doc_reference: Optional[str] = None


class HintAgentResponse(BaseModel):
    """AI-generated hint response."""
    hint_level: int
    hint_content: str
    hint_type: str  # direction, approach, specific, final
    questions: List[str] = []
    related_concept: Optional[RelatedConcept] = None
    encouragement: str = ""
    next_hint_preview: Optional[str] = None
    code_snippet: Optional[str] = None
    common_mistake_check: Optional[str] = None


# ============================================================
# RAG Search Models
# ============================================================

class RAGSearchRequest(BaseModel):
    """Request for RAG-based problem search."""
    query: str
    topics: List[str] = []
    difficulty: Optional[DifficultyEnum] = None
    language: Optional[LanguageEnum] = None
    limit: int = Field(5, ge=1, le=20)


class RAGSearchResult(BaseModel):
    """Single RAG search result."""
    id: str
    title: str
    description: str
    similarity_score: float
    difficulty: str
    topics: List[str]


class RAGSearchResponse(BaseModel):
    """RAG search response."""
    results: List[RAGSearchResult]
    query_embedding_used: bool = False
    fallback_to_code_gen: bool = False


# ============================================================
# Intent-Based Chat Models
# ============================================================

class SessionContext(BaseModel):
    """세션 컨텍스트 (의도 분류에 필요한 정보)."""
    last_solved_problem: Optional[Dict[str, Any]] = None  # 최근 푼 문제 (코드 포함)
    current_problem: Optional[Dict[str, Any]] = None  # 현재 풀고 있는 문제
    last_suggestion: Optional[str] = None  # 마지막 제안
    recent_problems: List[Dict[str, Any]] = []  # 최근 본 문제들


class IntentChatRequest(BaseModel):
    """Intent-based Chat Agent request."""
    message: str
    conversation_history: List[ChatAgentMessage] = []
    user_context: Optional[Dict[str, Any]] = None  # onboarding data
    session_context: Optional[SessionContext] = None  # 세션 컨텍스트


class IntentInfo(BaseModel):
    """분류된 의도 정보."""
    intent: str
    confidence: float
    method: str  # "embedding", "llm", "rule", "fallback"
    requires_context: Optional[str] = None  # "code", "problem", "previous_suggestion"
    next_action: Optional[str] = None


class IntentChatResponse(BaseModel):
    """Intent-based Chat Agent response."""
    message: str
    intent_info: IntentInfo
    collected_info: Optional[CollectedInfo] = None
    is_complete: bool = False
    search_query: Optional[str] = None
    action_data: Optional[Dict[str, Any]] = None  # 추가 액션 데이터
