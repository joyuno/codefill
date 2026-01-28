"""
Collection Tools

정보 수집 단계에서 사용하는 LLM 기반 도구들
- 임베딩 1차 매칭 + LLM 보조로 정확도 향상
- Structured output으로 안정적인 값 추출
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Literal
import json
import os

from ..services.openrouter import openrouter_service
from ..services.collection_embeddings import get_collection_embeddings_service


# ============================================================
# 동적 태그 로드
# ============================================================

_COLLECTION_TAG_CACHE = None

def _load_available_tags() -> List[str]:
    """JSON 파일에서 사용 가능한 태그 목록 로드"""
    global _COLLECTION_TAG_CACHE

    if _COLLECTION_TAG_CACHE is not None:
        return _COLLECTION_TAG_CACHE

    json_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "data", "tag_normalization.json"
    )

    default_tags = ["구현", "수학", "자료구조", "그리디", "DP", "정렬", "문자열",
                    "완전탐색", "그래프", "BFS/DFS", "트리", "이분탐색"]

    try:
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                _COLLECTION_TAG_CACHE = data.get("available_tags", default_tags)
                return _COLLECTION_TAG_CACHE
    except Exception:
        pass

    _COLLECTION_TAG_CACHE = default_tags
    return default_tags


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


@dataclass
class QuestionInfo:
    """질문 분석 정보"""
    question_type: Optional[str]       # "explanation" | "comparison" | "difficulty_inquiry" | "recommendation" | "how_to"
    question_target: Optional[str]     # "topic" | "difficulty" | "language" | "general"
    question_subjects: List[str]       # ["DP"], ["DP", "그래프"], ["골드"] 등

    def to_dict(self) -> Dict[str, Any]:
        return {
            "question_type": self.question_type,
            "question_target": self.question_target,
            "question_subjects": self.question_subjects,
        }


@dataclass
class ExtendedInfo:
    """확장 의도 분석 정보 (코딩 학습 관련 질문)"""
    category: Optional[str]            # "data_structure" | "algorithm" | "language_syntax" | "error" | "optimization" | "career" | "service"
    keywords: List[str]                # 핵심 키워드 배열
    language_context: Optional[str]    # "python" | "java" | "cpp" | "general"
    needs_search: bool = False         # 웹 검색 필요 여부

    def to_dict(self) -> Dict[str, Any]:
        return {
            "category": self.category,
            "keywords": self.keywords,
            "language_context": self.language_context,
            "needs_search": self.needs_search,
        }


# ============================================================
# 프롬프트 정의 (통합)
# ============================================================

UNIFIED_ANALYSIS_PROMPT = """당신은 AI 코딩 학습 도우미 챗봇의 메시지 분석기입니다.
사용자 메시지를 분석하여 의도, 값, 거부 여부, **관련성**을 한 번에 판단하세요.

## 0. 관련성 체크 (is_collection_related) - 중요!
현재 "알고리즘 문제 추천을 위한 정보 수집" 단계입니다.
메시지가 다음 중 하나에 해당하면 **true**:
- 주제/난이도/언어 선택 관련 ("정렬로 할게", "쉬운 거", "파이썬")
- 추천 요청 ("추천해줘", "뭐가 좋아?", "알아서 골라줘")
- 긍정/부정 응답 ("네", "좋아", "아니", "싫어", "다른 거")
- 문제 풀이 관련 질문 ("이분탐색이 뭐야?", "그리디 어려워?")

메시지가 다음 중 하나에 해당하면 **false**:
- 완전히 다른 주제 ("오늘 날씨 어때?")
- 코딩/학습과 무관한 일반 대화

## 1. 의도 분류 (intent) - 확장된 분류
### 정보 수집 관련
- "positive": 긍정/동의 ("네", "응", "좋아", "그래", "ㅇㅇ", "굳", "할게", "해줘", "시작")
- "negative": 부정/거절 ("아니", "싫어", "말고", "다른거", "패스", "ㄴㄴ", "별로")
- "value_input": 새 값 제시 ("구현으로 해줘", "정렬", "파이썬", "쉬운 거")
- "question": 알고리즘/문제 관련 질문 ("그리디가 뭐야?", "골드면 어려워?")
- "unclear": 애매한 응답 ("음...", "글쎄", "모르겠어")

### 코딩 학습 관련 (is_collection_related=false이지만 학습 도우미로서 대응 필요)
- "coding_concept": 프로그래밍 개념 질문 ("재귀함수가 뭐야?", "빅오 표기법 설명해줘", "스택이랑 큐 차이", "객체지향이 뭔데?")
- "syntax_help": 언어 문법/사용법 질문 ("파이썬 리스트 컴프리헨션 어떻게 써?", "자바 람다식 예시", "C++ 포인터 사용법")
- "error_debug": 에러/디버깅 관련 ("IndexError가 뭐야?", "런타임 에러 해결법", "시간 초과 왜 나?", "메모리 초과 어떻게 해결해?")
- "learning_advice": 학습 방법/조언 요청 ("알고리즘 공부 어떻게 해?", "코테 준비 순서", "초보자 로드맵", "취업 준비 어떻게?")
- "code_review": 코드 리뷰/개선 요청 ("이 코드 개선점 알려줘", "더 효율적인 방법?", "코드 봐줘", "최적화 방법")
- "hint_request": 현재 문제 힌트 요청 ("힌트 줘", "어떻게 접근해?", "모르겠어 도와줘", "막혔어")

### 서비스/시스템 관련
- "progress_inquiry": 학습 진도/통계 질문 ("내가 푼 문제 몇 개야?", "오늘 푼 문제", "내 레벨 뭐야?", "통계 보여줘", "학습 기록")
- "service_help": 서비스 사용법 질문 ("이 서비스 뭐야?", "어떻게 사용해?", "기능 설명해줘", "도움말")
- "account_inquiry": 계정/프로필 관련 ("내 프로필", "설정 바꾸고 싶어", "레벨업 어떻게 해?")

### 일반 대화
- "greeting": 인사/감사 ("안녕", "하이", "고마워", "감사합니다", "바이", "잘가")
- "chitchat": 잡담/감정 표현 ("심심해", "배고파", "힘들다", "재밌다", "화이팅")
- "off_topic": 완전히 관련 없는 주제 ("날씨 어때?", "점심 뭐 먹지?")

## 1-1. 질문 분석 (intent=question일 때 필수!)
**question_type** (질문 유형):
- "explanation": 개념/용어 설명 요청 ("그리디가 뭐야?", "이분탐색이 뭔데?", "골드면 어느 정도야?")
- "comparison": 비교 요청 ("정렬이랑 구현 차이가 뭐야?", "파이썬이랑 자바 뭐가 좋아?")
- "difficulty_inquiry": 난이도 관련 질문 ("골드면 얼마나 어려워?", "플래티넘 풀 수 있을까?")
- "recommendation": 추천 요청 ("뭐가 좋아?", "초보자한테 뭐 추천해?")
- "how_to": 방법 질문 ("구현 어떻게 공부해?", "문자열 잘하려면?")
- "topic_list": 전체 목록/옵션 요청 ("주제 다 보여줘", "목록 보여줘", "전부 알려줘", "뭐뭐 있어?", "그중에 골라볼게")

**question_target** (질문 대상 카테고리):
- "topic": 알고리즘 주제 관련 ("그리디가 뭐야?", "정렬 어려워?")
- "difficulty": 난이도 관련 ("골드면 어느 정도야?", "실버 쉬워?")
- "language": 언어 관련 ("파이썬 좋아?", "C++ 빨라?")
- "general": 일반적인 코딩/알고리즘 질문

**question_subjects** (질문에서 언급된 구체적인 대상들, 배열):
- 예: "그리디가 뭐야?" → ["그리디"]
- 예: "정렬이랑 구현 뭐가 달라?" → ["정렬", "구현"]
- 예: "골드면 어려워?" → ["골드"]

## 1-2. 확장 의도 분석 (coding_concept, syntax_help, error_debug 등일 때)
**extended_info** (확장 정보):
- "category": 질문 카테고리 ("data_structure", "algorithm", "language_syntax", "error", "optimization", "career", "service")
- "keywords": 핵심 키워드 배열 (["재귀", "함수"], ["IndexError", "리스트"])
- "language_context": 언어 맥락 ("python", "java", "cpp", "general")
- "needs_search": 웹 검색이 필요한지 (true/false) - 최신 정보, 공식 문서 참조 필요 시

## 2. 값 추출 (원하는 값만!)
- **topic**: 다양한 알고리즘 주제 (구현, 수학, 자료구조, 그리디, DP, 정렬, 문자열, 완전탐색, 그래프, BFS/DFS, 트리, 이분탐색 등)
- **difficulty**: easy(실버/쉬운), medium(골드/보통), medium_hard(플래티넘), hard(다이아/어려운), very_hard(마스터)
- **language**: python(파이썬), java(자바), cpp(씨플플/C++)
- **is_corporate_test**: true/false - 대기업 코테/코딩테스트 준비 요청인지

## 2-1. 대기업 코테 감지 (is_corporate_test)
다음 키워드가 포함되면 **is_corporate_test = true**:
- "대기업 코테", "대기업 코딩테스트", "대기업 준비"
- "카카오", "네이버", "라인", "삼성", "쿠팡", "배민", "토스", "당근" 등 기업명
- "프로그래머스 스타일", "프로그래머스 문제"
- "실전 코테", "기업 코테", "기업 코딩테스트"

is_corporate_test가 true이면 **추가 정보 수집이 필요**함을 나타냄

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
3. "기초 말고 정렬" → values.topic="정렬", rejected.topic="기초"
4. 동의어 인식: "다이나믹"="DP", "실버"="easy"
5. 확장 의도(coding_concept 등)는 is_collection_related=false로 설정

## 4. 단순 키워드 판단 (is_simple_keyword) - 성능 최적화용
메시지가 **단순 키워드 매칭**으로 처리 가능한지 판단합니다.

**is_simple_keyword = true** (단순 입력, 추가 분석 불필요):
- 주제 단독 입력: "정렬", "DP", "그리디", "이분탐색", "구현", "문자열"
- 난이도 단독 입력: "쉬운거", "골드", "플래티넘", "어려운거", "easy", "medium"
- 언어 단독 입력: "파이썬", "자바", "python", "C++"
- 단순 긍정: "응", "네", "ㅇㅇ", "굳", "좋아"
- 단순 부정 (대안 없음): "아니", "ㄴㄴ"

**is_simple_keyword = false** (복잡한 의도, 추가 분석 필요):
- 질문 포함: "정렬 어려워?", "DP가 뭐야?"
- 거절 + 대안: "정렬 말고 그리디", "다른 거로 해줘"
- 복합 입력: "쉬운 정렬 파이썬으로"
- 추천 요청: "뭐가 좋아?", "추천해줘"
- 조건 포함: "빨리 끝나는 거", "요즘 코테 자주 나오는 거"

## JSON 응답 형식
{
  "is_collection_related": true | false,
  "is_simple_keyword": true | false,
  "is_corporate_test": true | false,
  "intent": "positive" | "negative" | "value_input" | "question" | "unclear" | "off_topic" | "coding_concept" | "syntax_help" | "error_debug" | "learning_advice" | "code_review" | "hint_request" | "progress_inquiry" | "service_help" | "account_inquiry" | "greeting" | "chitchat",
  "confidence": 0.0-1.0,
  "values": {
    "topic": "주제명" | null,
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
  },
  "question_info": {
    "question_type": "explanation" | "comparison" | "difficulty_inquiry" | "recommendation" | "how_to" | "topic_list" | null,
    "question_target": "topic" | "difficulty" | "language" | "general" | null,
    "question_subjects": ["정렬", "골드"] | []
  },
  "extended_info": {
    "category": "data_structure" | "algorithm" | "language_syntax" | "error" | "optimization" | "career" | "service" | null,
    "keywords": ["키워드1", "키워드2"] | [],
    "language_context": "python" | "java" | "cpp" | "general" | null,
    "needs_search": true | false
  }
}"""


# ============================================================
# Collection Tool 클래스
# ============================================================

@dataclass
class UnifiedAnalysisResult:
    """통합 분석 결과"""
    intent: str  # 확장된 intent 타입들 포함
    confidence: float
    values: Dict[str, Optional[str]]      # {"topic": "DP", "difficulty": null, ...}
    rejected: Dict[str, Optional[str]]    # {"topic": "기초", ...}
    rejection_reason: Optional[str]       # "too_hard", "want_different", ...
    alternative: Optional[Dict[str, str]] # {"value": "DP", "step": "topic"}
    is_collection_related: bool = True    # 정보 수집과 관련 있는 메시지인지
    is_simple_keyword: bool = False       # 단순 키워드 매칭으로 처리 가능한지 (Hybrid fast-path용)
    is_corporate_test: bool = False       # 대기업 코테 준비 요청인지
    question_info: Optional[QuestionInfo] = None  # 질문 분석 정보 (intent=question일 때)
    extended_info: Optional[ExtendedInfo] = None  # 확장 의도 정보 (코딩 학습 관련)


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

            # is_collection_related 파싱 (기본값 True)
            is_related = result.get("is_collection_related", True)
            intent = result.get("intent", "unclear")

            # intent가 off_topic이면 is_related=False
            if intent == "off_topic":
                is_related = False

            # question_info 파싱 (intent=question일 때)
            question_info = None
            if intent == "question":
                q_info = result.get("question_info", {})
                if q_info:
                    question_info = QuestionInfo(
                        question_type=q_info.get("question_type"),
                        question_target=q_info.get("question_target"),
                        question_subjects=q_info.get("question_subjects", []),
                    )
                    print(f"[CollectionTool] Question detected: type={question_info.question_type}, "
                          f"target={question_info.question_target}, subjects={question_info.question_subjects}")

            # extended_info 파싱 (확장 의도일 때)
            extended_info = None
            extended_intents = ["coding_concept", "syntax_help", "error_debug", "learning_advice",
                               "code_review", "hint_request", "progress_inquiry", "service_help",
                               "account_inquiry", "greeting", "chitchat"]
            if intent in extended_intents:
                is_related = False  # 확장 의도는 정보 수집과 무관
                e_info = result.get("extended_info", {})
                if e_info:
                    extended_info = ExtendedInfo(
                        category=e_info.get("category"),
                        keywords=e_info.get("keywords", []),
                        language_context=e_info.get("language_context"),
                        needs_search=e_info.get("needs_search", False),
                    )
                    print(f"[CollectionTool] Extended intent: {intent}, category={extended_info.category}, "
                          f"keywords={extended_info.keywords}, needs_search={extended_info.needs_search}")

            # is_simple_keyword 파싱 (Hybrid fast-path용)
            is_simple_keyword = result.get("is_simple_keyword", False)

            # is_corporate_test 파싱 (대기업 코테 준비 요청)
            is_corporate_test = result.get("is_corporate_test", False)
            if is_corporate_test:
                print(f"[CollectionTool] Corporate test mode detected!")

            analysis = UnifiedAnalysisResult(
                intent=intent,
                confidence=result.get("confidence", 0.5),
                values=normalized_values,
                rejected=rejected,
                rejection_reason=result.get("rejection_reason"),
                alternative=alternative if alternative.get("value") else None,
                is_collection_related=is_related,
                is_simple_keyword=is_simple_keyword,
                is_corporate_test=is_corporate_test,
                question_info=question_info,
                extended_info=extended_info,
            )

            # 캐시 저장 (최대 100개)
            if len(self._analysis_cache) > 100:
                self._analysis_cache.clear()
            self._analysis_cache[cache_key] = analysis

            print(f"[CollectionTool] Unified analysis: intent={analysis.intent}, values={analysis.values}, is_simple_keyword={is_simple_keyword}")
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
                is_collection_related=True,  # 에러 시 기본값은 관련 있음으로
                is_simple_keyword=False,     # 에러 시 안전하게 full analysis
                is_corporate_test=False,     # 에러 시 기본값 False
                question_info=None,
                extended_info=None,
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
        existing_analysis: Optional[UnifiedAnalysisResult] = None,  # 기존 분석 결과 재사용
    ) -> ExtractionResult:
        """
        메시지에서 topic/difficulty/language 값 추출 (통합 분석 사용)

        Args:
            message: 사용자 메시지
            current_step: 현재 수집 단계 (우선순위 결정용)
            existing_values: 이미 수집된 값 (덮어쓰기 방지)
            use_llm_fallback: LLM 사용 여부 (기본 True)
            existing_analysis: 이미 수행된 분석 결과 (중복 LLM 호출 방지)

        Returns:
            ExtractionResult
        """
        existing_values = existing_values or {}

        # LLM First: 통합 분석 사용 (기존 분석 결과가 있으면 재사용)
        if use_llm_fallback:
            analysis = existing_analysis or await self.analyze(message)

            # 거부된 값이 있으면 details에 기록
            details = {
                "unified_analysis": True,
                "is_collection_related": analysis.is_collection_related,
                "intent": analysis.intent,  # intent 정보 추가
            }
            if analysis.rejected:
                for step, rejected_val in analysis.rejected.items():
                    if rejected_val:
                        details["is_rejection"] = True
                        details["rejected_step"] = step
                        details["rejected_value"] = rejected_val
                        print(f"[CollectionTool] Rejection detected: {step}={rejected_val}")

            # 관련 없는 메시지면 별도 플래그
            if not analysis.is_collection_related:
                details["is_off_topic"] = True
                print(f"[CollectionTool] Off-topic message detected: {message[:50]}...")

            # 질문이면 question_info 추가
            if analysis.intent == "question" and analysis.question_info:
                details["is_question"] = True
                details["question_info"] = analysis.question_info.to_dict()
                print(f"[CollectionTool] Question info added to details: {details['question_info']}")

            # 확장 의도면 extended_info 추가
            if analysis.extended_info:
                details["extended_info"] = analysis.extended_info.to_dict()
                print(f"[CollectionTool] Extended info added: {analysis.intent}")

            # LLM 결과 바로 반환 (임베딩 fallback 제거로 속도 개선)
            # 신뢰도가 낮아도 LLM 결과가 가장 정확함
            return ExtractionResult(
                values=analysis.values,
                confidence=analysis.confidence,
                extraction_type="unified_llm",
                details=details
            )

        # use_llm_fallback=False인 경우 (거의 사용 안함)
        return ExtractionResult(
            values={"topic": None, "difficulty": None, "language": None},
            confidence=0.0,
            extraction_type="none",
            details={"error": "llm_disabled"}
        )

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

        # LLM 결과 바로 반환 (임베딩 fallback 제거로 속도 개선)
        return ConfirmationResult(
            response=response,
            confidence=analysis.confidence,
            extracted_value=extracted_value,
            has_additional_info=has_additional,
            additional_values=additional_values if has_additional else None
        )

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

        # LLM 결과 바로 반환 (임베딩 fallback 제거로 속도 개선)
        return RejectionResult(
            reason=analysis.rejection_reason or "want_different",
            alternative=alternative,
            alternative_step=alternative_step,
            confidence=analysis.confidence,
            suggested_action=suggested_action
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
