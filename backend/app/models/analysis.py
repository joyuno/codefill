"""Analysis models for AI-based learning analysis."""

from pydantic import BaseModel
from typing import Optional, List, Dict


class TopicScore(BaseModel):
    """토픽별 점수."""
    topic: str
    score: float
    insight: Optional[str] = None  # LLM이 생성한 인사이트


class StatsSnapshot(BaseModel):
    """분석 시점 통계 스냅샷."""
    level: int = 1
    problemsSolved: int = 0
    accuracy: float = 0.0
    streak: int = 0


class HintUsage(BaseModel):
    """힌트 사용 패턴."""
    total_requested: int = 0
    helpful_count: int = 0
    helpful_rate: float = 0.0
    avg_hint_level: float = 0.0


class LearningStyle(BaseModel):
    """학습 스타일."""
    prefers_examples: bool = False
    prefers_analogies: bool = False
    hint_sensitivity: str = "medium"  # low, medium, high
    pace: str = "medium"  # slow, medium, fast


class RecommendedProblem(BaseModel):
    """추천 문제."""
    id: str
    originalId: Optional[str] = None
    name: str
    difficulty: str
    topic: str
    reason: str


# ============================================================
# Learning Analytics Framework Types
# ============================================================

class BKTTopicMastery(BaseModel):
    """BKT 토픽별 마스터리."""
    mastery: float = 0.0  # 마스터리 확률 (0.0~1.0)
    is_mastered: bool = False  # 80% 이상이면 True
    attempt_count: int = 0
    correct_count: int = 0


class BloomMetrics(BaseModel):
    """Bloom's Taxonomy 메트릭."""
    apply_rate: float = 0.0  # easy 정답률
    analyze_rate: float = 0.0  # medium 정답률
    create_rate: float = 0.0  # hard 정답률
    current_level: str = "Apply"
    next_level: str = "Analyze"
    gap_analysis: Optional[str] = None


class ErrorPatternDetail(BaseModel):
    """에러 패턴 상세."""
    count: int = 0
    rate: float = 0.0
    examples: List[Dict] = []


class ErrorAnalysis(BaseModel):
    """SRK 에러 패턴 분석."""
    dominant_type: Optional[str] = None  # "skill" | "rule" | "knowledge"
    summary: str = ""
    total_errors: int = 0
    patterns: Dict[str, ErrorPatternDetail] = {}


class AnalysisReport(BaseModel):
    """AI 분석 리포트."""
    id: Optional[str] = None
    summaryText: str
    strengths: List[TopicScore] = []
    weaknesses: List[TopicScore] = []
    recommendations: List[str] = []
    studyPlan: Optional[str] = None
    skillSnapshot: Dict[str, float] = {}
    statsSnapshot: StatsSnapshot = StatsSnapshot()
    difficultySnapshot: Dict[str, float] = {}
    recommendedProblems: List[RecommendedProblem] = []
    createdAt: Optional[str] = None

    # 새로 추가된 필드들
    conceptsStruggling: List[str] = []
    conceptsLearned: List[str] = []
    hintUsage: Optional[HintUsage] = None
    learningStyle: Optional[LearningStyle] = None
    commonErrorPatterns: List[str] = []
    moodDistribution: Dict[str, int] = {}
    breakthroughMoments: List[str] = []
    teachingNotes: List[str] = []

    # AI 코칭 피드백 (마크다운 형식의 상세 피드백)
    detailedFeedback: Optional[str] = None

    # Learning Analytics Framework 메트릭
    bktMastery: Optional[Dict[str, BKTTopicMastery]] = None
    bloomMetrics: Optional[BloomMetrics] = None
    errorAnalysis: Optional[ErrorAnalysis] = None


class AnalysisReportResponse(BaseModel):
    """분석 리포트 응답."""
    hasReport: bool
    report: Optional[AnalysisReport] = None


# ============================================================
# 스킬 스냅샷 (성장 추적용)
# ============================================================

class SkillSnapshot(BaseModel):
    """10문제마다 저장되는 스킬 스냅샷."""
    id: Optional[str] = None
    snapshotAt: int  # 10, 20, 30... (몇 번째 문제에서 스냅샷)
    problemsSolved: int = 0
    problemsAttempted: int = 0
    skillByTopic: Dict[str, float] = {}
    weakTopics: List[str] = []
    strongTopics: List[str] = []
    learningStyle: Optional[Dict] = None
    avgSolveTimeSeconds: Optional[int] = None
    avgHintsPerProblem: Optional[float] = None
    currentStreak: int = 0
    longestStreak: int = 0
    createdAt: Optional[str] = None


class SkillSnapshotsResponse(BaseModel):
    """스킬 스냅샷 목록 응답."""
    snapshots: List[SkillSnapshot] = []
    totalCount: int = 0


class SkillProfileResponse(BaseModel):
    """현재 스킬 프로필 응답 (user_analysis_reports 기반)."""
    hasProfile: bool
    skillByTopic: Dict[str, float] = {}
    weakTopics: List[str] = []
    strongTopics: List[str] = []
    totalProblemsSolved: int = 0
    totalProblemsAttempted: int = 0
    avgSolveTimeSeconds: Optional[int] = None
    avgHintsPerProblem: Optional[float] = None
    currentStreak: int = 0
    longestStreak: int = 0
    preferredProblemType: Optional[str] = None
    preferredLanguage: Optional[str] = None
    learningStyle: Optional[Dict] = None
    commonErrorPatterns: Optional[List[str]] = None
    updatedAt: Optional[str] = None
