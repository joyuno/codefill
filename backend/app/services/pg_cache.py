"""
PostgreSQL Caching Service

PostgreSQL 기반 캐싱 서비스 (Redis 대체)

Features:
1. 추천 결과 캐싱
2. 사용자 선호도 캐싱
3. A/B 테스트 할당 캐싱
4. 자동 TTL 관리 (expires_at)

장점:
- 추가 인프라 불필요 (Supabase 재활용)
- 서버 재시작해도 캐시 유지
- 단일 트랜잭션으로 캐시 + 데이터 동시 처리 가능

Usage:
    cache = get_pg_cache()
    await cache.set_recommendations(user_id, recommendations)
    cached = await cache.get_recommendations(user_id)
"""

import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import asdict

from ..database import get_supabase_client
from ..config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class PgCacheService:
    """
    PostgreSQL 캐싱 서비스

    Usage:
        cache = get_pg_cache()

        # 추천 캐싱
        await cache.set_recommendations(user_id, recommendations, algorithm="cosine")
        recommendations = await cache.get_recommendations(user_id, algorithm="cosine")

        # 선호도 캐싱
        await cache.set_user_preferences(user_id, preferences)
        preferences = await cache.get_user_preferences(user_id)

        # A/B 테스트 할당 캐싱
        await cache.set_ab_assignment(user_id, experiment, variant)
        variant = await cache.get_ab_assignment(user_id, experiment)
    """

    # 캐시 키 프리픽스
    PREFIX_RECOMMENDATIONS = "cf:rec:"
    PREFIX_PREFERENCES = "cf:pref:"
    PREFIX_AB_ASSIGNMENT = "ab:assign:"
    PREFIX_TRENDING = "cf:trending"
    PREFIX_POPULAR = "cf:popular"

    # 기본 TTL (초)
    DEFAULT_TTL_RECOMMENDATIONS = 300  # 5분
    DEFAULT_TTL_PREFERENCES = 600  # 10분
    DEFAULT_TTL_AB_ASSIGNMENT = 86400  # 24시간
    DEFAULT_TTL_TRENDING = 300  # 5분

    def __init__(self):
        self.db = get_supabase_client()

    @property
    def is_available(self) -> bool:
        """캐시 사용 가능 여부 (항상 True - PostgreSQL은 항상 사용 가능)"""
        return True

    # ============================================================
    # 범용 캐시 메서드
    # ============================================================

    async def _get(self, key: str) -> Optional[Any]:
        """캐시 조회 (내부용)"""
        try:
            result = self.db.rpc("cache_get", {"p_key": key}).execute()
            if result.data:
                return result.data
            return None
        except Exception as e:
            # RPC가 없으면 직접 쿼리
            try:
                result = self.db.table("cache") \
                    .select("value") \
                    .eq("key", key) \
                    .gt("expires_at", datetime.now().isoformat()) \
                    .single() \
                    .execute()
                if result.data:
                    return result.data.get("value")
            except Exception:
                pass
            logger.debug(f"[PgCache] Get failed for {key}: {e}")
            return None

    async def _set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """캐시 저장 (내부용)"""
        try:
            # JSON 직렬화
            if hasattr(value, 'to_dict'):
                json_value = value.to_dict()
            elif hasattr(value, '__dataclass_fields__'):
                json_value = asdict(value)
            else:
                json_value = value

            result = self.db.rpc("cache_set", {
                "p_key": key,
                "p_value": json_value,
                "p_ttl_seconds": ttl,
            }).execute()
            return True
        except Exception as e:
            # RPC가 없으면 직접 UPSERT
            try:
                from datetime import timedelta
                expires_at = (datetime.now() + timedelta(seconds=ttl)).isoformat()
                self.db.table("cache").upsert({
                    "key": key,
                    "value": json_value,
                    "expires_at": expires_at,
                    "updated_at": datetime.now().isoformat(),
                }).execute()
                return True
            except Exception as inner_e:
                logger.debug(f"[PgCache] Set failed for {key}: {inner_e}")
                return False

    async def _delete(self, key: str) -> bool:
        """캐시 삭제 (내부용)"""
        try:
            self.db.table("cache").delete().eq("key", key).execute()
            return True
        except Exception as e:
            logger.debug(f"[PgCache] Delete failed for {key}: {e}")
            return False

    async def _delete_pattern(self, pattern: str) -> int:
        """패턴 매칭 삭제 (예: 'cf:rec:user123:%')"""
        try:
            result = self.db.rpc("cache_delete_pattern", {"p_pattern": pattern}).execute()
            return result.data if result.data else 0
        except Exception as e:
            # RPC가 없으면 직접 삭제
            try:
                # LIKE 패턴으로 변환 (% -> 와일드카드)
                self.db.table("cache").delete().like("key", pattern).execute()
                return 1  # 정확한 카운트 불가
            except Exception:
                pass
            logger.debug(f"[PgCache] Delete pattern failed for {pattern}: {e}")
            return 0

    # ============================================================
    # 추천 캐싱
    # ============================================================

    async def get_recommendations(
        self,
        user_id: str,
        algorithm: str = "default",
    ) -> Optional[List[Dict[str, Any]]]:
        """캐시된 추천 조회"""
        key = f"{self.PREFIX_RECOMMENDATIONS}{user_id}:{algorithm}"
        cached = await self._get(key)
        if cached:
            logger.debug(f"[PgCache] HIT recommendations for {user_id}")
            return cached
        return None

    async def set_recommendations(
        self,
        user_id: str,
        recommendations: List[Any],
        algorithm: str = "default",
        ttl: Optional[int] = None,
    ) -> bool:
        """추천 결과 캐싱"""
        key = f"{self.PREFIX_RECOMMENDATIONS}{user_id}:{algorithm}"
        # dataclass -> dict 변환
        data = [
            r.to_dict() if hasattr(r, 'to_dict') else (asdict(r) if hasattr(r, '__dataclass_fields__') else r)
            for r in recommendations
        ]
        success = await self._set(key, data, ttl or self.DEFAULT_TTL_RECOMMENDATIONS)
        if success:
            logger.debug(f"[PgCache] SET recommendations for {user_id}")
        return success

    async def invalidate_recommendations(self, user_id: str) -> bool:
        """사용자 추천 캐시 무효화"""
        pattern = f"{self.PREFIX_RECOMMENDATIONS}{user_id}:%"
        count = await self._delete_pattern(pattern)
        logger.debug(f"[PgCache] Invalidated {count} recommendation keys for {user_id}")
        return count > 0

    # ============================================================
    # 선호도 캐싱
    # ============================================================

    async def get_user_preferences(self, user_id: str) -> Optional[Dict[str, Any]]:
        """캐시된 사용자 선호도 조회"""
        key = f"{self.PREFIX_PREFERENCES}{user_id}"
        cached = await self._get(key)
        if cached:
            logger.debug(f"[PgCache] HIT preferences for {user_id}")
        return cached

    async def set_user_preferences(
        self,
        user_id: str,
        preferences: Dict[str, Any],
        ttl: Optional[int] = None,
    ) -> bool:
        """사용자 선호도 캐싱"""
        key = f"{self.PREFIX_PREFERENCES}{user_id}"
        success = await self._set(key, preferences, ttl or self.DEFAULT_TTL_PREFERENCES)
        if success:
            logger.debug(f"[PgCache] SET preferences for {user_id}")
        return success

    async def invalidate_user_preferences(self, user_id: str) -> bool:
        """사용자 선호도 캐시 무효화"""
        key = f"{self.PREFIX_PREFERENCES}{user_id}"
        return await self._delete(key)

    # ============================================================
    # A/B 테스트 할당 캐싱
    # ============================================================

    async def get_ab_assignment(
        self,
        user_id: str,
        experiment_name: str,
    ) -> Optional[str]:
        """캐시된 A/B 테스트 할당 조회"""
        key = f"{self.PREFIX_AB_ASSIGNMENT}{user_id}:{experiment_name}"
        return await self._get(key)

    async def set_ab_assignment(
        self,
        user_id: str,
        experiment_name: str,
        variant_name: str,
        ttl: int = 86400,  # 24시간
    ) -> bool:
        """A/B 테스트 할당 캐싱"""
        key = f"{self.PREFIX_AB_ASSIGNMENT}{user_id}:{experiment_name}"
        return await self._set(key, variant_name, ttl)

    # ============================================================
    # 트렌딩/인기 캐싱
    # ============================================================

    async def get_trending(self) -> Optional[List[Dict[str, Any]]]:
        """캐시된 트렌딩 주제 조회"""
        return await self._get(self.PREFIX_TRENDING)

    async def set_trending(
        self,
        trending: List[Any],
        ttl: int = 300,
    ) -> bool:
        """트렌딩 주제 캐싱"""
        data = [
            r.to_dict() if hasattr(r, 'to_dict') else (asdict(r) if hasattr(r, '__dataclass_fields__') else r)
            for r in trending
        ]
        return await self._set(self.PREFIX_TRENDING, data, ttl)

    async def get_popular(self) -> Optional[List[Dict[str, Any]]]:
        """캐시된 인기 주제 조회"""
        return await self._get(self.PREFIX_POPULAR)

    async def set_popular(
        self,
        popular: List[Any],
        ttl: int = 300,
    ) -> bool:
        """인기 주제 캐싱"""
        data = [
            r.to_dict() if hasattr(r, 'to_dict') else (asdict(r) if hasattr(r, '__dataclass_fields__') else r)
            for r in popular
        ]
        return await self._set(self.PREFIX_POPULAR, data, ttl)

    # ============================================================
    # 유틸리티
    # ============================================================

    async def cleanup_expired(self) -> int:
        """만료된 캐시 정리"""
        try:
            result = self.db.rpc("cache_cleanup").execute()
            count = result.data if result.data else 0
            logger.info(f"[PgCache] Cleaned up {count} expired entries")
            return count
        except Exception as e:
            # RPC가 없으면 직접 삭제
            try:
                self.db.table("cache").delete().lt("expires_at", datetime.now().isoformat()).execute()
                return 0  # 정확한 카운트 불가
            except Exception:
                pass
            logger.debug(f"[PgCache] Cleanup failed: {e}")
            return 0

    async def health_check(self) -> Dict[str, Any]:
        """캐시 상태 확인"""
        try:
            # 캐시 테이블 통계
            result = self.db.table("cache").select("key", count="exact").execute()
            total_count = result.count if hasattr(result, 'count') else len(result.data or [])

            return {
                "status": "healthy",
                "type": "postgresql",
                "total_entries": total_count,
            }
        except Exception as e:
            return {
                "status": "error",
                "type": "postgresql",
                "error": str(e),
            }


# ============================================================
# Singleton Instance
# ============================================================

_pg_cache: Optional[PgCacheService] = None


def get_pg_cache() -> PgCacheService:
    """PgCacheService 싱글톤 반환"""
    global _pg_cache
    if _pg_cache is None:
        _pg_cache = PgCacheService()
    return _pg_cache
