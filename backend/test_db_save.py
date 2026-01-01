"""
DB 저장 테스트 스크립트
문제 생성 시 DB에 올바르게 저장되는지 검증

테스트 시나리오:
1. 기존 DB 문제 → problems_blank에 저장 확인
2. CodeGen 문제 → base_problems + problems_blank에 저장 확인
"""

import asyncio
import sys
sys.path.insert(0, '.')

from app.database import get_supabase_client
from app.services.problem_save import get_problem_save_service


async def test_db_save():
    db = get_supabase_client()
    problem_save = get_problem_save_service()

    print("=" * 60)
    print("DB 저장 테스트")
    print("=" * 60)

    # 1. 현재 상태 확인
    print("\n[1] 현재 DB 상태")
    tables = ['base_problems', 'problems_blank', 'problems_puzzle', 'problems_guided']
    for table in tables:
        result = db.table(table).select('id', count='exact').execute()
        print(f"  {table}: {result.count} records")

    # 2. 기존 DB 문제로 테스트 (taco_100 사용)
    print("\n[2] 기존 DB 문제 테스트 (taco_100)")
    test_original_id = "taco_100"
    base_problem_id = problem_save.get_base_problem_id(test_original_id)
    print(f"  base_problem_id: {base_problem_id}")

    if base_problem_id:
        # 테스트 유저 ID 생성 (실제로는 JWT에서 추출)
        test_creator_id = "00000000-0000-0000-0000-000000000001"

        # 이미 있는지 확인
        existing = problem_save.find_existing_problem(
            problem_type="blank",
            base_problem_id=base_problem_id,
            language="python"
        )

        if existing:
            print(f"  이미 존재: {existing.get('id')[:8]}...")
        else:
            # 테스트용 blank 문제 저장
            test_result = {
                "original_id": test_original_id,
                "language": "python",
                "code_template": "def solution(n):\n    return n * ___",
                "answers": ["2"]
            }

            save_result = await problem_save.save_generated_problem(
                problem_type="blank",
                generated_data=test_result,
                base_problem_id=base_problem_id,
                creator_id=test_creator_id,
            )
            print(f"  저장 결과: {save_result}")

    # 3. CodeGen 문제 테스트
    print("\n[3] CodeGen 문제 테스트")
    test_codegen_problem = {
        "title": "테스트 CodeGen 문제",
        "description": "이것은 테스트용 CodeGen 문제입니다.",
        "code": {
            "python": "def solution(n):\n    return n * 2"
        },
        "difficulty": "medium",
        "topics": ["DP", "기초"],
        "examples": [
            {"input": "5", "output": "10"},
            {"input": "3", "output": "6"}
        ]
    }

    collected_info = {
        "topics": ["DP", "기초"],
        "difficulty": "medium",
        "language": "python"
    }

    # base_problems에 저장
    saved_base_id = await problem_save.save_codegen_to_base_problems(
        generated_problem=test_codegen_problem,
        collected_info=collected_info
    )

    if saved_base_id:
        print(f"  base_problems에 저장됨: {saved_base_id}")

        # problems_blank에도 저장
        test_blank_result = {
            "original_id": f"codegen_test",
            "language": "python",
            "code_template": "def solution(n):\n    return n * ___",
            "answers": ["2"]
        }

        save_result = await problem_save.save_generated_problem(
            problem_type="blank",
            generated_data=test_blank_result,
            base_problem_id=saved_base_id,
            creator_id="00000000-0000-0000-0000-000000000001",
        )
        print(f"  problems_blank에 저장됨: {save_result}")
    else:
        print("  base_problems 저장 실패!")

    # 4. 최종 상태 확인
    print("\n[4] 최종 DB 상태")
    for table in tables:
        result = db.table(table).select('id', count='exact').execute()
        print(f"  {table}: {result.count} records")

    # 5. CodeGen 문제 확인
    print("\n[5] CodeGen 문제 확인")
    codegen = db.table('base_problems').select('original_id, name, source').eq('source', 'codegen').limit(5).execute()
    print(f"  CodeGen 문제 수: {len(codegen.data)}")
    for p in codegen.data:
        print(f"    - {p['original_id']}: {p['name'][:40]}...")

    print("\n" + "=" * 60)
    print("테스트 완료!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_db_save())
