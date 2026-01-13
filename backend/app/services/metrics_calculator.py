"""
Learning Analytics Metrics Calculator

BKT (Bayesian Knowledge Tracing), Bloom's Taxonomy 계산
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


# ============================================
# Data Classes
# ============================================

@dataclass
class BKTParams:
    """BKT 파라미터"""
    p_init: float = 0.3     # P(L0) 초기 마스터리
    p_transit: float = 0.1  # P(T) 학습 전이
    p_slip: float = 0.1     # P(S) 슬립 (알지만 틀릴 확률)
    p_guess: float = 0.2    # P(G) 추측 (모르지만 맞출 확률)


@dataclass
class BKTResult:
    """BKT 계산 결과"""
    topic: str
    mastery: float          # 현재 마스터리 확률 (0.0~1.0)
    is_mastered: bool       # 80% 이상이면 True
    attempt_count: int
    correct_count: int
    trajectory: List[float] # 마스터리 변화 추이


@dataclass
class BloomMetrics:
    """Bloom 분류별 메트릭"""
    apply_rate: float       # easy 정답률
    analyze_rate: float     # medium 정답률
    create_rate: float      # hard 정답률
    current_level: str      # 현재 달성 레벨
    next_level: str         # 다음 목표 레벨
    gap_analysis: str       # 레벨 간 격차 분석


# ============================================
# Metrics Calculator
# ============================================

class MetricsCalculator:
    """학습 분석 메트릭 계산기"""

    def __init__(self, bkt_params: Optional[BKTParams] = None):
        self.bkt_params = bkt_params or BKTParams()

    # ============================================
    # BKT (Bayesian Knowledge Tracing)
    # ============================================

    def calculate_bkt_mastery(
        self,
        attempt_sequence: List[bool],
        topic: str
    ) -> BKTResult:
        """
        정답/오답 시퀀스로 마스터리 확률 계산.

        BKT 업데이트 공식:
        - 정답 시: P(L|correct) = P(L) * (1-P(S)) / P(correct)
        - 오답 시: P(L|wrong) = P(L) * P(S) / P(wrong)
        - 학습 전이: P(L_new) = P(L) + (1 - P(L)) * P(T)

        Args:
            attempt_sequence: [True, False, True, ...] 정답/오답 시퀀스
            topic: 토픽명

        Returns:
            BKTResult: 마스터리 확률 및 관련 정보
        """
        if not attempt_sequence:
            return BKTResult(
                topic=topic,
                mastery=self.bkt_params.p_init,
                is_mastered=False,
                attempt_count=0,
                correct_count=0,
                trajectory=[self.bkt_params.p_init]
            )

        p = self.bkt_params
        mastery = p.p_init
        trajectory = [mastery]

        for is_correct in attempt_sequence:
            if is_correct:
                # P(correct) = P(L)*(1-P(S)) + (1-P(L))*P(G)
                p_correct = mastery * (1 - p.p_slip) + (1 - mastery) * p.p_guess
                # P(L|correct) using Bayes
                if p_correct > 0:
                    mastery = (mastery * (1 - p.p_slip)) / p_correct
            else:
                # P(wrong) = P(L)*P(S) + (1-P(L))*(1-P(G))
                p_wrong = mastery * p.p_slip + (1 - mastery) * (1 - p.p_guess)
                # P(L|wrong) using Bayes
                if p_wrong > 0:
                    mastery = (mastery * p.p_slip) / p_wrong

            # 학습 전이 적용
            mastery = mastery + (1 - mastery) * p.p_transit
            # 범위 제한 (0.01 ~ 0.99)
            mastery = max(0.01, min(0.99, mastery))
            trajectory.append(mastery)

        return BKTResult(
            topic=topic,
            mastery=round(mastery, 3),
            is_mastered=mastery >= 0.8,
            attempt_count=len(attempt_sequence),
            correct_count=sum(attempt_sequence),
            trajectory=trajectory
        )

    def calculate_all_topics_bkt(
        self,
        attempts_by_topic: Dict[str, List[bool]]
    ) -> Dict[str, BKTResult]:
        """
        모든 토픽에 대해 BKT 계산

        Args:
            attempts_by_topic: {"DP": [True, False, True], "Array": [True, True]}

        Returns:
            {topic: BKTResult}
        """
        results = {}
        for topic, sequence in attempts_by_topic.items():
            if sequence:  # 최소 1회 시도
                results[topic] = self.calculate_bkt_mastery(sequence, topic)
        return results

    # ============================================
    # Bloom's Taxonomy
    # ============================================

    def calculate_bloom_metrics(
        self,
        difficulty_stats: Dict[str, Dict[str, int]]
    ) -> BloomMetrics:
        """
        난이도별 성공률을 Bloom 레벨로 매핑

        Args:
            difficulty_stats: {
                "easy": {"success": 10, "total": 12},
                "medium": {"success": 5, "total": 10},
                "hard": {"success": 2, "total": 8}
            }

        Returns:
            BloomMetrics
        """
        def calc_rate(stats: Optional[Dict]) -> float:
            if not stats or stats.get("total", 0) == 0:
                return 0.0
            return round(stats["success"] / stats["total"], 3)

        apply_rate = calc_rate(difficulty_stats.get("easy"))
        analyze_rate = calc_rate(difficulty_stats.get("medium"))
        create_rate = calc_rate(difficulty_stats.get("hard"))

        # 현재 레벨 결정 (70% 이상 달성 시 해당 레벨 통과)
        if create_rate >= 0.7:
            current_level = "Create"
            next_level = "Master"
        elif analyze_rate >= 0.7:
            current_level = "Analyze"
            next_level = "Create"
        elif apply_rate >= 0.7:
            current_level = "Apply"
            next_level = "Analyze"
        else:
            current_level = "Remember"
            next_level = "Apply"

        # 격차 분석
        gaps = []
        if apply_rate < 0.7:
            gaps.append(f"Apply 달성 필요 ({int(apply_rate*100)}%)")
        elif analyze_rate < 0.5:
            gaps.append(f"Apply→Analyze 전환 중 ({int(analyze_rate*100)}%)")
        elif create_rate < 0.5:
            gaps.append(f"Analyze→Create 전환 중 ({int(create_rate*100)}%)")

        return BloomMetrics(
            apply_rate=apply_rate,
            analyze_rate=analyze_rate,
            create_rate=create_rate,
            current_level=current_level,
            next_level=next_level,
            gap_analysis=" | ".join(gaps) if gaps else "균형 잡힌 성장 중"
        )
