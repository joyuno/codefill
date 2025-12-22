#!/usr/bin/env python3
"""
백준 온라인 저지 문제 크롤러
https://www.acmicpc.net
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import os
from pathlib import Path
from typing import Optional, List, Dict

# 설정
BASE_URL = "https://www.acmicpc.net"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "baekjoon"
DELAY = 1.5  # 요청 간 딜레이 (초)


def get_problem(problem_id: int) -> Optional[Dict]:
    """단일 문제 크롤링"""
    url = f"{BASE_URL}/problem/{problem_id}"

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 404:
            return None
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"  Error fetching {problem_id}: {e}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    # 문제 제목
    title_tag = soup.select_one("#problem_title")
    if not title_tag:
        return None
    title = title_tag.text.strip()

    # 문제 설명
    description = ""
    desc_tag = soup.select_one("#problem_description")
    if desc_tag:
        description = desc_tag.get_text(separator="\n").strip()

    # 입력 형식
    input_format = ""
    input_tag = soup.select_one("#problem_input")
    if input_tag:
        input_format = input_tag.get_text(separator="\n").strip()

    # 출력 형식
    output_format = ""
    output_tag = soup.select_one("#problem_output")
    if output_tag:
        output_format = output_tag.get_text(separator="\n").strip()

    # 예제 입출력
    examples = []
    sample_inputs = soup.select("[id^='sample-input-']")
    sample_outputs = soup.select("[id^='sample-output-']")

    for i, (inp, out) in enumerate(zip(sample_inputs, sample_outputs), 1):
        examples.append({
            "input": inp.text.strip(),
            "output": out.text.strip()
        })

    # 제한 (시간, 메모리)
    info_table = soup.select_one("#problem-info")
    time_limit = ""
    memory_limit = ""
    if info_table:
        tds = info_table.select("td")
        if len(tds) >= 2:
            time_limit = tds[0].text.strip()
            memory_limit = tds[1].text.strip()

    # 알고리즘 분류 (태그)
    tags = []
    tag_elements = soup.select(".spoiler-link")
    for tag in tag_elements:
        tags.append(tag.text.strip())

    # 난이도 (solved.ac 연동 필요 - 별도 API)
    difficulty = None

    return {
        "id": problem_id,
        "title": title,
        "description": description,
        "input_format": input_format,
        "output_format": output_format,
        "examples": examples,
        "time_limit": time_limit,
        "memory_limit": memory_limit,
        "tags": tags,
        "difficulty": difficulty,
        "url": url,
        "source": "baekjoon"
    }


def get_solved_ac_tier(problem_id: int) -> Optional[Dict]:
    """solved.ac에서 문제 난이도 가져오기"""
    url = f"https://solved.ac/api/v3/problem/show?problemId={problem_id}"

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            data = response.json()
            tier_names = [
                "Unrated", "Bronze V", "Bronze IV", "Bronze III", "Bronze II", "Bronze I",
                "Silver V", "Silver IV", "Silver III", "Silver II", "Silver I",
                "Gold V", "Gold IV", "Gold III", "Gold II", "Gold I",
                "Platinum V", "Platinum IV", "Platinum III", "Platinum II", "Platinum I",
                "Diamond V", "Diamond IV", "Diamond III", "Diamond II", "Diamond I",
                "Ruby V", "Ruby IV", "Ruby III", "Ruby II", "Ruby I"
            ]
            tier = data.get("level", 0)
            return {
                "tier": tier,
                "tier_name": tier_names[tier] if tier < len(tier_names) else "Unknown",
                "tags": [t["key"] for t in data.get("tags", [])]
            }
    except:
        pass
    return None


def crawl_problems(start_id: int, end_id: int, include_tier: bool = True):
    """범위 내 문제들 크롤링"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    problems = []
    failed = []

    print(f"백준 문제 크롤링 시작: {start_id} ~ {end_id}")
    print(f"저장 경로: {OUTPUT_DIR}")
    print("=" * 50)

    for pid in range(start_id, end_id + 1):
        print(f"[{pid}/{end_id}] 크롤링 중...", end=" ")

        problem = get_problem(pid)
        if problem:
            # solved.ac 난이도 추가
            if include_tier:
                tier_info = get_solved_ac_tier(pid)
                if tier_info:
                    problem["difficulty"] = tier_info["tier_name"]
                    problem["tier"] = tier_info["tier"]
                    if not problem["tags"]:
                        problem["tags"] = tier_info["tags"]
                time.sleep(0.3)  # solved.ac API 딜레이

            problems.append(problem)
            print(f"✓ {problem['title']}")
        else:
            failed.append(pid)
            print("✗ 실패/없음")

        # 10개마다 중간 저장
        if len(problems) % 10 == 0 and problems:
            save_checkpoint(problems, start_id, pid)

        time.sleep(DELAY)

    # 최종 저장
    output_file = OUTPUT_DIR / f"problems_{start_id}_{end_id}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(problems, f, ensure_ascii=False, indent=2)

    print("=" * 50)
    print(f"완료! 성공: {len(problems)}, 실패: {len(failed)}")
    print(f"저장: {output_file}")

    return problems


def save_checkpoint(problems: list, start_id: int, current_id: int):
    """중간 저장"""
    checkpoint_file = OUTPUT_DIR / f"checkpoint_{start_id}_{current_id}.json"
    with open(checkpoint_file, "w", encoding="utf-8") as f:
        json.dump(problems, f, ensure_ascii=False, indent=2)


def crawl_by_tag(tag: str, max_problems: int = 100):
    """특정 태그의 문제들 크롤링"""
    # 태그별 문제 목록 페이지에서 문제 ID 추출
    url = f"{BASE_URL}/problemset?sort=ac_desc&algo={tag}"
    # ... 구현 필요
    pass


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="백준 문제 크롤러")
    parser.add_argument("--start", type=int, default=1000, help="시작 문제 번호")
    parser.add_argument("--end", type=int, default=1010, help="끝 문제 번호")
    parser.add_argument("--no-tier", action="store_true", help="solved.ac 난이도 제외")

    args = parser.parse_args()

    crawl_problems(args.start, args.end, include_tier=not args.no_tier)
