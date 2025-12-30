"""
Solutions Router - 문제 풀이 게시글 시스템

엔드포인트:
- GET /solutions/problem/{original_id} - 문제 게시글 페이지 (문제 + 정답 + 풀이 목록)
- GET /solutions - 풀이 목록
- POST /solutions - 풀이 작성
- GET /solutions/{id} - 풀이 상세
- PUT /solutions/{id} - 풀이 수정
- DELETE /solutions/{id} - 풀이 삭제
- POST /solutions/{id}/vote - 풀이 투표
- GET /solutions/{id}/comments - 댓글 목록
- POST /solutions/{id}/comments - 댓글 작성
- PUT /comments/{id} - 댓글 수정
- DELETE /comments/{id} - 댓글 삭제
- POST /comments/{id}/vote - 댓글 투표
"""

from fastapi import APIRouter, HTTPException, Depends, Query, status
from typing import Optional, List
from uuid import UUID

from ..database import get_db
from ..dependencies import get_current_user, get_optional_user
from ..models.solution import (
    SolutionCreate,
    SolutionUpdate,
    SolutionListItem,
    SolutionDetail,
    SolutionListResponse,
    CommentCreate,
    CommentUpdate,
    CommentItem,
    CommentListResponse,
    VoteRequest,
    VoteResponse,
    ProblemDiscussionResponse,
)

router = APIRouter()


# =====================================================
# 문제 게시글 페이지
# =====================================================

@router.get("/problem/{original_id}", response_model=ProblemDiscussionResponse)
async def get_problem_discussion(
    original_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    sort: str = Query("upvotes", regex="^(upvotes|newest|oldest)$"),
    db=Depends(get_db),
    current_user=Depends(get_optional_user)
):
    """
    문제 게시글 페이지 조회.

    - 문제 정보 (base_problems)
    - 공식 정답 코드 (solutions JSONB)
    - 사용자 풀이 목록 (problem_solutions)
    """
    try:
        # 1. 문제 정보 조회
        problem_result = db.table("base_problems")\
            .select("*")\
            .eq("original_id", original_id)\
            .single()\
            .execute()

        if not problem_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Problem not found"
            )

        problem = problem_result.data
        official_solutions = problem.get("solutions") or []

        # 2. 사용자 풀이 목록 조회
        base_problem_id = problem["id"]

        # 정렬
        order_column = "upvotes" if sort == "upvotes" else "created_at"
        order_desc = sort != "oldest"

        # 전체 개수
        count_result = db.table("problem_solutions")\
            .select("id", count="exact")\
            .eq("base_problem_id", base_problem_id)\
            .execute()
        total = count_result.count if count_result.count else 0

        # 풀이 목록
        offset = (page - 1) * limit
        solutions_query = db.table("solution_details")\
            .select("*")\
            .eq("base_problem_id", base_problem_id)

        if order_desc:
            solutions_query = solutions_query.order(order_column, desc=True)
        else:
            solutions_query = solutions_query.order(order_column)

        solutions_query = solutions_query.range(offset, offset + limit - 1)
        solutions_result = solutions_query.execute()

        # 현재 사용자의 투표 정보
        user_votes = {}
        if current_user:
            solution_ids = [s["id"] for s in (solutions_result.data or [])]
            if solution_ids:
                votes_result = db.table("solution_votes")\
                    .select("solution_id, vote_type")\
                    .eq("user_id", current_user["id"])\
                    .in_("solution_id", solution_ids)\
                    .execute()
                user_votes = {v["solution_id"]: v["vote_type"] for v in (votes_result.data or [])}

        items = []
        for s in (solutions_result.data or []):
            items.append(SolutionListItem(
                id=s["id"],
                user_id=s["user_id"],
                language=s["language"],
                code=s.get("code", ""),
                title=s.get("title"),
                upvotes=s.get("upvotes", 0),
                downvotes=s.get("downvotes", 0),
                comment_count=s.get("comment_count", 0),
                created_at=s["created_at"],
                author_name=s.get("author_name"),
                author_avatar=s.get("author_avatar"),
            ))

        has_more = (page * limit) < total

        return ProblemDiscussionResponse(
            problem=problem,
            official_solutions=official_solutions,
            user_solutions=SolutionListResponse(
                items=items,
                total=total,
                page=page,
                limit=limit,
                has_more=has_more,
            )
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get problem discussion: {str(e)}"
        )


# =====================================================
# 풀이 CRUD
# =====================================================

@router.get("", response_model=SolutionListResponse)
async def list_solutions(
    base_problem_id: Optional[UUID] = None,
    user_id: Optional[UUID] = None,
    language: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    sort: str = Query("upvotes", regex="^(upvotes|newest|oldest)$"),
    db=Depends(get_db)
):
    """풀이 목록 조회."""
    try:
        # 전체 개수
        count_query = db.table("problem_solutions").select("id", count="exact")
        if base_problem_id:
            count_query = count_query.eq("base_problem_id", str(base_problem_id))
        if user_id:
            count_query = count_query.eq("user_id", str(user_id))
        if language:
            count_query = count_query.eq("language", language)

        count_result = count_query.execute()
        total = count_result.count if count_result.count else 0

        # 풀이 목록
        query = db.table("solution_details").select("*")
        if base_problem_id:
            query = query.eq("base_problem_id", str(base_problem_id))
        if user_id:
            query = query.eq("user_id", str(user_id))
        if language:
            query = query.eq("language", language)

        # 정렬
        order_column = "upvotes" if sort == "upvotes" else "created_at"
        order_desc = sort != "oldest"
        if order_desc:
            query = query.order(order_column, desc=True)
        else:
            query = query.order(order_column)

        # 페이지네이션
        offset = (page - 1) * limit
        query = query.range(offset, offset + limit - 1)

        result = query.execute()

        items = []
        for s in (result.data or []):
            items.append(SolutionListItem(
                id=s["id"],
                user_id=s["user_id"],
                language=s["language"],
                code=s.get("code", ""),
                title=s.get("title"),
                upvotes=s.get("upvotes", 0),
                downvotes=s.get("downvotes", 0),
                comment_count=s.get("comment_count", 0),
                created_at=s["created_at"],
                author_name=s.get("author_name"),
                author_avatar=s.get("author_avatar"),
            ))

        has_more = (page * limit) < total

        return SolutionListResponse(
            items=items,
            total=total,
            page=page,
            limit=limit,
            has_more=has_more,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list solutions: {str(e)}"
        )


@router.post("", response_model=SolutionDetail, status_code=status.HTTP_201_CREATED)
async def create_solution(
    request: SolutionCreate,
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    """풀이 작성."""
    try:
        # 문제 존재 확인
        problem_result = db.table("base_problems")\
            .select("id")\
            .eq("id", str(request.base_problem_id))\
            .single()\
            .execute()

        if not problem_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Problem not found"
            )

        # 풀이 생성
        insert_data = {
            "base_problem_id": str(request.base_problem_id),
            "user_id": current_user["id"],
            "language": request.language,
            "code": request.code,
            "title": request.title,
            "description": request.description,
        }

        result = db.table("problem_solutions")\
            .insert(insert_data)\
            .execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create solution"
            )

        solution = result.data[0]

        return SolutionDetail(
            id=solution["id"],
            base_problem_id=solution["base_problem_id"],
            user_id=solution["user_id"],
            language=solution["language"],
            code=solution["code"],
            title=solution.get("title"),
            description=solution.get("description"),
            is_correct=solution.get("is_correct", True),
            upvotes=0,
            downvotes=0,
            view_count=0,
            comment_count=0,
            created_at=solution["created_at"],
            updated_at=solution["updated_at"],
            author_name=current_user.get("name"),
            author_avatar=current_user.get("avatar_url"),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create solution: {str(e)}"
        )


@router.get("/{solution_id}", response_model=SolutionDetail)
async def get_solution(
    solution_id: UUID,
    db=Depends(get_db),
    current_user=Depends(get_optional_user)
):
    """풀이 상세 조회."""
    try:
        result = db.table("solution_details")\
            .select("*")\
            .eq("id", str(solution_id))\
            .single()\
            .execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Solution not found"
            )

        s = result.data

        # 조회수 증가
        db.table("problem_solutions")\
            .update({"view_count": s.get("view_count", 0) + 1})\
            .eq("id", str(solution_id))\
            .execute()

        # 현재 사용자의 투표
        my_vote = None
        if current_user:
            vote_result = db.table("solution_votes")\
                .select("vote_type")\
                .eq("solution_id", str(solution_id))\
                .eq("user_id", current_user["id"])\
                .execute()
            if vote_result.data:
                my_vote = vote_result.data[0]["vote_type"]

        return SolutionDetail(
            id=s["id"],
            base_problem_id=s["base_problem_id"],
            user_id=s["user_id"],
            language=s["language"],
            code=s["code"],
            title=s.get("title"),
            description=s.get("description"),
            is_correct=s.get("is_correct", True),
            upvotes=s.get("upvotes", 0),
            downvotes=s.get("downvotes", 0),
            view_count=s.get("view_count", 0) + 1,
            comment_count=s.get("comment_count", 0),
            created_at=s["created_at"],
            updated_at=s["updated_at"],
            author_name=s.get("author_name"),
            author_avatar=s.get("author_avatar"),
            problem_original_id=s.get("problem_original_id"),
            problem_name=s.get("problem_name"),
            my_vote=my_vote,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get solution: {str(e)}"
        )


@router.put("/{solution_id}", response_model=SolutionDetail)
async def update_solution(
    solution_id: UUID,
    request: SolutionUpdate,
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    """풀이 수정 (본인만 가능)."""
    try:
        # 풀이 조회 및 권한 확인
        result = db.table("problem_solutions")\
            .select("*")\
            .eq("id", str(solution_id))\
            .single()\
            .execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Solution not found"
            )

        if result.data["user_id"] != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this solution"
            )

        # 업데이트
        update_data = {}
        if request.code is not None:
            update_data["code"] = request.code
        if request.language is not None:
            update_data["language"] = request.language
        if request.title is not None:
            update_data["title"] = request.title
        if request.description is not None:
            update_data["description"] = request.description

        if update_data:
            db.table("problem_solutions")\
                .update(update_data)\
                .eq("id", str(solution_id))\
                .execute()

        # 업데이트된 데이터 반환
        return await get_solution(solution_id, db, current_user)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update solution: {str(e)}"
        )


@router.delete("/{solution_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_solution(
    solution_id: UUID,
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    """풀이 삭제 (본인만 가능)."""
    try:
        # 풀이 조회 및 권한 확인
        result = db.table("problem_solutions")\
            .select("user_id")\
            .eq("id", str(solution_id))\
            .single()\
            .execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Solution not found"
            )

        if result.data["user_id"] != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this solution"
            )

        # 삭제
        db.table("problem_solutions")\
            .delete()\
            .eq("id", str(solution_id))\
            .execute()

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete solution: {str(e)}"
        )


# =====================================================
# 풀이 투표
# =====================================================

@router.post("/{solution_id}/vote", response_model=VoteResponse)
async def vote_solution(
    solution_id: UUID,
    request: VoteRequest,
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    """풀이 투표 (up/down)."""
    try:
        # 기존 투표 확인
        existing = db.table("solution_votes")\
            .select("id, vote_type")\
            .eq("solution_id", str(solution_id))\
            .eq("user_id", current_user["id"])\
            .execute()

        if existing.data:
            # 같은 투표면 취소
            if existing.data[0]["vote_type"] == request.vote_type.value:
                db.table("solution_votes")\
                    .delete()\
                    .eq("id", existing.data[0]["id"])\
                    .execute()
                my_vote = None
            else:
                # 다른 투표면 변경
                db.table("solution_votes")\
                    .update({"vote_type": request.vote_type.value})\
                    .eq("id", existing.data[0]["id"])\
                    .execute()
                my_vote = request.vote_type.value
        else:
            # 새 투표
            db.table("solution_votes")\
                .insert({
                    "solution_id": str(solution_id),
                    "user_id": current_user["id"],
                    "vote_type": request.vote_type.value,
                })\
                .execute()
            my_vote = request.vote_type.value

        # 업데이트된 투표 수 조회
        solution = db.table("problem_solutions")\
            .select("upvotes, downvotes")\
            .eq("id", str(solution_id))\
            .single()\
            .execute()

        return VoteResponse(
            success=True,
            upvotes=solution.data.get("upvotes", 0),
            downvotes=solution.data.get("downvotes", 0),
            my_vote=my_vote,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to vote: {str(e)}"
        )


# =====================================================
# 댓글 CRUD
# =====================================================

@router.get("/{solution_id}/comments", response_model=CommentListResponse)
async def list_comments(
    solution_id: UUID,
    db=Depends(get_db),
    current_user=Depends(get_optional_user)
):
    """댓글 목록 조회 (대댓글 포함)."""
    try:
        # 최상위 댓글 조회
        result = db.table("comment_details")\
            .select("*")\
            .eq("solution_id", str(solution_id))\
            .is_("parent_id", "null")\
            .order("created_at")\
            .execute()

        # 현재 사용자의 투표
        user_votes = {}
        if current_user:
            all_comment_ids = [c["id"] for c in (result.data or [])]
            if all_comment_ids:
                votes_result = db.table("comment_votes")\
                    .select("comment_id, vote_type")\
                    .eq("user_id", current_user["id"])\
                    .in_("comment_id", all_comment_ids)\
                    .execute()
                user_votes = {v["comment_id"]: v["vote_type"] for v in (votes_result.data or [])}

        items = []
        for c in (result.data or []):
            # 대댓글 조회
            replies_result = db.table("comment_details")\
                .select("*")\
                .eq("parent_id", c["id"])\
                .order("created_at")\
                .execute()

            replies = []
            for r in (replies_result.data or []):
                replies.append(CommentItem(
                    id=r["id"],
                    solution_id=r["solution_id"],
                    user_id=r.get("user_id"),
                    parent_id=r.get("parent_id"),
                    content=r["content"] if not r.get("is_deleted") else "[삭제된 댓글입니다]",
                    upvotes=r.get("upvotes", 0),
                    downvotes=r.get("downvotes", 0),
                    is_deleted=r.get("is_deleted", False),
                    reply_count=0,
                    created_at=r["created_at"],
                    updated_at=r["updated_at"],
                    author_name=r.get("author_name"),
                    author_avatar=r.get("author_avatar"),
                    my_vote=user_votes.get(r["id"]),
                ))

            items.append(CommentItem(
                id=c["id"],
                solution_id=c["solution_id"],
                user_id=c.get("user_id"),
                parent_id=c.get("parent_id"),
                content=c["content"] if not c.get("is_deleted") else "[삭제된 댓글입니다]",
                upvotes=c.get("upvotes", 0),
                downvotes=c.get("downvotes", 0),
                is_deleted=c.get("is_deleted", False),
                reply_count=c.get("reply_count", 0),
                created_at=c["created_at"],
                updated_at=c["updated_at"],
                author_name=c.get("author_name"),
                author_avatar=c.get("author_avatar"),
                my_vote=user_votes.get(c["id"]),
                replies=replies,
            ))

        return CommentListResponse(
            items=items,
            total=len(items),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list comments: {str(e)}"
        )


@router.post("/{solution_id}/comments", response_model=CommentItem, status_code=status.HTTP_201_CREATED)
async def create_comment(
    solution_id: UUID,
    request: CommentCreate,
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    """댓글 작성."""
    try:
        # 풀이 존재 확인
        solution_result = db.table("problem_solutions")\
            .select("id")\
            .eq("id", str(solution_id))\
            .single()\
            .execute()

        if not solution_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Solution not found"
            )

        # 대댓글인 경우 부모 확인
        if request.parent_id:
            parent_result = db.table("solution_comments")\
                .select("id, solution_id")\
                .eq("id", str(request.parent_id))\
                .single()\
                .execute()

            if not parent_result.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Parent comment not found"
                )

            if parent_result.data["solution_id"] != str(solution_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Parent comment does not belong to this solution"
                )

        # 댓글 생성
        insert_data = {
            "solution_id": str(solution_id),
            "user_id": current_user["id"],
            "content": request.content,
            "parent_id": str(request.parent_id) if request.parent_id else None,
        }

        result = db.table("solution_comments")\
            .insert(insert_data)\
            .execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create comment"
            )

        c = result.data[0]

        return CommentItem(
            id=c["id"],
            solution_id=c["solution_id"],
            user_id=c["user_id"],
            parent_id=c.get("parent_id"),
            content=c["content"],
            upvotes=0,
            downvotes=0,
            is_deleted=False,
            reply_count=0,
            created_at=c["created_at"],
            updated_at=c["updated_at"],
            author_name=current_user.get("name"),
            author_avatar=current_user.get("avatar_url"),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create comment: {str(e)}"
        )


# =====================================================
# 댓글 수정/삭제/투표 (별도 경로)
# =====================================================

@router.put("/comments/{comment_id}", response_model=CommentItem)
async def update_comment(
    comment_id: UUID,
    request: CommentUpdate,
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    """댓글 수정 (본인만 가능)."""
    try:
        # 댓글 조회 및 권한 확인
        result = db.table("solution_comments")\
            .select("*")\
            .eq("id", str(comment_id))\
            .single()\
            .execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found"
            )

        if result.data["user_id"] != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this comment"
            )

        # 업데이트
        db.table("solution_comments")\
            .update({"content": request.content})\
            .eq("id", str(comment_id))\
            .execute()

        # 업데이트된 데이터 반환
        updated = db.table("comment_details")\
            .select("*")\
            .eq("id", str(comment_id))\
            .single()\
            .execute()

        c = updated.data

        return CommentItem(
            id=c["id"],
            solution_id=c["solution_id"],
            user_id=c.get("user_id"),
            parent_id=c.get("parent_id"),
            content=c["content"],
            upvotes=c.get("upvotes", 0),
            downvotes=c.get("downvotes", 0),
            is_deleted=c.get("is_deleted", False),
            reply_count=c.get("reply_count", 0),
            created_at=c["created_at"],
            updated_at=c["updated_at"],
            author_name=c.get("author_name"),
            author_avatar=c.get("author_avatar"),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update comment: {str(e)}"
        )


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: UUID,
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    """댓글 삭제 (본인만 가능) - 소프트 삭제."""
    try:
        # 댓글 조회 및 권한 확인
        result = db.table("solution_comments")\
            .select("user_id, parent_id")\
            .eq("id", str(comment_id))\
            .single()\
            .execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found"
            )

        if result.data["user_id"] != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this comment"
            )

        # 대댓글이 있는지 확인
        replies = db.table("solution_comments")\
            .select("id", count="exact")\
            .eq("parent_id", str(comment_id))\
            .execute()

        if replies.count and replies.count > 0:
            # 대댓글이 있으면 소프트 삭제
            db.table("solution_comments")\
                .update({"is_deleted": True, "content": "[삭제된 댓글입니다]"})\
                .eq("id", str(comment_id))\
                .execute()
        else:
            # 대댓글이 없으면 하드 삭제
            db.table("solution_comments")\
                .delete()\
                .eq("id", str(comment_id))\
                .execute()

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete comment: {str(e)}"
        )


@router.post("/comments/{comment_id}/vote", response_model=VoteResponse)
async def vote_comment(
    comment_id: UUID,
    request: VoteRequest,
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    """댓글 투표 (up/down)."""
    try:
        # 기존 투표 확인
        existing = db.table("comment_votes")\
            .select("id, vote_type")\
            .eq("comment_id", str(comment_id))\
            .eq("user_id", current_user["id"])\
            .execute()

        if existing.data:
            # 같은 투표면 취소
            if existing.data[0]["vote_type"] == request.vote_type.value:
                db.table("comment_votes")\
                    .delete()\
                    .eq("id", existing.data[0]["id"])\
                    .execute()
                my_vote = None
            else:
                # 다른 투표면 변경
                db.table("comment_votes")\
                    .update({"vote_type": request.vote_type.value})\
                    .eq("id", existing.data[0]["id"])\
                    .execute()
                my_vote = request.vote_type.value
        else:
            # 새 투표
            db.table("comment_votes")\
                .insert({
                    "comment_id": str(comment_id),
                    "user_id": current_user["id"],
                    "vote_type": request.vote_type.value,
                })\
                .execute()
            my_vote = request.vote_type.value

        # 업데이트된 투표 수 조회
        comment = db.table("solution_comments")\
            .select("upvotes, downvotes")\
            .eq("id", str(comment_id))\
            .single()\
            .execute()

        return VoteResponse(
            success=True,
            upvotes=comment.data.get("upvotes", 0),
            downvotes=comment.data.get("downvotes", 0),
            my_vote=my_vote,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to vote: {str(e)}"
        )
