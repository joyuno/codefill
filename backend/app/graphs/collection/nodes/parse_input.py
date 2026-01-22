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
from app.services.langsmith_tracker import track_collection_node


@track_collection_node("parse_input", tags=["parsing"])
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
    # 2-1. LLM 기반 의도 분석 (Agentic)
    # ============================================================
    # 먼저 통합 분석으로 의도 파악
    context = f"현재 단계: {current_step}, 기존 값: topic={existing_values.get('topic')}, difficulty={existing_values.get('difficulty')}, language={existing_values.get('language')}"
    analysis = await collection_tool.analyze(message, context)

    print(f"[parse_input] LLM Analysis: intent={analysis.intent}, rejected={analysis.rejected}, "
          f"rejection_reason={analysis.rejection_reason}, alternative={analysis.alternative}")

    # ============================================================
    # 2-2. 주제/난이도/언어 변경 요청 감지 (LLM 기반)
    # ============================================================
    # LLM이 "negative" intent + rejection_reason 감지하면 변경 요청으로 처리
    is_change_request = (
        analysis.intent == "negative" and
        analysis.rejection_reason in ["want_different", "not_interested", "already_done"]
    )

    # rejected 필드에 값이 있으면 해당 단계 변경 요청
    change_step = None
    rejected_item = None
    for step in ["topic", "difficulty", "language"]:
        if analysis.rejected.get(step):
            rejected_item = analysis.rejected.get(step)
            # 기존 값과 일치하거나, 기존 값이 있는데 "다른거"라고 하면
            existing_val = existing_values.get(step)
            if existing_val:
                change_step = step
                print(f"[parse_input] Change request detected for {step}: rejected='{rejected_item}', existing='{existing_val}'")
                break

    # 기존 값이 있는 상태에서 "다른거", "싫어" 등 부정 의도 감지
    if not change_step and analysis.intent == "negative" and analysis.rejection_reason:
        # 가장 최근 설정된 값의 변경으로 추정
        if existing_values.get("language"):
            change_step = "language"
        elif existing_values.get("difficulty"):
            change_step = "difficulty"
        elif existing_values.get("topic"):
            change_step = "topic"

        if change_step:
            rejected_item = existing_values.get(change_step)
            print(f"[parse_input] Inferred change request for {change_step}: '{rejected_item}'")

    if is_change_request and change_step:
        existing_val = existing_values.get(change_step)
        print(f"[parse_input] Processing {change_step} change request: '{message}'")

        # 해당 값 초기화 및 rejected_values에 추가
        rejected_values = list(state.get("rejected_values", []))
        if existing_val and existing_val not in rejected_values:
            rejected_values.append(existing_val)

        updates[change_step] = None
        updates["rejected_values"] = rejected_values
        updates["current_step"] = change_step
        updates["is_negative_response"] = True
        updates["awaiting_confirmation"] = False
        updates["suggested_value"] = None

        # 대안이 있으면 바로 적용
        if analysis.alternative and analysis.alternative.get("value"):
            alt_value = analysis.alternative.get("value")
            alt_step = analysis.alternative.get("step") or change_step
            updates[alt_step] = alt_value
            updates["is_negative_response"] = False
            updates["current_step"] = _determine_next_step(
                topic=updates.get("topic") or (existing_values["topic"] if alt_step != "topic" else None),
                difficulty=updates.get("difficulty") or (existing_values["difficulty"] if alt_step != "difficulty" else None),
                language=updates.get("language") or (existing_values["language"] if alt_step != "language" else None),
            )
            print(f"[parse_input] Alternative selected: {alt_step}={alt_value}")
        else:
            # 대안 없으면 거절 분석으로 찾기
            rejection = await collection_tool.analyze_rejection(
                message=message,
                current_step=change_step,
                rejected_values=rejected_values,
            )
            print(f"[parse_input] Rejection analysis: reason={rejection.reason}, alternative={rejection.alternative}")

            if rejection.alternative:
                updates[change_step] = rejection.alternative
                updates["is_negative_response"] = False
                updates["current_step"] = _determine_next_step(
                    topic=updates.get("topic") or (existing_values["topic"] if change_step != "topic" else rejection.alternative),
                    difficulty=updates.get("difficulty") or (existing_values["difficulty"] if change_step != "difficulty" else rejection.alternative),
                    language=updates.get("language") or (existing_values["language"] if change_step != "language" else rejection.alternative),
                )
                print(f"[parse_input] Rejection alternative: {change_step}={rejection.alternative}")

        return updates

    # ============================================================
    # 3. 값 추출 (질문 or 선택) - 분석 결과 재사용
    # ============================================================
    # 이미 analyze() 호출했으므로 extract_values 대신 분석 결과 사용
    extraction = await collection_tool.extract_values(
        message=message,
        current_step=current_step,
        existing_values=existing_values,
        use_llm_fallback=True,
    )

    print(f"[parse_input] Extraction: {extraction.values} (conf={extraction.confidence:.2f}, type={extraction.extraction_type})")

    # ============================================================
    # 3-0. 확장 의도 처리 (코딩 학습 관련이지만 정보 수집과 무관)
    # ============================================================
    extended_intents = ["coding_concept", "syntax_help", "error_debug", "learning_advice",
                       "code_review", "hint_request", "progress_inquiry", "service_help",
                       "account_inquiry", "greeting", "chitchat"]

    llm_intent = extraction.details.get("intent") if extraction.details else None

    if llm_intent in extended_intents:
        print(f"[parse_input] Extended intent detected: {llm_intent}")
        updates["is_question"] = True
        updates["question_type"] = llm_intent  # 확장 의도 타입 그대로 전달
        updates["extended_intent"] = llm_intent
        # extended_info도 전달 (있는 경우)
        if extraction.details:
            updates["extended_info"] = extraction.details.get("extended_info")
        return updates

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

    # ============================================================
    # 3-2-1. 주제 목록 요청 감지 (키워드 기반 fallback)
    # "주제 다 보여줘", "전부 알려줘", "목록", "뭐뭐 있어?" 등
    # ============================================================
    message_lower = message.lower()
    is_topic_list_request = False

    # 키워드 기반 감지 (LLM 분석 보완용 fallback)
    topic_list_keywords = ["전부", "목록", "다 보여", "다 알려", "뭐가 있", "뭐 있", "종류", "카테고리",
                           "어떤 게 있", "있는 거", "선택지", "골라", "고를게", "내가 선택"]
    if any(kw in message_lower for kw in topic_list_keywords):
        is_topic_list_request = True
        print(f"[parse_input] Topic list request detected via keyword: {message[:50]}")

    # LLM 분석 결과에서 topic_list 감지
    if question_info and question_info.get("question_type") == "topic_list":
        is_topic_list_request = True
        print(f"[parse_input] Topic list request detected via LLM: {question_info}")

    # topic_list 요청이면 바로 handle_question으로 라우팅
    if is_topic_list_request:
        updates["is_question"] = True
        updates["question_type"] = "topic_list"
        updates["question_info"] = question_info or {"question_type": "topic_list", "question_target": "topic"}
        print(f"[parse_input] Routing to topic_list handler, current_step={current_step}")
        return updates

    # ============================================================
    # 3-2-2. 추천 요청 감지 ("너가 추천해줘", "알아서 해줘")
    # → 확인 없이 바로 값을 확정하고 다음 단계로 이동
    # ============================================================
    is_auto_recommend_request = False
    auto_recommend_keywords = ["너가 추천", "네가 추천", "알아서", "니가 골라", "네가 골라",
                               "추천해줘", "추천해", "랜덤으로", "아무거나"]

    if any(kw in message_lower for kw in auto_recommend_keywords):
        is_auto_recommend_request = True
        print(f"[parse_input] Auto-recommend request detected: {message[:50]}")

    # LLM 분석에서 recommendation 감지
    if question_info and question_info.get("question_type") == "recommendation":
        is_auto_recommend_request = True
        print(f"[parse_input] Auto-recommend detected via LLM")

    if is_auto_recommend_request:
        # 현재 단계에 대해 자동 추천값 선택
        from .handle_question import _get_non_rejected_default, fetch_user_profile_and_recommendations

        user_context = state.get("user_context", {}) or {}
        user_id = user_context.get("user_id") or user_context.get("id")
        rejected_values = list(state.get("rejected_values", []))

        # 개인화 추천 가져오기
        tool_result = await fetch_user_profile_and_recommendations(user_id, user_context)
        personalized = tool_result["recommendations"]

        # 현재 단계에 맞는 추천값 선택
        auto_value = None
        if current_step == "topic":
            auto_value = personalized.get("recommended_topic")
            if not auto_value:
                topic_options = personalized.get("topic_options", [])
                if topic_options:
                    import random
                    auto_value = random.choice(topic_options)
                else:
                    auto_value = _get_non_rejected_default("topic", rejected_values, None, None)
        elif current_step == "difficulty":
            auto_value = personalized.get("recommended_difficulty") or "medium"
        elif current_step == "language":
            auto_value = personalized.get("recommended_language") or "python"

        if auto_value:
            updates[current_step] = auto_value
            updates["auto_recommended"] = True  # 자동 추천임을 표시
            updates["auto_recommended_value"] = auto_value
            updates["current_step"] = _determine_next_step(
                topic=updates.get("topic") or existing_values["topic"],
                difficulty=updates.get("difficulty") or existing_values["difficulty"],
                language=updates.get("language") or existing_values["language"],
            )
            print(f"[parse_input] Auto-recommend applied: {current_step}={auto_value}, next_step={updates['current_step']}")
            return updates

    if is_question_intent and question_info:
        print(f"[parse_input] Question detected via Tool: {question_info}")
        updates["is_question"] = True
        updates["question_type"] = question_info.get("question_type", "explanation")
        updates["question_info"] = question_info  # 전체 정보 전달

        # 🔧 FIX: 질문과 함께 값도 추출됐으면 저장 (동시 처리)
        # 예: "파이썬으로 할게 근데 골드면 어느정도야?" → language=python + 질문 응답
        extracted_with_question = {}  # 이번 턴에 추출된 값 (handle_question에서 응답에 포함)
        for step in ["topic", "difficulty", "language"]:
            value = extraction.values.get(step)
            if value and extraction.confidence >= 0.50:
                if not existing_values.get(step):  # 기존 값이 없을 때만
                    updates[step] = value
                    extracted_with_question[step] = value
                    print(f"[parse_input] Value extracted with question: {step}={value}")

        # 추출된 값 정보를 handle_question에 전달
        if extracted_with_question:
            updates["extracted_with_question"] = extracted_with_question

        # 다음 단계도 업데이트 (추출된 값 반영)
        updates["current_step"] = _determine_next_step(
            topic=updates.get("topic") or existing_values["topic"],
            difficulty=updates.get("difficulty") or existing_values["difficulty"],
            language=updates.get("language") or existing_values["language"],
        )
        return updates

    # 현재 단계 값 확인
    current_value = extraction.values.get(current_step)

    # ============================================================
    # 키워드 기반 직접 매핑 (LLM 실패 시 fallback)
    # ============================================================
    # message_lower는 위에서 이미 정의됨

    # 난이도 직접 매핑
    DIFFICULTY_KEYWORDS = {
        "실버": "easy", "silver": "easy", "쉬움": "easy", "쉬운": "easy", "쉬운거": "easy", "easy": "easy",
        "골드": "medium", "gold": "medium", "중간": "medium", "보통": "medium", "medium": "medium",
        "플래티넘": "medium_hard", "플레티넘": "medium_hard", "platinum": "medium_hard",
        "다이아": "hard", "다이아몬드": "hard", "diamond": "hard", "어려움": "hard", "어려운": "hard", "hard": "hard",
        "마스터": "very_hard", "master": "very_hard",
    }

    # 언어 직접 매핑
    LANGUAGE_KEYWORDS = {
        "파이썬": "python", "python": "python", "py": "python",
        "자바": "java", "java": "java",
        "씨플플": "cpp", "c++": "cpp", "cpp": "cpp", "씨쁠쁠": "cpp",
    }

    # LLM 추출 실패 시 직접 매핑으로 보완
    direct_mapped = False
    if not current_value or extraction.confidence < 0.60:
        if current_step == "difficulty":
            for keyword, value in DIFFICULTY_KEYWORDS.items():
                if keyword in message_lower:
                    current_value = value
                    direct_mapped = True
                    print(f"[parse_input] Direct mapping: difficulty={value} from '{keyword}'")
                    break
        elif current_step == "language":
            for keyword, value in LANGUAGE_KEYWORDS.items():
                if keyword in message_lower:
                    current_value = value
                    direct_mapped = True
                    print(f"[parse_input] Direct mapping: language={value} from '{keyword}'")
                    break

    # 변경 의도 감지 (LLM 기반 - 하드코딩 키워드 제거)
    # 1. LLM이 분류한 intent가 "negative"인 경우
    # 2. LLM이 거절(rejection)을 감지한 경우
    # 3. 새 값이 추출되었고 기존 값과 다른 경우
    llm_intent = extraction.details.get("intent") if extraction.details else None
    is_rejection_detected = extraction.details.get("is_rejection", False) if extraction.details else False

    is_change_request = (
        llm_intent == "negative" or
        is_rejection_detected or
        # 새 값이 추출되었고 기존 값과 다르면 변경 요청으로 간주
        any(
            extraction.values.get(step) and
            existing_values.get(step) and
            extraction.values.get(step).lower() != existing_values.get(step).lower()
            for step in ["topic", "difficulty", "language"]
        )
    )

    if is_change_request:
        print(f"[parse_input] Change request detected: intent={llm_intent}, is_rejection={is_rejection_detected}")

    # 값이 추출되면 적용 (직접 매핑이면 confidence 무시)
    if current_value and (extraction.confidence >= 0.60 or direct_mapped):
        updates[current_step] = current_value
        updates["extracted_value"] = current_value

        # 다른 단계 값도 함께 적용 (원샷 입력)
        for step in ["topic", "difficulty", "language"]:
            if step != current_step:
                value = extraction.values.get(step)
                # 변경 요청이면 기존 값이 있어도 덮어쓰기
                if value and (not existing_values.get(step) or is_change_request):
                    updates[step] = value
                    print(f"[parse_input] Additional {step}: {value} (change_request={is_change_request})")

    # 현재 단계 값은 없지만 다른 단계 값이 추출된 경우 (변경 요청)
    elif not current_value and extraction.confidence >= 0.60 and is_change_request:
        for step in ["topic", "difficulty", "language"]:
            value = extraction.values.get(step)
            if value:
                updates[step] = value
                updates["extracted_value"] = value
                print(f"[parse_input] Change request: {step}={value}")
    else:
        # ============================================================
        # 값이 추출되지 않은 경우 처리 (LLM 기반 분석 사용)
        # ============================================================
        topic = existing_values.get("topic")
        difficulty = existing_values.get("difficulty")
        language = existing_values.get("language")

        # LLM 분석 결과에서 추천 요청 감지 (키워드 기반 제거)
        is_recommendation_request = (
            analysis.intent == "question" and
            analysis.question_info and
            analysis.question_info.question_type == "recommendation"
        )

        if is_recommendation_request:
            # 추천 요청 → handle_question에서 개인화 추천
            updates["is_question"] = True
            updates["question_type"] = "recommendation"
            print(f"[parse_input] Recommendation request detected (LLM): {message}")
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
            # 그 외에는 질문으로 처리 (LLM 분석 결과 활용)
            updates["is_question"] = True
            # 이미 분석된 question_info 사용
            if analysis.intent == "question" and analysis.question_info:
                question_type = analysis.question_info.question_type or "general"
                # 내부 타입으로 매핑
                type_mapping = {
                    "explanation": "explanation",
                    "comparison": "comparison",
                    "difficulty_inquiry": "explanation",
                    "recommendation": "recommendation",
                    "how_to": "explanation",
                }
                updates["question_type"] = type_mapping.get(question_type, "general")
            else:
                updates["question_type"] = "general"
            print(f"[parse_input] No value extracted, treating as question (type={updates['question_type']})")

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


async def _classify_question_type_async(message: str, analysis_result=None) -> str:
    """
    질문 유형 분류 (LLM 기반)

    Args:
        message: 사용자 메시지
        analysis_result: 이미 분석된 UnifiedAnalysisResult (있으면 재사용)

    Returns:
        질문 유형 문자열
    """
    # 이미 분석된 결과가 있고 question_info가 있으면 사용
    if analysis_result and analysis_result.question_info:
        question_type = analysis_result.question_info.question_type
        if question_type:
            # LLM의 question_type을 내부 타입으로 매핑
            type_mapping = {
                "explanation": "explanation",
                "comparison": "comparison",
                "difficulty_inquiry": "explanation",  # 난이도 질문도 설명으로 처리
                "recommendation": "recommendation",
                "how_to": "explanation",
            }
            return type_mapping.get(question_type, "general")

    # 분석 결과가 없으면 새로 분석
    if analysis_result is None:
        analysis_result = await collection_tool.analyze(message)

    # 질문이 아니면 general
    if analysis_result.intent != "question":
        return "general"

    # question_info에서 유형 추출
    if analysis_result.question_info:
        question_type = analysis_result.question_info.question_type

        # 주제 목록 요청 감지
        question_subjects = analysis_result.question_info.question_subjects or []
        if any(subj in ["목록", "전체", "있는", "종류", "카테고리"]
               for subj in question_subjects):
            return "topic_list"

        # question_type 매핑
        if question_type == "recommendation":
            return "recommendation"
        elif question_type in ["explanation", "difficulty_inquiry", "how_to"]:
            return "explanation"
        elif question_type == "comparison":
            return "comparison"

    return "general"


def _classify_question_type(message: str) -> str:
    """
    질문 유형 분류 (동기 버전 - 간단한 fallback용)

    Note: 가능하면 _classify_question_type_async를 사용하세요.
    """
    message_lower = message.lower()

    # 주제 목록 요청 (topic_list)
    if any(kw in message_lower for kw in ["주제 목록", "주제 다", "주제가 뭐",
                                           "어떤 주제", "무슨 주제"]):
        return "topic_list"

    # 추천 요청
    if any(p in message_lower for p in ["추천", "뭐가 좋", "알아서", "골라"]):
        return "recommendation"

    # 설명 요청
    if any(p in message_lower for p in ["뭐야", "뭔데", "설명"]):
        return "explanation"

    # 비교 요청
    if any(p in message_lower for p in ["차이", "비교"]):
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
