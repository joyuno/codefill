#!/usr/bin/env python3
"""
Process medium difficulty Baekjoon problems with empty solutions (index 270-299).
Generates solutions in Python, Java, and C++ with Korean comments.
"""

import json
import fcntl
import sys

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
    """Find medium difficulty problems with empty solutions and valid input_output."""
    empty_medium = []
    for i, problem in enumerate(data):
        difficulty = problem.get('difficulty', '')
        solutions = problem.get('solutions', [])
        input_output = problem.get('input_output', '')

        # Check if medium difficulty, empty solutions, and has valid input_output
        if (difficulty == 'medium' and
            (not solutions or len(solutions) == 0) and
            input_output and input_output.strip()):
            empty_medium.append((i, problem))

    return empty_medium

def main():
    filepath = '/Users/admin/Downloads/codefill/data/baekjoon/problems_with_github_solutions.json'

    print("Loading JSON file...")
    data = load_json_with_lock(filepath)
    print(f"Total problems loaded: {len(data)}")

    # Find empty medium problems
    empty_medium = find_empty_medium_problems(data)
    print(f"Total medium problems with empty solutions: {len(empty_medium)}")

    # Get problems from index 270 to 299
    start_idx = 270
    end_idx = 300

    if start_idx >= len(empty_medium):
        print(f"Start index {start_idx} is out of range. Only {len(empty_medium)} empty medium problems found.")
        return

    end_idx = min(end_idx, len(empty_medium))
    problems_to_process = empty_medium[start_idx:end_idx]

    print(f"\nProblems to process (indices {start_idx} to {end_idx-1}):")
    print("-" * 80)

    for local_idx, (global_idx, problem) in enumerate(problems_to_process):
        print(f"\n[{start_idx + local_idx}] Global Index: {global_idx}")
        print(f"  ID: {problem.get('id', 'N/A')}")
        print(f"  Name: {problem.get('name', 'N/A')}")
        print(f"  Difficulty: {problem.get('difficulty', 'N/A')}")

        # Parse input_output
        io_str = problem.get('input_output', '')
        if io_str:
            try:
                io_data = json.loads(io_str)
                inputs = io_data.get('inputs', [])
                outputs = io_data.get('outputs', [])
                print(f"  Input/Output examples: {len(inputs)}")
            except:
                print(f"  Input/Output: Error parsing")

        # Print first 200 chars of question
        question = problem.get('question', '')[:200]
        print(f"  Question preview: {question}...")

if __name__ == "__main__":
    main()
