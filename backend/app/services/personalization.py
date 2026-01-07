"""
Personalization Service

사용자 학습 데이터 기반 개인화 서비스

Features:
1. 학습 히스토리 분석
2. 강점/약점 파악
3. 다음 문제 추천
4. RAG 컨텍스트에 사용자 정보 주입
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass

from ..database import get_supabase_client
from ..config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class UserLearningProfile:
    """사용자 학습 프로필"""
    user_id: str
    total_attempts: int
    correct_rate: float
    strong_topics: List[str]
    weak_topics: List[str]
    preferred_difficulty: str
    recent_topics: List[str]
    avg_hints_used: float
    streak_days: int
    last_active: Optional[datetime]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "total_attempts": self.total_attempts,
            "correct_rate": self.correct_rate,
            "strong_topics": self.strong_topics,
            "weak_topics": self.weak_topics,
            "preferred_difficulty": self.preferred_difficulty,
            "recent_topics": self.recent_topics,
            "avg_hints_used": self.avg_hints_used,
            "streak_days": self.streak_days,
            "last_active": self.last_active.isoformat() if self.last_active else None,
        }


@dataclass
class ProblemRecommendation:
    """문제 추천 결과"""
    problem_id: str
    base_problem_id: Optional[str]
    problem_type: str
    difficulty: str
    topics: List[str]
    reason: str
    confidence: float  # 0.0 ~ 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "problem_id": self.problem_id,
            "base_problem_id": self.base_problem_id,
            "problem_type": self.problem_type,
            "difficulty": self.difficulty,
            "topics": self.topics,
            "reason": self.reason,
            "confidence": self.confidence,
        }


class PersonalizationService:
    """
    개인화 서비스

    Usage:
        service = get_personalization_service()
        profile = await service.get_user_profile(user_id)
        recommendations = await service.get_recommendations(user_id, limit=5)
    """

    def __init__(self):
        self.supabase = get_supabase_client()
        self._profile_cache: Dict[str, tuple] = {}  # user_id -> (profile, timestamp)
        self._cache_ttl = 300  # 5분 캐시

    # ============================================================
    # 학습 프로필 조회
    # ============================================================

    async def get_user_profile(
        self,
        user_id: str,
        use_cache: bool = True,
    ) -> Optional[UserLearningProfile]:
        """
        사용자 학습 프로필 조회

        Args:
            user_id: 사용자 ID
            use_cache: 캐시 사용 여부

        Returns:
            UserLearningProfile or None
        """
        # 캐시 확인
        if use_cache and user_id in self._profile_cache:
            profile, cached_at = self._profile_cache[user_id]
            if datetime.now().timestamp() - cached_at < self._cache_ttl:
                return profile

        try:
            # 1. 시도 기록 조회 (최근 100개)
            attempts_result = self.supabase.table("attempts") \
                .select("*, base_problems(tags, difficulty)") \
                .eq("user_id", user_id) \
                .order("submitted_at", desc=True) \
                .limit(100) \
                .execute()

            attempts = attempts_result.data or []

            if not attempts:
                # 시도 기록이 없으면 기본 프로필 반환
                return UserLearningProfile(
                    user_id=user_id,
                    total_attempts=0,
                    correct_rate=0.0,
                    strong_topics=[],
                    weak_topics=[],
                    preferred_difficulty="easy",
                    recent_topics=[],
                    avg_hints_used=0.0,
                    streak_days=0,
                    last_active=None,
                )

            # 2. 통계 계산
            total_attempts = len(attempts)
            correct_count = sum(1 for a in attempts if a.get("is_correct"))
            correct_rate = correct_count / total_attempts if total_attempts > 0 else 0.0

            # 3. 토픽별 성적 분석
            topic_stats = self._analyze_topic_stats(attempts)
            strong_topics = [t for t, stats in topic_stats.items() if stats["rate"] >= 0.7]
            weak_topics = [t for t, stats in topic_stats.items() if stats["rate"] < 0.5]

            # 4. 선호 난이도 분석
            preferred_difficulty = self._analyze_preferred_difficulty(attempts)

            # 5. 최근 학습 토픽
            recent_topics = self._get_recent_topics(attempts[:20])

            # 6. 힌트 사용량
            hints_used_list = [a.get("hints_used", 0) for a in attempts]
            avg_hints = sum(hints_used_list) / len(hints_used_list) if hints_used_list else 0.0

            # 7. 연속 학습일
            streak_days = await self._calculate_streak(user_id)

            # 8. 마지막 활동
            last_active = None
            if attempts:
                last_attempt_str = attempts[0].get("submitted_at")
                if last_attempt_str:
                    try:
                        last_active = datetime.fromisoformat(last_attempt_str.replace("Z", "+00:00"))
                    except ValueError:
                        pass

            profile = UserLearningProfile(
                user_id=user_id,
                total_attempts=total_attempts,
                correct_rate=correct_rate,
                strong_topics=strong_topics[:5],
                weak_topics=weak_topics[:5],
                preferred_difficulty=preferred_difficulty,
                recent_topics=recent_topics[:5],
                avg_hints_used=avg_hints,
                streak_days=streak_days,
                last_active=last_active,
            )

            # 캐시 저장
            self._profile_cache[user_id] = (profile, datetime.now().timestamp())

            return profile

        except Exception as e:
            logger.error(f"[Personalization] Failed to get user profile: {e}")
            return None

    def _analyze_topic_stats(
        self,
        attempts: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """토픽별 통계 분석"""
        topic_stats: Dict[str, Dict[str, Any]] = {}

        for attempt in attempts:
            # base_problems에서 tags 추출
            base_problem = attempt.get("base_problems") or {}
            tags = base_problem.get("tags", [])

            if not tags and isinstance(tags, str):
                tags = [tags]

            for tag in tags:
                if tag not in topic_stats:
                    topic_stats[tag] = {"total": 0, "correct": 0, "rate": 0.0}

                topic_stats[tag]["total"] += 1
                if attempt.get("is_correct"):
                    topic_stats[tag]["correct"] += 1

        # 정답률 계산
        for tag, stats in topic_stats.items():
            if stats["total"] > 0:
                stats["rate"] = stats["correct"] / stats["total"]

        return topic_stats

    def _analyze_preferred_difficulty(
        self,
        attempts: List[Dict[str, Any]]
    ) -> str:
        """선호 난이도 분석 (정답률 70%+ 중 가장 높은 난이도)"""
        difficulty_order = ["easy", "medium", "medium_hard", "hard", "very_hard"]
        difficulty_stats: Dict[str, Dict[str, int]] = {}

        for attempt in attempts:
            base_problem = attempt.get("base_problems") or {}
            difficulty = base_problem.get("difficulty", "medium")

            if difficulty not in difficulty_stats:
                difficulty_stats[difficulty] = {"total": 0, "correct": 0}

            difficulty_stats[difficulty]["total"] += 1
            if attempt.get("is_correct"):
                difficulty_stats[difficulty]["correct"] += 1

        # 정답률 70% 이상인 가장 높은 난이도 찾기
        preferred = "easy"
        for diff in difficulty_order:
            stats = difficulty_stats.get(diff, {})
            total = stats.get("total", 0)
            correct = stats.get("correct", 0)

            if total >= 3 and (correct / total) >= 0.7:
                preferred = diff

        return preferred

    def _get_recent_topics(self, recent_attempts: List[Dict[str, Any]]) -> List[str]:
        """최근 학습 토픽 추출"""
        topics = []
        seen = set()

        for attempt in recent_attempts:
            base_problem = attempt.get("base_problems") or {}
            tags = base_problem.get("tags", [])

            for tag in tags:
                if tag not in seen:
                    topics.append(tag)
                    seen.add(tag)

        return topics

    async def _calculate_streak(self, user_id: str) -> int:
        """연속 학습일 계산"""
        try:
            result = self.supabase.table("daily_activity") \
                .select("date") \
                .eq("user_id", user_id) \
                .order("date", desc=True) \
                .limit(30) \
                .execute()

            if not result.data:
                return 0

            dates = sorted(
                [datetime.strptime(d["date"], "%Y-%m-%d").date() for d in result.data],
                reverse=True
            )

            streak = 0
            today = datetime.now().date()

            for i, date in enumerate(dates):
                expected = today - timedelta(days=i)
                if date == expected:
                    streak += 1
                else:
                    break

            return streak

        except Exception as e:
            logger.warning(f"[Personalization] Failed to calculate streak: {e}")
            return 0

    # ============================================================
    # 문제 추천
    # ============================================================

    async def get_recommendations(
        self,
        user_id: str,
        limit: int = 5,
        problem_type: Optional[str] = None,
    ) -> List[ProblemRecommendation]:
        """
        개인화된 문제 추천

        Args:
            user_id: 사용자 ID
            limit: 추천 개수
            problem_type: 문제 유형 필터 (blank, puzzle, guided)

        Returns:
            List[ProblemRecommendation]
        """
        profile = await self.get_user_profile(user_id)

        if not profile:
            # 프로필 없으면 기본 추천
            return await self._get_default_recommendations(limit, problem_type)

        recommendations = []

        # 1. 약점 보완 문제 (40%)
        weak_limit = int(limit * 0.4) or 1
        weak_problems = await self._recommend_by_topics(
            profile.weak_topics,
            profile.preferred_difficulty,
            weak_limit,
            problem_type,
            already_solved_by=user_id,
        )
        for prob in weak_problems:
            prob.reason = "약점 보완을 위한 문제예요"
            prob.confidence = 0.9
        recommendations.extend(weak_problems)

        # 2. 다음 난이도 도전 문제 (30%)
        challenge_limit = int(limit * 0.3) or 1
        next_difficulty = self._get_next_difficulty(profile.preferred_difficulty)
        challenge_problems = await self._recommend_by_difficulty(
            next_difficulty,
            challenge_limit,
            problem_type,
            already_solved_by=user_id,
        )
        for prob in challenge_problems:
            prob.reason = "도전! 한 단계 높은 난이도예요"
            prob.confidence = 0.75
        recommendations.extend(challenge_problems)

        # 3. 복습 문제 (30%)
        review_limit = limit - len(recommendations)
        if review_limit > 0:
            review_problems = await self._recommend_for_review(
                user_id,
                profile.recent_topics,
                review_limit,
                problem_type,
            )
            for prob in review_problems:
                prob.reason = "복습하면 좋을 문제예요"
                prob.confidence = 0.8
            recommendations.extend(review_problems)

        return recommendations[:limit]

    async def _get_default_recommendations(
        self,
        limit: int,
        problem_type: Optional[str],
    ) -> List[ProblemRecommendation]:
        """기본 추천 (프로필 없을 때)"""
        try:
            query = self.supabase.table("base_problems") \
                .select("id, name, difficulty, tags") \
                .eq("difficulty", "easy") \
                .limit(limit)

            result = query.execute()

            return [
                ProblemRecommendation(
                    problem_id=p["id"],
                    base_problem_id=p["id"],
                    problem_type=problem_type or "blank",
                    difficulty=p.get("difficulty", "easy"),
                    topics=p.get("tags", []),
                    reason="초보자를 위한 쉬운 문제예요",
                    confidence=0.5,
                )
                for p in (result.data or [])
            ]

        except Exception as e:
            logger.error(f"[Personalization] Default recommendations failed: {e}")
            return []

    async def _recommend_by_topics(
        self,
        topics: List[str],
        difficulty: str,
        limit: int,
        problem_type: Optional[str],
        already_solved_by: Optional[str] = None,
    ) -> List[ProblemRecommendation]:
        """토픽 기반 추천"""
        if not topics:
            return []

        try:
            # 토픽 필터 (JSON 배열에서 검색)
            query = self.supabase.table("base_problems") \
                .select("id, name, difficulty, tags") \
                .eq("difficulty", difficulty) \
                .limit(limit * 2)

            result = query.execute()

            # 토픽 매칭 필터링
            matching = []
            for p in (result.data or []):
                p_tags = p.get("tags", [])
                if any(t in p_tags for t in topics):
                    matching.append(p)

            # 이미 푼 문제 제외
            if already_solved_by and matching:
                solved_ids = await self._get_solved_problem_ids(already_solved_by)
                matching = [p for p in matching if p["id"] not in solved_ids]

            return [
                ProblemRecommendation(
                    problem_id=p["id"],
                    base_problem_id=p["id"],
                    problem_type=problem_type or "blank",
                    difficulty=p.get("difficulty", "medium"),
                    topics=p.get("tags", []),
                    reason="",
                    confidence=0.0,
                )
                for p in matching[:limit]
            ]

        except Exception as e:
            logger.error(f"[Personalization] Topic recommendation failed: {e}")
            return []

    async def _recommend_by_difficulty(
        self,
        difficulty: str,
        limit: int,
        problem_type: Optional[str],
        already_solved_by: Optional[str] = None,
    ) -> List[ProblemRecommendation]:
        """난이도 기반 추천"""
        try:
            query = self.supabase.table("base_problems") \
                .select("id, name, difficulty, tags") \
                .eq("difficulty", difficulty) \
                .limit(limit * 2)

            result = query.execute()
            problems = result.data or []

            # 이미 푼 문제 제외
            if already_solved_by and problems:
                solved_ids = await self._get_solved_problem_ids(already_solved_by)
                problems = [p for p in problems if p["id"] not in solved_ids]

            return [
                ProblemRecommendation(
                    problem_id=p["id"],
                    base_problem_id=p["id"],
                    problem_type=problem_type or "blank",
                    difficulty=p.get("difficulty", difficulty),
                    topics=p.get("tags", []),
                    reason="",
                    confidence=0.0,
                )
                for p in problems[:limit]
            ]

        except Exception as e:
            logger.error(f"[Personalization] Difficulty recommendation failed: {e}")
            return []

    async def _recommend_for_review(
        self,
        user_id: str,
        recent_topics: List[str],
        limit: int,
        problem_type: Optional[str],
    ) -> List[ProblemRecommendation]:
        """복습 문제 추천 (틀렸던 문제 중)"""
        try:
            # 틀렸던 문제 조회
            wrong_result = self.supabase.table("attempts") \
                .select("base_problem_id, base_problems(id, name, difficulty, tags)") \
                .eq("user_id", user_id) \
                .eq("is_correct", False) \
                .order("submitted_at", desc=True) \
                .limit(limit * 3) \
                .execute()

            wrong_attempts = wrong_result.data or []

            # 중복 제거
            seen = set()
            recommendations = []

            for attempt in wrong_attempts:
                bp = attempt.get("base_problems")
                if not bp:
                    continue

                bp_id = bp.get("id")
                if bp_id in seen:
                    continue
                seen.add(bp_id)

                recommendations.append(ProblemRecommendation(
                    problem_id=bp_id,
                    base_problem_id=bp_id,
                    problem_type=problem_type or "blank",
                    difficulty=bp.get("difficulty", "medium"),
                    topics=bp.get("tags", []),
                    reason="",
                    confidence=0.0,
                ))

                if len(recommendations) >= limit:
                    break

            return recommendations

        except Exception as e:
            logger.error(f"[Personalization] Review recommendation failed: {e}")
            return []

    async def _get_solved_problem_ids(self, user_id: str) -> set:
        """이미 정답 처리된 문제 ID 목록"""
        try:
            result = self.supabase.table("attempts") \
                .select("base_problem_id") \
                .eq("user_id", user_id) \
                .eq("is_correct", True) \
                .execute()

            return {a.get("base_problem_id") for a in (result.data or []) if a.get("base_problem_id")}

        except Exception:
            return set()

    def _get_next_difficulty(self, current: str) -> str:
        """다음 난이도 반환"""
        difficulty_order = ["easy", "medium", "medium_hard", "hard", "very_hard"]
        try:
            idx = difficulty_order.index(current)
            if idx < len(difficulty_order) - 1:
                return difficulty_order[idx + 1]
        except ValueError:
            pass
        return current

    # ============================================================
    # RAG 컨텍스트 생성
    # ============================================================

    async def get_rag_context(self, user_id: str) -> Dict[str, Any]:
        """
        RAG 검색에 사용할 사용자 컨텍스트 생성

        Returns:
            {
                "user_level": "intermediate",
                "strong_topics": [...],
                "weak_topics": [...],
                "recent_topics": [...],
                "preferred_difficulty": "medium",
                "hint_tendency": "low" | "medium" | "high",
            }
        """
        profile = await self.get_user_profile(user_id)

        if not profile:
            return {
                "user_level": "beginner",
                "strong_topics": [],
                "weak_topics": [],
                "recent_topics": [],
                "preferred_difficulty": "easy",
                "hint_tendency": "medium",
            }

        # 사용자 레벨 결정
        if profile.correct_rate >= 0.8 and profile.total_attempts >= 50:
            user_level = "advanced"
        elif profile.correct_rate >= 0.6 and profile.total_attempts >= 20:
            user_level = "intermediate"
        else:
            user_level = "beginner"

        # 힌트 경향
        if profile.avg_hints_used < 0.5:
            hint_tendency = "low"
        elif profile.avg_hints_used < 1.5:
            hint_tendency = "medium"
        else:
            hint_tendency = "high"

        return {
            "user_level": user_level,
            "strong_topics": profile.strong_topics,
            "weak_topics": profile.weak_topics,
            "recent_topics": profile.recent_topics,
            "preferred_difficulty": profile.preferred_difficulty,
            "hint_tendency": hint_tendency,
            "total_attempts": profile.total_attempts,
            "correct_rate": profile.correct_rate,
            "streak_days": profile.streak_days,
        }

    def invalidate_cache(self, user_id: str):
        """사용자 캐시 무효화"""
        if user_id in self._profile_cache:
            del self._profile_cache[user_id]


# ============================================================
# Singleton Instance
# ============================================================

_personalization_service: Optional[PersonalizationService] = None


def get_personalization_service() -> PersonalizationService:
    """PersonalizationService 싱글톤 반환"""
    global _personalization_service
    if _personalization_service is None:
        _personalization_service = PersonalizationService()
    return _personalization_service
