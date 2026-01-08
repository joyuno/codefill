"""Analysis models for AI-based learning analysis."""

from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime


class TopicScore(BaseModel):
    """토픽별 점수."""
    topic: str
    score: float


class StatsSnapshot(BaseModel):
    """분석 시점 통계 스냅샷."""
    level: int = 1
    problemsSolved: int = 0
    accuracy: float = 0.0
    streak: int = 0


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


class AnalysisReportResponse(BaseModel):
    """분석 리포트 응답."""
    hasReport: bool
    report: Optional[AnalysisReport] = None
