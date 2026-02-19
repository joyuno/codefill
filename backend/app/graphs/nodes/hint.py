"""
Hint Generation Node

문제 풀이 힌트를 생성합니다.
"""
from typing import Dict, Any
from ..state import ChatState
from ...config import get_settings


async def provide_hint(state: ChatState) -> Dict[str, Any]:
    """
    현재 문제에 대한 힌트를 생성합니다.

    Returns:
        업데이트된 상태:
        - response_message: 힌트 메시지
        - action_data: 힌트 데이터
    """
    from ...services.openrouter import OpenRouterService

    user_context = state.get("user_context", {})
    selected_problem = state.get("selected_problem")
    message = state.get("message", "")

    # 현재 문제 확인
    current_problem = user_context.get("current_problem") or selected_problem

    if not current_problem:
        return {
            "response_message": "힌트를 드리려면 먼저 문제를 선택해야 해요! 어떤 문제를 풀어볼까요?",
            "action_trigger": None,
            "next_node": "respond",
        }

    # 현재 코드 확인
    current_code = user_context.get("current_code", "")
    hint_level = user_context.get("hint_level", 0) + 1

    openrouter = OpenRouterService()

    # 힌트 생성 프롬프트
    system_prompt = """당신은 코딩 교육 전문가입니다.
학생이 문제를 풀 때 힌트를 제공하는 역할입니다.

규칙:
1. 직접적인 정답을 알려주지 마세요
2. 소크라테스식 질문으로 유도하세요
3. 힌트 레벨에 따라 점점 더 구체적인 힌트를 제공하세요:
   - Level 1: 문제 접근 방향 제시
   - Level 2: 알고리즘/자료구조 힌트
   - Level 3: 구체적인 구현 힌트
4. 친근하고 격려하는 톤을 유지하세요
"""

    problem_info = f"""
문제: {current_problem.get('title') or current_problem.get('name', 'Unknown')}
설명: {current_problem.get('description') or current_problem.get('question', '')[:500]}
난이도: {current_problem.get('difficulty', 'medium')}
힌트 레벨: {hint_level}
"""

    if current_code:
        problem_info += f"\n학생의 현재 코드:\n```\n{current_code[:1000]}\n```"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"{problem_info}\n\n학생 요청: {message}"},
    ]

    try:
        settings = get_settings()
        response = await openrouter.chat_completion(
            messages=messages,
            model=settings.llm_model_hint,
            max_tokens=400,  # 힌트용
        )

        return {
            "response_message": response,
            "action_trigger": "hint_provided",
            "action_data": {
                "hint_level": hint_level,
                "problem_id": current_problem.get("id"),
            },
            "next_node": "respond",
        }

    except Exception as e:
        print(f"[Hint] Error: {e}")
        return {
            "response_message": "힌트 생성 중 오류가 발생했어요. 다시 시도해주세요!",
            "next_node": "respond",
        }
