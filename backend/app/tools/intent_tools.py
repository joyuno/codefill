"""
Intent Tools - 임베딩 기반 통합 의도 분류

키워드 매핑 제거 → CollectionEmbeddingsService 활용
- 주제/난이도/언어: 임베딩 유사도 매칭
- 긍정/부정 응답: 임베딩 기반 확인
- LLM Fallback: 복잡한 경우만
"""

import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum

from ..services.openrouter import openrouter_service


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


# ============================================================
# LLM 프롬프트 (복잡한 경우용)
# ============================================================

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
- set_topic: 주제 선택 (DP, 그래프, 정렬 등)
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
- topic: DP, 그래프, 정렬, 구현, 기초, 문자열, BFS/DFS, 이분탐색, 그리디, 백트래킹 등
- difficulty: easy, medium, medium_hard, hard, very_hard
- language: python, java, cpp
- learning_goal: big_tech (대기업/코테), mid_startup (스타트업), skill_up (실력향상)
- experience_level: beginner (입문), elementary (초급), intermediate (중급), advanced (고급)
- problem_type: blank (빈칸), puzzle (퍼즐/파슨스), guided (대화형/1대1)

### 4. 거부 표현 주의!
- "X 싫다", "X 지겨워", "X 짜증나" → X를 거부하는 것! negate 액션
- "기초는 싫다" → topic=null (기초 거부), action=negate
- 거부하는 값은 extracted_values에 넣지 말 것

### 5. 문제 질문 (inquire_problem)
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
        # 3. 임베딩 기반 분류 (LLM First - 임베딩도 ML 기반)
        # ============================================================
        embedding_result = await self._classify_with_embeddings(message, session_state)
        if embedding_result and embedding_result.confidence >= 0.70:
            return embedding_result

        # ============================================================
        # 4. LLM 분류 (임베딩 신뢰도 낮을 때)
        # ============================================================
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

    async def _classify_with_embeddings(
        self,
        message: str,
        session_state: Dict[str, Any],
    ) -> Optional[IntentResult]:
        """
        임베딩 기반 주제/난이도/언어 분류
        """
        embeddings = self._get_embeddings_service()

        if not embeddings.is_initialized():
            print("[IntentTool] Embeddings not initialized, skipping")
            return None

        # 모든 카테고리 동시 매칭
        matches = await embeddings.match_all(message)

        topic_match = matches.get("topic")
        diff_match = matches.get("difficulty")
        lang_match = matches.get("language")

        # 가장 높은 유사도 찾기
        best_match = None
        best_category = None
        best_similarity = 0.0

        if topic_match and topic_match.similarity > best_similarity:
            best_match = topic_match
            best_category = "topic"
            best_similarity = topic_match.similarity

        if diff_match and diff_match.similarity > best_similarity:
            best_match = diff_match
            best_category = "difficulty"
            best_similarity = diff_match.similarity

        if lang_match and lang_match.similarity > best_similarity:
            best_match = lang_match
            best_category = "language"
            best_similarity = lang_match.similarity

        if not best_match or best_similarity < 0.50:
            return None

        print(f"[IntentTool] Embedding match: {best_category}={best_match.value} (sim={best_similarity:.2f})")

        # 결과 구성
        extracted = {}
        action = ActionType.ASK_RECOMMENDATION

        if best_category == "topic":
            extracted["topic"] = best_match.value
            action = ActionType.SET_TOPIC
        elif best_category == "difficulty":
            extracted["difficulty"] = best_match.value
            action = ActionType.SET_DIFFICULTY
        elif best_category == "language":
            extracted["language"] = best_match.value
            action = ActionType.SET_LANGUAGE

        # 다른 매칭도 추가 (복합 입력: "파이썬으로 DP 쉬운 거")
        if topic_match and topic_match.similarity >= 0.60:
            extracted["topic"] = topic_match.value
        if diff_match and diff_match.similarity >= 0.60:
            extracted["difficulty"] = diff_match.value
        if lang_match and lang_match.similarity >= 0.60:
            extracted["language"] = lang_match.value

        return IntentResult(
            category=IntentCategory.INFO_COLLECTION,
            action=action,
            confidence=best_similarity,
            extracted_values=extracted,
            suggested_route="collection",
        )

    async def _classify_with_llm(
        self,
        message: str,
        session_state: Dict[str, Any],
    ) -> IntentResult:
        """LLM 기반 분류 (Fallback)"""
        # 컨텍스트 구성
        context_parts = []
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
            response = await openrouter_service.chat_completion(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "당신은 의도 분류 전문가입니다. JSON으로만 응답하세요."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
                max_tokens=300,
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


# 싱글톤
intent_tool = IntentTool()
