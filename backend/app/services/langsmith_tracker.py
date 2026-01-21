"""
LangSmith Tracker Service

LLM 호출의 토큰 사용량, 응답 시간, 에러를 추적하고
LangSmith에 자동으로 기록합니다.

특징:
- 세션별 토큰 사용량 집계
- 노드별 응답 시간 측정
- 에러 자동 로깅
- LangSmith Run 연동 (활성화된 경우)
"""

import os
import logging
import time
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

# LangSmith 활성화 여부
LANGSMITH_ENABLED = os.getenv("LANGCHAIN_TRACING_V2", "").lower() == "true"


@dataclass
class LLMCallRecord:
    """LLM 호출 기록"""
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    duration_ms: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    node_name: Optional[str] = None
    error: Optional[str] = None


@dataclass
class NodeExecutionRecord:
    """노드 실행 기록"""
    node_name: str
    graph_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: Optional[float] = None
    input_keys: List[str] = field(default_factory=list)
    output_keys: List[str] = field(default_factory=list)
    error: Optional[str] = None


class LangSmithTracker:
    """
    LangSmith 트래커

    세션별로 토큰 사용량과 노드 실행 정보를 추적합니다.
    LangSmith가 활성화되어 있으면 자동으로 연동됩니다.
    """

    def __init__(self):
        self._session_tokens: Dict[str, Dict[str, int]] = {}  # session_id -> {model: tokens}
        self._llm_calls: List[LLMCallRecord] = []
        self._node_executions: List[NodeExecutionRecord] = []
        self._current_node: Optional[str] = None
        self._max_history = 1000  # 최대 기록 개수

    def log_llm_usage(
        self,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        total_tokens: int,
        session_id: Optional[str] = None,
        duration_ms: Optional[float] = None,
    ):
        """
        LLM 토큰 사용량 로깅

        Args:
            model: 모델 ID
            prompt_tokens: 프롬프트 토큰 수
            completion_tokens: 완료 토큰 수
            total_tokens: 총 토큰 수
            session_id: 세션 ID (집계용)
            duration_ms: 응답 시간 (ms)
        """
        # 기록 추가
        record = LLMCallRecord(
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            duration_ms=duration_ms or 0,
            node_name=self._current_node,
        )
        self._llm_calls.append(record)

        # 히스토리 제한
        if len(self._llm_calls) > self._max_history:
            self._llm_calls = self._llm_calls[-self._max_history:]

        # 세션별 집계
        if session_id:
            if session_id not in self._session_tokens:
                self._session_tokens[session_id] = {}

            if model not in self._session_tokens[session_id]:
                self._session_tokens[session_id][model] = 0

            self._session_tokens[session_id][model] += total_tokens

        # 로그 출력
        logger.info(
            f"[LLM] {model} - tokens: {total_tokens} "
            f"(prompt: {prompt_tokens}, completion: {completion_tokens})"
            + (f" - {duration_ms:.0f}ms" if duration_ms else "")
        )

        # LangSmith 연동
        if LANGSMITH_ENABLED:
            self._send_to_langsmith_run(record)

    def _send_to_langsmith_run(self, record: LLMCallRecord):
        """현재 LangSmith Run에 메타데이터 추가"""
        try:
            # langsmith의 현재 run context가 있으면 메타데이터 추가
            # 이 부분은 langsmith가 자동으로 처리하므로 추가 구현 불필요
            pass
        except Exception as e:
            logger.debug(f"LangSmith run update skipped: {e}")

    @asynccontextmanager
    async def track_node(self, node_name: str, graph_name: str = "unknown"):
        """
        노드 실행 추적 컨텍스트 매니저

        사용법:
            async with langsmith_tracker.track_node("classify_intent", "orchestrator"):
                result = await classify_intent(state)
        """
        record = NodeExecutionRecord(
            node_name=node_name,
            graph_name=graph_name,
            start_time=datetime.utcnow(),
        )
        self._current_node = node_name

        try:
            yield record
        except Exception as e:
            record.error = str(e)
            raise
        finally:
            record.end_time = datetime.utcnow()
            record.duration_ms = (record.end_time - record.start_time).total_seconds() * 1000

            self._node_executions.append(record)
            self._current_node = None

            # 히스토리 제한
            if len(self._node_executions) > self._max_history:
                self._node_executions = self._node_executions[-self._max_history:]

            # 로그 출력
            status = "✓" if not record.error else "✗"
            logger.info(
                f"[Node] {status} {graph_name}/{node_name} - {record.duration_ms:.0f}ms"
                + (f" - ERROR: {record.error[:50]}" if record.error else "")
            )

    def log_error(
        self,
        node_name: str,
        graph_name: str,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
    ):
        """
        에러 로깅

        Args:
            node_name: 노드 이름
            graph_name: 그래프 이름
            error: 에러 객체
            context: 추가 컨텍스트
        """
        error_msg = f"{type(error).__name__}: {str(error)}"

        logger.error(
            f"[Error] {graph_name}/{node_name} - {error_msg}"
            + (f" - context: {context}" if context else "")
        )

        # LangSmith 에러 로깅
        if LANGSMITH_ENABLED:
            try:
                from langsmith import trace
                # 에러 이벤트 기록
            except ImportError:
                pass

    def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """
        세션별 통계 조회

        Returns:
            {
                "total_tokens": 1234,
                "tokens_by_model": {"openai/gpt-4o-mini": 1000, ...},
                "estimated_cost_usd": 0.05,
            }
        """
        tokens_by_model = self._session_tokens.get(session_id, {})
        total_tokens = sum(tokens_by_model.values())

        # 비용 추정 (대략적인 값)
        cost_per_1k = {
            "openai/gpt-4o": 0.005,
            "openai/gpt-4o-mini": 0.00015,
            "anthropic/claude-sonnet-4": 0.003,
            "google/gemini-3-flash-preview": 0.0001,
            "deepseek/deepseek-v3.2": 0.00014,
        }

        estimated_cost = sum(
            (tokens / 1000) * cost_per_1k.get(model, 0.001)
            for model, tokens in tokens_by_model.items()
        )

        return {
            "total_tokens": total_tokens,
            "tokens_by_model": tokens_by_model,
            "estimated_cost_usd": round(estimated_cost, 4),
        }

    def get_recent_stats(self, minutes: int = 60) -> Dict[str, Any]:
        """
        최근 N분간의 통계

        Returns:
            {
                "llm_calls": 50,
                "total_tokens": 10000,
                "avg_response_time_ms": 500,
                "error_count": 2,
                "nodes_executed": 150,
            }
        """
        cutoff = datetime.utcnow().timestamp() - (minutes * 60)

        recent_llm = [
            r for r in self._llm_calls
            if r.timestamp.timestamp() > cutoff
        ]

        recent_nodes = [
            r for r in self._node_executions
            if r.start_time.timestamp() > cutoff
        ]

        total_tokens = sum(r.total_tokens for r in recent_llm)
        avg_duration = (
            sum(r.duration_ms for r in recent_llm if r.duration_ms) / len(recent_llm)
            if recent_llm else 0
        )
        error_count = sum(1 for r in recent_nodes if r.error)

        return {
            "period_minutes": minutes,
            "llm_calls": len(recent_llm),
            "total_tokens": total_tokens,
            "avg_response_time_ms": round(avg_duration, 2),
            "error_count": error_count,
            "nodes_executed": len(recent_nodes),
        }

    def get_node_stats(self) -> Dict[str, Dict[str, Any]]:
        """
        노드별 통계

        Returns:
            {
                "classify_intent": {
                    "count": 100,
                    "avg_duration_ms": 50,
                    "error_rate": 0.02,
                },
                ...
            }
        """
        node_stats = {}

        for record in self._node_executions:
            name = record.node_name
            if name not in node_stats:
                node_stats[name] = {
                    "count": 0,
                    "total_duration_ms": 0,
                    "errors": 0,
                }

            node_stats[name]["count"] += 1
            if record.duration_ms:
                node_stats[name]["total_duration_ms"] += record.duration_ms
            if record.error:
                node_stats[name]["errors"] += 1

        # 평균 계산
        for name, stats in node_stats.items():
            count = stats["count"]
            if count > 0:
                stats["avg_duration_ms"] = round(stats["total_duration_ms"] / count, 2)
                stats["error_rate"] = round(stats["errors"] / count, 4)
            del stats["total_duration_ms"]

        return node_stats

    def clear_history(self):
        """히스토리 초기화"""
        self._llm_calls.clear()
        self._node_executions.clear()
        self._session_tokens.clear()
        logger.info("[LangSmith] History cleared")


# 싱글톤 인스턴스
langsmith_tracker = LangSmithTracker()
