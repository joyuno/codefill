"""
Hint Service
문제 유형별 힌트 생성 서비스

- Blank: 빈칸 채우기 힌트
- Puzzle: 블록 순서 힌트
- Guided: 단계별 도움
"""

import json
import logging
from typing import Dict, Any, Optional, List
from ..database import get_supabase_client
from ..services.openrouter import openrouter_service
from ..config import get_settings
from ..prompts.hint_blank_agent import BLANK_HINT_SYSTEM_PROMPT
from ..prompts.hint_puzzle_agent import PUZZLE_HINT_SYSTEM_PROMPT
from ..prompts.hint_guided_agent import GUIDED_HINT_SYSTEM_PROMPT

logger = logging.getLogger(__name__)
settings = get_settings()


class HintService:
    """문제 유형별 힌트 생성 서비스"""

    def __init__(self):
        self.supabase = get_supabase_client()

    # ============================================================
    # DB 조회 메서드
    # ============================================================

    def get_blank_problem(self, problem_id: str) -> Optional[Dict[str, Any]]:
        """problems_blank 테이블에서 문제 조회"""
        try:
            result = self.supabase.table("problems_blank") \
                .select("*") \
                .eq("id", problem_id) \
                .single() \
                .execute()

            return result.data if result.data else None

        except Exception as e:
            logger.error(f"[HintService] Failed to get blank problem: {e}")
            return None

    def get_puzzle_problem(self, problem_id: str) -> Optional[Dict[str, Any]]:
        """problems_puzzle 테이블에서 문제 조회"""
        try:
            result = self.supabase.table("problems_puzzle") \
                .select("*") \
                .eq("id", problem_id) \
                .single() \
                .execute()

            return result.data if result.data else None

        except Exception as e:
            logger.error(f"[HintService] Failed to get puzzle problem: {e}")
            return None

    def get_guided_problem(self, problem_id: str) -> Optional[Dict[str, Any]]:
        """problems_guided 테이블에서 문제 조회"""
        try:
            result = self.supabase.table("problems_guided") \
                .select("*") \
                .eq("id", problem_id) \
                .single() \
                .execute()

            return result.data if result.data else None

        except Exception as e:
            logger.error(f"[HintService] Failed to get guided problem: {e}")
            return None

    def get_base_problem(self, base_problem_id: str) -> Optional[Dict[str, Any]]:
        """base_problems 테이블에서 문제 정보 조회"""
        try:
            result = self.supabase.table("base_problems") \
                .select("id, name, question, difficulty, tags, solutions, input_output") \
                .eq("id", base_problem_id) \
                .single() \
                .execute()

            return result.data if result.data else None

        except Exception as e:
            logger.error(f"[HintService] Failed to get base problem: {e}")
            return None

    # ============================================================
    # Blank 힌트 생성
    # ============================================================

    async def generate_blank_hint(
        self,
        problem_id: str,
        base_problem_id: Optional[str],
        hint_level: int,
        current_blank_index: int = 0,
        user_answers: Optional[Dict[str, str]] = None,
        previous_hints: Optional[List[str]] = None,
        user_level: str = "intermediate",
        additional_info: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        빈칸 채우기 문제 힌트 생성

        Args:
            problem_id: problems_blank 테이블의 ID
            base_problem_id: base_problems 테이블의 ID (선택)
            hint_level: 힌트 레벨 (1-4)
            current_blank_index: 현재 질문하는 빈칸 번호 (0부터 시작)
            user_answers: 사용자가 현재 입력한 답들 {"0": "len", "1": ""}
            previous_hints: 이전에 제공한 힌트들
            user_level: 사용자 레벨
            additional_info: 추가 문제 정보 (프론트에서 전달)

        Returns:
            힌트 응답 딕셔너리
        """
        previous_hints = previous_hints or []
        user_answers = user_answers or {}

        # 1. problems_blank에서 데이터 조회
        blank_problem = self.get_blank_problem(problem_id)

        if not blank_problem:
            logger.warning(f"[HintService] Blank problem not found: {problem_id}")
            # 프론트에서 전달한 정보로 폴백
            if additional_info:
                blank_problem = {
                    "code_template": additional_info.get("code_template", ""),
                    "answers": additional_info.get("answers", []),
                    "language": additional_info.get("language", "python"),
                }
            else:
                return self._error_response("문제를 찾을 수 없습니다.")

        code_template = blank_problem.get("code_template", "")
        answers = blank_problem.get("answers", [])
        language = blank_problem.get("language", "python")

        # 2. base_problems에서 문제 정보 조회
        title = "문제"
        description = ""
        difficulty = "medium"
        topics = []
        solution_code = "(정답 코드 없음)"

        if base_problem_id:
            base_problem = self.get_base_problem(base_problem_id)
            if base_problem:
                title = base_problem.get("name", "문제")
                description = base_problem.get("question", "")[:500]  # 500자 제한
                difficulty = base_problem.get("difficulty", "medium")
                topics = base_problem.get("tags", [])
                # solutions에서 정답 코드 추출
                solutions = base_problem.get("solutions", [])
                if solutions:
                    # 언어에 맞는 솔루션 찾기
                    matching_sol = next((s for s in solutions if s.get("language") == language), None)
                    if matching_sol:
                        solution_code = matching_sol.get("code", "(정답 코드 없음)")
                    elif solutions[0]:
                        solution_code = solutions[0].get("code", "(정답 코드 없음)")
        elif additional_info:
            title = additional_info.get("title", "문제")
            description = additional_info.get("description", "")[:500]
            difficulty = additional_info.get("difficulty", "medium")
            topics = additional_info.get("topics", [])
            # 프론트에서 전달한 solution_code
            solution_code = additional_info.get("solution_code", "(정답 코드 없음)")

        # 3. 빈칸 수 및 현재 빈칸 검증
        total_blanks = len(answers)
        if current_blank_index >= total_blanks:
            current_blank_index = 0

        # 4. 힌트용 정답 정보 (레벨별로 다르게 제공)
        current_answer = answers[current_blank_index] if current_blank_index < len(answers) else ""
        answers_for_hint = self._prepare_answers_for_hint(answers, current_blank_index, hint_level)

        # 5. 시스템 프롬프트 구성
        system_prompt = BLANK_HINT_SYSTEM_PROMPT.format(
            title=title,
            description=description,
            difficulty=difficulty,
            language=language,
            topics=", ".join(topics) if topics else "알고리즘",
            code_template=code_template,
            total_blanks=total_blanks,
            current_blank_index=current_blank_index,
            user_answers=json.dumps(user_answers, ensure_ascii=False),
            answers_for_hint=answers_for_hint,
            solution_code=solution_code,
            hint_level=hint_level,
            previous_hints=json.dumps(previous_hints, ensure_ascii=False) if previous_hints else "없음",
        )

        # 6. LLM 호출
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"빈칸 {current_blank_index}번에 대한 Level {hint_level} 힌트를 생성해주세요."},
        ]

        try:
            response = await openrouter_service.chat_completion(
                model=settings.llm_model_hint,
                messages=messages,
                temperature=0.7,
                response_format={"type": "json_object"},
            )

            content = openrouter_service.get_content(response)
            result = openrouter_service.parse_json_response(content)

            logger.info(f"[HintService] Blank hint generated: level={hint_level}, blank={current_blank_index}")

            return result

        except Exception as e:
            logger.error(f"[HintService] Blank hint generation error: {e}")
            return self._fallback_blank_hint(hint_level, current_blank_index, current_answer)

    def _prepare_answers_for_hint(
        self,
        answers: List[str],
        current_blank_index: int,
        hint_level: int
    ) -> str:
        """
        힌트 레벨에 따라 정답 정보를 다르게 제공
        - Level 1-2: 정답 유형만
        - Level 3: 첫 글자와 길이
        - Level 4: 거의 정답
        """
        if current_blank_index >= len(answers):
            return "정답 정보 없음"

        answer = answers[current_blank_index]

        if hint_level == 1:
            return f"(정답 길이: {len(answer)}글자)"
        elif hint_level == 2:
            answer_type = self._detect_answer_type(answer)
            return f"(정답 유형: {answer_type}, 길이: {len(answer)}글자)"
        elif hint_level == 3:
            if len(answer) <= 1:
                return f"(정답: 1글자, 첫 글자: '{answer[0] if answer else '?'}')"
            return f"(정답: '{answer[0]}...' ({len(answer)}글자))"
        elif hint_level == 4:
            if len(answer) <= 2:
                return f"(정답: '{answer[0]}_')"
            else:
                # 마지막 1-2글자만 가림
                visible = answer[:-1] if len(answer) <= 4 else answer[:-2]
                return f"(정답: '{visible}...')"

        return "(정답 정보 비공개)"

    def _detect_answer_type(self, answer: str) -> str:
        """정답의 유형 감지"""
        operators = ["+", "-", "*", "/", "%", "//", "**", "==", "!=", "<", ">", "<=", ">=", "and", "or", "not", "in", "is"]
        builtins = ["len", "range", "print", "input", "int", "str", "float", "list", "dict", "set", "tuple", "sum", "max", "min", "abs", "sorted", "enumerate", "zip", "map", "filter", "open", "type", "isinstance"]
        methods = ["append", "extend", "insert", "remove", "pop", "clear", "index", "count", "sort", "reverse", "copy", "split", "join", "strip", "replace", "find", "upper", "lower", "keys", "values", "items", "get", "update"]
        keywords = ["if", "else", "elif", "for", "while", "break", "continue", "return", "def", "class", "import", "from", "as", "try", "except", "finally", "with", "yield", "lambda", "pass", "raise", "True", "False", "None"]

        if answer in operators:
            return "연산자"
        elif answer in builtins:
            return "내장 함수"
        elif answer in methods:
            return "메서드"
        elif answer in keywords:
            return "키워드"
        elif answer.isdigit() or (answer.startswith("-") and answer[1:].isdigit()):
            return "숫자"
        elif answer.isidentifier():
            return "변수/식별자"
        else:
            return "표현식"

    def _fallback_blank_hint(self, hint_level: int, blank_index: int, answer: str) -> Dict[str, Any]:
        """LLM 실패 시 폴백 힌트"""
        hint_messages = {
            1: f"빈칸 {blank_index}번을 살펴보세요. 주변 코드의 흐름을 따라가면 어떤 값이 필요한지 알 수 있어요.",
            2: f"이 빈칸에는 {self._detect_answer_type(answer)}가 들어가야 해요.",
            3: f"정답은 {len(answer)}글자예요. '{answer[0]}...'로 시작해요.",
            4: f"거의 다 왔어요! 정답은 '{answer[:-1] if len(answer) > 1 else answer}...'예요.",
        }

        return {
            "hint_level": hint_level,
            "hint_content": hint_messages.get(hint_level, "힌트를 불러올 수 없어요."),
            "hint_type": ["context", "operation", "range", "almost"][hint_level - 1],
            "questions": ["코드의 흐름을 따라가 보세요."],
            "blank_focus": {
                "blank_index": blank_index,
                "surrounding_code": None,
                "expected_role": None,
            },
            "encouragement": "포기하지 마세요! 조금만 더 생각해보면 답을 찾을 수 있어요.",
            "next_hint_preview": "다음 힌트에서는 더 구체적인 정보를 드릴게요." if hint_level < 4 else None,
        }

    def _error_response(self, message: str) -> Dict[str, Any]:
        """에러 응답"""
        return {
            "hint_level": 1,
            "hint_content": message,
            "hint_type": "error",
            "questions": [],
            "encouragement": "다시 시도해주세요!",
        }

    # ============================================================
    # Puzzle 힌트 생성
    # ============================================================

    async def generate_puzzle_hint(
        self,
        problem_id: str,
        base_problem_id: Optional[str],
        hint_level: int,
        user_order: Optional[List[str]] = None,
        correct_blocks: Optional[List[str]] = None,
        previous_hints: Optional[List[str]] = None,
        user_level: str = "intermediate",
        additional_info: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        퍼즐 (블록 정렬) 문제 힌트 생성

        Args:
            problem_id: problems_puzzle 테이블의 ID
            base_problem_id: base_problems 테이블의 ID (선택)
            hint_level: 힌트 레벨 (1-4)
            user_order: 사용자가 현재 정렬한 블록 ID 순서
            correct_blocks: 이미 정답으로 잠긴 블록 ID들
            previous_hints: 이전에 제공한 힌트들
            user_level: 사용자 레벨
            additional_info: 추가 문제 정보 (프론트에서 전달)

        Returns:
            힌트 응답 딕셔너리
        """
        previous_hints = previous_hints or []
        user_order = user_order or []
        correct_blocks = correct_blocks or []

        # 1. problems_puzzle에서 데이터 조회
        puzzle_problem = self.get_puzzle_problem(problem_id)

        if not puzzle_problem:
            logger.warning(f"[HintService] Puzzle problem not found: {problem_id}")
            # 프론트에서 전달한 정보로 폴백
            if additional_info:
                puzzle_problem = {
                    "blocks": additional_info.get("blocks", []),
                    "fixed_start": additional_info.get("fixed_start", ""),
                    "fixed_end": additional_info.get("fixed_end", ""),
                    "language": additional_info.get("language", "python"),
                }
            else:
                return self._error_response("문제를 찾을 수 없습니다.")

        blocks = puzzle_problem.get("blocks", [])
        fixed_start = puzzle_problem.get("fixed_start", "")
        fixed_end = puzzle_problem.get("fixed_end", "")
        language = puzzle_problem.get("language", "python")

        # 2. base_problems에서 문제 정보 조회
        title = "문제"
        description = ""
        difficulty = "medium"
        topics = []
        solution_code = "(정답 코드 없음)"

        if base_problem_id:
            base_problem = self.get_base_problem(base_problem_id)
            if base_problem:
                title = base_problem.get("name", "문제")
                description = base_problem.get("question", "")[:500]
                difficulty = base_problem.get("difficulty", "medium")
                topics = base_problem.get("tags", [])
                # solutions에서 정답 코드 추출
                solutions = base_problem.get("solutions", [])
                if solutions:
                    matching_sol = next((s for s in solutions if s.get("language") == language), None)
                    if matching_sol:
                        solution_code = matching_sol.get("code", "(정답 코드 없음)")
                    elif solutions[0]:
                        solution_code = solutions[0].get("code", "(정답 코드 없음)")
        elif additional_info:
            title = additional_info.get("title", "문제")
            description = additional_info.get("description", "")[:500]
            difficulty = additional_info.get("difficulty", "medium")
            topics = additional_info.get("topics", [])
            solution_code = additional_info.get("solution_code", "(정답 코드 없음)")

        # 3. 블록 정보 구성
        total_blocks = len(blocks)
        blocks_info = self._format_blocks_info(blocks)
        correct_order_hint = self._prepare_puzzle_order_hint(blocks, hint_level)

        # 4. 시스템 프롬프트 구성
        system_prompt = PUZZLE_HINT_SYSTEM_PROMPT.format(
            title=title,
            description=description,
            difficulty=difficulty,
            language=language,
            topics=", ".join(topics) if topics else "알고리즘",
            fixed_start=fixed_start or "(없음)",
            fixed_end=fixed_end or "(없음)",
            total_blocks=total_blocks,
            user_order=json.dumps(user_order, ensure_ascii=False) if user_order else "(아직 정렬 안 함)",
            correct_blocks=json.dumps(correct_blocks, ensure_ascii=False) if correct_blocks else "(없음)",
            blocks_info=blocks_info,
            correct_order_hint=correct_order_hint,
            solution_code=solution_code,
            hint_level=hint_level,
            previous_hints=json.dumps(previous_hints, ensure_ascii=False) if previous_hints else "없음",
        )

        # 5. LLM 호출
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Level {hint_level} 힌트를 생성해주세요."},
        ]

        try:
            response = await openrouter_service.chat_completion(
                model=settings.llm_model_hint,
                messages=messages,
                temperature=0.7,
                response_format={"type": "json_object"},
            )

            content = openrouter_service.get_content(response)
            result = openrouter_service.parse_json_response(content)

            logger.info(f"[HintService] Puzzle hint generated: level={hint_level}")

            return result

        except Exception as e:
            logger.error(f"[HintService] Puzzle hint generation error: {e}")
            return self._fallback_puzzle_hint(hint_level, blocks, user_order)

    def _format_blocks_info(self, blocks: List[Dict[str, Any]]) -> str:
        """블록 정보를 문자열로 포맷"""
        if not blocks:
            return "(블록 정보 없음)"

        lines = []
        for i, block in enumerate(blocks):
            block_id = block.get("id", i)
            code = block.get("code", "")
            lines.append(f"블록 {block_id}: ```{code}```")

        return "\n".join(lines)

    def _prepare_puzzle_order_hint(
        self,
        blocks: List[Dict[str, Any]],
        hint_level: int
    ) -> str:
        """
        힌트 레벨에 따라 정답 순서 정보를 다르게 제공
        - Level 1: 전체 블록 수만
        - Level 2: 첫 번째/마지막 블록 힌트
        - Level 3: 앞/중간/뒤 그룹 힌트
        - Level 4: 거의 완전한 순서
        """
        if not blocks:
            return "(정답 순서 정보 없음)"

        # 블록들을 ID 순서로 정렬 (ID가 정답 순서)
        sorted_blocks = sorted(blocks, key=lambda b: b.get("id", 0))
        total = len(sorted_blocks)

        if hint_level == 1:
            return f"(총 {total}개 블록을 올바른 순서로 정렬해야 함)"
        elif hint_level == 2:
            first_code = sorted_blocks[0].get("code", "")[:30]
            last_code = sorted_blocks[-1].get("code", "")[:30]
            return f"(첫 번째 블록: '{first_code}...', 마지막 블록: '{last_code}...')"
        elif hint_level == 3:
            # 앞/중간/뒤 3등분
            front = [b.get("id") for b in sorted_blocks[:total//3 + 1]]
            back = [b.get("id") for b in sorted_blocks[-(total//3 + 1):]]
            return f"(앞부분 블록 ID: {front}, 뒷부분 블록 ID: {back})"
        elif hint_level == 4:
            # 거의 완전한 순서 (마지막 2개만 가림)
            if total <= 3:
                visible = [b.get("id") for b in sorted_blocks[:-1]]
                return f"(순서: {visible} + ?)"
            else:
                visible = [b.get("id") for b in sorted_blocks[:-2]]
                return f"(순서: {visible} + ?, ?)"

        return "(정답 순서 비공개)"

    def _fallback_puzzle_hint(
        self,
        hint_level: int,
        blocks: List[Dict[str, Any]],
        user_order: List[str]
    ) -> Dict[str, Any]:
        """LLM 실패 시 폴백 힌트"""
        total = len(blocks)
        sorted_blocks = sorted(blocks, key=lambda b: b.get("id", 0))

        hint_messages = {
            1: "코드의 전체 흐름을 생각해보세요. 초기화 → 로직 → 결과 순서가 자연스러워요.",
            2: f"첫 번째로 와야 할 블록은 '{sorted_blocks[0].get('code', '')[:20]}...'예요.",
            3: f"총 {total}개 블록 중 앞쪽 1/3은 초기화와 관련있어요.",
            4: f"거의 다 왔어요! 마지막 2개 블록만 순서를 확인해보세요.",
        }

        return {
            "hint_level": hint_level,
            "hint_content": hint_messages.get(hint_level, "힌트를 불러올 수 없어요."),
            "hint_type": ["structure", "group", "position", "almost"][hint_level - 1],
            "puzzle_focus": {
                "wrong_blocks_count": len(user_order) if user_order else total,
                "focus_block_index": 0,
                "suggested_position": "앞부분" if hint_level <= 2 else "중간",
                "lock_suggestion": None,
            },
            "questions": ["코드의 실행 순서를 생각해보세요."],
            "encouragement": "포기하지 마세요! 논리적인 순서를 따라가면 답을 찾을 수 있어요.",
            "next_hint_preview": "다음 힌트에서는 더 구체적인 위치를 알려드릴게요." if hint_level < 4 else None,
        }

    # ============================================================
    # Guided 도움 생성
    # ============================================================

    async def generate_guided_help(
        self,
        problem_id: str,
        base_problem_id: Optional[str],
        help_level: int,
        current_step: int = 0,
        user_code: Optional[str] = None,
        previous_helps: Optional[List[str]] = None,
        user_level: str = "intermediate",
        additional_info: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        1대1 대화형 문제 도움 생성

        Args:
            problem_id: problems_guided 테이블의 ID
            base_problem_id: base_problems 테이블의 ID (선택)
            help_level: 도움 레벨 (1-4)
            current_step: 현재 학습 단계 (0부터 시작)
            user_code: 사용자가 현재 작성 중인 코드
            previous_helps: 이전에 제공한 도움들
            user_level: 사용자 레벨
            additional_info: 추가 문제 정보 (프론트에서 전달)

        Returns:
            도움 응답 딕셔너리
        """
        previous_helps = previous_helps or []
        user_code = user_code or ""

        # 1. problems_guided에서 데이터 조회
        guided_problem = self.get_guided_problem(problem_id)

        if not guided_problem:
            logger.warning(f"[HintService] Guided problem not found: {problem_id}")
            # 프론트에서 전달한 정보로 폴백
            if additional_info:
                guided_problem = {
                    "concepts": additional_info.get("concepts", []),
                    "flow": additional_info.get("flow", []),
                    "checkpoints": additional_info.get("checkpoints", []),
                    "language": additional_info.get("language", "python"),
                }
            else:
                return self._error_response("문제를 찾을 수 없습니다.")

        concepts = guided_problem.get("concepts", [])
        flow = guided_problem.get("flow", [])
        checkpoints = guided_problem.get("checkpoints", [])
        language = guided_problem.get("language", "python")

        # 2. base_problems에서 문제 정보 조회
        title = "문제"
        description = ""
        difficulty = "medium"
        topics = []
        solution_code = "(정답 코드 없음)"

        if base_problem_id:
            base_problem = self.get_base_problem(base_problem_id)
            if base_problem:
                title = base_problem.get("name", "문제")
                description = base_problem.get("question", "")[:500]
                difficulty = base_problem.get("difficulty", "medium")
                topics = base_problem.get("tags", [])
                # solutions에서 정답 코드 추출
                solutions = base_problem.get("solutions", [])
                if solutions:
                    matching_sol = next((s for s in solutions if s.get("language") == language), None)
                    if matching_sol:
                        solution_code = matching_sol.get("code", "(정답 코드 없음)")
                    elif solutions[0]:
                        solution_code = solutions[0].get("code", "(정답 코드 없음)")
        elif additional_info:
            title = additional_info.get("title", "문제")
            description = additional_info.get("description", "")[:500]
            difficulty = additional_info.get("difficulty", "medium")
            topics = additional_info.get("topics", [])
            solution_code = additional_info.get("solution_code") or additional_info.get("final_code", "(정답 코드 없음)")

        # 3. 학습 구조 정보 구성
        total_steps = len(flow) if flow else 1
        concepts_str = self._format_list_as_string(concepts, "개념")
        flow_str = self._format_list_as_string(flow, "단계")
        checkpoints_str = self._format_list_as_string(checkpoints, "체크포인트")

        # 4. 시스템 프롬프트 구성
        system_prompt = GUIDED_HINT_SYSTEM_PROMPT.format(
            title=title,
            description=description,
            difficulty=difficulty,
            language=language,
            topics=", ".join(topics) if topics else "알고리즘",
            concepts=concepts_str,
            flow=flow_str,
            checkpoints=checkpoints_str,
            solution_code=solution_code,
            current_step=current_step + 1,  # 1-based for display
            total_steps=total_steps,
            user_code=user_code or "(아직 코드 작성 안 함)",
            help_level=help_level,
            previous_helps=json.dumps(previous_helps, ensure_ascii=False) if previous_helps else "없음",
        )

        # 5. LLM 호출
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Level {help_level} 도움을 생성해주세요."},
        ]

        try:
            response = await openrouter_service.chat_completion(
                model=settings.llm_model_hint,
                messages=messages,
                temperature=0.7,
                response_format={"type": "json_object"},
            )

            content = openrouter_service.get_content(response)
            result = openrouter_service.parse_json_response(content)

            logger.info(f"[HintService] Guided help generated: level={help_level}, step={current_step}")

            return result

        except Exception as e:
            logger.error(f"[HintService] Guided help generation error: {e}")
            return self._fallback_guided_help(help_level, current_step, flow)

    def _format_list_as_string(self, items: List[Any], label: str) -> str:
        """리스트를 문자열로 포맷"""
        if not items:
            return f"({label} 정보 없음)"

        lines = []
        for i, item in enumerate(items):
            if isinstance(item, dict):
                # 딕셔너리인 경우 적절히 포맷
                item_str = json.dumps(item, ensure_ascii=False)
            else:
                item_str = str(item)
            lines.append(f"{i + 1}. {item_str}")

        return "\n".join(lines)

    def _fallback_guided_help(
        self,
        help_level: int,
        current_step: int,
        flow: List[Any]
    ) -> Dict[str, Any]:
        """LLM 실패 시 폴백 도움"""
        total_steps = len(flow) if flow else 1
        current_flow = flow[current_step] if current_step < len(flow) else "현재 단계"

        help_messages = {
            1: f"현재 단계 '{current_flow}'에서 배우는 개념을 다시 살펴보세요.",
            2: f"이 단계에서는 순서대로 접근해보세요. 먼저 입력을 처리하고, 그 다음 로직을 구현해요.",
            3: f"코드의 기본 구조를 먼저 작성해보세요. 함수 정의나 반복문부터 시작해요.",
            4: f"거의 다 왔어요! 마지막으로 결과를 반환하거나 출력하는 부분만 추가하면 돼요.",
        }

        return {
            "hint_level": help_level,
            "hint_content": help_messages.get(help_level, "도움을 불러올 수 없어요."),
            "hint_type": ["concept", "approach", "template", "almost"][help_level - 1],
            "guided_focus": {
                "current_step": current_step + 1,
                "step_name": str(current_flow)[:50],
                "concepts_covered": [],
                "checkpoint_status": "in_progress",
            },
            "code_template": None,
            "questions": ["현재 단계의 목표를 다시 확인해보세요."],
            "next_step_preview": f"다음 단계에서는 더 심화된 내용을 배울 거예요." if current_step + 1 < total_steps else None,
            "encouragement": "포기하지 마세요! 한 단계씩 차근차근 진행하면 완성할 수 있어요.",
        }


# Singleton instance
_hint_service = None


def get_hint_service() -> HintService:
    """HintService 싱글톤 반환"""
    global _hint_service
    if _hint_service is None:
        _hint_service = HintService()
    return _hint_service
