"""
Search Quality Evaluator Service

검색 결과 품질 평가 서비스

측정 가능한 메트릭 기반으로 검색 품질을 평가합니다.
LLM의 주관적 평가가 아닌, 실제 데이터 기반 객관적 평가.

Features:
1. 메타데이터 매칭 점수 (요청-결과 일치도)
2. 역사적 성공률 (CTR, 완료율, 스킵률)
3. 다양성 점수 (결과 세트 내 다양성)
4. 종합 품질 점수 계산

Usage:
    evaluator = get_search_quality_evaluator()
    score = await evaluator.evaluate(request_params, search_results)
    # score: 0.0 ~ 1.0
"""

import logging
from typing import Dict, Any, Optional, List, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

from ..database import get_supabase_client
from ..config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class QualityScore:
    """검색 품질 점수 상세"""
    overall: float              # 종합 점수 (0~1)
    metadata_match: float       # 메타데이터 매칭 점수 (0~1)
    historical_success: float   # 역사적 성공률 (0~1)
    diversity: float            # 다양성 점수 (0~1)
    details: Dict[str, Any]     # 상세 정보

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @property
    def grade(self) -> str:
        """점수 등급 (A~F)"""
        if self.overall >= 0.9:
            return "A"
        elif self.overall >= 0.8:
            return "B"
        elif self.overall >= 0.7:
            return "C"
        elif self.overall >= 0.6:
            return "D"
        else:
            return "F"


@dataclass
class ProblemHistoricalStats:
    """
    문제별 역사적 통계

    데이터 소스:
    - attempts: 실제 시도 데이터 (is_correct, score, time_spent, hints_used)
    - hint_logs: 힌트 요청 상세 (hint_level, xp_cost)
    - user_interactions: 폴백 데이터
    """
    problem_id: str
    # attempts 테이블 기반
    attempt_count: int          # 총 시도 수
    correct_count: int          # 정답 수
    avg_score: float            # 평균 점수
    avg_time_spent: float       # 평균 소요 시간 (초)
    avg_hints_used: float       # 평균 힌트 사용 수
    # hint_logs 테이블 기반
    total_hint_requests: int    # 총 힌트 요청 수
    avg_hint_level: float       # 평균 힌트 레벨 (높을수록 많은 힌트 사용)
    # user_interactions 폴백
    skip_count: int             # 스킵 수

    @property
    def success_rate(self) -> float:
        """정답률 (attempts 기반 - 가장 정확)"""
        return self.correct_count / self.attempt_count if self.attempt_count > 0 else 0.5

    @property
    def difficulty_score(self) -> float:
        """
        난이도 적절성 점수 (0~1)

        - 정답률 50~70%가 이상적 (너무 쉽지도 어렵지도 않음)
        - 힌트 사용 적당함 (1~2개)
        - 소요 시간 적당함
        """
        # 정답률이 50~70% 범위에 가까울수록 높은 점수
        ideal_success_rate = 0.6
        success_deviation = abs(self.success_rate - ideal_success_rate)
        success_score = max(0, 1 - success_deviation * 2)  # 0.6에서 멀어질수록 감소

        # 힌트 사용량 (0~2개가 이상적)
        hint_score = max(0, 1 - self.avg_hints_used / 5)  # 5개 이상이면 0

        return (success_score * 0.7 + hint_score * 0.3)

    @property
    def skip_rate(self) -> float:
        """스킵률"""
        total = self.attempt_count + self.skip_count
        return self.skip_count / total if total > 0 else 0.0


class SearchQualityEvaluator:
    """
    검색 품질 평가기

    세 가지 축으로 검색 품질을 평가:
    1. 메타데이터 매칭 (40%): 요청한 조건과 결과의 일치도
    2. 역사적 성공률 (40%): 과거 사용자들의 행동 데이터
    3. 다양성 (20%): 결과 세트 내 다양성

    Usage:
        evaluator = get_search_quality_evaluator()

        score = await evaluator.evaluate(
            request_params={
                "topics": ["dp", "graph"],
                "difficulty": "medium",
                "language": "python"
            },
            search_results=[...],
            user_id="..."  # 개인화된 평가 (선택)
        )

        print(f"품질 점수: {score.overall:.2f} ({score.grade})")
    """

    # 가중치 설정
    WEIGHT_METADATA = 0.40
    WEIGHT_HISTORICAL = 0.40
    WEIGHT_DIVERSITY = 0.20

    # 캐시 TTL
    STATS_CACHE_TTL = 300  # 5분

    def __init__(self):
        self.db = get_supabase_client()
        self._stats_cache: Dict[str, tuple] = {}  # problem_id -> (stats, timestamp)

    async def evaluate(
        self,
        request_params: Dict[str, Any],
        search_results: List[Dict[str, Any]],
        user_id: Optional[str] = None,
    ) -> QualityScore:
        """
        검색 결과 품질 평가

        Args:
            request_params: 검색 요청 파라미터
                - topics: List[str] - 요청한 주제
                - difficulty: str - 요청한 난이도
                - language: str - 요청한 언어
            search_results: 검색 결과 목록
            user_id: 사용자 ID (개인화된 평가용, 선택)

        Returns:
            QualityScore: 품질 점수 및 상세 정보
        """
        if not search_results:
            return QualityScore(
                overall=0.0,
                metadata_match=0.0,
                historical_success=0.0,
                diversity=0.0,
                details={"error": "검색 결과 없음"}
            )

        # 1. 메타데이터 매칭 점수 (40%)
        metadata_score, metadata_details = self._calculate_metadata_match(
            request_params, search_results
        )

        # 2. 역사적 성공률 점수 (40%)
        historical_score, historical_details = await self._calculate_historical_success(
            search_results
        )

        # 3. 다양성 점수 (20%)
        diversity_score, diversity_details = self._calculate_diversity(search_results)

        # 종합 점수 계산
        overall = (
            metadata_score * self.WEIGHT_METADATA +
            historical_score * self.WEIGHT_HISTORICAL +
            diversity_score * self.WEIGHT_DIVERSITY
        )

        return QualityScore(
            overall=round(overall, 4),
            metadata_match=round(metadata_score, 4),
            historical_success=round(historical_score, 4),
            diversity=round(diversity_score, 4),
            details={
                "result_count": len(search_results),
                "metadata": metadata_details,
                "historical": historical_details,
                "diversity": diversity_details,
                "weights": {
                    "metadata": self.WEIGHT_METADATA,
                    "historical": self.WEIGHT_HISTORICAL,
                    "diversity": self.WEIGHT_DIVERSITY,
                }
            }
        )

    def _calculate_metadata_match(
        self,
        request_params: Dict[str, Any],
        results: List[Dict[str, Any]],
    ) -> tuple[float, Dict[str, Any]]:
        """
        메타데이터 매칭 점수 계산

        - 난이도 일치: 50%
        - 주제 커버리지: 40%
        - 언어 가용성: 10%
        """
        requested_topics = set(t.lower() for t in request_params.get("topics", []))
        requested_difficulty = request_params.get("difficulty", "").lower()
        requested_language = request_params.get("language", "").lower()

        total_score = 0.0
        difficulty_matches = 0
        topic_coverage_sum = 0.0
        language_available = 0

        for result in results:
            result_score = 0.0

            # 난이도 일치 (50%)
            result_difficulty = (result.get("difficulty") or "").lower()
            if result_difficulty == requested_difficulty:
                result_score += 0.5
                difficulty_matches += 1
            elif self._is_adjacent_difficulty(requested_difficulty, result_difficulty):
                result_score += 0.25  # 인접 난이도는 절반 점수

            # 주제 커버리지 (40%)
            result_tags = set(t.lower() for t in result.get("tags", []))
            if requested_topics:
                coverage = len(requested_topics & result_tags) / len(requested_topics)
                result_score += coverage * 0.4
                topic_coverage_sum += coverage
            else:
                result_score += 0.4  # 주제 요청 없으면 만점

            # 언어 가용성 (10%)
            if requested_language:
                solutions = result.get("solutions", [])
                if any(s.get("language", "").lower() == requested_language for s in solutions):
                    result_score += 0.1
                    language_available += 1
            else:
                result_score += 0.1  # 언어 요청 없으면 만점

            total_score += result_score

        avg_score = total_score / len(results) if results else 0.0
        avg_topic_coverage = topic_coverage_sum / len(results) if results else 0.0

        return avg_score, {
            "difficulty_match_rate": difficulty_matches / len(results) if results else 0,
            "avg_topic_coverage": round(avg_topic_coverage, 3),
            "language_available_rate": language_available / len(results) if results else 0,
            "requested": {
                "topics": list(requested_topics),
                "difficulty": requested_difficulty,
                "language": requested_language,
            }
        }

    def _is_adjacent_difficulty(self, d1: str, d2: str) -> bool:
        """두 난이도가 인접한지 확인"""
        order = ["easy", "medium", "medium_hard", "hard", "very_hard"]
        try:
            idx1 = order.index(d1)
            idx2 = order.index(d2)
            return abs(idx1 - idx2) == 1
        except ValueError:
            return False

    async def _calculate_historical_success(
        self,
        results: List[Dict[str, Any]],
    ) -> tuple[float, Dict[str, Any]]:
        """
        역사적 성공률 점수 계산

        데이터 소스 (우선순위):
        1. attempts 테이블: is_correct, score, time_spent, hints_used
        2. hint_logs 테이블: hint_level별 사용량
        3. user_interactions 테이블: 폴백 (skip 등)

        평가 기준:
        - 정답률 (40%): attempts.is_correct 기반
        - 난이도 적절성 (30%): 50~70% 정답률이 이상적
        - 힌트 효율성 (20%): 적당한 힌트 사용 (0~2개)
        - 스킵률 역수 (10%): 낮을수록 좋음
        """
        problem_ids = [r.get("id") for r in results if r.get("id")]

        if not problem_ids:
            return 0.5, {"message": "문제 ID 없음 - 기본값 반환"}

        # 통계 조회 (attempts, hint_logs 포함)
        stats_map = await self._get_problem_stats_batch(problem_ids)

        if not stats_map:
            return 0.5, {"message": "역사적 데이터 없음 - 기본값 반환"}

        total_score = 0.0
        stats_used = 0
        success_sum = 0.0
        difficulty_sum = 0.0
        hint_efficiency_sum = 0.0
        skip_sum = 0.0

        for result in results:
            pid = result.get("id")
            stats = stats_map.get(pid)

            if stats and stats.attempt_count > 0:
                # 정답률 (40%) - attempts 기반
                success_score = stats.success_rate

                # 난이도 적절성 (30%) - 50~70% 정답률이 이상적
                difficulty_score = stats.difficulty_score

                # 힌트 효율성 (20%) - 적당한 힌트 사용
                hint_efficiency = max(0, 1 - stats.avg_hints_used / 5)

                # 스킵률 역수 (10%)
                skip_score = 1.0 - stats.skip_rate

                result_score = (
                    success_score * 0.40 +
                    difficulty_score * 0.30 +
                    hint_efficiency * 0.20 +
                    skip_score * 0.10
                )
                total_score += result_score
                stats_used += 1

                success_sum += stats.success_rate
                difficulty_sum += stats.difficulty_score
                hint_efficiency_sum += hint_efficiency
                skip_sum += stats.skip_rate
            else:
                # 데이터 없는 문제는 기본 점수
                total_score += 0.5
                stats_used += 1

        avg_score = total_score / stats_used if stats_used > 0 else 0.5
        data_count = len([s for s in stats_map.values() if s.attempt_count > 0])

        return avg_score, {
            "data_source": "attempts + hint_logs",
            "problems_with_data": data_count,
            "total_problems": len(problem_ids),
            "avg_success_rate": round(success_sum / data_count, 3) if data_count else 0,
            "avg_difficulty_score": round(difficulty_sum / data_count, 3) if data_count else 0,
            "avg_hint_efficiency": round(hint_efficiency_sum / data_count, 3) if data_count else 0,
            "avg_skip_rate": round(skip_sum / data_count, 3) if data_count else 0,
        }

    async def _get_problem_stats_batch(
        self,
        problem_ids: List[str],
    ) -> Dict[str, ProblemHistoricalStats]:
        """
        문제별 역사적 통계 일괄 조회

        데이터 소스:
        1. attempts 테이블 (주요): is_correct, score, time_spent, hints_used
        2. hint_logs 테이블: hint_level별 상세
        3. user_interactions 테이블 (폴백): skip 이벤트
        """
        result_map = {}

        # 캐시에서 먼저 확인
        uncached_ids = []
        now = datetime.now().timestamp()

        for pid in problem_ids:
            if pid in self._stats_cache:
                stats, cached_at = self._stats_cache[pid]
                if now - cached_at < self.STATS_CACHE_TTL:
                    result_map[pid] = stats
                else:
                    uncached_ids.append(pid)
            else:
                uncached_ids.append(pid)

        if not uncached_ids:
            return result_map

        try:
            # ============================================================
            # 1. attempts 테이블에서 실제 시도 데이터 조회
            # ============================================================
            attempts_response = self.db.table("attempts") \
                .select("problem_id, is_correct, score, time_spent, hints_used") \
                .in_("problem_id", uncached_ids) \
                .gte("created_at", (datetime.now() - timedelta(days=30)).isoformat()) \
                .execute()

            # 문제별 attempts 집계
            attempts_stats: Dict[str, Dict[str, Any]] = {}
            for attempt in (attempts_response.data or []):
                pid = attempt.get("problem_id")
                if not pid:
                    continue

                if pid not in attempts_stats:
                    attempts_stats[pid] = {
                        "count": 0,
                        "correct": 0,
                        "total_score": 0,
                        "total_time": 0,
                        "total_hints": 0,
                    }

                attempts_stats[pid]["count"] += 1
                if attempt.get("is_correct"):
                    attempts_stats[pid]["correct"] += 1
                attempts_stats[pid]["total_score"] += attempt.get("score") or 0
                attempts_stats[pid]["total_time"] += attempt.get("time_spent") or 0
                attempts_stats[pid]["total_hints"] += attempt.get("hints_used") or 0

            # ============================================================
            # 2. hint_logs 테이블에서 힌트 상세 조회
            # ============================================================
            hint_response = self.db.table("hint_logs") \
                .select("problem_id, hint_level") \
                .in_("problem_id", uncached_ids) \
                .gte("created_at", (datetime.now() - timedelta(days=30)).isoformat()) \
                .execute()

            # 문제별 힌트 집계
            hint_stats: Dict[str, Dict[str, Any]] = {}
            for hint in (hint_response.data or []):
                pid = hint.get("problem_id")
                if not pid:
                    continue

                if pid not in hint_stats:
                    hint_stats[pid] = {
                        "total_requests": 0,
                        "total_level": 0,
                    }

                hint_stats[pid]["total_requests"] += 1
                hint_stats[pid]["total_level"] += hint.get("hint_level") or 1

            # ============================================================
            # 3. user_interactions에서 skip 이벤트 조회 (폴백)
            # ============================================================
            skip_response = self.db.table("user_interactions") \
                .select("interaction_data") \
                .eq("interaction_type", "skip") \
                .gte("created_at", (datetime.now() - timedelta(days=30)).isoformat()) \
                .execute()

            skip_counts: Dict[str, int] = {}
            for interaction in (skip_response.data or []):
                data = interaction.get("interaction_data", {})
                pid = data.get("problem_id")
                if pid and pid in uncached_ids:
                    skip_counts[pid] = skip_counts.get(pid, 0) + 1

            # ============================================================
            # 4. ProblemHistoricalStats로 변환 및 캐시 저장
            # ============================================================
            all_pids = set(attempts_stats.keys()) | set(hint_stats.keys()) | set(skip_counts.keys())

            for pid in all_pids:
                att = attempts_stats.get(pid, {})
                hnt = hint_stats.get(pid, {})

                attempt_count = att.get("count", 0)
                hint_requests = hnt.get("total_requests", 0)

                hist_stats = ProblemHistoricalStats(
                    problem_id=pid,
                    # attempts 기반
                    attempt_count=attempt_count,
                    correct_count=att.get("correct", 0),
                    avg_score=att.get("total_score", 0) / attempt_count if attempt_count > 0 else 0,
                    avg_time_spent=att.get("total_time", 0) / attempt_count if attempt_count > 0 else 0,
                    avg_hints_used=att.get("total_hints", 0) / attempt_count if attempt_count > 0 else 0,
                    # hint_logs 기반
                    total_hint_requests=hint_requests,
                    avg_hint_level=hnt.get("total_level", 0) / hint_requests if hint_requests > 0 else 0,
                    # user_interactions 기반
                    skip_count=skip_counts.get(pid, 0),
                )

                result_map[pid] = hist_stats
                self._stats_cache[pid] = (hist_stats, now)

            logger.debug(f"[SearchQuality] Loaded stats for {len(all_pids)} problems "
                        f"(attempts: {len(attempts_stats)}, hints: {len(hint_stats)}, skips: {len(skip_counts)})")

        except Exception as e:
            logger.warning(f"[SearchQuality] Failed to fetch historical stats: {e}")
            import traceback
            traceback.print_exc()

        return result_map

    def _calculate_diversity(
        self,
        results: List[Dict[str, Any]],
    ) -> tuple[float, Dict[str, Any]]:
        """
        다양성 점수 계산

        - 태그 다양성: 60%
        - 난이도 분포: 40%
        """
        if len(results) <= 1:
            return 1.0, {"message": "결과 1개 이하 - 다양성 평가 불필요"}

        # 태그 수집
        all_tags: Set[str] = set()
        difficulties: List[str] = []

        for result in results:
            tags = result.get("tags", [])
            all_tags.update(t.lower() for t in tags)
            if diff := result.get("difficulty"):
                difficulties.append(diff.lower())

        # 태그 다양성 (60%)
        # 고유 태그 수 / (결과 수 * 평균 태그 수)
        total_tags = sum(len(r.get("tags", [])) for r in results)
        avg_tags_per_result = total_tags / len(results) if results else 1
        tag_diversity = len(all_tags) / (len(results) * max(avg_tags_per_result, 1))
        tag_diversity = min(tag_diversity, 1.0)  # 1.0 상한

        # 난이도 분포 (40%)
        unique_difficulties = len(set(difficulties))
        difficulty_diversity = unique_difficulties / len(results) if results else 0
        difficulty_diversity = min(difficulty_diversity, 1.0)

        total_score = tag_diversity * 0.6 + difficulty_diversity * 0.4

        return total_score, {
            "unique_tags": len(all_tags),
            "total_tags": total_tags,
            "tag_diversity": round(tag_diversity, 3),
            "unique_difficulties": unique_difficulties,
            "difficulty_diversity": round(difficulty_diversity, 3),
        }

    async def evaluate_and_log(
        self,
        request_params: Dict[str, Any],
        search_results: List[Dict[str, Any]],
        user_id: Optional[str] = None,
        experiment_name: str = "search_quality",
    ) -> QualityScore:
        """
        검색 품질 평가 및 A/B 테스트 이벤트 로깅

        평가 결과를 A/B 테스트 시스템에 기록하여
        알고리즘 변경의 효과를 측정할 수 있게 합니다.
        """
        score = await self.evaluate(request_params, search_results, user_id)

        # A/B 테스트 이벤트로 로깅 (user_id가 있는 경우)
        if user_id:
            try:
                from .ab_testing import get_ab_testing_service
                ab_service = get_ab_testing_service()

                await ab_service.track_event(
                    user_id=user_id,
                    experiment_name=experiment_name,
                    event_type="search_quality",
                    event_data={
                        "overall_score": score.overall,
                        "grade": score.grade,
                        "metadata_match": score.metadata_match,
                        "historical_success": score.historical_success,
                        "diversity": score.diversity,
                        "result_count": len(search_results),
                    }
                )
                logger.debug(f"[SearchQuality] Logged quality score: {score.overall:.3f} ({score.grade})")

            except Exception as e:
                logger.warning(f"[SearchQuality] Failed to log A/B event: {e}")

        return score

    def get_improvement_suggestions(self, score: QualityScore) -> List[str]:
        """품질 점수 기반 개선 제안"""
        suggestions = []

        if score.metadata_match < 0.7:
            details = score.details.get("metadata", {})
            if details.get("difficulty_match_rate", 1) < 0.5:
                suggestions.append("난이도 필터링 정확도 개선 필요")
            if details.get("avg_topic_coverage", 1) < 0.5:
                suggestions.append("주제 매칭 알고리즘 개선 필요 (토픽 확장 또는 시맨틱 검색)")

        if score.historical_success < 0.6:
            details = score.details.get("historical", {})
            if details.get("avg_completion_rate", 1) < 0.5:
                suggestions.append("완료율 낮은 문제 필터링 고려")
            if details.get("avg_skip_rate", 0) > 0.3:
                suggestions.append("스킵률 높은 문제 제외 고려")

        if score.diversity < 0.5:
            suggestions.append("MMR 또는 다양성 샘플링 강화 필요")

        if not suggestions:
            suggestions.append("검색 품질 양호 - 현재 설정 유지")

        return suggestions


# ============================================================
# Singleton Instance
# ============================================================

_search_quality_evaluator: Optional[SearchQualityEvaluator] = None


def get_search_quality_evaluator() -> SearchQualityEvaluator:
    """SearchQualityEvaluator 싱글톤 반환"""
    global _search_quality_evaluator
    if _search_quality_evaluator is None:
        _search_quality_evaluator = SearchQualityEvaluator()
    return _search_quality_evaluator
