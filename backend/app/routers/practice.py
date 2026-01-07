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
)
from ..models.problem import ProblemType

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

        # Check answers
        is_correct, blank_results = check_blank_answers(submission.answers, correct_blanks)

        # Calculate XP
        xp_earned = XPConfig.BLANK_CORRECT if is_correct else 0

        # Save attempt
        db.table("attempts").insert({
            "user_id": str(user_id),
            "problem_id": str(submission.problem_id),
            "is_correct": is_correct,
            "submitted_answer": str(submission.answers),
            "xp_earned": xp_earned,
        }).execute()

        # Update user stats if correct
        if is_correct:
            db.rpc("increment_user_stats", {
                "p_user_id": str(user_id),
                "p_xp": xp_earned,
                "p_problem_type": "blank"
            }).execute()

        return SubmissionResponse(
            result=SubmissionResult.CORRECT if is_correct else SubmissionResult.INCORRECT,
            is_correct=is_correct,
            xp_earned=xp_earned,
            blank_results=blank_results,
            feedback="정답입니다!" if is_correct else "틀린 빈칸이 있습니다. 다시 확인해보세요.",
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

        # Save attempt
        db.table("attempts").insert({
            "user_id": str(user_id),
            "problem_id": str(submission.problem_id),
            "is_correct": all_correct,
            "submitted_answer": str([{"id": b.id, "indent": b.indentation} for b in submission.block_order]),
            "xp_earned": xp_earned,
        }).execute()

        # Update user stats if correct
        if all_correct:
            db.rpc("increment_user_stats", {
                "p_user_id": str(user_id),
                "p_xp": xp_earned,
                "p_problem_type": "puzzle"
            }).execute()

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

        # attempts 테이블에 기록 시도 (UUID 형식인 경우에만)
        try:
            from uuid import UUID as UUIDType
            problem_uuid = UUIDType(submission.problem_id)
            db.table("attempts").insert({
                "user_id": str(user_id),
                "problem_id": str(problem_uuid),
                "is_correct": submission.is_correct,
                "xp_earned": xp_earned,
                "submitted_answer": f"type:{submission.problem_type}",
            }).execute()
        except ValueError:
            # UUID 형식이 아니면 attempts 테이블 건너뜀
            print(f"[RecordSolve] Problem ID is not UUID, skipping attempts table: {submission.problem_id}")
        except Exception as insert_err:
            # FK 제약 등으로 실패해도 XP 기록은 계속
            print(f"[RecordSolve] Attempts insert failed (non-blocking): {insert_err}")

        # 정답인 경우 user stats 업데이트 (XP, 잔디) - 이건 항상 시도
        if submission.is_correct and xp_earned > 0:
            try:
                db.rpc("increment_user_stats", {
                    "p_user_id": str(user_id),
                    "p_xp": xp_earned,
                    "p_problem_type": submission.problem_type
                }).execute()
                print(f"[RecordSolve] Updated user stats: +{xp_earned} XP, type={submission.problem_type}")
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
            message=message
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
