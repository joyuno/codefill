"""
user_analysis_reports 테이블의 주제 데이터 정규화 스크립트

skill_snapshot, strengths, weaknesses의 topic 값을
허용된 한국어 태그로 매핑하거나 삭제합니다.

실행: python scripts/normalize_analysis_topics.py
"""

import os
import sys
from dotenv import load_dotenv

# 프로젝트 루트를 path에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

from supabase import create_client

# 허용된 태그 목록
ALLOWED_TAGS = {
    "구현", "정렬", "문자열", "이분탐색", "그리디", "DP",
    "BFS/DFS", "그래프", "백트래킹", "완전탐색", "자료구조",
    "수학", "트리", "최단경로", "투포인터", "해시",
}

# 정규화 매핑 (영어/기타 → 허용된 한국어)
# base_problems 테이블의 모든 태그를 포함
TOPIC_NORMALIZATION = {
    # ===== 구현 =====
    "Array": "구현",
    "Implementation": "구현",
    "implementation": "구현",
    "Ad-hoc": "구현",
    "ad_hoc": "구현",
    "case_work": "구현",
    "케이스분류": "구현",
    "simulation": "구현",
    "시뮬레이션": "구현",
    "Fundamentals": "구현",
    "배열": "구현",
    "반복문": "구현",
    "기초": "구현",
    "파싱": "구현",
    "구성적": "구현",
    "애드혹": "구현",
    "전처리": "구현",
    "좌표압축": "구현",
    "traceback": "구현",
    "utf8": "구현",

    # ===== 정렬 =====
    "Sorting": "정렬",
    "sorting": "정렬",
    "merge_sort": "정렬",
    "quick_sort": "정렬",
    "각도정렬": "정렬",

    # ===== 문자열 =====
    "String": "문자열",
    "string": "문자열",
    "String algorithms": "문자열",
    "문자열 처리": "문자열",
    "kmp": "문자열",
    "KMP": "문자열",
    "trie": "문자열",
    "트라이": "문자열",
    "라빈카프": "문자열",
    "아호코라식": "문자열",
    "접미사배열": "문자열",
    "suffix_tree": "문자열",
    "팰린드롬": "문자열",
    "정규표현식": "문자열",
    "Z알고리즘": "문자열",

    # ===== 이분탐색 =====
    "Binary Search": "이분탐색",
    "binary_search": "이분탐색",
    "Parametric Search": "이분탐색",
    "parametric_search": "이분탐색",
    "이진 탐색": "이분탐색",
    "매개 변수 탐색": "이분탐색",
    "파라메트릭 서치": "이분탐색",
    "삼분탐색": "이분탐색",

    # ===== 그리디 =====
    "Greedy": "그리디",
    "greedy": "그리디",
    "Greedy algorithms": "그리디",
    "greedy_algorithms": "그리디",

    # ===== DP =====
    "DP": "DP",
    "dp": "DP",
    "dynamic_programming": "DP",
    "Dynamic programming": "DP",
    "Dynamic Programming": "DP",
    "Dynamic\r\n  programming": "DP",
    "동적계획법": "DP",
    "점화식": "DP",
    "memoization": "DP",
    "Unbounded Knapsack": "DP",
    "LIS": "DP",
    "LCS": "DP",
    "knuth": "DP",
    "slope_trick": "DP",
    "비트마스킹": "DP",
    "분할정복": "DP",
    "CHT": "DP",
    "리차오트리": "DP",
    "kitamasa": "DP",

    # ===== BFS/DFS =====
    "BFS": "BFS/DFS",
    "DFS": "BFS/DFS",
    "bfs": "BFS/DFS",
    "dfs": "BFS/DFS",
    "BFS/DFS": "BFS/DFS",
    "graph_traversal": "BFS/DFS",
    "Graph traversal": "BFS/DFS",
    "그래프 탐색": "BFS/DFS",
    "flood_fill": "BFS/DFS",
    "bidirectional_search": "BFS/DFS",

    # ===== 그래프 =====
    "Graph": "그래프",
    "graphs": "그래프",
    "Graph algorithms": "그래프",
    "topological_sort": "그래프",
    "topological_sorting": "그래프",
    "위상정렬": "그래프",
    "SCC": "그래프",
    "MST": "그래프",
    "유니온파인드": "그래프",
    "이분그래프": "그래프",
    "이분매칭": "그래프",
    "네트워크플로우": "그래프",
    "오일러경로": "그래프",
    "오일러투어": "그래프",
    "단절점": "그래프",
    "bcc": "그래프",
    "격자그래프": "그래프",
    "dual_graph": "그래프",
    "planar_graph": "그래프",
    "dominator_tree": "그래프",
    "circulation": "그래프",
    "hungarian": "그래프",
    "hall": "그래프",
    "general_matching": "그래프",
    "stoer_wagner": "그래프",
    "stable_marriage": "그래프",
    "함수그래프": "그래프",
    "degree_sequence": "그래프",
    "cactus": "그래프",

    # ===== 백트래킹 =====
    "Backtracking": "백트래킹",
    "backtracking": "백트래킹",
    "dancing_links": "백트래킹",
    "knuth_x": "백트래킹",

    # ===== 완전탐색 =====
    "Brute Force": "완전탐색",
    "bruteforcing": "완전탐색",
    "brute_force": "완전탐색",
    "Complete search": "완전탐색",
    "complete_search": "완전탐색",
    "mitm": "완전탐색",
    "pbs": "완전탐색",

    # ===== 자료구조 =====
    "Data Structures": "자료구조",
    "Data structures": "자료구조",
    "data_structures": "자료구조",
    "기본 자료구조": "자료구조",
    "Stack": "자료구조",
    "Queue": "자료구조",
    "stack": "자료구조",
    "queue": "자료구조",
    "스택": "자료구조",
    "큐": "자료구조",
    "덱": "자료구조",
    "deque": "자료구조",
    "priority_queue": "자료구조",
    "우선순위큐": "자료구조",
    "heap": "자료구조",
    "segtree": "자료구조",
    "세그먼트트리": "자료구조",
    "연결리스트": "자료구조",
    "집합": "자료구조",
    "딕셔너리": "자료구조",
    "희소테이블": "자료구조",
    "multi_segtree": "자료구조",
    "kinetic_segtree": "자료구조",
    "cartesian_tree": "자료구조",
    "splay_tree": "자료구조",
    "rb_tree": "자료구조",
    "rope": "자료구조",
    "link_cut_tree": "자료구조",
    "top_tree": "자료구조",
    "tree_set": "자료구조",
    "offline_dynamic_connectivity": "자료구조",

    # ===== 수학 =====
    "Math": "수학",
    "math": "수학",
    "Mathematics": "수학",
    "Number theory": "수학",
    "number_theory": "수학",
    "정수론": "수학",
    "조합론": "수학",
    "Combinatorics": "수학",
    "primality_test": "수학",
    "소수판별": "수학",
    "소수": "수학",
    "소인수분해": "수학",
    "arithmetic": "수학",
    "Bit manipulation": "수학",
    "game_theory": "수학",
    "게임이론": "수학",
    "스프라그그런디": "수학",
    "hackenbush": "수학",
    "Geometry": "수학",
    "geometry": "수학",
    "기하": "수학",
    "기하학": "수학",
    "볼록껍질": "수학",
    "회전캘리퍼스": "수학",
    "선분교차": "수학",
    "half_plane_intersection": "수학",
    "min_enclosing_circle": "수학",
    "point_in_convex_polygon": "수학",
    "point_in_non_convex_polygon": "수학",
    "polygon_area": "수학",
    "delaunay": "수학",
    "voronoi": "수학",
    "geometric_boolean_operations": "수학",
    "geometry_hyper": "수학",
    "FFT": "수학",
    "다항식": "수학",
    "generating_function": "수학",
    "polynomial_interpolation": "수학",
    "행렬": "수학",
    "선형대수": "수학",
    "가우스소거": "수학",
    "xor_basis": "수학",
    "분할거듭제곱": "수학",
    "모듈러역원": "수학",
    "확장유클리드": "수학",
    "유클리드": "수학",
    "중국인나머지": "수학",
    "페르마소정리": "수학",
    "오일러피": "수학",
    "에라토스테네스": "수학",
    "pisano": "수학",
    "mobius_inversion": "수학",
    "discrete_log": "수학",
    "discrete_sqrt": "수학",
    "berlekamp_massey": "수학",
    "pythagoras": "수학",
    "pick": "수학",
    "burnside": "수학",
    "inclusion_and_exclusion": "수학",
    "harmonic_number": "수학",
    "기댓값": "수학",
    "확률": "수학",
    "통계": "수학",
    "floor_sum": "수학",
    "arbitrary_precision": "수학",
    "수치해석": "수학",
    "미적분": "수학",
    "green": "수학",

    # ===== 트리 =====
    "Tree": "트리",
    "trees": "트리",
    "tree_diameter": "트리",
    "LCA": "트리",
    "HLD": "트리",
    "센트로이드": "트리",
    "센트로이드분할": "트리",
    "리루팅": "트리",
    "tree_compression": "트리",
    "tree_decomposition": "트리",
    "tree_isomorphism": "트리",
    "smaller_to_larger": "트리",
    "euler_characteristic": "트리",

    # ===== 최단경로 =====
    "Shortest Path": "최단경로",
    "Shortest paths": "최단경로",
    "shortest_path": "최단경로",
    "Dijkstra": "최단경로",
    "dijkstra": "최단경로",
    "다익스트라": "최단경로",
    "bellman_ford": "최단경로",
    "벨만포드": "최단경로",
    "floyd_warshall": "최단경로",
    "플로이드": "최단경로",
    "dial": "최단경로",
    "tsp": "최단경로",

    # ===== 투포인터 =====
    "Two Pointers": "투포인터",
    "two_pointer": "투포인터",
    "two_pointers": "투포인터",
    "Sliding Window": "투포인터",
    "sliding_window": "투포인터",
    "슬라이딩윈도우": "투포인터",
    "누적합": "투포인터",
    "누적 합": "투포인터",
    "차분배열": "투포인터",

    # ===== 해시 =====
    "Hash": "해시",
    "hashing": "해시",
    "hash_set": "해시",
    "해시테이블": "해시",

    # ===== None으로 매핑 (삭제) - 허용 태그로 매핑 불가 =====
    "prefix_sum": None,
    "Constructive algorithms": None,
    "2_sat": None,
    "alien": None,
    "asgsag": None,
    "beats": None,
    "bitset_lcs": None,
    "bulldozer": None,
    "cdq": None,
    "duality": None,
    "gradient_descent": None,
    "hirschberg": None,
    "invariant": None,
    "lte": None,
    "majority_vote": None,
    "matroid": None,
    "maximum_subarray": None,
    "Mo알고리즘": None,
    "오프라인쿼리": None,
    "제곱근분할": None,
    "분할상환분석": None,
    "선형계획법": None,
    "최적화": None,
    "휴리스틱": None,
    "랜덤화": None,
    "simulated_annealing": None,
    "물리": None,
    "parity": None,
    "pigeonhole_principle": None,
    "재귀": None,
    "스위핑": None,
}


def normalize_topic(topic: str):  # -> str | None
    """
    토픽을 정규화합니다.

    Returns:
        정규화된 토픽 또는 None (삭제 대상)
    """
    if not topic:
        return None

    # 이미 허용된 태그면 그대로
    if topic in ALLOWED_TAGS:
        return topic

    # 매핑 테이블에서 찾기
    return TOPIC_NORMALIZATION.get(topic)


def normalize_skill_snapshot(snapshot: dict) -> dict:
    """
    skill_snapshot의 키를 정규화합니다.
    동일한 정규화 결과는 점수를 합산합니다.
    """
    if not snapshot:
        return {}

    normalized = {}
    for topic, score in snapshot.items():
        new_topic = normalize_topic(topic)
        if new_topic:
            # 이미 있으면 점수 평균
            if new_topic in normalized:
                normalized[new_topic] = (normalized[new_topic] + score) / 2
            else:
                normalized[new_topic] = score

    return normalized


def normalize_topic_list(items: list) -> list:
    """
    strengths/weaknesses 배열을 정규화합니다.
    동일한 정규화 결과는 점수가 높은/낮은 것을 선택합니다.
    """
    if not items:
        return []

    normalized_map = {}
    for item in items:
        topic = item.get("topic")
        new_topic = normalize_topic(topic)

        if not new_topic:
            continue

        score = item.get("score", 0)
        insight = item.get("insight", "")

        if new_topic not in normalized_map:
            normalized_map[new_topic] = {
                "topic": new_topic,
                "score": score,
                "insight": insight
            }
        else:
            # 이미 있으면 점수 비교 (strengths는 높은 것, weaknesses는 낮은 것)
            # 여기서는 일단 점수가 더 극단적인 것을 선택
            existing = normalized_map[new_topic]
            if abs(score - 0.5) > abs(existing["score"] - 0.5):
                normalized_map[new_topic] = {
                    "topic": new_topic,
                    "score": score,
                    "insight": insight
                }

    return list(normalized_map.values())


def main():
    # Supabase 클라이언트 생성
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        print("❌ SUPABASE_URL 또는 SUPABASE_KEY가 설정되지 않았습니다.")
        return

    supabase = create_client(supabase_url, supabase_key)

    # 모든 리포트 조회
    print("📊 user_analysis_reports 조회 중...")
    result = supabase.table("user_analysis_reports").select("*").execute()

    if not result.data:
        print("데이터가 없습니다.")
        return

    print(f"총 {len(result.data)}개 리포트 발견")

    updated_count = 0

    for report in result.data:
        report_id = report.get("id")
        user_id = report.get("user_id")

        # 원본 데이터
        skill_snapshot = report.get("skill_snapshot") or {}
        strengths = report.get("strengths") or []
        weaknesses = report.get("weaknesses") or []

        # 정규화
        new_snapshot = normalize_skill_snapshot(skill_snapshot)
        new_strengths = normalize_topic_list(strengths)
        new_weaknesses = normalize_topic_list(weaknesses)

        # 변경 여부 확인
        snapshot_changed = new_snapshot != skill_snapshot
        strengths_changed = len(new_strengths) != len(strengths) or any(
            s.get("topic") != ns.get("topic")
            for s, ns in zip(sorted(strengths, key=lambda x: x.get("topic", "")),
                            sorted(new_strengths, key=lambda x: x.get("topic", "")))
        ) if new_strengths else strengths != []
        weaknesses_changed = len(new_weaknesses) != len(weaknesses) or any(
            w.get("topic") != nw.get("topic")
            for w, nw in zip(sorted(weaknesses, key=lambda x: x.get("topic", "")),
                            sorted(new_weaknesses, key=lambda x: x.get("topic", "")))
        ) if new_weaknesses else weaknesses != []

        if snapshot_changed or strengths_changed or weaknesses_changed:
            print(f"\n🔄 Updating report {report_id} (user: {user_id[:8]}...)")

            if snapshot_changed:
                old_keys = set(skill_snapshot.keys())
                new_keys = set(new_snapshot.keys())
                removed = old_keys - new_keys
                if removed:
                    print(f"   skill_snapshot 제거: {removed}")
                print(f"   skill_snapshot: {len(skill_snapshot)} → {len(new_snapshot)} topics")

            if strengths_changed:
                old_topics = [s.get("topic") for s in strengths]
                new_topics = [s.get("topic") for s in new_strengths]
                print(f"   strengths: {old_topics} → {new_topics}")

            if weaknesses_changed:
                old_topics = [w.get("topic") for w in weaknesses]
                new_topics = [w.get("topic") for w in new_weaknesses]
                print(f"   weaknesses: {old_topics} → {new_topics}")

            # DB 업데이트
            update_data = {
                "skill_snapshot": new_snapshot,
                "strengths": new_strengths,
                "weaknesses": new_weaknesses,
            }

            supabase.table("user_analysis_reports").update(update_data).eq("id", report_id).execute()
            updated_count += 1

    print(f"\n✅ 완료! {updated_count}개 리포트 업데이트됨")


if __name__ == "__main__":
    main()
