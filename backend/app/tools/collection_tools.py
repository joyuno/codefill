"""
Collection Tools

정보 수집 단계에서 사용하는 LLM 기반 도구들
- 임베딩 1차 매칭 + LLM 보조로 정확도 향상
- Structured output으로 안정적인 값 추출
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Literal
import json

from ..services.openrouter import openrouter_service
from ..services.collection_embeddings import get_collection_embeddings_service


# ============================================================
# 결과 데이터 클래스
# ============================================================

@dataclass
class ExtractionResult:
    """값 추출 결과"""
    values: Dict[str, Optional[str]]  # {"topic": "DP", "difficulty": None, "language": "python"}
    confidence: float                  # 전체 신뢰도 (0~1)
    extraction_type: str              # "embedding" | "llm" | "hybrid"
    details: Optional[Dict] = None    # 추가 정보 (매칭된 변형 등)


@dataclass
class ConfirmationResult:
    """긍정/부정 응답 분석 결과"""
    response: Literal["positive", "negative", "unclear"]
    confidence: float
    extracted_value: Optional[str] = None  # 긍정하면서 언급한 값 ("정렬 좋아" → "정렬")
    has_additional_info: bool = False       # 다른 정보도 포함 ("정렬 쉬운 거로" → True)
    additional_values: Optional[Dict[str, str]] = None  # {"difficulty": "easy"}


@dataclass
class RejectionResult:
    """거절 분석 결과"""
    reason: Optional[str]             # "too_hard" | "too_easy" | "already_done" | "not_interested" | "want_different"
    alternative: Optional[str]        # 대안 값 ("DP 말고 그래프" → "그래프")
    alternative_step: Optional[str]   # 대안이 어떤 단계 값인지 ("topic" | "difficulty" | "language")
    confidence: float
    suggested_action: Optional[str] = None  # "show_options" | "suggest_easier" | "suggest_different"


# ============================================================
# 프롬프트 정의 (통합)
# ============================================================

UNIFIED_ANALYSIS_PROMPT = """당신은 코딩 문제 추천 시스템의 메시지 분석기입니다.
사용자 메시지를 분석하여 의도, 값, 거부 여부를 한 번에 판단하세요.

## 1. 의도 분류 (intent)
- "positive": 긍정/동의 ("네", "응", "좋아", "그래", "ㅇㅇ", "굳", "할게", "해줘", "시작")
- "negative": 부정/거절 ("아니", "싫어", "말고", "다른거", "패스", "ㄴㄴ", "별로")
- "value_input": 새 값 제시 ("DP로 해줘", "정렬", "파이썬", "쉬운 거")
- "unclear": 질문/애매 ("그게 뭐야?", "음...", "모르겠어")

## 2. 값 추출 (원하는 값만!)
- **topic**: DP, 그래프, BFS/DFS, 정렬, 이분탐색, 그리디, 구현, 문자열, 기초, 수학, 스택/큐, 트리, 해시, 백트래킹
- **difficulty**: easy(실버/쉬운), medium(골드/보통), medium_hard(플래티넘), hard(다이아/어려운), very_hard(마스터)
- **language**: python(파이썬), java(자바), cpp(씨플플/C++)

## 3. 거부 분석 (intent=negative일 때)
**거부 이유** (rejection_reason):
- "too_hard": 어려움 ("어려워", "힘들어")
- "too_easy": 쉬움 ("쉬워", "심심해")
- "already_done": 해봤음 ("했어", "풀었어")
- "not_interested": 관심없음 ("별로", "재미없어")
- "want_different": 다른것 원함 ("다른거", "말고")
- "want_choose": 직접 선택 ("목록", "골라")

**거절된 값** (rejected): "X 싫다", "X 말고" → rejected에 X 기록

**대안** (alternative): "X 말고 Y로" → alternative에 Y 기록

## 핵심 규칙
1. 거부하는 값은 values에 넣지 말 것! (rejected에만 기록)
2. "기초 싫다" → values.topic=null, rejected.topic="기초"
3. "기초 말고 DP" → values.topic="DP", rejected.topic="기초"
4. 동의어 인식: "다이나믹"="DP", "실버"="easy"

## JSON 응답 형식
{
  "intent": "positive" | "negative" | "value_input" | "unclear",
  "confidence": 0.0-1.0,
  "values": {
    "topic": "DP" | null,
    "difficulty": "easy" | "medium" | "medium_hard" | "hard" | "very_hard" | null,
    "language": "python" | "java" | "cpp" | null
  },
  "rejected": {
    "topic": "string" | null,
    "difficulty": "string" | null,
    "language": "string" | null
  },
  "rejection_reason": "too_hard" | "too_easy" | "already_done" | "not_interested" | "want_different" | "want_choose" | null,
  "alternative": {
    "value": "string" | null,
    "step": "topic" | "difficulty" | "language" | null
  }
}"""


# ============================================================
# Collection Tool 클래스
# ============================================================

@dataclass
class UnifiedAnalysisResult:
    """통합 분석 결과"""
    intent: Literal["positive", "negative", "value_input", "unclear"]
    confidence: float
    values: Dict[str, Optional[str]]      # {"topic": "DP", "difficulty": null, ...}
    rejected: Dict[str, Optional[str]]    # {"topic": "기초", ...}
    rejection_reason: Optional[str]       # "too_hard", "want_different", ...
    alternative: Optional[Dict[str, str]] # {"value": "DP", "step": "topic"}


class CollectionTool:
    """정보 수집용 통합 Tool"""

    def __init__(self):
        self._embedding_service = None
        self._analysis_cache: Dict[str, UnifiedAnalysisResult] = {}  # 메시지별 캐시

    @property
    def embedding_service(self):
        """임베딩 서비스 lazy loading"""
        if self._embedding_service is None:
            self._embedding_service = get_collection_embeddings_service()
        return self._embedding_service

    # ============================================================
    # 통합 분석 메서드 (핵심)
    # ============================================================

    async def analyze(
        self,
        message: str,
        context: Optional[str] = None,
    ) -> UnifiedAnalysisResult:
        """
        메시지 통합 분석 (1회 LLM 호출로 모든 정보 추출)

        Returns:
            UnifiedAnalysisResult with intent, values, rejected, rejection_reason, alternative
        """
        # 캐시 확인 (동일 메시지 중복 호출 방지)
        cache_key = f"{message}:{context or ''}"
        if cache_key in self._analysis_cache:
            return self._analysis_cache[cache_key]

        try:
            prompt = UNIFIED_ANALYSIS_PROMPT
            user_content = f"메시지: {message}"
            if context:
                user_content = f"컨텍스트: {context}\n{user_content}"

            response = await openrouter_service.chat_completion(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": user_content}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )

            content = openrouter_service.get_content(response)
            result = json.loads(content)

            # 값 정규화
            values = result.get("values", {})
            normalized_values = {
                "topic": self._normalize_topic(values.get("topic")) if values.get("topic") else None,
                "difficulty": self._normalize_difficulty(values.get("difficulty")) if values.get("difficulty") else None,
                "language": self._normalize_language(values.get("language")) if values.get("language") else None,
            }

            rejected = result.get("rejected", {})
            alternative = result.get("alternative", {})
            if alternative and alternative.get("value"):
                step = alternative.get("step")
                if step:
                    alternative["value"] = self._normalize_value(step, alternative["value"])

            analysis = UnifiedAnalysisResult(
                intent=result.get("intent", "unclear"),
                confidence=result.get("confidence", 0.5),
                values=normalized_values,
                rejected=rejected,
                rejection_reason=result.get("rejection_reason"),
                alternative=alternative if alternative.get("value") else None,
            )

            # 캐시 저장 (최대 100개)
            if len(self._analysis_cache) > 100:
                self._analysis_cache.clear()
            self._analysis_cache[cache_key] = analysis

            print(f"[CollectionTool] Unified analysis: intent={analysis.intent}, values={analysis.values}")
            return analysis

        except Exception as e:
            print(f"[CollectionTool] Unified analysis error: {e}")
            return UnifiedAnalysisResult(
                intent="unclear",
                confidence=0.0,
                values={"topic": None, "difficulty": None, "language": None},
                rejected={},
                rejection_reason=None,
                alternative=None,
            )

    # ============================================================
    # 1. 값 추출 Tool (통합 분석 사용)
    # ============================================================

    async def extract_values(
        self,
        message: str,
        current_step: str = "topic",
        existing_values: Optional[Dict[str, str]] = None,
        use_llm_fallback: bool = True,
    ) -> ExtractionResult:
        """
        메시지에서 topic/difficulty/language 값 추출 (통합 분석 사용)

        Args:
            message: 사용자 메시지
            current_step: 현재 수집 단계 (우선순위 결정용)
            existing_values: 이미 수집된 값 (덮어쓰기 방지)
            use_llm_fallback: LLM 사용 여부 (기본 True)

        Returns:
            ExtractionResult
        """
        existing_values = existing_values or {}

        # LLM First: 통합 분석 사용
        if use_llm_fallback:
            analysis = await self.analyze(message)

            # 거부된 값이 있으면 details에 기록
            details = {"unified_analysis": True}
            if analysis.rejected:
                for step, rejected_val in analysis.rejected.items():
                    if rejected_val:
                        details["is_rejection"] = True
                        details["rejected_step"] = step
                        details["rejected_value"] = rejected_val
                        print(f"[CollectionTool] Rejection detected: {step}={rejected_val}")

            # 신뢰도 높으면 바로 반환
            if analysis.confidence >= 0.60:
                return ExtractionResult(
                    values=analysis.values,
                    confidence=analysis.confidence,
                    extraction_type="unified_llm",
                    details=details
                )

        # Fallback: 임베딩 기반 매칭 (LLM 실패 시)
        embedding_result = await self._extract_with_embedding(message, current_step)

        current_value = embedding_result.values.get(current_step)
        if current_value and embedding_result.confidence >= 0.75:
            return embedding_result

        # 둘 다 낮은 신뢰도면 LLM 결과 우선
        if use_llm_fallback:
            analysis = await self.analyze(message)
            return ExtractionResult(
                values=analysis.values,
                confidence=analysis.confidence,
                extraction_type="unified_llm",
                details={"unified_analysis": True}
            )
        return embedding_result

    async def _extract_with_embedding(
        self,
        message: str,
        current_step: str,
    ) -> ExtractionResult:
        """임베딩 기반 값 추출 (fallback용)"""
        values = {"topic": None, "difficulty": None, "language": None}
        details = {}
        max_confidence = 0.0

        if not self.embedding_service.is_initialized():
            return ExtractionResult(
                values=values,
                confidence=0.0,
                extraction_type="embedding",
                details={"error": "not_initialized"}
            )

        try:
            matches = await self.embedding_service.match_all(message)

            for category in ["topic", "difficulty", "language"]:
                match = matches.get(category)
                if match and match.similarity >= 0.65:
                    values[category] = match.value
                    details[category] = {
                        "matched_variant": match.matched_variant,
                        "similarity": match.similarity
                    }
                    max_confidence = max(max_confidence, match.similarity)

            current_match = matches.get(current_step)
            if current_match:
                max_confidence = max(max_confidence, current_match.similarity)

            return ExtractionResult(
                values=values,
                confidence=max_confidence,
                extraction_type="embedding",
                details=details
            )

        except Exception as e:
            print(f"[CollectionTool] Embedding extraction error: {e}")
            return ExtractionResult(
                values=values,
                confidence=0.0,
                extraction_type="embedding",
                details={"error": str(e)}
            )

    # ============================================================
    # 2. 긍정/부정 응답 분석 Tool (통합 분석 사용)
    # ============================================================

    async def analyze_confirmation(
        self,
        message: str,
        awaiting_value: Optional[str] = None,
        current_step: str = "topic",
    ) -> ConfirmationResult:
        """
        긍정/부정 응답 분석 (통합 분석 사용)

        Args:
            message: 사용자 메시지
            awaiting_value: 확인 대기 중인 값 (예: "DP")
            current_step: 현재 수집 단계

        Returns:
            ConfirmationResult
        """
        # 통합 분석 사용 (1회 LLM 호출로 모든 정보 추출)
        context = f"현재 '{awaiting_value}' 추천에 대한 응답" if awaiting_value else None
        analysis = await self.analyze(message, context)

        # intent → response 매핑
        response_map = {
            "positive": "positive",
            "negative": "negative",
            "value_input": "positive",  # 값 입력도 긍정적 진행
            "unclear": "unclear",
        }
        response = response_map.get(analysis.intent, "unclear")

        # 추가 값 확인
        additional_values = {k: v for k, v in analysis.values.items() if v}
        has_additional = bool(additional_values)
        extracted_value = analysis.values.get(current_step)

        result = ConfirmationResult(
            response=response,
            confidence=analysis.confidence,
            extracted_value=extracted_value,
            has_additional_info=has_additional,
            additional_values=additional_values if has_additional else None
        )

        # LLM 신뢰도 높으면 바로 반환
        if analysis.confidence >= 0.70:
            return result

        # Fallback: 임베딩 기반 체크 (LLM 신뢰도 낮을 때만)
        embedding_result = await self._check_confirmation_embedding(message)
        if embedding_result.confidence >= 0.85:
            # 임베딩 결과에 추가 값 정보 병합
            if embedding_result.response == "positive" and has_additional:
                embedding_result.has_additional_info = True
                embedding_result.additional_values = additional_values
                embedding_result.extracted_value = extracted_value
            return embedding_result

        return result

    async def _check_confirmation_embedding(self, message: str) -> ConfirmationResult:
        """임베딩 기반 긍정/부정 체크 (fallback용)"""
        if not self.embedding_service.is_initialized():
            return ConfirmationResult(response="unclear", confidence=0.0)

        try:
            is_positive, is_negative, confidence = await self.embedding_service.match_confirmation(message)

            if is_positive:
                return ConfirmationResult(response="positive", confidence=confidence)
            elif is_negative:
                return ConfirmationResult(response="negative", confidence=confidence)
            else:
                return ConfirmationResult(response="unclear", confidence=confidence)

        except Exception as e:
            print(f"[CollectionTool] Confirmation embedding error: {e}")
            return ConfirmationResult(response="unclear", confidence=0.0)

    # ============================================================
    # 3. 거절 분석 Tool (통합 분석 사용)
    # ============================================================

    async def analyze_rejection(
        self,
        message: str,
        current_step: str = "topic",
        rejected_values: Optional[List[str]] = None,
    ) -> RejectionResult:
        """
        거절 메시지 분석 (통합 분석 사용)

        Args:
            message: 사용자 메시지
            current_step: 현재 수집 단계
            rejected_values: 이미 거절된 값들

        Returns:
            RejectionResult
        """
        rejected_values = rejected_values or []

        # 통합 분석 사용
        context = f"현재 단계: {current_step}, 이미 거절된 값: {rejected_values}"
        analysis = await self.analyze(message, context)

        # 대안 추출
        alternative = None
        alternative_step = None
        if analysis.alternative:
            alternative = analysis.alternative.get("value")
            alternative_step = analysis.alternative.get("step")
        elif analysis.values.get(current_step):
            # alternative 필드가 없으면 values에서 추출
            alternative = analysis.values.get(current_step)
            alternative_step = current_step

        # 이미 거절된 값이면 제외
        if alternative and alternative in rejected_values:
            alternative = None
            alternative_step = None

        # suggested_action 결정
        suggested_action = None
        if analysis.rejection_reason == "too_hard":
            suggested_action = "suggest_easier"
        elif analysis.rejection_reason == "too_easy":
            suggested_action = "suggest_harder"
        elif analysis.rejection_reason == "want_choose":
            suggested_action = "show_options"
        elif alternative:
            suggested_action = "suggest_different"

        result = RejectionResult(
            reason=analysis.rejection_reason or "want_different",
            alternative=alternative,
            alternative_step=alternative_step,
            confidence=analysis.confidence,
            suggested_action=suggested_action
        )

        # 신뢰도 높으면 바로 반환
        if analysis.confidence >= 0.70:
            return result

        # Fallback: 임베딩으로 대안 값 추출 시도
        extraction = await self._extract_with_embedding(message, current_step)
        emb_alternative = extraction.values.get(current_step)
        if emb_alternative and emb_alternative not in rejected_values:
            result.alternative = emb_alternative
            result.alternative_step = current_step
            result.confidence = max(result.confidence, extraction.confidence)
            result.suggested_action = "suggest_different"

        return result

    # ============================================================
    # Helper 메서드
    # ============================================================

    def _merge_values(
        self,
        values1: Dict[str, Optional[str]],
        values2: Dict[str, Optional[str]],
    ) -> Dict[str, Optional[str]]:
        """두 결과 병합 (None이 아닌 값 우선)"""
        merged = {}
        for key in ["topic", "difficulty", "language"]:
            merged[key] = values1.get(key) or values2.get(key)
        return merged

    def _normalize_value(self, step: str, value: str) -> Optional[str]:
        """단계별 값 정규화"""
        if step == "topic":
            return self._normalize_topic(value)
        elif step == "difficulty":
            return self._normalize_difficulty(value)
        elif step == "language":
            return self._normalize_language(value)
        return value

    def _normalize_topic(self, value: str) -> Optional[str]:
        """주제 정규화"""
        if not value:
            return None

        value_lower = value.lower()

        # 정규화 매핑
        TOPIC_MAP = {
            "dp": "DP", "dynamic programming": "DP", "다이나믹": "DP", "동적": "DP",
            "그래프": "그래프", "graph": "그래프",
            "bfs": "BFS/DFS", "dfs": "BFS/DFS", "bfs/dfs": "BFS/DFS", "탐색": "BFS/DFS",
            "정렬": "정렬", "sort": "정렬", "sorting": "정렬",
            "이분탐색": "이분탐색", "binary search": "이분탐색", "이진탐색": "이분탐색",
            "그리디": "그리디", "greedy": "그리디",
            "구현": "구현", "implementation": "구현", "브루트포스": "구현",
            "문자열": "문자열", "string": "문자열",
            "기초": "기초", "basic": "기초", "기본": "기초",
            "수학": "수학", "math": "수학",
            "스택/큐": "스택/큐", "스택": "스택/큐", "큐": "스택/큐", "stack": "스택/큐", "queue": "스택/큐",
            "트리": "트리", "tree": "트리",
            "해시": "해시", "hash": "해시",
            "백트래킹": "백트래킹", "backtracking": "백트래킹",
        }

        return TOPIC_MAP.get(value_lower, value)

    def _normalize_difficulty(self, value: str) -> Optional[str]:
        """난이도 정규화"""
        if not value:
            return None

        value_lower = value.lower()

        DIFF_MAP = {
            # 티어
            "실버": "easy", "silver": "easy",
            "골드": "medium", "gold": "medium",
            "플래티넘": "medium_hard", "플레티넘": "medium_hard", "platinum": "medium_hard",
            "다이아": "hard", "다이아몬드": "hard", "diamond": "hard",
            "마스터": "very_hard", "master": "very_hard",
            # 일반
            "쉬움": "easy", "쉬운": "easy", "easy": "easy", "초급": "easy",
            "중간": "medium", "보통": "medium", "medium": "medium", "중급": "medium",
            "medium_hard": "medium_hard",
            "어려움": "hard", "어려운": "hard", "hard": "hard", "고급": "hard",
            "very_hard": "very_hard",
        }

        return DIFF_MAP.get(value_lower, value)

    def _normalize_language(self, value: str) -> Optional[str]:
        """언어 정규화"""
        if not value:
            return None

        value_lower = value.lower()

        LANG_MAP = {
            "파이썬": "python", "python": "python", "py": "python",
            "자바": "java", "java": "java",
            "씨플플": "cpp", "c++": "cpp", "cpp": "cpp",
        }

        return LANG_MAP.get(value_lower, value)


# 싱글톤 인스턴스
collection_tool = CollectionTool()
