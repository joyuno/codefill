"""
백준 문제의 question 컬럼 포맷팅 수정 스크립트

문제:
- 불필요한 줄바꿈이 많아 가독성이 떨어짐
- 예: "fibonacci(3)\n은" → "fibonacci(3)은"

수정 내용:
1. 코드/함수 뒤 조사 연결: ")\n은" → ")은"
2. 연속 빈줄 정리: 3줄 이상 → 2줄
3. 문장 중간 불필요한 줄바꿈 제거
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from supabase import create_client

# Supabase 설정
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://qukgaiwdusuxcswsqhjo.supabase.co")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_SERVICE_KEY:
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend", ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if line.startswith("SUPABASE_SERVICE_ROLE_KEY="):
                    SUPABASE_SERVICE_KEY = line.split("=", 1)[1].strip().strip('"\'')
                    break


def fix_question_formatting(text: str) -> str:
    """question 텍스트 포맷팅 수정"""
    if not text:
        return text

    # 1. \r\n → \n 통일
    text = text.replace('\r\n', '\n')

    # 2. 코드 블록 보존을 위해 임시 마킹
    # ```code``` 형태의 코드 블록 보존
    code_blocks = []
    def save_code_block(match):
        code_blocks.append(match.group(0))
        return f"__CODE_BLOCK_{len(code_blocks)-1}__"

    text = re.sub(r'```[\s\S]*?```', save_code_block, text)

    # 3. 들여쓰기된 코드 라인은 보존 (4칸 이상 들여쓰기)
    # 하지만 중괄호가 있는 코드는 보존해야 함

    # 4. 함수/괄호 뒤 조사 연결
    # )\n은, )\n는, )\n을, )\n를, )\n와, )\n과, )\n이, )\n가, )\n의, )\n에, )\n도, )\n로
    korean_particles = r'(은|는|을|를|와|과|이|가|의|에|도|로|으로|라고|라면|면|고|며)'
    text = re.sub(rf'\)\n({korean_particles})', r')\1', text)

    # 5. 숫자/영단어 뒤 조사 연결
    # 1\n은, N\n이 등
    text = re.sub(rf'(\w)\n({korean_particles})(\s|\.|\,|$)', r'\1\2\3', text)

    # 6. 연속 빈줄 정리 (3줄 이상 → 2줄)
    text = re.sub(r'\n{3,}', '\n\n', text)

    # 7. 문장 중간 불필요한 줄바꿈 제거
    # 한글로 끝나고 한글로 시작하는 경우 (마침표/느낌표/물음표 없이)
    # 예: "일어난다.\n\n\nfibonacci" 는 유지하지만
    # "fibonacci(3)\n은" 은 이미 위에서 처리됨

    # 8. 코드 블록 복원
    for i, block in enumerate(code_blocks):
        text = text.replace(f"__CODE_BLOCK_{i}__", block)

    # 9. 앞뒤 공백 정리
    text = text.strip()

    return text


def main():
    supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

    # 백준 문제만 조회 (source = 'baekjoon')
    print("Fetching baekjoon problems...")

    # 페이지네이션으로 전체 조회
    all_problems = []
    page_size = 1000
    offset = 0

    while True:
        result = supabase.table("base_problems")\
            .select("id, question")\
            .eq("source", "baekjoon")\
            .range(offset, offset + page_size - 1)\
            .execute()

        if not result.data:
            break

        all_problems.extend(result.data)
        print(f"Fetched {len(all_problems)} problems...")

        if len(result.data) < page_size:
            break
        offset += page_size

    print(f"Total problems to process: {len(all_problems)}")

    # 수정이 필요한 문제 필터링
    updates = []
    for p in all_problems:
        original = p["question"]
        fixed = fix_question_formatting(original)

        if original != fixed:
            updates.append({
                "id": p["id"],
                "question": fixed
            })

    print(f"Problems needing update: {len(updates)}")

    if not updates:
        print("No updates needed!")
        return

    # 예시 출력
    print("\n=== Example Fix ===")
    sample = updates[0] if updates else None
    if sample:
        original = next(p["question"] for p in all_problems if p["id"] == sample["id"])
        print("BEFORE:")
        print(original[:500])
        print("\nAFTER:")
        print(sample["question"][:500])

    # 확인 후 업데이트
    confirm = input("\nProceed with update? (y/n): ")
    if confirm.lower() != 'y':
        print("Cancelled.")
        return

    # 배치 업데이트
    BATCH_SIZE = 100
    updated_count = 0
    errors = []

    for i in range(0, len(updates), BATCH_SIZE):
        batch = updates[i:i + BATCH_SIZE]

        for item in batch:
            try:
                supabase.table("base_problems")\
                    .update({"question": item["question"]})\
                    .eq("id", item["id"])\
                    .execute()
                updated_count += 1
            except Exception as e:
                errors.append(f"{item['id']}: {e}")

        print(f"Updated {updated_count}/{len(updates)}")

    print(f"\n=== Complete ===")
    print(f"Updated: {updated_count}")
    print(f"Errors: {len(errors)}")

    if errors:
        for err in errors[:5]:
            print(f"  - {err}")


if __name__ == "__main__":
    main()
