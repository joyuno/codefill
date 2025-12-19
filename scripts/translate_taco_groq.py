#!/usr/bin/env python3
"""
TACO Dataset Translator using Groq API
구조화된 형식으로 번역
"""

import json
import os
from pathlib import Path
import httpx
import re
from dotenv import load_dotenv

# .env.local에서 환경변수 로드
load_dotenv('.env.local')

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data' / 'taco'
OUTPUT_DIR = DATA_DIR / 'translated'


def call_groq(prompt: str) -> str:
    """Groq API 호출"""
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2,
        "max_tokens": 3000
    }

    response = httpx.post(GROQ_API_URL, headers=headers, json=payload, timeout=60)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"].strip()


def translate_structured(question: str, source: str) -> dict:
    """문제를 구조화된 형식으로 번역"""

    prompt = f"""You are a professional translator for programming problems.
Translate the following coding problem from English to Korean.

IMPORTANT: Return ONLY a valid JSON object with this exact structure (no markdown, no code blocks):
{{
  "title": "문제 제목 (짧고 명확하게, 한글로)",
  "question": "문제 설명 (핵심 내용만, 입출력 형식 제외)",
  "input_format": "입력 형식 설명",
  "output_format": "출력 형식 설명",
  "constraints": "제약 조건 (있으면)",
  "examples": [
    {{
      "input": "예시 입력",
      "output": "예시 출력",
      "explanation": "설명 (있으면)"
    }}
  ],
  "time_complexity": "시간 복잡도 (있으면, 없으면 null)",
  "space_complexity": "공간 복잡도 (있으면, 없으면 null)"
}}

Rules:
1. Keep variable names, function names, code in English
2. Keep mathematical notation ($n$, $k$) as-is
3. Translate naturally to Korean, not word-by-word
4. Extract examples from the problem if present
5. Return ONLY valid JSON, no other text

Problem to translate:
{question}
"""

    result = call_groq(prompt)

    # JSON 파싱 시도
    try:
        # 마크다운 코드 블록 제거
        if "```json" in result:
            result = result.split("```json")[1].split("```")[0]
        elif "```" in result:
            result = result.split("```")[1].split("```")[0]

        return json.loads(result.strip())
    except json.JSONDecodeError:
        # 파싱 실패 시 기본 구조 반환
        return {
            "title": "번역 실패",
            "question": result,
            "input_format": "",
            "output_format": "",
            "constraints": "",
            "examples": [],
            "time_complexity": None,
            "space_complexity": None
        }


def extract_problems(n: int = 5):
    """TACO 데이터셋에서 n개의 문제를 추출"""
    problems = []

    with open(DATA_DIR / 'by_difficulty' / 'easy.json', 'r') as f:
        f.read(1)  # Skip [

        for _ in range(n):
            content = ""
            depth = 0
            started = False

            while True:
                c = f.read(1)
                if not c:
                    break
                if c == ',' and not started:
                    continue
                content += c

                if c == '{':
                    depth += 1
                    started = True
                elif c == '}':
                    depth -= 1
                    if started and depth == 0:
                        break

            if content.strip():
                problems.append(json.loads(content))

    return problems


def translate_problem(problem: dict, idx: int) -> dict:
    """단일 문제를 구조화된 형식으로 번역"""
    print(f"\n[{idx}] Translating problem from {problem.get('source', 'unknown')}...")

    question = problem.get('question', '')[:2500]
    source = problem.get('source', '')

    # 구조화된 번역
    translated = translate_structured(question, source)

    # 태그 번역
    tag_map = {
        'Data structures': '자료구조',
        'Mathematics': '수학',
        'Greedy algorithms': '그리디',
        'String algorithms': '문자열',
        'Fundamentals': '기초',
        'Dynamic programming': 'DP',
        'Sorting': '정렬',
        'Search': '탐색',
        'Graph': '그래프',
        'Tree': '트리',
    }

    tags = problem.get('tags', []) or []
    korean_tags = [tag_map.get(t, t) for t in tags[:5]]

    return {
        "id": f"taco_kr_{idx:03d}",
        "source": problem.get('source'),
        "difficulty": problem.get('difficulty'),
        "tags": korean_tags,
        "title": translated.get('title', ''),
        "question": translated.get('question', ''),
        "input_format": translated.get('input_format', ''),
        "output_format": translated.get('output_format', ''),
        "constraints": translated.get('constraints', ''),
        "examples": translated.get('examples', []),
        "time_complexity": translated.get('time_complexity'),
        "space_complexity": translated.get('space_complexity'),
        "solutions": problem.get('solutions', [])[:2] if problem.get('solutions') else [],
    }


def main():
    print("=" * 60)
    print("TACO Dataset Translator (Structured Format)")
    print("=" * 60)

    OUTPUT_DIR.mkdir(exist_ok=True)

    # 문제 추출
    print("\n[1/2] Extracting problems...")
    problems = extract_problems(5)
    print(f"  - Extracted {len(problems)} problems")

    # 번역
    print("\n[2/2] Translating with Groq (Llama 3.3 70B)...")
    translated = []

    for i, problem in enumerate(problems, 1):
        try:
            result = translate_problem(problem, i)
            translated.append(result)
            print(f"  ✓ Problem {i}: {result['title']}")
        except Exception as e:
            print(f"  ✗ Problem {i} failed: {e}")

    # 저장
    output_path = OUTPUT_DIR / 'sample_groq_structured.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(translated, f, ensure_ascii=False, indent=2)

    print(f"\n{'=' * 60}")
    print(f"Translation Complete!")
    print(f"{'=' * 60}")
    print(f"Saved to: {output_path}")

    # 결과 미리보기
    print("\n[Preview]")
    for t in translated:
        print(f"\n--- [{t['source']}] {t['title']} ---")
        print(f"Tags: {t['tags']}")
        print(f"Question: {t['question'][:200]}...")
        if t['examples']:
            print(f"Examples: {len(t['examples'])} provided")


if __name__ == "__main__":
    main()
