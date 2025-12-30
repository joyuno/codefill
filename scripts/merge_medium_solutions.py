#!/usr/bin/env python3
import json

# Read baek_medium.json
with open('/Users/admin/Downloads/codefill/data/baekjoon/baek_medium.json', 'r') as f:
    medium_data = json.load(f)

# Read main file
with open('/Users/admin/Downloads/codefill/data/baekjoon/problems_with_github_solutions.json', 'r') as f:
    main_data = json.load(f)

# Create a map of original_id to index for quick lookup
id_to_idx = {}
for idx, problem in enumerate(main_data):
    id_to_idx[problem.get('original_id', '')] = idx

# Merge solutions
merged_count = 0
for problem_id, solution_data in medium_data.items():
    if problem_id in id_to_idx:
        idx = id_to_idx[problem_id]
        if not main_data[idx].get('solutions'):
            main_data[idx]['solutions'] = solution_data['solutions']
            merged_count += 1
            print(f"Merged solutions for problem {problem_id}")

# Save main file
with open('/Users/admin/Downloads/codefill/data/baekjoon/problems_with_github_solutions.json', 'w') as f:
    json.dump(main_data, f, ensure_ascii=False, indent=2)

print(f"\nTotal merged: {merged_count} problems")
