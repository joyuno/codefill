"""
LangSmith Statistics API

LLM 사용량, 노드 실행 통계, 에러 조회 API
"""

from fastapi import APIRouter, Depends, Query
from typing import Optional
from ..services.langsmith_tracker import langsmith_tracker
from ..core.langsmith_config import get_langsmith_status

router = APIRouter(prefix="/langsmith", tags=["langsmith"])


@router.get("/status")
async def get_status():
    """
    LangSmith 설정 상태 조회

    Returns:
        {
            "enabled": true/false,
            "configured": true/false,
            "project": "codefill-dev" | null
        }
    """
    return get_langsmith_status()


@router.get("/stats/recent")
async def get_recent_stats(
    minutes: int = Query(60, ge=1, le=1440, description="조회 기간 (분)")
):
    """
    최근 N분간의 통계 조회

    Returns:
        {
            "period_minutes": 60,
            "llm_calls": 50,
            "total_tokens": 10000,
            "avg_response_time_ms": 500,
            "error_count": 2,
            "nodes_executed": 150
        }
    """
    return langsmith_tracker.get_recent_stats(minutes=minutes)


@router.get("/stats/nodes")
async def get_node_stats():
    """
    노드별 실행 통계 조회

    Returns:
        {
            "classify_intent": {
                "count": 100,
                "avg_duration_ms": 50,
                "error_rate": 0.02
            },
            ...
        }
    """
    return langsmith_tracker.get_node_stats()


@router.get("/stats/session/{session_id}")
async def get_session_stats(session_id: str):
    """
    세션별 토큰 사용량 조회

    Returns:
        {
            "total_tokens": 1234,
            "tokens_by_model": {"openai/gpt-4o-mini": 1000},
            "estimated_cost_usd": 0.05
        }
    """
    return langsmith_tracker.get_session_stats(session_id)


@router.post("/clear")
async def clear_history():
    """
    트래킹 히스토리 초기화 (개발용)
    """
    langsmith_tracker.clear_history()
    return {"message": "History cleared"}


@router.get("/dashboard")
async def get_dashboard():
    """
    대시보드용 종합 통계

    Returns:
        {
            "langsmith_status": {...},
            "recent_stats": {...},
            "node_stats": {...}
        }
    """
    return {
        "langsmith_status": get_langsmith_status(),
        "recent_1h": langsmith_tracker.get_recent_stats(minutes=60),
        "recent_24h": langsmith_tracker.get_recent_stats(minutes=1440),
        "node_stats": langsmith_tracker.get_node_stats(),
    }
