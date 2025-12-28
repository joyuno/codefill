from fastapi import APIRouter, HTTPException, Depends, Query, status
from typing import Optional, List
from uuid import UUID

from ..database import get_db
from ..models.problem import (
    Problem,
    ProblemDetail,
    ProblemListItem,
    ProblemFilter,
    ProblemType,
    Difficulty,
    Framework,
    HintRequest,
    HintResponse,
    Code,
    BaseProblemListItem,
    BaseProblemDetail,
    BaseProblemListResponse,
)

router = APIRouter()


# ===========================================
# base_problems 테이블 API (정적 경로 먼저 정의)
# ===========================================

@router.get("/base", response_model=BaseProblemListResponse)
async def list_base_problems(
    difficulty: Optional[str] = None,
    source: Optional[str] = None,
    search: Optional[str] = None,
    tags: Optional[str] = None,  # comma-separated
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db=Depends(get_db)
):
    """
    base_problems 테이블에서 문제 목록 조회.

    - difficulty: easy, medium, hard
    - source: baekjoon, codeforces, leetcode 등
    - search: 문제명 검색
    - tags: 태그 필터 (쉼표 구분)
    """
    try:
        # 먼저 전체 개수 조회
        count_query = db.table("base_problems").select("id", count="exact")

        if difficulty:
            count_query = count_query.eq("difficulty", difficulty)
        if source:
            count_query = count_query.eq("source", source)
        if search:
            count_query = count_query.ilike("name", f"%{search}%")
        if tags:
            tag_list = [t.strip() for t in tags.split(",")]
            count_query = count_query.overlaps("tags", tag_list)

        count_result = count_query.execute()
        total = count_result.count if count_result.count else 0

        # 실제 데이터 조회
        query = db.table("base_problems")\
            .select("id, original_id, name, difficulty, tags, source")\
            .order("original_id")

        if difficulty:
            query = query.eq("difficulty", difficulty)
        if source:
            query = query.eq("source", source)
        if search:
            query = query.ilike("name", f"%{search}%")
        if tags:
            tag_list = [t.strip() for t in tags.split(",")]
            query = query.overlaps("tags", tag_list)

        # Pagination
        offset = (page - 1) * limit
        query = query.range(offset, offset + limit - 1)

        result = query.execute()

        items = []
        for item in (result.data or []):
            items.append(BaseProblemListItem(
                id=item["id"],
                original_id=item.get("original_id", ""),
                name=item.get("name", "Untitled"),
                difficulty=item.get("difficulty", "medium"),
                tags=item.get("tags") or [],
                source=item.get("source"),
            ))

        has_more = (page * limit) < total

        return BaseProblemListResponse(
            items=items,
            total=total,
            page=page,
            limit=limit,
            has_more=has_more,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list base problems: {str(e)}"
        )


@router.get("/base/{original_id}", response_model=BaseProblemDetail)
async def get_base_problem(original_id: str, db=Depends(get_db)):
    """
    base_problems 테이블에서 문제 상세 조회 (Preview용).

    original_id로 조회 (예: "baekjoon_1001", "taco_1")
    """
    try:
        result = db.table("base_problems")\
            .select("*")\
            .eq("original_id", original_id)\
            .single()\
            .execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Problem not found"
            )

        item = result.data
        return BaseProblemDetail(
            id=item["id"],
            original_id=item.get("original_id", ""),
            name=item.get("name", "Untitled"),
            question=item.get("question", ""),
            difficulty=item.get("difficulty", "medium"),
            tags=item.get("tags") or [],
            source=item.get("source"),
            url=item.get("url"),
            input_output=item.get("input_output"),
            explanation=item.get("explanation"),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get base problem: {str(e)}"
        )


@router.get("/search/rag")
async def search_problems_rag(
    query: str = Query(..., min_length=2),
    framework: Optional[Framework] = None,
    limit: int = Query(5, ge=1, le=20),
    db=Depends(get_db)
):
    """
    Search problems using RAG (Retrieval Augmented Generation).

    Uses vector similarity search with pgvector.
    Requires OpenAI embeddings API key.
    """
    # TODO: Implement when OpenAI API key is available
    return {
        "message": "RAG search not yet implemented. Please provide OpenAI API key.",
        "query": query,
        "results": []
    }


# ===========================================
# 기존 problems 테이블 API (동적 경로는 나중에)
# ===========================================

@router.get("", response_model=List[ProblemListItem])
async def list_problems(
    framework: Optional[Framework] = None,
    difficulty: Optional[Difficulty] = None,
    problem_type: Optional[ProblemType] = None,
    search: Optional[str] = None,
    tags: Optional[str] = None,  # comma-separated
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db=Depends(get_db)
):
    """
    List problems with optional filtering.

    Supports filtering by:
    - framework (python, java, cpp, javascript)
    - difficulty (easy, medium, hard)
    - problem_type (blank, puzzle)
    - search (text search in title/description)
    - tags (comma-separated list)
    """
    try:
        # Build query
        query = db.table("problems")\
            .select("id, problem_type, difficulty, times_solved, avg_solve_time, codes(title, framework, tags)")

        if framework:
            query = query.eq("codes.framework", framework.value)

        if difficulty:
            query = query.eq("difficulty", difficulty.value)

        if problem_type:
            query = query.eq("problem_type", problem_type.value)

        # Pagination
        offset = (page - 1) * limit
        query = query.range(offset, offset + limit - 1)

        result = query.execute()

        items = []
        for item in (result.data or []):
            code_data = item.get("codes", {}) or {}
            items.append(ProblemListItem(
                id=item["id"],
                title=code_data.get("title", "Untitled"),
                framework=code_data.get("framework", "javascript"),
                difficulty=item.get("difficulty", "medium"),
                problem_type=item.get("problem_type", "blank"),
                topics=code_data.get("tags", []),
                times_solved=item.get("times_solved", 0),
                avg_solve_time=item.get("avg_solve_time"),
            ))

        return items

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list problems: {str(e)}"
        )


@router.get("/{problem_id}", response_model=ProblemDetail)
async def get_problem(problem_id: UUID, db=Depends(get_db)):
    """
    Get problem details for practice.

    Returns full problem data including:
    - Problem code and metadata
    - Type-specific data (blanks, test_cases, options)
    - Hints (without revealing answers)
    - Related concepts and docs
    """
    try:
        # Get problem with code
        result = db.table("problems")\
            .select("*, codes(*)")\
            .eq("id", str(problem_id))\
            .single()\
            .execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Problem not found"
            )

        problem_data = result.data
        code_data = problem_data.pop("codes", {})

        # Parse answer_data based on problem type
        answer_data = problem_data.get("answer_data", {})
        problem_type = problem_data.get("problem_type")

        problem_kwargs = {
            "id": problem_data["id"],
            "code_id": problem_data["code_id"],
            "problem_type": problem_type,
            "problem_code": problem_data["problem_code"],
            "difficulty": problem_data.get("difficulty", "medium"),
            "times_attempted": problem_data.get("times_attempted", 0),
            "times_solved": problem_data.get("times_solved", 0),
            "avg_solve_time": problem_data.get("avg_solve_time"),
            "created_at": problem_data["created_at"],
        }

        # Add type-specific data (without revealing answers)
        if problem_type == "blank" and answer_data.get("blanks"):
            # Include blanks but hide answers for client
            blanks = answer_data["blanks"]
            problem_kwargs["blanks"] = [
                {
                    "id": b["id"],
                    "position": i,  # Use index as position
                    "answer": "",   # Hide answer
                    "hints": b.get("hints", [])
                }
                for i, b in enumerate(blanks)
            ]
        elif problem_type == "puzzle" and answer_data.get("blocks"):
            # Include blocks for puzzle but shuffled (client handles randomization)
            blocks = answer_data["blocks"]
            distractors = answer_data.get("distractors", [])

            # Combine blocks and distractors for client (order hidden)
            all_blocks = [
                {
                    "id": b["id"],
                    "code": b["code"],
                    "indentation": 0,  # Client will determine indentation
                }
                for b in blocks
            ]
            # Add distractors
            all_blocks.extend([
                {
                    "id": d["id"],
                    "code": d["code"],
                    "indentation": 0,
                }
                for d in distractors
            ])

            problem_kwargs["puzzle_data"] = {
                "blocks": all_blocks,
                "correct_order": [],  # Hidden from client
                "distractors": None
            }

        # Get hints from problem data
        hints = problem_data.get("hints", {})

        return ProblemDetail(
            problem=Problem(**problem_kwargs),
            code=Code(**code_data),
            hints=hints.get("general", []),
            key_concepts=code_data.get("tags", []),
            related_docs=[],
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get problem: {str(e)}"
        )


@router.post("/{problem_id}/hint", response_model=HintResponse)
async def get_hint(
    problem_id: UUID,
    request: HintRequest,
    db=Depends(get_db)
):
    """
    Get hint for a problem.

    Hints are provided in 3 levels:
    - Level 1: General direction
    - Level 2: More specific guidance
    - Level 3: Almost gives away the answer

    Each hint costs 10 XP.
    """
    try:
        # Get problem hints
        result = db.table("problems")\
            .select("hints, problem_type, answer_data")\
            .eq("id", str(problem_id))\
            .single()\
            .execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Problem not found"
            )

        hints_data = result.data.get("hints", {})
        problem_type = result.data.get("problem_type")

        # Get level-specific hint
        level = request.hint_level
        level_key = f"level_{level}"

        hint_text = hints_data.get(level_key, f"No level {level} hint available for this problem.")

        return HintResponse(
            hint=hint_text,
            level=level,
            xp_cost=10,
            docs_reference=hints_data.get("docs_url"),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get hint: {str(e)}"
        )
