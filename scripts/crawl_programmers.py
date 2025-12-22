#!/usr/bin/env python3
"""
프로그래머스 코딩테스트 문제 크롤러 (Playwright 버전)
통일된 스키마로 저장 + 이미지 다운로드
"""

import json
import time
import re
import hashlib
import requests
from pathlib import Path
from typing import Optional, Dict, List
from urllib.parse import urljoin, urlparse

# 설정
BASE_URL = "https://school.programmers.co.kr"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "programmers"
IMAGES_DIR = OUTPUT_DIR / "images"
DELAY = 2.0

# 이미지 다운로드용 헤더
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def download_image(url: str, save_dir: Path) -> Optional[str]:
    """이미지 다운로드 후 로컬 경로 반환"""
    try:
        # URL 정규화
        if url.startswith("//"):
            url = "https:" + url
        elif url.startswith("/"):
            url = urljoin(BASE_URL, url)

        # 파일명 생성 (URL 해시 + 확장자)
        parsed = urlparse(url)
        ext = Path(parsed.path).suffix or ".png"
        if ext not in [".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"]:
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


def extract_and_download_images(html: str, lesson_id: int) -> tuple:
    """
    HTML에서 이미지 추출, 다운로드, URL 치환
    Returns: (치환된 HTML, 이미지 목록)
    """
    # 문제별 이미지 폴더
    img_dir = IMAGES_DIR / str(lesson_id)
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
            # 상대 경로로 치환 (images/{lesson_id}/{filename})
            local_path = f"images/{lesson_id}/{local_filename}"
            modified_html = modified_html.replace(original_url, local_path)
            images.append({
                "original_url": original_url,
                "local_path": local_path
            })

    return modified_html, images


def get_problem_list_from_page(page_num: int, browser_page) -> List[Dict]:
    """한 페이지에서 문제 목록 추출 (Playwright)"""
    url = f"{BASE_URL}/learn/challenges?order=recent&page={page_num}&languages=python3"

    try:
        browser_page.goto(url, wait_until="networkidle", timeout=30000)
        time.sleep(1)
    except Exception as e:
        print(f"  페이지 {page_num} 로드 실패: {e}")
        return []

    problems = []
    rows = browser_page.query_selector_all("tr")

    for row in rows:
        try:
            a_tag = row.query_selector("a[href*='lessons']")
            if not a_tag:
                continue

            href = a_tag.get_attribute("href")
            if not href:
                continue

            match = re.search(r'/lessons/(\d+)', href)
            if not match:
                continue

            lesson_id = int(match.group(1))

            # level 추출
            level = ""
            level_elem = row.query_selector("td.level span, span.level")
            if level_elem:
                level = level_elem.text_content().strip()

            # title 추출
            title = ""
            title_elem = row.query_selector("td.title, div.title")
            if title_elem:
                title = title_elem.text_content().strip()

            problems.append({
                "id": lesson_id,
                "title": title,
                "level": level,
                "href": href
            })

        except Exception as e:
            continue

    return problems


def create_browser_context(playwright):
    """안티 디텍션 브라우저 컨텍스트 생성"""
    browser = playwright.chromium.launch(
        headless=True,
        args=['--disable-blink-features=AutomationControlled']
    )
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        viewport={'width': 1920, 'height': 1080},
    )
    page = context.new_page()
    # Webdriver 감지 우회
    page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
    """)
    return browser, context, page


def get_all_problem_ids(max_pages: int = 28) -> List[Dict]:
    """모든 페이지에서 문제 ID 수집"""
    from playwright.sync_api import sync_playwright

    all_problems = []

    print(f"문제 목록 수집 중 (1~{max_pages} 페이지)...")
    print("Playwright 브라우저 시작...")
    print("=" * 50)

    with sync_playwright() as p:
        browser, context, page = create_browser_context(p)

        for page_num in range(1, max_pages + 1):
            print(f"[{page_num}/{max_pages}] 페이지 크롤링 중...", end=" ", flush=True)

            problems = get_problem_list_from_page(page_num, page)
            all_problems.extend(problems)

            print(f"✓ {len(problems)}개 발견 (총: {len(all_problems)}개)")
            time.sleep(DELAY)

        browser.close()

    print("=" * 50)
    print(f"총 {len(all_problems)}개 문제 발견")

    # 중복 제거
    unique = {p["id"]: p for p in all_problems}
    all_problems = list(unique.values())
    print(f"중복 제거 후: {len(all_problems)}개")

    return all_problems


def level_to_difficulty(level: str) -> str:
    """레벨을 difficulty로 변환
    Lv0, Lv1 → easy
    Lv2 → medium
    Lv3 → medium_hard
    Lv4 → hard
    Lv5, Lv6+ → very_hard
    """
    level_clean = re.sub(r'[^\d]', '', level)
    if not level_clean:
        return "unknown"

    level_num = int(level_clean)
    if level_num <= 1:
        return "easy"
    elif level_num == 2:
        return "medium"
    elif level_num == 3:
        return "medium_hard"
    elif level_num == 4:
        return "hard"
    else:
        return "very_hard"


def get_problem_detail(lesson_id: int, list_info: Dict, browser_page) -> Optional[Dict]:
    """문제 상세 크롤링 (Playwright로 description + 이미지 가져오기)"""
    url = f"{BASE_URL}/learn/courses/30/lessons/{lesson_id}"

    try:
        browser_page.goto(url, wait_until="domcontentloaded", timeout=30000)
        time.sleep(3)  # 충분한 대기 시간
    except Exception as e:
        print(f"  페이지 로드 실패: {e}")
        return None

    # 제목 추출
    title = list_info.get("title", "")
    if not title:
        title_elem = browser_page.query_selector("title")
        if title_elem:
            title = title_elem.text_content().replace("| 프로그래머스 스쿨", "").strip()
            title = title.replace("코딩테스트 연습 - ", "")

    # level
    level = list_info.get("level", "")

    # description - #tour2 (문제 설명 컨테이너)에서 HTML로 추출
    description_html = ""
    description_text = ""
    images = []

    desc_elem = browser_page.query_selector("#tour2")
    if desc_elem:
        # HTML과 텍스트 둘 다 추출
        description_html = desc_elem.inner_html()
        description_text = desc_elem.text_content().strip()

        # 이미지 다운로드 및 URL 치환
        if description_html:
            description_html, images = extract_and_download_images(description_html, lesson_id)
            if images:
                print(f"({len(images)}개 이미지)", end=" ")

    # 대안: .guide-section
    if not description_text:
        guide_elem = browser_page.query_selector(".guide-section")
        if guide_elem:
            description_html = guide_elem.inner_html()
            description_text = guide_elem.text_content().strip()
            if description_html:
                description_html, images = extract_and_download_images(description_html, lesson_id)

    # 입출력 예시 추출 - inputs/outputs 배열 형식
    inputs = []
    outputs = []
    tables = browser_page.query_selector_all("#tour2 table, .guide-section table")
    for table in tables:
        headers = table.query_selector_all("th")
        if headers:
            header_texts = [h.text_content().strip().lower() for h in headers]
            # 입출력 테이블인지 확인
            has_input = any("입력" in h or "input" in h or "매개변수" in h or "parameter" in h for h in header_texts)
            has_output = any("출력" in h or "output" in h or "result" in h or "return" in h for h in header_texts)

            if has_input or has_output:
                # 출력 컬럼 인덱스 찾기 (보통 마지막 컬럼)
                output_idx = -1
                for idx, h in enumerate(header_texts):
                    if "출력" in h or "output" in h or "result" in h or "return" in h:
                        output_idx = idx
                        break

                rows = table.query_selector_all("tbody tr")
                for row in rows:
                    cells = row.query_selector_all("td")
                    if len(cells) >= 2:
                        # 입력: 출력 컬럼 제외한 모든 컬럼 합치기
                        input_parts = []
                        for idx, cell in enumerate(cells):
                            if idx != output_idx and idx != len(cells) - 1:
                                # 헤더명과 값을 함께 저장
                                if idx < len(headers):
                                    header_name = headers[idx].text_content().strip()
                                    input_parts.append(f"{header_name} = {cell.text_content().strip()}")
                                else:
                                    input_parts.append(cell.text_content().strip())

                        if input_parts:
                            inputs.append("\n".join(input_parts))
                        else:
                            inputs.append(cells[0].text_content().strip())

                        # 출력: 마지막 컬럼 또는 output_idx
                        if output_idx >= 0 and output_idx < len(cells):
                            outputs.append(cells[output_idx].text_content().strip())
                        else:
                            outputs.append(cells[-1].text_content().strip())

    # 제한사항 추출
    constraints = ""
    constraint_headers = browser_page.query_selector_all("h5")
    for h5 in constraint_headers:
        if "제한" in h5.text_content():
            next_elem = h5.evaluate("el => el.nextElementSibling")
            if next_elem:
                constraints = browser_page.evaluate("el => el ? el.textContent : ''", next_elem)
                break

    # 태그 추출 (있다면)
    tags = []
    tag_elems = browser_page.query_selector_all(".algorithm-tag, .tag")
    for tag in tag_elems:
        tags.append(tag.text_content().strip())

    # 통일된 스키마로 반환 (level 필드 제거)
    return {
        "id": f"programmers_{lesson_id}",
        "question": description_text,  # 텍스트 버전
        "question_html": description_html,  # HTML 버전 (이미지 위치 보존)
        "images": images if images else None,  # 이미지 목록
        "solutions": [],  # 프로그래머스는 솔루션 비공개
        "input_output": json.dumps({"inputs": inputs, "outputs": outputs}, ensure_ascii=False) if inputs else None,
        "difficulty": level_to_difficulty(level),
        "tags": tags if tags else None,
        "name": f"[프로그래머스 {lesson_id}] {title}",
        "source": "programmers",
        "url": url,
        "starter_code": None,
        "explanation": constraints if constraints else None,
        "language": "python",
        "time_limit": None,
        "memory_limit": None,
        "original_id": str(lesson_id)
    }


def crawl_problems(problem_list: List[Dict], skip_existing: bool = True):
    """문제 상세 크롤링"""
    from playwright.sync_api import sync_playwright

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    output_file = OUTPUT_DIR / "problems.json"
    existing_problems = []
    existing_ids = set()

    if skip_existing and output_file.exists():
        try:
            with open(output_file, "r", encoding="utf-8") as f:
                existing_problems = json.load(f)
                existing_ids = {p.get("original_id") or str(p.get("id", "")).replace("programmers_", "") for p in existing_problems}
                print(f"기존 크롤링된 문제: {len(existing_ids)}개")
        except:
            pass

    # 스킵할 ID 제외
    new_problems = [p for p in problem_list if str(p["id"]) not in existing_ids]
    skipped = len(problem_list) - len(new_problems)

    if skipped > 0:
        print(f"스킵 (이미 크롤링됨): {skipped}개")

    problems = existing_problems.copy()
    failed = []
    total_images = 0

    print(f"프로그래머스 문제 상세 크롤링: {len(new_problems)}개")
    print(f"이미지 저장 경로: {IMAGES_DIR}")
    print("=" * 50)

    with sync_playwright() as p:
        browser, context, page = create_browser_context(p)

        for i, prob in enumerate(new_problems, 1):
            lesson_id = prob["id"]

            print(f"[{i}/{len(new_problems)}] {lesson_id} 크롤링 중...", end=" ", flush=True)

            detail = get_problem_detail(lesson_id, prob, page)
            if detail and detail.get("question"):
                problems.append(detail)
                img_count = len(detail.get("images") or [])
                total_images += img_count
                print(f"✓ {detail['difficulty']} {detail['name'][:30]}")
            else:
                failed.append(lesson_id)
                print("✗ 실패 (description 없음)")

            # 10개마다 저장
            if i % 10 == 0:
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(problems, f, ensure_ascii=False, indent=2)
                print(f"  [저장됨: {len(problems)}개, 이미지: {total_images}개]")

            time.sleep(DELAY)

        browser.close()

    # 최종 저장
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(problems, f, ensure_ascii=False, indent=2)

    print("=" * 50)
    print(f"완료! 총: {len(problems)}개 (신규: {len(new_problems)-len(failed)}, 기존: {len(existing_ids)}, 실패: {len(failed)})")
    print(f"다운로드된 이미지: {total_images}개")
    print(f"저장: {output_file}")

    return problems


def save_problem_list(problem_list: List[Dict]):
    """문제 목록 저장"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_file = OUTPUT_DIR / "problem_list.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(problem_list, f, ensure_ascii=False, indent=2)

    print(f"문제 목록 저장: {output_file}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="프로그래머스 문제 크롤러")
    parser.add_argument("--pages", type=int, default=28, help="크롤링할 페이지 수 (기본: 28)")
    parser.add_argument("--list-only", action="store_true", help="문제 목록만 수집")
    parser.add_argument("--detail-only", action="store_true", help="기존 목록으로 상세만 크롤링")
    parser.add_argument("--no-skip", action="store_true", help="기존 문제도 다시 크롤링")

    args = parser.parse_args()

    if args.detail_only:
        list_file = OUTPUT_DIR / "problem_list.json"
        if list_file.exists():
            with open(list_file, "r") as f:
                problem_list = json.load(f)
            print(f"기존 목록 로드: {len(problem_list)}개")
            crawl_problems(problem_list, skip_existing=not args.no_skip)
        else:
            print("문제 목록 파일이 없습니다. 먼저 목록을 수집하세요.")
    else:
        problem_list = get_all_problem_ids(args.pages)
        save_problem_list(problem_list)

        if not args.list_only:
            crawl_problems(problem_list, skip_existing=not args.no_skip)
