"""
Agent Router
API endpoints for AI agents
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import StreamingResponse
from typing import Optional, Union
import json

from ..database import get_db
from ..services.openrouter import openrouter_service
from ..services.rag import rag_service
from ..services.embedding import embedding_service
from ..prompts import (
    CHAT_AGENT_SYSTEM_PROMPT,
    BLANK_PROBLEM_SYSTEM_PROMPT,
    PUZZLE_PROBLEM_SYSTEM_PROMPT,
    GUIDED_PROBLEM_SYSTEM_PROMPT,
    CODE_GEN_SYSTEM_PROMPT,
    HINT_AGENT_SYSTEM_PROMPT,
)
from ..models.agent import (
    # Chat Agent
    ChatAgentRequest,
    ChatAgentResponse,
    CollectedInfo,
    # Problem Generation
    ProblemGenerationRequest,
    BlankProblemResponse,
    PuzzleProblemResponse,
    GuidedProblemResponse,
    ProblemTypeEnum,
    # Code Generation
    CodeGenerationRequest,
    CodeGenerationResponse,
    # Hint Agent
    HintAgentRequest,
    HintAgentResponse,
    # RAG
    RAGSearchRequest,
    RAGSearchResponse,
)

router = APIRouter()


# ============================================================
# Chat Agent - Information Collection
# ============================================================

@router.post("/chat", response_model=ChatAgentResponse)
async def chat_agent(request: ChatAgentRequest, db=Depends(get_db)):
    """
    AI-powered information collection chatbot.

    Collects user preferences for problem recommendation:
    - topics: algorithm topics (array)
    - difficulty: easy/medium/hard
    - language: python/java/cpp
    - specific_needs: free text
    - time_available: minutes

    Uses GPT-4o-mini via OpenRouter.
    """
    try:
        # Build user context string
        user_context_str = json.dumps(request.user_context or {}, ensure_ascii=False)

        # Format system prompt with user context
        system_prompt = CHAT_AGENT_SYSTEM_PROMPT.format(
            user_context=user_context_str
        )

        # Build messages
        messages = [{"role": "system", "content": system_prompt}]

        # Add conversation history
        for msg in request.conversation_history:
            messages.append({"role": msg.role, "content": msg.content})

        # Add current message
        messages.append({"role": "user", "content": request.message})

        # Call LLM
        response = await openrouter_service.chat_completion(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            response_format={"type": "json_object"},
        )

        content = openrouter_service.get_content(response)
        result = openrouter_service.parse_json_response(content)

        # Parse collected info
        collected = result.get("collected_info", {})

        return ChatAgentResponse(
            message=result.get("message", ""),
            collected_info=CollectedInfo(
                topics=collected.get("topics", []),
                difficulty=collected.get("difficulty"),
                language=collected.get("language"),
                specific_needs=collected.get("specific_needs"),
                time_available=collected.get("time_available"),
            ),
            is_complete=result.get("is_complete", False),
            search_query=result.get("search_query"),
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat agent error: {str(e)}"
        )


@router.post("/chat/stream")
async def chat_agent_stream(request: ChatAgentRequest, db=Depends(get_db)):
    """
    Streaming version of chat agent.
    Returns Server-Sent Events (SSE).
    """
    async def generate():
        try:
            user_context_str = json.dumps(request.user_context or {}, ensure_ascii=False)
            system_prompt = CHAT_AGENT_SYSTEM_PROMPT.format(
                user_context=user_context_str
            )

            messages = [{"role": "system", "content": system_prompt}]
            for msg in request.conversation_history:
                messages.append({"role": msg.role, "content": msg.content})
            messages.append({"role": "user", "content": request.message})

            async for chunk in openrouter_service.chat_completion_stream(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.7,
            ):
                yield f"data: {json.dumps({'content': chunk})}\n\n"

            yield f"data: {json.dumps({'done': True})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


# ============================================================
# Problem Generation
# ============================================================

@router.post("/generate/blank", response_model=BlankProblemResponse)
async def generate_blank_problem(request: ProblemGenerationRequest, db=Depends(get_db)):
    """
    Generate a blank-fill problem from base problem.

    Uses GPT-4o-mini via OpenRouter.
    """
    try:
        # Format base problem as JSON
        base_problem_json = json.dumps({
            "title": request.base_problem.title,
            "description": request.base_problem.description,
            "code": request.base_problem.code,
            "difficulty": request.base_problem.difficulty.value,
            "topics": request.base_problem.topics,
        }, ensure_ascii=False)

        system_prompt = BLANK_PROBLEM_SYSTEM_PROMPT.format(
            base_problem=base_problem_json,
            user_level=request.user_level.value,
            language=request.language.value,
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "위 문제를 빈칸 채우기 문제로 변환해주세요."},
        ]

        response = await openrouter_service.chat_completion(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            response_format={"type": "json_object"},
        )

        content = openrouter_service.get_content(response)
        result = openrouter_service.parse_json_response(content)

        return BlankProblemResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Blank problem generation error: {str(e)}"
        )


@router.post("/generate/puzzle", response_model=PuzzleProblemResponse)
async def generate_puzzle_problem(request: ProblemGenerationRequest, db=Depends(get_db)):
    """
    Generate a puzzle (Parsons) problem from base problem.

    Uses GPT-4o-mini via OpenRouter.
    """
    try:
        base_problem_json = json.dumps({
            "title": request.base_problem.title,
            "description": request.base_problem.description,
            "code": request.base_problem.code,
            "difficulty": request.base_problem.difficulty.value,
            "topics": request.base_problem.topics,
        }, ensure_ascii=False)

        system_prompt = PUZZLE_PROBLEM_SYSTEM_PROMPT.format(
            base_problem=base_problem_json,
            user_level=request.user_level.value,
            language=request.language.value,
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "위 문제를 퍼즐(Parsons) 문제로 변환해주세요."},
        ]

        response = await openrouter_service.chat_completion(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            response_format={"type": "json_object"},
        )

        content = openrouter_service.get_content(response)
        result = openrouter_service.parse_json_response(content)

        return PuzzleProblemResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Puzzle problem generation error: {str(e)}"
        )


@router.post("/generate/guided", response_model=GuidedProblemResponse)
async def generate_guided_problem(request: ProblemGenerationRequest, db=Depends(get_db)):
    """
    Generate a guided (1:1 conversational) problem from base problem.

    Uses GPT-4o-mini via OpenRouter.
    """
    try:
        base_problem_json = json.dumps({
            "title": request.base_problem.title,
            "description": request.base_problem.description,
            "code": request.base_problem.code,
            "difficulty": request.base_problem.difficulty.value,
            "topics": request.base_problem.topics,
        }, ensure_ascii=False)

        system_prompt = GUIDED_PROBLEM_SYSTEM_PROMPT.format(
            base_problem=base_problem_json,
            user_level=request.user_level.value,
            language=request.language.value,
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "위 문제를 1대1 대화형 문제로 변환해주세요."},
        ]

        response = await openrouter_service.chat_completion(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            response_format={"type": "json_object"},
        )

        content = openrouter_service.get_content(response)
        result = openrouter_service.parse_json_response(content)

        return GuidedProblemResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Guided problem generation error: {str(e)}"
        )


# ============================================================
# Code Generation (RAG Fallback)
# ============================================================

@router.post("/generate/code", response_model=CodeGenerationResponse)
async def generate_code(request: CodeGenerationRequest, db=Depends(get_db)):
    """
    Generate new educational code when RAG similarity is low.

    Uses Claude Sonnet via OpenRouter.
    """
    try:
        system_prompt = CODE_GEN_SYSTEM_PROMPT.format(
            user_request=json.dumps(request.user_request, ensure_ascii=False),
            similar_problems=json.dumps(request.similar_problems, ensure_ascii=False),
            user_status=request.user_status or "unknown",
            user_goal=request.user_goal or "unknown",
            user_level=request.user_level.value,
            strong_algorithms=", ".join(request.strong_algorithms) if request.strong_algorithms else "없음",
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "사용자 요청에 맞는 교육용 코드를 생성해주세요."},
        ]

        response = await openrouter_service.chat_completion(
            model="claude-sonnet",
            messages=messages,
            temperature=0.7,
            max_tokens=8192,
            response_format={"type": "json_object"},
        )

        content = openrouter_service.get_content(response)
        result = openrouter_service.parse_json_response(content)

        return CodeGenerationResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Code generation error: {str(e)}"
        )


# ============================================================
# Hint Generation
# ============================================================

@router.post("/hint", response_model=HintAgentResponse)
async def generate_hint(request: HintAgentRequest, db=Depends(get_db)):
    """
    Generate AI-powered hint for a problem.

    Uses Gemini Flash via OpenRouter.
    Supports 4 hint levels (progressive disclosure).
    """
    try:
        system_prompt = HINT_AGENT_SYSTEM_PROMPT.format(
            problem_info=json.dumps(request.problem_info, ensure_ascii=False),
            user_code=request.user_code or "아직 코드 작성 안 함",
            attempt_count=request.attempt_count,
            hint_level=request.hint_level,
            previous_hints=json.dumps(request.previous_hints, ensure_ascii=False),
            user_level=request.user_level.value,
            related_docs="[]",  # TODO: Implement Docs RAG
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"레벨 {request.hint_level} 힌트를 생성해주세요."},
        ]

        response = await openrouter_service.chat_completion(
            model="gemini-flash",
            messages=messages,
            temperature=0.7,
            response_format={"type": "json_object"},
        )

        content = openrouter_service.get_content(response)
        result = openrouter_service.parse_json_response(content)

        return HintAgentResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hint generation error: {str(e)}"
        )


# ============================================================
# RAG Search
# ============================================================

@router.post("/search", response_model=RAGSearchResponse)
async def search_problems_rag(request: RAGSearchRequest, db=Depends(get_db)):
    """
    Search problems using RAG (vector similarity).

    Uses OpenAI embeddings + pgvector.
    Falls back to keyword search if embeddings unavailable.
    """
    try:
        # Build search query from topics and query
        search_query = request.query
        if request.topics:
            search_query += " " + " ".join(request.topics)

        # Perform hybrid search
        results, should_fallback = await rag_service.search_problems_hybrid(
            query=search_query,
            topics=request.topics,
            difficulty=request.difficulty.value if request.difficulty else None,
            language=request.language.value if request.language else None,
            limit=request.limit,
        )

        # Convert results to response format
        search_results = []
        for r in results:
            search_results.append(RAGSearchResult(
                id=r.get("problem_id", ""),
                title=r.get("text_content", "")[:100] if r.get("text_content") else "",
                description=r.get("text_content", "")[:300] if r.get("text_content") else "",
                similarity_score=r.get("similarity", 0),
                difficulty=r.get("difficulty", "medium"),
                topics=r.get("tags", []) if r.get("tags") else [],
            ))

        return RAGSearchResponse(
            results=search_results,
            query_embedding_used=True,
            fallback_to_code_gen=should_fallback,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"RAG search error: {str(e)}"
        )


# ============================================================
# Full Flow Endpoint
# ============================================================

@router.post("/recommend")
async def recommend_problems(
    collected_info: dict,
    user_context: Optional[dict] = None,
    db=Depends(get_db)
):
    """
    Full recommendation flow:
    1. Embed collected_info + user_context
    2. Search pgvector for similar problems
    3. If high similarity: return top 3 problems
    4. If low similarity: generate new code, then return

    Returns list of recommended problems for user to choose.
    """
    try:
        # Step 1: Build search query from collected info
        topics = collected_info.get("topics", [])
        difficulty = collected_info.get("difficulty", "medium")
        language = collected_info.get("language", "python")
        specific_needs = collected_info.get("specific_needs", "")
        search_query_text = collected_info.get("search_query", "")

        # Build comprehensive search query
        search_query = search_query_text or " ".join(topics)
        if specific_needs:
            search_query += " " + specific_needs

        # Step 2: Perform hybrid search with RAG
        results, should_fallback = await rag_service.search_problems_hybrid(
            query=search_query,
            topics=topics,
            difficulty=difficulty,
            language=language,
            limit=5,
        )

        # Step 3: Get full problem data for results
        problem_ids = [r.get("problem_id") for r in results if r.get("problem_id")]
        problems = []

        if problem_ids:
            # Fetch full problem data from base_problems
            response = db.table("base_problems")\
                .select("*")\
                .in_("id", problem_ids)\
                .execute()
            problems = response.data or []

            # Add similarity scores to problems
            similarity_map = {r["problem_id"]: r.get("similarity", 0) for r in results}
            for p in problems:
                p["similarity_score"] = similarity_map.get(p["id"], 0)

            # Sort by similarity score
            problems.sort(key=lambda x: x.get("similarity_score", 0), reverse=True)

        # Step 4: Check if we should generate new problems
        if not should_fallback and len(problems) >= 3:
            return {
                "status": "found",
                "problems": problems[:3],
                "fallback_used": False,
            }

        # Step 5: Fallback - generate new problem using Claude Sonnet
        if should_fallback or len(problems) < 3:
            try:
                generated = await rag_service.generate_problem_with_rag(
                    user_request=collected_info,
                    similar_problems=problems,
                    user_context=user_context,
                )
                return {
                    "status": "generated",
                    "problems": problems,
                    "generated_problem": generated,
                    "fallback_used": True,
                    "message": "유사한 문제가 부족하여 새로운 문제를 생성했습니다.",
                }
            except Exception as gen_error:
                print(f"Code generation fallback error: {gen_error}")
                return {
                    "status": "partial",
                    "problems": problems,
                    "fallback_used": True,
                    "message": "유사한 문제가 부족합니다. 다른 주제를 선택해보세요.",
                }

        return {
            "status": "found",
            "problems": problems[:3],
            "fallback_used": False,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Recommendation error: {str(e)}"
        )


# ============================================================
# Admin Endpoints (for embedding management)
# ============================================================

@router.post("/admin/embed-problems")
async def embed_problems_batch(
    limit: int = 100,
    offset: int = 0,
    db=Depends(get_db)
):
    """
    Batch embed problems from base_problems table.
    Admin endpoint for populating embeddings.

    Args:
        limit: Number of problems to process
        offset: Offset for pagination
    """
    try:
        # Fetch problems without embeddings
        response = db.table("base_problems")\
            .select("*")\
            .range(offset, offset + limit - 1)\
            .execute()

        problems = response.data or []

        if not problems:
            return {
                "message": "No problems to embed",
                "processed": 0,
            }

        # Batch embed
        result = await rag_service.batch_embed_problems(problems)

        return {
            "message": f"Embedded {result['success']} problems",
            "success": result["success"],
            "failed": result["failed"],
            "offset": offset,
            "limit": limit,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch embedding error: {str(e)}"
        )


@router.get("/admin/embedding-stats")
async def get_embedding_stats(db=Depends(get_db)):
    """
    Get embedding statistics.
    """
    try:
        # Count total problems
        problems_count = db.table("base_problems")\
            .select("id", count="exact")\
            .execute()

        # Count embeddings
        embeddings_count = db.table("problem_embeddings")\
            .select("id", count="exact")\
            .execute()

        return {
            "total_problems": problems_count.count or 0,
            "total_embeddings": embeddings_count.count or 0,
            "coverage": (
                (embeddings_count.count / problems_count.count * 100)
                if problems_count.count else 0
            ),
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Stats error: {str(e)}"
        )
