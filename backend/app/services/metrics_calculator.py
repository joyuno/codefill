"""
Learning Analytics Metrics Calculator

BKT (Bayesian Knowledge Tracing), Bloom's Taxonomy, SRK Error Pattern 계산
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from difflib import SequenceMatcher
import re


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


@dataclass
class ErrorPattern:
    """오류 패턴 분류 결과"""
    error_type: str         # "skill" | "rule" | "knowledge" | "none"
    confidence: float       # 분류 신뢰도 (0.0~1.0)
    user_answer: str
    correct_answer: str
    explanation: str        # 분류 이유


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

    # ============================================
    # Error Pattern Classification (SRK)
    # ============================================

    def classify_error_pattern(
        self,
        user_answer: str,
        correct_answer: str,
        hints_used: int = 0
    ) -> ErrorPattern:
        """
        SRK 모델 기반 오류 분류

        - Skill-based: 타이핑 실수 (유사도 높음, 1-2글자 차이)
        - Rule-based: 규칙 적용 오류 (숫자/연산자 차이)
        - Knowledge-based: 개념 이해 부족 (완전히 다른 답 + 힌트 많이 사용)

        Args:
            user_answer: 사용자 입력
            correct_answer: 정답
            hints_used: 사용한 힌트 수

        Returns:
            ErrorPattern
        """
        user_clean = (user_answer or "").strip()
        correct_clean = (correct_answer or "").strip()

        # 정답인 경우
        if user_clean.lower() == correct_clean.lower():
            return ErrorPattern(
                error_type="none",
                confidence=1.0,
                user_answer=user_answer,
                correct_answer=correct_answer,
                explanation="정답"
            )

        # 빈 답변
        if not user_clean:
            return ErrorPattern(
                error_type="knowledge",
                confidence=0.9,
                user_answer=user_answer,
                correct_answer=correct_answer,
                explanation="답변 없음 - 개념 이해 부족 가능성"
            )

        # 1. 문자열 유사도 체크 (Skill-based)
        similarity = SequenceMatcher(None, user_clean.lower(), correct_clean.lower()).ratio()

        if similarity >= 0.8:
            return ErrorPattern(
                error_type="skill",
                confidence=similarity,
                user_answer=user_answer,
                correct_answer=correct_answer,
                explanation=f"타이핑 실수 (유사도 {int(similarity*100)}%)"
            )

        # 2. 규칙 기반 오류 체크 (Rule-based)
        # 숫자 차이 (i vs i+1, n vs n-1)
        if self._is_boundary_error(user_clean, correct_clean):
            return ErrorPattern(
                error_type="rule",
                confidence=0.8,
                user_answer=user_answer,
                correct_answer=correct_answer,
                explanation="경계값 오류 (off-by-one)"
            )

        # 연산자 차이 (< vs <=, == vs ===)
        if self._is_operator_error(user_clean, correct_clean):
            return ErrorPattern(
                error_type="rule",
                confidence=0.75,
                user_answer=user_answer,
                correct_answer=correct_answer,
                explanation="연산자 오류"
            )

        # 3. 지식 기반 오류 (Knowledge-based)
        # 유사도 낮고 힌트 많이 사용
        if similarity < 0.4 and hints_used >= 2:
            return ErrorPattern(
                error_type="knowledge",
                confidence=0.85,
                user_answer=user_answer,
                correct_answer=correct_answer,
                explanation=f"개념 이해 부족 (유사도 {int(similarity*100)}%, 힌트 {hints_used}회)"
            )

        # 기본값: 유사도 기반 판단
        if similarity < 0.4:
            return ErrorPattern(
                error_type="knowledge",
                confidence=0.6,
                user_answer=user_answer,
                correct_answer=correct_answer,
                explanation=f"다른 접근 방식 (유사도 {int(similarity*100)}%)"
            )

        return ErrorPattern(
            error_type="rule",
            confidence=0.5,
            user_answer=user_answer,
            correct_answer=correct_answer,
            explanation=f"규칙 적용 오류 가능성 (유사도 {int(similarity*100)}%)"
        )

    def _is_boundary_error(self, user: str, correct: str) -> bool:
        """경계값 오류 체크 (i vs i+1, n vs n-1 등)"""
        # 숫자 추출
        user_nums = re.findall(r'[+-]?\d+', user)
        correct_nums = re.findall(r'[+-]?\d+', correct)

        if len(user_nums) == len(correct_nums) and len(user_nums) > 0:
            for u, c in zip(user_nums, correct_nums):
                try:
                    if abs(int(u) - int(c)) == 1:
                        return True
                except ValueError:
                    pass

        # +1, -1 차이 체크
        patterns = [
            (r'(\w+)\s*\+\s*1', r'\1'),
            (r'(\w+)\s*-\s*1', r'\1'),
            (r'(\w+)', r'\1\s*[+-]\s*1'),
        ]
        for p1, p2 in patterns:
            if re.search(p1, user) and re.search(p2, correct):
                return True
            if re.search(p2, user) and re.search(p1, correct):
                return True

        return False

    def _is_operator_error(self, user: str, correct: str) -> bool:
        """연산자 오류 체크 (< vs <=, == vs === 등)"""
        operators = ['<=', '>=', '==', '!=', '===', '!==', '<', '>', '&&', '||']

        user_ops = set(op for op in operators if op in user)
        correct_ops = set(op for op in operators if op in correct)

        # 연산자가 다르면 True
        if user_ops and correct_ops and user_ops != correct_ops:
            # 나머지 부분이 비슷한지 확인
            user_no_op = re.sub(r'[<>=!&|]+', '', user)
            correct_no_op = re.sub(r'[<>=!&|]+', '', correct)
            if SequenceMatcher(None, user_no_op, correct_no_op).ratio() > 0.8:
                return True

        return False

    def aggregate_error_patterns(
        self,
        errors: List[ErrorPattern]
    ) -> Dict[str, Any]:
        """
        오류 패턴 집계

        Args:
            errors: ErrorPattern 리스트

        Returns:
            {
                "dominant_type": "rule",
                "summary": "경계 조건 주의 필요",
                "patterns": {"skill": {...}, "rule": {...}, "knowledge": {...}}
            }
        """
        if not errors:
            return {
                "dominant_type": None,
                "summary": "오류 데이터 없음",
                "patterns": {}
            }

        # 유효한 오류만 필터링 (none 제외)
        valid_errors = [e for e in errors if e.error_type != "none"]

        if not valid_errors:
            return {
                "dominant_type": None,
                "summary": "모든 문제 정답",
                "patterns": {}
            }

        patterns: Dict[str, int] = {"skill": 0, "rule": 0, "knowledge": 0}
        examples: Dict[str, List[Dict]] = {"skill": [], "rule": [], "knowledge": []}

        for err in valid_errors:
            if err.error_type in patterns:
                patterns[err.error_type] += 1
                if len(examples[err.error_type]) < 2:  # 예시 최대 2개
                    examples[err.error_type].append({
                        "user": err.user_answer,
                        "correct": err.correct_answer,
                        "reason": err.explanation
                    })

        total = sum(patterns.values())
        if total == 0:
            return {
                "dominant_type": None,
                "summary": "분류된 오류 없음",
                "patterns": {}
            }

        dominant = max(patterns, key=lambda k: patterns[k])

        summaries = {
            "skill": "주의력 향상 필요 - 천천히 확인하며 입력하세요",
            "rule": "규칙 적용 연습 필요 - 경계 조건과 연산자를 다시 확인하세요",
            "knowledge": "개념 학습 필요 - 기초 개념부터 복습하세요"
        }

        return {
            "dominant_type": dominant,
            "summary": summaries.get(dominant, ""),
            "total_errors": total,
            "patterns": {
                k: {
                    "count": v,
                    "rate": round(v / total, 2) if total > 0 else 0,
                    "examples": examples[k]
                }
                for k, v in patterns.items() if v > 0
            }
        }
