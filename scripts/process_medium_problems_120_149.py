#!/usr/bin/env python3
"""
백준 중간 난이도 문제 솔루션 생성 스크립트
인덱스 120-149 범위의 빈 솔루션 문제들을 처리합니다.
"""

import json
import fcntl
import os

def load_json_with_lock(filepath):
    """파일 잠금을 사용하여 JSON 파일을 읽습니다."""
    with open(filepath, 'r', encoding='utf-8') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_SH)
        data = json.load(f)
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    return data

def save_json_with_lock(filepath, data):
    """파일 잠금을 사용하여 JSON 파일을 저장합니다."""
    with open(filepath, 'w', encoding='utf-8') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        json.dump(data, f, ensure_ascii=False, indent=2)
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)

def find_empty_medium_problems(data):
    """빈 솔루션 배열을 가진 중간 난이도 문제들을 찾습니다."""
    empty_medium_problems = []
    for idx, problem in enumerate(data):
        difficulty = problem.get('difficulty', '')
        solutions = problem.get('solutions', [])
        input_output = problem.get('input_output', '')

        # 중간 난이도이고, 솔루션이 비어있고, input_output이 유효한 문제
        if difficulty == 'medium' and (not solutions or solutions == []) and input_output:
            empty_medium_problems.append((idx, problem))

    return empty_medium_problems

def main():
    filepath = '/Users/admin/Downloads/codefill/data/baekjoon/problems_with_github_solutions.json'

    print("JSON 파일 로딩 중...")
    data = load_json_with_lock(filepath)
    print(f"전체 문제 수: {len(data)}")

    # 빈 솔루션을 가진 중간 난이도 문제 찾기
    empty_medium_problems = find_empty_medium_problems(data)
    print(f"빈 솔루션을 가진 중간 난이도 문제 수: {len(empty_medium_problems)}")

    # 120-149 인덱스 범위의 문제들 출력
    start_idx = 120
    end_idx = 150  # exclusive

    problems_to_process = empty_medium_problems[start_idx:end_idx]

    print(f"\n처리할 문제 목록 (인덱스 {start_idx}-{end_idx-1}):")
    for i, (data_idx, problem) in enumerate(problems_to_process):
        print(f"  {start_idx + i}. [{data_idx}] {problem.get('name', 'N/A')} - {problem.get('id', 'N/A')}")
        # 문제 세부 정보 출력
        io = problem.get('input_output', '{}')
        try:
            io_data = json.loads(io) if isinstance(io, str) else io
            inputs = io_data.get('inputs', [])
            outputs = io_data.get('outputs', [])
            print(f"      입력 예시: {inputs[:2] if len(inputs) > 2 else inputs}")
            print(f"      출력 예시: {outputs[:2] if len(outputs) > 2 else outputs}")
        except:
            print(f"      IO 파싱 실패: {io[:100]}")

if __name__ == '__main__':
    main()
