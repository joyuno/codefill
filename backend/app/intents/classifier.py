"""
Intent Classifier
Embedding 기반 + LLM Fallback 하이브리드 의도 분류기
"""

import numpy as np
import json
import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

from .definitions import INTENT_DEFINITIONS, IntentType, CONTEXT_REQUIREMENTS
from ..config import get_settings
from ..services.embedding import embedding_service
from ..services.openrouter import openrouter_service
from ..services.moderation import moderation_service

# LLM 모델 설정
settings = get_settings()


@dataclass
class IntentResult:
    """의도 분류 결과"""
    intent: IntentType
    confidence: float
    method: str  # "embedding" | "llm" | "rule" | "fallback"
    requires_context: Optional[str] = None
    next_action: Optional[str] = None
    alternatives: Optional[List[Tuple[IntentType, float]]] = None


class IntentClassifier:
    """
    하이브리드 의도 분류기 (LLM First)

    분류 순서:
    1. Moderation API (유해 콘텐츠 필터링)
    2. Rule-based (코드 블록 등 구조적 패턴만)
    3. Embedding similarity (빠르고 저렴)
    4. LLM verification/classification (정확도 보완)
    """

    # 임계값 설정
    HIGH_CONFIDENCE_THRESHOLD = 0.85  # 이 이상이면 바로 결정
    MEDIUM_CONFIDENCE_THRESHOLD = 0.65  # 이 이상이면 LLM 확인
    LOW_CONFIDENCE_THRESHOLD = 0.50  # 이 미만이면 clarification

    def __init__(self):
        self.intent_embeddings: Dict[str, np.ndarray] = {}
        self.is_initialized = False

    async def initialize(self):
        """
        의도별 임베딩 사전 생성
        서버 시작 시 한 번만 호출
        """
        if self.is_initialized:
            return

        print("Initializing intent embeddings...")

        for intent_type, definition in INTENT_DEFINITIONS.items():
            examples = definition.get("examples", [])
            if not examples:
                continue

            try:
                # 예시 문장들의 임베딩 생성
                embeddings = await embedding_service.generate_embeddings_batch(examples)

                # 평균 벡터로 대표 임베딩 생성
                mean_embedding = np.mean(embeddings, axis=0)
                self.intent_embeddings[intent_type.value if hasattr(intent_type, 'value') else intent_type] = mean_embedding

                print(f"  ✓ {intent_type}: {len(examples)} examples embedded")

            except Exception as e:
                print(f"  ✗ {intent_type}: Failed - {e}")

        self.is_initialized = True
        print(f"Intent embeddings initialized: {len(self.intent_embeddings)} intents")

    async def classify(
        self,
        message: str,
        session_context: Optional[Dict[str, Any]] = None
    ) -> IntentResult:
        """
        메시지 의도 분류 (메인 메서드)

        Args:
            message: 사용자 메시지
            session_context: 세션 컨텍스트 (last_solved_problem, recent_problems 등)

        Returns:
            IntentResult
        """
        session_context = session_context or {}

        # Step 0: OpenAI Moderation API로 유해 콘텐츠 체크 (무료)
        moderation_result = await moderation_service.check(message)
        if moderation_result.is_flagged:
            print(f"[IntentClassifier] Moderation flagged: {moderation_result.reason}")
            return IntentResult(
                intent=IntentType.INAPPROPRIATE_MESSAGE,
                confidence=0.95,
                method="moderation_api",
                next_action="redirect_politely"
            )

        # Step 1: Rule-based 빠른 체크 (특수 패턴)
        rule_result = self._check_rules(message)
        if rule_result:
            return rule_result

        # Step 2: Embedding 기반 유사도 분류
        if not self.is_initialized:
            await self.initialize()

        embedding_result = await self._classify_by_embedding(message)

        # Step 3: 신뢰도에 따른 처리
        if embedding_result.confidence >= self.HIGH_CONFIDENCE_THRESHOLD:
            # 높은 신뢰도 → 바로 반환
            return self._enrich_result(embedding_result, session_context)

        elif embedding_result.confidence >= self.MEDIUM_CONFIDENCE_THRESHOLD:
            # 중간 신뢰도 → LLM 확인
            llm_result = await self._verify_with_llm(
                message, embedding_result, session_context
            )
            return self._enrich_result(llm_result, session_context)

        else:
            # 낮은 신뢰도 → LLM으로 직접 분류
            llm_result = await self._classify_with_llm(message, session_context)
            return self._enrich_result(llm_result, session_context)

    def _check_rules(self, message: str) -> Optional[IntentResult]:
        """
        규칙 기반 최소 분류 (구조적 패턴만)

        LLM First 원칙:
        - 의미 분석은 LLM/임베딩이 담당
        - 여기서는 구조적 패턴(코드 블록)만 감지
        - 나머지는 embedding → LLM 흐름으로 처리
        """
        # 코드 블록 포함 여부 (구조적 감지)
        has_code_block = bool(re.search(r'```[\w]*\n.*\n```', message, re.DOTALL))

        if has_code_block:
            message_lower = message.lower()
            # 코드 블록 + 유사 문제 요청
            if any(kw in message_lower for kw in ["비슷한", "유사한", "이 코드"]):
                return IntentResult(
                    intent=IntentType.SIMILAR_CODE_PROBLEM,
                    confidence=0.95,
                    method="rule",
                    requires_context="code",
                    next_action="code_similarity_search"
                )

            # 코드 블록 + 리뷰 요청
            if any(kw in message_lower for kw in ["봐줘", "확인", "맞아?", "리뷰", "틀린"]):
                return IntentResult(
                    intent=IntentType.CODE_REVIEW,
                    confidence=0.90,
                    method="rule",
                    requires_context="code",
                    next_action="review_code"
                )

        # 나머지는 LLM/임베딩 흐름으로 (키워드 패턴 제거)
        return None

    async def _classify_by_embedding(self, message: str) -> IntentResult:
        """
        Embedding 유사도 기반 분류
        """
        # 메시지 임베딩 생성
        message_embedding = await embedding_service.generate_embedding(message)
        message_embedding = np.array(message_embedding)

        # 각 의도와 유사도 계산
        similarities = {}
        for intent_name, intent_embedding in self.intent_embeddings.items():
            similarity = self._cosine_similarity(message_embedding, intent_embedding)
            similarities[intent_name] = similarity

        # 정렬
        sorted_intents = sorted(similarities.items(), key=lambda x: x[1], reverse=True)

        best_intent_name, best_score = sorted_intents[0]
        best_intent = IntentType(best_intent_name)

        # 상위 3개 대안
        alternatives = [
            (IntentType(name), score)
            for name, score in sorted_intents[1:4]
        ]

        return IntentResult(
            intent=best_intent,
            confidence=best_score,
            method="embedding",
            alternatives=alternatives
        )

    async def _verify_with_llm(
        self,
        message: str,
        embedding_result: IntentResult,
        session_context: Dict
    ) -> IntentResult:
        """
        LLM으로 임베딩 결과 검증
        """
        # 후보 의도들
        candidates = [embedding_result.intent]
        if embedding_result.alternatives:
            candidates.extend([alt[0] for alt in embedding_result.alternatives[:2]])

        candidate_descriptions = [
            f"- {c.value}: {INTENT_DEFINITIONS.get(c, {}).get('description', '')}"
            for c in candidates
        ]

        prompt = f"""사용자 메시지를 분석하여 의도를 판단해주세요.

메시지: "{message}"

후보 의도들:
{chr(10).join(candidate_descriptions)}

세션 정보:
- 최근 푼 문제 있음: {bool(session_context.get('last_solved_problem'))}
- 코드 포함: {'```' in message}

응답: {{"intent": "의도값", "confidence": 0.0-1.0}}"""

        try:
            response = await openrouter_service.chat_completion(
                model=settings.llm_model_intent,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,  # 분류는 결정적이어야 함
                max_tokens=100,   # 간단한 JSON 응답
                response_format={"type": "json_object"},
            )
            content = openrouter_service.get_content(response)
            result = openrouter_service.parse_json_response(content)

            verified_intent = IntentType(result.get("intent", embedding_result.intent.value))
            confidence = float(result.get("confidence", 0.8))

            return IntentResult(
                intent=verified_intent,
                confidence=min(confidence, 0.95),
                method="llm_verified",
                alternatives=embedding_result.alternatives
            )

        except Exception as e:
            print(f"LLM verification failed: {e}")
            return embedding_result

    async def _classify_with_llm(
        self,
        message: str,
        session_context: Dict
    ) -> IntentResult:
        """
        LLM으로 직접 분류 (낮은 신뢰도 시)
        """
        # 모든 의도 설명
        all_intents = [
            f"- {intent.value}: {defn.get('description', '')}"
            for intent, defn in INTENT_DEFINITIONS.items()
            if defn.get('examples')  # 예시가 있는 의도만
        ]

        prompt = f"""사용자 메시지의 의도를 분류해주세요.

메시지: "{message}"

세션 정보:
- 최근 푼 문제: {session_context.get('last_solved_problem', {}).get('title', '없음')}
- 이전 제안: {session_context.get('last_suggestion', '없음')}

가능한 의도들:
{chr(10).join(all_intents[:15])}  # 상위 15개만

분류 가이드:
- "싫다", "싫다고", "짜증나", "지겨워" 등 부정적 감정 → negation (거절/대안 요청)
- "기초 싫다", "쉬운거 말고" 등 특정 조건 거부 → negation
- 주제/난이도 변경 원할 때도 → negation (다른 대안 제시 필요)

응답: {{"intent": "의도값", "confidence": 0.0-1.0}}
불명확 시 "clarification_needed" 사용."""

        try:
            response = await openrouter_service.chat_completion(
                model=settings.llm_model_intent,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,  # 분류는 결정적이어야 함
                max_tokens=100,   # 간단한 JSON 응답
                response_format={"type": "json_object"},
            )
            content = openrouter_service.get_content(response)
            result = openrouter_service.parse_json_response(content)

            intent_value = result.get("intent", "clarification_needed")
            try:
                classified_intent = IntentType(intent_value)
            except ValueError:
                classified_intent = IntentType.CLARIFICATION_NEEDED

            return IntentResult(
                intent=classified_intent,
                confidence=float(result.get("confidence", 0.7)),
                method="llm"
            )

        except Exception as e:
            print(f"LLM classification failed: {e}")
            return IntentResult(
                intent=IntentType.CLARIFICATION_NEEDED,
                confidence=0.5,
                method="fallback"
            )

    def _enrich_result(
        self,
        result: IntentResult,
        session_context: Dict
    ) -> IntentResult:
        """
        결과에 추가 정보 보강
        """
        intent_def = INTENT_DEFINITIONS.get(result.intent, {})

        # 필요한 컨텍스트
        result.requires_context = intent_def.get("required_context")

        # 다음 액션
        result.next_action = intent_def.get("next_action")

        # 컨텍스트 체크
        if result.requires_context == "code":
            has_code = (
                session_context.get("last_solved_problem", {}).get("code") or
                "```" in session_context.get("message", "")
            )
            if not has_code:
                result.next_action = "request_code_context"

        elif result.requires_context == "problem":
            has_problem = bool(session_context.get("current_problem"))
            if not has_problem:
                result.next_action = "request_problem_context"

        return result

    @staticmethod
    def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
        """코사인 유사도 계산"""
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

    def extract_code_from_message(self, message: str) -> Optional[Tuple[str, str]]:
        """
        메시지에서 코드 블록 추출

        Returns:
            (language, code) or None
        """
        match = re.search(r'```(\w*)\n(.*?)\n```', message, re.DOTALL)
        if match:
            language = match.group(1) or "python"
            code = match.group(2)
            return (language, code)
        return None

    def extract_problem_reference(self, message: str) -> Optional[str]:
        """
        메시지에서 문제 참조 추출
        예: "피보나치 문제랑 비슷한" → "피보나치"
        """
        patterns = [
            r'([가-힣a-zA-Z0-9]+)\s*문제',
            r'([가-힣a-zA-Z0-9]+)\s*랑\s*비슷',
            r'아까\s+([가-힣a-zA-Z0-9]+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, message)
            if match:
                return match.group(1)

        return None


# 싱글톤 인스턴스
intent_classifier = IntentClassifier()
