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
