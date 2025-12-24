#!/usr/bin/env python3
"""
TACO 문제 데이터 중 solutions가 있는 것만 DB에 삽입
solutions 형식: [{language: "python", code: "..."}]
"""

import json
import os
import random
import requests
from pathlib import Path
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv(Path(__file__).parent.parent / 'backend/.env')

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: SUPABASE_URL 또는 SUPABASE_KEY가 설정되지 않았습니다.")
    exit(1)

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}

INPUT_FILE = Path(__file__).parent.parent / "data/taco/train.json"


def transform_solutions(solutions: list) -> list:
    """solutions를 [{language: "python", code: "..."}] 형태로 변환"""
    if not solutions:
        return []

    transformed = []
    for sol in solutions:
        if isinstance(sol, str):
            transformed.append({
                "language": "python",
                "code": sol
            })
        elif isinstance(sol, dict) and "code" in sol:
            # 이미 변환된 형식이면 그대로
            transformed.append(sol)

    return transformed[:5]  # 최대 5개


def transform_problem(problem: dict, index: int) -> dict:
    """TACO 데이터를 base_problems 스키마에 맞게 변환"""

    # solutions 변환
    solutions = transform_solutions(problem.get("solutions", []))

    # input_output 처리
    input_output = problem.get("input_output")
    if isinstance(input_output, dict):
        input_output = json.dumps(input_output, ensure_ascii=False)
    elif isinstance(input_output, str):
        pass

    # difficulty - 소문자로 변환
    difficulty = problem.get("difficulty").lower()

    # original_id를 taco_1 형식으로
    original_id = f"taco_{index}"

    # source - 직접 가져오기
    source = problem.get("source", "")

    name = problem.get("name", "")
    if name:
        name = name[:255]
    else:
        name = original_id

    return {
        "original_id": original_id,
        "name": name,
        "question": problem.get("question", ""),
        "input_output": input_output,
        "difficulty": difficulty,
        "tags": problem.get("tags") or [],
        "source": source,
        "url": problem.get("url"),
        "time_limit": problem.get("time_limit"),
        "memory_limit": problem.get("memory_limit"),
        "solutions": solutions,
        "explanation": problem.get("explanation"),
        "starter_code": problem.get("starter_code")
    }


def insert_batch(problems: list, batch_size: int = 50, start_index: int = 1):
    """배치로 문제 삽입"""
    url = f"{SUPABASE_URL}/rest/v1/base_problems"
    total = len(problems)
    inserted = 0
    errors = 0

    for i in range(0, total, batch_size):
        batch = problems[i:i+batch_size]
        transformed = [transform_problem(p, start_index + i + j) for j, p in enumerate(batch)]

        try:
            headers = {**HEADERS, "Prefer": "resolution=merge-duplicates"}
            response = requests.post(url, headers=headers, json=transformed, timeout=60)

            if response.status_code in [200, 201]:
                inserted += len(transformed)
            else:
                print(f"  Error at batch {i//batch_size}: {response.status_code}")
                print(f"  Response: {response.text[:200]}")
                errors += len(transformed)
        except Exception as e:
            print(f"  Exception: {e}")
            errors += len(transformed)

        if (i // batch_size) % 10 == 0 or i + batch_size >= total:
            print(f"  [{inserted + errors}/{total}] 삽입됨: {inserted}, 오류: {errors}")

    return inserted, errors


def main(sample_ratio: float = 0.2):
    print("=" * 60)
    print("TACO 문제 (solutions 있는 것만) DB 삽입")
    print("=" * 60)

    print(f"\n파일 로드 중: {INPUT_FILE}")
    print("(파일 크기가 크므로 시간이 걸릴 수 있습니다...)")

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    total_count = len(data)

    # solutions가 있는 문제만 필터링
    with_solutions = [p for p in data if p.get('solutions') and len(p.get('solutions', [])) > 0]

    print(f"\n전체 문제 수: {total_count}개")
    print(f"solutions 있는 문제: {len(with_solutions)}개")

    # 샘플 추출
    sample_count = int(len(with_solutions) * sample_ratio)
    random.seed(42)
    sampled = random.sample(with_solutions, sample_count)

    print(f"추출할 문제 수 ({sample_ratio*100:.0f}%): {sample_count}개")

    # 샘플 표시
    print("\n📝 변환된 solutions 형식 샘플:")
    sample_problem = sampled[0]
    transformed = transform_solutions(sample_problem.get('solutions', []))
    print(f"  원본 solutions 개수: {len(sample_problem.get('solutions', []))}")
    print(f"  변환된 solutions 개수: {len(transformed)}")
    if transformed:
        print(f"  변환된 형식: {{language: '{transformed[0]['language']}', code: '...'}}")
        print(f"  code 샘플: {transformed[0]['code'][:80]}...")

    print(f"\n⚠️  {sample_count}개 문제를 DB에 삽입합니다.")
    confirm = input("계속하시겠습니까? (y/n): ").strip().lower()

    if confirm != 'y':
        print("취소되었습니다.")
        return

    # DB 삽입
    print("\n" + "=" * 60)
    print("🚀 DB 삽입 시작!")
    print("=" * 60)

    inserted, errors = insert_batch(sampled)

    print("\n" + "=" * 60)
    print("✅ 완료!")
    print("=" * 60)
    print(f"  • 삽입: {inserted}개")
    print(f"  • 오류: {errors}개")
    print("=" * 60)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="TACO 문제 DB 삽입 (solutions 있는 것만)")
    parser.add_argument("--ratio", type=float, default=0.2, help="추출 비율 (기본: 0.2 = 20%)")

    args = parser.parse_args()
    main(sample_ratio=args.ratio)
