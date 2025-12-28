"""
Agent Router
API endpoints for AI agents
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import StreamingResponse
from typing import Optional, Union
import json

from ..database import get_db
from ..config import get_settings
from ..services.openrouter import openrouter_service
from ..services.rag import rag_service
from ..services.embedding import embedding_service
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
)
from ..models.agent import (
    # Chat Agent
    ChatAgentRequest,
    ChatAgentResponse,
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
)

router = APIRouter()


# ============================================================
# Chat Agent - Information Collection
# ============================================================

@router.post("/chat", response_model=ChatAgentResponse)
async def chat_agent(request: ChatAgentRequest, db=Depends(get_db)):
    """
    AI-powered information collection chatbot.

    Collects user preferences for problem recommendation:
    - topics: algorithm topics (array)
    - difficulty: easy/medium/hard
    - language: python/java/cpp
    - specific_needs: free text
    - time_available: minutes

    Uses GPT-4o-mini via OpenRouter.
    """
    try:
        # Build user context string
        user_context_str = json.dumps(request.user_context or {}, ensure_ascii=False)

        # Format system prompt with user context
        system_prompt = CHAT_AGENT_SYSTEM_PROMPT.format(
            user_context=user_context_str
        )

        # Build messages
        messages = [{"role": "system", "content": system_prompt}]

        # Add conversation history
        for msg in request.conversation_history:
            messages.append({"role": msg.role, "content": msg.content})

        # Add current message
        messages.append({"role": "user", "content": request.message})

        # Call LLM
        response = await openrouter_service.chat_completion(
            model=settings.llm_model_chat,
            messages=messages,
            temperature=0.7,
            response_format={"type": "json_object"},
        )

        content = openrouter_service.get_content(response)
        result = openrouter_service.parse_json_response(content)

        # Parse collected info
        collected = result.get("collected_info", {})

        return ChatAgentResponse(
            message=result.get("message", ""),
            collected_info=CollectedInfo(
                topics=collected.get("topics", []),
                difficulty=collected.get("difficulty"),
                language=collected.get("language"),
                specific_needs=collected.get("specific_needs"),
                time_available=collected.get("time_available"),
            ),
            is_complete=result.get("is_complete", False),
            search_query=result.get("search_query"),
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat agent error: {str(e)}"
        )


@router.post("/chat/stream")
async def chat_agent_stream(request: ChatAgentRequest, db=Depends(get_db)):
    """
    Streaming version of chat agent.
    Returns Server-Sent Events (SSE).
    """
    async def generate():
        try:
            user_context_str = json.dumps(request.user_context or {}, ensure_ascii=False)
            system_prompt = CHAT_AGENT_SYSTEM_PROMPT.format(
                user_context=user_context_str
            )

            messages = [{"role": "system", "content": system_prompt}]
            for msg in request.conversation_history:
                messages.append({"role": msg.role, "content": msg.content})
            messages.append({"role": "user", "content": request.message})

            async for chunk in openrouter_service.chat_completion_stream(
                model=settings.llm_model_chat,
                messages=messages,
                temperature=0.7,
            ):
                yield f"data: {json.dumps({'content': chunk})}\n\n"

            yield f"data: {json.dumps({'done': True})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


# ============================================================
# Intent-Based Chat Agent
# ============================================================

@router.post("/chat/intent", response_model=IntentChatResponse)
async def intent_chat_agent(request: IntentChatRequest, db=Depends(get_db)):
    """
    Intent-based AI chat agent.

    1. 사용자 메시지 의도 분류 (Embedding + LLM Fallback)
    2. 의도에 따른 적절한 응답 생성
    3. 코드 컨텍스트가 필요한 의도는 컨텍스트 확인

    Supported intents:
    - new_problem: 새 문제 요청 → 정보 수집 시작
    - similar_code_problem: 비슷한 코드 문제 → 코드 컨텍스트 필요
    - topic_specific: 특정 주제 문제 → 주제 추출 후 검색
    - hint_request: 힌트 요청 → 현재 문제 컨텍스트 필요
    - 등...
    """
    try:
        # Build session context for intent classification
        session_ctx = {}
        if request.session_context:
            session_ctx = {
                "last_solved_problem": request.session_context.last_solved_problem,
                "current_problem": request.session_context.current_problem,
                "last_suggestion": request.session_context.last_suggestion,
                "message": request.message,
            }

        # Check for code in message
        has_code_in_message = "```" in request.message

        # Step 1: Classify intent
        intent_result = await intent_classifier.classify(
            message=request.message,
            session_context=session_ctx
        )

        # Step 2: Check if context is required but missing
        if intent_result.requires_context == "code":
            has_code = (
                has_code_in_message or
                (request.session_context and request.session_context.last_solved_problem)
            )
            if not has_code:
                return IntentChatResponse(
                    message="비슷한 코드 문제를 찾으려면 코드가 필요해요! 🔍\n\n"
                            "1. 방금 푼 문제가 있다면 자동으로 사용할게요\n"
                            "2. 또는 코드를 직접 붙여넣어 주세요\n\n"
                            "```python\n# 여기에 코드를 붙여넣으세요\n```",
                    intent_info=IntentInfo(
                        intent=intent_result.intent.value,
                        confidence=intent_result.confidence,
                        method=intent_result.method,
                        requires_context="code",
                        next_action="request_code_context"
                    ),
                    is_complete=False,
                    action_data={"waiting_for": "code"}
                )

        if intent_result.requires_context == "problem":
            has_problem = request.session_context and request.session_context.current_problem
            if not has_problem:
                return IntentChatResponse(
                    message="현재 풀고 있는 문제가 없어요! 📝\n\n"
                            "먼저 문제를 선택해 주세요. 새 문제를 추천해 드릴까요?",
                    intent_info=IntentInfo(
                        intent=intent_result.intent.value,
                        confidence=intent_result.confidence,
                        method=intent_result.method,
                        requires_context="problem",
                        next_action="request_problem_context"
                    ),
                    is_complete=False,
                    action_data={"waiting_for": "problem", "suggest_new_problem": True}
                )

        # Step 3: Handle intent-specific actions
        response = await _handle_intent(
            intent_result=intent_result,
            request=request,
            db=db
        )

        return response

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Intent chat agent error: {str(e)}"
        )


async def _handle_intent(
    intent_result,
    request: IntentChatRequest,
    db
) -> IntentChatResponse:
    """
    의도별 응답 핸들러

    각 의도에 맞는 LLM 프롬프트와 액션을 실행합니다.
    """
    intent = intent_result.intent
    intent_def = INTENT_DEFINITIONS.get(intent, {})

    # ===== 문제 검색/추천 의도 =====
    if intent == IntentType.NEW_PROBLEM:
        return await _handle_new_problem(request, intent_result, db)

    elif intent == IntentType.SIMILAR_CODE_PROBLEM:
        return await _handle_similar_code_problem(request, intent_result, db)

    elif intent == IntentType.TOPIC_SPECIFIC:
        return await _handle_topic_specific(request, intent_result, db)

    elif intent == IntentType.DIFFICULTY_CHANGE:
        return await _handle_difficulty_change(request, intent_result)

    elif intent == IntentType.LANGUAGE_CHANGE:
        return await _handle_language_change(request, intent_result)

    elif intent == IntentType.RANDOM_RECOMMEND:
        return await _handle_random_recommend(request, intent_result, db)

    # ===== 문제 풀이 중 의도 =====
    elif intent == IntentType.HINT_REQUEST:
        return await _handle_hint_request(request, intent_result)

    elif intent == IntentType.SOLUTION_REQUEST:
        return await _handle_solution_request(request, intent_result)

    elif intent == IntentType.EXPLANATION_REQUEST:
        return await _handle_explanation(request, intent_result, db)

    elif intent == IntentType.CODE_REVIEW:
        return await _handle_code_review(request, intent_result)

    elif intent == IntentType.ERROR_HELP:
        return await _handle_error_help(request, intent_result)

    # ===== 진행 관련 의도 =====
    elif intent == IntentType.SKIP_PROBLEM:
        return _make_simple_response(
            "문제를 건너뛰었어요. 다른 문제를 추천해 드릴까요? 🔄",
            intent_result,
            action_data={"action": "skip", "suggest_new": True}
        )

    elif intent == IntentType.RETRY_PROBLEM:
        return _make_simple_response(
            "코드를 초기화했어요. 처음부터 다시 도전해보세요! 💪",
            intent_result,
            action_data={"action": "reset"}
        )

    elif intent == IntentType.SUBMIT_CODE:
        return _make_simple_response(
            "코드를 제출합니다. 잠시만 기다려주세요... ⏳",
            intent_result,
            action_data={"action": "submit"}
        )

    # ===== 학습/통계 의도 =====
    elif intent == IntentType.PROGRESS_CHECK:
        return _make_simple_response(
            "진행 상황을 확인할게요! 📊",
            intent_result,
            action_data={"action": "show_progress"}
        )

    elif intent == IntentType.WEAK_POINT:
        return _make_simple_response(
            "약점을 분석할게요. 잠시만요... 🔍",
            intent_result,
            action_data={"action": "analyze_weakness"}
        )

    elif intent == IntentType.STUDY_PLAN:
        return _make_simple_response(
            "맞춤 학습 계획을 세워드릴게요! 📅",
            intent_result,
            action_data={"action": "create_study_plan"}
        )

    # ===== 일반 대화 의도 =====
    elif intent == IntentType.GREETING:
        return _make_simple_response(
            "안녕하세요! 코딩 공부 도와드릴게요. 어떤 문제를 풀어볼까요? 💻",
            intent_result
        )

    elif intent == IntentType.THANKS:
        return _make_simple_response(
            "도움이 됐다니 기뻐요! 더 필요한 게 있으면 말씀해주세요. 😊",
            intent_result
        )

    elif intent == IntentType.GOODBYE:
        return _make_simple_response(
            "수고하셨어요! 다음에 또 만나요. 화이팅! 👋",
            intent_result
        )

    elif intent == IntentType.CONFUSION:
        return _make_simple_response(
            "헷갈리시는군요! 제가 도와드릴게요. 어떤 부분이 어려우신가요?\n\n"
            "1. 문제 이해가 어려우면 → 설명 요청\n"
            "2. 풀이 방향을 모르면 → 힌트 요청\n"
            "3. 코드가 안 되면 → 에러 도움 요청",
            intent_result
        )

    elif intent == IntentType.AFFIRMATION:
        return _make_simple_response(
            "좋아요! 진행할게요. 👍",
            intent_result,
            action_data={"action": "confirm_previous"}
        )

    elif intent == IntentType.NEGATION:
        return _make_simple_response(
            "알겠어요! 다른 걸로 해볼까요? 🔄",
            intent_result,
            action_data={"action": "offer_alternatives"}
        )

    elif intent == IntentType.OUT_OF_SCOPE:
        return _make_simple_response(
            "저는 코딩 학습 도우미예요! 🤖\n\n"
            "알고리즘 문제 풀이, 코드 리뷰, 힌트 제공 등을 도와드릴 수 있어요.\n"
            "새로운 문제를 풀어볼까요?",
            intent_result,
            action_data={"redirect": "coding"}
        )

    elif intent == IntentType.CLARIFICATION_NEEDED:
        return _make_simple_response(
            "죄송해요, 요청을 이해하기 어려워요. 😅\n\n"
            "더 구체적으로 말씀해주실 수 있나요?\n"
            "예: \"DP 문제 풀래\" 또는 \"힌트 줘\"",
            intent_result
        )

    # Default fallback
    return await _handle_general_chat(request, intent_result, db)


# ===== Intent Handlers =====

async def _handle_new_problem(request, intent_result, db) -> IntentChatResponse:
    """새 문제 요청 처리 - 정보 수집 시작"""
    return IntentChatResponse(
        message="새로운 문제를 찾아볼게요! 🔍\n\n"
                "어떤 유형의 문제를 풀고 싶으세요?\n"
                "- 알고리즘 (DP, 그래프, 정렬 등)\n"
                "- 난이도 (쉬움/보통/어려움)\n"
                "- 원하는 언어 (Python/Java/C++)\n\n"
                "자유롭게 말씀해 주세요!",
        intent_info=IntentInfo(
            intent=intent_result.intent.value,
            confidence=intent_result.confidence,
            method=intent_result.method,
            next_action="collect_preferences"
        ),
        is_complete=False,
        collected_info=CollectedInfo()
    )


async def _handle_similar_code_problem(request, intent_result, db) -> IntentChatResponse:
    """비슷한 코드 문제 찾기 - RAG 검색"""
    # Extract code from message or session
    code = None
    language = "python"

    # From message
    code_extract = intent_classifier.extract_code_from_message(request.message)
    if code_extract:
        language, code = code_extract

    # From session
    if not code and request.session_context and request.session_context.last_solved_problem:
        code = request.session_context.last_solved_problem.get("code", "")
        language = request.session_context.last_solved_problem.get("language", "python")

    if not code:
        return IntentChatResponse(
            message="코드를 찾을 수 없어요. 코드를 붙여넣어 주세요!",
            intent_info=IntentInfo(
                intent=intent_result.intent.value,
                confidence=intent_result.confidence,
                method=intent_result.method,
                requires_context="code",
                next_action="request_code_context"
            ),
            is_complete=False,
            action_data={"waiting_for": "code"}
        )

    # Perform code-based similarity search
    try:
        results, should_fallback = await rag_service.search_problems_hybrid(
            query=code[:1000],  # Limit code length
            topics=[],
            language=language,
            limit=5
        )

        if results and not should_fallback:
            problem_ids = [r.get("problem_id") for r in results if r.get("problem_id")]
            if problem_ids:
                response = db.table("base_problems")\
                    .select("id, name, difficulty, tags")\
                    .in_("id", problem_ids[:3])\
                    .execute()
                problems = response.data or []

                if problems:
                    problem_list = "\n".join([
                        f"  {i+1}. {p.get('name', 'Unknown')} ({p.get('difficulty', 'medium')})"
                        for i, p in enumerate(problems)
                    ])

                    return IntentChatResponse(
                        message=f"비슷한 코드 패턴의 문제를 찾았어요! 🎯\n\n{problem_list}\n\n"
                                "어떤 문제를 풀어볼까요? 번호로 선택해주세요!",
                        intent_info=IntentInfo(
                            intent=intent_result.intent.value,
                            confidence=intent_result.confidence,
                            method=intent_result.method,
                            next_action="select_problem"
                        ),
                        is_complete=False,
                        action_data={"found_problems": problems}
                    )

        # Fallback: Generate new problem
        return IntentChatResponse(
            message="비슷한 문제를 찾지 못했어요. 😅\n\n"
                    "대신 새로운 문제를 만들어 드릴까요? "
                    "어떤 주제나 난이도를 원하시나요?",
            intent_info=IntentInfo(
                intent=intent_result.intent.value,
                confidence=intent_result.confidence,
                method=intent_result.method,
                next_action="generate_new_problem"
            ),
            is_complete=False,
            action_data={"fallback": True, "original_code": code[:500]}
        )

    except Exception as e:
        return IntentChatResponse(
            message=f"검색 중 오류가 발생했어요: {str(e)}\n다시 시도해주세요.",
            intent_info=IntentInfo(
                intent=intent_result.intent.value,
                confidence=intent_result.confidence,
                method=intent_result.method,
                next_action="retry"
            ),
            is_complete=False
        )


async def _handle_topic_specific(request, intent_result, db) -> IntentChatResponse:
    """특정 주제 문제 요청"""
    # Extract topic from message using LLM
    topic_keywords = {
        "dp": "DP", "동적": "DP", "다이나믹": "DP",
        "그래프": "Graph", "bfs": "BFS", "dfs": "DFS",
        "정렬": "Sorting", "탐색": "Search",
        "투포인터": "Two Pointer", "이분탐색": "Binary Search",
        "스택": "Stack", "큐": "Queue", "해시": "Hash",
        "트리": "Tree", "힙": "Heap",
        "백트래킹": "Backtracking", "그리디": "Greedy",
        "분할정복": "Divide and Conquer",
        "문자열": "String", "구현": "Implementation",
    }

    detected_topic = None
    message_lower = request.message.lower()
    for key, topic in topic_keywords.items():
        if key in message_lower:
            detected_topic = topic
            break

    if detected_topic:
        return IntentChatResponse(
            message=f"{detected_topic} 문제를 찾아볼게요! 🔍\n\n"
                    f"난이도는 어떻게 할까요? (쉬움/보통/어려움)",
            intent_info=IntentInfo(
                intent=intent_result.intent.value,
                confidence=intent_result.confidence,
                method=intent_result.method,
                next_action="set_difficulty"
            ),
            is_complete=False,
            collected_info=CollectedInfo(topics=[detected_topic])
        )

    return IntentChatResponse(
        message="어떤 알고리즘 주제를 연습하고 싶으세요? 🤔\n\n"
                "- DP (동적 프로그래밍)\n"
                "- 그래프 (BFS, DFS)\n"
                "- 정렬/탐색\n"
                "- 자료구조 (스택, 큐, 트리)\n"
                "- 그리디/백트래킹",
        intent_info=IntentInfo(
            intent=intent_result.intent.value,
            confidence=intent_result.confidence,
            method=intent_result.method,
            next_action="select_topic"
        ),
        is_complete=False,
        collected_info=CollectedInfo()
    )


async def _handle_difficulty_change(request, intent_result) -> IntentChatResponse:
    """난이도 변경"""
    message_lower = request.message.lower()
    new_difficulty = None

    if any(kw in message_lower for kw in ["쉬운", "쉽", "초급", "기초"]):
        new_difficulty = "easy"
    elif any(kw in message_lower for kw in ["어려운", "어렵", "고급", "챌린지"]):
        new_difficulty = "hard"
    elif any(kw in message_lower for kw in ["중간", "보통", "적당"]):
        new_difficulty = "medium"

    if new_difficulty:
        difficulty_kr = {"easy": "쉬움", "medium": "보통", "hard": "어려움"}[new_difficulty]
        return IntentChatResponse(
            message=f"난이도를 '{difficulty_kr}'으로 변경했어요! ✅\n\n"
                    "이 난이도로 문제를 찾아볼까요?",
            intent_info=IntentInfo(
                intent=intent_result.intent.value,
                confidence=intent_result.confidence,
                method=intent_result.method,
                next_action="search_with_difficulty"
            ),
            is_complete=False,
            collected_info=CollectedInfo(difficulty=new_difficulty),
            action_data={"difficulty_updated": new_difficulty}
        )

    return IntentChatResponse(
        message="어떤 난이도로 바꿀까요?\n\n"
                "1. 쉬움 (Easy)\n"
                "2. 보통 (Medium)\n"
                "3. 어려움 (Hard)",
        intent_info=IntentInfo(
            intent=intent_result.intent.value,
            confidence=intent_result.confidence,
            method=intent_result.method,
            next_action="select_difficulty"
        ),
        is_complete=False
    )


async def _handle_language_change(request, intent_result) -> IntentChatResponse:
    """언어 변경"""
    message_lower = request.message.lower()
    new_language = None

    if any(kw in message_lower for kw in ["파이썬", "python", "py"]):
        new_language = "python"
    elif any(kw in message_lower for kw in ["자바", "java"]):
        new_language = "java"
    elif any(kw in message_lower for kw in ["c++", "cpp", "씨플플", "씨쁠쁠"]):
        new_language = "cpp"

    if new_language:
        return IntentChatResponse(
            message=f"언어를 {new_language.upper()}로 변경했어요! ✅",
            intent_info=IntentInfo(
                intent=intent_result.intent.value,
                confidence=intent_result.confidence,
                method=intent_result.method,
                next_action="continue"
            ),
            is_complete=False,
            collected_info=CollectedInfo(language=new_language),
            action_data={"language_updated": new_language}
        )

    return IntentChatResponse(
        message="어떤 언어로 바꿀까요?\n\n"
                "1. Python\n"
                "2. Java\n"
                "3. C++",
        intent_info=IntentInfo(
            intent=intent_result.intent.value,
            confidence=intent_result.confidence,
            method=intent_result.method,
            next_action="select_language"
        ),
        is_complete=False
    )


async def _handle_random_recommend(request, intent_result, db) -> IntentChatResponse:
    """아무거나 추천"""
    return IntentChatResponse(
        message="알겠어요! 제가 적당한 문제를 골라볼게요. 🎲\n\n"
                "잠시만 기다려주세요...",
        intent_info=IntentInfo(
            intent=intent_result.intent.value,
            confidence=intent_result.confidence,
            method=intent_result.method,
            next_action="recommend_random"
        ),
        is_complete=True,
        action_data={"action": "random_recommend"}
    )


async def _handle_hint_request(request, intent_result) -> IntentChatResponse:
    """힌트 요청"""
    problem = None
    if request.session_context:
        problem = request.session_context.current_problem

    if problem:
        return IntentChatResponse(
            message="힌트를 드릴게요! 💡\n\n"
                    "(힌트 에이전트에서 상세 힌트 생성 중...)",
            intent_info=IntentInfo(
                intent=intent_result.intent.value,
                confidence=intent_result.confidence,
                method=intent_result.method,
                next_action="generate_hint"
            ),
            is_complete=True,
            action_data={"action": "generate_hint", "problem_id": problem.get("id")}
        )

    return IntentChatResponse(
        message="힌트를 드리려면 현재 문제가 필요해요!\n문제를 먼저 선택해주세요.",
        intent_info=IntentInfo(
            intent=intent_result.intent.value,
            confidence=intent_result.confidence,
            method=intent_result.method,
            requires_context="problem",
            next_action="request_problem_context"
        ),
        is_complete=False
    )


async def _handle_solution_request(request, intent_result) -> IntentChatResponse:
    """정답 요청"""
    return IntentChatResponse(
        message="정말 정답을 볼까요? 🤔\n\n"
                "힌트를 먼저 보는 게 학습에 더 도움이 될 수 있어요!\n\n"
                "1. 네, 정답 보여줘\n"
                "2. 아니, 힌트만 줘",
        intent_info=IntentInfo(
            intent=intent_result.intent.value,
            confidence=intent_result.confidence,
            method=intent_result.method,
            next_action="confirm_solution"
        ),
        is_complete=False,
        action_data={"waiting_for": "confirmation"}
    )


async def _handle_explanation(request, intent_result, db) -> IntentChatResponse:
    """설명 요청"""
    return IntentChatResponse(
        message="어떤 부분을 설명해 드릴까요? 📚\n\n"
                "- 알고리즘 개념\n"
                "- 코드의 특정 부분\n"
                "- 시간/공간 복잡도\n"
                "- 풀이 접근법",
        intent_info=IntentInfo(
            intent=intent_result.intent.value,
            confidence=intent_result.confidence,
            method=intent_result.method,
            next_action="explain_topic"
        ),
        is_complete=False
    )


async def _handle_code_review(request, intent_result) -> IntentChatResponse:
    """코드 리뷰"""
    code = None
    code_extract = intent_classifier.extract_code_from_message(request.message)
    if code_extract:
        _, code = code_extract

    if not code and request.session_context and request.session_context.last_solved_problem:
        code = request.session_context.last_solved_problem.get("code")

    if code:
        return IntentChatResponse(
            message="코드를 리뷰할게요! 잠시만요... 🔍",
            intent_info=IntentInfo(
                intent=intent_result.intent.value,
                confidence=intent_result.confidence,
                method=intent_result.method,
                next_action="review_code"
            ),
            is_complete=True,
            action_data={"action": "code_review", "code": code[:2000]}
        )

    return IntentChatResponse(
        message="리뷰할 코드를 보여주세요!\n\n```python\n# 코드를 여기에 붙여넣어 주세요\n```",
        intent_info=IntentInfo(
            intent=intent_result.intent.value,
            confidence=intent_result.confidence,
            method=intent_result.method,
            requires_context="code",
            next_action="request_code_context"
        ),
        is_complete=False
    )


async def _handle_error_help(request, intent_result) -> IntentChatResponse:
    """에러 도움"""
    return IntentChatResponse(
        message="에러가 났군요! 😰 제가 도와드릴게요.\n\n"
                "어떤 에러가 발생했나요?\n"
                "- 코드와 에러 메시지를 함께 보여주시면 더 정확히 도와드릴 수 있어요!",
        intent_info=IntentInfo(
            intent=intent_result.intent.value,
            confidence=intent_result.confidence,
            method=intent_result.method,
            next_action="debug_code"
        ),
        is_complete=False,
        action_data={"waiting_for": "code_and_error"}
    )


async def _handle_general_chat(request, intent_result, db) -> IntentChatResponse:
    """일반 대화 - LLM으로 자연스러운 응답"""
    try:
        user_context_str = json.dumps(request.user_context or {}, ensure_ascii=False)
        system_prompt = f"""당신은 코딩 학습 도우미입니다. 친근하고 도움이 되는 응답을 해주세요.

사용자 정보:
{user_context_str}

분류된 의도: {intent_result.intent.value} (신뢰도: {intent_result.confidence:.2f})

주의사항:
- 코딩 학습과 관련된 내용으로 대화를 유도하세요
- 응답은 간결하게 (2-3문장)
- 이모지는 적절히 사용"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": request.message}
        ]

        response = await openrouter_service.chat_completion(
            model=settings.llm_model_chat,
            messages=messages,
            temperature=0.7,
            max_tokens=300,
        )
        content = openrouter_service.get_content(response)

        return IntentChatResponse(
            message=content,
            intent_info=IntentInfo(
                intent=intent_result.intent.value,
                confidence=intent_result.confidence,
                method=intent_result.method,
                next_action=intent_result.next_action
            ),
            is_complete=False
        )

    except Exception as e:
        return _make_simple_response(
            "죄송해요, 응답 생성 중 문제가 발생했어요. 다시 말씀해 주시겠어요?",
            intent_result
        )


def _make_simple_response(
    message: str,
    intent_result,
    action_data: dict = None
) -> IntentChatResponse:
    """간단한 응답 생성 헬퍼"""
    return IntentChatResponse(
        message=message,
        intent_info=IntentInfo(
            intent=intent_result.intent.value,
            confidence=intent_result.confidence,
            method=intent_result.method,
            requires_context=intent_result.requires_context,
            next_action=intent_result.next_action
        ),
        is_complete=False,
        action_data=action_data
    )


# ============================================================
# Problem Generation
# ============================================================

@router.post("/generate/blank", response_model=BlankProblemResponse)
async def generate_blank_problem(request: ProblemGenerationRequest, db=Depends(get_db)):
    """
    Generate a blank-fill problem from base problem.

    Uses GPT-4o-mini via OpenRouter.
    """
    try:
        # Format base problem as JSON
        base_problem_json = json.dumps({
            "title": request.base_problem.title,
            "description": request.base_problem.description,
            "code": request.base_problem.code,
            "difficulty": request.base_problem.difficulty.value,
            "topics": request.base_problem.topics,
        }, ensure_ascii=False)

        system_prompt = BLANK_PROBLEM_SYSTEM_PROMPT.format(
            base_problem=base_problem_json,
            user_level=request.user_level.value,
            language=request.language.value,
        )

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
        result = openrouter_service.parse_json_response(content)

        return BlankProblemResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Blank problem generation error: {str(e)}"
        )


@router.post("/generate/puzzle", response_model=PuzzleProblemResponse)
async def generate_puzzle_problem(request: ProblemGenerationRequest, db=Depends(get_db)):
    """
    Generate a puzzle (Parsons) problem from base problem.

    Uses GPT-4o-mini via OpenRouter.
    """
    try:
        base_problem_json = json.dumps({
            "title": request.base_problem.title,
            "description": request.base_problem.description,
            "code": request.base_problem.code,
            "difficulty": request.base_problem.difficulty.value,
            "topics": request.base_problem.topics,
        }, ensure_ascii=False)

        system_prompt = PUZZLE_PROBLEM_SYSTEM_PROMPT.format(
            base_problem=base_problem_json,
            user_level=request.user_level.value,
            language=request.language.value,
        )

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
        result = openrouter_service.parse_json_response(content)

        return PuzzleProblemResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Puzzle problem generation error: {str(e)}"
        )


@router.post("/generate/guided", response_model=GuidedProblemResponse)
async def generate_guided_problem(request: ProblemGenerationRequest, db=Depends(get_db)):
    """
    Generate a guided (1:1 conversational) problem from base problem.

    Uses GPT-4o-mini via OpenRouter.
    """
    try:
        base_problem_json = json.dumps({
            "title": request.base_problem.title,
            "description": request.base_problem.description,
            "code": request.base_problem.code,
            "difficulty": request.base_problem.difficulty.value,
            "topics": request.base_problem.topics,
        }, ensure_ascii=False)

        system_prompt = GUIDED_PROBLEM_SYSTEM_PROMPT.format(
            base_problem=base_problem_json,
            user_level=request.user_level.value,
            language=request.language.value,
        )

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

        return GuidedProblemResponse(**result)

    except Exception as e:
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
