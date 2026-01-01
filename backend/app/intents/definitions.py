"""
CodeFill Intent Definitions
모든 사용자 의도 정의 및 예시 문장

각 의도별 10-15개의 다양한 표현을 포함하여
임베딩 유사도 검색의 정확도를 높입니다.
"""

from enum import Enum
from typing import Dict, List


class IntentType(str, Enum):
    """사용자 의도 유형"""

    # ===== 문제 검색/추천 =====
    NEW_PROBLEM = "new_problem"                    # 새로운 문제 요청
    SIMILAR_CODE_PROBLEM = "similar_code_problem"  # 비슷한 코드/패턴 문제
    TOPIC_SPECIFIC = "topic_specific"              # 특정 주제 문제
    DIFFICULTY_CHANGE = "difficulty_change"        # 난이도 변경
    LANGUAGE_CHANGE = "language_change"            # 언어 변경
    RANDOM_RECOMMEND = "random_recommend"          # 아무거나 추천
    MORE_SEARCH = "more_search"                    # 추가 검색 (다음 5개)
    GENERATE_NEW = "generate_new"                  # 새 문제 생성 (CodeGen)

    # ===== 문제 풀이 중 =====
    HINT_REQUEST = "hint_request"                  # 힌트 요청
    SOLUTION_REQUEST = "solution_request"          # 정답/풀이 요청
    EXPLANATION_REQUEST = "explanation_request"    # 설명 요청
    CODE_REVIEW = "code_review"                    # 코드 리뷰 요청
    ERROR_HELP = "error_help"                      # 에러 도움 요청

    # ===== 문제 선택 =====
    PROBLEM_SELECTION = "problem_selection"        # 문제 선택 (리스트에서 선택)

    # ===== 진행 관련 =====
    SKIP_PROBLEM = "skip_problem"                  # 문제 건너뛰기
    RETRY_PROBLEM = "retry_problem"                # 다시 풀기
    SUBMIT_CODE = "submit_code"                    # 코드 제출

    # ===== 학습/통계 =====
    PROGRESS_CHECK = "progress_check"              # 진행상황 확인
    WEAK_POINT = "weak_point"                      # 약점 분석
    STUDY_PLAN = "study_plan"                      # 학습 계획

    # ===== 일반 대화 =====
    GREETING = "greeting"                          # 인사
    THANKS = "thanks"                              # 감사
    GOODBYE = "goodbye"                            # 종료
    CONFUSION = "confusion"                        # 모르겠다/헷갈린다
    AFFIRMATION = "affirmation"                    # 긍정 응답 (응, 좋아, 그래)
    NEGATION = "negation"                          # 부정 응답 (아니, 싫어, 다른거)

    # ===== 시스템 =====
    OUT_OF_SCOPE = "out_of_scope"                  # 범위 밖 요청
    CLARIFICATION_NEEDED = "clarification_needed"  # 명확화 필요


# ===== 의도별 예시 문장 =====
# 각 의도당 다양한 표현 10-15개 포함

INTENT_DEFINITIONS: Dict[str, Dict] = {

    # ============================================================
    # 문제 검색/추천
    # ============================================================

    IntentType.NEW_PROBLEM: {
        "description": "새로운 문제 요청",
        "examples": [
            "새로운 문제 풀고 싶어",
            "다른 문제 줘",
            "새 문제 추천해줘",
            "문제 하나 더",
            "다음 문제",
            "다른 거 할래",
            "이거 말고 다른 문제",
            "완전히 새로운 거",
            "안 풀어본 문제",
            "처음 보는 문제 줘",
            "다른 유형 문제",
            "새로운 도전",
            "다른 거 풀어볼래",
            # 추가: 목적/동기 표현
            "코테 준비 중인데",
            "코딩테스트 준비하려고",
            "면접 준비 중이야",
            "알고리즘 공부하려고",
            "문제 풀고 싶어",
            "연습하고 싶어",
            "실력 늘리고 싶어",
            "뭐 풀지",
            "심심한데 문제나 풀까",
            "심심해 문제 줘",
        ],
        "required_context": None,
        "next_action": "collect_preferences",
    },

    IntentType.SIMILAR_CODE_PROBLEM: {
        "description": "비슷한 코드/패턴 문제 요청",
        "examples": [
            # 명시적 요청
            "비슷한 코드 문제 찾아줘",
            "유사한 문제 더 없어?",
            "이 코드랑 비슷한 문제",
            "같은 패턴의 문제",
            "비슷한 유형 더 풀고 싶어",
            "이런 식의 문제 더",
            "유사한 알고리즘 문제",

            # 암묵적 참조
            "방금 푼 거랑 비슷한 거",
            "아까 풀었던 것처럼",
            "이것처럼 더 없어?",
            "이런 거 더 풀래",
            "같은 거 더",
            "비슷한 거 더 줘",
            "이런 유형 더 연습하고 싶어",

            # 특정 문제 참조
            "피보나치 문제랑 비슷한 거",
            "투포인터 문제 더 없어?",
            "방금 그 DP 문제 비슷한 거",
        ],
        "required_context": "code",  # 코드 컨텍스트 필요
        "next_action": "code_similarity_search",
    },

    IntentType.TOPIC_SPECIFIC: {
        "description": "특정 주제/알고리즘 문제 요청",
        "examples": [
            # === 단순 키워드 (단답 입력) ===
            "DP",
            "dp",
            "그래프",
            "정렬",
            "탐색",
            "BFS",
            "DFS",
            "그리디",
            "구현",
            "문자열",
            "이분탐색",
            "백트래킹",
            "다이나믹",
            "동적프로그래밍",
            "스택",
            "큐",
            "트리",
            "해시",

            # === 문장형 요청 ===
            # DP
            "DP 문제 풀래",
            "동적 프로그래밍 연습하고 싶어",
            "디피 문제 줘",
            "DP로 할래",
            "DP 할래",

            # 그래프
            "그래프 문제 풀고 싶어",
            "BFS 연습할래",
            "DFS 문제 있어?",
            "최단경로 문제",
            "그래프로 할게",

            # 정렬/탐색
            "정렬 알고리즘 문제",
            "이진탐색 연습",
            "투포인터 문제",
            "정렬로 할래",

            # 자료구조
            "스택 문제 풀래",
            "큐 문제 있어?",
            "해시 문제",
            "트리 문제 풀고 싶어",

            # 기타
            "백트래킹 연습",
            "그리디 문제",
            "분할정복 문제",
            "문자열 처리 문제",
            "구현 문제 풀래",
            "시뮬레이션 문제",
        ],
        "required_context": None,
        "next_action": "set_topic_and_continue",
    },

    IntentType.DIFFICULTY_CHANGE: {
        "description": "난이도 변경 요청",
        "examples": [
            # === 단순 키워드 (단답 입력) ===
            "실버",
            "골드",
            "플래티넘",
            "다이아",
            "마스터",
            "쉬움",
            "중간",
            "어려움",
            "easy",
            "medium",
            "hard",

            # === 문장형 요청 ===
            # 쉽게
            "더 쉬운 거",
            "쉬운 문제로",
            "난이도 낮춰줘",
            "이건 너무 어려워",
            "초급으로 해줘",
            "기초 문제",
            "실버로 할래",
            "골드로 해줘",

            # 어렵게
            "더 어려운 거",
            "어려운 문제로",
            "난이도 높여줘",
            "이건 너무 쉬워",
            "고급으로 해줘",
            "챌린지 문제",
            "다이아로",
            "플래티넘으로 할게",

            # 중간
            "중간 난이도로",
            "보통으로 해줘",
            "적당한 거",
        ],
        "required_context": None,
        "next_action": "update_difficulty",
    },

    IntentType.LANGUAGE_CHANGE: {
        "description": "프로그래밍 언어 변경",
        "examples": [
            # === 단순 키워드 (단답 입력) ===
            "파이썬",
            "python",
            "Python",
            "자바",
            "java",
            "Java",
            "씨플플",
            "cpp",
            "C++",

            # === 문장형 요청 ===
            "파이썬으로 할래",
            "자바로 바꿔줘",
            "C++로 풀고 싶어",
            "Python으로",
            "Java로 해줘",
            "씨플플로",
            "언어 바꿀래",
            "다른 언어로",
        ],
        "required_context": None,
        "next_action": "update_language",
    },

    IntentType.RANDOM_RECOMMEND: {
        "description": "아무거나 추천 요청 또는 초보자 기본 문제 요청",
        "examples": [
            "아무거나 추천해줘",
            "그냥 아무거나",
            "니가 골라줘",
            "추천해줘",
            "알아서 해줘",
            "뭐든 상관없어",
            "아무 문제나",
            "랜덤으로",
            "마음대로 해줘",
            "네가 정해",
            "골라줘",
            "맡길게",
            # 초보자/기본 요청
            "기본적인거",
            "제일 기본적인거",
            "기초적인거",
            "가장 쉬운거",
            "제일 쉬운거",
            "아무것도 모르는데",
            "하나도 모르는데",
            "초보인데",
            "처음인데",
            "입문자인데",
            "그런거 잘 모르는데",
            "뭔지 모르겠어",
            "그냥 아무거나 기본적인거",
        ],
        "required_context": None,
        "next_action": "recommend_based_on_level",
    },

    IntentType.MORE_SEARCH: {
        "description": "추가 검색 - 다음 5개 문제 요청",
        "examples": [
            # 더 찾아보기
            "더 찾아줘",
            "더 없어?",
            "다른 문제 더 보여줘",
            "비슷한 문제 더 찾아줘",
            "유사한 문제 더",
            "다음 문제들 보여줘",
            "다른 것도 보여줘",
            "더 있어?",
            "몇 개 더",
            "추가로 더",
            "다음 5개",
            "그 다음",
            "다른 거 더 없어?",
            "더 보여줘",
            "목록 더 보여줘",
        ],
        "required_context": "problem_list",
        "next_action": "search_more_problems",
    },

    IntentType.GENERATE_NEW: {
        "description": "새 문제 생성 - CodeGen으로 유사 문제 생성",
        "examples": [
            # 생성 요청
            "새 문제 생성해줘",
            "새로 만들어줘",
            "문제 생성해줘",
            "유사한 문제 생성해줘",
            "비슷한 문제 만들어줘",
            "AI가 만든 문제 풀고 싶어",
            "새로운 문제 만들어줘",
            "생성된 문제 풀래",
            "니가 만든 문제",
            "네가 만든 거 풀래",
            "새로운 유사 문제",
            "만들어준 문제 풀래",
            "생성 문제",
            "커스텀 문제",
            "새로 생성",
        ],
        "required_context": None,
        "next_action": "generate_new_problem",
    },

    # ============================================================
    # 문제 풀이 중
    # ============================================================

    IntentType.HINT_REQUEST: {
        "description": "힌트 요청",
        "examples": [
            "힌트 줘",
            "힌트 좀",
            "도움이 필요해",
            "모르겠어 힌트",
            "어떻게 접근해야 해?",
            "방향을 모르겠어",
            "막혔어",
            "감이 안 와",
            "어디서부터 시작해야 해?",
            "팁 좀 줘",
            "살짝만 알려줘",
            "조금만 도와줘",
            "접근법이 뭐야?",
        ],
        "required_context": "problem",
        "next_action": "provide_hint",
    },

    IntentType.SOLUTION_REQUEST: {
        "description": "정답/풀이 요청",
        "examples": [
            "정답 보여줘",
            "답 알려줘",
            "풀이 보고 싶어",
            "해답 줘",
            "모르겠어 답 줘",
            "포기 정답 보여줘",
            "솔루션 보여줘",
            "코드 답 줘",
            "어떻게 푸는 거야?",
            "정답 코드",
        ],
        "required_context": "problem",
        "next_action": "confirm_show_solution",
    },

    IntentType.EXPLANATION_REQUEST: {
        "description": "개념/코드 설명 요청",
        "examples": [
            "이게 무슨 뜻이야?",
            "설명해줘",
            "이 코드 뭐야?",
            "이 부분 이해가 안 돼",
            "왜 이렇게 하는 거야?",
            "이 알고리즘 설명해줘",
            "DP가 뭐야?",
            "시간복잡도가 뭐야?",
            "이게 왜 되는 거야?",
            "원리가 뭐야?",
            "개념 설명해줘",
        ],
        "required_context": None,
        "next_action": "explain_concept",
    },

    IntentType.CODE_REVIEW: {
        "description": "코드 리뷰 요청",
        "examples": [
            "내 코드 봐줘",
            "코드 리뷰해줘",
            "이거 맞아?",
            "코드 확인해줘",
            "뭐가 잘못됐어?",
            "어디가 틀렸어?",
            "개선할 점 있어?",
            "더 나은 방법 있어?",
            "이렇게 하면 돼?",
            "효율적이야?",
        ],
        "required_context": "code",
        "next_action": "review_code",
    },

    IntentType.ERROR_HELP: {
        "description": "에러/버그 도움 요청",
        "examples": [
            "에러가 나",
            "오류가 있어",
            "버그가 있는 것 같아",
            "왜 안 돼?",
            "실행이 안 돼",
            "틀렸다고 나와",
            "런타임 에러",
            "시간 초과",
            "메모리 초과",
            "컴파일 에러",
            "무한루프 도는 것 같아",
            "결과가 이상해",
        ],
        "required_context": "code",
        "next_action": "debug_code",
    },

    # ============================================================
    # 문제 선택
    # ============================================================

    IntentType.PROBLEM_SELECTION: {
        "description": "문제 리스트에서 특정 문제 선택",
        "examples": [
            # 번호로 선택
            "1번",
            "1번으로 할래",
            "첫번째 문제",
            "두번째 거",
            "2번 할게",
            "3번째 문제로",

            # 이름으로 선택
            "taco_139로 할게",
            "그 문제로 할래",
            "저거 풀래",
            "이거로 할게",
            "그거",
            "첫번째 거로",
            "위에 거",
            "마지막 거",

            # 선택 표현
            "그걸로 할게",
            "그 문제 선택",
            "이 문제 풀래",
            "저 문제로",
            "그거 할래",
            "이걸로",
        ],
        "required_context": "problem_list",
        "next_action": "select_problem_type",
    },

    # ============================================================
    # 진행 관련
    # ============================================================

    IntentType.SKIP_PROBLEM: {
        "description": "문제 건너뛰기",
        "examples": [
            "스킵",
            "건너뛸래",
            "이거 넘어가자",
            "패스",
            "다음 거 할래",
            "이건 나중에",
            "다음에 풀게",
            "못 풀겠어 넘겨",
        ],
        "required_context": "problem",
        "next_action": "skip_and_next",
    },

    IntentType.RETRY_PROBLEM: {
        "description": "다시 풀기",
        "examples": [
            "다시 풀래",
            "처음부터 다시",
            "리셋해줘",
            "다시 시작",
            "한 번 더 할래",
            "재시도",
            "리트라이",
            "초기화해줘",
        ],
        "required_context": "problem",
        "next_action": "reset_problem",
    },

    IntentType.SUBMIT_CODE: {
        "description": "코드 제출",
        "examples": [
            "제출할래",
            "제출",
            "채점해줘",
            "실행해봐",
            "테스트해봐",
            "확인해줘",
            "이거 맞는지 봐줘",
            "돌려봐",
        ],
        "required_context": "code",
        "next_action": "execute_code",
    },

    # ============================================================
    # 학습/통계
    # ============================================================

    IntentType.PROGRESS_CHECK: {
        "description": "진행상황 확인",
        "examples": [
            "내 진행상황",
            "얼마나 풀었어?",
            "통계 보여줘",
            "내 기록",
            "푼 문제 수",
            "성적 보여줘",
            "히스토리",
            "지금까지 뭐 풀었어?",
        ],
        "required_context": None,
        "next_action": "show_progress",
    },

    IntentType.WEAK_POINT: {
        "description": "약점 분석 요청",
        "examples": [
            "내 약점이 뭐야?",
            "뭘 더 공부해야 해?",
            "부족한 부분",
            "취약점 분석",
            "어디가 부족해?",
            "뭘 연습해야 해?",
            "못하는 게 뭐야?",
        ],
        "required_context": None,
        "next_action": "analyze_weakness",
    },

    IntentType.STUDY_PLAN: {
        "description": "학습 계획 요청",
        "examples": [
            "공부 계획 세워줘",
            "어떻게 공부해야 해?",
            "학습 로드맵",
            "추천 커리큘럼",
            "뭐부터 해야 해?",
            "순서대로 알려줘",
            "코테 준비 어떻게?",
        ],
        "required_context": None,
        "next_action": "create_study_plan",
    },

    # ============================================================
    # 일반 대화
    # ============================================================

    IntentType.GREETING: {
        "description": "인사",
        "examples": [
            "안녕",
            "안녕하세요",
            "하이",
            "헬로",
            "반가워",
            "시작하자",
            "왔어",
            "오늘도 힘내자",
        ],
        "required_context": None,
        "next_action": "greet_user",
    },

    IntentType.THANKS: {
        "description": "감사",
        "examples": [
            "고마워",
            "고마워!",
            "고마워요",
            "고마워요!",
            "감사합니다",
            "감사합니다!",
            "감사해요",
            "땡큐",
            "땡큐!",
            "thanks",
            "thank you",
            "도움이 됐어",
            "도움이 됐어!",
            "잘 됐어",
            "완벽해",
            "완벽해!",
            "최고야",
            "최고야!",
            "덕분에 해결했어",
            "이해됐어",
            "알겠어 고마워",
        ],
        "required_context": None,
        "next_action": "acknowledge_thanks",
    },

    IntentType.GOODBYE: {
        "description": "종료/작별",
        "examples": [
            "잘가",
            "바이",
            "나갈게",
            "끝낼래",
            "그만할래",
            "오늘은 여기까지",
            "다음에 또",
            "수고했어",
        ],
        "required_context": None,
        "next_action": "farewell",
    },

    IntentType.CONFUSION: {
        "description": "혼란/모르겠음 - 도움 요청",
        "examples": [
            # 기본 혼란
            "모르겠어",
            "헷갈려",
            "이해가 안 돼",
            "뭔 말이야?",
            "무슨 뜻이야?",
            "잘 모르겠는데",
            "어렵다",
            "복잡해",
            "뭘 해야 하지?",
            # 추가: 도움 요청
            "도와줘",
            "어떻게 해",
            "어떻게 해야 해",
            "뭐가 뭔지 모르겠어",
            "막막해",
            "감이 안 잡혀",
            "뭐부터 해야 돼?",
            "어디서부터 시작해?",
        ],
        "required_context": None,
        "next_action": "clarify_and_help",
    },

    IntentType.AFFIRMATION: {
        "description": "긍정 응답",
        "examples": [
            "응",
            "어",
            "그래",
            "좋아",
            "오케이",
            "ㅇㅋ",
            "그렇게 해",
            "맞아",
            "당연하지",
            "네",
            "예",
            "알겠어",
            "그거",
            "그걸로",
        ],
        "required_context": "previous_suggestion",
        "next_action": "confirm_previous",
    },

    IntentType.NEGATION: {
        "description": "부정 응답",
        "examples": [
            "아니",
            "아니야",
            "싫어",
            "다른 거",
            "그거 말고",
            "패스",
            "노노",
            "별로",
            "안 할래",
            "다시",
            "다른 걸로",
        ],
        "required_context": "previous_suggestion",
        "next_action": "offer_alternatives",
    },

    # ============================================================
    # 시스템
    # ============================================================

    IntentType.OUT_OF_SCOPE: {
        "description": "범위 밖 요청",
        "examples": [
            "날씨 알려줘",
            "맛집 추천해줘",
            "게임하자",
            "노래 틀어줘",
            "뉴스 알려줘",
            "주식 정보",
            "번역해줘",
            "영화 추천",
        ],
        "required_context": None,
        "next_action": "redirect_to_coding",
    },

    IntentType.CLARIFICATION_NEEDED: {
        "description": "명확화 필요 (시스템용)",
        "examples": [],  # 시스템에서 사용
        "required_context": None,
        "next_action": "ask_clarification",
    },
}


# ===== 의도 그룹 (응답 우선순위용) =====

INTENT_GROUPS = {
    "high_priority": [
        IntentType.ERROR_HELP,
        IntentType.HINT_REQUEST,
        IntentType.SUBMIT_CODE,
        IntentType.PROBLEM_SELECTION,  # 문제 선택도 높은 우선순위
    ],
    "problem_search": [
        IntentType.NEW_PROBLEM,
        IntentType.SIMILAR_CODE_PROBLEM,
        IntentType.TOPIC_SPECIFIC,
        IntentType.RANDOM_RECOMMEND,
        IntentType.MORE_SEARCH,
        IntentType.GENERATE_NEW,
    ],
    "modification": [
        IntentType.DIFFICULTY_CHANGE,
        IntentType.LANGUAGE_CHANGE,
    ],
    "learning": [
        IntentType.EXPLANATION_REQUEST,
        IntentType.CODE_REVIEW,
        IntentType.SOLUTION_REQUEST,
    ],
    "conversation": [
        IntentType.GREETING,
        IntentType.THANKS,
        IntentType.GOODBYE,
        IntentType.AFFIRMATION,
        IntentType.NEGATION,
        IntentType.CONFUSION,
    ],
}


# ===== 컨텍스트 요구사항 =====

CONTEXT_REQUIREMENTS = {
    "code": [
        IntentType.SIMILAR_CODE_PROBLEM,
        IntentType.CODE_REVIEW,
        IntentType.ERROR_HELP,
        IntentType.SUBMIT_CODE,
    ],
    "problem": [
        IntentType.HINT_REQUEST,
        IntentType.SOLUTION_REQUEST,
        IntentType.SKIP_PROBLEM,
        IntentType.RETRY_PROBLEM,
    ],
    "previous_suggestion": [
        IntentType.AFFIRMATION,
        IntentType.NEGATION,
    ],
    "problem_list": [
        IntentType.PROBLEM_SELECTION,
    ],
}
