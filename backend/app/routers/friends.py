"""
Friends Router - 친구 시스템

엔드포인트:
- GET /friends - 친구 목록
- GET /friends/requests - 받은 친구 요청
- GET /friends/requests/sent - 보낸 친구 요청
- GET /friends/counts - 미확인 알림 수
- POST /friends/request/{user_id} - 친구 요청 보내기
- POST /friends/{friendship_id}/accept - 요청 수락
- DELETE /friends/{friendship_id} - 요청 거부 또는 친구 삭제
- POST /friends/{user_id}/block - 차단
- DELETE /friends/{user_id}/block - 차단 해제
- GET /users/search - 유저 검색
- GET /messages/{user_id} - 대화 내역
- POST /messages/{user_id} - 메시지 전송
- PUT /messages/{user_id}/read - 읽음 처리
- DELETE /messages/{message_id} - 메시지 삭제
"""

from fastapi import APIRouter, HTTPException, Depends, Query, status
from typing import Optional
from uuid import UUID
from datetime import datetime

from ..database import get_db
from ..dependencies import get_current_user
from ..models.friend import (
    FriendRequest,
    Friend,
    FriendListResponse,
    FriendRequestsResponse,
    SentRequest,
    SentRequestsResponse,
    MessageCreate,
    Message,
    ConversationResponse,
    UserSearchResult,
    UserSearchResponse,
    UnreadCountResponse,
)

router = APIRouter()


# =====================================================
# 친구 목록 및 요청
# =====================================================

@router.get("", response_model=FriendListResponse)
async def list_friends(
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    """친구 목록 조회."""
    try:
        user_id = current_user["id"]

        # accepted 상태이고 차단되지 않은 친구 관계 조회
        result = db.table("friendship_details")\
            .select("*")\
            .eq("status", "accepted")\
            .is_("blocked_at", "null")\
            .or_(f"requester_id.eq.{user_id},addressee_id.eq.{user_id}")\
            .order("updated_at", desc=True)\
            .execute()

        friends = []
        for f in (result.data or []):
            # 상대방 정보 추출
            if f["requester_id"] == user_id:
                friend_id = f["addressee_id"]
                friend_name = f["addressee_name"]
                friend_avatar = f["addressee_avatar"]
            else:
                friend_id = f["requester_id"]
                friend_name = f["requester_name"]
                friend_avatar = f["requester_avatar"]

            # 안 읽은 메시지 수 조회
            unread_result = db.table("direct_messages")\
                .select("id", count="exact")\
                .eq("sender_id", friend_id)\
                .eq("receiver_id", user_id)\
                .eq("is_read", False)\
                .eq("deleted_by_receiver", False)\
                .execute()
            unread_count = unread_result.count if unread_result.count else 0

            # 마지막 메시지 조회
            last_msg_result = db.table("direct_messages")\
                .select("content, sender_id, created_at")\
                .or_(
                    f"and(sender_id.eq.{friend_id},receiver_id.eq.{user_id},deleted_by_receiver.eq.false),"
                    f"and(sender_id.eq.{user_id},receiver_id.eq.{friend_id},deleted_by_sender.eq.false)"
                )\
                .order("created_at", desc=True)\
                .limit(1)\
                .execute()

            last_message = None
            last_message_at = None
            last_message_is_mine = None
            if last_msg_result.data:
                lm = last_msg_result.data[0]
                last_message = lm["content"][:50]  # 최대 50자
                last_message_at = lm["created_at"]
                last_message_is_mine = lm["sender_id"] == user_id

            friends.append(Friend(
                user_id=friend_id,
                name=friend_name,
                avatar_url=friend_avatar,
                friendship_id=f["id"],
                since=f["updated_at"],
                is_blocked=False,
                unread_count=unread_count,
                last_message=last_message,
                last_message_at=last_message_at,
                last_message_is_mine=last_message_is_mine,
            ))

        return FriendListResponse(
            friends=friends,
            total=len(friends),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list friends: {str(e)}"
        )


@router.get("/requests", response_model=FriendRequestsResponse)
async def list_friend_requests(
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    """받은 친구 요청 목록."""
    try:
        user_id = current_user["id"]

        result = db.table("friendship_details")\
            .select("*")\
            .eq("addressee_id", user_id)\
            .eq("status", "pending")\
            .is_("blocked_at", "null")\
            .order("created_at", desc=True)\
            .execute()

        requests = []
        for f in (result.data or []):
            requests.append(FriendRequest(
                id=f["id"],
                requester_id=f["requester_id"],
                requester_name=f["requester_name"],
                requester_avatar=f["requester_avatar"],
                created_at=f["created_at"],
            ))

        return FriendRequestsResponse(
            requests=requests,
            total=len(requests),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list friend requests: {str(e)}"
        )


@router.get("/requests/sent", response_model=SentRequestsResponse)
async def list_sent_requests(
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    """보낸 친구 요청 목록."""
    try:
        user_id = current_user["id"]

        result = db.table("friendship_details")\
            .select("*")\
            .eq("requester_id", user_id)\
            .eq("status", "pending")\
            .order("created_at", desc=True)\
            .execute()

        requests = []
        for f in (result.data or []):
            requests.append(SentRequest(
                id=f["id"],
                addressee_id=f["addressee_id"],
                addressee_name=f["addressee_name"],
                addressee_avatar=f["addressee_avatar"],
                created_at=f["created_at"],
            ))

        return SentRequestsResponse(
            requests=requests,
            total=len(requests),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list sent requests: {str(e)}"
        )


@router.get("/counts", response_model=UnreadCountResponse)
async def get_unread_counts(
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    """미확인 알림 수 조회 (요청 + 안읽은 메시지)."""
    try:
        user_id = current_user["id"]

        # 대기중인 요청 수
        pending_result = db.table("friendships")\
            .select("id", count="exact")\
            .eq("addressee_id", user_id)\
            .eq("status", "pending")\
            .is_("blocked_at", "null")\
            .execute()
        pending_count = pending_result.count if pending_result.count else 0

        # 안 읽은 메시지 수
        unread_result = db.table("direct_messages")\
            .select("id", count="exact")\
            .eq("receiver_id", user_id)\
            .eq("is_read", False)\
            .eq("deleted_by_receiver", False)\
            .execute()
        unread_count = unread_result.count if unread_result.count else 0

        return UnreadCountResponse(
            pending_requests=pending_count,
            unread_messages=unread_count,
            total=pending_count + unread_count,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get unread counts: {str(e)}"
        )


# =====================================================
# 친구 요청/수락/거부/삭제
# =====================================================

@router.post("/request/{user_id}", status_code=status.HTTP_201_CREATED)
async def send_friend_request(
    user_id: UUID,
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    """친구 요청 보내기."""
    try:
        my_id = current_user["id"]

        # 자기 자신 확인
        if str(user_id) == my_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot send friend request to yourself"
            )

        # 대상 유저 존재 확인
        target_user = db.table("users")\
            .select("id")\
            .eq("id", str(user_id))\
            .single()\
            .execute()

        if not target_user.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # 이미 관계가 있는지 확인 (양방향)
        existing = db.table("friendships")\
            .select("id, status, blocked_at, requester_id")\
            .or_(
                f"and(requester_id.eq.{my_id},addressee_id.eq.{user_id}),"
                f"and(requester_id.eq.{user_id},addressee_id.eq.{my_id})"
            )\
            .execute()

        if existing.data:
            rel = existing.data[0]

            # 차단된 경우
            if rel.get("blocked_at"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot send friend request"
                )

            # 이미 친구인 경우
            if rel["status"] == "accepted":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Already friends"
                )

            # 이미 요청 중인 경우
            if rel["status"] == "pending":
                # 상대방이 보낸 요청이면 자동 수락
                if rel["requester_id"] == str(user_id):
                    db.table("friendships")\
                        .update({"status": "accepted"})\
                        .eq("id", rel["id"])\
                        .execute()
                    return {"message": "Friend request accepted", "status": "accepted"}
                else:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Friend request already sent"
                    )

        # 새 친구 요청 생성
        result = db.table("friendships")\
            .insert({
                "requester_id": my_id,
                "addressee_id": str(user_id),
                "status": "pending",
            })\
            .execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send friend request"
            )

        return {"message": "Friend request sent", "status": "pending"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send friend request: {str(e)}"
        )


@router.post("/{friendship_id}/accept")
async def accept_friend_request(
    friendship_id: UUID,
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    """친구 요청 수락."""
    try:
        user_id = current_user["id"]

        # 요청 확인 (내가 받은 요청인지)
        result = db.table("friendships")\
            .select("*")\
            .eq("id", str(friendship_id))\
            .eq("addressee_id", user_id)\
            .eq("status", "pending")\
            .single()\
            .execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Friend request not found"
            )

        # 수락
        db.table("friendships")\
            .update({"status": "accepted"})\
            .eq("id", str(friendship_id))\
            .execute()

        return {"message": "Friend request accepted"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to accept friend request: {str(e)}"
        )


@router.delete("/{friendship_id}")
async def delete_friendship(
    friendship_id: UUID,
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    """친구 요청 거부 또는 친구 삭제."""
    try:
        user_id = current_user["id"]

        # 관계 확인 (내가 관련된 관계인지)
        result = db.table("friendships")\
            .select("*")\
            .eq("id", str(friendship_id))\
            .or_(f"requester_id.eq.{user_id},addressee_id.eq.{user_id}")\
            .single()\
            .execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Friendship not found"
            )

        # 삭제
        db.table("friendships")\
            .delete()\
            .eq("id", str(friendship_id))\
            .execute()

        return {"message": "Friendship deleted"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete friendship: {str(e)}"
        )


# =====================================================
# 차단
# =====================================================

@router.post("/{user_id}/block")
async def block_user(
    user_id: UUID,
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    """유저 차단."""
    try:
        my_id = current_user["id"]

        # 기존 관계 확인
        existing = db.table("friendships")\
            .select("id, requester_id")\
            .or_(
                f"and(requester_id.eq.{my_id},addressee_id.eq.{user_id}),"
                f"and(requester_id.eq.{user_id},addressee_id.eq.{my_id})"
            )\
            .execute()

        if existing.data:
            # 기존 관계가 있으면 차단 처리
            db.table("friendships")\
                .update({"blocked_at": datetime.utcnow().isoformat()})\
                .eq("id", existing.data[0]["id"])\
                .execute()
        else:
            # 없으면 새로 생성
            db.table("friendships")\
                .insert({
                    "requester_id": my_id,
                    "addressee_id": str(user_id),
                    "status": "pending",
                    "blocked_at": datetime.utcnow().isoformat(),
                })\
                .execute()

        return {"message": "User blocked"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to block user: {str(e)}"
        )


@router.delete("/{user_id}/block")
async def unblock_user(
    user_id: UUID,
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    """유저 차단 해제."""
    try:
        my_id = current_user["id"]

        # 관계 삭제 (차단 해제 시 관계 자체를 삭제)
        db.table("friendships")\
            .delete()\
            .or_(
                f"and(requester_id.eq.{my_id},addressee_id.eq.{user_id}),"
                f"and(requester_id.eq.{user_id},addressee_id.eq.{my_id})"
            )\
            .not_.is_("blocked_at", "null")\
            .execute()

        return {"message": "User unblocked"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to unblock user: {str(e)}"
        )


# =====================================================
# 유저 검색
# =====================================================

@router.get("/search", response_model=UserSearchResponse)
async def search_users(
    q: str = Query(..., min_length=2, max_length=50),
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    """유저 검색 (이름으로 부분 일치)."""
    try:
        my_id = current_user["id"]

        # 유저 검색 (자신 제외)
        result = db.table("users")\
            .select("id, name, avatar_url")\
            .neq("id", my_id)\
            .ilike("name", f"%{q}%")\
            .limit(20)\
            .execute()

        if not result.data:
            return UserSearchResponse(users=[], total=0)

        user_ids = [u["id"] for u in result.data]

        # 각 유저와의 관계 조회
        friendships = db.table("friendships")\
            .select("requester_id, addressee_id, status, blocked_at")\
            .or_(
                f"and(requester_id.eq.{my_id},addressee_id.in.({','.join(user_ids)})),"
                f"and(addressee_id.eq.{my_id},requester_id.in.({','.join(user_ids)}))"
            )\
            .execute()

        # 관계 맵 생성
        relation_map = {}
        for f in (friendships.data or []):
            other_id = f["addressee_id"] if f["requester_id"] == my_id else f["requester_id"]
            if f.get("blocked_at"):
                relation_map[other_id] = "blocked"
            else:
                relation_map[other_id] = f["status"]

        users = []
        for u in result.data:
            # 차단된 유저는 제외
            if relation_map.get(u["id"]) == "blocked":
                continue

            users.append(UserSearchResult(
                id=u["id"],
                name=u["name"],
                avatar_url=u["avatar_url"],
                friendship_status=relation_map.get(u["id"]),
            ))

        return UserSearchResponse(
            users=users,
            total=len(users),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search users: {str(e)}"
        )


# =====================================================
# 메시지
# =====================================================

@router.get("/messages/{user_id}", response_model=ConversationResponse)
async def get_conversation(
    user_id: UUID,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    """특정 친구와의 대화 내역 조회."""
    try:
        my_id = current_user["id"]

        # 친구 관계 확인
        friendship = db.table("friendship_details")\
            .select("*")\
            .eq("status", "accepted")\
            .is_("blocked_at", "null")\
            .or_(
                f"and(requester_id.eq.{my_id},addressee_id.eq.{user_id}),"
                f"and(requester_id.eq.{user_id},addressee_id.eq.{my_id})"
            )\
            .single()\
            .execute()

        if not friendship.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Friend not found"
            )

        f = friendship.data

        # 친구 정보
        if f["requester_id"] == my_id:
            friend_id = f["addressee_id"]
            friend_name = f["addressee_name"]
            friend_avatar = f["addressee_avatar"]
        else:
            friend_id = f["requester_id"]
            friend_name = f["requester_name"]
            friend_avatar = f["requester_avatar"]

        friend = Friend(
            user_id=friend_id,
            name=friend_name,
            avatar_url=friend_avatar,
            friendship_id=f["id"],
            since=f["updated_at"],
            is_blocked=False,
            unread_count=0,
        )

        # 메시지 조회 (양방향)
        offset = (page - 1) * limit
        messages_result = db.table("message_details")\
            .select("*")\
            .or_(
                f"and(sender_id.eq.{my_id},receiver_id.eq.{user_id},deleted_by_sender.eq.false),"
                f"and(sender_id.eq.{user_id},receiver_id.eq.{my_id},deleted_by_receiver.eq.false)"
            )\
            .order("created_at", desc=True)\
            .range(offset, offset + limit)\
            .execute()

        # 총 개수
        count_result = db.table("direct_messages")\
            .select("id", count="exact")\
            .or_(
                f"and(sender_id.eq.{my_id},receiver_id.eq.{user_id},deleted_by_sender.eq.false),"
                f"and(sender_id.eq.{user_id},receiver_id.eq.{my_id},deleted_by_receiver.eq.false)"
            )\
            .execute()
        total = count_result.count if count_result.count else 0

        messages = []
        for m in reversed(messages_result.data or []):  # 시간순 정렬
            messages.append(Message(
                id=m["id"],
                sender_id=m["sender_id"],
                sender_name=m["sender_name"],
                sender_avatar=m["sender_avatar"],
                content=m["content"],
                is_read=m["is_read"],
                is_mine=m["sender_id"] == my_id,
                created_at=m["created_at"],
            ))

        has_more = (page * limit) < total

        return ConversationResponse(
            messages=messages,
            friend=friend,
            has_more=has_more,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get conversation: {str(e)}"
        )


@router.post("/messages/{user_id}", response_model=Message, status_code=status.HTTP_201_CREATED)
async def send_message(
    user_id: UUID,
    request: MessageCreate,
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    """메시지 전송."""
    try:
        my_id = current_user["id"]

        # 친구 관계 확인
        friendship = db.table("friendships")\
            .select("id, blocked_at")\
            .eq("status", "accepted")\
            .or_(
                f"and(requester_id.eq.{my_id},addressee_id.eq.{user_id}),"
                f"and(requester_id.eq.{user_id},addressee_id.eq.{my_id})"
            )\
            .single()\
            .execute()

        if not friendship.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Friend not found"
            )

        if friendship.data.get("blocked_at"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot send message to blocked user"
            )

        # 메시지 저장
        result = db.table("direct_messages")\
            .insert({
                "sender_id": my_id,
                "receiver_id": str(user_id),
                "content": request.content,
            })\
            .execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send message"
            )

        m = result.data[0]

        return Message(
            id=m["id"],
            sender_id=m["sender_id"],
            sender_name=current_user.get("name"),
            sender_avatar=current_user.get("avatar_url"),
            content=m["content"],
            is_read=False,
            is_mine=True,
            created_at=m["created_at"],
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send message: {str(e)}"
        )


@router.put("/messages/{user_id}/read")
async def mark_messages_read(
    user_id: UUID,
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    """대화 메시지 읽음 처리."""
    try:
        my_id = current_user["id"]

        # 해당 유저가 보낸 메시지를 읽음 처리
        db.table("direct_messages")\
            .update({"is_read": True})\
            .eq("sender_id", str(user_id))\
            .eq("receiver_id", my_id)\
            .eq("is_read", False)\
            .execute()

        return {"message": "Messages marked as read"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark messages as read: {str(e)}"
        )


@router.delete("/messages/{message_id}")
async def delete_message(
    message_id: UUID,
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    """메시지 삭제 (soft delete)."""
    try:
        my_id = current_user["id"]

        # 메시지 조회
        result = db.table("direct_messages")\
            .select("sender_id, receiver_id")\
            .eq("id", str(message_id))\
            .single()\
            .execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found"
            )

        m = result.data

        # 내가 발신자인지 수신자인지에 따라 다른 필드 업데이트
        if m["sender_id"] == my_id:
            db.table("direct_messages")\
                .update({"deleted_by_sender": True})\
                .eq("id", str(message_id))\
                .execute()
        elif m["receiver_id"] == my_id:
            db.table("direct_messages")\
                .update({"deleted_by_receiver": True})\
                .eq("id", str(message_id))\
                .execute()
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this message"
            )

        return {"message": "Message deleted"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete message: {str(e)}"
        )
