#!/usr/bin/env python3
"""
Script to find medium difficulty problems with empty solutions
and process problems from index 240 to 269.
"""

import json
import sys

# Load the JSON file
with open('/Users/admin/Downloads/codefill/data/baekjoon/problems_with_github_solutions.json', 'r', encoding='utf-8') as f:
    problems = json.load(f)

# Find medium difficulty problems with empty solutions and valid input_output
empty_medium_problems = []
for idx, problem in enumerate(problems):
    difficulty = problem.get('difficulty', '')
    solutions = problem.get('solutions', [])
    input_output = problem.get('input_output', '')

    # Check if solutions is empty or missing and difficulty is medium and has valid input_output
    if (not solutions or len(solutions) == 0) and difficulty == 'medium' and input_output:
        empty_medium_problems.append({
            'original_index': idx,
            'id': problem.get('id', ''),
            'name': problem.get('name', ''),
            'question': problem.get('question', ''),
            'input_output': input_output
        })

print(f"Total medium difficulty problems with empty solutions: {len(empty_medium_problems)}")
print(f"\nProblems from index 240 to 269 (30 problems):")
print("=" * 80)

# Get problems from index 240 to 269
for i in range(240, min(270, len(empty_medium_problems))):
    p = empty_medium_problems[i]
    print(f"\n[{i}] Original index: {p['original_index']}")
    print(f"ID: {p['id']}")
    print(f"Name: {p['name']}")
    print(f"Input/Output: {p['input_output'][:200]}..." if len(p['input_output']) > 200 else f"Input/Output: {p['input_output']}")
    print("-" * 40)
