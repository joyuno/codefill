"""Analysis router for AI-based learning analysis."""

from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID

from ..database import get_db
from ..dependencies import get_current_user_id
from ..models.analysis import (
    AnalysisReport,
    AnalysisReportResponse,
    TopicScore,
    StatsSnapshot,
    RecommendedProblem,
    HintUsage,
    LearningStyle,
)
from ..services.analysis_service import AnalysisService, InsufficientDataError

router = APIRouter()


@router.get("/report", response_model=AnalysisReportResponse)
async def get_analysis_report(
    user_id: UUID = Depends(get_current_user_id),
    db=Depends(get_db)
):
    """마지막 저장된 분석 리포트 조회."""
    try:
        service = AnalysisService(db)
        report_data = await service.get_latest_report(user_id)

        if not report_data:
            return AnalysisReportResponse(hasReport=False, report=None)

        # Transform to response model
        report = AnalysisReport(
            id=report_data.get("id"),
            summaryText=report_data.get("summaryText", ""),
            strengths=[
                TopicScore(topic=s["topic"], score=s["score"], insight=s.get("insight"))
                for s in report_data.get("strengths", [])
            ],
            weaknesses=[
                TopicScore(topic=w["topic"], score=w["score"], insight=w.get("insight"))
                for w in report_data.get("weaknesses", [])
            ],
            recommendations=report_data.get("recommendations", []),
            studyPlan=report_data.get("studyPlan"),
            skillSnapshot=report_data.get("skillSnapshot", {}),
            statsSnapshot=StatsSnapshot(**report_data.get("statsSnapshot", {})),
            difficultySnapshot=report_data.get("difficultySnapshot", {}),
            recommendedProblems=[
                RecommendedProblem(**p)
                for p in report_data.get("recommendedProblems", [])
            ],
            createdAt=report_data.get("createdAt"),
            # 새로 추가된 필드들
            conceptsStruggling=report_data.get("conceptsStruggling", []),
            conceptsLearned=report_data.get("conceptsLearned", []),
            hintUsage=HintUsage(**report_data["hintUsage"]) if report_data.get("hintUsage") and report_data["hintUsage"] else None,
            learningStyle=LearningStyle(**report_data["learningStyle"]) if report_data.get("learningStyle") and report_data["learningStyle"] else None,
            commonErrorPatterns=report_data.get("commonErrorPatterns", {}),
            moodDistribution=report_data.get("moodDistribution", {}),
            breakthroughMoments=report_data.get("breakthroughMoments", []),
            teachingNotes=report_data.get("teachingNotes", []),
        )

        return AnalysisReportResponse(hasReport=True, report=report)

    except Exception as e:
        # Return empty on error
        return AnalysisReportResponse(hasReport=False, report=None)


@router.post("/generate", response_model=AnalysisReport)
async def generate_analysis(
    user_id: UUID = Depends(get_current_user_id),
    db=Depends(get_db)
):
    """새로운 AI 분석 실행."""
    try:
        service = AnalysisService(db)
        report_data = await service.generate_analysis(user_id)

        return AnalysisReport(
            id=report_data.get("id"),
            summaryText=report_data.get("summaryText", ""),
            strengths=[
                TopicScore(topic=s["topic"], score=s["score"], insight=s.get("insight"))
                for s in report_data.get("strengths", [])
            ],
            weaknesses=[
                TopicScore(topic=w["topic"], score=w["score"], insight=w.get("insight"))
                for w in report_data.get("weaknesses", [])
            ],
            recommendations=report_data.get("recommendations", []),
            studyPlan=report_data.get("studyPlan"),
            skillSnapshot=report_data.get("skillSnapshot", {}),
            statsSnapshot=StatsSnapshot(**report_data.get("statsSnapshot", {})),
            difficultySnapshot=report_data.get("difficultySnapshot", {}),
            recommendedProblems=[
                RecommendedProblem(**p)
                for p in report_data.get("recommendedProblems", [])
            ],
            createdAt=report_data.get("createdAt"),
            # 새로 추가된 필드들
            conceptsStruggling=report_data.get("conceptsStruggling", []),
            conceptsLearned=report_data.get("conceptsLearned", []),
            hintUsage=HintUsage(**report_data["hintUsage"]) if report_data.get("hintUsage") and report_data["hintUsage"] else None,
            learningStyle=LearningStyle(**report_data["learningStyle"]) if report_data.get("learningStyle") and report_data["learningStyle"] else None,
            commonErrorPatterns=report_data.get("commonErrorPatterns", {}),
            moodDistribution=report_data.get("moodDistribution", {}),
            breakthroughMoments=report_data.get("breakthroughMoments", []),
            teachingNotes=report_data.get("teachingNotes", []),
        )

    except InsufficientDataError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"분석 생성 실패: {str(e)}")
