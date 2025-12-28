#!/usr/bin/env python3
"""
Medium 솔루션 배치 생성기 - 직접 솔루션 정의
사용법: python3 scripts/gen_medium_batch.py
"""

import json
from pathlib import Path

MEDIUM_FILE = Path(__file__).parent.parent / "data" / "baekjoon" / "baek_medium.json"
MAIN_FILE = Path(__file__).parent.parent / "data" / "baekjoon" / "problems_with_github_solutions.json"

def load_medium():
    if MEDIUM_FILE.exists():
        with open(MEDIUM_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_medium(data):
    with open(MEDIUM_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def merge_to_main():
    """병합 실행"""
    with open(MEDIUM_FILE, 'r', encoding='utf-8') as f:
        medium = json.load(f)

    with open(MAIN_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    merged = 0
    for i, p in enumerate(data):
        oid = p.get('original_id')
        if oid in medium and not p.get('solutions'):
            data[i]['solutions'] = medium[oid]['solutions']
            merged += 1

    with open(MAIN_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return merged

def get_empty_medium_problems(limit=20):
    """빈 솔루션인 medium 문제 가져오기"""
    with open(MAIN_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    empty = []
    for p in data:
        if not p.get('solutions') and p.get('difficulty') == 'medium':
            io = p.get('input_output')
            if io and 'inputs' in str(io):
                empty.append({
                    'id': p['original_id'],
                    'name': p['name'],
                    'io': str(io)[:300]
                })

    return empty[:limit]

def show_status():
    """현재 상태 출력"""
    with open(MAIN_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    total = len(data)
    has_sol = sum(1 for p in data if p.get('solutions'))
    empty_medium = sum(1 for p in data if not p.get('solutions') and p.get('difficulty') == 'medium')

    print(f"총 문제: {total}")
    print(f"솔루션 있음: {has_sol} ({has_sol/total*100:.1f}%)")
    print(f"빈 Medium: {empty_medium}")

    medium = load_medium()
    print(f"baek_medium.json: {len(medium)}개")

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "status":
            show_status()
        elif cmd == "merge":
            merged = merge_to_main()
            print(f"병합 완료: {merged}개")
        elif cmd == "list":
            problems = get_empty_medium_problems(20)
            for p in problems:
                print(f"{p['id']}|{p['name'][:30]}|{p['io'][:100]}")
    else:
        show_status()
