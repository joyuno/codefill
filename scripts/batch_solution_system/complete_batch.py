#!/usr/bin/env python3
"""
배치 완료 처리 스크립트

사용법:
  python3 complete_batch.py <worker_id>

pending_{worker_id}.json 파일을 읽어서
- 솔루션이 채워져 있으면 메인 파일에 병합
- 완료 상태로 마킹
"""

import json
import os
import sys
import shutil
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import MAIN_FILE, BATCH_DIR
from lock_manager import LockManager

def complete_batch(worker_id: str):
    pending_file = os.path.join(BATCH_DIR, f"pending_{worker_id}.json")

    if not os.path.exists(pending_file):
        print(f"❌ 파일을 찾을 수 없습니다: {pending_file}")
        return False

    with open(pending_file, 'r') as f:
        batch_data = json.load(f)

    # 솔루션이 채워졌는지 확인
    results = batch_data.get('results', [])
    valid_count = 0

    for result in results:
        solutions = result.get('solutions', [])
        if solutions and any(len(s.get('code', '').strip()) > 30 for s in solutions):
            valid_count += 1

    if valid_count == 0:
        print(f"⚠️ 아직 솔루션이 채워지지 않았습니다.")
        print(f"   pending 파일을 먼저 수정해주세요: {pending_file}")
        return False

    print(f"✅ {valid_count}개 문제의 솔루션 확인됨")

    # 메인 파일에 병합
    with open(MAIN_FILE, 'r') as f:
        main_data = json.load(f)

    indices = []
    merged_count = 0

    for result in results:
        idx = result.get('index')
        solutions = result.get('solutions', [])

        if idx is not None and 0 <= idx < len(main_data) and solutions:
            # 유효한 솔루션만 저장
            valid_solutions = [s for s in solutions if len(s.get('code', '').strip()) > 30]
            if valid_solutions:
                main_data[idx]['solutions'] = valid_solutions
                indices.append(idx)
                merged_count += 1

    with open(MAIN_FILE, 'w', encoding='utf-8') as f:
        json.dump(main_data, f, ensure_ascii=False, indent=2)

    # 완료 처리
    lock_manager = LockManager(worker_id)
    lock_manager.mark_completed(indices)

    # 완료된 배치 파일 이동
    merged_dir = os.path.join(BATCH_DIR, "merged")
    os.makedirs(merged_dir, exist_ok=True)

    completed_file = os.path.join(merged_dir, f"batch_{worker_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    shutil.move(pending_file, completed_file)

    print(f"✅ {merged_count}개 솔루션이 메인 파일에 병합되었습니다!")
    print(f"📁 완료된 배치: {completed_file}")

    # 현재 상태 출력
    status = lock_manager.get_status()
    print(f"\n📊 현재 진행 상황:")
    print(f"   완료: {status['completed']} / {status['total_empty']}")
    print(f"   남은 작업: {status['remaining']}")
    if status['total_empty'] > 0:
        progress = (status['completed'] / status['total_empty']) * 100
        print(f"   진행률: {progress:.1f}%")

    if status['remaining'] > 0:
        print(f"\n🔄 다음 배치를 시작하려면:")
        print(f"   python3 process_batch.py")

    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python3 complete_batch.py <worker_id>")
        sys.exit(1)

    worker_id = sys.argv[1]
    complete_batch(worker_id)
