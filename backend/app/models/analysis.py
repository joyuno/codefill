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
    commonErrorPatterns: Dict[str, int] = {}
    moodDistribution: Dict[str, int] = {}
    breakthroughMoments: List[str] = []
    teachingNotes: List[str] = []


class AnalysisReportResponse(BaseModel):
    """분석 리포트 응답."""
    hasReport: bool
    report: Optional[AnalysisReport] = None
