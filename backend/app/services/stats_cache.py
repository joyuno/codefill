"""
User Stats & Interactions Cache Service

인메모리 캐시로 자주 업데이트되는 데이터를 담아뒀다가 배치로 DB에 저장

Features:
1. user_stats 변경사항 누적 후 배치 업데이트
2. user_interactions 배치 삽입
3. daily_activity 배치 업데이트
4. 주기적 flush (30초) 또는 임계값 도달 시 flush

Usage:
    cache = get_stats_cache()

    # 개별 이벤트 (캐시에 누적)
    await cache.increment_xp(user_id, 10)
    await cache.increment_problems_solved(user_id)
    await cache.log_interaction(user_id, "click", {...})

    # 배치 이벤트 (프론트엔드에서 모아서 전송)
    await cache.log_interactions_batch(user_id, [...])

    # 수동 flush
    await cache.flush_user(user_id)
    await cache.flush_all()
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, date
from dataclasses import dataclass, field
from collections import defaultdict

from ..database import get_supabase_client

logger = logging.getLogger(__name__)


# ============================================================
# Data Classes
# ============================================================

@dataclass
class UserStatsDelta:
    """사용자 통계 변경분"""
    xp_delta: int = 0
    problems_solved_delta: int = 0
    hints_used_delta: int = 0
    seeds_delta: int = 0
    time_spent_delta: int = 0  # seconds
    last_updated: datetime = field(default_factory=datetime.now)

    def is_empty(self) -> bool:
        return (
            self.xp_delta == 0 and
            self.problems_solved_delta == 0 and
            self.hints_used_delta == 0 and
            self.seeds_delta == 0 and
            self.time_spent_delta == 0
        )


@dataclass
class DailyActivityDelta:
    """일별 활동 변경분"""
    date: date
    problems_solved_delta: int = 0
    xp_earned_delta: int = 0
    time_spent_delta: int = 0  # seconds
    hints_used_delta: int = 0

    def is_empty(self) -> bool:
        return (
            self.problems_solved_delta == 0 and
            self.xp_earned_delta == 0 and
            self.time_spent_delta == 0 and
            self.hints_used_delta == 0
        )


# ============================================================
# Stats Cache Service
# ============================================================

class StatsCacheService:
    """
    인메모리 통계 캐시 서비스

    - user_stats 변경분을 누적 후 배치 업데이트
    - user_interactions를 배치 삽입
    - 주기적 flush (30초) 또는 버퍼 크기 초과 시 flush
    """

    # 설정
    FLUSH_INTERVAL_SECONDS = 30  # 자동 flush 간격
    MAX_INTERACTIONS_BUFFER = 50  # 인터랙션 버퍼 최대 크기
    MAX_USERS_BUFFER = 20  # 유저 버퍼 최대 크기

    def __init__(self):
        self.db = get_supabase_client()

        # 인메모리 버퍼
        self._stats_deltas: Dict[str, UserStatsDelta] = {}
        self._daily_deltas: Dict[str, DailyActivityDelta] = {}  # key: "user_id:date"
        self._interactions_buffer: List[Dict[str, Any]] = []

        # 백그라운드 태스크
        self._flush_task: Optional[asyncio.Task] = None
        self._lock = asyncio.Lock()

    # ============================================================
    # Stats Increment (누적)
    # ============================================================

    async def increment_xp(self, user_id: str, amount: int) -> None:
        """XP 증가 (캐시에 누적)"""
        async with self._lock:
            delta = self._get_or_create_delta(user_id)
            delta.xp_delta += amount
            delta.last_updated = datetime.now()

            # 일별 활동도 업데이트
            daily = self._get_or_create_daily(user_id, date.today())
            daily.xp_earned_delta += amount

        await self._check_flush_needed()

    async def increment_problems_solved(self, user_id: str, count: int = 1) -> None:
        """풀이 완료 수 증가 (캐시에 누적)"""
        async with self._lock:
            delta = self._get_or_create_delta(user_id)
            delta.problems_solved_delta += count
            delta.last_updated = datetime.now()

            daily = self._get_or_create_daily(user_id, date.today())
            daily.problems_solved_delta += count

        await self._check_flush_needed()

    async def increment_hints_used(self, user_id: str, count: int = 1) -> None:
        """힌트 사용 수 증가 (캐시에 누적)"""
        async with self._lock:
            delta = self._get_or_create_delta(user_id)
            delta.hints_used_delta += count
            delta.last_updated = datetime.now()

            daily = self._get_or_create_daily(user_id, date.today())
            daily.hints_used_delta += count

        await self._check_flush_needed()

    async def increment_seeds(self, user_id: str, amount: int) -> None:
        """씨앗 증가 (캐시에 누적)"""
        async with self._lock:
            delta = self._get_or_create_delta(user_id)
            delta.seeds_delta += amount
            delta.last_updated = datetime.now()

        await self._check_flush_needed()

    async def increment_time_spent(self, user_id: str, seconds: int) -> None:
        """학습 시간 증가 (캐시에 누적)"""
        async with self._lock:
            delta = self._get_or_create_delta(user_id)
            delta.time_spent_delta += seconds
            delta.last_updated = datetime.now()

            daily = self._get_or_create_daily(user_id, date.today())
            daily.time_spent_delta += seconds

        await self._check_flush_needed()

    # ============================================================
    # Interaction Logging (버퍼링)
    # ============================================================

    async def log_interaction(
        self,
        user_id: str,
        interaction_type: str,
        data: Dict[str, Any],
        session_id: Optional[str] = None,
        user_metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """상호작용 기록 (버퍼에 추가)"""
        async with self._lock:
            self._interactions_buffer.append({
                "user_id": user_id,
                "session_id": session_id,
                "interaction_type": interaction_type,
                "interaction_data": data,
                "user_metadata": user_metadata or {},
                "created_at": datetime.now().isoformat(),
            })

        await self._check_flush_needed()

    async def log_interactions_batch(
        self,
        user_id: str,
        interactions: List[Dict[str, Any]],
        session_id: Optional[str] = None,
    ) -> int:
        """
        상호작용 배치 기록 (프론트엔드에서 모아서 전송)

        Args:
            user_id: 사용자 ID
            interactions: [{"type": "click", "data": {...}, "timestamp": "..."}]
            session_id: 세션 ID (선택)

        Returns:
            기록된 상호작용 수
        """
        async with self._lock:
            for interaction in interactions:
                self._interactions_buffer.append({
                    "user_id": user_id,
                    "session_id": session_id,
                    "interaction_type": interaction.get("type", "unknown"),
                    "interaction_data": interaction.get("data", {}),
                    "user_metadata": interaction.get("metadata", {}),
                    "created_at": interaction.get("timestamp", datetime.now().isoformat()),
                })

        # 배치는 즉시 flush
        await self._flush_interactions()
        return len(interactions)

    # ============================================================
    # Flush Operations
    # ============================================================

    async def flush_user(self, user_id: str) -> bool:
        """특정 사용자 데이터 즉시 flush"""
        async with self._lock:
            delta = self._stats_deltas.pop(user_id, None)
            daily_keys = [k for k in self._daily_deltas if k.startswith(f"{user_id}:")]
            daily_deltas = {k: self._daily_deltas.pop(k) for k in daily_keys}

        success = True

        if delta and not delta.is_empty():
            success = await self._apply_stats_delta(user_id, delta) and success

        for key, daily in daily_deltas.items():
            if not daily.is_empty():
                success = await self._apply_daily_delta(user_id, daily) and success

        return success

    async def flush_all(self) -> Dict[str, Any]:
        """모든 캐시 데이터 flush"""
        async with self._lock:
            stats_deltas = dict(self._stats_deltas)
            daily_deltas = dict(self._daily_deltas)
            interactions = list(self._interactions_buffer)

            self._stats_deltas.clear()
            self._daily_deltas.clear()
            self._interactions_buffer.clear()

        results = {
            "stats_flushed": 0,
            "daily_flushed": 0,
            "interactions_flushed": 0,
            "errors": [],
        }

        # Stats 업데이트
        for user_id, delta in stats_deltas.items():
            if not delta.is_empty():
                try:
                    await self._apply_stats_delta(user_id, delta)
                    results["stats_flushed"] += 1
                except Exception as e:
                    results["errors"].append(f"stats:{user_id}:{e}")

        # Daily 업데이트
        for key, daily in daily_deltas.items():
            user_id = key.split(":")[0]
            if not daily.is_empty():
                try:
                    await self._apply_daily_delta(user_id, daily)
                    results["daily_flushed"] += 1
                except Exception as e:
                    results["errors"].append(f"daily:{key}:{e}")

        # Interactions 삽입
        if interactions:
            try:
                self.db.table("user_interactions").insert(interactions).execute()
                results["interactions_flushed"] = len(interactions)
            except Exception as e:
                results["errors"].append(f"interactions:{e}")

        if results["stats_flushed"] or results["daily_flushed"] or results["interactions_flushed"]:
            logger.info(f"[StatsCache] Flushed: {results}")

        return results

    # ============================================================
    # Background Flush Task
    # ============================================================

    def start_background_flush(self) -> None:
        """백그라운드 flush 태스크 시작"""
        if self._flush_task is None or self._flush_task.done():
            self._flush_task = asyncio.create_task(self._background_flush_loop())
            logger.info("[StatsCache] Background flush started")

    def stop_background_flush(self) -> None:
        """백그라운드 flush 태스크 중지"""
        if self._flush_task and not self._flush_task.done():
            self._flush_task.cancel()
            logger.info("[StatsCache] Background flush stopped")

    async def _background_flush_loop(self) -> None:
        """주기적 flush 루프"""
        while True:
            try:
                await asyncio.sleep(self.FLUSH_INTERVAL_SECONDS)
                await self.flush_all()
            except asyncio.CancelledError:
                # 종료 시 남은 데이터 flush
                await self.flush_all()
                break
            except Exception as e:
                logger.error(f"[StatsCache] Background flush error: {e}")

    # ============================================================
    # Internal Helpers
    # ============================================================

    def _get_or_create_delta(self, user_id: str) -> UserStatsDelta:
        """유저 stats delta 가져오기/생성"""
        if user_id not in self._stats_deltas:
            self._stats_deltas[user_id] = UserStatsDelta()
        return self._stats_deltas[user_id]

    def _get_or_create_daily(self, user_id: str, activity_date: date) -> DailyActivityDelta:
        """일별 활동 delta 가져오기/생성"""
        key = f"{user_id}:{activity_date.isoformat()}"
        if key not in self._daily_deltas:
            self._daily_deltas[key] = DailyActivityDelta(date=activity_date)
        return self._daily_deltas[key]

    async def _check_flush_needed(self) -> None:
        """버퍼 크기 확인 후 필요시 flush"""
        should_flush_interactions = len(self._interactions_buffer) >= self.MAX_INTERACTIONS_BUFFER
        should_flush_stats = len(self._stats_deltas) >= self.MAX_USERS_BUFFER

        if should_flush_interactions:
            await self._flush_interactions()

        if should_flush_stats:
            await self.flush_all()

    async def _flush_interactions(self) -> None:
        """인터랙션 버퍼만 flush"""
        async with self._lock:
            interactions = list(self._interactions_buffer)
            self._interactions_buffer.clear()

        if interactions:
            try:
                self.db.table("user_interactions").insert(interactions).execute()
                logger.debug(f"[StatsCache] Flushed {len(interactions)} interactions")
            except Exception as e:
                logger.error(f"[StatsCache] Failed to flush interactions: {e}")

    async def _apply_stats_delta(self, user_id: str, delta: UserStatsDelta) -> bool:
        """user_stats에 delta 적용"""
        try:
            # RPC 호출로 atomic update
            self.db.rpc("increment_user_stats", {
                "p_user_id": user_id,
                "p_xp_delta": delta.xp_delta,
                "p_problems_solved_delta": delta.problems_solved_delta,
                "p_hints_used_delta": delta.hints_used_delta,
                "p_seeds_delta": delta.seeds_delta,
                "p_time_spent_delta": delta.time_spent_delta,
            }).execute()
            return True
        except Exception as e:
            # RPC 없으면 직접 업데이트 (fallback)
            try:
                # 현재 값 조회
                result = self.db.table("user_stats").select(
                    "total_xp, problems_solved, hints_used, seeds"
                ).eq("user_id", user_id).single().execute()

                if result.data:
                    current = result.data
                    self.db.table("user_stats").update({
                        "total_xp": current.get("total_xp", 0) + delta.xp_delta,
                        "problems_solved": current.get("problems_solved", 0) + delta.problems_solved_delta,
                        "hints_used": (current.get("hints_used") or 0) + delta.hints_used_delta,
                        "seeds": current.get("seeds", 0) + delta.seeds_delta,
                        "updated_at": datetime.now().isoformat(),
                    }).eq("user_id", user_id).execute()
                    return True
            except Exception as inner_e:
                logger.error(f"[StatsCache] Failed to apply stats delta: {inner_e}")
            return False

    async def _apply_daily_delta(self, user_id: str, delta: DailyActivityDelta) -> bool:
        """daily_activity에 delta 적용"""
        try:
            # UPSERT with increment
            self.db.rpc("upsert_daily_activity", {
                "p_user_id": user_id,
                "p_date": delta.date.isoformat(),
                "p_problems_solved_delta": delta.problems_solved_delta,
                "p_xp_earned_delta": delta.xp_earned_delta,
                "p_time_spent_delta": delta.time_spent_delta,
                "p_hints_used_delta": delta.hints_used_delta,
            }).execute()
            return True
        except Exception as e:
            # RPC 없으면 직접 upsert
            try:
                # 기존 레코드 확인
                result = self.db.table("daily_activity").select("*").eq(
                    "user_id", user_id
                ).eq("activity_date", delta.date.isoformat()).execute()

                if result.data and len(result.data) > 0:
                    current = result.data[0]
                    self.db.table("daily_activity").update({
                        "problems_solved": current.get("problems_solved", 0) + delta.problems_solved_delta,
                        "xp_earned": current.get("xp_earned", 0) + delta.xp_earned_delta,
                        "time_spent": current.get("time_spent", 0) + delta.time_spent_delta,
                        "hints_used": (current.get("hints_used") or 0) + delta.hints_used_delta,
                    }).eq("user_id", user_id).eq("activity_date", delta.date.isoformat()).execute()
                else:
                    self.db.table("daily_activity").insert({
                        "user_id": user_id,
                        "activity_date": delta.date.isoformat(),
                        "problems_solved": delta.problems_solved_delta,
                        "xp_earned": delta.xp_earned_delta,
                        "time_spent": delta.time_spent_delta,
                        "hints_used": delta.hints_used_delta,
                    }).execute()
                return True
            except Exception as inner_e:
                logger.error(f"[StatsCache] Failed to apply daily delta: {inner_e}")
            return False

    # ============================================================
    # Status
    # ============================================================

    def get_buffer_status(self) -> Dict[str, Any]:
        """버퍼 상태 조회"""
        return {
            "stats_users": len(self._stats_deltas),
            "daily_entries": len(self._daily_deltas),
            "interactions_buffered": len(self._interactions_buffer),
            "flush_task_running": self._flush_task is not None and not self._flush_task.done(),
        }


# ============================================================
# Singleton Instance
# ============================================================

_stats_cache: Optional[StatsCacheService] = None


def get_stats_cache() -> StatsCacheService:
    """StatsCacheService 싱글톤 반환"""
    global _stats_cache
    if _stats_cache is None:
        _stats_cache = StatsCacheService()
        _stats_cache.start_background_flush()
    return _stats_cache


async def shutdown_stats_cache() -> None:
    """앱 종료 시 호출 - 남은 데이터 flush"""
    global _stats_cache
    if _stats_cache is not None:
        _stats_cache.stop_background_flush()
        await _stats_cache.flush_all()
        logger.info("[StatsCache] Shutdown complete")
