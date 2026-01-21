"""
LangSmith Configuration for CodeFill

LangGraph 트레이싱 및 평가를 위한 설정:
- 자동 트레이싱 활성화
- 토큰 사용량 추적
- 커스텀 메타데이터 로깅
"""

import os
import logging
from typing import Optional, Dict, Any
from functools import wraps
from datetime import datetime

logger = logging.getLogger(__name__)

# ============================================================
# 환경변수 설정 확인
# ============================================================

LANGSMITH_ENABLED = os.getenv("LANGCHAIN_TRACING_V2", "").lower() == "true"
LANGSMITH_API_KEY = os.getenv("LANGCHAIN_API_KEY", "")
LANGSMITH_PROJECT = os.getenv("LANGCHAIN_PROJECT", "codefill-dev")
LANGSMITH_ENDPOINT = os.getenv("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com")


def is_langsmith_configured() -> bool:
    """LangSmith가 올바르게 설정되어 있는지 확인"""
    return bool(LANGSMITH_ENABLED and LANGSMITH_API_KEY)


def get_langsmith_status() -> Dict[str, Any]:
    """LangSmith 상태 반환"""
    return {
        "enabled": LANGSMITH_ENABLED,
        "configured": is_langsmith_configured(),
        "project": LANGSMITH_PROJECT if is_langsmith_configured() else None,
        "endpoint": LANGSMITH_ENDPOINT if is_langsmith_configured() else None,
    }


# ============================================================
# 트레이싱 유틸리티
# ============================================================

def with_langsmith_metadata(
    node_name: str,
    graph_name: str,
    extra_metadata: Optional[Dict[str, Any]] = None
):
    """
    LangGraph 노드에 LangSmith 메타데이터 추가

    사용법:
        @with_langsmith_metadata("classify_intent", "orchestrator")
        async def classify_intent(state):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            import langsmith

            # 메타데이터 구성
            metadata = {
                "node_name": node_name,
                "graph_name": graph_name,
                "timestamp": datetime.utcnow().isoformat(),
            }
            if extra_metadata:
                metadata.update(extra_metadata)

            # LangSmith가 활성화되어 있으면 run context 사용
            if is_langsmith_configured():
                try:
                    with langsmith.trace(
                        name=f"{graph_name}/{node_name}",
                        metadata=metadata,
                    ) as run:
                        result = await func(*args, **kwargs)

                        # 결과 메타데이터 추가
                        if isinstance(result, dict):
                            run.extra = run.extra or {}
                            run.extra["outputs"] = {
                                k: str(v)[:500] if isinstance(v, str) else v
                                for k, v in result.items()
                                if k in ("response_message", "next_node", "intent")
                            }

                        return result
                except Exception as e:
                    logger.warning(f"LangSmith tracing error: {e}")
                    return await func(*args, **kwargs)
            else:
                return await func(*args, **kwargs)

        return wrapper
    return decorator


class LangSmithMetrics:
    """
    LangSmith 메트릭 수집기

    각 노드의 실행 정보를 수집하고 LangSmith에 전송
    """

    def __init__(self):
        self._client = None

    @property
    def client(self):
        """Lazy loading for LangSmith client"""
        if self._client is None and is_langsmith_configured():
            try:
                from langsmith import Client
                self._client = Client()
            except ImportError:
                logger.warning("langsmith package not installed")
        return self._client

    def log_node_execution(
        self,
        node_name: str,
        graph_name: str,
        start_time: datetime,
        end_time: datetime,
        input_data: Optional[Dict[str, Any]] = None,
        output_data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        token_usage: Optional[Dict[str, int]] = None,
    ):
        """
        노드 실행 정보 로깅

        Args:
            node_name: 노드 이름
            graph_name: 그래프 이름
            start_time: 시작 시간
            end_time: 종료 시간
            input_data: 입력 데이터
            output_data: 출력 데이터
            error: 에러 메시지
            token_usage: 토큰 사용량 {"prompt_tokens": x, "completion_tokens": y, "total_tokens": z}
        """
        duration_ms = (end_time - start_time).total_seconds() * 1000

        log_data = {
            "node_name": node_name,
            "graph_name": graph_name,
            "duration_ms": duration_ms,
            "has_error": bool(error),
            "token_usage": token_usage,
        }

        logger.info(f"[LangSmith] {graph_name}/{node_name} - {duration_ms:.2f}ms")

        if error:
            logger.error(f"[LangSmith] {node_name} error: {error}")

    def log_llm_call(
        self,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        total_tokens: int,
        duration_ms: float,
        node_name: Optional[str] = None,
    ):
        """
        LLM 호출 정보 로깅

        Args:
            model: 모델 이름
            prompt_tokens: 프롬프트 토큰 수
            completion_tokens: 완료 토큰 수
            total_tokens: 총 토큰 수
            duration_ms: 응답 시간 (ms)
            node_name: 호출한 노드 이름
        """
        logger.info(
            f"[LangSmith] LLM Call - model={model}, "
            f"tokens={total_tokens} (p:{prompt_tokens}, c:{completion_tokens}), "
            f"duration={duration_ms:.2f}ms"
        )


# 싱글톤 인스턴스
langsmith_metrics = LangSmithMetrics()


# ============================================================
# 콜백 핸들러
# ============================================================

class LangSmithCallbackHandler:
    """
    LLM 호출 시 자동으로 토큰 사용량을 기록하는 콜백 핸들러

    OpenRouter/OpenAI 호출 시 사용:
        response = await openrouter_service.chat_completion(
            model="...",
            messages=[...],
            callbacks=[langsmith_callback_handler],
        )
    """

    def __init__(self):
        self.runs = []

    async def on_llm_start(self, model: str, messages: list):
        """LLM 호출 시작"""
        self.runs.append({
            "model": model,
            "start_time": datetime.utcnow(),
            "prompt_messages": len(messages),
        })

    async def on_llm_end(
        self,
        response: str,
        usage: Optional[Dict[str, int]] = None,
    ):
        """LLM 호출 종료"""
        if self.runs:
            run = self.runs.pop()
            end_time = datetime.utcnow()
            duration_ms = (end_time - run["start_time"]).total_seconds() * 1000

            if usage:
                langsmith_metrics.log_llm_call(
                    model=run.get("model", "unknown"),
                    prompt_tokens=usage.get("prompt_tokens", 0),
                    completion_tokens=usage.get("completion_tokens", 0),
                    total_tokens=usage.get("total_tokens", 0),
                    duration_ms=duration_ms,
                )

    async def on_llm_error(self, error: Exception):
        """LLM 호출 에러"""
        if self.runs:
            run = self.runs.pop()
            logger.error(f"[LangSmith] LLM error in {run.get('model')}: {error}")


# 싱글톤 인스턴스
langsmith_callback_handler = LangSmithCallbackHandler()


# ============================================================
# 초기화 함수
# ============================================================

def init_langsmith():
    """LangSmith 초기화 (앱 시작 시 호출)"""
    status = get_langsmith_status()

    if status["configured"]:
        logger.info(f"✅ LangSmith configured - project: {status['project']}")

        # 환경변수 재확인 (LangChain이 자동으로 읽음)
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_PROJECT"] = LANGSMITH_PROJECT
    else:
        logger.warning(
            "⚠️ LangSmith not configured. Set LANGCHAIN_TRACING_V2=true and LANGCHAIN_API_KEY"
        )

    return status
