"""
Agent Models
Request/Response models for AI agents

출력 형식: data/examples/ 폴더의 JSON 형식과 일치
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
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
    """Difficulty levels (5-tier system)."""
    EASY = "easy"           # 실버
    MEDIUM = "medium"       # 골드
    MEDIUM_HARD = "medium_hard"  # 플래티넘
    HARD = "hard"           # 다이아
    VERY_HARD = "very_hard"  # 마스터


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


class CollectedInfo(BaseModel):
    """Information collected by Chat Agent."""
    topics: List[str] = []
    difficulty: Optional[str] = None
    language: Optional[str] = None
    specific_needs: Optional[str] = None
    time_available: Optional[int] = None
    selected_problem: Optional[str] = None  # 선택된 문제 이름
    selected_problem_index: Optional[int] = None  # 선택된 문제 번호 (1-based)


class ChatAgentRequest(BaseModel):
    """Request to Chat Agent for info collection."""
    message: str
    conversation_history: List[ChatAgentMessage] = []
    user_context: Optional[Dict[str, Any]] = None  # onboarding data
    collected_info: Optional[CollectedInfo] = None  # 이전 턴에서 수집된 정보 (상태 유지용)


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
    original_id: Optional[str] = None  # base_problems의 original_id (예: "taco_100")
    name: Optional[str] = None  # DB에서 오는 문제 이름
    title: Optional[str] = None  # 생성된 문제 제목
    description: Optional[str] = None  # 문제 설명
    question: Optional[str] = None  # DB에서 오는 문제 설명 (description 대체)
    code: Optional[Union[str, dict]] = None  # str 또는 {"python": "...", "java": "..."}
    solutions: Optional[List[dict]] = None  # DB 문제의 솔루션 배열
    language: LanguageEnum = LanguageEnum.PYTHON
    difficulty: DifficultyEnum = DifficultyEnum.MEDIUM
    topics: List[str] = []
    tags: Optional[List[str]] = None  # DB 문제의 태그
    time_complexity: Optional[str] = None
    space_complexity: Optional[str] = None

    def get_title(self) -> str:
        """title 또는 name 반환"""
        return self.title or self.name or "Problem"

    def get_description(self) -> str:
        """description 또는 question 반환"""
        return self.description or self.question or ""

    def get_code(self, target_language: str = "python") -> str:
        """code 또는 solutions에서 코드 추출"""
        if self.code:
            # code가 dict인 경우: {"python": "...", "java": "..."}
            if isinstance(self.code, dict):
                return self.code.get(target_language) or next(iter(self.code.values()), "")
            # code가 문자열인 경우
            return self.code
        if self.solutions:
            # 타겟 언어의 솔루션 찾기
            for sol in self.solutions:
                if sol.get("language") == target_language:
                    return sol.get("code", "")
            # 없으면 첫 번째 솔루션
            if self.solutions:
                return self.solutions[0].get("code", "")
        return ""

        
class ProblemGenerationRequest(BaseModel):
    """Request to generate a problem."""
    base_problem: BaseProblemInfo
    problem_type: ProblemTypeEnum
    user_level: UserLevelEnum = UserLevelEnum.INTERMEDIATE
    language: LanguageEnum = LanguageEnum.PYTHON
    user_context: Optional[Dict[str, Any]] = None  # user_id 포함 (DB 저장용)


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

class ProblemTypeEnum(str, Enum):
    """Problem type enum for hints."""
    BLANK = "blank"
    PUZZLE = "puzzle"
    GUIDED = "guided"


class HintAgentRequest(BaseModel):
    """Request for AI-generated hint."""
    problem_id: str  # problems_blank, problems_puzzle, problems_guided 테이블의 ID
    base_problem_id: Optional[str] = None  # base_problems 테이블의 ID
    problem_type: ProblemTypeEnum = ProblemTypeEnum.BLANK  # 문제 유형
    problem_info: Dict[str, Any] = {}  # 추가 문제 정보 (선택)
    user_code: Optional[str] = None
    user_answers: Optional[Dict[str, str]] = None  # blank: 현재 입력한 답들
    current_blank_index: Optional[int] = None  # blank: 현재 질문하는 빈칸 번호
    attempt_count: int = 0
    hint_level: int = Field(1, ge=1, le=4)
    previous_hints: List[str] = []
    user_level: UserLevelEnum = UserLevelEnum.INTERMEDIATE


class RelatedConcept(BaseModel):
    """Related concept for hint."""
    name: str
    brief: str
    doc_reference: Optional[str] = None


class BlankFocus(BaseModel):
    """Blank-specific hint focus info."""
    blank_index: int
    surrounding_code: Optional[str] = None
    expected_role: Optional[str] = None


class HintAgentResponse(BaseModel):
    """AI-generated hint response."""
    hint_level: int
    hint_content: str
    hint_type: str  # context, operation, range, almost (for blank) / direction, approach, specific, final (general)
    questions: List[str] = []
    related_concept: Optional[RelatedConcept] = None
    encouragement: str = ""
    next_hint_preview: Optional[str] = None
    code_snippet: Optional[str] = None
    common_mistake_check: Optional[str] = None
    # Blank 전용 필드
    blank_focus: Optional[BlankFocus] = None
    wrong_answer_feedback: Optional[str] = None


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


# ============================================================
# Problem Solving Models (문제 풀이 중)
# ============================================================

class ProblemContextModel(BaseModel):
    """현재 풀고 있는 문제 정보."""
    id: str
    name: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    difficulty: str = "medium"
    topics: List[str] = []
    problem_type: str = "blank"  # blank, puzzle, guided

    # 정답 정보
    solution_code: Optional[str] = None
    blanks: Optional[List[Dict[str, Any]]] = None  # blank 문제
    correct_order: Optional[List[int]] = None  # puzzle 문제


class UserProgressModel(BaseModel):
    """사용자 진행 상황."""
    current_code: Optional[str] = None
    filled_blanks: Dict[str, str] = {}  # blank 문제
    arranged_blocks: List[int] = []  # puzzle 문제
    attempt_count: int = 0
    hint_count: int = 0
    last_error: Optional[str] = None


class SolvingRequest(BaseModel):
    """문제 풀이 중 요청."""
    message: str
    problem_context: ProblemContextModel
    user_progress: Optional[UserProgressModel] = None
    conversation_history: List[ChatAgentMessage] = []
    previous_hints: List[str] = []


class SolvingIntentInfo(BaseModel):
    """풀이 중 의도 정보."""
    intent: str  # hint_request, code_review, answer_check, feedback_request, give_up
    confidence: float
    sub_intent: Optional[str] = None  # hint_algorithm, hint_syntax, etc.


class SolvingResponse(BaseModel):
    """문제 풀이 중 응답."""
    message: str
    intent_info: SolvingIntentInfo
    hint_level: Optional[int] = None  # 1~4
    is_correct: Optional[bool] = None
    action_trigger: Optional[str] = None  # hint_provided, code_reviewed, correct_answer, etc.
    action_data: Optional[Dict[str, Any]] = None


# ============================================================
# Feedback Models (문제 풀이 완료 후 피드백)
# ============================================================

class FeedbackProblemInfo(BaseModel):
    """피드백용 문제 정보."""
    title: Optional[str] = None
    difficulty: Optional[str] = None
    topics: List[str] = []


class FeedbackRequest(BaseModel):
    """피드백 요청."""
    user_id: str
    problem_id: str
    problem_type: str = "blank"  # blank, puzzle, guided
    is_correct: bool = True
    solve_time_seconds: int = 0
    hints_used: int = 0
    xp_earned: int = 0
    attempt_count: Optional[int] = None  # 없으면 DB에서 조회
    problem_info: Optional[FeedbackProblemInfo] = None


class FeedbackSummary(BaseModel):
    """피드백 요약."""
    title: str
    highlight: str


class PerformanceAnalysis(BaseModel):
    """성과 분석."""
    time_feedback: str
    hint_feedback: str
    attempt_feedback: str


class TimeComparison(BaseModel):
    """시간 비교."""
    user_time: int
    avg_time: int
    percentile: str


class FeedbackVisualization(BaseModel):
    """피드백 시각화 데이터."""
    efficiency_score: int = 0
    speed_score: int = 0
    understanding_score: int = 0
    time_comparison: Optional[TimeComparison] = None


class NextSteps(BaseModel):
    """다음 단계 제안."""
    recommendation: str
    similar_problems: Optional[str] = None


class FeedbackResponse(BaseModel):
    """피드백 응답."""
    grade: str  # perfect, excellent, good, keep_going, learning
    grade_emoji: str
    grade_message: str
    summary: FeedbackSummary
    performance_analysis: PerformanceAnalysis
    learning_points: List[str] = []
    improvements: List[str] = []
    visualization: FeedbackVisualization
    next_steps: NextSteps
    encouragement: str
