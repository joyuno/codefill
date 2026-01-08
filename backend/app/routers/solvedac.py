"""
solved.ac Integration Router

백준/solved.ac 프로필 연동 API
- CORS 프록시 역할 (프론트엔드에서 직접 호출 불가)
- 프로필 정보 조회 및 저장
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime
import httpx

from ..database import get_db
from ..dependencies import get_current_user_id

router = APIRouter()

# solved.ac API 기본 URL
SOLVED_AC_API_URL = "https://solved.ac/api/v3"


# =====================================================
# Pydantic Models
# =====================================================

class SolvedAcOrganization(BaseModel):
    """solved.ac 소속 정보"""
    organizationId: int
    name: str
    type: str
    rating: int
    userCount: int
    color: Optional[str] = None


class SolvedAcProfile(BaseModel):
    """solved.ac 프로필 응답 모델"""
    handle: str
    bio: Optional[str] = None
    profileImageUrl: Optional[str] = None
    tier: int = 0
    rating: int = 0
    class_: int = 0  # 'class'는 Python 예약어
    classDecoration: Optional[str] = None
    solvedCount: int = 0
    exp: int = 0
    rank: Optional[int] = None
    maxStreak: int = 0
    organizations: List[SolvedAcOrganization] = []
    isLinked: bool = False  # 이미 다른 사용자가 연동했는지 여부

    class Config:
        populate_by_name = True


class SolvedAcProfileDB(BaseModel):
    """DB에 저장된 solved.ac 프로필"""
    id: str
    user_id: str
    handle: str
    tier: int = 0
    rating: int = 0
    solved_count: int = 0
    max_streak: int = 0
    last_synced_at: str
    created_at: str


class LinkSolvedAcRequest(BaseModel):
    """solved.ac 연동 요청"""
    handle: str


class LinkSolvedAcResponse(BaseModel):
    """solved.ac 연동 응답"""
    success: bool
    message: str
    profile: Optional[SolvedAcProfileDB] = None


class SyncSolvedAcResponse(BaseModel):
    """solved.ac 동기화 응답"""
    success: bool
    message: str
    profile: Optional[SolvedAcProfileDB] = None


# =====================================================
# Helper Functions
# =====================================================

def tier_to_name(tier: int) -> str:
    """티어 번호를 이름으로 변환"""
    if tier == 0:
        return "Unrated"

    tiers = ["Bronze", "Silver", "Gold", "Platinum", "Diamond", "Ruby", "Master"]
    levels = ["V", "IV", "III", "II", "I"]

    tier_index = (tier - 1) // 5
    level_index = (tier - 1) % 5

    if tier_index >= len(tiers):
        return "Master"

    return f"{tiers[tier_index]} {levels[level_index]}"


async def fetch_solved_ac_profile(handle: str) -> Optional[dict]:
    """solved.ac API에서 프로필 정보 조회"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{SOLVED_AC_API_URL}/user/show",
                params={"handle": handle},
                timeout=10.0
            )

            if response.status_code == 404:
                return None

            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"solved.ac API 호출 실패: {str(e)}"
            )


# =====================================================
# API Endpoints
# =====================================================

@router.get("/lookup/{handle}", response_model=SolvedAcProfile)
async def lookup_solved_ac_profile(handle: str, db=Depends(get_db)):
    """
    solved.ac 프로필 조회 (CORS 프록시)

    인증 없이 누구나 조회 가능 (연동 전 확인용)
    isLinked: 이미 다른 사용자가 연동한 경우 True
    """
    profile = await fetch_solved_ac_profile(handle)

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"'{handle}' 사용자를 찾을 수 없습니다. 백준 아이디를 확인해주세요."
        )

    # 이미 다른 사용자가 이 handle을 연동했는지 확인
    actual_handle = profile.get("handle", handle)
    existing_link = db.table("solved_ac_profiles")\
        .select("user_id")\
        .eq("handle", actual_handle)\
        .execute()

    is_linked = existing_link.data and len(existing_link.data) > 0

    return SolvedAcProfile(
        handle=actual_handle,
        bio=profile.get("bio"),
        profileImageUrl=profile.get("profileImageUrl"),
        tier=profile.get("tier", 0),
        rating=profile.get("rating", 0),
        class_=profile.get("class", 0),
        classDecoration=profile.get("classDecoration"),
        solvedCount=profile.get("solvedCount", 0),
        exp=profile.get("exp", 0),
        rank=profile.get("rank"),
        maxStreak=profile.get("maxStreak", 0),
        organizations=profile.get("organizations", []),
        isLinked=is_linked,
    )


@router.post("/link", response_model=LinkSolvedAcResponse)
async def link_solved_ac(
    request: LinkSolvedAcRequest,
    user_id: UUID = Depends(get_current_user_id),
    db=Depends(get_db)
):
    """
    solved.ac 프로필 연동

    - 백준 아이디로 solved.ac 프로필 조회
    - DB에 프로필 정보 저장
    """
    handle = request.handle.strip()

    if not handle:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="백준 아이디를 입력해주세요."
        )

    # solved.ac API 호출
    profile = await fetch_solved_ac_profile(handle)

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"'{handle}' 사용자를 찾을 수 없습니다. 백준 아이디를 확인해주세요."
        )

    # 다른 유저가 이미 이 handle을 사용 중인지 확인
    actual_handle = profile.get("handle", handle)
    duplicate_check = db.table("solved_ac_profiles")\
        .select("user_id")\
        .eq("handle", actual_handle)\
        .neq("user_id", str(user_id))\
        .execute()

    if duplicate_check.data and len(duplicate_check.data) > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"'{actual_handle}' 아이디는 이미 다른 사용자가 연동 중입니다."
        )

    # 이미 연동된 프로필이 있는지 확인
    existing = db.table("solved_ac_profiles")\
        .select("*")\
        .eq("user_id", str(user_id))\
        .execute()

    now = datetime.utcnow().isoformat()

    profile_data = {
        "user_id": str(user_id),
        "handle": profile.get("handle", handle),
        "tier": profile.get("tier", 0),
        "rating": profile.get("rating", 0),
        "solved_count": profile.get("solvedCount", 0),
        "max_streak": profile.get("maxStreak", 0),
        "last_synced_at": now,
    }

    if existing.data and len(existing.data) > 0:
        # 기존 프로필 업데이트
        result = db.table("solved_ac_profiles")\
            .update(profile_data)\
            .eq("user_id", str(user_id))\
            .execute()
        message = "solved.ac 프로필이 업데이트되었습니다."
    else:
        # 새 프로필 생성
        result = db.table("solved_ac_profiles")\
            .insert(profile_data)\
            .execute()
        message = "solved.ac 프로필이 연동되었습니다."

    if result.data and len(result.data) > 0:
        saved = result.data[0]
        return LinkSolvedAcResponse(
            success=True,
            message=message,
            profile=SolvedAcProfileDB(
                id=saved["id"],
                user_id=saved["user_id"],
                handle=saved["handle"],
                tier=saved.get("tier", 0),
                rating=saved.get("rating", 0),
                solved_count=saved.get("solved_count", 0),
                max_streak=saved.get("max_streak", 0),
                last_synced_at=saved.get("last_synced_at", now),
                created_at=saved.get("created_at", now),
            )
        )

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="프로필 저장에 실패했습니다."
    )


@router.get("/me", response_model=Optional[SolvedAcProfileDB])
async def get_my_solved_ac_profile(
    user_id: UUID = Depends(get_current_user_id),
    db=Depends(get_db)
):
    """내 solved.ac 연동 프로필 조회"""
    result = db.table("solved_ac_profiles")\
        .select("*")\
        .eq("user_id", str(user_id))\
        .execute()

    if not result.data or len(result.data) == 0:
        return None

    saved = result.data[0]
    return SolvedAcProfileDB(
        id=saved["id"],
        user_id=saved["user_id"],
        handle=saved["handle"],
        tier=saved.get("tier", 0),
        rating=saved.get("rating", 0),
        solved_count=saved.get("solved_count", 0),
        max_streak=saved.get("max_streak", 0),
        last_synced_at=saved.get("last_synced_at", ""),
        created_at=saved.get("created_at", ""),
    )


@router.post("/sync", response_model=SyncSolvedAcResponse)
async def sync_solved_ac_profile(
    user_id: UUID = Depends(get_current_user_id),
    db=Depends(get_db)
):
    """
    solved.ac 프로필 동기화 (최신 정보로 업데이트)
    """
    # 기존 연동된 프로필 조회
    existing = db.table("solved_ac_profiles")\
        .select("*")\
        .eq("user_id", str(user_id))\
        .single()\
        .execute()

    if not existing.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="연동된 solved.ac 프로필이 없습니다. 먼저 연동해주세요."
        )

    handle = existing.data["handle"]

    # solved.ac API 호출
    profile = await fetch_solved_ac_profile(handle)

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"'{handle}' 사용자를 더 이상 찾을 수 없습니다."
        )

    now = datetime.utcnow().isoformat()

    # 프로필 업데이트
    profile_data = {
        "tier": profile.get("tier", 0),
        "rating": profile.get("rating", 0),
        "solved_count": profile.get("solvedCount", 0),
        "max_streak": profile.get("maxStreak", 0),
        "last_synced_at": now,
    }

    result = db.table("solved_ac_profiles")\
        .update(profile_data)\
        .eq("user_id", str(user_id))\
        .execute()

    if result.data and len(result.data) > 0:
        saved = result.data[0]
        return SyncSolvedAcResponse(
            success=True,
            message="solved.ac 프로필이 동기화되었습니다.",
            profile=SolvedAcProfileDB(
                id=saved["id"],
                user_id=saved["user_id"],
                handle=saved["handle"],
                tier=saved.get("tier", 0),
                rating=saved.get("rating", 0),
                solved_count=saved.get("solved_count", 0),
                max_streak=saved.get("max_streak", 0),
                last_synced_at=saved.get("last_synced_at", now),
                created_at=saved.get("created_at", ""),
            )
        )

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="프로필 동기화에 실패했습니다."
    )


@router.delete("/unlink")
async def unlink_solved_ac(
    user_id: UUID = Depends(get_current_user_id),
    db=Depends(get_db)
):
    """solved.ac 연동 해제"""
    result = db.table("solved_ac_profiles")\
        .delete()\
        .eq("user_id", str(user_id))\
        .execute()

    return {
        "success": True,
        "message": "solved.ac 연동이 해제되었습니다."
    }


# =====================================================
# 티어 정보 조회 (유틸리티)
# =====================================================

@router.get("/tier-info/{tier}")
async def get_tier_info(tier: int):
    """티어 번호로 티어 정보 조회"""
    return {
        "tier": tier,
        "name": tier_to_name(tier),
        "color": get_tier_color(tier),
    }


def get_tier_color(tier: int) -> str:
    """티어에 따른 색상 반환"""
    if tier == 0:
        return "#2D2D2D"  # Unrated
    elif tier <= 5:
        return "#AD5600"  # Bronze
    elif tier <= 10:
        return "#435F7A"  # Silver
    elif tier <= 15:
        return "#EC9A00"  # Gold
    elif tier <= 20:
        return "#27E2A4"  # Platinum
    elif tier <= 25:
        return "#00B4FC"  # Diamond
    elif tier <= 30:
        return "#FF0062"  # Ruby
    else:
        return "#B300FF"  # Master
