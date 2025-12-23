from fastapi import APIRouter, HTTPException, Depends, status, Header
from typing import Optional, List
from uuid import UUID
from jose import jwt, JWTError

from ..database import get_db
from ..config import get_settings
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
)

router = APIRouter()
settings = get_settings()


async def get_current_user_id(authorization: str = Header(...), db=Depends(get_db)) -> UUID:
    """Extract and verify user ID from authorization header.

    Supports both:
    - Supabase Auth tokens (for email/password login)
    - Self-generated JWT tokens (for Kakao OAuth login)
    """
    try:
        token = authorization.replace("Bearer ", "")

        # First, try Supabase Auth token verification
        try:
            user = db.auth.get_user(token)
            if user is not None and user.user is not None:
                return UUID(user.user.id)
        except Exception:
            pass  # Not a Supabase token, try self-generated JWT

        # Second, try self-generated JWT verification (for Kakao OAuth)
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret,
                algorithms=[settings.jwt_algorithm]
            )
            token_type = payload.get("type")
            user_id = payload.get("sub")

            if token_type != "access" or not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )

            return UUID(user_id)
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )


@router.get("/me", response_model=UserProfile)
async def get_current_user(
    user_id: UUID = Depends(get_current_user_id),
    db=Depends(get_db)
):
    """Get current user's full profile."""
    try:
        # Get user
        user_result = db.table("users").select("*").eq("id", str(user_id)).single().execute()

        # Get stats
        stats_result = db.table("user_stats").select("*").eq("user_id", str(user_id)).single().execute()

        # Get preferences
        prefs_result = db.table("user_preferences").select("*").eq("user_id", str(user_id)).single().execute()

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
            .select("*")\
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
            .select("*")\
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
            .select("*")\
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
            bug_count=item.get("bug_count", 0),
            output_count=item.get("output_count", 0),
            refactor_count=item.get("refactor_count", 0),
        ) for item in (result.data or [])]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get activity: {str(e)}"
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
            .select("id, problem_id, is_correct, xp_earned, submitted_at, problems(code_id, problem_type, codes(title))")\
            .eq("user_id", str(user_id))\
            .eq("is_correct", True)\
            .order("submitted_at", desc=True)\
            .limit(limit)\
            .execute()

        for attempt in (attempts_result.data or []):
            problem = attempt.get("problems", {})
            code = problem.get("codes", {}) if problem else {}
            title = code.get("title", "Problem") if code else "Problem"
            problem_type = problem.get("problem_type", "blank") if problem else "blank"

            activities.append(RecentActivity(
                id=attempt["id"],
                type="solved",
                title=f"Solved: {title}",
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
        # Get user
        user_result = db.table("users").select("*").eq("id", str(user_id)).single().execute()
        user_data = user_result.data

        # Get stats
        stats_result = db.table("user_stats").select("*").eq("user_id", str(user_id)).single().execute()
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
        # Get stats
        stats_result = db.table("user_stats").select("*").eq("user_id", str(user_id)).single().execute()
        stats_data = stats_result.data or {}

        # Get solved counts by difficulty (from attempts + problems)
        difficulty_result = db.table("attempts")\
            .select("problems(difficulty)")\
            .eq("user_id", str(user_id))\
            .eq("is_correct", True)\
            .execute()

        solved_by_difficulty = {"easy": 0, "medium": 0, "hard": 0}
        for attempt in (difficulty_result.data or []):
            problem = attempt.get("problems", {})
            difficulty = problem.get("difficulty", "medium") if problem else "medium"
            if difficulty in solved_by_difficulty:
                solved_by_difficulty[difficulty] += 1

        return MypageStats(
            totalSolved=stats_data.get("problems_solved", 0),
            solvedByDifficulty=solved_by_difficulty,
            solvedByType={
                "blank": stats_data.get("blank_solved", 0),
                "puzzle": stats_data.get("bug_solved", 0) + stats_data.get("output_solved", 0),
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
