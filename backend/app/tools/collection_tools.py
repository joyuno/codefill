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
# 프롬프트 정의
# ============================================================

EXTRACTION_SYSTEM_PROMPT = """당신은 코딩 문제 추천 시스템의 입력 분석기입니다.
사용자 메시지에서 다음 정보를 추출하세요:

1. **topic** (주제): DP, 그래프, BFS/DFS, 정렬, 이분탐색, 그리디, 구현, 문자열, 기초, 수학, 스택/큐, 트리, 해시, 백트래킹
2. **difficulty** (난이도): easy(실버), medium(골드), medium_hard(플래티넘), hard(다이아), very_hard(마스터)
3. **language** (언어): python, java, cpp

규칙:
- 명시적으로 언급된 값만 추출
- 추측하지 말 것
- 동의어 인식: "다이나믹"="DP", "파이썬"="python", "쉬운"="easy" 등
- 한국어 슬랭 인식: "씨플플"="cpp", "자바"="java"
- 값이 없으면 null

JSON 형식으로만 응답:
{
  "topic": "DP" | null,
  "difficulty": "easy" | "medium" | "medium_hard" | "hard" | "very_hard" | null,
  "language": "python" | "java" | "cpp" | null,
  "confidence": 0.0-1.0
}"""

CONFIRMATION_SYSTEM_PROMPT = """당신은 사용자 응답 분석기입니다.
사용자가 추천에 대해 긍정/부정으로 응답했는지 판단하세요.

**긍정 표현** (response="positive"):
- 명시적: "네", "응", "예", "좋아", "그래", "ok", "ㅇㅇ"
- 슬랭: "굳", "ㄱㄱ", "오키", "고고", "가자", "해봐", "웅", "넵"
- 동의: "그거로", "그걸로 해", "할게", "할래", "해줘"
- 문제 시작: "풀래", "풀게", "시작", "해보자"

**부정 표현** (response="negative"):
- 명시적: "아니", "아니요", "싫어", "ㄴㄴ", "no"
- 거절: "말고", "다른거", "다시", "다른걸로", "패스"
- 불만: "별로", "그건 좀", "다른 게 좋겠어"

**불명확** (response="unclear"):
- 질문: "그게 뭐야?", "어떤 거?"
- 애매함: "음...", "글쎄", "모르겠어"

추가로 확인:
- 긍정하면서 특정 값을 언급했는지 ("정렬 좋아" → extracted_value="정렬")
- 다른 정보도 함께 포함했는지 ("정렬 쉬운 거로" → additional_values={"difficulty": "easy"})

JSON 형식으로만 응답:
{
  "response": "positive" | "negative" | "unclear",
  "confidence": 0.0-1.0,
  "extracted_value": "string" | null,
  "has_additional_info": true | false,
  "additional_values": {"topic": "...", "difficulty": "...", "language": "..."} | null
}"""

REJECTION_SYSTEM_PROMPT = """당신은 거절 응답 분석기입니다.
사용자가 왜 거절했는지, 대안을 원하는지 분석하세요.

**거절 이유** (reason):
- "too_hard": 어렵다고 느낌 ("어려워", "힘들어", "어렵")
- "too_easy": 쉽다고 느낌 ("쉬워", "심심해", "간단해")
- "already_done": 이미 해봤음 ("했어", "풀었어", "해봤어", "알아")
- "not_interested": 관심 없음 ("관심 없어", "재미없어", "별로")
- "want_different": 다른 것 원함 ("다른거", "말고", "대신")
- "want_choose": 직접 고르고 싶음 ("목록", "다 보여줘", "골라")

**대안 추출**:
"DP 말고 그래프로" → alternative="그래프", alternative_step="topic"
"쉬운 거 말고 어려운 거" → alternative="hard", alternative_step="difficulty"
"파이썬 대신 자바" → alternative="java", alternative_step="language"

JSON 형식으로만 응답:
{
  "reason": "too_hard" | "too_easy" | "already_done" | "not_interested" | "want_different" | "want_choose" | null,
  "alternative": "string" | null,
  "alternative_step": "topic" | "difficulty" | "language" | null,
  "confidence": 0.0-1.0,
  "suggested_action": "show_options" | "suggest_easier" | "suggest_harder" | "suggest_different" | null
}"""


# ============================================================
# Collection Tool 클래스
# ============================================================

class CollectionTool:
    """정보 수집용 통합 Tool"""

    def __init__(self):
        self._embedding_service = None

    @property
    def embedding_service(self):
        """임베딩 서비스 lazy loading"""
        if self._embedding_service is None:
            self._embedding_service = get_collection_embeddings_service()
        return self._embedding_service

    # ============================================================
    # 1. 값 추출 Tool
    # ============================================================

    async def extract_values(
        self,
        message: str,
        current_step: str = "topic",
        existing_values: Optional[Dict[str, str]] = None,
        use_llm_fallback: bool = True,
    ) -> ExtractionResult:
        """
        메시지에서 topic/difficulty/language 값 추출

        전략:
        1. 임베딩 기반 매칭 시도 (빠름, 저비용)
        2. 신뢰도 낮으면 LLM fallback (정확, 고비용)

        Args:
            message: 사용자 메시지
            current_step: 현재 수집 단계 (우선순위 결정용)
            existing_values: 이미 수집된 값 (덮어쓰기 방지)
            use_llm_fallback: LLM fallback 사용 여부

        Returns:
            ExtractionResult
        """
        existing_values = existing_values or {}

        # 1. 임베딩 기반 매칭 시도
        embedding_result = await self._extract_with_embedding(message, current_step)

        # 임베딩 성공 & 현재 단계 값이 있으면 바로 반환
        current_value = embedding_result.values.get(current_step)
        if current_value and embedding_result.confidence >= 0.75:
            print(f"[CollectionTool] Embedding extraction succeeded: {embedding_result.values}")
            return embedding_result

        # 2. LLM fallback (임베딩 실패 or 신뢰도 낮음)
        if use_llm_fallback and embedding_result.confidence < 0.60:
            print(f"[CollectionTool] Low confidence ({embedding_result.confidence:.2f}), using LLM fallback")
            llm_result = await self._extract_with_llm(message)

            # 임베딩 + LLM 결과 병합 (더 높은 신뢰도 우선)
            if llm_result.confidence > embedding_result.confidence:
                return ExtractionResult(
                    values=self._merge_values(embedding_result.values, llm_result.values),
                    confidence=max(embedding_result.confidence, llm_result.confidence),
                    extraction_type="hybrid",
                    details={"embedding": embedding_result.details, "llm": llm_result.details}
                )

        return embedding_result

    async def _extract_with_embedding(
        self,
        message: str,
        current_step: str,
    ) -> ExtractionResult:
        """임베딩 기반 값 추출"""
        values = {"topic": None, "difficulty": None, "language": None}
        details = {}
        max_confidence = 0.0

        if not self.embedding_service.is_initialized():
            print("[CollectionTool] Embedding service not initialized")
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

            # 현재 단계 값 기준으로 신뢰도 결정
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

    async def _extract_with_llm(self, message: str) -> ExtractionResult:
        """LLM 기반 값 추출 (structured output)"""
        values = {"topic": None, "difficulty": None, "language": None}

        try:
            response = await openrouter_service.chat_completion(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
                    {"role": "user", "content": f"메시지: {message}"}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )

            content = openrouter_service.get_content(response)
            result = json.loads(content)

            # 정규화된 값만 사용
            if result.get("topic"):
                values["topic"] = self._normalize_topic(result["topic"])
            if result.get("difficulty"):
                values["difficulty"] = self._normalize_difficulty(result["difficulty"])
            if result.get("language"):
                values["language"] = self._normalize_language(result["language"])

            return ExtractionResult(
                values=values,
                confidence=result.get("confidence", 0.8),
                extraction_type="llm",
                details={"raw_response": result}
            )

        except Exception as e:
            print(f"[CollectionTool] LLM extraction error: {e}")
            return ExtractionResult(
                values=values,
                confidence=0.0,
                extraction_type="llm",
                details={"error": str(e)}
            )

    # ============================================================
    # 2. 긍정/부정 응답 분석 Tool
    # ============================================================

    async def analyze_confirmation(
        self,
        message: str,
        awaiting_value: Optional[str] = None,
        current_step: str = "topic",
    ) -> ConfirmationResult:
        """
        긍정/부정 응답 분석

        Args:
            message: 사용자 메시지
            awaiting_value: 확인 대기 중인 값 (예: "DP")
            current_step: 현재 수집 단계

        Returns:
            ConfirmationResult
        """
        # 1. 임베딩 기반 빠른 체크
        embedding_result = await self._check_confirmation_embedding(message)

        # 명확한 긍정/부정이면 바로 반환
        if embedding_result.confidence >= 0.85:
            # 추가 값 추출
            if embedding_result.response == "positive":
                extraction = await self.extract_values(message, current_step, use_llm_fallback=False)
                if any(extraction.values.values()):
                    embedding_result.has_additional_info = True
                    embedding_result.additional_values = {k: v for k, v in extraction.values.items() if v}
                    # 현재 단계 값이 있으면 extracted_value로
                    if extraction.values.get(current_step):
                        embedding_result.extracted_value = extraction.values[current_step]

            return embedding_result

        # 2. 애매하면 LLM 사용
        return await self._analyze_confirmation_llm(message, awaiting_value, current_step)

    async def _check_confirmation_embedding(self, message: str) -> ConfirmationResult:
        """임베딩 기반 긍정/부정 체크"""
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

    async def _analyze_confirmation_llm(
        self,
        message: str,
        awaiting_value: Optional[str],
        current_step: str,
    ) -> ConfirmationResult:
        """LLM 기반 긍정/부정 분석"""
        try:
            context = f"현재 '{awaiting_value}' 추천에 대한 응답입니다." if awaiting_value else ""

            response = await openrouter_service.chat_completion(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": CONFIRMATION_SYSTEM_PROMPT},
                    {"role": "user", "content": f"{context}\n메시지: {message}"}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )

            content = openrouter_service.get_content(response)
            result = json.loads(content)

            # additional_values 정규화
            additional = result.get("additional_values")
            if additional:
                additional = {
                    k: self._normalize_value(k, v)
                    for k, v in additional.items()
                    if v
                }

            return ConfirmationResult(
                response=result.get("response", "unclear"),
                confidence=result.get("confidence", 0.5),
                extracted_value=result.get("extracted_value"),
                has_additional_info=result.get("has_additional_info", False),
                additional_values=additional if additional else None
            )

        except Exception as e:
            print(f"[CollectionTool] Confirmation LLM error: {e}")
            return ConfirmationResult(response="unclear", confidence=0.0)

    # ============================================================
    # 3. 거절 분석 Tool
    # ============================================================

    async def analyze_rejection(
        self,
        message: str,
        current_step: str = "topic",
        rejected_values: Optional[List[str]] = None,
    ) -> RejectionResult:
        """
        거절 메시지 분석

        Args:
            message: 사용자 메시지
            current_step: 현재 수집 단계
            rejected_values: 이미 거절된 값들

        Returns:
            RejectionResult
        """
        rejected_values = rejected_values or []

        # 1. 임베딩으로 대안 값 추출 시도
        extraction = await self.extract_values(message, current_step, use_llm_fallback=False)

        # 대안 값이 있고 거절된 값과 다르면
        alternative = extraction.values.get(current_step)
        if alternative and alternative not in rejected_values:
            # 간단한 키워드로 이유 추정
            reason = self._guess_rejection_reason(message)
            return RejectionResult(
                reason=reason,
                alternative=alternative,
                alternative_step=current_step,
                confidence=extraction.confidence,
                suggested_action="suggest_different"
            )

        # 2. LLM으로 상세 분석
        return await self._analyze_rejection_llm(message, current_step, rejected_values)

    def _guess_rejection_reason(self, message: str) -> Optional[str]:
        """간단한 키워드 기반 거절 이유 추정"""
        message_lower = message.lower()

        if any(k in message_lower for k in ["어려", "힘들", "어렵"]):
            return "too_hard"
        if any(k in message_lower for k in ["쉬워", "쉽", "심심"]):
            return "too_easy"
        if any(k in message_lower for k in ["했어", "풀었", "해봤", "알아"]):
            return "already_done"
        if any(k in message_lower for k in ["말고", "대신", "다른"]):
            return "want_different"
        if any(k in message_lower for k in ["목록", "골라", "보여"]):
            return "want_choose"

        return "want_different"

    async def _analyze_rejection_llm(
        self,
        message: str,
        current_step: str,
        rejected_values: List[str],
    ) -> RejectionResult:
        """LLM 기반 거절 분석"""
        try:
            context = f"현재 단계: {current_step}, 이미 거절된 값: {rejected_values}"

            response = await openrouter_service.chat_completion(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": REJECTION_SYSTEM_PROMPT},
                    {"role": "user", "content": f"{context}\n메시지: {message}"}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )

            content = openrouter_service.get_content(response)
            result = json.loads(content)

            # alternative 정규화
            alternative = result.get("alternative")
            alternative_step = result.get("alternative_step")
            if alternative and alternative_step:
                alternative = self._normalize_value(alternative_step, alternative)

            return RejectionResult(
                reason=result.get("reason"),
                alternative=alternative,
                alternative_step=alternative_step,
                confidence=result.get("confidence", 0.5),
                suggested_action=result.get("suggested_action")
            )

        except Exception as e:
            print(f"[CollectionTool] Rejection LLM error: {e}")
            return RejectionResult(
                reason="want_different",
                alternative=None,
                alternative_step=None,
                confidence=0.3
            )

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
