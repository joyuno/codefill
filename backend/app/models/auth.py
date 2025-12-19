from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from enum import Enum


class ExperienceLevel(str, Enum):
    """User experience levels."""
    NON_MAJOR = "non_major"           # 비전공
    LESS_THAN_6_MONTHS = "lt_6m"      # 6개월 미만
    SIX_TO_24_MONTHS = "6m_2y"        # 6개월~2년
    MORE_THAN_2_YEARS = "gt_2y"       # 2년 이상


class LearningGoal(str, Enum):
    """User learning goals."""
    CODING_TEST = "coding_test"       # 코테 준비
    WORK_SKILLS = "work_skills"       # 실무 역량
    FRAMEWORK = "framework"           # 프레임워크 학습
    FUN = "fun"                       # 재미


class SignupRequest(BaseModel):
    """Request model for user signup."""
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    name: str = Field(..., min_length=2, max_length=50)
    experience_level: Optional[ExperienceLevel] = None
    learning_goal: Optional[LearningGoal] = None
    preferred_language: Optional[str] = Field(default="javascript")
    preferred_framework: Optional[str] = None


class LoginRequest(BaseModel):
    """Request model for user login."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Response model for authentication tokens."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    """Request model for token refresh."""
    refresh_token: str


class PasswordResetRequest(BaseModel):
    """Request model for password reset."""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Request model for password reset confirmation."""
    token: str
    new_password: str = Field(..., min_length=8)


class AuthResponse(BaseModel):
    """Generic auth response."""
    success: bool
    message: str
    data: Optional[dict] = None
