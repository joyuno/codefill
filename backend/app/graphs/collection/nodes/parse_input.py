"""
Parse Input Node

사용자 메시지에서 직접 정보를 추출하는 노드
LLM 없이 패턴 매칭으로 빠르게 처리
"""
import re
from typing import Dict, Any, Optional
from ..state import (
    CollectionState,
    VALID_TOPICS,
    VALID_DIFFICULTIES,
    VALID_LANGUAGES,
    TOPIC_NORMALIZE,
    DIFFICULTY_NORMALIZE,
    LANGUAGE_NORMALIZE,
    QUESTION_PATTERNS,
    RECOMMENDATION_PATTERNS,
)


def parse_input(state: CollectionState) -> Dict[str, Any]:
    """
    사용자 메시지를 파싱하여 정보 추출

    1. 질문인지 선택인지 판단
    2. 현재 단계에 맞는 값 추출
    3. 추출된 값 정규화
    """
    message = state.get("message", "").lower().strip()
    current_step = state.get("current_step", "topic")

    # 결과 초기화
    updates: Dict[str, Any] = {
        "is_question": False,
        "extracted_value": None,
        "question_type": None,
    }

    # ============================================================
    # 1. 질문 패턴 감지
    # ============================================================
    is_question = _detect_question(message)
    if is_question:
        updates["is_question"] = True
        updates["question_type"] = _classify_question_type(message)
        return updates

    # ============================================================
    # 2. 현재 단계에 따른 값 추출
    # ============================================================
    if current_step == "topic":
        extracted = _extract_topic(message)
        if extracted:
            updates["extracted_value"] = extracted
            updates["topic"] = extracted

    elif current_step == "difficulty":
        extracted = _extract_difficulty(message)
        if extracted:
            updates["extracted_value"] = extracted
            updates["difficulty"] = extracted

    elif current_step == "language":
        extracted = _extract_language(message)
        if extracted:
            updates["extracted_value"] = extracted
            updates["language"] = extracted

    # ============================================================
    # 3. 모든 단계에서 한 번에 여러 정보가 들어올 수 있음
    # ============================================================
    # 예: "파이썬으로 쉬운 DP 문제 풀래"
    if not updates.get("topic"):
        topic = _extract_topic(message)
        if topic:
            updates["topic"] = topic

    if not updates.get("difficulty"):
        difficulty = _extract_difficulty(message)
        if difficulty:
            updates["difficulty"] = difficulty

    if not updates.get("language"):
        language = _extract_language(message)
        if language:
            updates["language"] = language

    # ============================================================
    # 4. 다음 단계 결정
    # ============================================================
    updates["current_step"] = _determine_next_step(
        topic=updates.get("topic") or state.get("topic"),
        difficulty=updates.get("difficulty") or state.get("difficulty"),
        language=updates.get("language") or state.get("language"),
    )

    return updates


def _detect_question(message: str) -> bool:
    """질문인지 판단"""
    # 질문 패턴 검사
    for pattern in QUESTION_PATTERNS:
        if pattern in message:
            # 단순 선택인지 질문인지 구분
            # "DP로 할게" vs "DP가 뭐야?"
            selection_indicators = ["할게", "할래", "으로", "로 해", "선택"]
            is_selection = any(ind in message for ind in selection_indicators)

            if not is_selection:
                return True

    # 물음표가 있으면 질문
    if "?" in message:
        return True

    return False


def _classify_question_type(message: str) -> str:
    """질문 유형 분류"""
    # 추천 요청
    for pattern in RECOMMENDATION_PATTERNS:
        if pattern in message:
            return "recommendation"

    # 설명 요청
    explanation_patterns = ["뭐야", "뭔데", "뭐지", "무슨", "어떤", "설명"]
    if any(p in message for p in explanation_patterns):
        return "explanation"

    # 비교 요청
    comparison_patterns = ["차이", "다른", "뭐가 다", "비교"]
    if any(p in message for p in comparison_patterns):
        return "comparison"

    return "general"


def _extract_topic(message: str) -> Optional[str]:
    """메시지에서 주제 추출"""
    message_lower = message.lower()

    # 직접 매칭
    for keyword in VALID_TOPICS:
        if keyword.lower() in message_lower:
            return TOPIC_NORMALIZE.get(keyword.lower(), keyword)

    # "기초", "기본" 등 추가 패턴
    if any(p in message for p in ["기초", "기본", "쉬운거", "처음"]):
        return "기초"

    # "아무거나", "랜덤" 등
    if any(p in message for p in ["아무", "랜덤", "random"]):
        return "기초"  # 기본값으로 기초 선택

    return None


def _extract_difficulty(message: str) -> Optional[str]:
    """메시지에서 난이도 추출"""
    message_lower = message.lower()

    # 직접 매칭
    for keyword in VALID_DIFFICULTIES:
        if keyword.lower() in message_lower:
            return DIFFICULTY_NORMALIZE.get(keyword.lower(), keyword)

    # 추가 패턴: "쉬" 포함 → easy
    if "쉬" in message:
        return "easy"

    # "어렵" 포함 → hard
    if "어렵" in message or "어려" in message:
        return "hard"

    # "중간", "보통" 포함 → medium
    if "중간" in message or "보통" in message:
        return "medium"

    return None


def _extract_language(message: str) -> Optional[str]:
    """메시지에서 언어 추출"""
    message_lower = message.lower()

    # 직접 매칭
    for keyword in VALID_LANGUAGES:
        if keyword.lower() in message_lower:
            return LANGUAGE_NORMALIZE.get(keyword.lower(), keyword)

    # 추가 패턴
    if "파이" in message or "py" in message_lower:
        return "python"

    if "자바" in message and "스크립트" not in message:  # JavaScript 제외
        return "java"

    if "씨플" in message or "c++" in message_lower or "cpp" in message_lower:
        return "cpp"

    return None


def _determine_next_step(topic: Optional[str], difficulty: Optional[str], language: Optional[str]) -> str:
    """다음 수집 단계 결정"""
    if not topic:
        return "topic"
    if not difficulty:
        return "difficulty"
    if not language:
        return "language"
    return "complete"
