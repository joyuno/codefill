"""
Mission models for Daily Missions and Weekly Challenges
"""
from pydantic import BaseModel
from typing import Optional, Dict, List


class UserMission(BaseModel):
    """사용자 미션 (진행 상황 포함)"""
    id: str                                    # user_mission_progress.id
    mission_id: str                            # missions.id
    code: str
    name: str
    description: Optional[str] = None
    condition_type: str
    condition_value: int                       # = target_value
    difficulty: Optional[str] = None
    current_progress: int
    target_value: int                          # missions.condition_value
    status: str                                # 'active', 'completed', 'claimed'
    reward_gold: int = 0
    reward_xp: int = 0
    reward_seeds: Optional[Dict[str, int]] = None


class DailyMissionsResponse(BaseModel):
    """일일 미션 응답"""
    missions: List[UserMission]
    today_completed: int
    today_claimed: int


class WeeklyChallengesResponse(BaseModel):
    """주간 챌린지 응답"""
    challenges: List[UserMission]
    week_completed: int
    week_claimed: int


class ClaimRewardResponse(BaseModel):
    """보상 수령 응답"""
    success: bool
    gold_earned: int = 0
    xp_earned: int = 0
    seeds_earned: Optional[Dict[str, int]] = None
    new_gold_balance: int = 0
    error: Optional[str] = None


class MissionsSummary(BaseModel):
    """미션 요약 (대시보드용)"""
    daily_active: int
    daily_completed: int
    daily_claimed: int
    weekly_active: int
    weekly_completed: int
    weekly_claimed: int
    today_gold_earned: int
    today_xp_earned: int
