"""
LangGraph Problem Solving Graph Definition

문제 풀이 중 힌트/피드백/정답 체크 그래프

플로우:
    START → classify_solving_intent
           ├─ hint_request → provide_hint
           ├─ code_review → review_code
           ├─ answer_check → check_answer
           ├─ feedback_request → provide_feedback
           ├─ give_up → show_solution
           └─ question → answer_question
          → respond → END
"""
from typing import Dict, Any
from langgraph.graph import StateGraph, END

from .solving_state import SolvingState, SOLVING_INTENT_TO_NODE
from .nodes.solving_intent import classify_solving_intent
from .nodes.solving import (
    provide_hint,
    review_code,
    check_answer,
    provide_feedback,
    show_solution,
    answer_question,
    summarize_problem,
)


def route_after_solving_intent(state: SolvingState) -> str:
    """
    의도 분류 후 라우팅
    """
    next_node = state.get("next_node", "answer_question")

    valid_nodes = {
        "provide_hint",
        "review_code",
        "check_answer",
        "provide_feedback",
        "show_solution",
        "answer_question",
        "summarize_problem",
        "respond",
    }

    if next_node in valid_nodes:
        return next_node
    return "answer_question"


async def respond_node(state: SolvingState) -> Dict[str, Any]:
    """
    최종 응답 노드
    """
    if not state.get("response_message"):
        return {
            "response_message": "무엇을 도와드릴까요?",
        }
    return {}


def create_solving_graph() -> StateGraph:
    """
    Problem Solving 그래프를 생성합니다.
    """
    workflow = StateGraph(SolvingState)

    # ===== 노드 추가 =====
    workflow.add_node("classify_solving_intent", classify_solving_intent)
    workflow.add_node("provide_hint", provide_hint)
    workflow.add_node("review_code", review_code)
    workflow.add_node("check_answer", check_answer)
    workflow.add_node("provide_feedback", provide_feedback)
    workflow.add_node("show_solution", show_solution)
    workflow.add_node("answer_question", answer_question)
    workflow.add_node("summarize_problem", summarize_problem)
    workflow.add_node("respond", respond_node)

    # ===== 엣지 정의 =====

    # 시작점
    workflow.set_entry_point("classify_solving_intent")

    # 의도 분류 후 조건부 라우팅
    workflow.add_conditional_edges(
        "classify_solving_intent",
        route_after_solving_intent,
        {
            "provide_hint": "provide_hint",
            "review_code": "review_code",
            "check_answer": "check_answer",
            "provide_feedback": "provide_feedback",
            "show_solution": "show_solution",
            "answer_question": "answer_question",
            "summarize_problem": "summarize_problem",
            "respond": "respond",
        }
    )

    # 모든 노드에서 respond로
    workflow.add_edge("provide_hint", "respond")
    workflow.add_edge("review_code", "respond")
    workflow.add_edge("check_answer", "respond")
    workflow.add_edge("provide_feedback", "respond")
    workflow.add_edge("show_solution", "respond")
    workflow.add_edge("answer_question", "respond")
    workflow.add_edge("summarize_problem", "respond")

    # respond에서 종료
    workflow.add_edge("respond", END)

    return workflow


# 컴파일된 그래프 (싱글톤)
_compiled_solving_graph = None


def get_solving_graph():
    """
    컴파일된 그래프 싱글톤 반환
    """
    global _compiled_solving_graph
    if _compiled_solving_graph is None:
        workflow = create_solving_graph()
        _compiled_solving_graph = workflow.compile()
    return _compiled_solving_graph


class ProblemSolvingGraph:
    """
    Problem Solving 그래프 래퍼 클래스
    """

    def __init__(self):
        self.graph = get_solving_graph()

    async def invoke(
        self,
        message: str,
        problem_context: dict,
        user_progress: dict = None,
        conversation_history: list = None,
        previous_hints: list = None,
    ) -> Dict[str, Any]:
        """
        그래프를 실행합니다.

        Args:
            message: 사용자 메시지
            problem_context: 현재 문제 정보 (필수)
            user_progress: 사용자 진행 상황
            conversation_history: 대화 히스토리
            previous_hints: 이전 힌트들

        Returns:
            그래프 실행 결과
        """
        initial_state: SolvingState = {
            "message": message,
            "problem_context": problem_context,
            "user_progress": user_progress or {},
            "conversation_history": conversation_history or [],
            "previous_hints": previous_hints or [],
            "hint_level": len(previous_hints) if previous_hints else 0,
        }

        result = await self.graph.ainvoke(initial_state)

        return result
