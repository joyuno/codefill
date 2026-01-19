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
from ..services.edge_case_logger import edge_case_logger


# ============================================================
# 관련 주제 확장 매핑 (재시도 폴백용)
# ============================================================
RELATED_TOPICS_MAP = {
    "DP": ["그리디", "분할정복", "메모이제이션"],
    "그리디": ["DP", "정렬"],
    "그래프": ["BFS", "DFS", "최단경로", "트리"],
    "BFS": ["DFS", "그래프", "최단경로"],
    "DFS": ["BFS", "그래프", "백트래킹"],
    "정렬": ["이진탐색", "투포인터"],
    "이진탐색": ["정렬", "투포인터"],
    "문자열": ["구현", "해시"],
    "구현": ["시뮬레이션", "문자열"],
    "백트래킹": ["DFS", "완전탐색"],
    "트리": ["그래프", "DFS", "BFS"],
    "스택": ["큐", "구현"],
    "큐": ["스택", "BFS"],
}


def _parse_requested_count(message: str) -> Optional[int]:
    """
    사용자 메시지에서 요청한 결과 개수를 파싱

    예: "10개 보여줘" → 10
        "20개 더 찾아줘" → 20
        "5개만" → 5

    Returns:
        요청된 개수 (없으면 None)
    """
    if not message:
        return None

    # 숫자 + 개 패턴
    count_match = re.search(r'(\d+)\s*개', message)
    if count_match:
        return int(count_match.group(1))

    return None


# 검색 결과 최대 개수 (한 번에 보여줄 수 있는 최대)
MAX_SEARCH_LIMIT = 10
DEFAULT_SEARCH_LIMIT = 5


def _expand_related_topics(topics: list) -> list:
    """
    검색 결과가 없을 때 관련 주제로 확장

    예: ["DP"] → ["DP", "그리디", "분할정복"]
    """
    if not topics:
        return ["구현", "정렬"]  # 기본 확장

    expanded = list(topics)
    for topic in topics:
        related = RELATED_TOPICS_MAP.get(topic, [])
        for r in related[:2]:  # 관련 주제 최대 2개씩 추가
            if r not in expanded:
                expanded.append(r)

    return expanded[:5]  # 최대 5개로 제한


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
    message = state.get("message", "")
    search_results = state.get("search_results", [])
    collected_info = state.get("collected_info", {})
    current_offset = state.get("search_offset", 0)
    selection_index = state.get("selection_index")

    # 🔢 사용자 요청 개수 파싱 (예: "10개 보여줘", "20개 더 찾아줘")
    requested_limit = _parse_requested_count(message)

    # 0. 문제 질문 의도 (inquire_problem)
    inquiry_target = state.get("inquiry_target")
    if intent == "inquire_problem" or inquiry_target:
        if search_results:
            print(f"[DiscoveryGraph] Problem inquiry detected: target={inquiry_target}")
            return {"next_node": "inquire_problem"}

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

    # 3. 더 찾아보기 의도 (다음 N개)
    if intent == "more_search" or intent == "show_more":
        # 사용자 요청 개수가 있으면 사용, 없으면 기본 5개
        fetch_count = requested_limit if requested_limit else 5
        new_offset = current_offset + fetch_count
        return {
            "search_offset": new_offset,
            "requested_limit": requested_limit,  # 사용자 요청 개수 전달
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

    # 7. Fallback: 의도 파악 실패 → 사용자에게 알리고 재검색
    # 검색 결과가 있는데 의도를 모르면 clarification 제공
    if search_results:
        return {
            "next_node": "fallback_clarify",
            "fallback_reason": "intent_unclear",
        }

    # 8. 기본: 검색
    return {"search_offset": 0, "next_node": "search_problems"}


async def search_problems_node(state: DiscoveryState) -> Dict[str, Any]:
    """
    Agentic RAG를 통해 문제를 검색합니다.

    개선된 로직:
    - topics + difficulty가 명확하면 메타데이터 검색만 (임베딩 비용 0)
    - 불명확하면 시맨틱 검색 (임베딩 사용)
    - offset을 사용하여 다음 결과를 가져올 수 있습니다.
    - 🔄 검색 실패 시 조건 완화 후 재시도 (difficulty → language → topics 순)
    - 🔢 사용자 요청 개수에 따라 동적 limit 적용 (최대 10개)
    """
    from ..services.rag import rag_service

    collected_info = state.get("collected_info", {})
    user_context = state.get("user_context", {})
    search_offset = state.get("search_offset", 0)
    message = state.get("message", "")

    # 🔢 사용자 요청 개수 확인 (state에서 전달받거나 메시지에서 파싱)
    requested_limit = state.get("requested_limit") or _parse_requested_count(message)
    limit_exceeded = False
    original_request = None

    if requested_limit:
        if requested_limit > MAX_SEARCH_LIMIT:
            # 최대 개수 초과 → 최대값으로 제한하고 안내 메시지 준비
            original_request = requested_limit
            requested_limit = MAX_SEARCH_LIMIT
            limit_exceeded = True
            print(f"[DiscoveryGraph:Search] Requested {original_request} items, limiting to {MAX_SEARCH_LIMIT}")
        per_page = requested_limit
    else:
        per_page = DEFAULT_SEARCH_LIMIT

    # 검색 파라미터
    topics = collected_info.get("topics", [])
    difficulty = collected_info.get("difficulty")
    language = collected_info.get("language", "python")

    # 디버그 로깅
    print(f"[DiscoveryGraph:Search] Params: topics={topics}, difficulty={difficulty}, language={language}, per_page={per_page}")

    # 검색 쿼리 생성 (시맨틱 검색 폴백용)
    query_parts = []
    if topics:
        query_parts.extend(topics)
    if difficulty:
        query_parts.append(f"{difficulty} difficulty")
    query = " ".join(query_parts) if query_parts else "기초 알고리즘 문제"

    # offset + N개를 가져와서 offset 이후 N개만 사용
    fetch_limit = search_offset + per_page

    # 🔄 조건 완화 재시도 로직
    retry_info = None  # 재시도 시 사용자에게 알릴 정보

    async def _do_search(t, d, lang):
        """실제 검색 수행"""
        q = " ".join(t) if t else "기초 알고리즘 문제"
        return await rag_service.search_problems_smart(
            query=q,
            topics=t,
            difficulty=d,
            language=lang,
            limit=fetch_limit,
            user_context=user_context,
        )

    try:
        # 1차 시도: 원본 조건으로 검색
        results, should_fallback, search_method = await _do_search(topics, difficulty, language)
        print(f"[DiscoveryGraph:Search] 1st try - Method: {search_method}, Results: {len(results)}")

        # 결과가 없고 offset이 0일 때만 재시도 (더보기 요청은 재시도 안함)
        if len(results) == 0 and search_offset == 0:

            # 2차 시도: difficulty 제거
            if difficulty:
                print(f"[DiscoveryGraph:Search] 2nd try - Removing difficulty filter")
                results, should_fallback, search_method = await _do_search(topics, None, language)
                print(f"[DiscoveryGraph:Search] 2nd try - Results: {len(results)}")

                if len(results) > 0:
                    retry_info = {
                        "relaxed": "difficulty",
                        "original": difficulty,
                        "message": f"'{difficulty}' 난이도에는 문제가 없어서 난이도 조건을 완화했어요."
                    }

            # 3차 시도: language도 제거 (python 외 요청 시)
            if len(results) == 0 and language and language != "python":
                print(f"[DiscoveryGraph:Search] 3rd try - Removing language filter")
                results, should_fallback, search_method = await _do_search(topics, None, None)
                print(f"[DiscoveryGraph:Search] 3rd try - Results: {len(results)}")

                if len(results) > 0:
                    retry_info = {
                        "relaxed": "language",
                        "original": language,
                        "message": f"'{language}' 언어 조건을 완화해서 다른 언어 문제도 포함했어요."
                    }

            # 4차 시도: topics 확장 (관련 주제 추가)
            if len(results) == 0 and topics:
                expanded_topics = _expand_related_topics(topics)
                if expanded_topics != topics:
                    print(f"[DiscoveryGraph:Search] 4th try - Expanding topics: {topics} → {expanded_topics}")
                    results, should_fallback, search_method = await _do_search(expanded_topics, None, None)
                    print(f"[DiscoveryGraph:Search] 4th try - Results: {len(results)}")

                    if len(results) > 0:
                        retry_info = {
                            "relaxed": "topics",
                            "original": topics,
                            "expanded": expanded_topics,
                            "message": f"'{', '.join(topics)}' 주제를 확장해서 관련 문제를 찾았어요."
                        }

        # offset 이후 결과만 사용 (per_page 적용)
        results = results[search_offset:search_offset + per_page]

        # 더 이상 결과가 없으면 fallback 여부 확인
        if len(results) == 0 and search_offset > 0:
            should_fallback = True
            print(f"[DiscoveryGraph:Search] No more results at offset {search_offset}")

    except Exception as e:
        print(f"[DiscoveryGraph:Search] RAG error: {e}")
        results = []
        should_fallback = True
        search_method = "error"

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

        # DB 필드: question, 프론트엔드 필드: description
        question_text = r.get("question") or r.get("description") or ""
        topics_list = r.get("topics") or tags if isinstance(tags, list) else []

        search_results.append({
            "id": r.get("id"),
            "original_id": r.get("original_id"),
            "name": r.get("name") or r.get("original_id"),
            "title": r.get("title") or r.get("name") or r.get("original_id"),
            "question": question_text,
            "description": question_text,  # 프론트엔드 호환용
            "difficulty": r.get("difficulty", "medium"),
            "tags": tags if isinstance(tags, list) else [],
            "topics": topics_list,  # topics가 없으면 tags 사용
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
        "search_method": search_method,  # 🚀 Agentic RAG: metadata | semantic | hybrid
        "retry_info": retry_info,  # 🔄 조건 완화 재시도 정보
        "per_page": per_page,  # 🔢 실제 적용된 페이지당 개수
        "limit_exceeded": limit_exceeded,  # 🔢 최대 개수 초과 여부
        "original_request": original_request,  # 🔢 원래 요청한 개수
        "next_node": next_node,
    }


async def filter_results_node(state: DiscoveryState) -> Dict[str, Any]:
    """
    검색 결과를 필터링하고 응답을 생성합니다.

    Note: RAG 검색이 이미 유사도 기반 정렬을 하므로 추가 reranking 불필요.
    동적 per_page에 따라 결과 개수 조정.
    """
    search_results = state.get("search_results", [])
    search_offset = state.get("search_offset", 0)
    retry_info = state.get("retry_info")  # 🔄 조건 완화 재시도 정보
    per_page = state.get("per_page", DEFAULT_SEARCH_LIMIT)  # 🔢 페이지당 개수
    limit_exceeded = state.get("limit_exceeded", False)  # 🔢 최대 개수 초과 여부
    original_request = state.get("original_request")  # 🔢 원래 요청한 개수

    # RAG 결과에서 per_page개 사용 (이미 유사도 정렬됨)
    filtered_results = search_results[:per_page]

    # 🔄 조건 완화 메시지 (있으면 앞에 추가)
    notices = []
    if retry_info and retry_info.get("message"):
        notices.append(f"⚠️ {retry_info['message']}")

    # 🔢 최대 개수 초과 안내
    if limit_exceeded and original_request:
        notices.append(f"📢 한 번에 최대 {MAX_SEARCH_LIMIT}개까지 보여드릴 수 있어요. ({original_request}개 요청 → {MAX_SEARCH_LIMIT}개 표시)")

    notice_text = "\n".join(notices) + "\n\n" if notices else ""

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
            response_message = f"{notice_text}추가로 찾은 문제들이에요 ({start_num}~{end_num}번):\n{problem_list}\n\n어떤 문제를 풀어볼까요?"
        else:
            problem_list = "\n".join([
                f"  {i+1}. {p.get('name') or p.get('title', 'Unknown')} ({p.get('difficulty', 'medium')})"
                for i, p in enumerate(filtered_results)
            ])
            # 최대 개수 안내
            more_hint = f"\n\n💡 더 보려면 \"더 보여줘\" 또는 \"N개 더 보여줘\"라고 말해주세요! (최대 {MAX_SEARCH_LIMIT}개)"
            response_message = f"{notice_text}찾은 문제들이에요:\n{problem_list}\n\n어떤 문제를 풀어볼까요? 번호로 선택해주세요!{more_hint}"

        action_data = {
            "status": "found",
            "problems": filtered_results,
            "search_offset": search_offset,
            "per_page": per_page,
            "has_more": len(filtered_results) == per_page,  # per_page개가 있으면 더 있을 수 있음
            "retry_info": retry_info,  # 🔄 조건 완화 정보 포함
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
    CodeGen Fallback 신호를 반환합니다.

    RAG 검색 결과가 없을 때 호출되며, 실제 문제 생성은 하지 않고
    프론트엔드에 "needs_codegen" 신호를 보내 스트리밍 엔드포인트를 호출하도록 합니다.

    이렇게 하면 chatMain의 20초 타임아웃에 걸리지 않고,
    프론트엔드에서 스트리밍으로 실시간 진행 상황을 표시할 수 있습니다.
    """
    collected_info = state.get("collected_info", {})
    search_results = state.get("search_results", [])  # RAG에서 찾은 유사 문제 (프론트엔드에서 참고용)

    # Fallback 알림 메시지
    topics_str = ", ".join(collected_info.get("topics", ["기초"]))

    print(f"[DiscoveryGraph:CodeGen] Fallback triggered - returning needs_codegen signal")
    print(f"[DiscoveryGraph:CodeGen] Topics: {topics_str}, Difficulty: {collected_info.get('difficulty', 'easy')}")

    # 실제 생성은 하지 않고, 프론트엔드에 신호만 반환
    response_message = (
        f"'{topics_str}' 관련 문제를 DB에서 찾지 못했어요.\n\n"
        f"새로운 문제를 생성할게요! 잠시만 기다려주세요..."
    )

    action_data = {
        "status": "needs_codegen",
        "is_fallback": True,
        # 프론트엔드에서 스트리밍 호출 시 필요한 정보
        "collected_info": collected_info,
        "similar_problems": search_results,
    }

    return {
        "generated_problem": None,
        "response_message": response_message,
        "action_data": action_data,
        "action_trigger": "needs_codegen",  # 프론트엔드에서 이 신호를 감지
        "is_fallback": True,
        "next_node": "respond",
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
    index_out_of_range = False
    if not selected_problem and selected_index and search_results:
        idx = selected_index - 1
        if 0 <= idx < len(search_results):
            selected_problem = search_results[idx]
        else:
            # EC-D03: 선택 인덱스 범위 초과
            index_out_of_range = True
            print(f"[DiscoveryGraph] Index out of range: {selected_index} (max: {len(search_results)})")

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
        # EC-D03: 인덱스 범위 초과 시 구체적인 안내
        if index_out_of_range and search_results:
            max_index = len(search_results)
            response_message = (
                f"**{selected_index}번** 문제는 없어요! "
                f"현재 검색 결과는 **1~{max_index}번**까지 있어요. "
                f"범위 내에서 선택해주세요! 🔢"
            )
            # EC-D03: 엣지케이스 로깅
            await edge_case_logger.log(
                code="EC-D03",
                user_id=state.get("user_context", {}).get("user_id"),
                session_id=state.get("session_id"),
                current_node="handle_selection",
                user_message=message,
                state_snapshot={
                    "selected_index": selected_index,
                    "max_index": max_index,
                    "search_results_count": len(search_results),
                },
                fallback_triggered=True,
                response_message=response_message,
                was_recovered=True,
            )
        else:
            response_message = "어떤 문제를 선택하셨는지 잘 모르겠어요. 번호나 이름으로 다시 말씀해주세요!"
        return {
            "response_message": response_message,
            "awaiting_selection": True,  # 선택 대기 상태 유지
            "next_node": next_node,
        }

    return {
        "selected_problem": selected_problem,
        "next_node": next_node,
    }


async def inquire_problem_node(state: DiscoveryState) -> Dict[str, Any]:
    """
    검색 결과에서 특정 문제에 대한 질문을 처리합니다.

    사용자가 문제 선택 전에 특정 문제에 대해 질문할 때:
    - "taco_749 요약해줘"
    - "두 번째 문제 뭐야?"
    - "3번 어떤 내용이야?"
    - "이거 뭐에 도움되냐?"
    """
    from ..tools.problem_inquiry_tool import get_problem_inquiry_tool

    message = state.get("message", "")
    inquiry_target = state.get("inquiry_target")
    search_results = state.get("search_results", [])
    filtered_results = state.get("filtered_results", [])
    user_context = state.get("user_context", {})
    conversation_history = state.get("conversation_history", [])

    # 검색 결과 확보
    if not search_results:
        search_results = filtered_results or user_context.get("search_results", [])

    if not search_results:
        return {
            "response_message": "먼저 문제를 검색해주세요! 어떤 주제로 연습하고 싶으신가요?",
            "next_node": "respond",
        }

    # inquiry_target이 없으면 메시지에서 추출 시도
    if not inquiry_target:
        # 숫자 패턴
        import re
        num_match = re.search(r'(\d+)\s*번', message)
        if num_match:
            inquiry_target = num_match.group(1)
        else:
            # 문제명 패턴 (taco_xxx)
            name_match = re.search(r'(taco_\d+)', message, re.IGNORECASE)
            if name_match:
                inquiry_target = name_match.group(1)
            else:
                # 서수 패턴
                ordinal_map = {"첫": "1", "두": "2", "세": "3", "네": "4", "다섯": "5"}
                for word, idx in ordinal_map.items():
                    if word in message:
                        inquiry_target = idx
                        break

    if not inquiry_target:
        return {
            "response_message": "어떤 문제에 대해 궁금하신가요? 번호나 이름을 알려주세요!",
            "next_node": "respond",
        }

    # Tool을 사용하여 질문 처리 (대화 히스토리 포함 - 꼬리 질문 맥락)
    inquiry_tool = get_problem_inquiry_tool()
    result = await inquiry_tool.inquire(
        question=message,
        inquiry_target=inquiry_target,
        search_results=search_results,
        conversation_history=conversation_history,
    )

    # 응답 구성 (선택 유도 포함)
    if result.success:
        response_message = result.response + "\n\n이 문제를 선택하시려면 번호를 말씀해주세요!"
    else:
        response_message = result.response

    return {
        "response_message": response_message,
        "awaiting_selection": True,  # 선택 대기 상태 유지
        "next_node": "respond",
    }


async def fallback_clarify_node(state: DiscoveryState) -> Dict[str, Any]:
    """
    의도 파악 실패 시 사용자에게 명확한 피드백 제공.

    - 현재 검색 결과가 있는 상태에서 의도를 파악하지 못함
    - 사용자에게 선택지를 다시 안내
    """
    search_results = state.get("search_results", [])
    fallback_reason = state.get("fallback_reason", "unknown")

    # 검색 결과가 있으면 선택 안내
    if search_results:
        problem_count = len(search_results)
        response_message = (
            f"요청을 정확히 이해하지 못했어요. 😅\n\n"
            f"현재 {problem_count}개의 문제가 검색되어 있어요:\n"
            f"• 번호로 선택하기 (예: \"1번\", \"두 번째\")\n"
            f"• 문제에 대해 질문하기 (예: \"1번 문제 설명해줘\")\n"
            f"• 다른 문제 찾기 (예: \"다른 문제 더 보여줘\")\n"
            f"• 새로 검색하기 (예: \"그래프 문제로 바꿔줘\")"
        )
    else:
        response_message = (
            "요청을 정확히 이해하지 못했어요. 😅\n\n"
            "어떤 주제의 문제를 풀고 싶으신가요?"
        )

    # EC-D01: 의도 파악 실패 로깅
    await edge_case_logger.log(
        code="EC-D01",
        user_id=state.get("user_context", {}).get("user_id"),
        session_id=state.get("session_id"),
        current_node="fallback_clarify",
        user_message=state.get("message"),
        state_snapshot={
            "fallback_reason": fallback_reason,
            "search_results_count": len(search_results),
        },
        fallback_triggered=True,
        response_message=response_message,
        was_recovered=True,
    )

    return {
        "response_message": response_message,
        "awaiting_selection": True,
        "next_node": "respond",
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
    최종 응답 노드 - LLM 기반 동적 응답 사용
    """
    if not state.get("response_message"):
        # 하드코딩된 폴백 대신 LLM 동적 응답
        from ..services.dynamic_response import dynamic_response_generator
        message = state.get("message", "")
        dynamic_response = await dynamic_response_generator.generate(
            message=message,
            intent="discovery_fallback",
            conversation_history=state.get("conversation_history"),
            user_context=state.get("user_context"),
        )
        return {"response_message": dynamic_response.message}
    return {}


# ============================================================
# Helper Functions
# ============================================================

def _is_selection_message(message: str) -> bool:
    """
    메시지가 문제 선택을 의미하는지 확인 (숫자 패턴만)

    Note: 키워드 기반 감지는 intent_tool에서 LLM 기반으로 처리됨.
          여기서는 구조적인 숫자 패턴만 확인 (fallback용).
    """
    selection_patterns = [
        r'\d+\s*번',  # 1번, 2번
        r'첫|두|세|네|다섯',  # 첫번째 등 (숫자 표현)
        r'\b[1-5]\b',  # 숫자만
        r'taco_\d+',  # 문제 이름 패턴
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

    valid_nodes = {"search_problems", "handle_selection", "filter_results", "generate_problem", "confirm_generation", "inquire_problem", "fallback_clarify"}
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
    workflow.add_node("inquire_problem", inquire_problem_node)  # 문제 질문 노드
    workflow.add_node("fallback_clarify", fallback_clarify_node)  # 의도 파악 실패 시 clarification
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
            "inquire_problem": "inquire_problem",  # 문제 질문
            "fallback_clarify": "fallback_clarify",  # 의도 파악 실패 시 clarification
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

    # inquire_problem → respond
    workflow.add_edge("inquire_problem", "respond")

    # fallback_clarify → respond
    workflow.add_edge("fallback_clarify", "respond")

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
        inquiry_target: str = None,
        inquiry_question: str = None,
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
            inquiry_target: 질문 대상 (인덱스 또는 문제명)
            inquiry_question: 원본 질문

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
            "inquiry_target": inquiry_target,  # 질문 대상 (인덱스 또는 문제명)
            "inquiry_question": inquiry_question,  # 원본 질문
        }

        result = await self.graph.ainvoke(initial_state)

        return result

    def get_mermaid_diagram(self) -> str:
        """그래프를 Mermaid 다이어그램으로 반환"""
        try:
            return self.graph.get_graph().draw_mermaid()
        except Exception:
            return "Mermaid diagram not available"
