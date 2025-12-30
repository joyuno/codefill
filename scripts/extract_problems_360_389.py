#!/usr/bin/env python3
"""
Extract problem details for medium difficulty problems from index 360 to 389.
"""

import json

# Load the JSON file
json_path = '/Users/admin/Downloads/codefill/data/baekjoon/problems_with_github_solutions.json'

with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Find medium difficulty problems with empty solutions and valid input_output
empty_medium_problems = []
for idx, problem in enumerate(data):
    solutions = problem.get('solutions', [])
    difficulty = problem.get('difficulty', '')
    input_output = problem.get('input_output', '')

    if (not solutions or len(solutions) == 0) and difficulty == 'medium' and input_output:
        empty_medium_problems.append({
            'original_index': idx,
            'problem': problem
        })

# Get problems from index 360 to 389
start_idx = 360
end_idx = 390
target_problems = empty_medium_problems[start_idx:end_idx]

# Print each problem's details
for i, item in enumerate(target_problems):
    p = item['problem']
    print(f"=" * 80)
    print(f"Problem {start_idx + i}: {p.get('id', '')} (JSON index: {item['original_index']})")
    print(f"Name: {p.get('name', '')}")
    print(f"-" * 40)
    print(f"Question:\n{p.get('question', '')[:2000]}")
    print(f"-" * 40)
    print(f"Input/Output:\n{p.get('input_output', '')}")
    print()
