"""
Handle Question Node

사용자가 질문을 할 때 LLM으로 답변 생성
답변 후 현재 단계의 질문으로 돌아감
"""
from typing import Dict, Any
from ..state import CollectionState


# 질문 유형별 프롬프트
QUESTION_PROMPTS = {
    "recommendation": """
사용자가 주제/난이도/언어 추천을 요청했습니다.

현재 수집 단계: {current_step}
수집된 정보:
- 주제: {topic}
- 난이도: {difficulty}
- 언어: {language}

사용자 메시지: "{message}"

친절하게 추천해주고, 현재 단계({current_step})에 맞는 선택을 유도하세요.
2-3문장으로 간결하게 답변하세요.

현재 단계별 유도:
- topic: 알고리즘 주제 선택 유도 (기초, DP, 그래프, 정렬, 구현 등)
- difficulty: 난이도 선택 유도 (쉬움, 중간, 어려움)
- language: 언어 선택 유도 (Python, Java, C++)
""",
    "explanation": """
사용자가 알고리즘/용어에 대한 설명을 요청했습니다.

현재 수집 단계: {current_step}
수집된 정보:
- 주제: {topic}
- 난이도: {difficulty}
- 언어: {language}

사용자 메시지: "{message}"

간단하게 설명해주고, 현재 단계({current_step})의 선택으로 유도하세요.
3-4문장으로 답변하세요.
""",
    "comparison": """
사용자가 비교/차이점을 물어봤습니다.

현재 수집 단계: {current_step}
수집된 정보:
- 주제: {topic}
- 난이도: {difficulty}
- 언어: {language}

사용자 메시지: "{message}"

간단히 비교해주고, 현재 단계({current_step})의 선택으로 유도하세요.
3-4문장으로 답변하세요.
""",
    "general": """
사용자가 질문을 했습니다.

현재 수집 단계: {current_step}
수집된 정보:
- 주제: {topic}
- 난이도: {difficulty}
- 언어: {language}

사용자 메시지: "{message}"

친절하게 답변하고, 현재 단계({current_step})의 선택으로 유도하세요.
2-3문장으로 간결하게 답변하세요.
""",
}

# 현재 단계별 선택 유도 메시지
STEP_GUIDANCE = {
    "topic": "\n\n어떤 알고리즘 주제로 해볼까요?",
    "difficulty": "\n\n난이도는 어떻게 할까요? (쉬움/중간/어려움)",
    "language": "\n\n어떤 언어로 풀어볼까요? (Python/Java/C++)",
}


async def handle_question(state: CollectionState) -> Dict[str, Any]:
    """
    질문에 대한 답변 생성

    LLM을 사용하여 친절한 답변 생성 후
    현재 단계의 질문으로 유도
    """
    # Import inside function to avoid circular imports
    from app.services.openrouter import openrouter_service

    question_type = state.get("question_type", "general")
    current_step = state.get("current_step", "topic")
    message = state.get("message", "")

    # 프롬프트 선택 및 포맷팅
    prompt_template = QUESTION_PROMPTS.get(question_type, QUESTION_PROMPTS["general"])
    prompt = prompt_template.format(
        current_step=current_step,
        topic=state.get("topic") or "미선택",
        difficulty=state.get("difficulty") or "미선택",
        language=state.get("language") or "미선택",
        message=message,
    )

    try:
        # LLM 호출
        response = await openrouter_service.chat_completion(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "당신은 CodeFill의 친근한 코딩 학습 도우미입니다. 간결하고 친근하게 답변하세요. 이모지는 적절히 사용하세요.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=300,
        )

        answer = openrouter_service.get_content(response)

        # 현재 단계 유도 메시지 추가 (이미 포함되어 있지 않으면)
        if current_step in STEP_GUIDANCE:
            # 이미 선택 유도가 있는지 확인
            has_guidance = any(
                keyword in answer
                for keyword in ["어떤", "할까요", "선택", "골라"]
            )
            if not has_guidance:
                answer += STEP_GUIDANCE[current_step]

        return {
            "response_message": answer,
            "is_question": False,  # 질문 처리 완료
        }

    except Exception as e:
        # LLM 호출 실패 시 기본 메시지
        print(f"[handle_question] LLM error: {e}")

        fallback_messages = {
            "topic": "알고리즘 주제를 선택해주세요! 기초, DP, 그래프, 정렬 등 다양한 주제가 있어요.",
            "difficulty": "난이도를 선택해주세요! 쉬움, 중간, 어려움 중에서 고르세요.",
            "language": "프로그래밍 언어를 선택해주세요! Python, Java, C++ 중에서 고르세요.",
        }

        return {
            "response_message": fallback_messages.get(
                current_step, "어떤 것으로 할지 선택해주세요!"
            ),
            "is_question": False,
        }
