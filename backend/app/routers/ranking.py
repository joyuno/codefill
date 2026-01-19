"""
Ranking Router - 랭킹 시스템

엔드포인트:
- GET /ranking/global - 글로벌 랭킹 (XP, 문제 풀이 수, 스트릭)
- GET /ranking/weekly - 주간 랭킹 (XP, 문제 풀이 수)
- GET /ranking/monthly - 월간 랭킹 (XP, 문제 풀이 수)
- GET /ranking/me - 내 순위 조회
- GET /ranking/challenge-page-data - Challenge 페이지 통합 데이터 (최적화)
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from fastapi import APIRouter, HTTPException, Depends, Query, status
from typing import Optional, Literal
from uuid import UUID

from ..database import get_db
from ..dependencies import get_current_user, get_current_user_id_optional
from ..models.ranking import (
    RankingItem,
    RankingListResponse,
    MyRankingResponse,
    MyRankingSummary,
    ChallengePageDataResponse,
)
from ..services.mission_service import MissionService

# Thread pool for parallel execution
_executor = ThreadPoolExecutor(max_workers=4)

router = APIRouter()


# =====================================================
# 글로벌 랭킹
# =====================================================

@router.get("/global", response_model=RankingListResponse)
async def get_global_ranking(
    type: Literal["xp", "problems", "streak"] = Query("xp", description="정렬 기준"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 항목 수"),
    db=Depends(get_db),
):
    """
    글로벌 랭킹 조회 (전체 기간 누적)

    - type: xp (경험치), problems (문제 풀이 수), streak (최장 스트릭)
    """
    try:
        offset = (page - 1) * limit

        # RPC 함수 호출
        result = db.rpc("get_global_ranking", {
            "p_type": type,
            "p_limit": limit,
            "p_offset": offset
        }).execute()

        # 전체 개수 조회
        count_result = db.rpc("get_ranking_total_count", {
            "p_period": "global",
            "p_type": type
        }).execute()

        total = count_result.data if count_result.data else 0

        items = [
            RankingItem(
                rank=item["rank"],
                user_id=item["user_id"],
                username=item["username"],
                profile_image=item["profile_image"],
                value=item["value"],
                level=item["level"]
            )
            for item in (result.data or [])
        ]

        return RankingListResponse(
            items=items,
            total=total,
            page=page,
            limit=limit,
            has_more=(page * limit) < total
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get global ranking: {str(e)}"
        )


# =====================================================
# 주간 랭킹
# =====================================================

@router.get("/weekly", response_model=RankingListResponse)
async def get_weekly_ranking(
    type: Literal["xp", "problems"] = Query("xp", description="정렬 기준"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 항목 수"),
    db=Depends(get_db),
):
    """
    주간 랭킹 조회 (이번 주 월요일 ~ 일요일)

    - type: xp (경험치), problems (문제 풀이 수)
    """
    try:
        offset = (page - 1) * limit

        # RPC 함수 호출
        result = db.rpc("get_weekly_ranking", {
            "p_type": type,
            "p_limit": limit,
            "p_offset": offset
        }).execute()

        # 전체 개수 조회
        count_result = db.rpc("get_ranking_total_count", {
            "p_period": "weekly",
            "p_type": type
        }).execute()

        total = count_result.data if count_result.data else 0

        items = [
            RankingItem(
                rank=item["rank"],
                user_id=item["user_id"],
                username=item["username"],
                profile_image=item["profile_image"],
                value=item["value"],
                level=item["level"]
            )
            for item in (result.data or [])
        ]

        return RankingListResponse(
            items=items,
            total=total,
            page=page,
            limit=limit,
            has_more=(page * limit) < total
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get weekly ranking: {str(e)}"
        )


# =====================================================
# 월간 랭킹
# =====================================================

@router.get("/monthly", response_model=RankingListResponse)
async def get_monthly_ranking(
    type: Literal["xp", "problems"] = Query("xp", description="정렬 기준"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 항목 수"),
    db=Depends(get_db),
):
    """
    월간 랭킹 조회 (이번 달 1일 ~ 말일)

    - type: xp (경험치), problems (문제 풀이 수)
    """
    try:
        offset = (page - 1) * limit

        # RPC 함수 호출
        result = db.rpc("get_monthly_ranking", {
            "p_type": type,
            "p_limit": limit,
            "p_offset": offset
        }).execute()

        # 전체 개수 조회
        count_result = db.rpc("get_ranking_total_count", {
            "p_period": "monthly",
            "p_type": type
        }).execute()

        total = count_result.data if count_result.data else 0

        items = [
            RankingItem(
                rank=item["rank"],
                user_id=item["user_id"],
                username=item["username"],
                profile_image=item["profile_image"],
                value=item["value"],
                level=item["level"]
            )
            for item in (result.data or [])
        ]

        return RankingListResponse(
            items=items,
            total=total,
            page=page,
            limit=limit,
            has_more=(page * limit) < total
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get monthly ranking: {str(e)}"
        )


# =====================================================
# 내 순위 조회
# =====================================================

@router.get("/me", response_model=MyRankingSummary)
async def get_my_ranking(
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    내 순위 조회 (모든 랭킹에서의 순위)
    - Optimized: 단일 RPC 호출로 랭킹 + 통계 함께 반환
    """
    try:
        user_id = current_user["id"]

        # Optimized RPC 함수 호출 (랭킹 + 내 통계 한번에 반환)
        result = db.rpc("get_my_ranking_optimized", {
            "p_user_id": user_id
        }).execute()

        if not result.data or len(result.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User ranking not found"
            )

        ranking_data = result.data[0]
        total_users = ranking_data.get("total_users", 1)
        global_xp_rank = ranking_data.get("global_xp_rank", total_users)

        # 상위 퍼센트 계산
        percentile = round((global_xp_rank / total_users) * 100, 1) if total_users > 0 else 100

        return MyRankingSummary(
            global_xp_rank=global_xp_rank,
            global_xp_percentile=percentile,
            global_solve_rank=ranking_data.get("global_solve_rank", total_users),
            global_streak_rank=ranking_data.get("global_streak_rank", total_users),
            weekly_xp_rank=ranking_data.get("weekly_xp_rank") or None,
            weekly_solve_rank=ranking_data.get("weekly_solve_rank") or None,
            monthly_xp_rank=ranking_data.get("monthly_xp_rank") or None,
            monthly_solve_rank=ranking_data.get("monthly_solve_rank") or None,
            total_users=total_users,
            # User stats now included in optimized RPC response
            my_total_xp=ranking_data.get("my_total_xp", 0),
            my_problems_solved=ranking_data.get("my_problems_solved", 0),
            my_longest_streak=ranking_data.get("my_longest_streak", 0),
            my_level=ranking_data.get("my_level", 1),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get my ranking: {str(e)}"
        )


# =====================================================
# Challenge 페이지 통합 데이터 (성능 최적화)
# =====================================================

@router.get("/challenge-page-data", response_model=ChallengePageDataResponse)
async def get_challenge_page_data(
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Challenge 페이지 통합 데이터 조회
    - 내 랭킹 + 일일미션 + 주간챌린지 + userId 한번에 반환
    - 3개 API 호출 → 1개로 통합하여 지연 시간 3배 감소
    - 내부적으로 3개 작업을 병렬 실행
    """
    try:
        user_id = current_user["id"]
        loop = asyncio.get_event_loop()
        mission_service = MissionService(db)

        # Helper functions for parallel execution
        def fetch_ranking():
            result = db.rpc("get_my_ranking_optimized", {
                "p_user_id": user_id
            }).execute()
            return result.data[0] if result.data else None

        def fetch_daily():
            return mission_service.get_daily_missions(user_id)

        def fetch_weekly():
            return mission_service.get_weekly_challenges(user_id)

        # 병렬 실행: 랭킹, 일일 미션, 주간 챌린지
        ranking_data, daily_data, weekly_data = await asyncio.gather(
            loop.run_in_executor(_executor, fetch_ranking),
            loop.run_in_executor(_executor, fetch_daily),
            loop.run_in_executor(_executor, fetch_weekly)
        )

        if not ranking_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User ranking not found"
            )

        total_users = ranking_data.get("total_users", 1)
        global_xp_rank = ranking_data.get("global_xp_rank", total_users)
        percentile = round((global_xp_rank / total_users) * 100, 1) if total_users > 0 else 100

        ranking = MyRankingSummary(
            global_xp_rank=global_xp_rank,
            global_xp_percentile=percentile,
            global_solve_rank=ranking_data.get("global_solve_rank", total_users),
            global_streak_rank=ranking_data.get("global_streak_rank", total_users),
            weekly_xp_rank=ranking_data.get("weekly_xp_rank") or None,
            weekly_solve_rank=ranking_data.get("weekly_solve_rank") or None,
            monthly_xp_rank=ranking_data.get("monthly_xp_rank") or None,
            monthly_solve_rank=ranking_data.get("monthly_solve_rank") or None,
            total_users=total_users,
            my_total_xp=ranking_data.get("my_total_xp", 0),
            my_problems_solved=ranking_data.get("my_problems_solved", 0),
            my_longest_streak=ranking_data.get("my_longest_streak", 0),
            my_level=ranking_data.get("my_level", 1),
        )

        return ChallengePageDataResponse(
            ranking=ranking,
            daily=daily_data.model_dump() if daily_data else {"missions": [], "today_completed": 0, "today_claimed": 0},
            weekly=weekly_data.model_dump() if weekly_data else {"challenges": [], "week_completed": 0, "week_claimed": 0},
            user_id=user_id
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get challenge page data: {str(e)}"
        )
