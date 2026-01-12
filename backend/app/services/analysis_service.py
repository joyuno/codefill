"""Analysis Service - AI 기반 학습 분석 및 리포트 생성."""

import json
import logging
from uuid import UUID
from datetime import datetime
from typing import Optional, List, Dict, Any, Set

from ..config import get_settings, get_logger
from ..services.openrouter import openrouter_service
from ..prompts.analysis_agent import ANALYSIS_SYSTEM_PROMPT

logger = get_logger(__name__)
settings = get_settings()

# 토픽 매핑 (한국어 → 영어 확장) - RAG 서비스와 동일
TOPIC_MAPPING = {
    "DP": ["Dynamic programming", "DP", "Memoization"],
    "동적 프로그래밍": ["Dynamic programming", "DP", "Memoization"],
    "이진 탐색": ["Binary search", "Divide and conquer", "Sorting"],
    "그래프": ["Graph algorithms", "Graph traversal", "BFS", "DFS"],
    "정렬": ["Sorting", "Implementation"],
    "문자열": ["String algorithms", "String"],
    "수학": ["Mathematics", "Number theory", "Math"],
    "그리디": ["Greedy algorithms", "Greedy"],
    "완전 탐색": ["Complete search", "Brute force", "Implementation"],
    "스택": ["Data structures", "Stack"],
    "큐": ["Data structures", "Queue"],
    "해시": ["Data structures", "Hash"],
    "트리": ["Tree algorithms", "Data structures"],
    "재귀": ["Recursion", "Divide and conquer"],
    "미로 탐색": ["BFS", "DFS", "Graph algorithms", "Graph traversal", "Maze"],
    "미로": ["BFS", "DFS", "Graph algorithms", "Graph traversal", "Maze"],
    "bfs": ["BFS", "Graph algorithms", "Graph traversal", "Breadth-first search"],
    "dfs": ["DFS", "Graph algorithms", "Graph traversal", "Depth-first search"],
    "너비 우선 탐색": ["BFS", "Graph algorithms", "Graph traversal", "Breadth-first search"],
    "깊이 우선 탐색": ["DFS", "Graph algorithms", "Graph traversal", "Depth-first search"],
    "최단 경로": ["BFS", "Shortest path", "Graph algorithms", "Dijkstra"],
    "다익스트라": ["Dijkstra", "Shortest path", "Graph algorithms"],
    "플로이드": ["Floyd-Warshall", "Shortest path", "Graph algorithms"],
    "백트래킹": ["Backtracking", "DFS", "Complete search", "Recursion"],
    "분할 정복": ["Divide and conquer", "Recursion"],
    "투 포인터": ["Two pointers", "Sliding window"],
    "슬라이딩 윈도우": ["Sliding window", "Two pointers"],
    "구현": ["Implementation", "Simulation"],
    "시뮬레이션": ["Simulation", "Implementation"],
    "배열": ["Array", "Implementation"],
    "연결 리스트": ["Linked list", "Data structures"],
    "힙": ["Heap", "Priority queue", "Data structures"],
    "우선순위 큐": ["Priority queue", "Heap", "Data structures"],
    "유니온 파인드": ["Union-Find", "Disjoint set", "Graph algorithms"],
    "세그먼트 트리": ["Segment tree", "Data structures", "Range query"],
    "비트마스킹": ["Bitmask", "Bit manipulation"],
}


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

        # 4. DB 저장 (upsert) - 새 필드들 포함
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
            "learning_style": analysis.get("learning_style") if analysis.get("learning_style") is not None else user_data.get("learning_style", {}),
            "common_error_patterns": analysis.get("common_error_patterns") if analysis.get("common_error_patterns") is not None else user_data.get("common_error_patterns", {}),
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

        # 2. 스킬 데이터 수집 (Option A: user_analysis_reports 우선, 폴백으로 attempts 직접 계산)
        # 먼저 user_analysis_reports에서 feedback_service가 계산한 ELO 데이터 조회
        skill_result = self.db.table("user_analysis_reports").select(
            "skill_by_topic, weak_topics, strong_topics, success_rate_by_difficulty, "
            "stats_by_problem_type, total_problems_solved, total_problems_attempted, "
            "avg_solve_time_seconds, avg_hints_per_problem, current_streak, longest_streak, "
            "preferred_problem_type, preferred_language, recent_topics, recent_difficulties, "
            "learning_style, common_error_patterns"
        ).eq("user_id", str(user_id)).execute()

        use_cached_skill = (
            skill_result.data and
            len(skill_result.data) > 0 and
            skill_result.data[0].get("skill_by_topic")  # 스킬 데이터가 실제로 있는지 확인
        )

        if use_cached_skill:
            # ✅ HEAD 방식: user_analysis_reports에서 ELO 기반 스킬 데이터 사용
            skill = skill_result.data[0]
            data["skill_by_topic"] = skill.get("skill_by_topic", {})
            data["weak_topics"] = skill.get("weak_topics", [])
            data["strong_topics"] = skill.get("strong_topics", [])

            # 추가 필드들
            data["stats_by_problem_type"] = skill.get("stats_by_problem_type", {})
            data["total_problems_solved"] = skill.get("total_problems_solved", 0)
            data["total_problems_attempted"] = skill.get("total_problems_attempted", 0)
            data["avg_solve_time_seconds"] = skill.get("avg_solve_time_seconds")
            data["avg_hints_per_problem"] = skill.get("avg_hints_per_problem")
            data["current_streak"] = skill.get("current_streak", 0)
            data["longest_streak"] = skill.get("longest_streak", 0)
            data["preferred_problem_type"] = skill.get("preferred_problem_type")
            data["preferred_language"] = skill.get("preferred_language")
            data["recent_topics"] = skill.get("recent_topics", [])
            data["recent_difficulties"] = skill.get("recent_difficulties", [])
            data["existing_learning_style"] = skill.get("learning_style")
            data["existing_error_patterns"] = skill.get("common_error_patterns")

            # difficulty_stats 변환
            diff_raw = skill.get("success_rate_by_difficulty", {})
            difficulty_stats = {}
            for diff, stats in (diff_raw or {}).items():
                if isinstance(stats, dict):
                    total = stats.get("total", 0)
                    success = stats.get("success", 0)
                    difficulty_stats[diff] = round(success / total, 2) if total > 0 else 0
                else:
                    difficulty_stats[diff] = float(stats) if stats else 0
            data["difficulty_stats"] = difficulty_stats
            data["learning_style"] = skill.get("learning_style") or {}
            data["common_error_patterns"] = skill.get("common_error_patterns") or {}

        else:
            # ✅ ehw 폴백: user_analysis_reports가 없으면 attempts에서 직접 계산
            data["existing_learning_style"] = None
            data["existing_error_patterns"] = None

        # 3. attempts 테이블에서 정확도 및 폴백용 스킬 데이터 계산
        attempts_for_skill = self.db.table("attempts").select(
            "topics, difficulty, is_correct"
        ).eq("user_id", str(user_id)).not_.is_("is_correct", "null").execute()

        # 폴백 계산 (use_cached_skill이 False일 때만 skill_by_topic 덮어쓰기)
        if not use_cached_skill:
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

            # learning_style, common_error_patterns 기본값
            data["learning_style"] = {}
            data["common_error_patterns"] = {}

        # 4. Overall accuracy (attempts 데이터 활용)
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

        # learning_style 정규화
        learning_style = result.get("learning_style")
        if learning_style and isinstance(learning_style, dict):
            learning_style = {
                "type": learning_style.get("type", "independent"),
                "description": learning_style.get("description", ""),
                "strategy": learning_style.get("strategy", ""),
            }
        elif learning_style and isinstance(learning_style, str):
            learning_style = {"type": learning_style, "description": "", "strategy": ""}
        else:
            # 기존 데이터 유지 또는 기본값
            learning_style = user_data.get("existing_learning_style") or {
                "type": "independent",
                "description": "아직 학습 스타일 분석 중입니다.",
                "strategy": "다양한 문제를 풀어보며 자신만의 학습 패턴을 찾아보세요."
            }

        # common_error_patterns 정규화
        error_patterns = result.get("common_error_patterns", [])
        if not error_patterns:
            error_patterns = user_data.get("existing_error_patterns", [])

        return {
            "summary": result.get("summary", "분석 결과를 생성했습니다."),
            "strengths": strengths,
            "weaknesses": weaknesses,
            "recommendations": result.get("recommendations", ["꾸준히 문제를 풀며 실력을 쌓아가세요!"]),
            "study_plan": result.get("study_plan", "다양한 유형의 문제에 도전해보세요!"),
            "learning_style": learning_style,
            "common_error_patterns": error_patterns,
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

        # Learning style (기존 데이터 유지 또는 기본값)
        learning_style = user_data.get("existing_learning_style") or {
            "type": "independent",
            "description": "아직 학습 스타일 분석 중입니다.",
            "strategy": "다양한 문제를 풀어보며 자신만의 학습 패턴을 찾아보세요."
        }

        # Common error patterns (기존 데이터 유지 또는 빈 배열)
        error_patterns = user_data.get("existing_error_patterns", [])

        return {
            "summary": summary,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "recommendations": recommendations,
            "study_plan": study_plan,
            "learning_style": learning_style,
            "common_error_patterns": error_patterns,
        }

    def _expand_topics(self, topics: List[str]) -> List[str]:
        """토픽을 영어 동의어로 확장."""
        expanded = set()
        for topic in topics:
            expanded.add(topic)
            topic_lower = topic.lower()

            # 직접 매핑 확인
            if topic in TOPIC_MAPPING:
                expanded.update(TOPIC_MAPPING[topic])

            # 소문자 매핑 확인
            for key, values in TOPIC_MAPPING.items():
                if key.lower() == topic_lower:
                    expanded.update(values)

        return list(expanded)

    def _get_recommended_difficulty(self, user_data: Dict[str, Any]) -> List[str]:
        """사용자 레벨에 맞는 추천 난이도 반환."""
        accuracy = user_data.get("accuracy", 0.5)
        difficulty_stats = user_data.get("difficulty_stats", {})

        # 정답률 기반 추천
        if accuracy < 0.4:
            return ["easy"]
        elif accuracy < 0.6:
            return ["easy", "medium"]
        elif accuracy < 0.8:
            return ["medium"]
        else:
            return ["medium", "hard"]

    async def _get_problem_success_rates(
        self, problem_ids: List[str]
    ) -> Dict[str, float]:
        """문제별 전체 사용자 정답률 조회."""
        if not problem_ids:
            return {}

        result = self.db.table("attempts").select(
            "base_problem_id, is_correct"
        ).in_("base_problem_id", problem_ids).execute()

        # 문제별 정답률 계산
        stats: Dict[str, Dict[str, int]] = {}
        for attempt in (result.data or []):
            pid = str(attempt.get("base_problem_id"))
            if pid not in stats:
                stats[pid] = {"correct": 0, "total": 0}
            stats[pid]["total"] += 1
            if attempt.get("is_correct"):
                stats[pid]["correct"] += 1

        # 정답률 계산
        rates = {}
        for pid in problem_ids:
            if pid in stats and stats[pid]["total"] > 0:
                rates[pid] = stats[pid]["correct"] / stats[pid]["total"]
            else:
                rates[pid] = 0.5  # 데이터 없으면 기본값

        return rates

    async def _get_recommended_problems(
        self, user_id: UUID, user_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        개선된 약점 기반 추천 문제 조회.

        개선점:
        1. 토픽 매핑 (한국어 → 영어 확장)
        2. 난이도 필터링 (사용자 레벨 기반)
        3. 이미 푼 문제 제외
        4. 역사적 성공률 고려 (50~70% 정답률 우선)
        5. 다양성 확보 (토픽별 최대 2개)
        """
        weak_topics = user_data.get("weak_topics", [])
        skill_by_topic = user_data.get("skill_by_topic", {})

        # 1. 이미 푼 문제 ID 조회
        solved_result = self.db.table("attempts").select(
            "base_problem_id"
        ).eq("user_id", str(user_id)).execute()

        solved_ids: Set[str] = set(
            str(a.get("base_problem_id")) for a in (solved_result.data or [])
            if a.get("base_problem_id")
        )

        # 2. 추천 난이도 결정
        recommended_difficulties = self._get_recommended_difficulty(user_data)

        # 3. 토픽 확장 (한국어 → 영어)
        if weak_topics:
            expanded_topics = self._expand_topics(weak_topics[:3])
        else:
            # 약점 없으면 일반적인 토픽으로
            expanded_topics = ["Implementation", "Array", "String"]

        # 4. 문제 검색 (overlaps 사용)
        try:
            result = self.db.table("base_problems").select(
                "id, original_id, name, difficulty, tags"
            ).overlaps("tags", expanded_topics).in_(
                "difficulty", recommended_difficulties
            ).limit(30).execute()
        except Exception as e:
            # overlaps 실패 시 단순 조회로 폴백
            logger.warning(f"overlaps query failed, falling back: {e}")
            result = self.db.table("base_problems").select(
                "id, original_id, name, difficulty, tags"
            ).in_("difficulty", recommended_difficulties).limit(30).execute()

        # 5. 이미 푼 문제 제외
        candidates = [
            p for p in (result.data or [])
            if str(p.get("id")) not in solved_ids
        ]

        if not candidates:
            # 후보가 없으면 난이도 제한 없이 재검색
            result = self.db.table("base_problems").select(
                "id, original_id, name, difficulty, tags"
            ).limit(10).execute()
            candidates = [
                p for p in (result.data or [])
                if str(p.get("id")) not in solved_ids
            ][:5]

            return [
                {
                    "id": str(p.get("id")),
                    "originalId": p.get("original_id"),
                    "name": p.get("name", "Unknown"),
                    "difficulty": p.get("difficulty", "medium"),
                    "topic": (p.get("tags") or ["general"])[0],
                    "reason": "실력 향상을 위한 추천 문제",
                }
                for p in candidates
            ]

        # 6. 역사적 성공률 조회
        problem_ids = [str(p["id"]) for p in candidates]
        success_rates = await self._get_problem_success_rates(problem_ids)

        # 7. 점수 계산 및 정렬
        scored = []
        for p in candidates:
            pid = str(p["id"])
            success_rate = success_rates.get(pid, 0.5)

            # 50~70% 정답률 선호 (너무 쉽거나 어려우면 감점)
            ideal_rate = 0.6
            rate_score = 1 - abs(success_rate - ideal_rate) * 2
            rate_score = max(0, rate_score)

            # 약점 토픽 매칭 점수
            topic_score = 0
            problem_tags = [t.lower() for t in (p.get("tags") or [])]
            for weak_topic in weak_topics:
                weak_lower = weak_topic.lower()
                # 직접 매칭 또는 확장된 토픽 매칭
                if weak_lower in problem_tags:
                    topic_score = 1
                    break
                expanded = self._expand_topics([weak_topic])
                for exp in expanded:
                    if exp.lower() in problem_tags:
                        topic_score = 0.8
                        break

            total_score = rate_score * 0.5 + topic_score * 0.5
            scored.append((p, total_score, success_rate))

        # 점수 순 정렬
        scored.sort(key=lambda x: x[1], reverse=True)

        # 8. 다양성 확보 (토픽별 최대 2개)
        topic_counts: Dict[str, int] = {}
        recommendations = []

        for p, score, success_rate in scored:
            if len(recommendations) >= 5:
                break

            main_topic = (p.get("tags") or ["general"])[0]
            if topic_counts.get(main_topic, 0) >= 2:
                continue

            topic_counts[main_topic] = topic_counts.get(main_topic, 0) + 1

            # reason에 성공률 정보 추가
            rate_percent = int(success_rate * 100)
            if weak_topics:
                # 약점 토픽 중 매칭되는 것 찾기
                matched_weak = None
                for wt in weak_topics:
                    if wt.lower() in [t.lower() for t in (p.get("tags") or [])]:
                        matched_weak = wt
                        break
                    expanded = self._expand_topics([wt])
                    for exp in expanded:
                        if exp.lower() in [t.lower() for t in (p.get("tags") or [])]:
                            matched_weak = wt
                            break
                    if matched_weak:
                        break

                if matched_weak:
                    user_skill = skill_by_topic.get(matched_weak, 0.5)
                    reason = f"{matched_weak} 실력 향상 추천 (현재 {int(user_skill*100)}%, 정답률 {rate_percent}%)"
                else:
                    reason = f"실력 향상 추천 (정답률 {rate_percent}%)"
            else:
                reason = f"실력 향상 추천 (정답률 {rate_percent}%)"

            recommendations.append({
                "id": str(p.get("id")),
                "originalId": p.get("original_id"),
                "name": p.get("name", "Unknown"),
                "difficulty": p.get("difficulty", "medium"),
                "topic": main_topic,
                "reason": reason,
            })

        return recommendations
