from fastapi import APIRouter, HTTPException, Depends, status
from typing import Optional

from ..database import get_db
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
