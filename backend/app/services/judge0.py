"""
Judge0 Code Execution Service

Judge0 API와 통신하여 코드를 실행합니다.
셀프 호스팅 또는 RapidAPI 모드 모두 지원합니다.

- 셀프 호스팅: JUDGE0_API_HOST가 비어있으면 X-Auth-Token 헤더 사용
- RapidAPI: JUDGE0_API_HOST가 설정되면 X-RapidAPI-Key/Host 헤더 사용
"""

import httpx
import base64
import re
import json
from typing import Optional, List, Dict, Any, Tuple
from ..config import get_settings

# 언어 ID 매핑 (Judge0 CE)
LANGUAGE_IDS = {
    "python": 71,      # Python (3.8.1)
    "python3": 71,
    "javascript": 63,  # JavaScript (Node.js 12.14.0)
    "java": 62,        # Java (OpenJDK 13.0.1)
    "cpp": 54,         # C++ (GCC 9.2.0)
    "c": 50,           # C (GCC 9.2.0)
    "typescript": 74,  # TypeScript (3.7.4)
    "go": 60,          # Go (1.13.5)
    "rust": 73,        # Rust (1.40.0)
    "ruby": 72,        # Ruby (2.7.0)
}

# 상태 코드 매핑
STATUS_DESCRIPTIONS = {
    1: "In Queue",
    2: "Processing",
    3: "Accepted",
    4: "Wrong Answer",
    5: "Time Limit Exceeded",
    6: "Compilation Error",
    7: "Runtime Error (SIGSEGV)",
    8: "Runtime Error (SIGXFSZ)",
    9: "Runtime Error (SIGFPE)",
    10: "Runtime Error (SIGABRT)",
    11: "Runtime Error (NZEC)",
    12: "Runtime Error (Other)",
    13: "Internal Error",
    14: "Exec Format Error",
}


class Judge0Service:
    """Judge0 API 서비스 클래스"""

    def __init__(self):
        settings = get_settings()
        self.base_url = settings.judge0_url
        self.api_key = settings.judge0_api_key
        self.api_host = settings.judge0_api_host

    def _get_headers(self) -> Dict[str, str]:
        """API 헤더 생성 (셀프 호스팅 또는 RapidAPI 지원)"""
        headers = {"Content-Type": "application/json"}

        # 셀프 호스팅: X-Auth-Token 사용
        # RapidAPI: X-RapidAPI-Key, X-RapidAPI-Host 사용
        if self.api_host:
            # RapidAPI 모드
            headers["X-RapidAPI-Key"] = self.api_key
            headers["X-RapidAPI-Host"] = self.api_host
        else:
            # 셀프 호스팅 모드
            if self.api_key:
                headers["X-Auth-Token"] = self.api_key

        return headers

    def get_language_id(self, language: str) -> int:
        """언어 이름을 ID로 변환"""
        return LANGUAGE_IDS.get(language.lower(), 71)  # 기본값: Python

    async def submit_code(
        self,
        source_code: str,
        language: str,
        stdin: str = "",
        expected_output: Optional[str] = None,
        cpu_time_limit: float = 5.0,
        memory_limit: int = 128000,
    ) -> Dict[str, Any]:
        """
        코드 제출 및 실행 (동기 방식 - wait=true)

        Args:
            source_code: 실행할 소스 코드
            language: 프로그래밍 언어 (python, javascript, java, cpp 등)
            stdin: 표준 입력
            expected_output: 예상 출력 (채점 시 사용)
            cpu_time_limit: CPU 시간 제한 (초)
            memory_limit: 메모리 제한 (KB)

        Returns:
            실행 결과 딕셔너리
        """
        language_id = self.get_language_id(language)

        # Base64 인코딩 (한글 등 유니코드 지원)
        encoded_source = base64.b64encode(source_code.encode('utf-8')).decode('utf-8')
        encoded_stdin = base64.b64encode((stdin or "").encode('utf-8')).decode('utf-8')

        payload = {
            "source_code": encoded_source,
            "language_id": language_id,
            "stdin": encoded_stdin,
        }

        if expected_output:
            encoded_expected = base64.b64encode(expected_output.encode('utf-8')).decode('utf-8')
            payload["expected_output"] = encoded_expected

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/submissions",
                params={"base64_encoded": "true", "wait": "true", "fields": "*"},
                headers=self._get_headers(),
                json=payload,
            )

            if response.status_code == 201 or response.status_code == 200:
                return self._parse_result(response.json())
            else:
                return {
                    "success": False,
                    "error": f"Judge0 API Error: {response.status_code}",
                    "detail": response.text,
                }

    async def submit_code_async(
        self,
        source_code: str,
        language: str,
        stdin: str = "",
    ) -> Dict[str, Any]:
        """
        코드 제출 (비동기 방식 - 토큰 반환)
        """
        language_id = self.get_language_id(language)

        payload = {
            "source_code": source_code,
            "language_id": language_id,
            "stdin": stdin,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/submissions",
                params={"base64_encoded": "false", "wait": "false"},
                headers=self._get_headers(),
                json=payload,
            )

            if response.status_code == 201:
                data = response.json()
                return {"success": True, "token": data.get("token")}
            else:
                return {
                    "success": False,
                    "error": f"Judge0 API Error: {response.status_code}",
                }

    async def get_submission(self, token: str) -> Dict[str, Any]:
        """토큰으로 제출 결과 조회"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.base_url}/submissions/{token}",
                params={"base64_encoded": "false"},
                headers=self._get_headers(),
            )

            if response.status_code == 200:
                return self._parse_result(response.json())
            else:
                return {
                    "success": False,
                    "error": f"Judge0 API Error: {response.status_code}",
                }

    def _decode_base64(self, value: Optional[str]) -> str:
        """Base64 디코딩 (None 또는 빈 문자열 처리)"""
        if not value:
            return ""
        try:
            return base64.b64decode(value).decode('utf-8')
        except Exception:
            return value  # 디코딩 실패시 원본 반환

    def _parse_result(self, data: Dict[str, Any], decode_base64: bool = True) -> Dict[str, Any]:
        """Judge0 응답 파싱"""
        status = data.get("status", {})
        status_id = status.get("id", 0)

        stdout = data.get("stdout") or ""
        stderr = data.get("stderr") or ""
        compile_output = data.get("compile_output") or ""
        message = data.get("message") or ""

        # Base64 디코딩
        if decode_base64:
            stdout = self._decode_base64(stdout)
            stderr = self._decode_base64(stderr)
            compile_output = self._decode_base64(compile_output)

        return {
            "success": True,
            "token": data.get("token"),
            "status": {
                "id": status_id,
                "description": status.get("description", STATUS_DESCRIPTIONS.get(status_id, "Unknown")),
            },
            "stdout": stdout,
            "stderr": stderr,
            "compile_output": compile_output,
            "message": message,
            "time": data.get("time"),
            "memory": data.get("memory"),
            "is_correct": status_id == 3,  # Accepted
            "is_error": status_id >= 4,
        }

    async def run_test_cases(
        self,
        source_code: str,
        language: str,
        test_cases: List[Dict[str, Any]],
        auto_wrap_function: bool = True,
    ) -> Dict[str, Any]:
        """
        여러 테스트 케이스 실행

        Args:
            source_code: 실행할 소스 코드
            language: 프로그래밍 언어
            test_cases: 테스트 케이스 리스트 [{"input": "...", "expected": "..."}]
            auto_wrap_function: 함수형 코드 자동 래핑 여부

        Returns:
            테스트 결과
        """
        results = []
        passed_count = 0

        # 함수형 코드 감지 (한 번만 수행)
        func_info = None
        if auto_wrap_function:
            func_info = detect_function_definition(source_code, language)
            print(f"[Judge0] Function detection: {func_info}")
            if func_info:
                func_name, params = func_info
                has_call = has_function_call(source_code, func_name)
                stdin_used = uses_stdin(source_code)
                print(f"[Judge0] Has function call: {has_call}, Uses stdin: {stdin_used}")
                # 이미 함수 호출이 있거나 stdin을 사용하면 래핑 불필요
                if has_call or stdin_used:
                    func_info = None

        for i, tc in enumerate(test_cases):
            test_input = tc.get("input", "")
            print(f"[Judge0] Test case {i}: input type={type(test_input)}, value={test_input}")
            stdin = ""

            # 함수형 코드 래핑
            code_to_run = source_code
            if func_info:
                func_name, params = func_info
                code_to_run = wrap_function_code(
                    source_code, language, test_input, func_name, params
                )
                print(f"[Judge0] Wrapped code:\n{code_to_run[-200:]}")
                # 래핑된 코드는 stdin 불필요 (인자가 코드에 직접 삽입됨)
                stdin = ""
            else:
                # 일반 코드는 stdin 사용
                if isinstance(test_input, list):
                    stdin = "\n".join(str(x) for x in test_input)
                elif isinstance(test_input, dict):
                    stdin = json.dumps(test_input)
                else:
                    stdin = str(test_input) if test_input else ""

            expected = tc.get("expected")
            if expected is not None:
                expected = str(expected)

            result = await self.submit_code(
                source_code=code_to_run,
                language=language,
                stdin=stdin,
                expected_output=expected,
            )

            # 결과 비교
            actual_output = result.get("stdout", "").strip()
            expected_str = str(expected).strip() if expected else ""

            passed = False
            if result.get("status", {}).get("id") == 3:
                passed = True
            elif expected and actual_output == expected_str:
                passed = True

            if passed:
                passed_count += 1

            results.append({
                "test_case": i + 1,
                "passed": passed,
                "input": tc.get("input"),
                "expected": expected,
                "actual": actual_output,
                "time": result.get("time"),
                "memory": result.get("memory"),
                "status": result.get("status"),
                "error": result.get("stderr") or result.get("compile_output") or result.get("message"),
            })

        return {
            "success": True,
            "total": len(test_cases),
            "passed": passed_count,
            "failed": len(test_cases) - passed_count,
            "all_passed": passed_count == len(test_cases),
            "results": results,
        }

    async def get_languages(self) -> List[Dict[str, Any]]:
        """지원 언어 목록 조회"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.base_url}/languages",
                headers=self._get_headers(),
            )

            if response.status_code == 200:
                return response.json()
            else:
                return []


# ============================================================
# 함수형 코드 자동 래핑 유틸리티
# ============================================================

def detect_function_definition(source_code: str, language: str) -> Optional[Tuple[str, List[str]]]:
    """
    코드에서 함수 정의를 감지합니다.

    Returns:
        (함수명, [파라미터 목록]) 또는 None
    """
    if language.lower() not in ["python", "python3"]:
        return None

    # Python 함수 정의 패턴: def function_name(param1, param2, ...):
    pattern = r'^def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(([^)]*)\)\s*:'
    match = re.search(pattern, source_code, re.MULTILINE)

    if not match:
        return None

    func_name = match.group(1)
    params_str = match.group(2).strip()

    # 파라미터 파싱 (타입 힌트 제거)
    params = []
    if params_str:
        for p in params_str.split(','):
            # 타입 힌트 제거: param: Type -> param
            param = p.split(':')[0].strip()
            # 기본값 제거: param=default -> param
            param = param.split('=')[0].strip()
            if param:
                params.append(param)

    return (func_name, params)


def has_function_call(source_code: str, func_name: str) -> bool:
    """
    코드에 해당 함수 호출이 있는지 확인합니다.
    (함수 정의 내부가 아닌 최상위 레벨에서 호출되는지 확인)
    """
    lines = source_code.split('\n')
    in_main_block = False

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue
        # 함수 정의가 아닌 라인에서 함수 호출 확인
        if not stripped.startswith('def '):
            # 최상위 레벨 (들여쓰기 없음)
            if not line.startswith(' ') and not line.startswith('\t'):
                if re.search(rf'\b{func_name}\s*\(', stripped):
                    return True
                # if __name__ == '__main__': 블록 감지
                if re.search(r'if\s+__name__\s*==\s*["\']__main__["\']', stripped):
                    in_main_block = True
                    continue
                else:
                    in_main_block = False

            # if __name__ 블록 내부의 호출 감지
            if in_main_block and (line.startswith(' ') or line.startswith('\t')):
                if re.search(rf'\b{func_name}\s*\(', stripped):
                    return True

            # print(func_name(...)) 패턴
            if re.search(rf'print\s*\(\s*{func_name}\s*\(', stripped):
                return True

    return False


def uses_stdin(source_code: str) -> bool:
    """코드가 stdin을 사용하는지 확인 (input() 또는 sys.stdin)"""
    return bool(
        re.search(r'\binput\s*\(', source_code) or
        re.search(r'sys\.stdin', source_code)
    )


def parse_variable_assignment_string(input_str: str) -> Optional[Dict[str, Any]]:
    """
    'n = 6, connections = [[0, 1], [0, 2]]' 형식의 문자열을 파싱합니다.

    Returns:
        {"n": 6, "connections": [[0, 1], [0, 2]]} 또는 None
    """
    if not isinstance(input_str, str):
        return None

    # 변수 할당 패턴 확인: "var = value" 형식이 있는지
    if '=' not in input_str:
        return None

    result = {}
    # 패턴: 변수명 = 값 (값은 리스트, 숫자, 문자열 등)
    # 예: n = 6, connections = [[0, 1], [0, 2]]

    # 간단한 파싱: eval 사용 (안전한 환경에서만)
    try:
        # "n = 6, connections = [[0,1]]" -> {"n": 6, "connections": [[0,1]]}
        # 각 할당문을 분리
        import ast

        # 쉼표로 분리하되, 리스트 내부의 쉼표는 제외
        # 정규식으로 "변수명 = 값" 패턴 추출
        pattern = r'(\w+)\s*=\s*'
        parts = re.split(pattern, input_str)

        # parts: ['', 'n', '6, ', 'connections', '[[0, 1], [0, 2]]']
        i = 1
        while i < len(parts) - 1:
            var_name = parts[i].strip()
            value_str = parts[i + 1].strip()

            # 다음 변수까지의 값 추출 (마지막 쉼표 제거)
            if value_str.endswith(','):
                value_str = value_str[:-1].strip()

            # 값 파싱
            try:
                value = ast.literal_eval(value_str)
            except (ValueError, SyntaxError):
                value = value_str

            result[var_name] = value
            i += 2

        return result if result else None

    except Exception as e:
        print(f"[Judge0] Failed to parse variable assignment: {e}")
        return None


def wrap_function_code(
    source_code: str,
    language: str,
    test_input: Any,
    func_name: str,
    params: List[str]
) -> str:
    """
    함수형 코드에 호출 래퍼를 추가합니다.

    Args:
        source_code: 원본 코드 (함수 정의만 있음)
        language: 프로그래밍 언어
        test_input: 테스트 입력 (JSON 형식 또는 문자열)
        func_name: 함수 이름
        params: 파라미터 목록

    Returns:
        래퍼가 추가된 코드
    """
    if language.lower() not in ["python", "python3"]:
        return source_code

    # 변수 할당 형식 문자열 파싱 시도: "n = 6, connections = [[0,1]]"
    if isinstance(test_input, str) and '=' in test_input:
        parsed = parse_variable_assignment_string(test_input)
        if parsed:
            print(f"[Judge0] Parsed variable assignment: {parsed}")
            test_input = parsed

    # 입력값 처리
    args = []

    if isinstance(test_input, dict):
        # 딕셔너리 형태: {"n": 5, "connections": [[0,1], [1,2]]}
        for param in params:
            if param in test_input:
                args.append(repr(test_input[param]))
            else:
                args.append("None")
    elif isinstance(test_input, list):
        # 리스트 형태: [5, [[0,1], [1,2]]]
        for i, param in enumerate(params):
            if i < len(test_input):
                args.append(repr(test_input[i]))
            else:
                args.append("None")
    elif isinstance(test_input, str):
        # 문자열 형태: JSON 파싱 시도
        try:
            parsed = json.loads(test_input)
            return wrap_function_code(source_code, language, parsed, func_name, params)
        except json.JSONDecodeError:
            # JSON 파싱 실패 시 stdin 기반 래퍼 생성
            wrapper = f"""
# Auto-generated test wrapper
import sys
import json

# 원본 함수 실행 및 결과 출력
if __name__ == "__main__":
    try:
        input_data = sys.stdin.read().strip()
        if input_data:
            args = json.loads(input_data)
            if isinstance(args, list):
                result = {func_name}(*args)
            elif isinstance(args, dict):
                result = {func_name}(**args)
            else:
                result = {func_name}(args)
            print(result)
    except Exception as e:
        print(f"Error: {{e}}", file=sys.stderr)
"""
            return source_code + wrapper
    else:
        # 단일 값
        args = [repr(test_input)]

    # 래퍼 코드 생성
    args_str = ", ".join(args)
    wrapper = f"\n\n# Auto-generated test call\nprint({func_name}({args_str}))\n"

    return source_code + wrapper


# 싱글톤 인스턴스
judge0_service = Judge0Service()
