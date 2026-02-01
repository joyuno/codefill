"""
Intent Tools - LLM 기반 통합 의도 분류

모든 의도 분류는 LLM(gemini-flash)이 담당
- 주제/난이도/언어: LLM이 컨텍스트 이해 (부정어, 복합문장 등)
- 긍정/부정 응답: 임베딩 기반 (awaiting_confirmation 상태에서만)
- 문제 선택: 구조적 패턴 매칭 (숫자, 서수)
"""

import json

# ============================================================
# 다중 의도 제한 상수 (가드레일)
# ============================================================
MAX_INTENTS = 3  # 한 번에 처리 가능한 최대 의도 개수
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum

from ..services.openrouter import openrouter_service
from ..config import get_settings
settings = get_settings()
from ..services.langsmith_tracker import track_intent_method


class IntentCategory(str, Enum):
    """상위 의도 카테고리"""
    INFO_COLLECTION = "info_collection"  # 정보 수집 필요
    DISCOVERY = "discovery"               # 문제 탐색/선택
    SOLVING = "solving"                   # 문제 풀이 중
    GENERAL = "general"                   # 일반 대화
    CONFIRMATION = "confirmation"         # 긍정/부정 응답


class ActionType(str, Enum):
    """세부 액션 타입"""
    # Info Collection
    SET_TOPIC = "set_topic"
    SET_DIFFICULTY = "set_difficulty"
    SET_LANGUAGE = "set_language"
    ASK_RECOMMENDATION = "ask_recommendation"
    QUICK_START = "quick_start"  # 정보 수집 스킵하고 바로 문제 유형 선택으로
    SET_SOURCE = "set_source"  # 문제 출처 설정 (백준, 리트코드, 프로그래머스)
    REQUEST_GENERATION = "request_generation"  # 새 문제 생성 요청
    CORPORATE_TEST = "corporate_test"  # 대기업 코테 관련 요청

    # Discovery
    SELECT_PROBLEM = "select_problem"
    SHOW_MORE = "show_more"
    GENERATE_NEW = "generate_new"
    CHANGE_FILTER = "change_filter"
    SELECT_PROBLEM_TYPE = "select_problem_type"
    INQUIRE_PROBLEM = "inquire_problem"  # 검색 결과 문제에 대한 질문

    # Solving (세부 의도)
    REQUEST_HINT = "request_hint"  # 힌트 버튼용 (레벨 증가)
    SUBMIT_CODE = "submit_code"
    ASK_QUESTION = "ask_question"
    GIVE_UP = "give_up"
    # 채팅 기반 도움 (힌트 버튼과 별개)
    CHAT_ASSIST = "chat_assist"  # 일반 채팅 도움
    CONCEPT_EXPLAIN = "concept_explain"  # 개념 설명
    APPROACH_HINT = "approach_hint"  # 접근법 힌트
    VALIDATE_DIRECTION = "validate_direction"  # 방향 확인
    CODE_REVIEW = "code_review"  # 코드 리뷰
    FEEDBACK_REQUEST = "feedback_request"  # 피드백 요청
    SUMMARIZE_PROBLEM = "summarize_problem"  # 문제 요약

    # Confirmation
    AFFIRM = "affirm"
    NEGATE = "negate"
    UNCLEAR = "unclear"

    # General
    GREETING = "greeting"
    THANKS = "thanks"
    HELP = "help"
    FREE_CHAT = "free_chat"


@dataclass
class IntentResult:
    """통합 의도 분류 결과"""
    category: IntentCategory
    action: ActionType
    confidence: float

    # 추출된 값들
    extracted_values: Dict[str, Any] = field(default_factory=dict)

    # 선택 관련
    selection_index: Optional[int] = None
    selection_type: Optional[str] = None

    # 문제 질문 관련 (inquire_problem)
    inquiry_target: Optional[str] = None  # 질문 대상 (인덱스 또는 문제명)
    inquiry_question: Optional[str] = None  # 원본 질문

    # 추가 정보
    requires_context: Optional[str] = None
    suggested_route: Optional[str] = None


@dataclass
class MultiIntentResult:
    """다중 의도 분류 결과"""
    intents: List[IntentResult]  # 감지된 의도들 (우선순위 순, MAX_INTENTS 제한)
    is_multi_intent: bool  # 다중 의도 여부
    original_message: str  # 원본 메시지
    exceeded_limit: bool = False  # MAX_INTENTS 초과 여부
    original_intent_count: int = 0  # 원래 감지된 의도 수 (제한 전)

    @property
    def primary_intent(self) -> Optional[IntentResult]:
        """첫 번째(주요) 의도 반환"""
        return self.intents[0] if self.intents else None

    @property
    def intent_count(self) -> int:
        """감지된 의도 수 (제한 적용 후)"""
        return len(self.intents)


# ============================================================
# LLM 프롬프트 (복잡한 경우용)
# ============================================================

# ============================================================
# 다중 의도 감지용 프롬프트
# ============================================================

MULTI_INTENT_PROMPT = """당신은 코딩 학습 챗봇의 **다중 의도 분류기**입니다.
사용자 메시지에서 **여러 개의 의도**를 감지하고 분리해야 합니다.

## 컨텍스트
{context}

## 사용자 메시지
"{message}"

## 분석 방법

### 1. 다중 의도 패턴 감지
- 접속사로 연결된 요청: "그리고", "또", "랑", "하고", "도"
- 나열된 요청: "먼저 ~, 그 다음 ~"
- 복합 요청: "~ 하고 ~ 도 알려줘"

### 2. 의도 분리 예시
- "정렬 문제 풀고 싶어, 그리고 내 레벨도 알려줘" → [set_topic, progress_check]
- "구현 문제 추천해줘 그리고 힌트도 줘" → [set_topic, request_hint]
- "문제 풀고 싶은데 어떤 거 풀어야 할지 모르겠어" → [ask_recommendation] (단일)
- "1번으로 하고 빈칸으로 할게" → [select_problem, select_problem_type]

### 3. 카테고리/액션 목록
**info_collection:** set_topic, set_difficulty, set_language, ask_recommendation, quick_start, set_source, request_generation, corporate_test
**discovery:** select_problem, show_more, generate_new, select_problem_type, inquire_problem
**solving:** request_hint, submit_code, ask_question, give_up, chat_assist, concept_explain, approach_hint, validate_direction, code_review
**confirmation:** affirm, negate
**general:** greeting, thanks, help, free_chat, progress_check, weak_point, study_plan

### 3-1. 문제 풀이 중 주의사항 (중요!)
**컨텍스트에 "현재 문제 풀이 중"이 있으면:**
- 블럭/순서/빈칸 관련 질문은 모두 **solving** 카테고리
- 숫자가 있어도 select_problem이 아님! (예: "두번째 블럭" → solving/chat_assist)
- **절대 info_collection이나 discovery로 분류 금지!**

### 4. 우선순위 및 분기 분류
**primary (메인 분기 결정)**:
- info_collection: set_topic, set_difficulty, set_language, ask_recommendation
- discovery: select_problem, show_more, generate_new
- solving: request_hint, submit_code, give_up

**secondary (메인 분기에 병합 가능)**:
- general: greeting, thanks, progress_check, weak_point, study_plan
- confirmation: affirm, negate

우선순위: primary 의도가 분기를 결정하고, secondary 의도는 응답에 병합

## 응답 형식 (JSON)
{{
  "is_multi_intent": true/false,
  "intents": [
    {{
      "category": "카테고리",
      "action": "액션",
      "confidence": 0.0-1.0,
      "extracted_values": {{}},
      "suggested_route": "collection|discovery|solving|respond"
    }}
  ],
  "reasoning": "분리 이유 (간단히)"
}}

**중요:**
- 의도가 1개뿐이면 is_multi_intent: false
- 의도가 2개 이상이면 is_multi_intent: true, intents 배열에 순서대로 나열
- 최대 3개까지만 분리 (그 이상은 복잡도 제한)
"""

UNIFIED_INTENT_PROMPT = """당신은 코딩 학습 챗봇의 의도 분류기입니다.
사용자 메시지를 분석하여 의도와 액션을 판단하세요.

## 컨텍스트
{context}

## 사용자 메시지
"{message}"

## 분류 기준

### 1. 카테고리 (category)
- info_collection: 문제 조건 설정 중 (주제/난이도/언어/목표/레벨 선택)
- discovery: 문제 탐색 중 (검색 결과에서 선택, 더 보기, 새로 생성)
- solving: 문제 풀이 중 (힌트 요청, 코드 제출, 질문, 요약)
- confirmation: 네/아니오 응답
- general: 인사, 감사, 일반 대화

### 2. 액션 (action)
**info_collection:**
- set_topic: 주제 선택 - "트리문제 풀래", "DP 연습할래", "그래프문제 추천", "정렬 공부하고 싶어", "구현 문제 풀고 싶어"
  - 핵심: 주제명이 포함된 모든 문제 풀기/추천/연습 요청
- set_difficulty: 난이도 선택 (실버~마스터, 쉬움~어려움)
- set_language: 언어 선택 (python, java, cpp)
- ask_recommendation: 추천 요청, 학습 목표/레벨 언급 ("추천해줘", "대기업 코테", "초보인데", "모르겠어", "아무거나 추천해줘")
- quick_start: 정보 수집 단계를 건너뛰고 빠르게 문제 풀이 시작 ("빨리 시작하자", "스킵", "귀찮아", "바로 문제 줘", "정보 수집 건너뛰고")

### 2-1. ask_recommendation vs quick_start 구분 (매우 중요!)
**ask_recommendation (info_collection 내에서 추천):**
- "모르겠어" → 무엇을 풀지 모르겠다, 도움이 필요함 → info_collection에서 추천
- "아무거나 추천해줘" → 추천을 원함 → info_collection에서 추천
- "뭐 풀까?", "뭐가 좋을까?" → 조언 요청 → info_collection에서 추천

**quick_start (바로 문제 유형 선택으로):**
- "빨리", "스킵", "귀찮아", "빠르게" → 시간이 없거나 절차를 생략하고 싶음
- "정보 수집 건너뛰고", "바로 문제 줘" → 명시적으로 단계 생략 요청
- "그냥 아무 문제나 줘" + 급한 어조 → 빠른 시작 원함

**핵심 차이:**
- ask_recommendation: 사용자가 **도움이 필요**해서 추천을 원함 (느긋함)
- quick_start: 사용자가 **빨리 시작**하고 싶어서 절차를 생략하고 싶음 (급함)

### 2-2. 출처/생성/대기업 코테 의도 (매우 중요!)
**set_source (출처 지정):**
- "백준 문제 풀고 싶어" → source: "baekjoon"
- "리트코드 문제 줘" → source: "leetcode"
- "프로그래머스 문제로" → source: "programmers"
- 출처 설정만 하고 나머지 정보 수집은 계속 진행

**request_generation (새 문제 생성 요청):**
- "새로운 문제 만들어줘", "문제 생성해줘", "DB에 없는 새 문제" → 새 문제 생성 의도
- 이 경우 추가 정보 수집(generation_details) 단계가 필요함
- extracted_values에 wants_generation: true 설정

**corporate_test (대기업 코테):**
- "카카오 코테 준비", "대기업 기출", "네이버 코딩테스트", "기출문제 풀고 싶어"
- "입사 코테", "채용 코테", "기업 코딩테스트"
- 이 경우 programmers_embeddings + problem_embeddings 모두에서 RAG 검색
- extracted_values에 is_corporate_test: true 설정

**discovery (검색 결과가 있을 때 - 매우 중요!):**

1. **select_problem**: 문제 선택 - 검색 결과 중 특정 문제를 **풀겠다**는 의도
   - 번호로 선택: "1번", "첫 번째", "맨 위 거", "2번 할래", "세 번째"
   - 이름으로 선택: "Two Sum", "Binary Search 풀래", "Valid Parentheses"
   - 암묵적 선택: "그거", "그걸로", "이거", "시작", "풀래", "할게" (검색 결과 참조)
   - **핵심**: 문제를 풀겠다/선택하겠다 = select_problem

2. **show_more**: 다른 문제 검색/더 보기 - 현재 결과가 마음에 안 들 때
   - "다른 거", "다른 문제", "더 보여줘", "더 찾아줘", "다시 찾아"
   - "이거 말고 다른 거", "비슷한 다른 문제", "더 없어?"
   - **핵심**: 기존 검색 조건으로 추가/다른 결과 원함

3. **change_filter**: 검색 조건 변경 - 주제/난이도/출처 변경
   - "정렬 문제로 바꿔줘" (기존: 구현) → 새 주제로 변경
   - "쉬운 거로 다시" (기존: hard) → 난이도 변경
   - "백준 문제로" (기존: leetcode) → 출처 변경
   - **핵심**: 검색 조건 변경 요청 = change_filter
   - extracted_values에 변경할 값 설정 (topic, difficulty, source 등)

4. **generate_new**: 새 문제 **생성** 요청 - DB에 없는 문제
   - "새로운 문제 만들어줘", "문제 생성해줘", "비슷한 문제 생성"
   - "이런 유형으로 새 문제", "연습 문제 만들어줘"
   - extracted_values: wants_generation=true
   - **핵심**: "생성", "만들어" 키워드 = generate_new

5. **generate_new + 대기업**: 대기업 코테 스타일 생성 요청
   - "카카오 스타일 문제 만들어줘", "대기업 기출 생성해줘"
   - "네이버 코테 같은 문제 생성", "삼성 기출 스타일로"
   - action=generate_new, extracted_values: is_corporate_test=true, wants_generation=true
   - **핵심**: 대기업 + 생성 = generate_new with is_corporate_test

6. **inquire_problem**: 두 가지 케이스가 있음 (컨텍스트에 따라 구분!)

   **(A) 검색 결과가 있을 때 - 문제 내용 질문:**
   - 검색 결과 중 특정 문제에 대한 설명/질문 요청
   - "1번 요약해줘", "Two Sum 어떤 내용?", "3번 풀만해?"
   - "어떤 게 더 쉬워?", "뭐가 좋을까?" (비교)
   - inquiry_target: 번호 또는 검색 결과에 있는 문제 이름 **그대로**
   - 예: "1번 알려줘" → inquiry_target="1"
   - 예: "Two Sum 설명해줘" → inquiry_target="Two Sum"

   **(B) 검색 결과가 없을 때 - 새로운 문제 검색:**
   - DB에서 특정 문제를 이름으로 찾아달라는 요청
   - "시식코너는 나의 것이라는 문제 찾아줘", "피보나치 수열 문제 알려줘"
   - inquiry_target: **문제 이름만 파싱**해서 설정 (동사/접미사 제거!)
   - **파싱 규칙:**
     - "시식코너는 나의 것이라는 문제 찾아줘" → inquiry_target="시식코너는 나의 것"
     - "Two Sum 문제 알려줘" → inquiry_target="Two Sum"
     - "피보나치 수열 문제 설명해줘" → inquiry_target="피보나치 수열"
   - **절대로 "문제", "찾아줘", "알려줘", "이라는" 등을 포함하지 말 것!**

   **핵심 구분법:**
   - 컨텍스트에 "검색 결과 N개 존재"가 있으면 → (A) 문제 내용 질문
   - 컨텍스트에 검색 결과가 없으면 → (B) 새로운 문제 검색

7. **free_chat (general)**: 검색 결과와 무관한 일반 질문
   - "정렬 알고리즘이 뭐야?", "시간복잡도 설명해줘"
   - "코테 팁 알려줘", "자바 vs 파이썬"
   - **핵심**: 검색 결과 문제 언급 없이 일반적 질문 = general / free_chat

8. **select_problem_type**: 문제 유형 선택 (문제 선택 후)
   - "빈칸으로", "퍼즐로 풀래", "대화형으로"

**검색 결과 있을 때 분류 우선순위 (중요!):**
1. 문제 번호/이름 + 풀겠다/선택 → **select_problem** (selection_index 필수!)
2. 문제 번호/이름 + 질문/설명/비교 → **inquire_problem** (inquiry_target 필수!)
3. "다른"/"더" + 문제/찾아 → **show_more**
4. 새 조건(주제/난이도/출처) 언급 → **change_filter** (extracted_values에 변경값)
5. "생성"/"만들어" 키워드 → **generate_new** (wants_generation=true)
6. 검색 결과 무관 일반 질문 → **general / free_chat**

**solving:**
- request_hint: 명시적 힌트 버튼 요청 ("힌트 줘", "hint")
- submit_code: 코드 제출/실행 ("제출", "실행해", "채점")
- give_up: 포기/정답 보기 ("포기", "정답 보여줘", "답이 뭐야")
- summarize_problem: 문제 요약 요청 ("요약해줘", "문제 설명해줘")
- chat_assist: 채팅 도움 요청 ("모르겠어", "어려워", "도와줘", "알려줘")
- concept_explain: 개념 설명 요청 ("이게 뭐야?", "왜 이렇게?", "원리가 뭐야")
- approach_hint: 접근법 질문 ("어떻게 시작해?", "어떻게 접근?", "방법이 뭐야")
- validate_direction: 방향 확인 ("이렇게 하면 맞아?", "이 방향이 맞나?", "틀렸나?")
- code_review: 코드 리뷰 요청 ("코드 봐줘", "리뷰해줘", "이 코드 어때")
- feedback_request: 피드백 요청 ("피드백 줘", "어떻게 개선해?")
- ask_question: 일반 질문 (위에 해당 안 되는 질문)

**confirmation:**
- affirm: 긍정 ("네", "응", "좋아", "그걸로", "ㅇㅇ", "굳")
- negate: 부정, 거절 ("아니", "다른 거", "말고", "싫어", "짜증나", "지겨워")

**general:**
- greeting: 인사 ("안녕", "하이")
- thanks: 감사 ("고마워", "감사")
- free_chat: 일반 대화, 잡담

### 3. 값 추출 (extracted_values) - 언급된 것만 추출
- topic: 구현, 정렬, 문자열, 이분탐색, 그리디, 백트래킹, BFS/DFS, 트리, 기초, 수학 등
- difficulty: easy, medium, medium_hard, hard, very_hard
- language: python, java, cpp
- source: 문제 출처 (baekjoon, leetcode) - "백준 문제", "리트코드 문제" 등
- wants_generation: true/false - 새 문제 생성 요청 여부 ("새 문제 만들어줘", "생성해줘")
- generation_details: 문자열 - 어떤 문제를 원하는지 자유 양식 설명 ("카카오 스타일로", "실전같은 문제")
- is_corporate_test: true/false - 대기업 코테 관련 여부 ("카카오", "네이버", "대기업", "기출", "입사", "채용")
- learning_goal: big_tech (대기업/코테), mid_startup (스타트업), skill_up (실력향상)
- experience_level: beginner (입문), elementary (초급), intermediate (중급), advanced (고급)
- problem_type: blank (빈칸), puzzle (퍼즐/파슨스), guided (대화형/1대1)

### 4. 문제 풀이 중 여부에 따른 분류 (매우 중요!)
**컨텍스트에 "문제 풀이 중 아님"이라고 되어 있으면:**
- "도와줘", "어렵네", "모르겠어" → **info_collection / ask_recommendation** (새 문제 추천 요청)
- "코테 도와줘", "연습하고 싶어" → **info_collection / ask_recommendation**
- solving 카테고리는 적용하면 안 됨!

**컨텍스트에 "현재 문제 풀이 중"이라고 되어 있을 때만:**
- "도와줘", "어렵다", "모르겠어" → **solving / chat_assist** (현재 문제에 대한 도움)
- solving 카테고리의 모든 액션 적용 가능
- **절대 info_collection이나 discovery로 분류하지 마세요!**

**빈칸/퍼즐/대화형 문제 풀이 중 특수 케이스:**
- "블럭 순서", "블록 배치", "빈칸 답변" 관련 질문 → **solving / chat_assist 또는 validate_direction**
- "두번째 블럭이랑 3번째" 같은 숫자 표현 → 문제 선택이 아님! **solving** 카테고리
- "이 순서 맞아?", "이렇게 하면 될까?" → **solving / validate_direction**
- "힌트 더 줘", "다른 힌트" → **solving / chat_assist**
- 숫자가 포함되어도 블럭/순서/빈칸과 함께면 → **solving** (절대 discovery/select_problem 아님!)

### 5. 부정/거부 표현 주의! (매우 중요)
**"X 말고"는 X를 원하지 않는다는 뜻!**
- "기초 말고" → topic=null (기초 거부!), action=ask_recommendation 또는 set_topic
- "정렬 말고 다른 거" → topic=null (정렬 거부!), action=ask_recommendation
- "쉬운 거 말고" → difficulty=null (easy 거부!)
- "파이썬 말고" → language=null (python 거부!)

**다른 거부 표현**
- "X 싫어", "X 지겨워", "X 짜증나" → X를 거부하는 것!
- "X 빼고", "X 제외" → X를 제외하고 추천
- "X 아닌 거" → X가 아닌 것 원함

**핵심 규칙: 거부하는 값은 절대 extracted_values에 넣지 말 것!**
- "기초 말고 아무거나" → {{"topic": null}} (기초를 넣으면 안 됨!)
- "이분탐색 문제 풀래" → {{"topic": "이분탐색"}} (긍정이므로 넣음)

### 6. 검색 결과가 있을 때 분류 (매우 중요!)
컨텍스트에 "검색 결과 N개 존재"가 있으면 discovery 카테고리 우선!

**select_problem (문제 선택):**
- "1번", "첫 번째" → category=discovery, action=select_problem, selection_index=1
- "두 번째 문제 풀래" → selection_index=2
- "Two Sum" (문제명 직접) → 해당 번호를 selection_index에 설정
- "그거", "그걸로", "이거 풀래" → selection_index=1
- **필수**: selection_index 설정!

**inquire_problem (두 가지 케이스):**
**(A) 검색 결과 있을 때 - 내용 질문:**
- "1번 요약해줘" → inquiry_target="1", inquiry_question="요약해줘"
- "Two Sum 어떤 내용?" → inquiry_target="Two Sum"
- "3번 풀만해?" → inquiry_target="3"
- "어떤 게 더 쉬워?" → inquiry_target="general" (비교 질문)

**(B) 검색 결과 없을 때 - 문제 이름 검색 (파싱 필수!):**
- "시식코너는 나의 것이라는 문제 찾아줘" → inquiry_target="시식코너는 나의 것"
- "피보나치 수열 문제 알려줘" → inquiry_target="피보나치 수열"
- **필수**: 검색 결과 없으면 문제 이름만 파싱! ("문제", "찾아줘" 등 제외)

**show_more (더 보기):**
- "다른 문제", "더 찾아줘", "이거 말고" → action=show_more
- 기존 조건 유지하고 추가 결과 요청

**change_filter (조건 변경):**
- "정렬로 바꿔", "쉬운 거로" → action=change_filter
- extracted_values에 변경할 값 설정

**generate_new (문제 생성):**
- "새 문제 만들어줘", "비슷한 문제 생성해줘" → action=generate_new
- extracted_values: wants_generation=true
- 대기업 스타일: is_corporate_test=true 추가

**free_chat (일반 질문):**
- 검색 결과 문제와 무관한 일반 코딩 질문
- "정렬이 뭐야?", "시간복잡도 설명해줘"

### 7. select_problem vs inquire_problem 구분법
**select_problem (풀겠다):**
- "1번 풀래", "이거", "그거로 할게", "시작", "선택"
- 질문 키워드 없음 → select_problem

**inquire_problem (질문/검색):**
- (A) 검색 결과 있음: "요약해줘", "설명해줘", "어때?", "풀만해?", "어떤 내용?"
- (B) 검색 결과 없음: "~라는 문제 찾아줘", "~ 문제 알려줘" (새 검색)
- 비교: "어떤 게 좋아?", "추천해줘"

**핵심 규칙:**
- 검색 결과 있고 질문 키워드 → inquire_problem (내용 설명)
- 검색 결과 없고 문제 이름 언급 → inquire_problem (새 검색, 이름 파싱!)
- 풀기/선택 의도 → select_problem
- 둘 다 없으면 문맥으로 판단 (단순 문제명만 → select_problem)

### 8. selection_index 설정 방법 (매우 중요!)
컨텍스트의 검색 결과 목록을 보고 사용자가 언급한 문제의 번호를 찾아 설정:
- 컨텍스트: "1번: Two Sum, 2번: Eligibility, 3번: Valid Parentheses"
- 사용자: "Eligibility 문제로 할게요" → **selection_index=2** (2번이므로)
- 사용자: "Two Sum" → **selection_index=1** (1번이므로)
- 사용자: "3번 풀래" → **selection_index=3**
- 문제 이름이 부분 매칭되어도 OK (예: "Elig" → Eligibility = 2번)
- **반드시 검색 결과에서 해당 문제의 번호를 찾아 selection_index 설정!**

## 응답 형식 (JSON)
{{
  "category": "info_collection|discovery|solving|confirmation|general",
  "action": "액션값",
  "confidence": 0.0-1.0,
  "extracted_values": {{"topic": null, "difficulty": null, "language": null, "learning_goal": null, "experience_level": null, "problem_type": null, "source": null, "wants_generation": false, "generation_details": null, "is_corporate_test": false}},
  "selection_index": null,
  "inquiry_target": null,
  "inquiry_question": null,
  "suggested_route": "collection|discovery|solving|respond"
}}
"""


class IntentTool:
    """임베딩 기반 통합 의도 분류 Tool"""

    def __init__(self):
        self._embeddings_service = None

    def _get_embeddings_service(self):
        """지연 로딩으로 임베딩 서비스 가져오기"""
        if self._embeddings_service is None:
            from ..services.collection_embeddings import get_collection_embeddings_service
            self._embeddings_service = get_collection_embeddings_service()
        return self._embeddings_service

    @track_intent_method("classify", tags=["main", "llm"])
    async def classify(
        self,
        message: str,
        session_state: Optional[Dict[str, Any]] = None,
    ) -> IntentResult:
        """
        메시지의 의도와 액션을 분류 (LLM First)

        Args:
            message: 사용자 메시지
            session_state: 세션 상태 (current_step, awaiting_confirmation 등)

        Returns:
            IntentResult
        """
        session_state = session_state or {}

        # ============================================================
        # 1. 확인 응답 처리 (awaiting_confirmation 상태에서 최우선)
        # ============================================================
        if session_state.get("awaiting_confirmation"):
            confirmation_result = await self._check_confirmation(message, session_state)
            if confirmation_result:
                return confirmation_result

        # ============================================================
        # 2. 문제 선택 (search_results 있을 때) - 구조적 패턴
        # ============================================================
        if session_state.get("search_results"):
            selection_result = self._check_problem_selection(message, session_state)
            if selection_result:
                return selection_result

        # ============================================================
        # 3. LLM 분류 (모든 의도 분류는 LLM이 담당)
        # ============================================================
        # 임베딩 기반 분류 제거 - LLM이 컨텍스트(부정어, 복합문장 등)를 더 잘 이해함
        return await self._classify_with_llm(message, session_state)

    async def _check_confirmation(
        self,
        message: str,
        session_state: Dict[str, Any],
    ) -> Optional[IntentResult]:
        """
        확인 응답 감지 (LLM First - 임베딩 기반)

        awaiting_confirmation=True 상태에서 긍정/부정 응답 감지
        """
        embeddings = self._get_embeddings_service()

        # 임베딩 서비스 미초기화 시 LLM으로 직접 처리 (키워드 fallback 제거)
        if not embeddings.is_initialized():
            print("[IntentTool] Embeddings not initialized, using LLM for confirmation")
            return None  # LLM 분류로 넘김

        # 임베딩 기반 긍정/부정 감지
        is_positive, is_negative, confidence = await embeddings.match_confirmation(message)

        print(f"[IntentTool] Confirmation check: pos={is_positive}, neg={is_negative}, conf={confidence:.2f}")

        if is_positive and confidence >= 0.60:
            # 긍정 응답 + suggested_value가 있으면 해당 값 적용
            suggested_value = session_state.get("suggested_value")
            current_step = session_state.get("current_step", "topic")

            extracted = {}
            if suggested_value:
                if current_step == "topic":
                    extracted["topic"] = suggested_value
                elif current_step == "difficulty":
                    extracted["difficulty"] = suggested_value
                elif current_step == "language":
                    extracted["language"] = suggested_value

            return IntentResult(
                category=IntentCategory.CONFIRMATION,
                action=ActionType.AFFIRM,
                confidence=confidence,
                extracted_values=extracted,
                suggested_route="collection",
            )

        if is_negative and confidence >= 0.60:
            return IntentResult(
                category=IntentCategory.CONFIRMATION,
                action=ActionType.NEGATE,
                confidence=confidence,
                suggested_route="collection",
            )

        # 확인 응답이 아님 → 다른 의도일 수 있음
        return None

    # _simple_confirmation_check 제거됨 - LLM이 처리
    # _check_goal_or_level_mention 제거됨 - LLM이 처리

    def _check_problem_selection(
        self,
        message: str,
        session_state: Dict[str, Any],
    ) -> Optional[IntentResult]:
        """문제 선택 감지"""
        import re
        msg_lower = message.lower().strip()

        # ============================================================
        # 문제 풀이 중일 때는 숫자 패턴을 문제 선택으로 해석하지 않음
        # "두번째 블럭", "3번째 순서" 같은 표현은 퍼즐 관련 질문
        # ============================================================
        current_problem = session_state.get("current_problem") or session_state.get("selected_problem")
        current_practice_state = session_state.get("current_practice_state") or {}
        is_solving = current_problem is not None or current_practice_state.get("problem_id") is not None

        # 퍼즐/빈칸 문제 풀이 중 관련 키워드 감지
        practice_keywords = ["블럭", "블록", "순서", "위치", "배치", "빈칸", "답변", "코드", "힌트"]
        has_practice_keyword = any(kw in msg_lower for kw in practice_keywords)

        # 문제 풀이 중이고 관련 키워드가 있으면 문제 선택이 아님
        if is_solving and has_practice_keyword:
            return None

        # "1번", "첫 번째", "맨 위"
        num_match = re.search(r'^(\d+)\s*번?$', msg_lower)
        if num_match:
            idx = int(num_match.group(1))
            return IntentResult(
                category=IntentCategory.DISCOVERY,
                action=ActionType.SELECT_PROBLEM,
                confidence=0.98,
                selection_index=idx,
                selection_type="number",
                suggested_route="discovery",
            )

        ordinal_map = {"첫": 1, "두": 2, "세": 3, "네번": 4, "다섯": 5}
        for word, idx in ordinal_map.items():
            # 문제 풀이 중에는 서수 패턴 무시 (블럭 순서 질문일 수 있음)
            if is_solving:
                continue
            if msg_lower.startswith(word):
                return IntentResult(
                    category=IntentCategory.DISCOVERY,
                    action=ActionType.SELECT_PROBLEM,
                    confidence=0.95,
                    selection_index=idx,
                    selection_type="ordinal",
                    suggested_route="discovery",
                )

        # ============================================================
        # 나머지는 LLM에 맡김 (문제명 선택, 질문 등)
        # search_results가 있으면 LLM이 select_problem/inquire_problem 분류
        # ============================================================
        return None

    @track_intent_method("_classify_with_llm", tags=["llm", "gemini-3-flash"])
    async def _classify_with_llm(
        self,
        message: str,
        session_state: Dict[str, Any],
    ) -> IntentResult:
        """LLM 기반 분류 (Fallback)"""
        # 컨텍스트 구성
        context_parts = []

        # 🔥 핵심: 현재 문제 풀이 중인지 여부
        # current_problem 또는 current_practice_state가 있으면 문제 풀이 중
        current_problem = session_state.get("current_problem") or session_state.get("selected_problem")
        current_practice_state = session_state.get("current_practice_state") or {}
        current_stage = session_state.get("stage", "")

        # current_practice_state에 problem_id가 있으면 문제 풀이 중
        is_solving = (
            current_stage == "solving" or
            current_problem is not None or
            current_practice_state.get("problem_id") is not None
        )

        if is_solving:
            # 문제 이름 추출 (current_problem 또는 current_practice_state에서)
            problem_name = "알 수 없음"
            problem_type = ""
            if current_problem:
                problem_name = current_problem.get("name") or current_problem.get("title") or "알 수 없음"
            elif current_practice_state.get("problem_title"):
                problem_name = current_practice_state.get("problem_title")
                problem_type = current_practice_state.get("problem_type", "")

            context_parts.append(f"- **현재 문제 풀이 중**: {problem_name}")
            if problem_type:
                context_parts.append(f"- **문제 유형**: {problem_type} (빈칸/퍼즐/대화형)")
                context_parts.append("- **주의**: 사용자가 현재 풀고 있는 문제에 대해 질문하면 solving 카테고리로 분류!")
        else:
            context_parts.append("- **문제 풀이 중 아님**: 새 문제 탐색/추천 단계")

        # 🔥 핵심: 검색 결과가 있으면 discovery 카테고리 우선!
        search_results = session_state.get("search_results", [])
        if search_results:
            context_parts.append(f"- **검색 결과 {len(search_results)}개 존재** (문제 선택/질문 가능):")
            for idx, p in enumerate(search_results[:5], 1):
                name = p.get("name") or ""
                title = p.get("title") or ""
                # 이름과 제목 모두 표시 (매칭 용이하게)
                display = f"{idx}번: {name}"
                if title and title != name:
                    display += f" ({title})"
                context_parts.append(f"  {display}")
            context_parts.append("- **주의**: 문제명/번호 언급 시 discovery 카테고리로 분류!")
            context_parts.append("- **중요**: 사용자가 문제를 선택하면 해당 번호를 selection_index에 설정!")

        if session_state.get("current_step"):
            context_parts.append(f"- 현재 수집 단계: {session_state['current_step']}")
        if session_state.get("topic"):
            context_parts.append(f"- 선택된 주제: {session_state['topic']}")
        if session_state.get("difficulty"):
            context_parts.append(f"- 선택된 난이도: {session_state['difficulty']}")
        if session_state.get("language"):
            context_parts.append(f"- 선택된 언어: {session_state['language']}")
        if session_state.get("awaiting_confirmation"):
            context_parts.append(f"- 확인 대기 중: {session_state.get('suggested_value')}")

        context = "\n".join(context_parts) if context_parts else "없음"

        prompt = UNIFIED_INTENT_PROMPT.format(context=context, message=message)

        try:
            # gemini-3-flash로 의도 분류
            response = await openrouter_service.chat_completion(
                model=settings.llm_model_lite,
                messages=[
                    {"role": "system", "content": "의도 분류 전문가"},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.0,  # 분류는 결정적이어야 함
                max_tokens=150,   # 분류 결과만 필요
                response_format={"type": "json_object"},
            )

            content = openrouter_service.get_content(response)
            result = json.loads(content)

            return IntentResult(
                category=IntentCategory(result.get("category", "general")),
                action=ActionType(result.get("action", "free_chat")),
                confidence=result.get("confidence", 0.7),
                extracted_values=result.get("extracted_values", {}),
                selection_index=result.get("selection_index"),
                selection_type=result.get("selection_type"),
                suggested_route=result.get("suggested_route"),
            )

        except Exception as e:
            print(f"[IntentTool] LLM classification error: {e}")
            import traceback
            traceback.print_exc()
            # 🔥 Fallback: 메시지 패턴으로 기본 분류 (fast-path와 동일한 결과)
            msg_lower = message.lower()
            msg_stripped = message.strip()

            # ============================================================
            # 1. 주제 키워드 (fast-path CHIP_TOPIC_KEYWORDS와 동일)
            # ============================================================
            topic_keywords = {
                "구현": "구현", "정렬": "정렬", "dp": "DP", "DP": "DP",
                "그리디": "그리디", "이분탐색": "이분탐색", "문자열": "문자열",
                "그래프": "그래프", "bfs/dfs": "BFS/DFS", "BFS/DFS": "BFS/DFS",
                "트리": "트리", "수학": "수학", "자료구조": "자료구조",
                "완전탐색": "완전탐색", "백트래킹": "백트래킹", "분할정복": "분할정복",
                "시뮬레이션": "시뮬레이션", "기초": "기초", "최단경로": "최단경로",
                "투포인터": "투포인터", "스택": "스택", "큐": "큐", "힙": "힙",
                "해시": "해시", "hash": "해시", "bfs": "BFS/DFS", "dfs": "BFS/DFS",
            }

            # ============================================================
            # 2. 난이도 키워드 (fast-path CHIP_DIFFICULTY_KEYWORDS와 동일)
            # ============================================================
            difficulty_keywords = {
                "실버": "easy", "silver": "easy", "easy": "easy", "쉬움": "easy",
                "골드": "medium", "gold": "medium", "medium": "medium", "보통": "medium",
                "플래티넘": "medium_hard", "platinum": "medium_hard",
                "다이아": "hard", "diamond": "hard", "hard": "hard",
                "마스터": "very_hard", "master": "very_hard",
            }

            # ============================================================
            # 3. 언어 키워드 (fast-path CHIP_LANGUAGE_KEYWORDS와 동일)
            # ============================================================
            language_keywords = {
                "파이썬": "python", "python": "python", "Python": "python",
                "자바": "java", "java": "java", "Java": "java",
                "c++": "cpp", "cpp": "cpp", "C++": "cpp",
            }

            # ============================================================
            # 키워드 매칭 (fast-path와 동일한 우선순위: topic → difficulty → language)
            # ============================================================

            # 1순위: 정확한 키워드 매칭 (칩 클릭과 동일)
            if msg_stripped in topic_keywords or msg_lower in topic_keywords:
                detected_topic = topic_keywords.get(msg_stripped) or topic_keywords.get(msg_lower)
                print(f"[IntentTool] Fallback: exact topic match → {detected_topic}")
                return IntentResult(
                    category=IntentCategory.INFO_COLLECTION,
                    action=ActionType.SET_TOPIC,
                    confidence=0.9,
                    extracted_values={"topic": detected_topic},
                    suggested_route="collection",
                )

            if msg_stripped in difficulty_keywords or msg_lower in difficulty_keywords:
                detected_difficulty = difficulty_keywords.get(msg_stripped) or difficulty_keywords.get(msg_lower)
                print(f"[IntentTool] Fallback: exact difficulty match → {detected_difficulty}")
                return IntentResult(
                    category=IntentCategory.INFO_COLLECTION,
                    action=ActionType.SET_DIFFICULTY,
                    confidence=0.9,
                    extracted_values={"difficulty": detected_difficulty},
                    suggested_route="collection",
                )

            if msg_stripped in language_keywords or msg_lower in language_keywords:
                detected_language = language_keywords.get(msg_stripped) or language_keywords.get(msg_lower)
                print(f"[IntentTool] Fallback: exact language match → {detected_language}")
                return IntentResult(
                    category=IntentCategory.INFO_COLLECTION,
                    action=ActionType.SET_LANGUAGE,
                    confidence=0.9,
                    extracted_values={"language": detected_language},
                    suggested_route="collection",
                )

            # 2순위: 추천 요청 감지 (ask_recommendation)
            recommendation_keywords = ["추천", "아무거나", "아무 문제", "뭐 풀", "뭘 풀", "모르겠", "도와줘", "골라줘"]
            if any(kw in msg_lower for kw in recommendation_keywords):
                print(f"[IntentTool] Fallback: recommendation keyword detected → ask_recommendation")
                return IntentResult(
                    category=IntentCategory.INFO_COLLECTION,
                    action=ActionType.ASK_RECOMMENDATION,
                    confidence=0.8,
                    extracted_values={},
                    suggested_route="collection",
                )

            # 2순위: 부분 매칭 (문장 내에 키워드 포함)
            practice_keywords = ["풀래", "풀고", "연습", "할래", "공부", "가져와", "줘", "문제", "해볼래", "시작"]
            has_practice_intent = any(kw in msg_lower for kw in practice_keywords)

            # 주제 부분 매칭
            for kw, value in topic_keywords.items():
                if kw in msg_lower:
                    print(f"[IntentTool] Fallback: partial topic match '{kw}' → {value}")
                    return IntentResult(
                        category=IntentCategory.INFO_COLLECTION,
                        action=ActionType.SET_TOPIC,
                        confidence=0.7,
                        extracted_values={"topic": value},
                        suggested_route="collection",
                    )

            # 난이도 부분 매칭
            for kw, value in difficulty_keywords.items():
                if kw in msg_lower:
                    print(f"[IntentTool] Fallback: partial difficulty match '{kw}' → {value}")
                    return IntentResult(
                        category=IntentCategory.INFO_COLLECTION,
                        action=ActionType.SET_DIFFICULTY,
                        confidence=0.7,
                        extracted_values={"difficulty": value},
                        suggested_route="collection",
                    )

            # 언어 부분 매칭
            for kw, value in language_keywords.items():
                if kw in msg_lower:
                    print(f"[IntentTool] Fallback: partial language match '{kw}' → {value}")
                    return IntentResult(
                        category=IntentCategory.INFO_COLLECTION,
                        action=ActionType.SET_LANGUAGE,
                        confidence=0.7,
                        extracted_values={"language": value},
                        suggested_route="collection",
                    )

            return IntentResult(
                category=IntentCategory.GENERAL,
                action=ActionType.FREE_CHAT,
                confidence=0.5,
                suggested_route="respond",
            )

    async def detect_problem_type(self, message: str) -> Optional[str]:
        """
        문제 유형 선택 감지 (LLM First)

        LLM classify 결과에서 problem_type 추출
        """
        # classify를 호출하여 extracted_values에서 problem_type 추출
        result = await self.classify(message)
        problem_type = result.extracted_values.get("problem_type")

        if problem_type in ["blank", "puzzle", "guided"]:
            return problem_type

        return None

    # ============================================================
    # 다중 의도 분류 (Multi-Intent Classification)
    # ============================================================

    def _has_multi_intent_signal(self, message: str) -> bool:
        """
        다중 의도 신호 감지 (빠른 휴리스틱)

        접속사, 쉼표 등으로 복합 요청 가능성 판단
        """
        import re

        # 다중 의도 접속사 패턴
        multi_patterns = [
            r'그리고',
            r'그리고\s+',
            r',\s*(그리고|또|그|그런데)',
            r'\s+또\s+',
            r'\s+도\s+',
            r'하고\s+',
            r'랑\s+',
            r'먼저\s+.+그\s*다음',
            r'일단\s+.+그리고',
        ]

        for pattern in multi_patterns:
            if re.search(pattern, message):
                return True

        # 쉼표로 구분된 여러 동사 패턴
        # "~ 해줘, ~ 알려줘"
        verb_endings = ['해줘', '알려줘', '보여줘', '줘', '할래', '할게']
        comma_split = message.split(',')
        if len(comma_split) >= 2:
            verb_count = sum(1 for part in comma_split if any(v in part for v in verb_endings))
            if verb_count >= 2:
                return True

        return False

    @track_intent_method("classify_multi", tags=["multi-intent", "llm"])
    async def classify_multi(
        self,
        message: str,
        session_state: Optional[Dict[str, Any]] = None,
    ) -> MultiIntentResult:
        """
        다중 의도 분류

        메시지에서 여러 의도를 감지하고 분리하여 반환합니다.
        단일 의도인 경우에도 MultiIntentResult 형식으로 반환합니다.

        Args:
            message: 사용자 메시지
            session_state: 세션 상태

        Returns:
            MultiIntentResult: 다중 의도 분류 결과
        """
        session_state = session_state or {}

        # ============================================================
        # 1. 빠른 휴리스틱: 다중 의도 신호 감지
        # ============================================================
        if not self._has_multi_intent_signal(message):
            # 단일 의도로 처리
            single_result = await self.classify(message, session_state)
            return MultiIntentResult(
                intents=[single_result],
                is_multi_intent=False,
                original_message=message,
            )

        # ============================================================
        # 2. LLM 기반 다중 의도 분류
        # ============================================================
        multi_result = await self._classify_multi_with_llm(message, session_state)

        # 다중 의도가 감지되지 않으면 단일 분류로 폴백
        if not multi_result.is_multi_intent or len(multi_result.intents) <= 1:
            single_result = await self.classify(message, session_state)
            return MultiIntentResult(
                intents=[single_result],
                is_multi_intent=False,
                original_message=message,
            )

        return multi_result

    @track_intent_method("_classify_multi_with_llm", tags=["multi-intent", "llm", "gemini-3-flash"])
    async def _classify_multi_with_llm(
        self,
        message: str,
        session_state: Dict[str, Any],
    ) -> MultiIntentResult:
        """
        LLM 기반 다중 의도 분류
        """
        # 컨텍스트 구성
        context_parts = []

        # 🔥 핵심: 현재 문제 풀이 중인지 여부 (단일 의도 분류와 동일한 로직)
        current_problem = session_state.get("current_problem") or session_state.get("selected_problem")
        current_practice_state = session_state.get("current_practice_state") or {}
        current_stage = session_state.get("stage", "")

        is_solving = (
            current_stage == "solving" or
            current_problem is not None or
            current_practice_state.get("problem_id") is not None
        )

        if is_solving:
            problem_name = "알 수 없음"
            problem_type = ""
            if current_problem:
                problem_name = current_problem.get("name") or current_problem.get("title") or "알 수 없음"
            elif current_practice_state.get("problem_title"):
                problem_name = current_practice_state.get("problem_title")
                problem_type = current_practice_state.get("problem_type", "")

            context_parts.append(f"- **현재 문제 풀이 중**: {problem_name}")
            if problem_type:
                context_parts.append(f"- **문제 유형**: {problem_type} (빈칸/퍼즐/대화형)")
        else:
            context_parts.append("- **문제 풀이 중 아님**: 새 문제 탐색/추천 단계")

        if session_state.get("current_step"):
            context_parts.append(f"- 현재 수집 단계: {session_state['current_step']}")
        if session_state.get("topic"):
            context_parts.append(f"- 선택된 주제: {session_state['topic']}")
        if session_state.get("search_results"):
            context_parts.append(f"- 검색 결과: {len(session_state['search_results'])}개 문제")

        context = "\n".join(context_parts) if context_parts else "없음"

        prompt = MULTI_INTENT_PROMPT.format(context=context, message=message)

        try:
            # gemini-3-flash로 다중 의도 분류
            response = await openrouter_service.chat_completion(
                model=settings.llm_model_lite,
                messages=[
                    {"role": "system", "content": "다중 의도 분류 전문가"},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.0,  # 분류는 결정적이어야 함
                max_tokens=200,   # 최대 3개 의도 분류용
                response_format={"type": "json_object"},
            )

            content = openrouter_service.get_content(response)
            result = json.loads(content)

            is_multi = result.get("is_multi_intent", False)
            raw_intents = result.get("intents", [])
            original_count = len(raw_intents)
            exceeded = original_count > MAX_INTENTS

            print(f"[IntentTool] Multi-intent LLM: is_multi={is_multi}, count={original_count}, exceeded={exceeded}")
            print(f"[IntentTool] Reasoning: {result.get('reasoning', 'N/A')}")

            if exceeded:
                print(f"[IntentTool] WARNING: {original_count} intents detected, limiting to {MAX_INTENTS}")

            # IntentResult 객체들로 변환 (MAX_INTENTS 제한 적용)
            intents = []
            for raw in raw_intents[:MAX_INTENTS]:
                try:
                    intent_result = IntentResult(
                        category=IntentCategory(raw.get("category", "general")),
                        action=ActionType(raw.get("action", "free_chat")),
                        confidence=raw.get("confidence", 0.7),
                        extracted_values=raw.get("extracted_values", {}),
                        selection_index=raw.get("selection_index"),
                        suggested_route=raw.get("suggested_route"),
                    )
                    intents.append(intent_result)
                except (ValueError, KeyError) as e:
                    print(f"[IntentTool] Failed to parse intent: {e}")
                    continue

            return MultiIntentResult(
                intents=intents,
                is_multi_intent=is_multi and len(intents) > 1,
                original_message=message,
                exceeded_limit=exceeded,
                original_intent_count=original_count,
            )

        except Exception as e:
            print(f"[IntentTool] Multi-intent LLM error: {e}")
            # 에러 시 단일 의도로 폴백
            return MultiIntentResult(
                intents=[],
                is_multi_intent=False,
                original_message=message,
                exceeded_limit=False,
                original_intent_count=0,
            )


# 싱글톤
intent_tool = IntentTool()
