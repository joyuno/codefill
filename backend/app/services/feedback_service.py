"""
Feedback Service
문제 풀이 완료 후 피드백 생성 서비스

DB에서 풀이 관련 데이터를 수집하고, LLM을 통해 맞춤형 피드백을 생성합니다.
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from ..database import get_supabase_client
from ..services.openrouter import openrouter_service
from ..config import get_settings
from ..prompts.feedback_agent import (
    FEEDBACK_SYSTEM_PROMPT,
    calculate_grade,
    format_solve_time,
    calculate_scores,
)

logger = logging.getLogger(__name__)
settings = get_settings()


class FeedbackService:
    """문제 풀이 피드백 생성 서비스"""

    def __init__(self):
        self.supabase = get_supabase_client()

    # ============================================================
    # DB 조회 메서드
    # ============================================================

    def get_attempt_info(self, attempt_id: str) -> Optional[Dict[str, Any]]:
        """attempts 테이블에서 시도 정보 조회"""
        try:
            result = self.supabase.table("attempts") \
                .select("*") \
                .eq("id", attempt_id) \
                .single() \
                .execute()
            return result.data if result.data else None
        except Exception as e:
            logger.error(f"[FeedbackService] Failed to get attempt: {e}")
            return None

    def get_attempt_details(self, attempt_id: str) -> Optional[Dict[str, Any]]:
        """attempt_details 테이블에서 상세 정보 조회"""
        try:
            result = self.supabase.table("attempt_details") \
                .select("*") \
                .eq("attempt_id", attempt_id) \
                .single() \
                .execute()
            return result.data if result.data else None
        except Exception as e:
            logger.warning(f"[FeedbackService] No attempt details: {e}")
            return None

    def get_hint_logs(self, user_id: str, problem_id: str) -> List[Dict[str, Any]]:
        """hint_logs 테이블에서 힌트 사용 내역 조회"""
        try:
            result = self.supabase.table("hint_logs") \
                .select("*") \
                .eq("user_id", user_id) \
                .eq("problem_id", problem_id) \
                .order("created_at") \
                .execute()
            return result.data if result.data else []
        except Exception as e:
            logger.warning(f"[FeedbackService] No hint logs: {e}")
            return []

    def get_user_stats(self, user_id: str) -> Optional[Dict[str, Any]]:
        """user_stats 테이블에서 사용자 통계 조회"""
        try:
            result = self.supabase.table("user_stats") \
                .select("*") \
                .eq("user_id", user_id) \
                .single() \
                .execute()
            return result.data if result.data else None
        except Exception as e:
            logger.warning(f"[FeedbackService] No user stats: {e}")
            return None

    def get_problem_info(self, problem_id: str) -> Optional[Dict[str, Any]]:
        """base_problems 또는 problems 테이블에서 문제 정보 조회"""
        try:
            # 먼저 base_problems에서 조회
            result = self.supabase.table("base_problems") \
                .select("id, name, question, difficulty, tags") \
                .eq("id", problem_id) \
                .single() \
                .execute()
            if result.data:
                return result.data
        except:
            pass

        try:
            # problems 테이블에서 조회
            result = self.supabase.table("problems") \
                .select("id, title, description, difficulty, tags, avg_solve_time") \
                .eq("id", problem_id) \
                .single() \
                .execute()
            return result.data if result.data else None
        except Exception as e:
            logger.warning(f"[FeedbackService] Problem not found: {e}")
            return None

    def get_previous_attempts(self, user_id: str, problem_id: str) -> List[Dict[str, Any]]:
        """이전 시도들 조회"""
        try:
            result = self.supabase.table("attempts") \
                .select("id, is_correct, hints_used, submitted_at") \
                .eq("user_id", user_id) \
                .eq("problem_id", problem_id) \
                .order("submitted_at") \
                .execute()
            return result.data if result.data else []
        except Exception as e:
            logger.warning(f"[FeedbackService] No previous attempts: {e}")
            return []

    # ============================================================
    # 시도 기록 저장
    # ============================================================

    async def save_attempt(
        self,
        user_id: str,
        problem_id: str,
        is_correct: bool,
        submitted_code: Optional[str] = None,
        submitted_answer: Optional[str] = None,
        started_at: Optional[datetime] = None,
        time_spent: Optional[int] = None,
        hints_used: int = 0,
        xp_earned: int = 0,
        score: int = 0,
    ) -> Optional[str]:
        """시도 기록을 DB에 저장"""
        try:
            data = {
                "user_id": user_id,
                "problem_id": problem_id,
                "is_correct": is_correct,
                "score": score,
                "submitted_code": submitted_code,
                "submitted_answer": submitted_answer,
                "time_spent": time_spent,
                "hints_used": hints_used,
                "xp_earned": xp_earned,
            }

            if started_at:
                data["started_at"] = started_at.isoformat()

            result = self.supabase.table("attempts").insert(data).execute()

            if result.data and len(result.data) > 0:
                attempt_id = result.data[0]["id"]
                logger.info(f"[FeedbackService] Attempt saved: {attempt_id}")
                return attempt_id

            return None

        except Exception as e:
            logger.error(f"[FeedbackService] Failed to save attempt: {e}")
            return None

    async def save_hint_log(
        self,
        user_id: str,
        problem_id: str,
        hint_level: int,
        hint_content: str,
        attempt_id: Optional[str] = None,
        xp_cost: int = 10,
    ) -> bool:
        """힌트 사용 기록 저장"""
        try:
            data = {
                "user_id": user_id,
                "problem_id": problem_id,
                "hint_level": hint_level,
                "hint_content": hint_content,
                "xp_cost": xp_cost,
            }

            if attempt_id:
                data["attempt_id"] = attempt_id

            self.supabase.table("hint_logs").insert(data).execute()
            return True

        except Exception as e:
            logger.error(f"[FeedbackService] Failed to save hint log: {e}")
            return False

    # ============================================================
    # 피드백 생성
    # ============================================================

    async def generate_feedback(
        self,
        user_id: str,
        problem_id: str,
        is_correct: bool,
        solve_time_seconds: int,
        hints_used: int,
        xp_earned: int,
        problem_info: Optional[Dict[str, Any]] = None,
        problem_type: str = "blank",
        attempt_count: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        문제 풀이 피드백 생성

        Args:
            user_id: 사용자 UUID
            problem_id: 문제 ID
            is_correct: 정답 여부
            solve_time_seconds: 풀이 시간 (초)
            hints_used: 사용한 힌트 수
            xp_earned: 획득한 XP
            problem_info: 추가 문제 정보
            problem_type: 문제 유형 (blank/puzzle/guided)
            attempt_count: 시도 횟수 (없으면 DB에서 조회)

        Returns:
            피드백 응답 딕셔너리
        """
        # 1. DB에서 정보 수집
        # 문제 정보
        db_problem = self.get_problem_info(problem_id)
        problem_title = "문제"
        difficulty = "medium"
        topics = []
        avg_solve_time = 300  # 기본 5분

        if db_problem:
            problem_title = db_problem.get("name") or db_problem.get("title", "문제")
            difficulty = db_problem.get("difficulty", "medium")
            topics = db_problem.get("tags", [])
            avg_solve_time = db_problem.get("avg_solve_time", 300)
        elif problem_info:
            problem_title = problem_info.get("title", "문제")
            difficulty = problem_info.get("difficulty", "medium")
            topics = problem_info.get("topics", [])

        # 사용자 통계
        user_stats = self.get_user_stats(user_id)
        user_level = 1
        total_solved = 0

        if user_stats:
            user_level = user_stats.get("level", 1)
            total_solved = user_stats.get("total_solved", 0)

        # 이전 시도 수 (제공되지 않은 경우)
        if attempt_count is None:
            previous_attempts = self.get_previous_attempts(user_id, problem_id)
            attempt_count = len(previous_attempts)

        # 힌트 사용 내역
        hint_logs = self.get_hint_logs(user_id, problem_id)
        hint_history = self._format_hint_history(hint_logs)
        hint_xp_cost = sum(h.get("xp_cost", 10) for h in hint_logs)

        # 틀린 시도 분석
        wrong_attempts = self._analyze_wrong_attempts(user_id, problem_id)

        # 2. 성과 등급 계산
        time_ratio = solve_time_seconds / avg_solve_time if avg_solve_time > 0 else 1.0
        grade, grade_emoji, grade_message = calculate_grade(hints_used, attempt_count, time_ratio)

        # 3. 점수 계산
        scores = calculate_scores(hints_used, attempt_count, solve_time_seconds, avg_solve_time)

        # 4. 시스템 프롬프트 구성
        system_prompt = FEEDBACK_SYSTEM_PROMPT.format(
            problem_title=problem_title,
            difficulty=difficulty,
            problem_type=problem_type,
            topics=", ".join(topics) if topics else "알고리즘",
            is_correct="정답" if is_correct else "오답",
            score=100 if is_correct else 0,
            solve_time_formatted=format_solve_time(solve_time_seconds),
            attempt_count=attempt_count,
            hints_used=hints_used,
            hint_xp_cost=hint_xp_cost,
            xp_earned=xp_earned,
            hint_history=hint_history,
            wrong_attempts=wrong_attempts,
            user_level=user_level,
            total_solved=total_solved,
            avg_solve_time=format_solve_time(avg_solve_time),
        )

        # 5. LLM 호출
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "이 풀이에 대한 피드백을 생성해주세요."},
        ]

        try:
            response = await openrouter_service.chat_completion(
                model=settings.llm_model_hint,  # 가벼운 모델 사용
                messages=messages,
                temperature=0.7,
                response_format={"type": "json_object"},
            )

            content = openrouter_service.get_content(response)
            result = openrouter_service.parse_json_response(content)

            # 계산된 값들 추가/오버라이드
            result["visualization"] = result.get("visualization", {})
            result["visualization"]["efficiency_score"] = scores["efficiency_score"]
            result["visualization"]["speed_score"] = scores["speed_score"]
            result["visualization"]["understanding_score"] = scores["understanding_score"]
            result["visualization"]["time_comparison"] = {
                "user_time": solve_time_seconds,
                "avg_time": avg_solve_time,
                "percentile": self._calculate_percentile(time_ratio),
            }

            # 기본값 보장
            result["grade"] = result.get("grade", grade)
            result["grade_emoji"] = result.get("grade_emoji", grade_emoji)
            result["grade_message"] = result.get("grade_message", grade_message)

            logger.info(f"[FeedbackService] Feedback generated: grade={result['grade']}")
            return result

        except Exception as e:
            logger.error(f"[FeedbackService] Feedback generation error: {e}")
            return self._fallback_feedback(
                is_correct, hints_used, attempt_count, solve_time_seconds,
                xp_earned, grade, grade_emoji, grade_message, scores
            )

    def _format_hint_history(self, hint_logs: List[Dict[str, Any]]) -> str:
        """힌트 사용 내역을 문자열로 포맷"""
        if not hint_logs:
            return "(힌트 사용 안 함)"

        lines = []
        for i, log in enumerate(hint_logs):
            level = log.get("hint_level", 1)
            content = (log.get("hint_content", "")[:100] + "...") if log.get("hint_content") else ""
            lines.append(f"  {i + 1}. Level {level}: {content}")

        return "\n".join(lines)

    def _analyze_wrong_attempts(self, user_id: str, problem_id: str) -> str:
        """틀린 시도 분석 (간단 버전)"""
        try:
            result = self.supabase.table("attempts") \
                .select("submitted_answer, submitted_at") \
                .eq("user_id", user_id) \
                .eq("problem_id", problem_id) \
                .eq("is_correct", False) \
                .order("submitted_at") \
                .limit(5) \
                .execute()

            if not result.data:
                return "(틀린 시도 없음 - 한 번에 정답!)"

            lines = []
            for i, attempt in enumerate(result.data):
                answer = attempt.get("submitted_answer", "")[:50]
                lines.append(f"  시도 {i + 1}: {answer}")

            return "\n".join(lines)

        except Exception as e:
            return "(분석 불가)"

    def _calculate_percentile(self, time_ratio: float) -> str:
        """시간 비율을 백분위로 변환"""
        if time_ratio < 0.5:
            return "상위 10%"
        elif time_ratio < 0.75:
            return "상위 25%"
        elif time_ratio < 1.0:
            return "상위 50%"
        elif time_ratio < 1.5:
            return "상위 75%"
        else:
            return "평균 이상"

    def _fallback_feedback(
        self,
        is_correct: bool,
        hints_used: int,
        attempt_count: int,
        solve_time: int,
        xp_earned: int,
        grade: str,
        grade_emoji: str,
        grade_message: str,
        scores: Dict[str, int],
    ) -> Dict[str, Any]:
        """LLM 실패 시 폴백 피드백"""
        return {
            "grade": grade,
            "grade_emoji": grade_emoji,
            "grade_message": grade_message,
            "summary": {
                "title": "문제 풀이 완료!" if is_correct else "다음에 더 잘할 수 있어요!",
                "highlight": f"{xp_earned} XP 획득!" if is_correct else "포기하지 마세요!",
            },
            "performance_analysis": {
                "time_feedback": f"풀이 시간: {format_solve_time(solve_time)}",
                "hint_feedback": f"힌트 {hints_used}회 사용" if hints_used > 0 else "힌트 없이 해결!",
                "attempt_feedback": f"총 {attempt_count}회 시도" if attempt_count > 1 else "한 번에 성공!",
            },
            "learning_points": [
                "문제를 끝까지 풀어냈습니다.",
                "이 경험이 실력 향상에 도움이 됩니다.",
            ],
            "improvements": [
                "비슷한 유형의 문제를 더 풀어보세요.",
                "시간을 재며 연습하면 속도가 빨라집니다.",
            ],
            "visualization": {
                "efficiency_score": scores["efficiency_score"],
                "speed_score": scores["speed_score"],
                "understanding_score": scores["understanding_score"],
                "time_comparison": {
                    "user_time": solve_time,
                    "avg_time": 300,
                    "percentile": "측정 중",
                },
            },
            "next_steps": {
                "recommendation": "다음 문제에 도전해보세요!",
                "similar_problems": None,
            },
            "encouragement": "잘했어요! 계속 도전하면 더 빠르게 성장할 수 있어요! 💪",
        }


# Singleton instance
_feedback_service = None


def get_feedback_service() -> FeedbackService:
    """FeedbackService 싱글톤 반환"""
    global _feedback_service
    if _feedback_service is None:
        _feedback_service = FeedbackService()
    return _feedback_service
