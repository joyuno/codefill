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
    NewBadge,
)
from ..models.problem import ProblemType
from ..services.badge_service import get_badge_service

router = APIRouter()


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


def get_next_attempt_number(db, user_id: str, problem_id: str) -> int:
    """
    동일 문제에 대한 다음 시도 번호 계산.
    첫 시도면 1, 이후 2, 3, ... 반환.
    """
    try:
        result = db.table("attempts")\
            .select("attempt_number")\
            .eq("user_id", user_id)\
            .eq("problem_id", problem_id)\
            .order("attempt_number", desc=True)\
            .limit(1)\
            .execute()

        if result.data and len(result.data) > 0:
            return (result.data[0].get("attempt_number") or 0) + 1
        return 1
    except Exception:
        return 1


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
    문제 풀이 시작 - pending attempt 생성

    문제 풀이를 시작할 때 호출하여 attempt_id를 발급받습니다.
    이 attempt_id로 힌트 요청, 제출 등의 상세 기록을 추적합니다.

    Returns:
        attempt_id: 시도 ID (UUID)
        started_at: 시작 시간
    """
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

        # 기본 attempt 데이터 (pending 상태)
        attempt_data = {
            "user_id": str(user_id),
            "is_correct": None,  # pending 상태
            "xp_earned": 0,
            "problem_type": request.problem_type,
            "difficulty": request.difficulty,
            "problem_name": request.problem_name,
            "topics": request.topics,
            "hints_used": 0,
            "total_hints_requested": 0,
        }

        # problem_id가 UUID 형식이면 추가 + attempt_number 계산
        try:
            problem_uuid = UUIDType(request.problem_id)
            attempt_data["problem_id"] = str(problem_uuid)
            # 동일 문제 시도 번호 계산
            attempt_data["attempt_number"] = get_next_attempt_number(
                db, str(user_id), str(problem_uuid)
            )
        except ValueError:
            attempt_data["attempt_number"] = 1  # UUID 아니면 첫 시도로 간주

        # attempts 테이블에 pending 레코드 생성
        result = db.table("attempts").insert(attempt_data).execute()

        if result.data and len(result.data) > 0:
            attempt_id = result.data[0]["id"]
            started_at = result.data[0].get("created_at", datetime.utcnow().isoformat())
            print(f"[StartPractice] Created pending attempt: {attempt_id}")

            return StartPracticeResponse(
                attempt_id=str(attempt_id),
                started_at=started_at,
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
            "step_number": step_number,
        }

        # 추가 필드 (None이 아닌 것만)
        for key, value in kwargs.items():
            if value is not None:
                detail_data[key] = value

        db.table("attempt_details").insert(detail_data).execute()
        print(f"[AttemptDetail] Recorded: attempt={attempt_id[:8]}..., action={action_type}")
        return True

    except Exception as e:
        print(f"[AttemptDetail] Error recording: {e}")
        return False


@router.post("/submit/blank", response_model=SubmissionResponse)
async def submit_blank(
    submission: BlankSubmission,
    user_id: UUID = Depends(get_user_id_from_token),
    db=Depends(get_db)
):
    """Submit answer for blank-fill problem."""
    try:
        # Get problem and correct answers
        result = db.table("problems")\
            .select("answer_data, difficulty")\
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

        # Check answers
        is_correct, blank_results = check_blank_answers(submission.answers, correct_blanks)

        # Calculate XP
        xp_earned = XPConfig.BLANK_CORRECT if is_correct else 0

        # Save attempt with attempt_number
        attempt_number = get_next_attempt_number(db, str(user_id), str(submission.problem_id))
        db.table("attempts").insert({
            "user_id": str(user_id),
            "problem_id": str(submission.problem_id),
            "is_correct": is_correct,
            "submitted_answer": str(submission.answers),
            "xp_earned": xp_earned,
            "attempt_number": attempt_number,
        }).execute()

        # Update user stats and check badges if correct
        new_badges = None
        if is_correct:
            db.rpc("increment_user_stats", {
                "p_user_id": str(user_id),
                "p_xp": xp_earned,
                "p_problem_type": "blank",
                "p_difficulty": difficulty,
            }).execute()

            # Check and award badges
            badge_service = get_badge_service()
            awarded = await badge_service.check_and_award_badges(
                user_id=str(user_id),
                trigger_type='solve',
                problem_type='blank',
                difficulty=difficulty,
            )
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
        # Get problem and correct answer data
        result = db.table("problems")\
            .select("answer_data, difficulty")\
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

        # Check block order and indentation
        puzzle_results = {}
        all_correct = True

        submitted_ids = [b.id for b in submission.block_order]

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

        # Also check if all required blocks are present
        if len(submission.block_order) != len(correct_order):
            all_correct = False

        # Calculate XP
        xp_earned = XPConfig.PUZZLE_CORRECT if all_correct else 0

        # Save attempt with attempt_number
        attempt_number = get_next_attempt_number(db, str(user_id), str(submission.problem_id))
        db.table("attempts").insert({
            "user_id": str(user_id),
            "problem_id": str(submission.problem_id),
            "is_correct": all_correct,
            "submitted_answer": str([{"id": b.id, "indent": b.indentation} for b in submission.block_order]),
            "xp_earned": xp_earned,
            "attempt_number": attempt_number,
        }).execute()

        # Update user stats and check badges if correct
        new_badges = None
        if all_correct:
            db.rpc("increment_user_stats", {
                "p_user_id": str(user_id),
                "p_xp": xp_earned,
                "p_problem_type": "puzzle",
                "p_difficulty": difficulty,
            }).execute()

            # Check and award badges
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

        # 이미 푼 문제인지 확인 (problem_id로 검색)
        already_solved = False
        xp_earned = base_xp

        try:
            # daily_activity에서 오늘 이미 이 문제를 풀었는지 확인할 수는 없음
            # 대신 간단히 problem_id를 키로 user_solved_problems 확인
            # 또는 attempts 테이블에서 확인 (UUID 형식인 경우에만)
            from uuid import UUID as UUIDType
            try:
                problem_uuid = UUIDType(submission.problem_id)
                # UUID 형식이면 attempts 테이블에서 확인
                prev_attempt = db.table("attempts")\
                    .select("id")\
                    .eq("user_id", str(user_id))\
                    .eq("problem_id", str(problem_uuid))\
                    .eq("is_correct", True)\
                    .limit(1)\
                    .execute()

                if prev_attempt.data and len(prev_attempt.data) > 0:
                    already_solved = True
                    xp_earned = base_xp // 4  # 1/4 XP
                    print(f"[RecordSolve] Already solved problem, reducing XP: {base_xp} -> {xp_earned}")
            except ValueError:
                # UUID 형식이 아님 (예: "taco_100")
                # 이 경우 별도의 테이블에서 확인하거나 건너뜀
                pass
        except Exception as check_err:
            print(f"[RecordSolve] Error checking previous solve: {check_err}")

        # attempts 테이블에 기록 시도
        attempt_id_used = None
        try:
            from uuid import UUID as UUIDType

            # base_problem_id 결정 (잔디 클릭 시 문제 정보 표시용)
            base_problem_id = None

            # 1. 직접 전달된 base_problem_id 사용
            if submission.base_problem_id:
                try:
                    base_uuid = UUIDType(submission.base_problem_id)
                    base_problem_id = str(base_uuid)
                except ValueError:
                    # UUID가 아니면 original_id로 간주하고 조회
                    try:
                        bp_result = db.table("base_problems")\
                            .select("id")\
                            .eq("original_id", submission.base_problem_id)\
                            .limit(1)\
                            .execute()
                        if bp_result.data and len(bp_result.data) > 0:
                            base_problem_id = bp_result.data[0]["id"]
                            print(f"[RecordSolve] Found base_problem_id from original_id: {submission.base_problem_id} -> {base_problem_id}")
                    except Exception as e:
                        print(f"[RecordSolve] Failed to lookup base_problem by original_id: {e}")

            # 2. problem_id로 base_problems 테이블에서 직접 조회 시도
            if not base_problem_id:
                try:
                    problem_uuid = UUIDType(submission.problem_id)
                    bp_result = db.table("base_problems")\
                        .select("id")\
                        .eq("id", str(problem_uuid))\
                        .limit(1)\
                        .execute()
                    if bp_result.data and len(bp_result.data) > 0:
                        base_problem_id = bp_result.data[0]["id"]
                        print(f"[RecordSolve] problem_id is base_problem: {base_problem_id}")
                except Exception:
                    pass  # 조회 실패 시 무시

            # attempt_id가 있으면 기존 attempt 업데이트, 없으면 새로 생성
            if submission.attempt_id and not submission.attempt_id.startswith("temp_"):
                # 기존 pending attempt 업데이트 (complete_attempt RPC 사용)
                try:
                    db.rpc("complete_attempt", {
                        "p_attempt_id": submission.attempt_id,
                        "p_is_correct": submission.is_correct,
                        "p_xp_earned": xp_earned,
                        "p_submitted_answer": f"type:{submission.problem_type}",
                    }).execute()
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
                }

                # problem_id가 UUID 형식이면 추가 + attempt_number 계산
                try:
                    problem_uuid = UUIDType(submission.problem_id)
                    attempt_data["problem_id"] = str(problem_uuid)
                    # 동일 문제 시도 번호 계산
                    attempt_data["attempt_number"] = get_next_attempt_number(
                        db, str(user_id), str(problem_uuid)
                    )
                except ValueError:
                    attempt_data["attempt_number"] = 1  # UUID 아니면 첫 시도로 간주

                if base_problem_id:
                    attempt_data["base_problem_id"] = base_problem_id

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

                detail_data = {
                    "attempt_id": str(attempt_id_used),
                    "action_type": action_type,
                }

                # 문제 유형별 추가 데이터
                if submission.problem_type == "blank":
                    detail_data["blank_is_correct"] = submission.is_correct
                elif submission.problem_type == "puzzle":
                    # puzzle 결과는 별도 puzzle_results 필드가 없으므로 is_correct만
                    pass
                elif submission.problem_type == "guided":
                    detail_data["guided_step"] = 0  # 최종 제출

                try:
                    db.table("attempt_details").insert(detail_data).execute()
                    print(f"[RecordSolve] Recorded attempt_detail: {action_type}")
                except Exception as detail_err:
                    print(f"[RecordSolve] Failed to record attempt_detail: {detail_err}")

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
                }).execute()
                print(f"[RecordSolve] Updated user stats: +{xp_earned} XP, type={submission.problem_type}")

                # Check and award badges
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

            except Exception as rpc_err:
                print(f"[RecordSolve] RPC error: {rpc_err}")
                return RecordResponse(
                    success=False,
                    xp_earned=0,
                    message=f"XP 업데이트 실패: {str(rpc_err)}"
                )

        message = "문제 풀이가 기록되었습니다!"
        if already_solved:
            message = f"이미 푼 문제입니다. (1/4 XP: +{xp_earned})"

        return RecordResponse(
            success=True,
            xp_earned=xp_earned,
            message=message,
            new_badges=new_badges,
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

        # attempt_details에 힌트 요청 기록
        if request.attempt_id:
            record_attempt_detail(
                db=db,
                attempt_id=request.attempt_id,
                action_type=AttemptDetailAction.BLANK_HINT_REQUEST.value,
                blank_index=request.blank_index,
                blank_hint_content=hint_content[:500] if hint_content else None,
                hint_was_requested=True,
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

        # attempt_details에 힌트 요청 기록
        if request.attempt_id:
            record_attempt_detail(
                db=db,
                attempt_id=request.attempt_id,
                action_type=AttemptDetailAction.PUZZLE_HINT_REQUEST.value,
                puzzle_hint_content=hint_content[:500] if hint_content else None,
                hint_was_requested=True,
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

        # attempt_details에 힌트 요청 기록
        if request.attempt_id:
            record_attempt_detail(
                db=db,
                attempt_id=request.attempt_id,
                action_type=AttemptDetailAction.GUIDED_MESSAGE.value,  # guided는 message로 기록
                guided_step=request.step_index,
                guided_tutor_response=hint_content[:1000] if hint_content else None,
                hint_was_requested=True,
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
