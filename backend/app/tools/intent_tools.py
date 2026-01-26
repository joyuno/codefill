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
**info_collection:** set_topic, set_difficulty, set_language, ask_recommendation
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
- set_topic: 주제 선택 (정렬, 구현, 이분탐색 등)
- set_difficulty: 난이도 선택 (실버~마스터, 쉬움~어려움)
- set_language: 언어 선택 (python, java, cpp)
- ask_recommendation: 추천 요청, 학습 목표/레벨 언급 ("추천해줘", "대기업 코테", "초보인데")

**discovery:**
- select_problem: 문제 선택 ("첫 번째", "1번", "맨 위 거")
- show_more: 더 보기 ("다른 거", "더 보여줘", "더 찾아")
- generate_new: 새 문제 생성 ("새로운 문제", "비슷한 문제 생성")
- select_problem_type: 문제 유형 선택 ("빈칸", "퍼즐", "대화형")
- inquire_problem: 검색 결과 문제에 대한 질문 ("taco_749 요약해줘", "두 번째 문제 뭐야?", "이거 뭐에 도움되냐", "3번 어떤 내용이야?")

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

### 6. 문제 질문 (inquire_problem)
- "taco_749 요약해줘" → inquiry_target="taco_749"
- "두 번째 문제 뭐야?" → inquiry_target="2"
- "3번 어떤 내용이야?" → inquiry_target="3"
- 질문의 의도: 요약, 도움말, 내용 설명, 난이도 설명 등

## 응답 형식 (JSON)
{{
  "category": "info_collection|discovery|solving|confirmation|general",
  "action": "액션값",
  "confidence": 0.0-1.0,
  "extracted_values": {{"topic": null, "difficulty": null, "language": null, "learning_goal": null, "experience_level": null, "problem_type": null}},
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
        # 문제 이름으로 선택 감지 (search_results와 매칭)
        # "**최적의 라이벌 매칭** (medium) 문제 풀래" 같은 패턴
        # ============================================================
        search_results = session_state.get("search_results", [])
        if search_results and any(kw in msg_lower for kw in ["풀래", "할래", "할게", "선택", "이거로", "그거로"]):
            # Markdown bold 제거: **text** → text
            clean_msg = re.sub(r'\*\*([^*]+)\*\*', r'\1', message)
            # 난이도 표기 제거: (medium), (easy) 등
            clean_msg = re.sub(r'\s*\([^)]+\)\s*', ' ', clean_msg)
            clean_msg_lower = clean_msg.lower().strip()

            for idx, problem in enumerate(search_results, 1):
                # 문제 이름/제목 추출
                problem_name = (problem.get("name") or problem.get("title") or "").lower()
                problem_title = (problem.get("title") or problem.get("name") or "").lower()

                # 문제 이름/제목이 메시지에 포함되어 있으면 선택
                if problem_name and problem_name in clean_msg_lower:
                    return IntentResult(
                        category=IntentCategory.DISCOVERY,
                        action=ActionType.SELECT_PROBLEM,
                        confidence=0.95,
                        selection_index=idx,
                        selection_type="name",
                        suggested_route="discovery",
                    )
                if problem_title and problem_title in clean_msg_lower:
                    return IntentResult(
                        category=IntentCategory.DISCOVERY,
                        action=ActionType.SELECT_PROBLEM,
                        confidence=0.95,
                        selection_index=idx,
                        selection_type="title",
                        suggested_route="discovery",
                    )

        return None

    @track_intent_method("_classify_with_llm", tags=["llm", "gpt-4o-mini"])
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
            # gpt-4o-mini가 gemini-flash보다 빠름 (타임아웃 방지)
            response = await openrouter_service.chat_completion(
                model="gpt-4o-mini",
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

    @track_intent_method("_classify_multi_with_llm", tags=["multi-intent", "llm", "gpt-4o-mini"])
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
            # gpt-4o-mini가 gemini-flash보다 빠름 (타임아웃 방지)
            response = await openrouter_service.chat_completion(
                model="gpt-4o-mini",
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
