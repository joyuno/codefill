"""
Problem Selection and Generation Nodes

문제 선택 및 유형별 문제 생성 (Blank/Puzzle/Guided)
"""
import re
from typing import Dict, Any
from ..state import ChatState, ProblemInfo


async def handle_problem_selection(state: ChatState) -> Dict[str, Any]:
    """
    사용자가 문제를 선택했을 때 처리합니다.

    Returns:
        업데이트된 상태:
        - selected_problem: 선택된 문제
        - response_message: 응답 메시지
        - action_data: 프론트엔드 액션 데이터 (문제 유형 선택 UI)
    """
    message = state.get("message", "").lower()
    search_results = state.get("search_results", [])
    generated_problem = state.get("generated_problem")
    collected_info = state.get("collected_info", {})
    user_context = state.get("user_context", {})

    # user_context에서도 search_results 확인 (프론트엔드에서 전달)
    if not search_results and user_context.get("search_results"):
        search_results = user_context.get("search_results", [])

    selected_problem = None
    selected_name = None
    selected_index = None

    # 1. collected_info에서 선택 정보 확인
    if collected_info.get("selected_problem"):
        selected_name = collected_info["selected_problem"]
    if collected_info.get("selected_problem_index"):
        selected_index = collected_info["selected_problem_index"]

    # 2. 메시지에서 번호 추출 (1번, 2번, 첫번째, 또는 그냥 숫자)
    if not selected_index:
        # "1번", "2번" 형식
        num_match = re.search(r'(\d+)\s*번', message)
        if num_match:
            selected_index = int(num_match.group(1))
        else:
            # "첫번째", "두번째" 등
            ordinal_map = {"첫": 1, "두": 2, "세": 3, "네": 4, "다섯": 5}
            for word, idx in ordinal_map.items():
                if word in message:
                    selected_index = idx
                    break
            # 그냥 숫자만 있는 경우 (e.g., "1 할게", "1번째")
            if not selected_index:
                simple_num = re.search(r'\b([1-5])\b', message)
                if simple_num:
                    selected_index = int(simple_num.group(1))

    # 3. 메시지에서 문제 이름 추출 (taco_139 등)
    if not selected_name:
        name_match = re.search(r'(taco_\d+)', message, re.IGNORECASE)
        if name_match:
            selected_name = name_match.group(1)

    # 4. 문제 찾기
    if selected_index and search_results:
        idx = selected_index - 1  # 1-indexed to 0-indexed
        if 0 <= idx < len(search_results):
            selected_problem = search_results[idx]

    if not selected_problem and selected_name and search_results:
        for p in search_results:
            if (p.get("name", "").lower() == selected_name.lower() or
                p.get("title", "").lower() == selected_name.lower()):
                selected_problem = p
                break

    # 5. generated_problem 확인
    if not selected_problem and generated_problem:
        # 생성된 문제가 있고, 메시지가 문제 선택을 암시하면
        if any(keyword in message for keyword in ["할게", "풀게", "좋아", "네", "그거"]):
            selected_problem = generated_problem

    # 6. 검색 결과의 첫 번째 문제 (default)
    if not selected_problem and search_results:
        # 메시지가 문제 선택을 암시하면 첫 번째 선택
        if any(keyword in message for keyword in ["할게", "풀게", "좋아", "네", "첫"]):
            selected_problem = search_results[0]

    if selected_problem:
        problem_title = selected_problem.get("title") or selected_problem.get("name", "선택한 문제")

        response_message = f"좋아요! {problem_title} 문제로 할게요. 어떤 방식으로 풀어볼까요?"
        action_data = {
            "action_trigger": "select_problem_type",
            "next_action": "show_problem_type_selector",
            "selected_problem": selected_problem,
        }
        next_node = "respond"
    else:
        # 문제를 찾지 못함
        response_message = "어떤 문제를 선택하셨는지 잘 모르겠어요. 번호나 이름으로 다시 말씀해주세요!"
        action_data = None
        next_node = "respond"

    return {
        "selected_problem": selected_problem,
        "response_message": response_message,
        "action_data": action_data,
        "action_trigger": "select_problem_type" if selected_problem else None,
        "next_node": next_node,
    }


async def generate_problem_type(state: ChatState) -> Dict[str, Any]:
    """
    선택된 문제를 특정 유형 (Blank/Puzzle/Guided)으로 생성합니다.

    이 노드는 프론트엔드에서 문제 유형을 선택한 후 호출됩니다.

    Returns:
        업데이트된 상태:
        - problem_content: 생성된 문제 콘텐츠
        - response_message: 응답 메시지
    """
    selected_problem = state.get("selected_problem")
    problem_type = state.get("problem_type")  # blank, puzzle, guided

    if not selected_problem:
        return {
            "response_message": "문제가 선택되지 않았어요. 먼저 문제를 선택해주세요!",
            "next_node": "respond",
        }

    if not problem_type:
        return {
            "response_message": "어떤 유형으로 풀어볼까요? (빈칸 채우기, 퍼즐, 1대1 대화형)",
            "action_data": {
                "action_trigger": "select_problem_type",
                "selected_problem": selected_problem,
            },
            "next_node": "respond",
        }

    # 문제 유형별 생성 로직은 기존 generate_blank, generate_puzzle, generate_guided 엔드포인트 활용
    # 여기서는 프론트엔드가 해당 엔드포인트를 직접 호출하므로, 상태만 업데이트

    response_message = f"좋아요! {problem_type} 유형으로 문제를 준비할게요. 잠시만요..."

    return {
        "response_message": response_message,
        "action_data": {
            "action_trigger": f"generate_{problem_type}",
            "selected_problem": selected_problem,
            "problem_type": problem_type,
        },
        "next_node": "respond",
    }
