#!/usr/bin/env python3
"""
태그 정규화 맵 업데이트 스크립트

사용법:
    python scripts/update_tag_normalization.py

기능:
    1. base_problems 테이블에서 모든 태그 조회
    2. 기존 정규화 맵과 비교하여 새 태그 감지
    3. 자동 매핑 가능한 태그는 자동 추가
    4. 매핑 필요한 태그 목록 출력
    5. 결과를 JSON 파일로 저장

백준 문제 추가 시:
    1. 백준 데이터 DB에 import
    2. 이 스크립트 실행
    3. 새 태그 매핑 확인/추가
    4. 다시 실행하여 JSON 업데이트
"""

import os
import sys
import json
import httpx
from collections import Counter
from typing import Dict, Set, List, Tuple

# 프로젝트 루트를 path에 추가
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from dotenv import load_dotenv
load_dotenv(os.path.join(backend_dir, ".env"))

# ============================================================
# 기본 정규화 규칙 (영문 → 한글)
# ============================================================
BASE_NORMALIZATION = {
    # 영문 태그 → 한글 (CSES, LeetCode 등)
    "Mathematics": "수학",
    "Data structures": "자료구조",
    "Implementation": "구현",
    "Greedy algorithms": "그리디",
    "String algorithms": "문자열",
    "Sorting": "정렬",
    "Dynamic programming": "DP",
    "Complete search": "완전탐색",
    "Fundamentals": "기초",
    "Constructive algorithms": "구현",
    "Number theory": "정수론",
    "Graph algorithms": "그래프",
    "Ad-hoc": "구현",
    "Graph traversal": "BFS/DFS",
    "Bit manipulation": "비트마스킹",
    "Combinatorics": "조합론",
    "Tree algorithms": "트리",
    "Amortized analysis": "분할상환",
    "Geometry": "기하학",
    "Game theory": "게임이론",
    "Matrices": "행렬",
    "Range queries": "구간쿼리",
    "Spanning trees": "최소신장트리",
    "Shortest paths": "최단경로",
    "Probability": "확률",
    "Divide and conquer": "분할정복",
    "Preprocessing": "전처리",
    "Segment trees revisited": "세그먼트트리",
    "Flows and cuts": "네트워크플로우",
    "Tree queries": "트리쿼리",
    "Polynomials and generating functions": "다항식",
    "Square root algorithms": "제곱근분할",
    "Strong connectivity": "강한연결요소",
    "Sweep line algorithms": "스위핑",
    "Unbounded Knapsack": "배낭문제",
    "Parametric Search": "파라메트릭서치",
    "Binary Search": "이분탐색",
    "Graph Theory": "그래프",
    "Graph": "그래프",
    "Hash Table": "해시",
    "Array": "배열",
    "Queue": "큐",
    "String": "문자열",

    # 백준 태그 (예상)
    "수학": "수학",
    "구현": "구현",
    "그리디 알고리즘": "그리디",
    "문자열": "문자열",
    "정렬": "정렬",
    "다이나믹 프로그래밍": "DP",
    "브루트포스 알고리즘": "완전탐색",
    "그래프 이론": "그래프",
    "그래프 탐색": "BFS/DFS",
    "너비 우선 탐색": "BFS/DFS",
    "깊이 우선 탐색": "BFS/DFS",
    "자료 구조": "자료구조",
    "트리": "트리",
    "정수론": "정수론",
    "기하학": "기하학",
    "이분 탐색": "이분탐색",
    "세그먼트 트리": "세그먼트트리",
    "최단 경로": "최단경로",
    "분할 정복": "분할정복",
    "백트래킹": "백트래킹",
    "스택": "스택/큐",
    "큐": "스택/큐",
    "해시를 사용한 집합과 맵": "해시",
    "해싱": "해시",
    "우선순위 큐": "힙",
    "힙": "힙",
    "투 포인터": "투포인터",
    "슬라이딩 윈도우": "슬라이딩윈도우",
    "비트마스킹": "비트마스킹",
    "조합론": "조합론",
    "게임 이론": "게임이론",
    "최소 스패닝 트리": "최소신장트리",
    "유니온 파인드": "유니온파인드",
    "위상 정렬": "위상정렬",
    "누적 합": "누적합",
    "에라토스테네스의 체": "정수론",
    "소수 판정": "정수론",
    "유클리드 호제법": "정수론",
    "플로이드-워셜": "최단경로",
    "다익스트라": "최단경로",
    "벨만-포드": "최단경로",
    "크루스칼": "최소신장트리",
    "프림": "최소신장트리",
    "LCA": "트리",
    "최소 공통 조상": "트리",

    # 이미 정규화된 형태로 DB에 저장된 경우 (자기 자신 매핑)
    "DP": "DP",
    "BFS/DFS": "BFS/DFS",
    "기초": "기초",
    "정렬": "정렬",
    "구현": "구현",
    "이분탐색": "이분탐색",
    "자료구조": "자료구조",
    "해시테이블": "해시",
}

# 의미 통합 (여러 태그 → 하나로)
SEMANTIC_MERGE = {
    # BFS/DFS 통합
    "BFS": "BFS/DFS",
    "DFS": "BFS/DFS",
    "bfs": "BFS/DFS",
    "dfs": "BFS/DFS",

    # 스택/큐 통합
    "스택": "스택/큐",
    "큐": "스택/큐",
    "stack": "스택/큐",
    "queue": "스택/큐",

    # DP 별칭
    "동적 프로그래밍": "DP",
    "동적프로그래밍": "DP",
    "dp": "DP",

    # 시뮬레이션 → 구현
    "시뮬레이션": "구현",
    "simulation": "구현",
}

# 제외할 태그
EXCLUDED_TAGS = {
    "기타", "etc", "기타 알고리즘", "미분류", "uncategorized",
    "출처", "source", "언어", "language", "asgsag",
}

# 주제 간 연관성 (정규화된 태그 기준)
TOPIC_RELATIONS = {
    "기초": ["구현", "정렬", "수학", "문자열"],
    "수학": ["정렬", "구현", "DP", "정수론", "조합론"],
    "정수론": ["수학", "조합론", "DP"],
    "조합론": ["수학", "DP", "백트래킹"],
    "BFS/DFS": ["그래프", "백트래킹", "최단경로", "완전탐색", "트리"],
    "그래프": ["BFS/DFS", "최단경로", "최소신장트리", "트리"],
    "백트래킹": ["BFS/DFS", "완전탐색", "조합론"],
    "완전탐색": ["백트래킹", "구현", "BFS/DFS"],
    "최단경로": ["그래프", "BFS/DFS", "DP"],
    "최소신장트리": ["그래프", "그리디"],
    "트리": ["그래프", "BFS/DFS", "DP"],
    "DP": ["그리디", "분할정복", "이분탐색", "트리"],
    "그리디": ["DP", "정렬", "이분탐색"],
    "분할정복": ["DP", "이분탐색"],
    "자료구조": ["해시", "트리", "구간쿼리", "세그먼트트리", "힙"],
    "해시": ["문자열", "자료구조"],
    "힙": ["자료구조", "그리디", "정렬"],
    "구간쿼리": ["세그먼트트리", "자료구조", "DP"],
    "세그먼트트리": ["구간쿼리", "트리", "자료구조"],
    "문자열": ["해시", "구현", "DP"],
    "정렬": ["이분탐색", "그리디", "자료구조"],
    "이분탐색": ["정렬", "파라메트릭서치", "그리디"],
    "파라메트릭서치": ["이분탐색", "그리디"],
    "비트마스킹": ["DP", "완전탐색"],
    "기하학": ["구현", "수학"],
    "구현": ["완전탐색", "문자열", "BFS/DFS", "정렬"],
    "투포인터": ["슬라이딩윈도우", "정렬", "이분탐색"],
    "슬라이딩윈도우": ["투포인터", "문자열"],
    "유니온파인드": ["그래프", "최소신장트리"],
    "위상정렬": ["그래프", "DP"],
}


class SupabaseClient:
    """간단한 Supabase REST API 클라이언트"""

    def __init__(self, url: str, key: str):
        self.url = url.rstrip("/")
        self.key = key
        self.headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        }

    def query(self, table: str, select: str = "*") -> List[Dict]:
        """테이블 조회"""
        endpoint = f"{self.url}/rest/v1/{table}?select={select}"

        with httpx.Client(timeout=30.0) as client:
            response = client.get(endpoint, headers=self.headers)
            response.raise_for_status()
            return response.json()


def get_supabase_client() -> SupabaseClient:
    """Supabase 클라이언트 생성"""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")

    if not url or not key:
        raise ValueError("SUPABASE_URL과 SUPABASE_SERVICE_ROLE_KEY 환경변수가 필요합니다")

    return SupabaseClient(url, key)


def fetch_all_tags(supabase: SupabaseClient) -> Counter:
    """DB에서 모든 태그와 빈도 조회"""
    print("📊 base_problems에서 태그 조회 중...")

    data = supabase.query("base_problems", "tags")

    tag_counter = Counter()
    for row in data:
        tags = row.get("tags") or []
        for tag in tags:
            if tag:
                tag_counter[tag] += 1

    print(f"   → {len(tag_counter)}개의 유니크 태그 발견 (총 {sum(tag_counter.values())}개 사용)")
    return tag_counter


def normalize_tag(tag: str, normalization_map: Dict[str, str]) -> str:
    """태그 정규화"""
    if not tag:
        return None

    tag = tag.strip()

    # 제외 태그 체크
    if tag.lower() in {t.lower() for t in EXCLUDED_TAGS}:
        return None

    # 정규화 맵에서 찾기
    if tag in normalization_map:
        return normalization_map[tag]

    # 소문자로도 확인
    for key, value in normalization_map.items():
        if key.lower() == tag.lower():
            return value

    # 매핑 없으면 원본 반환
    return tag


def analyze_tags(tag_counter: Counter) -> Tuple[Dict[str, str], List[str], Dict[str, int]]:
    """
    태그 분석 및 정규화 맵 생성

    Returns:
        (정규화맵, 매핑필요태그목록, 정규화된태그빈도)
    """
    # 기본 맵 + 의미 통합 맵 결합
    full_map = {**BASE_NORMALIZATION, **SEMANTIC_MERGE}

    unmapped_tags = []
    normalized_counts = Counter()

    for tag, count in tag_counter.items():
        normalized = normalize_tag(tag, full_map)

        if normalized is None:
            # 제외된 태그
            continue
        elif normalized == tag and tag not in full_map:
            # 매핑되지 않은 새 태그
            unmapped_tags.append((tag, count))
        else:
            normalized_counts[normalized] += count

    # 매핑 안 된 태그 중 빈도순 정렬
    unmapped_tags.sort(key=lambda x: -x[1])

    return full_map, unmapped_tags, normalized_counts


def generate_output(
    normalization_map: Dict[str, str],
    unmapped_tags: List[Tuple[str, int]],
    normalized_counts: Counter,
    output_path: str,
):
    """결과 JSON 파일 생성"""

    # 정규화된 태그 목록 (빈도순)
    available_tags = [tag for tag, _ in normalized_counts.most_common()]

    output = {
        "_description": "태그 정규화 맵 (자동 생성됨)",
        "_generated_by": "scripts/update_tag_normalization.py",
        "_last_updated": __import__("datetime").datetime.now().isoformat(),

        # 정규화 맵
        "normalization": normalization_map,

        # 의미 통합 맵
        "semantic_merge": SEMANTIC_MERGE,

        # 제외 태그
        "excluded_tags": list(EXCLUDED_TAGS),

        # 주제 연관성
        "topic_relations": TOPIC_RELATIONS,

        # DB에서 발견된 정규화 태그 목록 (빈도순)
        "available_tags": available_tags,

        # 태그별 문제 수
        "tag_counts": dict(normalized_counts.most_common()),

        # 매핑 필요한 태그 (수동 추가 필요)
        "unmapped_tags": [{"tag": tag, "count": count} for tag, count in unmapped_tags],
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 결과 저장: {output_path}")


def print_summary(normalized_counts: Counter, unmapped_tags: List[Tuple[str, int]]):
    """분석 결과 요약 출력"""

    print("\n" + "="*60)
    print("📋 정규화된 태그 목록 (빈도순)")
    print("="*60)

    for i, (tag, count) in enumerate(normalized_counts.most_common(30), 1):
        print(f"  {i:2}. {tag:15} ({count:4}개)")

    if len(normalized_counts) > 30:
        print(f"  ... 외 {len(normalized_counts) - 30}개")

    if unmapped_tags:
        print("\n" + "="*60)
        print("⚠️  매핑 필요한 태그 (수동 추가 필요)")
        print("="*60)

        for tag, count in unmapped_tags[:20]:
            print(f"  - {tag:30} ({count}개)")

        if len(unmapped_tags) > 20:
            print(f"  ... 외 {len(unmapped_tags) - 20}개")

        print("\n💡 위 태그들을 BASE_NORMALIZATION에 추가하세요:")
        print('   예: "새태그": "정규화된태그",')
    else:
        print("\n✅ 모든 태그가 정규화되었습니다!")


def main():
    print("🔄 태그 정규화 맵 업데이트")
    print("="*60)

    # Supabase 연결
    try:
        supabase = get_supabase_client()
    except Exception as e:
        print(f"❌ Supabase 연결 실패: {e}")
        return 1

    # 태그 조회
    tag_counter = fetch_all_tags(supabase)

    # 분석
    normalization_map, unmapped_tags, normalized_counts = analyze_tags(tag_counter)

    # 요약 출력
    print_summary(normalized_counts, unmapped_tags)

    # 결과 저장
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "app", "data")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "tag_normalization.json")

    generate_output(normalization_map, unmapped_tags, normalized_counts, output_path)

    print("\n" + "="*60)
    print("📌 다음 단계:")
    print("   1. unmapped_tags가 있으면 스크립트에 매핑 추가")
    print("   2. 다시 실행하여 JSON 업데이트")
    print("   3. user_tools.py에서 JSON 파일 로드하도록 수정 (선택)")
    print("="*60)

    return 0 if not unmapped_tags else 1


if __name__ == "__main__":
    sys.exit(main())
