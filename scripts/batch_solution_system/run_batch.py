#!/usr/bin/env python3
"""
단일 배치 실행 스크립트
Claude Code가 이 스크립트를 실행하면:
1. 다음 배치를 자동으로 가져옴
2. 각 문제 정보를 출력
3. Claude Code가 솔루션을 생성하면 저장
4. 메인 파일에 병합

사용법:
  python3 run_batch.py         # 다음 배치 정보 출력
  python3 run_batch.py save    # 솔루션 저장 (인터랙티브)
"""

import json
import os
import sys
import uuid
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import MAIN_FILE, BATCH_DIR
from lock_manager import LockManager

def get_and_print_next_batch():
    """다음 배치를 가져와서 문제 정보를 출력"""
    worker_id = str(uuid.uuid4())[:8]
    lock_manager = LockManager(worker_id)

    result = lock_manager.get_next_batch()

    if result is None:
        print("⏳ 진행 중인 배치가 있습니다. 완료 후 다시 시도하세요.")
        return None

    if result == (-1, -1):
        print("🎉 모든 솔루션이 완성되었습니다!")
        return None

    start_idx, end_idx, indices = result

    # 문제 로드
    with open(MAIN_FILE, 'r') as f:
        data = json.load(f)

    print(f"\n{'='*60}")
    print(f"📋 배치 Worker ID: {worker_id}")
    print(f"📋 처리할 인덱스: {indices}")
    print(f"{'='*60}\n")

    batch_info = {
        "worker_id": worker_id,
        "indices": indices,
        "problems": []
    }

    for idx in indices:
        problem = data[idx]
        problem_id = problem.get('original_id', problem.get('id', 'unknown'))
        name = problem.get('name', f'문제 {problem_id}')

        print(f"\n{'─'*50}")
        print(f"📌 [{idx}] {name} (백준 {problem_id})")
        print(f"{'─'*50}")

        question = problem.get('question', '')[:500]
        if not question:
            question = problem.get('question_html', '')[:500]
            import re
            question = re.sub(r'<[^>]+>', '', question)

        print(f"문제: {question}...")

        io = problem.get('input_output', '{}')
        if isinstance(io, str):
            try:
                io_data = json.loads(io)
            except:
                io_data = {}
        else:
            io_data = io

        inputs = io_data.get('inputs', [])[:2]
        outputs = io_data.get('outputs', [])[:2]

        if inputs and outputs:
            print(f"\n예제:")
            for i, (inp, out) in enumerate(zip(inputs, outputs)):
                print(f"  입력 {i+1}: {inp[:100]}...")
                print(f"  출력 {i+1}: {out[:100]}...")

        batch_info["problems"].append({
            "index": idx,
            "problem_id": problem_id,
            "name": name,
            "question": problem.get('question', ''),
            "input_output": io_data,
            "difficulty": problem.get('difficulty', ''),
            "time_limit": problem.get('time_limit', ''),
            "memory_limit": problem.get('memory_limit', '')
        })

    # pending 파일 저장
    pending_file = os.path.join(BATCH_DIR, f"pending_{worker_id}.json")
    with open(pending_file, 'w', encoding='utf-8') as f:
        json.dump(batch_info, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*60}")
    print(f"💾 배치 정보 저장됨: {pending_file}")
    print(f"\n다음 단계:")
    print(f"  1. 위 각 문제에 대해 Python, Java, C++ 솔루션을 생성하세요")
    print(f"  2. 솔루션을 batch_{worker_id}.json 파일로 저장하세요")
    print(f"  3. 다음 명령으로 병합: python3 run_batch.py merge {worker_id}")
    print(f"{'='*60}\n")

    return batch_info

def save_solutions_for_batch(worker_id: str, solutions_by_index: dict):
    """
    솔루션을 배치 결과 파일로 저장

    Args:
        worker_id: 워커 ID
        solutions_by_index: {인덱스: {"python": 코드, "java": 코드, "cpp": 코드}}
    """
    results = []

    for idx, sols in solutions_by_index.items():
        solution_list = []
        for lang in ['python', 'java', 'cpp']:
            if lang in sols and sols[lang]:
                solution_list.append({
                    "language": lang,
                    "code": sols[lang]
                })

        results.append({
            "index": int(idx),
            "solutions": solution_list
        })

    batch_file = os.path.join(BATCH_DIR, f"batch_{worker_id}.json")
    with open(batch_file, 'w', encoding='utf-8') as f:
        json.dump({
            "batch_id": worker_id,
            "created_at": datetime.now().isoformat(),
            "results": results
        }, f, ensure_ascii=False, indent=2)

    print(f"✅ 배치 결과 저장됨: {batch_file}")
    return batch_file

def merge_batch(worker_id: str):
    """배치 결과를 메인 파일에 병합"""
    batch_file = os.path.join(BATCH_DIR, f"batch_{worker_id}.json")

    if not os.path.exists(batch_file):
        print(f"❌ 배치 파일을 찾을 수 없습니다: {batch_file}")
        return False

    with open(batch_file, 'r') as f:
        batch_data = json.load(f)

    with open(MAIN_FILE, 'r') as f:
        main_data = json.load(f)

    merged_count = 0
    indices = []

    for result in batch_data.get('results', []):
        idx = result.get('index')
        solutions = result.get('solutions', [])

        if idx is not None and 0 <= idx < len(main_data) and solutions:
            main_data[idx]['solutions'] = solutions
            merged_count += 1
            indices.append(idx)

    with open(MAIN_FILE, 'w', encoding='utf-8') as f:
        json.dump(main_data, f, ensure_ascii=False, indent=2)

    # 완료 처리
    lock_manager = LockManager(worker_id)
    lock_manager.mark_completed(indices)

    # pending 파일 삭제
    pending_file = os.path.join(BATCH_DIR, f"pending_{worker_id}.json")
    if os.path.exists(pending_file):
        os.remove(pending_file)

    # 배치 파일 이동
    merged_dir = os.path.join(BATCH_DIR, "merged")
    os.makedirs(merged_dir, exist_ok=True)

    import shutil
    shutil.move(batch_file, os.path.join(merged_dir, f"batch_{worker_id}.json"))

    print(f"✅ {merged_count}개 솔루션이 메인 파일에 병합되었습니다!")

    # 현재 상태 출력
    status = lock_manager.get_status()
    print(f"\n📊 현재 진행 상황:")
    print(f"   완료: {status['completed']} / {status['total_empty']}")
    print(f"   남은 작업: {status['remaining']}")

    return True

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "merge" and len(sys.argv) > 2:
            merge_batch(sys.argv[2])
        elif sys.argv[1] == "status":
            worker_id = "status"
            lock_manager = LockManager(worker_id)
            status = lock_manager.get_status()
            print(f"\n📊 솔루션 생성 진행 상황:")
            print(f"   전체 빈 솔루션: {status['total_empty']}")
            print(f"   완료: {status['completed']}")
            print(f"   진행 중: {status['in_progress']}")
            print(f"   남은 작업: {status['remaining']}")
            if status['total_empty'] > 0:
                progress = (status['completed'] / status['total_empty']) * 100
                print(f"   진행률: {progress:.1f}%")
    else:
        get_and_print_next_batch()
