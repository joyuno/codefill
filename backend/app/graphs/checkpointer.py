"""
LangGraph Checkpointer Configuration

환경에 따른 Checkpointer 설정:
- development: MemorySaver (인메모리)
- production: PostgresSaver (Supabase PostgreSQL)

Usage:
    from .checkpointer import get_checkpointer

    async def init_graph():
        checkpointer = await get_checkpointer()
        graph = workflow.compile(checkpointer=checkpointer)
"""

import logging
from typing import Optional
from langgraph.checkpoint.memory import MemorySaver

from ..config import get_settings

logger = logging.getLogger(__name__)

# Checkpointer 싱글톤
_checkpointer: Optional[MemorySaver] = None
_checkpointer_initialized: bool = False


async def get_checkpointer():
    """
    환경에 따른 Checkpointer 반환

    - development: MemorySaver (인메모리, 재시작 시 초기화)
    - production: PostgresSaver (Supabase PostgreSQL, 영속적)

    Returns:
        Checkpointer 인스턴스
    """
    global _checkpointer, _checkpointer_initialized

    if _checkpointer_initialized:
        return _checkpointer

    settings = get_settings()

    # Development 환경: MemorySaver
    if settings.environment == "development" or not settings.supabase_db_url:
        logger.info("[Checkpointer] Using MemorySaver (in-memory)")
        _checkpointer = MemorySaver()
        _checkpointer_initialized = True
        return _checkpointer

    # Production 환경: PostgresSaver
    try:
        from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

        logger.info("[Checkpointer] Initializing PostgresSaver...")

        # PostgresSaver 생성 및 테이블 설정
        _checkpointer = await AsyncPostgresSaver.from_conn_string(
            settings.supabase_db_url
        )

        # 체크포인트 테이블 생성 (없으면)
        await _checkpointer.setup()

        logger.info("[Checkpointer] PostgresSaver initialized successfully")
        _checkpointer_initialized = True
        return _checkpointer

    except ImportError:
        logger.warning(
            "[Checkpointer] langgraph-checkpoint-postgres not installed. "
            "Falling back to MemorySaver."
        )
        _checkpointer = MemorySaver()
        _checkpointer_initialized = True
        return _checkpointer

    except Exception as e:
        logger.error(f"[Checkpointer] Failed to initialize PostgresSaver: {e}")
        logger.info("[Checkpointer] Falling back to MemorySaver")
        _checkpointer = MemorySaver()
        _checkpointer_initialized = True
        return _checkpointer


def get_sync_checkpointer():
    """
    동기 컨텍스트용 MemorySaver 반환 (개발/테스트용)

    Note: 실제 PostgresSaver가 필요하면 async 버전 사용
    """
    global _checkpointer

    if _checkpointer is None:
        _checkpointer = MemorySaver()

    return _checkpointer


async def close_checkpointer():
    """Checkpointer 연결 정리 (shutdown 시 호출)"""
    global _checkpointer, _checkpointer_initialized

    if _checkpointer is not None:
        try:
            # PostgresSaver는 close 메서드가 있음
            if hasattr(_checkpointer, 'close'):
                await _checkpointer.close()
            logger.info("[Checkpointer] Closed successfully")
        except Exception as e:
            logger.error(f"[Checkpointer] Error closing: {e}")

    _checkpointer = None
    _checkpointer_initialized = False


def create_thread_config(session_id: str, user_id: str = None) -> dict:
    """
    LangGraph 실행을 위한 config 생성

    Args:
        session_id: 세션 식별자 (대화 스레드)
        user_id: 사용자 ID (메타데이터용)

    Returns:
        LangGraph config 딕셔너리
    """
    config = {
        "configurable": {
            "thread_id": session_id,
        }
    }

    if user_id:
        config["configurable"]["user_id"] = user_id

    return config
