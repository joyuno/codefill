"""
Ranking System Models
랭킹 시스템 (글로벌, 주간, 월간)
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from enum import Enum


class RankingPeriod(str, Enum):
    """랭킹 기간."""
    GLOBAL = "global"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class RankingType(str, Enum):
    """랭킹 정렬 기준."""
    XP = "xp"
    PROBLEMS = "problems"
    STREAK = "streak"


# =====================================================
# Ranking Item Models
# =====================================================

class RankingItem(BaseModel):
    """랭킹 개별 항목."""
    rank: int
    user_id: UUID
    username: Optional[str] = None
    profile_image: Optional[str] = None
    value: int  # XP, 문제수, 또는 스트릭
    level: int


class RankingListResponse(BaseModel):
    """랭킹 목록 응답."""
    items: List[RankingItem]
    total: int
    page: int
    limit: int
    has_more: bool


# =====================================================
# My Ranking Models
# =====================================================

class MyRankingResponse(BaseModel):
    """내 순위 응답."""
    global_xp_rank: int
    global_solve_rank: int
    global_streak_rank: int
    weekly_xp_rank: int
    weekly_solve_rank: int
    monthly_xp_rank: int
    monthly_solve_rank: int
    total_users: int


class MyRankingSummary(BaseModel):
    """내 순위 요약 (상단 카드용)."""
    # 글로벌
    global_xp_rank: int
    global_xp_percentile: float  # 상위 몇 %인지
    global_solve_rank: int
    global_streak_rank: int
    # 주간
    weekly_xp_rank: Optional[int] = None
    weekly_solve_rank: Optional[int] = None
    # 월간
    monthly_xp_rank: Optional[int] = None
    monthly_solve_rank: Optional[int] = None
    # 통계
    total_users: int
    # 내 현재 값
    my_total_xp: int = 0
    my_problems_solved: int = 0
    my_longest_streak: int = 0
    my_level: int = 1
