"""
Badge Service
뱃지 획득 조건 체크 및 부여 서비스

- 문제 풀이 시 트리거되어 조건 충족 뱃지 자동 부여
- N+1 쿼리 방지를 위한 배치 처리
- trigger_type별 필요한 뱃지만 체크
"""

import logging
from typing import Dict, Any, List, Set, Optional
from datetime import datetime, date
from ..database import get_supabase_client

logger = logging.getLogger(__name__)


class BadgeService:
    """뱃지 획득 체크 및 부여 서비스"""

    def __init__(self):
        self.supabase = get_supabase_client()
        self._badges_cache: Optional[List[Dict[str, Any]]] = None

    # ============================================================
    # Public API
    # ============================================================

    async def check_and_award_badges(
        self,
        user_id: str,
        trigger_type: str = 'solve',
        problem_type: Optional[str] = None,
        difficulty: Optional[str] = None,
        is_first_try: bool = False,
        used_hint: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        뱃지 획득 조건 체크 및 부여

        Args:
            user_id: 사용자 UUID
            trigger_type: 트리거 유형 ('solve', 'streak', 'time')
            problem_type: 문제 유형 ('blank', 'puzzle', 'guided', 'implementation')
            difficulty: 난이도 ('easy', 'medium', 'hard')
            is_first_try: 첫 시도 정답 여부
            used_hint: 힌트 사용 여부

        Returns:
            새로 획득한 뱃지 목록
        """
        try:
            # 1. 사용자 통계 조회
            user_stats = self._get_user_stats(user_id)
            if not user_stats:
                logger.warning(f"[BadgeService] User stats not found: {user_id}")
                return []

            # 2. 사용자가 이미 보유한 뱃지 코드 조회
            existing_badges = self._get_user_existing_badges(user_id)

            # 3. 모든 뱃지 정의 조회 (캐시)
            all_badges = self._get_all_badges()

            # 4. 체크할 뱃지 필터링 (trigger_type 기반)
            badges_to_check = self._filter_badges_by_trigger(
                all_badges=all_badges,
                trigger_type=trigger_type,
                problem_type=problem_type,
                difficulty=difficulty,
            )

            # 5. 조건 충족 뱃지 확인
            earned_badge_codes: List[str] = []
            for badge in badges_to_check:
                code = badge.get('code')
                if code in existing_badges:
                    continue  # 이미 보유

                if self._check_badge_condition(
                    badge=badge,
                    user_stats=user_stats,
                    user_id=user_id,
                    is_first_try=is_first_try,
                    used_hint=used_hint,
                ):
                    earned_badge_codes.append(code)

            # 6. 뱃지 부여 (배치 INSERT)
            if earned_badge_codes:
                awarded = self._award_badges(user_id, earned_badge_codes)
                logger.info(f"[BadgeService] Awarded {len(awarded)} badges to {user_id}: {earned_badge_codes}")
                return awarded

            return []

        except Exception as e:
            logger.error(f"[BadgeService] Error checking badges: {e}")
            return []

    # ============================================================
    # Private Methods - Data Access
    # ============================================================

    def _get_user_stats(self, user_id: str) -> Optional[Dict[str, Any]]:
        """사용자 통계 조회"""
        try:
            result = self.supabase.table("user_stats") \
                .select("*") \
                .eq("user_id", user_id) \
                .single() \
                .execute()

            return result.data if result.data else None

        except Exception as e:
            logger.error(f"[BadgeService] Failed to get user stats: {e}")
            return None

    def _get_user_existing_badges(self, user_id: str) -> Set[str]:
        """사용자가 보유한 뱃지 코드 목록"""
        try:
            result = self.supabase.table("user_badges") \
                .select("badges(code)") \
                .eq("user_id", user_id) \
                .execute()

            if not result.data:
                return set()

            codes = set()
            for row in result.data:
                badge_info = row.get('badges')
                if badge_info and badge_info.get('code'):
                    codes.add(badge_info['code'])

            return codes

        except Exception as e:
            logger.error(f"[BadgeService] Failed to get user badges: {e}")
            return set()

    def _get_all_badges(self) -> List[Dict[str, Any]]:
        """모든 뱃지 정의 조회 (캐시 사용)"""
        if self._badges_cache is not None:
            return self._badges_cache

        try:
            result = self.supabase.table("badges") \
                .select("*") \
                .execute()

            self._badges_cache = result.data or []
            return self._badges_cache

        except Exception as e:
            logger.error(f"[BadgeService] Failed to get badges: {e}")
            return []

    def _get_daily_activity(self, user_id: str, activity_date: date) -> Optional[Dict[str, Any]]:
        """특정 날짜의 활동 기록 조회"""
        try:
            result = self.supabase.table("daily_activity") \
                .select("*") \
                .eq("user_id", user_id) \
                .eq("activity_date", activity_date.isoformat()) \
                .single() \
                .execute()

            return result.data if result.data else None

        except Exception as e:
            logger.debug(f"[BadgeService] Daily activity not found: {e}")
            return None

    # ============================================================
    # Private Methods - Badge Filtering
    # ============================================================

    def _filter_badges_by_trigger(
        self,
        all_badges: List[Dict[str, Any]],
        trigger_type: str,
        problem_type: Optional[str],
        difficulty: Optional[str],
    ) -> List[Dict[str, Any]]:
        """
        트리거 유형에 따라 체크할 뱃지 필터링
        60개 전체를 체크하지 않고 필요한 것만 체크
        """
        relevant_condition_types: Set[str] = set()

        if trigger_type == 'solve':
            # 문제 풀이 시 체크할 조건들
            relevant_condition_types.add('problems')  # 총 문제 수
            relevant_condition_types.add('level')     # 레벨
            relevant_condition_types.add('daily')     # 하루 집중
            relevant_condition_types.add('time')      # 시간대
            relevant_condition_types.add('accuracy')  # 정확도
            relevant_condition_types.add('no_hint')   # 힌트 없이
            relevant_condition_types.add('special')   # 특별 조건

            # 문제 유형별
            if problem_type:
                relevant_condition_types.add(problem_type)

            # 난이도별
            if difficulty:
                relevant_condition_types.add(difficulty)

        elif trigger_type == 'streak':
            relevant_condition_types.add('streak')

        # 필터링
        return [
            badge for badge in all_badges
            if badge.get('condition_type') in relevant_condition_types
        ]

    # ============================================================
    # Private Methods - Condition Checking
    # ============================================================

    def _check_badge_condition(
        self,
        badge: Dict[str, Any],
        user_stats: Dict[str, Any],
        user_id: str,
        is_first_try: bool = False,
        used_hint: bool = False,
    ) -> bool:
        """개별 뱃지 조건 체크"""
        condition_type = badge.get('condition_type')
        condition_value = badge.get('condition_value', 0)

        # 마일스톤 - 문제 해결
        if condition_type == 'problems':
            return user_stats.get('problems_solved', 0) >= condition_value

        # 마일스톤 - 스트릭
        elif condition_type == 'streak':
            return user_stats.get('current_streak', 0) >= condition_value

        # 마일스톤 - 레벨
        elif condition_type == 'level':
            return user_stats.get('level', 1) >= condition_value

        # 문제 유형별
        elif condition_type == 'blank':
            return user_stats.get('blank_solved', 0) >= condition_value

        elif condition_type == 'puzzle':
            return user_stats.get('puzzle_solved', 0) >= condition_value

        elif condition_type == 'guided':
            return user_stats.get('guided_solved', 0) >= condition_value

        elif condition_type == 'implementation':
            return user_stats.get('implementation_solved', 0) >= condition_value

        # 난이도별
        elif condition_type == 'easy':
            return user_stats.get('easy_solved', 0) >= condition_value

        elif condition_type == 'medium':
            return user_stats.get('medium_solved', 0) >= condition_value

        elif condition_type == 'hard':
            return user_stats.get('hard_solved', 0) >= condition_value

        # 하루 집중 (daily)
        elif condition_type == 'daily':
            today_activity = self._get_daily_activity(user_id, date.today())
            if today_activity:
                return today_activity.get('problems_solved', 0) >= condition_value
            return False

        # 시간대별 (time)
        elif condition_type == 'time':
            return self._check_time_badge(badge.get('code', ''))

        # 정확도 (accuracy) - 첫 시도 정답
        elif condition_type == 'accuracy':
            # 현재는 단순 체크, 향후 attempts 테이블에서 집계
            if is_first_try:
                first_try_count = self._get_first_try_count(user_id)
                return first_try_count >= condition_value
            return False

        # 힌트 없이 (no_hint)
        elif condition_type == 'no_hint':
            if not used_hint:
                no_hint_count = self._get_no_hint_count(user_id)
                return no_hint_count >= condition_value
            return False

        # 특별 조건 (special)
        elif condition_type == 'special':
            return self._check_special_badge(badge.get('code', ''), user_stats, user_id)

        return False

    def _check_time_badge(self, badge_code: str) -> bool:
        """시간대 뱃지 체크"""
        now = datetime.now()
        hour = now.hour
        weekday = now.weekday()  # 0=Monday, 6=Sunday

        if badge_code == 'night_owl':
            # 자정~6시
            return 0 <= hour < 6

        elif badge_code == 'early_bird':
            # 6시~9시
            return 6 <= hour < 9

        elif badge_code == 'weekend_coder':
            # 주말 (토, 일)
            return weekday >= 5

        return False

    def _check_special_badge(
        self,
        badge_code: str,
        user_stats: Dict[str, Any],
        user_id: str,
    ) -> bool:
        """특별 뱃지 조건 체크"""

        # all_difficulty: 각 난이도별 10개씩
        if badge_code == 'all_difficulty':
            easy = user_stats.get('easy_solved', 0) >= 10
            medium = user_stats.get('medium_solved', 0) >= 10
            hard = user_stats.get('hard_solved', 0) >= 10
            return easy and medium and hard

        # all_difficulty_master: 각 난이도별 50개씩
        elif badge_code == 'all_difficulty_master':
            easy = user_stats.get('easy_solved', 0) >= 50
            medium = user_stats.get('medium_solved', 0) >= 50
            hard = user_stats.get('hard_solved', 0) >= 50
            return easy and medium and hard

        # perfect_week: 일주일간 매일 5문제 이상
        elif badge_code == 'perfect_week':
            return self._check_perfect_period(user_id, days=7, min_problems=5)

        # perfect_month: 한 달간 매일 3문제 이상
        elif badge_code == 'perfect_month':
            return self._check_perfect_period(user_id, days=30, min_problems=3)

        # all_rounder: 모든 카테고리 뱃지 획득 (마지막에 체크)
        elif badge_code == 'all_rounder':
            # 이 뱃지는 복잡하므로 나중에 구현
            return False

        return False

    def _check_perfect_period(
        self,
        user_id: str,
        days: int,
        min_problems: int,
    ) -> bool:
        """연속 기간 동안 매일 최소 문제 수 달성 체크"""
        try:
            from datetime import timedelta

            today = date.today()
            start_date = today - timedelta(days=days - 1)

            result = self.supabase.table("daily_activity") \
                .select("activity_date, problems_solved") \
                .eq("user_id", user_id) \
                .gte("activity_date", start_date.isoformat()) \
                .lte("activity_date", today.isoformat()) \
                .execute()

            if not result.data or len(result.data) < days:
                return False

            # 모든 날에 min_problems 이상인지 체크
            activity_map = {
                row['activity_date']: row['problems_solved']
                for row in result.data
            }

            for i in range(days):
                check_date = (start_date + timedelta(days=i)).isoformat()
                if activity_map.get(check_date, 0) < min_problems:
                    return False

            return True

        except Exception as e:
            logger.error(f"[BadgeService] Perfect period check failed: {e}")
            return False

    def _get_first_try_count(self, user_id: str) -> int:
        """첫 시도 정답 횟수 조회"""
        try:
            result = self.supabase.table("attempts") \
                .select("id", count="exact") \
                .eq("user_id", user_id) \
                .eq("is_correct", True) \
                .eq("attempt_number", 1) \
                .execute()

            return result.count or 0

        except Exception as e:
            logger.error(f"[BadgeService] First try count failed: {e}")
            return 0

    def _get_no_hint_count(self, user_id: str) -> int:
        """힌트 미사용 정답 횟수 조회"""
        try:
            result = self.supabase.table("attempts") \
                .select("id", count="exact") \
                .eq("user_id", user_id) \
                .eq("is_correct", True) \
                .eq("hints_used", 0) \
                .execute()

            return result.count or 0

        except Exception as e:
            logger.error(f"[BadgeService] No hint count failed: {e}")
            return 0

    # ============================================================
    # Private Methods - Badge Awarding
    # ============================================================

    def _award_badges(
        self,
        user_id: str,
        badge_codes: List[str],
    ) -> List[Dict[str, Any]]:
        """뱃지 부여 (배치 INSERT)"""
        if not badge_codes:
            return []

        try:
            # 뱃지 ID 조회
            all_badges = self._get_all_badges()
            code_to_badge = {b['code']: b for b in all_badges}

            # INSERT 데이터 준비
            insert_data = []
            awarded_badges = []

            for code in badge_codes:
                badge = code_to_badge.get(code)
                if badge:
                    insert_data.append({
                        'user_id': user_id,
                        'badge_id': badge['id'],
                    })
                    awarded_badges.append({
                        'code': code,
                        'name': badge.get('name', ''),
                        'icon_url': badge.get('icon_url'),
                        'rarity': badge.get('rarity', 'common'),
                    })

            # 배치 INSERT
            if insert_data:
                self.supabase.table("user_badges") \
                    .insert(insert_data) \
                    .execute()

            return awarded_badges

        except Exception as e:
            logger.error(f"[BadgeService] Failed to award badges: {e}")
            return []

    def clear_cache(self):
        """뱃지 캐시 초기화"""
        self._badges_cache = None


# Singleton instance
_badge_service: Optional[BadgeService] = None


def get_badge_service() -> BadgeService:
    """BadgeService 싱글톤 반환"""
    global _badge_service
    if _badge_service is None:
        _badge_service = BadgeService()
    return _badge_service
