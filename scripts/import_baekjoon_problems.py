"""
Baekjoon 문제 데이터를 base_problems 테이블에 삽입하는 스크립트

사용법:
    python scripts/import_baekjoon_problems.py
"""

import json
import os
import sys
from datetime import datetime

# 프로젝트 루트를 path에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from supabase import create_client

# Supabase 설정
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://qukgaiwdusuxcswsqhjo.supabase.co")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_SERVICE_KEY:
    # .env 파일에서 읽기 시도
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend", ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if line.startswith("SUPABASE_SERVICE_ROLE_KEY="):
                    SUPABASE_SERVICE_KEY = line.split("=", 1)[1].strip().strip('"\'')
                    break

if not SUPABASE_SERVICE_KEY:
    print("Error: SUPABASE_SERVICE_ROLE_KEY not found")
    sys.exit(1)

# ELO 매핑
ELO_MAPPING = {
    "easy": 800,
    "medium": 1000,
    "medium_hard": 1150,
    "hard": 1300,
    "very_hard": 1500,
}

def transform_problem(problem: dict) -> dict:
    """JSON 데이터를 DB 스키마에 맞게 변환"""
    difficulty = problem.get("difficulty", "medium")
    elo_rating = ELO_MAPPING.get(difficulty, 1000)

    # input_output이 문자열인 경우 JSON으로 파싱
    input_output = problem.get("input_output")
    if isinstance(input_output, str):
        try:
            input_output = json.loads(input_output)
        except:
            input_output = None

    return {
        "original_id": problem.get("original_id") or problem.get("id", "").replace("baekjoon_", ""),
        "name": problem.get("name", "Unnamed Problem"),
        "question": problem.get("question", ""),
        "question_html": problem.get("question_html"),
        "input_output": input_output,
        "difficulty": difficulty,
        "tags": problem.get("tags", []),
        "source": problem.get("source", "baekjoon"),
        "url": problem.get("url"),
        "time_limit": problem.get("time_limit"),
        "memory_limit": problem.get("memory_limit"),
        "solutions": problem.get("solutions", []),
        "images": problem.get("images") or [],
        "starter_code": problem.get("starter_code"),
        "explanation": problem.get("explanation"),
        # 기본값 필드들
        "like_count": 0,
        "solve_count": 0,
        "elo_rating": elo_rating,
        "success_rate": None,
        "avg_solve_time_seconds": None,
        "elo_update_count": 0,
        "deleted_at": None,
    }

def main():
    # JSON 파일 로드
    data_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "data", "baekjoon", "data_baekjoon", "validated_problems_clean.json"
    )

    print(f"Loading data from: {data_path}")
    with open(data_path, "r", encoding="utf-8") as f:
        problems = json.load(f)

    print(f"Total problems to import: {len(problems)}")

    # Supabase 클라이언트 생성
    supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

    # 기존 original_id 목록 조회 (중복 방지)
    print("Checking existing problems...")
    existing_result = supabase.table("base_problems").select("original_id").execute()
    existing_ids = {row["original_id"] for row in existing_result.data}
    print(f"Existing problems in DB: {len(existing_ids)}")

    # 새로운 문제만 필터링
    new_problems = []
    for p in problems:
        original_id = p.get("original_id") or p.get("id", "").replace("baekjoon_", "")
        if original_id not in existing_ids:
            new_problems.append(p)

    print(f"New problems to insert: {len(new_problems)}")

    if not new_problems:
        print("No new problems to insert. Done!")
        return

    # 배치로 삽입 (500개씩)
    BATCH_SIZE = 500
    total_inserted = 0
    errors = []

    for i in range(0, len(new_problems), BATCH_SIZE):
        batch = new_problems[i:i + BATCH_SIZE]
        batch_data = [transform_problem(p) for p in batch]

        try:
            result = supabase.table("base_problems").insert(batch_data).execute()
            total_inserted += len(result.data)
            print(f"Inserted batch {i // BATCH_SIZE + 1}: {len(result.data)} problems (total: {total_inserted})")
        except Exception as e:
            error_msg = f"Batch {i // BATCH_SIZE + 1} failed: {str(e)}"
            print(f"Error: {error_msg}")
            errors.append(error_msg)

            # 개별 삽입 시도
            for j, problem in enumerate(batch):
                try:
                    data = transform_problem(problem)
                    supabase.table("base_problems").insert(data).execute()
                    total_inserted += 1
                except Exception as inner_e:
                    errors.append(f"Problem {problem.get('id', 'unknown')}: {str(inner_e)}")

    print(f"\n=== Import Complete ===")
    print(f"Total inserted: {total_inserted}")
    print(f"Errors: {len(errors)}")

    if errors:
        print("\nErrors:")
        for err in errors[:10]:  # 처음 10개만 출력
            print(f"  - {err}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more errors")

if __name__ == "__main__":
    main()
