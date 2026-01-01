"""
Info Collection Graph Nodes

각 노드는 단일 책임을 가지며, 상태를 업데이트하고 다음 노드로 전달합니다.

노드 구조:
- parse_input: 사용자 입력 파싱 (질문/선택 판단)
- handle_question: LLM으로 질문 답변 + 추천값 제안 (is_question=True일 때)
- confirm_value: 값 확정 + 다음 단계 이동 (통합)
- complete_collection: 정보 수집 완료
"""

from .parse_input import parse_input
from .handle_question import handle_question
from .complete import complete_collection

# 통합된 confirm_value 노드 (이전 choose_* 노드들 대체)
from .confirm_value import (
    confirm_value,
    choose_topic,       # Legacy wrapper
    choose_difficulty,  # Legacy wrapper
    choose_language,    # Legacy wrapper
    # Shared definitions
    TOPIC_CHIPS,
    DIFFICULTY_CHIPS,
    LANGUAGE_CHIPS,
)

__all__ = [
    "parse_input",
    "handle_question",
    "confirm_value",
    "choose_topic",
    "choose_difficulty",
    "choose_language",
    "complete_collection",
    # Chip definitions for reuse
    "TOPIC_CHIPS",
    "DIFFICULTY_CHIPS",
    "LANGUAGE_CHIPS",
]
