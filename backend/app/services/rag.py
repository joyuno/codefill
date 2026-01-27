"""
RAG Service
Hybrid search (vector + keyword) and code generation fallback
"""

import asyncio
import json
from typing import List, Dict, Any, Optional, Tuple
from ..database import get_supabase_client
from ..config import get_settings
from .embedding import embedding_service
from .openrouter import openrouter_codegen as openrouter_service
from ..prompts import CODE_GEN_SYSTEM_PROMPT

# LLM 모델 설정
settings = get_settings()


def normalize_code_newlines(code: str) -> str:
    """DB에 저장된 코드의 이스케이프된 줄바꿈을 실제 줄바꿈으로 변환"""
    if not code:
        return code
    code = code.replace('\\n', '\n')
    code = code.replace('\\t', '\t')
    return code


class RAGService:
    """Service for RAG-based problem search and code generation."""

    # Similarity threshold for fallback to code generation
    SIMILARITY_THRESHOLD = 0.30  # Below this, trigger code generation

    # Agentic RAG: Minimum metadata for skipping semantic search
    MIN_METADATA_FOR_SKIP = 2  # topics + difficulty 있으면 메타데이터 검색만

    # ============================================================
    # Topic Mapping (한국어 ↔ 영어/백준 태그)
    # 검색 시 양방향으로 사용됨
    # ============================================================
    TOPIC_MAPPING = {
        # ==================== 기본 알고리즘 ====================
        "DP": ["dp", "dynamic_programming", "dp_tree", "dp_digit", "dp_bitfield", "dp_deque", "dp_sum_over_subsets", "dp_connection_profile", "memoization", "knapsack"],
        "동적 프로그래밍": ["dp", "dynamic_programming", "dp_tree", "dp_digit", "dp_bitfield", "dp_deque", "memoization", "knapsack"],
        "그리디": ["greedy", "greedy_algorithms"],
        "탐욕법": ["greedy", "greedy_algorithms"],
        "완전 탐색": ["bruteforcing", "brute_force", "complete_search", "exhaustive_search"],
        "완전탐색": ["bruteforcing", "brute_force", "complete_search", "exhaustive_search"],  # 붙여쓰기 버전 (칩 매칭용)
        "브루트포스": ["bruteforcing", "brute_force", "complete_search"],
        "백트래킹": ["backtracking", "dfs", "recursion"],
        "분할 정복": ["divide_and_conquer", "divide_and_conquer_optimization", "recursion"],

        # ==================== 그래프 ====================
        "그래프": ["graphs", "graph_traversal", "BFS", "DFS", "bfs", "dfs", "shortest_path"],
        "BFS/DFS": ["BFS", "DFS", "BFS/DFS", "bfs", "dfs", "그래프", "graph_traversal"],
        "BFS": ["BFS", "bfs", "0_1_bfs", "graph_traversal", "breadth_first_search", "flood_fill"],
        "DFS": ["DFS", "dfs", "graph_traversal", "depth_first_search", "flood_fill"],
        "너비 우선 탐색": ["bfs", "0_1_bfs", "graph_traversal", "breadth_first_search"],
        "깊이 우선 탐색": ["dfs", "graph_traversal", "depth_first_search"],
        "최단 경로": ["shortest_path", "dijkstra", "bellman_ford", "floyd_warshall", "0_1_bfs"],
        "최단경로": ["shortest_path", "dijkstra", "bellman_ford", "floyd_warshall", "0_1_bfs"],  # 붙여쓰기 버전 (칩 매칭용)
        "다익스트라": ["dijkstra", "shortest_path"],
        "벨만 포드": ["bellman_ford", "shortest_path"],
        "플로이드": ["floyd_warshall", "shortest_path"],
        "플로이드 워셜": ["floyd_warshall", "shortest_path"],
        "미로": ["bfs", "dfs", "graph_traversal", "flood_fill"],
        "미로 탐색": ["bfs", "dfs", "graph_traversal", "flood_fill"],
        "위상 정렬": ["topological_sort", "dag", "graphs"],
        "사이클 검출": ["graphs", "dfs", "functional_graph"],
        "유니온 파인드": ["disjoint_set", "union_find", "graphs"],
        "서로소 집합": ["disjoint_set", "union_find"],
        "최소 신장 트리": ["mst", "graphs", "greedy"],
        "MST": ["mst", "graphs", "greedy"],
        "강한 연결 요소": ["scc", "graphs", "dfs"],
        "SCC": ["scc", "graphs"],
        "이분 그래프": ["bipartite_graph", "graphs", "bfs", "dfs"],
        "이분 매칭": ["bipartite_matching", "flow", "graphs"],
        "네트워크 플로우": ["flow", "mcmf", "mfmc", "circulation"],
        "플로우": ["flow", "mcmf", "mfmc"],
        "LCA": ["lca", "trees", "sparse_table"],
        "최소 공통 조상": ["lca", "trees"],

        # ==================== 탐색/정렬 ====================
        "이진 탐색": ["binary_search", "parametric_search"],
        "이분 탐색": ["binary_search", "parametric_search"],
        "이분탐색": ["binary_search", "parametric_search"],  # 붙여쓰기 버전 (칩 매칭용)
        "정렬": ["sorting", "merge_sort", "quick_sort"],
        "투 포인터": ["two_pointer", "two_pointers", "sliding_window"],
        "투포인터": ["two_pointer", "two_pointers", "sliding_window", "슬라이딩윈도우"],
        "슬라이딩 윈도우": ["sliding_window", "two_pointer", "two_pointers", "deque_trick", "monotone_queue_optimization"],
        "슬라이딩윈도우": ["sliding_window", "two_pointer", "two_pointers", "슬라이딩윈도우"],

        # ==================== 자료구조 ====================
        "자료구조": ["data_structures", "stack", "queue", "deque", "priority_queue", "heap", "hashing", "trees"],
        "스택": ["stack", "data_structures"],
        "큐": ["queue", "deque", "data_structures"],
        "덱": ["deque", "deque_trick", "data_structures"],
        "힙": ["priority_queue", "heap", "data_structures"],
        "우선순위 큐": ["priority_queue", "heap", "data_structures"],
        "해시": ["hashing", "hash_set", "data_structures"],
        "해시맵": ["hashing", "hash_set", "data_structures"],
        "트리": ["trees", "tree_diameter", "tree_isomorphism", "data_structures"],
        "세그먼트 트리": ["segtree", "lazyprop", "multi_segtree", "pst", "merge_sort_tree"],
        "펜윅 트리": ["segtree", "data_structures"],
        "트라이": ["trie", "string", "data_structures"],
        "연결 리스트": ["linked_list", "data_structures"],

        # ==================== 문자열 ====================
        "문자열": ["string", "kmp", "rabin_karp", "trie", "suffix_array", "manacher", "aho_corasick", "hashing"],
        "KMP": ["kmp", "string"],
        "라빈 카프": ["rabin_karp", "string", "hashing"],
        "접미사 배열": ["suffix_array", "string"],
        "팰린드롬": ["manacher", "palindrome_tree", "string"],
        "LCS": ["lcs", "dp", "string"],
        "최장 공통 부분 수열": ["lcs", "dp", "string"],
        "LIS": ["lis", "dp", "binary_search"],
        "최장 증가 부분 수열": ["lis", "dp", "binary_search"],

        # ==================== 수학/정수론 ====================
        "수학": ["math", "arithmetic", "number_theory"],
        "정수론": ["number_theory", "prime_factorization", "sieve", "euclidean", "modular_multiplicative_inverse"],
        "소수": ["primality_test", "sieve", "miller_rabin", "pollard_rho"],
        "소수 판별": ["primality_test", "sieve", "miller_rabin"],
        "에라토스테네스": ["sieve", "primality_test"],
        "유클리드": ["euclidean", "extended_euclidean", "gcd"],
        "확장 유클리드": ["extended_euclidean", "euclidean"],
        "모듈러 연산": ["modular_multiplicative_inverse", "exponentiation_by_squaring"],
        "조합론": ["combinatorics", "permutation_cycle_decomposition", "lucas", "crt"],
        "확률": ["probability", "linearity_of_expectation", "statistics"],
        "기하": ["geometry", "convex_hull", "rotating_calipers", "line_intersection", "geometry_3d"],
        "기하학": ["geometry", "convex_hull", "rotating_calipers", "line_intersection"],
        "볼록 껍질": ["convex_hull", "geometry", "rotating_calipers"],
        "컨벡스 헐": ["convex_hull", "geometry"],
        "CCW": ["geometry", "convex_hull", "line_intersection"],
        "행렬": ["linear_algebra", "gaussian_elimination", "matrix_exponentiation"],
        "FFT": ["fft", "math", "polynomial_interpolation"],

        # ==================== 게임 이론/기타 ====================
        "게임 이론": ["game_theory", "sprague_grundy", "hackenbush"],
        "스프라그 그런디": ["sprague_grundy", "game_theory"],
        "비트마스킹": ["bitmask", "bitset", "dp_bitfield"],
        "비트마스크": ["bitmask", "bitset", "dp_bitfield"],
        "구현": ["implementation", "simulation", "case_work", "ad_hoc"],
        "시뮬레이션": ["simulation", "implementation"],
        "파싱": ["parsing", "string", "implementation"],
        "정규표현식": ["regex", "string"],
        "좌표 압축": ["coordinate_compression", "sorting"],
        "누적 합": ["prefix_sum", "difference_array"],
        "구간 합": ["prefix_sum", "segtree"],
        "재귀": ["recursion", "divide_and_conquer", "dfs"],
        "메모이제이션": ["dp", "memoization", "recursion"],

        # ==================== 고급 알고리즘 ====================
        "센트로이드 분할": ["centroid", "centroid_decomposition", "trees"],
        "HLD": ["hld", "trees", "segtree"],
        "Heavy-Light 분할": ["hld", "trees"],
        "CHT": ["cht", "li_chao_tree", "dp"],
        "컨벡스 헐 트릭": ["cht", "li_chao_tree", "dp"],
        "Mo's 알고리즘": ["mo", "sqrt_decomposition"],
        "제곱근 분할": ["sqrt_decomposition", "mo"],
        "오일러 투어": ["euler_tour_technique", "trees"],
        "오일러 경로": ["eulerian_path", "graphs"],
        "단절점": ["articulation", "graphs", "dfs"],
        "단절선": ["articulation", "graphs", "dfs"],

        # ==================== 백준 영어 태그 → 한국어 검색 지원 ====================
        # (영어 태그로 검색해도 찾을 수 있도록)
        "dp": ["dp", "dynamic_programming", "dp_tree", "dp_digit"],
        "bfs": ["bfs", "0_1_bfs", "graph_traversal"],
        "dfs": ["dfs", "graph_traversal", "backtracking"],
        "greedy": ["greedy"],
        "implementation": ["implementation", "simulation", "ad_hoc"],
        "simulation": ["simulation", "implementation"],
        "string": ["string", "kmp", "trie", "hashing"],
        "binary_search": ["binary_search", "parametric_search"],
        "graphs": ["graphs", "graph_traversal", "bfs", "dfs"],
        "sorting": ["sorting"],
        "math": ["math", "arithmetic", "number_theory"],
        "geometry": ["geometry", "convex_hull"],
        "data_structures": ["data_structures", "segtree", "stack", "queue"],
        "trees": ["trees", "lca", "hld"],
        "number_theory": ["number_theory", "sieve", "primality_test"],
        "combinatorics": ["combinatorics", "probability"],
        "backtracking": ["backtracking", "dfs", "recursion"],
        "dijkstra": ["dijkstra", "shortest_path"],
        "shortest_path": ["shortest_path", "dijkstra", "bellman_ford", "floyd_warshall"],
        "flow": ["flow", "mcmf", "bipartite_matching"],
        "segtree": ["segtree", "lazyprop", "pst"],
        "divide_and_conquer": ["divide_and_conquer", "recursion"],
        "prefix_sum": ["prefix_sum", "difference_array"],
        "priority_queue": ["priority_queue", "heap"],
        "disjoint_set": ["disjoint_set", "union_find"],
        "mst": ["mst", "graphs"],
        "hashing": ["hashing", "string"],
        "recursion": ["recursion", "dfs", "divide_and_conquer"],
        "bruteforcing": ["bruteforcing", "brute_force", "exhaustive_search"],
    }

    # Difficulty mapping (Korean -> English)
    DIFFICULTY_MAPPING = {
        # 백준 난이도
        "브론즈": "easy",
        "실버": "easy",
        "골드": "medium",
        "플래티넘": "hard",
        "다이아": "hard",
        "루비": "very_hard",
        # 일반 표현
        "쉬움": "easy",
        "쉬운": "easy",
        "보통": "medium",
        "중간": "medium",
        "어려움": "hard",
        "어려운": "hard",
        "초급": "easy",
        "중급": "medium",
        "고급": "hard",
    }

    def __init__(self):
        self.db = get_supabase_client()

    def _normalize_difficulty(self, difficulty: str) -> str:
        """
        난이도를 DB 형식으로 정규화

        Args:
            difficulty: 입력 난이도 (한국어 또는 영어)

        Returns:
            정규화된 난이도 (easy/medium/hard/very_hard)
        """
        if not difficulty:
            return None

        difficulty_lower = difficulty.lower().strip()

        # 이미 정규화된 값인 경우
        if difficulty_lower in ["easy", "medium", "hard", "very_hard", "medium_hard"]:
            return difficulty_lower

        # 한국어 매핑 확인
        return self.DIFFICULTY_MAPPING.get(difficulty, difficulty_lower)

    # ============================================================
    # Agentic RAG: 검색 필요성 판단 및 스마트 검색
    # ============================================================

    def _has_sufficient_metadata(
        self,
        topics: List[str] = None,
        difficulty: str = None,
        language: str = None,
    ) -> bool:
        """
        메타데이터만으로 검색이 가능한지 판단

        조건:
        - topics가 있고 + difficulty가 있으면 → 메타데이터 검색 가능
        - 또는 topics가 2개 이상이면 → 메타데이터 검색 가능

        Returns:
            True: 메타데이터만으로 충분 (임베딩 스킵)
            False: 시맨틱 검색 필요
        """
        metadata_count = 0
        if topics and len(topics) > 0:
            metadata_count += 1
            if len(topics) >= 2:
                metadata_count += 1  # 토픽이 구체적
        if difficulty:
            metadata_count += 1
        if language:
            metadata_count += 0.5  # 언어는 보조 필터

        return metadata_count >= self.MIN_METADATA_FOR_SKIP

    async def search_problems_metadata_only(
        self,
        topics: List[str] = None,
        difficulty: str = None,
        language: str = None,
        limit: int = 5,
        exclude_ids: List[str] = None,
        source_filter: str = None,
    ) -> List[Dict[str, Any]]:
        """
        메타데이터만으로 문제 검색 (임베딩 비용 0)

        DB 필터링만 사용하여 빠르게 검색합니다.
        topics/difficulty가 명확할 때 사용합니다.

        Args:
            topics: 주제 필터
            difficulty: 난이도 필터
            language: 언어 필터
            limit: 최대 결과 수
            exclude_ids: 제외할 문제 ID
            source_filter: 출처 필터 (baekjoon, leetcode) - programmers는 검색에서 항상 제외

        Returns:
            검색된 문제 목록
        """
        try:
            print(f"[RAG:Metadata] Searching with metadata only: topics={topics}, diff={difficulty}, lang={language}, source={source_filter}")

            # programmers는 검색 RAG에서 항상 제외 (저작권)
            db_query = self.db.table("base_problems").select("*").neq("source", "programmers")

            # 출처 필터 적용 (baekjoon, leetcode 등)
            if source_filter and source_filter != "programmers":
                db_query = db_query.eq("source", source_filter)
                print(f"[RAG:Metadata] Applied source filter: {source_filter}")

            # 난이도 필터
            if difficulty:
                db_query = db_query.eq("difficulty", difficulty)

            # 토픽 필터 (확장된 토픽 사용)
            if topics:
                expanded_topics = self._expand_topics(topics)
                db_query = db_query.overlaps("tags", expanded_topics)

            # 충분한 결과를 위해 여유있게 가져오기
            fetch_limit = limit * 3 if language else limit
            db_query = db_query.limit(fetch_limit)

            response = db_query.execute()
            problems = response.data or []

            # 언어 필터링 (solutions 배열 내부 검색)
            if language and problems:
                problems = [
                    p for p in problems
                    if any(s.get("language") == language for s in p.get("solutions", []))
                ]

            # 제외 ID 필터링
            if exclude_ids and problems:
                exclude_set = set(exclude_ids)
                problems = [p for p in problems if p.get("id") not in exclude_set]

            # 결과가 있으면 랜덤하게 섞어서 다양성 확보
            if len(problems) > limit:
                import random
                random.shuffle(problems)

            print(f"[RAG:Metadata] Found {len(problems)} problems (returning top {limit})")
            return problems[:limit]

        except Exception as e:
            print(f"[RAG:Metadata] Error: {e}")
            import traceback
            traceback.print_exc()
            return []

    async def search_problems_smart(
        self,
        query: str,
        topics: List[str] = None,
        difficulty: str = None,
        language: str = None,
        limit: int = 5,
        exclude_ids: List[str] = None,
        user_context: Dict[str, Any] = None,
        source_filter: str = None,
        is_corporate_test: bool = False,
    ) -> Tuple[List[Dict[str, Any]], bool, str]:
        """
        Agentic RAG: 검색 필요성을 판단하여 최적의 방법 선택

        1단계: 메타데이터 충분성 확인
        2단계: 충분하면 메타데이터 검색, 아니면 시맨틱 검색

        Args:
            query: 검색 쿼리
            topics: 주제 필터
            difficulty: 난이도 필터
            language: 언어 필터
            limit: 최대 결과 수
            exclude_ids: 제외할 문제 ID
            user_context: 개인화 컨텍스트
            source_filter: 출처 필터 (baekjoon, leetcode) - programmers는 검색에서 항상 제외
            is_corporate_test: 대기업 코테 관련 여부 (True면 생성 시 programmers RAG도 참고)

        Returns:
            Tuple of (results, should_fallback, search_method)
            - results: 검색 결과
            - should_fallback: CodeGen 필요 여부
            - search_method: "metadata" | "semantic" | "hybrid"
        """
        # 난이도 정규화 (한국어 → 영어)
        normalized_difficulty = self._normalize_difficulty(difficulty)
        print(f"[RAG:Smart] Normalized difficulty: {difficulty} → {normalized_difficulty}")

        # 개인화 컨텍스트에서 추가 정보 추출
        enhanced_topics = topics or []
        if user_context and not topics:
            weak_topics = user_context.get("weak_topics", [])
            if weak_topics:
                enhanced_topics = weak_topics[:2]

        if user_context and not normalized_difficulty:
            normalized_difficulty = self._normalize_difficulty(user_context.get("preferred_difficulty"))

        # Agentic 판단: 메타데이터만으로 충분한가?
        if self._has_sufficient_metadata(enhanced_topics or topics, normalized_difficulty, language):
            print(f"[RAG:Smart] Using METADATA-ONLY search (cost: $0)")

            results = await self.search_problems_metadata_only(
                topics=enhanced_topics or topics,
                difficulty=normalized_difficulty,
                language=language,
                limit=limit,
                exclude_ids=exclude_ids,
                source_filter=source_filter,
            )

            # 결과가 부족하면 시맨틱 검색으로 폴백 (타임아웃 5초)
            if len(results) < 2:
                print(f"[RAG:Smart] Metadata search insufficient ({len(results)} results), falling back to semantic")
                try:
                    results, should_fallback = await asyncio.wait_for(
                        self.search_problems_hybrid(
                            query=query,
                            topics=enhanced_topics or topics,
                            difficulty=normalized_difficulty,
                            language=language,
                            limit=limit,
                            exclude_ids=exclude_ids,
                            user_context=user_context,
                            source_filter=source_filter,
                        ),
                        timeout=10.0,  # 10초 타임아웃
                    )
                except asyncio.TimeoutError:
                    print(f"[RAG:Smart] Semantic search timeout, using keyword fallback")
                    results = await self._keyword_search(
                        topics=enhanced_topics or topics,
                        difficulty=normalized_difficulty,
                        language=language,
                        limit=limit,
                        source_filter=source_filter,
                    )
                    return results, len(results) == 0, "keyword_fallback"
                return results, should_fallback, "hybrid"

            should_fallback = len(results) == 0
            return results, should_fallback, "metadata"

        else:
            print(f"[RAG:Smart] Using SEMANTIC search (insufficient metadata)")

            try:
                results, should_fallback = await asyncio.wait_for(
                    self.search_problems_hybrid(
                        query=query,
                        topics=enhanced_topics or topics,
                        difficulty=normalized_difficulty,
                        language=language,
                        limit=limit,
                        exclude_ids=exclude_ids,
                        user_context=user_context,
                        source_filter=source_filter,
                    ),
                    timeout=10.0,  # 10초 타임아웃
                )
            except asyncio.TimeoutError:
                print(f"[RAG:Smart] Semantic search timeout, using keyword fallback")
                results = await self._keyword_search(
                    topics=enhanced_topics or topics,
                    difficulty=normalized_difficulty,
                    language=language,
                    limit=limit,
                    source_filter=source_filter,
                )
                return results, len(results) == 0, "keyword_fallback"
            return results, should_fallback, "semantic"

    # ============================================================
    # 기존 Hybrid Search (시맨틱 검색)
    # ============================================================

    async def search_problems_hybrid(
        self,
        query: str,
        topics: List[str] = None,
        difficulty: str = None,
        language: str = None,
        limit: int = 5,
        exclude_ids: List[str] = None,
        user_context: Dict[str, Any] = None,
        source_filter: str = None,
    ) -> Tuple[List[Dict[str, Any]], bool]:
        """
        Hybrid search: Filter by tags/difficulty FIRST, then rank by vector similarity.

        Args:
            query: Search query text
            topics: Filter by topics
            difficulty: Filter by difficulty (easy/medium/hard)
            language: Filter by language (python/java/cpp)
            limit: Maximum results to return
            exclude_ids: Problem IDs to exclude (e.g., already solved)
            user_context: Personalization context (weak_topics, skill_levels, etc.)
            source_filter: 출처 필터 (baekjoon, leetcode) - programmers는 검색에서 항상 제외

        Returns:
            Tuple of (results, should_fallback_to_generation)
        """
        try:
            # Step 0: Enhance query with user context (personalization)
            enhanced_topics = topics or []
            if user_context:
                weak_topics = user_context.get("weak_topics", [])
                # Add weak topics to search if not already specified
                if weak_topics and not topics:
                    enhanced_topics = weak_topics[:2]
                # Adjust difficulty based on skill level if not specified
                if not difficulty and user_context.get("preferred_difficulty"):
                    difficulty = user_context["preferred_difficulty"]

            # Step 1: Build base query with filters
            # ⚠️ programmers 문제는 저작권 문제로 검색 결과에서 제외
            # (programmers_embeddings는 code generation RAG 컨텍스트로만 사용)
            db_query = self.db.table("base_problems").select("*").neq("source", "programmers")

            # 출처 필터 적용 (baekjoon, leetcode 등)
            if source_filter and source_filter != "programmers":
                db_query = db_query.eq("source", source_filter)
                print(f"[RAG:Hybrid] Applied source filter: {source_filter}")

            # Apply difficulty filter
            if difficulty:
                db_query = db_query.eq("difficulty", difficulty)

            # Apply topic filter (using expanded topics)
            if enhanced_topics:
                expanded_topics = self._expand_topics(enhanced_topics)
                # Use overlaps for array intersection
                db_query = db_query.overlaps("tags", expanded_topics)
            elif topics:
                expanded_topics = self._expand_topics(topics)
                db_query = db_query.overlaps("tags", expanded_topics)

            # Limit to reasonable number for embedding comparison
            db_query = db_query.limit(100)
            filtered_response = db_query.execute()
            filtered_problems = filtered_response.data or []

            if not filtered_problems:
                # No matches with filters, try without difficulty
                if difficulty:
                    return await self._search_without_difficulty(query, topics, language, limit)
                return [], True

            # Step 2: Generate query embedding
            query_embedding = await embedding_service.generate_embedding(query)

            # Step 3: Get embeddings for filtered problems and calculate similarity
            problem_ids = [p["id"] for p in filtered_problems]
            embeddings_response = self.db.table("problem_embeddings").select("problem_id, embedding").in_("problem_id", problem_ids).execute()

            # Parse embeddings (returned as strings from pgvector)
            embeddings_map = {}
            for e in (embeddings_response.data or []):
                emb = e["embedding"]
                if isinstance(emb, str):
                    emb = json.loads(emb)
                embeddings_map[e["problem_id"]] = emb

            # Calculate similarity and rank
            import numpy as np
            query_vec = np.array(query_embedding)

            results = []
            for problem in filtered_problems:
                pid = problem["id"]
                if pid in embeddings_map:
                    prob_vec = np.array(embeddings_map[pid])
                    similarity = float(np.dot(query_vec, prob_vec) / (np.linalg.norm(query_vec) * np.linalg.norm(prob_vec)))
                    problem["similarity"] = similarity
                    results.append(problem)

            # Sort by similarity
            results.sort(key=lambda x: x.get("similarity", 0), reverse=True)

            # Step 4: Apply language filter if needed
            if language:
                results = [
                    r for r in results
                    if any(s.get("language") == language for s in r.get("solutions", []))
                ]

            # Step 5: Exclude already solved problems (personalization)
            if exclude_ids:
                exclude_set = set(exclude_ids)
                results = [r for r in results if r.get("id") not in exclude_set]

            # Step 6: Check fallback
            # If we have filtered results (by topic/difficulty), don't fallback
            # Only fallback if no results at all
            should_fallback = len(results) == 0

            # Step 7: 🚀 MMR 다양성 재정렬 (결과가 충분할 때만)
            if len(results) > limit:
                results = self._mmr_rerank(
                    results=results,
                    embeddings_map=embeddings_map,
                    query_embedding=query_embedding,
                    limit=limit,
                    lambda_param=0.7,  # 70% 관련성, 30% 다양성
                )
                print(f"[RAG:Hybrid] Applied MMR reranking for diversity")

            # Step 8: 🚀 검색 품질 평가 (비동기, 로깅용)
            await self._evaluate_search_quality(
                request_params={
                    "topics": topics,
                    "difficulty": difficulty,
                    "language": language,
                },
                results=results[:limit],
                user_context=user_context,
            )

            return results[:limit], should_fallback

        except Exception as e:
            print(f"Hybrid search error: {e}")
            import traceback
            traceback.print_exc()
            return await self._keyword_search(topics, difficulty, language, limit), True

    async def _search_without_difficulty(
        self,
        query: str,
        topics: List[str],
        language: str,
        limit: int,
    ) -> Tuple[List[Dict[str, Any]], bool]:
        """Fallback search without difficulty filter."""
        try:
            # programmers 제외 (저작권)
            db_query = self.db.table("base_problems").select("*").neq("source", "programmers")

            if topics:
                expanded_topics = self._expand_topics(topics)
                db_query = db_query.overlaps("tags", expanded_topics)

            db_query = db_query.limit(50)
            response = db_query.execute()
            problems = response.data or []

            if not problems:
                return [], True

            # Rank by embedding similarity
            query_embedding = await embedding_service.generate_embedding(query)
            problem_ids = [p["id"] for p in problems]
            embeddings_response = self.db.table("problem_embeddings").select("problem_id, embedding").in_("problem_id", problem_ids).execute()

            # Parse embeddings (returned as strings from pgvector)
            embeddings_map = {}
            for e in (embeddings_response.data or []):
                emb = e["embedding"]
                if isinstance(emb, str):
                    emb = json.loads(emb)
                embeddings_map[e["problem_id"]] = emb

            import numpy as np
            query_vec = np.array(query_embedding)

            results = []
            for problem in problems:
                pid = problem["id"]
                if pid in embeddings_map:
                    prob_vec = np.array(embeddings_map[pid])
                    similarity = float(np.dot(query_vec, prob_vec) / (np.linalg.norm(query_vec) * np.linalg.norm(prob_vec)))
                    problem["similarity"] = similarity
                    results.append(problem)

            results.sort(key=lambda x: x.get("similarity", 0), reverse=True)
            return results[:limit], len(results) == 0

        except Exception as e:
            print(f"Search without difficulty error: {e}")
            return [], True

    async def _keyword_search(
        self,
        topics: List[str] = None,
        difficulty: str = None,
        language: str = None,
        limit: int = 5,
        source_filter: str = None,
    ) -> List[Dict[str, Any]]:
        """
        Fallback keyword-based search.
        """
        try:
            # programmers 제외 (저작권)
            query = self.db.table("base_problems").select("*").neq("source", "programmers")

            # 출처 필터 적용
            if source_filter and source_filter != "programmers":
                query = query.eq("source", source_filter)

            if difficulty:
                query = query.eq("difficulty", difficulty)

            if topics:
                # Use contains for array overlap
                query = query.contains("tags", topics)

            response = query.limit(limit).execute()
            return response.data or []

        except Exception as e:
            print(f"Keyword search error: {e}")
            return []

    def _expand_topics(self, topics: List[str]) -> List[str]:
        """Expand Korean topics to English equivalents."""
        expanded = set()
        for topic in topics:
            topic_lower = topic.lower()
            # Add original
            expanded.add(topic)
            # Check mapping
            if topic in self.TOPIC_MAPPING:
                expanded.update(self.TOPIC_MAPPING[topic])
            # Also check lowercase
            for key, values in self.TOPIC_MAPPING.items():
                if key.lower() == topic_lower:
                    expanded.update(values)
        return list(expanded)

    def _apply_filters(
        self,
        results: List[Dict[str, Any]],
        topics: List[str] = None,
        difficulty: str = None,
        language: str = None,
    ) -> List[Dict[str, Any]]:
        """
        Apply additional filters to search results.
        Uses flexible matching for topics.
        """
        filtered = results

        if difficulty:
            filtered = [r for r in filtered if r.get("difficulty") == difficulty]

        if topics:
            # Expand topics to include English equivalents
            expanded_topics = self._expand_topics(topics)
            expanded_lower = [t.lower() for t in expanded_topics]

            filtered = [
                r for r in filtered
                if any(
                    tag.lower() in expanded_lower or
                    any(et.lower() in tag.lower() for et in expanded_topics)
                    for tag in r.get("tags", [])
                )
            ]

        if language:
            filtered = [
                r for r in filtered
                if any(
                    s.get("language") == language
                    for s in r.get("solutions", [])
                )
            ]

        return filtered

    async def generate_problem_with_rag(
        self,
        user_request: Dict[str, Any],
        similar_problems: List[Dict[str, Any]],
        user_context: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Generate a new problem using RAG context from similar problems.

        Args:
            user_request: Collected info from chat agent
            similar_problems: Similar problems from vector search
            user_context: User onboarding data

        Returns:
            Generated problem data
        """
        print(f"[CodeGen] Starting generation...")
        print(f"[CodeGen] user_request: {user_request}")
        print(f"[CodeGen] Model: {settings.llm_model_code_gen}")

        user_context = user_context or {}

        # Format similar problems for context (question + solutions 포함)
        similar_context = []
        code_stats = {"total_lines": 0, "total_chars": 0, "count": 0}  # 코드 통계

        for p in similar_problems[:3]:  # Top 3 as context
            # solutions 코드 추출 (사용자가 선택한 언어 우선)
            solutions = p.get("solutions", [])
            solution_code = None
            preferred_lang = user_request.get("language", "python")

            # 선호 언어 코드 먼저 찾기
            for sol in solutions:
                if sol.get("language") == preferred_lang:
                    solution_code = normalize_code_newlines(sol.get("code", ""))[:2000]  # 2000자 제한
                    break

            # 없으면 첫 번째 솔루션 사용
            if not solution_code and solutions:
                solution_code = normalize_code_newlines(solutions[0].get("code", ""))[:2000]

            # 🆕 코드 통계 수집 (생성 시 참고용)
            if solution_code:
                code_stats["total_lines"] += solution_code.count("\n") + 1
                code_stats["total_chars"] += len(solution_code)
                code_stats["count"] += 1

            similar_context.append({
                "title": p.get("name", ""),
                "question": p.get("question", ""),  # 전체 question 전달
                "tags": p.get("tags", []),
                "difficulty": p.get("difficulty", ""),
                "solution_code": solution_code,  # 솔루션 코드 추가
                "solution_language": preferred_lang if solution_code else None,
            })

        # 🆕 평균 코드 통계 계산
        if code_stats["count"] > 0:
            avg_lines = code_stats["total_lines"] // code_stats["count"]
            avg_chars = code_stats["total_chars"] // code_stats["count"]
            user_request["code_length_guide"] = {
                "avg_lines": avg_lines,
                "avg_chars": avg_chars,
                "target_range": f"{max(10, avg_lines - 10)}~{avg_lines + 10}줄"
            }
            print(f"[CodeGen] Code stats: avg {avg_lines} lines, {avg_chars} chars")

        system_prompt = CODE_GEN_SYSTEM_PROMPT.format(
            user_request=json.dumps(user_request, ensure_ascii=False),
            similar_problems=json.dumps(similar_context, ensure_ascii=False),
            user_status=user_context.get("status", "unknown"),
            user_goal=user_context.get("goal", "unknown"),
            user_level=user_context.get("level", "intermediate"),
            strong_algorithms=", ".join(
                user_context.get("strong_algorithms", [])
            ) or "없음",
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "사용자 요청에 맞는 교육용 코드를 생성해주세요."},
        ]

        try:
            # Note: Claude doesn't support response_format, so we omit it
            # The prompt already instructs to output pure JSON
            response = await openrouter_service.chat_completion(
                model=settings.llm_model_code_gen,
                messages=messages,
                temperature=0.7,
                max_tokens=8192,
                # response_format={"type": "json_object"},  # Not supported by Claude
            )

            content = openrouter_service.get_content(response)

            # Debug: print first 500 chars of response
            print(f"[CodeGen] LLM Response preview: {content[:500]}...")

            return openrouter_service.parse_json_response(content)

        except Exception as e:
            print(f"[CodeGen] Error type: {type(e).__name__}")
            print(f"[CodeGen] Error message: {e}")
            import traceback
            traceback.print_exc()
            raise

    async def embed_and_store_problem(self, problem: Dict[str, Any]) -> bool:
        """
        Generate embedding for a problem and store it in the database.

        Args:
            problem: Problem data dictionary

        Returns:
            True if successful
        """
        try:
            # Create text for embedding
            text = embedding_service.create_problem_text_for_embedding(problem)

            # Generate embedding
            embedding = await embedding_service.generate_embedding(text)

            # Update problem with embedding
            problem_id = problem.get("id")
            if not problem_id:
                return False

            self.db.table("problem_embeddings").upsert({
                "problem_id": problem_id,
                "embedding": embedding,
                "text_content": text[:5000],  # Store truncated text
            }).execute()

            return True

        except Exception as e:
            print(f"Embed and store error for {problem.get('id')}: {e}")
            return False

    async def batch_embed_problems(
        self, problems: List[Dict[str, Any]], batch_size: int = 50
    ) -> Dict[str, int]:
        """
        Batch embed and store multiple problems.

        Args:
            problems: List of problem dictionaries
            batch_size: Number of problems per batch

        Returns:
            Dict with success and failure counts
        """
        success_count = 0
        fail_count = 0

        for i in range(0, len(problems), batch_size):
            batch = problems[i : i + batch_size]

            # Create texts for batch
            texts = [
                embedding_service.create_problem_text_for_embedding(p)
                for p in batch
            ]

            try:
                # Generate embeddings in batch
                embeddings = await embedding_service.generate_embeddings_batch(texts)

                # Store each embedding
                for j, problem in enumerate(batch):
                    try:
                        problem_id = problem.get("id")
                        if not problem_id:
                            fail_count += 1
                            continue

                        self.db.table("problem_embeddings").upsert({
                            "problem_id": problem_id,
                            "embedding": embeddings[j],
                            "text_content": texts[j][:5000],
                        }).execute()

                        success_count += 1

                    except Exception as e:
                        print(f"Store error for {problem.get('id')}: {e}")
                        fail_count += 1

            except Exception as e:
                print(f"Batch embedding error: {e}")
                fail_count += len(batch)

        return {"success": success_count, "failed": fail_count}

    async def search_concepts(
        self,
        query: str,
        topics: List[str] = None,
        limit: int = 3,
        user_id: str = None,
    ) -> List[Dict[str, Any]]:
        """
        개념/문서 검색 (Agentic RAG Guided Tutor용)

        학생 질문에 관련된 개념 설명을 검색합니다.
        base_problems 테이블의 description을 활용합니다.

        Args:
            query: 검색 쿼리 (학생 질문)
            topics: 관련 주제
            limit: 최대 결과 수
            user_id: 사용자 ID (개인화용)

        Returns:
            관련 문서 목록 [{content, metadata, similarity}]
        """
        # 개인화 컨텍스트 조회 (옵션)
        user_context = None
        if user_id:
            try:
                from .personalization import get_personalization_service
                ps = get_personalization_service()
                user_context = await ps.get_rag_context(user_id)
            except Exception as e:
                print(f"[RAG:SearchConcepts] Personalization error: {e}")

        # 개인화 컨텍스트 기반 토픽 확장
        if user_context:
            # 약점 토픽을 우선적으로 검색
            if user_context.get("weak_topics"):
                topics = list(set((topics or []) + user_context["weak_topics"]))
            # 최근 학습 토픽도 추가
            if user_context.get("recent_topics"):
                topics = list(set((topics or []) + user_context["recent_topics"][:2]))
        try:
            # Step 1: Query embedding 생성
            query_embedding = await embedding_service.generate_embedding(query)

            # Step 2: topics가 있으면 필터링
            if topics:
                expanded_topics = self._expand_topics(topics)
                # 필터링된 문제에서 검색
                db_query = self.db.table("base_problems").select(
                    "id, name, title, description, tags, difficulty"
                ).overlaps("tags", expanded_topics).limit(50)
            else:
                db_query = self.db.table("base_problems").select(
                    "id, name, title, description, tags, difficulty"
                ).limit(50)

            response = db_query.execute()
            problems = response.data or []

            if not problems:
                return []

            # Step 3: Embedding 유사도 계산
            problem_ids = [p["id"] for p in problems]
            embeddings_response = self.db.table("problem_embeddings").select(
                "problem_id, embedding"
            ).in_("problem_id", problem_ids).execute()

            embeddings_map = {}
            for e in (embeddings_response.data or []):
                try:
                    emb = e.get("embedding")
                    if isinstance(emb, str):
                        emb = json.loads(emb.replace("[", "[").replace("]", "]"))
                    embeddings_map[e["problem_id"]] = emb
                except Exception:
                    continue

            # Step 4: 유사도 계산 및 정렬
            results = []
            for p in problems:
                emb = embeddings_map.get(p["id"])
                if emb:
                    similarity = self._cosine_similarity(query_embedding, emb)
                else:
                    similarity = 0.3  # 기본값

                results.append({
                    "content": f"[{p.get('title', p.get('name', ''))}] {p.get('description', '')[:300]}",
                    "metadata": {
                        "id": p.get("id"),
                        "title": p.get("title") or p.get("name"),
                        "tags": p.get("tags", []),
                        "difficulty": p.get("difficulty"),
                    },
                    "similarity": similarity,
                })

            # 유사도 순 정렬
            results.sort(key=lambda x: x["similarity"], reverse=True)

            return results[:limit]

        except Exception as e:
            print(f"[RAG:SearchConcepts] Error: {e}")
            return []


    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """코사인 유사도 계산"""
        import numpy as np
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        return float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))

    def _mmr_rerank(
        self,
        results: List[Dict[str, Any]],
        embeddings_map: Dict[str, List[float]],
        query_embedding: List[float],
        limit: int = 5,
        lambda_param: float = 0.7,
    ) -> List[Dict[str, Any]]:
        """
        MMR (Maximal Marginal Relevance) 재정렬

        다양성과 관련성의 균형을 맞추어 결과를 재정렬합니다.

        Args:
            results: 원본 검색 결과 (similarity 포함)
            embeddings_map: 문제 ID -> 임베딩 매핑
            query_embedding: 쿼리 임베딩
            limit: 반환할 결과 수
            lambda_param: 관련성 vs 다양성 가중치 (0.7 = 70% 관련성, 30% 다양성)

        Returns:
            MMR로 재정렬된 결과
        """
        import numpy as np

        if len(results) <= limit:
            return results

        # 결과 중 임베딩이 있는 것만 필터링
        results_with_emb = [
            r for r in results
            if r.get("id") in embeddings_map
        ]

        if len(results_with_emb) <= limit:
            return results_with_emb

        query_vec = np.array(query_embedding)
        selected: List[Dict[str, Any]] = []
        candidates = results_with_emb.copy()

        while len(selected) < limit and candidates:
            best_idx = -1
            best_mmr = float("-inf")

            for i, candidate in enumerate(candidates):
                cand_id = candidate.get("id")
                cand_vec = np.array(embeddings_map.get(cand_id, []))

                if len(cand_vec) == 0:
                    continue

                # 쿼리와의 유사도 (관련성)
                relevance = candidate.get("similarity", 0.5)

                # 이미 선택된 문서들과의 최대 유사도 (다양성 페널티)
                max_sim_to_selected = 0.0
                if selected:
                    for s in selected:
                        s_id = s.get("id")
                        s_vec = embeddings_map.get(s_id)
                        if s_vec is not None:
                            sim = self._cosine_similarity(cand_vec.tolist(), s_vec)
                            max_sim_to_selected = max(max_sim_to_selected, sim)

                # MMR 점수 = λ × 관련성 - (1-λ) × 기존 선택과의 유사도
                mmr_score = lambda_param * relevance - (1 - lambda_param) * max_sim_to_selected

                if mmr_score > best_mmr:
                    best_mmr = mmr_score
                    best_idx = i

            if best_idx >= 0:
                selected.append(candidates.pop(best_idx))
            else:
                break

        return selected

    async def search_problems_personalized(
        self,
        query: str,
        user_id: str,
        topics: List[str] = None,
        difficulty: str = None,
        language: str = None,
        limit: int = 5,
    ) -> Tuple[List[Dict[str, Any]], bool]:
        """
        개인화된 문제 검색

        사용자 학습 프로필을 기반으로 검색 결과를 개인화합니다.

        Args:
            query: 검색 쿼리
            user_id: 사용자 ID
            topics: 주제 필터
            difficulty: 난이도 필터
            language: 언어 필터
            limit: 결과 개수

        Returns:
            Tuple of (results, should_fallback)
        """
        # 1. 개인화 컨텍스트 조회
        user_context = None
        solved_problem_ids = []
        try:
            from .personalization import get_personalization_service
            ps = get_personalization_service()
            user_context = await ps.get_rag_context(user_id)

            # 이미 푼 문제 ID 목록 조회
            solved_ids_set = await ps._get_solved_problem_ids(user_id)
            solved_problem_ids = list(solved_ids_set)
        except Exception as e:
            print(f"[RAG:PersonalizedSearch] Personalization error: {e}")

        # 2. 난이도 조정 (지정되지 않았으면 선호 난이도 사용)
        if not difficulty and user_context:
            difficulty = user_context.get("preferred_difficulty")

        # 3. 토픽 확장 (약점 토픽 우선)
        if user_context:
            weak_topics = user_context.get("weak_topics", [])
            if weak_topics and not topics:
                # 약점 토픽 중 하나를 랜덤 선택
                import random
                topics = [random.choice(weak_topics)]

        # 4. 기본 하이브리드 검색 실행 (이미 푼 문제 제외)
        results, should_fallback = await self.search_problems_hybrid(
            query=query,
            topics=topics,
            difficulty=difficulty,
            language=language,
            limit=limit * 2,  # 더 많이 가져와서 필터링
            exclude_ids=solved_problem_ids,  # 🔥 핵심: 이미 푼 문제 제외
            user_context=user_context,
        )

        if not results:
            return results, should_fallback

        # 5. 개인화 스코어링
        if user_context:
            for result in results:
                personalization_boost = 0.0
                result_tags = result.get("tags", [])
                result_difficulty = result.get("difficulty", "")

                # 약점 토픽 매칭 시 부스트
                weak_topics = user_context.get("weak_topics", [])
                if weak_topics and any(t in result_tags for t in weak_topics):
                    personalization_boost += 0.15

                # 선호 난이도 또는 한 단계 높은 난이도 매칭 시 부스트
                pref_diff = user_context.get("preferred_difficulty", "")
                if result_difficulty == pref_diff:
                    personalization_boost += 0.1
                elif self._is_next_difficulty(pref_diff, result_difficulty):
                    personalization_boost += 0.05

                # 최근 학습 토픽과 관련 시 부스트
                recent_topics = user_context.get("recent_topics", [])
                if recent_topics and any(t in result_tags for t in recent_topics):
                    personalization_boost += 0.05

                # 원본 유사도에 개인화 부스트 추가
                original_sim = result.get("similarity", 0.5)
                result["similarity"] = min(1.0, original_sim + personalization_boost)
                result["personalization_boost"] = personalization_boost

            # 재정렬
            results.sort(key=lambda x: x.get("similarity", 0), reverse=True)

        return results[:limit], should_fallback

    def _is_next_difficulty(self, current: str, target: str) -> bool:
        """target이 current의 다음 난이도인지 확인"""
        order = ["easy", "medium", "medium_hard", "hard", "very_hard"]
        try:
            curr_idx = order.index(current)
            tgt_idx = order.index(target)
            return tgt_idx == curr_idx + 1
        except ValueError:
            return False

    async def _evaluate_search_quality(
        self,
        request_params: Dict[str, Any],
        results: List[Dict[str, Any]],
        user_context: Optional[Dict[str, Any]] = None,
    ):
        """
        🚀 검색 품질 평가 및 로깅

        검색 결과의 품질을 측정하여 로깅합니다.
        A/B 테스트와 연동하여 알고리즘 개선 효과를 측정합니다.
        """
        try:
            from .search_quality import get_search_quality_evaluator

            evaluator = get_search_quality_evaluator()
            user_id = user_context.get("user_id") if user_context else None

            score = await evaluator.evaluate_and_log(
                request_params=request_params,
                search_results=results,
                user_id=user_id,
                experiment_name="search_quality_v1",
            )

            # 로깅 (디버그용)
            print(f"[RAG:Quality] Score: {score.overall:.3f} ({score.grade}) "
                  f"[meta:{score.metadata_match:.2f}, hist:{score.historical_success:.2f}, div:{score.diversity:.2f}]")

            # 품질이 낮으면 경고
            if score.overall < 0.5:
                suggestions = evaluator.get_improvement_suggestions(score)
                print(f"[RAG:Quality] ⚠️ Low quality - Suggestions: {suggestions}")

        except Exception as e:
            # 품질 평가 실패는 검색 결과에 영향을 주지 않음
            print(f"[RAG:Quality] Evaluation failed (non-blocking): {e}")

    # ============================================================
    # Code Generation RAG: programmers_embeddings 통합
    # ============================================================

    # 코테/대기업 관련 키워드
    CODING_TEST_KEYWORDS = [
        # 일반 코테 키워드
        "코테", "코딩테스트", "코딩 테스트", "coding test",
        "기출", "기출문제", "기출 문제",
        # 대기업 키워드
        "대기업", "빅테크", "big tech",
        "카카오", "kakao", "네이버", "naver", "라인", "line",
        "삼성", "samsung", "lg", "엘지", "sk", "에스케이",
        "쿠팡", "coupang", "배민", "배달의민족", "woowa", "우아한형제들",
        "토스", "toss", "당근", "당근마켓", "karrot",
        # 채용 키워드
        "채용", "인턴", "인턴십", "공채", "신입",
    ]

    def _detect_coding_test_intent(self, query: str) -> bool:
        """
        쿼리에서 코테/대기업 키워드 감지

        Args:
            query: 사용자 쿼리

        Returns:
            True: 코테/대기업 관련 요청
            False: 일반 요청
        """
        query_lower = query.lower()
        for keyword in self.CODING_TEST_KEYWORDS:
            if keyword.lower() in query_lower:
                print(f"[RAG:CodeGen] Detected coding test keyword: '{keyword}'")
                return True
        return False

    def _extract_company_filter(self, query: str) -> Optional[str]:
        """
        쿼리에서 특정 회사 필터 추출

        Args:
            query: 사용자 쿼리

        Returns:
            회사 키워드 (있으면) 또는 None
        """
        company_keywords = {
            "카카오": "카카오",
            "kakao": "카카오",
            "네이버": "네이버",
            "naver": "네이버",
            "라인": "라인",
            "line": "라인",
            "삼성": "삼성",
            "samsung": "삼성",
        }
        query_lower = query.lower()
        for keyword, company in company_keywords.items():
            if keyword in query_lower:
                return company
        return None

    async def search_programmers_for_codegen(
        self,
        query: str,
        topics: List[str] = None,
        difficulty: str = None,
        limit: int = 5,
        company_filter: str = None,
    ) -> List[Dict[str, Any]]:
        """
        [내부 전용] programmers 문제를 RAG 컨텍스트로 검색

        ⚠️ 저작권 주의:
        - 이 함수의 결과를 사용자에게 직접 제공하면 안 됨
        - generate_problem_with_rag()에 전달하여 새 문제 생성용으로만 사용
        - 대기업 기출 스타일의 새 문제를 생성할 때 참고 자료로 활용

        Args:
            query: 검색 쿼리
            topics: 주제 필터
            difficulty: 난이도 필터
            limit: 최대 결과 수
            company_filter: 회사 필터 (카카오, 네이버 등)

        Returns:
            RAG 컨텍스트용 programmers 문제 목록 (내부 사용 전용)
        """
        try:
            print(f"[RAG:Programmers] Searching programmers problems: query={query}, company={company_filter}")

            # Step 1: Query embedding 생성
            query_embedding = await embedding_service.generate_embedding(query)

            # Step 2: programmers 문제 필터링
            db_query = self.db.table("base_problems").select("*").eq("source", "programmers")

            # 회사 필터 (name에 회사명 포함)
            if company_filter:
                db_query = db_query.ilike("name", f"%{company_filter}%")

            # 난이도 필터
            if difficulty:
                db_query = db_query.eq("difficulty", difficulty)

            # 토픽 필터
            if topics:
                expanded_topics = self._expand_topics(topics)
                db_query = db_query.overlaps("tags", expanded_topics)

            db_query = db_query.limit(100)
            response = db_query.execute()
            problems = response.data or []

            if not problems:
                print(f"[RAG:Programmers] No problems found with filters")
                # 필터 없이 재시도
                problems = self.db.table("base_problems").select("*").eq("source", "programmers").limit(50).execute().data or []

            if not problems:
                return []

            # Step 3: programmers_embeddings에서 임베딩 조회
            problem_ids = [p["id"] for p in problems]
            embeddings_response = self.db.table("programmers_embeddings").select(
                "base_problem_id, embedding"
            ).in_("base_problem_id", problem_ids).execute()

            embeddings_map = {}
            for e in (embeddings_response.data or []):
                emb = e.get("embedding")
                if isinstance(emb, str):
                    emb = json.loads(emb)
                embeddings_map[e["base_problem_id"]] = emb

            # Step 4: 유사도 계산 및 정렬
            import numpy as np
            query_vec = np.array(query_embedding)

            results = []
            for problem in problems:
                pid = problem["id"]
                emb = embeddings_map.get(pid)
                if emb:
                    prob_vec = np.array(emb)
                    similarity = float(np.dot(query_vec, prob_vec) / (np.linalg.norm(query_vec) * np.linalg.norm(prob_vec)))
                    problem["similarity"] = similarity
                    results.append(problem)

            results.sort(key=lambda x: x.get("similarity", 0), reverse=True)
            print(f"[RAG:Programmers] Found {len(results)} problems, returning top {limit}")

            return results[:limit]

        except Exception as e:
            print(f"[RAG:Programmers] Error: {e}")
            import traceback
            traceback.print_exc()
            return []

    async def search_problems_for_codegen(
        self,
        query: str,
        topics: List[str] = None,
        difficulty: str = None,
        language: str = None,
        limit: int = 5,
    ) -> Tuple[List[Dict[str, Any]], bool, str]:
        """
        [내부 전용] Code Generation용 RAG 컨텍스트 검색

        ⚠️ 저작권 주의:
        - 이 함수의 결과를 사용자에게 직접 제공하면 안 됨
        - generate_problem_with_rag()에 전달하여 새 문제 생성용으로만 사용

        동작:
        - 코테/대기업 키워드 감지 시: programmers 기출을 참고하여 유사 문제 생성
        - 일반 요청 시: 모든 문제를 참고하여 새 문제 생성

        Args:
            query: 검색 쿼리
            topics: 주제 필터
            difficulty: 난이도 필터
            language: 언어 필터
            limit: 최대 결과 수

        Returns:
            Tuple of (rag_context, is_coding_test, search_source)
        """
        # 코테/대기업 키워드 감지
        is_coding_test = self._detect_coding_test_intent(query)
        company_filter = self._extract_company_filter(query)

        if is_coding_test:
            # programmers 문제만 검색
            print(f"[RAG:CodeGen] Using PROGRAMMERS-ONLY search (coding test intent)")
            results = await self.search_programmers_for_codegen(
                query=query,
                topics=topics,
                difficulty=difficulty,
                limit=limit,
                company_filter=company_filter,
            )
            return results, True, "programmers"

        else:
            # 통합 검색: 두 테이블 모두 사용
            print(f"[RAG:CodeGen] Using COMBINED search (both embeddings)")

            # 1. 일반 문제 검색 (problem_embeddings)
            general_results, _ = await self.search_problems_hybrid(
                query=query,
                topics=topics,
                difficulty=difficulty,
                language=language,
                limit=limit,
            )

            # 2. programmers 문제 검색 (추가 컨텍스트)
            programmers_results = await self.search_programmers_for_codegen(
                query=query,
                topics=topics,
                difficulty=difficulty,
                limit=2,  # 보조 컨텍스트로 2개만
            )

            # 3. 결과 병합 (중복 제거)
            seen_ids = set()
            combined = []

            for r in general_results:
                if r["id"] not in seen_ids:
                    seen_ids.add(r["id"])
                    combined.append(r)

            for r in programmers_results:
                if r["id"] not in seen_ids and len(combined) < limit:
                    seen_ids.add(r["id"])
                    r["source_note"] = "programmers_reference"
                    combined.append(r)

            # 유사도 순 정렬
            combined.sort(key=lambda x: x.get("similarity", 0), reverse=True)

            print(f"[RAG:CodeGen] Combined results: {len(combined)} (general: {len(general_results)}, programmers: {len(programmers_results)})")

            return combined[:limit], False, "combined"

    # ============================================================
    # 문제 이름 검색 (inquire_problem 인텐트용)
    # ============================================================

    async def search_problems_by_name(
        self,
        problem_name: str,
        similarity_threshold: float = 0.40,
        limit: int = 5,
    ) -> Tuple[List[Dict[str, Any]], bool]:
        """
        문제 이름으로 임베딩 유사도 검색

        Args:
            problem_name: 검색할 문제 이름
            similarity_threshold: 유사도 임계값 (기본 0.40, 프론트에서 0.92 threshold 적용)
            limit: 최대 결과 수

        Returns:
            Tuple of (results, found_exact_match)
            - results: 검색 결과 (유사도 순 정렬)
            - found_exact_match: 정확한 매칭 여부 (similarity >= 0.92)
        """
        try:
            print(f"[RAG:ByName] Searching for: '{problem_name}'")

            # Step 1: 쿼리 임베딩 생성
            query_embedding = await embedding_service.generate_embedding(problem_name)

            # Step 2: 모든 문제의 임베딩과 비교 (pgvector 사용)
            # base_problems + problem_embeddings 조인하여 유사도 계산
            # 참고: problem_embeddings의 embedding은 문제 전체 내용이지만,
            # 문제 이름으로 검색 시에도 유사도가 높게 나올 수 있음

            # 먼저 ILIKE로 이름 직접 매칭 시도
            direct_match = self.db.table("base_problems").select(
                "id, original_id, name, difficulty, tags, source, question"
            ).ilike("name", f"%{problem_name}%").neq("source", "programmers").limit(limit).execute()

            direct_results = []
            if direct_match.data:
                for p in direct_match.data:
                    direct_results.append({
                        "id": p["id"],
                        "original_id": p.get("original_id"),
                        "name": p["name"],
                        "title": p["name"],
                        "difficulty": p.get("difficulty", "medium"),
                        "tags": p.get("tags", []),
                        "topics": p.get("tags", []),
                        "source": p.get("source"),
                        "description": (p.get("question") or "")[:200],
                        "similarity": 1.0,  # 직접 매칭은 유사도 1.0
                        "match_type": "direct",
                    })
                print(f"[RAG:ByName] Direct match found: {len(direct_results)} results")

            # Step 3: 임베딩 유사도 검색 (직접 매칭 결과가 부족한 경우)
            embedding_results = []
            if len(direct_results) < limit:
                # 문제 ID 목록 가져오기 (programmers 제외)
                problems_response = self.db.table("base_problems").select(
                    "id, original_id, name, difficulty, tags, source, question"
                ).neq("source", "programmers").limit(200).execute()

                problems = problems_response.data or []
                problem_ids = [p["id"] for p in problems]
                problem_map = {p["id"]: p for p in problems}

                # 임베딩 가져오기
                embeddings_response = self.db.table("problem_embeddings").select(
                    "problem_id, embedding"
                ).in_("problem_id", problem_ids).execute()

                embeddings = embeddings_response.data or []

                # 유사도 계산
                import numpy as np
                query_vec = np.array(query_embedding)
                similarities = []

                for emb_data in embeddings:
                    prob_id = emb_data["problem_id"]
                    if prob_id not in problem_map:
                        continue

                    emb_vec = np.array(emb_data["embedding"])

                    # 코사인 유사도 계산
                    dot_product = np.dot(query_vec, emb_vec)
                    norm_product = np.linalg.norm(query_vec) * np.linalg.norm(emb_vec)
                    similarity = dot_product / norm_product if norm_product > 0 else 0

                    if similarity >= similarity_threshold:
                        p = problem_map[prob_id]
                        similarities.append({
                            "id": p["id"],
                            "original_id": p.get("original_id"),
                            "name": p["name"],
                            "title": p["name"],
                            "difficulty": p.get("difficulty", "medium"),
                            "tags": p.get("tags", []),
                            "topics": p.get("tags", []),
                            "source": p.get("source"),
                            "description": (p.get("question") or "")[:200],
                            "similarity": float(similarity),
                            "match_type": "embedding",
                        })

                # 유사도 순 정렬
                similarities.sort(key=lambda x: x["similarity"], reverse=True)
                embedding_results = similarities[:limit]
                print(f"[RAG:ByName] Embedding search found: {len(embedding_results)} results above threshold {similarity_threshold}")

            # Step 4: 결과 합치기 (직접 매칭 우선, 중복 제거)
            seen_ids = set()
            combined = []

            for r in direct_results:
                if r["id"] not in seen_ids:
                    seen_ids.add(r["id"])
                    combined.append(r)

            for r in embedding_results:
                if r["id"] not in seen_ids and len(combined) < limit:
                    seen_ids.add(r["id"])
                    combined.append(r)

            # 유사도 순 정렬
            combined.sort(key=lambda x: x["similarity"], reverse=True)

            # 정확한 매칭 여부 (유사도 0.92 이상)
            found_exact_match = any(r["similarity"] >= 0.92 for r in combined)

            print(f"[RAG:ByName] Final results: {len(combined)}, exact_match: {found_exact_match}")
            return combined[:limit], found_exact_match

        except Exception as e:
            print(f"[RAG:ByName] Error: {e}")
            import traceback
            traceback.print_exc()
            return [], False


# Singleton instance
rag_service = RAGService()
