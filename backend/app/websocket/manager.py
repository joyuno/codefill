"""
WebSocket Connection Manager
실시간 채팅을 위한 WebSocket 연결 관리
"""

from fastapi import WebSocket
from typing import Dict, List, Any
import json
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    WebSocket 연결 관리자.

    - 사용자별 연결 관리 (한 사용자가 여러 탭/기기에서 접속 가능)
    - 특정 사용자에게 메시지 전송
    - 연결/해제 이벤트 처리
    """

    def __init__(self):
        # {user_id: [websocket1, websocket2, ...]}
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        """새 WebSocket 연결 수락 및 등록."""
        await websocket.accept()

        if user_id not in self.active_connections:
            self.active_connections[user_id] = []

        self.active_connections[user_id].append(websocket)
        logger.info(f"User {user_id} connected. Total connections: {len(self.active_connections[user_id])}")

    def disconnect(self, websocket: WebSocket, user_id: str):
        """WebSocket 연결 해제."""
        if user_id in self.active_connections:
            try:
                self.active_connections[user_id].remove(websocket)
                logger.info(f"User {user_id} disconnected. Remaining connections: {len(self.active_connections[user_id])}")

                # 모든 연결이 끊어지면 사용자 제거
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]
                    logger.info(f"User {user_id} fully disconnected")
            except ValueError:
                pass  # 이미 제거됨

    def is_online(self, user_id: str) -> bool:
        """사용자가 온라인인지 확인."""
        return user_id in self.active_connections and len(self.active_connections[user_id]) > 0

    async def send_personal_message(self, user_id: str, message: dict):
        """
        특정 사용자에게 메시지 전송.
        사용자의 모든 연결(여러 탭/기기)에 전송.
        """
        if user_id not in self.active_connections:
            logger.debug(f"User {user_id} is not connected, message not sent")
            return False

        disconnected = []
        for connection in self.active_connections[user_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"Failed to send message to {user_id}: {e}")
                disconnected.append(connection)

        # 실패한 연결 정리
        for conn in disconnected:
            self.disconnect(conn, user_id)

        return True

    async def broadcast_to_users(self, user_ids: List[str], message: dict):
        """여러 사용자에게 메시지 브로드캐스트."""
        for user_id in user_ids:
            await self.send_personal_message(user_id, message)

    def get_online_users(self) -> List[str]:
        """현재 온라인인 모든 사용자 ID 목록."""
        return list(self.active_connections.keys())

    def get_connection_count(self, user_id: str) -> int:
        """특정 사용자의 연결 수."""
        return len(self.active_connections.get(user_id, []))


# 싱글톤 인스턴스
manager = ConnectionManager()
