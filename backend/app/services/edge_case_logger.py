"""
Edge Case Logger Service

런타임 엣지케이스 수집 및 분석을 위한 하이브리드 로깅 서비스
- Supabase: 상세 컨텍스트 저장 (디버깅/개선용)
- GA4: 집계용 이벤트 전송 (추세 분석용)
"""

import logging
import asyncio
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class EdgeCaseSeverity(str, Enum):
    """엣지케이스 심각도"""
    LOW = "low"          # 자동 복구됨, 사용자 영향 없음
    MEDIUM = "medium"    # fallback 처리됨, 사용자 경험 약간 저하
    HIGH = "high"        # 기능 실패, 사용자가 재시도 필요
    CRITICAL = "critical"  # 시스템 오류, 세션 중단


class GraphName(str, Enum):
    """LangGraph 이름"""
    ORCHESTRATOR = "orchestrator"
    DISCOVERY = "discovery"
    COLLECTION = "collection"
    SOLVING = "solving"
    GUIDED_TUTOR = "guided_tutor"


@dataclass
class EdgeCaseEvent:
    """엣지케이스 이벤트 데이터"""
    # 필수 필드
    edge_case_code: str      # 'EC-D03', 'EC-S02' 등
    edge_case_type: str      # 'index_out_of_range', 'no_code_submitted' 등
    graph_name: str          # 'discovery', 'collection', 'solving'

    # 선택 필드
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    current_node: Optional[str] = None
    previous_node: Optional[str] = None
    severity: str = EdgeCaseSeverity.LOW.value

    # 컨텍스트
    user_message: Optional[str] = None
    intent_detected: Optional[str] = None
    intent_confidence: Optional[float] = None
    state_snapshot: Optional[Dict[str, Any]] = None

    # 처리 결과
    fallback_triggered: bool = False
    response_message: Optional[str] = None
    was_recovered: bool = False

    # 태그
    tags: List[str] = field(default_factory=list)


# ============================================================
# 엣지케이스 코드 정의
# ============================================================
EDGE_CASE_CODES = {
    # Discovery (EC-D0x)
    "EC-D01": {"type": "intent_classification_failed", "severity": "medium", "graph": "discovery"},
    "EC-D02": {"type": "no_search_results", "severity": "low", "graph": "discovery"},
    "EC-D03": {"type": "index_out_of_range", "severity": "low", "graph": "discovery"},
    "EC-D04": {"type": "problem_generation_failed", "severity": "high", "graph": "discovery"},
    "EC-D05": {"type": "problem_type_invalid", "severity": "medium", "graph": "discovery"},

    # Collection (EC-C0x)
    "EC-C01": {"type": "input_parse_failed", "severity": "low", "graph": "collection"},
    "EC-C02": {"type": "invalid_topic_difficulty_language", "severity": "low", "graph": "collection"},
    "EC-C03": {"type": "empty_input", "severity": "low", "graph": "collection"},

    # Solving (EC-S0x)
    "EC-S01": {"type": "solving_intent_failed", "severity": "medium", "graph": "solving"},
    "EC-S02": {"type": "no_code_submitted", "severity": "low", "graph": "solving"},
    "EC-S03": {"type": "no_problem_context", "severity": "high", "graph": "solving"},
    "EC-S04": {"type": "code_execution_failed", "severity": "high", "graph": "solving"},

    # Multi-Intent (EC-M0x)
    "EC-M01": {"type": "primary_intent_conflict", "severity": "low", "graph": "orchestrator"},
    "EC-M02": {"type": "intent_limit_exceeded", "severity": "low", "graph": "orchestrator"},
    "EC-M03": {"type": "secondary_response_failed", "severity": "low", "graph": "orchestrator"},

    # General (EC-G0x)
    "EC-G01": {"type": "session_state_corrupted", "severity": "high", "graph": "orchestrator"},
    "EC-G02": {"type": "database_error", "severity": "critical", "graph": "orchestrator"},
    "EC-G03": {"type": "llm_api_error", "severity": "high", "graph": "orchestrator"},
}


class EdgeCaseLogger:
    """
    엣지케이스 로거 서비스

    사용법:
        from app.services.edge_case_logger import edge_case_logger

        await edge_case_logger.log(
            code="EC-D03",
            user_id=user_id,
            session_id=session_id,
            current_node="handle_selection",
            user_message="10번 선택할게",
            state_snapshot={"search_results": [...]},
            fallback_triggered=True,
            response_message="1~5번 중에서 선택해주세요!",
        )
    """

    def __init__(self):
        self._supabase = None
        self._ga4_enabled = False
        self._ga4_measurement_id = None
        self._ga4_api_secret = None
        self._buffer: List[EdgeCaseEvent] = []
        self._buffer_size = 10  # 버퍼 크기 (배치 처리용)

    def _get_supabase(self):
        """Lazy loading for Supabase client"""
        if self._supabase is None:
            from ..core.database import get_supabase_client
            self._supabase = get_supabase_client()
        return self._supabase

    def configure_ga4(self, measurement_id: str, api_secret: str):
        """GA4 설정"""
        self._ga4_measurement_id = measurement_id
        self._ga4_api_secret = api_secret
        self._ga4_enabled = True
        logger.info(f"[EdgeCaseLogger] GA4 configured: {measurement_id}")

    async def log(
        self,
        code: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        current_node: Optional[str] = None,
        previous_node: Optional[str] = None,
        user_message: Optional[str] = None,
        intent_detected: Optional[str] = None,
        intent_confidence: Optional[float] = None,
        state_snapshot: Optional[Dict[str, Any]] = None,
        fallback_triggered: bool = False,
        response_message: Optional[str] = None,
        was_recovered: bool = False,
        tags: Optional[List[str]] = None,
        send_ga4: bool = True,
    ) -> Optional[str]:
        """
        엣지케이스 로깅

        Args:
            code: 엣지케이스 코드 (EC-D03 등)
            user_id: 사용자 ID
            session_id: 세션 ID
            current_node: 현재 LangGraph 노드
            previous_node: 이전 노드
            user_message: 사용자 입력 원문
            intent_detected: 감지된 의도
            intent_confidence: 의도 신뢰도
            state_snapshot: 상태 스냅샷 (민감 데이터 제외)
            fallback_triggered: fallback 발생 여부
            response_message: 응답 메시지
            was_recovered: 자동 복구 여부
            tags: 추가 태그
            send_ga4: GA4 이벤트 전송 여부

        Returns:
            로그 ID (성공 시)
        """
        # 코드 정보 조회
        code_info = EDGE_CASE_CODES.get(code, {
            "type": "unknown",
            "severity": "medium",
            "graph": "orchestrator"
        })

        event = EdgeCaseEvent(
            edge_case_code=code,
            edge_case_type=code_info["type"],
            graph_name=code_info["graph"],
            severity=code_info["severity"],
            user_id=user_id,
            session_id=session_id,
            current_node=current_node,
            previous_node=previous_node,
            user_message=user_message,
            intent_detected=intent_detected,
            intent_confidence=intent_confidence,
            state_snapshot=self._sanitize_state(state_snapshot),
            fallback_triggered=fallback_triggered,
            response_message=response_message,
            was_recovered=was_recovered,
            tags=tags or [],
        )

        log_id = None

        # 1. Supabase에 상세 로그 저장
        try:
            log_id = await self._save_to_supabase(event)
        except Exception as e:
            logger.error(f"[EdgeCaseLogger] Failed to save to Supabase: {e}")

        # 2. GA4에 집계용 이벤트 전송
        if send_ga4 and self._ga4_enabled:
            try:
                await self._send_to_ga4(event)
            except Exception as e:
                logger.error(f"[EdgeCaseLogger] Failed to send to GA4: {e}")

        # 콘솔 로그
        logger.info(
            f"[EdgeCase] {code} ({code_info['type']}) "
            f"graph={code_info['graph']} node={current_node} "
            f"severity={code_info['severity']} fallback={fallback_triggered}"
        )

        return log_id

    async def log_quick(
        self,
        code: str,
        current_node: str,
        user_message: Optional[str] = None,
        **kwargs
    ) -> Optional[str]:
        """간편 로깅 (자주 사용하는 필드만)"""
        return await self.log(
            code=code,
            current_node=current_node,
            user_message=user_message,
            **kwargs
        )

    def _sanitize_state(self, state: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        상태 스냅샷에서 민감 데이터 제거

        - conversation_history는 길이만 저장
        - 큰 데이터는 요약
        """
        if not state:
            return None

        sanitized = {}
        for key, value in state.items():
            if key == "conversation_history":
                sanitized[key] = f"[{len(value) if value else 0} messages]"
            elif key in ("api_key", "password", "token", "secret"):
                sanitized[key] = "[REDACTED]"
            elif isinstance(value, list) and len(value) > 10:
                sanitized[key] = f"[{len(value)} items]"
            elif isinstance(value, str) and len(value) > 500:
                sanitized[key] = value[:500] + "..."
            else:
                sanitized[key] = value

        return sanitized

    async def _save_to_supabase(self, event: EdgeCaseEvent) -> Optional[str]:
        """Supabase에 저장"""
        supabase = self._get_supabase()

        data = {
            "user_id": event.user_id,
            "session_id": event.session_id,
            "graph_name": event.graph_name,
            "current_node": event.current_node,
            "previous_node": event.previous_node,
            "edge_case_code": event.edge_case_code,
            "edge_case_type": event.edge_case_type,
            "severity": event.severity,
            "user_message": event.user_message,
            "intent_detected": event.intent_detected,
            "intent_confidence": event.intent_confidence,
            "state_snapshot": event.state_snapshot,
            "fallback_triggered": event.fallback_triggered,
            "response_message": event.response_message,
            "was_recovered": event.was_recovered,
            "tags": event.tags,
        }

        result = supabase.table("edge_case_logs").insert(data).execute()

        if result.data:
            return result.data[0].get("id")
        return None

    async def _send_to_ga4(self, event: EdgeCaseEvent):
        """
        GA4 Measurement Protocol로 이벤트 전송

        참고: https://developers.google.com/analytics/devguides/collection/protocol/ga4
        """
        if not self._ga4_enabled:
            return

        import aiohttp

        url = f"https://www.google-analytics.com/mp/collect"
        params = {
            "measurement_id": self._ga4_measurement_id,
            "api_secret": self._ga4_api_secret,
        }

        # GA4 이벤트 데이터 (파라미터 25개 제한, 값 100자 제한)
        payload = {
            "client_id": event.session_id or "anonymous",
            "user_id": event.user_id,
            "events": [{
                "name": "edge_case_hit",
                "params": {
                    "edge_case_code": event.edge_case_code,
                    "edge_case_type": event.edge_case_type[:100] if event.edge_case_type else None,
                    "graph_name": event.graph_name,
                    "current_node": event.current_node[:100] if event.current_node else None,
                    "severity": event.severity,
                    "fallback_triggered": str(event.fallback_triggered),
                    "was_recovered": str(event.was_recovered),
                    "engagement_time_msec": 1,
                }
            }]
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, params=params, json=payload) as response:
                    if response.status != 204:
                        logger.warning(f"[EdgeCaseLogger] GA4 response: {response.status}")
        except Exception as e:
            logger.error(f"[EdgeCaseLogger] GA4 send failed: {e}")

    async def get_summary(self, days: int = 7, limit: int = 10) -> List[Dict[str, Any]]:
        """최근 엣지케이스 요약 조회"""
        supabase = self._get_supabase()

        result = supabase.rpc(
            "get_top_edge_cases",
            {"p_days": days, "p_limit": limit}
        ).execute()

        return result.data or []

    async def mark_resolved(self, code: str, version: str):
        """특정 코드의 엣지케이스를 해결됨으로 표시"""
        supabase = self._get_supabase()

        supabase.table("edge_case_logs").update({
            "resolved": True,
            "resolved_at": datetime.utcnow().isoformat(),
            "resolved_in_version": version,
        }).eq("edge_case_code", code).eq("resolved", False).execute()

        logger.info(f"[EdgeCaseLogger] Marked {code} as resolved in version {version}")


# 싱글톤 인스턴스
edge_case_logger = EdgeCaseLogger()


# ============================================================
# 편의 함수 (직접 import용)
# ============================================================
async def log_edge_case(code: str, **kwargs) -> Optional[str]:
    """엣지케이스 로깅 편의 함수"""
    return await edge_case_logger.log(code=code, **kwargs)


def get_edge_case_codes() -> Dict[str, Dict]:
    """정의된 엣지케이스 코드 목록 반환"""
    return EDGE_CASE_CODES.copy()
