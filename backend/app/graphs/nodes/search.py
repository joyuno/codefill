"""
Search Node

RAG 검색을 통한 문제 검색
"""
from typing import Dict, Any, List
from ..state import ChatState, ProblemInfo


async def search_problems(state: ChatState) -> Dict[str, Any]:
    """
    Agentic RAG를 통해 문제를 검색합니다.

    개선된 로직:
    - topics + difficulty가 명확하면 메타데이터 검색만 (임베딩 비용 0)
    - 불명확하면 시맨틱 검색 (임베딩 사용)

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
    user_context = state.get("user_context", {})

    # 검색 파라미터 구성
    topics = collected_info.get("topics", [])
    difficulty = collected_info.get("difficulty")
    language = collected_info.get("language", "python")

    # 검색 쿼리 생성 (시맨틱 검색 폴백용)
    query_parts = []
    if topics:
        query_parts.extend(topics)
    if difficulty:
        query_parts.append(f"{difficulty} difficulty")
    query = " ".join(query_parts) if query_parts else "기초 문제"

    # 🚀 Agentic RAG: 스마트 검색 수행
    try:
        results, should_fallback, search_method = await rag_service.search_problems_smart(
            query=query,
            topics=topics,
            difficulty=difficulty,
            language=language,
            limit=5,
            user_context=user_context,
        )
        print(f"[Search] Method: {search_method}, Results: {len(results)}")
    except Exception as e:
        print(f"[Search] RAG search error: {e}")
        results = []
        should_fallback = True

    # 결과를 ProblemInfo 형식으로 변환
    search_results: List[ProblemInfo] = []
    for r in results:
        # DB 필드: question, 프론트엔드 필드: description
        question_text = r.get("question") or r.get("description") or ""
        search_results.append({
            "id": r.get("id"),
            "original_id": r.get("original_id"),  # 문제 유형 생성 시 필요!
            "name": r.get("name") or r.get("original_id"),
            "title": r.get("title") or r.get("name") or r.get("original_id"),
            "question": question_text,
            "description": question_text,  # 프론트엔드 호환용
            "difficulty": r.get("difficulty", "medium"),
            "tags": r.get("tags", []),
            "topics": r.get("topics") or r.get("tags", []),  # topics가 없으면 tags 사용
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
    else:
        # 문제를 찾지 못함
        response_message = "조건에 맞는 문제를 찾지 못했어요. 다른 조건으로 검색해볼까요?"
        action_data = {
            "status": "not_found",
        }

    return {
        "search_results": search_results,
        "should_generate": should_generate,
        "response_message": response_message,
        "action_data": action_data,
        "action_trigger": "search_problems" if search_results else None,
        "next_node": "respond",
    }
