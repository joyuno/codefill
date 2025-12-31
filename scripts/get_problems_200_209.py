#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json

JSON_FILE = '/Users/admin/Downloads/codefill/data/baekjoon/problems_with_github_solutions.json'

with open(JSON_FILE, 'r', encoding='utf-8') as f:
    problems = json.load(f)

# medium 난이도이면서 solutions가 비어있고 input_output이 있는 문제 찾기
empty_medium = []
for i, problem in enumerate(problems):
    difficulty = problem.get('difficulty', '')
    solutions = problem.get('solutions', [])
    input_output = problem.get('input_output', '')

    if difficulty == 'medium' and (not solutions or len(solutions) == 0) and input_output:
        empty_medium.append({
            'original_index': i,
            'problem': problem
        })

# 200-209 문제 상세 출력
for idx in range(200, 210):
    if idx >= len(empty_medium):
        break
    p = empty_medium[idx]
    prob = p['problem']
    print(f"{'='*80}")
    print(f"리스트 인덱스: {idx}, 원본 인덱스: {p['original_index']}")
    print(f"ID: {prob.get('id')}")
    print(f"이름: {prob.get('name')}")
    print(f"\n문제:")
    print(prob.get('question', '')[:1500])
    print(f"\ninput_output:")
    print(prob.get('input_output', ''))
    print()
