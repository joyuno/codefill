"""
Agentic RAG Nodes for Guided Tutor

노드 구성:
1. retrieve_context: 관련 개념/문서 검색
2. grade_context: 검색 결과 관련성 평가
3. assess_understanding: 학생 이해도 평가
4. decide_action: 튜터 행동 결정
5. generate_response: 튜터 응답 생성
"""

from typing import Dict, Any, List
import json

from .state import (
    AgenticRAGState,
    TUTOR_ACTION_PROMPTS,
    UNDERSTANDING_TO_ACTION,
)


async def retrieve_context_node(state: AgenticRAGState) -> Dict[str, Any]:
    """
    문제 관련 컨텍스트 검색 (RAG)

    - 학생의 마지막 메시지 분석
    - 관련 개념/예제 검색
    """
    from ...services.rag import rag_service

    messages = state.get("messages", [])
    problem_context = state.get("problem_context", {})

    if not messages:
        return {"retrieved_docs": [], "retrieval_grade": "pending"}

    # 마지막 사용자 메시지
    last_message = ""
    for msg in reversed(messages):
        if msg.get("role") == "user" or msg.get("type") == "human":
            last_message = msg.get("content", "")
            break

    if not last_message:
        return {"retrieved_docs": [], "retrieval_grade": "pending"}

    # 검색 쿼리 구성
    topics = problem_context.get("topics", [])
    query = f"{last_message} {' '.join(topics)}"

    try:
        # RAG 검색 (개념/문서 검색)
        docs = await rag_service.search_concepts(
            query=query,
            topics=topics,
            limit=3,
        )

        retrieved_docs = [
            {
                "content": doc.get("content", ""),
                "metadata": doc.get("metadata", {}),
                "relevance_score": doc.get("similarity", 0.5),
            }
            for doc in docs
        ]

        return {
            "search_query": query,
            "retrieved_docs": retrieved_docs,
            "retrieval_grade": "pending",
        }

    except Exception as e:
        print(f"[GuidedTutor:Retrieve] Error: {e}")
        return {"retrieved_docs": [], "retrieval_grade": "not_relevant"}


async def grade_context_node(state: AgenticRAGState) -> Dict[str, Any]:
    """
    검색 결과 관련성 평가

    - 검색된 문서가 학생 질문에 관련 있는지 판단
    - 관련 없으면 다른 전략 사용
    """
    from ...services.openrouter import openrouter_service

    retrieved_docs = state.get("retrieved_docs", [])
    messages = state.get("messages", [])

    if not retrieved_docs:
        return {"retrieval_grade": "not_relevant"}

    # 마지막 사용자 메시지
    last_message = ""
    for msg in reversed(messages):
        if msg.get("role") == "user" or msg.get("type") == "human":
            last_message = msg.get("content", "")
            break

    # 문서 내용 요약
    docs_summary = "\n".join([d.get("content", "")[:200] for d in retrieved_docs[:2]])

    # LLM으로 관련성 평가
    grade_prompt = f"""
학생 질문: {last_message}

검색된 문서:
{docs_summary}

이 문서가 학생 질문에 관련이 있나요?
"relevant" 또는 "not_relevant" 중 하나만 답해주세요.
"""

    try:
        response = await openrouter_service.chat_completion(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a relevance grader. Answer only 'relevant' or 'not_relevant'."},
                {"role": "user", "content": grade_prompt},
            ],
            temperature=0,
        )

        content = openrouter_service.get_content(response)
        grade = "relevant" if "relevant" in content.lower() and "not" not in content.lower() else "not_relevant"

        return {"retrieval_grade": grade}

    except Exception as e:
        print(f"[GuidedTutor:Grade] Error: {e}")
        # 에러 시 평균 점수로 판단
        avg_score = sum(d.get("relevance_score", 0.5) for d in retrieved_docs) / len(retrieved_docs)
        return {"retrieval_grade": "relevant" if avg_score > 0.5 else "not_relevant"}


async def assess_understanding_node(state: AgenticRAGState) -> Dict[str, Any]:
    """
    학생 이해도 평가

    - 대화 히스토리 분석
    - 이해한 개념 / 어려워하는 개념 파악
    - 이해도 점수 산출
    """
    from ...services.openrouter import openrouter_service

    messages = state.get("messages", [])
    problem_context = state.get("problem_context", {})
    solution_code = state.get("solution_code", "")
    key_concepts = state.get("key_concepts", [])
    current_progress = state.get("student_progress", {})

    # 최근 대화만 분석 (최대 10개)
    recent_messages = messages[-10:] if len(messages) > 10 else messages
    conversation = "\n".join([
        f"{m.get('role', 'user')}: {m.get('content', '')}"
        for m in recent_messages
    ])

    assess_prompt = f"""
당신은 코딩 튜터입니다. 학생의 이해도를 평가해주세요.

=== 문제 정보 ===
제목: {problem_context.get('title', '')}
설명: {problem_context.get('description', '')[:300]}
핵심 개념: {', '.join(key_concepts)}

=== 정답 코드 (참고용) ===
{solution_code[:500]}

=== 최근 대화 ===
{conversation}

다음을 JSON으로 응답해주세요:
{{
    "understanding_score": 0.0~1.0 사이 숫자,
    "concepts_mastered": ["이해한 개념1", "이해한 개념2"],
    "concepts_struggling": ["어려워하는 개념1"],
    "current_focus": "현재 집중해야 할 개념"
}}
"""

    try:
        response = await openrouter_service.chat_completion(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an educational assessment expert. Respond only in JSON."},
                {"role": "user", "content": assess_prompt},
            ],
            temperature=0.3,
            response_format={"type": "json_object"},
        )

        content = openrouter_service.get_content(response)
        result = json.loads(content)

        new_progress = {
            "understanding_score": float(result.get("understanding_score", 0.5)),
            "concepts_mastered": result.get("concepts_mastered", []),
            "concepts_struggling": result.get("concepts_struggling", []),
            "current_focus": result.get("current_focus", key_concepts[0] if key_concepts else ""),
            "hints_received": current_progress.get("hints_received", 0),
            "attempts": current_progress.get("attempts", 0) + 1,
        }

        return {"student_progress": new_progress}

    except Exception as e:
        print(f"[GuidedTutor:Assess] Error: {e}")
        # 에러 시 기본값 유지
        return {
            "student_progress": {
                **current_progress,
                "understanding_score": current_progress.get("understanding_score", 0.5),
            }
        }


async def decide_action_node(state: AgenticRAGState) -> Dict[str, Any]:
    """
    튜터 행동 결정

    이해도와 상황에 따라 최적의 행동 선택:
    - explain: 개념 설명
    - ask_question: 이해 확인 질문
    - give_hint: 힌트 제공
    - give_example: 예제 제공
    - guide_code: 코드 작성 유도
    - celebrate: 정답 축하
    - encourage: 격려
    """
    student_progress = state.get("student_progress", {})
    understanding = student_progress.get("understanding_score", 0.5)
    struggling = student_progress.get("concepts_struggling", [])
    retrieval_grade = state.get("retrieval_grade", "pending")

    # 이해도에 따른 기본 행동
    action = "explain"  # 기본값
    for (low, high), act in UNDERSTANDING_TO_ACTION.items():
        if low <= understanding < high:
            action = act
            break

    # 어려워하는 개념이 있으면 힌트/설명 우선
    if struggling and understanding < 0.7:
        action = "give_hint" if understanding > 0.4 else "explain"

    # RAG 결과가 관련 없으면 예제 제공
    if retrieval_grade == "not_relevant" and understanding < 0.6:
        action = "give_example"

    # 거의 다 이해했으면 코드 유도
    if understanding >= 0.7 and understanding < 0.9:
        action = "guide_code"

    # 완전 이해하면 축하
    if understanding >= 0.9:
        action = "celebrate"

    return {"tutor_action": action}


async def generate_response_node(state: AgenticRAGState) -> Dict[str, Any]:
    """
    튜터 응답 생성 (2줄 이내)

    소크라테스식 질문법:
    - 직접 정답을 알려주지 않음
    - 학생이 스스로 발견하도록 유도
    """
    from ...services.openrouter import openrouter_service

    tutor_action = state.get("tutor_action", "explain")
    problem_context = state.get("problem_context", {})
    solution_code = state.get("solution_code", "")
    student_progress = state.get("student_progress", {})
    current_focus = student_progress.get("current_focus", "")
    retrieved_docs = state.get("retrieved_docs", [])
    messages = state.get("messages", [])

    # 최근 대화
    recent_messages = messages[-6:] if len(messages) > 6 else messages

    # 관련 문서 내용
    docs_context = "\n".join([d.get("content", "")[:150] for d in retrieved_docs[:2]])

    action_instruction = TUTOR_ACTION_PROMPTS.get(tutor_action, "도움을 주세요.")

    system_prompt = f"""
당신은 소크라테스식 코딩 튜터입니다.

=== 핵심 원칙 ===
1. 절대 정답 코드를 직접 보여주지 마세요
2. 학생이 스스로 발견하도록 질문으로 유도하세요
3. 응답은 반드시 2줄 이내로 해주세요
4. 한국어로 친근하게 대화하세요

=== 문제 정보 ===
제목: {problem_context.get('title', '')}
설명: {problem_context.get('description', '')[:200]}
핵심 개념: {', '.join(problem_context.get('topics', []))}

=== 정답 코드 (학생에게 보여주지 마세요!) ===
{solution_code[:300]}

=== 현재 집중 개념 ===
{current_focus}

=== 관련 참고 자료 ===
{docs_context}

=== 행동 지시 ===
{action_instruction}
"""

    try:
        # 대화 히스토리 구성
        chat_messages = [{"role": "system", "content": system_prompt}]
        for msg in recent_messages:
            role = msg.get("role", "user")
            if role == "human":
                role = "user"
            elif role == "ai":
                role = "assistant"
            chat_messages.append({"role": role, "content": msg.get("content", "")})

        response = await openrouter_service.chat_completion(
            model="gpt-4o-mini",
            messages=chat_messages,
            temperature=0.7,
        )

        content = openrouter_service.get_content(response)

        # 완료 여부 판단
        understanding = student_progress.get("understanding_score", 0.5)
        is_complete = understanding >= 0.9 and tutor_action == "celebrate"

        return {
            "response": content,
            "is_complete": is_complete,
            "suggested_next_step": "다음 문제로" if is_complete else None,
        }

    except Exception as e:
        print(f"[GuidedTutor:Generate] Error: {e}")
        return {
            "response": "죄송해요, 잠시 문제가 있었어요. 다시 질문해주세요!",
            "is_complete": False,
        }


# ============================================================
# Routing Helpers
# ============================================================

def should_retrieve(state: AgenticRAGState) -> bool:
    """RAG 검색이 필요한지 판단"""
    messages = state.get("messages", [])
    return len(messages) > 0


def route_after_grade(state: AgenticRAGState) -> str:
    """검색 결과 평가 후 라우팅"""
    grade = state.get("retrieval_grade", "pending")
    if grade == "relevant":
        return "assess_understanding"
    else:
        # 관련 없어도 이해도 평가는 진행
        return "assess_understanding"
