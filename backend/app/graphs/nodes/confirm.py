"""
Confirmation Nodes for Human-in-the-Loop

확인 요청 노드들 - 프론트엔드에서 확인 UI를 표시하고 사용자 응답을 처리

Usage:
    - 문제 생성 전 확인
    - 힌트 레벨 4 (정답 근접) 전 확인
    - 퍼즐 정답 공개 전 확인

Note:
    - interrupt() 대신 awaiting_confirmation 플래그를 사용
    - 프론트엔드에서 확인 버튼 클릭 시 다음 요청에 확인 응답 포함
    - 이 방식은 checkpointer 없이도 작동
"""

from typing import Dict, Any, Optional

from ..discovery_state import DiscoveryState
from ..solving_state import SolvingState


async def confirm_generation_node(state: DiscoveryState) -> Dict[str, Any]:
    """
    문제 생성 전 사용자 확인 노드

    interrupt() 대신 awaiting_confirmation 플래그 사용:
    1. 첫 호출: awaiting_confirmation=True, 확인 UI 표시 요청
    2. 확인 후 재호출: user_confirmed=True → 생성 진행

    Returns:
        proceed_generation: True면 생성 진행, False면 확인 대기
    """
    collected_info = state.get("collected_info", {})
    user_context = state.get("user_context", {})

    # 사용자가 이미 확인한 경우 (프론트엔드에서 확인 후 재호출)
    user_confirmed = user_context.get("generation_confirmed", False)
    user_cancelled = user_context.get("generation_cancelled", False)

    if user_confirmed:
        print("[ConfirmGeneration] User confirmed - proceeding to generate")
        return {
            "proceed_generation": True,
            "next_node": "generate_problem",
        }

    if user_cancelled:
        print("[ConfirmGeneration] User cancelled - returning to collection")
        return {
            "proceed_generation": False,
            "response_message": "알겠어요! 어떤 조건을 변경하고 싶으신가요?",
            "next_node": "respond",
            "action_trigger": "modify_conditions",
        }

    # 첫 호출: 확인 UI 표시 요청
    topics = collected_info.get("topics", [])
    topics_str = ", ".join(topics) if topics else "기초"

    # ============================================================
    # difficulty가 None일 때 사용자 레벨 기반으로 실제 기본값 설정
    # (이전에는 하드코딩 "easy"였으나, 이제 개인화 추천 사용)
    # ============================================================
    difficulty = collected_info.get("difficulty")
    if not difficulty:
        # user_context에서 experience_level 추출
        experience_level = user_context.get("experience_level", "unknown")

        # 레벨 → 난이도 매핑 (user_tools.py의 LEVEL_TO_DIFFICULTY와 동일)
        LEVEL_TO_DIFFICULTY = {
            "beginner": "easy",
            "elementary": "easy",
            "intermediate": "medium",
            "advanced": "hard",
            "unknown": "easy",
        }
        difficulty = LEVEL_TO_DIFFICULTY.get(experience_level, "easy")

        # collected_info에 실제로 저장 (이후 검색에서 사용)
        collected_info["difficulty"] = difficulty
        print(f"[ConfirmGeneration] Auto-set difficulty based on user level: {experience_level} → {difficulty}")

    language = collected_info.get("language", "python")

    confirm_message = (
        f"**문제 생성 확인**\n\n"
        f"- 주제: {topics_str}\n"
        f"- 난이도: {difficulty}\n"
        f"- 언어: {language}\n\n"
        f"이 조건으로 새 문제를 생성할까요?"
    )

    print(f"[ConfirmGeneration] Requesting user confirmation for: {topics_str}/{difficulty}/{language}")

    # 확인이 없으면 기본적으로 생성 진행 (UX 개선: 불필요한 확인 단계 제거)
    # Note: 실제로는 바로 생성 진행하고 프론트엔드에서 로딩 상태 표시
    return {
        "proceed_generation": True,
        "next_node": "generate_problem",
        "response_message": f"'{topics_str}' 관련 새 문제를 생성하고 있어요...",
        "action_trigger": "generating_problem",
        "action_data": {
            "status": "generating",
            "topics": topics,
            "difficulty": difficulty,
            "language": language,
        },
    }


async def confirm_hint_reveal_node(state: SolvingState) -> Dict[str, Any]:
    """
    힌트 레벨 4 (정답 근접 힌트) 전 확인 노드

    정답에 매우 가까운 힌트를 보기 전에 사용자 확인 요청

    Note: interrupt() 대신 awaiting_confirmation 플래그 사용
    """
    current_level = state.get("hint_level", 0)
    problem_context = state.get("problem_context", {})
    problem_title = problem_context.get("title", "문제")
    user_context = state.get("user_context", {})

    if current_level < 3:
        # 레벨 4 미만이면 확인 없이 진행
        return {"proceed_hint": True, "next_node": "provide_hint"}

    # 사용자가 이미 확인한 경우
    hint_confirmed = user_context.get("hint_reveal_confirmed", False)
    hint_cancelled = user_context.get("hint_reveal_cancelled", False)

    if hint_confirmed:
        return {"proceed_hint": True, "next_node": "provide_hint"}

    if hint_cancelled:
        return {
            "proceed_hint": False,
            "response_message": "좋아요! 천천히 생각해보세요. 도움이 필요하면 말씀해주세요.",
            "next_node": "respond",
        }

    # 레벨 4 힌트는 확인 없이 바로 제공 (UX 개선: 불필요한 확인 단계 제거)
    # 사용자가 힌트를 요청했다면 제공
    print(f"[ConfirmHintReveal] Level 4 hint requested for: {problem_title}")
    return {"proceed_hint": True, "next_node": "provide_hint"}


async def confirm_puzzle_solution_node(state: SolvingState) -> Dict[str, Any]:
    """
    퍼즐 정답 공개 전 확인 노드

    Note: interrupt() 대신 awaiting_confirmation 플래그 사용
    """
    problem_context = state.get("problem_context", {})
    problem_title = problem_context.get("title", "퍼즐 문제")
    attempt_count = state.get("user_progress", {}).get("attempt_count", 0)
    user_context = state.get("user_context", {})

    # 사용자가 이미 확인한 경우
    solution_confirmed = user_context.get("solution_reveal_confirmed", False)
    solution_cancelled = user_context.get("solution_reveal_cancelled", False)

    if solution_confirmed:
        return {"reveal_solution": True, "next_node": "show_solution"}

    if solution_cancelled:
        return {"reveal_solution": False, "next_node": "provide_hint"}

    # 정답 공개 요청이 있으면 바로 제공 (UX 개선)
    print(f"[ConfirmPuzzleSolution] Solution reveal requested for: {problem_title}")
    return {"reveal_solution": True, "next_node": "show_solution"}


# ============================================================
# Routing Helpers
# ============================================================

def should_confirm_generation(state: DiscoveryState) -> bool:
    """
    문제 생성 전 확인이 필요한지 판단

    조건:
    - force_generate가 True인 경우 (새 문제 생성 버튼)
    - RAG 검색 결과가 없는 경우 (fallback)
    """
    return state.get("force_generate", False) or state.get("should_generate", False)


def should_confirm_hint(state: SolvingState) -> bool:
    """
    힌트 공개 전 확인이 필요한지 판단

    조건:
    - 힌트 레벨 4 이상 요청
    """
    return state.get("hint_level", 0) >= 3
