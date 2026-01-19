#!/usr/bin/env python3
"""
백준 문제 question 필드 LaTeX 형식으로 재크롤링

validated_problems_clean.json의 문제들에 대해
백준에서 다시 크롤링하여 수학 기호(아래첨자, 위첨자)를
LaTeX 형식으로 변환하여 저장합니다.
"""

import json
import re
import time
import asyncio
import aiohttp
from pathlib import Path
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Tuple
import html


# 경로 설정
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data" / "baekjoon" / "data_baekjoon"
INPUT_FILE = DATA_DIR / "validated_problems_clean.json"
OUTPUT_FILE = DATA_DIR / "questions_latex.json"
CHECKPOINT_FILE = DATA_DIR / "crawl_checkpoint.json"

# 백준 URL
BAEKJOON_URL = "https://www.acmicpc.net/problem/{}"

# Rate limiting
REQUEST_DELAY = 0.5  # 초
CONCURRENT_REQUESTS = 3  # 동시 요청 수


def html_to_latex_text(html_content: str) -> str:
    """
    HTML을 LaTeX 수식이 포함된 텍스트로 변환

    - <sub>x</sub> → _{x} 또는 $_{x}$
    - <sup>x</sup> → ^{x} 또는 $^{x}$
    - 수식 컨텍스트 고려
    """
    if not html_content:
        return ""

    soup = BeautifulSoup(html_content, 'html.parser')

    def process_node(node) -> str:
        if node.name is None:  # 텍스트 노드
            return html.unescape(str(node))

        if node.name == 'sub':
            content = ''.join(process_node(child) for child in node.children)
            # 짧은 아래첨자는 인라인 LaTeX로
            return f'$_{{{content}}}$'

        if node.name == 'sup':
            content = ''.join(process_node(child) for child in node.children)
            return f'$^{{{content}}}$'

        if node.name == 'var':
            content = ''.join(process_node(child) for child in node.children)
            return f'${content}$'

        if node.name in ['p', 'div']:
            content = ''.join(process_node(child) for child in node.children)
            return content.strip() + '\n\n'

        if node.name == 'br':
            return '\n'

        if node.name == 'ul':
            items = []
            for li in node.find_all('li', recursive=False):
                item_content = ''.join(process_node(child) for child in li.children)
                items.append(f'- {item_content.strip()}')
            return '\n'.join(items) + '\n'

        if node.name == 'ol':
            items = []
            for i, li in enumerate(node.find_all('li', recursive=False), 1):
                item_content = ''.join(process_node(child) for child in li.children)
                items.append(f'{i}. {item_content.strip()}')
            return '\n'.join(items) + '\n'

        if node.name == 'pre':
            return f'```\n{node.get_text()}\n```\n'

        if node.name == 'code':
            return f'`{node.get_text()}`'

        if node.name == 'img':
            # 수식 이미지인 경우 alt 텍스트 사용
            alt = node.get('alt', '')
            if alt:
                return f'${alt}$'
            return ''

        if node.name == 'table':
            return process_table(node)

        # 기타 태그는 자식 노드 처리
        return ''.join(process_node(child) for child in node.children)

    def process_table(table_node) -> str:
        """테이블을 마크다운 형식으로 변환"""
        rows = []
        for tr in table_node.find_all('tr'):
            cells = []
            for td in tr.find_all(['td', 'th']):
                cell_content = ''.join(process_node(child) for child in td.children)
                cells.append(cell_content.strip())
            rows.append(' | '.join(cells))

        if rows:
            # 헤더 구분선 추가
            header = rows[0]
            separator = ' | '.join(['---'] * len(rows[0].split(' | ')))
            return header + '\n' + separator + '\n' + '\n'.join(rows[1:]) + '\n'
        return ''

    result = process_node(soup)

    # 연속된 LaTeX 표현식 병합 (예: $a$$_{1}$ → $a_{1}$)
    result = re.sub(r'\$\s*\$', '', result)

    # 연속된 공백/줄바꿈 정리
    result = re.sub(r'\n{3,}', '\n\n', result)
    result = re.sub(r' {2,}', ' ', result)

    return result.strip()


def extract_problem_id(baekjoon_id: str) -> Optional[str]:
    """baekjoon_10006 형식에서 문제 번호 추출"""
    match = re.search(r'baekjoon_(\d+)', baekjoon_id)
    if match:
        return match.group(1)
    return None


async def fetch_problem(
    session: aiohttp.ClientSession,
    problem_id: str,
    semaphore: asyncio.Semaphore
) -> Tuple[str, Optional[str]]:
    """단일 문제 크롤링"""
    url = BAEKJOON_URL.format(problem_id)

    async with semaphore:
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status != 200:
                    print(f"  [SKIP] {problem_id}: HTTP {response.status}")
                    return problem_id, None

                html_content = await response.text()
                soup = BeautifulSoup(html_content, 'html.parser')

                # 문제 설명 추출
                description_div = soup.find('div', id='problem_description')
                if not description_div:
                    print(f"  [SKIP] {problem_id}: 문제 설명 없음")
                    return problem_id, None

                # 입력/출력 설명도 포함
                sections = []

                # 문제 설명
                if description_div:
                    sections.append(html_to_latex_text(str(description_div)))

                # 입력
                input_div = soup.find('div', id='problem_input')
                if input_div:
                    sections.append("### 입력\n" + html_to_latex_text(str(input_div)))

                # 출력
                output_div = soup.find('div', id='problem_output')
                if output_div:
                    sections.append("### 출력\n" + html_to_latex_text(str(output_div)))

                question = '\n\n'.join(sections)

                await asyncio.sleep(REQUEST_DELAY)  # Rate limiting
                return problem_id, question

        except asyncio.TimeoutError:
            print(f"  [TIMEOUT] {problem_id}")
            return problem_id, None
        except Exception as e:
            print(f"  [ERROR] {problem_id}: {e}")
            return problem_id, None


async def crawl_batch(
    problem_ids: List[str],
    results: Dict[str, str],
    start_idx: int
) -> int:
    """배치 크롤링"""
    semaphore = asyncio.Semaphore(CONCURRENT_REQUESTS)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        tasks = [
            fetch_problem(session, pid, semaphore)
            for pid in problem_ids
        ]

        completed = 0
        for coro in asyncio.as_completed(tasks):
            problem_id, question = await coro
            if question:
                results[f"baekjoon_{problem_id}"] = question
            completed += 1

            if completed % 10 == 0:
                print(f"  진행: {start_idx + completed}/{start_idx + len(problem_ids)}")

    return completed


def load_checkpoint() -> Dict[str, str]:
    """체크포인트 로드"""
    if CHECKPOINT_FILE.exists():
        with open(CHECKPOINT_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_checkpoint(results: Dict[str, str]):
    """체크포인트 저장"""
    with open(CHECKPOINT_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)


def main():
    print("=" * 60)
    print("백준 문제 LaTeX 형식 크롤링")
    print("=" * 60)

    # 1. 기존 데이터 로드
    print("\n[1] 기존 데이터 로드...")
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        problems = json.load(f)
    print(f"  총 {len(problems)}개 문제")

    # 2. 문제 ID 추출
    problem_ids = []
    for p in problems:
        pid = extract_problem_id(p['id'])
        if pid:
            problem_ids.append(pid)
    print(f"  크롤링 대상: {len(problem_ids)}개")

    # 3. 체크포인트 로드
    results = load_checkpoint()
    already_done = set(results.keys())
    remaining_ids = [pid for pid in problem_ids if f"baekjoon_{pid}" not in already_done]
    print(f"  이미 완료: {len(already_done)}개")
    print(f"  남은 문제: {len(remaining_ids)}개")

    if not remaining_ids:
        print("\n모든 문제가 이미 크롤링되었습니다.")
    else:
        # 4. 배치 크롤링
        print(f"\n[2] 크롤링 시작 (동시 요청: {CONCURRENT_REQUESTS}, 딜레이: {REQUEST_DELAY}초)")

        BATCH_SIZE = 100
        for i in range(0, len(remaining_ids), BATCH_SIZE):
            batch = remaining_ids[i:i + BATCH_SIZE]
            print(f"\n배치 {i // BATCH_SIZE + 1}: {len(batch)}개 문제")

            asyncio.run(crawl_batch(batch, results, len(already_done) + i))

            # 배치마다 체크포인트 저장
            save_checkpoint(results)
            print(f"  체크포인트 저장 완료 (총 {len(results)}개)")

    # 5. 최종 결과 저장
    print(f"\n[3] 결과 저장: {OUTPUT_FILE}")

    # id와 question만 담은 리스트 형태로 저장
    output_data = [
        {"id": pid, "question": q}
        for pid, q in sorted(results.items())
    ]

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"  저장 완료: {len(output_data)}개 문제")
    print("\n" + "=" * 60)
    print("완료!")


if __name__ == "__main__":
    main()
