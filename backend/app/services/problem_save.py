"""
Problem Save Service
생성된 문제(blank, puzzle, guided)를 DB에 저장하는 서비스

Tables:
- problems_blank: 빈칸 채우기 문제
- problems_puzzle: 퍼즐 문제 (Parsons)
- problems_guided: 1대1 대화형 문제

Key Columns:
- base_problem_id: base_problems 테이블의 UUID (FK)
- creator_id: 문제를 푼 사용자의 UUID
- language: 프로그래밍 언어

Logic:
- 조회: base_problem_id + language로 기존 문제 확인
- 캐시 히트: 기존 문제 복사 + creator_id만 변경
- 캐시 미스: LLM 생성 후 저장
"""

from typing import Dict, Any, Optional
import logging
from ..database import get_supabase_client

logger = logging.getLogger(__name__)

# 유효한 난이도 목록
VALID_DIFFICULTIES = {"easy", "medium", "medium_hard", "hard", "very_hard"}

# 허용된 tags 목록 (정규화된 한국어)
ALLOWED_TAGS = {
    "구현", "정렬", "문자열", "이분탐색", "그리디", "DP",
    "BFS/DFS", "그래프", "백트래킹", "완전탐색", "자료구조",
    "수학", "트리", "최단경로", "투포인터", "해시",
}

# 영어/DB 토픽명 → 허용된 한국어 태그 매핑
TAG_NORMALIZATION_MAP = {
    # 구현
    "Array": "구현", "Implementation": "구현", "implementation": "구현",
    "ad_hoc": "구현", "case_work": "구현", "simulation": "구현",
    "시뮬레이션": "구현", "배열": "구현", "반복문": "구현", "기초": "구현",
    "케이스분류": "구현", "파싱": "구현", "구성적": "구현", "애드혹": "구현",
    "전처리": "구현", "좌표압축": "구현",
    # 정렬
    "Sorting": "정렬", "sorting": "정렬", "merge_sort": "정렬", "quick_sort": "정렬",
    "각도정렬": "정렬",
    # 문자열
    "String": "문자열", "string": "문자열", "문자열 처리": "문자열",
    "kmp": "문자열", "KMP": "문자열", "trie": "문자열", "트라이": "문자열",
    "라빈카프": "문자열", "아호코라식": "문자열", "접미사배열": "문자열",
    "팰린드롬": "문자열", "Z알고리즘": "문자열",
    # 이분탐색
    "Binary Search": "이분탐색", "binary_search": "이분탐색",
    "Parametric Search": "이분탐색", "parametric_search": "이분탐색",
    "이진 탐색": "이분탐색", "매개 변수 탐색": "이분탐색", "삼분탐색": "이분탐색",
    # 그리디
    "Greedy": "그리디", "greedy": "그리디", "greedy_algorithms": "그리디",
    # DP
    "DP": "DP", "dp": "DP", "dynamic_programming": "DP",
    "Dynamic Programming": "DP", "점화식": "DP", "memoization": "DP",
    "동적계획법": "DP", "LIS": "DP", "LCS": "DP", "비트마스킹": "DP",
    "분할정복": "DP", "CHT": "DP",
    # BFS/DFS
    "BFS": "BFS/DFS", "DFS": "BFS/DFS", "bfs": "BFS/DFS", "dfs": "BFS/DFS",
    "BFS/DFS": "BFS/DFS", "graph_traversal": "BFS/DFS",
    "그래프 탐색": "BFS/DFS", "flood_fill": "BFS/DFS",
    # 그래프
    "Graph": "그래프", "graphs": "그래프", "topological_sort": "그래프",
    "topological_sorting": "그래프", "위상정렬": "그래프",
    "SCC": "그래프", "MST": "그래프", "유니온파인드": "그래프",
    "이분그래프": "그래프", "이분매칭": "그래프", "네트워크플로우": "그래프",
    "오일러경로": "그래프", "단절점": "그래프",
    # 백트래킹
    "Backtracking": "백트래킹", "backtracking": "백트래킹",
    # 완전탐색
    "Brute Force": "완전탐색", "bruteforcing": "완전탐색",
    "brute_force": "완전탐색", "complete_search": "완전탐색",
    # 자료구조
    "Data Structures": "자료구조", "data_structures": "자료구조",
    "기본 자료구조": "자료구조", "Stack": "자료구조", "Queue": "자료구조",
    "stack": "자료구조", "queue": "자료구조", "스택": "자료구조", "큐": "자료구조",
    "덱": "자료구조", "deque": "자료구조", "priority_queue": "자료구조",
    "우선순위큐": "자료구조", "heap": "자료구조", "세그먼트트리": "자료구조",
    "연결리스트": "자료구조", "집합": "자료구조", "딕셔너리": "자료구조",
    # 수학
    "Math": "수학", "math": "수학", "Mathematics": "수학",
    "number_theory": "수학", "정수론": "수학", "조합론": "수학",
    "primality_test": "수학", "소수판별": "수학", "소수": "수학", "소인수분해": "수학",
    "arithmetic": "수학", "게임이론": "수학", "기하": "수학", "기하학": "수학",
    "FFT": "수학", "다항식": "수학", "행렬": "수학", "선형대수": "수학",
    "확률": "수학", "기댓값": "수학",
    # 트리
    "Tree": "트리", "trees": "트리", "tree_diameter": "트리",
    "LCA": "트리", "HLD": "트리", "센트로이드": "트리",
    # 최단경로
    "Shortest Path": "최단경로", "shortest_path": "최단경로",
    "Dijkstra": "최단경로", "dijkstra": "최단경로", "다익스트라": "최단경로",
    "bellman_ford": "최단경로", "벨만포드": "최단경로",
    "floyd_warshall": "최단경로", "플로이드": "최단경로",
    # 투포인터
    "Two Pointers": "투포인터", "two_pointer": "투포인터",
    "two_pointers": "투포인터", "Sliding Window": "투포인터",
    "sliding_window": "투포인터", "슬라이딩윈도우": "투포인터",
    "누적합": "투포인터", "누적 합": "투포인터",
    # 해시
    "Hash": "해시", "hashing": "해시", "hash_set": "해시", "해시테이블": "해시",
}


def normalize_tags(tags: list) -> list:
    """
    생성된 문제의 tags를 허용된 태그로 정규화

    Args:
        tags: 원본 태그 목록 (영어/한국어 혼합 가능)

    Returns:
        정규화된 태그 목록 (ALLOWED_TAGS에 있는 것만)
    """
    if not tags:
        return []

    normalized = set()
    for tag in tags:
        if not tag:
            continue
        # 이미 허용된 태그면 그대로 추가
        if tag in ALLOWED_TAGS:
            normalized.add(tag)
            continue
        # 매핑 테이블에서 찾기
        mapped = TAG_NORMALIZATION_MAP.get(tag)
        if mapped:
            normalized.add(mapped)
        else:
            # 매핑되지 않은 태그는 로그만 남기고 무시
            logger.debug(f"[TagNormalize] Unknown tag ignored: {tag}")

    result = list(normalized)
    logger.info(f"[TagNormalize] {tags} → {result}")
    return result


def _validate_blank_problem(data: Dict[str, Any]) -> bool:
    """
    빈칸 문제 캐시 데이터가 유효한지 검증

    조건:
    1. code_template에 _N_ 패턴이 있어야 함
    2. answers 배열이 있어야 함
    3. 패턴 수와 answers 수가 일치해야 함

    Returns:
        True if valid, False if invalid (should regenerate)
    """
    import re

    code_template = data.get("code_template", "")
    answers = data.get("answers", [])

    if not code_template or not answers:
        logger.warning("[CacheValidation] Empty code_template or answers")
        return False

    # _N_ 패턴 찾기 (예: _0_, _1_, _2_)
    blank_patterns = re.findall(r'_(\d+)_', code_template)

    if len(blank_patterns) == 0 and len(answers) > 0:
        logger.warning(f"[CacheValidation] ❌ Invalid cache: {len(answers)} answers but 0 patterns in code_template")
        logger.warning(f"[CacheValidation] code_template preview: {code_template[:200]}...")
        return False

    if len(blank_patterns) != len(answers):
        logger.warning(f"[CacheValidation] ⚠️ Pattern/answer mismatch: {len(blank_patterns)} patterns vs {len(answers)} answers")
        # 패턴이 있지만 수가 다른 경우는 경고만 (부분 유효)
        # 하지만 패턴이 0개면 완전히 무효
        if len(blank_patterns) == 0:
            return False

    logger.info(f"[CacheValidation] ✓ Valid cache: {len(blank_patterns)} patterns, {len(answers)} answers")
    return True


class ProblemSaveService:
    """생성된 문제를 DB에 저장하고 조회하는 서비스"""

    def __init__(self):
        self.supabase = get_supabase_client()

    # ============================================================
    # base_problem_id 조회 헬퍼
    # ============================================================

    def get_base_problem_id(self, original_id: str) -> Optional[str]:
        """
        original_id로 base_problems 테이블에서 UUID(id) 조회

        Args:
            original_id: 원본 문제 ID (예: "baekjoon_1001", "taco_123")

        Returns:
            base_problems.id (UUID) 또는 None
        """
        try:
            result = self.supabase.table("base_problems") \
                .select("id") \
                .eq("original_id", original_id) \
                .limit(1) \
                .execute()

            if result.data and len(result.data) > 0:
                return result.data[0]["id"]
            return None

        except Exception as e:
            logger.error(f"[ProblemSave] Failed to get base_problem_id: {e}")
            return None

    # ============================================================
    # CodeGen 문제를 base_problems에 저장
    # ============================================================

    async def save_codegen_to_base_problems(
        self,
        generated_problem: Dict[str, Any],
        collected_info: Dict[str, Any],
        user_id: Optional[str] = None,
        skip_validation: bool = False,
    ) -> Optional[str]:
        """
        CodeGen으로 생성된 문제를 base_problems 테이블에 저장
        ⚠️ 저장 전 테스트 케이스 검증 필수 - 통과한 경우만 저장
        ⚠️ 중복 이름 체크 - 같은 이름의 문제가 있으면 저장 안 함

        Args:
            generated_problem: CodeGen이 생성한 문제 데이터
            collected_info: 사용자가 선택한 topic, difficulty, language
            user_id: 생성 요청한 사용자 ID (optional, 추후 creator 추적용)
            skip_validation: True면 검증 스킵 (이미 검증된 경우)

        Returns:
            저장된 문제의 id (UUID) 또는 None
        """
        import uuid

        try:
            # difficulty 검증 (필수)
            difficulty = generated_problem.get("difficulty") or collected_info.get("difficulty")
            if not difficulty or difficulty not in VALID_DIFFICULTIES:
                logger.error(f"[ProblemSave] Invalid difficulty: {difficulty}")
                return None

            # ============================================================
            # 🆕 중복/유사 이름 체크 - 같거나 비슷한 이름의 문제가 있으면 저장 안 함
            # ============================================================
            problem_name = generated_problem.get("title", "Generated Problem")
            if problem_name:
                # 1. 정확히 같은 이름 체크
                existing_exact = self.supabase.table("base_problems") \
                    .select("id, name") \
                    .eq("name", problem_name) \
                    .limit(1) \
                    .execute()

                if existing_exact.data and len(existing_exact.data) > 0:
                    logger.warning(
                        f"[ProblemSave] ❌ Exact duplicate name - not saving: '{problem_name}'"
                    )
                    return None

                # 2. 비슷한 이름 체크 (앞 10글자가 같으면 유사로 판단)
                name_prefix = problem_name[:10] if len(problem_name) >= 10 else problem_name
                existing_similar = self.supabase.table("base_problems") \
                    .select("id, name") \
                    .ilike("name", f"{name_prefix}%") \
                    .limit(1) \
                    .execute()

                if existing_similar.data and len(existing_similar.data) > 0:
                    existing_name = existing_similar.data[0].get("name", "")
                    logger.warning(
                        f"[ProblemSave] ❌ Similar name detected - not saving: '{problem_name}' (similar to '{existing_name}')"
                    )
                    return None

            # original_id 생성 (codegen_UUID 형식)
            original_id = f"codegen_{uuid.uuid4().hex[:12]}"

            # solutions 추출 (여러 형식 지원)
            solutions = []

            # 형식 1: solutions 필드가 직접 있는 경우 (새 프롬프트)
            sol_data = generated_problem.get("solutions")
            if sol_data:
                if isinstance(sol_data, dict) and sol_data.get("code"):
                    # {"code": "...", "language": "python"}
                    solutions.append({
                        "language": sol_data.get("language", "python"),
                        "code": sol_data["code"]
                    })
                elif isinstance(sol_data, list):
                    # [{"code": "...", "language": "python"}]
                    solutions = sol_data

            # 형식 2: code 필드에서 변환 (기존 형식)
            if not solutions:
                code_data = generated_problem.get("code", {})
                if isinstance(code_data, dict):
                    for lang, code in code_data.items():
                        if code:
                            solutions.append({"language": lang, "code": code})
                elif isinstance(code_data, str):
                    solutions.append({
                        "language": collected_info.get("language", "python"),
                        "code": code_data
                    })

            # 솔루션이 없으면 저장 불가
            if not solutions:
                logger.warning(f"[ProblemSave] No solutions in generated problem")
                return None

            # input_output 구성 (새 형식 우선, 레거시 examples fallback)
            input_output = generated_problem.get("input_output")

            # 새 형식 검증: {"inputs": [...], "outputs": [...]}
            if input_output and isinstance(input_output, dict):
                if not (input_output.get("inputs") and input_output.get("outputs")):
                    input_output = None  # 잘못된 형식이면 무시

            # Fallback: 레거시 examples 형식에서 변환
            if not input_output:
                examples = generated_problem.get("examples", [])
                if examples:
                    inputs = []
                    outputs = []
                    for ex in examples:
                        if isinstance(ex, dict):
                            if ex.get("input"):
                                inputs.append(str(ex["input"]))
                            if ex.get("output"):
                                outputs.append(str(ex["output"]))
                    if inputs and outputs:
                        input_output = {"inputs": inputs, "outputs": outputs}

            # ============================================================
            # 🔒 테스트 케이스 검증 (통과해야만 저장) - skip_validation=True면 스킵
            # ============================================================
            if not skip_validation:
                if not input_output:
                    logger.warning(f"[ProblemSave] No test cases (input_output) - cannot validate")
                    return None

                # code_validator로 검증
                from .code_validator import get_code_validator
                validator = get_code_validator()

                # solutions를 code dict로 변환
                code_dict = {}
                for sol in solutions:
                    code_dict[sol["language"]] = sol["code"]

                # input_output을 examples 형식으로 변환
                test_examples = []
                inputs = input_output.get("inputs", [])
                outputs = input_output.get("outputs", [])
                for i in range(min(len(inputs), len(outputs))):
                    test_examples.append({
                        "input": inputs[i],
                        "output": outputs[i],
                    })

                if not test_examples:
                    logger.warning(f"[ProblemSave] No valid test examples - cannot validate")
                    return None

                # 검증 실행
                validation_result = await validator.validate_generated_code(
                    code=code_dict,
                    examples=test_examples,
                    language=collected_info.get("language", "python"),
                    min_pass_rate=0.8,  # 80% 이상 통과해야 저장
                )

                if not validation_result.valid:
                    logger.warning(
                        f"[ProblemSave] ❌ Validation FAILED - not saving to base_problems. "
                        f"Pass rate: {validation_result.pass_rate:.1%} ({validation_result.passed_count}/{validation_result.total_count}). "
                        f"Errors: {validation_result.errors}"
                    )
                    return None

                logger.info(
                    f"[ProblemSave] ✓ Validation PASSED - saving to base_problems. "
                    f"Pass rate: {validation_result.pass_rate:.1%} ({validation_result.passed_count}/{validation_result.total_count})"
                )
            else:
                logger.info(f"[ProblemSave] Skipping validation (already validated)")

            # tags 정규화 (허용된 태그로만 변환) - tags 우선, topics fallback
            raw_tags = generated_problem.get("tags") or generated_problem.get("topics") or collected_info.get("topics", [])
            normalized_tags = normalize_tags(raw_tags)
            # 정규화 후에도 태그가 없으면 collected_info의 topic 사용
            if not normalized_tags and collected_info.get("topic"):
                topic = collected_info.get("topic")
                normalized_tags = normalize_tags([topic]) if isinstance(topic, str) else normalize_tags(topic)

            # base_problems 데이터 구성
            # 필수 컬럼: original_id, name, question, solutions
            # 나머지는 DB default 값 사용 (created_at=now(), like_count=0, solve_count=0, elo_rating=1000)
            data = {
                "original_id": original_id,
                "name": generated_problem.get("title", "Generated Problem"),
                "question": generated_problem.get("description", ""),
                "difficulty": difficulty,  # 이미 검증됨
                "tags": normalized_tags if normalized_tags else None,
                "source": "codegen",
                "solutions": solutions,
                "input_output": input_output,
                # 선택적 컬럼 (LLM이 제공하면 사용)
                "time_limit": generated_problem.get("time_limit"),
                "memory_limit": generated_problem.get("memory_limit"),
                "explanation": generated_problem.get("explanation"),  # 해설이 있으면 저장
            }

            result = self.supabase.table("base_problems").insert(data).execute()

            if result.data and len(result.data) > 0:
                saved_id = result.data[0]["id"]
                saved_original_id = result.data[0]["original_id"]
                logger.info(f"[ProblemSave] CodeGen problem saved to base_problems: {saved_original_id}")
                return saved_id
            return None

        except Exception as e:
            logger.error(f"[ProblemSave] Failed to save CodeGen to base_problems: {e}")
            import traceback
            traceback.print_exc()
            return None

    # ============================================================
    # 조회 메서드 (Cache-First 로직용)
    # base_problem_id + language로 조회 (creator_id 무관)
    # ============================================================

    def find_existing_problem(
        self,
        problem_type: str,
        base_problem_id: str,
        language: str,
    ) -> Optional[Dict[str, Any]]:
        """
        기존 문제 조회 (다른 유저가 만든 것도 포함)

        Args:
            problem_type: 문제 유형 (blank, puzzle, guided)
            base_problem_id: base_problems 테이블의 UUID
            language: 프로그래밍 언어

        Returns:
            문제 데이터 또는 None (캐시 무효일 경우에도 None)
        """
        table_name = f"problems_{problem_type}"

        try:
            result = self.supabase.table(table_name) \
                .select("*") \
                .eq("base_problem_id", base_problem_id) \
                .eq("language", language) \
                .limit(1) \
                .execute()

            if result.data and len(result.data) > 0:
                cached_data = result.data[0]

                # 빈칸 문제의 경우 캐시 유효성 검증
                if problem_type == "blank":
                    if not _validate_blank_problem(cached_data):
                        logger.warning(f"[ProblemCache] Invalid blank cache for {base_problem_id}, will regenerate")
                        # 무효한 캐시는 삭제
                        try:
                            self.supabase.table(table_name) \
                                .delete() \
                                .eq("id", cached_data.get("id")) \
                                .execute()
                            logger.info(f"[ProblemCache] Deleted invalid cache: {cached_data.get('id')}")
                        except Exception as del_err:
                            logger.warning(f"[ProblemCache] Failed to delete invalid cache: {del_err}")
                        return None  # 캐시 미스로 처리하여 재생성 유도

                logger.info(f"[ProblemCache] {problem_type} problem found: {base_problem_id} ({language})")
                return cached_data
            return None

        except Exception as e:
            logger.error(f"[ProblemCache] Failed to find {problem_type} problem: {e}")
            return None

    def check_user_has_problem(
        self,
        problem_type: str,
        base_problem_id: str,
        language: str,
        creator_id: str,
    ) -> Optional[Dict[str, Any]]:
        """
        특정 유저가 이미 해당 문제를 가지고 있는지 확인

        Args:
            problem_type: 문제 유형 (blank, puzzle, guided)
            base_problem_id: base_problems 테이블의 UUID
            language: 프로그래밍 언어
            creator_id: 사용자 UUID

        Returns:
            문제 데이터 또는 None (캐시 무효일 경우에도 None)
        """
        table_name = f"problems_{problem_type}"

        try:
            result = self.supabase.table(table_name) \
                .select("*") \
                .eq("base_problem_id", base_problem_id) \
                .eq("language", language) \
                .eq("creator_id", creator_id) \
                .limit(1) \
                .execute()

            if result.data and len(result.data) > 0:
                cached_data = result.data[0]

                # 빈칸 문제의 경우 캐시 유효성 검증
                if problem_type == "blank":
                    if not _validate_blank_problem(cached_data):
                        logger.warning(f"[ProblemCache] User's invalid blank cache for {base_problem_id}, will regenerate")
                        # 무효한 캐시는 삭제
                        try:
                            self.supabase.table(table_name) \
                                .delete() \
                                .eq("id", cached_data.get("id")) \
                                .execute()
                            logger.info(f"[ProblemCache] Deleted user's invalid cache: {cached_data.get('id')}")
                        except Exception as del_err:
                            logger.warning(f"[ProblemCache] Failed to delete invalid cache: {del_err}")
                        return None  # 캐시 미스로 처리하여 재생성 유도

                logger.info(f"[ProblemCache] User already has {problem_type}: {base_problem_id}")
                return cached_data
            return None

        except Exception as e:
            logger.error(f"[ProblemCache] Failed to check user problem: {e}")
            return None

    # ============================================================
    # 복사 메서드 (캐시 히트 시 사용)
    # ============================================================

    async def copy_problem_for_user(
        self,
        problem_type: str,
        source_problem: Dict[str, Any],
        creator_id: str,
    ) -> Dict[str, Any]:
        """
        기존 문제를 복사하고 creator_id만 변경하여 새 레코드 생성

        Args:
            problem_type: 문제 유형 (blank, puzzle, guided)
            source_problem: 복사할 원본 문제 데이터
            creator_id: 새로운 사용자 UUID

        Returns:
            저장 결과
        """
        table_name = f"problems_{problem_type}"

        try:
            # 복사할 데이터 준비 (id, created_at, updated_at 제외)
            copy_data = {
                "base_problem_id": source_problem.get("base_problem_id"),
                "language": source_problem.get("language"),
                "creator_id": creator_id,  # 새 사용자로 변경
            }

            # 유형별 필드 복사
            if problem_type == "blank":
                copy_data["code_template"] = source_problem.get("code_template")
                copy_data["answers"] = source_problem.get("answers")

            elif problem_type == "puzzle":
                copy_data["fixed_start"] = source_problem.get("fixed_start")
                copy_data["fixed_end"] = source_problem.get("fixed_end")
                copy_data["blocks"] = source_problem.get("blocks")

            elif problem_type == "guided":
                # 새 스키마 (2026-01-12 리팩토링)
                copy_data["concept_explanation"] = source_problem.get("concept_explanation", "")
                copy_data["variables_guide"] = source_problem.get("variables_guide", {})
                copy_data["approach_guide"] = source_problem.get("approach_guide", "")
                copy_data["starter_code"] = source_problem.get("starter_code", "")

            # 새 레코드 삽입
            result = self.supabase.table(table_name).insert(copy_data).execute()

            logger.info(f"[ProblemSave] Copied {problem_type} for user {creator_id[:8]}...")
            return {"success": True, "data": result.data[0] if result.data else None}

        except Exception as e:
            logger.error(f"[ProblemSave] Failed to copy {problem_type}: {e}")
            return {"success": False, "error": str(e)}

    # ============================================================
    # 저장 메서드 (LLM 생성 후 사용)
    # ============================================================

    async def save_blank_problem(
        self,
        base_problem_id: str,
        language: str,
        code_template: str,
        answers: list,
        creator_id: str,
    ) -> Dict[str, Any]:
        """빈칸 채우기 문제 저장 (저장 전 유효성 검증)"""
        try:
            data = {
                "base_problem_id": base_problem_id,
                "language": language,
                "code_template": code_template,
                "answers": answers,
                "creator_id": creator_id,
            }

            # 저장 전 유효성 검증 - 무효한 데이터는 저장하지 않음
            if not _validate_blank_problem(data):
                logger.error(f"[ProblemSave] ❌ Refusing to save invalid blank problem: {base_problem_id[:8]}...")
                return {"success": False, "error": "Invalid blank problem: code_template has no _N_ patterns"}

            result = self.supabase.table("problems_blank").insert(data).execute()

            logger.info(f"[ProblemSave] Blank problem saved: {base_problem_id[:8]}... (user: {creator_id[:8]}...)")
            return {"success": True, "data": result.data[0] if result.data else None}

        except Exception as e:
            logger.error(f"[ProblemSave] Failed to save blank problem: {e}")
            return {"success": False, "error": str(e)}

    async def save_puzzle_problem(
        self,
        base_problem_id: str,
        language: str,
        blocks: list,
        creator_id: str,
        fixed_start: Optional[str] = None,
        fixed_end: Optional[str] = None,
    ) -> Dict[str, Any]:
        """퍼즐 문제 저장"""
        try:
            data = {
                "base_problem_id": base_problem_id,
                "language": language,
                "blocks": blocks,
                "creator_id": creator_id,
            }

            if fixed_start:
                data["fixed_start"] = fixed_start
            if fixed_end:
                data["fixed_end"] = fixed_end

            result = self.supabase.table("problems_puzzle").insert(data).execute()

            logger.info(f"[ProblemSave] Puzzle problem saved: {base_problem_id[:8]}... (user: {creator_id[:8]}...)")
            return {"success": True, "data": result.data[0] if result.data else None}

        except Exception as e:
            logger.error(f"[ProblemSave] Failed to save puzzle problem: {e}")
            return {"success": False, "error": str(e)}

    async def save_guided_problem(
        self,
        base_problem_id: str,
        language: str,
        creator_id: str,
        concept_explanation: str = "",
        variables_guide: dict = None,
        approach_guide: str = "",
        starter_code: str = "",
        # Legacy 파라미터 (하위 호환)
        concepts: list = None,
        flow: list = None,
        checkpoints: list = None,
    ) -> Dict[str, Any]:
        """
        1대1 대화형 문제 저장

        새 스키마 (2026-01-12 리팩토링):
        - concept_explanation: 핵심 개념 설명
        - variables_guide: 변수 가이드 (JSON)
        - approach_guide: 접근법 가이드
        - starter_code: 맛보기 코드
        """
        try:
            data = {
                "base_problem_id": base_problem_id,
                "language": language,
                "creator_id": creator_id,
                "concept_explanation": concept_explanation or "개념 설명이 제공되지 않았습니다.",
                "variables_guide": variables_guide or {"variables": []},
                "approach_guide": approach_guide or "접근법 가이드가 제공되지 않았습니다.",
                "starter_code": starter_code or f"# {language} 코드",
            }

            result = self.supabase.table("problems_guided").insert(data).execute()

            logger.info(f"[ProblemSave] Guided problem saved: {base_problem_id[:8]}... (user: {creator_id[:8]}...)")
            return {"success": True, "data": result.data[0] if result.data else None}

        except Exception as e:
            logger.error(f"[ProblemSave] Failed to save guided problem: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}

    async def save_generated_problem(
        self,
        problem_type: str,
        generated_data: Dict[str, Any],
        base_problem_id: str,
        creator_id: str,
    ) -> Dict[str, Any]:
        """
        LLM이 생성한 문제를 저장

        Args:
            problem_type: 문제 유형 (blank, puzzle, guided)
            generated_data: LLM이 생성한 데이터
            base_problem_id: base_problems 테이블의 UUID
            creator_id: 사용자 UUID

        Returns:
            저장 결과
        """
        language = generated_data.get("language", "python")

        if problem_type == "blank":
            return await self.save_blank_problem(
                base_problem_id=base_problem_id,
                language=language,
                code_template=generated_data.get("code_template", ""),
                answers=generated_data.get("answers", []),
                creator_id=creator_id,
            )

        elif problem_type == "puzzle":
            return await self.save_puzzle_problem(
                base_problem_id=base_problem_id,
                language=language,
                blocks=generated_data.get("blocks", []),
                creator_id=creator_id,
                fixed_start=generated_data.get("fixed_start"),
                fixed_end=generated_data.get("fixed_end"),
            )

        elif problem_type == "guided":
            # 새 스키마 (2026-01-12 리팩토링)
            return await self.save_guided_problem(
                base_problem_id=base_problem_id,
                language=language,
                creator_id=creator_id,
                concept_explanation=generated_data.get("concept_explanation", ""),
                variables_guide=generated_data.get("variables_guide", {}),
                approach_guide=generated_data.get("approach_guide", ""),
                starter_code=generated_data.get("starter_code", ""),
            )

        else:
            return {"success": False, "error": f"Unknown problem type: {problem_type}"}


# Singleton instance
_problem_save_service = None


def get_problem_save_service() -> ProblemSaveService:
    """ProblemSaveService 싱글톤 반환"""
    global _problem_save_service
    if _problem_save_service is None:
        _problem_save_service = ProblemSaveService()
    return _problem_save_service
