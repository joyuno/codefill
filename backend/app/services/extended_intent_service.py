"""
Extended Intent Service

AI 코딩 학습 도우미에서 발생하는 다양한 의도를 처리하는 서비스
- 프로그래밍 개념 설명
- 문법/사용법 안내
- 에러/디버깅 가이드
- 학습 조언
- 진도/통계 조회 (DB)
- 서비스 사용법
- 인사/잡담 응답
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass


@dataclass
class ExtendedIntentResponse:
    """확장 의도 응답 결과"""
    message: str
    intent_type: str
    data: Optional[Dict[str, Any]] = None
    chips: Optional[List[Dict[str, str]]] = None
    needs_followup: bool = False  # 추가 대화 필요 여부


# ============================================================
# 프로그래밍 개념 설명 데이터
# ============================================================

CODING_CONCEPTS = {
    # 자료구조
    "재귀": {
        "title": "재귀 (Recursion)",
        "explanation": "함수가 자기 자신을 호출하는 프로그래밍 기법입니다. 큰 문제를 작은 부분 문제로 나눠서 해결할 때 유용해요.",
        "example": "팩토리얼: n! = n * (n-1)! → 자기 자신을 호출",
        "tips": ["종료 조건(base case) 필수!", "스택 오버플로우 주의", "꼬리 재귀 최적화 고려"],
    },
    "빅오": {
        "title": "빅오 표기법 (Big-O Notation)",
        "explanation": "알고리즘의 시간/공간 복잡도를 나타내는 표기법입니다. 입력 크기(n)에 따른 연산 횟수 증가율을 표현해요.",
        "example": "O(1) < O(log n) < O(n) < O(n log n) < O(n²) < O(2ⁿ)",
        "tips": ["상수와 낮은 차수 항은 무시", "최악의 경우를 기준으로 표현", "실제 성능은 상수 요인도 중요"],
    },
    "스택": {
        "title": "스택 (Stack)",
        "explanation": "LIFO(Last In First Out) 구조의 자료구조입니다. 마지막에 넣은 데이터가 먼저 나와요.",
        "example": "브라우저 뒤로가기, 함수 호출 스택, 괄호 검사",
        "tips": ["push: 삽입, pop: 제거", "top으로 맨 위 확인", "언더플로우/오버플로우 주의"],
    },
    "큐": {
        "title": "큐 (Queue)",
        "explanation": "FIFO(First In First Out) 구조의 자료구조입니다. 먼저 넣은 데이터가 먼저 나와요.",
        "example": "프린터 대기열, BFS 탐색, 프로세스 스케줄링",
        "tips": ["enqueue: 삽입, dequeue: 제거", "원형 큐로 공간 효율화", "우선순위 큐는 힙으로 구현"],
    },
    "해시": {
        "title": "해시 테이블 (Hash Table)",
        "explanation": "키-값 쌍을 저장하는 자료구조입니다. 해시 함수로 키를 인덱스로 변환해 O(1) 접근이 가능해요.",
        "example": "딕셔너리(Python dict), 캐시, 데이터베이스 인덱싱",
        "tips": ["충돌 해결: 체이닝, 오픈 어드레싱", "좋은 해시 함수가 성능 좌우", "로드 팩터 관리 중요"],
    },
    "트리": {
        "title": "트리 (Tree)",
        "explanation": "계층적 구조를 가진 비선형 자료구조입니다. 노드와 엣지로 구성되며 루트에서 시작해요.",
        "example": "파일 시스템, DOM, 조직도, 이진 검색 트리",
        "tips": ["루트, 부모, 자식, 리프 노드", "높이와 깊이 구분", "균형 트리로 성능 유지"],
    },
    "그래프": {
        "title": "그래프 (Graph)",
        "explanation": "정점(노드)과 간선(엣지)으로 이루어진 자료구조입니다. 네트워크 구조를 표현할 때 사용해요.",
        "example": "소셜 네트워크, 지도/경로, 의존성 관리",
        "tips": ["방향/무방향 그래프", "인접 행렬 vs 인접 리스트", "BFS/DFS로 탐색"],
    },
    "힙": {
        "title": "힙 (Heap)",
        "explanation": "완전 이진 트리 기반의 자료구조입니다. 최대값/최소값을 O(1)에 찾을 수 있어요.",
        "example": "우선순위 큐, 힙 정렬, 다익스트라 알고리즘",
        "tips": ["최대 힙 vs 최소 힙", "삽입/삭제 O(log n)", "Python: heapq 모듈"],
    },
    # 알고리즘
    "dp": {
        "title": "동적 프로그래밍 (Dynamic Programming)",
        "explanation": "큰 문제를 작은 부분 문제로 나눠서 풀고, 결과를 저장해 재사용하는 기법입니다.",
        "example": "피보나치, 배낭 문제, LCS, 최단 경로",
        "tips": ["점화식 세우기가 핵심", "메모이제이션 vs 타뷸레이션", "상태 정의를 명확히"],
    },
    "그리디": {
        "title": "그리디 알고리즘 (Greedy Algorithm)",
        "explanation": "각 단계에서 당장 최선의 선택을 하는 알고리즘입니다. 항상 최적해를 보장하진 않아요.",
        "example": "거스름돈 문제, 활동 선택, 최소 신장 트리",
        "tips": ["최적 부분 구조 확인", "탐욕 선택 속성 증명 필요", "반례 찾아보기"],
    },
    "이분탐색": {
        "title": "이분 탐색 (Binary Search)",
        "explanation": "정렬된 배열에서 절반씩 범위를 줄여가며 찾는 알고리즘입니다. O(log n) 시간복잡도를 가져요.",
        "example": "숫자 찾기, lower/upper bound, 매개변수 탐색",
        "tips": ["정렬 필수!", "경계값 처리 주의", "탐색 범위 설정이 핵심"],
    },
    "bfs": {
        "title": "BFS (너비 우선 탐색)",
        "explanation": "가까운 노드부터 탐색하는 그래프 탐색 알고리즘입니다. 큐를 사용해요.",
        "example": "최단 경로(가중치 없는), 레벨 순회, 연결 요소",
        "tips": ["방문 체크 필수", "거리 배열로 최단 거리 저장", "0-1 BFS: deque 활용"],
    },
    "dfs": {
        "title": "DFS (깊이 우선 탐색)",
        "explanation": "한 방향으로 끝까지 탐색 후 되돌아오는 그래프 탐색 알고리즘입니다. 스택/재귀를 사용해요.",
        "example": "경로 탐색, 사이클 감지, 위상 정렬, 백트래킹",
        "tips": ["방문 체크 필수", "재귀 깊이 제한 주의", "백트래킹과 함께 자주 사용"],
    },
    "정렬": {
        "title": "정렬 알고리즘",
        "explanation": "데이터를 특정 순서로 배열하는 알고리즘입니다. 다양한 방법과 시간복잡도가 있어요.",
        "example": "퀵정렬 O(n log n), 병합정렬 O(n log n), 버블정렬 O(n²)",
        "tips": ["안정 정렬 vs 불안정 정렬", "in-place vs 추가 공간", "Python: sort(), sorted()"],
    },
    # 프로그래밍 개념
    "객체지향": {
        "title": "객체지향 프로그래밍 (OOP)",
        "explanation": "데이터(속성)와 기능(메서드)를 객체로 묶어 프로그래밍하는 패러다임입니다.",
        "example": "클래스, 상속, 다형성, 캡슐화",
        "tips": ["단일 책임 원칙", "상속보다 합성 고려", "인터페이스로 추상화"],
    },
    "시간복잡도": {
        "title": "시간 복잡도",
        "explanation": "알고리즘이 실행되는 데 걸리는 시간을 입력 크기의 함수로 표현한 것입니다.",
        "example": "반복문 1개: O(n), 중첩 2개: O(n²), 이진탐색: O(log n)",
        "tips": ["최악의 경우 기준", "상수 시간은 무시", "실제 벤치마크도 중요"],
    },
    "공간복잡도": {
        "title": "공간 복잡도",
        "explanation": "알고리즘이 사용하는 메모리 양을 입력 크기의 함수로 표현한 것입니다.",
        "example": "변수 몇 개: O(1), 배열 복사: O(n), 2D 배열: O(n²)",
        "tips": ["입력 공간 vs 보조 공간", "재귀 호출 스택 고려", "메모리 제한 확인"],
    },
}

# ============================================================
# 에러/디버깅 가이드
# ============================================================

ERROR_GUIDES = {
    "indexerror": {
        "title": "IndexError",
        "cause": "리스트/배열의 범위를 벗어난 인덱스에 접근할 때 발생합니다.",
        "solutions": [
            "인덱스 범위 확인: 0 <= index < len(array)",
            "빈 배열 체크: if array: 또는 if len(array) > 0:",
            "오프바이원 에러 주의: for i in range(len(arr)) 사용",
        ],
        "example": "arr = [1, 2, 3]; arr[3]  # IndexError! (0, 1, 2만 유효)",
    },
    "keyerror": {
        "title": "KeyError",
        "cause": "딕셔너리에 존재하지 않는 키로 접근할 때 발생합니다.",
        "solutions": [
            "dict.get(key, default) 사용",
            "if key in dict: 로 존재 확인",
            "defaultdict 사용 고려",
        ],
        "example": "d = {'a': 1}; d['b']  # KeyError!",
    },
    "시간초과": {
        "title": "시간 초과 (Time Limit Exceeded)",
        "cause": "알고리즘이 너무 느려서 제한 시간 내에 완료되지 못할 때 발생합니다.",
        "solutions": [
            "시간복잡도 분석: O(n²) → O(n log n) 개선",
            "불필요한 연산 제거",
            "적절한 자료구조 선택 (dict, set 활용)",
            "입출력 최적화: sys.stdin.readline()",
        ],
        "example": "n=100,000이면 O(n²)=10¹⁰ → 시간 초과!",
    },
    "메모리초과": {
        "title": "메모리 초과 (Memory Limit Exceeded)",
        "cause": "프로그램이 허용된 메모리보다 많은 메모리를 사용할 때 발생합니다.",
        "solutions": [
            "불필요한 배열/리스트 생성 피하기",
            "generator 사용 고려",
            "비트마스킹으로 공간 절약",
            "재귀 깊이 제한: sys.setrecursionlimit()",
        ],
        "example": "n=10⁶ 크기의 2D 배열 → 약 8GB 필요",
    },
    "런타임에러": {
        "title": "런타임 에러 (Runtime Error)",
        "cause": "프로그램 실행 중 예외가 발생할 때 나타납니다.",
        "solutions": [
            "0으로 나누기 체크",
            "재귀 깊이 제한 설정",
            "배열 범위 체크",
            "None 값 접근 주의",
        ],
        "example": "ZeroDivisionError, RecursionError, SegmentationFault",
    },
    "틀렸습니다": {
        "title": "틀렸습니다 (Wrong Answer)",
        "cause": "출력 결과가 예상 답과 다를 때 발생합니다.",
        "solutions": [
            "예제 케이스 다시 확인",
            "엣지 케이스 테스트: 0, 음수, 최대값",
            "출력 형식 확인: 공백, 줄바꿈",
            "오버플로우 체크",
        ],
        "example": "자료형 범위 초과, 반올림 오류, 조건 누락",
    },
}

# ============================================================
# 학습 조언
# ============================================================

LEARNING_ADVICE = {
    "초보자": {
        "title": "코딩 입문자 로드맵",
        "steps": [
            "1️⃣ 기본 문법 익히기 (변수, 조건문, 반복문)",
            "2️⃣ 간단한 문제 풀기 (입출력, 기초 연산)",
            "3️⃣ 자료구조 기초 (배열, 문자열)",
            "4️⃣ 기본 알고리즘 (정렬, 탐색)",
        ],
        "tips": ["하루 1-2문제 꾸준히", "모르면 해설 보고 다시 풀기", "코드 리뷰 받기"],
    },
    "알고리즘": {
        "title": "알고리즘 공부 방법",
        "steps": [
            "1️⃣ 개념 이해 → 2️⃣ 기본 문제 → 3️⃣ 응용 문제 → 4️⃣ 복습",
            "유형별 집중 학습: 한 주제 깊게 파기",
            "시간 제한 두고 풀기 연습",
        ],
        "tips": ["오답노트 작성", "다른 풀이 비교 분석", "시간복잡도 항상 계산"],
    },
    "코딩테스트": {
        "title": "코딩테스트 준비 전략",
        "steps": [
            "1️⃣ 기업별 출제 경향 파악",
            "2️⃣ 자주 나오는 유형 집중 (구현, DP, 그래프)",
            "3️⃣ 모의고사로 실전 연습",
            "4️⃣ 시간 배분 연습",
        ],
        "tips": ["쉬운 문제부터 풀기", "완벽한 풀이보다 부분점수", "엣지케이스 체크 습관화"],
    },
    "취업": {
        "title": "개발자 취업 준비",
        "steps": [
            "1️⃣ CS 기초 (자료구조, 알고리즘, 네트워크, DB)",
            "2️⃣ 프로젝트 경험 쌓기",
            "3️⃣ 코딩테스트 준비",
            "4️⃣ 포트폴리오 정리",
        ],
        "tips": ["GitHub 관리", "기술 블로그 작성", "모의 면접 연습"],
    },
}

# ============================================================
# 서비스 안내
# ============================================================

SERVICE_INFO = {
    "소개": "CodeFill은 AI 기반 코딩 학습 플랫폼입니다. 알고리즘 문제를 풀고, AI 튜터와 대화하며 실력을 키워보세요!",
    "기능": [
        "📚 **문제 풀이**: 다양한 난이도의 알고리즘 문제",
        "💡 **AI 힌트**: 막힐 때 단계별 힌트 제공",
        "🎯 **맞춤 추천**: 실력에 맞는 문제 추천",
        "📊 **학습 통계**: 진도와 성장 확인",
        "🤖 **AI 튜터**: 개념 설명과 코드 리뷰",
    ],
    "레벨업": "문제를 풀면 경험치를 얻고 레벨이 올라가요! 레벨이 높아질수록 더 도전적인 문제에 접근할 수 있어요.",
}

# ============================================================
# 인사/잡담 응답
# ============================================================

GREETING_RESPONSES = {
    "안녕": "안녕하세요! 🙌 오늘도 코딩 열심히 하러 오셨군요!",
    "하이": "하이! 👋 무엇을 도와드릴까요?",
    "고마워": "별말씀을요! 😊 더 궁금한 거 있으면 언제든 물어보세요!",
    "감사": "도움이 됐다니 기뻐요! 💪 화이팅!",
    "바이": "수고하셨어요! 다음에 또 만나요! 👋",
    "심심해": "그럼 문제 하나 풀어볼까요? 🎯 주제 추천해드릴게요!",
    "힘들다": "코딩은 원래 어렵죠... 😅 하지만 하나씩 해결하다 보면 실력이 늘어요! 포기하지 마세요!",
    "화이팅": "화이팅입니다! 💪🔥 오늘도 한 문제씩 정복해봐요!",
    "재밌다": "재밌으시다니 다행이에요! 😄 계속 즐겁게 공부해봐요!",
}


class ExtendedIntentService:
    """확장 의도 처리 서비스"""

    def __init__(self):
        self._openrouter = None

    @property
    def openrouter(self):
        """OpenRouter 서비스 lazy loading"""
        if self._openrouter is None:
            from app.services.openrouter import openrouter_service
            self._openrouter = openrouter_service
        return self._openrouter

    async def handle_intent(
        self,
        intent: str,
        message: str,
        extended_info: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        user_context: Optional[Dict[str, Any]] = None,
    ) -> ExtendedIntentResponse:
        """
        확장 의도 처리 메인 메서드

        Args:
            intent: 분류된 의도
            message: 원본 메시지
            extended_info: 확장 정보 (keywords, category 등)
            user_id: 사용자 ID (DB 조회용)
            user_context: 사용자 컨텍스트

        Returns:
            ExtendedIntentResponse
        """
        extended_info = extended_info or {}
        user_context = user_context or {}

        handlers = {
            "coding_concept": self._handle_coding_concept,
            "syntax_help": self._handle_syntax_help,
            "error_debug": self._handle_error_debug,
            "learning_advice": self._handle_learning_advice,
            "code_review": self._handle_code_review,
            "hint_request": self._handle_hint_request,
            "progress_inquiry": self._handle_progress_inquiry,
            "service_help": self._handle_service_help,
            "account_inquiry": self._handle_account_inquiry,
            "greeting": self._handle_greeting,
            "chitchat": self._handle_chitchat,
        }

        handler = handlers.get(intent)
        if handler:
            return await handler(message, extended_info, user_id, user_context)

        # 알 수 없는 의도 → 일반 응답
        return ExtendedIntentResponse(
            message="무엇을 도와드릴까요? 문제 풀이, 개념 설명, 학습 조언 등을 도와드릴 수 있어요!",
            intent_type="unknown",
            needs_followup=True,
        )

    # ============================================================
    # 개별 핸들러 구현
    # ============================================================

    async def _handle_coding_concept(
        self, message: str, extended_info: dict, user_id: str, user_context: dict
    ) -> ExtendedIntentResponse:
        """프로그래밍 개념 설명"""
        keywords = extended_info.get("keywords", [])

        # 키워드로 내장 개념 찾기
        for keyword in keywords:
            keyword_lower = keyword.lower()
            for concept_key, concept_data in CODING_CONCEPTS.items():
                if concept_key in keyword_lower or keyword_lower in concept_key:
                    response = self._format_concept(concept_data)
                    return ExtendedIntentResponse(
                        message=response,
                        intent_type="coding_concept",
                        data={"concept": concept_key},
                    )

        # 내장 개념에 없으면 LLM으로 설명 생성
        if extended_info.get("needs_search"):
            response = await self._generate_llm_explanation(message, "coding_concept")
        else:
            response = await self._generate_llm_explanation(message, "coding_concept")

        return ExtendedIntentResponse(
            message=response,
            intent_type="coding_concept",
        )

    async def _handle_syntax_help(
        self, message: str, extended_info: dict, user_id: str, user_context: dict
    ) -> ExtendedIntentResponse:
        """언어 문법/사용법 설명"""
        language = extended_info.get("language_context", "python")

        # LLM으로 문법 설명 생성
        response = await self._generate_llm_explanation(
            message, "syntax_help", language_context=language
        )

        return ExtendedIntentResponse(
            message=response,
            intent_type="syntax_help",
            data={"language": language},
        )

    async def _handle_error_debug(
        self, message: str, extended_info: dict, user_id: str, user_context: dict
    ) -> ExtendedIntentResponse:
        """에러/디버깅 가이드"""
        keywords = extended_info.get("keywords", [])
        message_lower = message.lower()

        # 키워드로 에러 가이드 찾기
        for error_key, error_data in ERROR_GUIDES.items():
            if error_key in message_lower or any(error_key in kw.lower() for kw in keywords):
                response = self._format_error_guide(error_data)
                return ExtendedIntentResponse(
                    message=response,
                    intent_type="error_debug",
                    data={"error_type": error_key},
                )

        # 내장 가이드에 없으면 LLM으로 설명
        response = await self._generate_llm_explanation(message, "error_debug")

        return ExtendedIntentResponse(
            message=response,
            intent_type="error_debug",
        )

    async def _handle_learning_advice(
        self, message: str, extended_info: dict, user_id: str, user_context: dict
    ) -> ExtendedIntentResponse:
        """학습 방법/조언"""
        message_lower = message.lower()

        # 키워드로 조언 찾기
        for advice_key, advice_data in LEARNING_ADVICE.items():
            if advice_key in message_lower:
                response = self._format_learning_advice(advice_data)
                return ExtendedIntentResponse(
                    message=response,
                    intent_type="learning_advice",
                    data={"advice_type": advice_key},
                )

        # 기본 학습 조언
        experience_level = user_context.get("experience_level", "beginner")
        if experience_level in ["beginner", "elementary"]:
            advice_data = LEARNING_ADVICE.get("초보자", LEARNING_ADVICE["알고리즘"])
        else:
            advice_data = LEARNING_ADVICE.get("알고리즘")

        response = self._format_learning_advice(advice_data)

        return ExtendedIntentResponse(
            message=response,
            intent_type="learning_advice",
        )

    async def _handle_code_review(
        self, message: str, extended_info: dict, user_id: str, user_context: dict
    ) -> ExtendedIntentResponse:
        """코드 리뷰 요청"""
        # 코드가 포함되어 있는지 확인
        has_code = "```" in message or "def " in message or "function" in message

        if has_code:
            response = await self._generate_llm_explanation(message, "code_review")
        else:
            response = (
                "코드 리뷰를 해드릴게요! 🔍\n\n"
                "리뷰받고 싶은 코드를 공유해주세요. 다음을 확인해드릴게요:\n"
                "• 효율성 개선점\n"
                "• 가독성 향상 방법\n"
                "• 잠재적 버그\n"
                "• 더 나은 접근법"
            )

        return ExtendedIntentResponse(
            message=response,
            intent_type="code_review",
            needs_followup=not has_code,
        )

    async def _handle_hint_request(
        self, message: str, extended_info: dict, user_id: str, user_context: dict
    ) -> ExtendedIntentResponse:
        """힌트 요청"""
        # 현재 풀고 있는 문제가 있는지 확인
        current_problem = user_context.get("current_problem")

        if current_problem:
            # 기존 hint_service 활용
            response = (
                f"현재 풀고 있는 문제에 대한 힌트를 드릴게요! 💡\n\n"
                f"어떤 부분에서 막히셨나요?\n"
                f"• 문제 이해\n"
                f"• 접근 방법\n"
                f"• 구현 방법"
            )
        else:
            response = (
                "힌트를 드리고 싶은데, 현재 풀고 있는 문제가 없는 것 같아요! 🤔\n\n"
                "문제를 선택하고 풀기 시작하면 힌트를 드릴 수 있어요.\n"
                "문제 추천을 원하시면 말씀해주세요!"
            )

        return ExtendedIntentResponse(
            message=response,
            intent_type="hint_request",
            needs_followup=True,
        )

    async def _handle_progress_inquiry(
        self, message: str, extended_info: dict, user_id: str, user_context: dict
    ) -> ExtendedIntentResponse:
        """진도/통계 조회"""
        if not user_id:
            return ExtendedIntentResponse(
                message="로그인하시면 학습 통계를 확인할 수 있어요! 📊",
                intent_type="progress_inquiry",
            )

        # DB에서 사용자 통계 조회
        try:
            stats = await self._fetch_user_stats(user_id)
            response = self._format_user_stats(stats)
        except Exception as e:
            print(f"[ExtendedIntentService] Stats fetch error: {e}")
            response = "통계를 불러오는 중 문제가 발생했어요. 잠시 후 다시 시도해주세요!"

        return ExtendedIntentResponse(
            message=response,
            intent_type="progress_inquiry",
            data=stats if 'stats' in dir() else None,
        )

    async def _handle_service_help(
        self, message: str, extended_info: dict, user_id: str, user_context: dict
    ) -> ExtendedIntentResponse:
        """서비스 사용법"""
        response = f"**{SERVICE_INFO['소개']}**\n\n"
        response += "**주요 기능:**\n"
        response += "\n".join(SERVICE_INFO["기능"])
        response += f"\n\n**레벨 시스템:** {SERVICE_INFO['레벨업']}"

        return ExtendedIntentResponse(
            message=response,
            intent_type="service_help",
        )

    async def _handle_account_inquiry(
        self, message: str, extended_info: dict, user_id: str, user_context: dict
    ) -> ExtendedIntentResponse:
        """계정/프로필 관련"""
        if not user_id:
            return ExtendedIntentResponse(
                message="로그인하시면 프로필과 설정을 확인할 수 있어요! 👤",
                intent_type="account_inquiry",
            )

        # 프로필 정보 조회
        try:
            profile = await self._fetch_user_profile(user_id)
            response = self._format_user_profile(profile, user_context)
        except Exception as e:
            print(f"[ExtendedIntentService] Profile fetch error: {e}")
            response = "프로필을 불러오는 중 문제가 발생했어요. 잠시 후 다시 시도해주세요!"

        return ExtendedIntentResponse(
            message=response,
            intent_type="account_inquiry",
        )

    async def _handle_greeting(
        self, message: str, extended_info: dict, user_id: str, user_context: dict
    ) -> ExtendedIntentResponse:
        """인사 응답"""
        message_lower = message.lower()

        for keyword, response in GREETING_RESPONSES.items():
            if keyword in message_lower:
                return ExtendedIntentResponse(
                    message=response,
                    intent_type="greeting",
                )

        # 기본 인사
        return ExtendedIntentResponse(
            message="안녕하세요! 😊 코딩 학습을 도와드릴게요. 무엇을 도와드릴까요?",
            intent_type="greeting",
            needs_followup=True,
        )

    async def _handle_chitchat(
        self, message: str, extended_info: dict, user_id: str, user_context: dict
    ) -> ExtendedIntentResponse:
        """잡담 응답"""
        message_lower = message.lower()

        for keyword, response in GREETING_RESPONSES.items():
            if keyword in message_lower:
                return ExtendedIntentResponse(
                    message=response,
                    intent_type="chitchat",
                )

        # 코딩 학습으로 자연스럽게 유도
        return ExtendedIntentResponse(
            message="ㅎㅎ 그렇군요! 😄 그럼 다시 코딩으로 돌아가볼까요? 어떤 주제로 연습해볼까요?",
            intent_type="chitchat",
            needs_followup=True,
        )

    # ============================================================
    # 헬퍼 메서드
    # ============================================================

    def _format_concept(self, concept_data: dict) -> str:
        """개념 데이터 포맷팅"""
        response = f"**{concept_data['title']}**\n\n"
        response += f"📖 {concept_data['explanation']}\n\n"
        response += f"💡 **예시:** {concept_data['example']}\n\n"
        response += "✅ **팁:**\n"
        for tip in concept_data["tips"]:
            response += f"  • {tip}\n"
        return response

    def _format_error_guide(self, error_data: dict) -> str:
        """에러 가이드 포맷팅"""
        response = f"**{error_data['title']}**\n\n"
        response += f"❓ **원인:** {error_data['cause']}\n\n"
        response += "✅ **해결 방법:**\n"
        for solution in error_data["solutions"]:
            response += f"  • {solution}\n"
        response += f"\n💡 **예시:** `{error_data['example']}`"
        return response

    def _format_learning_advice(self, advice_data: dict) -> str:
        """학습 조언 포맷팅"""
        response = f"**{advice_data['title']}**\n\n"
        response += "📌 **단계:**\n"
        for step in advice_data["steps"]:
            response += f"  {step}\n"
        response += "\n💡 **팁:**\n"
        for tip in advice_data["tips"]:
            response += f"  • {tip}\n"
        return response

    async def _generate_llm_explanation(
        self, message: str, intent_type: str, language_context: str = None
    ) -> str:
        """LLM으로 설명 생성"""
        try:
            system_prompts = {
                "coding_concept": "프로그래밍 개념을 쉽고 친근하게 설명해주세요. 예시와 함께 설명하세요.",
                "syntax_help": f"프로그래밍 문법/사용법을 설명해주세요. 언어: {language_context or 'Python'}. 코드 예시를 포함하세요.",
                "error_debug": "에러 해결 방법을 단계별로 설명해주세요. 원인과 해결책을 명확히 제시하세요.",
                "code_review": "코드를 리뷰하고 개선점을 제안해주세요. 효율성, 가독성, 버그 가능성을 확인하세요.",
            }

            system_prompt = system_prompts.get(
                intent_type,
                "친근하고 도움이 되는 답변을 해주세요. 코딩 학습 도우미입니다."
            )

            response = await self.openrouter.chat_completion(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                temperature=0.7,
                max_tokens=500,
            )

            return self.openrouter.get_content(response)

        except Exception as e:
            print(f"[ExtendedIntentService] LLM error: {e}")
            return "죄송해요, 답변을 생성하는 중 문제가 발생했어요. 다시 질문해주세요!"

    async def _fetch_user_stats(self, user_id: str) -> dict:
        """DB에서 사용자 통계 조회"""
        from app.core.supabase import get_supabase_client

        client = get_supabase_client()

        # 푼 문제 수 조회
        solved_response = client.table("user_problem_attempts").select(
            "id", count="exact"
        ).eq("user_id", user_id).eq("is_correct", True).execute()

        # 프로필 조회
        profile_response = client.table("profiles").select(
            "level", "xp", "problems_solved"
        ).eq("id", user_id).single().execute()

        profile = profile_response.data or {}

        return {
            "solved_count": profile.get("problems_solved", 0),
            "level": profile.get("level", 1),
            "xp": profile.get("xp", 0),
        }

    def _format_user_stats(self, stats: dict) -> str:
        """사용자 통계 포맷팅"""
        return (
            f"📊 **학습 통계**\n\n"
            f"🎯 푼 문제: **{stats.get('solved_count', 0)}개**\n"
            f"⭐ 레벨: **{stats.get('level', 1)}**\n"
            f"✨ 경험치: **{stats.get('xp', 0)} XP**\n\n"
            f"계속해서 문제를 풀면 레벨업할 수 있어요! 💪"
        )

    async def _fetch_user_profile(self, user_id: str) -> dict:
        """DB에서 사용자 프로필 조회"""
        from app.core.supabase import get_supabase_client

        client = get_supabase_client()

        response = client.table("profiles").select("*").eq("id", user_id).single().execute()

        return response.data or {}

    def _format_user_profile(self, profile: dict, user_context: dict) -> str:
        """사용자 프로필 포맷팅"""
        level_names = {
            "beginner": "입문자",
            "elementary": "초급자",
            "intermediate": "중급자",
            "advanced": "고급자",
        }

        experience = profile.get("experience_level") or user_context.get("experience_level", "unknown")
        level_name = level_names.get(experience, experience)

        return (
            f"👤 **내 프로필**\n\n"
            f"📊 레벨: **{profile.get('level', 1)}**\n"
            f"🎓 경험 수준: **{level_name}**\n"
            f"🎯 푼 문제: **{profile.get('problems_solved', 0)}개**\n"
            f"✨ 경험치: **{profile.get('xp', 0)} XP**\n"
        )


# 싱글톤 인스턴스
extended_intent_service = ExtendedIntentService()
