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
from ...prompts import (
    GUIDED_INITIAL_PROMPT,
    GUIDED_TUTOR_SYSTEM_PROMPT,
    STUDENT_STATUS,
    GUIDANCE_LEVEL,
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
                {"role": "system", "content": "Relevance grader. Answer 'relevant' or 'not_relevant'."},
                {"role": "user", "content": grade_prompt},
            ],
            temperature=0,
            max_tokens=20,  # 단순 분류용
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
                {"role": "system", "content": "Educational assessment expert. JSON only."},
                {"role": "user", "content": assess_prompt},
            ],
            temperature=0.3,
            max_tokens=300,  # 평가 결과용
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
    튜터 응답 생성

    1대1 대화형 튜터링:
    - 빈칸/퍼즐보다 더 구체적인 가이드 제공
    - 코드 일부 제공 가능 (전체 정답은 X)
    - 변수명/함수명 직접 추천
    """
    from ...services.openrouter import openrouter_service

    tutor_action = state.get("tutor_action", "explain")
    problem_context = state.get("problem_context", {})
    solution_code = state.get("solution_code", "")
    student_progress = state.get("student_progress", {})
    current_focus = student_progress.get("current_focus", "")
    retrieved_docs = state.get("retrieved_docs", [])
    messages = state.get("messages", [])
    current_student_code = state.get("current_student_code", "")

    # 최근 대화
    recent_messages = messages[-6:] if len(messages) > 6 else messages

    # 대화 히스토리 포맷
    conversation_history = "\n".join([
        f"{'학생' if m.get('role') in ['user', 'human'] else '튜터'}: {m.get('content', '')}"
        for m in recent_messages
    ])

    # 관련 문서 내용
    docs_context = "\n".join([d.get("content", "")[:150] for d in retrieved_docs[:2]])

    # 학습 구조 정보 (problems_guided 테이블에서)
    concepts = problem_context.get("concepts", [])
    flow = problem_context.get("flow", [])
    checkpoints = problem_context.get("checkpoints", [])

    # 현재 단계 (checkpoint 기반)
    completed_checkpoints = student_progress.get("concepts_mastered", [])
    current_step = len(completed_checkpoints) + 1
    total_steps = len(checkpoints) if checkpoints else len(flow) if flow else 3

    # 학생 상태 판단
    understanding = student_progress.get("understanding_score", 0.5)
    if understanding < 0.3:
        student_status = "starting"
    elif understanding < 0.5:
        student_status = "coding"
    elif understanding < 0.7:
        student_status = "stuck"
    elif understanding < 0.9:
        student_status = "almost_done"
    else:
        student_status = "completed"

    # GUIDED_TUTOR_SYSTEM_PROMPT 사용
    system_prompt = GUIDED_TUTOR_SYSTEM_PROMPT.format(
        title=problem_context.get('title', ''),
        description=problem_context.get('description', '')[:500],
        difficulty=problem_context.get('difficulty', 'medium'),
        language=problem_context.get('language', 'python'),
        topics=', '.join(problem_context.get('topics', [])),
        concepts=json.dumps(concepts, ensure_ascii=False, indent=2) if concepts else "[]",
        flow=json.dumps(flow, ensure_ascii=False, indent=2) if flow else "[]",
        checkpoints=json.dumps(checkpoints, ensure_ascii=False, indent=2) if checkpoints else "[]",
        solution_code=solution_code[:800],
        current_step=current_step,
        total_steps=total_steps,
        user_code=current_student_code or "# 아직 작성된 코드 없음",
        conversation_history=conversation_history or "대화 시작",
    )

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
            max_tokens=1000,  # 대화 응답용
            frequency_penalty=0.3,  # 반복 방지
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


# ============================================================
# Initial Guide Node (문제 시작 시 개념 + 변수 설계 안내)
# ============================================================

async def generate_initial_guide_node(state: AgenticRAGState) -> Dict[str, Any]:
    """
    초기 가이드 생성 (문제 시작 시)

    1대1 대화형의 핵심 기능:
    - 개념 정의 설명
    - 변수 설계 가이드 (개수, 타입, 초기값, 역할)
    - 학습 흐름 안내
    - 첫 번째 단계 유도

    주의: orchestrator_v2에서 이미 concept_explanation/approach_guide가 생성된 경우
          중복 LLM 호출을 방지하기 위해 기존 데이터를 재사용합니다.
    """
    from ...services.openrouter import openrouter_service

    problem_context = state.get("problem_context", {})
    solution_code = state.get("solution_code", "")

    # 학습 구조 정보 (problems_guided 테이블에서)
    concepts = problem_context.get("concepts", [])
    flow = problem_context.get("flow", [])
    checkpoints = problem_context.get("checkpoints", [])

    # ============================================================
    # 중복 호출 방지: 이미 생성된 데이터가 있으면 LLM 호출 스킵
    # ============================================================
    concept_explanation = problem_context.get("concept_explanation", "")
    approach_guide = problem_context.get("approach_guide", "")
    variables_guide = problem_context.get("variables_guide", {})

    if concept_explanation and approach_guide:
        # 이미 orchestrator에서 생성된 데이터가 있음 - LLM 호출 스킵
        # 기존 데이터로 초기 가이드 메시지 구성
        title = problem_context.get('title', '문제')
        topics = problem_context.get('topics', [])

        # variables_guide 포맷팅
        variables_text = ""
        if variables_guide:
            if isinstance(variables_guide, dict):
                var_items = []
                for var_name, var_info in variables_guide.items():
                    if isinstance(var_info, dict):
                        var_items.append(f"- `{var_name}`: {var_info.get('purpose', var_info.get('description', ''))}")
                    else:
                        var_items.append(f"- `{var_name}`: {var_info}")
                if var_items:
                    variables_text = "\n\n**📦 사용할 변수들:**\n" + "\n".join(var_items)

        message = (
            f"**{title}** 문제를 함께 풀어볼게요! 🎯\n\n"
            f"**💡 핵심 개념:**\n{concept_explanation}\n\n"
            f"**🛠️ 문제 접근법:**\n{approach_guide}"
            f"{variables_text}\n\n"
            "준비되셨나요? 먼저 무엇부터 시작해볼까요?"
        )

        return {
            "response": message,
            "initial_guide": {
                "message": message,
                "concept_explanation": concept_explanation,
                "approach_guide": approach_guide,
                "variables_guide": variables_guide,
            },
            "is_initial_guide": True,
            "student_progress": {
                "understanding_score": 0.1,
                "concepts_mastered": [],
                "concepts_struggling": [],
                "current_focus": flow[0] if flow else (concepts[0] if concepts else (topics[0] if topics else "")),
                "hints_received": 0,
                "attempts": 0,
            },
        }

    # ============================================================
    # 기존 로직: 데이터가 없으면 LLM으로 새로 생성
    # ============================================================
    # GUIDED_INITIAL_PROMPT 사용
    system_prompt = GUIDED_INITIAL_PROMPT.format(
        title=problem_context.get('title', ''),
        description=problem_context.get('description', '')[:500],
        difficulty=problem_context.get('difficulty', 'medium'),
        language=problem_context.get('language', 'python'),
        topics=', '.join(problem_context.get('topics', [])),
        concepts=json.dumps(concepts, ensure_ascii=False, indent=2) if concepts else "[]",
        flow=json.dumps(flow, ensure_ascii=False, indent=2) if flow else "[]",
        checkpoints=json.dumps(checkpoints, ensure_ascii=False, indent=2) if checkpoints else "[]",
        solution_code=solution_code[:800],
    )

    try:
        response = await openrouter_service.chat_completion(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "문제를 시작합니다. 초기 가이드를 제공해주세요."},
            ],
            temperature=0.7,
            max_tokens=1500,  # 초기 가이드용
            response_format={"type": "json_object"},
        )

        content = openrouter_service.get_content(response)

        # JSON 파싱
        try:
            result = json.loads(content)
            message = result.get("message", content)
        except json.JSONDecodeError:
            message = content

        return {
            "response": message,
            "initial_guide": result if isinstance(result, dict) else {"message": content},
            "is_initial_guide": True,
            "student_progress": {
                "understanding_score": 0.1,  # 시작
                "concepts_mastered": [],
                "concepts_struggling": [],
                "current_focus": flow[0] if flow else (concepts[0] if concepts else ""),
                "hints_received": 0,
                "attempts": 0,
            },
        }

    except Exception as e:
        print(f"[GuidedTutor:InitialGuide] Error: {e}")
        # 에러 시 기본 안내
        return {
            "response": f"안녕하세요! **{problem_context.get('title', '문제')}**를 함께 풀어볼게요.\n\n"
                       f"이 문제에서는 {', '.join(problem_context.get('topics', ['프로그래밍']))} 개념을 사용해요.\n\n"
                       "준비되셨나요? 먼저 무엇부터 해야 할지 생각해볼까요?",
            "is_initial_guide": True,
            "student_progress": {
                "understanding_score": 0.1,
                "concepts_mastered": [],
                "concepts_struggling": [],
                "current_focus": "",
                "hints_received": 0,
                "attempts": 0,
            },
        }


def is_first_message(state: AgenticRAGState) -> bool:
    """첫 번째 메시지인지 판단 (초기 가이드 필요 여부)"""
    messages = state.get("messages", [])
    return len(messages) <= 1
