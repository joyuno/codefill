#!/usr/bin/env python3
"""
데이터셋 통합 스크립트
Baekjoon + TACO → Unified Schema
"""

import json
import re
from pathlib import Path
from typing import Optional

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data'
OUTPUT_DIR = DATA_DIR / 'unified'


# ============================================================
# Unified Schema Definition
# ============================================================
"""
unified_schema = {
    # 필수 (공통)
    "question": str,           # 문제 설명
    "solutions": list[str],    # 정답 코드들
    "input_output": str,       # 테스트 케이스 (JSON string)
    "difficulty": str,         # 난이도 (정규화: easy, medium, hard)
    "tags": list[str],         # 알고리즘 태그
    "name": str,               # 문제 제목
    "source": str,             # 출처 (taco, baekjoon)
    "url": str,                # 원본 링크

    # 선택 (있으면 좋음)
    "starter_code": str,       # 시작 코드
    "explanation": str,        # 풀이 설명
    "language": str,           # 언어
    "time_limit": str,
    "memory_limit": str,

    # 메타
    "original_id": str,        # 원본 ID
}
"""


# ============================================================
# Difficulty Normalization
# ============================================================
def normalize_difficulty(difficulty: str) -> str:
    """난이도를 통합 형식으로 정규화"""
    if not difficulty:
        return "unknown"

    d = difficulty.lower().strip()

    # Baekjoon 형식
    if d in ['bronze', 'silver', 'easy']:
        return 'easy'
    if d in ['gold', 'medium']:
        return 'medium'
    if d in ['platinum', 'diamond', 'ruby', 'hard']:
        return 'hard'

    # TACO 형식
    if d == 'easy':
        return 'easy'
    if d == 'medium':
        return 'medium'
    if d == 'medium_hard':
        return 'medium_hard'
    if d == 'hard':
        return 'hard'
    if d == 'very_hard':
        return 'very_hard'
    if d == 'unknown_difficulty':
        return 'unknown'

    return d


# ============================================================
# Baekjoon → Unified
# ============================================================
def convert_baekjoon_to_unified(row: dict) -> dict:
    """백준 데이터를 통합 스키마로 변환"""
    q = row.get('question', {})
    a = row.get('answer', {})

    # 문제 설명 조합
    description = q.get('description', '')
    input_format = q.get('input_format', '')
    output_format = q.get('output_format', '')

    question_text = description
    if input_format:
        question_text += f"\n\n### 입력\n{input_format}"
    if output_format:
        question_text += f"\n\n### 출력\n{output_format}"

    # 제약조건 추가
    constraints = q.get('constraints')
    if constraints:
        question_text += f"\n\n### 제한\n{constraints}"

    # input_output 처리
    examples = q.get('examples', [])
    input_output = json.dumps(examples, ensure_ascii=False) if examples else "[]"

    # 태그 처리
    tags = row.get('tags', [])
    if not tags:
        algo_cat = row.get('algorithm_category')
        tags = [algo_cat] if algo_cat else []

    return {
        # 필수
        "question": question_text,
        "solutions": [a.get('code', '')] if a.get('code') else [],
        "input_output": input_output,
        "difficulty": normalize_difficulty(row.get('difficulty', '')),
        "tags": tags if isinstance(tags, list) else [tags],
        "name": q.get('title', ''),
        "source": "baekjoon",
        "url": q.get('external_link', ''),

        # 선택
        "starter_code": None,
        "explanation": a.get('explanation'),
        "language": row.get('language', ''),
        "time_limit": None,
        "memory_limit": None,

        # 메타
        "original_id": str(row.get('original_id', '')),
    }


# ============================================================
# TACO → Unified
# ============================================================
def convert_taco_to_unified(row: dict) -> dict:
    """TACO 데이터를 통합 스키마로 변환"""

    # input_output 처리
    io = row.get('input_output')
    if isinstance(io, dict):
        input_output = json.dumps(io, ensure_ascii=False)
    elif isinstance(io, str):
        input_output = io
    else:
        input_output = "[]"

    # 태그 처리
    tags = row.get('tags', []) or row.get('raw_tags', []) or []

    # 제목 추출 (name이 없으면 URL에서 추출)
    name = row.get('name')
    if not name:
        url = row.get('url', '')
        # URL에서 문제 ID 추출 시도
        if 'codeforces' in url:
            match = re.search(r'/problem/(\d+)/(\w+)', url)
            if match:
                name = f"CF {match.group(1)}{match.group(2)}"
        elif 'leetcode' in url:
            match = re.search(r'/problems/([^/]+)', url)
            if match:
                name = match.group(1).replace('-', ' ').title()

        if not name:
            name = f"Problem from {row.get('source', 'unknown')}"

    # original_id 추출
    url = row.get('url', '')
    original_id = None
    if 'codeforces' in url:
        match = re.search(r'/problem/(\d+)/(\w+)', url)
        if match:
            original_id = f"{match.group(1)}{match.group(2)}"
    elif 'leetcode' in url:
        match = re.search(r'/problems/([^/]+)', url)
        if match:
            original_id = match.group(1)
    elif url:
        # 마지막 path segment 사용
        original_id = url.rstrip('/').split('/')[-1]

    # solutions 처리
    solutions = row.get('solutions', [])
    if not isinstance(solutions, list):
        solutions = [solutions] if solutions else []

    return {
        # 필수
        "question": row.get('question', ''),
        "solutions": solutions,
        "input_output": input_output,
        "difficulty": normalize_difficulty(row.get('difficulty', '')),
        "tags": tags if isinstance(tags, list) else [tags],
        "name": name,
        "source": row.get('source', 'taco'),
        "url": row.get('url', ''),

        # 선택
        "starter_code": row.get('starter_code'),
        "explanation": None,
        "language": "python",  # TACO는 다국어
        "time_limit": row.get('time_limit'),
        "memory_limit": row.get('memory_limit'),

        # 메타
        "original_id": original_id or '',
    }


# ============================================================
# Main Conversion Functions
# ============================================================
def convert_baekjoon_dataset():
    """백준 데이터셋 전체 변환"""
    print("=" * 60)
    print("Converting Baekjoon Dataset")
    print("=" * 60)

    input_path = DATA_DIR / '1_algorithm' / 'baekjoon_with_answer.json'

    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"  - Loaded {len(data)} records")

    unified = []
    for row in data:
        try:
            converted = convert_baekjoon_to_unified(row)
            unified.append(converted)
        except Exception as e:
            print(f"  ✗ Error converting {row.get('original_id')}: {e}")

    print(f"  - Converted {len(unified)} records")
    return unified


def convert_taco_dataset(limit: Optional[int] = None):
    """TACO 데이터셋 변환 (by_difficulty 폴더 사용)"""
    print("=" * 60)
    print("Converting TACO Dataset")
    print("=" * 60)

    unified = []
    difficulty_dir = DATA_DIR / 'taco' / 'by_difficulty'

    # 각 난이도별 파일 처리
    for difficulty_file in difficulty_dir.glob('*.json'):
        print(f"  - Loading {difficulty_file.name}...")

        try:
            with open(difficulty_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for row in data:
                if limit and len(unified) >= limit:
                    break

                try:
                    converted = convert_taco_to_unified(row)
                    unified.append(converted)
                except Exception as e:
                    pass  # Skip failed records

            print(f"    - Total so far: {len(unified)}")

            if limit and len(unified) >= limit:
                break
        except Exception as e:
            print(f"    ✗ Error loading {difficulty_file.name}: {e}")

    print(f"  - Converted {len(unified)} records")
    return unified


def main():
    print("\n" + "=" * 60)
    print("Dataset Unification Tool")
    print("=" * 60)

    OUTPUT_DIR.mkdir(exist_ok=True)

    # 1. 백준 변환
    baekjoon_unified = convert_baekjoon_dataset()

    baekjoon_path = OUTPUT_DIR / 'baekjoon_unified.json'
    with open(baekjoon_path, 'w', encoding='utf-8') as f:
        json.dump(baekjoon_unified, f, ensure_ascii=False, indent=2)
    print(f"  - Saved to: {baekjoon_path}")

    # 2. TACO 변환 (샘플 100개만 - 빠른 테스트용)
    taco_unified = convert_taco_dataset(limit=100)

    taco_path = OUTPUT_DIR / 'taco_unified_sample.json'
    with open(taco_path, 'w', encoding='utf-8') as f:
        json.dump(taco_unified, f, ensure_ascii=False, indent=2)
    print(f"  - Saved to: {taco_path}")

    # 3. 통합 데이터셋 생성
    all_unified = baekjoon_unified + taco_unified

    all_path = OUTPUT_DIR / 'all_unified.json'
    with open(all_path, 'w', encoding='utf-8') as f:
        json.dump(all_unified, f, ensure_ascii=False, indent=2)
    print(f"  - Saved to: {all_path}")

    # 통계
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"  Baekjoon: {len(baekjoon_unified)} problems")
    print(f"  TACO (sample): {len(taco_unified)} problems")
    print(f"  Total: {len(all_unified)} problems")

    # 난이도 분포
    print("\n  Difficulty Distribution:")
    diff_counts = {}
    for item in all_unified:
        d = item['difficulty']
        diff_counts[d] = diff_counts.get(d, 0) + 1
    for d, c in sorted(diff_counts.items()):
        print(f"    - {d}: {c}")

    # 출처 분포
    print("\n  Source Distribution:")
    source_counts = {}
    for item in all_unified:
        s = item['source']
        source_counts[s] = source_counts.get(s, 0) + 1
    for s, c in sorted(source_counts.items(), key=lambda x: -x[1]):
        print(f"    - {s}: {c}")


if __name__ == "__main__":
    main()
