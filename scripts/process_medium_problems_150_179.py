#!/usr/bin/env python3
"""
Process medium difficulty Baekjoon problems (index 150-179) with empty solutions.
Generate solutions in Python, Java, and C++ with Korean comments.
"""

import json
import fcntl
import os

def load_json_with_lock(filepath):
    """Load JSON file with file lock."""
    with open(filepath, 'r', encoding='utf-8') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_SH)
        data = json.load(f)
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    return data

def save_json_with_lock(filepath, data):
    """Save JSON file with file lock."""
    with open(filepath, 'w', encoding='utf-8') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        json.dump(data, f, ensure_ascii=False, indent=2)
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)

def find_empty_medium_problems(data):
    """Find all medium difficulty problems with empty solutions and valid input_output."""
    empty_medium = []
    for idx, problem in enumerate(data):
        difficulty = problem.get('difficulty', '')
        solutions = problem.get('solutions', [])
        input_output = problem.get('input_output', '')

        # Check if medium difficulty, empty solutions, and has valid input_output
        if difficulty == 'medium' and (not solutions or len(solutions) == 0) and input_output:
            empty_medium.append({
                'index': idx,
                'id': problem.get('id', ''),
                'name': problem.get('name', ''),
                'question': problem.get('question', ''),
                'input_output': input_output
            })
    return empty_medium

def main():
    filepath = '/Users/admin/Downloads/codefill/data/baekjoon/problems_with_github_solutions.json'

    # Load the data
    data = load_json_with_lock(filepath)
    print(f"Total problems in file: {len(data)}")

    # Find empty medium problems
    empty_medium = find_empty_medium_problems(data)
    print(f"Total medium problems with empty solutions: {len(empty_medium)}")

    # Get problems from index 150 to 179 (30 problems)
    start_idx = 150
    end_idx = 180
    target_problems = empty_medium[start_idx:end_idx]

    print(f"\nProblems to process (index {start_idx} to {end_idx-1}):")
    print(f"Number of problems: {len(target_problems)}")
    print("\n" + "="*80)

    for i, p in enumerate(target_problems):
        print(f"\n{start_idx + i}. Problem ID: {p['id']}")
        print(f"   Name: {p['name']}")
        print(f"   Index in original file: {p['index']}")
        print(f"   Input/Output: {p['input_output'][:200]}..." if len(p.get('input_output', '')) > 200 else f"   Input/Output: {p['input_output']}")

if __name__ == '__main__':
    main()
