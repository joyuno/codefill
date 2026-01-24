"""
taco 문제 이름 수정
1. [출처] 접두사 제거
2. 30자 초과 시 LLM으로 요약
"""

import asyncio
import sys
import os
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import get_supabase_client
from app.services.openrouter import openrouter_service
from app.config import get_settings

settings = get_settings()


async def summarize_name(name: str, question: str) -> str:
    """
    긴 이름을 30자 이내로 요약

    Args:
        name: 현재 이름
        question: 문제 설명 (요약 참고용)

    Returns:
        요약된 이름 (30자 이내)
    """
    # question 앞부분만 사용 (토큰 절약)
    question_preview = question[:500] if question else ""

    prompt = f"""다음 알고리즘 문제 제목을 30자 이내로 줄여주세요.

현재 제목: {name}

문제 설명 (참고):
{question_preview}

요구사항:
1. 핵심 알고리즘이나 목표만 남기기
2. 불필요한 수식어 제거
3. 최대 30자
4. 제목만 출력 (따옴표, 설명 없이)

짧은 제목:"""

    try:
        response = await openrouter_service.chat_completion(
            model="gemini-flash",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=50,
        )

        content = openrouter_service.get_content(response).strip()
        content = content.replace('"', '').replace("'", "").strip()
        content = content.split('\n')[0].strip()

        # 여전히 길면 강제 자르기
        if len(content) > 30:
            content = content[:27] + "..."

        return content

    except Exception as e:
        print(f"  LLM Error: {e}")
        # 실패 시 단순 자르기
        return name[:27] + "..."


async def fix_taco_names(batch_size: int = 50, max_count: int = None):
    """
    이미 변경된 taco 문제 이름 수정
    1. [출처] 접두사 제거
    2. 30자 초과 시 요약
    """
    db = get_supabase_client()

    # [출처] 형식 이름 조회 (taco 소스만)
    result = db.table('base_problems').select(
        'id, name, question, source'
    ).like('name', '[%]%').in_(
        'source', ['codewars', 'codeforces', 'hackerrank', 'leetcode']
    ).execute()

    problems = result.data or []
    total_count = len(problems)
    print(f"Total problems to fix: {total_count}")

    if max_count:
        problems = problems[:max_count]

    fixed_count = 0
    summarized_count = 0
    error_count = 0

    for i, p in enumerate(problems):
        try:
            old_name = p['name']

            # [출처] 접두사 제거
            new_name = re.sub(r'^\[[^\]]+\]\s*', '', old_name)

            # 30자 초과 시 요약
            if len(new_name) > 30:
                new_name = await summarize_name(new_name, p.get('question', ''))
                summarized_count += 1
                # Rate limit 방지
                await asyncio.sleep(0.1)

            # 변경된 경우에만 업데이트
            if new_name != old_name:
                db.table('base_problems').update({
                    'name': new_name
                }).eq('id', p['id']).execute()

                print(f"  [{i+1}/{len(problems)}] {old_name[:40]}... → {new_name}")
                fixed_count += 1

            # 진행 상황 출력 (100개마다)
            if (i + 1) % 100 == 0:
                print(f"  Progress: {i+1}/{len(problems)} ({fixed_count} fixed, {summarized_count} summarized)")

        except Exception as e:
            print(f"  Error for {p.get('name', 'unknown')}: {e}")
            error_count += 1

    print(f"\n=== Complete ===")
    print(f"Fixed: {fixed_count}")
    print(f"Summarized (LLM): {summarized_count}")
    print(f"Errors: {error_count}")

    return {"fixed": fixed_count, "summarized": summarized_count, "errors": error_count}


async def main():
    batch_size = 50
    max_count = None

    if len(sys.argv) > 1:
        max_count = int(sys.argv[1])

    print(f"Starting taco name fix...")
    print(f"Max count: {max_count or 'all'}")

    await fix_taco_names(batch_size, max_count)


if __name__ == "__main__":
    asyncio.run(main())
