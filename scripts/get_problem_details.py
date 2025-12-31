import json

# JSON 파일 읽기
with open('/Users/admin/Downloads/codefill/data/baekjoon/problems_with_github_solutions.json', 'r', encoding='utf-8') as f:
    problems = json.load(f)

# medium 난이도이면서 solutions가 비어있고 input_output이 있는 문제 찾기
empty_medium_problems = []
for i, problem in enumerate(problems):
    difficulty = problem.get('difficulty', '')
    solutions = problem.get('solutions', [])
    input_output = problem.get('input_output', '')

    if difficulty == 'medium' and (not solutions or len(solutions) == 0) and input_output:
        empty_medium_problems.append({
            'original_index': i,
            'problem': problem
        })

# 인덱스 450-479 문제 상세 출력
for i in range(450, 480):
    if i < len(empty_medium_problems):
        p = empty_medium_problems[i]
        prob = p['problem']
        print(f"{'='*80}")
        print(f"문제 #{i} (원본 인덱스: {p['original_index']})")
        print(f"ID: {prob.get('id')}")
        print(f"이름: {prob.get('name')}")
        print(f"원본 ID: {prob.get('original_id')}")
        print(f"\n문제:")
        print(prob.get('question', '')[:3000])
        print(f"\ninput_output:")
        print(prob.get('input_output', ''))
        print()
