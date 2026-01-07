"""
Agent Router
API endpoints for AI agents
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, Union, List, Dict, Any
from uuid import UUID
import json
import re

from ..database import get_db
from ..config import get_settings
from ..dependencies import get_current_user_id_optional
from ..services.openrouter import openrouter_service
from ..services.rag import rag_service
from ..services.embedding import embedding_service
from ..services.problem_save import get_problem_save_service
from ..services.hint_service import get_hint_service
from ..services.feedback_service import get_feedback_service
from ..services.chat_session import get_chat_session_service
from ..services.user_history import get_user_history_service
from ..intents import intent_classifier, IntentType, INTENT_DEFINITIONS

# LLM 모델 설정
settings = get_settings()
from ..prompts import (
    CHAT_AGENT_SYSTEM_PROMPT,
    BLANK_PROBLEM_SYSTEM_PROMPT,
    PUZZLE_PROBLEM_SYSTEM_PROMPT,
    GUIDED_PROBLEM_SYSTEM_PROMPT,
    CODE_GEN_SYSTEM_PROMPT,
    HINT_AGENT_SYSTEM_PROMPT,
    FREE_CHAT_SYSTEM_PROMPT,
    INTENT_ACTION_MAP,
    CONTEXT_REQUIRED_INTENTS,
)
from ..models.agent import (
    # Chat Agent
    ChatAgentRequest,
    ChatAgentResponse,
    ChatAgentMessage,
    CollectedInfo,
    # Intent-Based Chat
    IntentChatRequest,
    IntentChatResponse,
    IntentInfo,
    SessionContext,
    # Problem Generation
    ProblemGenerationRequest,
    BlankProblemResponse,
    PuzzleProblemResponse,
    GuidedProblemResponse,
    ProblemTypeEnum,
    # Code Generation
    CodeGenerationRequest,
    CodeGenerationResponse,
    # Hint Agent
    HintAgentRequest,
    HintAgentResponse,
    # RAG
    RAGSearchRequest,
    RAGSearchResponse,
    # Problem Solving
    SolvingRequest,
    SolvingResponse,
    SolvingIntentInfo,
    # Feedback
    FeedbackRequest,
    FeedbackResponse,
)


# ============================================================
# 퍼즐 블록 후처리 헬퍼 함수
# ============================================================

def _calculate_base_indent(fixed_start: str) -> int:
    """
    fixed_start의 마지막 줄을 분석하여 블록의 기본 들여쓰기 레벨 계산

    예:
    - "class Solution:\\n    def solve(self):" → base_indent = 2
    - "def main():" → base_indent = 1
    """
    if not fixed_start:
        return 0

    lines = fixed_start.split('\n')
    last_line = lines[-1] if lines else ""

    # 마지막 줄의 들여쓰기 계산 (4칸 = 1레벨)
    leading_spaces = len(last_line) - len(last_line.lstrip())
    base_indent = leading_spaces // 4

    # 마지막 줄이 ':'로 끝나면 +1
    if last_line.rstrip().endswith(':'):
        base_indent += 1

    return base_indent


def _analyze_block_indent(code: str, base_indent: int, prev_code: str = "") -> int:
    """
    블록 코드를 분석하여 적절한 indent 레벨 계산

    Python 코드 패턴 기반:
    - return, break, continue, pass → 현재 레벨 유지
    - if, for, while, def, class, try, except, else, elif → 현재 레벨, 다음 블록 +1
    - 일반 코드 → base_indent 사용
    """
    code_stripped = code.strip()

    # 이전 블록이 ':'로 끝나면 +1
    if prev_code and prev_code.strip().endswith(':'):
        return base_indent + 1

    # 코드 시작 패턴 분석
    if code_stripped.startswith(('return ', 'return\n', 'break', 'continue', 'pass')):
        return base_indent
    if code_stripped.startswith(('if ', 'for ', 'while ', 'try:', 'except', 'else:', 'elif ')):
        return base_indent
    if code_stripped.startswith('def ') or code_stripped.startswith('class '):
        return max(base_indent - 1, 0)  # 함수/클래스 정의는 상위 레벨

    return base_indent


def _dedent_code(code: str) -> tuple[str, int]:
    """
    코드의 공통 들여쓰기를 제거하고 (dedent), 제거된 들여쓰기 레벨을 반환

    Returns:
        (dedented_code, indent_level): 들여쓰기가 제거된 코드와 레벨 (4칸 = 1레벨)
    """
    if not code:
        return code, 0

    lines = code.split('\n')

    # 비어있지 않은 줄들의 들여쓰기 수집
    indents = []
    for line in lines:
        if line.strip():  # 빈 줄 제외
            leading_spaces = len(line) - len(line.lstrip(' '))
            indents.append(leading_spaces)

    if not indents:
        return code, 0

    # 최소 공통 들여쓰기
    min_indent = min(indents)

    if min_indent == 0:
        return code, 0

    # 모든 줄에서 최소 들여쓰기 제거
    dedented_lines = []
    for line in lines:
        if line.strip():  # 비어있지 않은 줄
            dedented_lines.append(line[min_indent:])
        else:  # 빈 줄은 그대로
            dedented_lines.append(line)

    return '\n'.join(dedented_lines), min_indent // 4


def _process_block_indents(blocks: list, base_indent: int) -> list:
    """
    모든 블록의 코드를 정규화하고 indentation을 설정

    전략:
    1. 각 블록의 코드에서 공통 들여쓰기 제거 (dedent)
    2. LLM이 설정한 indent 값 또는 추출된 레벨 사용
    3. 코드 패턴 기반으로 indent 보정

    Note: 프론트엔드에서 indentation 값에 따라 들여쓰기를 다시 적용함
    """
    if not blocks:
        return blocks

    result = []
    prev_code = ""
    indent_stack = [base_indent]  # 들여쓰기 스택

    for i, block in enumerate(blocks):
        new_block = dict(block)
        code = block.get("code", "")

        # LLM이 설정한 값 (indent 또는 indentation 둘 다 체크)
        llm_indent = block.get("indentation") or block.get("indent")

        # 1. 코드 dedent (공통 들여쓰기 제거)
        dedented_code, extracted_indent = _dedent_code(code)
        new_block["code"] = dedented_code

        # 2. indent 값 결정
        if llm_indent is not None and llm_indent >= 0:
            # LLM이 설정한 값 사용
            new_block["indentation"] = llm_indent
            indent_stack = [llm_indent]
        elif extracted_indent > 0:
            # 코드에서 추출된 값 사용 (base_indent 고려)
            relative_indent = max(0, extracted_indent)
            new_block["indentation"] = relative_indent
            indent_stack = [relative_indent]
        else:
            # 코드 패턴 기반으로 계산
            code_stripped = dedented_code.strip()

            # 이전 블록이 ':'로 끝나면 들여쓰기 레벨 증가
            if prev_code.strip().endswith(':'):
                new_indent = indent_stack[-1] + 1
                indent_stack.append(new_indent)
            else:
                new_indent = indent_stack[-1]

            # return, break, continue 등 후 레벨 감소
            if code_stripped.startswith(('return ', 'return\n', 'return', 'break', 'continue', 'pass')):
                new_indent = indent_stack[-1]
                if len(indent_stack) > 1:
                    indent_stack.pop()

            new_block["indentation"] = new_indent

        result.append(new_block)
        prev_code = dedented_code

    return result


def assemble_puzzle_solution(
    fixed_start: str,
    blocks: list,
    fixed_end: str,
    indent_size: int = 4
) -> str:
    """
    퍼즐 문제의 블록들을 조합하여 완전한 정답 코드를 생성

    Args:
        fixed_start: 고정된 시작 코드
        blocks: 블록 목록 (id 순서가 정답 순서)
        fixed_end: 고정된 끝 코드
        indent_size: 들여쓰기 단위 (기본 4칸)

    Returns:
        완전한 정답 코드 문자열
    """
    # 블록을 ID 순서로 정렬 (ID가 정답 순서)
    sorted_blocks = sorted(blocks, key=lambda b: int(b.get("id", 0)))

    code_parts = []

    # 1. fixed_start 추가
    if fixed_start:
        code_parts.append(fixed_start.rstrip())

    # 2. 블록들 추가 (indentation 적용)
    for block in sorted_blocks:
        code = block.get("code", "")
        indentation = block.get("indentation") or block.get("indent", 0)

        # 각 줄에 들여쓰기 적용
        indent_str = " " * (indentation * indent_size)
        lines = code.split('\n')
        indented_lines = [indent_str + line if line.strip() else line for line in lines]
        code_parts.append('\n'.join(indented_lines))

    # 3. fixed_end 추가
    if fixed_end:
        code_parts.append(fixed_end.rstrip())

    return '\n'.join(code_parts)


def _merge_puzzle_blocks(blocks: list, max_blocks: int) -> list:
    """
    블록 수가 max_blocks를 초과할 경우 연속된 블록을 병합

    병합 전략:
    1. 같은 indentation을 가진 연속된 블록을 병합
    2. 짧은 블록들 (1줄)을 우선 병합
    """
    if len(blocks) <= max_blocks:
        return blocks

    # 병합해야 할 횟수
    merge_count = len(blocks) - max_blocks

    # 블록을 리스트로 복사
    result = list(blocks)

    for _ in range(merge_count):
        if len(result) <= max_blocks:
            break

        # 병합할 최적의 위치 찾기: 같은 indentation을 가진 연속 블록
        best_merge_idx = -1
        best_score = -1

        for i in range(len(result) - 1):
            curr = result[i]
            next_block = result[i + 1]

            # 같은 indentation이면 병합 가능
            curr_indent = curr.get("indentation") or curr.get("indent", 0)
            next_indent = next_block.get("indentation") or next_block.get("indent", 0)

            if curr_indent == next_indent:
                # 짧은 블록일수록 병합 우선순위 높음
                curr_lines = curr.get("code", "").count('\n') + 1
                next_lines = next_block.get("code", "").count('\n') + 1
                score = 10 - min(curr_lines + next_lines, 10)  # 짧을수록 높은 점수

                if score > best_score:
                    best_score = score
                    best_merge_idx = i

        # 같은 indentation이 없으면 그냥 첫 번째 연속 블록 병합
        if best_merge_idx == -1:
            best_merge_idx = 0

        # 병합 실행 (indentation 키 사용)
        merged_block = {
            "id": result[best_merge_idx]["id"],
            "code": result[best_merge_idx].get("code", "") + "\n" + result[best_merge_idx + 1].get("code", ""),
            "indentation": result[best_merge_idx].get("indentation") or result[best_merge_idx].get("indent", 0),
        }

        # 병합된 블록으로 교체
        result = result[:best_merge_idx] + [merged_block] + result[best_merge_idx + 2:]

    # id 재할당 (1부터 순차적으로)
    for i, block in enumerate(result):
        block["id"] = i + 1

    return result


def _is_incomplete_code(code: str) -> bool:
    """
    코드가 불완전한 구문인지 검사 (한 줄 코드가 잘못 분리된 경우)

    예:
    - "if n % i == 0]" → True (조건문 조각)
    - "return [i for i in range(1, n + 1, 2)" → True (괄호 불균형)
    - "for i in range(n):" → False (완전한 구문)
    """
    code = code.strip()

    # 빈 코드
    if not code:
        return True

    # 괄호 균형 체크
    open_parens = code.count('(') + code.count('[') + code.count('{')
    close_parens = code.count(')') + code.count(']') + code.count('}')

    if open_parens != close_parens:
        return True

    # 닫는 괄호로 시작하면 불완전
    if code[0] in ')]}>':
        return True

    # 키워드로만 시작하고 의미 있는 구문이 아닌 경우
    # 예: "if n % i == 0]" → 조건만 있고 : 없음
    if code.startswith(('if ', 'elif ', 'while ', 'for ')) and not code.rstrip().endswith(':'):
        # list comprehension 내부 조건일 수 있음 (예: "if n % i == 0")
        # 하지만 ]로 끝나면 불완전
        if code.endswith(']') or code.endswith(')'):
            return True

    return False


def _fix_split_blocks(blocks: list) -> list:
    """
    불완전하게 분리된 블록들을 병합

    예:
    [
        {"code": "return [i for i in range(1, n + 1, 2)"},
        {"code": "if n % i == 0]"}
    ]
    →
    [
        {"code": "return [i for i in range(1, n + 1, 2) if n % i == 0]"}
    ]
    """
    if not blocks or len(blocks) < 2:
        return blocks

    result = []
    i = 0

    while i < len(blocks):
        current = dict(blocks[i])
        current_code = current.get("code", "")

        # 현재 블록이 불완전하면 다음 블록과 병합 시도
        while i + 1 < len(blocks) and _is_incomplete_code(current_code):
            next_block = blocks[i + 1]
            next_code = next_block.get("code", "")

            # 공백/줄바꿈 없이 연결 (같은 줄)
            # 여는 괄호로 끝나고 닫는 괄호로 시작하면 공백으로 연결
            if current_code.rstrip().endswith((',', '(', '[', '{')):
                current_code = current_code + " " + next_code
            else:
                current_code = current_code + " " + next_code

            current["code"] = current_code
            i += 1

        # 다음 블록이 불완전하면 (닫는 괄호로 시작) 현재 블록과 병합
        if i + 1 < len(blocks):
            next_block = blocks[i + 1]
            next_code = next_block.get("code", "").strip()

            if next_code and next_code[0] in ')]}>':
                current_code = current_code + " " + next_code
                current["code"] = current_code
                i += 1

        result.append(current)
        i += 1

    # id 재할당
    for idx, block in enumerate(result):
        block["id"] = idx + 1

    return result


def _remove_fixed_end_duplicates(blocks: list, fixed_end: str) -> tuple:
    """
    fixed_end와 중복되는 블록 제거

    Returns:
        (cleaned_blocks, new_fixed_end)

    규칙:
    1. blocks를 합쳤을 때 fixed_end와 완전히 일치하면 → fixed_end 제거
    2. 블록 중 fixed_end와 중복되는 코드가 있으면 → 해당 블록 제거
    3. 블록이 1-2개만 남으면 → fixed_end를 없애고 전체를 블록으로
    """
    if not fixed_end or not blocks:
        return blocks, fixed_end

    fixed_end_normalized = fixed_end.strip().replace('\n', ' ').replace('  ', ' ')

    # 모든 블록 코드를 공백으로 연결해서 비교
    all_blocks_code = " ".join(b.get("code", "").strip() for b in blocks)
    all_blocks_normalized = all_blocks_code.replace('\n', ' ').replace('  ', ' ')

    # 블록을 합친 것이 fixed_end와 같으면 → fixed_end 제거, 블록 유지
    if all_blocks_normalized == fixed_end_normalized:
        print(f"[Puzzle Fix] blocks match fixed_end exactly, removing fixed_end")
        return blocks, None

    # 블록 중에서 fixed_end와 중복되는 것 제거
    cleaned_blocks = []
    for block in blocks:
        block_code = block.get("code", "").strip()
        block_normalized = block_code.replace('\n', ' ').replace('  ', ' ')

        # fixed_end에 블록 코드가 포함되어 있는지 확인
        if block_normalized in fixed_end_normalized:
            print(f"[Puzzle Fix] Removing duplicate block: {block_code[:50]}...")
            continue

        # fixed_end가 블록 코드에 포함되어 있는지도 확인
        if fixed_end_normalized in block_normalized:
            print(f"[Puzzle Fix] Block contains fixed_end, removing overlap")
            # 블록에서 fixed_end 부분 제거
            new_code = block_code.replace(fixed_end.strip(), "").strip()
            if new_code:
                block["code"] = new_code
                cleaned_blocks.append(block)
            continue

        cleaned_blocks.append(block)

    # id 재할당
    for idx, block in enumerate(cleaned_blocks):
        block["id"] = idx + 1

    # 블록이 너무 적으면 (1-2개) fixed_end도 블록으로 전환
    if len(cleaned_blocks) <= 2 and fixed_end:
        print(f"[Puzzle Fix] Only {len(cleaned_blocks)} blocks, converting fixed_end to block")
        # fixed_end를 블록으로 추가 (indentation 키 사용)
        existing_indent = 0
        if cleaned_blocks:
            existing_indent = cleaned_blocks[0].get("indentation") or cleaned_blocks[0].get("indent", 0)
        new_block = {
            "id": len(cleaned_blocks) + 1,
            "code": fixed_end.strip(),
            "indentation": existing_indent,
        }
        cleaned_blocks.append(new_block)
        return cleaned_blocks, None

    return cleaned_blocks, fixed_end


router = APIRouter()


# ============================================================
# Chat Agent - LangGraph 기반 대화 에이전트
# ============================================================

# LangGraph 가져오기
from ..graphs import (
    # Legacy
    ChatGraph,
    ProblemSolvingGraph,
    # Discovery
    DiscoveryGraph,
    # Orchestrator V2 (Tool 기반)
    ChatOrchestratorV2,
    get_orchestrator_v2,
)

# 전역 그래프 인스턴스 (싱글톤)
_solving_graph = None
_orchestrator = None


def get_solving_graph() -> ProblemSolvingGraph:
    """ProblemSolvingGraph 싱글톤 반환"""
    global _solving_graph
    if _solving_graph is None:
        _solving_graph = ProblemSolvingGraph()
    return _solving_graph


def get_chat_orchestrator() -> ChatOrchestratorV2:
    """ChatOrchestratorV2 싱글톤 반환"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = get_orchestrator_v2()
    return _orchestrator


# ============================================================
# Chat Agent - LangGraph 기반 메인 채팅 엔드포인트
# ============================================================

# 메인 오케스트레이터 (노드가 분리된 구조)
_chat_orchestrator_main = None


def get_chat_orchestrator_main():
    """메인 ChatOrchestrator 싱글톤 반환"""
    global _chat_orchestrator_main
    if _chat_orchestrator_main is None:
        from ..graphs.orchestrator_v2 import ChatOrchestratorV2
        _chat_orchestrator_main = ChatOrchestratorV2()
    return _chat_orchestrator_main


class ChatRequest(BaseModel):
    """LangGraph Chat 요청"""
    message: str
    conversation_history: List[ChatAgentMessage] = []  # 프론트엔드 fallback용 (DB 없을 때)
    user_context: Optional[Dict[str, Any]] = None
    session_state: Optional[Dict[str, Any]] = None  # 세션 상태
    session_id: Optional[str] = None  # 세션 ID (DB 세션용)


class ChatResponse(BaseModel):
    """LangGraph Chat 응답"""
    stage: str  # intent, collection, discovery, solving, problem_generation
    message: str
    intent: Optional[str] = None
    collected_info: Optional[CollectedInfo] = None
    search_results: Optional[List[Dict[str, Any]]] = None
    selected_problem: Optional[Dict[str, Any]] = None
    generated_problem: Optional[Dict[str, Any]] = None
    # 문제 유형별 생성 결과 (blank/puzzle/guided)
    generated_problem_data: Optional[Dict[str, Any]] = None
    action_trigger: Optional[str] = None
    action_data: Optional[Dict[str, Any]] = None
    next_stage: Optional[str] = None
    is_complete: bool = False
    # 정보 수집 단계: 네/아니오 응답 대기
    awaiting_confirmation: bool = False
    suggested_value: Optional[str] = None
    # Solving 결과
    hint_level: Optional[int] = None
    is_correct: Optional[bool] = None
    # 세션 추적
    session_id: Optional[str] = None  # 상태 영속화용 세션 ID


@router.post("/chat", response_model=ChatResponse)
async def chat_agent(
    request: ChatRequest,
    db=Depends(get_db),
    current_user_id: Optional[UUID] = Depends(get_current_user_id_optional),
):
    """
    LangGraph 기반 대화 챗봇 (정식 버전)

    3단계 그래프 구조:
    1. IntentGraph: 사용자 의도 분류
    2. DiscoveryGraph: 문제 탐색 (RAG 검색 / CodeGen fallback)
    3. SolvingGraph: 문제 풀이 도움 (힌트, 코드 리뷰 등)

    Flow:
        Message → IntentGraph (의도 분류)
                    ↓
               [needs_info_collection?]
                    ├─ Yes → InfoCollectionGraph
                    │              ↓
                    │        parse_input → ask_topic/difficulty/language
                    │              ↓
                    │        [is_complete?] → DiscoveryGraph
                    └─ No → DiscoveryGraph / SolvingGraph / 직접 응답

    Discovery Flow:
        route_discovery_intent → search_problems
            ├─ [유사도↑] filter_results ─┐
            └─ [fallback] generate_problem─┴→ handle_selection → confirm_problem → respond

    세션 관리:
        - DB에 대화 히스토리 저장 (chat_sessions, chat_messages 테이블)
        - 세션 상태 (stage, collected_info 등) DB 저장
        - 프론트엔드에서 session_id 전달하면 해당 세션 재사용
    """
    try:
        orchestrator = get_chat_orchestrator_main()
        chat_session_service = get_chat_session_service(db)

        # user_context에 user_id 추가 (DB 저장에 필요)
        user_context = request.user_context or {}
        user_id = str(current_user_id) if current_user_id else None
        if user_id:
            user_context["user_id"] = user_id

        # ============================================================
        # 사용자 히스토리 조회 (개인화 추천용)
        # ============================================================
        if user_id:
            try:
                user_history_service = get_user_history_service(db)
                personalization = await user_history_service.get_personalization_context(user_id)

                if personalization.get('has_history'):
                    user_context["personalization"] = personalization
                    print(f"[Chat] Loaded personalization: {len(personalization.get('recent_problems', []))} recent problems")

                    # 스킬 요약이 있으면 추가
                    if personalization.get('skill_summary'):
                        skill = personalization['skill_summary']
                        print(f"[Chat] User skill: weak={skill.get('weak_topics')}, strong={skill.get('strong_topics')}")

            except Exception as history_err:
                print(f"[Chat] Failed to load user history (non-blocking): {history_err}")

        # ============================================================
        # 세션 관리: DB에서 세션 가져오기 또는 생성
        # ============================================================
        session_id = None
        conversation_history = []
        session_state = request.session_state

        if user_id:
            try:
                # 세션 가져오기 또는 생성
                session_id = await chat_session_service.get_or_create_session(
                    user_id=user_id,
                    session_id=request.session_id
                )
                print(f"[Chat] Using session: {session_id[:8]}... for user: {user_id[:8]}...")

                # DB에서 대화 히스토리 로드
                conversation_history = await chat_session_service.convert_to_langchain_messages(
                    session_id=session_id,
                    limit=20  # 최근 20개 메시지만
                )
                print(f"[Chat] Loaded {len(conversation_history)} messages from DB")

                # DB에서 세션 상태 로드 (프론트엔드에서 전달한 것보다 DB 우선)
                if not session_state:
                    db_session_state = await chat_session_service.get_session_state(session_id)
                    if db_session_state:
                        session_state = {
                            "stage": db_session_state.get("current_stage", "intent"),
                            "collected_info": db_session_state.get("collected_info", {}),
                            "session_state": db_session_state.get("session_state", {}),
                        }
                        print(f"[Chat] Loaded session state from DB: stage={session_state.get('stage')}")

                # 사용자 메시지 DB에 저장
                await chat_session_service.add_message(
                    session_id=session_id,
                    role="user",
                    content=request.message,
                    message_type="text"
                )

            except Exception as session_err:
                print(f"[Chat] Session error (using fallback): {session_err}")
                # 세션 에러 시 프론트엔드에서 보낸 히스토리 사용
                conversation_history = [
                    {"role": msg.role, "content": msg.content}
                    for msg in request.conversation_history
                ]
                import uuid as uuid_module
                session_id = request.session_id or str(uuid_module.uuid4())
        else:
            # 비로그인 사용자: 프론트엔드에서 보낸 히스토리 사용
            conversation_history = [
                {"role": msg.role, "content": msg.content}
                for msg in request.conversation_history
            ]
            import uuid as uuid_module
            session_id = request.session_id or str(uuid_module.uuid4())

        # ============================================================
        # 오케스트레이터 실행
        # ============================================================
        result = await orchestrator.process(
            message=request.message,
            conversation_history=conversation_history,
            user_context=user_context,
            session_state=session_state,
            session_id=session_id,
        )

        # 결과 추출
        response_message = result.get("response_message", "") or result.get("message", "무엇을 도와드릴까요?")

        # collected_info 구성
        collected_info_data = result.get("collected_info", {})
        collected_info = None
        if collected_info_data:
            collected_info = CollectedInfo(
                topics=collected_info_data.get("topics") or [],
                difficulty=collected_info_data.get("difficulty"),
                language=collected_info_data.get("language"),
                specific_needs=collected_info_data.get("specific_needs"),
                time_available=collected_info_data.get("time_available"),
                selected_problem=collected_info_data.get("selected_problem"),
                selected_problem_index=collected_info_data.get("selected_problem_index"),
            )

        # ============================================================
        # 응답을 DB에 저장
        # ============================================================
        if user_id and session_id:
            try:
                # 어시스턴트 메시지 저장
                message_metadata = {}
                if result.get("action_trigger"):
                    message_metadata["action_trigger"] = result.get("action_trigger")
                if result.get("search_results"):
                    message_metadata["has_search_results"] = True
                if result.get("generated_problem"):
                    message_metadata["has_generated_problem"] = True

                await chat_session_service.add_message(
                    session_id=session_id,
                    role="assistant",
                    content=response_message,
                    message_type=result.get("action_trigger") or "text",
                    metadata=message_metadata if message_metadata else None
                )

                # 세션 상태 업데이트
                await chat_session_service.update_session_state(
                    session_id=session_id,
                    stage=result.get("stage"),
                    collected_info=collected_info_data,
                    session_state={
                        "awaiting_confirmation": result.get("awaiting_confirmation", False),
                        "suggested_value": result.get("suggested_value"),
                    },
                    current_problem_data=result.get("generated_problem") or result.get("selected_problem"),
                )
                print(f"[Chat] Saved response and state to DB")

            except Exception as save_err:
                print(f"[Chat] Failed to save to DB (non-blocking): {save_err}")

        return ChatResponse(
            stage=result.get("stage", "intent"),
            message=response_message,
            intent=result.get("intent"),
            collected_info=collected_info,
            search_results=result.get("search_results"),
            selected_problem=result.get("selected_problem"),
            generated_problem=result.get("generated_problem"),
            generated_problem_data=result.get("generated_problem_data"),
            action_trigger=result.get("action_trigger"),
            action_data=result.get("action_data"),
            next_stage=result.get("next_stage"),
            is_complete=result.get("is_complete", False),
            # 정보 수집 단계: 네/아니오 응답 대기
            awaiting_confirmation=result.get("awaiting_confirmation", False),
            suggested_value=result.get("suggested_value"),
            hint_level=result.get("hint_level"),
            is_correct=result.get("is_correct"),
            # 세션 추적 (클라이언트가 다음 요청에 사용)
            session_id=session_id,
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat agent error: {str(e)}"
        )


# ============================================================
# Resume Endpoint - Human-in-the-Loop 재개
# ============================================================

class ResumeRequest(BaseModel):
    """그래프 재개 요청 (interrupt 후)"""
    session_id: str  # 세션 ID (필수)
    user_response: Dict[str, Any]  # 사용자 응답 (action, data 등)


class ResumeResponse(BaseModel):
    """그래프 재개 응답"""
    stage: str
    message: str
    action_trigger: Optional[str] = None
    action_data: Optional[Dict[str, Any]] = None
    is_complete: bool = False
    session_id: str


@router.post("/resume", response_model=ResumeResponse)
async def resume_graph(
    request: ResumeRequest,
    db=Depends(get_db),
    current_user_id: Optional[UUID] = Depends(get_current_user_id_optional),
):
    """
    Interrupt된 그래프 재개 (Human-in-the-Loop)

    문제 생성 확인, 힌트 공개 확인 등 사용자 확인이 필요한 상황에서
    사용자 응답을 받아 그래프를 재개합니다.

    Usage:
        1. /chat에서 interrupt 발생 시 프론트엔드가 확인 UI 표시
        2. 사용자가 선택 후 이 엔드포인트로 응답 전송
        3. 그래프가 재개되어 결과 반환

    Request:
        - session_id: /chat 응답에서 받은 session_id
        - user_response: 사용자 선택 ({"action": "confirm|modify|cancel", ...})
    """
    try:
        from ..graphs.orchestrator_v2 import get_orchestrator_v2
        from ..graphs.checkpointer import create_thread_config

        orchestrator = get_orchestrator_v2()

        # Checkpointer가 초기화되어 있는지 확인
        if not orchestrator._initialized:
            await orchestrator.initialize()

        if not orchestrator.checkpointer:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Checkpointer not available. Cannot resume interrupted graph."
            )

        # 그래프 config 생성
        config = create_thread_config(
            session_id=request.session_id,
            user_id=str(current_user_id) if current_user_id else None,
        )

        # 현재 그래프 상태 확인 및 재개
        # Note: LangGraph의 resume 패턴 - 사용자 응답을 Command로 전달
        from langgraph.types import Command

        # 사용자 응답으로 그래프 재개
        # discovery_graph가 interrupt 상태라면 user_response를 resume 값으로 전달
        result = await orchestrator.discovery_graph.graph.ainvoke(
            Command(resume=request.user_response),
            config=config,
        )

        response_message = result.get("response_message", "")

        return ResumeResponse(
            stage=result.get("stage", "discovery"),
            message=response_message,
            action_trigger=result.get("action_trigger"),
            action_data=result.get("action_data"),
            is_complete=result.get("is_complete", False),
            session_id=request.session_id,
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Resume error: {str(e)}"
        )


# ============================================================
# Problem Solving Agent - LangGraph 기반 문제 풀이 에이전트
# ============================================================

@router.post("/solving", response_model=SolvingResponse)
async def solving_agent(request: SolvingRequest, db=Depends(get_db)):
    """
    LangGraph 기반 문제 풀이 도우미

    문제가 화면에 표시된 후, 사용자가 풀이 중일 때 사용

    Flow (LangGraph):
    START → classify_solving_intent
           ├─ hint_request → provide_hint (점진적 힌트)
           ├─ code_review → review_code (코드 리뷰)
           ├─ answer_check → check_answer (정답 체크)
           ├─ feedback_request → provide_feedback (종합 피드백)
           ├─ give_up → show_solution (정답 공개)
           └─ question → answer_question (일반 질문)
          → respond → END
    """
    try:
        graph = get_solving_graph()

        # 대화 히스토리를 딕셔너리 형태로 변환
        conversation_history = [
            {"role": msg.role, "content": msg.content}
            for msg in request.conversation_history
        ]

        # problem_context를 딕셔너리로 변환
        problem_context = request.problem_context.dict()

        # user_progress를 딕셔너리로 변환
        user_progress = request.user_progress.dict() if request.user_progress else {}

        # 그래프 실행
        result = await graph.invoke(
            message=request.message,
            problem_context=problem_context,
            user_progress=user_progress,
            conversation_history=conversation_history,
            previous_hints=request.previous_hints,
        )

        # 결과 추출
        response_message = result.get("response_message", "무엇을 도와드릴까요?")
        intent_result = result.get("intent_result", {})

        # SolvingIntentInfo 구성
        intent_info = SolvingIntentInfo(
            intent=intent_result.get("intent", "question"),
            confidence=intent_result.get("confidence", 0.0),
            sub_intent=intent_result.get("sub_intent"),
        )

        return SolvingResponse(
            message=response_message,
            intent_info=intent_info,
            hint_level=result.get("hint_level"),
            is_correct=result.get("is_correct"),
            action_trigger=result.get("action_trigger"),
            action_data=result.get("action_data"),
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Solving agent error: {str(e)}"
        )


# V1/V2 legacy code removed - see git history for:
# - /chat (V1)
# - /chat/legacy
# - /chat/v2
# - /chat/v2/eval
# - /chat/compare
# - /chat/stream
# - /chat/intent
# - _handle_intent, _make_simple_response, etc.


# ============================================================
# V1/V2 Legacy Code Removed
# ============================================================
# The following endpoints and functions have been removed (V3 only):
# - /chat (V1 endpoint)
# - /chat/legacy
# - /chat/v2, /chat/v2/eval
# - /chat/compare, /chat/compare/full
# - /chat/stream
# - /chat/intent
# - _chat_agent_legacy, _auto_search_problems
# - _handle_intent, _handle_new_problem, _handle_similar_code_problem, etc.
# - _make_simple_response, _handle_general_chat
# See git history for deleted code.


# ============================================================
# Problem Generation
# ============================================================

@router.post("/generate/blank", response_model=BlankProblemResponse)
async def generate_blank_problem(
    request: ProblemGenerationRequest,
    db=Depends(get_db),
    current_user_id: Optional[UUID] = Depends(get_current_user_id_optional),
):
    """
    Generate a blank-fill problem from base problem.

    Uses GPT-4o-mini via OpenRouter.
    Cache-First: DB에 있으면 복사, 없으면 LLM 생성 후 저장
    """
    try:
        bp = request.base_problem
        language = request.language.value
        # original_id 우선 사용 (프론트엔드에서 전달), 없으면 id, name 순으로 fallback
        original_id = bp.original_id or bp.id or bp.name

        # 로그인된 유저 ID 사용 (JWT 토큰에서 추출)
        creator_id = str(current_user_id) if current_user_id else None

        print(f"[Blank Gen] original_id: {original_id}, creator_id: {creator_id}")

        # ============================================================
        # Cache-First 로직
        # ============================================================
        problem_save_service = get_problem_save_service()

        # base_problem_id 조회 (UUID)
        base_problem_id = problem_save_service.get_base_problem_id(original_id)
        print(f"[Blank Gen] base_problem_id from DB: {base_problem_id}")

        if base_problem_id:
            # 1. 유저가 이미 가지고 있는지 확인
            if creator_id:
                user_existing = problem_save_service.check_user_has_problem(
                    problem_type="blank",
                    base_problem_id=base_problem_id,
                    language=language,
                    creator_id=creator_id,
                )
                if user_existing:
                    print(f"[Blank Gen] User already has problem: {original_id}")
                    return BlankProblemResponse(
                        original_id=user_existing.get("original_id", original_id),
                        language=user_existing.get("language", language),
                        code_template=user_existing.get("code_template", ""),
                        answers=user_existing.get("answers", []),
                    )

            # 2. 다른 유저가 만든 게 있는지 확인 → 복사
            existing = problem_save_service.find_existing_problem(
                problem_type="blank",
                base_problem_id=base_problem_id,
                language=language,
            )
            if existing:
                print(f"[Blank Gen] Cache hit! Copying for user: {original_id}")
                if creator_id:
                    await problem_save_service.copy_problem_for_user(
                        problem_type="blank",
                        source_problem=existing,
                        creator_id=creator_id,
                    )
                return BlankProblemResponse(
                    original_id=existing.get("original_id", original_id),
                    language=existing.get("language", language),
                    code_template=existing.get("code_template", ""),
                    answers=existing.get("answers", []),
                )

        # ============================================================
        # Cache Miss: LLM으로 생성
        # ============================================================
        print(f"[Blank Gen] Cache miss. Generating: {original_id}")

        title = bp.get_title()
        description = bp.get_description()
        code = bp.get_code(language)

        if not code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이 문제에는 솔루션 코드가 없습니다."
            )

        base_problem_json = json.dumps({
            "title": title,
            "description": description,
            "code": code,
            "difficulty": bp.difficulty.value,
            "topics": bp.topics or bp.tags or [],
        }, ensure_ascii=False)

        system_prompt = BLANK_PROBLEM_SYSTEM_PROMPT \
            .replace("{base_problem}", base_problem_json) \
            .replace("{user_level}", request.user_level.value) \
            .replace("{language}", language)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "위 문제를 빈칸 채우기 문제로 변환해주세요."},
        ]

        # ============================================================
        # LLM 호출 + 재시도 로직 (최대 3회 시도)
        # ============================================================
        MAX_RETRIES = 3
        result = None

        for attempt in range(MAX_RETRIES):
            response = await openrouter_service.chat_completion(
                model=settings.llm_model_blank_gen,
                messages=messages,
                temperature=0.7 + (attempt * 0.1),  # 재시도시 온도 약간 증가
                response_format={"type": "json_object"},
            )

            content = openrouter_service.get_content(response)
            print(f"[Blank Gen] Attempt {attempt + 1}: LLM response: {content[:300]}...")

            result = openrouter_service.parse_json_response(content)
            print(f"[Blank Gen] Parsed result keys: {result.keys()}")

            if not result.get("original_id"):
                result["original_id"] = original_id
            if not result.get("language"):
                result["language"] = language

            # 빈칸 패턴 검증
            code_template = result.get("code_template", "")
            answers = result.get("answers", [])
            blank_patterns = re.findall(r'_(\d+)_', code_template)

            print(f"[Blank Gen] Validation: {len(blank_patterns)} patterns found, {len(answers)} answers")

            # 유효한 출력인지 확인
            if len(answers) > 0 and len(blank_patterns) > 0:
                print(f"[Blank Gen] ✓ Valid output on attempt {attempt + 1}")
                break
            elif len(answers) > 0 and len(blank_patterns) == 0:
                print(f"[Blank Gen] ⚠️ Attempt {attempt + 1}: answers exist but no _N_ patterns!")
                print(f"[Blank Gen] code_template preview: {code_template[:200]}...")

                if attempt < MAX_RETRIES - 1:
                    print(f"[Blank Gen] Retrying... ({attempt + 2}/{MAX_RETRIES})")
                    # 재시도 메시지 추가
                    messages.append({"role": "assistant", "content": content})
                    messages.append({
                        "role": "user",
                        "content": "code_template에 빈칸이 없습니다. 코드의 핵심 부분을 _0_, _1_, _2_ 형식의 빈칸으로 변환해주세요. 예: 'result = _0_' 형태로요."
                    })
                else:
                    print(f"[Blank Gen] ❌ All {MAX_RETRIES} attempts failed - returning as-is")
            else:
                # answers가 없는 경우
                print(f"[Blank Gen] ⚠️ No answers in response")
                break

        # ============================================================
        # DB에 저장
        # ============================================================
        # Note: base_problems에 저장하는 로직 제거
        # - base_problems는 원본 문제 저장소 (Baekjoon, TACO 등)
        # - 유형별 테이블만 저장 (problems_blank, problems_puzzle, problems_guided)
        # - CodeGen 문제는 LangGraph의 code_gen 노드에서만 base_problems에 저장

        if base_problem_id and creator_id:
            try:
                save_result = await problem_save_service.save_generated_problem(
                    problem_type="blank",
                    generated_data=result,
                    base_problem_id=base_problem_id,
                    creator_id=creator_id,
                )
                if save_result.get("success"):
                    print(f"[Blank Gen] Saved to DB: {original_id} (user: {creator_id[:8]}...)")
                else:
                    print(f"[Blank Gen] DB save failed: {save_result.get('error')}")
            except Exception as save_err:
                print(f"[Blank Gen] DB save error (non-blocking): {save_err}")

        return BlankProblemResponse(**result)

    except Exception as e:
        import traceback
        print(f"[Blank Gen] Error: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Blank problem generation error: {str(e)}"
        )


@router.post("/generate/puzzle", response_model=PuzzleProblemResponse)
async def generate_puzzle_problem(
    request: ProblemGenerationRequest,
    db=Depends(get_db),
    current_user_id: Optional[UUID] = Depends(get_current_user_id_optional),
):
    """
    Generate a puzzle (Parsons) problem from base problem.

    Uses GPT-4o-mini via OpenRouter.
    Cache-First: DB에 있으면 복사, 없으면 LLM 생성 후 저장
    """
    try:
        bp = request.base_problem
        language = request.language.value
        # original_id 우선 사용 (프론트엔드에서 전달), 없으면 id, name 순으로 fallback
        original_id = bp.original_id or bp.id or bp.name

        # 로그인된 유저 ID 사용 (JWT 토큰에서 추출)
        creator_id = str(current_user_id) if current_user_id else None

        print(f"[Puzzle Gen] original_id: {original_id}, creator_id: {creator_id}")

        # ============================================================
        # Cache-First 로직
        # ============================================================
        problem_save_service = get_problem_save_service()
        base_problem_id = problem_save_service.get_base_problem_id(original_id)
        print(f"[Puzzle Gen] base_problem_id from DB: {base_problem_id}")

        if base_problem_id:
            if creator_id:
                user_existing = problem_save_service.check_user_has_problem(
                    problem_type="puzzle",
                    base_problem_id=base_problem_id,
                    language=language,
                    creator_id=creator_id,
                )
                if user_existing:
                    print(f"[Puzzle Gen] User already has problem: {original_id}")
                    return PuzzleProblemResponse(
                        original_id=user_existing.get("original_id", original_id),
                        language=user_existing.get("language", language),
                        fixed_start=user_existing.get("fixed_start"),
                        fixed_end=user_existing.get("fixed_end"),
                        blocks=user_existing.get("blocks", []),
                    )

            existing = problem_save_service.find_existing_problem(
                problem_type="puzzle",
                base_problem_id=base_problem_id,
                language=language,
            )
            if existing:
                print(f"[Puzzle Gen] Cache hit! Copying for user: {original_id}")
                if creator_id:
                    await problem_save_service.copy_problem_for_user(
                        problem_type="puzzle",
                        source_problem=existing,
                        creator_id=creator_id,
                    )
                return PuzzleProblemResponse(
                    original_id=existing.get("original_id", original_id),
                    language=existing.get("language", language),
                    fixed_start=existing.get("fixed_start"),
                    fixed_end=existing.get("fixed_end"),
                    blocks=existing.get("blocks", []),
                )

        # ============================================================
        # Cache Miss: LLM으로 생성
        # ============================================================
        print(f"[Puzzle Gen] Cache miss. Generating: {original_id}")

        title = bp.get_title()
        description = bp.get_description()
        code = bp.get_code(language)

        if not code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이 문제에는 솔루션 코드가 없습니다."
            )

        base_problem_json = json.dumps({
            "title": title,
            "description": description,
            "code": code,
            "difficulty": bp.difficulty.value,
            "topics": bp.topics or bp.tags or [],
        }, ensure_ascii=False)

        system_prompt = PUZZLE_PROBLEM_SYSTEM_PROMPT \
            .replace("{base_problem}", base_problem_json) \
            .replace("{user_level}", request.user_level.value) \
            .replace("{language}", language)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "위 문제를 퍼즐(Parsons) 문제로 변환해주세요."},
        ]

        # ============================================================
        # LLM 호출 + 재시도 로직 (최대 3회 시도)
        # ============================================================
        MAX_RETRIES = 3
        result = None
        last_error = None

        for attempt in range(MAX_RETRIES):
            try:
                response = await openrouter_service.chat_completion(
                    model=settings.llm_model_puzzle_gen,
                    messages=messages,
                    temperature=0.7 + (attempt * 0.1),
                    response_format={"type": "json_object"},
                )

                content = openrouter_service.get_content(response)
                print(f"[Puzzle Gen] Attempt {attempt + 1}: LLM response length: {len(content)}")

                result = openrouter_service.parse_json_response(content)
                print(f"[Puzzle Gen] Parsed result keys: {result.keys()}")

                # 블록이 있는지 확인
                blocks = result.get("blocks", [])
                if len(blocks) > 0:
                    print(f"[Puzzle Gen] ✓ Valid output on attempt {attempt + 1}: {len(blocks)} blocks")
                    break
                else:
                    print(f"[Puzzle Gen] ⚠️ Attempt {attempt + 1}: No blocks in response")
                    if attempt < MAX_RETRIES - 1:
                        messages.append({"role": "assistant", "content": content})
                        messages.append({
                            "role": "user",
                            "content": "blocks 배열이 비어있습니다. 코드를 블록 단위로 분리해서 blocks 배열에 넣어주세요."
                        })

            except ValueError as e:
                last_error = e
                print(f"[Puzzle Gen] ⚠️ Attempt {attempt + 1} parse error: {e}")
                if attempt < MAX_RETRIES - 1:
                    print(f"[Puzzle Gen] Retrying... ({attempt + 2}/{MAX_RETRIES})")
                else:
                    print(f"[Puzzle Gen] ❌ All {MAX_RETRIES} attempts failed")
                    raise

        if result is None:
            raise ValueError("Failed to generate puzzle after all retries")

        if not result.get("original_id"):
            result["original_id"] = original_id
        if not result.get("language"):
            result["language"] = language

        # ============================================================
        # 후처리: 블록 검증, 중복 제거, indent 보정, 블록 수 제한
        # ============================================================
        blocks = result.get("blocks", [])
        fixed_start = result.get("fixed_start", "")
        fixed_end = result.get("fixed_end", "")
        print(f"[Puzzle Gen] Original block count: {len(blocks)}")

        # 1. 불완전하게 분리된 블록 병합 (한 줄 코드가 여러 블록으로 쪼개진 경우)
        blocks = _fix_split_blocks(blocks)
        if len(blocks) != len(result.get("blocks", [])):
            print(f"[Puzzle Gen] Fixed split blocks: {len(result.get('blocks', []))} -> {len(blocks)}")
        result["blocks"] = blocks

        # 2. fixed_end와 중복되는 블록 제거
        blocks, fixed_end = _remove_fixed_end_duplicates(blocks, fixed_end)
        result["blocks"] = blocks
        result["fixed_end"] = fixed_end
        print(f"[Puzzle Gen] After duplicate removal: {len(blocks)} blocks, fixed_end: {bool(fixed_end)}")

        # 3. indent 보정 (코드 패턴 기반)
        base_indent = _calculate_base_indent(fixed_start)
        print(f"[Puzzle Gen] Base indent from fixed_start: {base_indent}")

        # 코드 패턴 분석하여 indent 설정
        blocks = _process_block_indents(blocks, base_indent)
        result["blocks"] = blocks

        # 디버그: indentation 값 출력
        indent_info = [(b.get("id"), b.get("indentation", 0), b.get("code", "")[:30]) for b in blocks[:5]]
        print(f"[Puzzle Gen] Block indentations (first 5): {indent_info}")

        # 4. 블록 수가 15개 초과시 자동 병합
        MAX_BLOCKS = 15
        if len(blocks) > MAX_BLOCKS:
            print(f"[Puzzle Gen] Merging blocks: {len(blocks)} -> {MAX_BLOCKS}")
            blocks = _merge_puzzle_blocks(blocks, MAX_BLOCKS)
            result["blocks"] = blocks
            print(f"[Puzzle Gen] After merge: {len(blocks)} blocks")

        # ============================================================
        # DB에 저장
        # ============================================================
        # Note: base_problems에 저장하는 로직 제거
        # - base_problems는 원본 문제 저장소 (Baekjoon, TACO 등)
        # - 유형별 테이블만 저장 (problems_blank, problems_puzzle, problems_guided)
        # - CodeGen 문제는 LangGraph의 code_gen 노드에서만 base_problems에 저장

        if base_problem_id and creator_id:
            try:
                save_result = await problem_save_service.save_generated_problem(
                    problem_type="puzzle",
                    generated_data=result,
                    base_problem_id=base_problem_id,
                    creator_id=creator_id,
                )
                if save_result.get("success"):
                    print(f"[Puzzle Gen] Saved to DB: {original_id} (user: {creator_id[:8]}...)")
                else:
                    print(f"[Puzzle Gen] DB save failed: {save_result.get('error')}")
            except Exception as save_err:
                print(f"[Puzzle Gen] DB save error (non-blocking): {save_err}")

        # 5. 정답 코드 조합 (indentation 적용)
        solution_code = assemble_puzzle_solution(
            fixed_start=result.get("fixed_start", ""),
            blocks=result.get("blocks", []),
            fixed_end=result.get("fixed_end", ""),
        )
        result["solution_code"] = solution_code
        print(f"[Puzzle Gen] Generated solution_code ({len(solution_code)} chars)")

        return PuzzleProblemResponse(**result)

    except Exception as e:
        import traceback
        print(f"[Puzzle Gen] Error: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Puzzle problem generation error: {str(e)}"
        )


@router.post("/generate/guided", response_model=GuidedProblemResponse)
async def generate_guided_problem(
    request: ProblemGenerationRequest,
    db=Depends(get_db),
    current_user_id: Optional[UUID] = Depends(get_current_user_id_optional),
):
    """
    Generate a guided (1:1 conversational) problem from base problem.

    Uses GPT-4o-mini via OpenRouter.
    Cache-First: DB에 있으면 복사, 없으면 LLM 생성 후 저장
    """
    try:
        bp = request.base_problem
        language = request.language.value
        # original_id 우선 사용 (프론트엔드에서 전달), 없으면 id, name 순으로 fallback
        original_id = bp.original_id or bp.id or bp.name

        # 로그인된 유저 ID 사용 (JWT 토큰에서 추출)
        creator_id = str(current_user_id) if current_user_id else None

        print(f"[Guided Gen] original_id: {original_id}, creator_id: {creator_id}")

        # ============================================================
        # Cache-First 로직
        # ============================================================
        problem_save_service = get_problem_save_service()
        base_problem_id = problem_save_service.get_base_problem_id(original_id)
        print(f"[Guided Gen] base_problem_id from DB: {base_problem_id}")

        if base_problem_id:
            if creator_id:
                user_existing = problem_save_service.check_user_has_problem(
                    problem_type="guided",
                    base_problem_id=base_problem_id,
                    language=language,
                    creator_id=creator_id,
                )
                if user_existing:
                    print(f"[Guided Gen] User already has problem: {original_id}")
                    return GuidedProblemResponse(
                        original_id=user_existing.get("original_id", original_id),
                        language=user_existing.get("language", language),
                        concepts=user_existing.get("concepts", []),
                        flow=user_existing.get("flow", []),
                        checkpoints=user_existing.get("checkpoints", []),
                    )

            existing = problem_save_service.find_existing_problem(
                problem_type="guided",
                base_problem_id=base_problem_id,
                language=language,
            )
            if existing:
                print(f"[Guided Gen] Cache hit! Copying for user: {original_id}")
                if creator_id:
                    await problem_save_service.copy_problem_for_user(
                        problem_type="guided",
                        source_problem=existing,
                        creator_id=creator_id,
                    )
                return GuidedProblemResponse(
                    original_id=existing.get("original_id", original_id),
                    language=existing.get("language", language),
                    concepts=existing.get("concepts", []),
                    flow=existing.get("flow", []),
                    checkpoints=existing.get("checkpoints", []),
                )

        # ============================================================
        # Cache Miss: LLM으로 생성
        # ============================================================
        print(f"[Guided Gen] Cache miss. Generating: {original_id}")

        title = bp.get_title()
        description = bp.get_description()
        code = bp.get_code(language)

        if not code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이 문제에는 솔루션 코드가 없습니다."
            )

        base_problem_json = json.dumps({
            "title": title,
            "description": description,
            "code": code,
            "difficulty": bp.difficulty.value,
            "topics": bp.topics or bp.tags or [],
        }, ensure_ascii=False)

        system_prompt = GUIDED_PROBLEM_SYSTEM_PROMPT \
            .replace("{base_problem}", base_problem_json) \
            .replace("{user_level}", request.user_level.value) \
            .replace("{language}", language)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "위 문제를 1대1 대화형 문제로 변환해주세요."},
        ]

        # ============================================================
        # LLM 호출 + 재시도 로직 (최대 3회 시도)
        # ============================================================
        MAX_RETRIES = 3
        result = None

        for attempt in range(MAX_RETRIES):
            try:
                response = await openrouter_service.chat_completion(
                    model=settings.llm_model_guided_gen,
                    messages=messages,
                    temperature=0.7 + (attempt * 0.1),
                    response_format={"type": "json_object"},
                )

                content = openrouter_service.get_content(response)
                print(f"[Guided Gen] Attempt {attempt + 1}: LLM response length: {len(content)}")

                result = openrouter_service.parse_json_response(content)
                print(f"[Guided Gen] Parsed result keys: {result.keys()}")

                # 필수 필드 확인
                concepts = result.get("concepts", [])
                flow = result.get("flow", [])
                if len(concepts) > 0 or len(flow) > 0:
                    print(f"[Guided Gen] ✓ Valid output on attempt {attempt + 1}")
                    break
                else:
                    print(f"[Guided Gen] ⚠️ Attempt {attempt + 1}: Empty concepts/flow")
                    if attempt < MAX_RETRIES - 1:
                        messages.append({"role": "assistant", "content": content})
                        messages.append({
                            "role": "user",
                            "content": "concepts와 flow 배열이 비어있습니다. 핵심 개념과 학습 흐름을 채워주세요."
                        })

            except ValueError as e:
                print(f"[Guided Gen] ⚠️ Attempt {attempt + 1} parse error: {e}")
                if attempt < MAX_RETRIES - 1:
                    print(f"[Guided Gen] Retrying... ({attempt + 2}/{MAX_RETRIES})")
                else:
                    print(f"[Guided Gen] ❌ All {MAX_RETRIES} attempts failed")
                    raise

        if result is None:
            raise ValueError("Failed to generate guided problem after all retries")

        if not result.get("original_id"):
            result["original_id"] = original_id
        if not result.get("language"):
            result["language"] = language

        # ============================================================
        # DB에 저장
        # ============================================================
        # Note: base_problems에 저장하는 로직 제거
        # - base_problems는 원본 문제 저장소 (Baekjoon, TACO 등)
        # - 유형별 테이블만 저장 (problems_blank, problems_puzzle, problems_guided)
        # - CodeGen 문제는 LangGraph의 code_gen 노드에서만 base_problems에 저장

        if base_problem_id and creator_id:
            try:
                save_result = await problem_save_service.save_generated_problem(
                    problem_type="guided",
                    generated_data=result,
                    base_problem_id=base_problem_id,
                    creator_id=creator_id,
                )
                if save_result.get("success"):
                    print(f"[Guided Gen] Saved to DB: {original_id} (user: {creator_id[:8]}...)")
                else:
                    print(f"[Guided Gen] DB save failed: {save_result.get('error')}")
            except Exception as save_err:
                print(f"[Guided Gen] DB save error (non-blocking): {save_err}")

        return GuidedProblemResponse(**result)

    except Exception as e:
        import traceback
        print(f"[Guided Gen] Error: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Guided problem generation error: {str(e)}"
        )


# ============================================================
# Code Generation (RAG Fallback)
# ============================================================

@router.post("/generate/code", response_model=CodeGenerationResponse)
async def generate_code(request: CodeGenerationRequest, db=Depends(get_db)):
    """
    Generate new educational code when RAG similarity is low.

    Uses Claude Sonnet via OpenRouter.
    """
    try:
        system_prompt = CODE_GEN_SYSTEM_PROMPT.format(
            user_request=json.dumps(request.user_request, ensure_ascii=False),
            similar_problems=json.dumps(request.similar_problems, ensure_ascii=False),
            user_status=request.user_status or "unknown",
            user_goal=request.user_goal or "unknown",
            user_level=request.user_level.value,
            strong_algorithms=", ".join(request.strong_algorithms) if request.strong_algorithms else "없음",
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "사용자 요청에 맞는 교육용 코드를 생성해주세요."},
        ]

        response = await openrouter_service.chat_completion(
            model=settings.llm_model_code_gen,
            messages=messages,
            temperature=0.7,
            max_tokens=8192,
            response_format={"type": "json_object"},
        )

        content = openrouter_service.get_content(response)
        result = openrouter_service.parse_json_response(content)

        return CodeGenerationResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Code generation error: {str(e)}"
        )


# ============================================================
# Hint Generation
# ============================================================

@router.post("/hint", response_model=HintAgentResponse)
async def generate_hint(request: HintAgentRequest, db=Depends(get_db)):
    """
    Generate AI-powered hint for a problem.

    Supports 4 hint levels (progressive disclosure).
    Routes to type-specific hint generators:
    - blank: 빈칸 채우기 전용 힌트
    - puzzle: 블록 순서 힌트 (TODO)
    - guided: 단계별 도움 (TODO)
    """
    try:
        hint_service = get_hint_service()
        problem_type = request.problem_type.value if request.problem_type else "blank"

        # Blank 문제 힌트 생성
        if problem_type == "blank":
            result = await hint_service.generate_blank_hint(
                problem_id=request.problem_id,
                base_problem_id=request.base_problem_id,
                hint_level=request.hint_level,
                current_blank_index=request.current_blank_index or 0,
                user_answers=request.user_answers,
                previous_hints=request.previous_hints,
                user_level=request.user_level.value,
                additional_info=request.problem_info,
            )
            return HintAgentResponse(**result)

        # Puzzle 문제 힌트 생성
        elif problem_type == "puzzle":
            # user_order와 correct_blocks 추출 (problem_info에서)
            user_order = request.problem_info.get("user_order", []) if request.problem_info else []
            correct_blocks = request.problem_info.get("correct_blocks", []) if request.problem_info else []

            result = await hint_service.generate_puzzle_hint(
                problem_id=request.problem_id,
                base_problem_id=request.base_problem_id,
                hint_level=request.hint_level,
                user_order=user_order,
                correct_blocks=correct_blocks,
                previous_hints=request.previous_hints,
                user_level=request.user_level.value,
                additional_info=request.problem_info,
            )
            return HintAgentResponse(**result)

        # Guided 문제 도움 생성
        elif problem_type == "guided":
            # current_step 추출 (problem_info에서)
            current_step = request.problem_info.get("current_step", 0) if request.problem_info else 0

            result = await hint_service.generate_guided_help(
                problem_id=request.problem_id,
                base_problem_id=request.base_problem_id,
                help_level=request.hint_level,
                current_step=current_step,
                user_code=request.user_code,
                previous_helps=request.previous_hints,
                user_level=request.user_level.value,
                additional_info=request.problem_info,
            )
            return HintAgentResponse(**result)

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown problem type: {problem_type}"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hint generation error: {str(e)}"
        )


# ============================================================
# Feedback Generation (문제 풀이 완료 후 피드백)
# ============================================================

@router.post("/feedback", response_model=FeedbackResponse)
async def generate_feedback(request: FeedbackRequest, db=Depends(get_db)):
    """
    문제 풀이 완료 후 피드백 생성

    정답 제출 후 호출되어 다음 정보를 기반으로 피드백 생성:
    - 풀이 시간
    - 힌트 사용량
    - 시도 횟수
    - 획득 XP

    Returns:
        grade, 성과 분석, 학습 포인트, 시각화 데이터 등
    """
    try:
        feedback_service = get_feedback_service()

        # 문제 정보 추출
        problem_info = None
        if request.problem_info:
            problem_info = {
                "title": request.problem_info.title,
                "difficulty": request.problem_info.difficulty,
                "topics": request.problem_info.topics,
            }

        # 피드백 생성
        result = await feedback_service.generate_feedback(
            user_id=request.user_id,
            problem_id=request.problem_id,
            is_correct=request.is_correct,
            solve_time_seconds=request.solve_time_seconds,
            hints_used=request.hints_used,
            xp_earned=request.xp_earned,
            problem_info=problem_info,
            problem_type=request.problem_type,
            attempt_count=request.attempt_count,
        )

        # FeedbackResponse 형식으로 변환
        return FeedbackResponse(
            grade=result.get("grade", "learning"),
            grade_emoji=result.get("grade_emoji", "🌱"),
            grade_message=result.get("grade_message", "잘했어요!"),
            summary={
                "title": result.get("summary", {}).get("title", "문제 풀이 완료!"),
                "highlight": result.get("summary", {}).get("highlight", ""),
            },
            performance_analysis={
                "time_feedback": result.get("performance_analysis", {}).get("time_feedback", ""),
                "hint_feedback": result.get("performance_analysis", {}).get("hint_feedback", ""),
                "attempt_feedback": result.get("performance_analysis", {}).get("attempt_feedback", ""),
            },
            learning_points=result.get("learning_points", []),
            improvements=result.get("improvements", []),
            visualization={
                "efficiency_score": result.get("visualization", {}).get("efficiency_score", 70),
                "speed_score": result.get("visualization", {}).get("speed_score", 70),
                "understanding_score": result.get("visualization", {}).get("understanding_score", 70),
                "time_comparison": result.get("visualization", {}).get("time_comparison"),
            },
            next_steps={
                "recommendation": result.get("next_steps", {}).get("recommendation", "다음 문제에 도전해보세요!"),
                "similar_problems": result.get("next_steps", {}).get("similar_problems"),
            },
            encouragement=result.get("encouragement", "계속 도전하세요! 💪"),
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Feedback generation error: {str(e)}"
        )


# ============================================================
# RAG Search
# ============================================================

@router.post("/search", response_model=RAGSearchResponse)
async def search_problems_rag(request: RAGSearchRequest, db=Depends(get_db)):
    """
    Search problems using RAG (vector similarity).

    Uses OpenAI embeddings + pgvector.
    Falls back to keyword search if embeddings unavailable.
    """
    try:
        # Build search query from topics and query
        search_query = request.query
        if request.topics:
            search_query += " " + " ".join(request.topics)

        # Perform hybrid search
        results, should_fallback = await rag_service.search_problems_hybrid(
            query=search_query,
            topics=request.topics,
            difficulty=request.difficulty.value if request.difficulty else None,
            language=request.language.value if request.language else None,
            limit=request.limit,
        )

        # Convert results to response format
        search_results = []
        for r in results:
            search_results.append(RAGSearchResult(
                id=r.get("problem_id", ""),
                title=r.get("text_content", "")[:100] if r.get("text_content") else "",
                description=r.get("text_content", "")[:300] if r.get("text_content") else "",
                similarity_score=r.get("similarity", 0),
                difficulty=r.get("difficulty", "medium"),
                topics=r.get("tags", []) if r.get("tags") else [],
            ))

        return RAGSearchResponse(
            results=search_results,
            query_embedding_used=True,
            fallback_to_code_gen=should_fallback,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"RAG search error: {str(e)}"
        )


# ============================================================
# Full Flow Endpoint
# ============================================================

@router.post("/recommend")
async def recommend_problems(
    collected_info: dict,
    user_context: Optional[dict] = None,
    db=Depends(get_db)
):
    """
    Full recommendation flow:
    1. Embed collected_info + user_context
    2. Search pgvector for similar problems
    3. If high similarity: return top 3 problems
    4. If low similarity: generate new code, then return

    Returns list of recommended problems for user to choose.
    """
    try:
        # Step 1: Build search query from collected info
        topics = collected_info.get("topics", [])
        difficulty = collected_info.get("difficulty", "medium")
        language = collected_info.get("language", "python")
        specific_needs = collected_info.get("specific_needs", "")
        search_query_text = collected_info.get("search_query", "")

        # Build comprehensive search query
        search_query = search_query_text or " ".join(topics)
        if specific_needs:
            search_query += " " + specific_needs

        # Step 2: Perform hybrid search with RAG
        results, should_fallback = await rag_service.search_problems_hybrid(
            query=search_query,
            topics=topics,
            difficulty=difficulty,
            language=language,
            limit=5,
        )

        # Step 3: Get full problem data for results
        problem_ids = [r.get("problem_id") for r in results if r.get("problem_id")]
        problems = []

        if problem_ids:
            # Fetch full problem data from base_problems
            response = db.table("base_problems")\
                .select("*")\
                .in_("id", problem_ids)\
                .execute()
            problems = response.data or []

            # Add similarity scores to problems
            similarity_map = {r["problem_id"]: r.get("similarity", 0) for r in results}
            for p in problems:
                p["similarity_score"] = similarity_map.get(p["id"], 0)

            # Sort by similarity score
            problems.sort(key=lambda x: x.get("similarity_score", 0), reverse=True)

        # Step 4: Check if we should generate new problems
        if not should_fallback and len(problems) >= 3:
            return {
                "status": "found",
                "problems": problems[:3],
                "fallback_used": False,
            }

        # Step 5: Fallback - generate new problem using Claude Sonnet
        if should_fallback or len(problems) < 3:
            try:
                generated = await rag_service.generate_problem_with_rag(
                    user_request=collected_info,
                    similar_problems=problems,
                    user_context=user_context,
                )
                return {
                    "status": "generated",
                    "problems": problems,
                    "generated_problem": generated,
                    "fallback_used": True,
                    "message": "유사한 문제가 부족하여 새로운 문제를 생성했습니다.",
                }
            except Exception as gen_error:
                print(f"Code generation fallback error: {gen_error}")
                return {
                    "status": "partial",
                    "problems": problems,
                    "fallback_used": True,
                    "message": "유사한 문제가 부족합니다. 다른 주제를 선택해보세요.",
                }

        return {
            "status": "found",
            "problems": problems[:3],
            "fallback_used": False,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Recommendation error: {str(e)}"
        )


# ============================================================
# Personalization Endpoints
# ============================================================

class UserProfileResponse(BaseModel):
    """사용자 학습 프로필 응답"""
    user_id: str
    total_attempts: int = 0
    correct_rate: float = 0.0
    strong_topics: List[str] = []
    weak_topics: List[str] = []
    preferred_difficulty: str = "easy"
    recent_topics: List[str] = []
    avg_hints_used: float = 0.0
    streak_days: int = 0
    last_active: Optional[str] = None


class RecommendationItem(BaseModel):
    """추천 문제 항목"""
    problem_id: str
    base_problem_id: Optional[str] = None
    problem_type: str = "blank"
    difficulty: str = "medium"
    topics: List[str] = []
    reason: str = ""
    confidence: float = 0.5


class PersonalizedRecommendationsResponse(BaseModel):
    """개인화된 문제 추천 응답"""
    recommendations: List[RecommendationItem]
    profile_summary: Optional[Dict[str, Any]] = None


@router.get("/user/profile", response_model=UserProfileResponse)
async def get_user_learning_profile(
    current_user_id: Optional[UUID] = Depends(get_current_user_id_optional),
):
    """
    사용자 학습 프로필 조회

    학습 히스토리를 분석하여 다음 정보를 제공:
    - 총 시도 횟수, 정답률
    - 강점/약점 토픽
    - 선호 난이도
    - 최근 학습 토픽
    - 연속 학습일

    Returns:
        UserProfileResponse
    """
    if not current_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="로그인이 필요합니다."
        )

    try:
        from ..services.personalization import get_personalization_service

        ps = get_personalization_service()
        profile = await ps.get_user_profile(str(current_user_id))

        if not profile:
            return UserProfileResponse(user_id=str(current_user_id))

        return UserProfileResponse(
            user_id=profile.user_id,
            total_attempts=profile.total_attempts,
            correct_rate=profile.correct_rate,
            strong_topics=profile.strong_topics,
            weak_topics=profile.weak_topics,
            preferred_difficulty=profile.preferred_difficulty,
            recent_topics=profile.recent_topics,
            avg_hints_used=profile.avg_hints_used,
            streak_days=profile.streak_days,
            last_active=profile.last_active.isoformat() if profile.last_active else None,
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"프로필 조회 오류: {str(e)}"
        )


@router.get("/user/recommendations", response_model=PersonalizedRecommendationsResponse)
async def get_personalized_recommendations(
    limit: int = 5,
    problem_type: Optional[str] = None,
    current_user_id: Optional[UUID] = Depends(get_current_user_id_optional),
):
    """
    개인화된 문제 추천

    사용자의 학습 프로필을 기반으로 맞춤 문제를 추천합니다.

    추천 전략:
    - 40%: 약점 보완 문제
    - 30%: 다음 난이도 도전 문제
    - 30%: 복습 문제 (틀렸던 문제)

    Args:
        limit: 추천 개수 (기본 5)
        problem_type: 문제 유형 필터 (blank, puzzle, guided)

    Returns:
        PersonalizedRecommendationsResponse
    """
    if not current_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="로그인이 필요합니다."
        )

    try:
        from ..services.personalization import get_personalization_service

        ps = get_personalization_service()
        recommendations = await ps.get_recommendations(
            user_id=str(current_user_id),
            limit=limit,
            problem_type=problem_type,
        )

        # 프로필 요약도 함께 반환
        rag_context = await ps.get_rag_context(str(current_user_id))

        return PersonalizedRecommendationsResponse(
            recommendations=[
                RecommendationItem(
                    problem_id=r.problem_id,
                    base_problem_id=r.base_problem_id,
                    problem_type=r.problem_type,
                    difficulty=r.difficulty,
                    topics=r.topics,
                    reason=r.reason,
                    confidence=r.confidence,
                )
                for r in recommendations
            ],
            profile_summary={
                "user_level": rag_context.get("user_level", "beginner"),
                "preferred_difficulty": rag_context.get("preferred_difficulty", "easy"),
                "weak_topics": rag_context.get("weak_topics", [])[:3],
                "streak_days": rag_context.get("streak_days", 0),
            }
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"추천 조회 오류: {str(e)}"
        )


@router.post("/search/personalized")
async def search_problems_personalized(
    request: RAGSearchRequest,
    current_user_id: Optional[UUID] = Depends(get_current_user_id_optional),
    db=Depends(get_db),
):
    """
    개인화된 문제 검색

    사용자의 학습 프로필을 고려하여 검색 결과를 개인화합니다.

    개인화 요소:
    - 약점 토픽 관련 결과 부스트
    - 선호 난이도 결과 우선
    - 이미 푼 문제 중복 방지 (옵션)
    """
    try:
        search_query = request.query
        if request.topics:
            search_query += " " + " ".join(request.topics)

        user_id = str(current_user_id) if current_user_id else None

        if user_id:
            # 개인화된 검색
            results, should_fallback = await rag_service.search_problems_personalized(
                query=search_query,
                user_id=user_id,
                topics=request.topics,
                difficulty=request.difficulty.value if request.difficulty else None,
                language=request.language.value if request.language else None,
                limit=request.limit,
            )
        else:
            # 일반 검색
            results, should_fallback = await rag_service.search_problems_hybrid(
                query=search_query,
                topics=request.topics,
                difficulty=request.difficulty.value if request.difficulty else None,
                language=request.language.value if request.language else None,
                limit=request.limit,
            )

        return {
            "results": results,
            "personalized": user_id is not None,
            "fallback_to_code_gen": should_fallback,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"검색 오류: {str(e)}"
        )


# ============================================================
# Admin Endpoints (for embedding management)
# ============================================================

@router.post("/admin/embed-problems")
async def embed_problems_batch(
    limit: int = 100,
    offset: int = 0,
    db=Depends(get_db)
):
    """
    Batch embed problems from base_problems table.
    Admin endpoint for populating embeddings.

    Args:
        limit: Number of problems to process
        offset: Offset for pagination
    """
    try:
        # Fetch problems without embeddings
        response = db.table("base_problems")\
            .select("*")\
            .range(offset, offset + limit - 1)\
            .execute()

        problems = response.data or []

        if not problems:
            return {
                "message": "No problems to embed",
                "processed": 0,
            }

        # Batch embed
        result = await rag_service.batch_embed_problems(problems)

        return {
            "message": f"Embedded {result['success']} problems",
            "success": result["success"],
            "failed": result["failed"],
            "offset": offset,
            "limit": limit,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch embedding error: {str(e)}"
        )


@router.get("/admin/embedding-stats")
async def get_embedding_stats(db=Depends(get_db)):
    """
    Get embedding statistics.
    """
    try:
        # Count total problems
        problems_count = db.table("base_problems")\
            .select("id", count="exact")\
            .execute()

        # Count embeddings
        embeddings_count = db.table("problem_embeddings")\
            .select("id", count="exact")\
            .execute()

        return {
            "total_problems": problems_count.count or 0,
            "total_embeddings": embeddings_count.count or 0,
            "coverage": (
                (embeddings_count.count / problems_count.count * 100)
                if problems_count.count else 0
            ),
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Stats error: {str(e)}"
        )
