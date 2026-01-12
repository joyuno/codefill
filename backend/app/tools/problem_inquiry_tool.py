"""
Problem Inquiry Tool - 검색 결과 문제에 대한 질문 처리

사용자가 검색 결과에서 특정 문제에 대해 질문할 때 사용:
- "taco_749 요약해줘"
- "두 번째 문제 뭐야?"
- "3번 어떤 내용이야?"
- "이거 뭐에 도움되냐?"
"""

import re
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from ..services.openrouter import openrouter_service
from ..config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class InquiryResult:
    """문제 질문 처리 결과"""
    success: bool
    response: str
    problem_info: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# ============================================================
# LLM 프롬프트
# ============================================================

PROBLEM_INQUIRY_PROMPT = """당신은 코딩 학습 도우미입니다.
사용자가 문제 목록에서 특정 문제에 대해 질문했습니다.

## 문제 정보
{problem_info}

## 사용자 질문
"{question}"

## 응답 지침
1. 사용자의 질문 의도에 맞게 답변하세요
2. 문제의 핵심 내용을 간결하게 설명하세요
3. 어떤 알고리즘/개념을 연습할 수 있는지 언급하세요
4. 난이도와 예상 풀이 시간 정보가 있으면 포함하세요
5. 친근하고 격려하는 어조를 유지하세요
6. 2-4문장으로 답변하세요

## 질문 유형별 답변 가이드
- "요약해줘" → 문제 핵심 내용 + 필요한 알고리즘
- "뭐야?" / "어떤 내용?" → 문제 설명 + 입출력 개요
- "뭐에 도움되냐" / "왜 풀어야해" → 학습 효과 + 실전 활용
- "어려워?" / "난이도" → 난이도 설명 + 필요한 사전 지식

답변:"""


class ProblemInquiryTool:
    """검색 결과 문제에 대한 질문 처리 Tool"""

    async def inquire(
        self,
        question: str,
        inquiry_target: str,
        search_results: List[Dict[str, Any]],
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> InquiryResult:
        """
        문제에 대한 질문을 처리합니다.

        Args:
            question: 사용자의 원본 질문
            inquiry_target: 질문 대상 (인덱스 "1", "2" 또는 문제명 "taco_749")
            search_results: 검색 결과 문제 목록
            conversation_history: 이전 대화 히스토리 (꼬리 질문 맥락 유지)

        Returns:
            InquiryResult
        """
        try:
            # 1. 대상 문제 찾기
            problem = self._find_problem(inquiry_target, search_results)

            if not problem:
                return InquiryResult(
                    success=False,
                    response=f"'{inquiry_target}'에 해당하는 문제를 찾지 못했어요. 번호나 이름을 다시 확인해주세요!",
                    error="problem_not_found",
                )

            # 2. 문제 정보 포맷팅
            problem_info = self._format_problem_info(problem)

            # 3. LLM으로 응답 생성 (대화 히스토리 포함)
            response = await self._generate_response(
                question, problem_info, conversation_history
            )

            return InquiryResult(
                success=True,
                response=response,
                problem_info=problem,
            )

        except Exception as e:
            logger.error(f"[ProblemInquiryTool] Error: {e}")
            import traceback
            traceback.print_exc()
            return InquiryResult(
                success=False,
                response="문제 정보를 가져오는 중 오류가 발생했어요. 다시 시도해주세요!",
                error=str(e),
            )

    def _find_problem(
        self,
        inquiry_target: str,
        search_results: List[Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        """
        inquiry_target을 기반으로 문제를 찾습니다.

        - 숫자 ("1", "2") → 인덱스로 검색
        - 문제명 ("taco_749") → 이름으로 검색
        """
        if not search_results:
            return None

        target = inquiry_target.strip()

        # 1. 인덱스 형태 ("1", "2", "첫번째" 등)
        index = self._parse_index(target)
        if index is not None:
            if 0 <= index < len(search_results):
                return search_results[index]

        # 2. 문제명으로 검색
        target_lower = target.lower()
        for problem in search_results:
            name = (problem.get("name") or "").lower()
            title = (problem.get("title") or "").lower()
            if target_lower in name or target_lower in title:
                return problem

        # 3. 부분 매칭 (taco_749 → taco_749_something)
        for problem in search_results:
            name = (problem.get("name") or "").lower()
            if name.startswith(target_lower) or target_lower in name:
                return problem

        return None

    def _parse_index(self, target: str) -> Optional[int]:
        """문자열에서 인덱스를 추출합니다."""
        # 순수 숫자
        if target.isdigit():
            return int(target) - 1  # 1-indexed → 0-indexed

        # "첫번째", "두번째" 등
        ordinal_map = {
            "첫": 0, "첫번째": 0, "첫째": 0, "1번째": 0,
            "두": 1, "두번째": 1, "둘째": 1, "2번째": 1,
            "세": 2, "세번째": 2, "셋째": 2, "3번째": 2,
            "네": 3, "네번째": 3, "넷째": 3, "4번째": 3,
            "다섯": 4, "다섯번째": 4, "5번째": 4,
        }

        for key, idx in ordinal_map.items():
            if key in target:
                return idx

        # "N번" 패턴
        num_match = re.search(r'(\d+)\s*번', target)
        if num_match:
            return int(num_match.group(1)) - 1

        return None

    def _format_problem_info(self, problem: Dict[str, Any]) -> str:
        """문제 정보를 LLM 프롬프트용으로 포맷팅합니다."""
        name = problem.get("name") or problem.get("title") or "Unknown"
        difficulty = problem.get("difficulty") or "medium"
        tags = problem.get("tags") or problem.get("topics") or []
        description = problem.get("description") or problem.get("question") or ""
        key_concepts = problem.get("key_concepts") or []

        # 난이도 한글 변환
        difficulty_map = {
            "easy": "쉬움",
            "medium": "중간",
            "medium_hard": "중상",
            "hard": "어려움",
            "very_hard": "매우 어려움",
        }
        difficulty_kr = difficulty_map.get(difficulty, difficulty)

        # 태그 포맷
        tags_str = ", ".join(tags[:5]) if tags else "없음"
        concepts_str = ", ".join(key_concepts[:3]) if key_concepts else ""

        # 설명 (너무 길면 자르기)
        desc_preview = description[:300] + "..." if len(description) > 300 else description

        info = f"""- 문제명: {name}
- 난이도: {difficulty_kr}
- 주제/태그: {tags_str}"""

        if concepts_str:
            info += f"\n- 핵심 개념: {concepts_str}"

        if desc_preview:
            info += f"\n- 문제 설명: {desc_preview}"

        return info

    async def _generate_response(
        self,
        question: str,
        problem_info: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> str:
        """LLM을 사용하여 응답을 생성합니다."""
        prompt = PROBLEM_INQUIRY_PROMPT.format(
            problem_info=problem_info,
            question=question,
        )

        messages = [
            {"role": "system", "content": "코딩 학습 도우미입니다. 친근하고 간결하게 답변합니다. 이전 대화 맥락을 참고하여 꼬리 질문에도 자연스럽게 응답합니다."},
        ]

        # 대화 히스토리 추가 (최근 6개 - 꼬리 질문 맥락 유지)
        if conversation_history:
            for msg in conversation_history[-6:]:
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", ""),
                })

        messages.append({"role": "user", "content": prompt})

        try:
            response = await openrouter_service.chat_completion(
                model=settings.llm_model_hint,  # 가벼운 모델 사용
                messages=messages,
                temperature=0.7,
                max_tokens=300,
            )

            content = openrouter_service.get_content(response)
            return content.strip()

        except Exception as e:
            logger.error(f"[ProblemInquiryTool] LLM error: {e}")
            # Fallback 응답
            return f"이 문제는 {problem_info.split('주제/태그:')[1].split(chr(10))[0].strip() if '주제/태그:' in problem_info else '다양한 알고리즘'} 관련 문제예요. 선택해서 풀어보시겠어요?"


# Singleton
_problem_inquiry_tool = None


def get_problem_inquiry_tool() -> ProblemInquiryTool:
    """ProblemInquiryTool 싱글톤 반환"""
    global _problem_inquiry_tool
    if _problem_inquiry_tool is None:
        _problem_inquiry_tool = ProblemInquiryTool()
    return _problem_inquiry_tool
