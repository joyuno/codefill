"""
Admin Models

관리자 기능을 위한 Pydantic 모델 정의
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime
from uuid import UUID


# ============================================================
# 사용자 관리 모델
# ============================================================

class AdminUserListItem(BaseModel):
    """사용자 목록 아이템"""
    id: UUID
    email: str
    name: Optional[str] = None
    role: str = "user"
    avatar_url: Optional[str] = None
    provider: str = "email"
    created_at: datetime
    deleted_at: Optional[datetime] = None
    banned_until: Optional[datetime] = None  # 정지 만료일
    # Stats
    level: int = 1
    total_xp: int = 0
    problems_solved: int = 0


class AdminUserListResponse(BaseModel):
    """사용자 목록 응답"""
    items: List[AdminUserListItem]
    total: int
    page: int
    limit: int
    has_more: bool


class AdminUserBadge(BaseModel):
    """사용자 배지"""
    id: str
    code: str
    name: str
    description: Optional[str] = None
    icon_url: Optional[str] = None
    rarity: str = "common"
    earned_at: datetime


class AdminRecentActivity(BaseModel):
    """최근 활동"""
    id: str
    type: str  # solved, badge
    title: str
    description: Optional[str] = None
    timestamp: datetime
    xp_earned: Optional[int] = None


class AdminUserDetail(BaseModel):
    """사용자 상세 정보"""
    id: UUID
    email: str
    name: Optional[str] = None
    username: Optional[str] = None
    role: str = "user"
    avatar_url: Optional[str] = None
    provider: str = "email"
    subscription_tier: str = "free"
    subscription_expires_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    banned_until: Optional[datetime] = None  # 정지 만료일
    last_activity_date: Optional[str] = None
    # Stats
    level: int = 1
    total_xp: int = 0
    problems_solved: int = 0
    problems_attempted: int = 0
    current_streak: int = 0
    longest_streak: int = 0
    # Problem type breakdown
    blank_solved: int = 0
    puzzle_solved: int = 0
    guided_solved: int = 0
    # Preferences
    preferred_language: Optional[str] = None
    daily_goal: Optional[int] = None
    # Onboarding
    current_status: Optional[str] = None
    learning_goal: Optional[str] = None
    experience_level: Optional[str] = None
    # Badges & Activity
    badges: List[AdminUserBadge] = []
    recent_activity: List[AdminRecentActivity] = []


class UpdateUserRoleRequest(BaseModel):
    """사용자 역할 변경 요청"""
    role: str = Field(..., pattern="^(admin|user)$")


class BanUserRequest(BaseModel):
    """사용자 정지/해제 요청"""
    is_banned: bool
    ban_days: Optional[int] = None  # 정지 일수 (None이면 영구 정지)
    reason: Optional[str] = None


class BanUserResponse(BaseModel):
    """사용자 정지/해제 응답"""
    success: bool
    user_id: UUID
    is_banned: bool
    banned_until: Optional[str] = None  # 정지 만료일 (ISO format)
    message: str


# ============================================================
# 문제 관리 모델
# ============================================================

class AdminProblemListItem(BaseModel):
    """문제 목록 아이템"""
    id: UUID
    original_id: str
    name: str
    difficulty: str
    source: Optional[str] = None
    tags: List[str] = []
    solve_count: int = 0
    like_count: int = 0
    has_blank: bool = False
    has_puzzle: bool = False
    has_guided: bool = False
    created_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None


class AdminProblemListResponse(BaseModel):
    """문제 목록 응답"""
    items: List[AdminProblemListItem]
    total: int
    page: int
    limit: int
    has_more: bool


class BlankVariant(BaseModel):
    """빈칸 채우기 변형"""
    id: UUID
    language: str
    code_template: str
    answers: List[str]
    created_at: Optional[datetime] = None


class PuzzleBlock(BaseModel):
    """퍼즐 블록"""
    id: int
    code: str


class PuzzleVariant(BaseModel):
    """퍼즐 변형"""
    id: UUID
    language: str
    fixed_start: Optional[str] = None
    fixed_end: Optional[str] = None
    blocks: List[Any] = []
    created_at: Optional[datetime] = None


class GuidedVariant(BaseModel):
    """가이드 변형 (DB 스키마에 맞춤)"""
    id: UUID
    language: str
    concept_explanation: str = ""
    variables_guide: List[Any] = []
    approach_guide: str = ""
    starter_code: str = ""
    status: str = "in_progress"
    attempts_count: int = 0
    hints_given: int = 0
    created_at: Optional[datetime] = None


class AdminBaseProblemDetail(BaseModel):
    """문제 상세 정보 (변형 포함)"""
    id: UUID
    original_id: str
    name: str
    question: str
    difficulty: str
    tags: List[str] = []
    source: Optional[str] = None
    url: Optional[str] = None
    time_limit: Optional[str] = None
    memory_limit: Optional[str] = None
    input_output: Optional[Any] = None
    solutions: List[Any] = []
    created_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    # 연결된 변형 문제들
    blanks: List[BlankVariant] = []
    puzzles: List[PuzzleVariant] = []
    guideds: List[GuidedVariant] = []


class UpdateBaseProblemRequest(BaseModel):
    """원본 문제 수정 요청"""
    name: Optional[str] = None
    question: Optional[str] = None
    difficulty: Optional[str] = None
    tags: Optional[List[str]] = None
    source: Optional[str] = None
    url: Optional[str] = None
    time_limit: Optional[str] = None
    memory_limit: Optional[str] = None
    input_output: Optional[Any] = None
    solutions: Optional[List[Any]] = None


# ============================================================
# 문제 생성 모델
# ============================================================

class SolutionInput(BaseModel):
    """솔루션 입력"""
    language: str
    code: str


class CreateBaseProblemRequest(BaseModel):
    """원본 문제 생성 요청"""
    original_id: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=255)
    question: str = Field(..., min_length=1)
    difficulty: str = Field(default="medium", pattern="^(easy|medium|hard)$")
    tags: List[str] = []
    source: Optional[str] = None
    url: Optional[str] = None
    time_limit: Optional[str] = None
    memory_limit: Optional[str] = None
    input_output: Optional[Any] = None
    solutions: List[SolutionInput] = []


class CreateBlankProblemRequest(BaseModel):
    """빈칸 채우기 문제 생성 요청"""
    language: str = Field(..., min_length=1)
    code_template: str = Field(..., min_length=1)  # _0_, _1_ 형식 포함
    answers: List[str] = Field(..., min_items=1)


class PuzzleBlockInput(BaseModel):
    """퍼즐 블록 입력"""
    id: int
    code: str


class CreatePuzzleProblemRequest(BaseModel):
    """퍼즐 문제 생성 요청"""
    language: str = Field(..., min_length=1)
    fixed_start: Optional[str] = None
    fixed_end: Optional[str] = None
    blocks: List[PuzzleBlockInput] = Field(..., min_items=1)


class VariableGuideItem(BaseModel):
    """변수 가이드 아이템"""
    name: str
    role: str
    type: str
    initial: Optional[str] = None


class CreateGuidedProblemRequest(BaseModel):
    """가이드 문제 생성 요청 (DB 스키마에 맞춤)"""
    language: str = Field(default="python", min_length=1)
    concept_explanation: str = Field(..., min_length=1)
    variables_guide: List[VariableGuideItem] = []
    approach_guide: str = Field(..., min_length=1)
    starter_code: str = Field(..., min_length=1)


class CreateProblemResponse(BaseModel):
    """문제 생성 응답"""
    success: bool
    id: UUID
    original_id: str
    message: str


# ============================================================
# 대시보드 통계 모델
# ============================================================

class AdminDashboardStats(BaseModel):
    """관리자 대시보드 통계"""
    total_users: int = 0
    active_users_today: int = 0
    total_problems: int = 0
    total_submissions: int = 0
    new_users_this_week: int = 0


# ============================================================
# 변형 문제 수정/삭제 모델
# ============================================================

class UpdateBlankProblemRequest(BaseModel):
    """빈칸 문제 수정 요청"""
    language: Optional[str] = None
    code_template: Optional[str] = None
    answers: Optional[List[str]] = None


class UpdatePuzzleProblemRequest(BaseModel):
    """퍼즐 문제 수정 요청"""
    language: Optional[str] = None
    fixed_start: Optional[str] = None
    fixed_end: Optional[str] = None
    blocks: Optional[List[PuzzleBlockInput]] = None


class UpdateGuidedProblemRequest(BaseModel):
    """가이드 문제 수정 요청"""
    language: Optional[str] = None
    concept_explanation: Optional[str] = None
    variables_guide: Optional[List[VariableGuideItem]] = None
    approach_guide: Optional[str] = None
    starter_code: Optional[str] = None


class VariantResponse(BaseModel):
    """변형 문제 작업 응답"""
    success: bool
    message: str
