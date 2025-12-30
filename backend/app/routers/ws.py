"""
WebSocket Router - 실시간 채팅

엔드포인트:
- WS /ws?token={jwt_token} - WebSocket 연결
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Optional
import json
import logging

from ..websocket import manager
from ..utils.security import verify_token
from ..database import get_supabase_client

router = APIRouter()
logger = logging.getLogger(__name__)


async def authenticate_websocket(token: str) -> Optional[dict]:
    """
    WebSocket 연결 시 JWT 토큰 검증.

    Returns:
        사용자 정보 dict 또는 None
    """
    if not token:
        return None

    payload = verify_token(token)
    if not payload or "sub" not in payload:
        return None

    # 사용자 정보 조회
    try:
        db = get_supabase_client()
        result = db.table("users").select("id, name, avatar_url").eq("id", payload["sub"]).single().execute()
        if result.data:
            return result.data
    except Exception as e:
        logger.error(f"Failed to get user info: {e}")

    return None


@router.websocket("")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(..., description="JWT access token")
):
    """
    WebSocket 연결 엔드포인트.

    연결 시 JWT 토큰으로 인증하고, 메시지 수신 대기.

    메시지 타입:
    - ping: 연결 유지 (pong 응답)
    - message: 채팅 메시지 전송
    - read: 메시지 읽음 처리
    """
    # 인증
    user = await authenticate_websocket(token)
    if not user:
        await websocket.close(code=4001, reason="Unauthorized")
        return

    user_id = user["id"]

    # 연결
    await manager.connect(websocket, user_id)

    try:
        # 연결 성공 알림
        await websocket.send_json({
            "type": "connected",
            "user_id": user_id,
        })

        # 메시지 수신 대기
        while True:
            try:
                data = await websocket.receive_json()
                await handle_message(user_id, user, data)
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON format"
                })

    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
        logger.info(f"WebSocket disconnected: {user_id}")
    except Exception as e:
        logger.error(f"WebSocket error for {user_id}: {e}")
        manager.disconnect(websocket, user_id)


async def handle_message(user_id: str, user: dict, data: dict):
    """
    수신된 메시지 처리.

    Args:
        user_id: 발신자 ID
        user: 발신자 정보
        data: 수신된 메시지 데이터
    """
    message_type = data.get("type")

    if message_type == "ping":
        # Ping-Pong (연결 유지)
        await manager.send_personal_message(user_id, {"type": "pong"})

    elif message_type == "message":
        # 채팅 메시지 전송
        receiver_id = data.get("receiver_id")
        content = data.get("content", "").strip()

        if not receiver_id or not content:
            await manager.send_personal_message(user_id, {
                "type": "error",
                "message": "receiver_id and content are required"
            })
            return

        # DB에 메시지 저장
        try:
            db = get_supabase_client()

            # 친구 관계 확인
            friendship = db.table("friendships")\
                .select("id, blocked_at")\
                .eq("status", "accepted")\
                .or_(
                    f"and(requester_id.eq.{user_id},addressee_id.eq.{receiver_id}),"
                    f"and(requester_id.eq.{receiver_id},addressee_id.eq.{user_id})"
                )\
                .single()\
                .execute()

            if not friendship.data or friendship.data.get("blocked_at"):
                await manager.send_personal_message(user_id, {
                    "type": "error",
                    "message": "Cannot send message to this user"
                })
                return

            # 메시지 저장
            result = db.table("direct_messages")\
                .insert({
                    "sender_id": user_id,
                    "receiver_id": receiver_id,
                    "content": content,
                })\
                .execute()

            if result.data:
                message_data = result.data[0]

                # 메시지 객체 생성
                new_message = {
                    "type": "new_message",
                    "message": {
                        "id": message_data["id"],
                        "sender_id": user_id,
                        "sender_name": user.get("name"),
                        "sender_avatar": user.get("avatar_url"),
                        "receiver_id": receiver_id,
                        "content": content,
                        "is_read": False,
                        "created_at": message_data["created_at"],
                    }
                }

                # 발신자에게 확인 전송
                await manager.send_personal_message(user_id, {
                    **new_message,
                    "message": {**new_message["message"], "is_mine": True}
                })

                # 수신자에게 전송 (온라인인 경우)
                if manager.is_online(receiver_id):
                    await manager.send_personal_message(receiver_id, {
                        **new_message,
                        "message": {**new_message["message"], "is_mine": False}
                    })

        except Exception as e:
            logger.error(f"Failed to save message: {e}")
            await manager.send_personal_message(user_id, {
                "type": "error",
                "message": "Failed to send message"
            })

    elif message_type == "read":
        # 읽음 처리
        sender_id = data.get("sender_id")

        if not sender_id:
            return

        try:
            db = get_supabase_client()

            # 해당 유저가 보낸 메시지를 읽음 처리
            db.table("direct_messages")\
                .update({"is_read": True})\
                .eq("sender_id", sender_id)\
                .eq("receiver_id", user_id)\
                .eq("is_read", False)\
                .execute()

            # 발신자에게 읽음 알림 (온라인인 경우)
            if manager.is_online(sender_id):
                await manager.send_personal_message(sender_id, {
                    "type": "messages_read",
                    "reader_id": user_id,
                })

        except Exception as e:
            logger.error(f"Failed to mark messages as read: {e}")

    else:
        await manager.send_personal_message(user_id, {
            "type": "error",
            "message": f"Unknown message type: {message_type}"
        })
