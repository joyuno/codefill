#!/usr/bin/env python3
"""
프로그래머스 코딩테스트 문제 크롤러
https://programmers.co.kr
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 설정
BASE_URL = "https://school.programmers.co.kr"
API_URL = "https://school.programmers.co.kr/api/v1"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "programmers"
DELAY = 2.0


def get_problem_list_api(page: int = 1, per_page: int = 20) -> list:
    """API로 문제 목록 가져오기"""
    url = f"{API_URL}/school/challenges"
    params = {
        "page": page,
        "perPage": per_page,
        "order": "recent"
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "application/json"
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json().get("challenges", [])
    except Exception as e:
        print(f"API 에러: {e}")

    return []


def setup_driver():
    """Selenium 드라이버 설정"""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")

    driver = webdriver.Chrome(options=options)
    return driver


def get_problem_with_selenium(driver, lesson_id: int) -> dict | None:
    """Selenium으로 문제 상세 크롤링"""
    url = f"{BASE_URL}/learn/courses/30/lessons/{lesson_id}"

    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "guide-section"))
        )
        time.sleep(1)  # 추가 렌더링 대기

        soup = BeautifulSoup(driver.page_source, "html.parser")

        # 문제 제목
        title = ""
        title_tag = soup.select_one(".challenge-title")
        if title_tag:
            title = title_tag.text.strip()

        # 난이도
        difficulty = ""
        level_tag = soup.select_one(".level-badge, .problem-level")
        if level_tag:
            difficulty = level_tag.text.strip()

        # 문제 설명
        description = ""
        desc_tag = soup.select_one(".guide-section-description")
        if desc_tag:
            description = desc_tag.get_text(separator="\n").strip()

        # 제한사항
        constraints = ""
        constraint_section = soup.select_one(".guide-section:has(h5:-soup-contains('제한사항'))")
        if constraint_section:
            constraints = constraint_section.get_text(separator="\n").strip()

        # 입출력 예
        examples = []
        example_table = soup.select_one(".guide-section table")
        if example_table:
            rows = example_table.select("tr")
            headers = [th.text.strip() for th in rows[0].select("th")] if rows else []
            for row in rows[1:]:
                cells = [td.text.strip() for td in row.select("td")]
                if cells:
                    example = dict(zip(headers, cells))
                    examples.append(example)

        # 입출력 예 설명
        example_desc = ""
        example_section = soup.select(".guide-section")
        for section in example_section:
            h5 = section.select_one("h5")
            if h5 and "입출력 예 설명" in h5.text:
                example_desc = section.get_text(separator="\n").strip()
                break

        return {
            "id": lesson_id,
            "title": title,
            "difficulty": difficulty,
            "description": description,
            "constraints": constraints,
            "examples": examples,
            "example_description": example_desc,
            "url": url,
            "source": "programmers"
        }

    except Exception as e:
        print(f"  Error: {e}")
        return None


def get_problem_requests(lesson_id: int) -> dict | None:
    """requests로 문제 크롤링 (로그인 불필요한 경우)"""
    url = f"{BASE_URL}/learn/courses/30/lessons/{lesson_id}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, "html.parser")

        # 문제 제목
        title = ""
        title_tag = soup.select_one("title")
        if title_tag:
            title = title_tag.text.replace("| 프로그래머스 스쿨", "").strip()

        # JavaScript에서 데이터 추출
        scripts = soup.select("script")
        for script in scripts:
            if script.string and "lesson" in str(script.string):
                # JSON 데이터 추출 시도
                match = re.search(r'lesson:\s*({.*?})\s*,', script.string, re.DOTALL)
                if match:
                    try:
                        data = json.loads(match.group(1))
                        return {
                            "id": lesson_id,
                            "title": data.get("title", title),
                            "description": data.get("description", ""),
                            "difficulty": data.get("level", ""),
                            "url": url,
                            "source": "programmers"
                        }
                    except:
                        pass

        return {
            "id": lesson_id,
            "title": title,
            "url": url,
            "source": "programmers"
        }

    except Exception as e:
        print(f"  Error: {e}")
        return None


def crawl_problem_list():
    """문제 목록 페이지 크롤링"""
    url = f"{BASE_URL}/learn/challenges"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }

    all_problems = []
    page = 1

    while True:
        print(f"페이지 {page} 크롤링 중...")
        response = requests.get(f"{url}?page={page}", headers=headers, timeout=10)

        if response.status_code != 200:
            break

        soup = BeautifulSoup(response.text, "html.parser")
        problem_cards = soup.select(".challenge-item, .list-item")

        if not problem_cards:
            break

        for card in problem_cards:
            link = card.select_one("a")
            if link:
                href = link.get("href", "")
                match = re.search(r"/lessons/(\d+)", href)
                if match:
                    lesson_id = int(match.group(1))
                    title = card.select_one(".title, .challenge-title")
                    level = card.select_one(".level, .badge")

                    all_problems.append({
                        "id": lesson_id,
                        "title": title.text.strip() if title else "",
                        "level": level.text.strip() if level else ""
                    })

        page += 1
        time.sleep(DELAY)

        if page > 50:  # 안전장치
            break

    return all_problems


def crawl_with_selenium(lesson_ids: list):
    """Selenium으로 상세 크롤링"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    driver = setup_driver()
    problems = []

    print(f"프로그래머스 문제 크롤링 시작: {len(lesson_ids)}개")
    print("=" * 50)

    try:
        for i, lesson_id in enumerate(lesson_ids, 1):
            print(f"[{i}/{len(lesson_ids)}] {lesson_id} 크롤링 중...", end=" ")

            problem = get_problem_with_selenium(driver, lesson_id)
            if problem:
                problems.append(problem)
                print(f"✓ {problem.get('title', 'No title')}")
            else:
                print("✗ 실패")

            # 10개마다 저장
            if i % 10 == 0:
                save_problems(problems, f"checkpoint_{i}")

            time.sleep(DELAY)

    finally:
        driver.quit()

    # 최종 저장
    save_problems(problems, "all_problems")

    print("=" * 50)
    print(f"완료! 총 {len(problems)}개 크롤링")

    return problems


def save_problems(problems: list, filename: str):
    """문제 저장"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_file = OUTPUT_DIR / f"{filename}.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(problems, f, ensure_ascii=False, indent=2)

    print(f"저장: {output_file}")


# 알려진 인기 문제 ID 목록
POPULAR_LESSONS = [
    # Level 1
    12906, 12903, 12910, 12912, 12915, 12916, 12917, 12918, 12919, 12921,
    12922, 12925, 12926, 12928, 12930, 12931, 12932, 12933, 12934, 12935,
    # Level 2
    12909, 12911, 12914, 12924, 12939, 12941, 12945, 12949, 12951, 12953,
    42577, 42578, 42583, 42584, 42585, 42586, 42587, 42588, 42746, 42747,
    # Level 3
    42579, 42627, 42628, 42629, 42839, 42840, 42841, 42842, 42860, 42861,
    42862, 42883, 42884, 42885, 42886, 42888, 42889, 42890, 42891, 42892,
    # 카카오 기출
    60057, 60058, 60059, 60060, 60061, 60062, 67256, 67257, 67258, 67259,
    72410, 72411, 72412, 72413, 72414, 72415, 77484, 77485, 77486, 81301,
]


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="프로그래머스 문제 크롤러")
    parser.add_argument("--mode", choices=["list", "detail", "popular"], default="popular",
                        help="크롤링 모드: list(목록), detail(상세), popular(인기문제)")
    parser.add_argument("--ids", type=str, help="크롤링할 문제 ID들 (콤마 구분)")

    args = parser.parse_args()

    if args.mode == "list":
        problems = crawl_problem_list()
        save_problems(problems, "problem_list")

    elif args.mode == "detail" and args.ids:
        ids = [int(x.strip()) for x in args.ids.split(",")]
        crawl_with_selenium(ids)

    elif args.mode == "popular":
        print("인기 문제 크롤링을 시작합니다...")
        print("Selenium이 필요합니다. 설치: pip install selenium")
        crawl_with_selenium(POPULAR_LESSONS)
