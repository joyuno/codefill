"""
Agentic RAG Graph for Guided Tutor

1대1 대화형 문제 풀이 그래프

플로우:
    START → retrieve_context (RAG 검색)
              ↓
           grade_context (관련성 평가)
              ↓
           assess_understanding (이해도 평가)
              ↓
           decide_action (행동 결정)
              ↓
           generate_response (응답 생성)
              ↓
           END
"""

from typing import Dict, Any, Optional
from langgraph.graph import StateGraph, END

from .state import AgenticRAGState
from .nodes import (
    retrieve_context_node,
    grade_context_node,
    assess_understanding_node,
    decide_action_node,
    generate_response_node,
    generate_initial_guide_node,
    should_retrieve,
    route_after_grade,
    is_first_message,
)


def create_guided_tutor_graph(checkpointer=None) -> StateGraph:
    """
    Guided Tutor 그래프 생성

    플로우:
        START → route_entry (첫 메시지 분기)
                 ├─ 첫 메시지 → generate_initial_guide → END
                 └─ 이후 메시지 → retrieve_context → grade_context
                                       → assess_understanding → decide_action
                                       → generate_response → END

    Args:
        checkpointer: LangGraph Checkpointer (상태 영속화용)

    Returns:
        컴파일된 그래프
    """
    workflow = StateGraph(AgenticRAGState)

    # 노드 추가
    workflow.add_node("generate_initial_guide", generate_initial_guide_node)
    workflow.add_node("retrieve_context", retrieve_context_node)
    workflow.add_node("grade_context", grade_context_node)
    workflow.add_node("assess_understanding", assess_understanding_node)
    workflow.add_node("decide_action", decide_action_node)
    workflow.add_node("generate_response", generate_response_node)

    # 시작점: 첫 메시지인지에 따라 분기
    def route_entry(state: AgenticRAGState) -> str:
        """첫 메시지면 초기 가이드, 아니면 일반 플로우"""
        if is_first_message(state):
            return "generate_initial_guide"
        return "retrieve_context"

    workflow.set_conditional_entry_point(
        route_entry,
        {
            "generate_initial_guide": "generate_initial_guide",
            "retrieve_context": "retrieve_context",
        }
    )

    # 초기 가이드 후 종료
    workflow.add_edge("generate_initial_guide", END)

    # 일반 플로우
    workflow.add_edge("retrieve_context", "grade_context")

    # grade_context 후 분기 (현재는 항상 assess로)
    workflow.add_conditional_edges(
        "grade_context",
        route_after_grade,
        {
            "assess_understanding": "assess_understanding",
        }
    )

    workflow.add_edge("assess_understanding", "decide_action")
    workflow.add_edge("decide_action", "generate_response")
    workflow.add_edge("generate_response", END)

    # 컴파일
    if checkpointer:
        return workflow.compile(checkpointer=checkpointer)
    return workflow.compile()


# ============================================================
# Compiled Graph Singleton
# ============================================================

_compiled_guided_tutor_graph = None


def get_guided_tutor_graph(checkpointer=None):
    """컴파일된 그래프 싱글톤 반환"""
    global _compiled_guided_tutor_graph
    if _compiled_guided_tutor_graph is None:
        _compiled_guided_tutor_graph = create_guided_tutor_graph(checkpointer)
    return _compiled_guided_tutor_graph


# ============================================================
# Graph Wrapper Class
# ============================================================

class GuidedTutorGraph:
    """
    Guided Tutor 그래프 래퍼 클래스

    Usage:
        tutor = GuidedTutorGraph()
        result = await tutor.invoke(
            message="for 문은 어떻게 쓰나요?",
            problem_context={...},
            solution_code="...",
        )
    """

    def __init__(self, checkpointer=None):
        self.graph = get_guided_tutor_graph(checkpointer)
        self.checkpointer = checkpointer

    async def invoke(
        self,
        message: str,
        problem_context: dict,
        solution_code: str,
        key_concepts: list = None,
        conversation_history: list = None,
        student_progress: dict = None,
        session_id: str = None,
        current_student_code: str = "",
    ) -> Dict[str, Any]:
        """
        그래프 실행

        Args:
            message: 학생 메시지
            problem_context: 문제 정보
            solution_code: 정답 코드 (튜터만 참조)
            key_concepts: 핵심 개념 목록
            conversation_history: 이전 대화 히스토리
            student_progress: 학생 진행 상황
            session_id: 세션 ID (상태 영속화용)
            current_student_code: 학생이 현재 작성 중인 코드

        Returns:
            {
                response: 튜터 응답,
                student_progress: 업데이트된 학생 상태,
                tutor_action: 수행한 행동,
                is_complete: 완료 여부,
            }
        """
        # 메시지 히스토리 구성
        messages = conversation_history or []
        messages.append({"role": "user", "content": message})

        initial_state: AgenticRAGState = {
            "messages": messages,
            "problem_context": problem_context,
            "solution_code": solution_code,
            "key_concepts": key_concepts or problem_context.get("topics", []),
            "current_student_code": current_student_code,  # 학생이 작성 중인 코드
            "student_progress": student_progress or {
                "understanding_score": 0.5,
                "concepts_mastered": [],
                "concepts_struggling": [],
                "current_focus": "",
                "hints_received": 0,
                "attempts": 0,
            },
            "retrieved_docs": [],
            "retrieval_grade": "pending",
        }

        # config 구성 (session_id가 있으면)
        config = None
        if session_id and self.checkpointer:
            from ..checkpointer import create_thread_config
            config = create_thread_config(session_id)

        # 그래프 실행
        result = await self.graph.ainvoke(initial_state, config=config)

        return {
            "response": result.get("response", ""),
            "student_progress": result.get("student_progress", {}),
            "tutor_action": result.get("tutor_action", ""),
            "is_complete": result.get("is_complete", False),
            "is_initial_guide": result.get("is_initial_guide", False),
            "initial_guide": result.get("initial_guide"),
            "suggested_next_step": result.get("suggested_next_step"),
            # 대화 히스토리에 튜터 응답 추가
            "messages": result.get("messages", []) + [
                {"role": "assistant", "content": result.get("response", "")}
            ],
        }

    async def continue_conversation(
        self,
        message: str,
        previous_state: dict,
        session_id: str = None,
    ) -> Dict[str, Any]:
        """
        대화 계속하기 (이전 상태 유지)

        Args:
            message: 새 학생 메시지
            previous_state: 이전 invoke 결과
            session_id: 세션 ID

        Returns:
            새 결과
        """
        return await self.invoke(
            message=message,
            problem_context=previous_state.get("problem_context", {}),
            solution_code=previous_state.get("solution_code", ""),
            key_concepts=previous_state.get("key_concepts", []),
            conversation_history=previous_state.get("messages", []),
            student_progress=previous_state.get("student_progress", {}),
            session_id=session_id,
        )
