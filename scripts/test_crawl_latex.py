#!/usr/bin/env python3
"""
테스트: 몇 개 문제만 크롤링하여 LaTeX 변환 확인
"""

import asyncio
import aiohttp
from bs4 import BeautifulSoup
import html
import re


def html_to_latex_text(html_content: str) -> str:
    """HTML을 LaTeX 수식이 포함된 텍스트로 변환"""
    if not html_content:
        return ""

    soup = BeautifulSoup(html_content, 'html.parser')

    def process_node(node) -> str:
        if node.name is None:  # 텍스트 노드
            return html.unescape(str(node))

        if node.name == 'sub':
            content = ''.join(process_node(child) for child in node.children)
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

        if node.name == 'pre':
            return f'```\n{node.get_text()}\n```\n'

        if node.name == 'code':
            return f'`{node.get_text()}`'

        if node.name == 'img':
            alt = node.get('alt', '')
            if alt:
                return f'${alt}$'
            return ''

        return ''.join(process_node(child) for child in node.children)

    result = process_node(soup)
    result = re.sub(r'\$\s*\$', '', result)
    result = re.sub(r'\n{3,}', '\n\n', result)
    result = re.sub(r' {2,}', ' ', result)

    return result.strip()


async def fetch_problem(problem_id: str) -> str:
    """단일 문제 크롤링"""
    url = f"https://www.acmicpc.net/problem/{problem_id}"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept-Language': 'ko-KR,ko;q=0.9',
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as response:
            if response.status != 200:
                return f"HTTP {response.status}"

            html_content = await response.text()
            soup = BeautifulSoup(html_content, 'html.parser')

            sections = []

            # 문제 설명
            desc = soup.find('div', id='problem_description')
            if desc:
                sections.append(html_to_latex_text(str(desc)))

            # 입력
            inp = soup.find('div', id='problem_input')
            if inp:
                sections.append("### 입력\n" + html_to_latex_text(str(inp)))

            # 출력
            out = soup.find('div', id='problem_output')
            if out:
                sections.append("### 출력\n" + html_to_latex_text(str(out)))

            return '\n\n'.join(sections)


async def main():
    # 테스트할 문제 ID (수학 기호가 많은 문제들)
    test_ids = ["10006", "1000", "17386"]

    for pid in test_ids:
        print(f"\n{'='*60}")
        print(f"문제 {pid}")
        print("=" * 60)

        result = await fetch_problem(pid)
        print(result[:1500])  # 처음 1500자만 출력
        print("...")


if __name__ == "__main__":
    asyncio.run(main())
