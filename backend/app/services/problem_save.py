"""
Problem Save Service
생성된 문제(blank, puzzle, guided)를 DB에 저장하는 서비스

Tables:
- problems_blank: 빈칸 채우기 문제
- problems_puzzle: 퍼즐 문제 (Parsons)
- problems_guided: 1대1 대화형 문제

Key Columns:
- base_problem_id: base_problems 테이블의 UUID (FK)
- creator_id: 문제를 푼 사용자의 UUID
- language: 프로그래밍 언어

Logic:
- 조회: base_problem_id + language로 기존 문제 확인
- 캐시 히트: 기존 문제 복사 + creator_id만 변경
- 캐시 미스: LLM 생성 후 저장
"""

from typing import Dict, Any, Optional
import logging
from ..database import get_supabase_client

logger = logging.getLogger(__name__)


class ProblemSaveService:
    """생성된 문제를 DB에 저장하고 조회하는 서비스"""

    def __init__(self):
        self.supabase = get_supabase_client()

    # ============================================================
    # base_problem_id 조회 헬퍼
    # ============================================================

    def get_base_problem_id(self, original_id: str) -> Optional[str]:
        """
        original_id로 base_problems 테이블에서 UUID(id) 조회

        Args:
            original_id: 원본 문제 ID (예: "baekjoon_1001", "taco_123")

        Returns:
            base_problems.id (UUID) 또는 None
        """
        try:
            result = self.supabase.table("base_problems") \
                .select("id") \
                .eq("original_id", original_id) \
                .limit(1) \
                .execute()

            if result.data and len(result.data) > 0:
                return result.data[0]["id"]
            return None

        except Exception as e:
            logger.error(f"[ProblemSave] Failed to get base_problem_id: {e}")
            return None

    # ============================================================
    # 조회 메서드 (Cache-First 로직용)
    # base_problem_id + language로 조회 (creator_id 무관)
    # ============================================================

    def find_existing_problem(
        self,
        problem_type: str,
        base_problem_id: str,
        language: str,
    ) -> Optional[Dict[str, Any]]:
        """
        기존 문제 조회 (다른 유저가 만든 것도 포함)

        Args:
            problem_type: 문제 유형 (blank, puzzle, guided)
            base_problem_id: base_problems 테이블의 UUID
            language: 프로그래밍 언어

        Returns:
            문제 데이터 또는 None
        """
        table_name = f"problems_{problem_type}"

        try:
            result = self.supabase.table(table_name) \
                .select("*") \
                .eq("base_problem_id", base_problem_id) \
                .eq("language", language) \
                .limit(1) \
                .execute()

            if result.data and len(result.data) > 0:
                logger.info(f"[ProblemCache] {problem_type} problem found: {base_problem_id} ({language})")
                return result.data[0]
            return None

        except Exception as e:
            logger.error(f"[ProblemCache] Failed to find {problem_type} problem: {e}")
            return None

    def check_user_has_problem(
        self,
        problem_type: str,
        base_problem_id: str,
        language: str,
        creator_id: str,
    ) -> Optional[Dict[str, Any]]:
        """
        특정 유저가 이미 해당 문제를 가지고 있는지 확인

        Args:
            problem_type: 문제 유형 (blank, puzzle, guided)
            base_problem_id: base_problems 테이블의 UUID
            language: 프로그래밍 언어
            creator_id: 사용자 UUID

        Returns:
            문제 데이터 또는 None
        """
        table_name = f"problems_{problem_type}"

        try:
            result = self.supabase.table(table_name) \
                .select("*") \
                .eq("base_problem_id", base_problem_id) \
                .eq("language", language) \
                .eq("creator_id", creator_id) \
                .limit(1) \
                .execute()

            if result.data and len(result.data) > 0:
                logger.info(f"[ProblemCache] User already has {problem_type}: {base_problem_id}")
                return result.data[0]
            return None

        except Exception as e:
            logger.error(f"[ProblemCache] Failed to check user problem: {e}")
            return None

    # ============================================================
    # 복사 메서드 (캐시 히트 시 사용)
    # ============================================================

    async def copy_problem_for_user(
        self,
        problem_type: str,
        source_problem: Dict[str, Any],
        creator_id: str,
    ) -> Dict[str, Any]:
        """
        기존 문제를 복사하고 creator_id만 변경하여 새 레코드 생성

        Args:
            problem_type: 문제 유형 (blank, puzzle, guided)
            source_problem: 복사할 원본 문제 데이터
            creator_id: 새로운 사용자 UUID

        Returns:
            저장 결과
        """
        table_name = f"problems_{problem_type}"

        try:
            # 복사할 데이터 준비 (id, created_at, updated_at 제외)
            copy_data = {
                "base_problem_id": source_problem.get("base_problem_id"),
                "original_id": source_problem.get("original_id"),
                "language": source_problem.get("language"),
                "creator_id": creator_id,  # 새 사용자로 변경
            }

            # 유형별 필드 복사
            if problem_type == "blank":
                copy_data["code_template"] = source_problem.get("code_template")
                copy_data["answers"] = source_problem.get("answers")

            elif problem_type == "puzzle":
                copy_data["fixed_start"] = source_problem.get("fixed_start")
                copy_data["fixed_end"] = source_problem.get("fixed_end")
                copy_data["blocks"] = source_problem.get("blocks")

            elif problem_type == "guided":
                copy_data["concepts"] = source_problem.get("concepts")
                copy_data["flow"] = source_problem.get("flow")
                copy_data["checkpoints"] = source_problem.get("checkpoints")

            # 새 레코드 삽입
            result = self.supabase.table(table_name).insert(copy_data).execute()

            logger.info(f"[ProblemSave] Copied {problem_type} for user {creator_id[:8]}...")
            return {"success": True, "data": result.data[0] if result.data else None}

        except Exception as e:
            logger.error(f"[ProblemSave] Failed to copy {problem_type}: {e}")
            return {"success": False, "error": str(e)}

    # ============================================================
    # 저장 메서드 (LLM 생성 후 사용)
    # ============================================================

    async def save_blank_problem(
        self,
        base_problem_id: str,
        original_id: str,
        language: str,
        code_template: str,
        answers: list,
        creator_id: str,
    ) -> Dict[str, Any]:
        """빈칸 채우기 문제 저장"""
        try:
            data = {
                "base_problem_id": base_problem_id,
                "original_id": original_id,
                "language": language,
                "code_template": code_template,
                "answers": answers,
                "creator_id": creator_id,
            }

            result = self.supabase.table("problems_blank").insert(data).execute()

            logger.info(f"[ProblemSave] Blank problem saved: {original_id} (user: {creator_id[:8]}...)")
            return {"success": True, "data": result.data[0] if result.data else None}

        except Exception as e:
            logger.error(f"[ProblemSave] Failed to save blank problem: {e}")
            return {"success": False, "error": str(e)}

    async def save_puzzle_problem(
        self,
        base_problem_id: str,
        original_id: str,
        language: str,
        blocks: list,
        creator_id: str,
        fixed_start: Optional[str] = None,
        fixed_end: Optional[str] = None,
    ) -> Dict[str, Any]:
        """퍼즐 문제 저장"""
        try:
            data = {
                "base_problem_id": base_problem_id,
                "original_id": original_id,
                "language": language,
                "blocks": blocks,
                "creator_id": creator_id,
            }

            if fixed_start:
                data["fixed_start"] = fixed_start
            if fixed_end:
                data["fixed_end"] = fixed_end

            result = self.supabase.table("problems_puzzle").insert(data).execute()

            logger.info(f"[ProblemSave] Puzzle problem saved: {original_id} (user: {creator_id[:8]}...)")
            return {"success": True, "data": result.data[0] if result.data else None}

        except Exception as e:
            logger.error(f"[ProblemSave] Failed to save puzzle problem: {e}")
            return {"success": False, "error": str(e)}

    async def save_guided_problem(
        self,
        base_problem_id: str,
        original_id: str,
        language: str,
        concepts: list,
        flow: list,
        checkpoints: list,
        creator_id: str,
    ) -> Dict[str, Any]:
        """1대1 대화형 문제 저장"""
        try:
            data = {
                "base_problem_id": base_problem_id,
                "original_id": original_id,
                "language": language,
                "concepts": concepts,
                "flow": flow,
                "checkpoints": checkpoints,
                "creator_id": creator_id,
            }

            result = self.supabase.table("problems_guided").insert(data).execute()

            logger.info(f"[ProblemSave] Guided problem saved: {original_id} (user: {creator_id[:8]}...)")
            return {"success": True, "data": result.data[0] if result.data else None}

        except Exception as e:
            logger.error(f"[ProblemSave] Failed to save guided problem: {e}")
            return {"success": False, "error": str(e)}

    async def save_generated_problem(
        self,
        problem_type: str,
        generated_data: Dict[str, Any],
        base_problem_id: str,
        creator_id: str,
    ) -> Dict[str, Any]:
        """
        LLM이 생성한 문제를 저장

        Args:
            problem_type: 문제 유형 (blank, puzzle, guided)
            generated_data: LLM이 생성한 데이터
            base_problem_id: base_problems 테이블의 UUID
            creator_id: 사용자 UUID

        Returns:
            저장 결과
        """
        original_id = generated_data.get("original_id", "unknown")
        language = generated_data.get("language", "python")

        if problem_type == "blank":
            return await self.save_blank_problem(
                base_problem_id=base_problem_id,
                original_id=original_id,
                language=language,
                code_template=generated_data.get("code_template", ""),
                answers=generated_data.get("answers", []),
                creator_id=creator_id,
            )

        elif problem_type == "puzzle":
            return await self.save_puzzle_problem(
                base_problem_id=base_problem_id,
                original_id=original_id,
                language=language,
                blocks=generated_data.get("blocks", []),
                creator_id=creator_id,
                fixed_start=generated_data.get("fixed_start"),
                fixed_end=generated_data.get("fixed_end"),
            )

        elif problem_type == "guided":
            return await self.save_guided_problem(
                base_problem_id=base_problem_id,
                original_id=original_id,
                language=language,
                concepts=generated_data.get("concepts", []),
                flow=generated_data.get("flow", []),
                checkpoints=generated_data.get("checkpoints", []),
                creator_id=creator_id,
            )

        else:
            return {"success": False, "error": f"Unknown problem type: {problem_type}"}


# Singleton instance
_problem_save_service = None


def get_problem_save_service() -> ProblemSaveService:
    """ProblemSaveService 싱글톤 반환"""
    global _problem_save_service
    if _problem_save_service is None:
        _problem_save_service = ProblemSaveService()
    return _problem_save_service
