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
)

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
    conversation_history: List[ChatAgentMessage] = []
    user_context: Optional[Dict[str, Any]] = None
    session_state: Optional[Dict[str, Any]] = None  # 세션 상태


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
    # Solving 결과
    hint_level: Optional[int] = None
    is_correct: Optional[bool] = None


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
    """
    try:
        orchestrator = get_chat_orchestrator_main()

        # 대화 히스토리를 딕셔너리 형태로 변환
        conversation_history = [
            {"role": msg.role, "content": msg.content}
            for msg in request.conversation_history
        ]

        # user_context에 user_id 추가 (DB 저장에 필요)
        user_context = request.user_context or {}
        if current_user_id:
            user_context["user_id"] = str(current_user_id)

        # 오케스트레이터 실행
        result = await orchestrator.process(
            message=request.message,
            conversation_history=conversation_history,
            user_context=user_context,
            session_state=request.session_state,
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
            hint_level=result.get("hint_level"),
            is_correct=result.get("is_correct"),
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat agent error: {str(e)}"
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
        original_id = bp.id or bp.name

        # 로그인된 유저 ID 사용 (JWT 토큰에서 추출)
        creator_id = str(current_user_id) if current_user_id else None

        # ============================================================
        # Cache-First 로직
        # ============================================================
        problem_save_service = get_problem_save_service()

        # base_problem_id 조회 (UUID)
        base_problem_id = problem_save_service.get_base_problem_id(original_id)

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

        response = await openrouter_service.chat_completion(
            model=settings.llm_model_blank_gen,
            messages=messages,
            temperature=0.7,
            response_format={"type": "json_object"},
        )

        content = openrouter_service.get_content(response)
        print(f"[Blank Gen] LLM response: {content[:500]}...")

        result = openrouter_service.parse_json_response(content)
        print(f"[Blank Gen] Parsed result keys: {result.keys()}")

        if not result.get("original_id"):
            result["original_id"] = original_id
        if not result.get("language"):
            result["language"] = language

        # ============================================================
        # DB에 저장
        # ============================================================
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
        original_id = bp.id or bp.name

        # 로그인된 유저 ID 사용 (JWT 토큰에서 추출)
        creator_id = str(current_user_id) if current_user_id else None

        # ============================================================
        # Cache-First 로직
        # ============================================================
        problem_save_service = get_problem_save_service()
        base_problem_id = problem_save_service.get_base_problem_id(original_id)

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

        response = await openrouter_service.chat_completion(
            model=settings.llm_model_puzzle_gen,
            messages=messages,
            temperature=0.7,
            response_format={"type": "json_object"},
        )

        content = openrouter_service.get_content(response)
        print(f"[Puzzle Gen] LLM response: {content[:500]}...")

        result = openrouter_service.parse_json_response(content)
        print(f"[Puzzle Gen] Parsed result keys: {result.keys()}")

        if not result.get("original_id"):
            result["original_id"] = original_id
        if not result.get("language"):
            result["language"] = language

        # ============================================================
        # DB에 저장
        # ============================================================
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
        original_id = bp.id or bp.name

        # 로그인된 유저 ID 사용 (JWT 토큰에서 추출)
        creator_id = str(current_user_id) if current_user_id else None

        # ============================================================
        # Cache-First 로직
        # ============================================================
        problem_save_service = get_problem_save_service()
        base_problem_id = problem_save_service.get_base_problem_id(original_id)

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

        response = await openrouter_service.chat_completion(
            model=settings.llm_model_guided_gen,
            messages=messages,
            temperature=0.7,
            response_format={"type": "json_object"},
        )

        content = openrouter_service.get_content(response)
        result = openrouter_service.parse_json_response(content)

        if not result.get("original_id"):
            result["original_id"] = original_id
        if not result.get("language"):
            result["language"] = language

        # ============================================================
        # DB에 저장
        # ============================================================
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

    Uses Gemini Flash via OpenRouter.
    Supports 4 hint levels (progressive disclosure).
    """
    try:
        system_prompt = HINT_AGENT_SYSTEM_PROMPT.format(
            problem_info=json.dumps(request.problem_info, ensure_ascii=False),
            user_code=request.user_code or "아직 코드 작성 안 함",
            attempt_count=request.attempt_count,
            hint_level=request.hint_level,
            previous_hints=json.dumps(request.previous_hints, ensure_ascii=False),
            user_level=request.user_level.value,
            related_docs="[]",  # TODO: Implement Docs RAG
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"레벨 {request.hint_level} 힌트를 생성해주세요."},
        ]

        response = await openrouter_service.chat_completion(
            model=settings.llm_model_hint,
            messages=messages,
            temperature=0.7,
            response_format={"type": "json_object"},
        )

        content = openrouter_service.get_content(response)
        result = openrouter_service.parse_json_response(content)

        return HintAgentResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hint generation error: {str(e)}"
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
