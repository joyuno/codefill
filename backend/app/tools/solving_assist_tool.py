"""
Solving Assist Tool - 문제 풀이 중 채팅 기반 도움

기존 힌트 버튼과 별개로, 채팅으로 간접적인 도움을 제공:
- 개념 설명 (정답 노출 없이)
- 방향 확인 ("이렇게 하면 맞아?")
- 간접 힌트 ("어떻게 시작해야 해?")

핵심 원칙:
1. 정답 코드를 절대 직접 보여주지 않음
2. 소크라테스식 질문으로 유도
3. 개념과 접근법만 설명
"""

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

from ..services.openrouter import openrouter_service
from ..database import get_supabase_client
from ..config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class AssistType(str, Enum):
    """도움 유형"""
    CONCEPT_EXPLAIN = "concept_explain"  # 개념 설명
    APPROACH_HINT = "approach_hint"  # 접근법 힌트
    VALIDATE_DIRECTION = "validate_direction"  # 방향 확인
    GENERAL_HELP = "general_help"  # 일반 도움


@dataclass
class AssistResult:
    """도움 결과"""
    success: bool
    response: str
    assist_type: AssistType
    problem_info: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# ============================================================
# LLM 프롬프트
# ============================================================

ASSIST_SYSTEM_PROMPT = """당신은 코딩 교육 전문가입니다. 학생이 {problem_type_name} 문제를 풀고 있습니다.

## 핵심 원칙 (절대 위반 금지)
1. **힌트를 사용하지 않은 {element_name}의 정답은 절대 알려주지 마세요**
2. **힌트를 사용한 {element_name}**에 대해서만 정답과 이유를 설명할 수 있어요
3. 대신 **개념**과 **사고 방향**으로 유도하세요
4. **소크라테스식 질문**으로 스스로 깨닫게 유도하세요

## 힌트 사용 여부에 따른 규칙
- **[힌트 사용한 {element_name}]**: 정답과 그 이유를 자세히 설명해도 됨
- **[힌트 미사용 {element_name}]**: 정답 절대 금지! 직접적인 힌트보다 간접적인 힌트 제공

## 허용되는 도움
- 관련 개념/알고리즘 설명 (예: "이 문제는 DP를 활용하면 좋아요")
- 힌트 사용한 {element_name}에 대한 추가 설명
- 학생의 방향이 맞는지 확인 (예: "좋은 방향이에요! 계속해보세요")

## 금지되는 도움
- 힌트 미사용 {element_name}의 정답 공개
- 정답 코드 전체 공개
- 구체적 지시 (힌트 미사용 시)

## 도움 유형별 응답
{assist_type_guide}

## 응답 형식 (필수! 구조화된 형식으로 답변)
아래 형식을 **반드시** 따르세요:

**[한 줄 요약]**
핵심 내용을 한 문장으로

**[설명]**
2-3문장으로 쉽게 설명

**[예시]** (있으면)
간단한 예시 코드나 상황

- 격려하는 톤 유지
- 힌트 사용한 {element_name} 질문 → 정답과 이유 설명 OK
- 힌트 미사용 {element_name} 질문 → "힌트 버튼을 눌러보세요!" 유도

## 절대 금지 (Guardrails)
- 새로운 문제를 생성하거나 만들어내지 마세요
- 힌트 미사용 {element_name}의 정답을 유추하게 하는 힌트도 금지
"""

ASSIST_TYPE_GUIDES = {
    AssistType.CONCEPT_EXPLAIN: """
**개념 설명 요청**
- 문제에 필요한 핵심 개념을 설명하세요
- 알고리즘/자료구조의 기본 원리 설명
- 왜 이 개념이 필요한지 설명
- 예시는 문제와 다른 상황으로 (정답 유추 방지)
""",
    AssistType.APPROACH_HINT: """
**접근법 힌트 요청**
- 문제를 어떻게 분석할지 방향 제시
- "먼저 ~를 생각해보세요" 형태로 유도
- 구체적 코드나 답은 절대 제공 금지
- 사고 과정을 유도하는 질문 활용
""",
    AssistType.VALIDATE_DIRECTION: """
**방향 확인 요청**
- 학생의 접근이 맞는지 피드백
- 맞으면 격려하고 계속 진행 유도
- 틀리면 "다른 방향도 생각해보세요" 정도로 힌트
- 정확히 무엇이 틀렸는지는 말하지 않음
""",
    AssistType.GENERAL_HELP: """
**일반 도움 요청**
- 학생의 질문 의도를 파악
- 개념 설명이나 힌트 중 적절한 것 선택
- 막연한 질문에는 구체적으로 뭐가 어려운지 역질문
"""
}


class SolvingAssistTool:
    """문제 풀이 채팅 도움 Tool"""

    def __init__(self):
        self.supabase = get_supabase_client()

    async def assist(
        self,
        message: str,
        problem_context: Dict[str, Any],
        assist_type: AssistType = AssistType.GENERAL_HELP,
        user_progress: Optional[Dict[str, Any]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> AssistResult:
        """
        문제 풀이 중 도움을 제공합니다.

        Args:
            message: 사용자 메시지
            problem_context: 현재 문제 정보
            assist_type: 도움 유형
            user_progress: 사용자 진행 상황
            conversation_history: 대화 히스토리

        Returns:
            AssistResult
        """
        try:
            # 1. 문제 정보 보강 (DB에서 추가 정보 조회)
            enriched_context = await self._enrich_problem_context(problem_context)

            # 2. LLM 프롬프트 구성
            problem_type = enriched_context.get("problem_type", "blank")
            system_prompt = self._build_system_prompt(assist_type, problem_type)
            user_prompt = self._build_user_prompt(
                message=message,
                problem_context=enriched_context,
                user_progress=user_progress,
            )

            # 3. LLM 호출
            messages = [
                {"role": "system", "content": system_prompt},
            ]

            # 대화 히스토리 추가 (최근 6개 - 꼬리 질문 맥락 유지)
            if conversation_history:
                for msg in conversation_history[-6:]:
                    messages.append({
                        "role": msg.get("role", "user"),
                        "content": msg.get("content", ""),
                    })

            messages.append({"role": "user", "content": user_prompt})

            response = await openrouter_service.chat_completion(
                model=settings.llm_model_hint,  # 가벼운 모델 사용
                messages=messages,
                temperature=0.7,
                max_tokens=250,
            )

            content = openrouter_service.get_content(response)

            return AssistResult(
                success=True,
                response=content.strip(),
                assist_type=assist_type,
                problem_info=enriched_context,
            )

        except Exception as e:
            logger.error(f"[SolvingAssistTool] Error: {e}")
            import traceback
            traceback.print_exc()
            return AssistResult(
                success=False,
                response="도움을 제공하는 중 오류가 발생했어요. 다시 시도해주세요!",
                assist_type=assist_type,
                error=str(e),
            )

    async def _enrich_problem_context(
        self,
        problem_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        DB에서 추가 문제 정보를 조회하여 컨텍스트를 보강합니다.

        - base_problems에서 solutions (정답 코드) 조회
        - problems_blank/puzzle에서 구조 정보 조회
        - 정답 자체는 LLM에 전달하되, 직접 출력은 금지
        """
        enriched = dict(problem_context)

        original_id = problem_context.get("original_id") or problem_context.get("name")
        problem_type = problem_context.get("problem_type", "blank")

        if not original_id:
            return enriched

        try:
            # 1. base_problems에서 정답 코드 및 설명 조회
            base_result = self.supabase.table("base_problems").select(
                "solutions, explanation, tags, question"
            ).eq("original_id", original_id).maybe_single().execute()

            if base_result.data:
                base_data = base_result.data
                # solutions는 내부적으로만 사용 (LLM이 참고하되 출력 금지)
                enriched["_internal_solutions"] = base_data.get("solutions", [])
                enriched["explanation"] = base_data.get("explanation")
                enriched["tags"] = base_data.get("tags", [])
                if not enriched.get("description"):
                    enriched["description"] = base_data.get("question")

            # 2. 문제 유형별 추가 정보
            if problem_type == "blank":
                blank_result = self.supabase.table("problems_blank").select(
                    "code_template, answers"
                ).eq("original_id", original_id).maybe_single().execute()

                if blank_result.data:
                    # 정답은 내부 참조용
                    enriched["_internal_blank_answers"] = blank_result.data.get("answers", [])
                    enriched["code_template"] = blank_result.data.get("code_template")
                    # 빈칸 개수 정보
                    template = blank_result.data.get("code_template", "")
                    blank_count = template.count("_") // 2  # _0_, _1_ 형식
                    enriched["blank_count"] = blank_count

            elif problem_type == "puzzle":
                puzzle_result = self.supabase.table("problems_puzzle").select(
                    "blocks, fixed_start, fixed_end"
                ).eq("original_id", original_id).maybe_single().execute()

                if puzzle_result.data:
                    blocks = puzzle_result.data.get("blocks", [])
                    # 블록 내용만 전달 (순서는 내부 참조용)
                    enriched["_internal_correct_order"] = [b.get("id") for b in blocks]
                    enriched["block_contents"] = [b.get("code") for b in blocks]
                    enriched["block_count"] = len(blocks)

        except Exception as e:
            logger.warning(f"[SolvingAssistTool] DB enrichment failed: {e}")

        return enriched

    def _build_system_prompt(self, assist_type: AssistType, problem_type: str = "blank") -> str:
        """시스템 프롬프트 구성"""
        type_guide = ASSIST_TYPE_GUIDES.get(assist_type, ASSIST_TYPE_GUIDES[AssistType.GENERAL_HELP])

        # 문제 유형별 용어 설정
        if problem_type == "puzzle":
            problem_type_name = "퍼즐 (블록 정렬)"
            element_name = "블록"
        elif problem_type == "guided":
            problem_type_name = "1대1 대화형"
            element_name = "단계"
        else:  # blank
            problem_type_name = "빈칸 채우기"
            element_name = "빈칸"

        return ASSIST_SYSTEM_PROMPT.format(
            assist_type_guide=type_guide,
            problem_type_name=problem_type_name,
            element_name=element_name
        )

    def _build_user_prompt(
        self,
        message: str,
        problem_context: Dict[str, Any],
        user_progress: Optional[Dict[str, Any]] = None,
    ) -> str:
        """사용자 프롬프트 구성 - 힌트 사용 여부에 따라 정답 정보 필터링"""
        # 문제 정보
        title = problem_context.get("title") or problem_context.get("name", "문제")
        description = problem_context.get("description") or ""
        problem_type = problem_context.get("problem_type", "blank")
        difficulty = problem_context.get("difficulty", "medium")
        tags = problem_context.get("tags", [])
        code_template = problem_context.get("code_template", "")

        # 힌트 사용 정보 추출
        used_hint_indices = []
        if user_progress:
            used_hint_indices = user_progress.get("used_hint_indices", [])

        # 문제 유형별 힌트 정보 (힌트 사용 여부에 따라 정답 공개)
        type_info = ""
        hint_info = ""

        if problem_type == "blank":
            internal_answers = problem_context.get("_internal_blank_answers", [])
            blank_count = len(internal_answers) if internal_answers else problem_context.get("blank_count", 0)
            type_info = f"빈칸 채우기 문제 ({blank_count}개 빈칸)"

            if internal_answers:
                # 힌트 사용한 빈칸만 정답 공개
                hinted_answers = []
                unhinted_indices = []
                for idx, answer in enumerate(internal_answers):
                    if idx in used_hint_indices:
                        hinted_answers.append(f"빈칸 {idx+1}번: '{answer}' (힌트 사용됨 - 설명 가능)")
                    else:
                        unhinted_indices.append(idx + 1)

                if hinted_answers:
                    hint_info = f"""
## 힌트 사용한 빈칸 (이 빈칸들은 정답과 이유 설명 가능!)
{chr(10).join(hinted_answers)}
"""
                if unhinted_indices:
                    hint_info += f"""
## 힌트 미사용 빈칸 (정답 절대 금지, 간접 힌트만!)
빈칸 {', '.join(map(str, unhinted_indices))}번은 힌트를 사용하지 않았습니다.
이 빈칸들에 대해서는:
- ❌ 정답 직접 알려주기 금지
- ✅ 관련 개념/문법 설명 가능 (예: "for문은 반복에 사용해요")
- ✅ 사고 방향 유도 가능 (예: "이 부분은 반복이 필요해 보이는데, 어떤 반복문이 좋을까요?")
- ✅ 학생 코드의 방향성 확인 가능 (예: "좋은 접근이에요!")
"""

            # 코드 템플릿 정보 (빈칸 위치 파악용)
            if code_template:
                hint_info += f"""
## 코드 템플릿 (빈칸 위치 참고용)
```
{code_template[:600]}
```
"""

        elif problem_type == "puzzle":
            blocks = problem_context.get("block_contents", [])
            block_count = len(blocks) if blocks else problem_context.get("block_count", 0)
            type_info = f"퍼즐 문제 ({block_count}개 블록 정렬)"

            # 힌트 사용한 블록만 정보 공개
            if blocks:
                hinted_blocks = []
                unhinted_indices = []
                for idx, block_code in enumerate(blocks):
                    if idx in used_hint_indices:
                        hinted_blocks.append(f"블록 {idx+1}: ```{block_code[:100]}``` (힌트 사용됨 - 역할 설명 가능)")
                    else:
                        unhinted_indices.append(idx + 1)

                if hinted_blocks:
                    hint_info = f"""
## 힌트 사용한 블록 (이 블록들은 역할 설명 가능!)
{chr(10).join(hinted_blocks)}
"""
                if unhinted_indices:
                    hint_info += f"""
## 힌트 미사용 블록 (순서/위치 절대 금지, 간접 힌트만!)
블록 {', '.join(map(str, unhinted_indices))}번은 힌트를 사용하지 않았습니다.
이 블록들에 대해서는:
- ❌ 순서나 위치 직접 알려주기 금지
- ✅ 블록 코드의 역할 설명 가능 (예: "이 블록은 변수를 초기화하는 코드네요")
- ✅ 프로그램 흐름 개념 설명 가능 (예: "보통 변수 초기화는 먼저 하고, 계산은 그 다음에 해요")
- ✅ 학생의 정렬 시도에 대해 방향성 피드백 가능
"""

        # 정답 코드 (개념 파악용 - 힌트 사용한 경우만)
        solutions_info = ""
        if used_hint_indices:  # 힌트를 하나라도 사용한 경우만 솔루션 참고 허용
            internal_solutions = problem_context.get("_internal_solutions", [])
            if internal_solutions:
                first_sol = internal_solutions[0] if internal_solutions else {}
                solutions_info = f"""
## 정답 코드 (힌트 사용 빈칸 설명용 참고 - 전체 코드 출력 금지)
```
{first_sol.get('code', '')[:500]}
```
"""

        # 사용자 진행 상황
        progress_info = ""
        if user_progress:
            current_code = user_progress.get("current_code", "")
            current_answers = user_progress.get("current_answers", {})
            if current_code:
                progress_info = f"\n## 학생의 현재 코드:\n```\n{current_code[:300]}\n```"
            if current_answers:
                progress_info += f"\n## 학생이 입력한 답:\n{current_answers}"

        prompt = f"""## 문제 정보
- 제목: {title}
- 유형: {type_info}
- 난이도: {difficulty}
- 주제: {', '.join(tags) if tags else '알고리즘'}
- 설명: {description[:400]}
{hint_info}
{solutions_info}
{progress_info}

## 학생 질문
"{message}"

**중요**: 힌트 사용한 빈칸/블록만 정답 설명 가능! 미사용 빈칸/블록 정답은 절대 금지!"""

        return prompt

    def classify_assist_type(self, message: str) -> AssistType:
        """
        메시지에서 도움 유형을 분류합니다.
        """
        message_lower = message.lower()

        # 개념 설명 패턴
        concept_patterns = [
            "뭐야", "뭔가요", "무엇", "개념", "원리", "왜", "이유",
            "어떻게 동작", "설명", "알려줘", "이해가 안",
        ]
        for pattern in concept_patterns:
            if pattern in message_lower:
                return AssistType.CONCEPT_EXPLAIN

        # 방향 확인 패턴
        validate_patterns = [
            "맞아", "맞나", "맞는지", "이렇게 하면", "이 방향",
            "괜찮", "틀린", "맞죠", "이게 맞아",
        ]
        for pattern in validate_patterns:
            if pattern in message_lower:
                return AssistType.VALIDATE_DIRECTION

        # 접근법 힌트 패턴
        hint_patterns = [
            "어떻게", "힌트", "모르겠", "막혔", "시작", "접근",
            "방법", "도움", "알려", "가르쳐",
        ]
        for pattern in hint_patterns:
            if pattern in message_lower:
                return AssistType.APPROACH_HINT

        return AssistType.GENERAL_HELP


# Singleton
_solving_assist_tool = None


def get_solving_assist_tool() -> SolvingAssistTool:
    """SolvingAssistTool 싱글톤 반환"""
    global _solving_assist_tool
    if _solving_assist_tool is None:
        _solving_assist_tool = SolvingAssistTool()
    return _solving_assist_tool
