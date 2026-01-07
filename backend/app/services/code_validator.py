"""
Code Validator Service

생성된 코드의 품질을 검증하는 서비스

Features:
1. Judge0를 통한 테스트 케이스 실행 검증
2. 문법 오류 검출
3. 시간/메모리 제한 검증
4. 코드 생성 실패 시 재생성 요청

Usage:
    validator = get_code_validator()
    result = await validator.validate_generated_code(
        code={"python": "..."},
        examples=[{"input": "1 2", "output": "3"}]
    )
    if result["valid"]:
        # 사용
    else:
        # 재생성 필요
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from .judge0 import judge0_service, LANGUAGE_IDS
from ..config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class ValidationResult:
    """코드 검증 결과"""
    valid: bool                     # 전체 통과 여부
    language: str                   # 검증된 언어
    passed_count: int               # 통과한 테스트 케이스 수
    total_count: int                # 전체 테스트 케이스 수
    pass_rate: float                # 통과율 (0~1)
    errors: List[str]               # 에러 목록
    details: List[Dict[str, Any]]   # 테스트별 상세 결과
    execution_time_avg: float       # 평균 실행 시간 (ms)
    memory_avg: float               # 평균 메모리 사용량 (KB)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "valid": self.valid,
            "language": self.language,
            "passed_count": self.passed_count,
            "total_count": self.total_count,
            "pass_rate": self.pass_rate,
            "errors": self.errors,
            "details": self.details,
            "execution_time_avg": self.execution_time_avg,
            "memory_avg": self.memory_avg,
        }


class CodeValidator:
    """
    코드 검증 서비스

    LLM이 생성한 코드가 실제로 동작하는지 Judge0로 검증합니다.

    Usage:
        validator = get_code_validator()

        # 생성된 코드 검증
        result = await validator.validate_generated_code(
            code={"python": "def solution(a, b): return a + b"},
            examples=[
                {"input": "1 2", "output": "3"},
                {"input": "10 20", "output": "30"},
            ]
        )

        if result.valid:
            print("코드 검증 통과!")
        else:
            print(f"검증 실패: {result.errors}")
    """

    # 검증 기준
    MIN_PASS_RATE = 0.8  # 최소 80% 통과 필요
    MAX_RETRIES = 2      # 최대 재시도 횟수
    TIMEOUT_SEC = 10     # 테스트 케이스당 타임아웃

    # 지원 언어 우선순위 (검증 순서)
    LANGUAGE_PRIORITY = ["python", "python3", "java", "cpp", "javascript"]

    def __init__(self):
        self.judge0 = judge0_service

    async def validate_generated_code(
        self,
        code: Dict[str, str],
        examples: List[Dict[str, Any]],
        language: Optional[str] = None,
        min_pass_rate: float = None,
    ) -> ValidationResult:
        """
        생성된 코드 검증

        Args:
            code: {"python": "...", "java": "..."} 언어별 코드
            examples: [{"input": "...", "output": "...", "explanation": "..."}]
            language: 검증할 언어 (None이면 자동 선택)
            min_pass_rate: 최소 통과율 (기본 0.8)

        Returns:
            ValidationResult: 검증 결과
        """
        if min_pass_rate is None:
            min_pass_rate = self.MIN_PASS_RATE

        # 1. 검증할 언어 선택
        target_language = self._select_language(code, language)
        if not target_language:
            return ValidationResult(
                valid=False,
                language="unknown",
                passed_count=0,
                total_count=len(examples),
                pass_rate=0.0,
                errors=["검증 가능한 언어 코드가 없습니다."],
                details=[],
                execution_time_avg=0,
                memory_avg=0,
            )

        source_code = code[target_language]

        # 2. 테스트 케이스 준비
        test_cases = self._prepare_test_cases(examples)
        if not test_cases:
            return ValidationResult(
                valid=False,
                language=target_language,
                passed_count=0,
                total_count=0,
                pass_rate=0.0,
                errors=["유효한 테스트 케이스가 없습니다."],
                details=[],
                execution_time_avg=0,
                memory_avg=0,
            )

        # 3. Judge0로 테스트 실행
        try:
            result = await self.judge0.run_test_cases(
                source_code=source_code,
                language=target_language,
                test_cases=test_cases,
            )

            if not result.get("success"):
                return ValidationResult(
                    valid=False,
                    language=target_language,
                    passed_count=0,
                    total_count=len(test_cases),
                    pass_rate=0.0,
                    errors=[f"Judge0 실행 실패: {result.get('error', 'Unknown')}"],
                    details=[],
                    execution_time_avg=0,
                    memory_avg=0,
                )

            # 4. 결과 분석
            return self._analyze_results(
                result=result,
                language=target_language,
                min_pass_rate=min_pass_rate,
            )

        except Exception as e:
            logger.error(f"[CodeValidator] Validation error: {e}")
            return ValidationResult(
                valid=False,
                language=target_language,
                passed_count=0,
                total_count=len(test_cases),
                pass_rate=0.0,
                errors=[f"검증 중 오류: {str(e)}"],
                details=[],
                execution_time_avg=0,
                memory_avg=0,
            )

    async def validate_with_retry(
        self,
        code_generator_func,
        examples: List[Dict[str, Any]],
        max_retries: int = None,
    ) -> tuple[Dict[str, str], ValidationResult]:
        """
        검증 실패 시 재생성하여 재검증

        Args:
            code_generator_func: async 코드 생성 함수
            examples: 테스트 케이스
            max_retries: 최대 재시도 횟수

        Returns:
            (생성된 코드, 검증 결과) 튜플
        """
        if max_retries is None:
            max_retries = self.MAX_RETRIES

        last_result = None
        last_code = None

        for attempt in range(max_retries + 1):
            # 코드 생성
            code = await code_generator_func()
            last_code = code

            if not code:
                logger.warning(f"[CodeValidator] Attempt {attempt + 1}: Code generation failed")
                continue

            # 검증
            result = await self.validate_generated_code(code, examples)
            last_result = result

            if result.valid:
                logger.info(f"[CodeValidator] Validation passed on attempt {attempt + 1}")
                return code, result

            logger.warning(
                f"[CodeValidator] Attempt {attempt + 1} failed: "
                f"{result.passed_count}/{result.total_count} passed, "
                f"errors: {result.errors}"
            )

        return last_code, last_result

    def _select_language(
        self,
        code: Dict[str, str],
        preferred: Optional[str] = None,
    ) -> Optional[str]:
        """검증할 언어 선택"""
        if preferred and preferred in code and code[preferred]:
            return preferred

        for lang in self.LANGUAGE_PRIORITY:
            if lang in code and code[lang]:
                return lang

        # 아무 언어나
        for lang, src in code.items():
            if src and lang in LANGUAGE_IDS:
                return lang

        return None

    def _prepare_test_cases(
        self,
        examples: List[Dict[str, Any]],
    ) -> List[Dict[str, str]]:
        """테스트 케이스 준비"""
        test_cases = []

        for ex in examples:
            input_data = ex.get("input", "")
            output_data = ex.get("output", "")

            # input이 리스트면 줄바꿈으로 연결
            if isinstance(input_data, list):
                input_data = "\n".join(str(x) for x in input_data)

            # output도 마찬가지
            if isinstance(output_data, list):
                output_data = "\n".join(str(x) for x in output_data)

            if output_data:  # output이 있는 경우만
                test_cases.append({
                    "input": str(input_data),
                    "expected": str(output_data).strip(),
                })

        return test_cases

    def _analyze_results(
        self,
        result: Dict[str, Any],
        language: str,
        min_pass_rate: float,
    ) -> ValidationResult:
        """테스트 결과 분석"""
        passed = result.get("passed", 0)
        total = result.get("total", 0)
        results = result.get("results", [])

        pass_rate = passed / total if total > 0 else 0.0
        valid = pass_rate >= min_pass_rate

        # 에러 수집
        errors = []
        for r in results:
            if not r.get("passed"):
                status = r.get("status", {})
                error_msg = r.get("error", "")
                status_desc = status.get("description", "")

                if status_desc in ["Compilation Error", "Runtime Error"]:
                    errors.append(f"TC{r.get('test_case')}: {status_desc} - {error_msg[:100]}")
                elif status_desc == "Wrong Answer":
                    errors.append(
                        f"TC{r.get('test_case')}: Wrong Answer "
                        f"(expected: {r.get('expected')[:50]}, got: {r.get('actual')[:50]})"
                    )
                elif status_desc == "Time Limit Exceeded":
                    errors.append(f"TC{r.get('test_case')}: Time Limit Exceeded")
                else:
                    errors.append(f"TC{r.get('test_case')}: {status_desc}")

        # 평균 실행 시간/메모리
        times = [float(r.get("time") or 0) for r in results if r.get("time")]
        memories = [float(r.get("memory") or 0) for r in results if r.get("memory")]

        avg_time = sum(times) / len(times) if times else 0
        avg_memory = sum(memories) / len(memories) if memories else 0

        return ValidationResult(
            valid=valid,
            language=language,
            passed_count=passed,
            total_count=total,
            pass_rate=pass_rate,
            errors=errors[:5],  # 최대 5개
            details=results,
            execution_time_avg=round(avg_time * 1000, 2),  # ms로 변환
            memory_avg=round(avg_memory, 2),
        )

    async def quick_syntax_check(
        self,
        code: str,
        language: str,
    ) -> Dict[str, Any]:
        """
        빠른 문법 검사 (실행 없이)

        간단한 입력으로 컴파일/파싱만 확인
        """
        try:
            result = await self.judge0.submit_code(
                source_code=code,
                language=language,
                stdin="",
                cpu_time_limit=1.0,
                memory_limit=32000,
            )

            status_id = result.get("status", {}).get("id", 0)

            return {
                "syntax_valid": status_id not in [6, 14],  # Compilation Error, Exec Format Error
                "status": result.get("status", {}),
                "compile_output": result.get("compile_output", ""),
            }

        except Exception as e:
            return {
                "syntax_valid": False,
                "error": str(e),
            }


# ============================================================
# Singleton Instance
# ============================================================

_code_validator: Optional[CodeValidator] = None


def get_code_validator() -> CodeValidator:
    """CodeValidator 싱글톤 반환"""
    global _code_validator
    if _code_validator is None:
        _code_validator = CodeValidator()
    return _code_validator
