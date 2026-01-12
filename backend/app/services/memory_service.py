"""
Memory Service - 세션 메모리 생성 및 관리

user_memories 테이블에 세션 요약을 저장하여
다음 세션에서 개인화된 학습 경험을 제공합니다.

🚀 v3: 로그 기반 분석 (LLM 미사용)
- 대화 패턴 분석으로 student_questions 추출
- 힌트/시도 패턴으로 breakthrough_moments 감지
- 비용 효율적인 규칙 기반 인사이트 생성
"""

import logging
import re
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class MemoryService:
    """사용자 세션 메모리 관리 서비스"""

    def __init__(self):
        from ..database import get_supabase_client
        self.supabase = get_supabase_client()

    def _extract_student_questions(self, chat_messages: List[Dict[str, str]]) -> List[str]:
        """
        대화 기록에서 학생 질문 추출 (규칙 기반)

        질문 패턴:
        - ? 로 끝나는 문장
        - "뭐", "어떻게", "왜", "언제", "어디" 등으로 시작하는 문장
        - "모르겠", "이해가 안", "헷갈" 포함 문장
        """
        questions = []
        question_patterns = [
            r'\?',  # 물음표
            r'^(뭐|어떻게|왜|언제|어디|무엇|어째서)',  # 의문사 시작
            r'(모르겠|이해가 안|헷갈|잘 모르|어려워)',  # 어려움 표현
            r'(맞나요|인가요|될까요|해야 하나요|어떤|어느)',  # 확인 질문
        ]

        if not chat_messages:
            return []

        for msg in chat_messages:
            if msg.get("role") != "user":
                continue
            content = msg.get("content", "").strip()
            if not content or len(content) < 5:
                continue

            # 질문 패턴 매칭
            for pattern in question_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    # 너무 긴 질문은 자르기
                    q = content[:100] + "..." if len(content) > 100 else content
                    if q not in questions:
                        questions.append(q)
                    break

        return questions[:5]  # 최대 5개

    def _detect_breakthrough_moments(
        self,
        was_successful: bool,
        hints_used: int,
        time_spent: int,
        problem_type: str,
        topics: List[str],
    ) -> List[str]:
        """
        돌파 순간 감지 (규칙 기반)

        돌파 패턴:
        - 힌트 없이 빠르게 해결 → "자력으로 해결"
        - 여러 힌트 후 성공 → "힌트를 통해 이해"
        - 첫 시도에서 성공 → "첫 시도 성공"
        """
        breakthroughs = []

        if not was_successful:
            return []

        topic_str = topics[0] if topics else "문제"

        # 힌트 없이 해결
        if hints_used == 0:
            if time_spent < 60:
                breakthroughs.append(f"{topic_str} 개념을 빠르게 파악함")
            elif time_spent < 180:
                breakthroughs.append(f"{topic_str} 문제를 스스로 해결함")
            else:
                breakthroughs.append(f"충분한 사고 후 {topic_str} 문제 해결")

        # 힌트를 통해 해결
        elif hints_used == 1:
            breakthroughs.append(f"한 번의 힌트로 {topic_str} 이해")
        elif hints_used <= 3:
            breakthroughs.append(f"힌트를 통해 {topic_str} 접근법 터득")
        else:
            breakthroughs.append(f"단계별 도움으로 {topic_str} 해결 과정 학습")

        # 문제 유형별 추가
        if problem_type == "guided":
            breakthroughs.append("1:1 대화를 통한 개념 이해")

        return breakthroughs[:3]

    def _generate_teaching_notes(
        self,
        was_successful: bool,
        hints_used: int,
        time_spent: int,
        difficulty: str,
        topics: List[str],
        problem_type: str,
    ) -> List[str]:
        """교육 노트 생성 (다음 세션 참고용)"""
        notes = []
        topic_str = ", ".join(topics[:2]) if topics else "일반"

        if was_successful:
            if hints_used == 0:
                notes.append(f"{topic_str} 이해도 높음")
                if difficulty in ["easy", "medium"]:
                    notes.append("더 어려운 난이도 도전 가능")
            elif hints_used <= 2:
                notes.append(f"{topic_str} 기본 이해 있음")
                notes.append("유사 문제로 추가 연습 권장")
            else:
                notes.append(f"{topic_str} 힌트 의존도 높음")
                notes.append("기초 개념 복습 필요")
        else:
            notes.append(f"{topic_str} 추가 학습 필요")
            if hints_used >= 3:
                notes.append("더 쉬운 문제부터 시작 권장")
            if time_spent < 60:
                notes.append("문제를 충분히 읽지 않았을 수 있음")
            notes.append(f"난이도 {difficulty}에서 어려움")

        return notes[:3]

    def _estimate_mood(
        self,
        was_successful: bool,
        hints_used: int,
        time_spent: int,
    ) -> List[str]:
        """감정 추정 (시작 → 종료)"""
        # 시작 감정
        start_mood = "neutral"

        # 종료 감정
        if was_successful:
            if hints_used == 0:
                end_mood = "confident"
            elif hints_used <= 2:
                end_mood = "satisfied"
            else:
                end_mood = "relieved"
        else:
            if hints_used >= 3:
                end_mood = "frustrated"
            else:
                end_mood = "challenged"

        return [start_mood, end_mood]

    def _generate_learning_insights(
        self,
        problem_name: str,
        problem_type: str,
        difficulty: str,
        topics: List[str],
        was_successful: bool,
        hints_used: int,
        time_spent: int,
        chat_messages: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """
        로그 기반 학습 인사이트 생성 (LLM 미사용)

        데이터 분석 전문가가 설계한 규칙 기반 분석:
        1. 대화 패턴 → student_questions
        2. 성과 패턴 → breakthrough_moments
        3. 학습 패턴 → teaching_notes, effective_approaches
        """
        topics = topics or []

        # 대화에서 질문 추출
        student_questions = self._extract_student_questions(chat_messages or [])

        # 돌파 순간 감지
        breakthrough_moments = self._detect_breakthrough_moments(
            was_successful=was_successful,
            hints_used=hints_used,
            time_spent=time_spent,
            problem_type=problem_type,
            topics=topics,
        )

        # 교육 노트 생성
        teaching_notes = self._generate_teaching_notes(
            was_successful=was_successful,
            hints_used=hints_used,
            time_spent=time_spent,
            difficulty=difficulty,
            topics=topics,
            problem_type=problem_type,
        )

        # 이해한/어려운 개념
        if was_successful:
            concepts_learned = topics[:5] if topics else ["문제 해결"]
            concepts_struggling = []
        else:
            concepts_learned = []
            concepts_struggling = topics[:3] if topics else ["문제 접근"]

        # 효과적 접근법
        effective_approaches = []
        if was_successful:
            if hints_used == 0:
                effective_approaches.append("독립적 문제 해결")
            elif hints_used <= 2:
                effective_approaches.append("힌트 활용 학습")
            if problem_type == "guided":
                effective_approaches.append("단계별 대화 학습")
            elif problem_type == "puzzle":
                effective_approaches.append("코드 구조 분석")
            elif problem_type == "blank":
                effective_approaches.append("빈칸 추론 학습")

        # 이해도 수준
        if was_successful and hints_used == 0:
            understanding_level = "high"
        elif was_successful and hints_used <= 2:
            understanding_level = "medium"
        elif was_successful:
            understanding_level = "medium"
        else:
            understanding_level = "low"

        # 감정 추정
        mood_trajectory = self._estimate_mood(was_successful, hints_used, time_spent)

        # 요약
        type_names = {"blank": "빈칸", "puzzle": "퍼즐", "guided": "가이드"}
        type_name = type_names.get(problem_type, problem_type)

        if was_successful:
            if hints_used == 0:
                summary = f"'{problem_name}' {type_name} 문제를 힌트 없이 해결"
            else:
                summary = f"'{problem_name}' {type_name} 문제를 {hints_used}개 힌트로 해결"
        else:
            summary = f"'{problem_name}' {type_name} 문제({difficulty})에서 어려움 겪음"

        return {
            "concepts_learned": concepts_learned,
            "concepts_struggling": concepts_struggling,
            "student_questions": student_questions,
            "breakthrough_moments": breakthrough_moments,
            "teaching_notes": teaching_notes,
            "effective_approaches": effective_approaches,
            "understanding_level": understanding_level,
            "mood_trajectory": mood_trajectory,
            "summary": summary,
        }

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
        attempt_id: Optional[str] = None,
        chat_messages: Optional[List[Dict[str, str]]] = None,
    ) -> Optional[str]:
        """
        문제 풀이 세션 메모리 생성 (v3: 로그 기반 분석)

        Args:
            user_id: 사용자 UUID
            session_id: 세션 ID
            problem_id: 문제 ID (deprecated - attempt_id 사용)
            problem_name: 문제 이름
            problem_type: 문제 유형 (blank, puzzle, guided)
            difficulty: 난이도
            topics: 문제 토픽들
            was_successful: 성공 여부
            hints_used: 힌트 사용 횟수
            time_spent: 풀이 시간 (초)
            attempt_count: 시도 횟수
            attempt_id: 시도 ID (attempts 테이블 참조)
            chat_messages: 대화 기록 (student_questions 추출용)

        Returns:
            생성된 메모리 ID 또는 None
        """
        try:
            # ============================================================
            # 로그 기반 learning_insights 생성
            # ============================================================
            learning_insights = self._generate_learning_insights(
                problem_name=problem_name,
                problem_type=problem_type,
                difficulty=difficulty,
                topics=topics or [],
                was_successful=was_successful,
                hints_used=hints_used,
                time_spent=time_spent,
                chat_messages=chat_messages,
            )

            # 요약 추출
            summary = learning_insights.get("summary", f"'{problem_name}' 문제 풀이 세션")

            # 학생 상태 추정
            mood_trajectory = learning_insights.get("mood_trajectory", ["neutral"])
            student_mood = mood_trajectory[-1] if mood_trajectory else "neutral"

            # ============================================================
            # 메모리 데이터 구성
            # attempt_id가 있으면 attempts 테이블에서 조인 가능한 필드들은 저장 안함
            # (problem_name, problem_type, difficulty, was_successful, hints, time_spent 등)
            # ============================================================
            memory_data = {
                "user_id": user_id,
                "session_id": session_id,
                "session_type": "problem_solving",
                "summary": summary,
                "key_topics": topics[:10] if topics else [],
                "key_concepts": topics[:5] if topics else [],
                # 세션 메타데이터 (세션 고유 정보)
                "duration_seconds": time_spent,
                # 대화 기반 인사이트 (attempts에 없는 정보)
                "student_questions": learning_insights.get("student_questions", []),
            }

            # attempt_id가 있으면 조인으로 나머지 정보 조회 가능
            # 없으면 비정규화 필드 저장 (레거시 호환성)
            if attempt_id:
                memory_data["attempt_id"] = attempt_id
                logger.info(f"[MemoryService] Storing with attempt_id: {attempt_id[:8]}... (lean mode)")
            else:
                # attempt_id 없는 레거시 케이스: 비정규화 필드 저장
                memory_data.update({
                    "problem_name": problem_name,
                    "problem_type": problem_type,
                    "problem_difficulty": difficulty,
                    "was_successful": was_successful,
                    "hints_needed": hints_used,
                    "time_spent_seconds": time_spent,
                    "attempt_count": attempt_count,
                })
                logger.warning(f"[MemoryService] No attempt_id - storing denormalized data")

            # DB 저장
            result = self.supabase.table("user_memories").insert(memory_data).execute()

            if result.data and len(result.data) > 0:
                memory_id = result.data[0]["id"]
                logger.info(
                    f"[MemoryService] Created memory: {memory_id} "
                    f"for user {user_id[:8]}... "
                    f"(questions: {len(learning_insights.get('student_questions', []))}, "
                    f"breakthroughs: {len(learning_insights.get('breakthrough_moments', []))})"
                )
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
                return f"'{problem_name}' {type_name} 문제({difficulty})를 힌트 없이 {time_spent}초 만에 해결했습니다."
            else:
                return f"'{problem_name}' {type_name} 문제({difficulty})를 {hints_used}개 힌트와 함께 해결했습니다."
        else:
            return f"'{problem_name}' {type_name} 문제({difficulty})에서 어려움을 겪었습니다."

    async def get_recent_memories(
        self,
        user_id: str,
        limit: int = 10,
        session_type: str = None,
    ) -> List[Dict[str, Any]]:
        """최근 세션 메모리 조회"""
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
        """사용자가 어려워하는 주제 목록 조회"""
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
        """사용자 학습 요약 조회"""
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
