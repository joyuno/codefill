#!/usr/bin/env python3
"""
백준 문제 솔루션 자동 생성 (OpenRouter + Grok Code Fast 1)
"""

import json
import time
import re
import requests
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
            
            # JSON 추출
            json_match = re.search(r'\{[\s\S]*\}', text)
            if json_match:
                codes = json.loads(json_match.group())
                return [
                    {"language": "python", "code": codes.get("python", "")},
                    {"language": "java", "code": codes.get("java", "")},
                    {"language": "cpp", "code": codes.get("cpp", "")}
                ]
        else:
            print(f"API Error: {response.status_code} - {response.text[:100]}")
    except Exception as e:
        print(f"Error: {e}")
    
    return None


def main():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # easy + 빈 솔루션 + 입출력 있는 문제
    empty_easy = []
    for i, p in enumerate(data):
        if not p.get('solutions') and p.get('difficulty') == 'easy':
            io = p.get('input_output')
            if io and 'inputs' in str(io):
                empty_easy.append((i, p))
    
    print(f"Easy 빈 솔루션: {len(empty_easy)}개")
    print("시작...\n")
    
    updated = 0
    for idx, (i, problem) in enumerate(empty_easy):
        pid = problem.get('original_id', '')
        name = problem.get('name', '')[:30]
        
        print(f"[{idx+1}/{len(empty_easy)}] {pid}: {name}...", end=" ", flush=True)
        
        solutions = generate_solution(problem)
        
        if solutions and all(s['code'] for s in solutions):
            data[i]['solutions'] = solutions
            updated += 1
            print("✓")
            
            if updated % 10 == 0:
                with open(DATA_FILE, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print(f"  💾 저장 ({updated}개)")
        else:
            print("✗")
        
        time.sleep(0.3)
    
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    total = len(data)
    has_sol = sum(1 for p in data if p.get('solutions'))
    print(f"\n완료! {updated}개 생성")
    print(f"현재: {has_sol}/{total}개 ({has_sol/total*100:.1f}%)")


if __name__ == "__main__":
    main()
