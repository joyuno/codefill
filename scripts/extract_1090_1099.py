#!/usr/bin/env python3
"""
백준 문제 1090-1099 추출 및 상세 정보 출력
"""

import json
from pathlib import Path

def main():
    data_path = Path(__file__).parent.parent / "data" / "baekjoon" / "checkpoint_1000_5073.json"

    with open(data_path, 'r', encoding='utf-8') as f:
        problems = json.load(f)

    # 1090-1099 범위의 문제만 필터링
    target_problems = [p for p in problems if p.get('original_id') and 1090 <= int(p.get('original_id', '0')) <= 1099]

    print(f"Found {len(target_problems)} problems in range 1090-1099\n")

    # JSON 파일로 저장
    output = []
    for p in target_problems:
        output.append({
            'original_id': p.get('original_id'),
            'name': p.get('name'),
            'question': p.get('question'),
            'input_output': p.get('input_output'),
            'difficulty': p.get('difficulty'),
            'tags': p.get('tags'),
            'time_limit': p.get('time_limit'),
            'memory_limit': p.get('memory_limit'),
            'url': p.get('url')
        })

    output_path = Path(__file__).parent.parent / "data" / "problems_1090_1099.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"Saved to: {output_path}")
    print(f"\nProblems extracted:")
    for p in output:
        print(f"  - {p['original_id']}: {p['name']}")

if __name__ == "__main__":
    main()
