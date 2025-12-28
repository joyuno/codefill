#!/usr/bin/env python3
"""
GitHub에서 백준 솔루션 크롤링
- 여러 레포에서 Python, Java, C++ 솔루션 수집
- 문제 번호별로 매핑
"""

import requests
import json
import time
import re
import base64
from pathlib import Path
from typing import Dict, List, Optional, Set
from collections import defaultdict

# 설정
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "baekjoon"
SOLUTIONS_FILE = OUTPUT_DIR / "github_solutions.json"
PROBLEMS_FILE = OUTPUT_DIR / "problems_filtered_final_12071.json"

# GitHub API
GITHUB_API = "https://api.github.com"
HEADERS = {
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "Baekjoon-Solution-Crawler"
}

# GitHub 토큰 (선택사항 - rate limit 증가)
# HEADERS["Authorization"] = "token YOUR_GITHUB_TOKEN"

# 크롤링할 레포 목록 (레포, 솔루션 경로 패턴)
REPOS = [
    # 대형 레포들
    ("tony9402/baekjoon", "solution"),
    ("JoinNova/baekjoon", ""),
    ("Zeta611/baekjoon-solutions", ""),
    ("Baekjoon-Solutions/Baekjoon_Solutions", ""),
    ("alstn2468/baekjoon-online-judge", ""),
    ("mori8/baekjoon-algorithm-python", ""),
    ("ChoiCube84/baekjoon-solutions", ""),
    ("ChaeWonKong/algorithm-with-python", "baekjoon"),
]

# 언어별 확장자
LANG_EXT = {
    ".py": "python",
    ".java": "java",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".c": "cpp",
}


def extract_problem_id(path: str, filename: str) -> Optional[str]:
    """파일 경로/이름에서 문제 번호 추출"""
    # 다양한 패턴 시도
    patterns = [
        r'/(\d{4,5})/',           # /1001/
        r'/(\d{4,5})\.',          # /1001.py
        r'[_-](\d{4,5})[_.-]',    # _1001_ or -1001-
        r'^(\d{4,5})\.',          # 1001.py
        r'(\d{4,5})\.(?:py|java|cpp|cc|c)$',  # 1001.py
        r'boj[_-]?(\d{4,5})',     # boj_1001 or boj1001
        r'백준[_-]?(\d{4,5})',    # 백준_1001
    ]

    full_path = f"{path}/{filename}"

    for pattern in patterns:
        match = re.search(pattern, full_path, re.IGNORECASE)
        if match:
            pid = match.group(1)
            # 유효한 백준 문제 번호 범위 (1000~40000)
            if 1000 <= int(pid) <= 40000:
                return pid

    return None


def get_file_content(repo: str, path: str) -> Optional[str]:
    """GitHub에서 파일 내용 가져오기"""
    url = f"{GITHUB_API}/repos/{repo}/contents/{path}"

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("encoding") == "base64":
                content = base64.b64decode(data["content"]).decode("utf-8", errors="ignore")
                return content
    except Exception as e:
        print(f"    파일 로드 실패: {path} ({e})")

    return None


def crawl_repo_recursive(repo: str, path: str = "", solutions: Dict = None,
                         visited: Set = None, depth: int = 0) -> Dict:
    """레포지토리 재귀 탐색"""
    if solutions is None:
        solutions = defaultdict(lambda: {"python": None, "java": None, "cpp": None})
    if visited is None:
        visited = set()

    if depth > 5:  # 너무 깊이 들어가지 않도록
        return solutions

    url = f"{GITHUB_API}/repos/{repo}/contents/{path}"

    if url in visited:
        return solutions
    visited.add(url)

    try:
        response = requests.get(url, headers=HEADERS, timeout=15)

        # Rate limit 확인
        remaining = int(response.headers.get("X-RateLimit-Remaining", 0))
        if remaining < 10:
            reset_time = int(response.headers.get("X-RateLimit-Reset", 0))
            wait_time = max(0, reset_time - time.time()) + 5
            print(f"\n⚠️ Rate limit 도달. {wait_time:.0f}초 대기...")
            time.sleep(wait_time)
            return solutions

        if response.status_code != 200:
            return solutions

        items = response.json()
        if not isinstance(items, list):
            return solutions

        for item in items:
            name = item.get("name", "")
            item_type = item.get("type", "")
            item_path = item.get("path", "")

            if item_type == "dir":
                # 재귀 탐색
                time.sleep(0.5)
                crawl_repo_recursive(repo, item_path, solutions, visited, depth + 1)

            elif item_type == "file":
                # 파일 확장자 확인
                ext = Path(name).suffix.lower()
                if ext not in LANG_EXT:
                    continue

                # 문제 번호 추출
                problem_id = extract_problem_id(path, name)
                if not problem_id:
                    continue

                lang = LANG_EXT[ext]

                # 이미 있으면 스킵
                if solutions[problem_id][lang]:
                    continue

                # 파일 내용 가져오기
                time.sleep(0.3)
                content = get_file_content(repo, item_path)

                if content and len(content) > 10:
                    solutions[problem_id][lang] = content
                    print(f"    ✓ {problem_id} ({lang})")

    except Exception as e:
        print(f"  탐색 오류: {path} ({e})")

    return solutions


def crawl_all_repos() -> Dict:
    """모든 레포에서 솔루션 수집"""
    all_solutions = defaultdict(lambda: {"python": None, "java": None, "cpp": None})

    print("=" * 60)
    print("🚀 GitHub 백준 솔루션 크롤링 시작")
    print("=" * 60)

    for repo, base_path in REPOS:
        print(f"\n📂 {repo} 크롤링 중...")

        try:
            repo_solutions = crawl_repo_recursive(repo, base_path)

            # 병합
            for pid, langs in repo_solutions.items():
                for lang, code in langs.items():
                    if code and not all_solutions[pid][lang]:
                        all_solutions[pid][lang] = code

            # 진행 상황
            total = len(all_solutions)
            python_count = sum(1 for s in all_solutions.values() if s["python"])
            java_count = sum(1 for s in all_solutions.values() if s["java"])
            cpp_count = sum(1 for s in all_solutions.values() if s["cpp"])

            print(f"  현재 수집: {total}개 문제 (Python: {python_count}, Java: {java_count}, C++: {cpp_count})")

            time.sleep(2)  # 레포 간 딜레이

        except Exception as e:
            print(f"  ❌ {repo} 실패: {e}")
            continue

    return dict(all_solutions)


def save_solutions(solutions: Dict):
    """솔루션 저장"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(SOLUTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(solutions, f, ensure_ascii=False, indent=2)

    print(f"\n💾 저장 완료: {SOLUTIONS_FILE}")


def merge_with_problems(solutions: Dict):
    """문제 JSON에 솔루션 병합"""
    if not PROBLEMS_FILE.exists():
        print(f"❌ 문제 파일 없음: {PROBLEMS_FILE}")
        return

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
    output_file = OUTPUT_DIR / "problems_with_solutions.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(problems, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 병합 완료: {matched}/{len(problems)}개 문제에 솔루션 추가")
    print(f"💾 저장: {output_file}")


def print_stats(solutions: Dict):
    """통계 출력"""
    total = len(solutions)
    python_count = sum(1 for s in solutions.values() if s.get("python"))
    java_count = sum(1 for s in solutions.values() if s.get("java"))
    cpp_count = sum(1 for s in solutions.values() if s.get("cpp"))

    all_three = sum(1 for s in solutions.values()
                    if s.get("python") and s.get("java") and s.get("cpp"))

    print("\n" + "=" * 60)
    print("📊 크롤링 결과")
    print("=" * 60)
    print(f"  총 문제: {total}개")
    print(f"  Python: {python_count}개 ({python_count/total*100:.1f}%)" if total else "")
    print(f"  Java: {java_count}개 ({java_count/total*100:.1f}%)" if total else "")
    print(f"  C++: {cpp_count}개 ({cpp_count/total*100:.1f}%)" if total else "")
    print(f"  3언어 모두: {all_three}개 ({all_three/total*100:.1f}%)" if total else "")
    print("=" * 60)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="GitHub 백준 솔루션 크롤러")
    parser.add_argument("--merge", action="store_true", help="문제 파일에 병합")
    parser.add_argument("--token", type=str, help="GitHub 토큰 (rate limit 증가)")

    args = parser.parse_args()

    if args.token:
        HEADERS["Authorization"] = f"token {args.token}"
        print("✅ GitHub 토큰 사용 (rate limit: 5000/hour)")
    else:
        print("⚠️ GitHub 토큰 없음 (rate limit: 60/hour)")
        print("   토큰 추가: --token YOUR_TOKEN")

    # 크롤링
    solutions = crawl_all_repos()

    # 저장
    save_solutions(solutions)

    # 통계
    print_stats(solutions)

    # 병합
    if args.merge:
        merge_with_problems(solutions)
