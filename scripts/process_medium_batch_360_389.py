#!/usr/bin/env python3
"""
Process medium difficulty Baekjoon problems with empty solutions.
Process problems from index 360 to 389 (30 problems).
"""

import json
import fcntl

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

    # Check if solutions is empty or missing AND difficulty is medium AND has valid input_output
    if (not solutions or len(solutions) == 0) and difficulty == 'medium' and input_output:
        empty_medium_problems.append({
            'index': idx,
            'id': problem.get('id', ''),
            'name': problem.get('name', ''),
            'question': problem.get('question', ''),
            'input_output': input_output
        })

print(f"Total medium difficulty problems with empty solutions: {len(empty_medium_problems)}")

# Get problems from index 360 to 389
start_idx = 360
end_idx = 390  # exclusive
target_problems = empty_medium_problems[start_idx:end_idx]

print(f"\nProblems to process (index {start_idx} to {end_idx-1}):")
for i, p in enumerate(target_problems):
    print(f"  {start_idx + i}: {p['id']} - {p['name']}")
    print(f"      Original index in JSON: {p['index']}")
