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
    # base_problem_id 해결 (FK 제약 충족용)
    # ============================================================

    def resolve_base_problem_id(self, problem_id: str, problem_type: str = "blank") -> Optional[str]:
        """
        problem_id에서 base_problem_id를 결정합니다.
        problem_hints 테이블이 base_problems와 FK 관계이므로 반드시 필요.

        Args:
            problem_id: problems_blank/puzzle/guided의 ID 또는 base_problems ID
            problem_type: 'blank', 'puzzle', 'guided'

        Returns:
            base_problems.id (UUID 문자열) 또는 None
        """
        if not problem_id:
            return None

        from uuid import UUID as UUIDType

        try:
            # 1. UUID 형식인지 확인
            try:
                problem_uuid = UUIDType(problem_id)
                uuid_str = str(problem_uuid)
            except ValueError:
                # UUID가 아니면 original_id로 처리
                uuid_str = None

            if uuid_str:
                # 1-1. base_problems 테이블에서 직접 조회 (이미 base_problem_id인 경우)
                bp_result = self.supabase.table("base_problems")\
                    .select("id")\
                    .eq("id", uuid_str)\
                    .limit(1)\
                    .execute()

                if bp_result.data and len(bp_result.data) > 0:
                    print(f"[HintService] ✓ Resolved as base_problem_id directly: {uuid_str[:8]}...")
                    return bp_result.data[0]["id"]

                # 1-2. 문제 유형별 테이블에서 base_problem_id 조회
                table_name = f"problems_{problem_type}"
                try:
                    type_result = self.supabase.table(table_name)\
                        .select("base_problem_id")\
                        .eq("id", uuid_str)\
                        .limit(1)\
                        .execute()

                    if type_result.data and len(type_result.data) > 0:
                        base_problem_id = type_result.data[0].get("base_problem_id")
                        if base_problem_id:
                            print(f"[HintService] ✓ Resolved via {table_name}: {base_problem_id[:8]}...")
                            return base_problem_id
                except Exception as e:
                    print(f"[HintService] Table lookup error for {table_name}: {e}")

            # 2. original_id로 시도 (UUID가 아닌 경우)
            bp_result = self.supabase.table("base_problems")\
                .select("id")\
                .eq("original_id", problem_id)\
                .limit(1)\
                .execute()

            if bp_result.data and len(bp_result.data) > 0:
                print(f"[HintService] ✓ Resolved via original_id: {bp_result.data[0]['id'][:8]}...")
                return bp_result.data[0]["id"]

            return None

        except Exception as e:
            print(f"[HintService] resolve_base_problem_id error: {e}")
            return None

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
    # 힌트 캐싱 메서드 (모든 유형 지원: blank, puzzle, guided)
    # ============================================================

    def get_cached_hint(
        self,
        problem_id: str,
        problem_type: str,
        hint_index: int,
    ) -> Optional[Dict[str, Any]]:
        """DB에서 캐시된 힌트 조회 (problem_hints 테이블)"""
        try:
            # .single() 대신 .limit(1) 사용 (데이터 없을 때 에러 방지)
            result = self.supabase.table("problem_hints") \
                .select("hint_content") \
                .eq("problem_id", str(problem_id)) \
                .eq("problem_type", problem_type) \
                .eq("hint_index", hint_index) \
                .limit(1) \
                .execute()

            if result.data and len(result.data) > 0:
                print(f"[HintCache] ✓ HIT: {problem_type}/{problem_id[:8]}..., index={hint_index}")
                logger.info(f"[HintCache] HIT: {problem_type}/{problem_id}, index={hint_index}")
                return {
                    "hint_content": result.data[0].get("hint_content", ""),
                }

            print(f"[HintCache] MISS: {problem_type}/{problem_id[:8]}..., index={hint_index} (generating...)")
            return None

        except Exception as e:
            # 캐시 조회 실패는 무시 (LLM 생성으로 진행)
            print(f"[HintCache] Query error: {e}")
            logger.debug(f"[HintCache] MISS or error: {e}")
            return None

    def save_hint_to_cache(
        self,
        problem_id: str,
        problem_type: str,
        hint_index: int,
        hint_content: str,
    ) -> bool:
        """생성된 힌트를 DB에 캐시 (problem_hints 테이블)"""
        try:
            # Supabase Python upsert 사용
            result = self.supabase.table("problem_hints").upsert(
                {
                    "problem_id": str(problem_id),
                    "problem_type": problem_type,
                    "hint_index": hint_index,
                    "hint_content": hint_content[:2000] if hint_content else "",
                },
                on_conflict="problem_id,problem_type,hint_index"
            ).execute()

            if result.data:
                print(f"[HintCache] ✓ SAVED to problem_hints: {problem_type}/{problem_id[:8]}..., index={hint_index}")
                logger.info(f"[HintCache] SAVED: {problem_type}/{problem_id}, index={hint_index}")
                return True
            else:
                print(f"[HintCache] ⚠ Upsert returned no data: {problem_type}/{problem_id[:8]}...")
                return False

        except Exception as e:
            # 상세 에러 출력 (디버깅용)
            print(f"[HintCache] ✗ Save FAILED: {problem_type}/{problem_id[:8]}..., error={e}")
            logger.error(f"[HintCache] Save failed: {e}")
            return False

    # ============================================================
    # Blank 힌트 - 정답 + 왜 정답인지 핵심 설명 (1-2줄)
    # ============================================================

    async def generate_blank_hint(
        self,
        problem_id: str,
        blank_index: int,
        code_template: Optional[str] = None,
        additional_info: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        빈칸 힌트 - 정답과 왜 정답인지 핵심 설명 제공

        Args:
            problem_id: problems_blank 테이블의 ID
            blank_index: 빈칸 인덱스 (0-based, 프론트에서 0부터 전달)
            code_template: 코드 템플릿
            additional_info: 추가 정보

        Returns:
            {
                blank_index: int,
                answer: str,  # 정답
                hint_content: str,  # 왜 정답인지 핵심 설명 (1-2줄)
                from_cache: bool,
            }
        """
        # 📍 인덱스 검증 및 로깅
        print(f"[HintService] 📥 generate_blank_hint called: problem_id={problem_id[:8]}..., blank_index={blank_index}")

        # blank_index 유효성 검증 (음수이면 0으로)
        if blank_index < 0:
            print(f"[HintService] ⚠ Invalid negative blank_index={blank_index}, correcting to 0")
            blank_index = 0

        # base_problem_id 해결 (FK 제약 충족용)
        base_problem_id = self.resolve_base_problem_id(problem_id, "blank")
        cache_problem_id = base_problem_id or problem_id  # FK용 ID 또는 폴백

        if not base_problem_id:
            print(f"[HintService] ⚠ Could not resolve base_problem_id for blank/{problem_id[:8]}...")

        # 빈칸 문제 정보 가져오기
        blank_problem = None
        if not code_template:
            blank_problem = self.get_blank_problem(problem_id)
            if blank_problem:
                code_template = blank_problem.get("code_template", "")
            elif additional_info:
                code_template = additional_info.get("code_template", "")

        if not code_template:
            return {
                "blank_index": blank_index,
                "answer": "",
                "hint_content": "코드 정보를 불러올 수 없습니다.",
                "from_cache": False,
            }

        # 정답 배열 가져오기
        answers = []
        if blank_problem:
            answers = blank_problem.get("answers", [])
        elif additional_info:
            answers = additional_info.get("answers", [])

        # 해당 빈칸의 정답 가져오기
        answer = ""
        if blank_index < len(answers):
            answer = answers[blank_index]
        else:
            print(f"[HintService] ⚠ blank_index={blank_index} >= answers length={len(answers)}")

        # 📍 코드 템플릿에서 빈칸 개수 확인 (인덱스 검증용)
        import re
        indexed_pattern = re.compile(r'_(\d+)_')
        all_blanks = indexed_pattern.findall(code_template)
        legacy_blanks = code_template.count("___")
        total_blanks = len(set(all_blanks)) if all_blanks else legacy_blanks

        print(f"[HintService] 📊 Code template analysis: indexed_blanks={sorted(set(all_blanks)) if all_blanks else 'none'}, legacy_blanks={legacy_blanks}, total={total_blanks}")

        # blank_index가 범위를 벗어나면 경고
        if total_blanks > 0 and blank_index >= total_blanks:
            print(f"[HintService] ⚠ blank_index={blank_index} >= total_blanks={total_blanks}, may be off-by-one error!")

        # 1. 캐시에서 힌트 조회 (base_problem_id 사용)
        cached = self.get_cached_hint(
            problem_id=cache_problem_id,
            problem_type="blank",
            hint_index=blank_index,
        )

        if cached:
            # 캐시 HIT - 정답과 함께 반환
            print(f"[HintService] ✓ Cache HIT for blank_index={blank_index}")
            return {
                "blank_index": blank_index,
                "answer": answer,
                "hint_content": cached["hint_content"],
                "from_cache": True,
            }

        # 2. 캐시 MISS: LLM으로 정답 설명 생성 (정답 + 왜 정답인지)
        print(f"[HintService] 🔄 Cache MISS - generating hint for blank_index={blank_index}, answer={answer}")
        hint_content = await self._generate_blank_answer_hint(
            code_template=code_template,
            blank_index=blank_index,
            answer=answer,
        )

        # 캐시에 저장 (base_problem_id가 있을 때만 - FK 제약)
        if base_problem_id:
            self.save_hint_to_cache(
                problem_id=base_problem_id,
                problem_type="blank",
                hint_index=blank_index,
                hint_content=hint_content,
            )
        else:
            print(f"[HintService] ⚠ Skipping cache save - no base_problem_id for blank/{problem_id[:8]}...")

        return {
            "blank_index": blank_index,
            "answer": answer,
            "hint_content": hint_content,
            "from_cache": False,
        }

    async def _generate_blank_answer_hint(
        self,
        code_template: str,
        blank_index: int,
        answer: str,
    ) -> str:
        """
        빈칸 정답 설명 힌트 생성 (정답 + 왜 정답인지 1-2줄 핵심 설명)
        DeepSeek V3 사용 - 코드 이해력이 뛰어남
        """
        try:
            from .openrouter import openrouter_service

            # 빈칸 주변 코드 추출
            surrounding_code = self._extract_surrounding_context(code_template, blank_index)

            # 📍 힌트 대상 빈칸을 코드에서 명확히 표시 (off-by-one 방지)
            # _N_ 패턴에서 해당 빈칸만 마커로 감싸기
            import re
            marked_code = re.sub(
                f'_{blank_index}_',
                f'>>HERE>>_{blank_index}_<<HERE<<',
                surrounding_code
            )
            # 레거시 ___ 패턴도 처리 (첫 번째만 마킹)
            if f'>>HERE>>_{blank_index}_<<HERE<<' not in marked_code and '___' in marked_code:
                # blank_index번째 ___를 찾아서 마킹
                legacy_count = 0
                def replace_nth(match):
                    nonlocal legacy_count
                    if legacy_count == blank_index:
                        legacy_count += 1
                        return '>>HERE>>___<<HERE<<'
                    legacy_count += 1
                    return match.group(0)
                marked_code = re.sub('___', replace_nth, surrounding_code)

            print(f"[HintService] Generating blank answer hint: index={blank_index}, answer={answer}, marked_code_preview={marked_code[:100]}...")

            prompt = f"""다음 코드에서 >>HERE>> ... <<HERE<< 로 표시된 빈칸의 정답은 "{answer}"입니다.
왜 이 정답이 맞는지 1-2줄로 핵심만 간결하게 설명해주세요.

코드 컨텍스트:
```
{marked_code}
```

규칙:
- "~이기 때문에 {answer}가 필요해요" 또는 "~를 위해 {answer}를 사용해요" 형식
- 코드 흐름/문법적 역할을 간결히 설명
- 한국어 1-2문장으로 핵심만 설명"""

            response = await openrouter_service.chat_completion(
                model="deepseek-v3",  # 코드 이해력이 뛰어난 DeepSeek V3 사용
                messages=[
                    {"role": "system", "content": "You are a helpful coding tutor. Explain WHY this answer is correct in 1-2 sentences. Focus on the code logic and syntax role. Respond in Korean only."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.5,
                max_tokens=150,
            )

            hint = openrouter_service.get_content(response)
            print(f"[HintService] Generated answer hint for blank {blank_index}: {hint[:50]}...")
            return hint.strip()

        except Exception as e:
            logger.error(f"[HintService] Blank answer hint error: {e}")
            # 폴백: 정답 유형 기반 간단 설명
            answer_type = self._detect_answer_type(answer)
            return f"이 자리에는 {answer_type}인 '{answer}'가 필요해요."

    async def _generate_blank_explanation(
        self,
        code_template: str,
        blank_index: int,
        answer: str,
        reveal_answer: bool = False,
    ) -> str:
        """
        빈칸에 해당 값이 들어가야 하는 이유 설명 (1-2줄)
        """
        try:
            from .openrouter import openrouter_service

            # 빈칸 주변 코드 추출 (앞뒤 3줄)
            surrounding_code = self._extract_surrounding_context(code_template, blank_index)

            if reveal_answer:
                prompt = f"""다음 코드에서 빈칸 #{blank_index + 1}에 "{answer}"가 들어가야 하는 이유를 1-2줄로 설명하세요.

코드 컨텍스트:
```
{surrounding_code}
```

규칙:
- 정답 "{answer}"가 왜 필요한지 간단히 설명
- 코드 흐름/문법적 역할 설명
- 반드시 한국어로 1-2문장만"""
            else:
                prompt = f"""다음 코드에서 빈칸 #{blank_index + 1}에 들어갈 값의 역할을 1-2줄로 설명하세요. (정답을 직접 알려주지 마세요)

코드 컨텍스트:
```
{surrounding_code}
```

규칙:
- 이 빈칸이 어떤 역할을 하는지 힌트 제공
- "~하는 역할이에요" 또는 "~를 위해 필요해요" 형식
- 반드시 한국어로 1-2문장만"""

            response = await openrouter_service.chat_completion(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful coding tutor. Respond in Korean, 1-2 sentences only."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.5,
                max_tokens=100,
            )

            explanation = openrouter_service.get_content(response)
            return explanation.strip()

        except Exception as e:
            print(f"[HintService] Blank explanation error: {e}")
            return "이 빈칸은 코드의 핵심 로직에 필요한 부분이에요."

    def _extract_surrounding_context(self, code_template: str, blank_index: int) -> str:
        """빈칸 주변 코드 추출 - _N_ 패턴 및 레거시 ___ 패턴 지원

        Args:
            code_template: 전체 코드 템플릿
            blank_index: 0-based 빈칸 인덱스
        """
        import re

        if not code_template:
            return ""

        lines = code_template.split("\n")

        # _N_ 패턴 (예: _0_, _1_, _10_) 먼저 찾기
        indexed_pattern = re.compile(r'_(\d+)_')
        target_line_idx = 0
        found = False
        found_blank_num = None

        for i, line in enumerate(lines):
            matches = indexed_pattern.findall(line)
            for match in matches:
                if int(match) == blank_index:
                    target_line_idx = i
                    found = True
                    found_blank_num = int(match)
                    break
            if found:
                break

        # _N_ 패턴 못 찾으면 레거시 ___ 패턴으로 폴백
        if not found:
            blank_count = 0
            for i, line in enumerate(lines):
                count = line.count("___")
                if count > 0:
                    if blank_count <= blank_index < blank_count + count:
                        target_line_idx = i
                        found = True
                        found_blank_num = blank_index
                        break
                    blank_count += count

        # 📍 인덱스 매칭 로깅
        print(f"[HintService] 🔍 _extract_surrounding_context: blank_index={blank_index}, found={found}, found_blank_num={found_blank_num}, target_line={target_line_idx}")

        if found:
            print(f"[HintService] 📍 Target line: '{lines[target_line_idx][:80]}...'")
        else:
            print(f"[HintService] ⚠ Could not find blank_{blank_index} in code template!")

        # 앞뒤 3줄 추출
        start = max(0, target_line_idx - 3)
        end = min(len(lines), target_line_idx + 4)

        return "\n".join(lines[start:end])

    # ============================================================
    # Puzzle 힌트 - 블록별 역할 설명 (캐싱 적용)
    # ============================================================

    async def generate_puzzle_block_hint(
        self,
        problem_id: str,
        block_index: int,
        blocks: Optional[List[Dict[str, Any]]] = None,
        additional_info: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        퍼즐 블록 힌트 - 블록의 역할 설명 (순서 알려주지 않음)

        Args:
            problem_id: problems_puzzle 테이블의 ID
            block_index: 블록 인덱스
            blocks: 블록 배열
            additional_info: 추가 정보

        Returns:
            {
                hint_index: int,
                hint_content: str,  # 블록 역할 설명
                from_cache: bool,
            }
        """
        # base_problem_id 해결 (FK 제약 충족용)
        base_problem_id = self.resolve_base_problem_id(problem_id, "puzzle")
        cache_problem_id = base_problem_id or problem_id  # FK용 ID 또는 폴백

        if not base_problem_id:
            print(f"[HintService] ⚠ Could not resolve base_problem_id for puzzle/{problem_id[:8]}...")

        # 블록 정보 가져오기
        if not blocks:
            puzzle_problem = self.get_puzzle_problem(problem_id)
            if puzzle_problem:
                blocks = puzzle_problem.get("blocks", [])
            elif additional_info:
                blocks = additional_info.get("blocks", [])

        if not blocks or block_index >= len(blocks):
            return {
                "hint_index": block_index,
                "hint_content": "블록 정보를 불러올 수 없습니다.",
                "from_cache": False,
            }

        # 1. 캐시에서 힌트 조회 (base_problem_id 사용)
        cached = self.get_cached_hint(
            problem_id=cache_problem_id,
            problem_type="puzzle",
            hint_index=block_index,
        )

        if cached:
            return {
                "hint_index": block_index,
                "hint_content": cached["hint_content"],
                "from_cache": True,
            }

        # 2. 캐시 MISS: LLM으로 힌트 생성
        block = blocks[block_index]
        block_code = block.get("code", "")

        hint_content = await self._generate_puzzle_block_role_hint(
            block_code=block_code,
            block_index=block_index,
            all_blocks=blocks,
        )

        # 캐시에 저장 (base_problem_id가 있을 때만 - FK 제약)
        if base_problem_id:
            self.save_hint_to_cache(
                problem_id=base_problem_id,
                problem_type="puzzle",
                hint_index=block_index,
                hint_content=hint_content,
            )
        else:
            print(f"[HintService] ⚠ Skipping cache save - no base_problem_id for puzzle/{problem_id[:8]}...")

        return {
            "hint_index": block_index,
            "hint_content": hint_content,
            "from_cache": False,
        }

    async def _generate_puzzle_block_role_hint(
        self,
        block_code: str,
        block_index: int,
        all_blocks: List[Dict[str, Any]],
    ) -> str:
        """퍼즐 블록 역할 힌트 생성 (순서 알려주지 않음)
        DeepSeek V3 사용 - 코드 이해력이 뛰어남
        """
        try:
            from .openrouter import openrouter_service

            # 전체 블록 코드 (컨텍스트용)
            all_code = "\n".join([b.get("code", "") for b in all_blocks])

            print(f"[HintService] Generating puzzle hint: block_index={block_index}, block_code={block_code[:50]}...")

            prompt = f"""다음 코드 블록이 전체 프로그램에서 어떤 역할을 하는지 1-2줄로 설명하세요.

블록 코드:
```
{block_code}
```

전체 블록들 (순서 무작위):
```
{all_code}
```

규칙:
- 이 블록이 무엇을 하는지만 설명
- 순서나 위치는 알려주지 마세요
- "이 블록은 ~하는 역할이에요" 형식
- 한국어 1-2문장으로 간결하게"""

            response = await openrouter_service.chat_completion(
                model="deepseek-v3",  # 코드 이해력이 뛰어난 DeepSeek V3 사용
                messages=[
                    {"role": "system", "content": "You are a helpful coding tutor. Explain what the code block does without revealing its position. Respond in Korean, 1-2 sentences only."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.5,
                max_tokens=150,
            )

            hint = openrouter_service.get_content(response)
            print(f"[HintService] Generated puzzle hint for block {block_index}: {hint[:50]}...")
            return hint.strip()

        except Exception as e:
            logger.error(f"[HintService] Puzzle block hint error: {e}")
            return "이 블록은 프로그램의 일부분을 담당해요. 코드를 잘 읽어보세요."

    # ============================================================
    # Guided 힌트 - 단계별 도움 (캐싱 적용)
    # ============================================================

    async def generate_guided_step_hint(
        self,
        problem_id: str,
        step_index: int,
        steps: Optional[List[Dict[str, Any]]] = None,
        additional_info: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Guided 단계별 힌트 - 현재 단계에서 무엇을 해야 하는지 설명

        Args:
            problem_id: problems_guided 테이블의 ID
            step_index: 단계 인덱스
            steps: 단계 배열 (flow)
            additional_info: 추가 정보

        Returns:
            {
                hint_index: int,
                hint_content: str,  # 단계별 도움
                from_cache: bool,
            }
        """
        # base_problem_id 해결 (FK 제약 충족용)
        base_problem_id = self.resolve_base_problem_id(problem_id, "guided")
        cache_problem_id = base_problem_id or problem_id  # FK용 ID 또는 폴백

        if not base_problem_id:
            print(f"[HintService] ⚠ Could not resolve base_problem_id for guided/{problem_id[:8]}...")

        # 단계 정보 가져오기
        if not steps:
            guided_problem = self.get_guided_problem(problem_id)
            if guided_problem:
                steps = guided_problem.get("flow", [])
            elif additional_info:
                steps = additional_info.get("flow", [])

        if not steps or step_index >= len(steps):
            return {
                "hint_index": step_index,
                "hint_content": "단계 정보를 불러올 수 없습니다.",
                "from_cache": False,
            }

        # 1. 캐시에서 힌트 조회 (base_problem_id 사용)
        cached = self.get_cached_hint(
            problem_id=cache_problem_id,
            problem_type="guided",
            hint_index=step_index,
        )

        if cached:
            return {
                "hint_index": step_index,
                "hint_content": cached["hint_content"],
                "from_cache": True,
            }

        # 2. 캐시 MISS: LLM으로 힌트 생성
        current_step = steps[step_index]
        step_content = current_step if isinstance(current_step, str) else json.dumps(current_step, ensure_ascii=False)

        hint_content = await self._generate_guided_step_role_hint(
            step_content=step_content,
            step_index=step_index,
            all_steps=steps,
        )

        # 캐시에 저장 (base_problem_id가 있을 때만 - FK 제약)
        if base_problem_id:
            self.save_hint_to_cache(
                problem_id=base_problem_id,
                problem_type="guided",
                hint_index=step_index,
                hint_content=hint_content,
            )
        else:
            print(f"[HintService] ⚠ Skipping cache save - no base_problem_id for guided/{problem_id[:8]}...")

        return {
            "hint_index": step_index,
            "hint_content": hint_content,
            "from_cache": False,
        }

    async def _generate_guided_step_role_hint(
        self,
        step_content: str,
        step_index: int,
        all_steps: List[Any],
    ) -> str:
        """Guided 단계 힌트 생성
        DeepSeek V3 사용 - 코드 이해력이 뛰어남
        """
        try:
            from .openrouter import openrouter_service

            total_steps = len(all_steps)

            print(f"[HintService] Generating guided hint: step_index={step_index}, total_steps={total_steps}")

            prompt = f"""현재 단계 {step_index + 1}/{total_steps}에서 학습자가 무엇을 해야 하는지 1-2줄로 도움을 주세요.

현재 단계:
{step_content}

규칙:
- 직접적인 정답을 알려주지 마세요
- "이 단계에서는 ~를 생각해보세요" 형식
- 힌트는 소크라테스식으로 질문 형태도 좋아요
- 한국어 1-2문장으로 간결하게"""

            response = await openrouter_service.chat_completion(
                model="deepseek-v3",  # 코드 이해력이 뛰어난 DeepSeek V3 사용
                messages=[
                    {"role": "system", "content": "You are a Socratic coding tutor. Guide the learner with questions without giving direct answers. Respond in Korean, 1-2 sentences only."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.5,
                max_tokens=150,
            )

            hint = openrouter_service.get_content(response)
            print(f"[HintService] Generated guided hint for step {step_index}: {hint[:50]}...")
            return hint.strip()

        except Exception as e:
            logger.error(f"[HintService] Guided step hint error: {e}")
            return "이 단계에서 필요한 것이 무엇인지 천천히 생각해보세요."

    # ============================================================
    # Blank 힌트 생성 (기존 - 레거시)
    # ============================================================

    async def generate_blank_hint_legacy(
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
                temperature=0.5,  # 힌트는 일관성 있게
                max_tokens=500,   # 힌트는 간결하게
                response_format={"type": "json_object"},
                frequency_penalty=0.3,  # 반복 방지
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
    # Puzzle 힌트 - 첫 틀린 위치 + 이유 (신규) - Smart Validator 통합
    # ============================================================

    async def generate_puzzle_hint_focused(
        self,
        problem_id: str,
        user_order: List[str],
        blocks: Optional[List[Dict[str, Any]]] = None,
        additional_info: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        퍼즐 힌트 - 스마트 검증 + 첫 틀린 블록 (2줄 이내)

        Args:
            problem_id: problems_puzzle 테이블의 ID
            user_order: 사용자가 배치한 블록 ID/인덱스 순서
            blocks: 블록 배열 (프론트에서 전달)
            additional_info: 추가 정보

        Returns:
            {
                is_correct: bool,
                hint_content: str (2줄 이내),
                first_wrong_position: int or None,
                correct_block_id: str or None,
                validation_type: "smart" | "strict" | "fallback"
            }
        """
        from .puzzle_validator import validate_puzzle

        # 블록 정보 가져오기
        if not blocks:
            puzzle_problem = self.get_puzzle_problem(problem_id)
            if puzzle_problem:
                blocks = puzzle_problem.get("blocks", [])
            elif additional_info:
                blocks = additional_info.get("blocks", [])

        if not blocks:
            return {
                "is_correct": False,
                "hint_content": "블록 정보를 불러올 수 없습니다.",
                "first_wrong_position": None,
                "correct_block_id": None,
                "validation_type": "error",
            }

        # 언어 정보
        language = "python"
        if additional_info:
            language = additional_info.get("language", "python")

        # 정답 순서 계산 (order 필드 기준)
        sorted_blocks = sorted(blocks, key=lambda b: b.get("order", 0))
        correct_order_ids = [b.get("id") for b in sorted_blocks]

        # 블록 내용 추출
        block_contents = [b.get("code", "") for b in sorted_blocks]

        # user_order를 인덱스로 변환 (ID -> index)
        id_to_idx = {b.get("id"): i for i, b in enumerate(sorted_blocks)}
        try:
            user_order_indices = [id_to_idx.get(uid, -1) for uid in user_order]
            correct_order_indices = list(range(len(sorted_blocks)))

            # 잘못된 ID가 있으면 폴백
            if -1 in user_order_indices:
                raise ValueError("Invalid block ID in user_order")

        except Exception as e:
            logger.warning(f"[HintService] Index conversion failed: {e}")
            # 폴백: 단순 비교
            return await self._fallback_puzzle_hint_focused(
                user_order, blocks, correct_order_ids
            )

        # 스마트 검증 수행
        try:
            result = await validate_puzzle(
                blocks=block_contents,
                user_order=user_order_indices,
                correct_order=correct_order_indices,
                language=language,
                strict_mode=False,
            )

            if result.is_correct:
                return {
                    "is_correct": True,
                    "hint_content": result.feedback,
                    "first_wrong_position": None,
                    "correct_block_id": None,
                    "validation_type": "smart",
                    "score": result.score,
                }

            # 틀린 경우 상세 정보 제공
            first_wrong_pos = result.first_wrong_position
            if first_wrong_pos is not None and first_wrong_pos < len(sorted_blocks):
                correct_block = sorted_blocks[correct_order_indices[first_wrong_pos]]
                correct_code = correct_block.get("code", "")[:60]
                correct_id = correct_block.get("id")

                # 이유 생성
                reason = await self._generate_puzzle_reason(
                    position=first_wrong_pos,
                    correct_code=correct_code,
                    blocks=blocks,
                )

                hint_content = (
                    f"블록 {first_wrong_pos + 1}번 위치가 틀렸어요.\n"
                    f"{reason}"
                )

                return {
                    "is_correct": False,
                    "hint_content": hint_content,
                    "first_wrong_position": first_wrong_pos,
                    "correct_block_id": correct_id,
                    "correct_code_preview": correct_code[:30],
                    "validation_type": "smart",
                    "score": result.score,
                }

            # first_wrong_position이 없는 경우
            return {
                "is_correct": False,
                "hint_content": result.feedback,
                "first_wrong_position": None,
                "correct_block_id": None,
                "validation_type": "smart",
                "score": result.score,
            }

        except Exception as e:
            logger.error(f"[HintService] Smart validation error: {e}")
            return await self._fallback_puzzle_hint_focused(
                user_order, blocks, correct_order_ids
            )

    async def _fallback_puzzle_hint_focused(
        self,
        user_order: List[str],
        blocks: List[Dict[str, Any]],
        correct_order: List[str],
    ) -> Dict[str, Any]:
        """스마트 검증 실패 시 폴백 힌트"""
        user_order_str = [str(b) for b in user_order]
        correct_order_str = [str(c) for c in correct_order]

        first_wrong = None
        for i, (user_id, correct_id) in enumerate(zip(user_order_str, correct_order_str)):
            if user_id != correct_id:
                first_wrong = {"position": i, "correct_block": correct_id}
                break

        if not first_wrong:
            return {
                "is_correct": True,
                "hint_content": "모두 정답입니다!",
                "first_wrong_position": None,
                "correct_block_id": None,
                "validation_type": "fallback",
            }

        correct_block = next(
            (b for b in blocks if str(b.get("id")) == first_wrong["correct_block"]),
            None
        )

        correct_code = correct_block.get("code", "")[:30] if correct_block else "?"

        return {
            "is_correct": False,
            "hint_content": f"블록 {first_wrong['position'] + 1}번이 틀렸어요. 정답 블록을 확인해보세요.",
            "first_wrong_position": first_wrong["position"],
            "correct_block_id": first_wrong["correct_block"],
            "correct_code_preview": correct_code,
            "validation_type": "fallback",
        }

    async def _generate_puzzle_reason(
        self,
        position: int,
        correct_code: str,
        blocks: List[Dict[str, Any]],
    ) -> str:
        """퍼즐 오답 이유 생성 (1줄)"""
        try:
            # 간단한 휴리스틱 우선
            code_lower = correct_code.lower().strip()

            # 코드 패턴으로 이유 추론
            if code_lower.startswith("def "):
                return "함수 정의가 먼저 와야 해요."
            elif code_lower.startswith("class "):
                return "클래스 정의가 먼저 와야 해요."
            elif code_lower.startswith("import ") or code_lower.startswith("from "):
                return "import문은 보통 가장 위에 와요."
            elif code_lower.startswith("for ") or code_lower.startswith("while "):
                return "반복문이 이 위치에 와야 해요."
            elif code_lower.startswith("if "):
                return "조건문이 이 위치에 와야 해요."
            elif code_lower.startswith("return "):
                return "return문은 함수 마지막에 와요."
            elif "=" in code_lower and not "==" in code_lower:
                return "변수 초기화가 이 위치에 필요해요."
            else:
                # 기본 메시지
                return "코드 실행 순서를 생각해보세요."

        except Exception as e:
            logger.error(f"[HintService] Puzzle reason generation error: {e}")
            return "이 블록이 먼저 와야 해요."

    # ============================================================
    # Puzzle 힌트 생성 (기존)
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
                temperature=0.5,  # 힌트는 일관성 있게
                max_tokens=500,   # 힌트는 간결하게
                response_format={"type": "json_object"},
                frequency_penalty=0.3,  # 반복 방지
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
                temperature=0.5,  # 힌트는 일관성 있게
                max_tokens=500,   # 힌트는 간결하게
                response_format={"type": "json_object"},
                frequency_penalty=0.3,  # 반복 방지
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

    # ============================================================
    # 힌트 사전 생성 (백그라운드 태스크)
    # ============================================================

    async def pregenerate_all_hints(
        self,
        problem_type: str,
        problem_id: str,
        problem_data: Dict[str, Any],
    ) -> None:
        """
        문제 생성 직후 모든 힌트를 백그라운드에서 미리 생성

        Args:
            problem_type: 'blank' | 'puzzle' | 'guided'
            problem_id: base_problem_id (UUID)
            problem_data: 생성된 문제 데이터

        힌트 개수:
            - blank: answers 배열 길이만큼
            - puzzle: blocks 배열 길이만큼
            - guided: variables_guide.variables 배열 길이만큼
        """
        import asyncio

        try:
            print(f"[HintPregen] Starting pregeneration for {problem_type}/{problem_id[:8]}...")

            if problem_type == "blank":
                await self._pregenerate_blank_hints(problem_id, problem_data)
            elif problem_type == "puzzle":
                await self._pregenerate_puzzle_hints(problem_id, problem_data)
            elif problem_type == "guided":
                await self._pregenerate_guided_hints(problem_id, problem_data)
            else:
                print(f"[HintPregen] Unknown problem type: {problem_type}")

        except Exception as e:
            # 백그라운드 태스크이므로 에러는 로깅만
            print(f"[HintPregen] Error: {e}")
            logger.error(f"[HintPregen] Failed for {problem_type}/{problem_id}: {e}")

    async def _pregenerate_blank_hints(
        self,
        problem_id: str,
        problem_data: Dict[str, Any],
    ) -> None:
        """Blank 문제 힌트 사전 생성 - answers 배열 길이만큼"""
        import asyncio

        answers = problem_data.get("answers", [])
        code_template = problem_data.get("code_template", "")
        total = len(answers)

        if total == 0:
            print(f"[HintPregen] No answers found for blank problem")
            return

        print(f"[HintPregen] Generating {total} blank hints...")

        # 3개씩 배치 처리
        BATCH_SIZE = 3
        for i in range(0, total, BATCH_SIZE):
            batch_indices = list(range(i, min(i + BATCH_SIZE, total)))
            tasks = []

            for idx in batch_indices:
                # 이미 캐시에 있는지 확인
                cached = self.get_cached_hint(
                    problem_id=problem_id,
                    problem_type="blank",
                    hint_index=idx,
                )

                if cached:
                    print(f"[HintPregen] Blank hint {idx} already cached, skipping")
                    continue

                # 힌트 생성 태스크 추가
                tasks.append(
                    self.generate_blank_hint(
                        problem_id=problem_id,
                        blank_index=idx,
                        code_template=code_template,
                        additional_info={"answers": answers, "code_template": code_template},
                    )
                )

            if tasks:
                await asyncio.gather(*tasks)
                print(f"[HintPregen] Batch {i//BATCH_SIZE + 1} complete ({len(tasks)} hints)")

        print(f"[HintPregen] ✓ Blank hints pregeneration complete ({total} hints)")

    async def _pregenerate_puzzle_hints(
        self,
        problem_id: str,
        problem_data: Dict[str, Any],
    ) -> None:
        """Puzzle 문제 힌트 사전 생성 - blocks 배열 길이만큼"""
        import asyncio

        blocks = problem_data.get("blocks", [])
        total = len(blocks)

        if total == 0:
            print(f"[HintPregen] No blocks found for puzzle problem")
            return

        print(f"[HintPregen] Generating {total} puzzle hints...")

        # 3개씩 배치 처리
        BATCH_SIZE = 3
        for i in range(0, total, BATCH_SIZE):
            batch_indices = list(range(i, min(i + BATCH_SIZE, total)))
            tasks = []

            for idx in batch_indices:
                # 이미 캐시에 있는지 확인
                cached = self.get_cached_hint(
                    problem_id=problem_id,
                    problem_type="puzzle",
                    hint_index=idx,
                )

                if cached:
                    print(f"[HintPregen] Puzzle hint {idx} already cached, skipping")
                    continue

                # 힌트 생성 태스크 추가
                tasks.append(
                    self.generate_puzzle_block_hint(
                        problem_id=problem_id,
                        block_index=idx,
                        blocks=blocks,
                    )
                )

            if tasks:
                await asyncio.gather(*tasks)
                print(f"[HintPregen] Batch {i//BATCH_SIZE + 1} complete ({len(tasks)} hints)")

        print(f"[HintPregen] ✓ Puzzle hints pregeneration complete ({total} hints)")

    async def _pregenerate_guided_hints(
        self,
        problem_id: str,
        problem_data: Dict[str, Any],
    ) -> None:
        """Guided 문제 힌트 사전 생성 - variables_guide.variables 배열 길이만큼"""
        import asyncio

        # variables_guide에서 variables 추출
        variables_guide = problem_data.get("variables_guide", {})
        if isinstance(variables_guide, str):
            import json as json_module
            try:
                variables_guide = json_module.loads(variables_guide)
            except Exception:
                variables_guide = {}

        variables = variables_guide.get("variables", [])
        total = len(variables)

        if total == 0:
            print(f"[HintPregen] No variables found for guided problem")
            return

        print(f"[HintPregen] Generating {total} guided hints...")

        # 3개씩 배치 처리
        BATCH_SIZE = 3
        for i in range(0, total, BATCH_SIZE):
            batch_indices = list(range(i, min(i + BATCH_SIZE, total)))
            tasks = []

            for idx in batch_indices:
                # 이미 캐시에 있는지 확인
                cached = self.get_cached_hint(
                    problem_id=problem_id,
                    problem_type="guided",
                    hint_index=idx,
                )

                if cached:
                    print(f"[HintPregen] Guided hint {idx} already cached, skipping")
                    continue

                # 힌트 생성 태스크 추가
                # guided는 variables를 steps로 변환하여 처리
                variable_info = variables[idx] if idx < len(variables) else {}
                steps = [variable_info]  # 단일 변수를 step으로 취급

                tasks.append(
                    self.generate_guided_step_hint(
                        problem_id=problem_id,
                        step_index=idx,
                        steps=steps,
                        additional_info={"variables_guide": variables_guide},
                    )
                )

            if tasks:
                await asyncio.gather(*tasks)
                print(f"[HintPregen] Batch {i//BATCH_SIZE + 1} complete ({len(tasks)} hints)")

        print(f"[HintPregen] ✓ Guided hints pregeneration complete ({total} hints)")


# Singleton instance
_hint_service = None


def get_hint_service() -> HintService:
    """HintService 싱글톤 반환"""
    global _hint_service
    if _hint_service is None:
        _hint_service = HintService()
    return _hint_service
