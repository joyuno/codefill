#!/usr/bin/env python3
"""
솔루션 생성 에이전트 실행기
Claude Code에서 배치로 문제를 처리하기 위한 스크립트

사용법:
1. Claude Code에서 이 스크립트의 출력을 복사
2. 에이전트에 전달하여 솔루션 생성
3. 생성된 솔루션을 apply_solutions.py로 적용
"""

import json
import argparse
from pathlib import Path


def load_problems(source: str) -> list:
    """문제 로드"""
    data_dir = Path(__file__).parent.parent / "data"

    if source == "baekjoon":
        path = data_dir / "baekjoon" / "checkpoint_1000_4562.json"
    else:
        path = data_dir / "programmers" / "problems.json"

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_unsolved_problems(problems: list) -> list:
    """solutions가 비어있는 문제만 추출"""
    return [p for p in problems if not p.get("solutions")]


def format_problems_for_agent(problems: list, start: int, batch_size: int) -> str:
    """에이전트에 전달할 형식으로 문제 포맷팅"""
    batch = problems[start:start + batch_size]

    output = []
    for p in batch:
        io = p.get("input_output", "")
        if isinstance(io, str):
            try:
                io = json.loads(io)
            except:
                io = {}

        output.append({
            "original_id": p.get("original_id"),
            "name": p.get("name"),
            "question": p.get("question", "")[:1500],  # 길이 제한
            "input_output": io
        })

    return json.dumps(output, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(description="솔루션 생성 에이전트 실행기")
    parser.add_argument("--source", choices=["baekjoon", "programmers"], default="baekjoon")
    parser.add_argument("--start", type=int, default=0, help="시작 인덱스")
    parser.add_argument("--batch", type=int, default=5, help="배치 크기")
    parser.add_argument("--show-prompt", action="store_true", help="에이전트 프롬프트 출력")

    args = parser.parse_args()

    problems = load_problems(args.source)
    unsolved = get_unsolved_problems(problems)

    print(f"소스: {args.source}")
    print(f"전체 문제: {len(problems)}개")
    print(f"미해결 문제: {len(unsolved)}개")
    print(f"처리 범위: {args.start} ~ {args.start + args.batch - 1}")
    print()

    if args.show_prompt:
        batch_data = format_problems_for_agent(unsolved, args.start, args.batch)
        print("=== 에이전트 프롬프트 ===")
        print(f"""
다음 코딩 문제들에 대해 Python, Java, C++ 정답 코드를 생성해주세요.

각 문제에 대해 다음 형식의 JSON을 출력해주세요:
```json
{{
  "original_id": "문제ID",
  "solutions": [
    {{"language": "python", "code": "정답코드"}},
    {{"language": "java", "code": "정답코드"}},
    {{"language": "cpp", "code": "정답코드"}}
  ]
}}
```

문제 목록:
{batch_data}
""")
    else:
        print("--show-prompt 옵션으로 프롬프트를 확인하세요")


if __name__ == "__main__":
    main()
