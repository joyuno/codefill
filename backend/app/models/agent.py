"""
Agent Models
Request/Response models for AI agents

출력 형식: data/examples/ 폴더의 JSON 형식과 일치
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from enum import Enum
from uuid import UUID


def _normalize_code_newlines(code: str) -> str:
    """DB에 저장된 코드의 이스케이프된 줄바꿈을 실제 줄바꿈으로 변환"""
    if not code:
        return code
    code = code.replace('\\n', '\n')
    code = code.replace('\\t', '\t')
    return code


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
    # 대기업 코테 관련
    is_corporate_test: Optional[bool] = None
    wants_generation: Optional[bool] = None
    generation_details: Optional[str] = None


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
        """code 또는 solutions에서 코드 추출 (이스케이프 줄바꿈 변환 포함)"""
        if self.code:
            # code가 dict인 경우: {"python": "...", "java": "..."}
            if isinstance(self.code, dict):
                code = self.code.get(target_language) or next(iter(self.code.values()), "")
                return _normalize_code_newlines(code)
            # code가 문자열인 경우
            return _normalize_code_newlines(self.code)
        if self.solutions:
            # 타겟 언어의 솔루션 찾기
            for sol in self.solutions:
                if sol.get("language") == target_language:
                    return _normalize_code_newlines(sol.get("code", ""))
            # 없으면 첫 번째 솔루션
            if self.solutions:
                return _normalize_code_newlines(self.solutions[0].get("code", ""))
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
    id: Union[int, str]  # 정답 순서 (1, 2, 3, ...) or string ID
    code: str
    indentation: int = 0  # 들여쓰기 레벨 (상대적)


class PuzzleProblemResponse(BaseModel):
    """
    Generated puzzle (Parsons) problem.
    형식: {original_id, language, fixed_start?, fixed_end?, blocks[], solution_code?}
    """
    original_id: str
    language: str
    fixed_start: Optional[str] = None  # 고정된 시작 코드
    fixed_end: Optional[str] = None    # 고정된 끝 코드
    blocks: List[PuzzleBlock]          # id 순서가 정답
    solution_code: Optional[str] = None  # 조합된 정답 코드 (indentation 적용)


# --- Guided Problem (새 스키마: 개념 정의, 변수 가이드, 접근법, 맛보기 코드) ---

class VariableGuide(BaseModel):
    """변수 가이드 항목"""
    name: str                 # 변수명
    role: str                 # 역할
    type: str                 # 자료형
    initial_value: str        # 초기값
    why_needed: str           # 왜 필요한지


class VariablesGuideResponse(BaseModel):
    """변수 가이드 전체"""
    total_count: int
    variables: List[VariableGuide]


class GuidedProblemResponse(BaseModel):
    """
    Generated guided (1:1) problem - 새 스키마.

    필드:
    - concept_explanation: 핵심 알고리즘/자료구조 설명 (2-4문장)
    - variables_guide: 변수 정의 (역할, 타입, 초기값)
    - approach_guide: 접근법 가이드 (2-3문장)
    - starter_code: 맛보기 코드 (함수 정의 제외 앞 2줄)
    """
    # 문제 식별
    base_problem_id: Optional[str] = None  # UUID
    language: str

    # 초기 가이드 (LLM 생성)
    concept_explanation: str              # 개념 설명
    variables_guide: VariablesGuideResponse  # 변수 가이드
    approach_guide: str                   # 접근법 가이드
    starter_code: str                     # 맛보기 코드

    # 선택적 필드 (DB 저장 후)
    guided_problem_id: Optional[str] = None  # problems_guided.id

    # 레거시 호환 (점진적 마이그레이션용)
    original_id: Optional[str] = None
    concepts: Optional[List[str]] = None
    flow: Optional[List[str]] = None
    checkpoints: Optional[List[str]] = None


# --- Guided Starter Code (에디터 기반 1대1 대화형) ---

class GuidedStarterRequest(BaseModel):
    """Request to get starter code for guided coding."""
    original_id: str  # base_problems.original_id
    language: LanguageEnum = LanguageEnum.PYTHON


class GuidedStarterResponse(BaseModel):
    """
    Starter code for guided (1:1) coding problem.
    - starter_code가 있으면 그대로 반환
    - 없으면 solutions에서 해당 언어 코드의 앞 2줄 반환
    """
    original_id: str
    language: str
    starter_code: str  # 에디터에 미리 표시할 코드
    has_starter_code: bool = False  # DB에 starter_code가 있었는지 여부


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
    """Generated educational code. (base_problems 테이블 컬럼명과 통일)"""
    title: str
    title_en: Optional[str] = None
    description: str
    solutions: Dict[str, str]  # {"code": "...", "language": "python"} 또는 {"python": "..."}
    input_format: Optional[str] = None
    output_format: Optional[str] = None
    input_output: Optional[Dict[str, List[str]]] = None  # {"inputs": [...], "outputs": [...]}
    constraints: Optional[List[str]] = None
    difficulty: str
    tags: List[str]  # base_problems.tags
    time_complexity: Optional[str] = None
    space_complexity: Optional[str] = None
    original_id: Optional[str] = None
    images: Optional[List[str]] = None


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
    user_code: Optional[str] = None  # guided: 사용자가 작성한 코드
    user_answers: Optional[Dict[str, str]] = None  # blank: 현재 입력한 답들
    current_blank_index: Optional[int] = None  # blank: 현재 질문하는 빈칸 번호
    previous_hints: List[str] = []  # guided: 이전 힌트 (힌트 횟수 계산용)
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
    hint_content: str
    hint_type: str = "hint"  # answer, position, code_line, complete, exhausted 등
    questions: List[str] = []
    encouragement: str = ""
    next_hint_preview: Optional[str] = None
    code_snippet: Optional[str] = None
    # Blank 전용 필드
    blank_focus: Optional[BlankFocus] = None
    # 레거시 호환 (optional)
    hint_level: Optional[int] = None
    related_concept: Optional[RelatedConcept] = None
    common_mistake_check: Optional[str] = None
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
