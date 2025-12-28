#!/usr/bin/env python3
"""새로운 medium 솔루션을 기존 baek_medium.json에 병합"""
import json

NEW_FILE = "data/baekjoon/new_medium_solutions.json"
MEDIUM_FILE = "data/baekjoon/baek_medium.json"

# 기존 데이터 로드
with open(MEDIUM_FILE, 'r', encoding='utf-8') as f:
    existing = json.load(f)

# 새 데이터 로드
with open(NEW_FILE, 'r', encoding='utf-8') as f:
    new_data = json.load(f)

# 병합
merged_count = 0
for problem_id, solution_data in new_data.items():
    existing[problem_id] = solution_data
    merged_count += 1

# 저장
with open(MEDIUM_FILE, 'w', encoding='utf-8') as f:
    json.dump(existing, f, ensure_ascii=False, indent=2)

print(f"병합 완료: {merged_count}개 문제 추가")
print(f"추가된 문제: {list(new_data.keys())}")
print(f"총 문제 수: {len(existing)}")
