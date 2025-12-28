from fastapi import APIRouter, HTTPException, Depends, status
from typing import Optional
from uuid import UUID
from datetime import datetime

from ..database import get_db
from ..dependencies import get_current_user_id as get_user_id_from_token  # 공통 인증 의존성
from ..models.practice import (
    BlankSubmission,
    PuzzleSubmission,
    SubmissionResponse,
    SubmissionResult,
    CodeExecutionRequest,
    CodeExecutionResponse,
    XPConfig,
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
