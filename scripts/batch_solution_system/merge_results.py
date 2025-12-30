#!/usr/bin/env python3
"""
배치 결과 병합기 - 모든 배치 결과를 메인 파일에 안전하게 병합
"""

import json
import os
import sys
import shutil
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import MAIN_FILE, BATCH_DIR

def backup_main_file():
    """메인 파일 백업"""
    backup_file = MAIN_FILE.replace('.json', f'_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
    shutil.copy2(MAIN_FILE, backup_file)
    print(f"📦 백업 생성됨: {backup_file}")
    return backup_file

def merge_all_batches():
    """모든 배치 결과를 메인 파일에 병합"""

    # 백업
    backup_main_file()

    # 메인 데이터 로드
    with open(MAIN_FILE, 'r') as f:
        main_data = json.load(f)

    # 완료된 배치 파일들 찾기
    batch_files = [f for f in os.listdir(BATCH_DIR) if f.startswith('batch_') and f.endswith('.json')]

    if not batch_files:
        print("⚠️ 병합할 배치 파일이 없습니다.")
        return

    total_merged = 0
    merged_batches = []

    for batch_file in sorted(batch_files):
        batch_path = os.path.join(BATCH_DIR, batch_file)

        try:
            with open(batch_path, 'r') as f:
                batch_data = json.load(f)

            for result in batch_data.get('results', []):
                idx = result.get('index')
                solutions = result.get('solutions', [])

                if idx is not None and 0 <= idx < len(main_data) and solutions:
                    main_data[idx]['solutions'] = solutions
                    total_merged += 1

            merged_batches.append(batch_file)
            print(f"✅ 병합됨: {batch_file}")

        except (json.JSONDecodeError, KeyError) as e:
            print(f"⚠️ 오류 발생 ({batch_file}): {e}")

    # 저장
    with open(MAIN_FILE, 'w', encoding='utf-8') as f:
        json.dump(main_data, f, ensure_ascii=False, indent=2)

    print(f"\n🎉 병합 완료!")
    print(f"   - 총 {total_merged}개 솔루션 병합됨")
    print(f"   - {len(merged_batches)}개 배치 파일 처리됨")

    # 처리된 배치 파일 이동
    merged_dir = os.path.join(BATCH_DIR, "merged")
    os.makedirs(merged_dir, exist_ok=True)

    for batch_file in merged_batches:
        src = os.path.join(BATCH_DIR, batch_file)
        dst = os.path.join(merged_dir, batch_file)
        shutil.move(src, dst)

    print(f"   - 배치 파일들 {merged_dir}로 이동됨")

def verify_solutions():
    """솔루션 상태 검증"""
    with open(MAIN_FILE, 'r') as f:
        data = json.load(f)

    empty_count = 0
    filled_count = 0

    for problem in data:
        solutions = problem.get('solutions', [])
        has_real = any(len(s.get('code', '').strip()) > 50 for s in solutions)

        if has_real:
            filled_count += 1
        else:
            empty_count += 1

    print(f"\n📊 솔루션 상태:")
    print(f"   - 전체 문제: {len(data)}")
    print(f"   - 솔루션 있음: {filled_count}")
    print(f"   - 솔루션 없음: {empty_count}")
    print(f"   - 완성률: {(filled_count/len(data)*100):.1f}%")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "verify":
        verify_solutions()
    else:
        merge_all_batches()
        verify_solutions()
