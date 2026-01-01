"""
User Tools - 사용자 프로필 조회 및 DB 기반 개인화 추천

핵심 Tool:
1. get_user_profile: DB에서 사용자 프로필 조회
2. get_topic_recommendations: DB 태그 분석 기반 주제 추천 (칩 UI 포함)
3. get_difficulty_recommendations: 사용자 레벨 기반 난이도 추천 (칩 UI 포함)

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

from ..database import get_supabase_client

logger = logging.getLogger(__name__)


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
        self._cache_timestamp: float = 0

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

            # user_preferences 테이블에서 선호도 조회
            pref_result = self.supabase.table("user_preferences") \
                .select("preferred_language, preferred_difficulty") \
                .eq("user_id", user_id) \
                .limit(1) \
                .execute()

            pref_data = pref_result.data[0] if pref_result.data else {}

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
        base_problems 테이블에서 태그 분포 조회 (캐싱)

        Returns:
            {"DP": 150, "그래프": 120, ...}
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

            # 태그 카운트
            tag_counter: Counter = Counter()
            for row in result.data:
                tags = row.get("tags", [])
                if tags:
                    for tag in tags:
                        if tag:
                            tag_counter[tag] += 1

            self._tag_cache = dict(tag_counter.most_common(50))
            self._cache_timestamp = time.time()

            logger.info(f"[UserTools] Tag distribution cached: {len(self._tag_cache)} tags")
            return self._tag_cache

        except Exception as e:
            logger.error(f"[UserTools] Failed to get tag distribution: {e}")
            return {}


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
