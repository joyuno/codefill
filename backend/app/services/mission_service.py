"""
Mission Service - Daily Missions and Weekly Challenges business logic
"""
from typing import List, Optional, Dict, Any
from ..models.mission import (
    UserMission,
    DailyMissionsResponse,
    WeeklyChallengesResponse,
    ClaimRewardResponse,
    MissionsSummary
)


class MissionService:
    """미션 서비스 클래스"""

    def __init__(self, db):
        self.db = db

    def get_daily_missions(self, user_id: str) -> DailyMissionsResponse:
        """오늘의 일일 미션 조회 (없으면 자동 생성)"""
        result = self.db.rpc("get_daily_missions", {
            "p_user_id": user_id
        }).execute()

        missions_data = result.data or []
        missions = [self._parse_user_mission(m) for m in missions_data]

        completed = sum(1 for m in missions if m.status in ['completed', 'claimed'])
        claimed = sum(1 for m in missions if m.status == 'claimed')

        return DailyMissionsResponse(
            missions=missions,
            today_completed=completed,
            today_claimed=claimed
        )

    def get_weekly_challenges(self, user_id: str) -> WeeklyChallengesResponse:
        """이번 주 챌린지 조회 (없으면 자동 생성)"""
        result = self.db.rpc("get_weekly_challenges", {
            "p_user_id": user_id
        }).execute()

        challenges_data = result.data or []
        challenges = [self._parse_user_mission(c) for c in challenges_data]

        completed = sum(1 for c in challenges if c.status in ['completed', 'claimed'])
        claimed = sum(1 for c in challenges if c.status == 'claimed')

        return WeeklyChallengesResponse(
            challenges=challenges,
            week_completed=completed,
            week_claimed=claimed
        )

    def update_progress(
        self,
        user_id: str,
        condition_type: str,
        difficulty: Optional[str] = None,
        increment: int = 1
    ) -> List[Dict[str, Any]]:
        """미션 진행률 업데이트 (문제 풀이 시 호출)"""
        result = self.db.rpc("update_mission_progress", {
            "p_user_id": user_id,
            "p_condition_type": condition_type,
            "p_difficulty": difficulty,
            "p_increment": increment
        }).execute()

        return result.data or []

    def claim_reward(self, user_id: str, progress_id: str) -> ClaimRewardResponse:
        """미션 보상 수령"""
        result = self.db.rpc("claim_mission_reward", {
            "p_user_id": user_id,
            "p_progress_id": progress_id
        }).execute()

        data = result.data or {}

        if not data.get("success", False):
            return ClaimRewardResponse(
                success=False,
                error=data.get("error", "Unknown error")
            )

        return ClaimRewardResponse(
            success=True,
            gold_earned=data.get("gold_earned", 0),
            xp_earned=data.get("xp_earned", 0),
            seeds_earned=data.get("seeds_earned"),
            new_gold_balance=data.get("new_gold_balance", 0)
        )

    def get_summary(self, user_id: str) -> MissionsSummary:
        """미션 요약 정보 (대시보드용)"""
        daily = self.get_daily_missions(user_id)
        weekly = self.get_weekly_challenges(user_id)

        today_gold = sum(m.reward_gold for m in daily.missions if m.status == 'claimed')
        today_xp = sum(m.reward_xp for m in daily.missions if m.status == 'claimed')

        return MissionsSummary(
            daily_active=sum(1 for m in daily.missions if m.status == 'active'),
            daily_completed=sum(1 for m in daily.missions if m.status == 'completed'),
            daily_claimed=daily.today_claimed,
            weekly_active=sum(1 for c in weekly.challenges if c.status == 'active'),
            weekly_completed=sum(1 for c in weekly.challenges if c.status == 'completed'),
            weekly_claimed=weekly.week_claimed,
            today_gold_earned=today_gold,
            today_xp_earned=today_xp
        )

    def _parse_user_mission(self, data: dict) -> UserMission:
        """DB 결과를 UserMission 모델로 변환"""
        return UserMission(
            id=str(data.get("id", "")),
            mission_id=str(data.get("mission_id", "")),
            code=data.get("code", ""),
            name=data.get("name", ""),
            description=data.get("description"),
            condition_type=data.get("condition_type", ""),
            condition_value=data.get("condition_value", 0),
            difficulty=data.get("difficulty"),
            current_progress=data.get("current_progress", 0),
            target_value=data.get("target_value", 0),
            status=data.get("status", "active"),
            reward_gold=data.get("reward_gold", 0),
            reward_xp=data.get("reward_xp", 0),
            reward_seeds=data.get("reward_seeds")
        )
