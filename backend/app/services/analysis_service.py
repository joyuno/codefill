"""Analysis Service - AI 기반 학습 분석 및 리포트 생성."""

import json
import logging
from uuid import UUID
from datetime import datetime
from typing import Optional, List, Dict, Any, Set

from ..config import get_settings, get_logger
from ..services.openrouter import openrouter_service
from ..prompts.analysis_agent import ANALYSIS_SYSTEM_PROMPT
from ..services.metrics_calculator import MetricsCalculator, BKTParams

logger = get_logger(__name__)
settings = get_settings()

# 토픽 정규화 맵 (중복 토픽명 → 표준 토픽명)
# 같은 토픽이 다른 이름으로 저장되는 것을 방지
TOPIC_NORMALIZE_MAP = {
    # DP 관련
    "dynamic programming": "DP",
    "Dynamic Programming": "DP",
    "Dynamic programming": "DP",
    "동적 프로그래밍": "DP",
    "Memoization": "DP",
    # BFS 관련
    "Breadth First Search": "BFS",
    "Breadth-first search": "BFS",
    "breadth first search": "BFS",
    "너비 우선 탐색": "BFS",
    # DFS 관련
    "Depth First Search": "DFS",
    "Depth-first search": "DFS",
    "depth first search": "DFS",
    "깊이 우선 탐색": "DFS",
    # Binary Search 관련
    "Binary Search": "Binary Search",
    "binary search": "Binary Search",
    "이진 탐색": "Binary Search",
    # Two Pointers 관련
    "Two Pointers": "Two Pointers",
    "Two pointers": "Two Pointers",
    "two pointers": "Two Pointers",
    "투 포인터": "Two Pointers",
    # Sliding Window 관련
    "Sliding Window": "Sliding Window",
    "Sliding window": "Sliding Window",
    "sliding window": "Sliding Window",
    "슬라이딩 윈도우": "Sliding Window",
    # Graph 관련
    "Graph algorithms": "Graph",
    "Graph traversal": "Graph",
    "graph algorithms": "Graph",
    "그래프": "Graph",
    # Data Structures 관련
    "Data structures": "Data Structures",
    "data structures": "Data Structures",
    "자료구조": "Data Structures",
    # Implementation 관련
    "implementation": "Implementation",
    "구현": "Implementation",
    # String 관련
    "String algorithms": "String",
    "string algorithms": "String",
    "문자열": "String",
    # Sorting 관련
    "sorting": "Sorting",
    "정렬": "Sorting",
    # Greedy 관련
    "Greedy algorithms": "Greedy",
    "greedy algorithms": "Greedy",
    "그리디": "Greedy",
}


def normalize_topic(topic: str) -> str:
    """토픽명을 표준 형태로 정규화."""
    return TOPIC_NORMALIZE_MAP.get(topic, topic)


def merge_topic_stats(stats: Dict[str, Any], is_bkt: bool = False) -> Dict[str, Any]:
    """중복 토픽을 병합하여 정규화된 통계 반환."""
    merged: Dict[str, Any] = {}

    for topic, value in stats.items():
        normalized = normalize_topic(topic)

        if normalized not in merged:
            merged[normalized] = value
        else:
            # 중복 토픽 병합
            if is_bkt:
                # BKT: attempt_count, correct_count 합산, mastery 재계산
                existing = merged[normalized]
                existing["attempt_count"] += value["attempt_count"]
                existing["correct_count"] += value["correct_count"]
                # mastery는 더 높은 값 사용 (또는 평균)
                existing["mastery"] = max(existing["mastery"], value["mastery"])
                existing["is_mastered"] = existing["mastery"] >= 0.8
            else:
                # skill_by_topic: 평균값 사용
                merged[normalized] = (merged[normalized] + value) / 2

    return merged


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
        self.metrics = MetricsCalculator()

    async def get_latest_report(self, user_id: UUID) -> Optional[Dict[str, Any]]:
        """최신 분석 리포트 조회."""
        result = self.db.table("user_analysis_reports").select("*").eq(
            "user_id", str(user_id)
        ).execute()

        if not result.data or len(result.data) == 0:
            return None

        data = result.data[0]  # 첫 번째 row 사용

        # 실시간 시각화 데이터 조회 (LLM 분석 스킵 - DB 저장값 사용)
        viz_data = await self._get_visualization_data(user_id, skip_llm=True)

        return {
            "id": data.get("id"),
            "summaryText": data.get("summary_text"),
            "strengths": data.get("strengths", []),
            "weaknesses": data.get("weaknesses", []),
            "recommendations": data.get("recommendations", []),
            "studyPlan": data.get("study_plan", ""),
            "skillSnapshot": data.get("skill_snapshot", {}),
            "statsSnapshot": data.get("stats_snapshot", {}),
            "difficultySnapshot": data.get("difficulty_snapshot", {}),
            "recommendedProblems": data.get("recommended_problems", []),
            "createdAt": data.get("created_at"),
            # 새로 추가된 필드들
            "conceptsStruggling": data.get("concepts_struggling", []),
            "conceptsLearned": data.get("concepts_learned", []),
            "hintUsage": data.get("hint_usage", {}),
            "commonErrorPatterns": data.get("common_error_patterns", {}),
            "moodDistribution": data.get("mood_distribution", {}),
            "breakthroughMoments": data.get("breakthrough_moments", []),
            "teachingNotes": data.get("teaching_notes", []),
            # AI 코칭 피드백
            "detailedFeedback": data.get("detailed_feedback"),
            # 학습 분석 프레임워크 메트릭
            "bktMastery": data.get("bkt_mastery", {}),
            "bloomMetrics": data.get("bloom_metrics", {}),
            # ELO 성장 데이터
            "eloHistory": data.get("elo_history", []),
            "eloOverall": data.get("elo_overall"),
            # 시각화 데이터 (DB 통계 + 저장된 LLM 분석)
            "problemTypeStats": viz_data.get("problemTypeStats", []),
            "recent10Attempts": viz_data.get("recent10Attempts", []),
            "recent10Analysis": data.get("recent_10_analysis"),  # DB에서 가져옴
            "hintIndependence": viz_data.get("hintIndependence", {}),
        }

    async def _get_visualization_data(self, user_id: UUID, skip_llm: bool = False) -> Dict[str, Any]:
        """실시간 시각화 데이터 조회.

        Args:
            user_id: 사용자 ID
            skip_llm: True면 LLM 분석 스킵 (페이지 로딩 시 사용)
        """

        # 1. 문제 유형별 정답률 (상위 5개)
        problem_type_result = self.db.table("attempts").select(
            "problem_type, is_correct"
        ).eq("user_id", str(user_id)).not_.is_("is_correct", "null").not_.is_("problem_type", "null").execute()

        problem_type_stats = []
        if problem_type_result.data:
            type_stats: Dict[str, Dict[str, int]] = {}
            for attempt in problem_type_result.data:
                ptype = attempt.get("problem_type")
                is_correct = attempt.get("is_correct", False)
                if ptype:
                    if ptype not in type_stats:
                        type_stats[ptype] = {"success": 0, "total": 0}
                    type_stats[ptype]["total"] += 1
                    if is_correct:
                        type_stats[ptype]["success"] += 1

            sorted_types = sorted(
                type_stats.items(),
                key=lambda x: x[1]["total"],
                reverse=True
            )[:5]

            problem_type_stats = [
                {
                    "type": ptype,
                    "total": stats["total"],
                    "success": stats["success"],
                    "rate": round(stats["success"] / stats["total"], 2) if stats["total"] > 0 else 0
                }
                for ptype, stats in sorted_types
            ]

        # 2. 최근 10문제 결과
        recent_attempts_result = self.db.table("attempts").select(
            "problem_name, problem_type, difficulty, topics, is_correct, hints_used, created_at"
        ).eq("user_id", str(user_id)).not_.is_("is_correct", "null").order(
            "created_at", desc=True
        ).limit(10).execute()

        recent_10_attempts = []
        if recent_attempts_result.data:
            recent_10_attempts = [
                {
                    "problem_name": a.get("problem_name", "Unknown"),
                    "problem_type": a.get("problem_type"),
                    "difficulty": a.get("difficulty"),
                    "topics": a.get("topics", []),
                    "is_correct": a.get("is_correct"),
                    "hints_used": a.get("hints_used", 0),
                    "created_at": a.get("created_at"),
                }
                for a in recent_attempts_result.data
            ]

        # 최근 10문제 LLM 분석 (skip_llm이면 스킵)
        recent_analysis = None
        if not skip_llm:
            recent_analysis = await self._analyze_recent_attempts(recent_10_attempts)

        # 3. 힌트 없이 해결 비율
        hint_result = self.db.table("attempts").select(
            "is_correct, hints_used"
        ).eq("user_id", str(user_id)).not_.is_("is_correct", "null").execute()

        hint_independence = {
            "solved_without_hint": 0,
            "solved_with_hint": 0,
            "failed_with_hint": 0,
            "failed_without_hint": 0,
            "total": 0,
            "independence_rate": 0,
        }

        if hint_result.data:
            solved_without_hint = 0
            solved_with_hint = 0
            failed_with_hint = 0
            failed_without_hint = 0

            for attempt in hint_result.data:
                is_correct = attempt.get("is_correct", False)
                hints_used = attempt.get("hints_used") or 0

                if is_correct and hints_used == 0:
                    solved_without_hint += 1
                elif is_correct and hints_used > 0:
                    solved_with_hint += 1
                elif not is_correct and hints_used > 0:
                    failed_with_hint += 1
                else:
                    failed_without_hint += 1

            total = len(hint_result.data)
            hint_independence = {
                "solved_without_hint": solved_without_hint,
                "solved_with_hint": solved_with_hint,
                "failed_with_hint": failed_with_hint,
                "failed_without_hint": failed_without_hint,
                "total": total,
                "independence_rate": round(solved_without_hint / total, 2) if total > 0 else 0,
            }

        return {
            "problemTypeStats": problem_type_stats,
            "recent10Attempts": recent_10_attempts,
            "recent10Analysis": recent_analysis,
            "hintIndependence": hint_independence,
        }

    async def generate_analysis(self, user_id: UUID) -> Dict[str, Any]:
        """AI 분석 실행 및 저장."""

        # 1. 사용자 데이터 수집 (분석용)
        user_data = await self._collect_user_data(user_id)

        # 1-1. ELO 데이터 직접 조회 (분석 로직과 독립 - 시각화용)
        elo_result = self.db.table("user_analysis_reports").select(
            "elo_history, elo_overall"
        ).eq("user_id", str(user_id)).execute()

        elo_history = []
        elo_overall = None
        if elo_result.data and len(elo_result.data) > 0:
            elo_history = elo_result.data[0].get("elo_history") or []
            elo_overall = elo_result.data[0].get("elo_overall")

        # 2. 데이터 충분한지 확인 (BKT 신뢰도를 위해 최소 10문제 필요)
        problems_solved = user_data.get("problems_solved", 0)
        if problems_solved < 10:
            raise InsufficientDataError(f"분석을 위해 최소 10개 이상의 문제를 풀어주세요. (현재 {problems_solved}개)")

        # 3. 분석 생성 (LLM 사용, 실패 시 템플릿 폴백)
        analysis = await self._generate_analysis_with_llm(user_data)

        # 3-1. 최근 10문제 LLM 분석 (별도 호출)
        recent_attempts = user_data.get("recent_10_attempts", [])
        recent_analysis = await self._analyze_recent_attempts(recent_attempts)

        # 4. DB 저장 (upsert) - 새 필드들 포함 (문제 추천은 별도 API로 분리)
        report_data = {
            "user_id": str(user_id),
            "summary_text": analysis["summary"],
            "strengths": analysis["strengths"],
            "weaknesses": analysis["weaknesses"],
            "recommendations": analysis.get("recommendations", []),
            "study_plan": analysis.get("study_plan", ""),
            "skill_snapshot": user_data.get("skill_by_topic", {}),
            "stats_snapshot": {
                "level": user_data.get("level", 1),
                "problemsSolved": user_data.get("problems_solved", 0),
                "accuracy": user_data.get("accuracy", 0),
                "streak": user_data.get("streak", 0),
            },
            "difficulty_snapshot": user_data.get("difficulty_stats", {}),
            "recommended_problems": [],  # 별도 API로 분리됨
            # 새로 추가된 필드들
            "concepts_struggling": user_data.get("concepts_struggling", []),
            "concepts_learned": user_data.get("concepts_learned", []),
            "hint_usage": user_data.get("hint_usage", {}),
            "common_error_patterns": analysis.get("common_error_patterns") if analysis.get("common_error_patterns") is not None else user_data.get("common_error_patterns", {}),
            "mood_distribution": user_data.get("mood_distribution", {}),
            "breakthrough_moments": user_data.get("breakthrough_moments", []),
            "teaching_notes": user_data.get("teaching_notes", []),
            # AI 코칭 피드백
            "detailed_feedback": analysis.get("detailed_feedback"),
            # 학습 분석 프레임워크 메트릭
            "bkt_mastery": user_data.get("bkt_mastery", {}),
            "bloom_metrics": user_data.get("bloom_metrics", {}),
            # BKT 기반 강점/약점 토픽
            "weak_topics": user_data.get("weak_topics", []),
            "strong_topics": user_data.get("strong_topics", []),
            # 최근 10문제 LLM 분석 결과
            "recent_10_analysis": recent_analysis,
        }

        # Update or Insert (ELO 필드는 건드리지 않음 - update_user_elo()가 관리)
        existing = self.db.table("user_analysis_reports").select("user_id").eq("user_id", str(user_id)).execute()

        if existing.data and len(existing.data) > 0:
            # 기존 데이터 있으면 update (ELO 필드 제외)
            self.db.table("user_analysis_reports").update(report_data).eq("user_id", str(user_id)).execute()
        else:
            # 새 사용자면 insert
            self.db.table("user_analysis_reports").insert(report_data).execute()

        return {
            "id": None,  # Will be generated
            "summaryText": analysis["summary"],
            "strengths": analysis["strengths"],
            "weaknesses": analysis["weaknesses"],
            "recommendations": analysis.get("recommendations", []),
            "studyPlan": analysis.get("study_plan", ""),
            "skillSnapshot": user_data.get("skill_by_topic", {}),
            "statsSnapshot": report_data["stats_snapshot"],
            "difficultySnapshot": user_data.get("difficulty_stats", {}),
            "recommendedProblems": [],  # 별도 API로 분리됨
            "createdAt": datetime.utcnow().isoformat(),
            # 새로 추가된 필드들
            "conceptsStruggling": user_data.get("concepts_struggling", []),
            "conceptsLearned": user_data.get("concepts_learned", []),
            "hintUsage": user_data.get("hint_usage", {}),
            "commonErrorPatterns": analysis.get("common_error_patterns") or user_data.get("common_error_patterns", []),
            "moodDistribution": user_data.get("mood_distribution", {}),
            "breakthroughMoments": user_data.get("breakthrough_moments", []),
            "teachingNotes": user_data.get("teaching_notes", []),
            # AI 코칭 피드백
            "detailedFeedback": analysis.get("detailed_feedback", ""),
            # 학습 분석 프레임워크 메트릭
            "bktMastery": user_data.get("bkt_mastery", {}),
            "bloomMetrics": user_data.get("bloom_metrics", {}),
            # 새로운 시각화 데이터
            "problemTypeStats": user_data.get("problem_type_stats", []),
            "recent10Attempts": user_data.get("recent_10_attempts", []),
            "recent10Analysis": recent_analysis,
            "hintIndependence": user_data.get("hint_independence", {}),
            # ELO 성장 데이터 (DB에서 직접 조회한 값 사용)
            "eloHistory": elo_history,
            "eloOverall": elo_overall,
        }

    async def recommend_problems(self, user_id: UUID) -> List[Dict[str, Any]]:
        """
        추천 문제 조회 (별도 API).

        분석 생성과 분리하여 사용자가 명시적으로 요청할 때만 실행.
        약점 기반 문제 추천을 수행하고 DB에 저장.
        """
        # 1. 사용자 데이터 수집
        user_data = await self._collect_user_data(user_id)

        # 2. 추천 문제 조회
        recommended = await self._get_recommended_problems(user_id, user_data)

        # 3. DB에 추천 문제 업데이트
        self.db.table("user_analysis_reports").update({
            "recommended_problems": recommended
        }).eq("user_id", str(user_id)).execute()

        return recommended

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
            "learning_style, common_error_patterns, elo_history, elo_overall"
        ).eq("user_id", str(user_id)).execute()

        use_cached_skill = (
            skill_result.data and
            len(skill_result.data) > 0 and
            skill_result.data[0].get("skill_by_topic")  # 스킬 데이터가 실제로 있는지 확인
        )

        if use_cached_skill:
            # ✅ HEAD 방식: user_analysis_reports에서 ELO 기반 스킬 데이터 사용
            skill = skill_result.data[0]
            raw_skill = skill.get("skill_by_topic", {})
            # 중복 토픽 정규화 (예: DP와 Dynamic Programming 병합)
            data["skill_by_topic"] = merge_topic_stats(raw_skill, is_bkt=False)
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

            # ELO 성장 데이터
            data["elo_history"] = skill.get("elo_history", [])
            data["elo_overall"] = skill.get("elo_overall")
            logger.debug(f"[ELO DEBUG] skill.elo_history: {skill.get('elo_history')}")
            logger.debug(f"[ELO DEBUG] skill.elo_overall: {skill.get('elo_overall')}")

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
        # 최근 500개만 가져와서 BKT 시퀀스 구성 (최신순 정렬 후 역순으로 시간순 변환)
        attempts_result = self.db.table("attempts").select(
            "topics, difficulty, is_correct, created_at"
        ).eq("user_id", str(user_id)).not_.is_("is_correct", "null").order(
            "created_at", desc=True  # 최신순으로 가져옴
        ).limit(500).execute()

        # BKT는 시간순(오래된 것 먼저)이 필요하므로 역순 정렬
        class AttemptsWrapper:
            def __init__(self, data):
                self.data = list(reversed(data)) if data else []

        attempts_for_skill = AttemptsWrapper(attempts_result.data)

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
            raw_skill_by_topic = {}
            weak_topics = []
            strong_topics = []

            for topic, stats in topic_stats.items():
                if stats["total"] > 0:
                    rate = round(stats["success"] / stats["total"], 2)
                    raw_skill_by_topic[topic] = rate

            # 중복 토픽 정규화 (예: DP와 Dynamic Programming 병합)
            skill_by_topic = merge_topic_stats(raw_skill_by_topic, is_bkt=False)

            # 정규화된 데이터로 weak/strong 판정
            for topic, rate in skill_by_topic.items():
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

        # ============================================
        # 학습 분석 프레임워크 메트릭 계산
        # ============================================

        # 4-1. BKT (Bayesian Knowledge Tracing) 계산
        # 토픽별 정답/오답 시퀀스 구성 (시간순)
        topic_sequences: Dict[str, List[bool]] = {}
        if attempts_for_skill.data:
            for attempt in attempts_for_skill.data:
                is_correct = attempt.get("is_correct", False)
                topics = attempt.get("topics") or []
                for topic in topics:
                    if topic not in topic_sequences:
                        topic_sequences[topic] = []
                    topic_sequences[topic].append(bool(is_correct))

        # BKT 마스터리 계산
        bkt_results = self.metrics.calculate_all_topics_bkt(topic_sequences)
        raw_bkt = {
            topic: {
                "mastery": result.mastery,
                "is_mastered": result.is_mastered,
                "attempt_count": result.attempt_count,
                "correct_count": result.correct_count,
            }
            for topic, result in bkt_results.items()
        }
        # 중복 토픽 정규화 (예: DP와 Dynamic Programming 병합)
        data["bkt_mastery"] = merge_topic_stats(raw_bkt, is_bkt=True)

        # 4-1-1. BKT 기반으로 weak_topics, strong_topics 재계산
        # (기존 단순 정답률 대신 BKT mastery 사용)
        bkt_based_weak = []
        bkt_based_strong = []
        for topic, bkt_data in data["bkt_mastery"].items():
            mastery = bkt_data["mastery"]
            if mastery < 0.5:
                bkt_based_weak.append(topic)
            elif mastery >= 0.8:
                bkt_based_strong.append(topic)

        data["weak_topics"] = bkt_based_weak
        data["strong_topics"] = bkt_based_strong

        # 4-2. Bloom's Taxonomy 메트릭 계산
        # difficulty_stats를 Bloom 형식으로 변환
        difficulty_for_bloom = data.get("difficulty_stats", {})
        bloom_input: Dict[str, Dict[str, int]] = {}

        # attempts_for_skill에서 난이도별 성공/전체 집계
        if attempts_for_skill.data:
            for attempt in attempts_for_skill.data:
                difficulty = attempt.get("difficulty")
                is_correct = attempt.get("is_correct", False)
                if difficulty:
                    if difficulty not in bloom_input:
                        bloom_input[difficulty] = {"success": 0, "total": 0}
                    bloom_input[difficulty]["total"] += 1
                    if is_correct:
                        bloom_input[difficulty]["success"] += 1

        bloom_result = self.metrics.calculate_bloom_metrics(bloom_input)
        data["bloom_metrics"] = {
            "apply_rate": bloom_result.apply_rate,
            "analyze_rate": bloom_result.analyze_rate,
            "create_rate": bloom_result.create_rate,
            "current_level": bloom_result.current_level,
            "next_level": bloom_result.next_level,
            "gap_analysis": bloom_result.gap_analysis,
        }

        # 5. user_memories - 최근 학습 세션 기록
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

            # learning_style는 LLM이 생성 (hint_usage 기반)
            # common_error_patterns은 learning_insights에서 추출
            if learning_insights_list:
                latest_insights = learning_insights_list[0]
                data["common_error_patterns"] = latest_insights.get("common_errors", {})

        # 5. attempt_details + hint_logs - 힌트 사용 패턴 및 오류 분석
        # 최근 시도들의 ID 조회
        recent_attempts = self.db.table("attempts").select(
            "id, base_problem_id"
        ).eq("user_id", str(user_id)).order(
            "created_at", desc=True
        ).limit(50).execute()

        if recent_attempts.data and len(recent_attempts.data) > 0:
            attempt_ids = [a["id"] for a in recent_attempts.data]
            problem_ids = list(set(
                str(a.get("base_problem_id")) for a in recent_attempts.data
                if a.get("base_problem_id")
            ))

            # ============ DEBUG: problem_ids 확인 (나중에 삭제할 것) ============
            print(f"\n🔍 [DEBUG] recent_attempts count: {len(recent_attempts.data)}")
            print(f"🔍 [DEBUG] problem_ids: {problem_ids}")
            print(f"🔍 [DEBUG] problem_ids count: {len(problem_ids)}")
            base_problem_ids_raw = [a.get("base_problem_id") for a in recent_attempts.data]
            print(f"🔍 [DEBUG] base_problem_id values (raw): {base_problem_ids_raw[:10]}...")  # 처음 10개만
            # ============ DEBUG END ============

            # attempt_details 조회 (에러 패턴 분석을 위해 blank_user_answer, blank_correct_answer 포함)
            details_result = self.db.table("attempt_details").select(
                "action_type, blank_hint_level, blank_is_correct, "
                "hint_was_requested, hint_was_helpful, blank_user_answer, blank_correct_answer"
            ).in_("attempt_id", attempt_ids).execute()

            # hint_logs 조회 (추가)
            hint_logs_result = self.db.table("hint_logs").select(
                "hint_level, xp_cost, problem_id"
            ).eq("user_id", str(user_id)).order(
                "created_at", desc=True
            ).limit(100).execute()

            # attempt_details 분석
            total_hints_requested = 0
            helpful_hints = 0
            hint_levels_from_details = []
            blank_correct_count = 0
            blank_total_count = 0

            if details_result.data and len(details_result.data) > 0:
                for detail in details_result.data:
                    # 힌트 요청 횟수
                    if detail.get("hint_was_requested"):
                        total_hints_requested += 1
                        if detail.get("hint_was_helpful"):
                            helpful_hints += 1

                    # 힌트 레벨 분포
                    hint_level = detail.get("blank_hint_level")
                    if hint_level is not None:
                        hint_levels_from_details.append(hint_level)

                    # 빈칸 정답률
                    if detail.get("blank_is_correct") is not None:
                        blank_total_count += 1
                        if detail.get("blank_is_correct"):
                            blank_correct_count += 1

            # hint_logs 분석 (레벨별 힌트 사용 횟수)
            by_level: Dict[str, int] = {}
            total_from_logs = 0
            problems_with_hints: Set[str] = set()

            if hint_logs_result.data and len(hint_logs_result.data) > 0:
                for log in hint_logs_result.data:
                    hint_level = log.get("hint_level")
                    if hint_level is not None:
                        level_key = str(hint_level)
                        by_level[level_key] = by_level.get(level_key, 0) + 1
                        total_from_logs += 1

                    problem_id = log.get("problem_id")
                    if problem_id:
                        problems_with_hints.add(str(problem_id))

            # 힌트 사용 통계 집계
            total_hints = max(total_hints_requested, total_from_logs)
            # base_problem_id가 NULL일 경우 problems_solved를 폴백으로 사용
            num_problems = len(problem_ids) if problem_ids else data.get("problems_solved", 1)
            avg_per_problem = round(total_hints / num_problems, 2) if num_problems > 0 else 0

            data["hint_usage"] = {
                "total_requested": total_hints,
                "by_level": by_level,
                "helpful_count": helpful_hints,
                "helpful_rate": round(helpful_hints / total_hints_requested, 2) if total_hints_requested > 0 else 0,
                "avg_per_problem": avg_per_problem,
                "avg_hint_level": round(sum(hint_levels_from_details) / len(hint_levels_from_details), 2) if hint_levels_from_details else 0,
            }
            data["blank_accuracy"] = round(
                blank_correct_count / blank_total_count, 2
            ) if blank_total_count > 0 else None

        # ============================================
        # 새로운 시각화용 데이터 수집
        # ============================================

        # 6. 문제 유형별 정답률 (상위 5개)
        problem_type_result = self.db.table("attempts").select(
            "problem_type, is_correct"
        ).eq("user_id", str(user_id)).not_.is_("is_correct", "null").not_.is_("problem_type", "null").execute()

        if problem_type_result.data:
            type_stats: Dict[str, Dict[str, int]] = {}
            for attempt in problem_type_result.data:
                ptype = attempt.get("problem_type")
                is_correct = attempt.get("is_correct", False)
                if ptype:
                    if ptype not in type_stats:
                        type_stats[ptype] = {"success": 0, "total": 0}
                    type_stats[ptype]["total"] += 1
                    if is_correct:
                        type_stats[ptype]["success"] += 1

            # 시도 횟수 기준 상위 5개
            sorted_types = sorted(
                type_stats.items(),
                key=lambda x: x[1]["total"],
                reverse=True
            )[:5]

            data["problem_type_stats"] = [
                {
                    "type": ptype,
                    "total": stats["total"],
                    "success": stats["success"],
                    "rate": round(stats["success"] / stats["total"], 2) if stats["total"] > 0 else 0
                }
                for ptype, stats in sorted_types
            ]
        else:
            data["problem_type_stats"] = []

        # 7. 최근 10문제 결과
        recent_attempts_result = self.db.table("attempts").select(
            "problem_name, problem_type, difficulty, topics, is_correct, hints_used, created_at"
        ).eq("user_id", str(user_id)).not_.is_("is_correct", "null").order(
            "created_at", desc=True
        ).limit(10).execute()

        if recent_attempts_result.data:
            data["recent_10_attempts"] = [
                {
                    "problem_name": a.get("problem_name", "Unknown"),
                    "problem_type": a.get("problem_type"),
                    "difficulty": a.get("difficulty"),
                    "topics": a.get("topics", []),
                    "is_correct": a.get("is_correct"),
                    "hints_used": a.get("hints_used", 0),
                    "created_at": a.get("created_at"),
                }
                for a in recent_attempts_result.data
            ]
        else:
            data["recent_10_attempts"] = []

        # 8. 힌트 없이 해결 비율
        hint_independence_result = self.db.table("attempts").select(
            "is_correct, hints_used"
        ).eq("user_id", str(user_id)).not_.is_("is_correct", "null").execute()

        if hint_independence_result.data:
            solved_without_hint = 0
            solved_with_hint = 0
            failed_with_hint = 0
            failed_without_hint = 0

            for attempt in hint_independence_result.data:
                is_correct = attempt.get("is_correct", False)
                hints_used = attempt.get("hints_used") or 0

                if is_correct and hints_used == 0:
                    solved_without_hint += 1
                elif is_correct and hints_used > 0:
                    solved_with_hint += 1
                elif not is_correct and hints_used > 0:
                    failed_with_hint += 1
                else:
                    failed_without_hint += 1

            total = len(hint_independence_result.data)
            data["hint_independence"] = {
                "solved_without_hint": solved_without_hint,
                "solved_with_hint": solved_with_hint,
                "failed_with_hint": failed_with_hint,
                "failed_without_hint": failed_without_hint,
                "total": total,
                "independence_rate": round(solved_without_hint / total, 2) if total > 0 else 0,
            }
        else:
            data["hint_independence"] = {
                "solved_without_hint": 0,
                "solved_with_hint": 0,
                "failed_with_hint": 0,
                "failed_without_hint": 0,
                "total": 0,
                "independence_rate": 0,
            }

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
                model=settings.llm_model_analysis,  # gemini-flash
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": "위 데이터를 분석해주세요."}
                ],
                temperature=0.7,
                max_tokens=3000,
                response_format={"type": "json_object"},
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

        # common_error_patterns 정규화
        error_patterns = result.get("common_error_patterns", [])
        if not error_patterns:
            error_patterns = user_data.get("existing_error_patterns", [])

        # recommendations 정규화
        recommendations = result.get("recommendations", [])
        if not recommendations:
            recommendations = ["꾸준히 문제를 풀며 실력을 쌓아가세요!"]

        # study_plan 정규화
        study_plan = result.get("study_plan", "")
        if not study_plan:
            study_plan = "다양한 유형의 문제에 도전해보세요!"

        return {
            "summary": result.get("summary", "분석 결과를 생성했습니다."),
            "strengths": strengths,
            "weaknesses": weaknesses,
            "recommendations": recommendations,
            "study_plan": study_plan,
            "common_error_patterns": error_patterns,
            "detailed_feedback": result.get("detailed_feedback", ""),
        }

    async def _analyze_recent_attempts(self, recent_attempts: List[Dict[str, Any]]) -> str:
        """최근 10문제 결과를 LLM으로 간단히 분석."""
        if not recent_attempts:
            return "최근 풀이 기록이 없습니다."

        try:
            # 간단한 통계 계산
            total = len(recent_attempts)
            correct = sum(1 for a in recent_attempts if a.get("is_correct"))
            with_hints = sum(1 for a in recent_attempts if (a.get("hints_used") or 0) > 0)

            # 연속 성공/실패 패턴 찾기
            results = [a.get("is_correct") for a in recent_attempts]
            streak_info = self._find_streak_pattern(results)

            prompt = f"""최근 10문제 풀이 결과를 2-3문장으로 간단히 분석해주세요.

데이터:
- 정답: {correct}/{total}
- 힌트 사용: {with_hints}문제
- 결과 패턴 (최근→과거): {['✓' if r else '✗' for r in results]}
- 연속 패턴: {streak_info}

규칙:
1. 한국어로 작성
2. 격려보다 객관적 사실 중심
3. 2-3문장 이내
4. 개선 포인트 1개 제안

예시: "최근 10문제 중 7문제를 맞혔습니다. 마지막 3문제 연속 정답으로 상승세입니다. 힌트 의존도를 줄이면 더 빠른 성장이 가능합니다."
"""

            response = await openrouter_service.chat_completion(
                model=settings.llm_model_analysis,  # gemini-flash
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200,
            )

            content = openrouter_service.get_content(response)
            return content.strip()

        except Exception as e:
            logger.warning(f"최근 시도 분석 실패: {e}")
            # 폴백: 간단한 통계 기반 메시지
            correct = sum(1 for a in recent_attempts if a.get("is_correct"))
            total = len(recent_attempts)
            return f"최근 {total}문제 중 {correct}문제를 맞혔습니다. (정답률 {round(correct/total*100)}%)"

    def _find_streak_pattern(self, results: List[bool]) -> str:
        """연속 성공/실패 패턴 찾기."""
        if not results:
            return "기록 없음"

        # 최근부터 연속 패턴 확인
        current = results[0]
        streak = 1
        for r in results[1:]:
            if r == current:
                streak += 1
            else:
                break

        if current:
            return f"최근 {streak}연속 정답"
        else:
            return f"최근 {streak}연속 오답"

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

        # Common error patterns (기존 데이터 유지 또는 빈 배열)
        error_patterns = user_data.get("existing_error_patterns", [])

        # Generate a basic detailed feedback for template fallback
        detailed_parts = []
        detailed_parts.append("## 학습 현황 분석\n")
        detailed_parts.append(f"현재까지 {problems_solved}개의 문제를 풀었고, 정답률은 {int(accuracy * 100)}%입니다.\n\n")

        if strengths:
            detailed_parts.append("### 강점\n")
            for s in strengths[:2]:
                detailed_parts.append(f"- **{s['topic']}**: {s['insight']}\n")
            detailed_parts.append("\n")

        if weaknesses:
            detailed_parts.append("### 개선이 필요한 영역\n")
            for w in weaknesses[:2]:
                detailed_parts.append(f"- **{w['topic']}**: {w['insight']}\n")
            detailed_parts.append("\n")

        detailed_feedback = "".join(detailed_parts)

        return {
            "summary": summary,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "recommendations": recommendations,
            "study_plan": study_plan,
            "common_error_patterns": error_patterns,
            "detailed_feedback": detailed_feedback,
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

    async def get_wrong_problems(
        self,
        user_id: UUID,
        limit: int = 10,
        offset: int = 0,
        sort_by: str = "recent",  # recent, difficulty, hints
        difficulty_filter: Optional[str] = None,  # easy, medium, hard 등
        topic_filter: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        틀린 문제 목록 조회 (복습용).

        - is_correct=false인 시도들 중 최근 것들
        - 같은 문제를 여러 번 틀렸으면 가장 최근 시도만 포함
        - 이미 맞춘 문제는 제외 (복습 완료)
        - 정렬, 필터, 페이지네이션 지원
        """
        # 1. 틀린 시도 조회 (전체)
        wrong_attempts = self.db.table("attempts").select(
            "base_problem_id, problem_name, problem_type, difficulty, topics, hints_used, created_at"
        ).eq("user_id", str(user_id)).eq(
            "is_correct", False
        ).not_.is_("base_problem_id", "null").order(
            "created_at", desc=True
        ).limit(500).execute()

        if not wrong_attempts.data:
            return {"problems": [], "total": 0, "hasMore": False}

        # 2. 맞춘 문제 ID 목록 (복습 완료된 것들 제외용)
        correct_result = self.db.table("attempts").select(
            "base_problem_id"
        ).eq("user_id", str(user_id)).eq(
            "is_correct", True
        ).execute()

        solved_ids: set[str] = {
            str(a.get("base_problem_id"))
            for a in (correct_result.data or [])
            if a.get("base_problem_id")
        }

        # 3. 중복 제거 + 필터링 (같은 문제는 가장 최근 시도만)
        seen_problems: set[str] = set()
        unique_wrong: List[Dict[str, Any]] = []

        for attempt in wrong_attempts.data:
            problem_id = str(attempt.get("base_problem_id"))

            # 이미 맞춘 문제는 제외
            if problem_id in solved_ids:
                continue

            # 중복 제거
            if problem_id in seen_problems:
                continue

            # 난이도 필터
            if difficulty_filter:
                if attempt.get("difficulty") != difficulty_filter:
                    continue

            # 토픽 필터
            if topic_filter:
                topics = attempt.get("topics") or []
                if topic_filter not in topics:
                    continue

            seen_problems.add(problem_id)
            unique_wrong.append(attempt)

        if not unique_wrong:
            return {"problems": [], "total": 0, "hasMore": False}

        # 4. 정렬
        if sort_by == "difficulty":
            # 난이도 순서 정의
            diff_order = {"easy": 0, "medium": 1, "medium_hard": 2, "hard": 3, "very_hard": 4}
            unique_wrong.sort(key=lambda x: diff_order.get(x.get("difficulty", "medium"), 1))
        elif sort_by == "hints":
            # 힌트 많이 사용한 순
            unique_wrong.sort(key=lambda x: x.get("hints_used", 0), reverse=True)
        # else: recent (기본값, 이미 created_at desc로 정렬됨)

        total = len(unique_wrong)

        # 5. 페이지네이션 적용
        paginated = unique_wrong[offset:offset + limit]

        if not paginated:
            return {"problems": [], "total": total, "hasMore": False}

        # 6. base_problems에서 original_id 조회
        problem_ids = [str(a.get("base_problem_id")) for a in paginated]
        problems_result = self.db.table("base_problems").select(
            "id, original_id"
        ).in_("id", problem_ids).execute()

        # ID -> original_id 매핑
        original_id_map: Dict[str, str] = {
            str(p.get("id")): p.get("original_id")
            for p in (problems_result.data or [])
            if p.get("original_id")
        }

        # 7. 응답 형식으로 변환
        problems = [
            {
                "id": str(a.get("base_problem_id")),
                "originalId": original_id_map.get(str(a.get("base_problem_id"))),
                "name": a.get("problem_name", "Unknown"),
                "problemType": a.get("problem_type"),
                "difficulty": a.get("difficulty", "medium"),
                "topics": a.get("topics", []),
                "hintsUsed": a.get("hints_used", 0),
                "lastAttemptAt": a.get("created_at"),
            }
            for a in paginated
        ]

        return {
            "problems": problems,
            "total": total,
            "hasMore": offset + limit < total,
        }
