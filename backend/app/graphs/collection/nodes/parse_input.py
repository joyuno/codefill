"""
Parse Input Node (Tool-based)

사용자 메시지 파싱 - LLM Tool 기반으로 리팩토링
- 임베딩 1차 매칭 + LLM 보조
- 복잡한 키워드 매칭 제거
- 긍정/부정/거절 분석을 Tool에 위임
"""

from typing import Dict, Any, Optional
from ..state import CollectionState
from app.tools.collection_tools import collection_tool


async def parse_input(state: CollectionState) -> Dict[str, Any]:
    """
    사용자 메시지 파싱 (Tool 기반)

    1. 확인 대기 상태면 → 긍정/부정 분석
    2. 아니면 → 값 추출
    3. 다음 단계 결정
    """
    message = state.get("message", "").strip()
    current_step = state.get("current_step", "topic")
    awaiting_confirmation = state.get("awaiting_confirmation", False)

    # 기존 값들
    existing_values = {
        "topic": state.get("topic"),
        "difficulty": state.get("difficulty"),
        "language": state.get("language"),
    }

    # 결과 초기화
    updates: Dict[str, Any] = {
        "is_question": False,
        "extracted_value": None,
        "question_type": None,
        "is_positive_response": False,
        "is_negative_response": False,
    }

    # ============================================================
    # 1. 확인 대기 상태: 긍정/부정 분석
    # ============================================================
    if awaiting_confirmation:
        suggested = state.get("suggested_value")
        confirmation = await collection_tool.analyze_confirmation(
            message=message,
            awaiting_value=suggested,
            current_step=current_step,
        )

        print(f"[parse_input] Confirmation: {confirmation.response} (conf={confirmation.confidence:.2f})")

        # 긍정 응답
        if confirmation.response == "positive":
            # 애매한 긍정 (재확인 필요)
            if confirmation.confidence < 0.65:
                print(f"[parse_input] Ambiguous positive, asking reconfirmation")
                updates["awaiting_confirmation"] = True
                updates["needs_reconfirmation"] = True
                return updates

            updates["is_positive_response"] = True
            updates["awaiting_confirmation"] = False

            # 긍정하면서 언급한 값 처리
            final_value = confirmation.extracted_value or suggested

            # 현재 단계 값 적용
            if final_value:
                updates[current_step] = final_value
                updates["extracted_value"] = final_value

            # 추가 정보 (원샷 입력: "정렬 쉬운 거로")
            if confirmation.has_additional_info and confirmation.additional_values:
                for step, value in confirmation.additional_values.items():
                    if step != current_step and value:
                        updates[step] = value
                        print(f"[parse_input] Additional {step}: {value}")

            # 다음 단계 결정
            updates["current_step"] = _determine_next_step(
                topic=updates.get("topic") or existing_values["topic"],
                difficulty=updates.get("difficulty") or existing_values["difficulty"],
                language=updates.get("language") or existing_values["language"],
            )
            print(f"[parse_input] Positive confirmed: {final_value}, next={updates['current_step']}")
            return updates

        # 부정 응답
        elif confirmation.response == "negative":
            updates["is_negative_response"] = True
            updates["awaiting_confirmation"] = False

            # 거절된 값 추적
            rejected_values = list(state.get("rejected_values", []))
            if suggested and suggested not in rejected_values:
                rejected_values.append(suggested)
            updates["rejected_values"] = rejected_values
            updates["suggested_value"] = None

            # 거절 분석 (이유 + 대안)
            rejection = await collection_tool.analyze_rejection(
                message=message,
                current_step=current_step,
                rejected_values=rejected_values,
            )
            print(f"[parse_input] Rejection: reason={rejection.reason}, alternative={rejection.alternative}")

            if rejection.reason:
                updates["rejection_reason"] = rejection.reason

            # 대안이 있으면 바로 적용
            if rejection.alternative:
                step = rejection.alternative_step or current_step
                updates[step] = rejection.alternative
                updates["is_negative_response"] = False  # 대안 선택이므로

                updates["current_step"] = _determine_next_step(
                    topic=updates.get("topic") or existing_values["topic"],
                    difficulty=updates.get("difficulty") or existing_values["difficulty"],
                    language=updates.get("language") or existing_values["language"],
                )
                print(f"[parse_input] Alternative selected: {rejection.alternative}")
                return updates

            # 대안 없으면 다시 추천 요청
            updates["is_question"] = True
            updates["question_type"] = "rejection"
            return updates

        # 불명확 → 값 추출 시도
        print(f"[parse_input] Unclear confirmation, trying value extraction...")

    # ============================================================
    # 2. 이미 모든 값이 수집된 경우 (complete 단계) → 바로 완료
    # ============================================================
    if current_step == "complete":
        print(f"[parse_input] Already complete, skipping extraction")
        updates["current_step"] = "complete"
        updates["is_complete"] = True
        return updates

    # ============================================================
    # 3. 값 추출 (질문 or 선택)
    # ============================================================
    extraction = await collection_tool.extract_values(
        message=message,
        current_step=current_step,
        existing_values=existing_values,
        use_llm_fallback=True,
    )

    print(f"[parse_input] Extraction: {extraction.values} (conf={extraction.confidence:.2f}, type={extraction.extraction_type})")

    # ============================================================
    # 3-1. 관련 없는 메시지 (off-topic) 처리
    # ============================================================
    is_off_topic = extraction.details.get("is_off_topic", False) if extraction.details else False
    if is_off_topic:
        print(f"[parse_input] Off-topic message detected, routing to handle with guidance")
        updates["is_question"] = True
        updates["question_type"] = "off_topic"
        updates["is_off_topic"] = True
        return updates

    # ============================================================
    # 3-2. 질문 메시지 처리 (Tool 기반)
    # ============================================================
    is_question_intent = extraction.details.get("is_question", False) if extraction.details else False
    question_info = extraction.details.get("question_info") if extraction.details else None

    if is_question_intent and question_info:
        print(f"[parse_input] Question detected via Tool: {question_info}")
        updates["is_question"] = True
        updates["question_type"] = question_info.get("question_type", "explanation")
        updates["question_info"] = question_info  # 전체 정보 전달
        return updates

    # 현재 단계 값 확인
    current_value = extraction.values.get(current_step)

    # 값이 추출되면 적용
    if current_value and extraction.confidence >= 0.60:
        updates[current_step] = current_value
        updates["extracted_value"] = current_value

        # 다른 단계 값도 함께 적용 (원샷 입력)
        for step in ["topic", "difficulty", "language"]:
            if step != current_step:
                value = extraction.values.get(step)
                if value and not existing_values.get(step):
                    updates[step] = value
                    print(f"[parse_input] Additional {step}: {value}")
    else:
        # ============================================================
        # 값이 추출되지 않은 경우 처리
        # ============================================================
        topic = existing_values.get("topic")
        difficulty = existing_values.get("difficulty")
        language = existing_values.get("language")
        message_lower = message.lower()

        # 먼저: 추천/모르겠다 요청인지 확인 → handle_question으로 라우팅
        recommendation_keywords = ["추천", "뭐가 좋", "알아서", "골라", "모르겠", "몰라", "수준에 맞", "레벨에 맞"]
        is_recommendation_request = any(kw in message_lower for kw in recommendation_keywords)

        if is_recommendation_request:
            # 추천 요청 → handle_question에서 개인화 추천
            updates["is_question"] = True
            updates["question_type"] = "recommendation"
            print(f"[parse_input] Recommendation request detected: {message}")
        # 이전 단계 값이 있고, 현재 단계 값이 없는 경우 → 다음 질문하러 가야 함
        elif topic and current_step == "difficulty" and not difficulty:
            # topic이 방금 설정됨 → 난이도 물어보러 confirm_value로
            print(f"[parse_input] Topic set, moving to difficulty selection")
            updates["is_question"] = False
        elif topic and difficulty and current_step == "language" and not language:
            # difficulty가 방금 설정됨 → 언어 물어보러 confirm_value로
            print(f"[parse_input] Difficulty set, moving to language selection")
            updates["is_question"] = False
        else:
            # 그 외에는 질문으로 처리
            updates["is_question"] = True
            updates["question_type"] = _classify_question_type(message)
            print(f"[parse_input] No value extracted, treating as question")

    # ============================================================
    # 4. 다음 단계 결정
    # ============================================================
    updates["current_step"] = _determine_next_step(
        topic=updates.get("topic") or existing_values["topic"],
        difficulty=updates.get("difficulty") or existing_values["difficulty"],
        language=updates.get("language") or existing_values["language"],
    )

    return updates


def _determine_next_step(
    topic: Optional[str],
    difficulty: Optional[str],
    language: Optional[str],
) -> str:
    """다음 수집 단계 결정"""
    if not topic:
        return "topic"
    if not difficulty:
        return "difficulty"
    if not language:
        return "language"
    return "complete"


def _classify_question_type(message: str) -> str:
    """질문 유형 분류 (간단한 키워드 체크)"""
    message_lower = message.lower()

    # 추천 요청
    if any(p in message_lower for p in ["추천", "뭐가 좋", "알아서", "골라", "아무"]):
        return "recommendation"

    # 설명 요청
    if any(p in message_lower for p in ["뭐야", "뭔데", "무슨", "어떤", "설명"]):
        return "explanation"

    # 비교 요청
    if any(p in message_lower for p in ["차이", "다른", "비교"]):
        return "comparison"

    return "general"


# ============================================================
# 라우팅 함수 (그래프용)
# ============================================================

def route_after_parse(state: CollectionState) -> str:
    """parse_input 후 라우팅 결정"""
    if state.get("is_question"):
        return "handle_question"

    current_step = state.get("current_step", "topic")

    if current_step == "complete":
        return "complete"
    elif current_step == "topic":
        return "choose_topic"
    elif current_step == "difficulty":
        return "choose_difficulty"
    elif current_step == "language":
        return "choose_language"
    else:
        return "handle_question"
