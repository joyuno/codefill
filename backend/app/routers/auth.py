from fastapi import APIRouter, HTTPException, Depends, status
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
)

router = APIRouter()
settings = get_settings()

KAKAO_AUTH_URL = "https://kauth.kakao.com/oauth/authorize"
KAKAO_TOKEN_URL = "https://kauth.kakao.com/oauth/token"
KAKAO_USER_INFO_URL = "https://kapi.kakao.com/v2/user/me"


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

        # Create user record in our users table
        # Use upsert to handle cases where the record might already exist
        db.table("users").upsert({
            "id": user_id,
            "email": request.email,
            "name": request.name,
            "provider": "email",
        }, on_conflict="id").execute()

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
    """
    try:
        auth_response = db.auth.refresh_session(request.refresh_token)

        if auth_response.session is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        return TokenResponse(
            access_token=auth_response.session.access_token,
            refresh_token=auth_response.session.refresh_token,
            token_type="bearer",
            expires_in=auth_response.session.expires_in or 3600,
        )

    except Exception as e:
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
            else:
                generated_email = f"kakao_{kakao_id}@codefill.local"
                user_id = _create_kakao_user(db, kakao_id, generated_email, nickname, profile_image)

        # 5. Generate JWT tokens
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        refresh_token_expires = timedelta(days=settings.refresh_token_expire_days)

        access_token = jwt.encode({"sub": str(user_id), "exp": datetime.utcnow() + access_token_expires, "type": "access"}, settings.jwt_secret, algorithm=settings.jwt_algorithm)
        refresh_token = jwt.encode({"sub": str(user_id), "exp": datetime.utcnow() + refresh_token_expires, "type": "refresh"}, settings.jwt_secret, algorithm=settings.jwt_algorithm)

        # 6. Redirect to frontend with tokens
        redirect_url = f"{settings.frontend_url}/auth/callback?access_token={access_token}&refresh_token={refresh_token}&expires_in={int(access_token_expires.total_seconds())}"
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
