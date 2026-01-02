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

    # Solving
    REQUEST_HINT = "request_hint"
    SUBMIT_CODE = "submit_code"
    ASK_QUESTION = "ask_question"
    GIVE_UP = "give_up"

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
- info_collection: 문제 조건 설정 중 (주제/난이도/언어 선택)
- discovery: 문제 탐색 중 (검색 결과에서 선택, 더 보기, 새로 생성)
- solving: 문제 풀이 중 (힌트 요청, 코드 제출, 질문)
- confirmation: 네/아니오 응답
- general: 인사, 감사, 일반 대화

### 2. 액션 (action)
**info_collection:**
- set_topic: 주제 선택 (DP, 그래프, 정렬 등)
- set_difficulty: 난이도 선택 (실버~마스터)
- set_language: 언어 선택 (python, java, cpp)
- ask_recommendation: 추천 요청 ("추천해줘", "뭐가 좋아?")

**discovery:**
- select_problem: 문제 선택 ("첫 번째", "1번", "맨 위 거")
- show_more: 더 보기 ("다른 거", "더 보여줘")
- select_problem_type: 문제 유형 선택 ("빈칸", "퍼즐", "대화형")

**solving:**
- request_hint: 힌트 요청 ("힌트", "모르겠어")
- ask_question: 질문 ("이게 뭐야?", "왜 틀렸어?")

**confirmation:**
- affirm: 긍정 ("네", "응", "좋아", "그걸로")
- negate: 부정 ("아니", "다른 거", "말고")

**general:**
- greeting: 인사
- thanks: 감사
- free_chat: 일반 대화

### 3. 값 추출 (extracted_values)
- topic: DP, 그래프, 정렬, 구현, 기초, 문자열 등
- difficulty: easy, medium, medium_hard, hard, very_hard
- language: python, java, cpp

## 응답 형식 (JSON)
{{
  "category": "info_collection|discovery|solving|confirmation|general",
  "action": "액션값",
  "confidence": 0.0-1.0,
  "extracted_values": {{"topic": null, "difficulty": null, "language": null}},
  "selection_index": null,
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
        메시지의 의도와 액션을 임베딩 기반으로 분류

        Args:
            message: 사용자 메시지
            session_state: 세션 상태 (current_step, awaiting_confirmation 등)

        Returns:
            IntentResult
        """
        session_state = session_state or {}
        msg_lower = message.lower().strip()
        msg_len = len(message)

        # ============================================================
        # 1. 확인 응답 처리 (awaiting_confirmation 상태에서 최우선)
        # ============================================================
        if session_state.get("awaiting_confirmation"):
            confirmation_result = await self._check_confirmation(message, session_state)
            if confirmation_result:
                return confirmation_result

        # ============================================================
        # 2. 문제 선택 (search_results 있을 때)
        # ============================================================
        if session_state.get("search_results"):
            selection_result = self._check_problem_selection(message, session_state)
            if selection_result:
                return selection_result

        # ============================================================
        # 2-1. 디스커버리 액션 감지 (새 문제 생성, 더 찾아보기)
        # ============================================================
        # 새 문제 생성 요청
        if any(kw in msg_lower for kw in ["새로운 유사", "새 문제 생성", "비슷한 문제 생성", "유사한 문제 생성", "새로운 문제"]):
            return IntentResult(
                category=IntentCategory.DISCOVERY,
                action=ActionType.GENERATE_NEW,
                confidence=0.95,
                suggested_route="discovery",
            )
        # 더 찾아보기 요청
        if any(kw in msg_lower for kw in ["더 찾아", "더 보여", "다른 문제", "다음 문제", "비슷한 문제 더"]):
            return IntentResult(
                category=IntentCategory.DISCOVERY,
                action=ActionType.SHOW_MORE,
                confidence=0.95,
                suggested_route="discovery",
            )

        # ============================================================
        # 3. 풀이 중 요청 (힌트, 요약, 질문 등)
        # ============================================================
        if session_state.get("current_problem"):
            # 문제 요약 요청
            if any(kw in msg_lower for kw in ["요약", "summary", "간단히", "정리", "문제 설명"]):
                return IntentResult(
                    category=IntentCategory.SOLVING,
                    action=ActionType.ASK_QUESTION,  # solving graph에서 summarize_problem으로 라우팅됨
                    confidence=0.95,
                    suggested_route="solving",
                )
            # 힌트 요청
            if any(h in msg_lower for h in ["힌트", "모르겠", "어려워", "도와줘"]):
                return IntentResult(
                    category=IntentCategory.SOLVING,
                    action=ActionType.REQUEST_HINT,
                    confidence=0.95,
                    suggested_route="solving",
                )

        # ============================================================
        # 4. 인사/감사 (짧은 메시지)
        # ============================================================
        if msg_len <= 15:
            if any(g in msg_lower for g in ["안녕", "하이", "hello", "hi"]):
                return IntentResult(
                    category=IntentCategory.GENERAL,
                    action=ActionType.GREETING,
                    confidence=0.95,
                    suggested_route="respond",
                )
            if any(t in msg_lower for t in ["고마워", "감사", "땡큐", "thanks"]):
                return IntentResult(
                    category=IntentCategory.GENERAL,
                    action=ActionType.THANKS,
                    confidence=0.95,
                    suggested_route="respond",
                )

        # ============================================================
        # 5. 학습 목표/레벨 언급 감지 (대기업, 코테, 취업 등)
        # ============================================================
        goal_result = self._check_goal_or_level_mention(message, session_state)
        if goal_result:
            return goal_result

        # ============================================================
        # 6. 임베딩 기반 주제/난이도/언어 감지
        # ============================================================
        embedding_result = await self._classify_with_embeddings(message, session_state)
        if embedding_result and embedding_result.confidence >= 0.70:
            return embedding_result

        # ============================================================
        # 6. LLM Fallback (복잡한 경우)
        # ============================================================
        return await self._classify_with_llm(message, session_state)

    async def _check_confirmation(
        self,
        message: str,
        session_state: Dict[str, Any],
    ) -> Optional[IntentResult]:
        """
        확인 응답 감지 (임베딩 기반)

        awaiting_confirmation=True 상태에서 "응", "네", "좋아" 등 감지
        """
        embeddings = self._get_embeddings_service()

        if not embeddings.is_initialized():
            # 임베딩 서비스 미초기화 시 간단한 키워드 체크
            return self._simple_confirmation_check(message, session_state)

        # 임베딩 기반 긍정/부정 감지
        is_positive, is_negative, confidence = await embeddings.match_confirmation(message)

        print(f"[IntentTool] Confirmation check: pos={is_positive}, neg={is_negative}, conf={confidence:.2f}")

        if is_positive and confidence >= 0.60:
            # 긍정 응답 + suggested_value가 있으면 해당 값 적용
            suggested_value = session_state.get("suggested_value")
            current_step = session_state.get("current_step", "topic")

            extracted = {}
            if suggested_value:
                # suggested_value를 현재 단계에 적용
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

    def _simple_confirmation_check(
        self,
        message: str,
        session_state: Dict[str, Any],
    ) -> Optional[IntentResult]:
        """임베딩 서비스 미초기화 시 간단한 키워드 체크"""
        msg_lower = message.lower().strip()

        # 긍정 키워드
        positive_keywords = [
            "응", "어", "네", "예", "넵", "넹", "ㅇㅇ", "ㅇㅋ", "ok", "yes",
            "좋아", "좋아요", "그래", "그렇게", "할게", "할래", "해줘",
            "맞아", "동의", "확인", "오케이", "굳", "굿", "ㄱㄱ",
        ]

        # 부정 키워드
        negative_keywords = [
            "아니", "아뇨", "ㄴㄴ", "no", "싫어", "별로", "다른",
            "말고", "바꿔", "다시", "패스", "스킵",
        ]

        for kw in positive_keywords:
            if kw in msg_lower or msg_lower == kw:
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
                    confidence=0.95,
                    extracted_values=extracted,
                    suggested_route="collection",
                )

        for kw in negative_keywords:
            if kw in msg_lower or msg_lower == kw:
                return IntentResult(
                    category=IntentCategory.CONFIRMATION,
                    action=ActionType.NEGATE,
                    confidence=0.95,
                    suggested_route="collection",
                )

        return None

    def _check_goal_or_level_mention(
        self,
        message: str,
        session_state: Dict[str, Any],
    ) -> Optional[IntentResult]:
        """
        학습 목표나 레벨 언급 감지

        "대기업 코테", "취업 준비", "입문자", "초보" 등
        → 이 정보를 컨텍스트에 반영하고 개인화 추천으로 연결
        """
        msg_lower = message.lower().strip()

        extracted = {}

        # ============================================================
        # 학습 목표 (learning_goal) 감지
        # ============================================================
        # 대기업 목표
        if any(kw in msg_lower for kw in ["대기업", "빅테크", "네카라쿠배", "삼성", "카카오", "네이버", "라인"]):
            extracted["learning_goal"] = "big_tech"

        # 스타트업/중소기업 목표
        elif any(kw in msg_lower for kw in ["스타트업", "중소기업", "중견기업", "실무"]):
            extracted["learning_goal"] = "mid_startup"

        # 실력 향상 목표
        elif any(kw in msg_lower for kw in ["실력 향상", "공부", "학습", "배우", "연습"]):
            extracted["learning_goal"] = "skill_up"

        # ============================================================
        # 경험 레벨 (experience_level) 감지
        # ============================================================
        # 입문자/초보
        if any(kw in msg_lower for kw in ["입문", "초보", "초심자", "처음", "시작", "기초부터"]):
            extracted["experience_level"] = "beginner"

        # 초급
        elif any(kw in msg_lower for kw in ["초급", "기본", "쉬운 것부터"]):
            extracted["experience_level"] = "elementary"

        # 중급
        elif any(kw in msg_lower for kw in ["중급", "어느정도", "좀 해봤", "경험 있"]):
            extracted["experience_level"] = "intermediate"

        # 고급
        elif any(kw in msg_lower for kw in ["고급", "어려운", "상급", "챌린지", "전문"]):
            extracted["experience_level"] = "advanced"

        # ============================================================
        # 코딩 테스트 관련 키워드
        # ============================================================
        if any(kw in msg_lower for kw in ["코테", "코딩테스트", "코딩 테스트", "알고리즘 테스트"]):
            # 코테 언급 시 기본적으로 big_tech 목표로 설정 (없으면)
            if "learning_goal" not in extracted:
                extracted["learning_goal"] = "big_tech"

        # 추출된 값이 있으면 INFO_COLLECTION으로 분류
        if extracted:
            print(f"[IntentTool] Goal/Level detected: {extracted}")
            return IntentResult(
                category=IntentCategory.INFO_COLLECTION,
                action=ActionType.ASK_RECOMMENDATION,
                confidence=0.85,
                extracted_values=extracted,
                suggested_route="collection",
            )

        return None

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
        """문제 유형 선택 감지"""
        msg_lower = message.lower()

        if any(k in msg_lower for k in ["빈칸", "빈 칸", "blank", "채우기"]):
            return "blank"
        if any(k in msg_lower for k in ["퍼즐", "puzzle", "파슨스", "parsons", "블록"]):
            return "puzzle"
        if any(k in msg_lower for k in ["대화", "guided", "가이드", "1대1", "튜터"]):
            return "guided"

        return None


# 싱글톤
intent_tool = IntentTool()
