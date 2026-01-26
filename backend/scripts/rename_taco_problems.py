"""
taco 문제 이름을 LLM으로 한국어화

taco_숫자 형식의 이름을 question 내용을 요약한 한국어 제목으로 변경합니다.
gemini-flash 모델 사용 (저렴하고 빠름)
"""

import asyncio
import sys
import os
import json
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import get_supabase_client
from app.services.openrouter import openrouter_service
from app.config import get_settings

settings = get_settings()


async def generate_korean_name(question: str, tags: list, source: str) -> str:
    """
    question을 요약하여 한국어 문제 제목 생성

    Args:
        question: 문제 설명
        tags: 문제 태그
        source: 출처 (codewars, codeforces 등)

    Returns:
        한국어 제목 (30자 이내)
    """
    # question 앞부분만 사용 (토큰 절약)
    question_preview = question[:1500] if question else ""
    tags_str = ", ".join(tags[:5]) if tags else ""

    prompt = f"""다음 알고리즘 문제의 핵심 내용을 파악하여 한국어 제목을 생성해주세요.

문제 설명:
{question_preview}

태그: {tags_str}
출처: {source}

요구사항:
1. 문제의 핵심 알고리즘이나 자료구조를 반영
2. 최대 30자 이내의 간결한 한국어 제목 (필수!)
3. 예시: "이진 탐색 최적값", "BFS 최단거리", "DP 배낭"
4. 제목만 출력 (따옴표, 설명, [출처] 없이)

한국어 제목:"""

    try:
        response = await openrouter_service.chat_completion(
            model="gemini-flash",  # 빠르고 저렴
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=100,
        )

        content = openrouter_service.get_content(response).strip()

        # 따옴표, 줄바꿈 제거
        content = content.replace('"', '').replace("'", "").strip()
        content = content.split('\n')[0].strip()

        # 30자 제한 (필수)
        if len(content) > 30:
            content = content[:27] + "..."

        return content

    except Exception as e:
        print(f"  LLM Error: {e}")
        return None


async def rename_taco_problems(batch_size: int = 20, start_offset: int = 0, max_count: int = None):
    """
    taco 문제 이름을 한국어로 변경

    Args:
        batch_size: 한 번에 처리할 문제 수
        start_offset: 시작 오프셋
        max_count: 최대 처리 개수 (None이면 전체)
    """
    db = get_supabase_client()

    # taco 이름 패턴 문제 조회
    count_result = db.table('base_problems').select('id', count='exact').like('name', 'taco_%').execute()
    total_count = count_result.count
    print(f"Total taco problems: {total_count}")

    if max_count:
        total_count = min(total_count, start_offset + max_count)

    success_count = 0
    error_count = 0
    skip_count = 0
    offset = start_offset

    while offset < total_count:
        # 배치 조회
        result = db.table('base_problems').select(
            'id, name, question, tags, source'
        ).like('name', 'taco_%').range(offset, offset + batch_size - 1).execute()

        problems = result.data
        if not problems:
            break

        print(f"\nBatch {offset}-{offset+batch_size}: Processing {len(problems)} problems...")

        for p in problems:
            try:
                # 이미 한국어 이름이면 스킵
                if not p['name'].startswith('taco_'):
                    skip_count += 1
                    continue

                # question이 없으면 스킵
                if not p.get('question'):
                    print(f"  {p['name']}: No question, skipping")
                    skip_count += 1
                    continue

                # LLM으로 한국어 이름 생성
                korean_name = await generate_korean_name(
                    question=p['question'],
                    tags=p.get('tags', []),
                    source=p.get('source', 'unknown')
                )

                if korean_name:
                    # [출처] 접두사 없이 한국어 이름만 사용 (30자 이내)
                    new_name = korean_name

                    # DB 업데이트
                    db.table('base_problems').update({
                        'name': new_name[:30]  # 30자 제한
                    }).eq('id', p['id']).execute()

                    print(f"  ✓ {p['name']} → {new_name}")
                    success_count += 1
                else:
                    print(f"  ✗ {p['name']}: Failed to generate name")
                    error_count += 1

                # Rate limit 방지
                await asyncio.sleep(0.1)

            except Exception as e:
                print(f"  Error for {p['name']}: {e}")
                error_count += 1

        offset += batch_size

        # 배치 간 딜레이
        await asyncio.sleep(0.5)

        # 진행 상황 출력
        progress = (offset / total_count) * 100
        print(f"  Progress: {progress:.1f}% ({success_count} success, {error_count} errors, {skip_count} skipped)")

    print(f"\n=== Complete ===")
    print(f"Success: {success_count}")
    print(f"Errors: {error_count}")
    print(f"Skipped: {skip_count}")

    return {"success": success_count, "errors": error_count, "skipped": skip_count}


async def main():
    batch_size = 20
    start_offset = 0
    max_count = None

    if len(sys.argv) > 1:
        batch_size = int(sys.argv[1])
    if len(sys.argv) > 2:
        start_offset = int(sys.argv[2])
    if len(sys.argv) > 3:
        max_count = int(sys.argv[3])

    print(f"Starting taco problem renaming...")
    print(f"Batch size: {batch_size}, Start offset: {start_offset}, Max count: {max_count or 'all'}")

    await rename_taco_problems(batch_size, start_offset, max_count)


if __name__ == "__main__":
    asyncio.run(main())
