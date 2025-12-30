"""
LangGraph Chat Graph Definition

CodeFill 챗봇의 메인 그래프를 정의합니다.

플로우:
    START → classify_intent
           ├─ new_problem/topic_specific → collect_info → search_problems
           │                              └─ (부족시) → generate_problem_codegen
           ├─ random_recommend → search_problems
           ├─ problem_selection → handle_problem_selection
           ├─ hint_request → provide_hint
           ├─ greeting → handle_greeting
           └─ others → handle_general
          → respond → END
"""
from typing import Literal, Dict, Any
from langgraph.graph import StateGraph, END

from .state import ChatState, INTENT_TO_NODE
from .nodes import (
    classify_intent,
    collect_info,
    free_chat,
    search_problems,
    generate_problem_codegen,
    handle_problem_selection,
    provide_hint,
    handle_greeting,
    handle_thanks,
    handle_general,
    handle_context_missing,
)


def route_after_intent(state: ChatState) -> str:
    """
    의도 분류 후 라우팅

    next_node 값에 따라 다음 노드를 결정합니다.
    """
    next_node = state.get("next_node", "handle_general")

    # 유효한 노드인지 확인
    valid_nodes = {
        "collect_info",
        "search_problems",
        "handle_problem_selection",
        "provide_hint",
        "handle_greeting",
        "handle_thanks",
        "handle_general",
        "handle_context_missing",
        "respond",
    }

    if next_node in valid_nodes:
        return next_node
    else:
        return "handle_general"


def route_after_collect(state: ChatState) -> str:
    """
    정보 수집 후 라우팅

    정보가 충분하면 검색, 아니면 응답(추가 질문)
    """
    next_node = state.get("next_node", "respond")

    if next_node == "search_problems":
        return "search_problems"
    elif next_node == "handle_problem_selection":
        return "handle_problem_selection"
    else:
        return "respond"


def route_after_search(state: ChatState) -> str:
    """
    검색 후 라우팅

    결과가 충분하면 응답, 부족하면 CodeGen
    """
    next_node = state.get("next_node", "respond")

    if next_node == "generate_problem_codegen":
        return "generate_problem_codegen"
    else:
        return "respond"


def create_chat_graph() -> StateGraph:
    """
    Chat 그래프를 생성합니다.

    Returns:
        컴파일된 StateGraph
    """
    # 그래프 생성
    workflow = StateGraph(ChatState)

    # ===== 노드 추가 =====
    workflow.add_node("classify_intent", classify_intent)
    workflow.add_node("collect_info", collect_info)
    workflow.add_node("search_problems", search_problems)
    workflow.add_node("generate_problem_codegen", generate_problem_codegen)
    workflow.add_node("handle_problem_selection", handle_problem_selection)
    workflow.add_node("provide_hint", provide_hint)
    workflow.add_node("handle_greeting", handle_greeting)
    workflow.add_node("handle_thanks", handle_thanks)
    workflow.add_node("handle_general", handle_general)
    workflow.add_node("handle_context_missing", handle_context_missing)
    workflow.add_node("respond", respond_node)

    # ===== 엣지 정의 =====

    # 시작점
    workflow.set_entry_point("classify_intent")

    # 의도 분류 후 조건부 라우팅
    workflow.add_conditional_edges(
        "classify_intent",
        route_after_intent,
        {
            "collect_info": "collect_info",
            "search_problems": "search_problems",
            "handle_problem_selection": "handle_problem_selection",
            "provide_hint": "provide_hint",
            "handle_greeting": "handle_greeting",
            "handle_thanks": "handle_thanks",
            "handle_general": "handle_general",
            "handle_context_missing": "handle_context_missing",
            "respond": "respond",
        }
    )

    # 정보 수집 후 조건부 라우팅
    workflow.add_conditional_edges(
        "collect_info",
        route_after_collect,
        {
            "search_problems": "search_problems",
            "handle_problem_selection": "handle_problem_selection",
            "respond": "respond",
        }
    )

    # 검색 후 조건부 라우팅
    workflow.add_conditional_edges(
        "search_problems",
        route_after_search,
        {
            "generate_problem_codegen": "generate_problem_codegen",
            "respond": "respond",
        }
    )

    # 나머지 노드들은 respond로
    workflow.add_edge("generate_problem_codegen", "respond")
    workflow.add_edge("handle_problem_selection", "respond")
    workflow.add_edge("provide_hint", "respond")
    workflow.add_edge("handle_greeting", "respond")
    workflow.add_edge("handle_thanks", "respond")
    workflow.add_edge("handle_general", "respond")
    workflow.add_edge("handle_context_missing", "respond")

    # respond에서 종료
    workflow.add_edge("respond", END)

    return workflow


async def respond_node(state: ChatState) -> Dict[str, Any]:
    """
    최종 응답 노드

    상태에서 response_message를 추출하여 반환합니다.
    이 노드는 실제로 아무것도 하지 않고 상태를 그대로 전달합니다.
    """
    # 응답 메시지가 없으면 기본 메시지
    if not state.get("response_message"):
        return {
            "response_message": "무엇을 도와드릴까요?",
        }
    return {}


# 컴파일된 그래프 (싱글톤)
_compiled_graph = None


def get_chat_graph():
    """
    컴파일된 그래프 싱글톤 반환
    """
    global _compiled_graph
    if _compiled_graph is None:
        workflow = create_chat_graph()
        _compiled_graph = workflow.compile()
    return _compiled_graph


class ChatGraph:
    """
    Chat 그래프 래퍼 클래스

    API에서 사용하기 편하게 래핑합니다.
    """

    def __init__(self):
        self.graph = get_chat_graph()

    async def invoke(
        self,
        message: str,
        conversation_history: list = None,
        user_context: dict = None,
        collected_info: dict = None,
        search_results: list = None,
    ) -> Dict[str, Any]:
        """
        그래프를 실행합니다.

        Args:
            message: 사용자 메시지
            conversation_history: 대화 히스토리
            user_context: 사용자 컨텍스트
            collected_info: 이미 수집된 정보
            search_results: 이미 검색된 문제 목록

        Returns:
            그래프 실행 결과
        """
        # 초기 상태 구성
        initial_state: ChatState = {
            "message": message,
            "conversation_history": conversation_history or [],
            "user_context": user_context or {},
            "collected_info": collected_info or {},
            "search_results": search_results or [],
        }

        # 그래프 실행
        result = await self.graph.ainvoke(initial_state)

        return result

    def get_mermaid_diagram(self) -> str:
        """
        그래프를 Mermaid 다이어그램으로 반환
        """
        try:
            return self.graph.get_graph().draw_mermaid()
        except Exception:
            return "Mermaid diagram not available"
