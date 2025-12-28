#!/usr/bin/env python3
"""
GitHub 레포를 로컬에 clone 후 솔루션 수집
- API 제한 없이 빠른 수집
- Python, Java, C++ 솔루션 수집
"""

import subprocess
import json
import re
import shutil
from pathlib import Path
from typing import Dict, Optional
from collections import defaultdict

# 설정
BASE_DIR = Path(__file__).parent.parent
OUTPUT_DIR = BASE_DIR / "data" / "baekjoon"
CLONE_DIR = BASE_DIR / "temp_repos"
SOLUTIONS_FILE = OUTPUT_DIR / "github_solutions.json"
PROBLEMS_FILE = OUTPUT_DIR / "problems_filtered_final_12071.json"

# 크롤링할 레포 목록 (확장)
REPOS = [
    # 대형/인기 레포
    "tony9402/baekjoon",
    "encrypted-def/basic-algo-lecture",
    "JoinNova/baekjoon",
    "ChoiCube84/baekjoon-solutions",

    # Python 레포
    "mori8/baekjoon-algorithm-python",
    "ChaeWonKong/algorithm-with-python",
    "TopGun1405/BaekJoonOJ-Python",
    "tjdms4327/Baekjoon_Python",
    "SeoJangSeok/Baekjoon_Python",
    "sihyunkimm/Baekjoon-python",
    "LifeIsRightward/python_baekjoon",
    "steve5535/baekjoon-python",
    "Junhee8649/BaekjoonPython",
    "gyugyu99/baekjoon-python",
    "Shin-ye-jin/Baekjoon_python",
    "sujin1018/BaekJoon-Python",
    "TaeWooKim-SCH/baekjoon_python",
    "Yunjuchan/baekjoon-java-python",
    "chulhee23/BOJ-algorithm-python",
    "Donsworkout/boj_algorithm_python",

    # Java 레포
    "DDing77/Algorithm_BOJ-java",
    "minseonkkim/Algorithm_BOJ",

    # C++ / 다중 언어 레포
    "Zeta611/baekjoon-solutions",
    "alstn2468/baekjoon-online-judge",
    "arcane222-algorithm/BOJ",
    "junttang/BOJ-AlgorithmPractice",
    "moonwonki/BOJ_Algorithm",
    "Isaac-Lee/BOJ-Algorithm",
    "Donsworkout/boj_algorithm",
    "SOOJEONGKIMM/BOJ_algorithm",
    "yoonjaecho/Algorithm_BOJ",
    "Eighteeen/BOJ_Algorithm_Study",
]

# 언어별 확장자
LANG_EXT = {
    ".py": "python",
    ".java": "java",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".c": "cpp",  # C도 cpp로 취급
}


def extract_problem_id(file_path: str) -> Optional[str]:
    """파일 경로에서 문제 번호 추출"""
    patterns = [
        r'/(\d{4,5})/',           # /1001/
        r'/(\d{4,5})\.',          # /1001.py
        r'[_-](\d{4,5})[_.-]',    # _1001_ or -1001-
        r'/(\d{4,5})\.(?:py|java|cpp|cc|c)$',
        r'boj[_-]?(\d{4,5})',
        r'백준[_-]?(\d{4,5})',
        r'^(\d{4,5})\.(?:py|java|cpp|cc|c)$',
    ]

    for pattern in patterns:
        match = re.search(pattern, file_path, re.IGNORECASE)
        if match:
            pid = match.group(1)
            if 1000 <= int(pid) <= 40000:
                return pid

    return None


def clone_repo(repo: str) -> Optional[Path]:
    """레포지토리 클론"""
    repo_name = repo.replace("/", "_")
    repo_path = CLONE_DIR / repo_name

    if repo_path.exists():
        print(f"  이미 존재: {repo_name}")
        return repo_path

    url = f"https://github.com/{repo}.git"

    try:
        print(f"  클론 중: {repo}...", end=" ", flush=True)
        result = subprocess.run(
            ["git", "clone", "--depth", "1", url, str(repo_path)],
            capture_output=True,
            text=True,
            timeout=120
        )
        if result.returncode == 0:
            print("✓")
            return repo_path
        else:
            print(f"✗ ({result.stderr[:50]})")
            return None
    except Exception as e:
        print(f"✗ ({e})")
        return None


def scan_repo(repo_path: Path, target_pids: set) -> Dict:
    """레포에서 솔루션 파일 스캔"""
    solutions = defaultdict(lambda: {"python": None, "java": None, "cpp": None})

    for ext, lang in LANG_EXT.items():
        # 해당 확장자 파일 모두 찾기
        for file_path in repo_path.rglob(f"*{ext}"):
            # .git 폴더 제외
            if ".git" in str(file_path):
                continue

            # 문제 번호 추출
            pid = extract_problem_id(str(file_path))
            if not pid:
                continue

            # 우리 문제 목록에 있는지 확인
            if target_pids and pid not in target_pids:
                continue

            # 이미 있으면 스킵
            if solutions[pid][lang]:
                continue

            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                if len(content) > 20:  # 너무 짧은 파일 제외
                    solutions[pid][lang] = content
            except:
                pass

    return dict(solutions)


def load_problem_ids() -> set:
    """문제 파일에서 ID 목록 로드"""
    if not PROBLEMS_FILE.exists():
        return set()

    with open(PROBLEMS_FILE, "r", encoding="utf-8") as f:
        problems = json.load(f)

    return {p.get("original_id", "") for p in problems}


def merge_solutions(all_solutions: Dict, new_solutions: Dict) -> Dict:
    """솔루션 병합"""
    for pid, langs in new_solutions.items():
        if pid not in all_solutions:
            all_solutions[pid] = {"python": None, "java": None, "cpp": None}

        for lang, code in langs.items():
            if code and not all_solutions[pid].get(lang):
                all_solutions[pid][lang] = code

    return all_solutions


def save_solutions(solutions: Dict):
    """솔루션 저장"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(SOLUTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(solutions, f, ensure_ascii=False, indent=2)

    print(f"💾 저장 완료: {SOLUTIONS_FILE}")


def merge_with_problems(solutions: Dict):
    """문제 JSON에 솔루션 병합"""
    if not PROBLEMS_FILE.exists():
        print(f"❌ 문제 파일 없음: {PROBLEMS_FILE}")
        return 0

    with open(PROBLEMS_FILE, "r", encoding="utf-8") as f:
        problems = json.load(f)

    matched = 0
    for problem in problems:
        pid = problem.get("original_id", "")

        if pid in solutions:
            sol_data = solutions[pid]
            new_solutions = []

            for lang in ["python", "java", "cpp"]:
                if sol_data.get(lang):
                    new_solutions.append({
                        "language": lang,
                        "code": sol_data[lang]
                    })

            if new_solutions:
                problem["solutions"] = new_solutions
                matched += 1

    # 저장
    output_file = OUTPUT_DIR / "problems_with_github_solutions.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(problems, f, ensure_ascii=False, indent=2)

    print(f"✅ 병합 완료: {matched}/{len(problems)}개 문제")
    print(f"💾 저장: {output_file}")

    return matched


def print_stats(solutions: Dict, total_problems: int = 0):
    """통계 출력"""
    total = len(solutions)
    python_count = sum(1 for s in solutions.values() if s.get("python"))
    java_count = sum(1 for s in solutions.values() if s.get("java"))
    cpp_count = sum(1 for s in solutions.values() if s.get("cpp"))

    all_three = sum(1 for s in solutions.values()
                    if s.get("python") and s.get("java") and s.get("cpp"))

    print("\n" + "=" * 60)
    print("📊 수집 결과")
    print("=" * 60)
    print(f"  수집된 문제: {total}개" + (f" / {total_problems}개 ({total/total_problems*100:.1f}%)" if total_problems else ""))
    print(f"  Python: {python_count}개")
    print(f"  Java: {java_count}개")
    print(f"  C++: {cpp_count}개")
    print(f"  3언어 모두: {all_three}개")
    print("=" * 60)


def cleanup():
    """임시 폴더 정리"""
    if CLONE_DIR.exists():
        print(f"\n🗑️ 임시 폴더 정리: {CLONE_DIR}")
        shutil.rmtree(CLONE_DIR)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="GitHub 백준 솔루션 로컬 크롤러")
    parser.add_argument("--merge", action="store_true", help="문제 파일에 병합")
    parser.add_argument("--keep", action="store_true", help="클론된 레포 유지")
    parser.add_argument("--resume", action="store_true", help="기존 솔루션 이어서")

    args = parser.parse_args()

    # 문제 ID 로드
    target_pids = load_problem_ids()
    print(f"📋 대상 문제 수: {len(target_pids)}개")

    # 기존 솔루션 로드
    all_solutions = {}
    if args.resume and SOLUTIONS_FILE.exists():
        with open(SOLUTIONS_FILE, "r", encoding="utf-8") as f:
            all_solutions = json.load(f)
        print(f"📂 기존 솔루션 로드: {len(all_solutions)}개")

    # 클론 디렉토리 생성
    CLONE_DIR.mkdir(parents=True, exist_ok=True)

    print("\n" + "=" * 60)
    print("🚀 GitHub 레포 클론 및 스캔 시작")
    print("=" * 60)

    for repo in REPOS:
        print(f"\n📂 {repo}")

        # 클론
        repo_path = clone_repo(repo)
        if not repo_path:
            continue

        # 스캔
        print(f"  스캔 중...", end=" ", flush=True)
        repo_solutions = scan_repo(repo_path, target_pids)
        print(f"✓ {len(repo_solutions)}개 문제 발견")

        # 병합
        all_solutions = merge_solutions(all_solutions, repo_solutions)

        # 중간 저장
        save_solutions(all_solutions)

        # 진행 상황
        python_count = sum(1 for s in all_solutions.values() if s.get("python"))
        java_count = sum(1 for s in all_solutions.values() if s.get("java"))
        cpp_count = sum(1 for s in all_solutions.values() if s.get("cpp"))
        print(f"  현재 총계: {len(all_solutions)}개 (Py:{python_count}, Java:{java_count}, C++:{cpp_count})")

    # 최종 통계
    print_stats(all_solutions, len(target_pids))

    # 문제 파일에 병합
    if args.merge:
        merge_with_problems(all_solutions)

    # 정리
    if not args.keep:
        cleanup()

    print("\n✅ 완료!")


if __name__ == "__main__":
    main()
