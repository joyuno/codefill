import json

# JSON 파일 읽기
with open('/Users/admin/Downloads/codefill/data/baekjoon/problems_with_github_solutions.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 빈 솔루션 배열을 가진 medium 난이도 문제 찾기
empty_medium_problems = []
for i, problem in enumerate(data):
    difficulty = problem.get('difficulty', '')
    solutions = problem.get('solutions', [])
    input_output = problem.get('input_output', '')

    # solutions가 비어있거나 없고, difficulty가 medium이며, input_output이 유효한 경우
    if (not solutions or len(solutions) == 0) and difficulty == 'medium' and input_output:
        empty_medium_problems.append({
            'index': i,
            'id': problem.get('id', ''),
            'name': problem.get('name', ''),
            'question': problem.get('question', '')[:100] if problem.get('question') else '',
            'input_output': problem.get('input_output', '')
        })

print(f"총 문제 수: {len(data)}")
print(f"빈 솔루션 + medium + valid input_output 문제 수: {len(empty_medium_problems)}")
print()

# 인덱스 450-479 문제 출력 (30개)
print("인덱스 450-479 문제:")
for i, prob in enumerate(empty_medium_problems[450:480]):
    print(f"{450+i}: [{prob['index']}] {prob['id']} - {prob['name']}")
