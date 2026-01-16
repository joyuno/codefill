"""
Admin Router

관리자 기능 API 엔드포인트
- 사용자 관리
- 문제 관리
- 문제 생성
"""

from fastapi import APIRouter, HTTPException, Depends, Query, status
from typing import Optional, List
from uuid import UUID, uuid4
from datetime import datetime, timedelta

from ..database import get_db
from ..dependencies import get_current_admin_user
from ..models.admin import (
    # Users
    AdminUserListResponse,
    AdminUserListItem,
    AdminUserDetail,
    AdminUserBadge,
    AdminRecentActivity,
    UpdateUserRoleRequest,
    BanUserRequest,
    BanUserResponse,
    # Problems
    AdminProblemListResponse,
    AdminProblemListItem,
    AdminBaseProblemDetail,
    UpdateBaseProblemRequest,
    BlankVariant,
    PuzzleVariant,
    GuidedVariant,
    # Create Problems
    CreateBaseProblemRequest,
    CreateBlankProblemRequest,
    CreatePuzzleProblemRequest,
    CreateGuidedProblemRequest,
    CreateProblemResponse,
    # Update Variants
    UpdateBlankProblemRequest,
    UpdatePuzzleProblemRequest,
    UpdateGuidedProblemRequest,
    VariantResponse,
    # Dashboard
    AdminDashboardStats,
)

router = APIRouter()


# ============================================================
# 대시보드
# ============================================================

@router.get("/dashboard", response_model=AdminDashboardStats)
async def get_dashboard_stats(
    admin=Depends(get_current_admin_user),
    db=Depends(get_db)
):
    """관리자 대시보드 통계"""
    try:
        # 전체 사용자 수
        users_result = db.table("users").select("id", count="exact").is_("deleted_at", "null").execute()
        total_users = users_result.count or 0

        # 전체 문제 수
        problems_result = db.table("base_problems").select("id", count="exact").is_("deleted_at", "null").execute()
        total_problems = problems_result.count or 0

        # 전체 제출 수
        submissions_result = db.table("attempts").select("id", count="exact").execute()
        total_submissions = submissions_result.count or 0

        # 오늘 활성 사용자 수 (user_stats.last_activity_date = today)
        today = datetime.utcnow().date().isoformat()
        active_result = db.table("user_stats").select("id", count="exact").eq("last_activity_date", today).execute()
        active_users_today = active_result.count or 0

        # 이번 주 신규 사용자 수 (users.created_at >= 7일 전)
        week_ago = (datetime.utcnow() - timedelta(days=7)).isoformat()
        new_users_result = db.table("users").select("id", count="exact").gte("created_at", week_ago).is_("deleted_at", "null").execute()
        new_users_this_week = new_users_result.count or 0

        return AdminDashboardStats(
            total_users=total_users,
            total_problems=total_problems,
            total_submissions=total_submissions,
            active_users_today=active_users_today,
            new_users_this_week=new_users_this_week,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get dashboard stats: {str(e)}"
        )


# ============================================================
# 사용자 관리 API
# ============================================================

@router.get("/users", response_model=AdminUserListResponse)
async def list_users(
    search: Optional[str] = None,
    role: Optional[str] = None,
    include_banned: bool = False,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    admin=Depends(get_current_admin_user),
    db=Depends(get_db)
):
    """관리자: 사용자 목록 조회"""
    try:
        now = datetime.utcnow().isoformat()

        # 전체 개수 조회
        count_query = db.table("users").select("id", count="exact")

        if not include_banned:
            # 정지되지 않은 사용자만: banned_until이 NULL이거나 현재 시간보다 이전
            count_query = count_query.or_(f"banned_until.is.null,banned_until.lt.{now}")
        if role:
            count_query = count_query.eq("role", role)
        if search:
            count_query = count_query.or_(f"email.ilike.%{search}%,name.ilike.%{search}%")

        count_result = count_query.execute()
        total = count_result.count or 0

        # 데이터 조회
        query = db.table("users").select(
            "id, email, name, role, avatar_url, provider, created_at, deleted_at, banned_until"
        )

        if not include_banned:
            # 정지되지 않은 사용자만
            query = query.or_(f"banned_until.is.null,banned_until.lt.{now}")
        if role:
            query = query.eq("role", role)
        if search:
            query = query.or_(f"email.ilike.%{search}%,name.ilike.%{search}%")

        # 페이지네이션
        offset = (page - 1) * limit
        query = query.order("created_at", desc=True).range(offset, offset + limit - 1)

        result = query.execute()
        users_data = result.data or []

        # user_stats 조회
        user_ids = [u["id"] for u in users_data]
        stats_map = {}

        if user_ids:
            stats_result = db.table("user_stats").select(
                "user_id, level, total_xp, problems_solved"
            ).in_("user_id", user_ids).execute()

            for stat in (stats_result.data or []):
                stats_map[stat["user_id"]] = stat

        # 응답 생성
        items = []
        for user in users_data:
            stats = stats_map.get(user["id"], {})
            items.append(AdminUserListItem(
                id=user["id"],
                email=user["email"],
                name=user.get("name"),
                role=user.get("role", "user"),
                avatar_url=user.get("avatar_url"),
                provider=user.get("provider", "email"),
                created_at=user["created_at"],
                deleted_at=user.get("deleted_at"),
                banned_until=user.get("banned_until"),
                level=stats.get("level", 1),
                total_xp=stats.get("total_xp", 0),
                problems_solved=stats.get("problems_solved", 0),
            ))

        has_more = (page * limit) < total

        return AdminUserListResponse(
            items=items,
            total=total,
            page=page,
            limit=limit,
            has_more=has_more,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list users: {str(e)}"
        )


@router.get("/users/{user_id}", response_model=AdminUserDetail)
async def get_user_detail(
    user_id: UUID,
    admin=Depends(get_current_admin_user),
    db=Depends(get_db)
):
    """관리자: 사용자 상세 조회"""
    try:
        # 사용자 정보 조회
        user_result = db.table("users").select("*").eq("id", str(user_id)).single().execute()

        if not user_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        user = user_result.data

        # 통계 조회
        stats_result = db.table("user_stats").select("*").eq("user_id", str(user_id)).single().execute()
        stats = stats_result.data or {}

        # 설정 조회
        prefs_result = db.table("user_preferences").select(
            "preferred_language, daily_goal"
        ).eq("user_id", str(user_id)).single().execute()
        prefs = prefs_result.data or {}

        # 구독 정보 조회
        sub_result = db.table("subscriptions").select(
            "expires_at"
        ).eq("user_id", str(user_id)).eq("status", "active").single().execute()
        subscription = sub_result.data or {}

        # 배지 조회 (최근 10개)
        badges_result = db.table("user_badges").select(
            "id, earned_at, badges(code, name, description, icon_url, rarity)"
        ).eq("user_id", str(user_id)).order("earned_at", desc=True).limit(10).execute()

        badges = []
        for badge_entry in (badges_result.data or []):
            badge_info = badge_entry.get("badges", {})
            if badge_info:
                badges.append(AdminUserBadge(
                    id=badge_entry["id"],
                    code=badge_info.get("code", ""),
                    name=badge_info.get("name", ""),
                    description=badge_info.get("description"),
                    icon_url=badge_info.get("icon_url"),
                    rarity=badge_info.get("rarity", "common"),
                    earned_at=badge_entry["earned_at"],
                ))

        # 최근 활동 조회 (최근 10개)
        attempts_result = db.table("attempts").select(
            "id, problem_type, xp_earned, submitted_at"
        ).eq("user_id", str(user_id)).eq("is_correct", True).order(
            "submitted_at", desc=True
        ).limit(10).execute()

        recent_activity = []
        for attempt in (attempts_result.data or []):
            problem_type = attempt.get("problem_type", "blank") or "blank"
            recent_activity.append(AdminRecentActivity(
                id=attempt["id"],
                type="solved",
                title=f"{problem_type.capitalize()} 문제 해결",
                description=f"{problem_type} 유형 문제 완료",
                timestamp=attempt["submitted_at"],
                xp_earned=attempt.get("xp_earned", 0),
            ))

        return AdminUserDetail(
            id=user["id"],
            email=user["email"],
            name=user.get("name"),
            username=user.get("username"),
            role=user.get("role", "user"),
            avatar_url=user.get("avatar_url"),
            provider=user.get("provider", "email"),
            subscription_tier=user.get("subscription_tier", "free"),
            subscription_expires_at=subscription.get("expires_at"),
            created_at=user["created_at"],
            updated_at=user.get("updated_at"),
            deleted_at=user.get("deleted_at"),
            banned_until=user.get("banned_until"),
            last_activity_date=stats.get("last_activity_date"),
            level=stats.get("level", 1),
            total_xp=stats.get("total_xp", 0),
            problems_solved=stats.get("problems_solved", 0),
            problems_attempted=stats.get("problems_attempted", 0),
            current_streak=stats.get("current_streak", 0),
            longest_streak=stats.get("longest_streak", 0),
            blank_solved=stats.get("blank_solved", 0),
            puzzle_solved=stats.get("puzzle_solved", 0),
            guided_solved=stats.get("guided_solved", 0),
            preferred_language=prefs.get("preferred_language"),
            daily_goal=prefs.get("daily_goal"),
            current_status=user.get("current_status"),
            learning_goal=user.get("learning_goal"),
            experience_level=user.get("experience_level"),
            badges=badges,
            recent_activity=recent_activity,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user detail: {str(e)}"
        )


@router.put("/users/{user_id}/role")
async def update_user_role(
    user_id: UUID,
    request: UpdateUserRoleRequest,
    admin=Depends(get_current_admin_user),
    db=Depends(get_db)
):
    """관리자: 사용자 역할 변경"""
    try:
        # 자기 자신의 역할은 변경 불가
        if str(user_id) == admin.get("id"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot change your own role"
            )

        result = db.table("users").update({
            "role": request.role,
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", str(user_id)).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return {
            "success": True,
            "user_id": user_id,
            "role": request.role,
            "message": f"User role updated to {request.role}"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user role: {str(e)}"
        )


@router.put("/users/{user_id}/ban", response_model=BanUserResponse)
async def ban_user(
    user_id: UUID,
    request: BanUserRequest,
    admin=Depends(get_current_admin_user),
    db=Depends(get_db)
):
    """관리자: 사용자 정지/해제 (banned_until 활용)"""
    from datetime import timedelta

    try:
        # 자기 자신은 정지 불가
        if str(user_id) == admin.get("id"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot ban yourself"
            )

        update_data = {
            "updated_at": datetime.utcnow().isoformat()
        }

        banned_until_str = None
        if request.is_banned:
            if request.ban_days and request.ban_days > 0:
                # 임시 정지: N일 후까지
                banned_until = datetime.utcnow() + timedelta(days=request.ban_days)
            else:
                # 영구 정지: 9999년 12월 31일
                banned_until = datetime(9999, 12, 31, 23, 59, 59)
            banned_until_str = banned_until.isoformat()
            update_data["banned_until"] = banned_until_str
        else:
            # 정지 해제
            update_data["banned_until"] = None

        result = db.table("users").update(update_data).eq("id", str(user_id)).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        if request.is_banned:
            if request.ban_days and request.ban_days > 0:
                action_msg = f"{request.ban_days}일 정지되었습니다"
            else:
                action_msg = "영구 정지되었습니다"
        else:
            action_msg = "정지가 해제되었습니다"

        return BanUserResponse(
            success=True,
            user_id=user_id,
            is_banned=request.is_banned,
            banned_until=banned_until_str,
            message=action_msg
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ban/unban user: {str(e)}"
        )


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: UUID,
    admin=Depends(get_current_admin_user),
    db=Depends(get_db)
):
    """
    관리자: 사용자 완전 삭제 (복구 불가)

    모든 관련 데이터가 CASCADE 삭제됩니다.
    - user_stats, user_preferences, attempts, hint_logs, daily_activity,
      user_badges, subscriptions, problem_solutions, solution_votes, comment_votes: CASCADE
    - solution_comments: SET NULL (익명화)
    """
    try:
        # 자기 자신은 삭제 불가
        if str(user_id) == admin.get("id"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="자기 자신은 삭제할 수 없습니다"
            )

        # 사용자 존재 확인
        user_check = db.table("users").select("id, email, name, role").eq("id", str(user_id)).execute()
        if not user_check.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자를 찾을 수 없습니다"
            )

        user = user_check.data[0]

        # 관리자 삭제 시 추가 경고 (다른 관리자만 가능)
        if user.get("role") == "admin":
            # 다른 관리자가 있는지 확인
            other_admins = db.table("users").select("id", count="exact").eq("role", "admin").neq("id", str(user_id)).is_("deleted_at", "null").execute()
            if not other_admins.count or other_admins.count == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="마지막 관리자는 삭제할 수 없습니다"
                )

        # 완전 삭제 (CASCADE로 연관 데이터 자동 삭제)
        result = db.table("users").delete().eq("id", str(user_id)).execute()
        deleted_count = len(result.data) if result.data else 0

        if deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="사용자 삭제에 실패했습니다"
            )

        # 삭제 확인
        verify = db.table("users").select("id").eq("id", str(user_id)).execute()
        if verify.data and len(verify.data) > 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="사용자 삭제 확인에 실패했습니다"
            )

        return {
            "success": True,
            "message": f"사용자 '{user.get('name') or user.get('email')}'이(가) 완전히 삭제되었습니다"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"사용자 삭제 실패: {str(e)}"
        )


# ============================================================
# 문제 관리 API
# ============================================================

@router.get("/problems", response_model=AdminProblemListResponse)
async def list_problems(
    search: Optional[str] = None,
    difficulty: Optional[str] = None,
    source: Optional[str] = None,
    include_deleted: bool = False,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    admin=Depends(get_current_admin_user),
    db=Depends(get_db)
):
    """관리자: 문제 목록 조회"""
    try:
        # 전체 개수 조회
        count_query = db.table("base_problems").select("id", count="exact")

        if not include_deleted:
            count_query = count_query.is_("deleted_at", "null")
        if difficulty:
            count_query = count_query.eq("difficulty", difficulty)
        if source:
            count_query = count_query.eq("source", source)
        if search:
            count_query = count_query.or_(f"name.ilike.%{search}%,original_id.ilike.%{search}%")

        count_result = count_query.execute()
        total = count_result.count or 0

        # 데이터 조회
        query = db.table("base_problems").select(
            "id, original_id, name, difficulty, source, tags, solve_count, like_count, created_at, deleted_at"
        )

        if not include_deleted:
            query = query.is_("deleted_at", "null")
        if difficulty:
            query = query.eq("difficulty", difficulty)
        if source:
            query = query.eq("source", source)
        if search:
            query = query.or_(f"name.ilike.%{search}%,original_id.ilike.%{search}%")

        # 페이지네이션
        offset = (page - 1) * limit
        query = query.order("created_at", desc=True).range(offset, offset + limit - 1)

        result = query.execute()
        problems_data = result.data or []

        # 변형 문제 존재 여부 확인 (base_problem_id 사용)
        # base_problems.id를 사용해서 variant 테이블 조회
        base_problem_ids = [p["id"] for p in problems_data]
        # original_id -> id 매핑 (응답용)
        id_to_original = {p["id"]: p["original_id"] for p in problems_data}

        blank_exists = set()
        puzzle_exists = set()
        guided_exists = set()

        if base_problem_ids:
            # Blank 존재 확인 (base_problem_id 사용)
            blank_result = db.table("problems_blank").select("base_problem_id").in_("base_problem_id", base_problem_ids).execute()
            blank_exists = {id_to_original[b["base_problem_id"]] for b in (blank_result.data or []) if b["base_problem_id"] in id_to_original}

            # Puzzle 존재 확인 (base_problem_id 사용)
            puzzle_result = db.table("problems_puzzle").select("base_problem_id").in_("base_problem_id", base_problem_ids).execute()
            puzzle_exists = {id_to_original[p["base_problem_id"]] for p in (puzzle_result.data or []) if p["base_problem_id"] in id_to_original}

            # Guided 존재 확인 (base_problem_id 사용)
            guided_result = db.table("problems_guided").select("base_problem_id").in_("base_problem_id", base_problem_ids).execute()
            guided_exists = {id_to_original[g["base_problem_id"]] for g in (guided_result.data or []) if g["base_problem_id"] in id_to_original}

        # 응답 생성
        items = []
        for problem in problems_data:
            items.append(AdminProblemListItem(
                id=problem["id"],
                original_id=problem["original_id"],
                name=problem["name"],
                difficulty=problem["difficulty"],
                source=problem.get("source"),
                tags=problem.get("tags", []),
                solve_count=problem.get("solve_count", 0),
                like_count=problem.get("like_count", 0),
                has_blank=problem["original_id"] in blank_exists,
                has_puzzle=problem["original_id"] in puzzle_exists,
                has_guided=problem["original_id"] in guided_exists,
                created_at=problem.get("created_at"),
                deleted_at=problem.get("deleted_at"),
            ))

        has_more = (page * limit) < total

        return AdminProblemListResponse(
            items=items,
            total=total,
            page=page,
            limit=limit,
            has_more=has_more,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list problems: {str(e)}"
        )


@router.get("/problems/{original_id}", response_model=AdminBaseProblemDetail)
async def get_problem_detail(
    original_id: str,
    admin=Depends(get_current_admin_user),
    db=Depends(get_db)
):
    """관리자: 문제 상세 조회 (변형 포함)"""
    try:
        # 원본 문제 조회
        problem_result = db.table("base_problems").select("*").eq("original_id", original_id).single().execute()

        if not problem_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Problem not found"
            )

        problem = problem_result.data
        base_problem_id = problem["id"]

        # Blank 변형 조회 (base_problem_id 사용)
        blank_result = db.table("problems_blank").select("*").eq("base_problem_id", base_problem_id).execute()
        blanks = [
            BlankVariant(
                id=b["id"],
                language=b["language"],
                code_template=b["code_template"],
                answers=b.get("answers", []),
                created_at=b.get("created_at"),
            )
            for b in (blank_result.data or [])
        ]

        # Puzzle 변형 조회 (base_problem_id 사용)
        puzzle_result = db.table("problems_puzzle").select("*").eq("base_problem_id", base_problem_id).execute()
        puzzles = [
            PuzzleVariant(
                id=p["id"],
                language=p["language"],
                fixed_start=p.get("fixed_start"),
                fixed_end=p.get("fixed_end"),
                blocks=p.get("blocks", []),
                created_at=p.get("created_at"),
            )
            for p in (puzzle_result.data or [])
        ]

        # Guided 변형 조회 (base_problem_id 사용, DB 스키마에 맞춤)
        guided_result = db.table("problems_guided").select("*").eq("base_problem_id", base_problem_id).execute()
        guideds = [
            GuidedVariant(
                id=g["id"],
                language=g["language"],
                concept_explanation=g.get("concept_explanation", ""),
                variables_guide=g.get("variables_guide", []),
                approach_guide=g.get("approach_guide", ""),
                starter_code=g.get("starter_code", ""),
                status=g.get("status", "in_progress"),
                attempts_count=g.get("attempts_count", 0),
                hints_given=g.get("hints_given", 0),
                created_at=g.get("created_at"),
            )
            for g in (guided_result.data or [])
        ]

        return AdminBaseProblemDetail(
            id=problem["id"],
            original_id=problem["original_id"],
            name=problem["name"],
            question=problem["question"],
            difficulty=problem["difficulty"],
            tags=problem.get("tags", []),
            source=problem.get("source"),
            url=problem.get("url"),
            time_limit=problem.get("time_limit"),
            memory_limit=problem.get("memory_limit"),
            input_output=problem.get("input_output"),
            solutions=problem.get("solutions", []),
            created_at=problem.get("created_at"),
            deleted_at=problem.get("deleted_at"),
            blanks=blanks,
            puzzles=puzzles,
            guideds=guideds,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get problem detail: {str(e)}"
        )


@router.put("/problems/{original_id}")
async def update_problem(
    original_id: str,
    request: UpdateBaseProblemRequest,
    admin=Depends(get_current_admin_user),
    db=Depends(get_db)
):
    """관리자: 원본 문제 수정"""
    try:
        update_data = request.model_dump(exclude_unset=True, exclude_none=True)

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )

        update_data["updated_at"] = datetime.utcnow().isoformat()

        result = db.table("base_problems").update(update_data).eq("original_id", original_id).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Problem not found"
            )

        return {
            "success": True,
            "original_id": original_id,
            "message": "Problem updated successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update problem: {str(e)}"
        )


@router.delete("/problems/{original_id}")
async def delete_problem(
    original_id: str,
    admin=Depends(get_current_admin_user),
    db=Depends(get_db)
):
    """관리자: 문제 soft delete"""
    try:
        result = db.table("base_problems").update({
            "deleted_at": datetime.utcnow().isoformat()
        }).eq("original_id", original_id).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Problem not found"
            )

        return {
            "success": True,
            "original_id": original_id,
            "message": "Problem deleted successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete problem: {str(e)}"
        )


# ============================================================
# 문제 생성 API
# ============================================================

@router.post("/problems/base", response_model=CreateProblemResponse)
async def create_base_problem(
    request: CreateBaseProblemRequest,
    admin=Depends(get_current_admin_user),
    db=Depends(get_db)
):
    """관리자: 원본 문제 생성"""
    try:
        # 중복 확인
        existing = db.table("base_problems").select("id").eq("original_id", request.original_id).execute()

        if existing.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Problem with original_id '{request.original_id}' already exists"
            )

        # 문제 생성
        problem_id = uuid4()
        problem_data = {
            "id": str(problem_id),
            "original_id": request.original_id,
            "name": request.name,
            "question": request.question,
            "difficulty": request.difficulty,
            "tags": request.tags,
            "source": request.source,
            "url": request.url,
            "time_limit": request.time_limit,
            "memory_limit": request.memory_limit,
            "input_output": request.input_output,
            "solutions": [s.model_dump() for s in request.solutions],
            "solve_count": 0,
            "like_count": 0,
            "created_at": datetime.utcnow().isoformat(),
        }

        result = db.table("base_problems").insert(problem_data).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create problem"
            )

        return CreateProblemResponse(
            success=True,
            id=problem_id,
            original_id=request.original_id,
            message="Base problem created successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create base problem: {str(e)}"
        )


@router.post("/problems/{original_id}/blank", response_model=CreateProblemResponse)
async def create_blank_problem(
    original_id: str,
    request: CreateBlankProblemRequest,
    admin=Depends(get_current_admin_user),
    db=Depends(get_db)
):
    """관리자: 빈칸 채우기 문제 생성"""
    try:
        # 원본 문제 존재 확인
        base_result = db.table("base_problems").select("id").eq("original_id", original_id).single().execute()

        if not base_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Base problem not found"
            )

        # 중복 확인 (동일 언어) - base_problem_id 사용
        existing = db.table("problems_blank").select("id").eq("base_problem_id", base_result.data["id"]).eq("language", request.language).execute()

        if existing.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Blank problem for {request.language} already exists"
            )

        # 생성 (base_problem_id만 사용, original_id 컬럼은 삭제됨)
        blank_id = uuid4()
        blank_data = {
            "id": str(blank_id),
            "base_problem_id": base_result.data["id"],
            "creator_id": admin.get("id"),
            "language": request.language,
            "code_template": request.code_template,
            "answers": request.answers,
            "created_at": datetime.utcnow().isoformat(),
        }

        result = db.table("problems_blank").insert(blank_data).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create blank problem"
            )

        return CreateProblemResponse(
            success=True,
            id=blank_id,
            original_id=original_id,
            message=f"Blank problem ({request.language}) created successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create blank problem: {str(e)}"
        )


@router.post("/problems/{original_id}/puzzle", response_model=CreateProblemResponse)
async def create_puzzle_problem(
    original_id: str,
    request: CreatePuzzleProblemRequest,
    admin=Depends(get_current_admin_user),
    db=Depends(get_db)
):
    """관리자: 퍼즐 문제 생성"""
    try:
        # 원본 문제 존재 확인
        base_result = db.table("base_problems").select("id").eq("original_id", original_id).single().execute()

        if not base_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Base problem not found"
            )

        # 중복 확인 (동일 언어) - base_problem_id 사용
        existing = db.table("problems_puzzle").select("id").eq("base_problem_id", base_result.data["id"]).eq("language", request.language).execute()

        if existing.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Puzzle problem for {request.language} already exists"
            )

        # 생성 (base_problem_id만 사용, original_id 컬럼은 삭제됨)
        puzzle_id = uuid4()
        puzzle_data = {
            "id": str(puzzle_id),
            "base_problem_id": base_result.data["id"],
            "creator_id": admin.get("id"),
            "language": request.language,
            "fixed_start": request.fixed_start,
            "fixed_end": request.fixed_end,
            "blocks": [b.model_dump() for b in request.blocks],
            "created_at": datetime.utcnow().isoformat(),
        }

        result = db.table("problems_puzzle").insert(puzzle_data).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create puzzle problem"
            )

        return CreateProblemResponse(
            success=True,
            id=puzzle_id,
            original_id=original_id,
            message=f"Puzzle problem ({request.language}) created successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create puzzle problem: {str(e)}"
        )


@router.post("/problems/{original_id}/guided", response_model=CreateProblemResponse)
async def create_guided_problem(
    original_id: str,
    request: CreateGuidedProblemRequest,
    admin=Depends(get_current_admin_user),
    db=Depends(get_db)
):
    """관리자: 가이드 문제 생성"""
    try:
        # 원본 문제 존재 확인
        base_result = db.table("base_problems").select("id").eq("original_id", original_id).single().execute()

        if not base_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Base problem not found"
            )

        # 중복 확인 (동일 언어) - base_problem_id 사용
        existing = db.table("problems_guided").select("id").eq("base_problem_id", base_result.data["id"]).eq("language", request.language).execute()

        if existing.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Guided problem for {request.language} already exists"
            )

        # 생성 (DB 스키마에 맞춤)
        guided_id = uuid4()
        guided_data = {
            "id": str(guided_id),
            "base_problem_id": base_result.data["id"],
            "creator_id": admin.get("id"),
            "language": request.language,
            "concept_explanation": request.concept_explanation,
            "variables_guide": [v.model_dump() for v in request.variables_guide],
            "approach_guide": request.approach_guide,
            "starter_code": request.starter_code,
            "status": "in_progress",
            "created_at": datetime.utcnow().isoformat(),
        }

        result = db.table("problems_guided").insert(guided_data).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create guided problem"
            )

        return CreateProblemResponse(
            success=True,
            id=guided_id,
            original_id=original_id,
            message=f"Guided problem ({request.language}) created successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create guided problem: {str(e)}"
        )


# ============================================================
# 변형 문제 수정 API
# ============================================================

@router.put("/problems/{original_id}/blank/{blank_id}", response_model=VariantResponse)
async def update_blank_problem(
    original_id: str,
    blank_id: UUID,
    request: UpdateBlankProblemRequest,
    admin=Depends(get_current_admin_user),
    db=Depends(get_db)
):
    """관리자: 빈칸 문제 수정"""
    try:
        update_data = request.model_dump(exclude_unset=True, exclude_none=True)
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )

        update_data["updated_at"] = datetime.utcnow().isoformat()
        result = db.table("problems_blank").update(update_data).eq("id", str(blank_id)).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Blank problem not found")

        return VariantResponse(success=True, message="Blank problem updated successfully")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update blank problem: {str(e)}")


@router.put("/problems/{original_id}/puzzle/{puzzle_id}", response_model=VariantResponse)
async def update_puzzle_problem(
    original_id: str,
    puzzle_id: UUID,
    request: UpdatePuzzleProblemRequest,
    admin=Depends(get_current_admin_user),
    db=Depends(get_db)
):
    """관리자: 퍼즐 문제 수정"""
    try:
        update_data = request.model_dump(exclude_unset=True, exclude_none=True)
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )

        # blocks를 JSON 직렬화
        if "blocks" in update_data and update_data["blocks"]:
            update_data["blocks"] = [b.model_dump() if hasattr(b, 'model_dump') else b for b in update_data["blocks"]]

        update_data["updated_at"] = datetime.utcnow().isoformat()
        result = db.table("problems_puzzle").update(update_data).eq("id", str(puzzle_id)).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Puzzle problem not found")

        return VariantResponse(success=True, message="Puzzle problem updated successfully")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update puzzle problem: {str(e)}")


@router.put("/problems/{original_id}/guided/{guided_id}", response_model=VariantResponse)
async def update_guided_problem(
    original_id: str,
    guided_id: UUID,
    request: UpdateGuidedProblemRequest,
    admin=Depends(get_current_admin_user),
    db=Depends(get_db)
):
    """관리자: 가이드 문제 수정"""
    try:
        update_data = request.model_dump(exclude_unset=True, exclude_none=True)
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )

        # variables_guide를 JSON 직렬화
        if "variables_guide" in update_data and update_data["variables_guide"]:
            update_data["variables_guide"] = [v.model_dump() if hasattr(v, 'model_dump') else v for v in update_data["variables_guide"]]

        update_data["updated_at"] = datetime.utcnow().isoformat()
        result = db.table("problems_guided").update(update_data).eq("id", str(guided_id)).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Guided problem not found")

        return VariantResponse(success=True, message="Guided problem updated successfully")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update guided problem: {str(e)}")


# ============================================================
# 변형 문제 삭제 API
# ============================================================

@router.delete("/problems/{original_id}/blank/{blank_id}", response_model=VariantResponse)
async def delete_blank_problem(
    original_id: str,
    blank_id: UUID,
    admin=Depends(get_current_admin_user),
    db=Depends(get_db)
):
    """관리자: 빈칸 문제 삭제"""
    try:
        result = db.table("problems_blank").delete().eq("id", str(blank_id)).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Blank problem not found")

        return VariantResponse(success=True, message="Blank problem deleted successfully")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete blank problem: {str(e)}")


@router.delete("/problems/{original_id}/puzzle/{puzzle_id}", response_model=VariantResponse)
async def delete_puzzle_problem(
    original_id: str,
    puzzle_id: UUID,
    admin=Depends(get_current_admin_user),
    db=Depends(get_db)
):
    """관리자: 퍼즐 문제 삭제"""
    try:
        result = db.table("problems_puzzle").delete().eq("id", str(puzzle_id)).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Puzzle problem not found")

        return VariantResponse(success=True, message="Puzzle problem deleted successfully")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete puzzle problem: {str(e)}")


@router.delete("/problems/{original_id}/guided/{guided_id}", response_model=VariantResponse)
async def delete_guided_problem(
    original_id: str,
    guided_id: UUID,
    admin=Depends(get_current_admin_user),
    db=Depends(get_db)
):
    """관리자: 가이드 문제 삭제"""
    try:
        result = db.table("problems_guided").delete().eq("id", str(guided_id)).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Guided problem not found")

        return VariantResponse(success=True, message="Guided problem deleted successfully")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete guided problem: {str(e)}")


# ============================================================
# 문제 복구 API
# ============================================================

@router.post("/problems/{original_id}/restore", response_model=VariantResponse)
async def restore_problem(
    original_id: str,
    admin=Depends(get_current_admin_user),
    db=Depends(get_db)
):
    """관리자: 삭제된 문제 복구"""
    try:
        result = db.table("base_problems").update({
            "deleted_at": None,
            "updated_at": datetime.utcnow().isoformat()
        }).eq("original_id", original_id).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Problem not found")

        return VariantResponse(success=True, message="Problem restored successfully")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to restore problem: {str(e)}")


# ============================================================
# 커뮤니티 솔루션/댓글 관리 API
# ============================================================

@router.delete("/solutions/{solution_id}", response_model=VariantResponse)
async def admin_delete_solution(
    solution_id: UUID,
    admin=Depends(get_current_admin_user),
    db=Depends(get_db)
):
    """관리자: 커뮤니티 풀이 삭제"""
    try:
        # 먼저 풀이 존재 확인
        check = db.table("problem_solutions").select("id").eq("id", str(solution_id)).single().execute()
        if not check.data:
            raise HTTPException(status_code=404, detail="Solution not found")

        # 연관된 댓글 삭제
        db.table("solution_comments").delete().eq("solution_id", str(solution_id)).execute()

        # 연관된 투표 삭제
        db.table("solution_votes").delete().eq("solution_id", str(solution_id)).execute()

        # 풀이 삭제
        result = db.table("problem_solutions").delete().eq("id", str(solution_id)).execute()

        return VariantResponse(success=True, message="Solution deleted successfully")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete solution: {str(e)}")


@router.delete("/solutions/comments/{comment_id}", response_model=VariantResponse)
async def admin_delete_comment(
    comment_id: UUID,
    admin=Depends(get_current_admin_user),
    db=Depends(get_db)
):
    """관리자: 커뮤니티 댓글 삭제"""
    try:
        # 댓글 존재 및 대댓글 여부 확인
        result = db.table("solution_comments")\
            .select("id, parent_id")\
            .eq("id", str(comment_id))\
            .single()\
            .execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Comment not found")

        # 대댓글이 있는지 확인
        replies = db.table("solution_comments")\
            .select("id", count="exact")\
            .eq("parent_id", str(comment_id))\
            .execute()

        if replies.count and replies.count > 0:
            # 대댓글이 있으면 소프트 삭제
            db.table("solution_comments")\
                .update({"is_deleted": True, "content": "[관리자에 의해 삭제된 댓글입니다]"})\
                .eq("id", str(comment_id))\
                .execute()
        else:
            # 대댓글이 없으면 하드 삭제
            db.table("comment_votes").delete().eq("comment_id", str(comment_id)).execute()
            db.table("solution_comments").delete().eq("id", str(comment_id)).execute()

        return VariantResponse(success=True, message="Comment deleted successfully")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete comment: {str(e)}")
