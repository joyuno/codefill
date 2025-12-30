#!/usr/bin/env python3
"""Merge solutions from baek_medium.json into problems_with_github_solutions.json"""

import json

# Load solutions file
with open('baek_medium.json', 'r') as f:
    solutions_data = json.load(f)

# Create mapping of original_id (as string) to solutions
solutions_map = {str(item['original_id']): item['solutions'] for item in solutions_data}

# Load main problems file
with open('data/baekjoon/problems_with_github_solutions.json', 'r') as f:
    problems_data = json.load(f)

# Merge solutions
updated_count = 0
for problem in problems_data:
    problem_id = str(problem.get('original_id', ''))
    if problem_id in solutions_map:
        if not problem.get('solutions'):
            problem['solutions'] = solutions_map[problem_id]
            updated_count += 1
            print(f"Updated: {problem_id} - {problem['name']}")

# Save updated data
with open('data/baekjoon/problems_with_github_solutions.json', 'w') as f:
    json.dump(problems_data, f, ensure_ascii=False, indent=2)

print(f"\nTotal problems updated: {updated_count}")

# Count remaining problems without solutions (medium difficulty with input_output)
empty_count = 0
for p in problems_data:
    if not p.get('solutions') and p.get('difficulty') == 'medium' and p.get('input_output') and 'inputs' in str(p.get('input_output')):
        empty_count += 1

print(f"Remaining medium problems without solutions: {empty_count}")
