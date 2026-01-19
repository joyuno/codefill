from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File
from typing import Optional, List, Dict, Any
from uuid import UUID
import uuid as uuid_module

from ..database import get_db
from ..config import get_settings
from ..dependencies import get_current_user_id  # 공통 인증 의존성
from ..models.user import (
    User,
    UserProfile,
    UserStats,
    UserPreferences,
    Badge,
    UpdateUserRequest,
    UpdatePreferencesRequest,
    DailyActivity,
    RecentActivity,
    MypageProfile,
    MypageStats,
    MypageBadge,
    MypageAllResponse,
    SolvedAcProfileSimple,
    ChangeNicknameRequest,
    ChangeNicknameResponse,
    DateActivityDetail,
    SolvedProblem,
    # Public Profile Models
    PublicProfile,
    PublicStats,
    PublicFarm,
    PublicFarmCharacter,
    PublicFarmSlot,
    PublicBadge,
    PublicActivityData,
    PublicProfileAll,
)

router = APIRouter()
settings = get_settings()


@router.get("/me", response_model=UserProfile)
async def get_current_user(
    user_id: UUID = Depends(get_current_user_id),
    db=Depends(get_db)
):
    """Get current user's full profile."""
    try:
        # Get user (필요한 컬럼만 선택)
        user_result = db.table("users").select(
            "id, email, name, avatar_url, created_at"
        ).eq("id", str(user_id)).single().execute()

        # Get stats (필요한 컬럼만 선택)
        stats_result = db.table("user_stats").select(
            "user_id, level, total_xp, problems_solved, current_streak, longest_streak, "
            "blank_solved, puzzle_solved, guided_solved"
        ).eq("user_id", str(user_id)).single().execute()

        # Get preferences (필요한 컬럼만 선택)
        prefs_result = db.table("user_preferences").select(
            "user_id, preferred_language, theme, notifications_enabled, daily_goal"
        ).eq("user_id", str(user_id)).single().execute()

        # Get badges
        badges_result = db.table("user_badges")\
            .select("*, badges(*)")\
            .eq("user_id", str(user_id))\
            .execute()

        # Get subscription
        sub_result = db.table("subscriptions")\
            .select("*, plans(*)")\
            .eq("user_id", str(user_id))\
            .eq("status", "active")\
            .single()\
            .execute()

        user_data = user_result.data
        stats_data = stats_result.data or {}
        prefs_data = prefs_result.data or {}

        badges = []
        if badges_result.data:
            for badge_entry in badges_result.data:
                badge_data = badge_entry.get("badges", {})
                badges.append(Badge(
                    id=badge_data.get("id"),
                    code=badge_data.get("code"),
                    name=badge_data.get("name"),
                    description=badge_data.get("description"),
                    icon_url=badge_data.get("icon_url"),
                    rarity=badge_data.get("rarity", "common"),
                    earned_at=badge_entry.get("earned_at"),
                ))

        subscription = "free"
        if sub_result.data and sub_result.data.get("plans"):
            subscription = sub_result.data["plans"].get("code", "free")

        return UserProfile(
            user=User(**user_data),
            stats=UserStats(**stats_data),
            preferences=UserPreferences(**prefs_data),
            badges=badges,
            subscription=subscription,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user profile: {str(e)}"
        )


@router.put("/me", response_model=User)
async def update_current_user(
    request: UpdateUserRequest,
    user_id: UUID = Depends(get_current_user_id),
    db=Depends(get_db)
):
    """Update current user's basic info."""
    try:
        update_data = request.model_dump(exclude_unset=True, exclude_none=True)
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )

        result = db.table("users")\
            .update(update_data)\
            .eq("id", str(user_id))\
            .execute()

        return User(**result.data[0])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user: {str(e)}"
        )


@router.get("/me/stats", response_model=UserStats)
async def get_user_stats(
    user_id: UUID = Depends(get_current_user_id),
    db=Depends(get_db)
):
    """Get current user's statistics."""
    try:
        result = db.table("user_stats")\
            .select(
                "user_id, level, total_xp, problems_solved, current_streak, longest_streak, "
                "blank_solved, puzzle_solved, guided_solved"
            )\
            .eq("user_id", str(user_id))\
            .single()\
            .execute()

        return UserStats(**result.data)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stats: {str(e)}"
        )


@router.get("/me/preferences", response_model=UserPreferences)
async def get_user_preferences(
    user_id: UUID = Depends(get_current_user_id),
    db=Depends(get_db)
):
    """Get current user's preferences."""
    try:
        result = db.table("user_preferences")\
            .select("user_id, preferred_language, theme, notifications_enabled, daily_goal")\
            .eq("user_id", str(user_id))\
            .single()\
            .execute()

        return UserPreferences(**result.data)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get preferences: {str(e)}"
        )


@router.put("/me/preferences", response_model=UserPreferences)
async def update_user_preferences(
    request: UpdatePreferencesRequest,
    user_id: UUID = Depends(get_current_user_id),
    db=Depends(get_db)
):
    """Update current user's preferences."""
    try:
        update_data = request.model_dump(exclude_unset=True, exclude_none=True)
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )

        result = db.table("user_preferences")\
            .update(update_data)\
            .eq("user_id", str(user_id))\
            .execute()

        return UserPreferences(**result.data[0])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update preferences: {str(e)}"
        )


@router.post("/me/initialize-elo")
async def initialize_user_elo(
    user_id: UUID = Depends(get_current_user_id),
):
    """
    온보딩 완료 후 초기 ELO 설정

    users 테이블의 experience_level, learning_goal과
    user_preferences의 preferred_difficulty를 기반으로 초기 ELO를 계산합니다.

    반환값:
        - initial_elo: 설정된 초기 ELO (770~1130 범위)
        - factors: 계산에 사용된 요소들
    """
    from ..services.feedback_service import FeedbackService

    try:
        service = FeedbackService()
        initial_elo = service.set_initial_elo_for_user(str(user_id))

        return {
            "success": True,
            "initial_elo": initial_elo,
            "message": f"초기 ELO가 {initial_elo}로 설정되었습니다.",
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize ELO: {str(e)}"
        )


@router.get("/me/badges", response_model=List[Badge])
async def get_user_badges(
    user_id: UUID = Depends(get_current_user_id),
    db=Depends(get_db)
):
    """Get current user's badges."""
    try:
        result = db.table("user_badges")\
            .select("*, badges(*)")\
            .eq("user_id", str(user_id))\
            .execute()

        badges = []
        if result.data:
            for badge_entry in result.data:
                badge_data = badge_entry.get("badges", {})
                badges.append(Badge(
                    id=badge_data.get("id"),
                    code=badge_data.get("code"),
                    name=badge_data.get("name"),
                    description=badge_data.get("description"),
                    icon_url=badge_data.get("icon_url"),
                    rarity=badge_data.get("rarity", "common"),
                    earned_at=badge_entry.get("earned_at"),
                ))

        return badges

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get badges: {str(e)}"
        )


@router.get("/me/activity", response_model=List[DailyActivity])
async def get_user_activity(
    days: int = 365,
    user_id: UUID = Depends(get_current_user_id),
    db=Depends(get_db)
):
    """Get current user's activity history (for grass heatmap)."""
    try:
        from datetime import datetime, timedelta

        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        result = db.table("daily_activity")\
            .select("activity_date, problems_solved, xp_earned, time_spent, blank_count, puzzle_count, guided_count")\
            .eq("user_id", str(user_id))\
            .gte("activity_date", start_date)\
            .order("activity_date", desc=False)\
            .execute()

        return [DailyActivity(
            date=item["activity_date"],
            problems_solved=item.get("problems_solved", 0),
            xp_earned=item.get("xp_earned", 0),
            time_spent=item.get("time_spent", 0),
            blank_count=item.get("blank_count", 0),
            puzzle_count=item.get("puzzle_count", 0),
            guided_count=item.get("guided_count", 0),
        ) for item in (result.data or [])]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get activity: {str(e)}"
        )


@router.get("/me/activity/{date}", response_model=DateActivityDetail)
async def get_activity_by_date(
    date: str,
    user_id: UUID = Depends(get_current_user_id),
    db=Depends(get_db)
):
    """Get user's activity detail for a specific date (잔디 클릭 시 상세)."""
    try:
        from datetime import datetime

        # Validate date format
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Use YYYY-MM-DD."
            )

        # Get daily activity summary (limit(1)로 0~1개 결과 허용)
        daily_result = db.table("daily_activity")\
            .select("problems_solved, xp_earned")\
            .eq("user_id", str(user_id))\
            .eq("activity_date", date)\
            .limit(1)\
            .execute()

        daily_data = daily_result.data[0] if daily_result.data else {}
        problems_solved = daily_data.get("problems_solved", 0)
        xp_earned = daily_data.get("xp_earned", 0)

        # Get solved problems with base_problems.name via JOIN
        start_of_day = f"{date}T00:00:00"
        end_of_day = f"{date}T23:59:59"
        problems = fetch_solved_problems_with_names(db, str(user_id), start_of_day, end_of_day)

        return DateActivityDetail(
            date=date,
            problems_solved=problems_solved if problems_solved else len(problems),
            xp_earned=xp_earned if xp_earned else sum(p.xp_earned for p in problems),
            problems=problems,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get activity for date: {str(e)}"
        )


@router.get("/me/recent", response_model=List[RecentActivity])
async def get_recent_activity(
    limit: int = 10,
    user_id: UUID = Depends(get_current_user_id),
    db=Depends(get_db)
):
    """Get current user's recent activity for mypage."""
    try:
        from datetime import datetime
        activities = []

        # 1. Get recent solved problems from attempts
        attempts_result = db.table("attempts")\
            .select("id, problem_type, xp_earned, submitted_at")\
            .eq("user_id", str(user_id))\
            .eq("is_correct", True)\
            .order("submitted_at", desc=True)\
            .limit(limit)\
            .execute()

        for attempt in (attempts_result.data or []):
            problem_type = attempt.get("problem_type", "blank") or "blank"

            activities.append(RecentActivity(
                id=attempt["id"],
                type="solved",
                title=f"Solved: {problem_type.capitalize()} Problem",
                description=f"{problem_type.capitalize()} problem completed",
                timestamp=attempt["submitted_at"],
                xp_gained=attempt.get("xp_earned", 0),
            ))

        # 2. Get recently earned badges
        badges_result = db.table("user_badges")\
            .select("id, earned_at, badges(name, description)")\
            .eq("user_id", str(user_id))\
            .order("earned_at", desc=True)\
            .limit(5)\
            .execute()

        for badge_entry in (badges_result.data or []):
            badge = badge_entry.get("badges", {})
            activities.append(RecentActivity(
                id=badge_entry["id"],
                type="badge",
                title=f"New Badge: {badge.get('name', 'Badge')}",
                description=badge.get("description", ""),
                timestamp=badge_entry["earned_at"],
            ))

        # Sort by timestamp descending and limit
        activities.sort(key=lambda x: x.timestamp, reverse=True)
        return activities[:limit]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get recent activity: {str(e)}"
        )


def calculate_required_xp(level: int) -> int:
    """Calculate required XP for next level."""
    # 100 XP for level 1, increasing by 50 each level
    return level * 100 + (level - 1) * 50


def calculate_current_xp(total_xp: int, level: int) -> int:
    """Calculate current XP within the level."""
    xp_for_current_level = 0
    for l in range(1, level):
        xp_for_current_level += calculate_required_xp(l)
    return total_xp - xp_for_current_level


@router.get("/me/profile", response_model=MypageProfile)
async def get_mypage_profile(
    user_id: UUID = Depends(get_current_user_id),
    db=Depends(get_db)
):
    """Get flattened user profile for mypage."""
    try:
        # Get user (필요한 컬럼만 선택)
        user_result = db.table("users").select(
            "id, email, name, avatar_url, role, created_at"
        ).eq("id", str(user_id)).single().execute()
        user_data = user_result.data

        # Get stats (필요한 컬럼만 선택)
        stats_result = db.table("user_stats").select(
            "level, total_xp, problems_solved, current_streak, longest_streak"
        ).eq("user_id", str(user_id)).single().execute()
        stats_data = stats_result.data or {}

        # Get subscription
        sub_result = db.table("subscriptions")\
            .select("*, plans(*)")\
            .eq("user_id", str(user_id))\
            .eq("status", "active")\
            .single()\
            .execute()

        subscription = "free"
        if sub_result.data and sub_result.data.get("plans"):
            subscription = sub_result.data["plans"].get("code", "free")

        level = stats_data.get("level", 1)
        total_xp = stats_data.get("total_xp", 0)

        return MypageProfile(
            id=str(user_data["id"]),
            email=user_data.get("email", ""),
            username=user_data.get("name", "User"),
            avatarShape="hexagon",
            avatarColor=user_data.get("avatar_url") or "hsl(142, 71%, 45%)",
            role=user_data.get("role", "user"),
            level=level,
            currentXP=calculate_current_xp(total_xp, level),
            requiredXP=calculate_required_xp(level),
            totalXP=total_xp,
            solvedCount=stats_data.get("problems_solved", 0),
            streak=stats_data.get("current_streak", 0),
            maxStreak=stats_data.get("longest_streak", 0),
            joinedAt=user_data.get("created_at", ""),
            subscription=subscription,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get profile: {str(e)}"
        )


@router.get("/me/mypage-stats", response_model=MypageStats)
async def get_mypage_stats(
    user_id: UUID = Depends(get_current_user_id),
    db=Depends(get_db)
):
    """Get user stats formatted for mypage."""
    try:
        # Get stats (필요한 컬럼만 선택) - puzzle_solved, guided_solved 추가
        stats_result = db.table("user_stats").select(
            "level, total_xp, problems_solved, current_streak, longest_streak, "
            "blank_solved, puzzle_solved, guided_solved, "
            "easy_solved, medium_solved, hard_solved"
        ).eq("user_id", str(user_id)).single().execute()
        stats_data = stats_result.data or {}

        # 난이도별 통계 (실제 컬럼 사용)
        solved_by_difficulty = {
            "easy": stats_data.get("easy_solved", 0),
            "medium": stats_data.get("medium_solved", 0),
            "hard": stats_data.get("hard_solved", 0),
        }

        return MypageStats(
            totalSolved=stats_data.get("problems_solved", 0),
            solvedByDifficulty=solved_by_difficulty,
            solvedByType={
                "blank": stats_data.get("blank_solved", 0),
                "puzzle": stats_data.get("puzzle_solved", 0),
                "guided": stats_data.get("guided_solved", 0),
            },
            currentStreak=stats_data.get("current_streak", 0),
            maxStreak=stats_data.get("longest_streak", 0),
            totalXP=stats_data.get("total_xp", 0),
            level=stats_data.get("level", 1),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stats: {str(e)}"
        )


@router.get("/me/mypage-badges", response_model=List[MypageBadge])
async def get_mypage_badges(
    user_id: UUID = Depends(get_current_user_id),
    db=Depends(get_db)
):
    """Get user badges formatted for mypage."""
    try:
        result = db.table("user_badges")\
            .select("*, badges(*)")\
            .eq("user_id", str(user_id))\
            .execute()

        badges = []
        # Default icon mapping for badges
        icon_map = {
            "first_problem": "🎯",
            "streak_7": "🔥",
            "streak_30": "🏆",
            "streak_100": "👑",
            "problems_50": "💪",
            "problems_100": "🎖️",
            "level_10": "⭐",
            "level_50": "🌟",
        }

        if result.data:
            for badge_entry in result.data:
                badge_data = badge_entry.get("badges", {})
                code = badge_data.get("code", "")
                badges.append(MypageBadge(
                    id=str(badge_data.get("id", "")),
                    name=badge_data.get("name", "Badge"),
                    icon=icon_map.get(code, "🏅"),
                    icon_url=badge_data.get("icon_url"),
                    description=badge_data.get("description", ""),
                    earnedAt=badge_entry.get("earned_at", ""),
                    rarity=badge_data.get("rarity", "common"),
                ))

        return badges

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get badges: {str(e)}"
        )


# =====================================================
# Unified Mypage API - 통합 마이페이지 API
# =====================================================

@router.get("/me/mypage-all", response_model=MypageAllResponse)
async def get_mypage_all(
    user_id: UUID = Depends(get_current_user_id),
    db=Depends(get_db)
):
    """
    통합 마이페이지 API - 한 번의 호출로 모든 마이페이지 데이터 반환.

    기존 5개 API 호출을 1개로 통합:
    - /me/profile
    - /me/mypage-stats
    - /me/mypage-badges
    - /me/recent
    - /solved-ac/me
    """
    from datetime import datetime

    try:
        # ===== 1. Profile 데이터 (users + user_stats + subscriptions) =====
        user_result = db.table("users").select(
            "id, email, name, avatar_url, created_at"
        ).eq("id", str(user_id)).single().execute()
        user_data = user_result.data

        stats_result = db.table("user_stats").select(
            "level, total_xp, problems_solved, current_streak, longest_streak, "
            "blank_solved, puzzle_solved, guided_solved, "
            "easy_solved, medium_solved, hard_solved"
        ).eq("user_id", str(user_id)).single().execute()
        stats_data = stats_result.data or {}

        sub_result = db.table("subscriptions")\
            .select("status, plans(code)")\
            .eq("user_id", str(user_id))\
            .eq("status", "active")\
            .limit(1)\
            .execute()

        subscription = "free"
        if sub_result.data and len(sub_result.data) > 0:
            sub_data = sub_result.data[0]
            if sub_data.get("plans"):
                subscription = sub_data["plans"].get("code", "free")

        level = stats_data.get("level", 1)
        total_xp = stats_data.get("total_xp", 0)

        profile = MypageProfile(
            id=str(user_data["id"]),
            email=user_data.get("email", ""),
            username=user_data.get("name", "User"),
            avatarShape="hexagon",
            avatarColor=user_data.get("avatar_url") or "hsl(142, 71%, 45%)",
            level=level,
            currentXP=calculate_current_xp(total_xp, level),
            requiredXP=calculate_required_xp(level),
            totalXP=total_xp,
            solvedCount=stats_data.get("problems_solved", 0),
            streak=stats_data.get("current_streak", 0),
            maxStreak=stats_data.get("longest_streak", 0),
            joinedAt=user_data.get("created_at", ""),
            subscription=subscription,
        )

        # ===== 2. Stats 데이터 (user_stats에서 이미 가져옴, 재사용) =====
        total_solved = stats_data.get("problems_solved", 0)
        solved_by_difficulty = {
            "easy": stats_data.get("easy_solved", 0),
            "medium": stats_data.get("medium_solved", 0),
            "hard": stats_data.get("hard_solved", 0),
        }

        stats = MypageStats(
            totalSolved=total_solved,
            solvedByDifficulty=solved_by_difficulty,
            solvedByType={
                "blank": stats_data.get("blank_solved", 0),
                "puzzle": stats_data.get("puzzle_solved", 0),
                "guided": stats_data.get("guided_solved", 0),
            },
            currentStreak=stats_data.get("current_streak", 0),
            maxStreak=stats_data.get("longest_streak", 0),
            totalXP=total_xp,
            level=level,
        )

        # ===== 3. Badges 데이터 =====
        badges_result = db.table("user_badges")\
            .select("earned_at, badges(id, code, name, description, icon_url, rarity)")\
            .eq("user_id", str(user_id))\
            .execute()

        icon_map = {
            "first_problem": "🎯", "streak_7": "🔥", "streak_30": "🏆",
            "streak_100": "👑", "problems_50": "💪", "problems_100": "🎖️",
            "level_10": "⭐", "level_50": "🌟",
        }

        badges = []
        for badge_entry in (badges_result.data or []):
            badge_data = badge_entry.get("badges", {})
            code = badge_data.get("code", "")
            badges.append(MypageBadge(
                id=str(badge_data.get("id", "")),
                name=badge_data.get("name", ""),
                icon=icon_map.get(code, "🏅"),
                icon_url=badge_data.get("icon_url"),
                description=badge_data.get("description", ""),
                earnedAt=badge_entry.get("earned_at", ""),
                rarity=badge_data.get("rarity", "common"),
            ))

        # ===== 4. Recent Activity 데이터 =====
        activities = []

        # Recent solved problems
        attempts_result = db.table("attempts")\
            .select("id, problem_type, xp_earned, submitted_at")\
            .eq("user_id", str(user_id))\
            .eq("is_correct", True)\
            .order("submitted_at", desc=True)\
            .limit(10)\
            .execute()

        for attempt in (attempts_result.data or []):
            problem_type = attempt.get("problem_type", "blank") or "blank"
            activities.append(RecentActivity(
                id=attempt["id"],
                type="solved",
                title=f"Solved: {problem_type.capitalize()} Problem",
                description=f"{problem_type.capitalize()} problem completed",
                timestamp=attempt["submitted_at"],
                xp_gained=attempt.get("xp_earned", 0),
            ))

        # Recent badges (별도 조회 대신 위에서 가져온 badges 활용)
        for badge in badges[:3]:  # 최근 3개만
            activities.append(RecentActivity(
                id=badge.id,
                type="badge",
                title=f"Badge: {badge.name}",
                description=badge.description,
                timestamp=badge.earnedAt,
                xp_gained=None,
            ))

        # Sort by timestamp
        activities.sort(key=lambda x: x.timestamp if x.timestamp else "", reverse=True)
        activities = activities[:10]  # 최대 10개

        # ===== 5. Solved.ac 프로필 =====
        solvedac_result = db.table("solved_ac_profiles")\
            .select("handle, tier, rating, solved_count, max_streak, last_synced_at")\
            .eq("user_id", str(user_id))\
            .limit(1)\
            .execute()

        solved_ac = None
        if solvedac_result.data and len(solvedac_result.data) > 0:
            sa_data = solvedac_result.data[0]
            solved_ac = SolvedAcProfileSimple(
                handle=sa_data["handle"],
                tier=sa_data.get("tier", 0),
                rating=sa_data.get("rating", 0),
                solved_count=sa_data.get("solved_count", 0),
                max_streak=sa_data.get("max_streak", 0),
                last_synced_at=sa_data.get("last_synced_at", ""),
            )

        return MypageAllResponse(
            profile=profile,
            stats=stats,
            badges=badges,
            recentActivity=activities,
            solvedAc=solved_ac,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get mypage data: {str(e)}"
        )


# =====================================================
# Nickname Change Endpoint
# =====================================================

@router.put("/me/nickname", response_model=ChangeNicknameResponse)
async def change_nickname(
    request: ChangeNicknameRequest,
    user_id: UUID = Depends(get_current_user_id),
    db=Depends(get_db)
):
    """
    Change user's nickname. Limited to once per 30 days.
    """
    from datetime import datetime, timedelta, timezone

    # Get user's current name
    user_result = db.table("users").select("name").eq("id", str(user_id)).single().execute()
    if not user_result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다."
        )

    user = user_result.data
    # 참고: 30일 제한 기능은 nickname_last_changed_at 컬럼 추가 후 활성화

    # Check nickname availability (case-insensitive, exclude current user)
    new_nickname = request.new_nickname.strip()
    existing = db.table("users")\
        .select("id")\
        .ilike("name", new_nickname)\
        .neq("id", str(user_id))\
        .is_("deleted_at", "null")\
        .execute()

    if existing.data and len(existing.data) > 0:
        return ChangeNicknameResponse(
            success=False,
            message="이미 사용 중인 닉네임입니다."
        )

    # Update nickname and timestamp
    # Update name only (nickname_last_changed_at column not in current schema)
    db.table("users").update({
        "name": new_nickname,
    }).eq("id", str(user_id)).execute()

    # 참고: 30일 제한 기능은 nickname_last_changed_at 컬럼 추가 후 활성화
    return ChangeNicknameResponse(
        success=True,
        message="닉네임이 변경되었습니다.",
        next_change_available_at=None
    )


# =====================================================
# Avatar Upload Endpoint
# =====================================================

ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/gif", "image/webp"]
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


def ensure_avatars_bucket_exists(db):
    """Ensure the 'avatars' bucket exists in Supabase Storage."""
    try:
        # Try to list buckets and check if 'avatars' exists
        buckets = db.storage.list_buckets()
        bucket_names = [b.name for b in buckets]

        if "avatars" not in bucket_names:
            # Create the bucket with public access
            db.storage.create_bucket("avatars", options={"public": True})
    except Exception as e:
        # If bucket already exists or other non-critical error, continue
        # The actual upload will fail if there's a real problem
        pass


@router.post("/me/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    user_id: UUID = Depends(get_current_user_id),
    db=Depends(get_db)
):
    """Upload user avatar image to Supabase Storage."""
    try:
        # Validate file type
        if file.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="지원하지 않는 이미지 형식입니다. (JPEG, PNG, GIF, WebP만 가능)"
            )

        # Read file content
        content = await file.read()

        # Validate file size
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="파일 크기가 5MB를 초과합니다."
            )

        # Ensure bucket exists
        ensure_avatars_bucket_exists(db)

        # Generate unique filename
        file_ext = file.filename.split(".")[-1] if file.filename else "jpg"
        unique_filename = f"{user_id}/{uuid_module.uuid4()}.{file_ext}"

        # Upload to Supabase Storage
        storage = db.storage.from_("avatars")

        # Delete old avatar if exists
        try:
            old_files = storage.list(path=f"{user_id}")
            for old_file in old_files:
                storage.remove([f"{user_id}/{old_file['name']}"])
        except Exception:
            pass  # Ignore errors when deleting old files

        # Upload new avatar
        result = storage.upload(
            path=unique_filename,
            file=content,
            file_options={"content-type": file.content_type}
        )

        # Get public URL
        public_url = storage.get_public_url(unique_filename)

        # Update user's avatar_url in database
        db.table("users").update({"avatar_url": public_url}).eq("id", str(user_id)).execute()

        return {
            "success": True,
            "avatar_url": public_url,
            "message": "프로필 이미지가 변경되었습니다."
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"이미지 업로드에 실패했습니다: {str(e)}"
        )


@router.delete("/me/avatar")
async def delete_avatar(
    user_id: UUID = Depends(get_current_user_id),
    db=Depends(get_db)
):
    """Delete user avatar image."""
    try:
        # Delete from storage
        storage = db.storage.from_("avatars")
        try:
            files = storage.list(path=f"{user_id}")
            for file in files:
                storage.remove([f"{user_id}/{file['name']}"])
        except Exception:
            pass

        # Clear avatar_url in database
        db.table("users").update({"avatar_url": None}).eq("id", str(user_id)).execute()

        return {
            "success": True,
            "message": "프로필 이미지가 삭제되었습니다."
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"이미지 삭제에 실패했습니다: {str(e)}"
        )


# =====================================================
# Public Profile Endpoints (공개 프로필 - 인증 불필요)
# =====================================================

def get_user_by_username(db, username: str):
    """Helper: username으로 사용자 조회."""
    result = db.table("users")\
        .select("id, email, name, avatar_url, created_at")\
        .eq("name", username)\
        .is_("deleted_at", "null")\
        .single()\
        .execute()
    return result.data


def fetch_solved_problems_with_names(db, user_id: str, start_of_day: str, end_of_day: str) -> list:
    """
    Helper: attempts에서 푼 문제를 가져와서 문제 이름과 함께 반환.

    우선순위:
    1. attempts.problem_name (직접 저장된 이름)
    2. base_problems.name (base_problem_id로 조회)
    3. "Unknown Problem" (fallback)
    """
    # 1. attempts에서 정답 제출 기록 가져오기 (problem_name 포함)
    attempts_result = db.table("attempts")\
        .select("id, base_problem_id, problem_name, problem_type, xp_earned, submitted_at, difficulty")\
        .eq("user_id", user_id)\
        .eq("is_correct", True)\
        .gte("submitted_at", start_of_day)\
        .lte("submitted_at", end_of_day)\
        .order("submitted_at", desc=True)\
        .execute()

    if not attempts_result.data:
        return []

    # 2. problem_name이 없는 경우만 base_problem_id로 조회
    base_ids = list(set(
        str(a["base_problem_id"])
        for a in attempts_result.data
        if a.get("base_problem_id") and not a.get("problem_name")
    ))

    # 3. base_problems에서 name 조회 (필요한 경우만)
    base_to_name = {}
    if base_ids:
        base_result = db.table("base_problems")\
            .select("id, name")\
            .in_("id", base_ids)\
            .execute()
        for bp in (base_result.data or []):
            base_to_name[str(bp["id"])] = bp.get("name", "Unknown Problem")

    # 4. SolvedProblem 리스트 생성
    problems = []
    for attempt in attempts_result.data:
        # 우선순위: attempts.problem_name > base_problems.name > fallback
        problem_name = attempt.get("problem_name")
        if not problem_name:
            base_problem_id = attempt.get("base_problem_id")
            problem_name = base_to_name.get(str(base_problem_id), "Unknown Problem") if base_problem_id else "Unknown Problem"

        problems.append(SolvedProblem(
            id=str(attempt["id"]),
            name=problem_name,
            difficulty=attempt.get("difficulty") or "medium",
            problem_type=attempt.get("problem_type", "blank") or "blank",
            xp_earned=attempt.get("xp_earned", 0) or 0,
            solved_at=attempt["submitted_at"],
        ))

    return problems


@router.get("/{username}/public-profile", response_model=PublicProfile)
async def get_public_profile(
    username: str,
    db=Depends(get_db)
):
    """Get public profile by username. No auth required."""
    try:
        user = get_user_by_username(db, username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자를 찾을 수 없습니다."
            )

        user_id = user["id"]

        # Get stats (필요한 컬럼만 선택)
        stats_result = db.table("user_stats")\
            .select("level, total_xp, problems_solved, current_streak")\
            .eq("user_id", str(user_id))\
            .single()\
            .execute()
        stats_data = stats_result.data or {}

        level = stats_data.get("level", 1)
        total_xp = stats_data.get("total_xp", 0)

        return PublicProfile(
            id=str(user_id),
            username=user.get("name", "User"),
            avatarUrl=user.get("avatar_url"),  # 실제 이미지 URL (없으면 None)
            avatarColor="hsl(142, 71%, 45%)",  # 폴백 배경색
            level=level,
            currentXP=calculate_current_xp(total_xp, level),
            requiredXP=calculate_required_xp(level),
            totalXP=total_xp,
            solvedCount=stats_data.get("problems_solved", 0),
            streak=stats_data.get("current_streak", 0),
            joinedAt=user.get("created_at", ""),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get public profile: {str(e)}"
        )


@router.get("/{username}/public-stats", response_model=PublicStats)
async def get_public_stats(
    username: str,
    db=Depends(get_db)
):
    """Get public stats by username. No auth required."""
    try:
        user = get_user_by_username(db, username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자를 찾을 수 없습니다."
            )

        user_id = user["id"]

        # Get stats (필요한 컬럼만 선택) - puzzle_solved, guided_solved 추가
        stats_result = db.table("user_stats")\
            .select("level, total_xp, problems_solved, current_streak, longest_streak, "
                    "blank_solved, puzzle_solved, guided_solved, "
                    "easy_solved, medium_solved, hard_solved")\
            .eq("user_id", str(user_id))\
            .single()\
            .execute()
        stats_data = stats_result.data or {}

        # 난이도별 통계 (실제 컬럼 사용)
        solved_by_difficulty = {
            "easy": stats_data.get("easy_solved", 0),
            "medium": stats_data.get("medium_solved", 0),
            "hard": stats_data.get("hard_solved", 0),
        }

        return PublicStats(
            totalSolved=stats_data.get("problems_solved", 0),
            solvedByDifficulty=solved_by_difficulty,
            solvedByType={
                "blank": stats_data.get("blank_solved", 0),
                "puzzle": stats_data.get("puzzle_solved", 0),
                "guided": stats_data.get("guided_solved", 0),
            },
            currentStreak=stats_data.get("current_streak", 0),
            maxStreak=stats_data.get("longest_streak", 0),
            totalXP=stats_data.get("total_xp", 0),
            level=stats_data.get("level", 1),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get public stats: {str(e)}"
        )


@router.get("/{username}/public-activity", response_model=List[DailyActivity])
async def get_public_activity(
    username: str,
    days: int = 365,
    db=Depends(get_db)
):
    """Get public activity (grass) by username. No auth required."""
    try:
        from datetime import datetime, timedelta

        user = get_user_by_username(db, username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자를 찾을 수 없습니다."
            )

        user_id = user["id"]
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        result = db.table("daily_activity")\
            .select("activity_date, problems_solved, xp_earned, time_spent, blank_count, puzzle_count, guided_count")\
            .eq("user_id", str(user_id))\
            .gte("activity_date", start_date)\
            .order("activity_date", desc=False)\
            .execute()

        return [DailyActivity(
            date=item["activity_date"],
            problems_solved=item.get("problems_solved", 0),
            xp_earned=item.get("xp_earned", 0),
            time_spent=item.get("time_spent", 0),
            blank_count=item.get("blank_count", 0),
            puzzle_count=item.get("puzzle_count", 0),
            guided_count=item.get("guided_count", 0),
        ) for item in (result.data or [])]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get public activity: {str(e)}"
        )


@router.get("/{username}/public-farm", response_model=PublicFarm)
async def get_public_farm(
    username: str,
    db=Depends(get_db)
):
    """Get public farm minimap data by username. No auth required."""
    try:
        user = get_user_by_username(db, username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자를 찾을 수 없습니다."
            )

        user_id = user["id"]

        # Get farm data (필요한 컬럼만 선택)
        farm_result = db.table("farms")\
            .select("id, farm_level, gold, character_data")\
            .eq("user_id", str(user_id))\
            .single()\
            .execute()

        if not farm_result.data:
            return PublicFarm(hasCharacter=False)

        farm = farm_result.data
        character_data = farm.get("character_data")

        if not character_data:
            return PublicFarm(hasCharacter=False)

        # Get farm slots (필요한 컬럼만 선택)
        slots_result = db.table("farm_slots")\
            .select("slot_index, crop_type, growth_stage")\
            .eq("farm_id", farm["id"])\
            .order("slot_index")\
            .execute()

        slots = []
        for slot in (slots_result.data or []):
            slots.append(PublicFarmSlot(
                slotIndex=slot.get("slot_index", 0),
                cropType=slot.get("crop_type"),
                stage=slot.get("growth_stage", 0),
                isReady=slot.get("growth_stage", 0) >= 6,
            ))

        return PublicFarm(
            hasCharacter=True,
            character=PublicFarmCharacter(
                name=character_data.get("name", "농부"),
                hair=character_data.get("hair", "short"),
                hairColor=character_data.get("hairColor", "#8B4513"),
                face=character_data.get("face", "smile"),
                outfit=character_data.get("outfit", "overalls"),
                outfitColor=character_data.get("outfitColor", "#8B4513"),
                farmName=character_data.get("farmName", "나의 농장"),
            ),
            farmLevel=farm.get("farm_level", 1),
            gold=farm.get("gold", 0),
            slots=slots,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get public farm: {str(e)}"
        )


@router.get("/{username}/public-activity/{date}", response_model=DateActivityDetail)
async def get_public_activity_by_date(
    username: str,
    date: str,
    db=Depends(get_db)
):
    """Get public activity detail for a specific date. No auth required."""
    try:
        from datetime import datetime

        # Validate date format
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Use YYYY-MM-DD."
            )

        user = get_user_by_username(db, username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자를 찾을 수 없습니다."
            )

        user_id = user["id"]

        # Get daily activity summary (limit(1)로 0~1개 결과 허용)
        daily_result = db.table("daily_activity")\
            .select("problems_solved, xp_earned")\
            .eq("user_id", str(user_id))\
            .eq("activity_date", date)\
            .limit(1)\
            .execute()

        daily_data = daily_result.data[0] if daily_result.data else {}
        problems_solved = daily_data.get("problems_solved", 0)
        xp_earned = daily_data.get("xp_earned", 0)

        # Get solved problems with base_problems.name via JOIN
        start_of_day = f"{date}T00:00:00"
        end_of_day = f"{date}T23:59:59"
        problems = fetch_solved_problems_with_names(db, str(user_id), start_of_day, end_of_day)

        return DateActivityDetail(
            date=date,
            problems_solved=problems_solved if problems_solved else len(problems),
            xp_earned=xp_earned if xp_earned else sum(p.xp_earned for p in problems),
            problems=problems,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get public activity for date: {str(e)}"
        )


@router.get("/{username}/public-badges", response_model=List[PublicBadge])
async def get_public_badges(
    username: str,
    db=Depends(get_db)
):
    """Get public badges by username. No auth required."""
    try:
        user = get_user_by_username(db, username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자를 찾을 수 없습니다."
            )

        user_id = user["id"]

        result = db.table("user_badges")\
            .select("*, badges(*)")\
            .eq("user_id", str(user_id))\
            .execute()

        badges = []
        icon_map = {
            "first_problem": "🎯",
            "streak_7": "🔥",
            "streak_30": "🏆",
            "streak_100": "👑",
            "problems_50": "💪",
            "problems_100": "🎖️",
            "level_10": "⭐",
            "level_50": "🌟",
        }

        for badge_entry in (result.data or []):
            badge_data = badge_entry.get("badges", {}) or {}
            code = badge_data.get("code", "")
            badges.append(PublicBadge(
                id=str(badge_data.get("id", "")),
                name=badge_data.get("name", "Badge"),
                icon=icon_map.get(code, "🏅"),
                icon_url=badge_data.get("icon_url"),
                description=badge_data.get("description", ""),
                rarity=badge_data.get("rarity", "common"),
            ))

        return badges

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get public badges: {str(e)}"
        )


@router.get("/{username}/public-all", response_model=PublicProfileAll)
async def get_public_profile_all(
    username: str,
    days: int = 365,
    db=Depends(get_db)
):
    """
    Get all public profile data in a single request. No auth required.

    Combines: profile, badges, farm, activity into one response.
    This is optimized to reduce multiple API calls and DB queries.
    """
    try:
        from datetime import datetime, timedelta

        # 1. 사용자 조회 (한 번만!)
        user = get_user_by_username(db, username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자를 찾을 수 없습니다."
            )

        user_id = user["id"]

        # 2. 모든 데이터 병렬 조회 (동일 user_id 사용)
        # 2-1. Stats
        stats_result = db.table("user_stats")\
            .select("level, total_xp, problems_solved, current_streak")\
            .eq("user_id", str(user_id))\
            .single()\
            .execute()
        stats_data = stats_result.data or {}

        level = stats_data.get("level", 1)
        total_xp = stats_data.get("total_xp", 0)

        # 2-2. Badges
        badges_result = db.table("user_badges")\
            .select("*, badges(*)")\
            .eq("user_id", str(user_id))\
            .execute()

        icon_map = {
            "first_problem": "🎯",
            "streak_7": "🔥",
            "streak_30": "🏆",
            "streak_100": "👑",
            "problems_50": "💪",
            "problems_100": "🎖️",
            "level_10": "⭐",
            "level_50": "🌟",
        }

        badges = []
        for badge_entry in (badges_result.data or []):
            badge_data = badge_entry.get("badges", {}) or {}
            code = badge_data.get("code", "")
            badges.append(PublicBadge(
                id=str(badge_data.get("id", "")),
                name=badge_data.get("name", "Badge"),
                icon=icon_map.get(code, "🏅"),
                icon_url=badge_data.get("icon_url"),
                description=badge_data.get("description", ""),
                rarity=badge_data.get("rarity", "common"),
            ))

        # 2-3. Farm (user_farm 테이블 사용)
        farm = PublicFarm(hasCharacter=False)
        try:
            farm_result = db.table("user_farm")\
                .select("id, farm_level, gold, character_data, farm_slots")\
                .eq("user_id", str(user_id))\
                .single()\
                .execute()

            if farm_result.data:
                farm_data = farm_result.data
                character_data = farm_data.get("character_data")

                if character_data:
                    # farm_slots는 JSONB 컬럼
                    farm_slots_json = farm_data.get("farm_slots") or []
                    slots = [PublicFarmSlot(
                        slotIndex=slot.get("slot", 0),
                        cropType=slot.get("crop_code"),
                        stage=slot.get("stage", 0),
                        isReady=slot.get("stage", 0) >= 6,
                    ) for slot in farm_slots_json]

                    farm = PublicFarm(
                        hasCharacter=True,
                        character=PublicFarmCharacter(
                            name=character_data.get("name", "Farmer"),
                            hair=character_data.get("hair", "short"),
                            hairColor=character_data.get("hair_color", "#8B4513"),
                            face=character_data.get("face", "happy"),
                            outfit=character_data.get("outfit", "basic"),
                            outfitColor=character_data.get("outfit_color", "#4A90D9"),
                            farmName=character_data.get("farm_name", "My Farm"),
                        ),
                        farmLevel=farm_data.get("farm_level", 1),
                        gold=farm_data.get("gold", 0),
                        slots=slots,
                    )
        except Exception:
            pass  # Farm이 없으면 기본값 사용

        # 2-4. Activity (365 days)
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        activity_result = db.table("daily_activity")\
            .select("activity_date, problems_solved, xp_earned, time_spent, blank_count, puzzle_count, guided_count")\
            .eq("user_id", str(user_id))\
            .gte("activity_date", start_date)\
            .order("activity_date", desc=False)\
            .execute()

        activity_days = [DailyActivity(
            date=item["activity_date"],
            problems_solved=item.get("problems_solved", 0),
            xp_earned=item.get("xp_earned", 0),
            time_spent=item.get("time_spent", 0),
            blank_count=item.get("blank_count", 0),
            puzzle_count=item.get("puzzle_count", 0),
            guided_count=item.get("guided_count", 0),
        ) for item in (activity_result.data or [])]

        # 3. 통합 응답 구성
        return PublicProfileAll(
            profile=PublicProfile(
                id=str(user_id),
                username=user.get("name", "User"),
                avatarUrl=user.get("avatar_url"),
                avatarColor="hsl(142, 71%, 45%)",
                level=level,
                currentXP=calculate_current_xp(total_xp, level),
                requiredXP=calculate_required_xp(level),
                totalXP=total_xp,
                solvedCount=stats_data.get("problems_solved", 0),
                streak=stats_data.get("current_streak", 0),
                joinedAt=user.get("created_at", ""),
            ),
            badges=badges,
            farm=farm,
            activity=PublicActivityData(
                days=activity_days,
                totalDays=len(activity_days),
            ),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get public profile: {str(e)}"
        )


# ============================================================
# Batch Interaction API (프론트엔드 로컬 버퍼링용)
# ============================================================

from pydantic import BaseModel


class InteractionItem(BaseModel):
    """단일 상호작용 아이템"""
    type: str  # click, select, view, etc.
    data: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}
    timestamp: Optional[str] = None  # ISO format


class BatchInteractionsRequest(BaseModel):
    """배치 상호작용 요청"""
    interactions: List[InteractionItem]
    session_id: Optional[str] = None


class BatchInteractionsResponse(BaseModel):
    """배치 상호작용 응답"""
    success: bool
    logged_count: int
    message: str


@router.post("/interactions/batch", response_model=BatchInteractionsResponse)
async def log_interactions_batch(
    request: BatchInteractionsRequest,
    user_id: UUID = Depends(get_current_user_id),
):
    """
    프론트엔드에서 로컬에 버퍼링한 상호작용들을 배치로 전송

    프론트엔드 사용 예시:
    ```javascript
    // 로컬 버퍼에 쌓기
    interactionBuffer.push({ type: 'click', data: { ... }, timestamp: new Date().toISOString() });

    // 주기적으로 또는 페이지 이탈 시 전송
    if (interactionBuffer.length >= 10) {
        await fetch('/api/users/interactions/batch', {
            method: 'POST',
            body: JSON.stringify({ interactions: interactionBuffer })
        });
        interactionBuffer.length = 0;
    }
    ```
    """
    from ..services.stats_cache import get_stats_cache

    try:
        cache = get_stats_cache()
        interactions_dicts = [
            {
                "type": item.type,
                "data": item.data,
                "metadata": item.metadata,
                "timestamp": item.timestamp,
            }
            for item in request.interactions
        ]

        logged_count = await cache.log_interactions_batch(
            user_id=str(user_id),
            interactions=interactions_dicts,
            session_id=request.session_id,
        )

        return BatchInteractionsResponse(
            success=True,
            logged_count=logged_count,
            message=f"{logged_count}개의 상호작용이 기록되었습니다",
        )

    except Exception as e:
        return BatchInteractionsResponse(
            success=False,
            logged_count=0,
            message=f"기록 실패: {str(e)}",
        )


@router.get("/interactions/buffer-status")
async def get_buffer_status(
    user_id: UUID = Depends(get_current_user_id),
):
    """캐시 버퍼 상태 조회 (디버깅/모니터링용)"""
    from ..services.stats_cache import get_stats_cache

    cache = get_stats_cache()
    return cache.get_buffer_status()
