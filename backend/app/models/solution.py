from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from enum import Enum


class VoteType(str, Enum):
    UP = "up"
    DOWN = "down"


# =====================================================
# Solution Models
# =====================================================

class SolutionCreate(BaseModel):
    """풀이 작성 요청."""
    base_problem_id: UUID
    language: str = Field(..., max_length=20)
    code: str
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None


class SolutionUpdate(BaseModel):
    """풀이 수정 요청."""
    code: Optional[str] = None
    language: Optional[str] = Field(None, max_length=20)
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None


class SolutionAuthor(BaseModel):
    """풀이 작성자 정보."""
    id: UUID
    name: Optional[str] = None
    avatar_url: Optional[str] = None


class SolutionListItem(BaseModel):
    """풀이 목록 아이템."""
    id: UUID
    user_id: UUID
    language: str
    code: str  # 코드도 목록에서 바로 표시
    title: Optional[str] = None
    upvotes: int = 0
    downvotes: int = 0
    comment_count: int = 0
    created_at: datetime
    author_name: Optional[str] = None
    author_avatar: Optional[str] = None


class SolutionDetail(BaseModel):
    """풀이 상세 정보."""
    id: UUID
    base_problem_id: UUID
    user_id: UUID
    language: str
    code: str
    title: Optional[str] = None
    description: Optional[str] = None
    is_correct: bool = True
    upvotes: int = 0
    downvotes: int = 0
    view_count: int = 0
    comment_count: int = 0
    created_at: datetime
    updated_at: datetime
    author_name: Optional[str] = None
    author_avatar: Optional[str] = None
    problem_original_id: Optional[str] = None
    problem_name: Optional[str] = None
    my_vote: Optional[str] = None  # 'up', 'down', or None


class SolutionListResponse(BaseModel):
    """풀이 목록 응답."""
    items: List[SolutionListItem]
    total: int
    page: int
    limit: int
    has_more: bool


# =====================================================
# Comment Models
# =====================================================

class CommentCreate(BaseModel):
    """댓글 작성 요청."""
    content: str = Field(..., min_length=1)
    parent_id: Optional[UUID] = None  # 대댓글인 경우


class CommentUpdate(BaseModel):
    """댓글 수정 요청."""
    content: str = Field(..., min_length=1)


class CommentAuthor(BaseModel):
    """댓글 작성자 정보."""
    id: UUID
    name: Optional[str] = None
    avatar_url: Optional[str] = None


class CommentItem(BaseModel):
    """댓글 아이템."""
    id: UUID
    solution_id: UUID
    user_id: Optional[UUID] = None
    parent_id: Optional[UUID] = None
    content: str
    upvotes: int = 0
    downvotes: int = 0
    is_deleted: bool = False
    reply_count: int = 0
    created_at: datetime
    updated_at: datetime
    author_name: Optional[str] = None
    author_avatar: Optional[str] = None
    my_vote: Optional[str] = None  # 'up', 'down', or None
    replies: Optional[List["CommentItem"]] = None  # 대댓글 목록


class CommentListResponse(BaseModel):
    """댓글 목록 응답."""
    items: List[CommentItem]
    total: int


# =====================================================
# Vote Models
# =====================================================

class VoteRequest(BaseModel):
    """투표 요청."""
    vote_type: VoteType


class VoteResponse(BaseModel):
    """투표 응답."""
    success: bool
    upvotes: int
    downvotes: int
    my_vote: Optional[str] = None


# =====================================================
# Problem Discussion Page Models
# =====================================================

class ProblemDiscussionResponse(BaseModel):
    """문제 게시글 페이지 응답."""
    problem: dict  # base_problems 정보
    official_solutions: List[dict]  # 공식 정답 코드
    user_solutions: SolutionListResponse  # 사용자 풀이 목록
