#!/usr/bin/env python3
"""
백준 Medium 난이도 솔루션 자동 생성 (OpenRouter + Grok Code Fast 1)
"""

import json
import time
import re
import sys
import requests
import fcntl
from pathlib import Path

DATA_FILE = Path(__file__).parent.parent / "data" / "baekjoon" / "problems_with_github_solutions.json"
API_KEY = "<REDACTED_OPENROUTER_KEY>"
API_URL = "https://openrouter.ai/api/v1/chat/completions"

def generate_solution(problem: dict) -> list:
    """Grok Code Fast 1 API로 솔루션 생성"""

    question = problem.get('question', '')[:2000]
    io = problem.get('input_output', '')
    name = problem.get('name', '')

    prompt = f"""백준 문제를 풀어주세요.

문제: {name}

{question}

입출력 예제: {io}

Python, Java, C++ 3개 언어로 정답 코드를 작성해주세요.
모든 주석은 한국어로 작성해주세요.

반드시 아래 JSON 형식으로만 응답하세요 (다른 텍스트 없이):
{{"python": "파이썬코드", "java": "자바코드", "cpp": "C++코드"}}"""

    try:
        response = requests.post(
            API_URL,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "x-ai/grok-code-fast-1",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 6000
            },
            timeout=60
        )

        if response.status_code == 200:
            text = response.json()['choices'][0]['message']['content']
            json_match = re.search(r'\{[\s\S]*\}', text)
            if json_match:
                codes = json.loads(json_match.group())
                return [
                    {"language": "python", "code": codes.get("python", "")},
                    {"language": "java", "code": codes.get("java", "")},
                    {"language": "cpp", "code": codes.get("cpp", "")}
                ]
        else:
            print(f"API Error: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")

    return None


def save_with_lock(data):
    """파일 락으로 안전하게 저장"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        json.dump(data, f, ensure_ascii=False, indent=2)
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)


def main(offset=0, batch_size=10):
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # medium + 빈 솔루션 + 입출력 있는 문제
    empty_medium = []
    for i, p in enumerate(data):
        if not p.get('solutions') and p.get('difficulty') == 'medium':
            io = p.get('input_output')
            if io and 'inputs' in str(io):
                empty_medium.append((i, p))

    # 오프셋부터 배치 크기만큼
    batch = empty_medium[offset:offset + batch_size]

    print(f"[Batch {offset//batch_size + 1}] Medium {offset}~{offset+len(batch)} ({len(batch)}개)")

    updated = 0
    for idx, (i, problem) in enumerate(batch):
        pid = problem.get('original_id', '')
        name = problem.get('name', '')[:25]

        print(f"  [{idx+1}/{len(batch)}] {pid}: {name}...", end=" ", flush=True)

        solutions = generate_solution(problem)

        if solutions and all(s['code'] for s in solutions):
            # 최신 데이터 다시 로드 후 업데이트
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            data[i]['solutions'] = solutions
            save_with_lock(data)
            updated += 1
            print("✓")
        else:
            print("✗")

        time.sleep(0.5)

    print(f"  완료: {updated}/{len(batch)}개 성공")
    return updated


if __name__ == "__main__":
    offset = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    batch_size = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    main(offset, batch_size)
