"""
임베딩 생성 스크립트 v2 (No Chunking)

1. programmers_embeddings: JSON 파일에서 programmers 문제 임베딩 생성
   - base_problems에는 저장하지 않음 (저작권 이슈)
   - RAG 컨텍스트로만 사용

2. problem_embeddings: base_problems 테이블 기준으로 재생성
   - 기존 데이터 삭제 후 새로 생성

⚠️ 청킹 없이 전체 텍스트를 하나의 임베딩으로 저장
- 문제당 1개의 임베딩 (question + solutions 전체)
- 코드 조각 문제 해결
"""

import asyncio
import json
import sys
import os
from typing import List, Dict, Any
from datetime import datetime

# 버퍼링 비활성화 (실시간 출력)
sys.stdout.reconfigure(line_buffering=True)

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import get_supabase_client
from app.services.embedding import embedding_service


# ============================================================
# Text Content 생성 (청킹 없이 전체)
# ============================================================

def create_full_text_content(problem: Dict[str, Any]) -> Dict[str, Any]:
    """
    문제에서 전체 텍스트 컨텐츠 생성 (청킹 없음)

    Returns:
        {"text": 전체 텍스트, "question": 문제설명, "solutions": 솔루션 목록}
    """
    parts = []

    # 1. 문제 설명 (전체)
    question = problem.get("question", "") or ""
    if question.strip():
        parts.append(f"[QUESTION]\n{question.strip()}")

    # 2. 솔루션 코드 (전체, 언어별)
    solutions = problem.get("solutions", []) or []
    solution_list = []

    for sol in solutions:
        if isinstance(sol, dict):
            code = sol.get("code", "")
            lang = sol.get("language", "python")
            if code and code.strip():
                parts.append(f"[SOLUTION:{lang}]\n{code.strip()}")
                solution_list.append({"language": lang, "code": code.strip()})

    # 전체 텍스트 (임베딩용) - 8000자 제한 (OpenAI 토큰 한도)
    full_text = "\n\n".join(parts)[:8000]

    return {
        "text": full_text,
        "question": question.strip()[:3000],  # DB 저장용
        "solutions": solution_list,
    }


# ============================================================
# 1. Programmers Embeddings 생성
# ============================================================

async def generate_programmers_embeddings(
    json_path: str = "/Users/admin/Downloads/codefill/data/programmers/problems_validated_solutions.json",
    batch_size: int = 20,
    clear_existing: bool = True,
):
    """
    Programmers 문제 임베딩 생성 (청킹 없음)

    - base_problems에는 저장하지 않음 (저작권 이슈)
    - programmers_embeddings 테이블에만 저장
    - 문제당 1개 임베딩 (전체 텍스트)
    """
    print("=" * 60)
    print("Programmers Embeddings 생성 (No Chunking)")
    print("=" * 60)

    db = get_supabase_client()

    # JSON 파일 로드
    with open(json_path, "r", encoding="utf-8") as f:
        problems = json.load(f)

    print(f"Total programmers problems: {len(problems)}")

    # 기존 데이터 삭제
    if clear_existing:
        print("Clearing existing programmers_embeddings...")
        try:
            db.table("programmers_embeddings").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
            print("Cleared existing data")
        except Exception as e:
            print(f"Warning: Could not clear existing data: {e}")

    success_count = 0
    error_count = 0

    # 배치 처리
    for batch_start in range(0, len(problems), batch_size):
        batch = problems[batch_start:batch_start + batch_size]

        if (batch_start + 1) % 50 == 0 or batch_start == 0:
            print(f"\n[{batch_start+1}-{min(batch_start+batch_size, len(problems))}/{len(problems)}] Processing batch...")

        try:
            # 배치 텍스트 준비
            texts = []
            valid_problems = []

            for problem in batch:
                content = create_full_text_content(problem)
                if content["text"].strip():
                    texts.append(content["text"])
                    valid_problems.append({
                        "problem": problem,
                        "content": content,
                    })

            if not texts:
                continue

            # OpenAI 임베딩 생성 (배치)
            embeddings = await embedding_service.generate_embeddings_batch(texts, batch_size=batch_size)

            # DB 저장
            for item, embedding in zip(valid_problems, embeddings):
                problem = item["problem"]
                content = item["content"]

                problem_id = problem.get("id", "")
                original_id = problem.get("original_id", problem_id)

                # original_id에서 숫자만 추출 (예: "programmers_389481" -> "389481")
                if isinstance(original_id, str) and original_id.startswith("programmers_"):
                    original_id = original_id.replace("programmers_", "")

                try:
                    # text_content: question + solutions JSON
                    text_content = json.dumps({
                        "question": content["question"],
                        "solutions": content["solutions"][:3],  # 최대 3개 솔루션
                    }, ensure_ascii=False)[:4000]

                    db.table("programmers_embeddings").insert({
                        "problem_id": original_id,
                        "embedding": embedding,
                        "text_content": text_content,
                    }).execute()

                    success_count += 1
                except Exception as e:
                    print(f"  Error storing {original_id}: {e}")
                    error_count += 1

            # Rate limit 방지
            await asyncio.sleep(0.5)

        except Exception as e:
            print(f"  Error processing batch: {e}")
            error_count += len(batch)
            import traceback
            traceback.print_exc()

        # 진행상황 출력
        if (batch_start + batch_size) % 100 == 0:
            print(f"\n=== Progress: {min(batch_start + batch_size, len(problems))}/{len(problems)} ===\n")

    print("\n" + "=" * 60)
    print(f"Programmers Embeddings Complete")
    print(f"Success: {success_count} problems")
    print(f"Errors: {error_count}")
    print("=" * 60)

    return {"success": success_count, "errors": error_count}


# ============================================================
# 2. Problem Embeddings 재생성
# ============================================================

async def regenerate_problem_embeddings(
    batch_size: int = 20,
    clear_existing: bool = True,
):
    """
    base_problems 테이블 기준으로 problem_embeddings 재생성 (청킹 없음)

    - 문제당 1개 임베딩 (전체 텍스트)
    """
    print("=" * 60)
    print("Problem Embeddings 재생성 (No Chunking)")
    print("=" * 60)

    db = get_supabase_client()

    # 기존 데이터 삭제
    if clear_existing:
        print("Clearing existing problem_embeddings...")
        try:
            db.table("problem_embeddings").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
            print("Cleared existing data")
        except Exception as e:
            print(f"Warning: Could not clear existing data: {e}")

    # base_problems 조회
    print("Fetching base_problems...")

    # 페이지네이션으로 전체 조회 (필요한 컬럼만)
    all_problems = []
    offset = 0
    page_size = 50  # 타임아웃 방지를 위해 작게

    while True:
        for retry in range(3):
            try:
                result = db.table("base_problems").select(
                    "id, name, question, solutions"
                ).is_("deleted_at", "null").range(offset, offset + page_size - 1).execute()
                break
            except Exception as e:
                print(f"  Retry {retry+1}/3 for fetching problems (offset={offset}): {e}")
                await asyncio.sleep(2)
                if retry == 2:
                    raise

        if not result.data:
            break
        all_problems.extend(result.data)
        offset += page_size
        if (offset % 500) == 0:
            print(f"  Fetched {len(all_problems)} problems...")
        if len(result.data) < page_size:
            break

    print(f"Total base_problems: {len(all_problems)}")

    # 이미 처리된 problem_id 조회 (--no-clear 옵션 시 건너뛰기 용)
    existing_problem_ids = set()
    if not clear_existing:
        print("Fetching existing embeddings to skip...")
        offset = 0
        page_size = 1000
        while True:
            existing_result = db.table("problem_embeddings").select("problem_id").range(offset, offset + page_size - 1).execute()
            if not existing_result.data:
                break
            existing_problem_ids.update(r["problem_id"] for r in existing_result.data)
            if len(existing_result.data) < page_size:
                break
            offset += page_size
        print(f"Already embedded: {len(existing_problem_ids)} problems")

    # 처리할 문제 필터링
    problems_to_process = [p for p in all_problems if p.get("id") not in existing_problem_ids]
    print(f"Problems to process: {len(problems_to_process)}")

    success_count = 0
    error_count = 0
    skipped_count = len(all_problems) - len(problems_to_process)

    # 배치 처리
    for batch_start in range(0, len(problems_to_process), batch_size):
        batch = problems_to_process[batch_start:batch_start + batch_size]

        if (batch_start + 1) % 100 == 0 or batch_start == 0:
            print(f"\n[{batch_start+1}-{min(batch_start+batch_size, len(problems_to_process))}/{len(problems_to_process)}] Processing batch...")

        try:
            # 배치 텍스트 준비
            texts = []
            valid_problems = []

            for problem in batch:
                content = create_full_text_content(problem)
                if content["text"].strip():
                    texts.append(content["text"])
                    valid_problems.append({
                        "problem": problem,
                        "content": content,
                    })

            if not texts:
                continue

            # OpenAI 임베딩 생성 (배치)
            embeddings = await embedding_service.generate_embeddings_batch(texts, batch_size=batch_size)

            # DB 저장
            for item, embedding in zip(valid_problems, embeddings):
                problem = item["problem"]
                content = item["content"]
                problem_id = problem.get("id")

                try:
                    # text_content: question + solutions JSON
                    text_content = json.dumps({
                        "question": content["question"],
                        "solutions": content["solutions"][:3],
                    }, ensure_ascii=False)[:4000]

                    db.table("problem_embeddings").insert({
                        "problem_id": problem_id,
                        "embedding": embedding,
                        "text_content": text_content,
                    }).execute()

                    success_count += 1
                except Exception as e:
                    print(f"  Error storing {problem_id}: {e}")
                    error_count += 1

            # Rate limit 방지
            await asyncio.sleep(0.5)

        except Exception as e:
            print(f"  Error processing batch: {e}")
            error_count += len(batch)
            import traceback
            traceback.print_exc()

        # 진행상황 출력
        if (batch_start + batch_size) % 200 == 0:
            print(f"\n=== Progress: {min(batch_start + batch_size, len(problems_to_process))}/{len(problems_to_process)} ===\n")

    print("\n" + "=" * 60)
    print(f"Problem Embeddings Complete")
    print(f"Success: {success_count} problems")
    print(f"Skipped: {skipped_count} problems (already embedded)")
    print(f"Errors: {error_count}")
    print("=" * 60)

    return {"success": success_count, "errors": error_count, "skipped": skipped_count}


# ============================================================
# Main
# ============================================================

async def main():
    import argparse

    parser = argparse.ArgumentParser(description="Generate embeddings for problems (No Chunking)")
    parser.add_argument(
        "--target",
        choices=["programmers", "base_problems", "all"],
        default="all",
        help="Which embeddings to generate",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=20,
        help="Batch size for embedding generation",
    )
    parser.add_argument(
        "--no-clear",
        action="store_true",
        help="Do not clear existing data",
    )

    args = parser.parse_args()

    print(f"Target: {args.target}")
    print(f"Batch size: {args.batch_size}")
    print(f"Clear existing: {not args.no_clear}")
    print(f"Embedding model: OpenAI text-embedding-3-small (1536 dims)")
    print(f"Strategy: No Chunking (1 embedding per problem)")
    print()

    if args.target in ["programmers", "all"]:
        await generate_programmers_embeddings(
            batch_size=args.batch_size,
            clear_existing=not args.no_clear,
        )

    if args.target in ["base_problems", "all"]:
        await regenerate_problem_embeddings(
            batch_size=args.batch_size,
            clear_existing=not args.no_clear,
        )

    print("\n=== All Done ===")


if __name__ == "__main__":
    asyncio.run(main())
