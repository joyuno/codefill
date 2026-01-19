"""
Missions Router - Daily Missions and Weekly Challenges API endpoints
"""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from ..database import get_db
from ..dependencies import get_current_user_id
from ..models.mission import (
    DailyMissionsResponse,
    WeeklyChallengesResponse,
    ClaimRewardResponse,
    MissionsSummary
)
from ..services.mission_service import MissionService

# Thread pool for parallel execution of sync RPC calls
_executor = ThreadPoolExecutor(max_workers=4)

router = APIRouter(prefix="/missions", tags=["missions"])


@router.get("/daily", response_model=DailyMissionsResponse)
async def get_daily_missions(
    user_id: UUID = Depends(get_current_user_id),
    db=Depends(get_db)
):
    """
    오늘의 일일 미션 조회
    - 미션이 없으면 자동으로 3개 할당
    - 매일 자정에 새로운 미션으로 갱신
    """
    service = MissionService(db)
    return service.get_daily_missions(str(user_id))


@router.get("/weekly", response_model=WeeklyChallengesResponse)
async def get_weekly_challenges(
    user_id: UUID = Depends(get_current_user_id),
    db=Depends(get_db)
):
    """
    이번 주 챌린지 조회
    - 챌린지가 없으면 자동으로 2개 할당
    - 매주 월요일에 새로운 챌린지로 갱신
    """
    service = MissionService(db)
    return service.get_weekly_challenges(str(user_id))


@router.post("/{mission_id}/claim", response_model=ClaimRewardResponse)
async def claim_mission_reward(
    mission_id: str,
    user_id: UUID = Depends(get_current_user_id),
    db=Depends(get_db)
):
    """
    미션 보상 수령
    - status가 'completed'인 미션만 보상 수령 가능
    - 골드, XP, 씨앗 지급
    """
    service = MissionService(db)
    result = service.claim_reward(str(user_id), mission_id)

    if not result.success:
        raise HTTPException(status_code=400, detail=result.error)

    return result


@router.get("/summary", response_model=MissionsSummary)
async def get_missions_summary(
    user_id: UUID = Depends(get_current_user_id),
    db=Depends(get_db)
):
    """
    미션 요약 정보 (대시보드용)
    - 일일/주간 미션 진행 상황
    - 오늘 획득한 골드/XP
    """
    service = MissionService(db)
    return service.get_summary(str(user_id))


@router.get("/all")
async def get_all_missions(
    user_id: UUID = Depends(get_current_user_id),
    db=Depends(get_db)
):
    """
    일일 미션 + 주간 챌린지 모두 조회
    - 미션 페이지에서 한 번에 로딩용
    - Optimized: 병렬 실행으로 2배 성능 개선
    """
    service = MissionService(db)
    loop = asyncio.get_event_loop()

    # 병렬 실행: 2개 RPC 호출을 동시에 실행
    daily, weekly = await asyncio.gather(
        loop.run_in_executor(_executor, service.get_daily_missions, str(user_id)),
        loop.run_in_executor(_executor, service.get_weekly_challenges, str(user_id))
    )

    return {
        "daily": daily,
        "weekly": weekly
    }
