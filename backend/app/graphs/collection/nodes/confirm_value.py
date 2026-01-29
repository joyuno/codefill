"""
Confirm Value Node (Unified)

choose_topic, choose_difficulty, choose_language를 하나로 통합
사용자가 직접 값을 선택했을 때 확정하고 다음 단계로 이동
"""
from typing import Dict, Any, List, Optional
from ..state import CollectionState, DIFFICULTY_TO_TIER
from app.services.langsmith_tracker import track_collection_node


# ============================================================
# Tier Question Detection & Answering (LLM 기반)
# ============================================================

# DB값 → 티어명 + 설명
TIER_INFO = {
    "easy": ("실버", "기본 개념 연습"),
    "medium": ("골드", "응용 문제"),
    "medium_hard": ("플래티넘", "심화 응용"),
    "hard": ("다이아", "도전적인 문제"),
    "very_hard": ("마스터", "최상위 난이도"),
}


async def _detect_tier_question_async(message: str, analysis_result=None) -> Optional[str]:
    """
    메시지에서 티어 관련 질문 감지 (LLM 기반)

    Args:
        message: 사용자 메시지
        analysis_result: 이미 분석된 UnifiedAnalysisResult (있으면 재사용)

    Returns:
        티어 설명 문자열 or None
    """
    from app.tools.collection_tools import collection_tool

    # 이미 분석된 결과가 있으면 재사용
    if analysis_result is None:
        analysis_result = await collection_tool.analyze(message)

    # 질문이 아니면 None
    if analysis_result.intent != "question":
        return None

    # question_info에서 티어/난이도 관련 질문인지 확인
    question_info = analysis_result.question_info
    if not question_info:
        return None

    # 난이도 관련 질문인지 확인
    is_tier_question = (
        question_info.question_target == "difficulty" or
        question_info.question_type == "difficulty_inquiry" or
        any(subj in ["실버", "골드", "플래티넘", "다이아", "마스터", "티어", "난이도",
                     "easy", "medium", "hard", "very_hard"]
            for subj in (question_info.question_subjects or []))
    )

    if not is_tier_question:
        return None

    # 특정 난이도 언급 확인
    subjects = [s.lower() for s in (question_info.question_subjects or [])]

    difficulty_map = {
        "실버": "easy", "silver": "easy", "easy": "easy", "쉬움": "easy",
        "골드": "medium", "gold": "medium", "medium": "medium", "보통": "medium",
        "플래티넘": "medium_hard", "platinum": "medium_hard",
        "다이아": "hard", "diamond": "hard", "hard": "hard", "어려움": "hard",
        "마스터": "very_hard", "master": "very_hard",
    }

    for subj in subjects:
        if subj in difficulty_map:
            db_val = difficulty_map[subj]
            tier_name, tier_desc = TIER_INFO.get(db_val, (db_val, ""))
            return f"참고로 {subj}은 **{tier_name}** 티어예요! ({tier_desc})"

    # 특정 값 언급 없으면 전체 티어 설명
    return ("참고로 난이도 티어는 이렇게 돼요:\n"
            "• easy = 실버 (기본 개념)\n"
            "• medium = 골드 (응용)\n"
            "• medium_hard = 플래티넘 (심화)\n"
            "• hard = 다이아 (도전적)\n"
            "• very_hard = 마스터 (최상위)")


# ============================================================
# Shared Chip Definitions
# ============================================================

# 기본 주제 칩 (비로그인 또는 개인화 실패 시 폴백)
DEFAULT_TOPIC_CHIPS: List[Dict[str, str]] = [
    {"label": "구현", "value": "구현", "category": "topic"},
    {"label": "정렬", "value": "정렬", "category": "topic"},
    {"label": "문자열", "value": "문자열", "category": "topic"},
    {"label": "이분탐색", "value": "이분탐색", "category": "topic"},
    {"label": "그리디", "value": "그리디", "category": "topic"},
    {"label": "DP", "value": "DP", "category": "topic"},
]

# 모든 가능한 주제 목록 (개인화 칩 생성 시 사용)
ALL_TOPICS: List[str] = [
    "구현", "정렬", "문자열", "이분탐색", "그리디", "DP",
    "BFS/DFS", "그래프", "백트래킹", "완전탐색", "자료구조",
    "수학", "트리", "최단경로", "투포인터", "해시",
]

# 영어/DB 토픽명 → ALL_TOPICS 한국어 매핑
# user_analysis_reports의 strengths/weaknesses에 저장된 토픽명을 ALL_TOPICS로 변환
TOPIC_NAME_MAPPING: Dict[str, str] = {
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
    "Dynamic\r\n  programming": "DP", "동적계획법": "DP",
    "LIS": "DP", "LCS": "DP", "비트마스킹": "DP", "분할정복": "DP", "CHT": "DP",
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


def normalize_topic(topic: str) -> Optional[str]:
    """
    영어/DB 토픽명을 ALL_TOPICS 한국어로 변환

    Args:
        topic: 원본 토픽명 (영어 또는 한국어)

    Returns:
        ALL_TOPICS에 있는 한국어 토픽명 또는 None
    """
    if not topic:
        return None
    # 이미 ALL_TOPICS에 있으면 그대로 반환
    if topic in ALL_TOPICS:
        return topic
    # 매핑 테이블에서 찾기
    return TOPIC_NAME_MAPPING.get(topic)


# 레거시 호환용
TOPIC_CHIPS = DEFAULT_TOPIC_CHIPS

DIFFICULTY_CHIPS: List[Dict[str, str]] = [
    {"label": "실버", "value": "실버", "category": "difficulty"},
    {"label": "골드", "value": "골드", "category": "difficulty"},
    {"label": "플래티넘", "value": "플래티넘", "category": "difficulty"},
    {"label": "다이아", "value": "다이아", "category": "difficulty"},
    {"label": "마스터", "value": "마스터", "category": "difficulty"},
]

# TODO: Java, C++ 데이터 확보 후 공개 예정
LANGUAGE_CHIPS: List[Dict[str, str]] = [
    {"label": "Python", "value": "python", "category": "language"},
    # {"label": "Java", "value": "java", "category": "language"},
    # {"label": "C++", "value": "cpp", "category": "language"},
]

# Display mappings
LANGUAGE_DISPLAY = {
    "python": "Python",
    # "java": "Java",
    # "cpp": "C++",
}


# ============================================================
# 개인화 주제 칩 생성 함수
# ============================================================

async def get_personalized_topic_chips(
    user_id: Optional[str] = None,
    learning_goal: Optional[str] = None,
    experience_level: Optional[str] = None,
) -> List[Dict[str, str]]:
    """
    사용자 맞춤 주제 칩 생성 (user_analysis_reports 테이블 기반)

    약점 분석을 한 유저만 개인화 칩 제공:
    1. 자주 푸는 주제 1개 (strongTopics에서)
    2. 안 풀어본 주제 1개 (skillByTopic에 없는 것)
    3. 약점분석 점수 낮은 주제 1개 (weaknesses에서)
    4. 랜덤 주제 1개

    약점 분석을 안 한 유저: 기본 6개 칩 반환

    Args:
        user_id: 사용자 UUID (없으면 기본 칩 반환)
        learning_goal: 학습 목표 (미사용)
        experience_level: 경험 레벨 (미사용)

    Returns:
        개인화된 주제 칩 리스트 (4개) 또는 기본 칩 (6개)
    """
    import random
    import logging
    from app.database import get_supabase_client

    logger = logging.getLogger(__name__)

    # 비로그인 사용자는 기본 칩 반환
    if not user_id:
        return DEFAULT_TOPIC_CHIPS

    try:
        supabase = get_supabase_client()

        # user_analysis_reports 테이블에서 가장 최근 리포트 조회

        report_result = supabase.table("user_analysis_reports")\
            .select("skill_snapshot, strengths, weaknesses")\
            .eq("user_id", user_id)\
            .order("created_at", desc=True)\
            .limit(1)\
            .execute()

        if not report_result.data or len(report_result.data) == 0:
            return DEFAULT_TOPIC_CHIPS

        report = report_result.data[0]
        skill_snapshot = report.get("skill_snapshot", {}) or {}
        strengths = report.get("strengths", []) or []
        weaknesses = report.get("weaknesses", []) or []

        # 풀어본 주제 = skill_snapshot에 있는 것 (normalize해서 저장)
        solved_topics_normalized = set()
        for t in skill_snapshot.keys():
            normalized = normalize_topic(t)
            if normalized:
                solved_topics_normalized.add(normalized)
        # 안 풀어본 주제 = ALL_TOPICS - solved_topics (normalized)
        unsolved_topics = set(ALL_TOPICS) - solved_topics_normalized

        chips = []
        used_topics = set()

        # 1. 자주 푸는 주제 (strengths에서 선택, 없으면 skill_snapshot 점수 높은 것)
        if strengths:
            # score 높은 순 정렬
            sorted_strengths = sorted(strengths, key=lambda x: x.get("score", 0), reverse=True)
            for s in sorted_strengths:
                raw_topic = s.get("topic")
                topic = normalize_topic(raw_topic)  # 영어→한국어 매핑
                if topic and topic not in used_topics:
                    chips.append({
                        "label": f"{topic} (자주 풂)",
                        "value": topic,
                        "category": "topic",
                    })
                    used_topics.add(topic)
                    break
        # strengths가 없으면 skill_snapshot에서 점수 높은 것
        if len(chips) == 0 and skill_snapshot:
            sorted_skills = sorted(skill_snapshot.items(), key=lambda x: x[1], reverse=True)
            for raw_topic, score in sorted_skills:
                topic = normalize_topic(raw_topic)  # 영어→한국어 매핑
                if topic and topic not in used_topics:
                    chips.append({
                        "label": f"{topic} (자주 풂)",
                        "value": topic,
                        "category": "topic",
                    })
                    used_topics.add(topic)
                    break

        # 2. 안 풀어본 주제 (새로운 도전)
        available_unsolved = unsolved_topics - used_topics
        if available_unsolved:
            new_topic = random.choice(list(available_unsolved))
            chips.append({
                "label": f"{new_topic} (새로운 도전)",
                "value": new_topic,
                "category": "topic",
            })
            used_topics.add(new_topic)

        # 3. 약점분석 점수 낮은 주제 (weaknesses에서)
        if weaknesses:
            # score 낮은 순 정렬 (약점이므로)
            sorted_weaknesses = sorted(weaknesses, key=lambda x: x.get("score", 100))
            for w in sorted_weaknesses:
                raw_topic = w.get("topic")
                topic = normalize_topic(raw_topic)  # 영어→한국어 매핑
                if topic and topic not in used_topics:
                    chips.append({
                        "label": f"{topic} (약점 보완)",
                        "value": topic,
                        "category": "topic",
                    })
                    used_topics.add(topic)
                    break

        # 4. 랜덤 주제 (미사용된 것 중)
        all_available = set(ALL_TOPICS) - used_topics
        if all_available:
            random_topic = random.choice(list(all_available))
            chips.append({
                "label": random_topic,
                "value": random_topic,
                "category": "topic",
            })
            used_topics.add(random_topic)

        # 최소 4개 보장 (부족하면 미사용 주제로 채움)
        while len(chips) < 4:
            remaining = set(ALL_TOPICS) - used_topics
            if not remaining:
                break
            topic = random.choice(list(remaining))
            chips.append({
                "label": topic,
                "value": topic,
                "category": "topic",
            })
            used_topics.add(topic)

        return chips if chips else DEFAULT_TOPIC_CHIPS

    except Exception as e:
        return DEFAULT_TOPIC_CHIPS


# ============================================================
# Unified Confirm Value Node
# ============================================================

@track_collection_node("confirm_value", tags=["confirm"])
async def confirm_value(state: CollectionState) -> Dict[str, Any]:
    """
    통합 값 확정 노드 (async - LLM 기반 질문 감지)

    현재 단계(current_step)에 따라:
    - 값이 있으면 확정하고 다음 단계로 이동
    - 값이 없으면 해당 단계 질문 표시

    Returns:
        current_step, response_message, chips, (is_complete if done)
    """
    topic = state.get("topic")
    difficulty = state.get("difficulty")
    language = state.get("language")
    current_step = state.get("current_step", "topic")
    message = state.get("message", "")

    # 자동 추천 여부 확인
    auto_recommended = state.get("auto_recommended", False)
    auto_recommended_value = state.get("auto_recommended_value")

    # Fast-path에서 왔으면 LLM 호출 스킵 (칩 클릭 = 질문 아님)
    hybrid_fast_path = state.get("hybrid_fast_path", False)

    # 티어 관련 질문 감지 (LLM 기반) - fast-path가 아닐 때만
    tier_answer = None
    if message and not hybrid_fast_path:
        tier_answer = await _detect_tier_question_async(message)

    # ============================================================
    # Topic Stage
    # ============================================================
    if current_step == "topic":
        if not topic:
            # 개인화 칩 우선 사용 (graph.py에서 생성됨)
            topic_chips = state.get("personalized_topic_chips") or DEFAULT_TOPIC_CHIPS
            return {
                "current_step": "topic",
                "response_message": (
                    "어떤 알고리즘 주제로 연습할까요?\n\n"
                    "원하는 주제를 선택해주세요!"
                ),
                "chips": topic_chips,
            }

        # Topic confirmed → move to difficulty
        # 자동 추천이면 메시지 조정
        if auto_recommended and auto_recommended_value == topic:
            topic_msg = f"제가 추천드리는 **{topic}** 주제로 할게요!"
        else:
            topic_msg = f"{topic} 주제로 할게요."

        return {
            "current_step": "difficulty",
            "response_message": (
                f"{topic_msg}\n\n"
                f"난이도를 선택해주세요!\n"
                f"실버 - 기본 개념 연습\n"
                f"골드 - 응용 문제\n"
                f"플래티넘 - 심화 응용\n"
                f"다이아 - 도전적인 문제\n"
                f"마스터 - 최상위 난이도"
            ),
            "chips": DIFFICULTY_CHIPS,
            "auto_recommended": False,  # 플래그 리셋
        }

    # ============================================================
    # Difficulty Stage
    # ============================================================
    if current_step == "difficulty":
        if not topic:
            return {
                "current_step": "topic",
                "response_message": "먼저 주제를 선택해주세요!",
                "chips": TOPIC_CHIPS,
            }

        if not difficulty:
            return {
                "current_step": "difficulty",
                "response_message": (
                    f"{topic} 주제로 할게요.\n\n"
                    f"난이도를 선택해주세요!\n"
                    f"실버 - 기본 개념 연습\n"
                    f"골드 - 응용 문제\n"
                    f"플래티넘 - 심화 응용\n"
                    f"다이아 - 도전적인 문제\n"
                    f"마스터 - 최상위 난이도"
                ),
                "chips": DIFFICULTY_CHIPS,
            }

        # Difficulty confirmed → move to language
        tier_name = DIFFICULTY_TO_TIER.get(difficulty, difficulty)

        # 자동 추천이면 메시지 조정
        if auto_recommended and auto_recommended_value == difficulty:
            difficulty_msg = f"제가 추천드리는 **{tier_name}** 난이도로 할게요!"
        else:
            difficulty_msg = f"좋아요! {topic} 주제의 {tier_name} 문제로 할게요."

        # 기본 응답
        response = f"{difficulty_msg}\n\n"

        # 티어 관련 질문이 있었으면 답변 추가
        if tier_answer:
            response += f"{tier_answer}\n\n"

        response += "어떤 프로그래밍 언어로 풀어볼까요?"

        return {
            "current_step": "language",
            "response_message": response,
            "chips": LANGUAGE_CHIPS,
            "auto_recommended": False,  # 플래그 리셋
        }

    # ============================================================
    # Language Stage
    # ============================================================
    if current_step == "language":
        if not topic:
            return {
                "current_step": "topic",
                "response_message": "먼저 주제를 선택해주세요!",
                "chips": TOPIC_CHIPS,
            }

        if not difficulty:
            return {
                "current_step": "difficulty",
                "response_message": f"{topic} 주제로 할게요. 난이도를 선택해주세요!",
                "chips": DIFFICULTY_CHIPS,
            }

        if not language:
            tier_name = DIFFICULTY_TO_TIER.get(difficulty, difficulty)

            # 기본 응답
            response = f"{topic} 주제의 {tier_name} 문제로 할게요.\n\n"

            # 티어 관련 질문이 있었으면 답변 추가
            if tier_answer:
                response += f"{tier_answer}\n\n"

            response += "어떤 언어로 풀어볼까요?"

            return {
                "current_step": "language",
                "response_message": response,
                "chips": LANGUAGE_CHIPS,
            }

        # Language confirmed → check if generation_details needed
        tier_name = DIFFICULTY_TO_TIER.get(difficulty, difficulty)
        language_display = LANGUAGE_DISPLAY.get(language.lower(), language)

        # 새 문제 생성 요청이면 generation_details 단계로 이동
        wants_generation = state.get("wants_generation", False)
        generation_details = state.get("generation_details")

        if wants_generation and not generation_details:
            return {
                "current_step": "generation_details",
                "response_message": (
                    f"{language_display}로 할게요!\n\n"
                    f"어떤 스타일의 문제를 원하시나요?\n\n"
                    f"예시:\n"
                    f"• \"카카오 코테 스타일로\"\n"
                    f"• \"실전 면접 같은 문제\"\n"
                    f"• \"입출력 예제 많은 문제\"\n"
                    f"• \"알고리즘 개념 설명 포함된 문제\"\n\n"
                    f"자유롭게 설명해주세요!"
                ),
                "chips": [
                    {"label": "카카오 스타일", "value": "카카오 코테 스타일로", "category": "generation"},
                    {"label": "실전 면접형", "value": "실전 면접 같은 문제", "category": "generation"},
                    {"label": "아무거나", "value": "아무거나 괜찮아요", "category": "generation"},
                ],
            }

        # 자동 추천이면 메시지 조정
        if auto_recommended and auto_recommended_value == language:
            complete_msg = (
                f"제가 추천드리는 **{language_display}**로 할게요!\n\n"
                f"{topic} 주제의 {tier_name} 문제를 {language_display}로 풀어볼게요!\n\n"
                f"문제를 찾고 있어요..."
            )
        else:
            complete_msg = (
                f"좋아요! {topic} 주제의 {tier_name} 문제를 {language_display}로 풀어볼게요!\n\n"
                f"문제를 찾고 있어요..."
            )

        return {
            "current_step": "complete",
            "is_complete": True,
            "response_message": complete_msg,
        }

    # ============================================================
    # Generation Details Stage (선택적 4단계 - 새 문제 생성 요청 시)
    # ============================================================
    if current_step == "generation_details":
        generation_details = state.get("generation_details")
        tier_name = DIFFICULTY_TO_TIER.get(difficulty, difficulty)
        language_display = LANGUAGE_DISPLAY.get(language.lower(), language) if language else "Python"

        if not generation_details:
            return {
                "current_step": "generation_details",
                "response_message": (
                    f"어떤 스타일의 문제를 원하시나요?\n\n"
                    f"자유롭게 설명해주세요! (예: 카카오 스타일, 실전 면접형, 개념 설명 포함 등)"
                ),
                "chips": [
                    {"label": "카카오 스타일", "value": "카카오 코테 스타일로", "category": "generation"},
                    {"label": "실전 면접형", "value": "실전 면접 같은 문제", "category": "generation"},
                    {"label": "아무거나", "value": "아무거나 괜찮아요", "category": "generation"},
                ],
            }

        # Generation details confirmed → complete!
        return {
            "current_step": "complete",
            "is_complete": True,
            "response_message": (
                f"좋아요! {topic} 주제의 {tier_name} 문제를 {language_display}로 생성할게요!\n\n"
                f"요청하신 스타일: **{generation_details}**\n\n"
                f"새로운 문제를 생성 중이에요..."
            ),
        }

    # ============================================================
    # Complete Stage (shouldn't reach here normally)
    # ============================================================
    return {
        "current_step": "complete",
        "is_complete": True,
        "response_message": "모든 정보가 수집되었어요! 문제를 찾고 있어요...",
    }


# ============================================================
# Legacy Compatibility Wrappers (async)
# ============================================================

async def choose_topic(state: CollectionState) -> Dict[str, Any]:
    """Legacy wrapper for confirm_value (topic stage)"""
    return await confirm_value(state)


async def choose_difficulty(state: CollectionState) -> Dict[str, Any]:
    """Legacy wrapper for confirm_value (difficulty stage)"""
    return await confirm_value(state)


async def choose_language(state: CollectionState) -> Dict[str, Any]:
    """Legacy wrapper for confirm_value (language stage)"""
    return await confirm_value(state)
