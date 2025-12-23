#!/usr/bin/env python3
"""
생성된 솔루션을 JSON 파일에 적용하는 스크립트

사용법:
python3 apply_solutions.py --source baekjoon --solutions '[{"original_id": "1000", "solutions": [...]}]'

또는 파일에서 읽기:
python3 apply_solutions.py --source baekjoon --file solutions.json
"""

import json
import argparse
from pathlib import Path


def load_problems(source: str) -> tuple:
    """문제 로드 및 경로 반환"""
    data_dir = Path(__file__).parent.parent / "data"

    if source == "baekjoon":
        path = data_dir / "baekjoon" / "checkpoint_1000_4562.json"
    else:
        path = data_dir / "programmers" / "problems.json"

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f), path


def save_problems(problems: list, path: Path):
    """문제 저장"""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(problems, f, ensure_ascii=False, indent=2)


def apply_solutions(problems: list, solutions: list) -> int:
    """솔루션 적용"""
    # original_id로 인덱싱
    problem_map = {p.get("original_id"): p for p in problems}

    applied = 0
    for sol in solutions:
        oid = sol.get("original_id")
        if oid in problem_map:
            problem_map[oid]["solutions"] = sol.get("solutions", [])
            applied += 1
            print(f"  ✓ {oid} 솔루션 적용")
        else:
            print(f"  ✗ {oid} 문제를 찾을 수 없음")

    return applied


def main():
    parser = argparse.ArgumentParser(description="솔루션 적용")
    parser.add_argument("--source", choices=["baekjoon", "programmers"], required=True)
    parser.add_argument("--solutions", help="JSON 문자열로 솔루션")
    parser.add_argument("--file", help="솔루션 JSON 파일 경로")

    args = parser.parse_args()

    # 솔루션 로드
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            solutions = json.load(f)
    elif args.solutions:
        solutions = json.loads(args.solutions)
    else:
        print("--solutions 또는 --file 옵션이 필요합니다")
        return

    # 문제 로드
    problems, path = load_problems(args.source)
    print(f"소스: {args.source}")
    print(f"문제 수: {len(problems)}개")
    print(f"적용할 솔루션: {len(solutions)}개")
    print()

    # 솔루션 적용
    applied = apply_solutions(problems, solutions)

    # 저장
    save_problems(problems, path)
    print(f"\n완료! {applied}개 솔루션 적용됨")


if __name__ == "__main__":
    main()
