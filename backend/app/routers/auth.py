from fastapi import APIRouter, HTTPException, Depends, status, Header
from fastapi.responses import RedirectResponse
from typing import Optional
import httpx
import secrets
import uuid

from ..database import get_db
from ..config import get_settings
from ..models.auth import (
    SignupRequest,
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
    AuthResponse,
    CheckEmailRequest,
    CheckNicknameRequest,
    CheckResponse,
    ChangePasswordRequest,
    WithdrawRequest,
    RecoveryRequiredResponse,
    RecoverAccountRequest,
    RecoverOAuthRequest,
)

router = APIRouter()
settings = get_settings()

REJOIN_RESTRICTION_DAYS = 30  # 재가입 제한 일수

KAKAO_AUTH_URL = "https://kauth.kakao.com/oauth/authorize"
KAKAO_TOKEN_URL = "https://kauth.kakao.com/oauth/token"
KAKAO_USER_INFO_URL = "https://kapi.kakao.com/v2/user/me"

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USER_INFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

GITHUB_AUTH_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_USER_URL = "https://api.github.com/user"
GITHUB_EMAILS_URL = "https://api.github.com/user/emails"


@router.post("/signup", response_model=TokenResponse)
async def signup(request: SignupRequest, db=Depends(get_db)):
    """
    Register a new user with email and password.

    Creates user account with:
    - Basic info (email, name, password)
    - Optional profile info (experience, goal, preferences)
    - Initial user_stats record (via database trigger)
    - Initial user_preferences record (via database trigger)

    Returns JWT tokens for automatic login after signup.
    """
    from ..utils.security import hash_password, create_access_token, create_refresh_token

    try:
        email = request.email.lower()

        # Check if email already exists
        existing = db.table("users").select("id").ilike("email", email).is_("deleted_at", "null").execute()
        if existing.data and len(existing.data) > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Generate user ID and hash password
        user_id = str(uuid.uuid4())
        password_hash = hash_password(request.password)

        # Build user data for users table
        user_data = {
            "id": user_id,
            "email": email,
            "name": request.name,
            "password_hash": password_hash,
            "provider": "email",
        }

        # Add onboarding data if provided
        if request.onboarding_data:
            onboarding = request.onboarding_data
            if onboarding.status:
                user_data["current_status"] = onboarding.status.value
            if onboarding.goal:
                user_data["learning_goal"] = onboarding.goal.value
            if onboarding.level:
                user_data["experience_level"] = onboarding.level.value
            if onboarding.strong_algorithms:
                user_data["strong_algorithms"] = onboarding.strong_algorithms
            if onboarding.solved_ac_id:
                user_data["solved_ac_id"] = onboarding.solved_ac_id
            if onboarding.desired_job:
                user_data["desired_job"] = onboarding.desired_job

        # Create user record
        db.table("users").insert(user_data).execute()

        # Note: user_stats and user_preferences are created by database trigger
        # handle_new_user() - no need to create them manually

        # Create solved_ac_profiles record if solved_ac_id is provided
        if request.onboarding_data and request.onboarding_data.solved_ac_id:
            try:
                # Fetch profile from solved.ac API
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"https://solved.ac/api/v3/user/show",
                        params={"handle": request.onboarding_data.solved_ac_id},
                        timeout=10.0
                    )
                    if response.status_code == 200:
                        profile = response.json()
                        actual_handle = profile.get("handle", request.onboarding_data.solved_ac_id)

                        # 다른 유저가 이미 이 handle을 사용 중인지 확인
                        duplicate_check = db.table("solved_ac_profiles")\
                            .select("user_id")\
                            .eq("handle", actual_handle)\
                            .execute()

                        if not (duplicate_check.data and len(duplicate_check.data) > 0):
                            # 중복이 없을 때만 INSERT
                            from datetime import datetime
                            now = datetime.utcnow().isoformat()
                            db.table("solved_ac_profiles").insert({
                                "user_id": user_id,
                                "handle": actual_handle,
                                "tier": profile.get("tier", 0),
                                "rating": profile.get("rating", 0),
                                "solved_count": profile.get("solvedCount", 0),
                                "max_streak": profile.get("maxStreak", 0),
                                "last_synced_at": now,
                            }).execute()
            except Exception as e:
                # Don't fail signup if solved.ac integration fails
                print(f"Failed to create solved_ac_profile: {e}")

        # Update preferences if provided
        if request.preferred_language:
            db.table("user_preferences").update({
                "preferred_language": request.preferred_language,
            }).eq("user_id", user_id).execute()

        # Generate JWT tokens for automatic login
        access_token = create_access_token(user_id)
        refresh_token = create_refresh_token(user_id)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60
        )

    except HTTPException:
        raise
    except Exception as e:
        error_message = str(e)
        if "duplicate" in error_message.lower() or "already" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Signup failed: {error_message}"
        )


@router.post("/login")
async def login(request: LoginRequest, db=Depends(get_db)):
    """
    Authenticate user with email and password.
    Uses bcrypt password verification and returns JWT tokens.

    If user is soft-deleted (within 30 days), returns recovery_required response.
    User must confirm recovery via /auth/recover endpoint.
    """
    from ..utils.security import verify_password, create_access_token, create_refresh_token
    from datetime import datetime, timedelta, timezone

    email = request.email.lower()

    try:
        # 1. First, check for active users (deleted_at IS NULL)
        result = db.table("users").select("id, password_hash").ilike("email", email).is_("deleted_at", "null").execute()

        if result.data and len(result.data) > 0:
            user = result.data[0]

            # Verify password
            if not user.get("password_hash") or not verify_password(request.password, user["password_hash"]):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="이메일 또는 비밀번호가 올바르지 않습니다."
                )

            # Generate JWT tokens (normal login)
            access_token = create_access_token(user["id"])
            refresh_token = create_refresh_token(user["id"])

            return TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
                expires_in=settings.access_token_expire_minutes * 60,
            )

        # 2. Check for soft-deleted users within 30 days (recovery eligible)
        deleted_result = db.table("users").select("id, email, password_hash, deleted_at").ilike("email", email).not_.is_("deleted_at", "null").order("deleted_at", desc=True).limit(1).execute()

        if deleted_result.data and len(deleted_result.data) > 0:
            deleted_user = deleted_result.data[0]
            deleted_at_str = deleted_user.get("deleted_at")

            if deleted_at_str:
                if isinstance(deleted_at_str, str):
                    deleted_at = datetime.fromisoformat(deleted_at_str.replace('Z', '+00:00'))
                else:
                    deleted_at = deleted_at_str

                recovery_deadline = deleted_at + timedelta(days=REJOIN_RESTRICTION_DAYS)
                now = datetime.now(timezone.utc)

                if now < recovery_deadline:
                    # Verify password before offering recovery
                    if not deleted_user.get("password_hash") or not verify_password(request.password, deleted_user["password_hash"]):
                        raise HTTPException(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="이메일 또는 비밀번호가 올바르지 않습니다."
                        )

                    # Return recovery required response (don't auto-recover)
                    days_remaining = (recovery_deadline - now).days + 1
                    return RecoveryRequiredResponse(
                        recovery_required=True,
                        message="탈퇴한 계정입니다. 계정을 복구하시겠습니까?",
                        email=deleted_user.get("email", email),
                        deleted_at=deleted_at_str if isinstance(deleted_at_str, str) else deleted_at.isoformat(),
                        days_remaining=days_remaining,
                    )

        # No user found
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 올바르지 않습니다."
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )


@router.post("/recover", response_model=TokenResponse)
async def recover_account(request: RecoverAccountRequest, db=Depends(get_db)):
    """
    Recover a soft-deleted account and login.
    Called after user confirms they want to recover their account.
    """
    from ..utils.security import verify_password, create_access_token, create_refresh_token
    from datetime import datetime, timedelta, timezone

    email = request.email.lower()

    try:
        # Find soft-deleted user
        deleted_result = db.table("users").select("id, password_hash, deleted_at").ilike("email", email).not_.is_("deleted_at", "null").order("deleted_at", desc=True).limit(1).execute()

        if not deleted_result.data or len(deleted_result.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="복구할 계정을 찾을 수 없습니다."
            )

        deleted_user = deleted_result.data[0]
        deleted_at_str = deleted_user.get("deleted_at")

        # Check if within recovery period
        if deleted_at_str:
            if isinstance(deleted_at_str, str):
                deleted_at = datetime.fromisoformat(deleted_at_str.replace('Z', '+00:00'))
            else:
                deleted_at = deleted_at_str

            recovery_deadline = deleted_at + timedelta(days=REJOIN_RESTRICTION_DAYS)
            now = datetime.now(timezone.utc)

            if now >= recovery_deadline:
                raise HTTPException(
                    status_code=status.HTTP_410_GONE,
                    detail="복구 가능 기간(30일)이 지났습니다."
                )

        # Verify password
        if not deleted_user.get("password_hash") or not verify_password(request.password, deleted_user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="비밀번호가 올바르지 않습니다."
            )

        # Recover the account
        db.table("users").update({"deleted_at": None}).eq("id", deleted_user["id"]).execute()

        # Generate JWT tokens
        access_token = create_access_token(deleted_user["id"])
        refresh_token = create_refresh_token(deleted_user["id"])

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Recovery failed: {str(e)}"
        )


@router.post("/recover-oauth", response_model=TokenResponse)
async def recover_oauth_account(
    request: RecoverOAuthRequest,
    db=Depends(get_db)
):
    """
    Recover a soft-deleted OAuth account.
    Called after user confirms they want to recover via OAuth provider.
    No password needed - OAuth provider already verified identity.
    """
    from ..utils.security import create_access_token, create_refresh_token
    from datetime import datetime, timedelta, timezone

    provider = request.provider
    provider_id = request.provider_id

    try:
        # Find soft-deleted user by provider
        deleted_result = db.table("users").select("id, deleted_at").eq("provider", provider).eq("provider_id", provider_id).not_.is_("deleted_at", "null").order("deleted_at", desc=True).limit(1).execute()

        if not deleted_result.data or len(deleted_result.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="복구할 계정을 찾을 수 없습니다."
            )

        deleted_user = deleted_result.data[0]
        deleted_at_str = deleted_user.get("deleted_at")

        # Check if within recovery period
        if deleted_at_str:
            if isinstance(deleted_at_str, str):
                deleted_at = datetime.fromisoformat(deleted_at_str.replace('Z', '+00:00'))
            else:
                deleted_at = deleted_at_str

            recovery_deadline = deleted_at + timedelta(days=REJOIN_RESTRICTION_DAYS)
            now = datetime.now(timezone.utc)

            if now >= recovery_deadline:
                raise HTTPException(
                    status_code=status.HTTP_410_GONE,
                    detail="복구 가능 기간(30일)이 지났습니다."
                )

        # Recover the account
        db.table("users").update({"deleted_at": None}).eq("id", deleted_user["id"]).execute()

        # Generate JWT tokens
        access_token = create_access_token(deleted_user["id"])
        refresh_token = create_refresh_token(deleted_user["id"])

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Recovery failed: {str(e)}"
        )


@router.post("/logout", response_model=AuthResponse)
async def logout():
    """
    Logout the current user.
    Client-side handles token deletion from localStorage.
    """
    return AuthResponse(
        success=True,
        message="Logged out successfully"
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest):
    """
    Refresh access token using refresh token.
    Uses JWT verification and generates new token pair.
    """
    from ..utils.security import verify_token, create_access_token, create_refresh_token

    payload = verify_token(request.refresh_token)
    if payload:
        token_type = payload.get("type")
        user_id = payload.get("sub")

        if token_type == "refresh" and user_id:
            new_access_token = create_access_token(user_id)
            new_refresh_token = create_refresh_token(user_id)

            return TokenResponse(
                access_token=new_access_token,
                refresh_token=new_refresh_token,
                token_type="bearer",
                expires_in=settings.access_token_expire_minutes * 60,
            )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired refresh token"
    )


@router.post("/password/reset", response_model=AuthResponse)
async def request_password_reset(request: PasswordResetRequest):
    """
    Request password reset email.
    TODO: Implement email sending functionality.
    """
    # For now, always return success to not reveal if email exists
    return AuthResponse(
        success=True,
        message="Password reset email sent if account exists"
    )


@router.put("/password/reset", response_model=AuthResponse)
async def confirm_password_reset(request: PasswordResetConfirm):
    """
    Confirm password reset with token.
    TODO: Implement token verification and password update.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Password reset is not yet implemented"
    )


# =====================================================
# Duplicate Check Endpoints
# =====================================================

@router.post("/check-email", response_model=CheckResponse)
async def check_email_availability(request: CheckEmailRequest, db=Depends(get_db)):
    """
    Check if email is available for registration.
    - Active user: "이미 사용 중인 이메일"
    - Withdrawn user (within 30 days): "로그인하여 계정 복구" 안내
    - Withdrawn user (after 30 days) or no user: "사용 가능한 이메일"
    """
    from datetime import datetime, timedelta, timezone

    email = request.email.lower()

    # 1. Check active users (deleted_at is NULL)
    active_user = db.table("users").select("id").ilike("email", email).is_("deleted_at", "null").execute()
    if active_user.data and len(active_user.data) > 0:
        return CheckResponse(available=False, message="이미 사용 중인 이메일입니다.")

    # 2. Check withdrawn users (deleted_at is NOT NULL, within 30 days)
    withdrawn_user = db.table("users").select("id, deleted_at").ilike("email", email).not_.is_("deleted_at", "null").order("deleted_at", desc=True).limit(1).execute()
    if withdrawn_user.data and len(withdrawn_user.data) > 0:
        deleted_at_str = withdrawn_user.data[0].get("deleted_at")
        if deleted_at_str:
            if isinstance(deleted_at_str, str):
                deleted_at = datetime.fromisoformat(deleted_at_str.replace('Z', '+00:00'))
            else:
                deleted_at = deleted_at_str

            recovery_deadline = deleted_at + timedelta(days=REJOIN_RESTRICTION_DAYS)
            now = datetime.now(timezone.utc)

            if now < recovery_deadline:
                # User can recover their account by logging in
                return CheckResponse(
                    available=False,
                    message="탈퇴 처리 중인 계정입니다. 로그인하시면 계정을 복구할 수 있습니다."
                )
            # else: 30 days passed, user data will be deleted, can signup fresh

    return CheckResponse(available=True, message="사용 가능한 이메일입니다.")


@router.post("/check-nickname", response_model=CheckResponse)
async def check_nickname_availability(request: CheckNicknameRequest, db=Depends(get_db)):
    """
    Check if nickname is available.
    """
    nickname = request.nickname.strip()

    # Check if nickname already exists (case-insensitive, exclude soft-deleted users)
    existing = db.table("users").select("id").ilike("name", nickname).is_("deleted_at", "null").execute()
    if existing.data and len(existing.data) > 0:
        return CheckResponse(available=False, message="이미 사용 중인 닉네임입니다.")

    return CheckResponse(available=True, message="사용 가능한 닉네임입니다.")


# =====================================================
# Password Change Endpoint
# =====================================================

@router.put("/password/change", response_model=AuthResponse)
async def change_password(
    request: ChangePasswordRequest,
    authorization: str = Header(...),
    db=Depends(get_db)
):
    """
    Change password for email/password users.
    OAuth users (Kakao, Google) cannot use this endpoint.
    """
    from ..utils.security import verify_token, verify_password, hash_password

    # Get token from Authorization header
    token = authorization.replace("Bearer ", "") if authorization else None
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증이 필요합니다."
        )

    # Verify JWT token
    payload = verify_token(token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰입니다."
        )

    user_id = payload.get("sub")

    # Get user to check provider and password_hash
    user_result = db.table("users").select("provider, password_hash").eq("id", user_id).single().execute()
    if not user_result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다."
        )

    user = user_result.data

    if user["provider"] != "email":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="소셜 로그인 사용자는 비밀번호를 변경할 수 없습니다."
        )

    if not user.get("password_hash"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="비밀번호를 변경할 수 없습니다."
        )

    # Verify current password
    if not verify_password(request.current_password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="현재 비밀번호가 올바르지 않습니다."
        )

    # Update password_hash
    new_hash = hash_password(request.new_password)
    db.table("users").update({"password_hash": new_hash}).eq("id", user_id).execute()
    return AuthResponse(success=True, message="비밀번호가 변경되었습니다.")


# =====================================================
# Account Withdrawal Endpoint (회원탈퇴)
# =====================================================

@router.delete("/withdraw", response_model=AuthResponse)
async def withdraw_account(
    request: WithdrawRequest,
    authorization: str = Header(...),
    db=Depends(get_db)
):
    """
    회원탈퇴 (Soft Delete).

    - 일반 가입자, 소셜 가입자 모두 동일하게 탈퇴 가능
    - '탈퇴합니다' 확인 문구 입력 필요
    - TODO: 이메일 인증 기능 추가 예정

    Soft delete 방식:
    - users.deleted_at에 현재 시간 설정
    - 관련 데이터는 FK 설정에 따라 자동 처리됨
    """
    from datetime import datetime, timezone
    from ..utils.security import verify_token

    # Verify confirmation text
    if request.confirmation != "탈퇴합니다":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="확인 문구가 일치하지 않습니다. '탈퇴합니다'를 정확히 입력해주세요."
        )

    # Get token from Authorization header
    token = authorization.replace("Bearer ", "") if authorization else None
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증이 필요합니다."
        )

    # Verify JWT token
    payload = verify_token(token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰입니다."
        )

    user_id = payload.get("sub")

    # Check if user exists
    user_result = db.table("users").select("id, email").eq("id", user_id).is_("deleted_at", "null").single().execute()
    if not user_result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다."
        )

    # TODO: 이메일 인증 검증 (나중에 구현)
    # if request.email_verification_token:
    #     verify_email_token(request.email_verification_token, user_result.data["email"])

    # Soft delete: Set deleted_at timestamp
    now = datetime.now(timezone.utc)
    db.table("users").update({
        "deleted_at": now.isoformat()
    }).eq("id", user_id).execute()

    return AuthResponse(
        success=True,
        message="회원탈퇴가 완료되었습니다. 30일 이내에 로그인하시면 계정을 복구할 수 있습니다. 30일 후에는 모든 데이터가 영구 삭제됩니다."
    )


# =====================================================
# OAuth Helper Functions
# =====================================================

def _check_withdrawn_user_for_recovery(db, email: str = None, provider: str = None, provider_id: str = None) -> Optional[dict]:
    """
    Check if user is withdrawn and within recovery period (30 days).
    Does NOT auto-recover - returns info for confirmation page.

    Returns:
        dict with user_id, days_remaining if recovery eligible, None otherwise
    """
    from datetime import datetime, timedelta, timezone

    # Check by provider_id first (for returning social users)
    if provider and provider_id:
        withdrawn = db.table("users").select("id, email, deleted_at").eq("provider", provider).eq("provider_id", provider_id).not_.is_("deleted_at", "null").order("deleted_at", desc=True).limit(1).execute()
        if withdrawn.data and len(withdrawn.data) > 0:
            deleted_at_str = withdrawn.data[0].get("deleted_at")
            user_id = withdrawn.data[0].get("id")
            user_email = withdrawn.data[0].get("email")
            if deleted_at_str and user_id:
                if isinstance(deleted_at_str, str):
                    deleted_at = datetime.fromisoformat(deleted_at_str.replace('Z', '+00:00'))
                else:
                    deleted_at = deleted_at_str
                recovery_deadline = deleted_at + timedelta(days=REJOIN_RESTRICTION_DAYS)
                now = datetime.now(timezone.utc)
                if now < recovery_deadline:
                    days_remaining = (recovery_deadline - now).days + 1
                    return {
                        "user_id": user_id,
                        "email": user_email,
                        "days_remaining": days_remaining,
                        "provider": provider,
                        "provider_id": provider_id,
                    }

    # Check by email (for email-linked accounts)
    if email:
        withdrawn = db.table("users").select("id, email, deleted_at, provider, provider_id").ilike("email", email).not_.is_("deleted_at", "null").order("deleted_at", desc=True).limit(1).execute()
        if withdrawn.data and len(withdrawn.data) > 0:
            deleted_at_str = withdrawn.data[0].get("deleted_at")
            user_id = withdrawn.data[0].get("id")
            user_email = withdrawn.data[0].get("email")
            if deleted_at_str and user_id:
                if isinstance(deleted_at_str, str):
                    deleted_at = datetime.fromisoformat(deleted_at_str.replace('Z', '+00:00'))
                else:
                    deleted_at = deleted_at_str
                recovery_deadline = deleted_at + timedelta(days=REJOIN_RESTRICTION_DAYS)
                now = datetime.now(timezone.utc)
                if now < recovery_deadline:
                    days_remaining = (recovery_deadline - now).days + 1
                    return {
                        "user_id": user_id,
                        "email": user_email,
                        "days_remaining": days_remaining,
                        "provider": withdrawn.data[0].get("provider"),
                        "provider_id": withdrawn.data[0].get("provider_id"),
                    }

    return None


def _recover_user(db, user_id: str) -> None:
    """Recover a soft-deleted user by clearing deleted_at."""
    db.table("users").update({"deleted_at": None}).eq("id", user_id).execute()


# =====================================================
# Kakao OAuth Endpoints
# =====================================================

@router.get("/kakao/login")
async def kakao_login():
    """
    Redirect to Kakao OAuth authorization page.
    """
    state = secrets.token_urlsafe(32)
    kakao_auth_url = (
        f"{KAKAO_AUTH_URL}"
        f"?client_id={settings.kakao_client_id}"
        f"&redirect_uri={settings.kakao_redirect_uri}"
        f"&response_type=code"
        f"&state={state}"
    )
    return RedirectResponse(url=kakao_auth_url)


@router.get("/kakao/callback")
async def kakao_callback(
    code: str,
    state: Optional[str] = None,
    error: Optional[str] = None,
    error_description: Optional[str] = None,
    db=Depends(get_db)
):
    """
    Handle Kakao OAuth callback.
    Exchange authorization code for tokens, get user info, and redirect to frontend.
    """
    if error:
        return RedirectResponse(url=f"{settings.frontend_url}/login?error={error}&message={error_description}")

    try:
        async with httpx.AsyncClient() as client:
            # 1. Exchange authorization code for tokens
            token_response = await client.post(
                KAKAO_TOKEN_URL,
                data={
                    "grant_type": "authorization_code",
                    "client_id": settings.kakao_client_id,
                    "client_secret": settings.kakao_client_secret,
                    "redirect_uri": settings.kakao_redirect_uri,
                    "code": code,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded;charset=utf-8"},
            )
            if token_response.status_code != 200:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to get Kakao token: {token_response.text}")
            token_data = token_response.json()
            kakao_access_token = token_data["access_token"]

            # 2. Get user info from Kakao
            user_response = await client.get(KAKAO_USER_INFO_URL, headers={"Authorization": f"Bearer {kakao_access_token}"})
            if user_response.status_code != 200:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to get Kakao user info")
            kakao_user = user_response.json()

        # 3. Extract user info
        kakao_id = str(kakao_user["id"])
        kakao_account = kakao_user.get("kakao_account", {})
        profile = kakao_account.get("profile", {})
        email = kakao_account.get("email")
        nickname = profile.get("nickname", f"kakao_{kakao_id}")
        profile_image = profile.get("profile_image_url")

        # 3.5. Check for withdrawn user - redirect to recovery confirmation page
        recovery_info = _check_withdrawn_user_for_recovery(db, email=email, provider="kakao", provider_id=kakao_id)
        if recovery_info:
            # Redirect to recovery confirmation page
            from urllib.parse import quote
            redirect_url = (
                f"{settings.frontend_url}/auth/recover"
                f"?provider=kakao"
                f"&provider_id={kakao_id}"
                f"&email={quote(recovery_info.get('email', ''))}"
                f"&days={recovery_info['days_remaining']}"
            )
            return RedirectResponse(url=redirect_url)

        # 4. Check if user exists in our database (exclude soft-deleted users)
        existing_user = db.table("users").select("*").eq("provider", "kakao").eq("provider_id", kakao_id).is_("deleted_at", "null").execute()
        is_new_user = False

        if existing_user.data and len(existing_user.data) > 0:
            user = existing_user.data[0]
            user_id = user["id"]
        else:
            # Check if email already exists (link accounts, exclude soft-deleted)
            if email:
                email_user = db.table("users").select("*").ilike("email", email).is_("deleted_at", "null").execute()
                if email_user.data and len(email_user.data) > 0:
                    # Same email exists - just login, don't overwrite provider
                    user = email_user.data[0]
                    user_id = user["id"]
                    # Only update avatar if not set
                    if not user.get("avatar_url") and profile_image:
                        db.table("users").update({"avatar_url": profile_image}).eq("id", user_id).execute()
                else:
                    user_id = _create_kakao_user(db, kakao_id, email, nickname, profile_image)
                    is_new_user = True
            else:
                generated_email = f"kakao_{kakao_id}@codefill.local"
                user_id = _create_kakao_user(db, kakao_id, generated_email, nickname, profile_image)
                is_new_user = True

        # 5. Generate JWT tokens using utility functions
        from ..utils.security import create_access_token, create_refresh_token
        access_token = create_access_token(user_id)
        refresh_token = create_refresh_token(user_id)

        # 6. Redirect to frontend with tokens (include is_new_user flag)
        redirect_url = f"{settings.frontend_url}/auth/callback?access_token={access_token}&refresh_token={refresh_token}&expires_in={settings.access_token_expire_minutes * 60}&is_new_user={str(is_new_user).lower()}"
        return RedirectResponse(url=redirect_url)

    except HTTPException:
        raise
    except Exception as e:
        return RedirectResponse(url=f"{settings.frontend_url}/login?error=kakao_login_failed&message={str(e)}")


def _create_kakao_user(db, kakao_id: str, email: str, nickname: str, profile_image: Optional[str]) -> str:
    """Create a new user from Kakao OAuth data."""
    user_id = str(uuid.uuid4())
    db.table("users").insert({"id": user_id, "email": email, "name": nickname, "avatar_url": profile_image, "provider": "kakao", "provider_id": kakao_id}).execute()
    return user_id


# =====================================================
# Google OAuth Endpoints
# =====================================================

@router.get("/google/login")
async def google_login():
    """
    Redirect to Google OAuth authorization page.
    """
    state = secrets.token_urlsafe(32)
    google_auth_url = (
        f"{GOOGLE_AUTH_URL}"
        f"?client_id={settings.google_client_id}"
        f"&redirect_uri={settings.google_redirect_uri}"
        f"&response_type=code"
        f"&scope=openid email profile"
        f"&access_type=offline"
        f"&state={state}"
    )
    return RedirectResponse(url=google_auth_url)


@router.get("/google/callback")
async def google_callback(
    code: str = None,
    state: Optional[str] = None,
    error: Optional[str] = None,
    error_description: Optional[str] = None,
    db=Depends(get_db)
):
    """
    Handle Google OAuth callback.
    Exchange authorization code for tokens, get user info, and redirect to frontend.
    """
    if error:
        return RedirectResponse(url=f"{settings.frontend_url}/login?error={error}&message={error_description}")

    if not code:
        return RedirectResponse(url=f"{settings.frontend_url}/login?error=no_code&message=Authorization code not provided")

    try:
        async with httpx.AsyncClient() as client:
            # 1. Exchange authorization code for tokens
            token_response = await client.post(
                GOOGLE_TOKEN_URL,
                data={
                    "code": code,
                    "client_id": settings.google_client_id,
                    "client_secret": settings.google_client_secret,
                    "redirect_uri": settings.google_redirect_uri,
                    "grant_type": "authorization_code",
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            if token_response.status_code != 200:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to get Google token: {token_response.text}")
            token_data = token_response.json()
            google_access_token = token_data["access_token"]

            # 2. Get user info from Google
            user_response = await client.get(
                GOOGLE_USER_INFO_URL,
                headers={"Authorization": f"Bearer {google_access_token}"}
            )
            if user_response.status_code != 200:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to get Google user info")
            google_user = user_response.json()

        # 3. Extract user info
        google_id = str(google_user["id"])
        email = google_user.get("email")
        name = google_user.get("name", f"google_{google_id}")
        profile_image = google_user.get("picture")

        # 3.5. Check for withdrawn user - redirect to recovery confirmation page
        recovery_info = _check_withdrawn_user_for_recovery(db, email=email, provider="google", provider_id=google_id)
        if recovery_info:
            # Redirect to recovery confirmation page
            from urllib.parse import quote
            redirect_url = (
                f"{settings.frontend_url}/auth/recover"
                f"?provider=google"
                f"&provider_id={google_id}"
                f"&email={quote(recovery_info.get('email', ''))}"
                f"&days={recovery_info['days_remaining']}"
            )
            return RedirectResponse(url=redirect_url)

        # 4. Check if user exists in our database (exclude soft-deleted users)
        existing_user = db.table("users").select("*").eq("provider", "google").eq("provider_id", google_id).is_("deleted_at", "null").execute()
        is_new_user = False

        if existing_user.data and len(existing_user.data) > 0:
            user = existing_user.data[0]
            user_id = user["id"]
        else:
            # Check if email already exists (link accounts, exclude soft-deleted)
            if email:
                email_user = db.table("users").select("*").ilike("email", email).is_("deleted_at", "null").execute()
                if email_user.data and len(email_user.data) > 0:
                    # Same email exists - just login, don't overwrite provider
                    user = email_user.data[0]
                    user_id = user["id"]
                    # Only update avatar if not set
                    if not user.get("avatar_url") and profile_image:
                        db.table("users").update({"avatar_url": profile_image}).eq("id", user_id).execute()
                else:
                    user_id = _create_google_user(db, google_id, email, name, profile_image)
                    is_new_user = True
            else:
                # Google should always provide email, but handle edge case
                generated_email = f"google_{google_id}@codefill.local"
                user_id = _create_google_user(db, google_id, generated_email, name, profile_image)
                is_new_user = True

        # 5. Generate JWT tokens using utility functions
        from ..utils.security import create_access_token, create_refresh_token
        access_token = create_access_token(user_id)
        refresh_token = create_refresh_token(user_id)

        # 6. Redirect to frontend with tokens (include is_new_user flag)
        redirect_url = f"{settings.frontend_url}/auth/callback?access_token={access_token}&refresh_token={refresh_token}&expires_in={settings.access_token_expire_minutes * 60}&is_new_user={str(is_new_user).lower()}"
        return RedirectResponse(url=redirect_url)

    except HTTPException:
        raise
    except Exception as e:
        return RedirectResponse(url=f"{settings.frontend_url}/login?error=google_login_failed&message={str(e)}")


def _create_google_user(db, google_id: str, email: str, name: str, profile_image: Optional[str]) -> str:
    """Create a new user from Google OAuth data."""
    user_id = str(uuid.uuid4())
    db.table("users").insert({
        "id": user_id,
        "email": email,
        "name": name,
        "avatar_url": profile_image,
        "provider": "google",
        "provider_id": google_id
    }).execute()
    return user_id


# =====================================================
# GitHub OAuth Endpoints
# =====================================================

@router.get("/github/login")
async def github_login():
    """
    Redirect to GitHub OAuth authorization page.
    """
    state = secrets.token_urlsafe(32)
    github_auth_url = (
        f"{GITHUB_AUTH_URL}"
        f"?client_id={settings.github_client_id}"
        f"&redirect_uri={settings.github_redirect_uri}"
        f"&scope=read:user user:email"
        f"&state={state}"
    )
    return RedirectResponse(url=github_auth_url)


@router.get("/github/callback")
async def github_callback(
    code: str = None,
    state: Optional[str] = None,
    error: Optional[str] = None,
    error_description: Optional[str] = None,
    db=Depends(get_db)
):
    """
    Handle GitHub OAuth callback.
    Exchange authorization code for tokens, get user info, and redirect to frontend.
    """
    if error:
        return RedirectResponse(url=f"{settings.frontend_url}/login?error={error}&message={error_description}")

    if not code:
        return RedirectResponse(url=f"{settings.frontend_url}/login?error=no_code&message=Authorization code not provided")

    try:
        async with httpx.AsyncClient() as client:
            # 1. Exchange authorization code for access token
            token_response = await client.post(
                GITHUB_TOKEN_URL,
                json={
                    "client_id": settings.github_client_id,
                    "client_secret": settings.github_client_secret,
                    "code": code,
                },
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                },
            )
            if token_response.status_code != 200:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to get GitHub token: {token_response.text}")

            token_data = token_response.json()

            # Check for error in token response
            if "error" in token_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"GitHub OAuth error: {token_data.get('error_description', token_data['error'])}"
                )

            github_access_token = token_data["access_token"]

            # 2. Get user info from GitHub
            user_response = await client.get(
                GITHUB_USER_URL,
                headers={
                    "Authorization": f"Bearer {github_access_token}",
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28",
                }
            )
            if user_response.status_code != 200:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to get GitHub user info")
            github_user = user_response.json()

            # 3. Get user emails from GitHub (separate API call required)
            emails_response = await client.get(
                GITHUB_EMAILS_URL,
                headers={
                    "Authorization": f"Bearer {github_access_token}",
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28",
                }
            )

            email = None
            if emails_response.status_code == 200:
                emails = emails_response.json()
                # Find primary verified email
                primary_email = next(
                    (e["email"] for e in emails if e.get("primary") and e.get("verified")),
                    None
                )
                if primary_email:
                    email = primary_email
                elif emails:
                    # Fallback to first verified email
                    verified_email = next(
                        (e["email"] for e in emails if e.get("verified")),
                        None
                    )
                    email = verified_email or emails[0].get("email")

            # Fallback to public email from user profile
            if not email:
                email = github_user.get("email")

        # 4. Extract user info
        github_id = str(github_user["id"])
        login = github_user.get("login", f"github_{github_id}")
        name = github_user.get("name") or login
        avatar_url = github_user.get("avatar_url")

        # 4.5. Check for withdrawn user - redirect to recovery confirmation page
        recovery_info = _check_withdrawn_user_for_recovery(db, email=email, provider="github", provider_id=github_id)
        if recovery_info:
            from urllib.parse import quote
            redirect_url = (
                f"{settings.frontend_url}/auth/recover"
                f"?provider=github"
                f"&provider_id={github_id}"
                f"&email={quote(recovery_info.get('email', ''))}"
                f"&days={recovery_info['days_remaining']}"
            )
            return RedirectResponse(url=redirect_url)

        # 5. Check if user exists in our database (exclude soft-deleted users)
        existing_user = db.table("users").select("*").eq("provider", "github").eq("provider_id", github_id).is_("deleted_at", "null").execute()
        is_new_user = False

        if existing_user.data and len(existing_user.data) > 0:
            user = existing_user.data[0]
            user_id = user["id"]
        else:
            # Check if email already exists (link accounts, exclude soft-deleted)
            if email:
                email_user = db.table("users").select("*").ilike("email", email).is_("deleted_at", "null").execute()
                if email_user.data and len(email_user.data) > 0:
                    # Same email exists - just login, don't overwrite provider
                    user = email_user.data[0]
                    user_id = user["id"]
                    # Only update avatar if not set
                    if not user.get("avatar_url") and avatar_url:
                        db.table("users").update({"avatar_url": avatar_url}).eq("id", user_id).execute()
                else:
                    user_id = _create_github_user(db, github_id, email, name, avatar_url)
                    is_new_user = True
            else:
                # No email available, generate a placeholder
                generated_email = f"github_{github_id}@codefill.local"
                user_id = _create_github_user(db, github_id, generated_email, name, avatar_url)
                is_new_user = True

        # 6. Generate JWT tokens using utility functions
        from ..utils.security import create_access_token, create_refresh_token
        access_token = create_access_token(user_id)
        refresh_token = create_refresh_token(user_id)

        # 7. Redirect to frontend with tokens (include is_new_user flag)
        redirect_url = f"{settings.frontend_url}/auth/callback?access_token={access_token}&refresh_token={refresh_token}&expires_in={settings.access_token_expire_minutes * 60}&is_new_user={str(is_new_user).lower()}"
        return RedirectResponse(url=redirect_url)

    except HTTPException:
        raise
    except Exception as e:
        return RedirectResponse(url=f"{settings.frontend_url}/login?error=github_login_failed&message={str(e)}")


def _create_github_user(db, github_id: str, email: str, name: str, avatar_url: Optional[str]) -> str:
    """Create a new user from GitHub OAuth data."""
    user_id = str(uuid.uuid4())
    db.table("users").insert({
        "id": user_id,
        "email": email,
        "name": name,
        "avatar_url": avatar_url,
        "provider": "github",
        "provider_id": github_id
    }).execute()
    return user_id
