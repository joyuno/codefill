"""
Problem Solving Nodes

문제 풀이 중 힌트, 코드 리뷰, 정답 체크, 피드백 노드
"""
import json
from typing import Dict, Any, List
from ..solving_state import SolvingState


async def provide_hint(state: SolvingState) -> Dict[str, Any]:
    """
    점진적 힌트를 제공합니다.

    힌트 레벨:
    - Level 1: 문제 접근 방향 (어떤 알고리즘/자료구조?)
    - Level 2: 구체적인 알고리즘 힌트
    - Level 3: 의사코드 수준의 힌트
    - Level 4: 핵심 코드 일부 공개
    """
    from ...services.openrouter import openrouter_service

    problem_context = state.get("problem_context", {})
    user_progress = state.get("user_progress", {})
    intent_result = state.get("intent_result", {})
    previous_hints = state.get("previous_hints", [])

    # 힌트 레벨 결정 (이전 힌트 수 + 1)
    hint_level = min(len(previous_hints) + 1, 4)

    # 서브 의도에 따른 힌트 타입 조정
    sub_intent = intent_result.get("sub_intent", "hint_general")

    system_prompt = f"""당신은 코딩 교육 전문가입니다. 학생에게 힌트를 제공합니다.

규칙:
1. 직접적인 정답은 절대 알려주지 마세요
2. 소크라테스식 질문으로 유도하세요
3. 힌트 레벨 {hint_level}에 맞게 제공하세요:
   - Level 1: "이 문제는 어떤 유형일까요?" 수준
   - Level 2: "~~ 알고리즘/자료구조를 생각해보세요" 수준
   - Level 3: "1. 먼저 ~~ 2. 그다음 ~~" 의사코드 수준
   - Level 4: 핵심 부분의 코드 구조 (변수명은 가림)
4. 격려하는 톤을 유지하세요

힌트 타입: {sub_intent}
"""

    problem_info = f"""
문제: {problem_context.get('title', 'Unknown')}
설명: {problem_context.get('description', '')[:500]}
난이도: {problem_context.get('difficulty', 'medium')}
주제: {', '.join(problem_context.get('topics', []))}
문제 유형: {problem_context.get('problem_type', 'unknown')}
"""

    user_info = f"""
현재 코드:
```
{user_progress.get('current_code', '아직 작성 안 함')[:500]}
```
시도 횟수: {user_progress.get('attempt_count', 0)}
이전 힌트들: {previous_hints[-2:] if previous_hints else '없음'}
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"{problem_info}\n\n{user_info}\n\nLevel {hint_level} 힌트를 주세요."},
    ]

    try:
        response = await openrouter_service.chat_completion(
            messages=messages,
            model="gpt-4o-mini",
            temperature=0.7,
        )
        hint_text = openrouter_service.get_content(response)

        # 힌트 기록 업데이트
        updated_hints = previous_hints + [hint_text]

        return {
            "response_message": hint_text,
            "hint_level": hint_level,
            "previous_hints": updated_hints,
            "action_trigger": "hint_provided",
            "action_data": {
                "hint_level": hint_level,
                "hint_type": sub_intent,
                "hints_remaining": 4 - hint_level,
            },
            "next_node": "respond",
        }

    except Exception as e:
        print(f"[Hint] Error: {e}")
        return {
            "response_message": "힌트 생성 중 오류가 발생했어요. 다시 시도해주세요!",
            "next_node": "respond",
        }


async def review_code(state: SolvingState) -> Dict[str, Any]:
    """
    사용자 코드를 리뷰합니다.

    체크 항목:
    - 문법 오류
    - 로직 오류
    - 엣지 케이스 처리
    - 코드 스타일/가독성
    """
    from ...services.openrouter import openrouter_service

    problem_context = state.get("problem_context", {})
    user_progress = state.get("user_progress", {})
    message = state.get("message", "")

    # 메시지에서 코드 추출 또는 user_progress에서 가져오기
    code = _extract_code(message) or user_progress.get("current_code", "")

    if not code:
        return {
            "response_message": "리뷰할 코드가 없어요! 코드를 작성하고 다시 요청해주세요.",
            "next_node": "respond",
        }

    system_prompt = """당신은 친절한 코드 리뷰어입니다. 학생의 코드를 검토합니다.

규칙:
1. 정답을 직접 알려주지 마세요
2. 발견한 문제점을 질문 형태로 제시하세요
3. 잘한 부분은 칭찬하세요
4. 개선 방향을 힌트로 제시하세요

JSON으로 응답:
{
    "overall_feedback": "전체 피드백",
    "good_points": ["잘한 점들"],
    "issues": [{"type": "문제 유형", "description": "설명", "hint": "힌트"}],
    "suggestions": ["개선 제안들"]
}
"""

    problem_info = f"""
문제: {problem_context.get('title', 'Unknown')}
설명: {problem_context.get('description', '')[:300]}
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"{problem_info}\n\n학생 코드:\n```\n{code}\n```"},
    ]

    try:
        response = await openrouter_service.chat_completion(
            messages=messages,
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
        )
        content = openrouter_service.get_content(response)
        review_result = openrouter_service.parse_json_response(content)

        # 응답 메시지 구성
        response_parts = [review_result.get("overall_feedback", "")]

        good_points = review_result.get("good_points", [])
        if good_points:
            response_parts.append("\n**잘한 점:**")
            for point in good_points[:3]:
                response_parts.append(f"  - {point}")

        issues = review_result.get("issues", [])
        if issues:
            response_parts.append("\n**확인해볼 부분:**")
            for issue in issues[:3]:
                response_parts.append(f"  - {issue.get('description', '')}")
                if issue.get('hint'):
                    response_parts.append(f"    힌트: {issue['hint']}")

        response_message = "\n".join(response_parts)

        return {
            "response_message": response_message,
            "code_analysis": review_result,
            "action_trigger": "code_reviewed",
            "action_data": {
                "issues_count": len(issues),
                "has_critical": any(i.get("type") == "critical" for i in issues),
            },
            "next_node": "respond",
        }

    except Exception as e:
        print(f"[CodeReview] Error: {e}")
        return {
            "response_message": "코드 리뷰 중 오류가 발생했어요. 다시 시도해주세요!",
            "next_node": "respond",
        }


async def check_answer(state: SolvingState) -> Dict[str, Any]:
    """
    정답을 체크합니다.

    문제 유형별 체크:
    - blank: 빈칸 답안 비교
    - puzzle: 블록 순서 비교
    - guided: 단계별 완료 확인
    """
    from ...services.openrouter import openrouter_service

    problem_context = state.get("problem_context", {})
    user_progress = state.get("user_progress", {})
    message = state.get("message", "")

    problem_type = problem_context.get("problem_type", "blank")

    # 사용자 답안 추출
    user_answer = _extract_user_answer(message, user_progress, problem_type)

    if not user_answer:
        return {
            "response_message": "제출할 답안이 없어요! 코드를 작성하고 제출해주세요.",
            "next_node": "respond",
        }

    # 정답 비교 (문제 유형별)
    # 문자열(코드)인 경우 코드 체크로 처리
    if isinstance(user_answer, str):
        is_correct, feedback = await _check_code_answer(
            user_answer, problem_context, openrouter_service
        )
    elif problem_type == "blank" and isinstance(user_answer, dict):
        is_correct, feedback = await _check_blank_answer(
            user_answer, problem_context, openrouter_service
        )
    elif problem_type == "puzzle" and isinstance(user_answer, list):
        is_correct, feedback = _check_puzzle_answer(
            user_answer, problem_context
        )
    elif problem_type == "guided":
        is_correct, feedback = await _check_guided_answer(
            user_answer, problem_context, openrouter_service
        )
    else:
        is_correct, feedback = await _check_code_answer(
            str(user_answer), problem_context, openrouter_service
        )

    # 결과 메시지
    if is_correct:
        response_message = f"정답이에요! {feedback}"
        action_trigger = "correct_answer"
    else:
        response_message = f"아쉽지만 틀렸어요. {feedback}"
        action_trigger = "wrong_answer"

    return {
        "response_message": response_message,
        "is_correct": is_correct,
        "action_trigger": action_trigger,
        "action_data": {
            "is_correct": is_correct,
            "attempt_count": user_progress.get("attempt_count", 0) + 1,
        },
        "next_node": "respond",
    }


async def provide_feedback(state: SolvingState) -> Dict[str, Any]:
    """
    종합 피드백을 제공합니다.

    포함 내용:
    - 문제 풀이 과정 평가
    - 강점/약점 분석
    - 개선 제안
    - 다음 학습 추천
    """
    from ...services.openrouter import openrouter_service

    problem_context = state.get("problem_context", {})
    user_progress = state.get("user_progress", {})
    previous_hints = state.get("previous_hints", [])
    is_correct = state.get("is_correct")

    system_prompt = """당신은 코딩 교육 전문가입니다. 학생의 문제 풀이에 대한 종합 피드백을 제공합니다.

규칙:
1. 구체적이고 건설적인 피드백을 주세요
2. 잘한 점은 반드시 언급하세요
3. 개선점은 학습 방향과 함께 제시하세요
4. 격려하는 톤을 유지하세요

JSON으로 응답:
{
    "summary": "한줄 요약",
    "strengths": ["강점들"],
    "improvements": ["개선점들"],
    "learning_tips": ["학습 팁들"],
    "next_recommendation": "다음 추천 문제/주제"
}
"""

    context = f"""
문제: {problem_context.get('title', 'Unknown')}
난이도: {problem_context.get('difficulty', 'medium')}
주제: {', '.join(problem_context.get('topics', []))}

학생 코드:
```
{user_progress.get('current_code', '없음')[:800]}
```

시도 횟수: {user_progress.get('attempt_count', 0)}
힌트 사용: {len(previous_hints)}회
정답 여부: {'맞음' if is_correct else '틀림' if is_correct is False else '미제출'}
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": context},
    ]

    try:
        response = await openrouter_service.chat_completion(
            messages=messages,
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
        )
        content = openrouter_service.get_content(response)
        feedback = openrouter_service.parse_json_response(content)

        # 응답 메시지 구성
        parts = [f"**{feedback.get('summary', '수고하셨어요!')}**\n"]

        strengths = feedback.get("strengths", [])
        if strengths:
            parts.append("**잘한 점:**")
            for s in strengths[:3]:
                parts.append(f"  - {s}")

        improvements = feedback.get("improvements", [])
        if improvements:
            parts.append("\n**개선할 점:**")
            for i in improvements[:3]:
                parts.append(f"  - {i}")

        tips = feedback.get("learning_tips", [])
        if tips:
            parts.append("\n**학습 팁:**")
            for t in tips[:2]:
                parts.append(f"  - {t}")

        if feedback.get("next_recommendation"):
            parts.append(f"\n**다음 추천:** {feedback['next_recommendation']}")

        response_message = "\n".join(parts)

        return {
            "response_message": response_message,
            "action_trigger": "feedback_provided",
            "action_data": feedback,
            "next_node": "respond",
        }

    except Exception as e:
        print(f"[Feedback] Error: {e}")
        return {
            "response_message": "피드백 생성 중 오류가 발생했어요. 다시 시도해주세요!",
            "next_node": "respond",
        }


async def show_solution(state: SolvingState) -> Dict[str, Any]:
    """
    정답을 보여줍니다 (포기 시).
    """
    problem_context = state.get("problem_context", {})

    solution_code = problem_context.get("solution_code", "")

    if solution_code:
        response_message = f"""포기하셨군요. 다음에 다시 도전해봐요!

**정답 코드:**
```
{solution_code}
```

**설명:** 이 문제의 핵심은 {', '.join(problem_context.get('topics', ['알고리즘']))}입니다.
"""
    else:
        response_message = "정답 코드를 불러올 수 없어요. 다른 문제를 풀어볼까요?"

    return {
        "response_message": response_message,
        "action_trigger": "solution_shown",
        "action_data": {
            "solution_shown": True,
            "problem_id": problem_context.get("id"),
        },
        "next_node": "respond",
    }


async def summarize_problem(state: SolvingState) -> Dict[str, Any]:
    """
    문제를 요약해서 보여줍니다.

    문제의 description/question을 간단히 요약하여 제공
    """
    from ...services.openrouter import openrouter_service

    problem_context = state.get("problem_context", {})

    # 문제 정보 추출
    title = problem_context.get("title") or problem_context.get("name", "문제")
    description = problem_context.get("description") or problem_context.get("question", "")
    topics = problem_context.get("topics", [])
    difficulty = problem_context.get("difficulty", "medium")
    problem_type = problem_context.get("problem_type", "unknown")

    if not description:
        return {
            "response_message": "문제 설명을 찾을 수 없어요.",
            "next_node": "respond",
        }

    system_prompt = """당신은 문제 요약 전문가입니다. 주어진 코딩 문제를 학생이 이해하기 쉽게 요약합니다.

규칙:
1. 핵심 목표를 명확히 제시하세요
2. 입력과 출력이 무엇인지 간단히 설명하세요
3. 핵심 알고리즘/자료구조 힌트는 포함하지 마세요 (학생이 스스로 생각하게)
4. 2-3문장으로 간결하게 요약하세요

출력 형식:
**문제 요약:** [요약 내용]

**핵심 목표:** [한 줄로 정리]
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"문제: {title}\n\n설명:\n{description[:1500]}"},
    ]

    try:
        response = await openrouter_service.chat_completion(
            messages=messages,
            model="gpt-4o-mini",
            temperature=0.3,
        )
        summary = openrouter_service.get_content(response)

        # 추가 정보 포함
        meta_info = f"\n\n**주제:** {', '.join(topics) if topics else '알고리즘'}\n**난이도:** {difficulty}"

        return {
            "response_message": summary + meta_info,
            "action_trigger": "problem_summarized",
            "action_data": {
                "title": title,
                "topics": topics,
                "difficulty": difficulty,
            },
            "next_node": "respond",
        }

    except Exception as e:
        print(f"[SummarizeProblem] Error: {e}")
        # 폴백: 원본 description 일부 표시
        short_desc = description[:500] + "..." if len(description) > 500 else description
        return {
            "response_message": f"**{title}**\n\n{short_desc}",
            "next_node": "respond",
        }


async def answer_question(state: SolvingState) -> Dict[str, Any]:
    """
    일반 질문에 답변합니다.
    """
    from ...services.openrouter import openrouter_service

    message = state.get("message", "")
    problem_context = state.get("problem_context", {})
    conversation_history = state.get("conversation_history", [])

    system_prompt = f"""당신은 코딩 학습 도우미입니다.
현재 학생이 "{problem_context.get('title', '문제')}"를 풀고 있습니다.

규칙:
1. 직접적인 정답은 알려주지 마세요
2. 질문에 친절하게 답변하세요
3. 필요하면 힌트를 요청하도록 안내하세요
"""

    messages = [{"role": "system", "content": system_prompt}]
    for msg in conversation_history[-4:]:
        messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})
    messages.append({"role": "user", "content": message})

    try:
        response = await openrouter_service.chat_completion(
            messages=messages,
            model="gpt-4o-mini",
        )
        response_message = openrouter_service.get_content(response)

        return {
            "response_message": response_message,
            "next_node": "respond",
        }

    except Exception as e:
        print(f"[AnswerQuestion] Error: {e}")
        return {
            "response_message": "답변 생성 중 오류가 발생했어요. 다시 질문해주세요!",
            "next_node": "respond",
        }


# ===== Helper Functions =====

def _extract_code(message: str) -> str:
    """메시지에서 코드 블록 추출"""
    import re
    code_match = re.search(r'```(?:\w+)?\n?(.*?)```', message, re.DOTALL)
    if code_match:
        return code_match.group(1).strip()
    return ""


def _extract_user_answer(message: str, user_progress: dict, problem_type: str):
    """사용자 답안 추출"""
    # 메시지에 코드가 있으면 우선 사용
    code_in_message = _extract_code(message)
    if code_in_message:
        return code_in_message

    # 없으면 problem_type별로 user_progress에서 추출
    if problem_type == "blank":
        blanks = user_progress.get("filled_blanks", {})
        if blanks:
            return blanks
        # 빈칸 정보가 없으면 current_code 사용
        return user_progress.get("current_code", "")
    elif problem_type == "puzzle":
        return user_progress.get("arranged_blocks", [])
    else:
        return user_progress.get("current_code", "")


async def _check_blank_answer(user_answer: dict, problem_context: dict, openrouter) -> tuple:
    """빈칸 채우기 정답 체크"""
    blanks = problem_context.get("blanks", [])

    if not blanks:
        return False, "문제 데이터를 불러올 수 없어요."

    correct_count = 0
    total = len(blanks)

    for blank in blanks:
        blank_id = blank.get("id")
        expected = blank.get("answer", "")
        user_val = user_answer.get(blank_id, "")

        # 공백 제거 후 비교
        if user_val.strip() == expected.strip():
            correct_count += 1

    is_correct = correct_count == total

    if is_correct:
        feedback = "모든 빈칸을 정확히 채웠어요!"
    else:
        feedback = f"{total}개 중 {correct_count}개 맞았어요. 다시 확인해보세요!"

    return is_correct, feedback


def _check_puzzle_answer(user_answer: list, problem_context: dict) -> tuple:
    """퍼즐 정답 체크"""
    expected_order = problem_context.get("correct_order", [])

    if not expected_order:
        return False, "문제 데이터를 불러올 수 없어요."

    is_correct = user_answer == expected_order

    if is_correct:
        feedback = "블록 순서가 정확해요!"
    else:
        feedback = "블록 순서가 맞지 않아요. 다시 배치해보세요!"

    return is_correct, feedback


async def _check_guided_answer(user_answer: str, problem_context: dict, openrouter) -> tuple:
    """대화형 문제 정답 체크"""
    # LLM으로 코드 정확성 평가
    return await _check_code_answer(user_answer, problem_context, openrouter)


async def _check_code_answer(user_code: str, problem_context: dict, openrouter) -> tuple:
    """일반 코드 정답 체크 (LLM 기반)"""
    system_prompt = """코드가 문제의 정답인지 평가하세요.

JSON으로 응답:
{
    "is_correct": true/false,
    "feedback": "피드백 메시지"
}
"""

    problem_info = f"""
문제: {problem_context.get('title', '')}
설명: {problem_context.get('description', '')[:500]}
예상 정답: {problem_context.get('solution_code', '')[:300]}

학생 코드:
{user_code[:500]}
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": problem_info},
    ]

    try:
        response = await openrouter.chat_completion(
            messages=messages,
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
        )
        content = openrouter.get_content(response)
        result = openrouter.parse_json_response(content)

        return result.get("is_correct", False), result.get("feedback", "")

    except Exception:
        return False, "코드 평가 중 오류가 발생했어요."
