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
    SkillSnapshot,
    SkillSnapshotsResponse,
    SkillProfileResponse,
    BKTTopicMastery,
    BloomMetrics,
    ErrorAnalysis,
    ErrorPatternDetail,
    # 새로운 시각화 타입
    ProblemTypeStat,
    RecentAttempt,
    HintIndependence,
)
from ..services.analysis_service import AnalysisService, InsufficientDataError

router = APIRouter()


def _transform_bkt_mastery(bkt_data: dict | None) -> dict | None:
    """BKT 마스터리 데이터를 모델로 변환."""
    if not bkt_data:
        return None
    return {
        topic: BKTTopicMastery(
            mastery=data.get("mastery", 0.0),
            is_mastered=data.get("is_mastered", False),
            attempt_count=data.get("attempt_count", 0),
            correct_count=data.get("correct_count", 0),
        )
        for topic, data in bkt_data.items()
    }


def _transform_error_analysis(error_data: dict | None) -> ErrorAnalysis | None:
    """에러 분석 데이터를 모델로 변환."""
    if not error_data:
        return None
    patterns = {}
    raw_patterns = error_data.get("patterns", {})
    for key, val in raw_patterns.items():
        patterns[key] = ErrorPatternDetail(
            count=val.get("count", 0),
            rate=val.get("rate", 0.0),
            examples=val.get("examples", []),
        )
    return ErrorAnalysis(
        dominant_type=error_data.get("dominant_type"),
        summary=error_data.get("summary", ""),
        total_errors=error_data.get("total_errors", 0),
        patterns=patterns,
    )


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
            detailedFeedback=report_data.get("detailedFeedback"),
            # Learning Analytics Framework 메트릭
            bktMastery=_transform_bkt_mastery(report_data.get("bktMastery")),
            bloomMetrics=BloomMetrics(**report_data["bloomMetrics"]) if report_data.get("bloomMetrics") else None,
            errorAnalysis=_transform_error_analysis(report_data.get("errorAnalysis")),
            # 새로운 시각화 데이터
            problemTypeStats=[
                ProblemTypeStat(**p)
                for p in report_data.get("problemTypeStats", [])
            ],
            recent10Attempts=[
                RecentAttempt(**a)
                for a in report_data.get("recent10Attempts", [])
            ],
            recent10Analysis=report_data.get("recent10Analysis"),
            hintIndependence=HintIndependence(**report_data["hintIndependence"]) if report_data.get("hintIndependence") else None,
        )

        return AnalysisReportResponse(hasReport=True, report=report)

    except Exception as e:
        # Return empty on error
        import traceback
        print(f"❌ [ERROR] get_analysis_report failed: {e}")
        traceback.print_exc()
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
            detailedFeedback=report_data.get("detailedFeedback"),
            # Learning Analytics Framework 메트릭
            bktMastery=_transform_bkt_mastery(report_data.get("bktMastery")),
            bloomMetrics=BloomMetrics(**report_data["bloomMetrics"]) if report_data.get("bloomMetrics") else None,
            errorAnalysis=_transform_error_analysis(report_data.get("errorAnalysis")),
            # 새로운 시각화 데이터
            problemTypeStats=[
                ProblemTypeStat(**p)
                for p in report_data.get("problemTypeStats", [])
            ],
            recent10Attempts=[
                RecentAttempt(**a)
                for a in report_data.get("recent10Attempts", [])
            ],
            recent10Analysis=report_data.get("recent10Analysis"),
            hintIndependence=HintIndependence(**report_data["hintIndependence"]) if report_data.get("hintIndependence") else None,
        )

    except InsufficientDataError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"분석 생성 실패: {str(e)}")


@router.post("/recommend-problems", response_model=list[RecommendedProblem])
async def recommend_problems(
    user_id: UUID = Depends(get_current_user_id),
    db=Depends(get_db)
):
    """
    추천 문제 조회 (분석과 분리됨).

    약점 기반으로 추천 문제를 검색하고 DB에 저장합니다.
    분석 생성과 별도로 호출하여 필요할 때만 실행합니다.
    """
    try:
        service = AnalysisService(db)
        problems = await service.recommend_problems(user_id)

        return [
            RecommendedProblem(**p)
            for p in problems
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"추천 문제 조회 실패: {str(e)}")


# ============================================================
# 스킬 스냅샷 API (성장 추적용)
# ============================================================

@router.get("/snapshots", response_model=SkillSnapshotsResponse)
async def get_skill_snapshots(
    user_id: UUID = Depends(get_current_user_id),
    db=Depends(get_db)
):
    """
    스킬 스냅샷 히스토리 조회.

    10문제마다 저장된 스냅샷을 시간순으로 반환합니다.
    성장 그래프, 과거 비교 등에 활용.
    """
    try:
        result = db.table("user_skill_snapshots") \
            .select("*") \
            .eq("user_id", str(user_id)) \
            .order("snapshot_at") \
            .execute()

        snapshots = []
        for row in (result.data or []):
            snapshots.append(SkillSnapshot(
                id=str(row.get("id")),
                snapshotAt=row.get("snapshot_at", 0),
                problemsSolved=row.get("problems_solved", 0),
                problemsAttempted=row.get("problems_attempted", 0),
                skillByTopic=row.get("skill_by_topic", {}),
                weakTopics=row.get("weak_topics", []),
                strongTopics=row.get("strong_topics", []),
                learningStyle=row.get("learning_style"),
                avgSolveTimeSeconds=row.get("avg_solve_time_seconds"),
                avgHintsPerProblem=row.get("avg_hints_per_problem"),
                currentStreak=row.get("current_streak", 0),
                longestStreak=row.get("longest_streak", 0),
                createdAt=row.get("created_at"),
            ))

        return SkillSnapshotsResponse(
            snapshots=snapshots,
            totalCount=len(snapshots),
        )

    except Exception as e:
        return SkillSnapshotsResponse(snapshots=[], totalCount=0)


@router.get("/profile", response_model=SkillProfileResponse)
async def get_skill_profile(
    user_id: UUID = Depends(get_current_user_id),
    db=Depends(get_db)
):
    """
    현재 스킬 프로필 조회 (user_analysis_reports 기반).

    실시간 스킬 추적 데이터를 반환합니다.
    """
    try:
        result = db.table("user_analysis_reports") \
            .select("*") \
            .eq("user_id", str(user_id)) \
            .single() \
            .execute()

        if not result.data:
            return SkillProfileResponse(hasProfile=False)

        row = result.data
        return SkillProfileResponse(
            hasProfile=True,
            skillByTopic=row.get("skill_by_topic", {}),
            weakTopics=row.get("weak_topics", []),
            strongTopics=row.get("strong_topics", []),
            totalProblemsSolved=row.get("total_problems_solved", 0),
            totalProblemsAttempted=row.get("total_problems_attempted", 0),
            avgSolveTimeSeconds=row.get("avg_solve_time_seconds"),
            avgHintsPerProblem=row.get("avg_hints_per_problem"),
            currentStreak=row.get("current_streak", 0),
            longestStreak=row.get("longest_streak", 0),
            preferredProblemType=row.get("preferred_problem_type"),
            preferredLanguage=row.get("preferred_language"),
            learningStyle=row.get("learning_style"),
            commonErrorPatterns=row.get("common_error_patterns"),
            updatedAt=row.get("updated_at"),
        )

    except Exception as e:
        return SkillProfileResponse(hasProfile=False)
