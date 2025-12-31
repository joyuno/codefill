#!/usr/bin/env python3
"""
백준 Medium 난이도 문제 솔루션 생성 스크립트
한 번에 하나의 문제를 처리하고 즉시 저장합니다.
"""

import json
import fcntl
import os

JSON_FILE = '/Users/admin/Downloads/codefill/data/baekjoon/problems_with_github_solutions.json'

def load_json_with_lock():
    """파일 잠금을 사용하여 JSON 파일을 로드합니다."""
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_SH)
        data = json.load(f)
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    return data

def save_json_with_lock(data):
    """파일 잠금을 사용하여 JSON 파일을 저장합니다."""
    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        json.dump(data, f, ensure_ascii=False, indent=2)
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)

def get_empty_medium_problems(data):
    """빈 solutions 배열을 가진 medium 난이도 문제를 반환합니다."""
    return [p for p in data if p.get('difficulty') == 'medium' and not p.get('solutions')]

def add_solution_to_problem(problem_id, solutions):
    """특정 문제에 솔루션을 추가하고 저장합니다."""
    data = load_json_with_lock()

    for problem in data:
        if problem['id'] == problem_id:
            problem['solutions'] = solutions
            break

    save_json_with_lock(data)

    # 저장 확인
    verify_data = load_json_with_lock()
    for problem in verify_data:
        if problem['id'] == problem_id:
            return len(problem.get('solutions', [])) == len(solutions)
    return False

if __name__ == "__main__":
    data = load_json_with_lock()
    empty_problems = get_empty_medium_problems(data)
    print(f"빈 솔루션을 가진 Medium 문제 수: {len(empty_problems)}")
    print("\n처음 10개 문제:")
    for i, p in enumerate(empty_problems[:10]):
        print(f"{i+1}. {p['id']}: {p.get('name', 'N/A')}")
