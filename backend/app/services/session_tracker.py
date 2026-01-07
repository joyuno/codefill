"""
Session Tracker Service

문제 풀이 세션 추적 및 포기 감지 서비스

Features:
1. 문제 시작 시점 기록
2. 하트비트로 활성 세션 추적
3. 타임아웃 시 자동 포기 처리
4. 페이지 이탈/세션 종료 감지

사용 시나리오:
- 문제 시작 → start_session()
- 주기적 하트비트 (30초) → heartbeat()
- 문제 완료 → complete_session()
- 문제 스킵 → skip_session()
- 타임아웃/이탈 → 자동으로 abandon 처리

Usage:
    tracker = get_session_tracker()

    # 문제 시작
    session_id = await tracker.start_session(user_id, problem_id)

    # 하트비트 (프론트엔드에서 30초마다)
    await tracker.heartbeat(session_id)

    # 완료 또는 스킵
    await tracker.complete_session(session_id, is_correct=True)
    await tracker.skip_session(session_id)
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from uuid import uuid4
from dataclasses import dataclass, asdict
from enum import Enum

from ..database import get_supabase_client
from ..config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class SessionStatus(str, Enum):
    """세션 상태"""
    ACTIVE = "active"           # 진행 중
    COMPLETED = "completed"     # 정상 완료
    SKIPPED = "skipped"         # 사용자가 스킵
    ABANDONED = "abandoned"     # 포기 (타임아웃/이탈)
    EXPIRED = "expired"         # 세션 만료


@dataclass
class PracticeSession:
    """문제 풀이 세션"""
    id: str
    user_id: str
    problem_id: str
    problem_type: str           # blank, puzzle, guided
    status: SessionStatus
    started_at: datetime
    last_heartbeat: datetime
    completed_at: Optional[datetime]
    hints_used: int
    attempt_count: int
    time_spent_seconds: int
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "status": self.status.value,
            "started_at": self.started_at.isoformat(),
            "last_heartbeat": self.last_heartbeat.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class SessionTracker:
    """
    문제 풀이 세션 추적기

    문제 시작부터 완료/포기까지의 전체 세션을 추적합니다.

    포기 판정 기준:
    1. 하트비트 타임아웃 (2분 이상 하트비트 없음)
    2. 세션 만료 (30분 이상 경과)
    3. 명시적 페이지 이탈 이벤트

    Usage:
        tracker = get_session_tracker()

        # 문제 시작
        session_id = await tracker.start_session(
            user_id="...",
            problem_id="...",
            problem_type="blank"
        )

        # 프론트엔드에서 30초마다 호출
        await tracker.heartbeat(session_id)

        # 문제 완료
        await tracker.complete_session(session_id, is_correct=True, score=85)

        # 또는 스킵
        await tracker.skip_session(session_id, reason="too_hard")
    """

    # 타임아웃 설정 (초)
    HEARTBEAT_TIMEOUT = 1800      # 하트비트 없으면 30분 후 포기 처리
    SESSION_MAX_DURATION = 5400  # 최대 세션 길이 90분
    HEARTBEAT_INTERVAL = 30      # 권장 하트비트 간격

    def __init__(self):
        self.db = get_supabase_client()
        # 인메모리 캐시 (DB 부하 감소)
        self._active_sessions: Dict[str, PracticeSession] = {}

    async def start_session(
        self,
        user_id: str,
        problem_id: str,
        problem_type: str = "blank",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        문제 풀이 세션 시작

        Args:
            user_id: 사용자 UUID
            problem_id: 문제 ID
            problem_type: 문제 유형 (blank/puzzle/guided)
            metadata: 추가 메타데이터

        Returns:
            session_id: 세션 ID
        """
        session_id = str(uuid4())
        now = datetime.now()

        session = PracticeSession(
            id=session_id,
            user_id=user_id,
            problem_id=problem_id,
            problem_type=problem_type,
            status=SessionStatus.ACTIVE,
            started_at=now,
            last_heartbeat=now,
            completed_at=None,
            hints_used=0,
            attempt_count=0,
            time_spent_seconds=0,
            metadata=metadata or {},
        )

        # 인메모리 캐시에 저장
        self._active_sessions[session_id] = session

        # DB에 기록 (user_interactions)
        try:
            self.db.table("user_interactions").insert({
                "user_id": user_id,
                "interaction_type": "session_start",
                "interaction_data": {
                    "session_id": session_id,
                    "problem_id": problem_id,
                    "problem_type": problem_type,
                },
            }).execute()
        except Exception as e:
            logger.warning(f"[SessionTracker] Failed to log session start: {e}")

        logger.info(f"[SessionTracker] Session started: {session_id} for user={user_id}, problem={problem_id}")
        return session_id

    async def heartbeat(
        self,
        session_id: str,
        hints_used: Optional[int] = None,
        attempt_count: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        세션 하트비트

        프론트엔드에서 주기적으로 호출하여 세션 활성 상태 유지

        Args:
            session_id: 세션 ID
            hints_used: 현재까지 사용한 힌트 수
            attempt_count: 현재까지 시도 횟수

        Returns:
            {"success": bool, "session_status": str}
        """
        session = self._active_sessions.get(session_id)
        if not session:
            return {"success": False, "error": "Session not found", "session_status": "unknown"}

        if session.status != SessionStatus.ACTIVE:
            return {"success": False, "error": "Session not active", "session_status": session.status.value}

        now = datetime.now()

        # 세션 만료 체크
        elapsed = (now - session.started_at).total_seconds()
        if elapsed > self.SESSION_MAX_DURATION:
            await self._mark_abandoned(session, reason="session_expired")
            return {"success": False, "error": "Session expired", "session_status": "expired"}

        # 하트비트 업데이트
        session.last_heartbeat = now
        session.time_spent_seconds = int(elapsed)

        if hints_used is not None:
            session.hints_used = hints_used
        if attempt_count is not None:
            session.attempt_count = attempt_count

        return {"success": True, "session_status": "active", "time_spent": session.time_spent_seconds}

    async def complete_session(
        self,
        session_id: str,
        is_correct: bool,
        score: int = 0,
        submitted_answer: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        세션 완료 처리

        Args:
            session_id: 세션 ID
            is_correct: 정답 여부
            score: 점수
            submitted_answer: 제출한 답

        Returns:
            세션 완료 정보
        """
        session = self._active_sessions.get(session_id)
        if not session:
            return {"success": False, "error": "Session not found"}

        now = datetime.now()
        session.status = SessionStatus.COMPLETED
        session.completed_at = now
        session.time_spent_seconds = int((now - session.started_at).total_seconds())

        # DB에 완료 기록
        try:
            self.db.table("user_interactions").insert({
                "user_id": session.user_id,
                "interaction_type": "complete",
                "interaction_data": {
                    "session_id": session_id,
                    "problem_id": session.problem_id,
                    "problem_type": session.problem_type,
                    "is_correct": is_correct,
                    "score": score,
                    "time_spent": session.time_spent_seconds,
                    "hints_used": session.hints_used,
                    "attempt_count": session.attempt_count,
                },
            }).execute()
        except Exception as e:
            logger.error(f"[SessionTracker] Failed to log completion: {e}")

        # 캐시에서 제거
        del self._active_sessions[session_id]

        logger.info(f"[SessionTracker] Session completed: {session_id}, correct={is_correct}, time={session.time_spent_seconds}s")

        return {
            "success": True,
            "session_id": session_id,
            "status": "completed",
            "time_spent": session.time_spent_seconds,
            "hints_used": session.hints_used,
            "attempt_count": session.attempt_count,
        }

    async def skip_session(
        self,
        session_id: str,
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        세션 스킵 처리 (사용자가 명시적으로 건너뛰기)

        Args:
            session_id: 세션 ID
            reason: 스킵 이유 (too_hard, not_interested, etc.)

        Returns:
            스킵 결과
        """
        session = self._active_sessions.get(session_id)
        if not session:
            return {"success": False, "error": "Session not found"}

        now = datetime.now()
        session.status = SessionStatus.SKIPPED
        session.completed_at = now
        session.time_spent_seconds = int((now - session.started_at).total_seconds())

        # DB에 스킵 기록
        try:
            self.db.table("user_interactions").insert({
                "user_id": session.user_id,
                "interaction_type": "skip",
                "interaction_data": {
                    "session_id": session_id,
                    "problem_id": session.problem_id,
                    "problem_type": session.problem_type,
                    "reason": reason,
                    "time_spent": session.time_spent_seconds,
                    "hints_used": session.hints_used,
                    "attempt_count": session.attempt_count,
                },
            }).execute()
        except Exception as e:
            logger.error(f"[SessionTracker] Failed to log skip: {e}")

        # 캐시에서 제거
        del self._active_sessions[session_id]

        logger.info(f"[SessionTracker] Session skipped: {session_id}, reason={reason}")

        return {
            "success": True,
            "session_id": session_id,
            "status": "skipped",
            "time_spent": session.time_spent_seconds,
        }

    async def abandon_session(
        self,
        session_id: str,
        reason: str = "user_left",
    ) -> Dict[str, Any]:
        """
        세션 포기 처리 (페이지 이탈 등)

        프론트엔드의 beforeunload/visibilitychange 이벤트에서 호출

        Args:
            session_id: 세션 ID
            reason: 포기 이유 (user_left, tab_closed, navigation, etc.)

        Returns:
            포기 결과
        """
        session = self._active_sessions.get(session_id)
        if not session:
            return {"success": False, "error": "Session not found"}

        await self._mark_abandoned(session, reason)

        return {
            "success": True,
            "session_id": session_id,
            "status": "abandoned",
            "reason": reason,
            "time_spent": session.time_spent_seconds,
        }

    async def _mark_abandoned(
        self,
        session: PracticeSession,
        reason: str,
    ):
        """세션을 포기 상태로 표시"""
        now = datetime.now()
        session.status = SessionStatus.ABANDONED
        session.completed_at = now
        session.time_spent_seconds = int((now - session.started_at).total_seconds())

        # DB에 포기 기록
        try:
            self.db.table("user_interactions").insert({
                "user_id": session.user_id,
                "interaction_type": "abandon",
                "interaction_data": {
                    "session_id": session.id,
                    "problem_id": session.problem_id,
                    "problem_type": session.problem_type,
                    "reason": reason,
                    "time_spent": session.time_spent_seconds,
                    "hints_used": session.hints_used,
                    "attempt_count": session.attempt_count,
                    "last_heartbeat": session.last_heartbeat.isoformat(),
                },
            }).execute()
        except Exception as e:
            logger.error(f"[SessionTracker] Failed to log abandonment: {e}")

        # 캐시에서 제거
        if session.id in self._active_sessions:
            del self._active_sessions[session.id]

        logger.info(f"[SessionTracker] Session abandoned: {session.id}, reason={reason}, time={session.time_spent_seconds}s")

    async def cleanup_stale_sessions(self) -> int:
        """
        타임아웃된 세션 정리

        백그라운드 태스크로 주기적 실행 (예: 1분마다)

        Returns:
            정리된 세션 수
        """
        now = datetime.now()
        stale_sessions = []

        for session_id, session in list(self._active_sessions.items()):
            if session.status != SessionStatus.ACTIVE:
                continue

            # 하트비트 타임아웃 체크
            heartbeat_age = (now - session.last_heartbeat).total_seconds()
            if heartbeat_age > self.HEARTBEAT_TIMEOUT:
                stale_sessions.append((session, "heartbeat_timeout"))
                continue

            # 세션 만료 체크
            session_age = (now - session.started_at).total_seconds()
            if session_age > self.SESSION_MAX_DURATION:
                stale_sessions.append((session, "session_expired"))

        # 포기 처리
        for session, reason in stale_sessions:
            await self._mark_abandoned(session, reason)

        if stale_sessions:
            logger.info(f"[SessionTracker] Cleaned up {len(stale_sessions)} stale sessions")

        return len(stale_sessions)

    def get_active_session(self, user_id: str) -> Optional[PracticeSession]:
        """사용자의 현재 활성 세션 조회"""
        for session in self._active_sessions.values():
            if session.user_id == user_id and session.status == SessionStatus.ACTIVE:
                return session
        return None

    def get_session(self, session_id: str) -> Optional[PracticeSession]:
        """세션 ID로 세션 조회 (metadata 포함)"""
        return self._active_sessions.get(session_id)

    async def get_abandonment_stats(
        self,
        user_id: Optional[str] = None,
        days: int = 30,
    ) -> Dict[str, Any]:
        """
        포기 통계 조회

        Args:
            user_id: 특정 사용자 (None이면 전체)
            days: 조회 기간

        Returns:
            포기 관련 통계
        """
        try:
            query = self.db.table("user_interactions") \
                .select("interaction_type, interaction_data") \
                .in_("interaction_type", ["complete", "skip", "abandon"]) \
                .gte("created_at", (datetime.now() - timedelta(days=days)).isoformat())

            if user_id:
                query = query.eq("user_id", user_id)

            result = query.execute()
            interactions = result.data or []

            # 집계
            stats = {
                "complete": 0,
                "skip": 0,
                "abandon": 0,
                "total": 0,
                "completion_rate": 0.0,
                "abandonment_rate": 0.0,
                "abandon_reasons": {},
            }

            for interaction in interactions:
                itype = interaction.get("interaction_type")
                idata = interaction.get("interaction_data", {})

                stats["total"] += 1
                if itype in stats:
                    stats[itype] += 1

                if itype == "abandon":
                    reason = idata.get("reason", "unknown")
                    stats["abandon_reasons"][reason] = stats["abandon_reasons"].get(reason, 0) + 1

            if stats["total"] > 0:
                stats["completion_rate"] = round(stats["complete"] / stats["total"], 3)
                stats["abandonment_rate"] = round(stats["abandon"] / stats["total"], 3)

            return stats

        except Exception as e:
            logger.error(f"[SessionTracker] Failed to get abandonment stats: {e}")
            return {"error": str(e)}


# ============================================================
# Singleton Instance
# ============================================================

_session_tracker: Optional[SessionTracker] = None


def get_session_tracker() -> SessionTracker:
    """SessionTracker 싱글톤 반환"""
    global _session_tracker
    if _session_tracker is None:
        _session_tracker = SessionTracker()
    return _session_tracker
