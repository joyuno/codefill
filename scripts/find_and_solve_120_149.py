#!/usr/bin/env python3
"""
실제 120-149 범위의 문제를 확인하고 솔루션을 생성합니다.
"""

import json
import fcntl

def load_json_with_lock(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_SH)
        data = json.load(f)
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    return data

def find_empty_medium_problems(data):
    empty_medium_problems = []
    for idx, problem in enumerate(data):
        difficulty = problem.get('difficulty', '')
        solutions = problem.get('solutions', [])
        input_output = problem.get('input_output', '')

        if difficulty == 'medium' and (not solutions or solutions == []) and input_output:
            empty_medium_problems.append((idx, problem))

    return empty_medium_problems

filepath = '/Users/admin/Downloads/codefill/data/baekjoon/problems_with_github_solutions.json'
data = load_json_with_lock(filepath)
empty_medium_problems = find_empty_medium_problems(data)

print(f"총 빈 중간 난이도 문제 수: {len(empty_medium_problems)}")
print("\n인덱스 120-149의 문제들:")

for i in range(120, min(150, len(empty_medium_problems))):
    data_idx, problem = empty_medium_problems[i]
    problem_id = problem.get('id', 'N/A')
    name = problem.get('name', 'N/A')
    io = problem.get('input_output', '{}')
    question = problem.get('question', '')[:200]

    print(f"\n=== [{i}] {name} ===")
    print(f"ID: {problem_id}")
    print(f"Question: {question}...")

    try:
        io_data = json.loads(io) if isinstance(io, str) else io
        inputs = io_data.get('inputs', [])[:2]
        outputs = io_data.get('outputs', [])[:2]
        print(f"Input example: {inputs}")
        print(f"Output example: {outputs}")
    except:
        print(f"IO: {io[:100]}")
