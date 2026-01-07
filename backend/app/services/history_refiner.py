"""
History Refiner Service

대화 히스토리를 정제하고 의도에 맞게 필터링하는 서비스

Features:
1. 의도별 히스토리 필터링 (problem_search, code_help, general)
2. 히스토리 요약 (긴 대화 압축)
3. 중요 컨텍스트 추출 (주제, 난이도, 선택된 문제 등)
4. 토큰 제한 준수

Usage:
    refiner = get_history_refiner()
    refined = await refiner.refine(history, intent="problem_search", max_messages=10)
"""

import re
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class RefinedHistory:
    """정제된 히스토리 결과"""
    messages: List[Dict[str, str]]  # 정제된 메시지 목록
    context_summary: Dict[str, Any]  # 추출된 컨텍스트 요약
    original_count: int  # 원본 메시지 수
    refined_count: int  # 정제 후 메시지 수

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class HistoryRefiner:
    """
    히스토리 정제 서비스

    의도에 따라 필요한 히스토리만 선별하고 요약합니다.

    Usage:
        refiner = get_history_refiner()

        # 의도별 필터링
        refined = await refiner.refine(
            history=conversation_history,
            intent="problem_search",
            max_messages=10
        )

        # 결과 사용
        messages = refined.messages  # 정제된 메시지
        context = refined.context_summary  # 컨텍스트 요약
    """

    # 의도별 관련 키워드
    INTENT_KEYWORDS = {
        "problem_search": {
            "include": ["dp", "그래프", "정렬", "탐색", "문제", "주제", "난이도",
                       "쉬운", "어려운", "중간", "실버", "골드", "플래티넘",
                       "추천", "찾아", "검색", "풀고 싶", "연습"],
            "exclude": ["코드", "오류", "에러", "틀렸", "수정"],
        },
        "code_help": {
            "include": ["코드", "오류", "에러", "틀렸", "수정", "왜", "안 돼",
                       "런타임", "컴파일", "시간초과", "메모리", "출력", "입력",
                       "힌트", "도움", "이해", "설명"],
            "exclude": [],
        },
        "problem_selection": {
            "include": ["1번", "2번", "3번", "4번", "5번", "첫", "두", "세",
                       "선택", "할게", "풀게", "그거", "이거"],
            "exclude": [],
        },
        "general": {
            "include": [],
            "exclude": [],
        },
    }

    # 컨텍스트 추출 패턴
    CONTEXT_PATTERNS = {
        "topic": [
            r"(dp|동적\s*프로그래밍|그래프|정렬|탐색|이분\s*탐색|그리디|자료\s*구조)",
            r"(bfs|dfs|다익스트라|플로이드|백트래킹|분할\s*정복)",
        ],
        "difficulty": [
            r"(쉬운|easy|실버|silver)",
            r"(중간|medium|골드|gold)",
            r"(어려운|hard|플래티넘|platinum|다이아|diamond)",
        ],
        "problem_index": [
            r"(\d+)\s*번",
            r"(첫|두|세|네|다섯)\s*(번째)?",
        ],
    }

    def __init__(self):
        self._llm_summarizer = None  # LLM 요약기 (나중에 초기화)

    async def refine(
        self,
        history: List[Dict[str, Any]],
        intent: str = "general",
        max_messages: int = 10,
        include_system: bool = False,
    ) -> RefinedHistory:
        """
        히스토리 정제

        Args:
            history: 원본 대화 히스토리
            intent: 현재 의도 (problem_search, code_help, general 등)
            max_messages: 최대 메시지 수
            include_system: 시스템 메시지 포함 여부

        Returns:
            RefinedHistory: 정제된 히스토리 및 컨텍스트
        """
        if not history:
            return RefinedHistory(
                messages=[],
                context_summary={},
                original_count=0,
                refined_count=0,
            )

        original_count = len(history)

        # 1. 시스템 메시지 필터링
        if not include_system:
            history = [m for m in history if m.get("role") != "system"]

        # 2. 의도별 필터링
        filtered_history = self._filter_by_intent(history, intent)

        # 3. 컨텍스트 추출
        context_summary = self._extract_context(history)

        # 4. 최근 메시지 우선 + 중요 메시지 포함
        refined_messages = self._prioritize_messages(
            filtered_history,
            max_messages,
            context_summary
        )

        # 5. LangChain 형식으로 변환
        formatted_messages = [
            {"role": m.get("role", "user"), "content": m.get("content", "")}
            for m in refined_messages
        ]

        logger.debug(
            f"[HistoryRefiner] Refined {original_count} → {len(formatted_messages)} "
            f"messages for intent={intent}"
        )

        return RefinedHistory(
            messages=formatted_messages,
            context_summary=context_summary,
            original_count=original_count,
            refined_count=len(formatted_messages),
        )

    def _filter_by_intent(
        self,
        history: List[Dict[str, Any]],
        intent: str
    ) -> List[Dict[str, Any]]:
        """의도에 맞는 메시지만 필터링"""
        keywords = self.INTENT_KEYWORDS.get(intent, self.INTENT_KEYWORDS["general"])
        include_kw = keywords.get("include", [])
        exclude_kw = keywords.get("exclude", [])

        # general이거나 키워드가 없으면 전체 반환
        if intent == "general" or not include_kw:
            return history

        filtered = []
        for msg in history:
            content = msg.get("content", "").lower()

            # 포함 키워드 체크
            has_include = any(kw in content for kw in include_kw)

            # 제외 키워드 체크
            has_exclude = any(kw in content for kw in exclude_kw)

            # 포함 키워드가 있고 제외 키워드가 없으면 포함
            if has_include and not has_exclude:
                filtered.append(msg)
            # assistant 응답은 이전 user 메시지와 연결되므로 포함
            elif msg.get("role") == "assistant" and filtered:
                # 바로 이전 메시지가 포함되었으면 이것도 포함
                filtered.append(msg)

        # 필터링 결과가 너무 적으면 최근 메시지라도 포함
        if len(filtered) < 3:
            return history[-10:]

        return filtered

    def _extract_context(self, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """대화에서 중요 컨텍스트 추출"""
        context = {
            "topics": [],
            "difficulty": None,
            "selected_problem_index": None,
            "mentioned_problems": [],
            "user_questions": [],
        }

        all_content = " ".join(
            m.get("content", "") for m in history if m.get("role") == "user"
        )
        all_content_lower = all_content.lower()

        # 주제 추출
        for pattern in self.CONTEXT_PATTERNS["topic"]:
            matches = re.findall(pattern, all_content_lower)
            context["topics"].extend(matches)
        context["topics"] = list(set(context["topics"]))[:3]  # 최대 3개

        # 난이도 추출
        for pattern in self.CONTEXT_PATTERNS["difficulty"]:
            match = re.search(pattern, all_content_lower)
            if match:
                difficulty_text = match.group(1)
                if difficulty_text in ["쉬운", "easy", "실버", "silver"]:
                    context["difficulty"] = "easy"
                elif difficulty_text in ["중간", "medium", "골드", "gold"]:
                    context["difficulty"] = "medium"
                elif difficulty_text in ["어려운", "hard", "플래티넘", "platinum", "다이아", "diamond"]:
                    context["difficulty"] = "hard"
                break

        # 문제 번호 추출
        for pattern in self.CONTEXT_PATTERNS["problem_index"]:
            match = re.search(pattern, all_content_lower)
            if match:
                idx_text = match.group(1)
                if idx_text.isdigit():
                    context["selected_problem_index"] = int(idx_text)
                else:
                    ordinal_map = {"첫": 1, "두": 2, "세": 3, "네": 4, "다섯": 5}
                    context["selected_problem_index"] = ordinal_map.get(idx_text)
                break

        # 최근 질문 추출 (마지막 3개)
        user_messages = [m for m in history if m.get("role") == "user"]
        context["user_questions"] = [
            m.get("content", "")[:100]  # 100자로 제한
            for m in user_messages[-3:]
        ]

        return context

    def _prioritize_messages(
        self,
        history: List[Dict[str, Any]],
        max_messages: int,
        context: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        메시지 우선순위 지정

        규칙:
        1. 최근 메시지 우선
        2. 컨텍스트 관련 메시지 우선
        3. user-assistant 쌍 유지
        """
        if len(history) <= max_messages:
            return history

        # 점수 기반 우선순위
        scored_messages = []
        for i, msg in enumerate(history):
            score = 0
            content = msg.get("content", "").lower()

            # 최근 메시지에 높은 점수
            recency_score = i / len(history)  # 0~1
            score += recency_score * 5

            # 컨텍스트 주제 언급 시 가산점
            for topic in context.get("topics", []):
                if topic in content:
                    score += 2

            # 난이도 언급 시 가산점
            if context.get("difficulty") and context["difficulty"] in content:
                score += 1

            scored_messages.append((score, i, msg))

        # 점수순 정렬 후 상위 N개 선택
        scored_messages.sort(key=lambda x: x[0], reverse=True)
        selected_indices = set(idx for _, idx, _ in scored_messages[:max_messages])

        # 원래 순서 유지하면서 선택된 메시지만 반환
        result = []
        for i, msg in enumerate(history):
            if i in selected_indices:
                result.append(msg)

        # user-assistant 쌍 유지 (user 다음에 assistant가 오도록)
        return self._ensure_message_pairs(result)

    def _ensure_message_pairs(
        self,
        messages: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """user-assistant 메시지 쌍 유지"""
        if not messages:
            return messages

        result = []
        for i, msg in enumerate(messages):
            result.append(msg)

            # 마지막이 user면 그대로 둠 (응답 대기 중)
            # 중간에 user가 연속되면 이전 assistant가 빠진 것이므로 무시

        return result

    async def summarize_long_history(
        self,
        history: List[Dict[str, Any]],
        max_tokens: int = 500,
    ) -> str:
        """
        긴 히스토리를 요약 (LLM 사용)

        Note: LLM 비용이 발생하므로 히스토리가 매우 긴 경우에만 사용
        """
        if len(history) < 20:
            # 짧으면 그냥 최근 메시지 반환
            return self._simple_summary(history)

        # TODO: LLM 요약 구현 (비용 고려 필요)
        # 현재는 규칙 기반 요약 사용
        return self._simple_summary(history)

    def _simple_summary(self, history: List[Dict[str, Any]]) -> str:
        """규칙 기반 간단 요약"""
        context = self._extract_context(history)

        summary_parts = []

        if context["topics"]:
            summary_parts.append(f"주제: {', '.join(context['topics'])}")

        if context["difficulty"]:
            summary_parts.append(f"난이도: {context['difficulty']}")

        if context["selected_problem_index"]:
            summary_parts.append(f"선택된 문제: {context['selected_problem_index']}번")

        if not summary_parts:
            return "이전 대화 없음"

        return " | ".join(summary_parts)


# ============================================================
# Singleton Instance
# ============================================================

_history_refiner: Optional[HistoryRefiner] = None


def get_history_refiner() -> HistoryRefiner:
    """HistoryRefiner 싱글톤 반환"""
    global _history_refiner
    if _history_refiner is None:
        _history_refiner = HistoryRefiner()
    return _history_refiner
