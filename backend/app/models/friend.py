"""
Friend System Models
친구 시스템 (친구 요청, 수락/거부, 1:1 메시지)
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from enum import Enum


class FriendshipStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"


# =====================================================
# Friend Models
# =====================================================

class FriendRequest(BaseModel):
    """받은 친구 요청."""
    id: UUID
    requester_id: UUID
    requester_name: Optional[str] = None
    requester_avatar: Optional[str] = None
    created_at: datetime


class Friend(BaseModel):
    """친구 정보."""
    user_id: UUID
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    friendship_id: UUID
    since: datetime  # 친구가 된 시간
    is_blocked: bool = False
    unread_count: int = 0  # 안 읽은 메시지 수
    last_message: Optional[str] = None  # 마지막 메시지 내용
    last_message_at: Optional[datetime] = None  # 마지막 메시지 시간
    last_message_is_mine: Optional[bool] = None  # 마지막 메시지가 내가 보낸 건지


class FriendListResponse(BaseModel):
    """친구 목록 응답."""
    friends: List[Friend]
    total: int


class FriendRequestsResponse(BaseModel):
    """친구 요청 목록 응답."""
    requests: List[FriendRequest]
    total: int


class SentRequest(BaseModel):
    """보낸 친구 요청."""
    id: UUID
    addressee_id: UUID
    addressee_name: Optional[str] = None
    addressee_avatar: Optional[str] = None
    created_at: datetime


class SentRequestsResponse(BaseModel):
    """보낸 요청 목록 응답."""
    requests: List[SentRequest]
    total: int


# =====================================================
# Message Models
# =====================================================

class MessageCreate(BaseModel):
    """메시지 전송 요청."""
    content: str = Field(..., min_length=1, max_length=2000)


class Message(BaseModel):
    """메시지."""
    id: UUID
    sender_id: UUID
    sender_name: Optional[str] = None
    sender_avatar: Optional[str] = None
    content: str
    is_read: bool
    is_mine: bool  # 내가 보낸 메시지인지
    created_at: datetime


class ConversationResponse(BaseModel):
    """대화 내역 응답."""
    messages: List[Message]
    friend: Friend
    has_more: bool


# =====================================================
# User Search Models
# =====================================================

class UserSearchResult(BaseModel):
    """유저 검색 결과."""
    id: UUID
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    friendship_status: Optional[str] = None  # null, pending, accepted, blocked


class UserSearchResponse(BaseModel):
    """유저 검색 응답."""
    users: List[UserSearchResult]
    total: int


# =====================================================
# Notification Count Models
# =====================================================

class UnreadCountResponse(BaseModel):
    """미확인 알림 수 응답."""
    pending_requests: int
    unread_messages: int
    total: int
