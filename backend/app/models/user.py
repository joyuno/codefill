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
    """Badge rarity levels."""
    COMMON = "common"
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
