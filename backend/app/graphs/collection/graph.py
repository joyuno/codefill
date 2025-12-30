"""
Info Collection Graph

LangGraph를 사용한 정보 수집 그래프 정의

Flow:
    START → parse_input
              ↓
         [is_question?]
              ├─ Yes → handle_question → (현재 단계 질문 노드로)
              ↓ No
         [current_step?]
              ├─ topic → ask_topic
              ├─ difficulty → ask_difficulty
              ├─ language → ask_language
              └─ complete → complete_collection
                    ↓
                   END
"""
from typing import Dict, Any, List, Optional
from langgraph.graph import StateGraph, END

from .state import CollectionState, get_initial_state
from .nodes import (
    parse_input,
    ask_topic,
    ask_difficulty,
    ask_language,
    handle_question,
    complete_collection,
)


def _route_after_parse(state: CollectionState) -> str:
    """parse_input 후 라우팅 결정"""
    # 질문이면 handle_question으로
    if state.get("is_question"):
        return "handle_question"

    # 현재 단계에 따라 라우팅
    current_step = state.get("current_step", "topic")

    if current_step == "complete":
        return "complete"
    elif current_step == "language":
        return "ask_language"
    elif current_step == "difficulty":
        return "ask_difficulty"
    else:
        return "ask_topic"


def _route_after_question(state: CollectionState) -> str:
    """handle_question 후 라우팅 결정 (현재 단계 질문 노드로)"""
    current_step = state.get("current_step", "topic")

    if current_step == "complete":
        return "complete"
    elif current_step == "language":
        return "ask_language"
    elif current_step == "difficulty":
        return "ask_difficulty"
    else:
        return "ask_topic"


def _route_after_ask(state: CollectionState) -> str:
    """ask 노드 후 라우팅 (END)"""
    # 응답이 있으면 종료
    if state.get("response_message"):
        return END

    # 완료 상태면 complete로
    if state.get("current_step") == "complete":
        return "complete"

    return END


def create_info_collection_graph() -> StateGraph:
    """정보 수집 그래프 생성"""

    # 그래프 빌더 생성
    builder = StateGraph(CollectionState)

    # ============================================================
    # 노드 추가
    # ============================================================
    builder.add_node("parse_input", parse_input)
    builder.add_node("handle_question", handle_question)
    builder.add_node("ask_topic", ask_topic)
    builder.add_node("ask_difficulty", ask_difficulty)
    builder.add_node("ask_language", ask_language)
    builder.add_node("complete", complete_collection)

    # ============================================================
    # 엣지 정의
    # ============================================================

    # 시작점 설정
    builder.set_entry_point("parse_input")

    # parse_input 후 조건부 라우팅
    builder.add_conditional_edges(
        "parse_input",
        _route_after_parse,
        {
            "handle_question": "handle_question",
            "ask_topic": "ask_topic",
            "ask_difficulty": "ask_difficulty",
            "ask_language": "ask_language",
            "complete": "complete",
        },
    )

    # handle_question 후 현재 단계 질문 노드로
    builder.add_conditional_edges(
        "handle_question",
        _route_after_question,
        {
            "ask_topic": "ask_topic",
            "ask_difficulty": "ask_difficulty",
            "ask_language": "ask_language",
            "complete": "complete",
        },
    )

    # ask 노드들 → END
    builder.add_edge("ask_topic", END)
    builder.add_edge("ask_difficulty", END)
    builder.add_edge("ask_language", END)
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

        # 그래프 실행
        result = await self.graph.ainvoke(initial_state)

        # 결과 포맷팅
        return {
            "message": result.get("response_message", ""),
            "collected_info": {
                "topic": result.get("topic"),
                "difficulty": result.get("difficulty"),
                "language": result.get("language"),
            },
            "is_complete": result.get("is_complete", False),
            "action_trigger": "search_problems" if result.get("is_complete") else None,
        }
