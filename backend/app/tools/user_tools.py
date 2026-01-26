"""
User Tools - 사용자 프로필 조회 및 DB 기반 개인화 추천

핵심 Tool:
1. get_user_profile: DB에서 사용자 프로필 조회
2. get_topic_recommendations: DB 태그 분석 기반 주제 추천 (칩 UI 포함)
3. get_difficulty_recommendations: 사용자 레벨 기반 난이도 추천 (칩 UI 포함)

태그 정규화:
- scripts/update_tag_normalization.py 실행하면 data/tag_normalization.json 생성
- 백준 등 새 데이터 추가 시 스크립트 재실행으로 태그 매핑 업데이트

대기업 코테 빈출 유형 (실제 데이터 + 전문 지식):
- DP (동적 프로그래밍): 삼성, 카카오, 네이버 필수
- 그래프 (BFS/DFS): 거의 모든 기업 출제
- 구현/시뮬레이션: 삼성 특화
- 이분탐색: 카카오 빈출
- 자료구조: 스택, 큐, 힙
- 그리디: 기본 유형
"""

from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from collections import Counter
import logging
import json
import os

from ..database import get_supabase_client

logger = logging.getLogger(__name__)


# ============================================================
# 태그 정규화 데이터 로드
# ============================================================
def _load_tag_normalization() -> Dict[str, Any]:
    """
    태그 정규화 JSON 파일 로드

    scripts/update_tag_normalization.py 실행 시 생성됨
    파일이 없으면 하드코딩된 기본값 사용
    """
    json_path = os.path.join(os.path.dirname(__file__), "data", "tag_normalization.json")

    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                logger.info(f"[UserTools] Loaded tag normalization from JSON: {len(data.get('normalization', {}))} mappings")
                return data
        except Exception as e:
            logger.warning(f"[UserTools] Failed to load tag normalization JSON: {e}")

    return None


# JSON 파일 로드 시도
_TAG_DATA = _load_tag_normalization()


# ============================================================
# 대기업 코테 빈출 유형 (전문 지식 기반)
# ============================================================

# 대기업별 빈출 알고리즘 (실제 기출 분석 기반)
COMPANY_ALGORITHM_FREQUENCY = {
    "삼성": ["구현", "시뮬레이션", "BFS/DFS", "그래프", "완전탐색"],
    "카카오": ["문자열", "구현", "이분탐색", "DP", "그래프"],
    "네이버": ["DP", "그래프", "구현", "자료구조", "정렬"],
    "라인": ["DP", "그래프", "문자열", "구현", "자료구조"],
    "쿠팡": ["DP", "그래프", "이분탐색", "자료구조", "정렬"],
    "배민": ["구현", "DP", "그래프", "자료구조", "문자열"],
}

# 대기업 코테 종합 빈출 순위 (TOP 10)
BIG_TECH_TOP_ALGORITHMS = [
    {"tag": "DP", "rank": 1, "reason": "거의 모든 대기업 필수, 특히 카카오/네이버"},
    {"tag": "그래프", "rank": 2, "reason": "BFS/DFS 포함, 삼성/카카오 빈출"},
    {"tag": "구현", "rank": 3, "reason": "삼성 특화, 시뮬레이션 포함"},
    {"tag": "이분탐색", "rank": 4, "reason": "카카오/쿠팡 빈출"},
    {"tag": "문자열", "rank": 5, "reason": "카카오 특화"},
    {"tag": "자료구조", "rank": 6, "reason": "스택/큐/힙, 기본기"},
    {"tag": "정렬", "rank": 7, "reason": "기초지만 자주 출제"},
    {"tag": "그리디", "rank": 8, "reason": "기본 유형"},
    {"tag": "백트래킹", "rank": 9, "reason": "완전탐색 변형"},
    {"tag": "BFS/DFS", "rank": 10, "reason": "그래프 기초"},
]

# 스타트업/중소기업 추천 알고리즘
STARTUP_ALGORITHMS = ["구현", "정렬", "문자열", "DP", "자료구조", "그래프"]

# 실력 향상용 기초 알고리즘
SKILL_UP_ALGORITHMS = ["기초", "정렬", "구현", "문자열", "스택/큐", "수학"]

# ============================================================
# 태그 정규화 (의미 중복 병합) - 기본값
# ============================================================
# JSON 파일이 있으면 그것을 사용, 없으면 아래 기본값 사용
# scripts/update_tag_normalization.py 실행 시 JSON 파일 생성됨
_DEFAULT_TAG_NORMALIZATION = {
    # ============================================================
    # 영문 태그 → 한글 정규화 (DB 실제 태그 기반)
    # ============================================================
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

    # ============================================================
    # BFS/DFS 계열 통합
    # ============================================================
    "bfs": "BFS/DFS",
    "dfs": "BFS/DFS",
    "BFS": "BFS/DFS",
    "DFS": "BFS/DFS",
    "너비 우선 탐색": "BFS/DFS",
    "깊이 우선 탐색": "BFS/DFS",

    # ============================================================
    # 스택/큐 계열 통합
    # ============================================================
    "스택": "스택/큐",
    "큐": "스택/큐",
    "stack": "스택/큐",
    "queue": "스택/큐",

    # ============================================================
    # DP 별칭
    # ============================================================
    "동적 프로그래밍": "DP",
    "동적프로그래밍": "DP",
    "다이나믹 프로그래밍": "DP",
    "동적계획법": "DP",
    "dp": "DP",

    # ============================================================
    # 기타 한글 별칭
    # ============================================================
    "이진 탐색": "이분탐색",
    "이진탐색": "이분탐색",
    "binary search": "이분탐색",
    "two pointer": "투포인터",
    "two pointers": "투포인터",
    "graph": "그래프",
    "sort": "정렬",
    "sorting": "정렬",
    "string": "문자열",
    "strings": "문자열",
    "implementation": "구현",
    "시뮬레이션": "구현",
    "brute force": "완전탐색",
    "bruteforce": "완전탐색",
    "브루트포스": "완전탐색",
    "backtracking": "백트래킹",
    "greedy": "그리디",
    "그리디 알고리즘": "그리디",
    "탐욕법": "그리디",
    "math": "수학",
    "mathematics": "수학",
    "매개 변수 탐색": "파라메트릭서치",
    "파라메트릭 서치": "파라메트릭서치",
    "누적 합": "누적합",
    "해시테이블": "해시",
    "딕셔너리": "해시",
}

# 제외할 태그 (추천에서 제외) - 기본값
_DEFAULT_EXCLUDED_TAGS = {
    "기타", "etc", "기타 알고리즘", "미분류", "uncategorized",
    "출처", "source", "언어", "language",
    "asgsag",  # DB에 있는 의미없는 태그
}

# ============================================================
# 주제 간 연관성 맵 (학습 경로 기반) - 기본값
# ============================================================
# 각 주제에서 다음으로 추천할 연관 주제들
# base_problems.tags의 실제 태그를 정규화한 값 기준
_DEFAULT_TOPIC_RELATIONS = {
    # ============================================================
    # 기초 → 응용
    # ============================================================
    "기초": ["구현", "정렬", "수학", "문자열"],
    "수학": ["정렬", "구현", "DP", "정수론", "조합론"],
    "정수론": ["수학", "조합론", "DP"],
    "조합론": ["수학", "DP", "백트래킹"],

    # ============================================================
    # 탐색 계열
    # ============================================================
    "BFS/DFS": ["그래프", "백트래킹", "최단경로", "완전탐색", "트리"],
    "그래프": ["BFS/DFS", "최단경로", "최소신장트리", "트리"],
    "백트래킹": ["BFS/DFS", "완전탐색", "조합론"],
    "완전탐색": ["백트래킹", "구현", "BFS/DFS"],
    "최단경로": ["그래프", "BFS/DFS", "DP"],
    "최소신장트리": ["그래프", "그리디"],
    "트리": ["그래프", "BFS/DFS", "DP"],

    # ============================================================
    # DP 계열
    # ============================================================
    "DP": ["그리디", "분할정복", "이분탐색", "트리"],
    "그리디": ["DP", "정렬", "이분탐색"],
    "분할정복": ["DP", "이분탐색"],

    # ============================================================
    # 자료구조 계열
    # ============================================================
    "자료구조": ["해시", "트리", "구간쿼리", "세그먼트트리"],
    "해시": ["문자열", "자료구조"],
    "구간쿼리": ["세그먼트트리", "자료구조", "DP"],
    "세그먼트트리": ["구간쿼리", "트리", "자료구조"],

    # ============================================================
    # 문자열 계열
    # ============================================================
    "문자열": ["해시", "구현", "DP"],
    "정렬": ["이분탐색", "그리디", "자료구조"],

    # ============================================================
    # 고급 기법
    # ============================================================
    "이분탐색": ["정렬", "파라메트릭서치", "그리디"],
    "파라메트릭서치": ["이분탐색", "그리디"],
    "비트마스킹": ["DP", "완전탐색"],
    "기하학": ["구현", "수학"],

    # ============================================================
    # 구현
    # ============================================================
    "구현": ["완전탐색", "문자열", "BFS/DFS", "정렬"],
}

# ============================================================
# 실제 사용되는 상수 (JSON 파일 우선, 없으면 기본값)
# ============================================================
if _TAG_DATA:
    # JSON 파일에서 로드된 데이터 사용
    TAG_NORMALIZATION = {**_DEFAULT_TAG_NORMALIZATION, **_TAG_DATA.get("normalization", {}), **_TAG_DATA.get("semantic_merge", {})}
    EXCLUDED_TAGS = set(_TAG_DATA.get("excluded_tags", [])) | _DEFAULT_EXCLUDED_TAGS
    TOPIC_RELATIONS = _TAG_DATA.get("topic_relations", _DEFAULT_TOPIC_RELATIONS)
    logger.info(f"[UserTools] Using JSON tag data: {len(TAG_NORMALIZATION)} mappings, {len(TOPIC_RELATIONS)} relations")
else:
    # 기본값 사용
    TAG_NORMALIZATION = _DEFAULT_TAG_NORMALIZATION
    EXCLUDED_TAGS = _DEFAULT_EXCLUDED_TAGS
    TOPIC_RELATIONS = _DEFAULT_TOPIC_RELATIONS


# 레벨별 권장 난이도 (온보딩 기준)
# beginner (입문자): 거의 안 풀어봄 → 실버
# elementary (초급자): 백준 브론즈~실버 / 프로그래머스 Lv.1 → 실버~골드
# intermediate (중급자): 백준 골드 / 프로그래머스 Lv.2 → 골드~플래티넘
# advanced (고급자): 백준 플래티넘+ / 프로그래머스 Lv.3+ → 다이아~마스터
LEVEL_TO_DIFFICULTY = {
    "beginner": {"recommended": "easy", "range": ["easy"]},                      # 입문자 → 실버
    "elementary": {"recommended": "easy", "range": ["easy", "medium"]},          # 초급자 → 실버, 골드
    "intermediate": {"recommended": "medium", "range": ["medium", "medium_hard"]},  # 중급자 → 골드, 플래티넘
    "advanced": {"recommended": "hard", "range": ["hard", "very_hard"]},         # 고급자 → 다이아, 마스터
    "unknown": {"recommended": "easy", "range": ["easy", "medium"]},
}

# 난이도 표시명 (프론트엔드 tiers.ts와 동기화)
# 아이콘은 프론트엔드에서 렌더링 (SilverIcon, GoldIcon 등)
DIFFICULTY_DISPLAY = {
    "easy": {"display": "실버", "nameEn": "Silver", "description": "기본 개념 연습"},
    "medium": {"display": "골드", "nameEn": "Gold", "description": "응용 문제"},
    "medium_hard": {"display": "플래티넘", "nameEn": "Platinum", "description": "심화 응용"},
    "hard": {"display": "다이아", "nameEn": "Diamond", "description": "도전적인 문제"},
    "very_hard": {"display": "마스터", "nameEn": "Master", "description": "최상위 난이도"},
}


@dataclass
class UserProfileResult:
    """사용자 프로필 조회 결과"""
    success: bool
    user_id: Optional[str] = None
    experience_level: Optional[str] = None
    learning_goal: Optional[str] = None
    current_status: Optional[str] = None
    strong_algorithms: Optional[List[str]] = None
    preferred_difficulty: Optional[str] = None
    preferred_language: Optional[str] = None
    total_xp: int = 0
    level: int = 1
    problems_solved: int = 0
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "user_id": self.user_id,
            "experience_level": self.experience_level,
            "learning_goal": self.learning_goal,
            "current_status": self.current_status,
            "strong_algorithms": self.strong_algorithms or [],
            "preferred_difficulty": self.preferred_difficulty,
            "preferred_language": self.preferred_language,
            "total_xp": self.total_xp,
            "level": self.level,
            "problems_solved": self.problems_solved,
            "error": self.error,
        }


@dataclass
class TopicChip:
    """주제 선택 칩"""
    label: str           # 표시 텍스트 (예: "DP (동적 프로그래밍)")
    value: str           # 선택 값 (예: "DP")
    category: str = "topic"
    problem_count: int = 0  # DB에 있는 문제 수
    rank: Optional[int] = None  # 빈출 순위 (대기업 목표 시)
    reason: Optional[str] = None  # 추천 이유

    def to_dict(self) -> Dict[str, Any]:
        return {
            "label": self.label,
            "value": self.value,
            "category": self.category,
            "problem_count": self.problem_count,
            "rank": self.rank,
            "reason": self.reason,
        }


@dataclass
class DifficultyChip:
    """난이도 선택 칩 (프론트엔드에서 아이콘 렌더링)"""
    label: str           # 표시 텍스트 (예: "골드")
    value: str           # 선택 값 (예: "medium")
    category: str = "difficulty"
    nameEn: str = ""     # 영문 이름 (아이콘 매칭용)
    description: str = ""
    is_recommended: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "label": self.label,
            "value": self.value,
            "category": self.category,
            "nameEn": self.nameEn,
            "description": self.description,
            "is_recommended": self.is_recommended,
        }


@dataclass
class TopicRecommendationResult:
    """주제 추천 결과 (칩 UI 포함)"""
    success: bool
    recommended_topic: str
    topic_chips: List[TopicChip] = field(default_factory=list)
    message: str = ""
    personalization_context: str = ""  # "대기업 코테 준비 중급자"
    db_analysis: Optional[Dict[str, int]] = None  # DB 태그 분포

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "recommended_topic": self.recommended_topic,
            "topic_chips": [c.to_dict() for c in self.topic_chips],
            "message": self.message,
            "personalization_context": self.personalization_context,
            "db_analysis": self.db_analysis,
        }


@dataclass
class DifficultyRecommendationResult:
    """난이도 추천 결과 (칩 UI 포함)"""
    success: bool
    recommended_difficulty: str
    recommended_display: str
    difficulty_chips: List[DifficultyChip] = field(default_factory=list)
    message: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "recommended_difficulty": self.recommended_difficulty,
            "recommended_display": self.recommended_display,
            "difficulty_chips": [c.to_dict() for c in self.difficulty_chips],
            "message": self.message,
        }


@dataclass
class RecommendationResult:
    """통합 개인화 추천 결과 (기존 호환)"""
    recommended_topic: str
    recommended_difficulty: str
    recommended_difficulty_display: str
    topic_options: List[str]
    difficulty_options: List[str]
    personalization_reason: str
    user_summary: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "recommended_topic": self.recommended_topic,
            "recommended_difficulty": self.recommended_difficulty,
            "recommended_difficulty_display": self.recommended_difficulty_display,
            "topic_options": self.topic_options,
            "difficulty_options": self.difficulty_options,
            "personalization_reason": self.personalization_reason,
            "user_summary": self.user_summary,
        }


class UserTools:
    """사용자 관련 Tool 모음 - DB 기반 개인화 추천"""

    def __init__(self):
        self.supabase = get_supabase_client()
        self._tag_cache: Optional[Dict[str, int]] = None
        self._available_tags_cache: Optional[set] = None  # DB에 있는 정규화된 태그
        self._cache_timestamp: float = 0

    # ============================================================
    # 태그 정규화 헬퍼
    # ============================================================

    def _normalize_tag(self, tag: str) -> Optional[str]:
        """
        태그를 정규화된 형태로 변환

        예: "BFS" → "BFS/DFS", "동적프로그래밍" → "DP"

        Returns:
            정규화된 태그명, 제외 대상이면 None
        """
        if not tag:
            return None

        tag = tag.strip()

        # 제외 태그 체크
        if tag.lower() in {t.lower() for t in EXCLUDED_TAGS}:
            return None

        # 정규화 맵에서 찾기
        normalized = TAG_NORMALIZATION.get(tag)
        if normalized:
            return normalized

        # 소문자로도 확인
        normalized = TAG_NORMALIZATION.get(tag.lower())
        if normalized:
            return normalized

        # 정규화 맵에 없으면 원본 반환
        return tag

    def _normalize_tags(self, tags: List[str]) -> List[str]:
        """
        태그 목록을 정규화하고 중복 제거

        Returns:
            정규화된 유니크 태그 목록
        """
        normalized = set()
        for tag in tags:
            norm = self._normalize_tag(tag)
            if norm:
                normalized.add(norm)
        return list(normalized)

    async def _get_available_tags_from_db(self, force_refresh: bool = False) -> set:
        """
        base_problems 테이블에서 사용 가능한 정규화된 태그 목록 조회

        Returns:
            정규화된 유니크 태그 set
        """
        import time

        # 캐시 유효시간: 1시간
        if not force_refresh and self._available_tags_cache and (time.time() - self._cache_timestamp < 3600):
            return self._available_tags_cache

        try:
            # base_problems에서 tags 컬럼 조회
            result = self.supabase.table("base_problems") \
                .select("tags") \
                .execute()

            if not result.data:
                logger.warning("[UserTools] No data in base_problems")
                return set()

            # 정규화된 태그 수집
            available_tags = set()
            for row in result.data:
                tags = row.get("tags", [])
                if tags:
                    for tag in tags:
                        normalized = self._normalize_tag(tag)
                        if normalized:
                            available_tags.add(normalized)

            self._available_tags_cache = available_tags
            logger.info(f"[UserTools] Available tags from DB: {len(available_tags)} unique tags")
            return available_tags

        except Exception as e:
            logger.error(f"[UserTools] Failed to get available tags: {e}")
            return set()

    async def _get_user_solved_tags(self, user_id: str) -> set:
        """
        사용자가 풀어본 문제들의 정규화된 태그 목록 조회

        attempts + base_problems 조인으로 정확한 태그 추출

        Returns:
            사용자가 풀어본 정규화된 태그 set
        """
        try:
            # attempts에서 base_problem_id 조회
            attempts_result = self.supabase.table("attempts") \
                .select("base_problem_id") \
                .eq("user_id", user_id) \
                .not_.is_("base_problem_id", "null") \
                .execute()

            if not attempts_result.data:
                return set()

            # base_problem_id 목록 추출
            base_problem_ids = list(set(
                row.get("base_problem_id")
                for row in attempts_result.data
                if row.get("base_problem_id")
            ))

            if not base_problem_ids:
                return set()

            # base_problems에서 해당 문제들의 태그 조회
            problems_result = self.supabase.table("base_problems") \
                .select("tags") \
                .in_("id", base_problem_ids) \
                .execute()

            if not problems_result.data:
                return set()

            # 정규화된 태그 수집
            solved_tags = set()
            for row in problems_result.data:
                tags = row.get("tags", [])
                if tags:
                    for tag in tags:
                        normalized = self._normalize_tag(tag)
                        if normalized:
                            solved_tags.add(normalized)

            logger.info(f"[UserTools] User {user_id[:8]}... solved tags: {len(solved_tags)}")
            return solved_tags

        except Exception as e:
            logger.error(f"[UserTools] Failed to get user solved tags: {e}")
            return set()

    # ============================================================
    # Tool 1: 사용자 프로필 조회
    # ============================================================

    async def get_user_profile(self, user_id: str) -> UserProfileResult:
        """
        DB에서 사용자 프로필 조회

        Tool 설명 (LLM용):
        - 사용자의 경험 레벨, 학습 목표, 선호 난이도/언어 조회
        - "내 수준에 맞게 추천해줘" 같은 요청 시 호출
        - 개인화 추천을 위한 기반 정보 제공

        Args:
            user_id: 사용자 UUID

        Returns:
            UserProfileResult with experience_level, learning_goal, etc.
        """
        if not user_id:
            return UserProfileResult(success=False, error="user_id가 필요합니다")

        try:
            # users 테이블에서 프로필 조회
            user_result = self.supabase.table("users") \
                .select("id, experience_level, learning_goal, current_status, strong_algorithms") \
                .eq("id", user_id) \
                .limit(1) \
                .execute()

            if not user_result.data or len(user_result.data) == 0:
                logger.warning(f"[UserTools] User not found: {user_id[:8]}...")
                return UserProfileResult(success=False, error="사용자를 찾을 수 없습니다")

            user_data = user_result.data[0]

            # user_preferences 테이블은 사용하지 않음 (테이블 없음)
            pref_data = {}

            # user_stats 테이블에서 통계 조회
            stats_result = self.supabase.table("user_stats") \
                .select("total_xp, level, problems_solved") \
                .eq("user_id", user_id) \
                .limit(1) \
                .execute()

            stats_data = stats_result.data[0] if stats_result.data else {}

            logger.info(f"[UserTools] Profile fetched: level={user_data.get('experience_level')}, goal={user_data.get('learning_goal')}")

            return UserProfileResult(
                success=True,
                user_id=user_id,
                experience_level=user_data.get("experience_level"),
                learning_goal=user_data.get("learning_goal"),
                current_status=user_data.get("current_status"),
                strong_algorithms=user_data.get("strong_algorithms") or [],
                preferred_difficulty=pref_data.get("preferred_difficulty"),
                preferred_language=pref_data.get("preferred_language"),
                total_xp=stats_data.get("total_xp", 0),
                level=stats_data.get("level", 1),
                problems_solved=stats_data.get("problems_solved", 0),
            )

        except Exception as e:
            logger.error(f"[UserTools] Failed to get user profile: {e}")
            return UserProfileResult(success=False, error=str(e))

    # ============================================================
    # Tool 2: DB 기반 주제 추천 (칩 UI 포함)
    # ============================================================

    async def get_topic_recommendations(
        self,
        learning_goal: str = "unknown",
        experience_level: str = "unknown",
        strong_algorithms: List[str] = None,
        limit: int = 6,
    ) -> TopicRecommendationResult:
        """
        학습 목표와 레벨에 따른 주제 추천 (DB 태그 분석 + 전문 지식)

        Tool 설명 (LLM용):
        - 대기업 목표: 실제 코테 빈출 유형 기반 추천 + DB 문제 수
        - 스타트업 목표: 실무 중심 알고리즘 추천
        - 실력향상: 기초부터 단계별 추천
        - 칩 UI로 사용자가 선택 가능

        Args:
            learning_goal: big_tech / mid_startup / skill_up / unknown
            experience_level: beginner / elementary / intermediate / advanced / unknown
            strong_algorithms: 이미 잘하는 알고리즘 목록 (제외)
            limit: 반환할 칩 개수

        Returns:
            TopicRecommendationResult with topic_chips for UI
        """
        strong = strong_algorithms or []
        strong_lower = [s.lower() for s in strong]

        # DB에서 태그 분포 조회
        tag_counts = await self._get_tag_distribution()

        # 목표별 추천 알고리즘 선택
        if learning_goal == "big_tech":
            base_algorithms = BIG_TECH_TOP_ALGORITHMS
            context = "대기업 코테"
            message = "대기업 코테에서 가장 많이 나오는 유형이에요! 원하는 주제를 선택해주세요."
        elif learning_goal == "mid_startup":
            base_algorithms = [{"tag": t, "rank": i+1, "reason": "실무 활용도 높음"}
                              for i, t in enumerate(STARTUP_ALGORITHMS)]
            context = "스타트업 취업"
            message = "스타트업에서 자주 요구하는 실무 중심 알고리즘이에요!"
        else:
            base_algorithms = [{"tag": t, "rank": i+1, "reason": "기초 실력 향상"}
                              for i, t in enumerate(SKILL_UP_ALGORITHMS)]
            context = "실력 향상"
            message = "기초부터 탄탄하게! 원하는 주제를 선택해주세요."

        # 레벨에 따른 필터링/정렬
        level_context = {
            "beginner": "입문자",
            "elementary": "초급자",
            "intermediate": "중급자",
            "advanced": "고급자",
        }.get(experience_level, "")

        if level_context:
            context = f"{context} 준비 {level_context}"

        # 칩 생성 (잘하는 알고리즘 제외)
        topic_chips = []
        for algo in base_algorithms:
            tag = algo["tag"]
            if tag.lower() in strong_lower:
                continue

            # DB 문제 수 조회
            problem_count = tag_counts.get(tag, 0)

            # 레이블 생성 (이모지 없이 순위 표시)
            rank = algo.get("rank", 99)
            if learning_goal == "big_tech" and rank <= 5:
                label = f"{tag} (TOP {rank})"
            else:
                label = tag

            topic_chips.append(TopicChip(
                label=label,
                value=tag,
                category="topic",
                problem_count=problem_count,
                rank=rank if rank <= 10 else None,
                reason=algo.get("reason"),
            ))

            if len(topic_chips) >= limit:
                break

        # 추천 주제 (첫 번째)
        recommended = topic_chips[0].value if topic_chips else "기초"

        return TopicRecommendationResult(
            success=True,
            recommended_topic=recommended,
            topic_chips=topic_chips,
            message=message,
            personalization_context=context,
            db_analysis=tag_counts,
        )

    # ============================================================
    # Tool 3: 난이도 추천 (칩 UI 포함)
    # ============================================================

    def get_difficulty_recommendations(
        self,
        experience_level: str = "unknown",
        selected_topic: Optional[str] = None,
    ) -> DifficultyRecommendationResult:
        """
        사용자 레벨에 따른 난이도 추천 (칩 UI 포함)

        Tool 설명 (LLM용):
        - 레벨에 맞는 난이도 범위 추천
        - 선택한 주제에 따라 메시지 커스텀
        - 칩 UI로 사용자가 선택 가능

        Args:
            experience_level: beginner / elementary / intermediate / advanced / unknown
            selected_topic: 선택된 주제 (메시지 커스텀용)

        Returns:
            DifficultyRecommendationResult with difficulty_chips for UI
        """
        level_config = LEVEL_TO_DIFFICULTY.get(experience_level, LEVEL_TO_DIFFICULTY["unknown"])
        recommended = level_config["recommended"]
        difficulty_range = level_config["range"]

        # 칩 생성 (프론트엔드에서 아이콘 렌더링)
        difficulty_chips = []
        for diff in difficulty_range:
            display_info = DIFFICULTY_DISPLAY.get(diff, {})
            is_recommended = (diff == recommended)

            label = display_info.get("display", diff)
            if is_recommended:
                label += " (추천)"

            difficulty_chips.append(DifficultyChip(
                label=label,
                value=diff,
                category="difficulty",
                nameEn=display_info.get("nameEn", ""),
                description=display_info.get("description", ""),
                is_recommended=is_recommended,
            ))

        # 메시지 생성
        topic_mention = f"{selected_topic} 주제로" if selected_topic else ""
        level_name = {"beginner": "입문자", "elementary": "초급자",
                      "intermediate": "중급자", "advanced": "고급자"}.get(experience_level, "")

        if level_name:
            message = f"{topic_mention} {level_name}에게 적합한 난이도를 추천해드려요!"
        else:
            message = f"{topic_mention} 원하는 난이도를 선택해주세요!"

        recommended_display = DIFFICULTY_DISPLAY.get(recommended, {}).get("display", "실버")

        return DifficultyRecommendationResult(
            success=True,
            recommended_difficulty=recommended,
            recommended_display=recommended_display,
            difficulty_chips=difficulty_chips,
            message=message.strip(),
        )

    # ============================================================
    # Tool 4: 통합 추천 (기존 호환용)
    # ============================================================

    def get_personalized_recommendations(
        self,
        profile: UserProfileResult = None,
        experience_level: str = None,
        learning_goal: str = None,
        strong_algorithms: List[str] = None,
        preferred_difficulty: str = None,
    ) -> RecommendationResult:
        """
        기존 호환용 통합 추천 (레거시)

        Args:
            profile: UserProfileResult (get_user_profile 결과)
            experience_level: 직접 전달 시 사용
            learning_goal: 직접 전달 시 사용
            strong_algorithms: 이미 잘하는 알고리즘 목록
            preferred_difficulty: 선호 난이도

        Returns:
            RecommendationResult (기존 형식)
        """
        # profile이 있으면 그 값 사용
        if profile and profile.success:
            exp_level = profile.experience_level or experience_level or "unknown"
            goal = profile.learning_goal or learning_goal or "unknown"
            strong = profile.strong_algorithms or strong_algorithms or []
            pref_diff = profile.preferred_difficulty or preferred_difficulty
        else:
            exp_level = experience_level or "unknown"
            goal = learning_goal or "unknown"
            strong = strong_algorithms or []
            pref_diff = preferred_difficulty

        # 난이도 결정
        if pref_diff and pref_diff in DIFFICULTY_DISPLAY:
            recommended_difficulty = pref_diff
        else:
            level_config = LEVEL_TO_DIFFICULTY.get(exp_level, LEVEL_TO_DIFFICULTY["unknown"])
            recommended_difficulty = level_config["recommended"]

        # 주제 결정
        strong_lower = [s.lower() for s in strong]

        if goal == "big_tech":
            base_topics = [a["tag"] for a in BIG_TECH_TOP_ALGORITHMS]
        elif goal == "mid_startup":
            base_topics = STARTUP_ALGORITHMS
        else:
            base_topics = SKILL_UP_ALGORITHMS

        topic_options = [t for t in base_topics if t.lower() not in strong_lower][:6]
        recommended_topic = topic_options[0] if topic_options else "기초"

        # 난이도 옵션
        level_config = LEVEL_TO_DIFFICULTY.get(exp_level, LEVEL_TO_DIFFICULTY["unknown"])
        difficulty_options = level_config["range"]

        # 개인화 이유
        reasons = []
        level_names = {"beginner": "입문자", "elementary": "초급자",
                       "intermediate": "중급자", "advanced": "고급자"}
        if exp_level in level_names:
            reasons.append(f"{level_names[exp_level]}에게 적합한")

        goal_names = {"big_tech": "대기업 코테에 자주 나오는",
                      "mid_startup": "실무에서 활용도 높은",
                      "skill_up": "기본기를 다지는"}
        if goal in goal_names:
            reasons.append(goal_names[goal])

        personalization_reason = " ".join(reasons) if reasons else "추천"

        # 사용자 요약
        summary_parts = []
        if exp_level in level_names:
            summary_parts.append(level_names[exp_level])
        if goal in goal_names:
            goal_short = {"big_tech": "대기업 목표", "mid_startup": "스타트업 목표", "skill_up": "실력향상"}
            summary_parts.append(goal_short.get(goal, ""))
        if strong:
            summary_parts.append(f"{'/'.join(strong[:2])} 잘함")

        user_summary = " | ".join(summary_parts) if summary_parts else "프로필 미설정"

        return RecommendationResult(
            recommended_topic=recommended_topic,
            recommended_difficulty=recommended_difficulty,
            recommended_difficulty_display=DIFFICULTY_DISPLAY.get(recommended_difficulty, {}).get("display", "실버"),
            topic_options=topic_options,
            difficulty_options=difficulty_options,
            personalization_reason=personalization_reason,
            user_summary=user_summary,
        )

    # ============================================================
    # 내부 헬퍼: DB 태그 분포 조회
    # ============================================================

    async def _get_tag_distribution(self) -> Dict[str, int]:
        """
        base_problems 테이블에서 정규화된 태그 분포 조회 (캐싱)

        Returns:
            {"DP": 150, "BFS/DFS": 120, ...} (정규화된 태그명)
        """
        import time

        # 캐시 유효시간: 1시간
        if self._tag_cache and (time.time() - self._cache_timestamp < 3600):
            return self._tag_cache

        try:
            # base_problems에서 tags 컬럼 조회
            result = self.supabase.table("base_problems") \
                .select("tags") \
                .execute()

            if not result.data:
                logger.warning("[UserTools] No data in base_problems")
                return {}

            # 정규화된 태그 카운트
            tag_counter: Counter = Counter()
            for row in result.data:
                tags = row.get("tags", [])
                if tags:
                    for tag in tags:
                        # 정규화 적용
                        normalized = self._normalize_tag(tag)
                        if normalized:
                            tag_counter[normalized] += 1

            self._tag_cache = dict(tag_counter.most_common(50))
            self._cache_timestamp = time.time()

            # 사용 가능한 태그도 캐시
            self._available_tags_cache = set(self._tag_cache.keys())

            logger.info(f"[UserTools] Tag distribution cached: {len(self._tag_cache)} normalized tags")
            return self._tag_cache

        except Exception as e:
            logger.error(f"[UserTools] Failed to get tag distribution: {e}")
            return {}

    # ============================================================
    # Tool 5: 전체 주제 목록 조회 (정적 파일 기반)
    # ============================================================

    def get_all_topics(
        self,
        category: Optional[str] = None,
        level: Optional[str] = None,
        include_counts: bool = True,
    ) -> Dict[str, Any]:
        """
        문제집에 있는 모든 주제 목록을 반환합니다.

        Tool 설명 (LLM용):
        - "문제집에 있는 주제 다 알려줘" 같은 요청 시 호출
        - 카테고리별, 난이도별 필터링 가능
        - 각 주제별 문제 수 포함

        Args:
            category: 카테고리 필터 (자료구조, 알고리즘, 수학, 기타)
            level: 난이도 레벨 필터 (beginner, elementary, intermediate, advanced)
            include_counts: 문제 수 포함 여부

        Returns:
            {
                "success": True,
                "total_topics": 32,
                "total_problems": 1897,
                "topics": ["수학", "자료구조", ...],
                "by_category": {...},  # category 필터 없을 때
                "by_level": {...},  # level 필터 있을 때
                "topic_details": [{name, problem_count}, ...]
            }
        """
        try:
            # 정적 JSON 파일 로드
            taxonomy_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "data",
                "topic_taxonomy.json"
            )

            if not os.path.exists(taxonomy_path):
                logger.warning(f"[UserTools] Topic taxonomy file not found: {taxonomy_path}")
                return {
                    "success": False,
                    "error": "주제 데이터 파일이 없습니다. 관리자에게 문의해주세요.",
                    "topics": [],
                }

            with open(taxonomy_path, "r", encoding="utf-8") as f:
                taxonomy = json.load(f)

            result = {
                "success": True,
                "total_topics": taxonomy.get("_total_topics", 0),
                "total_problems": taxonomy.get("_total_problems", 0),
            }

            # 카테고리 필터
            if category:
                by_category = taxonomy.get("by_category", {})
                if category in by_category:
                    topics_in_category = by_category[category]
                    result["topics"] = [t["name"] for t in topics_in_category]
                    result["category"] = category
                    if include_counts:
                        result["topic_details"] = topics_in_category
                else:
                    result["topics"] = []
                    result["error"] = f"'{category}' 카테고리를 찾을 수 없습니다. 가능한 카테고리: {list(by_category.keys())}"
            # 레벨 필터
            elif level:
                by_level = taxonomy.get("by_level", {})
                if level in by_level:
                    result["topics"] = by_level[level]
                    result["level"] = level
                    result["recommendation_reason"] = f"{level} 레벨에 적합한 주제입니다."
                else:
                    result["topics"] = []
                    result["error"] = f"'{level}' 레벨을 찾을 수 없습니다."
            # 전체 조회
            else:
                result["topics"] = taxonomy.get("topic_names", [])
                result["by_category"] = {
                    cat: [t["name"] for t in topics]
                    for cat, topics in taxonomy.get("by_category", {}).items()
                }
                if include_counts:
                    result["topic_details"] = taxonomy.get("all_topics", [])

            logger.info(f"[UserTools] get_all_topics: {len(result.get('topics', []))} topics returned")
            return result

        except Exception as e:
            logger.error(f"[UserTools] Failed to get all topics: {e}")
            return {
                "success": False,
                "error": str(e),
                "topics": [],
            }

    # ============================================================
    # Tool 6: 풀이 이력 기반 개인화 추천
    # ============================================================

    async def get_history_based_recommendation(
        self,
        user_id: str,
        rejected_topics: List[str] = None,
    ) -> Dict[str, Any]:
        """
        사용자 풀이 이력을 기반으로 다음 주제를 추천합니다.

        핵심 로직:
        1. base_problems 테이블에서 실제 존재하는 태그 목록 조회 (정규화됨)
        2. 사용자가 풀어본 문제의 태그 조회 (attempts + base_problems 조인)
        3. 안 풀어본 태그 중에서:
           - 연관 태그 우선 추천 (TOPIC_RELATIONS 기반)
           - 거절 시 비연관 태그 랜덤 추천

        Args:
            user_id: 사용자 UUID
            rejected_topics: 거절된 주제 목록 (제외)

        Returns:
            {
                "success": True,
                "recommended_topic": "그래프",
                "recommendation_type": "related" | "unrelated" | "default",
                "reason": "BFS/DFS를 잘 푸셨네요! 연관된 그래프 문제에 도전해보세요.",
                "solved_tags": [...],  # 사용자가 푼 태그들
                "unsolved_tags": [...],  # 안 푼 태그들
                "alternative_topics": ["백트래킹", "최단경로"],  # 대안 추천
            }
        """
        import random

        # 거절된 주제 정규화
        rejected = set()
        for t in (rejected_topics or []):
            norm = self._normalize_tag(t)
            if norm:
                rejected.add(norm.lower())

        try:
            # 1. DB에서 사용 가능한 태그 목록 조회 (정규화됨)
            available_tags = await self._get_available_tags_from_db()
            if not available_tags:
                logger.warning("[UserTools] No tags available in DB")
                return await self._get_default_recommendation_async(rejected)

            # 2. 사용자가 풀어본 태그 조회
            solved_tags = await self._get_user_solved_tags(user_id)

            # 3. 안 풀어본 태그 계산
            unsolved_tags = available_tags - solved_tags

            # 거절된 태그 제외
            unsolved_tags = {t for t in unsolved_tags if t.lower() not in rejected}

            logger.info(
                f"[UserTools] User {user_id[:8]}... - "
                f"solved: {len(solved_tags)}, unsolved: {len(unsolved_tags)}, rejected: {len(rejected)}"
            )

            # 풀이 이력이 없으면 기본 추천
            if not solved_tags:
                return await self._get_default_recommendation_async(rejected)

            # 4. 연관 태그 찾기 (풀어본 태그들의 연관 태그)
            related_unsolved = set()
            base_topics_for_related = []

            for solved in solved_tags:
                related = TOPIC_RELATIONS.get(solved, [])
                for r in related:
                    # 정규화된 연관 태그가 DB에 있고, 안 풀어봤으면 추가
                    normalized_r = self._normalize_tag(r)
                    if normalized_r and normalized_r in unsolved_tags:
                        related_unsolved.add(normalized_r)
                        base_topics_for_related.append(solved)

            # 5. 추천 결정
            if related_unsolved:
                # 연관 태그 중 랜덤 선택
                recommended = random.choice(list(related_unsolved))
                # 이 추천의 기반이 된 풀어본 태그 찾기
                base_topic = None
                for solved in solved_tags:
                    if recommended in [self._normalize_tag(r) for r in TOPIC_RELATIONS.get(solved, [])]:
                        base_topic = solved
                        break

                alternatives = [t for t in related_unsolved if t != recommended][:2]

                return {
                    "success": True,
                    "recommended_topic": recommended,
                    "recommendation_type": "related",
                    "reason": f"{base_topic}를 푸셨네요! 연관된 {recommended} 문제에 도전해보세요." if base_topic else f"{recommended} 주제를 추천해요!",
                    "solved_tags": list(solved_tags),
                    "unsolved_tags": list(unsolved_tags),
                    "alternative_topics": alternatives,
                }

            # 6. 연관 태그가 없으면 비연관 태그 랜덤 추천
            if unsolved_tags:
                recommended = random.choice(list(unsolved_tags))
                alternatives = [t for t in unsolved_tags if t != recommended][:2]

                return {
                    "success": True,
                    "recommended_topic": recommended,
                    "recommendation_type": "unrelated",
                    "reason": f"새로운 유형인 {recommended}에 도전해보세요! 다양한 문제를 풀어보면 실력이 늘어요.",
                    "solved_tags": list(solved_tags),
                    "unsolved_tags": list(unsolved_tags),
                    "alternative_topics": alternatives,
                }

            # 7. 모든 태그를 다 풀어봤거나 거절됨 → 가장 적게 푼 태그 추천 (복습)
            # 이 경우는 드물지만 처리
            available_for_review = {t for t in available_tags if t.lower() not in rejected}
            if available_for_review:
                recommended = random.choice(list(available_for_review))
                return {
                    "success": True,
                    "recommended_topic": recommended,
                    "recommendation_type": "review",
                    "reason": f"대단해요! 다양한 주제를 다 풀어보셨네요. {recommended} 복습은 어때요?",
                    "solved_tags": list(solved_tags),
                    "unsolved_tags": [],
                    "alternative_topics": [],
                }

            return await self._get_default_recommendation_async(rejected)

        except Exception as e:
            logger.error(f"[UserTools] Failed to get history-based recommendation: {e}")
            return await self._get_default_recommendation_async(rejected)

    async def _get_default_recommendation_async(self, rejected: set) -> Dict[str, Any]:
        """
        기본 추천 (풀이 이력 없을 때) - DB 태그 기반

        Args:
            rejected: 거절된 정규화 태그 set (소문자)

        Returns:
            추천 결과 dict
        """
        import random

        try:
            # DB에서 사용 가능한 태그 조회
            available_tags = await self._get_available_tags_from_db()

            if available_tags:
                # 거절 태그 제외
                available = [t for t in available_tags if t.lower() not in rejected]

                if available:
                    recommended = random.choice(available)
                    alternatives = [t for t in available if t != recommended][:2]

                    return {
                        "success": True,
                        "recommended_topic": recommended,
                        "recommendation_type": "default",
                        "reason": f"{recommended}부터 시작해볼까요? 다양한 문제가 준비되어 있어요.",
                        "solved_tags": [],
                        "unsolved_tags": list(available),
                        "alternative_topics": alternatives,
                    }

        except Exception as e:
            logger.error(f"[UserTools] Failed to get default recommendation: {e}")

        # DB 조회 실패 시 하드코딩 폴백
        fallback_topics = ["구현", "정렬", "문자열", "수학", "BFS/DFS", "그리디"]
        available = [t for t in fallback_topics if t.lower() not in rejected]

        if not available:
            available = fallback_topics

        recommended = random.choice(available)

        return {
            "success": True,
            "recommended_topic": recommended,
            "recommendation_type": "default",
            "reason": f"{recommended}부터 시작해볼까요? 기초를 다지기 좋은 주제예요.",
            "solved_tags": [],
            "unsolved_tags": [],
            "alternative_topics": [t for t in available if t != recommended][:2],
        }


# ============================================================
# Tool Definitions for LLM (OpenAI Function Calling 형식)
# ============================================================

USER_TOOLS_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "get_user_profile",
            "description": "DB에서 사용자 프로필을 조회합니다. 경험 레벨, 학습 목표, 선호도 등을 가져옵니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "사용자의 UUID"
                    }
                },
                "required": ["user_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_topic_recommendations",
            "description": "학습 목표와 레벨에 따른 주제 추천을 생성합니다. 대기업 코테 빈출 유형, DB 문제 수 분석을 포함합니다. 칩 UI로 사용자가 선택할 수 있는 형태로 반환합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "learning_goal": {
                        "type": "string",
                        "enum": ["big_tech", "mid_startup", "skill_up", "unknown"],
                        "description": "학습 목표"
                    },
                    "experience_level": {
                        "type": "string",
                        "enum": ["beginner", "elementary", "intermediate", "advanced", "unknown"],
                        "description": "경험 레벨"
                    },
                    "strong_algorithms": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "이미 잘하는 알고리즘 목록 (추천에서 제외)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "반환할 추천 개수 (기본 6)"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_difficulty_recommendations",
            "description": "사용자 레벨에 맞는 난이도를 추천합니다. 칩 UI로 사용자가 선택할 수 있는 형태로 반환합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "experience_level": {
                        "type": "string",
                        "enum": ["beginner", "elementary", "intermediate", "advanced", "unknown"],
                        "description": "경험 레벨"
                    },
                    "selected_topic": {
                        "type": "string",
                        "description": "선택된 주제 (메시지 커스텀용)"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_all_topics",
            "description": "문제집에 있는 모든 주제(알고리즘/자료구조) 목록을 조회합니다. '어떤 주제가 있어?', '문제집에 있는 주제 다 알려줘', '알고리즘 목록' 같은 요청 시 사용합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "enum": ["자료구조", "알고리즘", "수학", "기타"],
                        "description": "카테고리 필터 (선택사항)"
                    },
                    "level": {
                        "type": "string",
                        "enum": ["beginner", "elementary", "intermediate", "advanced"],
                        "description": "난이도 레벨 필터 (선택사항)"
                    },
                    "include_counts": {
                        "type": "boolean",
                        "description": "각 주제별 문제 수 포함 여부 (기본 true)"
                    }
                },
                "required": []
            }
        }
    }
]


# 싱글톤 인스턴스
_user_tools = None


def get_user_tools() -> UserTools:
    """UserTools 싱글톤 반환"""
    global _user_tools
    if _user_tools is None:
        _user_tools = UserTools()
    return _user_tools
