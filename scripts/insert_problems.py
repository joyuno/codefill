#!/usr/bin/env python3
"""
문제 데이터를 Supabase base_problems 테이블에 삽입하는 스크립트
"""

import json
import os
import requests
from dotenv import load_dotenv
from pathlib import Path

# 환경 변수 로드
load_dotenv(Path(__file__).parent.parent / '.env.local')

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}


def transform_problem(problem: dict) -> dict:
    """크롤링 데이터를 base_problems 스키마에 맞게 변환"""
    # input_output 파싱 (문자열인 경우 JSON으로 변환)
    input_output = problem.get("input_output")
    if isinstance(input_output, str):
        try:
            input_output = json.loads(input_output)
        except:
            input_output = None

    # solutions 처리 (빈 배열이면 빈 배열 유지)
    solutions = problem.get("solutions", [])
    if not solutions:
        solutions = []

    # difficulty 매핑
    difficulty = problem.get("difficulty", "medium")
    if difficulty in ["medium_hard", "very_hard"]:
        difficulty = "hard"
    elif difficulty == "unknown":
        difficulty = "medium"

    return {
        "original_id": str(problem.get("original_id", problem.get("id", ""))),
        "name": problem.get("name", problem.get("title", ""))[:255],
        "question": problem.get("question", ""),
        "input_output": input_output,
        "difficulty": difficulty,
        "tags": problem.get("tags", []),
        "source": problem.get("source", "unknown"),
        "url": problem.get("url"),
        "time_limit": problem.get("time_limit"),
        "memory_limit": problem.get("memory_limit"),
        "solutions": solutions
    }


def delete_existing():
    """기존 샘플 데이터 삭제"""
    print("기존 데이터 삭제 중...")

    # 연관 테이블 먼저 삭제
    for table in ["problems_blank", "problems_puzzle", "problems_guided"]:
        url = f"{SUPABASE_URL}/rest/v1/{table}?original_id=neq.KEEP_NONE"
        response = requests.delete(url, headers=HEADERS)
        print(f"  {table}: {response.status_code}")

    # base_problems 삭제
    url = f"{SUPABASE_URL}/rest/v1/base_problems?original_id=neq.KEEP_NONE"
    response = requests.delete(url, headers=HEADERS)
    print(f"  base_problems: {response.status_code}")


def insert_batch(problems: list, batch_size: int = 100):
    """배치로 문제 삽입"""
    url = f"{SUPABASE_URL}/rest/v1/base_problems"
    total = len(problems)
    inserted = 0
    errors = 0

    for i in range(0, total, batch_size):
        batch = problems[i:i+batch_size]
        transformed = [transform_problem(p) for p in batch]

        # 중복 original_id 제거
        seen = set()
        unique = []
        for p in transformed:
            if p["original_id"] not in seen:
                seen.add(p["original_id"])
                unique.append(p)

        try:
            # upsert 사용 (중복 시 업데이트)
            headers = {**HEADERS, "Prefer": "resolution=merge-duplicates"}
            response = requests.post(url, headers=headers, json=unique)

            if response.status_code in [200, 201]:
                inserted += len(unique)
            else:
                print(f"  Error at batch {i//batch_size}: {response.status_code}")
                print(f"  Response: {response.text[:200]}")
                errors += len(unique)
        except Exception as e:
            print(f"  Exception: {e}")
            errors += len(unique)

        print(f"  [{inserted + errors}/{total}] 삽입됨: {inserted}, 오류: {errors}")

    return inserted, errors


def main():
    print("=" * 50)
    print("문제 데이터 삽입 시작")
    print("=" * 50)

    # 1. 기존 데이터 삭제
    delete_existing()

    # 2. 백준 데이터 로드
    print("\n백준 데이터 로드 중...")
    baekjoon_path = Path(__file__).parent.parent / "data/baekjoon/checkpoint_1000_4562.json"
    with open(baekjoon_path, "r", encoding="utf-8") as f:
        baekjoon = json.load(f)
    print(f"  {len(baekjoon)}개 로드됨")

    # 3. 프로그래머스 데이터 로드
    print("\n프로그래머스 데이터 로드 중...")
    programmers_path = Path(__file__).parent.parent / "data/programmers/problems.json"
    with open(programmers_path, "r", encoding="utf-8") as f:
        programmers = json.load(f)
    print(f"  {len(programmers)}개 로드됨")

    # 4. 백준 삽입
    print("\n백준 문제 삽입 중...")
    b_inserted, b_errors = insert_batch(baekjoon)

    # 5. 프로그래머스 삽입
    print("\n프로그래머스 문제 삽입 중...")
    p_inserted, p_errors = insert_batch(programmers)

    # 6. 결과 출력
    print("\n" + "=" * 50)
    print("완료!")
    print(f"백준: {b_inserted}개 삽입, {b_errors}개 오류")
    print(f"프로그래머스: {p_inserted}개 삽입, {p_errors}개 오류")
    print(f"총: {b_inserted + p_inserted}개 삽입")
    print("=" * 50)


if __name__ == "__main__":
    main()
