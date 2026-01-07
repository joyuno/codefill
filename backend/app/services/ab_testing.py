"""
A/B Testing Service for Recommendation Algorithms

추천 알고리즘 A/B 테스트 프레임워크

Features:
1. 실험 정의 및 관리
2. 사용자 그룹 할당 (해시 기반 일관성)
3. 메트릭 수집 및 분석
4. 통계적 유의성 검정

Usage:
    service = get_ab_testing_service()
    variant = await service.get_variant(user_id, "rec_algo_v2")
    await service.track_event(user_id, "rec_algo_v2", "click", {"topic": "dp"})
"""

import logging
import hashlib
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

from ..database import get_supabase_client
from ..config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class ExperimentStatus(str, Enum):
    """실험 상태"""
    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"


@dataclass
class Variant:
    """실험 변형 (그룹)"""
    name: str           # "control", "treatment_a", "treatment_b"
    weight: float       # 트래픽 비율 (0.0 ~ 1.0)
    config: Dict[str, Any]  # 변형별 설정

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Experiment:
    """A/B 테스트 실험"""
    id: str
    name: str
    description: str
    status: ExperimentStatus
    variants: List[Variant]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    target_sample_size: int
    current_sample_size: int
    created_at: datetime
    updated_at: datetime

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "variants": [v.to_dict() for v in self.variants],
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "target_sample_size": self.target_sample_size,
            "current_sample_size": self.current_sample_size,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass
class ExperimentMetrics:
    """실험 메트릭"""
    experiment_id: str
    variant_name: str
    impressions: int        # 노출 수
    clicks: int             # 클릭 수
    conversions: int        # 전환 수 (문제 완료)
    total_time_spent: float # 총 소요 시간 (초)

    @property
    def ctr(self) -> float:
        """클릭률 (Click-Through Rate)"""
        return self.clicks / self.impressions if self.impressions > 0 else 0

    @property
    def conversion_rate(self) -> float:
        """전환율"""
        return self.conversions / self.clicks if self.clicks > 0 else 0

    @property
    def avg_time_spent(self) -> float:
        """평균 소요 시간"""
        return self.total_time_spent / self.conversions if self.conversions > 0 else 0


class ABTestingService:
    """
    A/B 테스트 서비스

    Usage:
        service = get_ab_testing_service()

        # 사용자에게 할당된 변형 조회
        variant = await service.get_variant(user_id, "rec_algo_v2")
        # variant.name: "control" | "treatment_a" | ...
        # variant.config: {"algorithm": "cosine_similarity"}

        # 이벤트 트래킹
        await service.track_event(user_id, "rec_algo_v2", "impression")
        await service.track_event(user_id, "rec_algo_v2", "click", {"topic": "dp"})
        await service.track_event(user_id, "rec_algo_v2", "conversion", {"time_spent": 120})
    """

    # 기본 실험 정의 (하드코딩 - 나중에 DB로 이동 가능)
    DEFAULT_EXPERIMENTS = {
        "rec_algo_v2": {
            "name": "rec_algo_v2",
            "description": "추천 알고리즘 v2 테스트 (코사인 유사도 vs 기존)",
            "variants": [
                {"name": "control", "weight": 0.5, "config": {"algorithm": "basic"}},
                {"name": "treatment", "weight": 0.5, "config": {"algorithm": "cosine_similarity"}},
            ],
            "target_sample_size": 1000,
        },
        "cold_start_onboarding": {
            "name": "cold_start_onboarding",
            "description": "신규 사용자 온보딩 테스트",
            "variants": [
                {"name": "control", "weight": 0.5, "config": {"show_onboarding": False}},
                {"name": "treatment", "weight": 0.5, "config": {"show_onboarding": True}},
            ],
            "target_sample_size": 500,
        },
        "suggestion_ui": {
            "name": "suggestion_ui",
            "description": "추천 선택지 UI 테스트",
            "variants": [
                {"name": "chips", "weight": 0.33, "config": {"ui_type": "chips"}},
                {"name": "buttons", "weight": 0.34, "config": {"ui_type": "buttons"}},
                {"name": "cards", "weight": 0.33, "config": {"ui_type": "cards"}},
            ],
            "target_sample_size": 1500,
        },
    }

    def __init__(self):
        self.db = get_supabase_client()
        self._assignment_cache: Dict[str, Dict[str, str]] = {}  # user_id -> {exp_name -> variant_name}

    def _hash_assignment(self, user_id: str, experiment_name: str) -> float:
        """
        결정론적 해시 기반 그룹 할당

        동일한 사용자는 항상 같은 그룹에 할당됨
        """
        hash_input = f"{user_id}:{experiment_name}"
        hash_value = hashlib.md5(hash_input.encode()).hexdigest()
        # 해시를 0~1 사이 값으로 변환
        return int(hash_value[:8], 16) / 0xFFFFFFFF

    async def get_variant(self, user_id: str, experiment_name: str) -> Optional[Variant]:
        """
        사용자에게 할당된 변형 조회

        Args:
            user_id: 사용자 ID
            experiment_name: 실험 이름

        Returns:
            할당된 Variant 또는 None (실험이 없거나 비활성인 경우)
        """
        # 캐시 확인
        cache_key = f"{user_id}:{experiment_name}"
        if user_id in self._assignment_cache:
            cached = self._assignment_cache[user_id].get(experiment_name)
            if cached:
                exp_def = self.DEFAULT_EXPERIMENTS.get(experiment_name)
                if exp_def:
                    for v in exp_def["variants"]:
                        if v["name"] == cached:
                            return Variant(**v)

        # 실험 정의 조회
        exp_def = self.DEFAULT_EXPERIMENTS.get(experiment_name)
        if not exp_def:
            logger.warning(f"[ABTest] Unknown experiment: {experiment_name}")
            return None

        variants = exp_def["variants"]
        if not variants:
            return None

        # 해시 기반 그룹 할당
        hash_value = self._hash_assignment(user_id, experiment_name)

        cumulative_weight = 0.0
        assigned_variant = None
        for v in variants:
            cumulative_weight += v["weight"]
            if hash_value < cumulative_weight:
                assigned_variant = Variant(**v)
                break

        if not assigned_variant:
            assigned_variant = Variant(**variants[-1])

        # 캐시에 저장
        if user_id not in self._assignment_cache:
            self._assignment_cache[user_id] = {}
        self._assignment_cache[user_id][experiment_name] = assigned_variant.name

        # DB에 할당 기록 (비동기)
        try:
            self.db.table("ab_test_assignments").upsert({
                "user_id": user_id,
                "experiment_name": experiment_name,
                "variant_name": assigned_variant.name,
                "assigned_at": datetime.now().isoformat(),
            }).execute()
        except Exception as e:
            logger.debug(f"[ABTest] Failed to record assignment: {e}")

        logger.debug(f"[ABTest] User {user_id} assigned to {experiment_name}:{assigned_variant.name}")
        return assigned_variant

    async def track_event(
        self,
        user_id: str,
        experiment_name: str,
        event_type: str,
        event_data: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        이벤트 트래킹

        Args:
            user_id: 사용자 ID
            experiment_name: 실험 이름
            event_type: "impression" | "click" | "conversion" | "custom"
            event_data: 추가 데이터

        Returns:
            성공 여부
        """
        try:
            # 현재 할당된 변형 조회
            variant = await self.get_variant(user_id, experiment_name)
            if not variant:
                return False

            # 이벤트 기록
            self.db.table("ab_test_events").insert({
                "user_id": user_id,
                "experiment_name": experiment_name,
                "variant_name": variant.name,
                "event_type": event_type,
                "event_data": event_data or {},
                "created_at": datetime.now().isoformat(),
            }).execute()

            logger.debug(f"[ABTest] Event tracked: {experiment_name}:{variant.name}:{event_type}")
            return True

        except Exception as e:
            logger.error(f"[ABTest] Failed to track event: {e}")
            return False

    async def get_experiment_metrics(self, experiment_name: str) -> Dict[str, ExperimentMetrics]:
        """
        실험 메트릭 조회

        Returns:
            variant_name -> ExperimentMetrics 매핑
        """
        try:
            # 이벤트 집계 쿼리
            result = self.db.table("ab_test_events") \
                .select("variant_name, event_type, event_data") \
                .eq("experiment_name", experiment_name) \
                .execute()

            events = result.data or []

            # 변형별 집계
            metrics: Dict[str, Dict[str, Any]] = {}

            for event in events:
                variant = event.get("variant_name")
                event_type = event.get("event_type")
                event_data = event.get("event_data", {})

                if variant not in metrics:
                    metrics[variant] = {
                        "impressions": 0,
                        "clicks": 0,
                        "conversions": 0,
                        "total_time_spent": 0.0,
                    }

                if event_type == "impression":
                    metrics[variant]["impressions"] += 1
                elif event_type == "click":
                    metrics[variant]["clicks"] += 1
                elif event_type == "conversion":
                    metrics[variant]["conversions"] += 1
                    if "time_spent" in event_data:
                        metrics[variant]["total_time_spent"] += event_data["time_spent"]

            # ExperimentMetrics 객체로 변환
            result_metrics = {}
            for variant_name, data in metrics.items():
                result_metrics[variant_name] = ExperimentMetrics(
                    experiment_id=experiment_name,
                    variant_name=variant_name,
                    impressions=data["impressions"],
                    clicks=data["clicks"],
                    conversions=data["conversions"],
                    total_time_spent=data["total_time_spent"],
                )

            return result_metrics

        except Exception as e:
            logger.error(f"[ABTest] Failed to get metrics: {e}")
            return {}

    def calculate_statistical_significance(
        self,
        control_metrics: ExperimentMetrics,
        treatment_metrics: ExperimentMetrics,
        metric_type: str = "conversion_rate",
    ) -> Dict[str, Any]:
        """
        통계적 유의성 검정 (Z-test for proportions)

        Args:
            control_metrics: 대조군 메트릭
            treatment_metrics: 처리군 메트릭
            metric_type: "ctr" | "conversion_rate"

        Returns:
            {
                "significant": bool,  # 95% 신뢰수준에서 유의한가
                "p_value": float,
                "lift": float,  # 상대적 개선율 (%)
                "control_rate": float,
                "treatment_rate": float,
            }
        """
        import math

        if metric_type == "ctr":
            c_rate = control_metrics.ctr
            t_rate = treatment_metrics.ctr
            c_n = control_metrics.impressions
            t_n = treatment_metrics.impressions
        else:  # conversion_rate
            c_rate = control_metrics.conversion_rate
            t_rate = treatment_metrics.conversion_rate
            c_n = control_metrics.clicks
            t_n = treatment_metrics.clicks

        if c_n == 0 or t_n == 0:
            return {
                "significant": False,
                "p_value": 1.0,
                "lift": 0.0,
                "control_rate": c_rate,
                "treatment_rate": t_rate,
                "message": "샘플 수 부족",
            }

        # Pooled proportion
        pooled_p = (c_rate * c_n + t_rate * t_n) / (c_n + t_n)
        pooled_se = math.sqrt(pooled_p * (1 - pooled_p) * (1/c_n + 1/t_n))

        if pooled_se == 0:
            return {
                "significant": False,
                "p_value": 1.0,
                "lift": 0.0,
                "control_rate": c_rate,
                "treatment_rate": t_rate,
                "message": "분산 0",
            }

        # Z-score
        z_score = (t_rate - c_rate) / pooled_se

        # P-value (two-tailed) - 간단한 근사값 사용
        # 실제로는 scipy.stats.norm.sf를 사용해야 함
        p_value = 2 * (1 - self._normal_cdf(abs(z_score)))

        # 상대적 개선율 (lift)
        lift = ((t_rate - c_rate) / c_rate * 100) if c_rate > 0 else 0

        return {
            "significant": p_value < 0.05,  # 95% 신뢰수준
            "p_value": round(p_value, 4),
            "z_score": round(z_score, 3),
            "lift": round(lift, 2),
            "control_rate": round(c_rate, 4),
            "treatment_rate": round(t_rate, 4),
        }

    def _normal_cdf(self, x: float) -> float:
        """
        표준 정규 분포 누적 분포 함수 근사
        (scipy 없이 간단한 근사값 사용)
        """
        import math
        return 0.5 * (1 + math.erf(x / math.sqrt(2)))


# ============================================================
# Singleton Instance
# ============================================================

_ab_testing_service: Optional[ABTestingService] = None


def get_ab_testing_service() -> ABTestingService:
    """ABTestingService 싱글톤 반환"""
    global _ab_testing_service
    if _ab_testing_service is None:
        _ab_testing_service = ABTestingService()
    return _ab_testing_service
