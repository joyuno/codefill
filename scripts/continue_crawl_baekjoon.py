#!/usr/bin/env python3
"""
백준 크롤링 이어서 진행
- 체크포인트 파일에서 로드
- 이미 크롤링된 문제 제외하고 계속 진행
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
DELAY = 1.5

# 티어 설정 (브론즈 4,5 제외)
TIERS = ",".join(str(i) for i in range(3, 31))


def get_problem_list_page(page: int = 1) -> List[Dict]:
    """문제 리스트 페이지에서 문제 정보 추출"""
    url = f"{BASE_URL}/problemset?sort=submit_desc&tier={TIERS}&page={page}"

    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
    except Exception as e:
        print(f"  페이지 {page} 로드 실패: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    problems = []

    tbody = soup.select_one("tbody")
    if not tbody:
        return []

    rows = tbody.select("tr")
    for row in rows:
        cols = row.select("td")
        if len(cols) < 6:
            continue

        try:
            problem_id = cols[0].text.strip()
            title_elem = cols[1].select_one("a")
            title = title_elem.text.strip() if title_elem else cols[1].text.strip()
            ratio_text = cols[5].text.strip().replace("%", "")
            ratio = float(ratio_text) if ratio_text else 0
            accepted = cols[3].text.strip().replace(",", "")
            accepted = int(accepted) if accepted else 0

            problems.append({
                "id": int(problem_id),
                "title": title,
                "ratio": ratio,
                "accepted": accepted
            })
        except:
            continue

    return problems


def get_total_pages() -> int:
    """전체 페이지 수 확인"""
    url = f"{BASE_URL}/problemset?sort=submit_desc&tier={TIERS}"

    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
    except Exception as e:
        print(f"페이지 로드 실패: {e}")
        return 0

    soup = BeautifulSoup(response.text, "html.parser")
    pagination = soup.select(".pagination a")
    max_page = 1

    for link in pagination:
        href = link.get("href", "")
        if "page=" in href:
            try:
                page_part = href.split("page=")[-1]
                if "&" in page_part:
                    page_str = page_part.split("&")[0]
                else:
                    page_str = page_part
                page_num = int(page_str)
                max_page = max(max_page, page_num)
            except:
                pass

    return max_page


def download_image(url: str, save_dir: Path) -> Optional[str]:
    """이미지 다운로드"""
    try:
        if url.startswith("//"):
            url = "https:" + url
        elif url.startswith("/"):
            url = urljoin(BASE_URL, url)

        parsed = urlparse(url)
        ext = Path(parsed.path).suffix or ".png"
        if ext.lower() not in [".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".bmp"]:
            ext = ".png"

        url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
        filename = f"{url_hash}{ext}"
        save_path = save_dir / filename

        if save_path.exists():
            return filename

        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()

        save_path.write_bytes(response.content)
        return filename

    except Exception as e:
        print(f"    이미지 다운로드 실패: {url[:50]}... ({e})")
        return None


def extract_and_download_images(html: str, problem_id: int) -> tuple:
    """HTML에서 이미지 추출 및 다운로드"""
    img_dir = IMAGES_DIR / str(problem_id)
    img_dir.mkdir(parents=True, exist_ok=True)

    images = []
    modified_html = html

    img_pattern = r'<img[^>]+src=["\']([^"\']+)["\']'
    matches = re.findall(img_pattern, html, re.IGNORECASE)

    for original_url in matches:
        local_filename = download_image(original_url, img_dir)

        if local_filename:
            local_path = f"images/{problem_id}/{local_filename}"
            modified_html = modified_html.replace(original_url, local_path)
            images.append({
                "original_url": original_url,
                "local_path": local_path
            })

    return modified_html, images


def tier_to_difficulty(tier_name: str) -> str:
    """티어를 difficulty로 변환"""
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


def get_problem_detail(problem_id: int) -> Optional[Dict]:
    """문제 상세 크롤링"""
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

    title_tag = soup.select_one("#problem_title")
    if not title_tag:
        return None
    title = title_tag.text.strip()

    description_html = ""
    description_text = ""

    desc_tag = soup.select_one("#problem_description")
    if desc_tag:
        description_html = str(desc_tag)
        description_text = desc_tag.get_text(separator="\n").strip()

    input_html = ""
    input_text = ""
    input_tag = soup.select_one("#problem_input")
    if input_tag:
        input_html = str(input_tag)
        input_text = input_tag.get_text(separator="\n").strip()

    output_html = ""
    output_text = ""
    output_tag = soup.select_one("#problem_output")
    if output_tag:
        output_html = str(output_tag)
        output_text = output_tag.get_text(separator="\n").strip()

    full_html = description_html
    if input_html:
        full_html += f"\n<h3>입력</h3>\n{input_html}"
    if output_html:
        full_html += f"\n<h3>출력</h3>\n{output_html}"

    images = []
    if full_html:
        full_html, images = extract_and_download_images(full_html, problem_id)

    question_parts = []
    if description_text:
        question_parts.append(description_text)
    if input_text:
        question_parts.append(f"\n\n### 입력\n{input_text}")
    if output_text:
        question_parts.append(f"\n\n### 출력\n{output_text}")
    question = "".join(question_parts)

    inputs = []
    outputs = []
    sample_inputs = soup.select("[id^='sample-input-']")
    sample_outputs = soup.select("[id^='sample-output-']")

    for inp, out in zip(sample_inputs, sample_outputs):
        inputs.append(inp.text.strip())
        outputs.append(out.text.strip())

    info_table = soup.select_one("#problem-info")
    time_limit = None
    memory_limit = None
    if info_table:
        tds = info_table.select("td")
        if len(tds) >= 2:
            time_limit = tds[0].text.strip()
            memory_limit = tds[1].text.strip()

    tags = []
    tag_elements = soup.select(".spoiler-link")
    for tag in tag_elements:
        tags.append(tag.text.strip())

    return {
        "id": f"baekjoon_{problem_id}",
        "question": question,
        "question_html": full_html,
        "images": images if images else None,
        "solutions": [],
        "input_output": json.dumps({"inputs": inputs, "outputs": outputs}, ensure_ascii=False) if inputs else None,
        "difficulty": "unknown",
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
    """solved.ac에서 난이도 가져오기"""
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


def save_checkpoint(problems: list, count: int):
    """체크포인트 저장"""
    checkpoint_file = OUTPUT_DIR / f"checkpoint_filtered_{count}.json"
    with open(checkpoint_file, "w", encoding="utf-8") as f:
        json.dump(problems, f, ensure_ascii=False, indent=2)
    print(f"\n  💾 체크포인트 저장: {checkpoint_file}")


def continue_crawl(checkpoint_file: str, max_ratio: float = 70.0, top_percent: float = 50.0):
    """체크포인트에서 이어서 크롤링"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    # 1. 체크포인트 로드
    checkpoint_path = OUTPUT_DIR / checkpoint_file
    if not checkpoint_path.exists():
        print(f"체크포인트 파일을 찾을 수 없습니다: {checkpoint_path}")
        return

    with open(checkpoint_path, "r", encoding="utf-8") as f:
        crawled_problems = json.load(f)

    crawled_ids = set(int(p["original_id"]) for p in crawled_problems)
    print(f"✅ 체크포인트 로드 완료: {len(crawled_problems)}개 문제")

    # 2. 전체 문제 리스트 수집
    print("\n📋 문제 리스트 수집 중...")
    total_pages = get_total_pages()
    target_pages = int(total_pages * (top_percent / 100))
    print(f"  전체 페이지: {total_pages}, 대상 페이지: {target_pages}")

    all_problems = []
    for page in range(1, target_pages + 1):
        print(f"  [{page}/{target_pages}]", end=" ", flush=True)
        problems = get_problem_list_page(page)
        filtered = [p for p in problems if p["ratio"] <= max_ratio]
        all_problems.extend(filtered)
        print(f"✓ {len(filtered)}개")
        time.sleep(0.3)

    # 3. 아직 크롤링 안된 문제 필터링
    remaining = [p for p in all_problems if p["id"] not in crawled_ids]

    print(f"\n📊 현황:")
    print(f"  • 전체 대상: {len(all_problems)}개")
    print(f"  • 완료: {len(crawled_ids)}개")
    print(f"  • 남은 문제: {len(remaining)}개")

    if not remaining:
        print("\n✅ 모든 문제가 이미 크롤링되었습니다!")
        return crawled_problems

    # 4. 크롤링 계속
    print(f"\n🚀 남은 {len(remaining)}개 문제 크롤링 시작...")

    total_images = 0
    failed = []

    for i, problem_info in enumerate(remaining, 1):
        pid = problem_info["id"]
        current_total = len(crawled_problems)
        print(f"[{i}/{len(remaining)}] (총 {current_total}) 문제 {pid}...", end=" ", flush=True)

        problem = get_problem_detail(pid)
        if problem:
            img_count = len(problem.get("images") or [])
            total_images += img_count
            if img_count > 0:
                print(f"({img_count}img)", end=" ")

            tier_info = get_solved_ac_tier(pid)
            if tier_info:
                problem["difficulty"] = tier_info["difficulty"]
                if not problem["tags"]:
                    problem["tags"] = tier_info["tags"]
            time.sleep(0.3)

            problem["acceptance_rate"] = problem_info["ratio"]
            crawled_problems.append(problem)
            print(f"✓ {problem['difficulty']}")
        else:
            failed.append(pid)
            print("✗")

        # 100개마다 저장
        if len(crawled_problems) % 100 == 0:
            save_checkpoint(crawled_problems, len(crawled_problems))

        time.sleep(DELAY)

    # 5. 최종 저장
    final_file = OUTPUT_DIR / f"problems_filtered_final_{len(crawled_problems)}.json"
    with open(final_file, "w", encoding="utf-8") as f:
        json.dump(crawled_problems, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 60)
    print("✅ 크롤링 완료!")
    print(f"  • 총 문제: {len(crawled_problems)}개")
    print(f"  • 이번 추가: {len(remaining) - len(failed)}개")
    print(f"  • 실패: {len(failed)}개")
    print(f"  • 이미지: {total_images}개")
    print(f"  • 저장: {final_file}")
    print("=" * 60)

    return crawled_problems


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="백준 크롤링 이어서 진행")
    parser.add_argument("--checkpoint", type=str, default="checkpoint_filtered_3200.json",
                        help="체크포인트 파일명")
    parser.add_argument("--max-ratio", type=float, default=70.0)
    parser.add_argument("--top-percent", type=float, default=50.0)

    args = parser.parse_args()

    continue_crawl(args.checkpoint, args.max_ratio, args.top_percent)
