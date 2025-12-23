from fastapi import APIRouter, HTTPException, Depends, status, Header
from fastapi.responses import RedirectResponse
from typing import Optional
import httpx
import secrets
import uuid
from datetime import datetime, timedelta
from jose import jwt

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
)

router = APIRouter()
settings = get_settings()

KAKAO_AUTH_URL = "https://kauth.kakao.com/oauth/authorize"
KAKAO_TOKEN_URL = "https://kauth.kakao.com/oauth/token"
KAKAO_USER_INFO_URL = "https://kapi.kakao.com/v2/user/me"

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USER_INFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"


@router.post("/signup", response_model=AuthResponse)
async def signup(request: SignupRequest, db=Depends(get_db)):
    """
    Register a new user with email and password.

    Creates user account with:
    - Basic info (email, name, password)
    - Optional profile info (experience, goal, preferences)
    - Initial user_stats record
    - Initial user_preferences record
    """
    try:
        # Create user in Supabase Auth
        auth_response = db.auth.sign_up({
            "email": request.email,
            "password": request.password,
            "options": {
                "data": {
                    "name": request.name,
                    "experience_level": request.experience_level.value if request.experience_level else None,
                    "learning_goal": request.learning_goal.value if request.learning_goal else None,
                }
            }
        })

        if auth_response.user is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user"
            )

        user_id = auth_response.user.id

        # Build user data for users table
        user_data = {
            "id": user_id,
            "email": request.email,
            "name": request.name,
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

        # Create user record in our users table
        # Use upsert to handle cases where the record might already exist
        db.table("users").upsert(user_data, on_conflict="id").execute()

        # Note: user_stats and user_preferences are created by database trigger
        # handle_new_user() - no need to create them manually

        # Update preferences if provided
        if request.preferred_language:
            db.table("user_preferences").update({
                "preferred_language": request.preferred_language,
            }).eq("user_id", user_id).execute()

        return AuthResponse(
            success=True,
            message="User created successfully. Please check your email to verify your account.",
            data={"user_id": str(user_id)}
        )

    except Exception as e:
        error_message = str(e)
        if "already registered" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Signup failed: {error_message}"
        )


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db=Depends(get_db)):
    """
    Authenticate user with email and password.

    Returns access and refresh tokens.
    """
    try:
        auth_response = db.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password,
        })

        if auth_response.session is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        return TokenResponse(
            access_token=auth_response.session.access_token,
            refresh_token=auth_response.session.refresh_token,
            token_type="bearer",
            expires_in=auth_response.session.expires_in or 3600,
        )

    except Exception as e:
        error_message = str(e)
        if "invalid" in error_message.lower() or "credentials" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {error_message}"
        )


@router.post("/logout", response_model=AuthResponse)
async def logout(db=Depends(get_db)):
    """
    Logout the current user.

    Invalidates the current session.
    """
    try:
        db.auth.sign_out()
        return AuthResponse(
            success=True,
            message="Logged out successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Logout failed: {str(e)}"
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest, db=Depends(get_db)):
    """
    Refresh access token using refresh token.

    Supports both:
    - Supabase Auth refresh tokens (for email/password login)
    - Self-generated JWT refresh tokens (for Kakao OAuth login)
    """
    # First, try Supabase Auth refresh
    try:
        auth_response = db.auth.refresh_session(request.refresh_token)
        if auth_response.session is not None:
            return TokenResponse(
                access_token=auth_response.session.access_token,
                refresh_token=auth_response.session.refresh_token,
                token_type="bearer",
                expires_in=auth_response.session.expires_in or 3600,
            )
    except Exception:
        pass  # Not a Supabase token, try self-generated JWT

    # Second, try self-generated JWT refresh (for Kakao OAuth)
    try:
        from jose import JWTError
        payload = jwt.decode(
            request.refresh_token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm]
        )

        token_type = payload.get("type")
        user_id = payload.get("sub")

        if token_type != "refresh" or not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token type"
            )

        # Generate new tokens
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        refresh_token_expires = timedelta(days=settings.refresh_token_expire_days)

        new_access_token = jwt.encode(
            {"sub": user_id, "exp": datetime.utcnow() + access_token_expires, "type": "access"},
            settings.jwt_secret,
            algorithm=settings.jwt_algorithm
        )
        new_refresh_token = jwt.encode(
            {"sub": user_id, "exp": datetime.utcnow() + refresh_token_expires, "type": "refresh"},
            settings.jwt_secret,
            algorithm=settings.jwt_algorithm
        )

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=int(access_token_expires.total_seconds()),
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )


@router.post("/password/reset", response_model=AuthResponse)
async def request_password_reset(request: PasswordResetRequest, db=Depends(get_db)):
    """
    Request password reset email.
    """
    try:
        db.auth.reset_password_for_email(request.email)
        return AuthResponse(
            success=True,
            message="Password reset email sent if account exists"
        )
    except Exception as e:
        # Don't reveal if email exists
        return AuthResponse(
            success=True,
            message="Password reset email sent if account exists"
        )


@router.put("/password/reset", response_model=AuthResponse)
async def confirm_password_reset(request: PasswordResetConfirm, db=Depends(get_db)):
    """
    Confirm password reset with token.
    """
    try:
        db.auth.update_user({"password": request.new_password})
        return AuthResponse(
            success=True,
            message="Password updated successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )


# =====================================================
# Duplicate Check Endpoints
# =====================================================

@router.post("/check-email", response_model=CheckResponse)
async def check_email_availability(request: CheckEmailRequest, db=Depends(get_db)):
    """
    Check if email is available for registration.
    """
    email = request.email.lower()

    # Check if email already exists (exclude soft-deleted users)
    existing = db.table("users").select("id").ilike("email", email).is_("deleted_at", "null").execute()
    if existing.data and len(existing.data) > 0:
        return CheckResponse(available=False, message="이미 사용 중인 이메일입니다.")

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
    from jose import JWTError

    # Get token from Authorization header
    token = authorization.replace("Bearer ", "") if authorization else None
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증이 필요합니다."
        )

    # Get user ID from token
    user_id = None

    # Try Supabase Auth token first
    try:
        user = db.auth.get_user(token)
        if user is not None and user.user is not None:
            user_id = str(user.user.id)
    except Exception:
        pass

    # Try self-generated JWT (for OAuth users)
    if not user_id:
        try:
            payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
            token_type = payload.get("type")
            if token_type == "access":
                user_id = payload.get("sub")
        except JWTError:
            pass

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰입니다."
        )

    # Get user to check provider
    user_result = db.table("users").select("provider, email").eq("id", user_id).single().execute()
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

    # Verify current password by attempting login
    try:
        verify_response = db.auth.sign_in_with_password({
            "email": user["email"],
            "password": request.current_password,
        })
        if verify_response.session is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="현재 비밀번호가 올바르지 않습니다."
            )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="현재 비밀번호가 올바르지 않습니다."
        )

    # Update password using Supabase Admin API
    try:
        db.auth.admin.update_user_by_id(user_id, {"password": request.new_password})
        return AuthResponse(success=True, message="비밀번호가 변경되었습니다.")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="비밀번호 변경에 실패했습니다."
        )


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

        # 4. Check if user exists in our database
        existing_user = db.table("users").select("*").eq("provider", "kakao").eq("provider_id", kakao_id).execute()
        is_new_user = False

        if existing_user.data and len(existing_user.data) > 0:
            user = existing_user.data[0]
            user_id = user["id"]
        else:
            # Check if email already exists (link accounts)
            if email:
                email_user = db.table("users").select("*").eq("email", email).execute()
                if email_user.data and len(email_user.data) > 0:
                    user = email_user.data[0]
                    user_id = user["id"]
                    db.table("users").update({"provider": "kakao", "provider_id": kakao_id, "avatar_url": profile_image or user.get("avatar_url")}).eq("id", user_id).execute()
                else:
                    user_id = _create_kakao_user(db, kakao_id, email, nickname, profile_image)
                    is_new_user = True
            else:
                generated_email = f"kakao_{kakao_id}@codefill.local"
                user_id = _create_kakao_user(db, kakao_id, generated_email, nickname, profile_image)
                is_new_user = True

        # 5. Generate JWT tokens
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        refresh_token_expires = timedelta(days=settings.refresh_token_expire_days)

        access_token = jwt.encode({"sub": str(user_id), "exp": datetime.utcnow() + access_token_expires, "type": "access"}, settings.jwt_secret, algorithm=settings.jwt_algorithm)
        refresh_token = jwt.encode({"sub": str(user_id), "exp": datetime.utcnow() + refresh_token_expires, "type": "refresh"}, settings.jwt_secret, algorithm=settings.jwt_algorithm)

        # 6. Redirect to frontend with tokens (include is_new_user flag)
        redirect_url = f"{settings.frontend_url}/auth/callback?access_token={access_token}&refresh_token={refresh_token}&expires_in={int(access_token_expires.total_seconds())}&is_new_user={str(is_new_user).lower()}"
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

        # 4. Check if user exists in our database
        existing_user = db.table("users").select("*").eq("provider", "google").eq("provider_id", google_id).execute()
        is_new_user = False

        if existing_user.data and len(existing_user.data) > 0:
            user = existing_user.data[0]
            user_id = user["id"]
        else:
            # Check if email already exists (link accounts)
            if email:
                email_user = db.table("users").select("*").eq("email", email).execute()
                if email_user.data and len(email_user.data) > 0:
                    user = email_user.data[0]
                    user_id = user["id"]
                    # Update provider info
                    db.table("users").update({
                        "provider": "google",
                        "provider_id": google_id,
                        "avatar_url": profile_image or user.get("avatar_url")
                    }).eq("id", user_id).execute()
                else:
                    user_id = _create_google_user(db, google_id, email, name, profile_image)
                    is_new_user = True
            else:
                # Google should always provide email, but handle edge case
                generated_email = f"google_{google_id}@codefill.local"
                user_id = _create_google_user(db, google_id, generated_email, name, profile_image)
                is_new_user = True

        # 5. Generate JWT tokens
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        refresh_token_expires = timedelta(days=settings.refresh_token_expire_days)

        access_token = jwt.encode(
            {"sub": str(user_id), "exp": datetime.utcnow() + access_token_expires, "type": "access"},
            settings.jwt_secret,
            algorithm=settings.jwt_algorithm
        )
        refresh_token = jwt.encode(
            {"sub": str(user_id), "exp": datetime.utcnow() + refresh_token_expires, "type": "refresh"},
            settings.jwt_secret,
            algorithm=settings.jwt_algorithm
        )

        # 6. Redirect to frontend with tokens (include is_new_user flag)
        redirect_url = f"{settings.frontend_url}/auth/callback?access_token={access_token}&refresh_token={refresh_token}&expires_in={int(access_token_expires.total_seconds())}&is_new_user={str(is_new_user).lower()}"
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
