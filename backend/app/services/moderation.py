"""
Content Moderation Service

OpenAI Moderation API를 사용한 유해 콘텐츠 감지
- 무료 API
- 욕설, 혐오, 폭력, 성적 콘텐츠 등 자동 감지
- 한국어 지원

하드코딩된 키워드 리스트 없이 AI 기반 감지
"""

from dataclasses import dataclass
from typing import Optional
import os

try:
    from openai import AsyncOpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False


@dataclass
class ModerationResult:
    """Moderation 결과"""
    is_flagged: bool
    categories: dict  # 감지된 카테고리들
    category_scores: dict  # 각 카테고리 점수 (0~1)
    reason: Optional[str] = None  # 감지된 경우 주요 이유


class ModerationService:
    """
    OpenAI Moderation API 기반 콘텐츠 필터링

    사용:
        result = await moderation_service.check("검사할 텍스트")
        if result.is_flagged:
            # 유해 콘텐츠 처리
    """

    def __init__(self):
        self._client: Optional[AsyncOpenAI] = None

    @property
    def client(self) -> Optional[AsyncOpenAI]:
        """Lazy initialization of OpenAI client"""
        if self._client is None and HAS_OPENAI:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self._client = AsyncOpenAI(api_key=api_key)
        return self._client

    async def check(self, text: str) -> ModerationResult:
        """
        텍스트의 유해성 검사

        Args:
            text: 검사할 텍스트

        Returns:
            ModerationResult: 검사 결과

        Note:
            OpenAI Moderation API는 무료입니다.
            카테고리: hate, harassment, self-harm, sexual, violence 등
        """
        if not self.client:
            # OpenAI 클라이언트 없으면 통과 (개발 환경 등)
            return ModerationResult(
                is_flagged=False,
                categories={},
                category_scores={},
            )

        try:
            response = await self.client.moderations.create(
                model="omni-moderation-latest",  # 최신 모델 (다국어 지원 향상)
                input=text,
            )

            result = response.results[0]

            # 감지된 카테고리 추출
            flagged_categories = {
                cat: flagged
                for cat, flagged in result.categories.model_dump().items()
                if flagged
            }

            # 주요 이유 (가장 높은 점수의 카테고리)
            reason = None
            if result.flagged and result.category_scores:
                scores = result.category_scores.model_dump()
                max_category = max(scores, key=scores.get)
                reason = self._category_to_korean(max_category)

            return ModerationResult(
                is_flagged=result.flagged,
                categories=flagged_categories,
                category_scores=result.category_scores.model_dump() if result.category_scores else {},
                reason=reason,
            )

        except Exception as e:
            print(f"[ModerationService] Error: {e}")
            # 오류 시 통과 (서비스 중단 방지)
            return ModerationResult(
                is_flagged=False,
                categories={},
                category_scores={},
            )

    def _category_to_korean(self, category: str) -> str:
        """카테고리를 한국어로 변환"""
        mapping = {
            "hate": "혐오 표현",
            "hate/threatening": "혐오/위협",
            "harassment": "괴롭힘",
            "harassment/threatening": "괴롭힘/위협",
            "self-harm": "자해",
            "self-harm/intent": "자해 의도",
            "self-harm/instructions": "자해 방법",
            "sexual": "성적 콘텐츠",
            "sexual/minors": "미성년자 관련",
            "violence": "폭력",
            "violence/graphic": "노골적 폭력",
        }
        return mapping.get(category, category)


# 싱글톤 인스턴스
moderation_service = ModerationService()
