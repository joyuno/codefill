"""Analysis Service - AI 기반 학습 분석 및 리포트 생성."""

import json
import logging
from uuid import UUID
from datetime import datetime
from typing import Optional, List, Dict, Any

from ..config import get_settings, get_logger
from ..services.openrouter import openrouter_service
from ..prompts.analysis_agent import ANALYSIS_SYSTEM_PROMPT

logger = get_logger(__name__)
settings = get_settings()


class InsufficientDataError(Exception):
    """분석에 필요한 데이터가 부족할 때 발생."""
    pass


class AnalysisService:
    """사용자 학습 데이터 분석 서비스."""

    def __init__(self, db):
        self.db = db

    async def get_latest_report(self, user_id: UUID) -> Optional[Dict[str, Any]]:
        """최신 분석 리포트 조회."""
        result = self.db.table("user_analysis_reports").select("*").eq(
            "user_id", str(user_id)
        ).execute()

        if not result.data or len(result.data) == 0:
            return None

        data = result.data[0]  # 첫 번째 row 사용
        return {
            "id": data.get("id"),
            "summaryText": data.get("summary_text"),
            "strengths": data.get("strengths", []),
            "weaknesses": data.get("weaknesses", []),
            "recommendations": data.get("recommendations", []),
            "studyPlan": data.get("study_plan"),
            "skillSnapshot": data.get("skill_snapshot", {}),
            "statsSnapshot": data.get("stats_snapshot", {}),
            "difficultySnapshot": data.get("difficulty_snapshot", {}),
            "recommendedProblems": data.get("recommended_problems", []),
            "createdAt": data.get("created_at"),
            # 새로 추가된 필드들
            "conceptsStruggling": data.get("concepts_struggling", []),
            "conceptsLearned": data.get("concepts_learned", []),
            "hintUsage": data.get("hint_usage", {}),
            "learningStyle": data.get("learning_style", {}),
            "commonErrorPatterns": data.get("common_error_patterns", {}),
            "moodDistribution": data.get("mood_distribution", {}),
            "breakthroughMoments": data.get("breakthrough_moments", []),
            "teachingNotes": data.get("teaching_notes", []),
        }

    async def generate_analysis(self, user_id: UUID) -> Dict[str, Any]:
        """AI 분석 실행 및 저장."""

        # 1. 사용자 데이터 수집
        user_data = await self._collect_user_data(user_id)

        # 2. 데이터 충분한지 확인
        problems_solved = user_data.get("problems_solved", 0)
        if problems_solved < 1:
            raise InsufficientDataError("분석을 위해 최소 1개 이상의 문제를 풀어주세요.")

        # 3. 분석 생성 (LLM 사용, 실패 시 템플릿 폴백)
        analysis = await self._generate_analysis_with_llm(user_data)

        # 3. 추천 문제 조회
        recommended = await self._get_recommended_problems(user_id, user_data)

        # 4. DB 저장 (upsert)
        report_data = {
            "user_id": str(user_id),
            "summary_text": analysis["summary"],
            "strengths": analysis["strengths"],
            "weaknesses": analysis["weaknesses"],
            "recommendations": analysis["recommendations"],
            "study_plan": analysis["study_plan"],
            "skill_snapshot": user_data.get("skill_by_topic", {}),
            "stats_snapshot": {
                "level": user_data.get("level", 1),
                "problemsSolved": user_data.get("problems_solved", 0),
                "accuracy": user_data.get("accuracy", 0),
                "streak": user_data.get("streak", 0),
            },
            "difficulty_snapshot": user_data.get("difficulty_stats", {}),
            "recommended_problems": recommended,
            # 새로 추가된 필드들
            "concepts_struggling": user_data.get("concepts_struggling", []),
            "concepts_learned": user_data.get("concepts_learned", []),
            "hint_usage": user_data.get("hint_usage", {}),
            "learning_style": user_data.get("learning_style", {}),
            "common_error_patterns": user_data.get("common_error_patterns", {}),
            "mood_distribution": user_data.get("mood_distribution", {}),
            "breakthrough_moments": user_data.get("breakthrough_moments", []),
            "teaching_notes": user_data.get("teaching_notes", []),
        }

        # Upsert (insert or update)
        self.db.table("user_analysis_reports").upsert(
            report_data,
            on_conflict="user_id"
        ).execute()

        return {
            "id": None,  # Will be generated
            "summaryText": analysis["summary"],
            "strengths": analysis["strengths"],
            "weaknesses": analysis["weaknesses"],
            "recommendations": analysis["recommendations"],
            "studyPlan": analysis["study_plan"],
            "skillSnapshot": user_data.get("skill_by_topic", {}),
            "statsSnapshot": report_data["stats_snapshot"],
            "difficultySnapshot": user_data.get("difficulty_stats", {}),
            "recommendedProblems": recommended,
            "createdAt": datetime.utcnow().isoformat(),
            # 새로 추가된 필드들
            "conceptsStruggling": user_data.get("concepts_struggling", []),
            "conceptsLearned": user_data.get("concepts_learned", []),
            "hintUsage": user_data.get("hint_usage", {}),
            "learningStyle": user_data.get("learning_style", {}),
            "commonErrorPatterns": user_data.get("common_error_patterns", {}),
            "moodDistribution": user_data.get("mood_distribution", {}),
            "breakthroughMoments": user_data.get("breakthrough_moments", []),
            "teachingNotes": user_data.get("teaching_notes", []),
        }

    async def _collect_user_data(self, user_id: UUID) -> Dict[str, Any]:
        """사용자 학습 데이터 수집."""
        data = {}

        # 1. user_stats
        stats_result = self.db.table("user_stats").select(
            "level, problems_solved, current_streak"
        ).eq("user_id", str(user_id)).execute()

        if stats_result.data and len(stats_result.data) > 0:
            stats = stats_result.data[0]
            data["level"] = stats.get("level", 1)
            data["problems_solved"] = stats.get("problems_solved", 0)
            data["streak"] = stats.get("current_streak", 0)

        # 2. attempts 테이블에서 스킬 데이터 직접 계산
        attempts_for_skill = self.db.table("attempts").select(
            "topics, difficulty, is_correct"
        ).eq("user_id", str(user_id)).not_.is_("is_correct", "null").execute()

        # 토픽별 성공률 계산
        topic_stats = {}  # {topic: {"success": 0, "total": 0}}
        difficulty_raw = {}  # {difficulty: {"success": 0, "total": 0}}

        if attempts_for_skill.data:
            for attempt in attempts_for_skill.data:
                is_correct = attempt.get("is_correct", False)
                topics = attempt.get("topics") or []
                difficulty = attempt.get("difficulty")

                # 토픽별 집계
                for topic in topics:
                    if topic not in topic_stats:
                        topic_stats[topic] = {"success": 0, "total": 0}
                    topic_stats[topic]["total"] += 1
                    if is_correct:
                        topic_stats[topic]["success"] += 1

                # 난이도별 집계
                if difficulty:
                    if difficulty not in difficulty_raw:
                        difficulty_raw[difficulty] = {"success": 0, "total": 0}
                    difficulty_raw[difficulty]["total"] += 1
                    if is_correct:
                        difficulty_raw[difficulty]["success"] += 1

        # skill_by_topic 계산 (성공률 0.0~1.0)
        skill_by_topic = {}
        weak_topics = []
        strong_topics = []

        for topic, stats in topic_stats.items():
            if stats["total"] > 0:
                rate = round(stats["success"] / stats["total"], 2)
                skill_by_topic[topic] = rate
                if rate < 0.4:
                    weak_topics.append(topic)
                elif rate > 0.7:
                    strong_topics.append(topic)

        data["skill_by_topic"] = skill_by_topic
        data["weak_topics"] = weak_topics
        data["strong_topics"] = strong_topics

        # difficulty_stats 계산
        difficulty_stats = {}
        for diff, stats in difficulty_raw.items():
            if stats["total"] > 0:
                difficulty_stats[diff] = round(stats["success"] / stats["total"], 2)
            else:
                difficulty_stats[diff] = 0
        data["difficulty_stats"] = difficulty_stats

        # learning_style, common_error_patterns은 user_memories에서 추출 (아래에서 처리)
        data["learning_style"] = {}
        data["common_error_patterns"] = {}

        # 3. Overall accuracy (위에서 조회한 attempts_for_skill 데이터 활용)
        if attempts_for_skill.data:
            total = len(attempts_for_skill.data)
            correct = sum(1 for a in attempts_for_skill.data if a.get("is_correct"))
            data["accuracy"] = round(correct / total, 2) if total > 0 else 0
        else:
            data["accuracy"] = 0

        # 4. user_memories - 최근 학습 세션 기록
        memories_result = self.db.table("user_memories").select(
            "summary, key_topics, concepts_learned, concepts_struggling, "
            "teaching_notes, breakthrough_moments, student_mood, "
            "problem_name, was_successful, hints_needed, created_at, learning_insights"
        ).eq("user_id", str(user_id)).order(
            "created_at", desc=True
        ).limit(10).execute()

        if memories_result.data and len(memories_result.data) > 0:
            # 어려워한 개념들 집계
            all_struggling = []
            all_learned = []
            all_teaching_notes = []
            all_breakthroughs = []
            mood_counts = {}
            session_summaries = []
            learning_insights_list = []

            for mem in memories_result.data:
                # 어려워한 개념
                struggling = mem.get("concepts_struggling") or []
                all_struggling.extend(struggling)

                # 이해한 개념
                learned = mem.get("concepts_learned") or []
                all_learned.extend(learned)

                # 교육 노트
                notes = mem.get("teaching_notes") or []
                all_teaching_notes.extend(notes)

                # 돌파 순간
                breakthroughs = mem.get("breakthrough_moments") or []
                all_breakthroughs.extend(breakthroughs)

                # 학생 mood 집계
                mood = mem.get("student_mood")
                if mood:
                    mood_counts[mood] = mood_counts.get(mood, 0) + 1

                # 세션 요약
                if mem.get("summary"):
                    session_summaries.append({
                        "summary": mem.get("summary"),
                        "problem_name": mem.get("problem_name"),
                        "was_successful": mem.get("was_successful"),
                        "hints_needed": mem.get("hints_needed"),
                    })

                # learning_insights 수집
                insights = mem.get("learning_insights")
                if insights and isinstance(insights, dict):
                    learning_insights_list.append(insights)

            data["concepts_struggling"] = list(set(all_struggling))[:10]
            data["concepts_learned"] = list(set(all_learned))[:10]
            data["teaching_notes"] = all_teaching_notes[:5]
            data["breakthrough_moments"] = all_breakthroughs[:5]
            data["mood_distribution"] = mood_counts
            data["recent_sessions"] = session_summaries[:5]

            # learning_style 추출 (가장 최근 learning_insights에서)
            if learning_insights_list:
                latest_insights = learning_insights_list[0]
                data["learning_style"] = {
                    "prefers_examples": latest_insights.get("prefers_examples", False),
                    "prefers_analogies": latest_insights.get("prefers_analogies", False),
                    "hint_sensitivity": latest_insights.get("hint_sensitivity", "medium"),
                    "pace": latest_insights.get("pace", "medium"),
                }
                data["common_error_patterns"] = latest_insights.get("common_errors", {})

        # 5. attempt_details - 힌트 사용 패턴 및 오류 분석
        # 최근 시도들의 ID 조회
        recent_attempts = self.db.table("attempts").select(
            "id"
        ).eq("user_id", str(user_id)).order(
            "created_at", desc=True
        ).limit(50).execute()

        if recent_attempts.data and len(recent_attempts.data) > 0:
            attempt_ids = [a["id"] for a in recent_attempts.data]

            # attempt_details 조회
            details_result = self.db.table("attempt_details").select(
                "action_type, blank_hint_level, blank_is_correct, "
                "hint_was_requested, hint_was_helpful"
            ).in_("attempt_id", attempt_ids).execute()

            if details_result.data and len(details_result.data) > 0:
                total_hints_requested = 0
                helpful_hints = 0
                hint_levels = []
                blank_correct_count = 0
                blank_total_count = 0

                for detail in details_result.data:
                    # 힌트 요청 횟수
                    if detail.get("hint_was_requested"):
                        total_hints_requested += 1
                        if detail.get("hint_was_helpful"):
                            helpful_hints += 1

                    # 힌트 레벨 분포
                    hint_level = detail.get("blank_hint_level")
                    if hint_level is not None:
                        hint_levels.append(hint_level)

                    # 빈칸 정답률
                    if detail.get("blank_is_correct") is not None:
                        blank_total_count += 1
                        if detail.get("blank_is_correct"):
                            blank_correct_count += 1

                data["hint_usage"] = {
                    "total_requested": total_hints_requested,
                    "helpful_count": helpful_hints,
                    "helpful_rate": round(helpful_hints / total_hints_requested, 2) if total_hints_requested > 0 else 0,
                    "avg_hint_level": round(sum(hint_levels) / len(hint_levels), 2) if hint_levels else 0,
                }
                data["blank_accuracy"] = round(
                    blank_correct_count / blank_total_count, 2
                ) if blank_total_count > 0 else None

        return data

    async def _generate_analysis_with_llm(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """LLM을 사용한 분석 생성. 실패 시 템플릿으로 폴백."""
        try:
            # 프롬프트 생성
            prompt = ANALYSIS_SYSTEM_PROMPT.format(
                user_data=json.dumps(user_data, ensure_ascii=False, indent=2)
            )

            # LLM 호출
            logger.info("LLM 분석 생성 시작")
            response = await openrouter_service.chat_completion(
                model=settings.llm_model_analysis,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": "위 데이터를 분석하고 JSON으로 응답하세요."}
                ],
                temperature=0.7,
                max_tokens=1500,
            )

            content = openrouter_service.get_content(response)
            result = openrouter_service.parse_json_response(content)
            logger.info("LLM 분석 생성 완료")

            # 결과 검증 및 정규화
            return self._normalize_llm_result(result, user_data)

        except Exception as e:
            logger.warning(f"LLM 분석 실패, 템플릿으로 폴백: {e}")
            return self._generate_analysis_content(user_data)

    def _normalize_llm_result(self, result: Dict[str, Any], user_data: Dict[str, Any]) -> Dict[str, Any]:
        """LLM 결과를 정규화하고 필수 필드 보장."""
        skill_by_topic = user_data.get("skill_by_topic", {})

        # 강점 정규화
        strengths = []
        for s in result.get("strengths", []):
            if isinstance(s, dict) and "topic" in s:
                topic = s["topic"]
                strengths.append({
                    "topic": topic,
                    "score": s.get("score", skill_by_topic.get(topic, 0.7)),
                    "insight": s.get("insight", ""),
                })

        # 약점 정규화
        weaknesses = []
        for w in result.get("weaknesses", []):
            if isinstance(w, dict) and "topic" in w:
                topic = w["topic"]
                weaknesses.append({
                    "topic": topic,
                    "score": w.get("score", skill_by_topic.get(topic, 0.3)),
                    "insight": w.get("insight", ""),
                })

        return {
            "summary": result.get("summary", "분석 결과를 생성했습니다."),
            "strengths": strengths,
            "weaknesses": weaknesses,
            "recommendations": result.get("recommendations", ["꾸준히 문제를 풀며 실력을 쌓아가세요!"]),
            "study_plan": result.get("study_plan", "다양한 유형의 문제에 도전해보세요!"),
        }

    def _generate_analysis_content(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """분석 콘텐츠 생성 (MVP: 템플릿 기반)."""

        skill_by_topic = user_data.get("skill_by_topic", {})
        weak_topics = user_data.get("weak_topics", [])
        strong_topics = user_data.get("strong_topics", [])
        level = user_data.get("level", 1)
        problems_solved = user_data.get("problems_solved", 0)
        accuracy = user_data.get("accuracy", 0)
        streak = user_data.get("streak", 0)

        # Strengths
        strengths = []
        for topic in (strong_topics or [])[:5]:
            score = skill_by_topic.get(topic, 0.7)
            strengths.append({
                "topic": topic,
                "score": round(score, 2),
                "insight": f"{topic} 영역에서 높은 성취도를 보이고 있습니다."
            })

        # Weaknesses
        weaknesses = []
        for topic in (weak_topics or [])[:5]:
            score = skill_by_topic.get(topic, 0.3)
            weaknesses.append({
                "topic": topic,
                "score": round(score, 2),
                "insight": f"{topic} 기초 개념부터 다시 학습하면 빠르게 향상될 수 있습니다."
            })

        # Summary text
        if weaknesses:
            weak_names = ", ".join([w["topic"] for w in weaknesses[:2]])
            summary = f"{weak_names} 영역에서 어려움을 겪고 있습니다. 기초부터 단계적으로 학습하면 빠르게 성장할 수 있습니다."
        elif strengths:
            strong_names = ", ".join([s["topic"] for s in strengths[:2]])
            summary = f"{strong_names} 영역에서 뛰어난 실력을 보이고 있습니다. 다른 영역도 도전해보세요!"
        else:
            summary = "아직 분석할 데이터가 충분하지 않습니다. 더 많은 문제를 풀어보세요!"

        # Recommendations
        recommendations = []
        if streak > 0:
            recommendations.append(f"현재 {streak}일 연속 학습 중입니다! 이 페이스를 유지하세요.")
        if accuracy < 0.5 and problems_solved > 5:
            recommendations.append("정답률이 낮은 편입니다. 쉬운 문제부터 차근차근 풀어보세요.")
        if weaknesses:
            weak_topic = weaknesses[0]["topic"]
            recommendations.append(f"{weak_topic} 기초 문제부터 시작해보세요.")
        if not recommendations:
            recommendations.append("꾸준히 문제를 풀며 실력을 쌓아가세요!")

        # Study plan
        if weaknesses:
            plan_topics = " → ".join([w["topic"] for w in weaknesses[:3]])
            study_plan = f"추천 학습 경로: {plan_topics}"
        else:
            study_plan = "다양한 유형의 문제에 도전해보세요!"

        return {
            "summary": summary,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "recommendations": recommendations,
            "study_plan": study_plan,
        }

    async def _get_recommended_problems(
        self, user_id: UUID, user_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """약점 기반 추천 문제 조회."""

        weak_topics = user_data.get("weak_topics", [])
        skill_by_topic = user_data.get("skill_by_topic", {})

        if not weak_topics:
            # 약점 없으면 랜덤 문제
            result = self.db.table("base_problems").select(
                "id, original_id, name, difficulty, tags"
            ).limit(5).execute()

            return [
                {
                    "id": str(p.get("id")),
                    "originalId": p.get("original_id"),
                    "name": p.get("name", "Unknown"),
                    "difficulty": p.get("difficulty", "medium"),
                    "topic": (p.get("tags") or ["general"])[0],
                    "reason": "실력 향상을 위한 추천 문제",
                }
                for p in (result.data or [])
            ]

        # 이미 푼 문제 ID 조회
        solved_result = self.db.table("attempts").select(
            "base_problem_id"
        ).eq("user_id", str(user_id)).eq("is_correct", True).execute()

        solved_ids = set(
            a.get("base_problem_id") for a in (solved_result.data or [])
            if a.get("base_problem_id")
        )

        # 약점 토픽 기반 문제 조회
        recommendations = []
        for topic in weak_topics[:3]:
            result = self.db.table("base_problems").select(
                "id, original_id, name, difficulty, tags"
            ).contains("tags", [topic]).limit(5).execute()

            for p in (result.data or []):
                pid = str(p.get("id"))
                if pid not in solved_ids and len(recommendations) < 5:
                    score = skill_by_topic.get(topic, 0.5)
                    recommendations.append({
                        "id": pid,
                        "originalId": p.get("original_id"),
                        "name": p.get("name", "Unknown"),
                        "difficulty": p.get("difficulty", "medium"),
                        "topic": topic,
                        "reason": f"{topic} 실력 향상을 위한 추천 (현재 {int(score*100)}%)",
                    })

        return recommendations[:5]
