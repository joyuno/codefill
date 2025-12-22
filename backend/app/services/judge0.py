"""
Judge0 Code Execution Service

RapidAPI를 통해 Judge0 CE API와 통신하여 코드를 실행합니다.
"""

import httpx
import base64
from typing import Optional, List, Dict, Any
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
        """RapidAPI 헤더 생성"""
        return {
            "Content-Type": "application/json",
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": self.api_host,
        }

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
    ) -> Dict[str, Any]:
        """
        여러 테스트 케이스 실행

        Args:
            source_code: 실행할 소스 코드
            language: 프로그래밍 언어
            test_cases: 테스트 케이스 리스트 [{"input": "...", "expected": "..."}]

        Returns:
            테스트 결과
        """
        results = []
        passed_count = 0

        for i, tc in enumerate(test_cases):
            stdin = tc.get("input", "")
            if isinstance(stdin, list):
                # input이 리스트면 JSON 문자열로 변환하거나 줄바꿈으로 연결
                stdin = "\n".join(str(x) for x in stdin)

            expected = tc.get("expected")
            if expected is not None:
                expected = str(expected)

            result = await self.submit_code(
                source_code=source_code,
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


# 싱글톤 인스턴스
judge0_service = Judge0Service()
