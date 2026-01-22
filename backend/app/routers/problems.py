from fastapi import APIRouter, HTTPException, Depends, Query, status
from typing import Optional
from uuid import UUID

from ..database import get_db
from ..dependencies import get_current_user_id_optional
from ..models.problem import (
    BaseProblemListItem,
    BaseProblemDetail,
    BaseProblemListResponse,
)

router = APIRouter()


# ===========================================
# base_problems 테이블 API
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
        # 단일 쿼리로 데이터 + count 조회 (최적화)
        query = db.table("base_problems")\
            .select("id, original_id, name, difficulty, tags, source, input_output, solve_count, like_count", count="exact")\
            .order("original_id")

        # 필터 적용
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

        # count="exact" 옵션으로 전체 개수도 함께 조회됨
        total = result.count if result.count is not None else 0

        items = [
            BaseProblemListItem(
                id=item["id"],
                original_id=item.get("original_id", ""),
                name=item.get("name", "Untitled"),
                difficulty=item.get("difficulty", "medium"),
                tags=item.get("tags") or [],
                source=item.get("source"),
                input_output=item.get("input_output"),
                solve_count=item.get("solve_count", 0),
                like_count=item.get("like_count", 0),
            )
            for item in (result.data or [])
        ]

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
async def get_base_problem(
    original_id: str,
    db=Depends(get_db),
    user_id: Optional[UUID] = Depends(get_current_user_id_optional),
):
    """
    base_problems 테이블에서 문제 상세 조회 (Preview용).

    original_id로 조회 (예: "baekjoon_1001", "taco_1")
    통계 정보(solve_count, like_count, is_liked)도 함께 반환.
    """
    try:
        # 문제 상세 + 통계 조회 (단일 쿼리)
        result = db.table("base_problems")\
            .select("id, original_id, name, question, difficulty, tags, source, url, input_output, explanation, solutions, solve_count, like_count")\
            .eq("original_id", original_id)\
            .single()\
            .execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Problem not found"
            )

        item = result.data
        problem_id = item["id"]

        # 현재 사용자의 좋아요 여부 확인 (로그인한 경우만)
        is_liked = False
        if user_id:
            like_check = db.table("problem_likes")\
                .select("id")\
                .eq("user_id", str(user_id))\
                .eq("base_problem_id", problem_id)\
                .execute()
            is_liked = bool(like_check.data)

        return BaseProblemDetail(
            id=problem_id,
            original_id=item.get("original_id", ""),
            name=item.get("name", "Untitled"),
            question=item.get("question", ""),
            difficulty=item.get("difficulty", "medium"),
            tags=item.get("tags") or [],
            source=item.get("source"),
            url=item.get("url"),
            input_output=item.get("input_output"),
            explanation=item.get("explanation"),
            solutions=item.get("solutions") or [],
            solve_count=item.get("solve_count", 0),
            like_count=item.get("like_count", 0),
            is_liked=is_liked,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get base problem: {str(e)}"
        )
