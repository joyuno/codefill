#!/usr/bin/env python3
"""
question_html을 KaTeX + 이미지 URL이 포함된 마크다운으로 변환

변환 내용:
1. <sub>x</sub> → $_{x}$ (KaTeX 아래첨자)
2. <sup>x</sup> → $^{x}$ (KaTeX 위첨자)
3. 기존 $(...)$ LaTeX 수식 유지
4. 상대 이미지 경로 → 절대 경로 (https://www.acmicpc.net/...)
5. HTML → 깔끔한 마크다운
"""

import json
import re
import html
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString
from typing import Optional


# 경로 설정
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data" / "baekjoon" / "data_baekjoon"
INPUT_FILE = DATA_DIR / "validated_problems_clean.json"
OUTPUT_FILE = DATA_DIR / "validated_problems_latex.json"

# 백준 기본 URL
BAEKJOON_BASE_URL = "https://www.acmicpc.net"


def fix_image_url(src: str) -> str:
    """이미지 URL을 절대 경로로 변환"""
    if not src:
        return src

    # 이미 절대 경로
    if src.startswith('http://') or src.startswith('https://'):
        return src

    # data URI (base64)
    if src.startswith('data:'):
        return src

    # 상대 경로 → 절대 경로
    if src.startswith('/'):
        return f"{BAEKJOON_BASE_URL}{src}"
    else:
        return f"{BAEKJOON_BASE_URL}/{src}"


def html_to_katex_markdown(html_content: str) -> str:
    """HTML을 KaTeX 수식이 포함된 마크다운으로 변환"""
    if not html_content:
        return ""

    soup = BeautifulSoup(html_content, 'html.parser')

    def process_node(node, in_math: bool = False) -> str:
        """노드를 재귀적으로 처리"""

        # 텍스트 노드
        if isinstance(node, NavigableString):
            text = str(node)
            # HTML 엔티티 디코딩
            text = html.unescape(text)
            return text

        # 요소 노드
        tag = node.name

        # 아래첨자 → KaTeX
        if tag == 'sub':
            content = ''.join(process_node(child, True) for child in node.children)
            content = content.strip()
            if content:
                return f'$_{{{content}}}$'
            return ''

        # 위첨자 → KaTeX
        if tag == 'sup':
            content = ''.join(process_node(child, True) for child in node.children)
            content = content.strip()
            if content:
                return f'$^{{{content}}}$'
            return ''

        # 변수 (이탤릭) → KaTeX
        if tag == 'var':
            content = ''.join(process_node(child, True) for child in node.children)
            return f'${content}$'

        # 수식 블록 (MathJax/KaTeX)
        if tag == 'span' and node.get('class') and 'math-tex' in ' '.join(node.get('class', [])):
            return node.get_text()

        # 이미지
        if tag == 'img':
            src = fix_image_url(node.get('src', ''))
            alt = node.get('alt', '이미지')
            if src:
                return f'\n\n![{alt}]({src})\n\n'
            return ''

        # 단락
        if tag == 'p':
            content = ''.join(process_node(child) for child in node.children)
            return content.strip() + '\n\n'

        # 줄바꿈
        if tag == 'br':
            return '\n'

        # 제목
        if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            level = int(tag[1])
            content = ''.join(process_node(child) for child in node.children)
            return f"{'#' * level} {content.strip()}\n\n"

        # 강조
        if tag in ['strong', 'b']:
            content = ''.join(process_node(child) for child in node.children)
            return f'**{content}**'

        if tag in ['em', 'i']:
            content = ''.join(process_node(child) for child in node.children)
            return f'*{content}*'

        # 코드
        if tag == 'code':
            content = node.get_text()
            return f'`{content}`'

        if tag == 'pre':
            content = node.get_text()
            return f'\n```\n{content}\n```\n'

        # 목록
        if tag == 'ul':
            items = []
            for li in node.find_all('li', recursive=False):
                item_content = ''.join(process_node(child) for child in li.children)
                items.append(f'- {item_content.strip()}')
            return '\n'.join(items) + '\n\n'

        if tag == 'ol':
            items = []
            for i, li in enumerate(node.find_all('li', recursive=False), 1):
                item_content = ''.join(process_node(child) for child in li.children)
                items.append(f'{i}. {item_content.strip()}')
            return '\n'.join(items) + '\n\n'

        # 테이블
        if tag == 'table':
            return process_table(node)

        # div, span 등 컨테이너
        if tag in ['div', 'span', 'section', 'article']:
            content = ''.join(process_node(child) for child in node.children)
            if tag == 'div':
                return content + '\n'
            return content

        # 링크
        if tag == 'a':
            href = node.get('href', '')
            content = ''.join(process_node(child) for child in node.children)
            if href:
                return f'[{content}]({href})'
            return content

        # 기타 태그는 자식 노드만 처리
        return ''.join(process_node(child) for child in node.children)

    def process_table(table_node) -> str:
        """테이블을 마크다운으로 변환"""
        rows = []
        header_processed = False

        for tr in table_node.find_all('tr'):
            cells = []
            is_header = tr.find('th') is not None

            for td in tr.find_all(['td', 'th']):
                cell_content = ''.join(process_node(child) for child in td.children)
                cells.append(cell_content.strip().replace('|', '\\|'))

            if cells:
                row = '| ' + ' | '.join(cells) + ' |'
                rows.append(row)

                # 첫 번째 행 후에 구분선 추가
                if not header_processed:
                    separator = '| ' + ' | '.join(['---'] * len(cells)) + ' |'
                    rows.append(separator)
                    header_processed = True

        return '\n'.join(rows) + '\n\n' if rows else ''

    result = process_node(soup)

    # 연속된 LaTeX 병합: $a$$_{1}$ → $a_{1}$
    result = re.sub(r'\$\s*\$', '', result)

    # 연속된 공백/줄바꿈 정리
    result = re.sub(r'\n{3,}', '\n\n', result)
    result = re.sub(r' {2,}', ' ', result)
    result = re.sub(r'\n +', '\n', result)

    return result.strip()


def convert_problem(problem: dict) -> dict:
    """단일 문제 변환"""
    result = problem.copy()

    question_html = problem.get('question_html', '')
    if question_html:
        result['question'] = html_to_katex_markdown(question_html)

    return result


def main():
    print("=" * 60)
    print("question_html → KaTeX 마크다운 변환")
    print("=" * 60)

    # 1. 데이터 로드
    print("\n[1] 데이터 로드...")
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        problems = json.load(f)
    print(f"  총 {len(problems)}개 문제")

    # 2. 변환
    print("\n[2] 변환 중...")
    converted = []
    for i, p in enumerate(problems):
        converted.append(convert_problem(p))
        if (i + 1) % 1000 == 0:
            print(f"  {i + 1}/{len(problems)} 완료")

    # 3. 저장
    print(f"\n[3] 저장: {OUTPUT_FILE}")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(converted, f, ensure_ascii=False, indent=2)

    # 4. 샘플 출력
    print("\n[4] 변환 샘플:")

    # 이미지가 있는 문제 샘플
    img_sample = next((p for p in converted if '![' in p.get('question', '')), None)
    if img_sample:
        print(f"\n--- 이미지 포함 문제 ({img_sample['id']}) ---")
        print(img_sample['question'][:1000])

    # 수식이 있는 문제 샘플
    math_sample = next((p for p in converted if '$_' in p.get('question', '') or '$^' in p.get('question', '')), None)
    if math_sample:
        print(f"\n--- 수식 포함 문제 ({math_sample['id']}) ---")
        print(math_sample['question'][:1000])

    print("\n" + "=" * 60)
    print("완료!")


if __name__ == "__main__":
    main()
