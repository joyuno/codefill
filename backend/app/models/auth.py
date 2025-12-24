from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from enum import Enum


# =====================================================
# Legacy Enums (for backwards compatibility)
# =====================================================

class ExperienceLevel(str, Enum):
    """User experience levels (legacy)."""
    NON_MAJOR = "non_major"
    LESS_THAN_6_MONTHS = "lt_6m"
    SIX_TO_24_MONTHS = "6m_2y"
    MORE_THAN_2_YEARS = "gt_2y"


class LearningGoal(str, Enum):
    """User learning goals (legacy)."""
    CODING_TEST = "coding_test"
    WORK_SKILLS = "work_skills"
    FRAMEWORK = "framework"
    FUN = "fun"


# =====================================================
# New Onboarding Enums (matching frontend)
# =====================================================

class CurrentStatus(str, Enum):
    """User current status."""
    STUDENT = "student"               # 학생
    JOB_SEEKER = "job_seeker"         # 취준생
    EMPLOYED = "employed"             # 현직자
    CAREER_CHANGE = "career_change"   # 전환


class OnboardingGoal(str, Enum):
    """User learning goal from onboarding."""
    BIG_TECH = "big_tech"             # 대기업 코딩테스트
    MID_STARTUP = "mid_startup"       # 중견/스타트업 코딩테스트
    SKILL_UP = "skill_up"             # 코딩 실력 향상
    UNKNOWN = "unknown"               # 아직 잘 모르겠어요


class OnboardingLevel(str, Enum):
    """User coding test experience level."""
    BEGINNER = "beginner"             # 입문 (거의 안 풀어봄)
    ELEMENTARY = "elementary"         # 초급 (브론즈~실버)
    INTERMEDIATE = "intermediate"     # 중급 (골드)
    ADVANCED = "advanced"             # 고급 (플래티넘+)
    UNKNOWN = "unknown"               # 잘 모르겠어요


class OnboardingData(BaseModel):
    """Onboarding data collected during signup."""
    status: Optional[CurrentStatus] = None
    goal: Optional[OnboardingGoal] = None
    level: Optional[OnboardingLevel] = None
    solved_ac_id: Optional[str] = None
    strong_algorithms: Optional[List[str]] = None
    desired_job: Optional[str] = None  # 희망 직무 (자유 텍스트)


class SignupRequest(BaseModel):
    """Request model for user signup."""
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    name: str = Field(..., min_length=2, max_length=50)
    # Legacy fields (for backwards compatibility)
    experience_level: Optional[ExperienceLevel] = None
    learning_goal: Optional[LearningGoal] = None
    preferred_language: Optional[str] = Field(default="javascript")
    preferred_framework: Optional[str] = None
    # New onboarding data
    onboarding_data: Optional[OnboardingData] = None


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


# =====================================================
# Duplicate Check Models
# =====================================================

class CheckEmailRequest(BaseModel):
    """Request model for email duplicate check."""
    email: EmailStr


class CheckNicknameRequest(BaseModel):
    """Request model for nickname duplicate check."""
    nickname: str = Field(..., min_length=2, max_length=50)


class CheckResponse(BaseModel):
    """Response model for duplicate checks."""
    available: bool
    message: str


# =====================================================
# Password Change Models
# =====================================================

class ChangePasswordRequest(BaseModel):
    """Request model for password change."""
    current_password: str
    new_password: str = Field(..., min_length=8)


# =====================================================
# Account Withdrawal Models
# =====================================================

class WithdrawRequest(BaseModel):
    """Request model for account withdrawal (회원탈퇴)."""
    confirmation: str = Field(
        ...,
        description="User must type '탈퇴합니다' to confirm withdrawal"
    )
    # TODO: 이메일 인증 토큰 추가 (나중에 구현)
    # email_verification_token: Optional[str] = None


# =====================================================
# Account Recovery Models
# =====================================================

class RecoveryRequiredResponse(BaseModel):
    """Response when account recovery confirmation is needed."""
    recovery_required: bool = True
    message: str
    email: str
    deleted_at: str
    days_remaining: int


class RecoverAccountRequest(BaseModel):
    """Request model for account recovery with login."""
    email: EmailStr
    password: str


class RecoverOAuthRequest(BaseModel):
    """Request model for OAuth account recovery."""
    provider: str = Field(..., description="OAuth provider (kakao, google)")
    provider_id: str = Field(..., description="Provider user ID")
