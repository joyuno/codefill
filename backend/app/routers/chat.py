"""
Chat Router
AI-powered Intent Classification + Response Generation

규칙 기반에서 하이브리드(Embedding + LLM) 기반으로 업그레이드
- Embedding 유사도 기반 빠른 분류
- LLM 검증으로 정확도 보완
- 의도별 맞춤 응답 생성
"""

from fastapi import APIRouter, HTTPException, Depends, Header, status
from fastapi.responses import StreamingResponse
from typing import Optional, List, AsyncGenerator
from uuid import UUID
from pydantic import BaseModel
import json

from ..database import get_db
from ..intents import intent_classifier, IntentType, INTENT_DEFINITIONS

router = APIRouter()


class ChatMessage(BaseModel):
    """Chat message model."""
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    """Chat request model."""
    message: str
    conversation_history: List[ChatMessage] = []
    session_context: Optional[dict] = None  # 세션 컨텍스트 추가


class QuickChip(BaseModel):
    """Quick action chip for frontend."""
    label: str
    value: str
    category: str = "action"


class ChatResponse(BaseModel):
    """Chat response model."""
    message: str
    intent: Optional[str] = None
    confidence: Optional[float] = None  # 신뢰도 추가
    method: Optional[str] = None  # 분류 방법 추가
    action: Optional[dict] = None
    chips: Optional[List[QuickChip]] = None  # 프론트엔드 호환용 quick chips
    sessionId: Optional[str] = None  # 세션 ID (호환성)


class PracticeChatRequest(BaseModel):
    """Practice chatbot request."""
    message: str
    collected_info: Optional[dict] = None


class PracticeChatResponse(BaseModel):
    """Practice chatbot response."""
    message: str
    is_ready: bool = False
    collected_info: Optional[dict] = None
    recommended_problems: Optional[List[dict]] = None


# ============================================================
# Intent별 응답 생성
# ============================================================

async def generate_intent_response(
    intent: IntentType,
    confidence: float,
    message: str = "",
    conversation_history: list = None,
    user_context: dict = None,
) -> dict:
    """
    의도별 맞춤 응답 생성 - LLM 기반 동적 메시지 + 정적 chips

    Args:
        intent: 분류된 의도
        confidence: 분류 신뢰도
        message: 원본 사용자 메시지
        conversation_history: 대화 히스토리
        user_context: 사용자 컨텍스트

    Returns:
        dict with message, action, and chips
    """
    from ..services.dynamic_response import dynamic_response_generator

    # chips와 action은 정적으로 유지 (UI 요소)
    intent_configs = {
        IntentType.NEW_PROBLEM: {
            "action": {"type": "collect_info", "next": "topic"},
            "chips": [
                {"label": "DP", "value": "dp", "category": "topic"},
                {"label": "그래프", "value": "graph", "category": "topic"},
                {"label": "정렬", "value": "sort", "category": "topic"},
            ]
        },
        IntentType.SIMILAR_CODE_PROBLEM: {
            "action": {"type": "collect_info", "next": "code", "requires_context": "code"},
            "chips": None
        },
        IntentType.TOPIC_SPECIFIC: {
            "action": {"type": "collect_info", "next": "difficulty"},
            "chips": [
                {"label": "Easy", "value": "easy", "category": "difficulty"},
                {"label": "Medium", "value": "medium", "category": "difficulty"},
                {"label": "Hard", "value": "hard", "category": "difficulty"},
            ]
        },
        IntentType.DIFFICULTY_CHANGE: {
            "action": {"type": "update_setting", "setting": "difficulty"},
            "chips": [
                {"label": "Easy", "value": "easy", "category": "difficulty"},
                {"label": "Medium", "value": "medium", "category": "difficulty"},
                {"label": "Hard", "value": "hard", "category": "difficulty"},
            ]
        },
        IntentType.LANGUAGE_CHANGE: {
            "action": {"type": "update_setting", "setting": "language"},
            "chips": [
                {"label": "Python", "value": "python", "category": "language"},
                {"label": "Java", "value": "java", "category": "language"},
                {"label": "C++", "value": "cpp", "category": "language"},
            ]
        },
        IntentType.RANDOM_RECOMMEND: {
            "action": {"type": "recommend", "mode": "random"},
            "chips": None
        },
        IntentType.HINT_REQUEST: {
            "action": {"type": "hint", "requires_context": "problem"},
            "chips": [
                {"label": "살짝만", "value": "hint_1", "category": "hint"},
                {"label": "조금 더", "value": "hint_2", "category": "hint"},
                {"label": "많이", "value": "hint_3", "category": "hint"},
            ]
        },
        IntentType.SOLUTION_REQUEST: {
            "action": {"type": "confirm", "next": "solution"},
            "chips": [
                {"label": "힌트 먼저", "value": "hint", "category": "action"},
                {"label": "정답 보기", "value": "solution", "category": "action"},
            ]
        },
        IntentType.EXPLANATION_REQUEST: {
            "action": {"type": "explain"},
            "chips": [
                {"label": "알고리즘", "value": "algorithm", "category": "explain"},
                {"label": "코드", "value": "code", "category": "explain"},
                {"label": "시간복잡도", "value": "complexity", "category": "explain"},
            ]
        },
        IntentType.CODE_REVIEW: {
            "action": {"type": "review", "requires_context": "code"},
            "chips": None
        },
        IntentType.ERROR_HELP: {
            "action": {"type": "debug", "requires_context": "code"},
            "chips": None
        },
        IntentType.SKIP_PROBLEM: {
            "action": {"type": "skip", "suggest_new": True},
            "chips": [
                {"label": "다른 문제", "value": "new_problem", "category": "action"},
                {"label": "쉬운 문제", "value": "easy", "category": "difficulty"},
            ]
        },
        IntentType.RETRY_PROBLEM: {
            "action": {"type": "reset"},
            "chips": None
        },
        IntentType.SUBMIT_CODE: {
            "action": {"type": "submit"},
            "chips": None
        },
        IntentType.PROGRESS_CHECK: {
            "action": {"type": "show_progress"},
            "chips": None
        },
        IntentType.WEAK_POINT: {
            "action": {"type": "analyze_weakness"},
            "chips": None
        },
        IntentType.STUDY_PLAN: {
            "action": {"type": "create_plan", "next": "goal"},
            "chips": [
                {"label": "코딩 테스트", "value": "coding_test", "category": "goal"},
                {"label": "알고리즘 기초", "value": "basics", "category": "goal"},
                {"label": "특정 주제", "value": "specific", "category": "goal"},
            ]
        },
        IntentType.GREETING: {
            "action": None,
            "chips": [
                {"label": "문제 풀기", "value": "practice", "category": "action"},
                {"label": "학습 로드맵", "value": "study_plan", "category": "action"},
                {"label": "약점 분석", "value": "weakness", "category": "action"},
            ]
        },
        IntentType.THANKS: {
            "action": None,
            "chips": [
                {"label": "다른 문제", "value": "new_problem", "category": "action"},
                {"label": "비슷한 문제", "value": "similar", "category": "action"},
            ]
        },
        IntentType.GOODBYE: {
            "action": None,
            "chips": None
        },
        IntentType.CONFUSION: {
            "action": {"type": "clarify"},
            "chips": [
                {"label": "설명해줘", "value": "explain", "category": "action"},
                {"label": "힌트 줘", "value": "hint", "category": "action"},
                {"label": "에러 도와줘", "value": "error", "category": "action"},
            ]
        },
        IntentType.AFFIRMATION: {
            "action": {"type": "confirm_previous"},
            "chips": None
        },
        IntentType.NEGATION: {
            "action": {"type": "offer_alternatives"},
            "chips": [
                {"label": "다른 문제", "value": "new_problem", "category": "action"},
                {"label": "다른 난이도", "value": "difficulty", "category": "action"},
            ]
        },
        IntentType.OUT_OF_SCOPE: {
            "action": None,
            "chips": [
                {"label": "문제 풀기", "value": "practice", "category": "action"},
                {"label": "코드 리뷰", "value": "review", "category": "action"},
            ]
        },
        IntentType.INAPPROPRIATE_MESSAGE: {
            "action": None,
            "chips": [
                {"label": "문제 풀기", "value": "practice", "category": "action"},
                {"label": "쉬운 문제부터", "value": "easy", "category": "difficulty"},
                {"label": "추천받기", "value": "recommend", "category": "action"},
            ]
        },
        IntentType.CLARIFICATION_NEEDED: {
            "action": {"type": "clarify"},
            "chips": [
                {"label": "문제 풀기", "value": "practice", "category": "action"},
                {"label": "힌트 요청", "value": "hint", "category": "action"},
                {"label": "코드 리뷰", "value": "review", "category": "action"},
            ]
        },
    }

    # 설정 가져오기 (chips, action)
    config = intent_configs.get(intent, {
        "action": None,
        "chips": [
            {"label": "문제 풀기", "value": "practice", "category": "action"},
            {"label": "힌트 요청", "value": "hint", "category": "action"},
        ]
    })

    # LLM 기반 동적 메시지 생성 (하드코딩된 메시지 제거)
    dynamic_response = await dynamic_response_generator.generate(
        message=message,
        intent=intent.value if hasattr(intent, 'value') else str(intent),
        conversation_history=conversation_history,
        user_context=user_context,
    )

    return {
        "message": dynamic_response.message,
        "action": config.get("action"),
        "chips": config.get("chips"),
    }


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest, db=Depends(get_db)):
    """
    Main chat endpoint (Orchestrator).

    AI-powered Intent Classification:
    1. Embedding 유사도 기반 빠른 분류
    2. 중간 신뢰도 시 LLM 검증
    3. 낮은 신뢰도 시 LLM 직접 분류
    """
    import uuid

    try:
        # 세션 컨텍스트 구성
        session_ctx = request.session_context or {}
        session_ctx["message"] = request.message

        # AI 기반 의도 분류
        intent_result = await intent_classifier.classify(
            message=request.message,
            session_context=session_ctx
        )

        # 의도별 응답 생성 (LLM 기반 동적 응답)
        response_data = await generate_intent_response(
            intent=intent_result.intent,
            confidence=intent_result.confidence,
            message=request.message,
            conversation_history=request.session_context.get("conversation_history") if request.session_context else None,
            user_context=request.session_context,
        )

        # chips 변환 (dict -> QuickChip)
        chips = None
        if response_data.get("chips"):
            chips = [
                QuickChip(
                    label=chip["label"],
                    value=chip["value"],
                    category=chip.get("category", "action")
                )
                for chip in response_data["chips"]
            ]

        return ChatResponse(
            message=response_data["message"],
            intent=intent_result.intent.value,
            confidence=intent_result.confidence,
            method=intent_result.method,
            action=response_data.get("action"),
            chips=chips,
            sessionId=str(uuid.uuid4()),  # 호환성을 위한 세션 ID
        )

    except Exception as e:
        # Fallback 응답 - LLM 기반 동적 응답 시도
        print(f"Chat intent classification error: {e}")
        try:
            from ..services.dynamic_response import dynamic_response_generator
            fallback_response = await dynamic_response_generator.generate(
                message=request.message,
                intent="error_fallback",
                conversation_history=None,
                user_context=None,
            )
            fallback_message = fallback_response.message
        except Exception:
            fallback_message = "잠깐 문제가 있었어. 다시 말해줄래?"

        return ChatResponse(
            message=fallback_message,
            intent="greeting",
            confidence=0.5,
            method="fallback",
            action=None,
            chips=[
                QuickChip(label="문제 풀기", value="practice", category="action"),
                QuickChip(label="학습 로드맵", value="study_plan", category="action"),
                QuickChip(label="약점 분석", value="weakness", category="action"),
            ],
            sessionId=str(uuid.uuid4()),
        )


@router.post("/practice", response_model=PracticeChatResponse)
async def practice_chat(request: PracticeChatRequest, db=Depends(get_db)):
    """
    Practice Chatbot for collecting problem generation info.

    Collects:
    - framework: react, vue, python, etc.
    - difficulty: easy, medium, hard
    - topic: specific topic (optional)
    - problem_type: blank, bug, output, refactor
    """
    collected = request.collected_info or {}
    message_lower = request.message.lower()

    # Detect framework
    frameworks = {
        "react": ["react", "리액트"],
        "vue": ["vue", "뷰"],
        "javascript": ["javascript", "js", "자바스크립트"],
        "typescript": ["typescript", "ts", "타입스크립트"],
        "python": ["python", "파이썬"],
    }

    for fw, keywords in frameworks.items():
        for kw in keywords:
            if kw in message_lower and "framework" not in collected:
                collected["framework"] = fw
                break

    # Detect difficulty
    if "쉬" in message_lower or "easy" in message_lower:
        collected["difficulty"] = "easy"
    elif "어려" in message_lower or "hard" in message_lower:
        collected["difficulty"] = "hard"
    elif "중간" in message_lower or "medium" in message_lower:
        collected["difficulty"] = "medium"

    # Detect problem type
    problem_types = {
        "blank": ["빈칸", "blank", "채우기"],
        "bug": ["버그", "bug", "수정", "디버깅"],
        "output": ["출력", "output", "예측"],
        "refactor": ["리팩토링", "refactor", "클린"],
    }

    for pt, keywords in problem_types.items():
        for kw in keywords:
            if kw in message_lower and "problem_type" not in collected:
                collected["problem_type"] = pt
                break

    # Check what's missing
    required = ["framework", "difficulty", "problem_type"]
    missing = [f for f in required if f not in collected]

    if not missing:
        # All info collected, ready to generate
        # Fetch matching problems from DB
        try:
            query = db.table("problems")\
                .select("id, difficulty, problem_type, codes(title, framework)")\
                .eq("problem_type", collected["problem_type"])\
                .eq("difficulty", collected["difficulty"])\
                .limit(5)

            result = query.execute()

            problems = []
            for item in (result.data or []):
                code_data = item.get("codes", {})
                if code_data.get("framework") == collected["framework"]:
                    problems.append({
                        "id": item["id"],
                        "title": code_data.get("title", ""),
                        "difficulty": item["difficulty"],
                        "problem_type": item["problem_type"],
                    })

            if problems:
                return PracticeChatResponse(
                    message=f"좋아요! {collected['framework']} {collected['difficulty']} 난이도의 {collected['problem_type']} 문제를 찾았어요. 아래에서 선택해주세요!",
                    is_ready=True,
                    collected_info=collected,
                    recommended_problems=problems,
                )
            else:
                return PracticeChatResponse(
                    message=f"죄송해요, {collected['framework']} {collected['difficulty']} 난이도의 {collected['problem_type']} 문제가 아직 없어요. 다른 조건을 선택해주시겠어요?",
                    is_ready=False,
                    collected_info={},  # Reset
                )
        except Exception as e:
            return PracticeChatResponse(
                message=f"문제를 찾는 중 오류가 발생했어요. 다시 시도해주세요.",
                is_ready=False,
                collected_info=collected,
            )

    # Ask for missing info
    prompts = {
        "framework": "어떤 언어/프레임워크로 연습하고 싶으신가요? (React, Vue, JavaScript, Python 등)",
        "difficulty": "난이도는 어느 정도로 할까요? (실버/골드/플래티넘/다이아/마스터)",
        "problem_type": "어떤 유형의 문제를 풀어볼까요?\n• 빈칸 채우기: 코드의 핵심 부분 맞추기\n• 버그 수정: 오류 찾아 고치기\n• 출력 예측: 실행 결과 맞추기\n• 리팩토링: 더 좋은 코드로 개선하기",
    }

    next_prompt = prompts.get(missing[0], "무엇을 도와드릴까요?")

    return PracticeChatResponse(
        message=next_prompt,
        is_ready=False,
        collected_info=collected,
    )


@router.post("/stream")
async def chat_stream(request: ChatRequest, db=Depends(get_db)):
    """
    Streaming chat endpoint for real-time responses.

    Returns Server-Sent Events (SSE) stream.
    Uses AI-powered intent classification.
    """
    async def generate_stream() -> AsyncGenerator[str, None]:
        try:
            # 세션 컨텍스트 구성
            session_ctx = request.session_context or {}
            session_ctx["message"] = request.message

            # AI 기반 의도 분류
            intent_result = await intent_classifier.classify(
                message=request.message,
                session_context=session_ctx
            )

            # 의도별 응답 생성 (LLM 기반 동적 응답)
            response_data = await generate_intent_response(
                intent=intent_result.intent,
                confidence=intent_result.confidence,
                message=request.message,
                conversation_history=request.session_context.get("conversation_history") if request.session_context else None,
                user_context=request.session_context,
            )

            # 스트리밍 방식으로 응답 전송
            message = response_data["message"]
            for char in message:
                yield f"data: {json.dumps({'content': char})}\n\n"

            yield f"data: {json.dumps({'done': True, 'intent': intent_result.intent.value, 'confidence': intent_result.confidence, 'method': intent_result.method})}\n\n"

        except Exception as e:
            print(f"Stream error: {e}")
            # LLM 기반 동적 폴백
            try:
                from ..services.dynamic_response import dynamic_response_generator
                fallback_response = await dynamic_response_generator.generate(
                    message=request.message,
                    intent="error_fallback",
                )
                fallback_message = fallback_response.message
            except Exception:
                fallback_message = "잠깐 문제가 있었어. 다시 말해줄래?"

            for char in fallback_message:
                yield f"data: {json.dumps({'content': char})}\n\n"
            yield f"data: {json.dumps({'done': True, 'intent': 'greeting', 'error': str(e)})}\n\n"

    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream"
    )
