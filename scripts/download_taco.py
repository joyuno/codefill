#!/usr/bin/env python3
"""
TACO Dataset Downloader

Hugging Face에서 BAAI/TACO 데이터셋을 다운로드하여 로컬에 저장합니다.
huggingface_hub를 사용하여 직접 파일을 다운로드합니다.
"""

import os
import json
from huggingface_hub import hf_hub_download, list_repo_files

# 저장 경로
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'taco')
os.makedirs(DATA_DIR, exist_ok=True)

REPO_ID = "BAAI/TACO"

def download_and_save():
    print("=" * 60)
    print("TACO Dataset Downloader (via huggingface_hub)")
    print("=" * 60)

    # 레포지토리 파일 목록 확인
    print("\n[1/3] Listing repository files...")
    try:
        files = list_repo_files(REPO_ID, repo_type="dataset")
        print(f"  - Found {len(files)} files")

        # 데이터 파일 필터링
        data_files = [f for f in files if f.endswith('.jsonl') or f.endswith('.json') or f.endswith('.parquet')]
        print(f"  - Data files: {data_files[:10]}...")  # 처음 10개만 표시
    except Exception as e:
        print(f"  - Error listing files: {e}")
        data_files = []

    # 파일 다운로드
    print("\n[2/3] Downloading data files...")
    downloaded_files = []

    # 일반적인 데이터 파일 패턴 시도
    patterns = [
        "data/train.jsonl",
        "data/test.jsonl",
        "train.jsonl",
        "test.jsonl",
        "data/train-00000-of-00001.parquet",
        "data/test-00000-of-00001.parquet",
    ]

    for pattern in patterns:
        try:
            print(f"  - Trying to download: {pattern}")
            local_path = hf_hub_download(
                repo_id=REPO_ID,
                filename=pattern,
                repo_type="dataset",
                local_dir=DATA_DIR,
            )
            downloaded_files.append(local_path)
            print(f"    ✓ Downloaded: {local_path}")
        except Exception as e:
            print(f"    ✗ Not found or error: {str(e)[:50]}")

    # 실제 파일 목록에서 다운로드
    if data_files:
        for filename in data_files:
            if filename in patterns:
                continue  # 이미 시도함
            try:
                print(f"  - Downloading: {filename}")
                local_path = hf_hub_download(
                    repo_id=REPO_ID,
                    filename=filename,
                    repo_type="dataset",
                    local_dir=DATA_DIR,
                )
                downloaded_files.append(local_path)
                print(f"    ✓ Downloaded: {local_path}")
            except Exception as e:
                print(f"    ✗ Error: {str(e)[:50]}")

    # 완료 메시지
    print("\n[3/3] Summary")
    print("=" * 60)
    print(f"Downloaded {len(downloaded_files)} files to: {DATA_DIR}/")
    for f in downloaded_files:
        print(f"  - {f}")

    return downloaded_files

if __name__ == "__main__":
    download_and_save()
