"""
Security utilities for password hashing and JWT token management.

This module provides:
- Password hashing with bcrypt
- JWT access/refresh token creation
- Token verification
"""

from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt, JWTError
from uuid import UUID
from typing import Optional, Union

from ..config import get_settings

# Password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password: Plain text password

    Returns:
        Hashed password string
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to compare against

    Returns:
        True if password matches, False otherwise
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False


def create_access_token(user_id: Union[UUID, str]) -> str:
    """
    Create a JWT access token.

    Args:
        user_id: User ID to encode in the token

    Returns:
        JWT access token string
    """
    settings = get_settings()
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode = {
        "sub": str(user_id),
        "exp": expire,
        "type": "access"
    }

    return jwt.encode(
        to_encode,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm
    )


def create_refresh_token(user_id: Union[UUID, str]) -> str:
    """
    Create a JWT refresh token.

    Args:
        user_id: User ID to encode in the token

    Returns:
        JWT refresh token string
    """
    settings = get_settings()
    expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)

    to_encode = {
        "sub": str(user_id),
        "exp": expire,
        "type": "refresh"
    }

    return jwt.encode(
        to_encode,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm
    )


def verify_token(token: str) -> Optional[dict]:
    """
    Verify and decode a JWT token.

    Args:
        token: JWT token string to verify

    Returns:
        Decoded token payload if valid, None otherwise
    """
    settings = get_settings()

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm]
        )
        return payload
    except JWTError:
        return None


def get_user_id_from_token(token: str) -> Optional[str]:
    """
    Extract user ID from a valid JWT token.

    Args:
        token: JWT token string

    Returns:
        User ID string if token is valid, None otherwise
    """
    payload = verify_token(token)
    if payload:
        return payload.get("sub")
    return None
