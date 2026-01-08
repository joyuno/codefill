"""
Chat Session Service
DB에 대화 히스토리를 저장하고 관리하는 서비스
"""

from typing import Optional, List, Dict, Any
from uuid import UUID
import json
import logging

logger = logging.getLogger(__name__)


class ChatSessionService:
    """채팅 세션 관리 서비스"""

    def __init__(self, db):
        self.db = db

    async def get_or_create_session(
        self,
        user_id: str,
        session_id: Optional[str] = None
    ) -> str:
        """
        세션을 가져오거나 새로 생성
        - session_id가 주어지면 해당 세션 반환
        - 없으면 30분 이내 최근 세션 반환
        - 없으면 새 세션 생성
        """
        try:
            result = self.db.rpc(
                'get_or_create_chat_session',
                {
                    'p_user_id': user_id,
                    'p_session_id': session_id
                }
            ).execute()

            if result.data:
                return str(result.data)

            # RPC 실패 시 직접 생성
            return await self._create_session_directly(user_id)

        except Exception as e:
            logger.error(f"Error in get_or_create_session: {e}")
            return await self._create_session_directly(user_id)

    async def _create_session_directly(self, user_id: str) -> str:
        """직접 세션 생성 (fallback)"""
        try:
            result = self.db.table('chat_sessions').insert({
                'user_id': user_id,
                'session_type': 'exploration'
            }).execute()

            if result.data and len(result.data) > 0:
                return result.data[0]['id']

            raise Exception("Failed to create session")
        except Exception as e:
            logger.error(f"Error creating session directly: {e}")
            raise

    async def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        message_type: str = 'text',
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """메시지 추가"""
        try:
            result = self.db.rpc(
                'add_chat_message',
                {
                    'p_session_id': session_id,
                    'p_role': role,
                    'p_content': content,
                    'p_message_type': message_type,
                    'p_metadata': json.dumps(metadata) if metadata else None
                }
            ).execute()

            if result.data:
                return str(result.data)
            return None

        except Exception as e:
            logger.error(f"Error adding message: {e}")
            return None

    async def get_history(
        self,
        session_id: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """세션의 메시지 히스토리 가져오기"""
        try:
            result = self.db.table('chat_messages').select(
                'role, content, message_type, metadata, created_at'
            ).eq(
                'session_id', session_id
            ).order(
                'sequence_number', desc=False
            ).limit(limit).execute()

            if result.data:
                return result.data
            return []

        except Exception as e:
            logger.error(f"Error getting history: {e}")
            return []

    async def get_session_state(self, session_id: str) -> Optional[Dict[str, Any]]:
        """세션 상태 가져오기"""
        try:
            result = self.db.table('chat_sessions').select(
                'current_stage, collected_info, session_state, '
                'current_problem_data, attempt_id, hints_used'
            ).eq('id', session_id).single().execute()

            if result.data:
                return result.data
            return None

        except Exception as e:
            logger.error(f"Error getting session state: {e}")
            return None

    async def update_session_state(
        self,
        session_id: str,
        stage: Optional[str] = None,
        collected_info: Optional[Dict[str, Any]] = None,
        session_state: Optional[Dict[str, Any]] = None,
        current_problem_data: Optional[Dict[str, Any]] = None,
        attempt_id: Optional[str] = None,
        hints_used: Optional[int] = None
    ) -> bool:
        """세션 상태 업데이트"""
        try:
            update_data = {'updated_at': 'now()'}

            if stage is not None:
                update_data['current_stage'] = stage
            if collected_info is not None:
                update_data['collected_info'] = collected_info
            if session_state is not None:
                update_data['session_state'] = session_state
            if current_problem_data is not None:
                update_data['current_problem_data'] = current_problem_data
            if attempt_id is not None:
                update_data['attempt_id'] = attempt_id
            if hints_used is not None:
                update_data['hints_used'] = hints_used

            self.db.table('chat_sessions').update(
                update_data
            ).eq('id', session_id).execute()

            return True

        except Exception as e:
            logger.error(f"Error updating session state: {e}")
            return False

    async def get_full_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """세션 전체 정보 가져오기 (상태 + 히스토리)"""
        try:
            # 세션 정보
            session_result = self.db.table('chat_sessions').select('*').eq(
                'id', session_id
            ).single().execute()

            if not session_result.data:
                return None

            session = session_result.data

            # 메시지 히스토리
            messages = await self.get_history(session_id, limit=50)
            session['messages'] = messages

            return session

        except Exception as e:
            logger.error(f"Error getting full session: {e}")
            return None

    async def convert_to_langchain_messages(
        self,
        session_id: str,
        limit: int = 20
    ) -> List[Dict[str, str]]:
        """DB 히스토리를 LangChain 메시지 형식으로 변환"""
        history = await self.get_history(session_id, limit)

        messages = []
        for msg in history:
            messages.append({
                'role': msg['role'],
                'content': msg['content']
            })

        return messages


def get_chat_session_service(db) -> ChatSessionService:
    """ChatSessionService 인스턴스 생성"""
    return ChatSessionService(db)
