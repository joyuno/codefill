from fastapi import APIRouter, HTTPException, Depends, Header, status
from fastapi.responses import StreamingResponse
from typing import Optional, List, AsyncGenerator
from uuid import UUID
from pydantic import BaseModel
import json

from ..database import get_db

router = APIRouter()


class ChatMessage(BaseModel):
    """Chat message model."""
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    """Chat request model."""
    message: str
    conversation_history: List[ChatMessage] = []


class ChatResponse(BaseModel):
    """Chat response model."""
    message: str
    intent: Optional[str] = None
    action: Optional[dict] = None


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


# Intent keywords for rule-based routing
INTENT_KEYWORDS = {
    "PRACTICE": ["문제", "풀", "연습", "practice", "solve", "코딩", "코드", "빈칸", "버그", "출력", "리팩토링"],
    "PATH": ["커리큘럼", "로드맵", "학습 경로", "계획", "path", "roadmap", "curriculum"],
    "TUTOR": ["분석", "약점", "튜터", "코칭", "tutor", "weakness", "coach"],
    "REVIEW": ["복습", "review", "다시"],
}


def detect_intent(message: str) -> str:
    """Rule-based intent detection."""
    message_lower = message.lower()

    for intent, keywords in INTENT_KEYWORDS.items():
        for keyword in keywords:
            if keyword in message_lower:
                return intent

    return "GENERAL"


def generate_rule_based_response(message: str, intent: str) -> ChatResponse:
    """Generate response based on detected intent."""

    responses = {
        "PRACTICE": ChatResponse(
            message="문제를 풀어보고 싶으시군요! 어떤 프레임워크나 언어로 연습하고 싶으신가요? (예: React, Python, JavaScript)",
            intent="PRACTICE",
            action={"type": "collect_info", "next": "framework"}
        ),
        "PATH": ChatResponse(
            message="학습 로드맵을 만들어드릴게요. 먼저 목표가 무엇인가요? (예: 코테 준비, 실무 역량 강화, 프레임워크 학습)",
            intent="PATH",
            action={"type": "collect_info", "next": "goal"}
        ),
        "TUTOR": ChatResponse(
            message="약점 분석을 해드릴게요. 전체 분석을 원하시나요, 아니면 특정 분야만 분석할까요?",
            intent="TUTOR",
            action={"type": "collect_info", "next": "scope"}
        ),
        "REVIEW": ChatResponse(
            message="복습 문제를 가져올게요. 잠시만 기다려주세요.",
            intent="REVIEW",
            action={"type": "fetch_review"}
        ),
        "GENERAL": ChatResponse(
            message="안녕하세요! CodeFill에 오신 것을 환영합니다. 저는 AI 코딩 학습 도우미예요. 무엇을 도와드릴까요?\n\n• 문제 풀기\n• 학습 로드맵 만들기\n• 약점 분석\n• 복습하기",
            intent="GENERAL",
            action=None
        ),
    }

    return responses.get(intent, responses["GENERAL"])


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest, db=Depends(get_db)):
    """
    Main chat endpoint (Orchestrator).

    Detects user intent and routes to appropriate flow.
    Currently uses rule-based detection.
    AI-powered orchestration requires OpenRouter API key.
    """
    intent = detect_intent(request.message)
    response = generate_rule_based_response(request.message, intent)

    return response


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
        "difficulty": "난이도는 어느 정도로 할까요? (쉬움/중간/어려움)",
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
    AI streaming requires OpenRouter API key.
    """
    async def generate_stream() -> AsyncGenerator[str, None]:
        # Rule-based response for now
        intent = detect_intent(request.message)
        response = generate_rule_based_response(request.message, intent)

        # Simulate streaming by yielding characters
        for char in response.message:
            yield f"data: {json.dumps({'content': char})}\n\n"

        yield f"data: {json.dumps({'done': True, 'intent': intent})}\n\n"

    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream"
    )
