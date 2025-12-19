#!/usr/bin/env python3
"""
TACO Dataset Converter

Parquet 파일을 JSON으로 변환하고 난이도별로 정리합니다.
"""

import os
import json
import pandas as pd
import numpy as np
from pathlib import Path

# 경로 설정
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data' / 'taco'
OUTPUT_DIR = DATA_DIR

def is_null(value):
    """값이 null인지 확인합니다."""
    if value is None:
        return True
    if isinstance(value, float) and np.isnan(value):
        return True
    if isinstance(value, (list, np.ndarray)) and len(value) == 0:
        return True
    return False

def parse_json_field(value):
    """JSON 문자열 필드를 파싱합니다."""
    if is_null(value):
        return None
    if isinstance(value, str):
        try:
            return json.loads(value)
        except:
            try:
                return eval(value)
            except:
                return value
    if isinstance(value, np.ndarray):
        return value.tolist()
    return value

def clean_value(value):
    """값을 JSON 직렬화 가능한 형태로 정리합니다."""
    if is_null(value):
        return None
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, (np.integer, np.int64)):
        return int(value)
    if isinstance(value, (np.floating, np.float64)):
        return float(value) if not np.isnan(value) else None
    if isinstance(value, bytes):
        return value.decode('utf-8', errors='ignore')
    return value

def convert_parquet_to_json():
    print("=" * 60)
    print("TACO Dataset Converter")
    print("=" * 60)

    # Train 파일 병합
    print("\n[1/4] Loading train parquet files...")
    train_files = sorted(DATA_DIR.glob("ALL/train-*.parquet"))
    print(f"  - Found {len(train_files)} train files")

    train_dfs = []
    for f in train_files:
        df = pd.read_parquet(f)
        train_dfs.append(df)
        print(f"    - {f.name}: {len(df)} rows")

    train_df = pd.concat(train_dfs, ignore_index=True)
    print(f"  - Total train samples: {len(train_df)}")

    # Test 파일 로드
    print("\n[2/4] Loading test parquet files...")
    test_files = sorted(DATA_DIR.glob("ALL/test-*.parquet"))
    test_df = pd.read_parquet(test_files[0]) if test_files else pd.DataFrame()
    print(f"  - Total test samples: {len(test_df)}")

    # 데이터 변환
    print("\n[3/4] Converting to JSON format...")

    def row_to_dict(row):
        """DataFrame 행을 딕셔너리로 변환합니다."""
        d = {}
        for key, value in row.items():
            # JSON 필드 파싱
            if key in ['solutions', 'input_output', 'raw_tags', 'tags', 'skill_types']:
                d[key] = parse_json_field(value)
            else:
                d[key] = clean_value(value)
        return d

    # Train 데이터 변환
    train_data = []
    for i, (_, row) in enumerate(train_df.iterrows()):
        train_data.append(row_to_dict(row))
        if (i + 1) % 5000 == 0:
            print(f"    - Processed {i + 1}/{len(train_df)} train samples")
    print(f"  - Converted {len(train_data)} train samples")

    # Test 데이터 변환
    test_data = [row_to_dict(row) for _, row in test_df.iterrows()]
    print(f"  - Converted {len(test_data)} test samples")

    # 파일 저장
    print("\n[4/4] Saving files...")

    # Train JSON 저장
    train_path = OUTPUT_DIR / 'train.json'
    with open(train_path, 'w', encoding='utf-8') as f:
        json.dump(train_data, f, ensure_ascii=False)
    print(f"  - Saved: {train_path} ({os.path.getsize(train_path) / 1024 / 1024:.1f} MB)")

    # Test JSON 저장
    test_path = OUTPUT_DIR / 'test.json'
    with open(test_path, 'w', encoding='utf-8') as f:
        json.dump(test_data, f, ensure_ascii=False)
    print(f"  - Saved: {test_path} ({os.path.getsize(test_path) / 1024 / 1024:.1f} MB)")

    # 난이도별 분류
    print("\n  - Creating difficulty-based splits...")
    difficulty_dir = OUTPUT_DIR / 'by_difficulty'
    difficulty_dir.mkdir(exist_ok=True)

    all_data = train_data + test_data
    difficulty_counts = {}

    for sample in all_data:
        diff = sample.get('difficulty') or 'UNKNOWN'
        if diff not in difficulty_counts:
            difficulty_counts[diff] = []
        difficulty_counts[diff].append(sample)

    for diff, samples in difficulty_counts.items():
        diff_path = difficulty_dir / f'{diff.lower()}.json'
        with open(diff_path, 'w', encoding='utf-8') as f:
            json.dump(samples, f, ensure_ascii=False)
        print(f"    - {diff}: {len(samples)} samples")

    # 통계 저장
    stats = {
        "dataset": "BAAI/TACO",
        "description": "Topics in Algorithmic COde generation benchmark",
        "train_samples": len(train_data),
        "test_samples": len(test_data),
        "total_samples": len(all_data),
        "difficulty_distribution": {k: len(v) for k, v in difficulty_counts.items()},
        "fields": list(train_data[0].keys()) if train_data else [],
        "sources": list(set(str(s.get('source')) for s in all_data if s.get('source'))),
    }

    stats_path = OUTPUT_DIR / 'stats.json'
    with open(stats_path, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    print(f"  - Saved: {stats_path}")

    # 완료 메시지
    print("\n" + "=" * 60)
    print("Conversion Complete!")
    print("=" * 60)
    print(f"\nTotal: {stats['total_samples']} problems")
    print(f"  - Train: {stats['train_samples']}")
    print(f"  - Test: {stats['test_samples']}")
    print(f"\nDifficulty distribution:")
    for diff, count in sorted(stats['difficulty_distribution'].items()):
        print(f"  - {diff}: {count}")
    print(f"\nSources: {len(stats['sources'])} platforms")
    print(f"\nFiles saved to: {OUTPUT_DIR}/")

if __name__ == "__main__":
    convert_parquet_to_json()
