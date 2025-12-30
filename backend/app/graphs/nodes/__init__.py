"""
LangGraph Node Functions

각 노드는 ChatState/SolvingState를 입력받아 업데이트된 상태를 반환합니다.
"""
# Chat Graph 노드 (문제 선택)
from .intent import classify_intent
from .collect import collect_info, free_chat
from .search import search_problems, generate_problem_codegen
from .problem import handle_problem_selection, generate_problem_type
from .hint import provide_hint
from .general import (
    handle_greeting,
    handle_thanks,
    handle_general,
    handle_context_missing,
)

# Solving Graph 노드 (문제 풀이)
from .solving_intent import classify_solving_intent
from .solving import (
    provide_hint as solving_provide_hint,
    review_code,
    check_answer,
    provide_feedback,
    show_solution,
    answer_question,
)

__all__ = [
    # Chat Graph
    "classify_intent",
    "collect_info",
    "free_chat",
    "search_problems",
    "generate_problem_codegen",
    "handle_problem_selection",
    "generate_problem_type",
    "provide_hint",
    "handle_greeting",
    "handle_thanks",
    "handle_general",
    "handle_context_missing",
    # Solving Graph
    "classify_solving_intent",
    "solving_provide_hint",
    "review_code",
    "check_answer",
    "provide_feedback",
    "show_solution",
    "answer_question",
]
