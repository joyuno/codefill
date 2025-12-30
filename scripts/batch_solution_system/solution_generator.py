# 솔루션 생성기 - Claude Code가 직접 솔루션을 생성

import json
import re
from typing import Optional

def generate_solution_prompt(problem: dict) -> str:
    """문제 정보를 바탕으로 솔루션 생성 프롬프트 구성"""

    question = problem.get('question', '') or problem.get('question_html', '')
    # HTML 태그 제거
    question = re.sub(r'<[^>]+>', '', question)

    input_output = problem.get('input_output', '{}')
    if isinstance(input_output, str):
        try:
            io_data = json.loads(input_output)
        except:
            io_data = {}
    else:
        io_data = input_output

    examples = ""
    inputs = io_data.get('inputs', [])
    outputs = io_data.get('outputs', [])
    for i, (inp, out) in enumerate(zip(inputs[:3], outputs[:3])):
        examples += f"\n예제 {i+1}:\n입력: {inp}\n출력: {out}\n"

    time_limit = problem.get('time_limit', '2 초')
    memory_limit = problem.get('memory_limit', '256 MB')
    difficulty = problem.get('difficulty', 'unknown')
    problem_id = problem.get('original_id', problem.get('id', 'unknown'))

    return f"""백준 {problem_id}번 문제 솔루션을 Python, Java, C++ 세 가지 언어로 작성해주세요.

## 문제
{question}

## 제한
- 시간 제한: {time_limit}
- 메모리 제한: {memory_limit}
- 난이도: {difficulty}

## 예제
{examples}

## 요구사항
1. 각 언어별로 정확하고 효율적인 솔루션 작성
2. 한국어 주석으로 핵심 로직 설명
3. 백준 온라인 저지에서 실행 가능한 형태
4. 입력은 표준입력, 출력은 표준출력 사용

## 응답 형식
다음 JSON 형식으로 응답:
```json
{{
  "python": "파이썬 코드",
  "java": "자바 코드",
  "cpp": "C++ 코드"
}}
```
"""

def parse_solution_response(response: str) -> Optional[dict]:
    """Claude 응답에서 솔루션 추출"""
    # JSON 블록 찾기
    json_match = re.search(r'```json\s*([\s\S]*?)\s*```', response)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass

    # 직접 JSON 파싱 시도
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        pass

    # 코드 블록에서 개별 언어 추출
    solutions = {}

    python_match = re.search(r'```python\s*([\s\S]*?)\s*```', response)
    if python_match:
        solutions['python'] = python_match.group(1)

    java_match = re.search(r'```java\s*([\s\S]*?)\s*```', response)
    if java_match:
        solutions['java'] = java_match.group(1)

    cpp_match = re.search(r'```(?:cpp|c\+\+)\s*([\s\S]*?)\s*```', response)
    if cpp_match:
        solutions['cpp'] = cpp_match.group(1)

    return solutions if solutions else None

def format_solutions_for_storage(solutions: dict) -> list:
    """솔루션을 저장 형식으로 변환"""
    result = []

    if solutions.get('python'):
        result.append({
            "language": "python",
            "code": solutions['python']
        })

    if solutions.get('java'):
        result.append({
            "language": "java",
            "code": solutions['java']
        })

    if solutions.get('cpp'):
        result.append({
            "language": "cpp",
            "code": solutions['cpp']
        })

    return result
