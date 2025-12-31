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
            'index': i,
            'id': problem.get('id'),
            'name': problem.get('name'),
            'original_id': problem.get('original_id')
        })

print(f"총 문제 수: {len(problems)}")
print(f"Medium 난이도 + 빈 solutions + 유효한 input_output: {len(empty_medium_problems)}")
print()

# 인덱스 180-209의 문제들 출력
print("인덱스 180-209의 문제들:")
for i, p in enumerate(empty_medium_problems[180:210]):
    print(f"{180+i}: [{p['index']}] {p['id']} - {p['name']}")
