#!/usr/bin/env python3
"""
백준 온라인 저지 문제 크롤러
https://www.acmicpc.net
이미지 다운로드 + 통합 스키마
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
import hashlib
from pathlib import Path
from typing import Optional, List, Dict
from urllib.parse import urljoin, urlparse

# 설정
BASE_URL = "https://www.acmicpc.net"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "baekjoon"
IMAGES_DIR = OUTPUT_DIR / "images"
DELAY = 1.5  # 요청 간 딜레이 (초)


def download_image(url: str, save_dir: Path) -> Optional[str]:
    """이미지 다운로드 후 로컬 파일명 반환"""
    try:
        # URL 정규화
        if url.startswith("//"):
            url = "https:" + url
        elif url.startswith("/"):
            url = urljoin(BASE_URL, url)

        # 파일명 생성 (URL 해시 + 확장자)
        parsed = urlparse(url)
        ext = Path(parsed.path).suffix or ".png"
        if ext.lower() not in [".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".bmp"]:
            ext = ".png"

        url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
        filename = f"{url_hash}{ext}"
        save_path = save_dir / filename

        # 이미 다운로드된 경우 스킵
        if save_path.exists():
            return filename

        # 다운로드
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()

        save_path.write_bytes(response.content)
        return filename

    except Exception as e:
        print(f"    이미지 다운로드 실패: {url[:50]}... ({e})")
        return None


def extract_and_download_images(html: str, problem_id: int) -> tuple:
    """
    HTML에서 이미지 추출, 다운로드, URL 치환
    Returns: (치환된 HTML, 이미지 목록)
    """
    # 문제별 이미지 폴더
    img_dir = IMAGES_DIR / str(problem_id)
    img_dir.mkdir(parents=True, exist_ok=True)

    images = []
    modified_html = html

    # img 태그에서 src 추출
    img_pattern = r'<img[^>]+src=["\']([^"\']+)["\']'
    matches = re.findall(img_pattern, html, re.IGNORECASE)

    for original_url in matches:
        # 이미지 다운로드
        local_filename = download_image(original_url, img_dir)

        if local_filename:
            # 상대 경로로 치환 (images/{problem_id}/{filename})
            local_path = f"images/{problem_id}/{local_filename}"
            modified_html = modified_html.replace(original_url, local_path)
            images.append({
                "original_url": original_url,
                "local_path": local_path
            })

    return modified_html, images


def tier_to_difficulty(tier_name: str) -> str:
    """solved.ac 티어를 difficulty로 변환
    Bronze → easy
    Silver → medium
    Gold → medium_hard
    Platinum → hard
    Diamond/Ruby → very_hard
    """
    if not tier_name:
        return "unknown"

    tier_lower = tier_name.lower()
    if "bronze" in tier_lower:
        return "easy"
    elif "silver" in tier_lower:
        return "medium"
    elif "gold" in tier_lower:
        return "medium_hard"
    elif "platinum" in tier_lower:
        return "hard"
    elif "diamond" in tier_lower or "ruby" in tier_lower:
        return "very_hard"
    else:
        return "unknown"


def get_problem(problem_id: int) -> Optional[Dict]:
    """단일 문제 크롤링 (이미지 포함)"""
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

    # 문제 설명 (HTML 보존)
    description_html = ""
    description_text = ""
    images = []

    desc_tag = soup.select_one("#problem_description")
    if desc_tag:
        description_html = str(desc_tag)
        description_text = desc_tag.get_text(separator="\n").strip()

    # 입력 형식 (HTML 보존)
    input_html = ""
    input_text = ""
    input_tag = soup.select_one("#problem_input")
    if input_tag:
        input_html = str(input_tag)
        input_text = input_tag.get_text(separator="\n").strip()

    # 출력 형식 (HTML 보존)
    output_html = ""
    output_text = ""
    output_tag = soup.select_one("#problem_output")
    if output_tag:
        output_html = str(output_tag)
        output_text = output_tag.get_text(separator="\n").strip()

    # 전체 HTML 합치기 (이미지 위치 보존)
    full_html = description_html
    if input_html:
        full_html += f"\n<h3>입력</h3>\n{input_html}"
    if output_html:
        full_html += f"\n<h3>출력</h3>\n{output_html}"

    # 이미지 다운로드 및 URL 치환
    if full_html:
        full_html, images = extract_and_download_images(full_html, problem_id)

    # 텍스트 버전 question
    question_parts = []
    if description_text:
        question_parts.append(description_text)
    if input_text:
        question_parts.append(f"\n\n### 입력\n{input_text}")
    if output_text:
        question_parts.append(f"\n\n### 출력\n{output_text}")
    question = "".join(question_parts)

    # 예제 입출력 - inputs/outputs 형식
    inputs = []
    outputs = []
    sample_inputs = soup.select("[id^='sample-input-']")
    sample_outputs = soup.select("[id^='sample-output-']")

    for inp, out in zip(sample_inputs, sample_outputs):
        inputs.append(inp.text.strip())
        outputs.append(out.text.strip())

    # 제한 (시간, 메모리)
    info_table = soup.select_one("#problem-info")
    time_limit = None
    memory_limit = None
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

    return {
        "id": f"baekjoon_{problem_id}",
        "question": question,
        "question_html": full_html,  # HTML 버전 (이미지 위치 보존)
        "images": images if images else None,
        "solutions": [],
        "input_output": json.dumps({"inputs": inputs, "outputs": outputs}, ensure_ascii=False) if inputs else None,
        "difficulty": "unknown",  # solved.ac에서 업데이트됨
        "tags": tags if tags else None,
        "name": f"[백준 {problem_id}] {title}",
        "source": "baekjoon",
        "url": url,
        "starter_code": None,
        "explanation": None,
        "language": "python",
        "time_limit": time_limit,
        "memory_limit": memory_limit,
        "original_id": str(problem_id)
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
            tier_name = tier_names[tier] if tier < len(tier_names) else "Unknown"
            return {
                "tier_name": tier_name,
                "difficulty": tier_to_difficulty(tier_name),
                "tags": [t["key"] for t in data.get("tags", [])]
            }
    except:
        pass
    return None


def crawl_problems(start_id: int, end_id: int, include_tier: bool = True):
    """범위 내 문제들 크롤링"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    problems = []
    failed = []
    total_images = 0

    print(f"백준 문제 크롤링 시작: {start_id} ~ {end_id}")
    print(f"저장 경로: {OUTPUT_DIR}")
    print(f"이미지 저장 경로: {IMAGES_DIR}")
    print("=" * 50)

    for pid in range(start_id, end_id + 1):
        print(f"[{pid}/{end_id}] 크롤링 중...", end=" ", flush=True)

        problem = get_problem(pid)
        if problem:
            # 이미지 카운트
            img_count = len(problem.get("images") or [])
            total_images += img_count
            if img_count > 0:
                print(f"({img_count}개 이미지)", end=" ")

            # solved.ac 난이도 추가
            if include_tier:
                tier_info = get_solved_ac_tier(pid)
                if tier_info:
                    problem["difficulty"] = tier_info["difficulty"]
                    if not problem["tags"]:
                        problem["tags"] = tier_info["tags"]
                time.sleep(0.3)  # solved.ac API 딜레이

            problems.append(problem)
            print(f"✓ {problem['difficulty']} {problem['name'][:30]}")
        else:
            failed.append(pid)
            print("✗ 실패/없음")

        # 500개마다 중간 저장
        if len(problems) % 500 == 0 and problems:
            save_checkpoint(problems, start_id, pid)
            print(f"  [저장됨: {len(problems)}개, 이미지: {total_images}개]")

        time.sleep(DELAY)

    # 최종 저장
    output_file = OUTPUT_DIR / f"problems_{start_id}_{end_id}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(problems, f, ensure_ascii=False, indent=2)

    print("=" * 50)
    print(f"완료! 성공: {len(problems)}, 실패: {len(failed)}")
    print(f"다운로드된 이미지: {total_images}개")
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
