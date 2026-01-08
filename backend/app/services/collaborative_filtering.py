"""
Collaborative Filtering Service

협업 필터링 기반 추천 서비스

Features:
1. 사용자 상호작용 로깅
2. 선호도 집계 및 업데이트
3. 유사 사용자 찾기
4. 협업 필터링 기반 추천
5. 🚀 A/B 테스팅 통합

Usage:
    service = get_collaborative_service()
    await service.log_interaction(user_id, "topic_select", {"topic": "dp"})
    recommendations = await service.get_recommendations(user_id)
"""

import logging
from typing import Dict, Any, Optional, List, TYPE_CHECKING
from datetime import datetime, timedelta
from dataclasses import dataclass

from ..database import get_supabase_client
from ..config import get_settings

if TYPE_CHECKING:
    from .ab_testing import ABTestingService
    from .pg_cache import PgCacheService

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class CollaborativeRecommendation:
    """협업 필터링 추천 결과"""
    topic: str
    difficulty: str
    score: float
    reason: str
    source: str  # "similar_user" | "popular" | "trending"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "topic": self.topic,
            "difficulty": self.difficulty,
            "score": self.score,
            "reason": self.reason,
            "source": self.source,
        }


@dataclass
class SimilarUser:
    """유사 사용자 정보"""
    user_id: str
    similarity_score: float
    common_topics: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "similarity_score": self.similarity_score,
            "common_topics": self.common_topics,
        }


class CollaborativeFilteringService:
    """
    협업 필터링 서비스

    Usage:
        service = get_collaborative_service()

        # 상호작용 로깅
        await service.log_interaction(
            user_id="...",
            interaction_type="topic_select",
            data={"topic": "dp", "difficulty": "medium"}
        )

        # 추천 받기
        recommendations = await service.get_recommendations(user_id)
    """

    # 상호작용 유형
    INTERACTION_TYPES = {
        "topic_select",      # 주제 선택
        "difficulty_select", # 난이도 선택
        "language_select",   # 언어 선택
        "problem_select",    # 문제 선택
        "problem_type_select",  # 문제 유형 선택 (blank/puzzle/guided)
        "hint_request",      # 힌트 요청
        "complete",          # 문제 완료
        "skip",              # 문제 스킵
        "feedback",          # 피드백 (좋아요/싫어요)
    }

    # 🚀 A/B 테스트 실험명
    AB_EXPERIMENT_NAME = "rec_algo_v2"

    def __init__(self):
        self.db = get_supabase_client()
        self._cache: Dict[str, tuple] = {}  # user_id -> (data, timestamp) - in-memory fallback
        self._cache_ttl = 300  # 5분 캐시
        self._ab_testing: Optional["ABTestingService"] = None
        self._pg_cache: Optional["PgCacheService"] = None

    def _get_pg_cache(self) -> Optional["PgCacheService"]:
        """PostgreSQL 캐시 서비스 lazy 초기화"""
        if self._pg_cache is None:
            try:
                from .pg_cache import get_pg_cache
                self._pg_cache = get_pg_cache()
            except Exception as e:
                logger.warning(f"[Collaborative] Failed to initialize PostgreSQL cache: {e}")
        return self._pg_cache

    def _get_ab_testing_service(self) -> Optional["ABTestingService"]:
        """A/B 테스팅 서비스 lazy 초기화"""
        if self._ab_testing is None:
            try:
                from .ab_testing import get_ab_testing_service
                self._ab_testing = get_ab_testing_service()
            except Exception as e:
                logger.warning(f"[Collaborative] Failed to initialize A/B testing: {e}")
        return self._ab_testing

    async def _get_algorithm_variant(self, user_id: str) -> str:
        """
        🚀 A/B 테스트를 통해 사용자에게 적용할 알고리즘 결정

        Returns:
            "basic" | "cosine_similarity"
        """
        ab_service = self._get_ab_testing_service()
        if not ab_service:
            return "cosine_similarity"  # A/B 서비스 없으면 기본값

        try:
            variant = await ab_service.get_variant(user_id, self.AB_EXPERIMENT_NAME)
            if variant:
                return variant.config.get("algorithm", "cosine_similarity")
        except Exception as e:
            logger.warning(f"[Collaborative] A/B variant lookup failed: {e}")

        return "cosine_similarity"

    async def _track_recommendation_event(
        self,
        user_id: str,
        event_type: str,
        event_data: Optional[Dict[str, Any]] = None,
    ):
        """🚀 추천 이벤트를 A/B 테스트에 기록"""
        ab_service = self._get_ab_testing_service()
        if ab_service:
            try:
                await ab_service.track_event(
                    user_id,
                    self.AB_EXPERIMENT_NAME,
                    event_type,
                    event_data,
                )
            except Exception as e:
                logger.debug(f"[Collaborative] A/B event tracking failed: {e}")

    async def track_recommendation_click(
        self,
        user_id: str,
        topic: str,
        difficulty: str,
    ):
        """
        🚀 추천 클릭 이벤트 기록 (A/B 테스트용)

        사용자가 추천을 클릭했을 때 호출
        """
        await self._track_recommendation_event(
            user_id,
            "click",
            {"topic": topic, "difficulty": difficulty}
        )

    async def track_recommendation_conversion(
        self,
        user_id: str,
        topic: str,
        difficulty: str,
        time_spent: Optional[float] = None,
        was_successful: bool = True,
    ):
        """
        🚀 추천 전환 이벤트 기록 (A/B 테스트용)

        사용자가 추천된 문제를 완료했을 때 호출
        """
        await self._track_recommendation_event(
            user_id,
            "conversion",
            {
                "topic": topic,
                "difficulty": difficulty,
                "time_spent": time_spent,
                "was_successful": was_successful,
            }
        )

    # ============================================================
    # 상호작용 로깅
    # ============================================================

    async def log_interaction(
        self,
        user_id: str,
        interaction_type: str,
        data: Dict[str, Any],
        session_id: Optional[str] = None,
        user_metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """
        사용자 상호작용 로깅

        Args:
            user_id: 사용자 ID
            interaction_type: 상호작용 유형
            data: 상호작용 데이터
            session_id: 세션 ID (선택)
            user_metadata: 사용자 메타데이터 (선택)

        Returns:
            interaction_id or None
        """
        if interaction_type not in self.INTERACTION_TYPES:
            logger.warning(f"[Collaborative] Unknown interaction type: {interaction_type}")

        try:
            result = self.db.table("user_interactions").insert({
                "user_id": user_id,
                "session_id": session_id,
                "interaction_type": interaction_type,
                "interaction_data": data,
                "user_metadata": user_metadata or {},
            }).execute()

            if result.data:
                interaction_id = result.data[0].get("id")
                logger.debug(f"[Collaborative] Logged interaction: {interaction_type} for {user_id}")

                # 비동기로 선호도 업데이트 (10회 상호작용마다)
                try:
                    count_result = self.db.table("user_interactions") \
                        .select("id", count="exact") \
                        .eq("user_id", user_id) \
                        .execute()
                    interaction_count = count_result.count or 0

                    # 10회마다 선호도 요약 업데이트 (성능 최적화)
                    if interaction_count > 0 and interaction_count % 10 == 0:
                        await self.update_user_preferences(user_id)
                        logger.info(f"[Collaborative] Updated preferences for {user_id} (interaction #{interaction_count})")
                except Exception as pref_err:
                    logger.warning(f"[Collaborative] Preferences update skipped: {pref_err}")

                return interaction_id

        except Exception as e:
            logger.error(f"[Collaborative] Failed to log interaction: {e}")

        return None

    # ============================================================
    # 선호도 집계
    # ============================================================

    async def update_user_preferences(self, user_id: str) -> bool:
        """
        사용자 선호도 집계 업데이트

        최근 30일간의 상호작용을 분석하여 선호도 요약 생성

        Args:
            user_id: 사용자 ID

        Returns:
            성공 여부
        """
        try:
            # 최근 상호작용 조회
            result = self.db.table("user_interactions") \
                .select("*") \
                .eq("user_id", user_id) \
                .gte("created_at", (datetime.now() - timedelta(days=30)).isoformat()) \
                .execute()

            interactions = result.data or []

            if not interactions:
                return False

            # 선호도 계산
            topic_counts: Dict[str, int] = {}
            difficulty_counts: Dict[str, int] = {}
            language_counts: Dict[str, int] = {}
            problem_type_counts: Dict[str, int] = {}

            total_hints = 0
            total_completes = 0
            total_skips = 0
            goal = None
            level = None

            for interaction in interactions:
                data = interaction.get("interaction_data", {})
                interaction_type = interaction.get("interaction_type", "")
                metadata = interaction.get("user_metadata", {})

                # 메타데이터 추출
                if not goal and metadata.get("goal"):
                    goal = metadata["goal"]
                if not level and metadata.get("level"):
                    level = metadata["level"]

                # 주제 카운트
                if topic := data.get("topic"):
                    topic_counts[topic] = topic_counts.get(topic, 0) + 1

                # 난이도 카운트
                if difficulty := data.get("difficulty"):
                    difficulty_counts[difficulty] = difficulty_counts.get(difficulty, 0) + 1

                # 언어 카운트
                if language := data.get("language"):
                    language_counts[language] = language_counts.get(language, 0) + 1

                # 문제 유형 카운트
                if problem_type := data.get("problem_type"):
                    problem_type_counts[problem_type] = problem_type_counts.get(problem_type, 0) + 1

                # 통계
                if interaction_type == "hint_request":
                    total_hints += 1
                elif interaction_type == "complete":
                    total_completes += 1
                elif interaction_type == "skip":
                    total_skips += 1

            # 정규화 (비율로 변환)
            def normalize(counts: Dict[str, int]) -> Dict[str, float]:
                total = sum(counts.values())
                if total == 0:
                    return {}
                return {k: round(v / total, 3) for k, v in counts.items()}

            topic_prefs = normalize(topic_counts)
            difficulty_prefs = normalize(difficulty_counts)
            language_prefs = normalize(language_counts)
            problem_type_prefs = normalize(problem_type_counts)

            # 학습 패턴
            total_problems = total_completes + total_skips
            learning_pattern = {
                "hint_usage_rate": round(total_hints / max(total_problems, 1), 2),
                "completion_rate": round(total_completes / max(total_problems, 1), 2),
                "total_interactions": len(interactions),
            }

            # 유사 사용자 찾기
            similar_users = await self._find_similar_users_internal(user_id, topic_prefs, goal, level)

            # Upsert
            upsert_data = {
                "user_id": user_id,
                "topic_preferences": topic_prefs,
                "difficulty_preferences": difficulty_prefs,
                "language_preferences": language_prefs,
                "problem_type_preferences": problem_type_prefs,
                "learning_pattern": learning_pattern,
                "goal": goal,
                "level": level,
                "similar_users": [su.to_dict() for su in similar_users],
                "updated_at": datetime.now().isoformat(),
            }

            self.db.table("user_preferences_summary").upsert(upsert_data).execute()

            # 캐시 무효화
            if user_id in self._cache:
                del self._cache[user_id]

            logger.info(f"[Collaborative] Updated preferences for {user_id}")
            return True

        except Exception as e:
            logger.error(f"[Collaborative] Failed to update preferences: {e}")
            return False

    def _cosine_similarity(self, vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
        """
        두 선호도 벡터 간의 코사인 유사도 계산

        코사인 유사도 = (A·B) / (||A|| * ||B||)
        """
        if not vec1 or not vec2:
            return 0.0

        # 공통 키 찾기
        common_keys = set(vec1.keys()) & set(vec2.keys())
        if not common_keys:
            return 0.0

        # 내적 계산
        dot_product = sum(vec1[k] * vec2[k] for k in common_keys)

        # 노름(크기) 계산
        norm1 = sum(v ** 2 for v in vec1.values()) ** 0.5
        norm2 = sum(v ** 2 for v in vec2.values()) ** 0.5

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def _jaccard_similarity(self, set1: set, set2: set) -> float:
        """
        Jaccard 유사도 = |A ∩ B| / |A ∪ B|
        집합 기반 유사도 (주제 겹침)
        """
        if not set1 or not set2:
            return 0.0

        intersection = len(set1 & set2)
        union = len(set1 | set2)

        return intersection / union if union > 0 else 0.0

    async def _find_similar_users_internal(
        self,
        user_id: str,
        topic_prefs: Dict[str, float],
        goal: Optional[str],
        level: Optional[str],
        limit: int = 10,
    ) -> List[SimilarUser]:
        """
        🚀 개선된 유사 사용자 찾기 (Matrix Factorization 대체)

        사용 알고리즘:
        1. 코사인 유사도: 주제 선호도 벡터 비교 (40%)
        2. Jaccard 유사도: 주제 집합 겹침 (20%)
        3. 메타데이터 매칭: 목표/레벨 일치 (30%)
        4. 활동량 가중치: 상호작용 많은 사용자 우선 (10%)
        """
        try:
            # 다른 사용자 선호도 조회 (학습 패턴 포함)
            result = self.db.table("user_preferences_summary") \
                .select("user_id, topic_preferences, difficulty_preferences, goal, level, learning_pattern") \
                .neq("user_id", user_id) \
                .limit(200) \
                .execute()

            other_users = result.data or []
            similar_users = []

            my_topics_set = set(topic_prefs.keys())

            for other in other_users:
                other_id = other.get("user_id")
                other_topics = other.get("topic_preferences", {})
                other_difficulty = other.get("difficulty_preferences", {})
                other_goal = other.get("goal")
                other_level = other.get("level")
                other_pattern = other.get("learning_pattern", {})

                # ============================================================
                # 1. 코사인 유사도 (주제 선호도 벡터) - 40%
                # ============================================================
                topic_cosine = self._cosine_similarity(topic_prefs, other_topics)

                # ============================================================
                # 2. Jaccard 유사도 (주제 집합 겹침) - 20%
                # ============================================================
                other_topics_set = set(other_topics.keys())
                topic_jaccard = self._jaccard_similarity(my_topics_set, other_topics_set)

                # ============================================================
                # 3. 메타데이터 매칭 - 30%
                # ============================================================
                metadata_score = 0.0

                # 목표 일치 (15%)
                if goal and other_goal == goal:
                    metadata_score += 0.5

                # 레벨 일치 또는 인접 (15%)
                level_order = ["beginner", "elementary", "intermediate", "advanced"]
                if level and other_level:
                    try:
                        my_idx = level_order.index(level)
                        other_idx = level_order.index(other_level)
                        level_diff = abs(my_idx - other_idx)
                        if level_diff == 0:
                            metadata_score += 0.5  # 정확히 일치
                        elif level_diff == 1:
                            metadata_score += 0.3  # 인접 레벨
                    except ValueError:
                        pass

                # ============================================================
                # 4. 활동량 가중치 (신뢰도) - 10%
                # ============================================================
                total_interactions = other_pattern.get("total_interactions", 0)
                activity_score = min(total_interactions / 50, 1.0)  # 50개 이상이면 최대점

                # ============================================================
                # 최종 유사도 계산 (가중 평균)
                # ============================================================
                final_score = (
                    topic_cosine * 0.40 +
                    topic_jaccard * 0.20 +
                    metadata_score * 0.30 +
                    activity_score * 0.10
                )

                common_topics = list(my_topics_set & other_topics_set)

                if final_score > 0.2:  # 최소 유사도 임계값
                    similar_users.append(SimilarUser(
                        user_id=other_id,
                        similarity_score=round(final_score, 3),
                        common_topics=common_topics,
                    ))

            # 유사도 순 정렬
            similar_users.sort(key=lambda x: x.similarity_score, reverse=True)
            logger.debug(f"[Collaborative] Found {len(similar_users)} similar users for {user_id}")
            return similar_users[:limit]

        except Exception as e:
            logger.error(f"[Collaborative] Failed to find similar users: {e}")
            return []

    # ============================================================
    # 협업 필터링 추천
    # ============================================================

    def _temporal_decay(self, days_ago: float, half_life: float = 7.0) -> float:
        """
        시간 감쇠 함수 (지수 감쇠)

        최근 상호작용에 더 높은 가중치 부여
        half_life: 가중치가 절반이 되는 일수 (기본 7일)
        """
        import math
        return math.exp(-0.693 * days_ago / half_life)  # ln(2) ≈ 0.693

    def _sample_with_diversity(
        self,
        recommendations: List[CollaborativeRecommendation],
        limit: int,
        top_n_multiplier: int = 3,
    ) -> List[CollaborativeRecommendation]:
        """
        🚀 다양성을 위한 Top-N 샘플링

        항상 정확히 Top-K를 반환하는 대신,
        Top-N (N = K * multiplier) 에서 가중치 랜덤 샘플링

        이를 통해:
        1. 매번 다른 추천 제공 (신선함)
        2. 높은 점수 문제는 여전히 높은 확률로 선택
        3. 낮은 점수 문제도 가끔 노출 (탐색)

        Args:
            recommendations: 점수순 정렬된 추천 목록
            limit: 반환할 추천 수
            top_n_multiplier: Top-N 계산용 배수 (기본 3 = Top 15에서 5개 샘플링)

        Returns:
            다양성이 적용된 추천 목록
        """
        import random

        if len(recommendations) <= limit:
            return recommendations

        # Top-N 풀에서 샘플링 (N = limit * multiplier)
        pool_size = min(len(recommendations), limit * top_n_multiplier)
        candidate_pool = recommendations[:pool_size]

        # 점수 기반 가중치 계산 (softmax-like)
        # score가 높을수록 선택 확률 높음
        scores = [max(r.score, 0.01) for r in candidate_pool]  # 최소 0.01
        total_score = sum(scores)
        weights = [s / total_score for s in scores]

        # 가중치 기반 샘플링 (중복 없이)
        selected = []
        remaining_pool = list(zip(candidate_pool, weights))

        for _ in range(min(limit, len(remaining_pool))):
            if not remaining_pool:
                break

            # 가중치 기반 선택
            items, probs = zip(*remaining_pool)
            # 정규화
            total = sum(probs)
            normalized_probs = [p / total for p in probs]

            # 랜덤 선택
            r = random.random()
            cumsum = 0
            chosen_idx = 0
            for i, prob in enumerate(normalized_probs):
                cumsum += prob
                if r <= cumsum:
                    chosen_idx = i
                    break

            selected.append(items[chosen_idx])
            remaining_pool.pop(chosen_idx)

        logger.debug(f"[Collaborative] Sampled {len(selected)} from top {pool_size} with diversity")
        return selected

    async def get_recommendations(
        self,
        user_id: str,
        limit: int = 5,
    ) -> List[CollaborativeRecommendation]:
        """
        🚀 개선된 협업 필터링 기반 추천

        개선점:
        1. 시간 감쇠 (최근 상호작용 우선)
        2. 완료율 기반 가중치 (성공한 문제 우선)
        3. 다양성 보장 (같은 주제 중복 방지)
        4. 트렌딩 주제 혼합
        5. 🚀 A/B 테스팅 (알고리즘 선택)

        Args:
            user_id: 사용자 ID
            limit: 최대 추천 수

        Returns:
            추천 목록
        """
        try:
            # 🚀 A/B 테스트: 알고리즘 변형 결정
            algorithm = await self._get_algorithm_variant(user_id)
            logger.debug(f"[Collaborative] Using algorithm: {algorithm} for user {user_id}")

            # 🚀 PostgreSQL 캐시 확인 (우선)
            pg_cache = self._get_pg_cache()
            if pg_cache and pg_cache.is_available:
                cached = await pg_cache.get_recommendations(user_id, algorithm)
                if cached:
                    logger.debug(f"[Collaborative] PostgreSQL cache HIT for {user_id}")
                    # Dict -> CollaborativeRecommendation 변환
                    return [CollaborativeRecommendation(**r) for r in cached[:limit]]

            # In-memory 캐시 확인 (폴백)
            cache_key = f"{user_id}:{algorithm}"
            if cache_key in self._cache:
                data, cached_at = self._cache[cache_key]
                if datetime.now().timestamp() - cached_at < self._cache_ttl:
                    return data[:limit]

            # 유사 사용자 조회
            prefs_result = self.db.table("user_preferences_summary") \
                .select("similar_users, topic_preferences, difficulty_preferences") \
                .eq("user_id", user_id) \
                .single() \
                .execute()

            if not prefs_result.data:
                # 선호도 없으면 인기 추천 + 트렌딩 혼합
                popular = await self._get_popular_recommendations(limit - 1)
                trending = await self._get_trending_recommendations(1)
                return popular + trending

            similar_users = prefs_result.data.get("similar_users", [])
            my_topics = set(prefs_result.data.get("topic_preferences", {}).keys())
            my_difficulty_prefs = prefs_result.data.get("difficulty_preferences", {})

            if not similar_users:
                popular = await self._get_popular_recommendations(limit - 1)
                trending = await self._get_trending_recommendations(1)
                return popular + trending

            # 유사 사용자들의 최근 상호작용 조회 (created_at 포함)
            similar_user_ids = [su.get("user_id") for su in similar_users[:10]]

            interactions_result = self.db.table("user_interactions") \
                .select("user_id, interaction_data, interaction_type, created_at") \
                .in_("user_id", similar_user_ids) \
                .in_("interaction_type", ["complete", "problem_select", "skip"]) \
                .gte("created_at", (datetime.now() - timedelta(days=30)).isoformat()) \
                .order("created_at", desc=True) \
                .limit(200) \
                .execute()

            interactions = interactions_result.data or []

            # 주제/난이도 점수 집계 (시간 감쇠 + 완료 가중치 적용)
            topic_scores: Dict[str, Dict[str, float]] = {}  # topic -> {difficulty -> score}
            topic_success_rate: Dict[str, tuple] = {}  # topic -> (success_count, total_count)

            user_similarity_map = {su.get("user_id"): su.get("similarity_score", 0) for su in similar_users}
            now = datetime.now()

            for interaction in interactions:
                data = interaction.get("interaction_data", {})
                topic = data.get("topic")
                difficulty = data.get("difficulty", "medium")
                interaction_user_id = interaction.get("user_id")
                interaction_type = interaction.get("interaction_type")
                created_at_str = interaction.get("created_at")

                if not topic:
                    continue

                # 이미 내가 많이 푼 주제는 제외 (새로운 주제 추천)
                if topic in my_topics:
                    continue

                similarity = user_similarity_map.get(interaction_user_id, 0)

                # 시간 감쇠 계산
                decay = 1.0
                if created_at_str:
                    try:
                        created_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
                        days_ago = (now - created_at.replace(tzinfo=None)).days
                        decay = self._temporal_decay(days_ago)
                    except (ValueError, TypeError):
                        pass

                # 완료 가중치 (complete > select > skip)
                type_weight = {"complete": 1.5, "problem_select": 1.0, "skip": 0.3}.get(interaction_type, 1.0)

                # 점수 = 유사도 × 시간감쇠 × 완료가중치
                score = similarity * decay * type_weight

                if topic not in topic_scores:
                    topic_scores[topic] = {}
                if difficulty not in topic_scores[topic]:
                    topic_scores[topic][difficulty] = 0

                topic_scores[topic][difficulty] += score

                # 성공률 추적
                if topic not in topic_success_rate:
                    topic_success_rate[topic] = (0, 0)
                success, total = topic_success_rate[topic]
                if interaction_type == "complete":
                    topic_success_rate[topic] = (success + 1, total + 1)
                elif interaction_type == "skip":
                    topic_success_rate[topic] = (success, total + 1)

            # 추천 생성
            recommendations = []
            for topic, difficulties in topic_scores.items():
                best_difficulty = max(difficulties.items(), key=lambda x: x[1])

                # 성공률 기반 이유 생성
                success, total = topic_success_rate.get(topic, (0, 0))
                success_rate = success / total if total > 0 else 0

                if success_rate > 0.7:
                    reason = f"비슷한 사용자들이 {int(success_rate*100)}% 성공한 주제예요"
                elif success_rate > 0.4:
                    reason = "비슷한 사용자들이 풀고 있는 주제예요"
                else:
                    reason = "도전적인 주제예요 (성공률 낮음)"

                recommendations.append(CollaborativeRecommendation(
                    topic=topic,
                    difficulty=best_difficulty[0],
                    score=best_difficulty[1],
                    reason=reason,
                    source="similar_user",
                ))

            # 점수순 정렬
            recommendations.sort(key=lambda x: x.score, reverse=True)

            # 🚀 다양성 강화: Top-N에서 랜덤 샘플링 (매번 다른 추천)
            recommendations = self._sample_with_diversity(recommendations, limit)

            # 🚀 PostgreSQL 캐시 저장 (우선)
            if pg_cache and pg_cache.is_available:
                await pg_cache.set_recommendations(user_id, recommendations, algorithm)
                logger.debug(f"[Collaborative] PostgreSQL cache SET for {user_id}")
            else:
                # In-memory 캐시 저장 (폴백)
                self._cache[cache_key] = (recommendations, datetime.now().timestamp())

            # 🚀 A/B 테스트: impression 이벤트 기록
            await self._track_recommendation_event(
                user_id,
                "impression",
                {
                    "algorithm": algorithm,
                    "recommendation_count": len(recommendations[:limit]),
                    "topics": [r.topic for r in recommendations[:limit]],
                }
            )

            return recommendations[:limit]

        except Exception as e:
            logger.error(f"[Collaborative] Failed to get recommendations: {e}")
            return await self._get_popular_recommendations(limit)

    async def _get_trending_recommendations(self, limit: int) -> List[CollaborativeRecommendation]:
        """
        🚀 트렌딩 추천 (최근 급상승 주제)

        최근 3일간 상호작용 증가율이 높은 주제 추천
        """
        try:
            # 최근 3일
            recent_result = self.db.table("user_interactions") \
                .select("interaction_data") \
                .in_("interaction_type", ["complete", "problem_select"]) \
                .gte("created_at", (datetime.now() - timedelta(days=3)).isoformat()) \
                .limit(300) \
                .execute()

            # 이전 7일 (3~10일 전)
            previous_result = self.db.table("user_interactions") \
                .select("interaction_data") \
                .in_("interaction_type", ["complete", "problem_select"]) \
                .gte("created_at", (datetime.now() - timedelta(days=10)).isoformat()) \
                .lt("created_at", (datetime.now() - timedelta(days=3)).isoformat()) \
                .limit(300) \
                .execute()

            recent_interactions = recent_result.data or []
            previous_interactions = previous_result.data or []

            # 주제별 카운트
            recent_counts: Dict[str, int] = {}
            previous_counts: Dict[str, int] = {}

            for interaction in recent_interactions:
                topic = interaction.get("interaction_data", {}).get("topic")
                if topic:
                    recent_counts[topic] = recent_counts.get(topic, 0) + 1

            for interaction in previous_interactions:
                topic = interaction.get("interaction_data", {}).get("topic")
                if topic:
                    previous_counts[topic] = previous_counts.get(topic, 0) + 1

            # 증가율 계산
            trending_scores = []
            for topic, recent_count in recent_counts.items():
                prev_count = previous_counts.get(topic, 1)  # 0 방지
                # 증가율 = (최근 - 이전) / 이전 * 100
                growth_rate = (recent_count - prev_count) / max(prev_count, 1)
                if growth_rate > 0.2:  # 20% 이상 증가한 주제만
                    trending_scores.append((topic, growth_rate, recent_count))

            # 증가율 순 정렬
            trending_scores.sort(key=lambda x: (x[1], x[2]), reverse=True)

            recommendations = []
            for topic, growth_rate, count in trending_scores[:limit]:
                recommendations.append(CollaborativeRecommendation(
                    topic=topic,
                    difficulty="medium",
                    score=growth_rate,
                    reason=f"최근 인기 급상승 📈 (+{int(growth_rate*100)}%)",
                    source="trending",
                ))

            return recommendations

        except Exception as e:
            logger.error(f"[Collaborative] Trending recommendations failed: {e}")
            return []

    async def _get_popular_recommendations(self, limit: int) -> List[CollaborativeRecommendation]:
        """인기 기반 폴백 추천"""
        # 전체 상호작용에서 인기 주제 추출
        try:
            result = self.db.table("user_interactions") \
                .select("interaction_data") \
                .in_("interaction_type", ["complete", "problem_select"]) \
                .gte("created_at", (datetime.now() - timedelta(days=7)).isoformat()) \
                .limit(500) \
                .execute()

            interactions = result.data or []
            topic_counts: Dict[str, int] = {}

            for interaction in interactions:
                topic = interaction.get("interaction_data", {}).get("topic")
                if topic:
                    topic_counts[topic] = topic_counts.get(topic, 0) + 1

            if not topic_counts:
                # 하드코딩 폴백
                return [
                    CollaborativeRecommendation("dp", "medium", 1.0, "인기 주제", "popular"),
                    CollaborativeRecommendation("graph", "medium", 0.9, "인기 주제", "popular"),
                ]

            recommendations = []
            sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)

            for topic, count in sorted_topics[:limit]:
                recommendations.append(CollaborativeRecommendation(
                    topic=topic,
                    difficulty="medium",
                    score=count / max(len(interactions), 1),
                    reason="이번 주 인기 주제예요",
                    source="popular",
                ))

            return recommendations

        except Exception as e:
            logger.error(f"[Collaborative] Popular recommendations failed: {e}")
            return []

    # ============================================================
    # 유틸리티
    # ============================================================

    async def get_user_preferences(self, user_id: str) -> Optional[Dict[str, Any]]:
        """사용자 선호도 조회"""
        try:
            result = self.db.table("user_preferences_summary") \
                .select("*") \
                .eq("user_id", user_id) \
                .single() \
                .execute()

            return result.data

        except Exception:
            return None

    async def invalidate_cache(self, user_id: str):
        """캐시 무효화 (PostgreSQL + In-memory)"""
        # PostgreSQL 캐시 무효화
        pg_cache = self._get_pg_cache()
        if pg_cache and pg_cache.is_available:
            await pg_cache.invalidate_recommendations(user_id)

        # In-memory 캐시 무효화 (알고리즘별 키 모두 삭제)
        keys_to_delete = [k for k in self._cache if k.startswith(f"{user_id}:")]
        for key in keys_to_delete:
            del self._cache[key]


# ============================================================
# Singleton Instance
# ============================================================

_collaborative_service: Optional[CollaborativeFilteringService] = None


def get_collaborative_service() -> CollaborativeFilteringService:
    """CollaborativeFilteringService 싱글톤 반환"""
    global _collaborative_service
    if _collaborative_service is None:
        _collaborative_service = CollaborativeFilteringService()
    return _collaborative_service
