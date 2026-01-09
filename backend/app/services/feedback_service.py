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
    calculate_xp,
    get_difficulty_config,
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
        """attempt_details에서 힌트 사용 내역 조회 (hint_logs 대체)"""
        try:
            # 먼저 해당 문제의 attempt 조회
            attempt_result = self.supabase.table("attempts") \
                .select("id") \
                .eq("user_id", user_id) \
                .eq("problem_id", problem_id) \
                .order("created_at", desc=True) \
                .limit(1) \
                .execute()

            if not attempt_result.data:
                return []

            attempt_id = attempt_result.data[0]["id"]

            # attempt_details에서 힌트 요청 기록 조회
            result = self.supabase.table("attempt_details") \
                .select("*") \
                .eq("attempt_id", attempt_id) \
                .eq("hint_was_requested", True) \
                .order("created_at") \
                .execute()

            if not result.data:
                return []

            # hint_logs 형식으로 변환
            hint_logs = []
            for i, detail in enumerate(result.data):
                hint_content = (
                    detail.get("blank_hint_content") or
                    detail.get("puzzle_hint_content") or
                    detail.get("guided_tutor_response") or ""
                )
                hint_logs.append({
                    "hint_level": i + 1,
                    "hint_content": hint_content,
                    "xp_cost": detail.get("xp_cost", 5),
                    "created_at": detail.get("created_at"),
                })

            return hint_logs

        except Exception as e:
            logger.warning(f"[FeedbackService] No hint logs from attempt_details: {e}")
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
        """이전 시도들 조회 (base_problem_id 기준)"""
        try:
            # problem_id에서 base_problem_id 추출 (UUID 또는 복합 ID 형태 처리)
            base_problem_id = problem_id
            result = self.supabase.table("attempts") \
                .select("id, is_correct, hints_used, submitted_at") \
                .eq("user_id", user_id) \
                .eq("base_problem_id", base_problem_id) \
                .order("submitted_at") \
                .execute()
            return result.data if result.data else []
        except Exception as e:
            logger.warning(f"[FeedbackService] No previous attempts: {e}")
            return []

    # ============================================================
    # 시도 기록 저장
    # ============================================================

    def _get_next_attempt_number(self, user_id: str, problem_id: str) -> int:
        """동일 문제에 대한 다음 시도 번호 계산 (base_problem_id 기준)"""
        try:
            base_problem_id = problem_id
            result = self.supabase.table("attempts")\
                .select("attempt_number")\
                .eq("user_id", user_id)\
                .eq("base_problem_id", base_problem_id)\
                .order("attempt_number", desc=True)\
                .limit(1)\
                .execute()

            if result.data and len(result.data) > 0:
                return (result.data[0].get("attempt_number") or 0) + 1
            return 1
        except Exception:
            return 1

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
            # 동일 문제 시도 번호 계산
            attempt_number = self._get_next_attempt_number(user_id, problem_id)

            data = {
                "user_id": user_id,
                "base_problem_id": problem_id,  # base_problem_id 컬럼 사용
                "is_correct": is_correct,
                "score": score,
                "submitted_code": submitted_code,
                "submitted_answer": submitted_answer,
                "time_spent": time_spent,
                "hints_used": hints_used,
                "xp_earned": xp_earned,
                "attempt_number": attempt_number,
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

    # NOTE: save_hint_log 제거됨 - hint_logs 테이블은 attempt_details로 통합됨
    # 힌트 기록은 practice.py의 record_attempt_detail()에서 처리

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
        attempt_id: Optional[str] = None,  # attempts 테이블 ID
        base_problem_id: Optional[str] = None,  # base_problems 테이블 ID
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
            attempt_id: attempts 테이블의 ID
            base_problem_id: base_problems 테이블의 ID

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

        # 3. 점수 계산 (난이도별 차등 적용)
        scores = calculate_scores(
            hints_used=hints_used,
            attempt_count=attempt_count,
            time_seconds=solve_time_seconds,
            avg_time=avg_solve_time,
            difficulty=difficulty,  # 난이도 전달
        )

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

            # attempts 테이블에 score 업데이트
            avg_score = (scores["efficiency_score"] + scores["speed_score"] + scores["understanding_score"]) // 3
            self._update_attempt_score(user_id, problem_id, avg_score, solve_time_seconds)

            # 🚀 피드백 결과 저장 (활용을 위해)
            await self._save_feedback_history(
                user_id=user_id,
                problem_id=problem_id,
                result=result,
                scores=scores,
                difficulty=difficulty,
                problem_type=problem_type,
                topics=topics,
                attempt_id=attempt_id,
                base_problem_id=base_problem_id,
            )

            logger.info(f"[FeedbackService] Feedback generated: grade={result['grade']}, avg_score={avg_score}")
            return result

        except Exception as e:
            logger.error(f"[FeedbackService] Feedback generation error: {e}")
            # fallback에서도 score 업데이트
            avg_score = (scores["efficiency_score"] + scores["speed_score"] + scores["understanding_score"]) // 3
            self._update_attempt_score(user_id, problem_id, avg_score, solve_time_seconds)
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
        """틀린 시도 분석 (간단 버전) - base_problem_id 기준"""
        try:
            base_problem_id = problem_id
            result = self.supabase.table("attempts") \
                .select("submitted_answer, submitted_at") \
                .eq("user_id", user_id) \
                .eq("base_problem_id", base_problem_id) \
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

    def _update_attempt_score(
        self,
        user_id: str,
        problem_id: str,
        score: int,
        time_spent: int,
    ) -> bool:
        """
        최근 attempt의 score와 time_spent 업데이트

        Args:
            user_id: 사용자 UUID
            problem_id: 문제 ID
            score: 평균 점수 (0-100)
            time_spent: 풀이 시간 (초)
        """
        try:
            # user_id로 최근 attempt 찾기 (problem_id가 UUID가 아닐 수 있으므로)
            result = self.supabase.table("attempts") \
                .select("id") \
                .eq("user_id", user_id) \
                .order("created_at", desc=True) \
                .limit(1) \
                .execute()

            if not result.data or len(result.data) == 0:
                logger.warning(f"[FeedbackService] No attempt found for user={user_id}")
                return False

            attempt_id = result.data[0]["id"]

            # score와 time_spent 업데이트
            self.supabase.table("attempts") \
                .update({
                    "score": score,
                    "time_spent": time_spent,
                }) \
                .eq("id", attempt_id) \
                .execute()

            logger.info(f"[FeedbackService] Attempt updated: id={attempt_id}, score={score}, time_spent={time_spent}s")
            return True

        except Exception as e:
            logger.error(f"[FeedbackService] Failed to update attempt score: {e}")
            return False

    async def _save_feedback_history(
        self,
        user_id: str,
        problem_id: str,
        result: Dict[str, Any],
        scores: Dict[str, int],
        difficulty: str,
        problem_type: str,
        topics: List[str],
        attempt_id: Optional[str] = None,  # 직접 전달받음
        base_problem_id: Optional[str] = None,  # base_problems.id
    ) -> bool:
        """
        🚀 피드백 결과를 feedback_history 테이블에 저장

        저장된 데이터는 다음 용도로 활용:
        1. 학습 인사이트 대시보드
        2. 개선 필요 영역 분석
        3. 주간 리포트 생성
        4. 추천 알고리즘 개선
        """
        try:
            avg_score = (scores["efficiency_score"] + scores["speed_score"] + scores["understanding_score"]) // 3

            # attempt_id가 없으면 최근 attempt 조회 (fallback)
            if not attempt_id:
                attempt_result = self.supabase.table("attempts") \
                    .select("id, base_problem_id") \
                    .eq("user_id", user_id) \
                    .order("created_at", desc=True) \
                    .limit(1) \
                    .execute()
                if attempt_result.data:
                    attempt_id = attempt_result.data[0]["id"]
                    if not base_problem_id:
                        base_problem_id = attempt_result.data[0].get("base_problem_id")

            feedback_data = {
                "user_id": user_id,
                "problem_id": problem_id,  # 레거시 호환
                "base_problem_id": base_problem_id,  # 새로운 FK
                "attempt_id": attempt_id,
                # 등급 정보
                "grade": result.get("grade", "learning"),
                "grade_emoji": result.get("grade_emoji", "🌱"),
                "grade_message": result.get("grade_message", ""),
                # 점수
                "efficiency_score": scores["efficiency_score"],
                "speed_score": scores["speed_score"],
                "understanding_score": scores["understanding_score"],
                "difficulty_bonus": scores.get("difficulty_bonus", 0),
                "avg_score": avg_score,
                # 피드백 상세
                "summary_title": result.get("summary", {}).get("title", ""),
                "summary_highlight": result.get("summary", {}).get("highlight", ""),
                "learning_points": result.get("learning_points", []),
                "improvements": result.get("improvements", []),
                "encouragement": result.get("encouragement", ""),
                # 메타데이터
                "problem_type": problem_type,
                "difficulty": difficulty,
                "topics": topics,
            }

            logger.info(f"[FeedbackService] Saving feedback_history: attempt_id={attempt_id}, base_problem_id={base_problem_id}, type={problem_type}")
            self.supabase.table("feedback_history").insert(feedback_data).execute()

            logger.info(f"[FeedbackService] Feedback history saved for user={user_id}, grade={result.get('grade')}")
            return True

        except Exception as e:
            logger.warning(f"[FeedbackService] Failed to save feedback history: {e}")
            return False

    async def get_user_learning_insights(self, user_id: str) -> Dict[str, Any]:
        """
        사용자 학습 인사이트 조회

        피드백 데이터를 기반으로 학습 분석 제공
        """
        try:
            # user_learning_insights 뷰 조회
            result = self.supabase.rpc(
                "get_improvement_areas",
                {"p_user_id": user_id}
            ).execute()

            improvement_areas = result.data or []

            # 주간 리포트 조회
            weekly_result = self.supabase.rpc(
                "get_weekly_learning_report",
                {"p_user_id": user_id}
            ).execute()

            weekly_report = weekly_result.data or []

            # 전체 통계
            stats_result = self.supabase.table("feedback_history") \
                .select("grade, avg_score, difficulty") \
                .eq("user_id", user_id) \
                .execute()

            stats_data = stats_result.data or []
            total_count = len(stats_data)
            perfect_count = len([s for s in stats_data if s.get("grade") == "perfect"])
            avg_overall = sum(s.get("avg_score", 0) for s in stats_data) / total_count if total_count else 0

            return {
                "total_problems": total_count,
                "perfect_count": perfect_count,
                "perfect_rate": round(perfect_count / total_count, 2) if total_count else 0,
                "avg_score": round(avg_overall, 1),
                "improvement_areas": improvement_areas,
                "weekly_report": weekly_report,
            }

        except Exception as e:
            logger.error(f"[FeedbackService] Failed to get learning insights: {e}")
            return {"error": str(e)}

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


    # ============================================================
    # user_skill_profiles 업데이트 (ELO-like)
    # ============================================================

    async def update_skill_profile(
        self,
        user_id: str,
        problem_topics: List[str],
        difficulty: str,
        is_correct: bool,
        problem_type: Optional[str] = None,  # 문제 유형 (blank/puzzle/guided)
        time_spent: Optional[int] = None,     # 풀이 시간 (초)
        hints_used: Optional[int] = None,     # 힌트 사용 횟수
    ) -> Dict[str, Any]:
        """
        사용자 스킬 프로필 업데이트 (ELO-like 알고리즘)

        Args:
            user_id: 사용자 UUID
            problem_topics: 문제 토픽 목록
            difficulty: 난이도 (easy/medium/hard/very_hard)
            is_correct: 정답 여부
            problem_type: 문제 유형 (blank/puzzle/guided)
            time_spent: 풀이 시간 (초)
            hints_used: 힌트 사용 횟수

        Returns:
            업데이트된 스킬 정보
        """
        try:
            # 1. 현재 프로파일 조회 (없으면 생성)
            profile_result = self.supabase.table("user_skill_profiles") \
                .select("*") \
                .eq("user_id", user_id) \
                .limit(1) \
                .execute()

            if profile_result and profile_result.data and len(profile_result.data) > 0:
                profile = profile_result.data[0]
            else:
                # 새 프로파일 생성
                profile = {
                    "user_id": user_id,
                    "skill_by_topic": {},
                    "success_rate_by_difficulty": {},
                    "weak_topics": [],
                }

            skill_by_topic = profile.get("skill_by_topic", {})
            success_rate = profile.get("success_rate_by_difficulty", {})

            # 2. 토픽별 실력 업데이트 (ELO-like)
            for topic in problem_topics:
                if not topic:
                    continue

                current_skill = skill_by_topic.get(topic, 0.5)

                if is_correct:
                    # 정답: 실력 상승 (현재 실력이 높을수록 상승폭 감소)
                    new_skill = current_skill + 0.05 * (1 - current_skill)
                else:
                    # 오답: 실력 하락 (현재 실력이 낮을수록 하락폭 감소)
                    new_skill = current_skill - 0.03 * current_skill

                # 0.0 ~ 1.0 범위 유지
                skill_by_topic[topic] = round(max(0.0, min(1.0, new_skill)), 3)

            # 3. 난이도별 성공률 업데이트
            if difficulty not in success_rate:
                success_rate[difficulty] = {"success": 0, "total": 0}

            success_rate[difficulty]["total"] += 1
            if is_correct:
                success_rate[difficulty]["success"] += 1

            # 4. 약점/강점 토픽 분석
            weak_topics = [t for t, s in skill_by_topic.items() if s < 0.4]
            strong_topics = [t for t, s in skill_by_topic.items() if s > 0.7]

            # 5. 문제 유형별 통계 업데이트
            stats_by_type = profile.get("stats_by_problem_type", {}) or {}
            if problem_type:
                if problem_type not in stats_by_type:
                    stats_by_type[problem_type] = {"success": 0, "total": 0, "total_time": 0, "total_hints": 0}
                stats_by_type[problem_type]["total"] += 1
                if is_correct:
                    stats_by_type[problem_type]["success"] += 1
                if time_spent:
                    stats_by_type[problem_type]["total_time"] = stats_by_type[problem_type].get("total_time", 0) + time_spent
                if hints_used is not None:
                    stats_by_type[problem_type]["total_hints"] = stats_by_type[problem_type].get("total_hints", 0) + hints_used
                # 평균 계산
                total_count = stats_by_type[problem_type]["total"]
                if total_count > 0:
                    stats_by_type[problem_type]["avg_time"] = round(stats_by_type[problem_type].get("total_time", 0) / total_count)
                    stats_by_type[problem_type]["avg_hints"] = round(stats_by_type[problem_type].get("total_hints", 0) / total_count, 2)

            # 5b. 전체 평균 풀이 시간/힌트 계산
            total_time = sum(s.get("total_time", 0) for s in stats_by_type.values())
            total_hints = sum(s.get("total_hints", 0) for s in stats_by_type.values())
            total_count = sum(s.get("total", 0) for s in stats_by_type.values())
            avg_solve_time = round(total_time / total_count) if total_count > 0 else None
            avg_hints_per = round(total_hints / total_count, 2) if total_count > 0 else None

            # 5c. 선호 문제 유형 (가장 많이 푼 유형)
            preferred_type = None
            if stats_by_type:
                preferred_type = max(stats_by_type.keys(), key=lambda k: stats_by_type[k].get("total", 0))

            # 5d. Streak 계산
            current_streak = profile.get("current_streak", 0) or 0
            longest_streak = profile.get("longest_streak", 0) or 0
            if is_correct:
                current_streak += 1
                longest_streak = max(longest_streak, current_streak)
            else:
                current_streak = 0

            # 5e. 총 문제 수 추적
            total_problems_attempted = profile.get("total_problems_attempted", 0) or 0
            total_problems_solved = profile.get("total_problems_solved", 0) or 0
            total_problems_attempted += 1
            if is_correct:
                total_problems_solved += 1

            # 6. 최근 토픽/난이도 추적
            recent_topics = profile.get("recent_topics", []) or []
            recent_difficulties = profile.get("recent_difficulties", []) or []

            # 최근 토픽에 현재 문제 토픽 추가 (최대 20개)
            for topic in problem_topics:
                if topic and topic not in recent_topics:
                    recent_topics.insert(0, topic)
            recent_topics = recent_topics[:20]

            # 최근 난이도 추가 (최대 10개)
            if difficulty and difficulty not in recent_difficulties[:3]:
                recent_difficulties.insert(0, difficulty)
            recent_difficulties = recent_difficulties[:10]

            # 7. DB 업데이트 (upsert)
            update_data = {
                "user_id": user_id,
                "skill_by_topic": skill_by_topic,
                "success_rate_by_difficulty": success_rate,
                "weak_topics": weak_topics[:10],
                "strong_topics": strong_topics[:10],
                "recent_topics": recent_topics,
                "recent_difficulties": recent_difficulties,
                # 새로운 필드들 추가
                "stats_by_problem_type": stats_by_type,
                "current_streak": current_streak,
                "longest_streak": longest_streak,
                "total_problems_attempted": total_problems_attempted,
                "total_problems_solved": total_problems_solved,
                "updated_at": "now()",
            }
            # Optional 필드들 (None이 아닐 때만)
            if preferred_type:
                update_data["preferred_problem_type"] = preferred_type
            if avg_solve_time is not None:
                update_data["avg_solve_time_seconds"] = avg_solve_time
            if avg_hints_per is not None:
                update_data["avg_hints_per_problem"] = avg_hints_per

            self.supabase.table("user_skill_profiles") \
                .upsert(update_data, on_conflict="user_id") \
                .execute()

            logger.info(f"[FeedbackService] Skill profile updated for user {user_id}")

            return {
                "skill_by_topic": skill_by_topic,
                "weak_topics": weak_topics,
                "updated_topics": problem_topics,
            }

        except Exception as e:
            logger.error(f"[FeedbackService] Failed to update skill profile: {e}")
            return {"skill_by_topic": {}, "weak_topics": [], "error": str(e)}

    async def recalculate_skill_profile_from_history(
        self,
        user_id: str,
        force_llm_analysis: bool = False,
    ) -> Dict[str, Any]:
        """
        🚀 히스토리 테이블 기반 user_skill_profiles 전체 재계산

        attempts, user_memories 테이블을 분석하여 모든 컬럼을 채웁니다.
        10개 이상 문제를 풀었을 때 LLM으로 learning_style, common_error_patterns 분석.

        Args:
            user_id: 사용자 UUID
            force_llm_analysis: True면 10개 미만이어도 LLM 분석 실행

        Returns:
            업데이트된 스킬 프로필 정보
        """
        try:
            logger.info(f"[FeedbackService] Recalculating skill profile for user {user_id[:8]}...")

            # ============================================================
            # 1. attempts 테이블에서 모든 시도 조회
            # ============================================================
            attempts_result = self.supabase.table("attempts") \
                .select("*, base_problems(tags, difficulty, problem_type)") \
                .eq("user_id", user_id) \
                .order("created_at") \
                .execute()

            attempts = attempts_result.data or []
            total_attempted = len(attempts)

            if total_attempted == 0:
                logger.info(f"[FeedbackService] No attempts found for user {user_id[:8]}")
                return {"error": "No attempts found", "total_attempted": 0}

            # ============================================================
            # 2. 기본 통계 계산
            # ============================================================
            total_solved = sum(1 for a in attempts if a.get("is_correct"))
            total_time = sum(a.get("time_spent", 0) or 0 for a in attempts)
            total_hints = sum(a.get("hints_used", 0) or 0 for a in attempts)

            avg_solve_time = round(total_time / total_attempted) if total_attempted > 0 else 0
            avg_hints_per = round(total_hints / total_attempted, 2) if total_attempted > 0 else 0

            # ============================================================
            # 3. 문제 유형별 통계
            # ============================================================
            stats_by_type = {}
            skill_by_topic = {}
            success_rate_by_difficulty = {}
            languages_used = {}

            for attempt in attempts:
                is_correct = attempt.get("is_correct", False)
                time_spent = attempt.get("time_spent", 0) or 0
                hints_used = attempt.get("hints_used", 0) or 0

                # base_problems에서 정보 추출
                base_problem = attempt.get("base_problems") or {}
                problem_type = base_problem.get("problem_type", "unknown")
                difficulty = base_problem.get("difficulty", "medium")
                tags = base_problem.get("tags", []) or []

                # 3a. 문제 유형별 통계
                if problem_type not in stats_by_type:
                    stats_by_type[problem_type] = {
                        "success": 0, "total": 0,
                        "total_time": 0, "total_hints": 0
                    }
                stats_by_type[problem_type]["total"] += 1
                if is_correct:
                    stats_by_type[problem_type]["success"] += 1
                stats_by_type[problem_type]["total_time"] += time_spent
                stats_by_type[problem_type]["total_hints"] += hints_used

                # 3b. 난이도별 성공률
                if difficulty not in success_rate_by_difficulty:
                    success_rate_by_difficulty[difficulty] = {"success": 0, "total": 0}
                success_rate_by_difficulty[difficulty]["total"] += 1
                if is_correct:
                    success_rate_by_difficulty[difficulty]["success"] += 1

                # 3c. 토픽별 스킬 (ELO-like)
                for topic in tags:
                    if not topic:
                        continue
                    current_skill = skill_by_topic.get(topic, 0.5)
                    if is_correct:
                        new_skill = current_skill + 0.05 * (1 - current_skill)
                    else:
                        new_skill = current_skill - 0.03 * current_skill
                    skill_by_topic[topic] = round(max(0.0, min(1.0, new_skill)), 3)

                # 3d. 언어 사용 통계 (submitted_code에서 추론)
                submitted_code = attempt.get("submitted_code", "")
                if submitted_code:
                    if "def " in submitted_code or "import " in submitted_code:
                        languages_used["python"] = languages_used.get("python", 0) + 1
                    elif "function " in submitted_code or "const " in submitted_code:
                        languages_used["javascript"] = languages_used.get("javascript", 0) + 1
                    elif "public class " in submitted_code or "void " in submitted_code:
                        languages_used["java"] = languages_used.get("java", 0) + 1

            # 문제 유형별 평균 계산
            for ptype, stats in stats_by_type.items():
                count = stats["total"]
                if count > 0:
                    stats["avg_time"] = round(stats["total_time"] / count)
                    stats["avg_hints"] = round(stats["total_hints"] / count, 2)
                    stats["success_rate"] = round(stats["success"] / count, 2)

            # ============================================================
            # 4. 선호 문제 유형/언어
            # ============================================================
            preferred_type = max(stats_by_type.keys(), key=lambda k: stats_by_type[k]["total"]) if stats_by_type else None
            preferred_language = max(languages_used.keys(), key=lambda k: languages_used[k]) if languages_used else None

            # ============================================================
            # 5. 약점/강점 토픽
            # ============================================================
            weak_topics = [t for t, s in skill_by_topic.items() if s < 0.4]
            strong_topics = [t for t, s in skill_by_topic.items() if s > 0.7]

            # ============================================================
            # 6. user_memories에서 추가 분석
            # ============================================================
            memories_result = self.supabase.table("user_memories") \
                .select("concepts_learned, concepts_struggling, teaching_notes") \
                .eq("user_id", user_id) \
                .execute()

            memories = memories_result.data or []

            # 메모리에서 집계
            all_concepts_learned = []
            all_concepts_struggling = []
            all_teaching_notes = []

            for mem in memories:
                all_concepts_learned.extend(mem.get("concepts_learned") or [])
                all_concepts_struggling.extend(mem.get("concepts_struggling") or [])
                all_teaching_notes.extend(mem.get("teaching_notes") or [])

            # 빈도 집계
            from collections import Counter
            learned_counter = Counter(all_concepts_learned)
            struggling_counter = Counter(all_concepts_struggling)

            # weak_topics 보완 (메모리 기반)
            for topic, count in struggling_counter.most_common(10):
                if topic and topic not in weak_topics:
                    weak_topics.append(topic)

            # strong_topics 보완 (메모리 기반)
            for topic, count in learned_counter.most_common(10):
                if topic and topic not in strong_topics:
                    strong_topics.append(topic)

            # ============================================================
            # 7. Streak 계산 (연속 정답)
            # ============================================================
            current_streak = 0
            longest_streak = 0
            temp_streak = 0

            for attempt in attempts:
                if attempt.get("is_correct"):
                    temp_streak += 1
                    longest_streak = max(longest_streak, temp_streak)
                else:
                    temp_streak = 0

            # 마지막 연속 정답 수
            for attempt in reversed(attempts):
                if attempt.get("is_correct"):
                    current_streak += 1
                else:
                    break

            # ============================================================
            # 8. LLM 분석 (10개 이상 풀었을 때)
            # ============================================================
            learning_style = None
            common_error_patterns = None

            if total_solved >= 10 or force_llm_analysis:
                logger.info(f"[FeedbackService] Running LLM analysis for user {user_id[:8]} (solved={total_solved})")
                llm_analysis = await self._analyze_learning_patterns_with_llm(
                    user_id=user_id,
                    attempts=attempts,
                    memories=memories,
                    skill_by_topic=skill_by_topic,
                    stats_by_type=stats_by_type,
                )
                learning_style = llm_analysis.get("learning_style")
                common_error_patterns = llm_analysis.get("common_error_patterns")

            # ============================================================
            # 9. recent_topics, recent_difficulties (최근 20개)
            # ============================================================
            recent_attempts = attempts[-20:] if len(attempts) > 20 else attempts
            recent_topics = []
            recent_difficulties = []

            for a in reversed(recent_attempts):
                bp = a.get("base_problems") or {}
                tags = bp.get("tags") or []
                diff = bp.get("difficulty")
                for t in tags:
                    if t and t not in recent_topics:
                        recent_topics.append(t)
                if diff and diff not in recent_difficulties:
                    recent_difficulties.append(diff)

            recent_topics = recent_topics[:20]
            recent_difficulties = recent_difficulties[:10]

            # ============================================================
            # 10. DB 업데이트 (upsert)
            # ============================================================
            update_data = {
                "user_id": user_id,
                # 기본 통계
                "total_problems_attempted": total_attempted,
                "total_problems_solved": total_solved,
                "avg_solve_time_seconds": avg_solve_time,
                "avg_hints_per_problem": avg_hints_per,
                # 분석 결과
                "skill_by_topic": skill_by_topic,
                "success_rate_by_difficulty": success_rate_by_difficulty,
                "stats_by_problem_type": stats_by_type,
                # 선호도
                "preferred_problem_type": preferred_type,
                "preferred_language": preferred_language,
                # 강점/약점
                "weak_topics": weak_topics[:15],
                "strong_topics": strong_topics[:15],
                # 최근 활동
                "recent_topics": recent_topics,
                "recent_difficulties": recent_difficulties,
                # Streak
                "current_streak": current_streak,
                "longest_streak": longest_streak,
                # 타임스탬프
                "updated_at": "now()",
            }

            # LLM 분석 결과 (있을 때만)
            if learning_style:
                update_data["learning_style"] = learning_style
            if common_error_patterns:
                update_data["common_error_patterns"] = common_error_patterns

            self.supabase.table("user_skill_profiles") \
                .upsert(update_data, on_conflict="user_id") \
                .execute()

            logger.info(f"[FeedbackService] Skill profile recalculated: user={user_id[:8]}, attempted={total_attempted}, solved={total_solved}")

            return {
                "success": True,
                "total_attempted": total_attempted,
                "total_solved": total_solved,
                "weak_topics": weak_topics[:5],
                "strong_topics": strong_topics[:5],
                "preferred_type": preferred_type,
                "learning_style": learning_style,
                "llm_analysis_run": total_solved >= 10 or force_llm_analysis,
            }

        except Exception as e:
            logger.error(f"[FeedbackService] Failed to recalculate skill profile: {e}")
            import traceback
            traceback.print_exc()
            return {"error": str(e)}

    async def _analyze_learning_patterns_with_llm(
        self,
        user_id: str,
        attempts: List[Dict[str, Any]],
        memories: List[Dict[str, Any]],
        skill_by_topic: Dict[str, float],
        stats_by_type: Dict[str, Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        LLM을 사용하여 학습 패턴 분석

        분석 항목:
        - learning_style: 학습 스타일 (visual, textual, hands-on, etc.)
        - common_error_patterns: 자주 하는 실수 패턴
        """
        try:
            # 분석용 요약 데이터 구성
            total_attempts = len(attempts)
            correct_attempts = [a for a in attempts if a.get("is_correct")]
            wrong_attempts = [a for a in attempts if not a.get("is_correct")]

            # 힌트 사용 패턴
            hint_heavy = sum(1 for a in attempts if (a.get("hints_used") or 0) >= 3)
            no_hint = sum(1 for a in attempts if (a.get("hints_used") or 0) == 0)

            # 시간 패턴
            times = [a.get("time_spent", 0) or 0 for a in attempts if a.get("time_spent")]
            avg_time = sum(times) / len(times) if times else 0
            fast_solves = sum(1 for t in times if t < avg_time * 0.5)
            slow_solves = sum(1 for t in times if t > avg_time * 1.5)

            # 약점 토픽
            weak_topics = [t for t, s in skill_by_topic.items() if s < 0.4][:5]

            # 메모리에서 teaching_notes 추출
            teaching_notes = []
            for mem in memories:
                notes = mem.get("teaching_notes") or []
                teaching_notes.extend(notes)
            teaching_notes = list(set(teaching_notes))[:10]

            # 프롬프트 구성
            analysis_prompt = f"""당신은 코딩 학습 분석 전문가입니다.
다음 학습자의 데이터를 분석하여 학습 스타일과 실수 패턴을 파악해주세요.

## 학습자 데이터 요약
- 총 시도: {total_attempts}회
- 정답: {len(correct_attempts)}회 ({round(len(correct_attempts)/total_attempts*100)}%)
- 오답: {len(wrong_attempts)}회

## 힌트 사용 패턴
- 힌트 많이 사용 (3개+): {hint_heavy}회
- 힌트 미사용: {no_hint}회

## 풀이 시간 패턴
- 평균 풀이 시간: {round(avg_time)}초
- 빠른 풀이 (평균의 50% 미만): {fast_solves}회
- 느린 풀이 (평균의 150% 이상): {slow_solves}회

## 문제 유형별 통계
{json.dumps(stats_by_type, ensure_ascii=False, indent=2)}

## 약점 토픽
{weak_topics if weak_topics else "아직 파악된 약점 없음"}

## 교수 노트 (이전 세션에서 기록된 관찰)
{teaching_notes if teaching_notes else "없음"}

위 데이터를 분석하여 다음 JSON 형식으로 응답해주세요:
{{
    "learning_style": "학습 스타일 (예: 'methodical', 'exploratory', 'hint-dependent', 'independent', 'fast-learner', 'careful-thinker' 중 하나 또는 조합)",
    "learning_style_description": "학습 스타일에 대한 1-2문장 설명",
    "common_error_patterns": ["실수 패턴 1", "실수 패턴 2", ...],
    "recommendations": ["학습 추천 1", "학습 추천 2"]
}}
"""

            messages = [
                {"role": "system", "content": "학습 분석 전문가입니다. JSON 형식으로만 응답합니다."},
                {"role": "user", "content": analysis_prompt},
            ]

            response = await openrouter_service.chat_completion(
                model=settings.llm_model_hint,  # 가벼운 모델 사용
                messages=messages,
                temperature=0.3,
                response_format={"type": "json_object"},
            )

            content = openrouter_service.get_content(response)
            result = openrouter_service.parse_json_response(content)

            logger.info(f"[FeedbackService] LLM analysis completed: style={result.get('learning_style')}")

            return {
                "learning_style": result.get("learning_style"),
                "learning_style_description": result.get("learning_style_description"),
                "common_error_patterns": result.get("common_error_patterns", []),
                "recommendations": result.get("recommendations", []),
            }

        except Exception as e:
            logger.error(f"[FeedbackService] LLM analysis failed: {e}")
            return {}

    async def save_attempt_with_skill_update(
        self,
        user_id: str,
        problem_id: str,
        is_correct: bool,
        problem_topics: List[str] = None,
        difficulty: str = "medium",
        submitted_code: Optional[str] = None,
        submitted_answer: Optional[str] = None,
        time_spent: Optional[int] = None,
        hints_used: int = 0,
        xp_earned: int = 0,
    ) -> Dict[str, Any]:
        """
        시도 기록 저장 + 스킬 프로필 업데이트 (통합)

        Returns:
            {"attempt_id": str, "skill_updates": dict}
        """
        # 1. 시도 기록 저장
        attempt_id = await self.save_attempt(
            user_id=user_id,
            problem_id=problem_id,
            is_correct=is_correct,
            submitted_code=submitted_code,
            submitted_answer=submitted_answer,
            time_spent=time_spent,
            hints_used=hints_used,
            xp_earned=xp_earned,
        )

        # 2. 스킬 프로필 업데이트
        skill_updates = {}
        if problem_topics:
            skill_updates = await self.update_skill_profile(
                user_id=user_id,
                problem_topics=problem_topics,
                difficulty=difficulty,
                is_correct=is_correct,
            )

        return {
            "attempt_id": attempt_id,
            "skill_updates": skill_updates,
        }


# Singleton instance
_feedback_service = None


def get_feedback_service() -> FeedbackService:
    """FeedbackService 싱글톤 반환"""
    global _feedback_service
    if _feedback_service is None:
        _feedback_service = FeedbackService()
    return _feedback_service
