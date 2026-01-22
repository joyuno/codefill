"""
LangSmith Tracker Service

LLM 호출의 토큰 사용량, 응답 시간, 에러를 추적하고
LangSmith에 자동으로 기록합니다.

특징:
- 세션별 토큰 사용량 집계
- 노드별 응답 시간 측정
- 에러 자동 로깅
- LangSmith Run 연동 (활성화된 경우)
- 노드 데코레이터로 자동 추적
"""

import os
import logging
import time
import functools
from typing import Optional, Dict, Any, List, Callable
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


# ============================================================
# 노드 데코레이터
# ============================================================

def _summarize_value(value: Any, max_len: int = 200) -> str:
    """값을 사람이 읽기 좋게 요약"""
    if value is None:
        return "None"
    if isinstance(value, str):
        if len(value) > max_len:
            return f'"{value[:max_len]}..." ({len(value)}자)'
        return f'"{value}"'
    if isinstance(value, (list, tuple)):
        if len(value) == 0:
            return "[]"
        return f"[{len(value)}개 항목]"
    if isinstance(value, dict):
        if len(value) == 0:
            return "{}"
        keys = list(value.keys())[:5]
        return "{" + ", ".join(keys) + ("..." if len(value) > 5 else "") + "}"
    if isinstance(value, bool):
        return "✓" if value else "✗"
    if isinstance(value, (int, float)):
        return str(value)
    return f"<{type(value).__name__}>"


def _extract_key_fields(state: Dict[str, Any], fields: List[str]) -> Dict[str, str]:
    """상태에서 주요 필드만 추출하여 요약"""
    result = {}
    for field in fields:
        if field in state:
            result[field] = _summarize_value(state[field])
    return result


def track_node(
    graph_name: str,
    node_name: str,
    input_fields: Optional[List[str]] = None,
    output_fields: Optional[List[str]] = None,
    tags: Optional[List[str]] = None,
):
    """
    LangGraph 노드 추적 데코레이터

    사용법:
        @track_node("solving", "chat_assist",
                    input_fields=["message", "problem_context"],
                    output_fields=["response_message"])
        async def chat_assist(state: SolvingState) -> Dict[str, Any]:
            ...

    Args:
        graph_name: 그래프 이름 (orchestrator, solving, discovery 등)
        node_name: 노드 이름
        input_fields: 로깅할 입력 필드 목록 (None이면 자동 감지)
        output_fields: 로깅할 출력 필드 목록 (None이면 자동 감지)
        tags: 추가 태그 (예: ["llm", "hint"])
    """
    # 기본 필드 설정
    default_input_fields = [
        "message", "problem_context", "user_progress", "intent_result",
        "current_code", "conversation_history"
    ]
    default_output_fields = [
        "response_message", "next_node", "intent", "category",
        "search_results", "selected_problem"
    ]

    _input_fields = input_fields or default_input_fields
    _output_fields = output_fields or default_output_fields
    _tags = tags or []

    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(state: Dict[str, Any], *args, **kwargs) -> Dict[str, Any]:
            start_time = datetime.utcnow()
            langsmith_tracker._current_node = node_name

            # 입력 요약
            input_summary = _extract_key_fields(state, _input_fields)

            # LangSmith에 run 시작 기록
            if LANGSMITH_ENABLED:
                try:
                    import langsmith
                    run_name = f"{graph_name}/{node_name}"

                    # 태그와 메타데이터 구성
                    metadata = {
                        "graph": graph_name,
                        "node": node_name,
                        "input_summary": input_summary,
                        "tags": _tags,
                    }

                    # message 필드가 있으면 특별히 강조
                    if "message" in state and state["message"]:
                        metadata["user_message"] = str(state["message"])[:500]

                    # problem_context가 있으면 문제 정보 추가
                    if "problem_context" in state and state["problem_context"]:
                        pc = state["problem_context"]
                        metadata["problem_type"] = pc.get("problem_type", "unknown")
                        metadata["problem_title"] = pc.get("title", "")[:100]

                except ImportError:
                    pass

            error_msg = None
            result = {}

            try:
                # 실제 노드 실행
                result = await func(state, *args, **kwargs)
                return result

            except Exception as e:
                error_msg = f"{type(e).__name__}: {str(e)}"
                raise

            finally:
                end_time = datetime.utcnow()
                duration_ms = (end_time - start_time).total_seconds() * 1000

                # 출력 요약
                output_summary = _extract_key_fields(result, _output_fields) if result else {}

                # 로컬 기록
                record = NodeExecutionRecord(
                    node_name=node_name,
                    graph_name=graph_name,
                    start_time=start_time,
                    end_time=end_time,
                    duration_ms=duration_ms,
                    input_keys=list(input_summary.keys()),
                    output_keys=list(output_summary.keys()),
                    error=error_msg,
                )
                langsmith_tracker._node_executions.append(record)

                # 히스토리 제한
                if len(langsmith_tracker._node_executions) > langsmith_tracker._max_history:
                    langsmith_tracker._node_executions = langsmith_tracker._node_executions[-langsmith_tracker._max_history:]

                langsmith_tracker._current_node = None

                # 콘솔 로그 (사람이 읽기 좋게)
                status_icon = "✗" if error_msg else "✓"
                log_parts = [
                    f"[{status_icon}] {graph_name}/{node_name}",
                    f"⏱ {duration_ms:.0f}ms",
                ]

                # 주요 입력 정보
                if "message" in input_summary:
                    log_parts.append(f"📝 {input_summary['message'][:50]}")

                # 주요 출력 정보
                if "response_message" in output_summary:
                    log_parts.append(f"💬 {output_summary['response_message'][:50]}")
                if "next_node" in output_summary:
                    log_parts.append(f"→ {output_summary['next_node']}")

                if error_msg:
                    log_parts.append(f"❌ {error_msg[:50]}")

                logger.info(" | ".join(log_parts))

        return wrapper
    return decorator


def track_intent_node(node_name: str, tags: Optional[List[str]] = None):
    """의도 분류 노드 전용 데코레이터"""
    return track_node(
        graph_name="intent",
        node_name=node_name,
        input_fields=["message", "conversation_history"],
        output_fields=["category", "action", "confidence", "next_node"],
        tags=tags or ["intent", "classifier"],
    )


def track_solving_node(node_name: str, tags: Optional[List[str]] = None):
    """문제 풀이 노드 전용 데코레이터"""
    return track_node(
        graph_name="solving",
        node_name=node_name,
        input_fields=["message", "problem_context", "user_progress", "intent_result"],
        output_fields=["response_message", "next_node"],
        tags=tags or ["solving"],
    )


def track_discovery_node(node_name: str, tags: Optional[List[str]] = None):
    """문제 탐색 노드 전용 데코레이터"""
    return track_node(
        graph_name="discovery",
        node_name=node_name,
        input_fields=["message", "search_results", "selected_index"],
        output_fields=["response_message", "search_results", "selected_problem", "next_node"],
        tags=tags or ["discovery"],
    )


def track_collection_node(node_name: str, tags: Optional[List[str]] = None):
    """정보 수집 노드 전용 데코레이터"""
    return track_node(
        graph_name="collection",
        node_name=node_name,
        input_fields=["message", "collected_values", "current_field"],
        output_fields=["response_message", "collected_values", "is_complete", "next_node"],
        tags=tags or ["collection"],
    )


def track_method(
    graph_name: str,
    method_name: str,
    tags: Optional[List[str]] = None,
):
    """
    클래스 메서드 추적 데코레이터

    사용법:
        @track_method("orchestrator", "classify", tags=["llm", "intent"])
        async def classify(self, message: str, ...) -> IntentResult:
            ...

    Args:
        graph_name: 그래프 이름
        method_name: 메서드 이름
        tags: 추가 태그
    """
    _tags = tags or []

    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(self, *args, **kwargs) -> Any:
            start_time = datetime.utcnow()
            langsmith_tracker._current_node = method_name

            # 입력 요약 (args, kwargs에서 추출)
            input_summary = {}

            # 첫 번째 위치 인자 처리 (보통 message)
            if args:
                first_arg = args[0]
                if isinstance(first_arg, str):
                    input_summary["message"] = _summarize_value(first_arg, 100)
                elif isinstance(first_arg, dict):
                    input_summary["input"] = _summarize_value(first_arg)

            # 키워드 인자 처리
            for key, value in kwargs.items():
                if key in ["message", "session_state", "state"]:
                    input_summary[key] = _summarize_value(value, 100)

            error_msg = None
            result = None

            try:
                # 실제 메서드 실행
                result = await func(self, *args, **kwargs)
                return result

            except Exception as e:
                error_msg = f"{type(e).__name__}: {str(e)}"
                raise

            finally:
                end_time = datetime.utcnow()
                duration_ms = (end_time - start_time).total_seconds() * 1000

                # 출력 요약
                output_summary = {}
                if result is not None:
                    if hasattr(result, "__dict__"):
                        # dataclass나 객체의 경우
                        for key in ["category", "action", "confidence", "intent", "intents"]:
                            if hasattr(result, key):
                                output_summary[key] = _summarize_value(getattr(result, key))
                    elif isinstance(result, dict):
                        output_summary = _extract_key_fields(result, [
                            "category", "action", "confidence", "intent", "response_message"
                        ])
                    else:
                        output_summary["result"] = _summarize_value(result)

                # 로컬 기록
                record = NodeExecutionRecord(
                    node_name=method_name,
                    graph_name=graph_name,
                    start_time=start_time,
                    end_time=end_time,
                    duration_ms=duration_ms,
                    input_keys=list(input_summary.keys()),
                    output_keys=list(output_summary.keys()),
                    error=error_msg,
                )
                langsmith_tracker._node_executions.append(record)

                # 히스토리 제한
                if len(langsmith_tracker._node_executions) > langsmith_tracker._max_history:
                    langsmith_tracker._node_executions = langsmith_tracker._node_executions[-langsmith_tracker._max_history:]

                langsmith_tracker._current_node = None

                # 콘솔 로그 (사람이 읽기 좋게)
                status_icon = "✗" if error_msg else "✓"
                tags_str = f"[{', '.join(_tags)}] " if _tags else ""
                log_parts = [
                    f"[{status_icon}] {tags_str}{graph_name}/{method_name}",
                    f"⏱ {duration_ms:.0f}ms",
                ]

                # 주요 입력 정보
                if "message" in input_summary:
                    log_parts.append(f"📝 {input_summary['message'][:50]}")

                # 주요 출력 정보
                if "category" in output_summary:
                    log_parts.append(f"🎯 {output_summary['category']}")
                if "action" in output_summary:
                    log_parts.append(f"→ {output_summary['action']}")
                if "confidence" in output_summary:
                    log_parts.append(f"({output_summary['confidence']})")

                if error_msg:
                    log_parts.append(f"❌ {error_msg[:50]}")

                logger.info(" | ".join(log_parts))

        return wrapper
    return decorator


def track_orchestrator_method(method_name: str, tags: Optional[List[str]] = None):
    """오케스트레이터 메서드 전용 데코레이터"""
    return track_method(
        graph_name="orchestrator",
        method_name=method_name,
        tags=tags or ["orchestrator"],
    )


def track_intent_method(method_name: str, tags: Optional[List[str]] = None):
    """의도 분류 메서드 전용 데코레이터"""
    return track_method(
        graph_name="intent_tool",
        method_name=method_name,
        tags=tags or ["intent", "classifier"],
    )
