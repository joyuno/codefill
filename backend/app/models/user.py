from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum
from uuid import UUID


class SubscriptionPlan(str, Enum):
    """Subscription plans."""
    FREE = "free"
    PRO = "pro"
    MAX = "max"


class BadgeRarity(str, Enum):
    """Badge rarity levels (5 tiers)."""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


class Badge(BaseModel):
    """Badge model."""
    id: UUID
    code: str
    name: str
    description: Optional[str] = None
    icon_url: Optional[str] = None
    rarity: BadgeRarity = BadgeRarity.COMMON
    earned_at: Optional[datetime] = None


class UserStats(BaseModel):
    """User statistics model."""
    total_xp: int = 0
    level: int = 1
    problems_solved: int = 0
    problems_attempted: int = 0
    blank_solved: int = 0
    bug_solved: int = 0
    output_solved: int = 0
    refactor_solved: int = 0
    current_streak: int = 0
    longest_streak: int = 0
    seeds: int = 0


class UserPreferences(BaseModel):
    """User preferences model."""
    preferred_language: str = "javascript"
    preferred_difficulty: str = "medium"
    daily_goal: int = 5
    email_notifications: bool = True
    push_notifications: bool = True
    review_reminders: bool = True
    theme: str = "dark"
    editor_font_size: int = 14


class User(BaseModel):
    """User model."""
    id: UUID
    email: str
    name: str
    avatar_url: Optional[str] = None
    provider: str = "email"
    # Onboarding data
    current_status: Optional[str] = None        # student, job_seeker, employed, career_change
    learning_goal: Optional[str] = None         # big_tech, mid_startup, skill_up, unknown
    experience_level: Optional[str] = None      # beginner, elementary, intermediate, advanced, unknown
    strong_algorithms: Optional[List[str]] = None
    solved_ac_id: Optional[str] = None
    desired_job: Optional[str] = None           # 희망 직무 (자유 텍스트)
    # Timestamps
    created_at: datetime
    updated_at: datetime


class UserProfile(BaseModel):
    """Full user profile with stats and badges."""
    user: User
    stats: UserStats
    preferences: UserPreferences
    badges: List[Badge] = []
    subscription: SubscriptionPlan = SubscriptionPlan.FREE


class UpdateUserRequest(BaseModel):
    """Request model for updating user info."""
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    avatar_url: Optional[str] = None
    # Onboarding fields
    current_status: Optional[str] = None
    learning_goal: Optional[str] = None
    experience_level: Optional[str] = None
    strong_algorithms: Optional[List[str]] = None
    solved_ac_id: Optional[str] = None
    desired_job: Optional[str] = Field(None, max_length=20)


class UpdatePreferencesRequest(BaseModel):
    """Request model for updating preferences."""
    preferred_language: Optional[str] = None
    preferred_difficulty: Optional[str] = None
    daily_goal: Optional[int] = Field(None, ge=1, le=50)
    email_notifications: Optional[bool] = None
    push_notifications: Optional[bool] = None
    review_reminders: Optional[bool] = None
    theme: Optional[str] = None
    editor_font_size: Optional[int] = Field(None, ge=10, le=24)


class DailyActivity(BaseModel):
    """Daily activity record."""
    date: str  # YYYY-MM-DD
    problems_solved: int = 0
    xp_earned: int = 0
    time_spent: int = 0  # seconds
    blank_count: int = 0
    bug_count: int = 0
    output_count: int = 0
    refactor_count: int = 0


class RecentActivityType(str, Enum):
    """Recent activity types."""
    SOLVED = "solved"
    BADGE = "badge"
    STREAK = "streak"
    LEVELUP = "levelup"


class RecentActivity(BaseModel):
    """Recent activity record for mypage."""
    id: str
    type: RecentActivityType
    title: str
    description: str
    timestamp: datetime
    xp_gained: Optional[int] = None


class MypageProfile(BaseModel):
    """Flattened user profile for mypage."""
    id: str
    email: str
    username: str
    avatarShape: str = "hexagon"
    avatarColor: str = "hsl(142, 71%, 45%)"
    level: int = 1
    currentXP: int = 0
    requiredXP: int = 100
    totalXP: int = 0
    solvedCount: int = 0
    streak: int = 0
    maxStreak: int = 0
    joinedAt: str
    subscription: str = "free"


class MypageStats(BaseModel):
    """User stats for mypage."""
    totalSolved: int = 0
    solvedByDifficulty: dict = {"easy": 0, "medium": 0, "hard": 0}
    solvedByType: dict = {"blank": 0, "puzzle": 0}
    currentStreak: int = 0
    maxStreak: int = 0
    totalXP: int = 0
    level: int = 1


class MypageBadge(BaseModel):
    """Badge format for mypage."""
    id: str
    name: str
    icon: str
    icon_url: Optional[str] = None
    description: str
    earnedAt: str
    rarity: str = "common"


class SolvedAcProfileSimple(BaseModel):
    """Simplified solved.ac profile for mypage."""
    handle: str
    tier: int = 0
    rating: int = 0
    solved_count: int = 0
    last_synced_at: str


class MypageAllResponse(BaseModel):
    """통합 마이페이지 응답 - 한 번의 API 호출로 모든 데이터 반환."""
    profile: MypageProfile
    stats: MypageStats
    badges: List[MypageBadge]
    recentActivity: List[RecentActivity]
    solvedAc: Optional[SolvedAcProfileSimple] = None


# =====================================================
# Nickname Change Models
# =====================================================

class ChangeNicknameRequest(BaseModel):
    """Request model for nickname change."""
    new_nickname: str = Field(..., min_length=2, max_length=50)


# =====================================================
# Date Activity Models (잔디 클릭 시 상세)
# =====================================================

class SolvedProblem(BaseModel):
    """특정 날짜에 푼 문제."""
    id: str
    name: str
    difficulty: str
    problem_type: str
    xp_earned: int
    solved_at: datetime


class DateActivityDetail(BaseModel):
    """특정 날짜의 활동 상세."""
    date: str
    problems_solved: int
    xp_earned: int
    problems: List[SolvedProblem]


class ChangeNicknameResponse(BaseModel):
    """Response model for nickname change."""
    success: bool
    message: str
    next_change_available_at: Optional[datetime] = None


# =====================================================
# Public Profile Models (공개 프로필)
# =====================================================

class PublicProfile(BaseModel):
    """공개 프로필 기본 정보."""
    id: str
    username: str
    avatarUrl: Optional[str] = None  # 실제 프로필 이미지 URL
    avatarColor: str = "hsl(142, 71%, 45%)"  # 폴백 배경색
    level: int = 1
    currentXP: int = 0
    requiredXP: int = 100
    totalXP: int = 0
    solvedCount: int = 0
    streak: int = 0
    joinedAt: str


class PublicStats(BaseModel):
    """공개 통계."""
    totalSolved: int = 0
    solvedByDifficulty: dict = {"easy": 0, "medium": 0, "hard": 0}
    solvedByType: dict = {"blank": 0, "puzzle": 0}
    currentStreak: int = 0
    maxStreak: int = 0
    totalXP: int = 0
    level: int = 1


class PublicFarmCharacter(BaseModel):
    """공개 농장 캐릭터 정보."""
    name: str
    hair: str
    hairColor: str
    face: str
    outfit: str
    outfitColor: str
    farmName: str


class PublicFarmSlot(BaseModel):
    """공개 농장 슬롯 정보."""
    slotIndex: int
    cropType: Optional[str] = None
    stage: int = 0
    isReady: bool = False


class PublicFarm(BaseModel):
    """공개 농장 미니맵 데이터."""
    hasCharacter: bool = False
    character: Optional[PublicFarmCharacter] = None
    farmLevel: int = 1
    gold: int = 0
    slots: List[PublicFarmSlot] = []


class PublicBadge(BaseModel):
    """공개 뱃지."""
    id: str
    name: str
    icon: str
    description: str
    rarity: str = "common"
