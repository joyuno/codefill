"""
LangGraph Discovery Graph Definition (Stage 2)

2단계: 문제 탐색 그래프

역할:
- RAG 기반 문제 검색
- 검색 결과 필터링 / CodeGen fallback
- 사용자 문제 선택 처리
- 문제 확정 및 유형 선택

플로우:
    START → route_discovery_intent
              ↓
    search_problems (RAG 검색)
              ↓ (조건부 분기)
    ├─ 유사도 높음 → filter_results
    └─ fallback → generate_problem
              ↓ (합류)
    handle_selection (문제유형 선택)
              ↓ (조건부)
    ├─ 선택 안됨 → respond (목록 표시, 선택 대기)
    └─ 선택됨 → confirm_problem (문제 생성 agent)
                    ↓
                  respond → END
"""
import re
from typing import Dict, Any, List
from langgraph.graph import StateGraph, END

from .discovery_state import (
    DiscoveryState,
    ProblemInfo,
    DISCOVERY_INTENTS,
    IMMEDIATE_SEARCH_INTENTS,
    SELECTION_INTENTS,
)


# ============================================================
# Node Functions
# ============================================================

async def route_discovery_intent_node(state: DiscoveryState) -> Dict[str, Any]:
    """
    Discovery 그래프의 진입점.
    의도에 따라 다음 노드를 결정합니다.
    """
    intent = state.get("intent", "")
    message = state.get("message", "")
    search_results = state.get("search_results", [])
    collected_info = state.get("collected_info", {})

    # 1. 이미 검색 결과가 있고 문제 선택 의도인 경우
    if intent in SELECTION_INTENTS or (search_results and _is_selection_message(message)):
        return {"next_node": "handle_selection"}

    # 2. 새 문제 검색이 필요한 경우
    if intent in IMMEDIATE_SEARCH_INTENTS:
        return {"next_node": "search_problems"}

    # 3. 수집된 정보가 있으면 검색
    if collected_info.get("topics") or collected_info.get("difficulty"):
        return {"next_node": "search_problems"}

    # 4. 기본: 검색
    return {"next_node": "search_problems"}


async def search_problems_node(state: DiscoveryState) -> Dict[str, Any]:
    """
    RAG를 통해 문제를 검색합니다.
    """
    from ..services.rag import rag_service

    collected_info = state.get("collected_info", {})

    # 검색 파라미터
    topics = collected_info.get("topics", [])
    difficulty = collected_info.get("difficulty")
    language = collected_info.get("language", "python")

    # 검색 쿼리 생성
    query_parts = []
    if topics:
        query_parts.extend(topics)
    if difficulty:
        query_parts.append(f"{difficulty} difficulty")
    query = " ".join(query_parts) if query_parts else "기초 알고리즘 문제"

    # RAG 검색
    try:
        results, should_fallback = await rag_service.search_problems_hybrid(
            query=query,
            topics=topics,
            difficulty=difficulty,
            language=language,
            limit=5
        )
    except Exception as e:
        print(f"[DiscoveryGraph:Search] RAG error: {e}")
        results = []
        should_fallback = True

    # ProblemInfo 형식으로 변환
    search_results: List[ProblemInfo] = []
    for r in results:
        search_results.append({
            "id": r.get("id"),
            "name": r.get("name") or r.get("original_id"),
            "title": r.get("title") or r.get("name"),
            "question": r.get("question"),
            "description": r.get("description"),
            "difficulty": r.get("difficulty", "medium"),
            "tags": r.get("tags", []),
            "topics": r.get("topics", []),
            "solutions": r.get("solutions", []),
            "similarity": r.get("similarity"),
        })

    # 결과 판단
    should_generate = should_fallback or len(search_results) == 0

    if should_generate:
        next_node = "generate_problem"
    else:
        next_node = "filter_results"

    return {
        "search_results": search_results,
        "should_generate": should_generate,
        "next_node": next_node,
    }


async def filter_results_node(state: DiscoveryState) -> Dict[str, Any]:
    """
    검색 결과를 필터링하고 응답을 생성합니다.
    """
    search_results = state.get("search_results", [])
    collected_info = state.get("collected_info", {})

    # 필터링 (현재는 패스스루, 추후 고도화 가능)
    filtered_results = search_results[:5]

    # 응답 메시지 생성
    if filtered_results:
        problem_list = "\n".join([
            f"  {i+1}. {p.get('name') or p.get('title', 'Unknown')} ({p.get('difficulty', 'medium')})"
            for i, p in enumerate(filtered_results)
        ])
        response_message = f"찾은 문제들이에요:\n{problem_list}\n\n어떤 문제를 풀어볼까요? 번호로 선택해주세요!"

        action_data = {
            "status": "found",
            "problems": filtered_results,
        }
        action_trigger = "search_problems"
    else:
        response_message = "조건에 맞는 문제를 찾지 못했어요. 다른 조건으로 시도해볼까요?"
        action_data = {"status": "not_found"}
        action_trigger = None

    return {
        "filtered_results": filtered_results,
        "response_message": response_message,
        "action_data": action_data,
        "action_trigger": action_trigger,
        "awaiting_selection": True,  # 선택 대기 상태
        "next_node": "handle_selection",
    }


async def generate_problem_node(state: DiscoveryState) -> Dict[str, Any]:
    """
    CodeGen을 통해 새 문제를 생성합니다.
    """
    from ..services.openrouter import openrouter_service
    from ..prompts.code_gen_agent import CODE_GEN_SYSTEM_PROMPT
    import json

    collected_info = state.get("collected_info", {})

    user_request = {
        "topics": collected_info.get("topics", ["기초"]),
        "difficulty": collected_info.get("difficulty", "easy"),
        "language": collected_info.get("language", "python"),
        "specific_needs": collected_info.get("specific_needs", ""),
    }

    print(f"[DiscoveryGraph:CodeGen] Starting generation...")

    messages = [
        {"role": "system", "content": CODE_GEN_SYSTEM_PROMPT},
        {"role": "user", "content": json.dumps(user_request, ensure_ascii=False)},
    ]

    try:
        response = await openrouter_service.chat_completion(
            messages=messages,
            model="claude-sonnet",
            response_format={"type": "json_object"},
        )
        content = openrouter_service.get_content(response)
        result = openrouter_service.parse_json_response(content)

        generated_problem: ProblemInfo = {
            "id": None,
            "title": result.get("title", "새 문제"),
            "description": result.get("description", ""),
            "difficulty": result.get("difficulty", collected_info.get("difficulty", "easy")),
            "topics": result.get("topics", collected_info.get("topics", [])),
            "code": result.get("code", {}),
        }

        response_message = f"새로 만든 문제예요:\n  • {generated_problem['title']} ({generated_problem['difficulty']})\n\n이 문제를 풀어볼까요?"
        action_data = {
            "status": "generated",
            "generated_problem": generated_problem,
        }
        action_trigger = "generated"

    except Exception as e:
        print(f"[DiscoveryGraph:CodeGen] Error: {e}")
        generated_problem = None
        response_message = "문제 생성 중 오류가 발생했어요. 다른 조건으로 다시 시도해볼까요?"
        action_data = {"status": "error", "error": str(e)}
        action_trigger = None

    return {
        "generated_problem": generated_problem,
        "response_message": response_message,
        "action_data": action_data,
        "action_trigger": action_trigger,
        "awaiting_selection": True,  # 선택 대기 상태
        "next_node": "handle_selection",
    }


async def handle_selection_node(state: DiscoveryState) -> Dict[str, Any]:
    """
    사용자의 문제 선택을 처리합니다.

    - 선택 대기 상태 (awaiting_selection): respond로 이동하여 목록 표시
    - 선택 정보 있음: confirm_problem으로 이동
    """
    message = state.get("message", "").lower()
    search_results = state.get("search_results", [])
    filtered_results = state.get("filtered_results", [])
    generated_problem = state.get("generated_problem")
    collected_info = state.get("collected_info", {})
    user_context = state.get("user_context", {})
    awaiting_selection = state.get("awaiting_selection", False)

    # 선택 대기 상태: 목록만 보여주고 respond로 이동
    if awaiting_selection and not _has_selection_info(message, collected_info):
        return {"next_node": "respond"}

    # filtered_results나 user_context에서 search_results 확인
    if not search_results:
        search_results = filtered_results or user_context.get("search_results", [])

    selected_problem = None
    selected_name = None
    selected_index = None

    # 1. collected_info에서 선택 정보 확인
    if collected_info.get("selected_problem"):
        selected_name = collected_info["selected_problem"]
    if collected_info.get("selected_problem_index"):
        selected_index = collected_info["selected_problem_index"]

    # 2. 메시지에서 번호 추출
    if not selected_index:
        num_match = re.search(r'(\d+)\s*번', message)
        if num_match:
            selected_index = int(num_match.group(1))
        else:
            ordinal_map = {"첫": 1, "두": 2, "세": 3, "네": 4, "다섯": 5}
            for word, idx in ordinal_map.items():
                if word in message:
                    selected_index = idx
                    break
            if not selected_index:
                simple_num = re.search(r'\b([1-5])\b', message)
                if simple_num:
                    selected_index = int(simple_num.group(1))

    # 3. 메시지에서 문제 이름 추출
    if not selected_name:
        name_match = re.search(r'(taco_\d+)', message, re.IGNORECASE)
        if name_match:
            selected_name = name_match.group(1)

    # 4. 문제 찾기
    if selected_index and search_results:
        idx = selected_index - 1
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
        if any(kw in message for kw in ["할게", "풀게", "좋아", "네", "그거", "응"]):
            selected_problem = generated_problem

    # 6. 첫 번째 문제 default
    if not selected_problem and search_results:
        if any(kw in message for kw in ["할게", "풀게", "좋아", "네", "첫", "응"]):
            selected_problem = search_results[0]

    if selected_problem:
        next_node = "confirm_problem"
    else:
        next_node = "respond"
        response_message = "어떤 문제를 선택하셨는지 잘 모르겠어요. 번호나 이름으로 다시 말씀해주세요!"
        return {
            "response_message": response_message,
            "next_node": next_node,
        }

    return {
        "selected_problem": selected_problem,
        "next_node": next_node,
    }


async def confirm_problem_node(state: DiscoveryState) -> Dict[str, Any]:
    """
    선택된 문제를 확정하고 문제 유형 선택 UI를 표시합니다.
    """
    selected_problem = state.get("selected_problem")

    if not selected_problem:
        return {
            "response_message": "문제가 선택되지 않았어요. 다시 선택해주세요!",
            "next_node": "respond",
        }

    problem_title = selected_problem.get("title") or selected_problem.get("name", "선택한 문제")

    response_message = (
        f"좋아요! **{problem_title}** 문제로 할게요.\n\n"
        "어떤 방식으로 풀어볼까요?\n"
        "• **빈칸 채우기** - 핵심 부분만 채우기\n"
        "• **퍼즐 맞추기** - 코드 순서 맞추기\n"
        "• **1:1 대화형** - 단계별 대화로 풀기"
    )

    action_data = {
        "action_trigger": "select_problem_type",
        "next_action": "show_problem_type_selector",
        "selected_problem": selected_problem,
    }

    return {
        "is_confirmed": True,
        "response_message": response_message,
        "action_data": action_data,
        "action_trigger": "select_problem_type",
        "route_to": "solving",  # 문제 풀이 단계로 라우팅
        "next_node": "respond",
    }


async def respond_node(state: DiscoveryState) -> Dict[str, Any]:
    """
    최종 응답 노드
    """
    if not state.get("response_message"):
        return {"response_message": "무엇을 도와드릴까요?"}
    return {}


# ============================================================
# Helper Functions
# ============================================================

def _is_selection_message(message: str) -> bool:
    """메시지가 문제 선택을 의미하는지 확인"""
    selection_patterns = [
        r'\d+\s*번',  # 1번, 2번
        r'첫|두|세|네|다섯',  # 첫번째 등
        r'\b[1-5]\b',  # 숫자만
        r'할게|풀게|좋아|네|응|그거',  # 확인 표현
        r'taco_\d+',  # 문제 이름
    ]
    message_lower = message.lower()
    return any(re.search(p, message_lower) for p in selection_patterns)


def _has_selection_info(message: str, collected_info: dict) -> bool:
    """선택 정보가 있는지 확인"""
    # collected_info에 선택 정보가 있으면 True
    if collected_info.get("selected_problem") or collected_info.get("selected_problem_index"):
        return True
    # 메시지에 선택 의도가 있으면 True
    return _is_selection_message(message)


# ============================================================
# Routing Functions
# ============================================================

def route_after_discovery_intent(state: DiscoveryState) -> str:
    """진입점 후 라우팅"""
    next_node = state.get("next_node", "search_problems")
    valid_nodes = {"search_problems", "handle_selection", "filter_results"}
    return next_node if next_node in valid_nodes else "search_problems"


def route_after_search(state: DiscoveryState) -> str:
    """검색 후 라우팅"""
    next_node = state.get("next_node", "filter_results")
    if next_node == "generate_problem":
        return "generate_problem"
    return "filter_results"


def route_after_selection(state: DiscoveryState) -> str:
    """선택 후 라우팅"""
    next_node = state.get("next_node", "respond")
    if next_node == "confirm_problem":
        return "confirm_problem"
    return "respond"


# ============================================================
# Graph Builder
# ============================================================

def create_discovery_graph() -> StateGraph:
    """
    Discovery 그래프를 생성합니다.
    """
    workflow = StateGraph(DiscoveryState)

    # 노드 추가
    workflow.add_node("route_discovery_intent", route_discovery_intent_node)
    workflow.add_node("search_problems", search_problems_node)
    workflow.add_node("filter_results", filter_results_node)
    workflow.add_node("generate_problem", generate_problem_node)
    workflow.add_node("handle_selection", handle_selection_node)
    workflow.add_node("confirm_problem", confirm_problem_node)
    workflow.add_node("respond", respond_node)

    # 시작점
    workflow.set_entry_point("route_discovery_intent")

    # route_discovery_intent 후 라우팅
    workflow.add_conditional_edges(
        "route_discovery_intent",
        route_after_discovery_intent,
        {
            "search_problems": "search_problems",
            "handle_selection": "handle_selection",
            "filter_results": "filter_results",
        }
    )

    # search_problems 후 라우팅
    workflow.add_conditional_edges(
        "search_problems",
        route_after_search,
        {
            "filter_results": "filter_results",
            "generate_problem": "generate_problem",
        }
    )

    # filter_results → handle_selection (합류)
    workflow.add_edge("filter_results", "handle_selection")

    # generate_problem → handle_selection (합류)
    workflow.add_edge("generate_problem", "handle_selection")

    # handle_selection 후 라우팅
    workflow.add_conditional_edges(
        "handle_selection",
        route_after_selection,
        {
            "confirm_problem": "confirm_problem",
            "respond": "respond",
        }
    )

    # confirm_problem → respond
    workflow.add_edge("confirm_problem", "respond")

    # respond → END
    workflow.add_edge("respond", END)

    return workflow


# ============================================================
# Compiled Graph Singleton
# ============================================================

_compiled_discovery_graph = None


def get_discovery_graph():
    """컴파일된 그래프 싱글톤 반환"""
    global _compiled_discovery_graph
    if _compiled_discovery_graph is None:
        workflow = create_discovery_graph()
        _compiled_discovery_graph = workflow.compile()
    return _compiled_discovery_graph


# ============================================================
# Graph Wrapper Class
# ============================================================

class DiscoveryGraph:
    """
    Discovery 그래프 래퍼 클래스
    """

    def __init__(self):
        self.graph = get_discovery_graph()

    async def invoke(
        self,
        message: str,
        collected_info: dict,
        intent: str = "new_problem",
        conversation_history: list = None,
        user_context: dict = None,
        search_results: list = None,
    ) -> Dict[str, Any]:
        """
        그래프를 실행합니다.

        Args:
            message: 사용자 메시지
            collected_info: IntentGraph에서 수집된 정보
            intent: 현재 의도
            conversation_history: 대화 히스토리
            user_context: 사용자 컨텍스트
            search_results: 이전 검색 결과 (있으면)

        Returns:
            {
                search_results: 검색된 문제 목록,
                selected_problem: 선택된 문제,
                problem_type: 문제 유형,
                response_message: 응답 메시지,
                action_trigger: 액션 트리거,
                action_data: 액션 데이터,
                route_to: 다음 라우팅 (solving, respond),
            }
        """
        initial_state: DiscoveryState = {
            "message": message,
            "collected_info": collected_info or {},
            "intent": intent,
            "conversation_history": conversation_history or [],
            "user_context": user_context or {},
            "search_results": search_results or [],
        }

        result = await self.graph.ainvoke(initial_state)

        return result

    def get_mermaid_diagram(self) -> str:
        """그래프를 Mermaid 다이어그램으로 반환"""
        try:
            return self.graph.get_graph().draw_mermaid()
        except Exception:
            return "Mermaid diagram not available"
