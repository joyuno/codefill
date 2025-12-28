#!/usr/bin/env python3
"""
TACO 문제 데이터를 20% 랜덤 추출하여 Supabase에 삽입하는 스크립트
"""

import json
import os
import random
import requests
from pathlib import Path
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv(Path(__file__).parent.parent / '.env')

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
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

INPUT_FILE = Path(__file__).parent.parent / "data/unified/taco_unified.json"


def transform_problem(problem: dict, index: int) -> dict:
    """TACO 데이터를 base_problems 스키마에 맞게 변환"""

    # solutions 처리
    solutions = problem.get("solutions", [])
    if not solutions:
        solutions = []

    # input_output 처리
    input_output = problem.get("input_output")
    if isinstance(input_output, dict):
        input_output = json.dumps(input_output, ensure_ascii=False)
    elif isinstance(input_output, str):
        pass  # 이미 문자열이면 그대로 사용

    # difficulty 매핑 (TACO에는 없을 수 있음)
    difficulty = problem.get("difficulty", "medium")

    # original_id를 taco_1, taco_2 형식으로 변경
    original_id = f"taco_{index}"

    # source 추출 (원본 id에서)
    original_problem_id = problem.get("id", "")
    source = "taco"
    if "_" in original_problem_id:
        source = original_problem_id.split("_")[0]  # codeforces, atcoder 등

    name = problem.get("name", original_problem_id)[:255]

    return {
        "original_id": original_id,
        "name": name,
        "question": problem.get("question", ""),
        "input_output": input_output,
        "difficulty": difficulty,
        "tags": problem.get("tags", []),
        "source": source,
        "url": problem.get("url"),
        "time_limit": problem.get("time_limit"),
        "memory_limit": problem.get("memory_limit"),
        "solutions": solutions[:5] if solutions else [],
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
        # 각 문제에 고유 인덱스 부여
        transformed = [transform_problem(p, start_index + i + j) for j, p in enumerate(batch)]

        try:
            # upsert 사용 (중복 시 업데이트)
            headers = {**HEADERS, "Prefer": "resolution=merge-duplicates"}
            response = requests.post(url, headers=headers, json=transformed)

            if response.status_code in [200, 201]:
                inserted += len(transformed)
            else:
                print(f"  Error at batch {i//batch_size}: {response.status_code}")
                print(f"  Response: {response.text[:200]}")
                errors += len(transformed)
        except Exception as e:
            print(f"  Exception: {e}")
            errors += len(transformed)

        print(f"  [{inserted + errors}/{total}] 삽입됨: {inserted}, 오류: {errors}")

    return inserted, errors


def main(sample_count: int = 5000):
    print("=" * 60)
    print(f"TACO 문제 데이터 로드 및 {sample_count}개 랜덤 추출")
    print("=" * 60)

    # 파일 로드 (메모리 주의)
    print(f"\n파일 로드 중: {INPUT_FILE}")
    print("(4.6GB 파일이므로 시간이 걸릴 수 있습니다...)")

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    total_count = len(data)

    print(f"\n전체 문제 수: {total_count}개")
    print(f"추출할 문제 수: {sample_count}개")

    # 랜덤 추출
    random.seed(42)  # 재현 가능하도록 시드 설정
    sampled = random.sample(data, sample_count)

    print(f"\n랜덤 추출 완료: {len(sampled)}개")

    # 사용자 컨펌
    print("\n" + "=" * 60)
    print("📊 추출 결과 요약")
    print("=" * 60)
    print(f"  • 전체: {total_count}개")
    print(f"  • 추출: {sample_count}개")
    print("=" * 60)

    # 샘플 표시
    print("\n📝 샘플 5개:")
    for i, p in enumerate(sampled[:5], 1):
        pid = p.get("id", "unknown")
        q_preview = p.get("question", "")[:50].replace("\n", " ")
        sol_count = len(p.get("solutions", []))
        print(f"  {i}. {pid} ({sol_count}개 솔루션)")

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

    parser = argparse.ArgumentParser(description="TACO 문제 DB 삽입")
    parser.add_argument("--count", type=int, default=5000, help="추출할 문제 수 (기본: 5000)")

    args = parser.parse_args()
    main(sample_count=args.count)
