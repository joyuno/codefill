"""
Topic Taxonomy Generator

base_problems 테이블에서 모든 고유 tags를 추출하고,
유사/중복 태그를 정제하여 정적 JSON 파일로 저장합니다.

사용법:
  cd backend
  python -m scripts.generate_topic_taxonomy

결과:
  app/data/topic_taxonomy.json
"""

import os
import sys
import json
import asyncio
from collections import Counter
from typing import Dict, List, Set, Tuple
import re

# 프로젝트 루트 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from app.database import get_supabase_client as _get_supabase
from supabase import Client

# ============================================================
# 태그 정규화 및 한국어 매핑 (수동 정의)
# ============================================================

# 영어 → 한국어 태그 매핑 (DB 태그 기반 확장)
TAG_KO_MAPPING = {
    # 자료구조
    "array": "배열",
    "arrays": "배열",
    "string": "문자열",
    "strings": "문자열",
    "string algorithms": "문자열",
    "hash table": "해시 테이블",
    "hash-table": "해시 테이블",
    "hashtable": "해시 테이블",
    "hashing": "해시",
    "hash": "해시",
    "linked list": "연결 리스트",
    "linked-list": "연결 리스트",
    "linkedlist": "연결 리스트",
    "stack": "스택",
    "queue": "큐",
    "deque": "덱",
    "tree": "트리",
    "trees": "트리",
    "tree algorithms": "트리",
    "tree queries": "트리 쿼리",
    "binary tree": "이진 트리",
    "binary-tree": "이진 트리",
    "binary search tree": "이진 탐색 트리",
    "bst": "이진 탐색 트리",
    "heap": "힙",
    "priority queue": "우선순위 큐",
    "priority-queue": "우선순위 큐",
    "graph": "그래프",
    "graphs": "그래프",
    "graph algorithms": "그래프",
    "trie": "트라이",
    "segment tree": "세그먼트 트리",
    "segment trees revisited": "세그먼트 트리",
    "fenwick tree": "펜윅 트리",
    "union find": "유니온 파인드",
    "union-find": "유니온 파인드",
    "disjoint set": "분리 집합",
    "data structures": "자료구조",
    "range queries": "구간 쿼리",
    "matrices": "행렬",

    # 알고리즘
    "sorting": "정렬",
    "sort": "정렬",
    "binary search": "이분 탐색",
    "binary-search": "이분 탐색",
    "binarysearch": "이분 탐색",
    "parametric search": "파라메트릭 서치",
    "two pointers": "투 포인터",
    "two-pointers": "투 포인터",
    "sliding window": "슬라이딩 윈도우",
    "sliding-window": "슬라이딩 윈도우",
    "dynamic programming": "DP",
    "dynamic-programming": "DP",
    "dp": "DP",
    "unbounded knapsack": "DP (배낭)",
    "greedy": "그리디",
    "greedy algorithms": "그리디",
    "backtracking": "백트래킹",
    "recursion": "재귀",
    "divide and conquer": "분할 정복",
    "divide-and-conquer": "분할 정복",
    "bfs": "BFS",
    "breadth-first search": "BFS",
    "dfs": "DFS",
    "depth-first search": "DFS",
    "graph traversal": "BFS/DFS",
    "shortest path": "최단 경로",
    "shortest paths": "최단 경로",
    "dijkstra": "다익스트라",
    "floyd-warshall": "플로이드-워셜",
    "bellman-ford": "벨만-포드",
    "topological sort": "위상 정렬",
    "topological-sort": "위상 정렬",
    "minimum spanning tree": "최소 신장 트리",
    "spanning trees": "최소 신장 트리",
    "mst": "최소 신장 트리",
    "kruskal": "크루스칼",
    "prim": "프림",
    "complete search": "완전 탐색",
    "brute force": "완전 탐색",
    "brute-force": "완전 탐색",
    "bruteforce": "완전 탐색",
    "flows and cuts": "네트워크 플로우",
    "strong connectivity": "강한 연결 요소",
    "sweep line algorithms": "스위핑",
    "square root algorithms": "제곱근 분할",

    # 수학
    "math": "수학",
    "mathematics": "수학",
    "number theory": "정수론",
    "number-theory": "정수론",
    "geometry": "기하학",
    "combinatorics": "조합론",
    "probability": "확률",
    "bit manipulation": "비트 연산",
    "bit-manipulation": "비트 연산",
    "bitwise": "비트 연산",
    "bitmask": "비트마스크",
    "polynomials and generating functions": "다항식/생성함수",

    # 기타
    "implementation": "구현",
    "simulation": "시뮬레이션",
    "constructive algorithms": "구성적 알고리즘",
    "ad-hoc": "애드혹",
    "fundamentals": "기초",
    "amortized analysis": "분할 상환",
    "preprocessing": "전처리",
    "prefix sum": "누적 합",
    "prefix-sum": "누적 합",
    "matrix": "행렬",
    "game theory": "게임 이론",
    "design": "설계",
    "database": "데이터베이스",
    "sql": "SQL",
    "shell": "쉘",
    "concurrency": "동시성",
    "interactive": "인터랙티브",
}

# 유사 태그 그룹 (대표 태그로 통합) - DB 태그 기반 확장
TAG_GROUPS = {
    "DP": ["dp", "dynamic programming", "dynamic-programming", "memoization", "unbounded knapsack"],
    "그래프": ["graph", "graphs", "graph algorithms"],
    "BFS/DFS": ["bfs", "dfs", "breadth-first search", "depth-first search", "graph traversal"],
    "이분 탐색": ["binary search", "binary-search", "binarysearch", "parametric search"],
    "투 포인터": ["two pointers", "two-pointers", "sliding window", "sliding-window"],
    "정렬": ["sorting", "sort"],
    "해시": ["hash", "hash table", "hash-table", "hashtable", "hashing"],
    "스택/큐": ["stack", "queue", "deque"],
    "트리": ["tree", "trees", "binary tree", "binary-tree", "tree algorithms", "tree queries"],
    "힙": ["heap", "priority queue", "priority-queue"],
    "문자열": ["string", "strings", "string algorithms"],
    "배열": ["array", "arrays"],
    "자료구조": ["data structures"],
    "구현": ["implementation", "simulation"],
    "완전 탐색": ["brute force", "brute-force", "bruteforce", "complete search"],
    "백트래킹": ["backtracking"],
    "그리디": ["greedy", "greedy algorithms"],
    "수학": ["math", "mathematics", "number theory"],
    "비트 연산": ["bit manipulation", "bit-manipulation", "bitwise", "bitmask"],
    "최단 경로": ["shortest path", "shortest paths", "dijkstra", "bellman-ford", "floyd-warshall"],
    "최소 신장 트리": ["spanning trees", "minimum spanning tree", "mst", "kruskal", "prim"],
    "세그먼트 트리": ["segment tree", "segment trees revisited", "range queries"],
    "기초": ["fundamentals"],
    "구성적": ["constructive algorithms"],
    "애드혹": ["ad-hoc"],
    "네트워크 플로우": ["flows and cuts"],
    "강한 연결 요소": ["strong connectivity"],
}

# 난이도별 권장 주제 (순서대로)
TOPIC_BY_LEVEL = {
    "beginner": ["기초", "배열", "문자열", "수학", "정렬", "구현"],
    "elementary": ["정렬", "스택/큐", "해시", "투 포인터", "완전 탐색", "그리디"],
    "intermediate": ["이분 탐색", "DP", "BFS/DFS", "그래프", "백트래킹", "자료구조"],
    "advanced": ["DP", "그래프", "트리", "세그먼트 트리", "최단 경로", "최소 신장 트리", "네트워크 플로우"],
}

# 카테고리 정의
CATEGORIES = {
    "자료구조": ["자료구조", "배열", "문자열", "해시", "스택/큐", "트리", "힙", "그래프", "세그먼트 트리", "트라이"],
    "알고리즘": ["정렬", "이분 탐색", "투 포인터", "DP", "그리디", "백트래킹", "BFS/DFS", "분할 정복", "최단 경로", "최소 신장 트리", "위상 정렬", "완전 탐색", "네트워크 플로우", "강한 연결 요소"],
    "수학": ["수학", "정수론", "기하학", "조합론", "확률", "비트 연산", "행렬"],
    "기타": ["구현", "기초", "구성적", "애드혹", "분할 상환", "전처리", "게임 이론"],
}


def get_supabase_client() -> Client:
    """Supabase 클라이언트 생성 (프로젝트 모듈 사용)"""
    return _get_supabase()


def normalize_tag(tag: str) -> str:
    """태그 정규화 (소문자, 공백 제거)"""
    return tag.lower().strip()


def get_representative_tag(tag: str) -> Tuple[str, str]:
    """
    태그를 대표 태그로 변환

    Returns:
        (대표_태그_한국어, 원본_영어)
    """
    normalized = normalize_tag(tag)

    # 그룹에서 찾기
    for rep_tag, variants in TAG_GROUPS.items():
        if normalized in [v.lower() for v in variants]:
            return rep_tag, tag

    # 직접 매핑에서 찾기
    if normalized in TAG_KO_MAPPING:
        return TAG_KO_MAPPING[normalized], tag

    # 그대로 반환 (이미 한국어인 경우)
    if re.search(r'[가-힣]', tag):
        return tag, tag

    return tag, tag


async def fetch_all_tags(supabase: Client) -> Counter:
    """DB에서 모든 태그 추출 및 카운트"""
    print("📦 DB에서 태그 추출 중...")

    result = supabase.table("base_problems") \
        .select("tags") \
        .execute()

    if not result.data:
        print("⚠️ base_problems 테이블에 데이터가 없습니다.")
        return Counter()

    tag_counter = Counter()
    for row in result.data:
        tags = row.get("tags", [])
        if tags:
            for tag in tags:
                if tag and tag.strip():
                    tag_counter[tag.strip()] += 1

    print(f"✅ {len(result.data)}개 문제에서 {len(tag_counter)}개 고유 태그 추출")
    return tag_counter


def process_tags(tag_counter: Counter) -> Dict:
    """
    태그 정제 및 분류

    Returns:
        {
            "all_topics": [...],  # 모든 정제된 주제 목록
            "by_category": {...},  # 카테고리별 분류
            "by_level": {...},  # 난이도별 추천
            "tag_mapping": {...},  # 원본 → 정제 매핑
            "problem_counts": {...},  # 주제별 문제 수
        }
    """
    print("\n🔄 태그 정제 중...")

    # 대표 태그로 변환 및 카운트 합산
    rep_tag_counts = Counter()
    tag_mapping = {}  # 원본 → 정제 매핑
    original_tags = {}  # 정제 → 원본들

    for tag, count in tag_counter.items():
        rep_tag, original = get_representative_tag(tag)
        rep_tag_counts[rep_tag] += count
        tag_mapping[tag] = rep_tag

        if rep_tag not in original_tags:
            original_tags[rep_tag] = []
        if original not in original_tags[rep_tag]:
            original_tags[rep_tag].append(original)

    # 문제 수 기준 정렬
    sorted_topics = [tag for tag, _ in rep_tag_counts.most_common()]

    # 카테고리별 분류
    # 전역 CATEGORIES 사용
    by_category = {}
    categorized = set()
    for cat, topic_list in CATEGORIES.items():
        by_category[cat] = [t for t in topic_list if t in sorted_topics]
        categorized.update(by_category[cat])

    # 미분류 태그
    uncategorized = [t for t in sorted_topics if t not in categorized]
    if uncategorized:
        by_category["기타"] = by_category.get("기타", []) + uncategorized

    # 난이도별 추천
    by_level = {}
    for level, topics in TOPIC_BY_LEVEL.items():
        by_level[level] = [t for t in topics if t in sorted_topics]

    print(f"✅ {len(sorted_topics)}개 정제된 주제 생성")
    print(f"   카테고리: {list(by_category.keys())}")

    return {
        "all_topics": sorted_topics,
        "by_category": by_category,
        "by_level": by_level,
        "tag_mapping": tag_mapping,
        "original_tags": original_tags,
        "problem_counts": dict(rep_tag_counts),
    }


def generate_topic_taxonomy(processed: Dict) -> Dict:
    """최종 taxonomy JSON 생성"""

    # 문제 수가 있는 주제만 포함 (최소 1개 이상)
    all_topics = []
    for topic in processed["all_topics"]:
        count = processed["problem_counts"].get(topic, 0)
        if count > 0:
            all_topics.append({
                "name": topic,
                "problem_count": count,
                "aliases": processed["original_tags"].get(topic, []),
            })

    # 카테고리별 정리
    by_category = {}
    for cat, topics in processed["by_category"].items():
        by_category[cat] = [
            {
                "name": t,
                "problem_count": processed["problem_counts"].get(t, 0),
            }
            for t in topics
            if processed["problem_counts"].get(t, 0) > 0
        ]

    taxonomy = {
        "_description": "CodeFill 문제집의 모든 주제 목록 (자동 생성됨)",
        "_generated_at": None,  # 실행 시 채워짐
        "_total_topics": len(all_topics),
        "_total_problems": sum(t["problem_count"] for t in all_topics),

        # 전체 주제 목록 (문제 수 기준 정렬)
        "all_topics": all_topics,

        # 카테고리별 분류
        "by_category": by_category,

        # 난이도별 추천
        "by_level": processed["by_level"],

        # 검색용 매핑 (영어 → 한국어)
        "tag_mapping": processed["tag_mapping"],

        # 빠른 조회용 - 이름만
        "topic_names": [t["name"] for t in all_topics],
    }

    return taxonomy


async def main():
    """메인 실행"""
    from datetime import datetime

    print("=" * 60)
    print("🏷️  Topic Taxonomy Generator")
    print("=" * 60)

    # Supabase 연결
    supabase = get_supabase_client()

    # 1. DB에서 태그 추출
    tag_counter = await fetch_all_tags(supabase)

    if not tag_counter:
        print("❌ 태그가 없습니다. 종료합니다.")
        return

    # 2. 태그 정제
    processed = process_tags(tag_counter)

    # 3. Taxonomy 생성
    taxonomy = generate_topic_taxonomy(processed)
    taxonomy["_generated_at"] = datetime.now().isoformat()

    # 4. JSON 파일로 저장
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "app", "data")
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, "topic_taxonomy.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(taxonomy, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 60)
    print(f"✅ 저장 완료: {output_path}")
    print(f"   - 총 주제 수: {taxonomy['_total_topics']}")
    print(f"   - 총 문제 수: {taxonomy['_total_problems']}")
    print("=" * 60)

    # 주제 목록 미리보기
    print("\n📋 주제 목록 (상위 20개):")
    for topic in taxonomy["all_topics"][:20]:
        print(f"   - {topic['name']} ({topic['problem_count']}문제)")

    if len(taxonomy["all_topics"]) > 20:
        print(f"   ... 외 {len(taxonomy['all_topics']) - 20}개")


if __name__ == "__main__":
    asyncio.run(main())
