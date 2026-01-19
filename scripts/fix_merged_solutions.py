"""
백준 문제의 합쳐진 Python 솔루션 수정 스크립트

문제:
- 원본 데이터에서 두 개 이상의 솔루션이 하나의 코드로 합쳐짐
- 예: 일반 솔루션 + exec 코드골프 버전

수정 방법:
- exec가 포함된 Python 솔루션에서 첫 번째 완전한 솔루션만 추출
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


def extract_first_solution(code: str) -> str:
    """
    합쳐진 코드에서 첫 번째 완전한 솔루션만 추출

    패턴:
    1. 줄바꿈 없이 바로 두 번째 솔루션이 시작되는 경우
    2. exec로 시작하는 코드골프 버전이 뒤에 붙은 경우
    """
    if not code:
        return code

    lines = code.split('\n')

    # exec로 시작하는 별도 솔루션 찾기
    # 패턴: 줄이 'exec(' 또는 'f=lambda'로 시작하면서 앞에 정상 코드가 있는 경우
    result_lines = []
    found_exec_start = False

    for i, line in enumerate(lines):
        stripped = line.strip()

        # exec나 lambda로 시작하는 새로운 솔루션 감지
        # 단, 첫 줄이거나 들여쓰기 안에 있으면 제외
        if i > 0 and not line.startswith(' ') and not line.startswith('\t'):
            if stripped.startswith('exec(') or stripped.startswith('f=lambda'):
                # 앞에 실제 코드가 있었는지 확인
                if any(l.strip() for l in result_lines):
                    found_exec_start = True
                    break

            # 두 번째 솔루션 시작 감지 (같은 변수 재정의)
            # 예: a,b,c=map(int,input().split()) 가 다시 나오는 경우
            if '=' in stripped and 'input()' in stripped:
                # 이미 비슷한 패턴이 앞에 있었는지 확인
                prev_code = '\n'.join(result_lines)
                if 'input()' in prev_code and len(result_lines) > 3:
                    # 새로운 솔루션 시작으로 판단
                    break

        result_lines.append(line)

    result = '\n'.join(result_lines).strip()

    # 결과가 너무 짧으면 원본 반환
    if len(result) < 20:
        return code

    return result


def fix_solution_with_llm_pattern(code: str) -> str:
    """
    더 정밀한 패턴 매칭으로 첫 번째 솔루션 추출
    """
    if not code:
        return code

    # exec가 없는 경우에도 중복 솔루션 체크
    original_code = code
    lines = code.split('\n')

    # 패턴 0: 코드가 exec(로 시작하면 다음 솔루션을 찾아서 사용
    first_line = lines[0].strip() if lines else ""
    if first_line.startswith('exec(') or first_line.startswith('i=input;exec'):
        # exec 이후에 정상 솔루션 찾기
        for i, line in enumerate(lines[1:], 1):
            stripped = line.strip()
            # 정상 솔루션 시작 (for, while, import, def 등)
            if stripped and not stripped.startswith('#'):
                if any(stripped.startswith(kw) for kw in ['for ', 'while ', 'import ', 'def ', 'class ', 'n=', 'a=', 'n,', 'a,']):
                    # 이 줄부터 끝까지가 진짜 솔루션
                    result = '\n'.join(lines[i:]).strip()
                    if len(result) > 30:
                        return result
        return original_code

    # 패턴 1: f=lambda로 시작하는 두 번째 솔루션
    match = re.search(r'\n[a-z]=lambda[^:]+:', code)
    if match and match.start() > 50:
        result = code[:match.start()].strip()
        if len(result) > 30:
            return result

    # 패턴 2: 줄 시작이 exec(로 시작하는 독립된 솔루션
    match = re.search(r'\nexec\([\'"]', code)
    if match and match.start() > 50:
        result = code[:match.start()].strip()
        if len(result) > 30:
            return result

    # 패턴 3: 줄 시작이 i=input 또는 i=lambda 등으로 두 번째 솔루션 시작
    match = re.search(r'\n[a-z]=(?:input|lambda)', code)
    if match and match.start() > 50:
        result = code[:match.start()].strip()
        if len(result) > 30:
            return result

    # 패턴 4: while 1: 또는 for 루프가 반복되는 경우
    main_patterns = [r'\nwhile\s+1:', r'\nwhile\s+True:', r'\nfor\s+_\s+in', r'\nfor\s+i\s+in']
    for pattern in main_patterns:
        matches = list(re.finditer(pattern, code))
        if len(matches) >= 2:
            # 두 번째 발생 위치에서 자르기
            second_match = matches[1]
            if second_match.start() > 50:
                result = code[:second_match.start()].strip()
                if len(result) > 30:
                    return result

    # 패턴 4-1: 같은 import가 반복되는 경우
    import_match = re.search(r'^(import \w+)', code)
    if import_match:
        import_stmt = import_match.group(1)
        # 같은 import가 다시 나오는지 확인
        second_import = code.find('\n' + import_stmt, 10)
        if second_import > 50:
            result = code[:second_import].strip()
            if len(result) > 30:
                return result

    # 패턴 4-2: l=[];로 시작하고 다시 l=[]가 나오는 경우
    if code.startswith('l=[]'):
        second_l = code.find('\nl=[]', 10)
        if second_l > 30:
            result = code[:second_l].strip()
            if len(result) > 30:
                return result

    # 패턴 5: 같은 변수 할당 패턴이 다시 나오는 경우
    seen_input_patterns = set()
    for i, line in enumerate(lines):
        stripped = line.strip()
        # 들여쓰기 없는 줄에서 input() 패턴 찾기
        if not line.startswith(' ') and not line.startswith('\t'):
            if 'input()' in stripped and '=' in stripped:
                # 변수 할당 패턴 추출 (예: a,b,c=)
                var_pattern = stripped.split('=')[0].strip()
                if var_pattern in seen_input_patterns and i > 3:
                    # 두 번째로 같은 패턴 발견 - 여기서 자르기
                    first_part = '\n'.join(lines[:i]).strip()
                    if len(first_part) > 30:
                        return first_part
                seen_input_patterns.add(var_pattern)

    # 패턴 6: import로 시작하는 두 번째 솔루션 (import 없이 시작한 후 import로 다시 시작)
    first_has_import = 'import ' in '\n'.join(lines[:3])
    if not first_has_import:
        match = re.search(r'\nimport\s+', code)
        if match and match.start() > 50:
            result = code[:match.start()].strip()
            if len(result) > 30:
                return result

    # 패턴 7: print(len(set 등 완전히 다른 접근법이 뒤에 붙은 경우
    match = re.search(r'\nprint\(len\(set\(', code)
    if match and match.start() > 30:
        result = code[:match.start()].strip()
        if len(result) > 30:
            return result

    return original_code


def main():
    supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

    # 전체 문제 조회 (페이지네이션)
    print("Fetching all baekjoon problems...")

    all_problems = []
    page_size = 1000
    offset = 0

    while True:
        result = supabase.table("base_problems")\
            .select("id, original_id, name, solutions")\
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

    problems = all_problems
    print(f"Total problems: {len(problems)}")

    updates = []

    for p in problems:
        if not p.get("solutions"):
            continue

        solutions = p["solutions"]
        modified = False
        new_solutions = []

        for sol in solutions:
            if sol.get("language") == "python":
                code = sol.get("code", "")

                # 중복 솔루션이 있을 수 있는 코드 처리
                if len(code) > 80:
                    fixed_code = fix_solution_with_llm_pattern(code)

                    if fixed_code != code and len(fixed_code) > 30:
                        sol = sol.copy()
                        sol["code"] = fixed_code
                        modified = True
                        print(f"\n[{p['original_id']}] {p['name']}")
                        print(f"  Before: {len(code)} chars")
                        print(f"  After:  {len(fixed_code)} chars")

            new_solutions.append(sol)

        if modified:
            updates.append({
                "id": p["id"],
                "original_id": p["original_id"],
                "name": p["name"],
                "solutions": new_solutions
            })

    print(f"\n{'='*50}")
    print(f"Problems to update: {len(updates)}")

    if not updates:
        print("No updates needed!")
        return

    # 미리보기
    print("\n=== Preview ===")
    for u in updates[:3]:
        print(f"- [{u['original_id']}] {u['name']}")
        py_sol = next((s for s in u['solutions'] if s['language'] == 'python'), None)
        if py_sol:
            print(f"  New code preview: {py_sol['code'][:200]}...")

    confirm = input("\nProceed with update? (y/n): ")
    if confirm.lower() != 'y':
        print("Cancelled.")
        return

    # 업데이트 실행
    updated = 0
    errors = []

    for u in updates:
        try:
            supabase.table("base_problems")\
                .update({"solutions": u["solutions"]})\
                .eq("id", u["id"])\
                .execute()
            updated += 1
            print(f"Updated: [{u['original_id']}] {u['name']}")
        except Exception as e:
            errors.append(f"{u['original_id']}: {e}")

    print(f"\n=== Complete ===")
    print(f"Updated: {updated}")
    print(f"Errors: {len(errors)}")

    if errors:
        for err in errors[:5]:
            print(f"  - {err}")


if __name__ == "__main__":
    main()
