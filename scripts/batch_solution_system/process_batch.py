#!/usr/bin/env python3
"""
Claude Code 무한 재귀 배치 처리 스크립트

이 파일은 Claude Code가 읽고 실행할 수 있도록 설계되었습니다.
각 실행에서:
1. 다음 배치를 가져옴
2. 각 문제의 솔루션을 출력 형식으로 요청
3. 결과를 저장하고 병합

Claude Code에서 실행:
  python3 process_batch.py

그 후 Claude Code에게:
"위 문제들의 Python, Java, C++ 솔루션을 생성하고 저장해줘"
"""

import json
import os
import sys
import uuid
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import MAIN_FILE, BATCH_DIR
from lock_manager import LockManager

def main():
    worker_id = str(uuid.uuid4())[:8]
    lock_manager = LockManager(worker_id)

    # 상태 확인
    status = lock_manager.get_status()

    if status['total_empty'] == 0:
        # 첫 실행 - empty_indices 수집
        result = lock_manager.get_next_batch()
    else:
        result = lock_manager.get_next_batch()

    if result is None:
        print("⏳ 진행 중인 배치가 있습니다.")
        print("   진행 중인 워커의 작업이 완료될 때까지 대기하거나,")
        print("   locks/ 폴더의 worker_*.lock 파일을 삭제하세요.")
        return

    if result == (-1, -1):
        print("🎉 모든 솔루션이 완성되었습니다!")
        final_status = lock_manager.get_status()
        print(f"   총 {final_status['completed']}개 완료")
        return

    start_idx, end_idx, indices = result

    # 문제 로드
    with open(MAIN_FILE, 'r') as f:
        data = json.load(f)

    print(f"=" * 70)
    print(f"🚀 배치 시작 - Worker: {worker_id}")
    print(f"   인덱스: {indices}")
    print(f"=" * 70)

    # 저장할 결과 구조
    results_template = {
        "batch_id": worker_id,
        "indices": indices,
        "results": []
    }

    for idx in indices:
        problem = data[idx]
        problem_id = problem.get('original_id', problem.get('id', 'unknown'))

        print(f"\n{'─' * 70}")
        print(f"📌 문제 {problem_id} (인덱스: {idx})")
        print(f"{'─' * 70}")

        # 문제 설명
        question = problem.get('question', '') or problem.get('question_html', '')
        import re
        question = re.sub(r'<[^>]+>', '', question)

        print(f"\n## 문제 설명")
        print(question[:1000])
        if len(question) > 1000:
            print("... (truncated)")

        # 입출력 예제
        io = problem.get('input_output', '{}')
        if isinstance(io, str):
            try:
                io_data = json.loads(io)
            except:
                io_data = {}
        else:
            io_data = io

        inputs = io_data.get('inputs', [])
        outputs = io_data.get('outputs', [])

        if inputs and outputs:
            print(f"\n## 예제")
            for i, (inp, out) in enumerate(zip(inputs[:2], outputs[:2])):
                print(f"입력 {i+1}:")
                print(inp[:200])
                print(f"출력 {i+1}:")
                print(out[:200])

        print(f"\n## 제한")
        print(f"- 시간: {problem.get('time_limit', 'N/A')}")
        print(f"- 메모리: {problem.get('memory_limit', 'N/A')}")
        print(f"- 난이도: {problem.get('difficulty', 'N/A')}")

        # 솔루션 템플릿
        results_template["results"].append({
            "index": idx,
            "problem_id": problem_id,
            "solutions": []  # Claude Code가 채울 부분
        })

    # pending 파일 저장
    pending_file = os.path.join(BATCH_DIR, f"pending_{worker_id}.json")
    with open(pending_file, 'w', encoding='utf-8') as f:
        json.dump(results_template, f, ensure_ascii=False, indent=2)

    print(f"\n{'=' * 70}")
    print(f"📝 솔루션 생성 요청")
    print(f"{'=' * 70}")
    print(f"""
위 각 문제에 대해 Python, Java, C++ 솔루션을 생성해주세요.

저장 파일: {pending_file}

솔루션 형식:
{{
  "index": <인덱스>,
  "problem_id": "<문제번호>",
  "solutions": [
    {{"language": "python", "code": "..."}},
    {{"language": "java", "code": "..."}},
    {{"language": "cpp", "code": "..."}}
  ]
}}

완료 후 실행:
  python3 complete_batch.py {worker_id}
""")

    return worker_id

if __name__ == "__main__":
    main()
