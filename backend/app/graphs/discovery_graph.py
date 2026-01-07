"""
LangGraph Discovery Graph Definition (Stage 2)

2단계: 문제 탐색 그래프 (임베딩 기반 개선)

역할:
- RAG 기반 문제 검색
- 검색 결과 필터링 / CodeGen fallback
- 임베딩 기반 사용자 의도 인식 (액션, 문제 선택)
- 문제 확정 및 유형 선택
- Human-in-the-Loop: 문제 생성 전 확인 (interrupt_before)

플로우:
    START → route_discovery_intent (임베딩 기반 액션 인식)
              ↓
    search_problems (RAG 검색)
              ↓ (조건부 분기)
    ├─ 유사도 높음 → filter_results (임베딩 재순위)
    └─ fallback → [interrupt] confirm_generation → generate_problem
              ↓ (합류)
    handle_selection (임베딩 기반 문제 선택)
              ↓ (조건부)
    ├─ 선택 안됨 → respond (목록 표시, 선택 대기)
    └─ 선택됨 → confirm_problem (문제 생성 agent)
                    ↓
                  respond → END
"""
import re
import json
from typing import Dict, Any, List, Optional
from langgraph.graph import StateGraph, END

from .discovery_state import (
    DiscoveryState,
    ProblemInfo,
    DISCOVERY_INTENTS,
    IMMEDIATE_SEARCH_INTENTS,
    SELECTION_INTENTS,
    GENERATE_INTENTS,
)
from .nodes.confirm import confirm_generation_node, should_confirm_generation


# ============================================================
# Node Functions
# ============================================================

async def route_discovery_intent_node(state: DiscoveryState) -> Dict[str, Any]:
    """
    Discovery 그래프의 진입점.

    Note: 대부분의 의도 분류는 orchestrator의 intent_tool에서 이미 처리됨.
    이 노드는 state에 전달된 intent와 selection_index를 기반으로 라우팅만 수행.
    """
    intent = state.get("intent", "")
    search_results = state.get("search_results", [])
    collected_info = state.get("collected_info", {})
    current_offset = state.get("search_offset", 0)
    selection_index = state.get("selection_index")

    # 1. 오케스트레이터에서 이미 선택 인덱스를 감지한 경우 → 바로 선택 처리
    if selection_index and search_results:
        print(f"[DiscoveryGraph] Using pre-detected selection_index: {selection_index}")
        return {"next_node": "handle_selection"}

    # 2. 강제 생성 의도 (새 문제 생성 버튼)
    if intent in GENERATE_INTENTS:
        return {
            "force_generate": True,
            "next_node": "generate_problem",
        }

    # 3. 더 찾아보기 의도 (다음 5개)
    if intent == "more_search" or intent == "show_more":
        new_offset = current_offset + 5
        return {
            "search_offset": new_offset,
            "next_node": "search_problems",
        }

    # 4. 문제 선택 의도 (검색 결과가 있을 때)
    if intent in SELECTION_INTENTS or intent == "select_problem":
        if search_results:
            return {"next_node": "handle_selection"}

    # 5. 새 문제 검색이 필요한 경우
    if intent in IMMEDIATE_SEARCH_INTENTS:
        return {"search_offset": 0, "next_node": "search_problems"}

    # 6. 수집된 정보가 있으면 검색
    if collected_info.get("topics") or collected_info.get("difficulty"):
        return {"search_offset": 0, "next_node": "search_problems"}

    # 7. 기본: 검색
    return {"search_offset": 0, "next_node": "search_problems"}


async def search_problems_node(state: DiscoveryState) -> Dict[str, Any]:
    """
    RAG를 통해 문제를 검색합니다.
    offset을 사용하여 다음 결과를 가져올 수 있습니다.
    """
    from ..services.rag import rag_service

    collected_info = state.get("collected_info", {})
    search_offset = state.get("search_offset", 0)

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

    # RAG 검색 (offset 적용: limit을 늘려서 가져온 후 슬라이싱)
    try:
        # offset + 5개를 가져와서 offset 이후 5개만 사용
        fetch_limit = search_offset + 5
        results, should_fallback = await rag_service.search_problems_hybrid(
            query=query,
            topics=topics,
            difficulty=difficulty,
            language=language,
            limit=fetch_limit
        )
        # offset 이후 결과만 사용
        results = results[search_offset:search_offset + 5]

        # 더 이상 결과가 없으면 fallback 여부 확인
        if len(results) == 0 and search_offset > 0:
            should_fallback = True
            print(f"[DiscoveryGraph:Search] No more results at offset {search_offset}")

    except Exception as e:
        print(f"[DiscoveryGraph:Search] RAG error: {e}")
        results = []
        should_fallback = True

    # ProblemInfo 형식으로 변환
    search_results: List[ProblemInfo] = []
    for r in results:
        # input_output이 JSON 문자열인 경우 파싱
        input_output = r.get("input_output")
        if isinstance(input_output, str):
            try:
                input_output = json.loads(input_output)
            except (json.JSONDecodeError, TypeError):
                input_output = None

        # tags가 JSON 문자열인 경우 파싱
        tags = r.get("tags", [])
        if isinstance(tags, str):
            try:
                tags = json.loads(tags)
            except (json.JSONDecodeError, TypeError):
                tags = []

        search_results.append({
            "id": r.get("id"),
            "original_id": r.get("original_id"),
            "name": r.get("name") or r.get("original_id"),
            "title": r.get("title") or r.get("name"),
            "question": r.get("question"),
            "description": r.get("description"),
            "difficulty": r.get("difficulty", "medium"),
            "tags": tags if isinstance(tags, list) else [],
            "topics": r.get("topics", []),
            "solutions": r.get("solutions", []),
            "input_output": input_output,  # 파싱된 입출력 예제
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

    Note: RAG 검색이 이미 유사도 기반 정렬을 하므로 추가 reranking 불필요.
    단순히 상위 5개를 사용합니다.
    """
    search_results = state.get("search_results", [])
    search_offset = state.get("search_offset", 0)

    # RAG 결과에서 상위 5개 사용 (이미 유사도 정렬됨)
    filtered_results = search_results[:5]

    # 응답 메시지 생성
    if filtered_results:
        # offset에 따른 메시지 조정
        if search_offset > 0:
            start_num = search_offset + 1
            end_num = search_offset + len(filtered_results)
            problem_list = "\n".join([
                f"  {start_num + i}. {p.get('name') or p.get('title', 'Unknown')} ({p.get('difficulty', 'medium')})"
                for i, p in enumerate(filtered_results)
            ])
            response_message = f"추가로 찾은 문제들이에요 ({start_num}~{end_num}번):\n{problem_list}\n\n어떤 문제를 풀어볼까요?"
        else:
            problem_list = "\n".join([
                f"  {i+1}. {p.get('name') or p.get('title', 'Unknown')} ({p.get('difficulty', 'medium')})"
                for i, p in enumerate(filtered_results)
            ])
            response_message = f"찾은 문제들이에요:\n{problem_list}\n\n어떤 문제를 풀어볼까요? 번호로 선택해주세요!"

        action_data = {
            "status": "found",
            "problems": filtered_results,
            "search_offset": search_offset,
            "has_more": len(filtered_results) == 5,  # 5개가 있으면 더 있을 수 있음
        }
        action_trigger = "search_problems"
    else:
        if search_offset > 0:
            response_message = "더 이상 조건에 맞는 문제가 없어요. 새 문제를 생성해볼까요?"
        else:
            response_message = "조건에 맞는 문제를 찾지 못했어요. 다른 조건으로 시도해볼까요?"
        action_data = {"status": "not_found", "search_offset": search_offset}
        action_trigger = None

    return {
        "filtered_results": filtered_results,
        "response_message": response_message,
        "action_data": action_data,
        "action_trigger": action_trigger,
        "search_offset": search_offset,
        "awaiting_selection": True,  # 선택 대기 상태
        "next_node": "handle_selection",
    }


async def generate_problem_node(state: DiscoveryState) -> Dict[str, Any]:
    """
    CodeGen을 통해 새 문제를 생성합니다.
    RAG 검색 결과가 없을 때 fallback으로 호출됩니다.

    생성된 문제는 base_problems 테이블에 저장되어 이후 문제 유형 생성 시 참조됩니다.
    """
    from ..services.rag import rag_service
    from ..services.problem_save import get_problem_save_service
    from ..config import get_settings
    import json

    settings = get_settings()
    collected_info = state.get("collected_info", {})
    search_results = state.get("search_results", [])  # RAG에서 찾은 유사 문제 (fallback용 참고)

    user_request = {
        "topics": collected_info.get("topics", ["기초"]),
        "difficulty": collected_info.get("difficulty", "easy"),
        "language": collected_info.get("language", "python"),
        "specific_needs": collected_info.get("specific_needs", ""),
    }

    # Fallback 알림 메시지
    topics_str = ", ".join(collected_info.get("topics", ["기초"]))
    fallback_message = f"'{topics_str}' 관련 문제를 찾지 못했어요. 유사한 새로운 문제를 생성하고 있어요..."

    print(f"[DiscoveryGraph:CodeGen] Fallback triggered - {fallback_message}")
    print(f"[DiscoveryGraph:CodeGen] Starting generation with RAG context...")

    try:
        # RAG 서비스를 통해 문제 생성 (유사 문제 참고)
        user_context = state.get("user_context", {})
        generated_result = await rag_service.generate_problem_with_rag(
            user_request=user_request,
            similar_problems=search_results,  # 유사도가 낮더라도 참고용으로 전달
            user_context=user_context,
        )

        # ============================================================
        # CodeGen 문제를 base_problems에 저장 (Feature 1)
        # - title 필드가 name 컬럼으로 저장됨
        # - 이후 문제 유형 생성 시 base_problem_id로 참조
        # ============================================================
        problem_save_service = get_problem_save_service()
        saved_base_id = await problem_save_service.save_codegen_to_base_problems(
            generated_problem=generated_result,
            collected_info=collected_info,
        )

        if saved_base_id:
            print(f"[DiscoveryGraph:CodeGen] Saved to base_problems: {saved_base_id}")
            # saved_base_id (UUID)를 id로 설정
            problem_id = saved_base_id
            # original_id 조회
            original_id = None
            try:
                result = problem_save_service.supabase.table("base_problems") \
                    .select("original_id") \
                    .eq("id", saved_base_id) \
                    .limit(1) \
                    .execute()
                if result.data:
                    original_id = result.data[0].get("original_id")
            except Exception:
                pass
        else:
            print(f"[DiscoveryGraph:CodeGen] Warning: Failed to save to base_problems")
            problem_id = None
            original_id = None

        generated_problem: ProblemInfo = {
            "id": problem_id,
            "original_id": original_id,
            "title": generated_result.get("title", "새 문제"),
            "name": generated_result.get("title", "새 문제"),  # name도 title과 동일하게
            "title_en": generated_result.get("title_en"),
            "description": generated_result.get("description", ""),
            "question": generated_result.get("description", ""),  # question도 추가
            "difficulty": generated_result.get("difficulty", collected_info.get("difficulty", "easy")),
            "topics": generated_result.get("topics", collected_info.get("topics", [])),
            "tags": generated_result.get("topics", collected_info.get("topics", [])),  # tags도 동일
            "code": generated_result.get("code", {}),
            "solutions": [],  # solutions 형식으로 변환
            "input_format": generated_result.get("input_format"),
            "output_format": generated_result.get("output_format"),
            "examples": generated_result.get("examples", []),
            "constraints": generated_result.get("constraints", []),
            "key_concepts": generated_result.get("key_concepts", []),
        }

        # solutions 형식으로 code 변환
        code_data = generated_result.get("code", {})
        if isinstance(code_data, dict):
            for lang, code in code_data.items():
                if code:
                    generated_problem["solutions"].append({"language": lang, "code": code})

        response_message = (
            f"요청하신 조건에 맞는 문제를 DB에서 찾지 못해서, 새로운 문제를 생성했어요!\n\n"
            f"**{generated_problem['title']}** ({generated_problem['difficulty']})\n\n"
            f"이 문제를 풀어볼까요?"
        )
        action_data = {
            "status": "generated",
            "generated_problem": generated_problem,
            "is_fallback": True,
            "fallback_message": fallback_message,
        }
        action_trigger = "problem_generated"

    except Exception as e:
        print(f"[DiscoveryGraph:CodeGen] Error: {e}")
        import traceback
        traceback.print_exc()
        generated_problem = None
        response_message = "문제 생성 중 오류가 발생했어요. 다른 조건으로 다시 시도해볼까요?"
        action_data = {"status": "error", "error": str(e), "is_fallback": True}
        action_trigger = None

    return {
        "generated_problem": generated_problem,
        "response_message": response_message,
        "action_data": action_data,
        "action_trigger": action_trigger,
        "is_fallback": True,
        "fallback_message": fallback_message,
        "awaiting_selection": True,  # 선택 대기 상태
        "next_node": "handle_selection",
    }


async def handle_selection_node(state: DiscoveryState) -> Dict[str, Any]:
    """
    사용자의 문제 선택을 처리합니다.

    매칭 우선순위:
    1. state에서 전달받은 selection_index (intent_tool에서 이미 감지됨)
    2. collected_info의 선택 정보
    3. 패턴 매칭 (폴백)
    4. 단순 긍정 응답 → 첫 번째 문제
    """
    message = state.get("message", "")
    message_lower = message.lower()
    search_results = state.get("search_results", [])
    filtered_results = state.get("filtered_results", [])
    generated_problem = state.get("generated_problem")
    collected_info = state.get("collected_info", {})
    user_context = state.get("user_context", {})
    awaiting_selection = state.get("awaiting_selection", False)

    # 선택 대기 상태: 목록만 보여주고 respond로 이동
    if awaiting_selection and not state.get("selection_index") and not _has_selection_info(message_lower, collected_info):
        return {"next_node": "respond"}

    # filtered_results나 user_context에서 search_results 확인
    if not search_results:
        search_results = filtered_results or user_context.get("search_results", [])

    selected_problem = None
    selected_name = None
    selected_index = None

    # 1. state에서 selection_index 확인 (intent_tool에서 전달)
    if state.get("selection_index"):
        selected_index = state["selection_index"]
        print(f"[DiscoveryGraph] Using pre-detected selection_index: {selected_index}")

    # 2. collected_info에서 선택 정보 확인
    if not selected_index:
        if collected_info.get("selected_problem"):
            selected_name = collected_info["selected_problem"]
        if collected_info.get("selected_problem_index"):
            selected_index = collected_info["selected_problem_index"]

    # 3. 폴백: 패턴 매칭
    if not selected_index and not selected_name:
        num_match = re.search(r'(\d+)\s*번', message_lower)
        if num_match:
            selected_index = int(num_match.group(1))
        else:
            ordinal_map = {"첫": 1, "두": 2, "세": 3, "네": 4, "다섯": 5}
            for word, idx in ordinal_map.items():
                if word in message_lower:
                    selected_index = idx
                    break
            if not selected_index:
                simple_num = re.search(r'\b([1-5])\b', message_lower)
                if simple_num:
                    selected_index = int(simple_num.group(1))

    # 4. 메시지에서 문제 이름 추출
    if not selected_name and not selected_index:
        name_match = re.search(r'(taco_\d+)', message_lower, re.IGNORECASE)
        if name_match:
            selected_name = name_match.group(1)

    # 5. 문제 찾기 (인덱스 기반)
    if not selected_problem and selected_index and search_results:
        idx = selected_index - 1
        if 0 <= idx < len(search_results):
            selected_problem = search_results[idx]

    # 6. 문제 찾기 (이름 기반)
    if not selected_problem and selected_name and search_results:
        for p in search_results:
            if (p.get("name", "").lower() == selected_name.lower() or
                p.get("title", "").lower() == selected_name.lower()):
                selected_problem = p
                break

    # 7. generated_problem 확인
    if not selected_problem and generated_problem:
        if any(kw in message_lower for kw in ["할게", "풀게", "좋아", "네", "그거", "응"]):
            selected_problem = generated_problem

    # 8. 첫 번째 문제 default
    if not selected_problem and search_results:
        if any(kw in message_lower for kw in ["할게", "풀게", "좋아", "네", "첫", "응"]):
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

    # 강제 생성 요청이면 확인 노드로
    if state.get("force_generate") and next_node == "generate_problem":
        return "confirm_generation"

    valid_nodes = {"search_problems", "handle_selection", "filter_results", "generate_problem", "confirm_generation"}
    return next_node if next_node in valid_nodes else "search_problems"


def route_after_search(state: DiscoveryState) -> str:
    """검색 후 라우팅"""
    next_node = state.get("next_node", "filter_results")

    # fallback 생성이면 확인 노드로
    if next_node == "generate_problem" and state.get("should_generate"):
        return "confirm_generation"

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

def create_discovery_graph(checkpointer=None) -> StateGraph:
    """
    Discovery 그래프를 생성합니다.

    Args:
        checkpointer: LangGraph Checkpointer (상태 영속화용)
    """
    workflow = StateGraph(DiscoveryState)

    # 노드 추가
    workflow.add_node("route_discovery_intent", route_discovery_intent_node)
    workflow.add_node("search_problems", search_problems_node)
    workflow.add_node("filter_results", filter_results_node)
    # Human-in-the-Loop: 문제 생성 전 확인 노드
    workflow.add_node("confirm_generation", confirm_generation_node)
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
            "confirm_generation": "confirm_generation",  # 확인 노드로 먼저 이동
            "generate_problem": "generate_problem",  # 확인 없이 직접 생성 (fallback)
        }
    )

    # search_problems 후 라우팅
    workflow.add_conditional_edges(
        "search_problems",
        route_after_search,
        {
            "filter_results": "filter_results",
            "confirm_generation": "confirm_generation",  # 생성 전 확인
            "generate_problem": "generate_problem",
        }
    )

    # confirm_generation 후 라우팅
    workflow.add_conditional_edges(
        "confirm_generation",
        lambda s: s.get("next_node", "generate_problem"),
        {
            "generate_problem": "generate_problem",
            "respond": "respond",
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
        selection_index: int = None,
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
            selection_index: intent_tool에서 감지한 선택 인덱스 (1-based)

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
            "selection_index": selection_index,  # 오케스트레이터에서 전달받은 선택 인덱스
        }

        result = await self.graph.ainvoke(initial_state)

        return result

    def get_mermaid_diagram(self) -> str:
        """그래프를 Mermaid 다이어그램으로 반환"""
        try:
            return self.graph.get_graph().draw_mermaid()
        except Exception:
            return "Mermaid diagram not available"
