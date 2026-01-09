from fastapi import APIRouter, HTTPException, Depends, status
from typing import Optional
from uuid import UUID
from datetime import datetime

from ..database import get_db
from ..dependencies import (
    get_current_user_id as get_user_id_from_token,
    get_current_user_id_optional as get_user_id_from_token_optional,
)  # 공통 인증 의존성
from ..models.practice import (
    BlankSubmission,
    PuzzleSubmission,
    SubmissionResponse,
    SubmissionResult,
    CodeExecutionRequest,
    CodeExecutionResponse,
    XPConfig,
    RecordSubmission,
    RecordResponse,
    HintCheckResponse,
    HintUseResponse,
    StartPracticeRequest,
    StartPracticeResponse,
    AttemptDetailAction,
    NewBadge,  # 뱃지 응답용 모델
    FeedbackData,  # 피드백 데이터 모델
    # Session tracking models
    SessionHeartbeatRequest,
    SessionHeartbeatResponse,
    SessionEndRequest,
    SessionEndResponse,
)
from ..models.problem import ProblemType
from ..services.badge_service import get_badge_service

router = APIRouter()


# ============================================================
# Helper Functions
# ============================================================

def get_next_attempt_number(db, user_id: str, base_problem_id: str) -> int:
    """동일 문제에 대한 다음 시도 번호 계산 (base_problem_id 기준)"""
    try:
        result = db.table("attempts")\
            .select("attempt_number")\
            .eq("user_id", user_id)\
            .eq("base_problem_id", base_problem_id)\
            .order("attempt_number", desc=True)\
            .limit(1)\
            .execute()

        if result.data and len(result.data) > 0:
            return (result.data[0].get("attempt_number") or 0) + 1
        return 1
    except Exception:
        return 1


def check_blank_answers(submitted: dict, correct: list) -> tuple[bool, dict]:
    """Check blank fill answers."""
    results = {}
    all_correct = True

    for blank in correct:
        blank_id = blank["id"]
        correct_answer = blank["answer"].strip().lower()
        submitted_answer = submitted.get(blank_id, "").strip().lower()

        is_correct = correct_answer == submitted_answer
        results[blank_id] = is_correct
        if not is_correct:
            all_correct = False

    return all_correct, results


async def resolve_base_problem_id(db, problem_id: str) -> Optional[str]:
    """
    problem_id에서 base_problem_id를 결정합니다.

    문제 ID가 다양한 형태로 전달될 수 있습니다:
    1. base_problems 테이블의 UUID (id)
    2. base_problems 테이블의 original_id (예: "taco_100")
    3. problems_blank/puzzle/guided 테이블의 UUID

    이 함수는 어떤 형태든 base_problems.id로 변환합니다.
    """
    if not problem_id:
        return None

    from uuid import UUID as UUIDType

    try:
        # 1. UUID 형식인지 확인
        try:
            problem_uuid = UUIDType(problem_id)
            uuid_str = str(problem_uuid)

            # 1-1. base_problems 테이블에서 직접 조회
            bp_result = db.table("base_problems")\
                .select("id")\
                .eq("id", uuid_str)\
                .limit(1)\
                .execute()

            if bp_result.data and len(bp_result.data) > 0:
                return bp_result.data[0]["id"]

            # 1-2. problems_blank에서 original_id로 base_problems 찾기
            blank_result = db.table("problems_blank")\
                .select("original_id")\
                .eq("id", uuid_str)\
                .limit(1)\
                .execute()

            if blank_result.data and len(blank_result.data) > 0:
                original_id = blank_result.data[0].get("original_id")
                if original_id:
                    bp_result = db.table("base_problems")\
                        .select("id")\
                        .eq("original_id", original_id)\
                        .limit(1)\
                        .execute()
                    if bp_result.data:
                        return bp_result.data[0]["id"]

            # 1-3. problems_puzzle에서 찾기
            puzzle_result = db.table("problems_puzzle")\
                .select("original_id")\
                .eq("id", uuid_str)\
                .limit(1)\
                .execute()

            if puzzle_result.data and len(puzzle_result.data) > 0:
                original_id = puzzle_result.data[0].get("original_id")
                if original_id:
                    bp_result = db.table("base_problems")\
                        .select("id")\
                        .eq("original_id", original_id)\
                        .limit(1)\
                        .execute()
                    if bp_result.data:
                        return bp_result.data[0]["id"]

            # 1-4. problems_guided에서 찾기
            guided_result = db.table("problems_guided")\
                .select("original_id")\
                .eq("id", uuid_str)\
                .limit(1)\
                .execute()

            if guided_result.data and len(guided_result.data) > 0:
                original_id = guided_result.data[0].get("original_id")
                if original_id:
                    bp_result = db.table("base_problems")\
                        .select("id")\
                        .eq("original_id", original_id)\
                        .limit(1)\
                        .execute()
                    if bp_result.data:
                        return bp_result.data[0]["id"]

        except ValueError:
            pass  # UUID 형식이 아님

        # 2. original_id 형식 (예: "taco_100", "boj_1234")
        bp_result = db.table("base_problems")\
            .select("id")\
            .eq("original_id", problem_id)\
            .limit(1)\
            .execute()

        if bp_result.data and len(bp_result.data) > 0:
            return bp_result.data[0]["id"]

        return None

    except Exception as e:
        print(f"[resolve_base_problem_id] Error: {e}")
        return None


# ============================================================
# Practice Start - Create Pending Attempt
# ============================================================

@router.post("/start", response_model=StartPracticeResponse)
async def start_practice(
    request: StartPracticeRequest,
    user_id: Optional[UUID] = Depends(get_user_id_from_token_optional),
    db=Depends(get_db)
):
    """
    문제 풀이 시작 - pending attempt 생성 + 세션 추적 시작

    문제 풀이를 시작할 때 호출하여 attempt_id를 발급받습니다.
    이 attempt_id로 힌트 요청, 제출 등의 상세 기록을 추적합니다.
    SessionTracker로 세션 상태(진행/포기/완료)도 추적합니다.

    Returns:
        attempt_id: 시도 ID (UUID)
        started_at: 시작 시간
        session_id: 세션 ID (세션 추적용)
    """
    from ..services.session_tracker import get_session_tracker

    if not user_id:
        # 비로그인 시에도 임시 attempt_id 발급 (DB 저장 없이)
        import uuid
        temp_id = str(uuid.uuid4())
        return StartPracticeResponse(
            attempt_id=f"temp_{temp_id}",
            started_at=datetime.utcnow().isoformat(),
            message="임시 세션입니다. 로그인하면 기록이 저장됩니다."
        )

    try:
        from uuid import UUID as UUIDType

        # 시작 시간 기록
        started_at_dt = datetime.utcnow()

        # 기본 attempt 데이터 (pending 상태 - is_correct=False로 시작)
        attempt_data = {
            "user_id": str(user_id),
            "is_correct": False,  # 시작 시 False, 제출 시 업데이트
            "xp_earned": 0,
            "problem_type": request.problem_type,
            "difficulty": request.difficulty,
            "problem_name": request.problem_name,
            "topics": request.topics,
            "hints_used": 0,
            "total_hints_requested": 0,
            "started_at": started_at_dt.isoformat(),  # 시작 시간 명시적 저장
        }

        # base_problem_id 추가 - base_problems.id로 변환해서 저장
        # attempts.base_problem_id가 base_problems.id를 직접 참조
        if request.problem_id:
            resolved_problem_id = await resolve_base_problem_id(db, request.problem_id)
            if resolved_problem_id:
                attempt_data["base_problem_id"] = resolved_problem_id
                print(f"[StartPractice] Resolved base_problem_id: {request.problem_id} -> {resolved_problem_id}")
            else:
                print(f"[StartPractice] WARNING: Could not resolve to base_problems.id: {request.problem_id}")

        # attempts 테이블에 pending 레코드 생성
        result = db.table("attempts").insert(attempt_data).execute()

        if result.data and len(result.data) > 0:
            attempt_id = result.data[0]["id"]
            started_at = started_at_dt.isoformat()
            print(f"[StartPractice] Created pending attempt: {attempt_id}")

            # 🚀 SessionTracker 세션 시작
            session_id = None
            try:
                tracker = get_session_tracker()
                session_id = await tracker.start_session(
                    user_id=str(user_id),
                    problem_id=request.problem_id,
                    problem_type=request.problem_type or "blank",
                    metadata={
                        "attempt_id": str(attempt_id),
                        "difficulty": request.difficulty,
                        "problem_name": request.problem_name,
                        "topics": request.topics or [],
                    }
                )
                print(f"[StartPractice] Session started: {session_id}")

                # ✅ session_id를 attempts 테이블에 저장
                if session_id:
                    db.table("attempts").update({
                        "session_id": session_id
                    }).eq("id", attempt_id).execute()
                    print(f"[StartPractice] Linked session_id to attempt")

            except Exception as e:
                print(f"[StartPractice] Session tracking error (non-blocking): {e}")

            # ✅ chat_sessions 테이블에 attempt_id 연결
            if request.chat_session_id:
                try:
                    db.table("chat_sessions").update({
                        "attempt_id": str(attempt_id),
                        "current_stage": "solving",
                        "solve_start_time": started_at_dt.isoformat(),
                    }).eq("id", request.chat_session_id).execute()
                    print(f"[StartPractice] Linked attempt_id to chat_session: {request.chat_session_id}")
                except Exception as e:
                    print(f"[StartPractice] chat_sessions update error (non-blocking): {e}")

            return StartPracticeResponse(
                attempt_id=str(attempt_id),
                started_at=started_at,
                session_id=session_id,
                message="문제 풀이를 시작합니다."
            )

        raise Exception("Failed to create attempt record")

    except Exception as e:
        import traceback
        print(f"[StartPractice] Error: {e}")
        traceback.print_exc()

        # 에러 시에도 임시 ID 반환
        import uuid
        temp_id = str(uuid.uuid4())
        return StartPracticeResponse(
            attempt_id=f"temp_{temp_id}",
            started_at=datetime.utcnow().isoformat(),
            message=f"임시 세션입니다. (오류: {str(e)[:50]})"
        )


# ============================================================
# Attempt Detail Recording Helper
# ============================================================

def record_attempt_detail(
    db,
    attempt_id: str,
    action_type: str,
    step_number: int = None,
    **kwargs
) -> bool:
    """
    attempt_details 테이블에 상세 기록 저장 (내부 헬퍼)

    Args:
        db: Supabase client
        attempt_id: attempt UUID
        action_type: AttemptDetailAction 값
        step_number: 순서 번호
        **kwargs: 유형별 추가 필드
    """
    # temp_ 로 시작하면 DB 기록 안함
    if attempt_id.startswith("temp_"):
        print(f"[AttemptDetail] Skipping temp attempt: {attempt_id}")
        return False

    try:
        detail_data = {
            "attempt_id": attempt_id,
            "action_type": action_type,
            "step_number": step_number if step_number is not None else 1,
            "hint_was_requested": kwargs.get("hint_was_requested", False),
        }

        # 추가 필드 (None이 아닌 것만)
        for key, value in kwargs.items():
            if value is not None and key != "hint_was_requested":
                detail_data[key] = value

        db.table("attempt_details").insert(detail_data).execute()
        print(f"[AttemptDetail] Recorded: attempt={attempt_id[:8]}..., action={action_type}")
        return True

    except Exception as e:
        print(f"[AttemptDetail] Error recording: {e}")
        return False


# NOTE: record_hint_log 함수 제거됨
# hint_logs 테이블은 attempt_details로 통합
# 힌트 기록은 record_attempt_detail()에서 xp_cost와 함께 처리


@router.post("/submit/blank", response_model=SubmissionResponse)
async def submit_blank(
    submission: BlankSubmission,
    user_id: UUID = Depends(get_user_id_from_token),
    db=Depends(get_db)
):
    """Submit answer for blank-fill problem."""
    try:
        # Get problem and correct answers (+ title, tags for complete recording)
        result = db.table("problems")\
            .select("answer_data, difficulty, title, tags")\
            .eq("id", str(submission.problem_id))\
            .single()\
            .execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Problem not found"
            )

        answer_data = result.data.get("answer_data", {})
        correct_blanks = answer_data.get("blanks", [])
        difficulty = result.data.get("difficulty")
        problem_name = result.data.get("title")
        topics = result.data.get("tags", [])

        # Check answers
        is_correct, blank_results = check_blank_answers(submission.answers, correct_blanks)

        # Check if already solved (for repeat solve detection)
        already_solved = False
        if is_correct:
            prev_attempt = db.table("attempts")\
                .select("id")\
                .eq("user_id", str(user_id))\
                .eq("problem_id", str(submission.problem_id))\
                .eq("is_correct", True)\
                .limit(1)\
                .execute()
            already_solved = bool(prev_attempt.data)

        # Calculate XP based on difficulty (1/4 if repeat)
        base_xp = XPConfig.get_xp_for_difficulty(difficulty, "blank") if is_correct else 0
        xp_earned = base_xp // 4 if already_solved else base_xp

        # Save attempt with all fields
        attempt_number = get_next_attempt_number(db, str(user_id), str(submission.problem_id))
        attempt_result = db.table("attempts").insert({
            "user_id": str(user_id),
            "problem_id": str(submission.problem_id),
            "is_correct": is_correct,
            "submitted_answer": str(submission.answers),
            "xp_earned": xp_earned,
            "attempt_number": attempt_number,
            "problem_type": "blank",
            "difficulty": difficulty,
            "problem_name": problem_name,
            "topics": topics,
            "hints_used": 0,
            "total_hints_requested": 0,
            "started_at": datetime.utcnow().isoformat(),
        }).execute()

        # Record attempt_details for submission
        if attempt_result.data and len(attempt_result.data) > 0:
            attempt_id = attempt_result.data[0]["id"]
            record_attempt_detail(
                db=db,
                attempt_id=str(attempt_id),
                action_type=AttemptDetailAction.BLANK_SUBMIT.value,
                step_number=1,
                blank_is_correct=is_correct,
            )

        # Update user stats and check badges if correct
        new_badges = None
        if is_correct:
            db.rpc("increment_user_stats", {
                "p_user_id": str(user_id),
                "p_xp": xp_earned,
                "p_problem_type": "blank",
                "p_difficulty": difficulty,
                "p_is_repeat": already_solved,
            }).execute()

            # Check and award badges (only for first solve)
            badge_service = get_badge_service()
            awarded = await badge_service.check_and_award_badges(
                user_id=str(user_id),
                trigger_type='solve',
                problem_type='blank',
                difficulty=difficulty,
            ) if not already_solved else []
            if awarded:
                new_badges = [NewBadge(**b) for b in awarded]

        return SubmissionResponse(
            result=SubmissionResult.CORRECT if is_correct else SubmissionResult.INCORRECT,
            is_correct=is_correct,
            xp_earned=xp_earned,
            blank_results=blank_results,
            feedback="정답입니다!" if is_correct else "틀린 빈칸이 있습니다. 다시 확인해보세요.",
            new_badges=new_badges,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit: {str(e)}"
        )


@router.post("/submit/puzzle", response_model=SubmissionResponse)
async def submit_puzzle(
    submission: PuzzleSubmission,
    user_id: UUID = Depends(get_user_id_from_token),
    db=Depends(get_db)
):
    """Submit answer for puzzle (Parsons) problem."""
    try:
        # Get problem and correct answer data (+ title, tags for complete recording)
        result = db.table("problems")\
            .select("answer_data, difficulty, title, tags")\
            .eq("id", str(submission.problem_id))\
            .single()\
            .execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Problem not found"
            )

        answer_data = result.data.get("answer_data", {})
        correct_order = answer_data.get("correct_order", [])
        correct_blocks = {b["id"]: b for b in answer_data.get("blocks", [])}
        difficulty = result.data.get("difficulty")
        problem_name = result.data.get("title")
        topics = result.data.get("tags", [])

        # Check block order and indentation
        puzzle_results = {}
        all_correct = True
        wrong_positions = []

        submitted_ids = [b.id for b in submission.block_order]
        user_order = [{"id": b.id, "indent": b.indentation} for b in submission.block_order]

        # Check if order matches
        for i, block in enumerate(submission.block_order):
            block_id = block.id

            # Check if block is in correct position
            is_correct_position = (i < len(correct_order) and correct_order[i] == block_id)

            # Check if indentation is correct
            correct_block = correct_blocks.get(block_id, {})
            correct_indent = correct_block.get("indentation", 0)
            is_correct_indent = (block.indentation == correct_indent)

            is_block_correct = is_correct_position and is_correct_indent
            puzzle_results[block_id] = is_block_correct

            if not is_block_correct:
                all_correct = False
                wrong_positions.append({
                    "index": i,
                    "block_id": block_id,
                    "wrong_position": not is_correct_position,
                    "wrong_indent": not is_correct_indent,
                })

        # Also check if all required blocks are present
        if len(submission.block_order) != len(correct_order):
            all_correct = False

        # Check if already solved (for repeat solve detection)
        already_solved = False
        if all_correct:
            prev_attempt = db.table("attempts")\
                .select("id")\
                .eq("user_id", str(user_id))\
                .eq("problem_id", str(submission.problem_id))\
                .eq("is_correct", True)\
                .limit(1)\
                .execute()
            already_solved = bool(prev_attempt.data)

        # Calculate XP based on difficulty (1/4 if repeat)
        base_xp = XPConfig.get_xp_for_difficulty(difficulty, "puzzle") if all_correct else 0
        xp_earned = base_xp // 4 if already_solved else base_xp

        # Save attempt with all fields
        attempt_number = get_next_attempt_number(db, str(user_id), str(submission.problem_id))
        attempt_result = db.table("attempts").insert({
            "user_id": str(user_id),
            "problem_id": str(submission.problem_id),
            "is_correct": all_correct,
            "submitted_answer": str(user_order),
            "xp_earned": xp_earned,
            "attempt_number": attempt_number,
            "problem_type": "puzzle",
            "difficulty": difficulty,
            "problem_name": problem_name,
            "topics": topics,
            "hints_used": 0,
            "total_hints_requested": 0,
            "started_at": datetime.utcnow().isoformat(),
        }).execute()

        # Record attempt_details for submission
        if attempt_result.data and len(attempt_result.data) > 0:
            attempt_id = attempt_result.data[0]["id"]
            record_attempt_detail(
                db=db,
                attempt_id=str(attempt_id),
                action_type=AttemptDetailAction.PUZZLE_SUBMIT.value,
                step_number=1,
                puzzle_user_order=user_order,
                puzzle_correct_order=correct_order,
                puzzle_wrong_positions=wrong_positions if wrong_positions else None,
            )

        # Update user stats and check badges if correct
        new_badges = None
        if all_correct:
            db.rpc("increment_user_stats", {
                "p_user_id": str(user_id),
                "p_xp": xp_earned,
                "p_problem_type": "puzzle",
                "p_difficulty": difficulty,
                "p_is_repeat": already_solved,
            }).execute()

            # Check and award badges (only for first solve)
            if not already_solved:
                badge_service = get_badge_service()
                awarded = await badge_service.check_and_award_badges(
                    user_id=str(user_id),
                    trigger_type='solve',
                    problem_type='puzzle',
                    difficulty=difficulty,
                )
                if awarded:
                    new_badges = [NewBadge(**b) for b in awarded]

        if all_correct:
            feedback = "정답입니다! 코드 블록을 올바른 순서와 들여쓰기로 배열했습니다."
        else:
            wrong_count = sum(1 for v in puzzle_results.values() if not v)
            feedback = f"틀렸습니다. {wrong_count}개의 블록이 잘못된 위치나 들여쓰기를 가지고 있습니다."

        return SubmissionResponse(
            result=SubmissionResult.CORRECT if all_correct else SubmissionResult.INCORRECT,
            is_correct=all_correct,
            xp_earned=xp_earned,
            feedback=feedback,
            puzzle_results=puzzle_results,
            new_badges=new_badges,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit: {str(e)}"
        )


@router.post("/run", response_model=CodeExecutionResponse)
async def run_code(request: CodeExecutionRequest):
    """
    Execute code and return output.

    Judge0 API를 통해 Python/Java/C++ 코드를 실행합니다.
    JavaScript/React는 프론트엔드에서 Sandpack으로 처리됩니다.
    """
    from ..services.judge0 import judge0_service

    # JavaScript는 프론트엔드 Sandpack에서 처리
    if request.language.lower() in ["javascript", "js", "react", "jsx", "tsx"]:
        return CodeExecutionResponse(
            success=False,
            error="JavaScript/React는 프론트엔드에서 실행됩니다. Sandpack을 사용하세요.",
        )

    try:
        # Judge0 API를 통해 코드 실행
        result = await judge0_service.submit_code(
            source_code=request.code,
            language=request.language,
            stdin=request.test_input or "",
        )

        if not result.get("success"):
            return CodeExecutionResponse(
                success=False,
                error=result.get("error") or result.get("detail") or "코드 실행에 실패했습니다.",
            )

        # 실행 시간 변환 (초 -> 밀리초)
        execution_time_ms = None
        if result.get("time"):
            try:
                execution_time_ms = int(float(result["time"]) * 1000)
            except (ValueError, TypeError):
                pass

        # 에러 확인 (stderr, compile_output)
        error_msg = None
        if result.get("stderr"):
            error_msg = result["stderr"]
        elif result.get("compile_output"):
            error_msg = result["compile_output"]
        elif result.get("is_error"):
            error_msg = result.get("message", "실행 중 오류가 발생했습니다.")

        return CodeExecutionResponse(
            success=not result.get("is_error", False),
            output=result.get("stdout", ""),
            error=error_msg,
            execution_time=execution_time_ms,
        )

    except Exception as e:
        return CodeExecutionResponse(
            success=False,
            error=f"코드 실행 오류: {str(e)}",
        )


VALID_DIFFICULTIES = {"easy", "medium", "medium_hard", "hard", "very_hard"}


@router.post("/submit/record", response_model=RecordResponse)
async def record_solve(
    submission: RecordSubmission,
    user_id: Optional[UUID] = Depends(get_user_id_from_token_optional),
    db=Depends(get_db)
):
    """
    Record problem solve for XP and grass (daily activity).

    문제 풀이를 기록하고 XP/잔디를 업데이트합니다.
    XP는 항상 difficulty 기반으로 계산됩니다 (클라이언트 xp_earned 무시).

    Features:
    - 로그인 안 해도 에러 없이 처리 (XP 기록만 안 됨)
    - 이미 푼 문제는 1/4 XP만 부여
    - difficulty 필수 (easy, medium, medium_hard, hard, very_hard)
    """
    # 로그인 안 한 경우 조용히 처리
    if not user_id:
        print(f"[RecordSolve] No user_id - skipping record")
        return RecordResponse(
            success=False,
            xp_earned=0,
            message="로그인이 필요합니다."
        )

    try:
        # difficulty 유효성 검증
        difficulty = submission.difficulty
        if not difficulty or difficulty not in VALID_DIFFICULTIES:
            print(f"[RecordSolve] Invalid difficulty: {difficulty}")
            return RecordResponse(
                success=False,
                xp_earned=0,
                message=f"유효하지 않은 난이도입니다: {difficulty}"
            )

        # XP는 항상 difficulty 기반으로 계산 (클라이언트가 보낸 xp_earned 무시)
        if submission.is_correct:
            base_xp = XPConfig.get_xp_for_difficulty(difficulty, submission.problem_type)
        else:
            base_xp = 0

        # base_problem_id 결정 (핵심: 반복 풀이 체크 + 잔디에 사용)
        # 여러 소스에서 결정: submission.base_problem_id > submission.problem_id
        base_problem_id = None

        # 1. 직접 전달된 base_problem_id 사용
        if submission.base_problem_id:
            base_problem_id = await resolve_base_problem_id(db, submission.base_problem_id)

        # 2. problem_id로 base_problem_id 찾기
        if not base_problem_id:
            base_problem_id = await resolve_base_problem_id(db, submission.problem_id)

        print(f"[RecordSolve] Resolved base_problem_id: {base_problem_id} (from problem_id={submission.problem_id})")

        # 이미 푼 문제인지 확인 (base_problem_id로 검색)
        already_solved = False
        xp_earned = base_xp

        # 이전 풀이 체크: base_problem_id 기준
        if base_problem_id:
            try:
                prev_attempt = db.table("attempts")\
                    .select("id")\
                    .eq("user_id", str(user_id))\
                    .eq("base_problem_id", base_problem_id)\
                    .eq("is_correct", True)\
                    .limit(1)\
                    .execute()

                if prev_attempt.data and len(prev_attempt.data) > 0:
                    already_solved = True
                    xp_earned = base_xp // 4  # 1/4 XP
                    print(f"[RecordSolve] Already solved (base_problem_id={base_problem_id}), reducing XP: {base_xp} -> {xp_earned}")
            except Exception as check_err:
                print(f"[RecordSolve] Error checking previous solve: {check_err}")

        # attempts 테이블에 기록 시도
        attempt_id_used = None
        try:
            from uuid import UUID as UUIDType

            # attempt_id가 있으면 기존 attempt 업데이트, 없으면 새로 생성
            if submission.attempt_id and not submission.attempt_id.startswith("temp_"):
                # 기존 pending attempt 업데이트 (직접 UPDATE 사용 - 더 많은 필드 업데이트)
                try:
                    update_data = {
                        "is_correct": submission.is_correct,
                        "xp_earned": xp_earned,
                        "submitted_answer": f"type:{submission.problem_type}",
                        # ✅ 추가 필드
                        "submitted_code": submission.submitted_code,
                        "time_spent": submission.time_spent,
                    }
                    # session_id가 있으면 업데이트 (없으면 기존 유지)
                    if submission.session_id:
                        update_data["session_id"] = submission.session_id
                    # base_problem_id 업데이트 (base_problems.id 직접 참조)
                    if base_problem_id:
                        update_data["base_problem_id"] = base_problem_id

                    db.table("attempts").update(update_data).eq("id", submission.attempt_id).execute()
                    attempt_id_used = submission.attempt_id
                    print(f"[RecordSolve] Updated existing attempt: {attempt_id_used}")
                except Exception as e:
                    print(f"[RecordSolve] Failed to update existing attempt, will create new: {e}")
                    attempt_id_used = None

            # 기존 attempt 업데이트 실패 또는 attempt_id 없음 → 새로 생성
            if not attempt_id_used:
                # 기본 attempt 데이터 (모든 컬럼 채우기)
                attempt_data = {
                    "user_id": str(user_id),
                    "is_correct": submission.is_correct,
                    "xp_earned": xp_earned,
                    "problem_type": submission.problem_type,
                    "submitted_answer": f"type:{submission.problem_type}",
                    "hints_used": submission.hints_used or 0,
                    "difficulty": submission.difficulty,
                    "problem_name": submission.problem_name,
                    "total_hints_requested": submission.hints_used or 0,
                    "topics": submission.topics,
                    # ✅ 추가 필드: submitted_code, time_spent, session_id
                    "submitted_code": submission.submitted_code,
                    "time_spent": submission.time_spent,
                    "session_id": submission.session_id,
                }

                # base_problem_id에 base_problems.id를 저장
                # attempts.base_problem_id가 base_problems.id를 직접 참조함
                if base_problem_id:
                    attempt_data["base_problem_id"] = base_problem_id
                    # 동일 문제 시도 번호 계산 (base_problem_id 기준)
                    attempt_data["attempt_number"] = get_next_attempt_number(
                        db, str(user_id), base_problem_id
                    )
                else:
                    attempt_data["attempt_number"] = 1
                    print(f"[RecordSolve] WARNING: No base_problem_id resolved for problem_id={submission.problem_id}")

                result = db.table("attempts").insert(attempt_data).execute()
                if result.data and len(result.data) > 0:
                    attempt_id_used = result.data[0]["id"]
                print(f"[RecordSolve] New attempt recorded: problem_id={submission.problem_id}, attempt_id={attempt_id_used}")

            # attempt_details에 제출 기록 추가
            if attempt_id_used:
                action_type = {
                    "blank": AttemptDetailAction.BLANK_SUBMIT.value,
                    "puzzle": AttemptDetailAction.PUZZLE_SUBMIT.value,
                    "guided": AttemptDetailAction.GUIDED_STEP_COMPLETE.value,
                }.get(submission.problem_type, "blank_submit")

                # 문제 유형별 상세 데이터 준비
                detail_kwargs = {
                    "hint_was_requested": submission.hints_used > 0 if submission.hints_used else False,
                }

                if submission.problem_type == "blank":
                    detail_kwargs["blank_is_correct"] = submission.is_correct
                    # 힌트 레벨 (힌트 사용 횟수 기반)
                    detail_kwargs["blank_hint_level"] = min(submission.hints_used or 0, 2)
                elif submission.problem_type == "puzzle":
                    # puzzle은 puzzle_ 필드 사용
                    detail_kwargs["puzzle_validation_method"] = "exact"
                elif submission.problem_type == "guided":
                    detail_kwargs["guided_step"] = 0  # 최종 제출
                    detail_kwargs["guided_understanding_score"] = 1.0 if submission.is_correct else 0.5
                    if submission.topics:
                        detail_kwargs["guided_concepts_covered"] = submission.topics

                # record_attempt_detail 함수 사용
                record_attempt_detail(
                    db=db,
                    attempt_id=str(attempt_id_used),
                    action_type=action_type,
                    step_number=1,  # 최종 제출은 step 1
                    **detail_kwargs
                )
                print(f"[RecordSolve] Recorded attempt_detail: {action_type}")

        except Exception as insert_err:
            # FK 제약 등으로 실패해도 XP 기록은 계속
            print(f"[RecordSolve] Attempts insert failed (non-blocking): {insert_err}")

        # 정답인 경우 user stats 업데이트 (XP, 잔디) - 이건 항상 시도
        new_badges = None
        if submission.is_correct and xp_earned > 0:
            try:
                db.rpc("increment_user_stats", {
                    "p_user_id": str(user_id),
                    "p_xp": xp_earned,
                    "p_problem_type": submission.problem_type,
                    "p_difficulty": submission.difficulty,
                    "p_is_repeat": already_solved,
                }).execute()
                print(f"[RecordSolve] Updated user stats: +{xp_earned} XP, type={submission.problem_type}, repeat={already_solved}")

                # Check and award badges (only for first solve)
                if not already_solved:
                    badge_service = get_badge_service()
                    awarded = await badge_service.check_and_award_badges(
                        user_id=str(user_id),
                        trigger_type='solve',
                        problem_type=submission.problem_type,
                        difficulty=submission.difficulty,
                    )
                    if awarded:
                        new_badges = [NewBadge(**b) for b in awarded]
                        print(f"[RecordSolve] Awarded {len(awarded)} badges")

                # Update mission progress (daily/weekly missions)
                try:
                    from ..services.mission_service import MissionService
                    mission_service = MissionService(db)

                    # problem_type에 따른 condition_type 매핑
                    condition_type = submission.problem_type  # blank, puzzle, output, bug, refactor
                    if submission.problem_type == "guided":
                        condition_type = "problems"  # guided는 일반 문제로 처리

                    # 미션 진행률 업데이트 (일일 + 주간)
                    mission_service.update_progress(
                        user_id=str(user_id),
                        condition_type=condition_type,
                        difficulty=submission.difficulty,
                        increment=1
                    )

                    # 'problems' 조건도 함께 업데이트 (모든 문제 풀이 미션)
                    if condition_type != "problems":
                        mission_service.update_progress(
                            user_id=str(user_id),
                            condition_type="problems",
                            difficulty=submission.difficulty,
                            increment=1
                        )

                    print(f"[RecordSolve] Updated mission progress: type={condition_type}, diff={submission.difficulty}")
                except Exception as mission_err:
                    print(f"[RecordSolve] Mission progress update error (non-blocking): {mission_err}")

            except Exception as rpc_err:
                print(f"[RecordSolve] RPC error: {rpc_err}")
                return RecordResponse(
                    success=False,
                    xp_earned=0,
                    message=f"XP 업데이트 실패: {str(rpc_err)}"
                )

        # ============================================================
        # user_skill_profiles 업데이트 (ELO-like 스킬 추적)
        # ============================================================
        if submission.topics and len(submission.topics) > 0:
            try:
                from ..services.feedback_service import get_feedback_service
                feedback_service = get_feedback_service()
                await feedback_service.update_skill_profile(
                    user_id=str(user_id),
                    problem_topics=submission.topics,
                    difficulty=submission.difficulty or "medium",
                    is_correct=submission.is_correct,
                )
                print(f"[RecordSolve] Updated skill profile for topics: {submission.topics}")
            except Exception as skill_err:
                print(f"[RecordSolve] Skill profile update error (non-blocking): {skill_err}")

        # ============================================================
        # user_memories 세션 메모리 생성
        # ============================================================
        try:
            from ..services.memory_service import get_memory_service
            import uuid as uuid_module
            memory_service = get_memory_service()
            session_id = submission.attempt_id or str(uuid_module.uuid4())
            await memory_service.create_problem_session_memory(
                user_id=str(user_id),
                session_id=session_id,
                problem_id=submission.problem_id,
                problem_name=submission.problem_name or "Unknown",
                problem_type=submission.problem_type,
                difficulty=submission.difficulty or "medium",
                topics=submission.topics or [],
                was_successful=submission.is_correct,
                hints_used=submission.hints_used or 0,
                attempt_id=str(attempt_id_used) if attempt_id_used else None,  # attempt 참조 추가
            )
            print(f"[RecordSolve] Created session memory for user {str(user_id)[:8]}...")
        except Exception as mem_err:
            print(f"[RecordSolve] Memory creation error (non-blocking): {mem_err}")

        # ============================================================
        # 피드백 생성 및 feedback_history 저장
        # ============================================================
        feedback_data = None
        if submission.is_correct:
            try:
                from ..services.feedback_service import get_feedback_service
                fb_service = get_feedback_service()
                feedback_result = await fb_service.generate_feedback(
                    user_id=str(user_id),
                    problem_id=submission.problem_id,
                    is_correct=submission.is_correct,
                    solve_time_seconds=submission.time_spent or 0,
                    hints_used=submission.hints_used or 0,
                    xp_earned=xp_earned,
                    problem_info={
                        "title": submission.problem_name or "문제",
                        "difficulty": submission.difficulty or "medium",
                        "topics": submission.topics or [],
                    },
                    problem_type=submission.problem_type,
                )

                # FeedbackData 모델로 변환
                feedback_data = FeedbackData(
                    grade=feedback_result.get("grade", "learning"),
                    grade_emoji=feedback_result.get("grade_emoji", "🌱"),
                    grade_message=feedback_result.get("grade_message", ""),
                    summary_title=feedback_result.get("summary", {}).get("title", ""),
                    summary_highlight=feedback_result.get("summary", {}).get("highlight", ""),
                    efficiency_score=feedback_result.get("visualization", {}).get("efficiency_score", 0),
                    speed_score=feedback_result.get("visualization", {}).get("speed_score", 0),
                    understanding_score=feedback_result.get("visualization", {}).get("understanding_score", 0),
                    learning_points=feedback_result.get("learning_points", []),
                    improvements=feedback_result.get("improvements", []),
                    encouragement=feedback_result.get("encouragement", ""),
                )
                print(f"[RecordSolve] Generated feedback: grade={feedback_data.grade}")

                # ✅ attempts 테이블에 feedback_grade, feedback_data, score 업데이트
                if attempt_id_used:
                    try:
                        import json
                        # score 계산: 효율성/속도/이해도 평균
                        avg_score = (
                            feedback_data.efficiency_score +
                            feedback_data.speed_score +
                            feedback_data.understanding_score
                        ) // 3

                        feedback_data_json = {
                            "grade": feedback_data.grade,
                            "grade_emoji": feedback_data.grade_emoji,
                            "grade_message": feedback_data.grade_message,
                            "efficiency_score": feedback_data.efficiency_score,
                            "speed_score": feedback_data.speed_score,
                            "understanding_score": feedback_data.understanding_score,
                            "learning_points": feedback_data.learning_points,
                            "improvements": feedback_data.improvements,
                        }

                        db.table("attempts").update({
                            "feedback_grade": feedback_data.grade,
                            "feedback_data": feedback_data_json,
                            "score": avg_score,
                        }).eq("id", attempt_id_used).execute()
                        print(f"[RecordSolve] Updated attempt with feedback: grade={feedback_data.grade}, score={avg_score}")
                    except Exception as fb_update_err:
                        print(f"[RecordSolve] Failed to update attempt with feedback (non-blocking): {fb_update_err}")
            except Exception as fb_err:
                print(f"[RecordSolve] Feedback generation error (non-blocking): {fb_err}")

        message = "문제 풀이가 기록되었습니다!"
        if already_solved:
            message = f"이미 푼 문제입니다. (1/4 XP: +{xp_earned})"

        return RecordResponse(
            success=True,
            xp_earned=xp_earned,
            message=message,
            new_badges=new_badges,
            feedback=feedback_data,
        )

    except Exception as e:
        import traceback
        print(f"[RecordSolve] Error: {e}")
        traceback.print_exc()
        return RecordResponse(
            success=False,
            xp_earned=0,
            message=f"기록 실패: {str(e)}"
        )


@router.get("/hint/check", response_model=HintCheckResponse)
async def check_hint_availability(
    user_id: Optional[UUID] = Depends(get_user_id_from_token_optional),
    db=Depends(get_db)
):
    """
    Check if user can use a hint (has enough XP).

    레벨 1에서 XP가 5 미만이면 힌트 사용 불가.
    """
    hint_cost = XPConfig.HINT_COST

    if not user_id:
        return HintCheckResponse(
            can_use=False,
            current_xp=0,
            hint_cost=hint_cost,
            message="로그인이 필요합니다."
        )

    try:
        # Get current XP and level
        result = db.table("user_stats")\
            .select("total_xp, level")\
            .eq("user_id", str(user_id))\
            .single()\
            .execute()

        if not result.data:
            return HintCheckResponse(
                can_use=False,
                current_xp=0,
                hint_cost=hint_cost,
                message="사용자 정보를 찾을 수 없습니다."
            )

        current_xp = result.data.get("total_xp", 0)
        current_level = result.data.get("level", 1)

        # Level 1 with XP < hint_cost = can't use
        if current_level == 1 and current_xp < hint_cost:
            return HintCheckResponse(
                can_use=False,
                current_xp=current_xp,
                hint_cost=hint_cost,
                message=f"XP가 부족합니다. (현재: {current_xp}, 필요: {hint_cost})"
            )

        return HintCheckResponse(
            can_use=True,
            current_xp=current_xp,
            hint_cost=hint_cost,
            message="힌트를 사용할 수 있습니다."
        )

    except Exception as e:
        print(f"[HintCheck] Error: {e}")
        return HintCheckResponse(
            can_use=False,
            current_xp=0,
            hint_cost=hint_cost,
            message=f"오류: {str(e)}"
        )


@router.post("/hint/use", response_model=HintUseResponse)
async def use_hint(
    user_id: Optional[UUID] = Depends(get_user_id_from_token_optional),
    db=Depends(get_db)
):
    """
    Deduct XP for using a hint.

    힌트 사용 시 5 XP 차감. 레벨 1에서 XP가 부족하면 실패.
    """
    hint_cost = XPConfig.HINT_COST

    if not user_id:
        return HintUseResponse(
            success=False,
            xp_deducted=0,
            remaining_xp=0,
            message="로그인이 필요합니다."
        )

    try:
        # Call RPC to deduct XP
        result = db.rpc("deduct_hint_xp", {
            "p_user_id": str(user_id),
            "p_xp_cost": hint_cost
        }).execute()

        # Check if successful (RPC returns boolean)
        success = result.data if result.data is not None else False

        if not success:
            # Get current XP to show in message
            stats = db.table("user_stats")\
                .select("total_xp")\
                .eq("user_id", str(user_id))\
                .single()\
                .execute()
            current_xp = stats.data.get("total_xp", 0) if stats.data else 0

            return HintUseResponse(
                success=False,
                xp_deducted=0,
                remaining_xp=current_xp,
                message=f"XP가 부족합니다. (현재: {current_xp}, 필요: {hint_cost})"
            )

        # Get updated XP
        stats = db.table("user_stats")\
            .select("total_xp")\
            .eq("user_id", str(user_id))\
            .single()\
            .execute()
        remaining_xp = stats.data.get("total_xp", 0) if stats.data else 0

        return HintUseResponse(
            success=True,
            xp_deducted=hint_cost,
            remaining_xp=remaining_xp,
            message=f"힌트 사용! -{hint_cost} XP"
        )

    except Exception as e:
        print(f"[HintUse] Error: {e}")
        return HintUseResponse(
            success=False,
            xp_deducted=0,
            remaining_xp=0,
            message=f"오류: {str(e)}"
        )


# ============================================================
# Blank Hint - Masked/Reveal Toggle
# ============================================================

from pydantic import BaseModel
from typing import List


class BlankHintRequest(BaseModel):
    """빈칸 힌트 요청 (단순화: 역할 설명만)"""
    problem_id: str
    blank_index: int
    code_template: Optional[str] = None  # 코드 템플릿
    attempt_id: Optional[str] = None  # attempt 추적용


class BlankHintResponse(BaseModel):
    """빈칸 힌트 응답 (정답 없이 역할만)"""
    blank_index: int
    hint_content: str  # 역할/이유 설명 (1-2줄)
    from_cache: bool = False


@router.post("/hint/blank", response_model=BlankHintResponse)
async def get_blank_hint(
    request: BlankHintRequest,
    user_id: Optional[UUID] = Depends(get_user_id_from_token_optional),
    db=Depends(get_db)
):
    """
    빈칸 힌트 - 역할/이유 설명만 (정답 알려주지 않음)

    - 각 빈칸별로 1번만 힌트 요청 가능
    - 첫 요청 시 LLM 생성 후 캐시 저장
    - 이후 요청은 캐시에서 반환
    - attempt_id가 있으면 attempt_details에 기록
    """
    from ..services.hint_service import get_hint_service

    hint_service = get_hint_service()

    try:
        hint_result = await hint_service.generate_blank_hint(
            problem_id=request.problem_id,
            blank_index=request.blank_index,
            code_template=request.code_template,
        )

        hint_content = hint_result.get("hint_content", "힌트를 불러올 수 없습니다.")

        # attempt_details에 힌트 요청 기록 (hint_logs 통합)
        if request.attempt_id:
            record_attempt_detail(
                db=db,
                attempt_id=request.attempt_id,
                action_type=AttemptDetailAction.BLANK_HINT_REQUEST.value,
                blank_index=request.blank_index,
                blank_hint_content=hint_content[:500] if hint_content else None,
                hint_was_requested=True,
                xp_cost=5,  # hint_logs에서 통합
            )

            # attempts 테이블의 hints_used, total_hints_requested 증가
            if not request.attempt_id.startswith("temp_"):
                try:
                    db.rpc("increment_attempt_hints", {
                        "p_attempt_id": request.attempt_id
                    }).execute()
                except Exception as e:
                    print(f"[BlankHint] Failed to increment hints: {e}")

        return BlankHintResponse(
            blank_index=hint_result.get("blank_index", request.blank_index),
            hint_content=hint_content,
            from_cache=hint_result.get("from_cache", False),
        )

    except Exception as e:
        print(f"[BlankHint] Error: {e}")
        return BlankHintResponse(
            blank_index=request.blank_index,
            hint_content=f"힌트 생성 오류: {str(e)}",
            from_cache=False,
        )


# ============================================================
# Puzzle Hint - 블록별 역할 설명
# ============================================================

class PuzzleHintRequest(BaseModel):
    """퍼즐 힌트 요청"""
    problem_id: str
    block_index: int
    blocks: Optional[List[dict]] = None  # 블록 배열
    attempt_id: Optional[str] = None  # attempt 추적용


class PuzzleHintResponse(BaseModel):
    """퍼즐 힌트 응답"""
    block_index: int
    hint_content: str  # 블록 역할 설명
    from_cache: bool = False


@router.post("/hint/puzzle", response_model=PuzzleHintResponse)
async def get_puzzle_hint(
    request: PuzzleHintRequest,
    user_id: Optional[UUID] = Depends(get_user_id_from_token_optional),
    db=Depends(get_db)
):
    """
    퍼즐 힌트 - 블록의 역할 설명 (순서 알려주지 않음)

    - 각 블록이 무슨 역할을 하는지만 설명
    - 첫 요청 시 LLM 생성 후 캐시 저장
    - attempt_id가 있으면 attempt_details에 기록
    """
    from ..services.hint_service import get_hint_service

    hint_service = get_hint_service()

    try:
        hint_result = await hint_service.generate_puzzle_block_hint(
            problem_id=request.problem_id,
            block_index=request.block_index,
            blocks=request.blocks,
        )

        hint_content = hint_result.get("hint_content", "힌트를 불러올 수 없습니다.")

        # attempt_details에 힌트 요청 기록 (hint_logs 통합)
        if request.attempt_id:
            record_attempt_detail(
                db=db,
                attempt_id=request.attempt_id,
                action_type=AttemptDetailAction.PUZZLE_HINT_REQUEST.value,
                puzzle_hint_content=hint_content[:500] if hint_content else None,
                hint_was_requested=True,
                xp_cost=5,  # hint_logs에서 통합
            )

            # attempts 테이블의 hints_used, total_hints_requested 증가
            if not request.attempt_id.startswith("temp_"):
                try:
                    db.rpc("increment_attempt_hints", {
                        "p_attempt_id": request.attempt_id
                    }).execute()
                except Exception as e:
                    print(f"[PuzzleHint] Failed to increment hints: {e}")

        return PuzzleHintResponse(
            block_index=hint_result.get("hint_index", request.block_index),
            hint_content=hint_content,
            from_cache=hint_result.get("from_cache", False),
        )

    except Exception as e:
        print(f"[PuzzleHint] Error: {e}")
        return PuzzleHintResponse(
            block_index=request.block_index,
            hint_content=f"힌트 생성 오류: {str(e)}",
            from_cache=False,
        )


# ============================================================
# Guided Hint - 단계별 도움
# ============================================================

class GuidedHintRequest(BaseModel):
    """Guided 힌트 요청"""
    problem_id: str
    step_index: int
    steps: Optional[List[dict]] = None  # 단계 배열
    attempt_id: Optional[str] = None  # attempt 추적용


class GuidedHintResponse(BaseModel):
    """Guided 힌트 응답"""
    step_index: int
    hint_content: str  # 단계별 도움
    from_cache: bool = False


@router.post("/hint/guided", response_model=GuidedHintResponse)
async def get_guided_hint(
    request: GuidedHintRequest,
    user_id: Optional[UUID] = Depends(get_user_id_from_token_optional),
    db=Depends(get_db)
):
    """
    Guided 힌트 - 단계별 도움 (소크라테스식)

    - 현재 단계에서 무엇을 해야 하는지 힌트
    - 직접적인 정답 제공 안함
    - attempt_id가 있으면 attempt_details에 기록
    """
    from ..services.hint_service import get_hint_service

    hint_service = get_hint_service()

    try:
        hint_result = await hint_service.generate_guided_step_hint(
            problem_id=request.problem_id,
            step_index=request.step_index,
            steps=request.steps,
        )

        hint_content = hint_result.get("hint_content", "힌트를 불러올 수 없습니다.")

        # attempt_details에 힌트 요청 기록 (hint_logs 통합)
        if request.attempt_id:
            record_attempt_detail(
                db=db,
                attempt_id=request.attempt_id,
                action_type=AttemptDetailAction.GUIDED_MESSAGE.value,  # guided는 message로 기록
                guided_step=request.step_index,
                guided_tutor_response=hint_content[:1000] if hint_content else None,
                hint_was_requested=True,
                xp_cost=5,  # hint_logs에서 통합
            )

            # attempts 테이블의 hints_used, total_hints_requested 증가
            if not request.attempt_id.startswith("temp_"):
                try:
                    db.rpc("increment_attempt_hints", {
                        "p_attempt_id": request.attempt_id
                    }).execute()
                except Exception as e:
                    print(f"[GuidedHint] Failed to increment hints: {e}")

        return GuidedHintResponse(
            step_index=hint_result.get("hint_index", request.step_index),
            hint_content=hint_content,
            from_cache=hint_result.get("from_cache", False),
        )

    except Exception as e:
        print(f"[GuidedHint] Error: {e}")
        return GuidedHintResponse(
            step_index=request.step_index,
            hint_content=f"힌트 생성 오류: {str(e)}",
            from_cache=False,
        )


# ============================================================
# Session Tracking Endpoints
# ============================================================

@router.post("/session/heartbeat", response_model=SessionHeartbeatResponse)
async def session_heartbeat(
    request: SessionHeartbeatRequest,
    user_id: Optional[UUID] = Depends(get_user_id_from_token_optional),
):
    """
    세션 하트비트 - 세션 활성 상태 유지

    프론트엔드에서 30초마다 호출하여 세션이 활성 상태임을 알립니다.
    하트비트가 15분 이상 없으면 세션은 포기(abandoned)로 처리됩니다.

    Returns:
        success: 성공 여부
        session_status: active, expired, abandoned
        time_spent: 현재까지 풀이 시간(초)
    """
    from ..services.session_tracker import get_session_tracker

    if not user_id:
        return SessionHeartbeatResponse(
            success=False,
            session_status="unknown",
            error="로그인이 필요합니다."
        )

    try:
        tracker = get_session_tracker()
        result = await tracker.heartbeat(
            session_id=request.session_id,
            hints_used=request.hints_used,
            attempt_count=request.attempt_count,
        )

        return SessionHeartbeatResponse(
            success=result.get("success", False),
            session_status=result.get("session_status", "unknown"),
            time_spent=result.get("time_spent"),
            error=result.get("error"),
        )

    except Exception as e:
        print(f"[SessionHeartbeat] Error: {e}")
        return SessionHeartbeatResponse(
            success=False,
            session_status="error",
            error=str(e),
        )


@router.post("/session/end", response_model=SessionEndResponse)
async def session_end(
    request: SessionEndRequest,
    user_id: Optional[UUID] = Depends(get_user_id_from_token_optional),
):
    """
    세션 종료 - 완료/스킵/포기

    문제 풀이 종료 시 호출합니다.
    - complete: 정답 제출 완료 (user_memories는 record_solve에서 저장)
    - skip: 사용자가 문제 건너뛰기 → user_memories 저장
    - abandon: 페이지 이탈/세션 종료 → user_memories 저장

    Returns:
        세션 종료 결과 (풀이 시간, 힌트 사용량 등)
    """
    from ..services.session_tracker import get_session_tracker
    from ..services.memory_service import get_memory_service

    if not user_id:
        return SessionEndResponse(
            success=False,
            session_id=request.session_id,
            status="error",
            time_spent=0,
            error="로그인이 필요합니다."
        )

    try:
        tracker = get_session_tracker()
        memory_service = get_memory_service()

        # 🔑 세션 정보 미리 가져오기 (skip/abandon 시 메모리 저장용)
        session = tracker.get_session(request.session_id)
        session_metadata = session.metadata if session else {}

        if request.end_type == "complete":
            # complete는 record_solve에서 user_memories를 저장하므로 여기서는 tracker만 처리
            result = await tracker.complete_session(
                session_id=request.session_id,
                is_correct=request.is_correct or True,
                score=request.score or 0,
            )
        elif request.end_type == "skip":
            result = await tracker.skip_session(
                session_id=request.session_id,
                reason=request.reason,
            )
            # 🧠 skip 시에도 user_memories 저장 (어려워하는 주제 추적)
            if session:
                try:
                    await memory_service.create_problem_session_memory(
                        user_id=str(user_id),
                        session_id=request.session_id,
                        problem_id=session.problem_id,
                        problem_name=session_metadata.get("problem_name", "Unknown"),
                        problem_type=session.problem_type,
                        difficulty=session_metadata.get("difficulty", "medium"),
                        topics=session_metadata.get("topics", []),
                        was_successful=False,  # skip = 미완료
                        hints_used=session.hints_used,
                        time_spent=result.get("time_spent", 0),
                        attempt_count=session.attempt_count,
                    )
                    print(f"[SessionEnd] Created memory for skipped session: {request.session_id}")
                except Exception as mem_err:
                    print(f"[SessionEnd] Memory creation error (non-blocking): {mem_err}")

        elif request.end_type == "abandon":
            result = await tracker.abandon_session(
                session_id=request.session_id,
                reason=request.reason or "user_left",
            )
            # 🧠 abandon 시에도 user_memories 저장 (어려워하는 주제 추적)
            if session:
                try:
                    await memory_service.create_problem_session_memory(
                        user_id=str(user_id),
                        session_id=request.session_id,
                        problem_id=session.problem_id,
                        problem_name=session_metadata.get("problem_name", "Unknown"),
                        problem_type=session.problem_type,
                        difficulty=session_metadata.get("difficulty", "medium"),
                        topics=session_metadata.get("topics", []),
                        was_successful=False,  # abandon = 미완료
                        hints_used=session.hints_used,
                        time_spent=result.get("time_spent", 0),
                        attempt_count=session.attempt_count,
                    )
                    print(f"[SessionEnd] Created memory for abandoned session: {request.session_id}")
                except Exception as mem_err:
                    print(f"[SessionEnd] Memory creation error (non-blocking): {mem_err}")
        else:
            return SessionEndResponse(
                success=False,
                session_id=request.session_id,
                status="error",
                time_spent=0,
                error=f"Unknown end_type: {request.end_type}"
            )

        return SessionEndResponse(
            success=result.get("success", False),
            session_id=request.session_id,
            status=result.get("status", "unknown"),
            time_spent=result.get("time_spent", 0),
            hints_used=result.get("hints_used", 0),
            attempt_count=result.get("attempt_count", 0),
            error=result.get("error"),
        )

    except Exception as e:
        print(f"[SessionEnd] Error: {e}")
        return SessionEndResponse(
            success=False,
            session_id=request.session_id,
            status="error",
            time_spent=0,
            error=str(e),
        )


@router.get("/session/stats")
async def get_session_stats(
    user_id: Optional[UUID] = Depends(get_user_id_from_token_optional),
    days: int = 30,
):
    """
    세션 통계 조회

    포기율, 완료율 등 세션 관련 통계를 조회합니다.

    Args:
        days: 조회 기간 (기본 30일)

    Returns:
        complete, skip, abandon 비율 및 상세 통계
    """
    from ..services.session_tracker import get_session_tracker

    if not user_id:
        return {"error": "로그인이 필요합니다."}

    try:
        tracker = get_session_tracker()
        stats = await tracker.get_abandonment_stats(
            user_id=str(user_id),
            days=days,
        )
        return stats

    except Exception as e:
        print(f"[SessionStats] Error: {e}")
        return {"error": str(e)}


# ============================================================
# Debug Endpoints (개발용)
# ============================================================

@router.get("/debug/recent-data")
async def debug_recent_data(
    user_id: Optional[UUID] = Depends(get_user_id_from_token_optional),
    db=Depends(get_db),
    limit: int = 5,
):
    """
    디버깅용: 최근 attempts, user_memories 데이터 확인

    DB에 데이터가 올바르게 저장되고 있는지 확인하는 엔드포인트입니다.
    - attempts: base_problem_id, problem_id 확인
    - user_memories: attempt_id 확인
    """
    if not user_id:
        return {"error": "로그인이 필요합니다."}

    try:
        # 최근 attempts 조회
        attempts_result = db.table("attempts")\
            .select("id, user_id, base_problem_id, problem_id, problem_name, is_correct, xp_earned, created_at")\
            .eq("user_id", str(user_id))\
            .order("created_at", desc=True)\
            .limit(limit)\
            .execute()

        # 최근 user_memories 조회
        memories_result = db.table("user_memories")\
            .select("id, user_id, problem_name, attempt_id, was_successful, created_at")\
            .eq("user_id", str(user_id))\
            .order("created_at", desc=True)\
            .limit(limit)\
            .execute()

        return {
            "user_id": str(user_id),
            "recent_attempts": attempts_result.data or [],
            "recent_memories": memories_result.data or [],
            "summary": {
                "attempts_count": len(attempts_result.data) if attempts_result.data else 0,
                "attempts_with_base_problem_id": sum(
                    1 for a in (attempts_result.data or []) if a.get("base_problem_id")
                ),
                "memories_count": len(memories_result.data) if memories_result.data else 0,
                "memories_with_attempt_id": sum(
                    1 for m in (memories_result.data or []) if m.get("attempt_id")
                ),
            }
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}


@router.get("/debug/resolve-problem/{problem_id}")
async def debug_resolve_problem(
    problem_id: str,
    db=Depends(get_db),
):
    """
    디버깅용: problem_id가 base_problems.id로 올바르게 변환되는지 확인

    Args:
        problem_id: 테스트할 문제 ID (UUID 또는 original_id 형식)

    Returns:
        resolve 결과와 base_problems 정보
    """
    try:
        resolved_id = await resolve_base_problem_id(db, problem_id)

        result = {
            "input_problem_id": problem_id,
            "resolved_base_problem_id": resolved_id,
        }

        if resolved_id:
            # base_problems에서 상세 정보 조회
            bp_result = db.table("base_problems")\
                .select("id, original_id, name, difficulty, source")\
                .eq("id", resolved_id)\
                .limit(1)\
                .execute()

            if bp_result.data:
                result["base_problem_info"] = bp_result.data[0]
            else:
                result["base_problem_info"] = None
        else:
            result["error"] = "Could not resolve to base_problems.id"

        return result

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e), "input_problem_id": problem_id}
