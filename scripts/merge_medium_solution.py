#!/usr/bin/env python3
"""medium 솔루션을 원본 파일에 병합"""
import json

MEDIUM_FILE = "data/baekjoon/baek_medium.json"
MAIN_FILE = "data/baekjoon/problems_with_github_solutions.json"

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

print(f"병합 완료: {merged}개")
