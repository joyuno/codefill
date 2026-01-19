"""
Code Execution Router

Judge0 API를 통한 코드 실행 엔드포인트
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List, Any

from ..services.judge0 import (
    judge0_service,
    detect_function_definition,
    has_function_call,
    wrap_function_code,
    parse_variable_assignment_string,
)
import json

router = APIRouter()


# ===========================================
# Request/Response Models
# ===========================================


class ExecuteCodeRequest(BaseModel):
    """코드 실행 요청"""
    source_code: str = Field(..., description="실행할 소스 코드")
    language: str = Field(..., description="프로그래밍 언어 (python, javascript, java, cpp 등)")
    stdin: str = Field(default="", description="표준 입력")
    expected_output: Optional[str] = Field(default=None, description="예상 출력 (채점용)")
    cpu_time_limit: float = Field(default=5.0, ge=0.1, le=15.0, description="CPU 시간 제한 (초)")
    memory_limit: int = Field(default=128000, ge=1000, le=512000, description="메모리 제한 (KB)")


class TestCase(BaseModel):
    """테스트 케이스"""
    input: Any = Field(..., description="입력값")
    expected: Any = Field(..., description="예상 출력값")
    is_hidden: bool = Field(default=False, description="숨김 테스트 케이스 여부")


class RunTestsRequest(BaseModel):
    """테스트 케이스 실행 요청"""
    source_code: str = Field(..., description="실행할 소스 코드")
    language: str = Field(..., description="프로그래밍 언어")
    test_cases: List[TestCase] = Field(..., description="테스트 케이스 목록")


class ExecutionStatus(BaseModel):
    """실행 상태"""
    id: int
    description: str


class ExecuteCodeResponse(BaseModel):
    """코드 실행 응답"""
    success: bool
    token: Optional[str] = None
    status: Optional[ExecutionStatus] = None
    stdout: str = ""
    stderr: str = ""
    compile_output: str = ""
    message: str = ""
    time: Optional[str] = None
    memory: Optional[int] = None
    is_correct: bool = False
    is_error: bool = False
    error: Optional[str] = None
    detail: Optional[str] = None


class TestCaseResult(BaseModel):
    """단일 테스트 케이스 결과"""
    test_case: int
    passed: bool
    input: Any
    expected: Any
    actual: str
    time: Optional[str] = None
    memory: Optional[int] = None
    status: Optional[ExecutionStatus] = None
    error: Optional[str] = None


class RunTestsResponse(BaseModel):
    """테스트 케이스 실행 응답"""
    success: bool
    total: int
    passed: int
    failed: int
    all_passed: bool
    results: List[TestCaseResult]


class LanguageInfo(BaseModel):
    """언어 정보"""
    id: int
    name: str


# ===========================================
# Endpoints
# ===========================================


@router.post("/run", response_model=ExecuteCodeResponse)
async def execute_code(request: ExecuteCodeRequest):
    """
    코드 실행

    소스 코드를 Judge0 API를 통해 실행하고 결과를 반환합니다.
    함수형 코드의 경우 자동으로 함수 호출 래퍼를 추가합니다.
    """
    try:
        source_code = request.source_code
        stdin = request.stdin

        # 함수형 코드 자동 래핑
        func_info = detect_function_definition(source_code, request.language)
        if func_info:
            func_name, params = func_info
            if not has_function_call(source_code, func_name):
                test_input = None

                # 1. 변수 할당 형식 파싱 시도: "n = 5, connections = [[0,1]]"
                if stdin and '=' in stdin:
                    test_input = parse_variable_assignment_string(stdin)
                    if test_input:
                        print(f"[Execute] Parsed variable assignment: {test_input}")

                # 2. JSON 파싱 시도
                if test_input is None and stdin:
                    try:
                        test_input = json.loads(stdin)
                        print(f"[Execute] Parsed JSON: {test_input}")
                    except (json.JSONDecodeError, TypeError):
                        pass

                # 3. 줄 단위로 JSON 파싱 시도
                if test_input is None and stdin:
                    lines = stdin.strip().split('\n')
                    parsed_lines = []
                    for line in lines:
                        # 각 줄도 변수 할당 형식인지 확인
                        if '=' in line:
                            parsed = parse_variable_assignment_string(line)
                            if parsed:
                                parsed_lines.append(parsed)
                                continue
                        try:
                            parsed_lines.append(json.loads(line))
                        except json.JSONDecodeError:
                            parsed_lines.append(line)
                    if parsed_lines:
                        # 단일 딕셔너리면 그대로 사용
                        if len(parsed_lines) == 1 and isinstance(parsed_lines[0], dict):
                            test_input = parsed_lines[0]
                        else:
                            test_input = parsed_lines
                    print(f"[Execute] Parsed lines: {test_input}")

                # 래퍼 코드 추가
                if test_input is not None:
                    source_code = wrap_function_code(
                        source_code, request.language, test_input, func_name, params
                    )
                    stdin = ""  # 래핑된 코드는 stdin 불필요
                    print(f"[Execute] Wrapped function code with input: {test_input}")

        result = await judge0_service.submit_code(
            source_code=source_code,
            language=request.language,
            stdin=stdin,
            expected_output=request.expected_output,
            cpu_time_limit=request.cpu_time_limit,
            memory_limit=request.memory_limit,
        )

        if not result.get("success"):
            error_detail = result.get("detail", result.get("error", "Code execution failed"))
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=error_detail
            )

        return ExecuteCodeResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Execution error: {str(e)}"
        )


@router.post("/test", response_model=RunTestsResponse)
async def run_tests(request: RunTestsRequest):
    """
    테스트 케이스 실행

    여러 테스트 케이스를 실행하고 각 결과를 반환합니다.
    """
    try:
        # TestCase 모델을 dict로 변환
        test_cases = [
            {"input": tc.input, "expected": tc.expected}
            for tc in request.test_cases
        ]

        result = await judge0_service.run_test_cases(
            source_code=request.source_code,
            language=request.language,
            test_cases=test_cases,
        )

        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Test execution failed"
            )

        return RunTestsResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Test execution error: {str(e)}"
        )


@router.get("/languages", response_model=List[LanguageInfo])
async def get_languages():
    """
    지원 언어 목록 조회

    Judge0에서 지원하는 프로그래밍 언어 목록을 반환합니다.
    """
    try:
        languages = await judge0_service.get_languages()
        return [
            LanguageInfo(id=lang.get("id", 0), name=lang.get("name", "Unknown"))
            for lang in languages
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get languages: {str(e)}"
        )


@router.get("/submission/{token}")
async def get_submission(token: str):
    """
    제출 결과 조회

    토큰으로 이전에 제출한 코드의 실행 결과를 조회합니다.
    """
    try:
        result = await judge0_service.get_submission(token)

        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Submission not found"
            )

        return ExecuteCodeResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get submission: {str(e)}"
        )
