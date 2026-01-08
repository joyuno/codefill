"""
Info Collection Graph

LangGraph를 사용한 정보 수집 그래프 정의

New Flow (이미지 기반):
    START → parse_input
              ↓
         [is_question?]
              ├─ True → handle_question → END (awaiting_confirmation)
              ↓ False
         [current_step?]
              ├─ topic → choose_topic → END
              ├─ difficulty → choose_difficulty → END
              ├─ language → choose_language → END
              └─ complete → complete_collection → END

핵심 변경:
- is_question=True: handle_question (LLM 추천 + 네/아니오 대기)
- is_question=False: choose_* (직접 선택 확정)
- 네/아니오 응답은 다음 턴의 parse_input에서 처리
"""
from typing import Dict, Any, List, Optional
from langgraph.graph import StateGraph, END

from .state import CollectionState, get_initial_state
from .nodes import (
    parse_input,
    handle_question,
    confirm_value,  # 통합된 노드
    complete_collection,
)


def _route_after_parse(state: CollectionState) -> str:
    """
    parse_input 후 라우팅 결정

    - is_question=True → handle_question (LLM 추천)
    - needs_reconfirmation=True → handle_question (재확인 질문)
    - current_step=complete → complete
    - else → confirm_value (값 확정)
    """
    # 애매한 응답 재확인 필요 → handle_question
    if state.get("needs_reconfirmation"):
        return "handle_question"

    # 질문이면 handle_question으로 (LLM 추천 + 네/아니오 칩)
    if state.get("is_question"):
        return "handle_question"

    # 완료 단계
    if state.get("current_step") == "complete":
        return "complete"

    # 직접 선택 → 통합 confirm_value 노드
    return "confirm_value"


def _route_after_handle_question(state: CollectionState) -> str:
    """
    handle_question 후 라우팅

    handle_question은 항상 응답 메시지와 함께 종료
    awaiting_confirmation=True 상태로 END
    """
    return END


def _route_after_choose(state: CollectionState) -> str:
    """
    choose_* 노드 후 라우팅

    값 확정 후:
    - 다음 단계 값이 필요하면 → 해당 choose_* 노드로 (체인)
    - 모든 값이 있으면 → complete
    - 응답 메시지가 있으면 → END (사용자에게 다음 질문 표시)
    """
    # 응답 메시지가 있으면 일단 END (다음 턴에서 계속)
    if state.get("response_message"):
        return END

    # 완료 상태면 complete로
    if state.get("is_complete") or state.get("current_step") == "complete":
        return "complete"

    return END


def create_info_collection_graph() -> StateGraph:
    """
    정보 수집 그래프 생성 (간소화된 구조)

    Flow:
        parse_input → [is_question?]
                      ├─ Yes → handle_question → END
                      └─ No → confirm_value → END
                              (또는 complete → END)
    """
    builder = StateGraph(CollectionState)

    # ============================================================
    # 노드 추가 (간소화: 3개 choose_* → 1개 confirm_value)
    # ============================================================
    builder.add_node("parse_input", parse_input)
    builder.add_node("handle_question", handle_question)
    builder.add_node("confirm_value", confirm_value)  # 통합 노드
    builder.add_node("complete", complete_collection)

    # ============================================================
    # 엣지 정의
    # ============================================================
    builder.set_entry_point("parse_input")

    # parse_input 후 조건부 라우팅
    builder.add_conditional_edges(
        "parse_input",
        _route_after_parse,
        {
            "handle_question": "handle_question",
            "confirm_value": "confirm_value",
            "complete": "complete",
        },
    )

    # 모든 노드 → END
    builder.add_edge("handle_question", END)
    builder.add_edge("confirm_value", END)
    builder.add_edge("complete", END)

    return builder.compile()


class InfoCollectionGraph:
    """정보 수집 그래프 래퍼 클래스"""

    def __init__(self):
        self.graph = create_info_collection_graph()

    async def invoke(
        self,
        message: str,
        conversation_history: List[Dict[str, str]] = None,
        user_context: Dict[str, Any] = None,
        existing_topic: str = None,
        existing_difficulty: str = None,
        existing_language: str = None,
        existing_awaiting_confirmation: bool = False,
        existing_suggested_value: str = None,
    ) -> Dict[str, Any]:
        """
        그래프 실행

        Args:
            message: 사용자 메시지
            conversation_history: 대화 히스토리
            user_context: 사용자 컨텍스트 (레벨 등)
            existing_topic: 이전에 수집된 주제
            existing_difficulty: 이전에 수집된 난이도
            existing_language: 이전에 수집된 언어
            existing_awaiting_confirmation: 네/아니오 응답 대기 상태
            existing_suggested_value: 추천된 값

        Returns:
            {
                "message": str,  # 응답 메시지
                "collected_info": {
                    "topic": str | None,
                    "difficulty": str | None,
                    "language": str | None,
                },
                "is_complete": bool,
                "action_trigger": str | None,
                "awaiting_confirmation": bool,  # 네/아니오 응답 대기
                "suggested_value": str | None,  # 추천된 값
                "action_data": dict | None,  # 프론트엔드용 추가 데이터
            }
        """
        # 초기 상태 생성
        initial_state = get_initial_state(
            message=message,
            conversation_history=conversation_history,
            user_context=user_context,
            existing_topic=existing_topic,
            existing_difficulty=existing_difficulty,
            existing_language=existing_language,
        )

        # 기존 상태 병합 (awaiting_confirmation, suggested_value)
        if existing_awaiting_confirmation:
            initial_state["awaiting_confirmation"] = existing_awaiting_confirmation
        if existing_suggested_value:
            initial_state["suggested_value"] = existing_suggested_value

        # 그래프 실행
        result = await self.graph.ainvoke(initial_state)

        # 결과 포맷팅
        awaiting_confirmation = result.get("awaiting_confirmation", False)
        suggested_value = result.get("suggested_value")
        current_step = result.get("current_step", "topic")

        # action_data 생성 (프론트엔드용)
        action_data = None

        # 노드에서 반환된 chips가 있으면 사용
        result_chips = result.get("chips")

        if awaiting_confirmation and suggested_value:
            # 확인 대기 상태 - 네/아니오 칩
            action_data = {
                "type": "confirmation",
                "suggested_value": suggested_value,
                "current_step": current_step,
                "chips": [
                    {"label": "네", "value": "yes", "category": "confirmation"},
                    {"label": "아니오, 다른 거", "value": "no", "category": "confirmation"},
                ],
            }
        elif result_chips:
            # 선택지 칩이 있는 경우 - 빠른 선택용
            action_data = {
                "type": "selection",
                "current_step": current_step,
                "chips": result_chips,
            }

        # 수집된 정보 - 그래프 결과 우선, 기존 값 fallback (상태 유실 방지)
        final_topic = result.get("topic") or existing_topic
        final_difficulty = result.get("difficulty") or existing_difficulty
        final_language = result.get("language") or existing_language

        # 디버깅 로그
        print(f"[InfoCollectionGraph] Result: topic={result.get('topic')}, difficulty={result.get('difficulty')}, language={result.get('language')}")
        print(f"[InfoCollectionGraph] Final: topic={final_topic}, difficulty={final_difficulty}, language={final_language}")

        return {
            "message": result.get("response_message", ""),
            "collected_info": {
                "topic": final_topic,
                "difficulty": final_difficulty,
                "language": final_language,
            },
            "is_complete": result.get("is_complete", False),
            "action_trigger": "search_problems" if result.get("is_complete") else None,
            "awaiting_confirmation": awaiting_confirmation,
            "suggested_value": suggested_value,
            "action_data": action_data,
        }
