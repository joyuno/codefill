"""
보안 유틸리티 - 비밀번호 해싱 및 JWT 토큰 관리

제공 기능:
- bcrypt를 사용한 비밀번호 해싱
- JWT Access/Refresh 토큰 생성
- 토큰 검증
"""

from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt, JWTError
from uuid import UUID
from typing import Optional, Union

from ..config import get_settings

# bcrypt를 사용한 비밀번호 해싱 컨텍스트
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    bcrypt를 사용하여 비밀번호를 해싱합니다.

    Args:
        password: 평문 비밀번호

    Returns:
        해싱된 비밀번호 문자열
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    평문 비밀번호와 해싱된 비밀번호를 비교 검증합니다.

    Args:
        plain_password: 검증할 평문 비밀번호
        hashed_password: 비교할 해싱된 비밀번호

    Returns:
        비밀번호가 일치하면 True, 아니면 False
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False


def create_access_token(user_id: Union[UUID, str]) -> str:
    """
    JWT Access 토큰을 생성합니다.

    Args:
        user_id: 토큰에 인코딩할 사용자 ID

    Returns:
        JWT Access 토큰 문자열
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
    JWT Refresh 토큰을 생성합니다.

    Args:
        user_id: 토큰에 인코딩할 사용자 ID

    Returns:
        JWT Refresh 토큰 문자열
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
    JWT 토큰을 검증하고 디코딩합니다.

    Args:
        token: 검증할 JWT 토큰 문자열

    Returns:
        유효한 경우 디코딩된 토큰 페이로드, 아니면 None
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
    유효한 JWT 토큰에서 사용자 ID를 추출합니다.

    Args:
        token: JWT 토큰 문자열

    Returns:
        토큰이 유효하면 사용자 ID 문자열, 아니면 None
    """
    payload = verify_token(token)
    if payload:
        return payload.get("sub")
    return None
