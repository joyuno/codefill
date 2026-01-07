"""
Common FastAPI Dependencies

인증 관련 공통 의존성 함수들을 제공합니다.
라우터에서 중복되는 인증 함수들을 통합하여 관리합니다.
"""

from fastapi import Header, HTTPException, Depends, status
from uuid import UUID
from typing import Optional, Dict, Any

from .utils.security import verify_token
from .database import get_db


# ============================================================
# Authentication Dependencies
# ============================================================

async def get_current_user_id(
    authorization: str = Header(..., description="Bearer token")
) -> UUID:
    """
    JWT 토큰에서 현재 사용자 ID를 추출합니다.

    Args:
        authorization: Authorization 헤더 (Bearer token)

    Returns:
        UUID: 사용자 ID

    Raises:
        HTTPException 401: 토큰이 없거나 유효하지 않은 경우
    """
    token = authorization.replace("Bearer ", "")
    payload = verify_token(token)

    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        return UUID(payload["sub"])
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_id_optional(
    authorization: Optional[str] = Header(None, description="Bearer token")
) -> Optional[UUID]:
    """
    JWT 토큰에서 사용자 ID를 추출합니다 (선택적).

    동작:
    - 토큰이 없으면: None 반환 (비로그인 사용자, 정상)
    - 토큰이 있지만 만료/무효: 401 반환 (프론트엔드가 토큰 갱신 시도)
    - 토큰이 유효하면: UUID 반환

    Args:
        authorization: Authorization 헤더 (Bearer token, optional)

    Returns:
        Optional[UUID]: 사용자 ID 또는 None (토큰 없는 경우)

    Raises:
        HTTPException 401: 토큰이 있지만 만료되거나 유효하지 않은 경우
    """
    # 토큰이 없으면 None (비로그인 사용자)
    if not authorization:
        return None

    token = authorization.replace("Bearer ", "")
    payload = verify_token(token)

    # 토큰이 있지만 유효하지 않으면 401 (세션 만료 → 프론트에서 갱신 시도)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired or invalid",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        return UUID(payload["sub"])
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    user_id: UUID = Depends(get_current_user_id),
    db = Depends(get_db),
) -> Dict[str, Any]:
    """
    현재 로그인한 사용자 정보를 조회합니다.

    Args:
        user_id: 사용자 ID (get_current_user_id에서 추출)
        db: Supabase 클라이언트

    Returns:
        Dict: 사용자 정보

    Raises:
        HTTPException 404: 사용자를 찾을 수 없는 경우
    """
    result = db.table("users").select("*").eq("id", str(user_id)).single().execute()

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return result.data


async def get_optional_user(
    user_id: Optional[UUID] = Depends(get_current_user_id_optional),
    db = Depends(get_db),
) -> Optional[Dict[str, Any]]:
    """
    현재 로그인한 사용자 정보를 조회합니다 (선택적).
    토큰이 없거나 유효하지 않아도 에러를 발생시키지 않습니다.

    Args:
        user_id: 사용자 ID (optional)
        db: Supabase 클라이언트

    Returns:
        Optional[Dict]: 사용자 정보 또는 None
    """
    if not user_id:
        return None

    result = db.table("users").select("*").eq("id", str(user_id)).single().execute()

    if not result.data:
        return None

    return result.data


async def get_current_user_with_profile(
    user_id: UUID = Depends(get_current_user_id),
    db = Depends(get_db),
) -> Dict[str, Any]:
    """
    현재 로그인한 사용자와 프로필 정보를 함께 조회합니다.

    Args:
        user_id: 사용자 ID
        db: Supabase 클라이언트

    Returns:
        Dict: 사용자 및 프로필 정보
    """
    # 사용자 정보 조회
    user_result = db.table("users").select("*").eq("id", str(user_id)).single().execute()

    if not user_result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user_data = user_result.data

    # 프로필 정보 조회
    profile_result = db.table("profiles").select("*").eq("user_id", str(user_id)).single().execute()

    if profile_result.data:
        user_data["profile"] = profile_result.data
    else:
        user_data["profile"] = None

    return user_data


# ============================================================
# Token Validation Helpers
# ============================================================

def extract_token_from_header(authorization: str) -> str:
    """
    Authorization 헤더에서 토큰을 추출합니다.

    Args:
        authorization: Authorization 헤더 값

    Returns:
        str: 추출된 토큰
    """
    if authorization.startswith("Bearer "):
        return authorization[7:]
    return authorization


def validate_token_type(payload: Dict[str, Any], expected_type: str = "access") -> bool:
    """
    토큰 타입을 검증합니다.

    Args:
        payload: 토큰 페이로드
        expected_type: 예상 토큰 타입 ("access" 또는 "refresh")

    Returns:
        bool: 토큰 타입이 일치하면 True
    """
    return payload.get("type") == expected_type
