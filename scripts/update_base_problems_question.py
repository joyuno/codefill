#!/usr/bin/env python3
"""
Supabase base_problems 테이블의 question 필드를
KaTeX 마크다운으로 업데이트하는 스크립트

validated_problems_latex.json의 변환된 question을
original_id로 매칭하여 DB에 반영
"""

import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client

# 환경변수 로드
load_dotenv(Path(__file__).parent.parent / "backend" / ".env")

# 경로 설정
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data" / "baekjoon" / "data_baekjoon"
INPUT_FILE = DATA_DIR / "validated_problems_latex.json"

# Supabase 설정
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# 배치 크기
BATCH_SIZE = 100


def get_supabase_client() -> Client:
    """Supabase 클라이언트 생성"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("SUPABASE_URL 또는 SUPABASE_SERVICE_ROLE_KEY가 설정되지 않았습니다.")
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def extract_original_id(problem_id: str) -> str:
    """baekjoon_10006 형식에서 원본 ID 추출"""
    # baekjoon_10006 → 10006 (숫자만 추출)
    if problem_id.startswith("baekjoon_"):
        return problem_id.replace("baekjoon_", "")
    return problem_id


def main():
    print("=" * 60)
    print("Supabase base_problems.question 업데이트")
    print("=" * 60)

    # 1. 변환된 데이터 로드
    print("\n[1] 변환된 데이터 로드...")
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        problems = json.load(f)
    print(f"  총 {len(problems)}개 문제")

    # 2. Supabase 연결
    print("\n[2] Supabase 연결...")
    supabase = get_supabase_client()
    print("  연결 성공")

    # 3. 배치 업데이트
    print(f"\n[3] 업데이트 시작 (배치 크기: {BATCH_SIZE})...")

    success_count = 0
    error_count = 0
    not_found_count = 0

    for i in range(0, len(problems), BATCH_SIZE):
        batch = problems[i:i + BATCH_SIZE]
        batch_num = i // BATCH_SIZE + 1
        total_batches = (len(problems) + BATCH_SIZE - 1) // BATCH_SIZE

        for p in batch:
            original_id = extract_original_id(p['id'])
            question = p.get('question', '')

            if not question:
                continue

            try:
                # original_id로 매칭하여 업데이트
                result = supabase.table("base_problems").update({
                    "question": question
                }).eq("original_id", original_id).execute()

                if result.data:
                    success_count += 1
                else:
                    not_found_count += 1

            except Exception as e:
                error_count += 1
                if error_count <= 5:  # 처음 5개 에러만 출력
                    print(f"  [ERROR] {original_id}: {e}")

        print(f"  배치 {batch_num}/{total_batches} 완료 (성공: {success_count}, 미발견: {not_found_count}, 에러: {error_count})")

    # 4. 결과 출력
    print("\n" + "=" * 60)
    print("결과 요약")
    print("=" * 60)
    print(f"  성공: {success_count}개")
    print(f"  미발견: {not_found_count}개")
    print(f"  에러: {error_count}개")
    print(f"  총계: {len(problems)}개")

    return success_count > 0


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n오류 발생: {e}")
        sys.exit(1)
