"""
Search and Problem Generation Nodes

RAG 검색 및 CodeGen을 통한 문제 검색/생성
"""
import json
from typing import Dict, Any, List
from ..state import ChatState, ProblemInfo


async def search_problems(state: ChatState) -> Dict[str, Any]:
    """
    RAG를 통해 문제를 검색합니다.

    Returns:
        업데이트된 상태:
        - search_results: 검색된 문제 목록
        - should_generate: CodeGen fallback 필요 여부
        - response_message: 응답 메시지
        - action_data: 프론트엔드 액션 데이터
        - next_node: 다음 노드
    """
    from ...services.rag import rag_service

    collected_info = state.get("collected_info", {})

    # 검색 파라미터 구성
    topics = collected_info.get("topics", [])
    difficulty = collected_info.get("difficulty")
    language = collected_info.get("language", "python")

    # 검색 쿼리 생성
    query_parts = []
    if topics:
        query_parts.extend(topics)
    if difficulty:
        query_parts.append(f"{difficulty} difficulty")
    query = " ".join(query_parts) if query_parts else "기초 문제"

    # RAG 검색 수행
    try:
        results, should_fallback = await rag_service.search_problems_hybrid(
            query=query,
            topics=topics,
            difficulty=difficulty,
            language=language,
            limit=5
        )
    except Exception as e:
        print(f"[Search] RAG search error: {e}")
        results = []
        should_fallback = True

    # 결과를 ProblemInfo 형식으로 변환
    search_results: List[ProblemInfo] = []
    for r in results:
        search_results.append({
            "id": r.get("id"),
            "original_id": r.get("original_id"),  # 문제 유형 생성 시 필요!
            "name": r.get("name") or r.get("original_id"),
            "title": r.get("title") or r.get("name"),
            "question": r.get("question"),
            "description": r.get("description"),
            "difficulty": r.get("difficulty", "medium"),
            "tags": r.get("tags", []),
            "topics": r.get("topics", []),
            "solutions": r.get("solutions", []),
            "input_output": r.get("input_output"),  # 테스트 케이스용
            "similarity": r.get("similarity"),
        })

    # 결과가 충분한지 확인
    should_generate = should_fallback or len(search_results) == 0

    if search_results:
        # 문제를 찾음
        problem_list = "\n".join([
            f"  {i+1}. {p.get('name') or p.get('title', 'Unknown')} ({p.get('difficulty', 'medium')})"
            for i, p in enumerate(search_results[:5])
        ])
        response_message = f"찾은 문제들이에요:\n{problem_list}\n\n어떤 문제를 풀어볼까요?"

        action_data = {
            "status": "found",
            "problems": search_results[:5],
        }
        next_node = "respond"
    else:
        # CodeGen으로 fallback
        response_message = ""  # generate_problem_codegen에서 설정
        action_data = None
        next_node = "generate_problem_codegen"

    return {
        "search_results": search_results,
        "should_generate": should_generate,
        "response_message": response_message,
        "action_data": action_data,
        "action_trigger": "search_problems" if search_results else None,
        "next_node": next_node,
    }


async def generate_problem_codegen(state: ChatState) -> Dict[str, Any]:
    """
    CodeGen을 통해 새 문제를 생성합니다 (RAG 결과가 부족할 때).

    Returns:
        업데이트된 상태:
        - generated_problem: 생성된 문제
        - response_message: 응답 메시지
        - action_data: 프론트엔드 액션 데이터
    """
    from ...services.openrouter import openrouter_service
    from ...prompts.code_gen_agent import CODE_GEN_SYSTEM_PROMPT

    collected_info = state.get("collected_info", {})

    # 사용자 요청 구성
    user_request = {
        "topics": collected_info.get("topics", ["기초"]),
        "difficulty": collected_info.get("difficulty", "easy"),
        "language": collected_info.get("language", "python"),
        "specific_needs": collected_info.get("specific_needs", ""),
    }

    print(f"[CodeGen] Starting generation...")
    print(f"[CodeGen] user_request: {user_request}")

    # CodeGen 호출
    messages = [
        {"role": "system", "content": CODE_GEN_SYSTEM_PROMPT},
        {"role": "user", "content": json.dumps(user_request, ensure_ascii=False)},
    ]

    try:
        response = await openrouter_service.chat_completion(
            messages=messages,
            model="claude-sonnet",  # 코드 생성은 Claude Sonnet
            response_format={"type": "json_object"},
        )

        content = openrouter_service.get_content(response)
        print(f"[CodeGen] LLM Response preview: {content[:500]}...")

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

    except Exception as e:
        print(f"[CodeGen] Error: {e}")
        generated_problem = None
        response_message = "문제 생성 중 오류가 발생했어요. 다른 조건으로 다시 시도해볼까요?"
        action_data = {"status": "error", "error": str(e)}

    return {
        "generated_problem": generated_problem,
        "response_message": response_message,
        "action_data": action_data,
        "action_trigger": "generated" if generated_problem else None,
        "next_node": "respond",
    }
