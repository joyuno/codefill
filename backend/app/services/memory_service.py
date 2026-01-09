"""
Memory Service - 세션 메모리 생성 및 관리

user_memories 테이블에 세션 요약을 저장하여
다음 세션에서 개인화된 학습 경험을 제공합니다.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class MemoryService:
    """사용자 세션 메모리 관리 서비스"""

    def __init__(self):
        from ..database import get_supabase_client
        self.supabase = get_supabase_client()

    async def create_problem_session_memory(
        self,
        user_id: str,
        session_id: str,
        problem_id: str,
        problem_name: str,
        problem_type: str,
        difficulty: str,
        topics: List[str],
        was_successful: bool,
        hints_used: int = 0,
        time_spent: int = 0,
        attempt_count: int = 1,
        attempt_id: Optional[str] = None,  # attempt 참조 (추가)
    ) -> Optional[str]:
        """
        문제 풀이 세션 메모리 생성

        Args:
            user_id: 사용자 UUID
            session_id: 세션 ID
            problem_id: 문제 ID
            problem_name: 문제 이름
            problem_type: 문제 유형 (blank, puzzle, guided)
            difficulty: 난이도
            topics: 문제 토픽들
            was_successful: 성공 여부
            hints_used: 힌트 사용 횟수
            time_spent: 풀이 시간 (초)
            attempt_count: 시도 횟수
            attempt_id: 시도 ID (attempts 테이블 참조)

        Returns:
            생성된 메모리 ID 또는 None
        """
        try:
            # 요약 생성 (LLM 없이 템플릿 기반)
            summary = self._generate_problem_summary(
                problem_name=problem_name,
                problem_type=problem_type,
                difficulty=difficulty,
                was_successful=was_successful,
                hints_used=hints_used,
                time_spent=time_spent,
            )

            # 학습 인사이트 분석
            concepts_learned = []
            concepts_struggling = []
            teaching_notes = []

            if was_successful:
                concepts_learned = topics[:5] if topics else []
                if hints_used == 0:
                    teaching_notes.append("힌트 없이 스스로 해결함")
                elif hints_used <= 2:
                    teaching_notes.append("약간의 힌트로 해결 가능")
            else:
                concepts_struggling = topics[:5] if topics else []
                if hints_used >= 3:
                    teaching_notes.append("이 주제 추가 설명 필요")
                teaching_notes.append(f"난이도 {difficulty}에서 어려움")

            # 학생 상태 추정
            student_mood = "confident" if was_successful and hints_used == 0 else \
                          "curious" if was_successful else \
                          "frustrated" if hints_used >= 3 else "neutral"

            # 메모리 데이터
            memory_data = {
                "user_id": user_id,
                "session_id": session_id,
                "session_type": "problem_solving",
                "summary": summary,
                "key_topics": topics[:10] if topics else [],
                "key_concepts": topics[:5] if topics else [],
                "concepts_learned": concepts_learned,
                "concepts_struggling": concepts_struggling,
                "teaching_notes": teaching_notes,
                # 비정규화 필드 (빠른 조회용)
                # problem_id는 삭제됨 - attempt_id를 통해 조회
                "problem_name": problem_name,
                "problem_type": problem_type,
                "problem_difficulty": difficulty,
                "was_successful": was_successful,
                "hints_needed": hints_used,
                "time_spent_seconds": time_spent,
                "attempt_count": attempt_count,
                "student_mood": student_mood,
                "conversation_tone": "encouraging" if was_successful else "supportive",
                # 추가 필드
                "duration_seconds": time_spent,  # time_spent와 동일
            }

            # attempt_id 추가 (FK 참조) - 필수 필드
            if attempt_id:
                memory_data["attempt_id"] = attempt_id
                logger.info(f"[MemoryService] Including attempt_id: {attempt_id[:8]}...")
            else:
                logger.warning(f"[MemoryService] No attempt_id provided - memory will not have attempt reference")

            # DB 저장
            result = self.supabase.table("user_memories").insert(memory_data).execute()

            if result.data and len(result.data) > 0:
                memory_id = result.data[0]["id"]
                logger.info(f"[MemoryService] Created memory: {memory_id} for user {user_id[:8]}...")
                return memory_id

            return None

        except Exception as e:
            logger.error(f"[MemoryService] Error creating memory: {e}")
            return None

    def _generate_problem_summary(
        self,
        problem_name: str,
        problem_type: str,
        difficulty: str,
        was_successful: bool,
        hints_used: int,
        time_spent: int,
    ) -> str:
        """문제 풀이 요약 생성"""
        type_names = {
            "blank": "빈칸 채우기",
            "puzzle": "퍼즐(Parsons)",
            "guided": "가이드",
        }
        type_name = type_names.get(problem_type, problem_type)

        if was_successful:
            if hints_used == 0:
                return f"'{problem_name}' {type_name} 문제({difficulty})를 힌트 없이 {time_spent}초 만에 해결했습니다. 이 주제를 잘 이해하고 있습니다."
            else:
                return f"'{problem_name}' {type_name} 문제({difficulty})를 {hints_used}개 힌트와 함께 해결했습니다. 약간의 도움이 필요했지만 성공적으로 완료했습니다."
        else:
            return f"'{problem_name}' {type_name} 문제({difficulty})에서 어려움을 겪었습니다. {hints_used}개 힌트를 사용했지만 완료하지 못했습니다. 이 주제 추가 학습이 필요합니다."

    async def get_recent_memories(
        self,
        user_id: str,
        limit: int = 10,
        session_type: str = None,
    ) -> List[Dict[str, Any]]:
        """
        최근 세션 메모리 조회

        Args:
            user_id: 사용자 UUID
            limit: 조회 개수
            session_type: 세션 유형 필터 (optional)

        Returns:
            메모리 목록
        """
        try:
            query = self.supabase.table("user_memories") \
                .select("*") \
                .eq("user_id", user_id) \
                .order("created_at", desc=True) \
                .limit(limit)

            if session_type:
                query = query.eq("session_type", session_type)

            result = query.execute()
            return result.data if result.data else []

        except Exception as e:
            logger.error(f"[MemoryService] Error getting memories: {e}")
            return []

    async def get_struggling_topics(self, user_id: str, days: int = 30) -> List[str]:
        """
        사용자가 어려워하는 주제 목록 조회

        Args:
            user_id: 사용자 UUID
            days: 최근 N일

        Returns:
            어려운 주제 목록
        """
        try:
            result = self.supabase.table("user_memories") \
                .select("concepts_struggling") \
                .eq("user_id", user_id) \
                .not_.is_("concepts_struggling", "null") \
                .order("created_at", desc=True) \
                .limit(50) \
                .execute()

            if not result.data:
                return []

            # 어려운 주제 빈도 집계
            topic_count = {}
            for memory in result.data:
                for topic in (memory.get("concepts_struggling") or []):
                    topic_count[topic] = topic_count.get(topic, 0) + 1

            # 빈도순 정렬
            sorted_topics = sorted(topic_count.items(), key=lambda x: x[1], reverse=True)
            return [topic for topic, _ in sorted_topics[:10]]

        except Exception as e:
            logger.error(f"[MemoryService] Error getting struggling topics: {e}")
            return []

    async def get_learning_summary(self, user_id: str) -> Dict[str, Any]:
        """
        사용자 학습 요약 조회

        Returns:
            {
                "total_sessions": int,
                "success_rate": float,
                "strong_topics": list,
                "weak_topics": list,
                "recent_activity": list,
            }
        """
        try:
            # 최근 메모리 조회
            memories = await self.get_recent_memories(user_id, limit=100)

            if not memories:
                return {
                    "total_sessions": 0,
                    "success_rate": 0.0,
                    "strong_topics": [],
                    "weak_topics": [],
                    "recent_activity": [],
                }

            # 통계 계산
            total = len(memories)
            successful = sum(1 for m in memories if m.get("was_successful"))
            success_rate = successful / total if total > 0 else 0.0

            # 토픽 분석
            learned_topics = {}
            struggling_topics = {}

            for memory in memories:
                for topic in (memory.get("concepts_learned") or []):
                    learned_topics[topic] = learned_topics.get(topic, 0) + 1
                for topic in (memory.get("concepts_struggling") or []):
                    struggling_topics[topic] = struggling_topics.get(topic, 0) + 1

            strong_topics = sorted(learned_topics.items(), key=lambda x: x[1], reverse=True)[:5]
            weak_topics = sorted(struggling_topics.items(), key=lambda x: x[1], reverse=True)[:5]

            return {
                "total_sessions": total,
                "success_rate": round(success_rate, 2),
                "strong_topics": [t for t, _ in strong_topics],
                "weak_topics": [t for t, _ in weak_topics],
                "recent_activity": memories[:5],
            }

        except Exception as e:
            logger.error(f"[MemoryService] Error getting learning summary: {e}")
            return {}


# Singleton
_memory_service = None


def get_memory_service() -> MemoryService:
    """MemoryService 싱글톤 반환"""
    global _memory_service
    if _memory_service is None:
        _memory_service = MemoryService()
    return _memory_service
