#!/usr/bin/env python3
"""
솔루션 생성 스크립트 (Claude Code와 함께 사용)
- 문제를 읽고 Python, Java, C++ 정답 코드 생성
- language 필드 제거
- solutions 필드 완성
"""

import json
from pathlib import Path
from typing import List, Dict


def load_problems(file_path: Path) -> List[Dict]:
    """문제 로드"""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_problems(problems: List[Dict], file_path: Path):
    """문제 저장"""
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(problems, f, ensure_ascii=False, indent=2)


def get_problem_for_generation(problem: Dict) -> str:
    """솔루션 생성을 위한 프롬프트 생성"""
    name = problem.get("name", "Unknown")
    question = problem.get("question", "")
    input_output = problem.get("input_output", "")

    if isinstance(input_output, str):
        try:
            input_output = json.loads(input_output)
        except:
            pass

    prompt = f"""
## 문제: {name}

### 문제 설명
{question[:2000]}

### 입출력 예시
{json.dumps(input_output, ensure_ascii=False, indent=2) if input_output else "없음"}

---
위 문제에 대해 Python, Java, C++ 정답 코드를 생성해주세요.

다음 JSON 형식으로 출력해주세요:
```json
{{
  "solutions": [
    {{"language": "python", "code": "..."}},
    {{"language": "java", "code": "..."}},
    {{"language": "cpp", "code": "..."}}
  ]
}}
```
"""
    return prompt


def extract_problems_batch(problems: List[Dict], start: int, batch_size: int = 10) -> List[Dict]:
    """배치로 문제 추출"""
    return problems[start:start + batch_size]


def format_batch_prompt(problems: List[Dict]) -> str:
    """배치 프롬프트 생성"""
    prompts = []
    for i, p in enumerate(problems):
        prompts.append(f"### 문제 {i+1}: {p.get('original_id', 'unknown')}\n{get_problem_for_generation(p)}")

    return "\n\n---\n\n".join(prompts)


def main():
    data_dir = Path(__file__).parent.parent / "data"

    # 파일 경로
    baekjoon_path = data_dir / "baekjoon" / "checkpoint_1000_4562.json"
    programmers_path = data_dir / "programmers" / "problems.json"

    # 문제 로드
    baekjoon = load_problems(baekjoon_path)
    programmers = load_problems(programmers_path)

    print(f"백준: {len(baekjoon)}개")
    print(f"프로그래머스: {len(programmers)}개")

    # language 필드 제거하고 solutions 확인
    for p in baekjoon:
        if "language" in p:
            del p["language"]
        if not p.get("solutions"):
            p["solutions"] = []

    for p in programmers:
        if "language" in p:
            del p["language"]
        if not p.get("solutions"):
            p["solutions"] = []

    # 변경사항 저장
    save_problems(baekjoon, baekjoon_path)
    save_problems(programmers, programmers_path)

    print("\nlanguage 필드 제거 완료!")
    print("solutions 생성은 Claude Code 에이전트를 통해 진행해주세요.")

    # 첫 번째 문제 예시 출력
    print("\n=== 첫 번째 문제 예시 ===")
    print(get_problem_for_generation(baekjoon[0]))


if __name__ == "__main__":
    main()
