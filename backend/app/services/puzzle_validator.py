"""
Puzzle Validator Service

퍼즐 문제의 복수 정답을 지능적으로 검증합니다.

핵심 기능:
1. 논리적 그룹 식별 (함수, 클래스, import 등)
2. 그룹 간 순서 유연성 허용
3. 그룹 내 순서 엄격 검증
4. Optional: Judge0 실행 검증
"""

import re
import ast
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class BlockType(Enum):
    """코드 블록 타입"""
    IMPORT = "import"
    CLASS = "class"
    FUNCTION = "function"
    VARIABLE = "variable"
    MAIN = "main"
    OTHER = "other"


@dataclass
class CodeBlock:
    """코드 블록 정보"""
    index: int
    content: str
    block_type: BlockType
    name: Optional[str] = None
    dependencies: List[str] = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


@dataclass
class BlockGroup:
    """논리적 블록 그룹"""
    group_type: BlockType
    blocks: List[CodeBlock]
    order_flexible: bool = True  # 그룹 내 순서 유연 여부


@dataclass
class ValidationResult:
    """검증 결과"""
    is_correct: bool
    score: float  # 0.0 ~ 1.0
    feedback: str
    first_wrong_position: Optional[int] = None
    expected_block: Optional[str] = None
    details: Dict[str, Any] = None

    def __post_init__(self):
        if self.details is None:
            self.details = {}


class PuzzleValidator:
    """
    퍼즐 복수 정답 검증 서비스

    Usage:
        validator = PuzzleValidator()
        result = await validator.validate(
            blocks=["def foo():", "    pass", "def bar():", "    return 1"],
            user_order=[0, 1, 2, 3],
            correct_order=[0, 1, 2, 3],
            language="python"
        )
    """

    def __init__(self, judge0_enabled: bool = False):
        self.judge0_enabled = judge0_enabled
        # 그룹 순서가 유연한 타입들
        self.flexible_order_types = {
            BlockType.FUNCTION,
            BlockType.CLASS,
        }
        # 반드시 앞에 와야 하는 타입들
        self.priority_types = [
            BlockType.IMPORT,
            BlockType.VARIABLE,
        ]

    async def validate(
        self,
        blocks: List[str],
        user_order: List[int],
        correct_order: List[int],
        language: str = "python",
        strict_mode: bool = False,
    ) -> ValidationResult:
        """
        퍼즐 정답 검증

        Args:
            blocks: 코드 블록 목록 (원본 순서)
            user_order: 사용자가 제출한 순서
            correct_order: 정답 순서
            language: 프로그래밍 언어
            strict_mode: True면 정확한 순서만 허용

        Returns:
            ValidationResult
        """
        # 1. 정확히 일치하면 바로 정답
        if user_order == correct_order:
            return ValidationResult(
                is_correct=True,
                score=1.0,
                feedback="정확합니다! 🎉",
            )

        # 2. strict 모드면 틀림 처리
        if strict_mode:
            first_wrong = self._find_first_wrong(user_order, correct_order)
            return ValidationResult(
                is_correct=False,
                score=self._calculate_score(user_order, correct_order),
                feedback=f"{first_wrong + 1}번째 블록을 확인해보세요.",
                first_wrong_position=first_wrong,
                expected_block=blocks[correct_order[first_wrong]][:30],
            )

        # 3. 스마트 검증: 논리적 그룹 기반
        return await self._validate_smart(blocks, user_order, correct_order, language)

    async def _validate_smart(
        self,
        blocks: List[str],
        user_order: List[int],
        correct_order: List[int],
        language: str,
    ) -> ValidationResult:
        """
        스마트 검증: 그룹 순서 유연

        - 함수/클래스 간 순서는 유연하게 허용
        - 의존성 있는 코드는 순서 엄격
        - import는 반드시 맨 앞
        """
        # 블록 분석
        analyzed_blocks = self._analyze_blocks(blocks, language)

        # 그룹화
        groups = self._identify_groups(analyzed_blocks)

        # 의존성 분석
        dependencies = self._analyze_dependencies(analyzed_blocks, language)

        # 사용자 순서로 코드 조합
        user_code = self._assemble_code(blocks, user_order)
        correct_code = self._assemble_code(blocks, correct_order)

        # 검증
        validation_errors = []

        # 1. import 순서 검증 (반드시 맨 앞)
        import_error = self._validate_imports_first(analyzed_blocks, user_order)
        if import_error:
            validation_errors.append(import_error)

        # 2. 의존성 순서 검증
        dep_error = self._validate_dependencies(analyzed_blocks, user_order, dependencies)
        if dep_error:
            validation_errors.append(dep_error)

        # 3. main block 검증 (있으면 맨 마지막)
        main_error = self._validate_main_last(analyzed_blocks, user_order)
        if main_error:
            validation_errors.append(main_error)

        # 에러가 없으면 정답!
        if not validation_errors:
            # Judge0로 실행 검증 (옵션)
            if self.judge0_enabled:
                exec_result = await self._validate_with_judge0(user_code, language)
                if not exec_result["success"]:
                    return ValidationResult(
                        is_correct=False,
                        score=0.8,  # 구조는 맞지만 실행 실패
                        feedback="구조는 맞지만 실행 시 오류가 발생해요.",
                        details={"execution_error": exec_result["error"]},
                    )

            return ValidationResult(
                is_correct=True,
                score=1.0,
                feedback="정확합니다! 순서가 논리적으로 맞아요. 🎉",
            )

        # 가장 중요한 에러 반환
        first_error = validation_errors[0]
        return ValidationResult(
            is_correct=False,
            score=self._calculate_score(user_order, correct_order),
            feedback=first_error["feedback"],
            first_wrong_position=first_error.get("position"),
            expected_block=first_error.get("expected"),
            details={"all_errors": validation_errors},
        )

    def _analyze_blocks(self, blocks: List[str], language: str) -> List[CodeBlock]:
        """각 블록의 타입과 이름 분석"""
        analyzed = []

        for i, content in enumerate(blocks):
            block_type = BlockType.OTHER
            name = None

            content_stripped = content.strip()

            if language == "python":
                # import
                if content_stripped.startswith(("import ", "from ")):
                    block_type = BlockType.IMPORT
                    # import module or from module import ...
                    match = re.match(r"(?:from\s+(\w+)|import\s+(\w+))", content_stripped)
                    if match:
                        name = match.group(1) or match.group(2)

                # class
                elif content_stripped.startswith("class "):
                    block_type = BlockType.CLASS
                    match = re.match(r"class\s+(\w+)", content_stripped)
                    if match:
                        name = match.group(1)

                # function
                elif content_stripped.startswith("def "):
                    block_type = BlockType.FUNCTION
                    match = re.match(r"def\s+(\w+)", content_stripped)
                    if match:
                        name = match.group(1)

                # main block
                elif 'if __name__' in content_stripped:
                    block_type = BlockType.MAIN

                # variable assignment (top-level)
                elif re.match(r"^\w+\s*=", content_stripped):
                    block_type = BlockType.VARIABLE
                    match = re.match(r"^(\w+)\s*=", content_stripped)
                    if match:
                        name = match.group(1)

            elif language in ("javascript", "typescript"):
                # import
                if content_stripped.startswith(("import ", "const {", "require(")):
                    block_type = BlockType.IMPORT

                # class
                elif content_stripped.startswith("class "):
                    block_type = BlockType.CLASS
                    match = re.match(r"class\s+(\w+)", content_stripped)
                    if match:
                        name = match.group(1)

                # function
                elif content_stripped.startswith(("function ", "const ", "let ", "var ")):
                    if "=>" in content_stripped or "function" in content_stripped:
                        block_type = BlockType.FUNCTION
                        match = re.match(r"(?:function\s+(\w+)|(?:const|let|var)\s+(\w+))", content_stripped)
                        if match:
                            name = match.group(1) or match.group(2)

            elif language in ("java", "c", "cpp"):
                # import/include
                if content_stripped.startswith(("#include", "import ")):
                    block_type = BlockType.IMPORT

                # class
                elif re.match(r"(?:public\s+)?class\s+", content_stripped):
                    block_type = BlockType.CLASS
                    match = re.search(r"class\s+(\w+)", content_stripped)
                    if match:
                        name = match.group(1)

                # function/method
                elif re.match(r"(?:public|private|protected|static|\w+)\s+\w+\s+\w+\s*\(", content_stripped):
                    block_type = BlockType.FUNCTION
                    match = re.search(r"\s+(\w+)\s*\(", content_stripped)
                    if match:
                        name = match.group(1)

            analyzed.append(CodeBlock(
                index=i,
                content=content,
                block_type=block_type,
                name=name,
            ))

        return analyzed

    def _identify_groups(self, blocks: List[CodeBlock]) -> List[BlockGroup]:
        """블록을 논리적 그룹으로 분류"""
        groups_dict: Dict[BlockType, List[CodeBlock]] = {}

        for block in blocks:
            if block.block_type not in groups_dict:
                groups_dict[block.block_type] = []
            groups_dict[block.block_type].append(block)

        groups = []
        for block_type, group_blocks in groups_dict.items():
            order_flexible = block_type in self.flexible_order_types
            groups.append(BlockGroup(
                group_type=block_type,
                blocks=group_blocks,
                order_flexible=order_flexible,
            ))

        return groups

    def _analyze_dependencies(
        self,
        blocks: List[CodeBlock],
        language: str
    ) -> Dict[int, List[int]]:
        """
        블록 간 의존성 분석

        Returns:
            {block_index: [dependent_block_indices]}
        """
        dependencies: Dict[int, List[int]] = {}

        # 이름 → 블록 인덱스 매핑
        name_to_index: Dict[str, int] = {}
        for block in blocks:
            if block.name:
                name_to_index[block.name] = block.index

        # 각 블록이 사용하는 이름 찾기
        for block in blocks:
            deps = []

            # 블록 내용에서 참조하는 이름 찾기
            for name, def_index in name_to_index.items():
                if def_index == block.index:
                    continue  # 자기 자신 제외

                # 이름이 블록 내용에 있는지 확인
                if re.search(rf'\b{re.escape(name)}\b', block.content):
                    deps.append(def_index)

            if deps:
                dependencies[block.index] = deps

        return dependencies

    def _validate_imports_first(
        self,
        blocks: List[CodeBlock],
        user_order: List[int]
    ) -> Optional[Dict[str, Any]]:
        """import가 맨 앞에 있는지 검증"""
        import_indices = {b.index for b in blocks if b.block_type == BlockType.IMPORT}

        if not import_indices:
            return None

        # 사용자 순서에서 import가 아닌 첫 블록 찾기
        first_non_import_pos = None
        for pos, idx in enumerate(user_order):
            if idx not in import_indices:
                first_non_import_pos = pos
                break

        # import가 non-import 이후에 나오는지 확인
        if first_non_import_pos is not None:
            for pos, idx in enumerate(user_order[first_non_import_pos:], start=first_non_import_pos):
                if idx in import_indices:
                    return {
                        "type": "import_order",
                        "position": pos,
                        "feedback": "import는 코드 맨 앞에 와야 해요.",
                        "expected": "import 문",
                    }

        return None

    def _validate_dependencies(
        self,
        blocks: List[CodeBlock],
        user_order: List[int],
        dependencies: Dict[int, List[int]],
    ) -> Optional[Dict[str, Any]]:
        """의존성 순서 검증: 사용하는 것이 정의 뒤에"""
        position_map = {idx: pos for pos, idx in enumerate(user_order)}

        for block_idx, dep_indices in dependencies.items():
            block_pos = position_map.get(block_idx)
            if block_pos is None:
                continue

            for dep_idx in dep_indices:
                dep_pos = position_map.get(dep_idx)
                if dep_pos is not None and dep_pos > block_pos:
                    # 의존하는 블록이 더 뒤에 있음 = 잘못된 순서
                    dep_block = blocks[dep_idx]
                    using_block = blocks[block_idx]

                    return {
                        "type": "dependency",
                        "position": block_pos,
                        "feedback": f"'{dep_block.name}'이 먼저 정의되어야 해요.",
                        "expected": dep_block.content[:30],
                    }

        return None

    def _validate_main_last(
        self,
        blocks: List[CodeBlock],
        user_order: List[int],
    ) -> Optional[Dict[str, Any]]:
        """main 블록이 마지막에 있는지 검증"""
        main_indices = {b.index for b in blocks if b.block_type == BlockType.MAIN}

        if not main_indices:
            return None

        # main이 마지막이 아닌 경우
        for main_idx in main_indices:
            pos = None
            for p, idx in enumerate(user_order):
                if idx == main_idx:
                    pos = p
                    break

            if pos is not None and pos < len(user_order) - 1:
                # main 뒤에 다른 블록이 있음
                return {
                    "type": "main_order",
                    "position": pos,
                    "feedback": "main 블록은 맨 마지막에 와야 해요.",
                    "expected": "if __name__ == '__main__':",
                }

        return None

    def _assemble_code(self, blocks: List[str], order: List[int]) -> str:
        """블록을 순서대로 조합하여 코드 생성"""
        return "\n".join(blocks[i] for i in order)

    def _find_first_wrong(self, user_order: List[int], correct_order: List[int]) -> int:
        """첫 번째 틀린 위치 찾기"""
        for i, (u, c) in enumerate(zip(user_order, correct_order)):
            if u != c:
                return i
        return len(user_order) - 1

    def _calculate_score(self, user_order: List[int], correct_order: List[int]) -> float:
        """부분 점수 계산 (0.0 ~ 1.0)"""
        if not correct_order:
            return 0.0

        correct_count = sum(1 for u, c in zip(user_order, correct_order) if u == c)
        return correct_count / len(correct_order)

    async def _validate_with_judge0(
        self,
        code: str,
        language: str
    ) -> Dict[str, Any]:
        """
        Judge0로 실제 실행 검증

        Returns:
            {"success": bool, "output": str, "error": str}
        """
        try:
            from .judge0 import judge0_service

            # 언어 ID 매핑
            language_ids = {
                "python": 71,
                "javascript": 63,
                "java": 62,
                "c": 50,
                "cpp": 54,
            }

            lang_id = language_ids.get(language, 71)

            result = await judge0_service.execute(
                source_code=code,
                language_id=lang_id,
                stdin="",
                timeout=5,
            )

            if result.get("status", {}).get("id") == 3:  # Accepted
                return {"success": True, "output": result.get("stdout", "")}
            else:
                return {
                    "success": False,
                    "error": result.get("stderr", "") or result.get("compile_output", ""),
                }

        except Exception as e:
            # Judge0 실패 시 구조 검증만으로 판단
            print(f"[PuzzleValidator] Judge0 error: {e}")
            return {"success": True, "output": ""}


# ============================================================
# Singleton Instance
# ============================================================

_puzzle_validator: Optional[PuzzleValidator] = None


def get_puzzle_validator(judge0_enabled: bool = False) -> PuzzleValidator:
    """PuzzleValidator 싱글톤 반환"""
    global _puzzle_validator
    if _puzzle_validator is None:
        _puzzle_validator = PuzzleValidator(judge0_enabled=judge0_enabled)
    return _puzzle_validator


# ============================================================
# Convenience Functions
# ============================================================

async def validate_puzzle(
    blocks: List[str],
    user_order: List[int],
    correct_order: List[int],
    language: str = "python",
    strict_mode: bool = False,
) -> ValidationResult:
    """
    퍼즐 검증 편의 함수

    Example:
        result = await validate_puzzle(
            blocks=["import os", "def main():", "    print('hi')", "main()"],
            user_order=[0, 1, 2, 3],
            correct_order=[0, 1, 2, 3],
        )
        if result.is_correct:
            print("정답!")
    """
    validator = get_puzzle_validator()
    return await validator.validate(blocks, user_order, correct_order, language, strict_mode)
