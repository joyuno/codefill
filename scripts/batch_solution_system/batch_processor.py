#!/usr/bin/env python3
"""
배치 프로세서 - Claude Code에서 직접 실행
이 스크립트는 Claude Code가 직접 솔루션을 생성하여 채우도록 설계됨
"""

import json
import os
import sys
import uuid
from datetime import datetime

# 현재 디렉토리를 path에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import MAIN_FILE, BATCH_DIR, BATCH_SIZE
from lock_manager import LockManager
from solution_generator import format_solutions_for_storage

def get_problems_for_batch(indices: list[int]) -> list[dict]:
    """지정된 인덱스의 문제들 로드"""
    with open(MAIN_FILE, 'r') as f:
        data = json.load(f)

    problems = []
    for idx in indices:
        if 0 <= idx < len(data):
            problem = data[idx].copy()
            problem['_index'] = idx
            problems.append(problem)

    return problems

def save_batch_result(batch_id: str, results: list[dict]):
    """배치 결과를 파일로 저장"""
    output_file = os.path.join(BATCH_DIR, f"batch_{batch_id}.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "batch_id": batch_id,
            "created_at": datetime.now().isoformat(),
            "results": results
        }, f, ensure_ascii=False, indent=2)
    return output_file

def apply_batch_to_main(batch_file: str):
    """배치 결과를 메인 파일에 적용"""
    with open(batch_file, 'r') as f:
        batch_data = json.load(f)

    with open(MAIN_FILE, 'r') as f:
        main_data = json.load(f)

    for result in batch_data['results']:
        idx = result['index']
        solutions = result['solutions']

        if 0 <= idx < len(main_data) and solutions:
            main_data[idx]['solutions'] = solutions

    with open(MAIN_FILE, 'w', encoding='utf-8') as f:
        json.dump(main_data, f, ensure_ascii=False, indent=2)

    print(f"✅ Applied {len(batch_data['results'])} solutions to main file")

def get_next_batch_info():
    """다음 배치 정보 출력 (Claude Code가 이를 읽고 처리)"""
    worker_id = str(uuid.uuid4())[:8]
    lock_manager = LockManager(worker_id)

    result = lock_manager.get_next_batch()

    if result is None:
        print("⏳ 다른 워커가 처리 중입니다. 잠시 후 다시 시도하세요.")
        return None

    if result == (-1, -1):
        print("✅ 모든 솔루션 생성이 완료되었습니다!")
        return None

    start_idx, end_idx, indices = result
    problems = get_problems_for_batch(indices)

    print(f"📋 배치 할당됨: Worker {worker_id}")
    print(f"   인덱스: {indices}")
    print(f"   문제 수: {len(problems)}")

    return {
        "worker_id": worker_id,
        "indices": indices,
        "problems": problems
    }

def print_status():
    """현재 진행 상황 출력"""
    worker_id = "status_check"
    lock_manager = LockManager(worker_id)
    status = lock_manager.get_status()

    print("\n📊 솔루션 생성 진행 상황:")
    print(f"   전체 빈 솔루션: {status['total_empty']}")
    print(f"   완료: {status['completed']}")
    print(f"   진행 중: {status['in_progress']}")
    print(f"   남은 작업: {status['remaining']}")

    if status['total_empty'] > 0:
        progress = (status['completed'] / status['total_empty']) * 100
        print(f"   진행률: {progress:.1f}%")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "status":
            print_status()
        elif sys.argv[1] == "next":
            batch_info = get_next_batch_info()
            if batch_info:
                # 문제 정보 JSON으로 출력
                output_file = os.path.join(BATCH_DIR, f"pending_{batch_info['worker_id']}.json")
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(batch_info, f, ensure_ascii=False, indent=2)
                print(f"\n📁 처리할 문제 저장됨: {output_file}")
        elif sys.argv[1] == "apply" and len(sys.argv) > 2:
            apply_batch_to_main(sys.argv[2])
    else:
        print("사용법:")
        print("  python batch_processor.py status  - 진행 상황 확인")
        print("  python batch_processor.py next    - 다음 배치 가져오기")
        print("  python batch_processor.py apply <batch_file>  - 배치 결과 적용")
