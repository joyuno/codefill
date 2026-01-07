# CodeFill LangGraph 고급 기능 활용 개선 계획서

## 핵심 LangGraph 기능

| 기능 | 설명 | 적용 위치 |
|-----|-----|----------|
| **PostgresSaver** | Supabase PostgreSQL에 그래프 상태 영속화 | 전체 그래프 |
| **MemorySaver** | 개발/테스트용 인메모리 체크포인터 | 로컬 개발 |
| **interrupt_before** | 특정 노드 실행 전 중단 및 사용자 확인 | 문제 생성, 힌트 공개 |
| **Human-in-the-Loop** | 사용자 입력 대기 후 재개 | 문제 유형 선택, 확인 단계 |
| **Agentic RAG** | RAG 기반 지능형 에이전트 노드 | 1대1 대화형 튜터, 개인화 추천 |

---

## Phase 1: PostgresSaver 기반 상태 영속화

### 목표
- 페이지 새로고침 시에도 세션 상태 유지
- 대화 히스토리를 백엔드에서 관리

### 구현

#### 1-1. Checkpointer 설정

```python
# backend/app/graphs/checkpointer.py
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.checkpoint.memory import MemorySaver
from ..config import get_settings

settings = get_settings()

async def get_checkpointer():
    """환경에 따른 Checkpointer 반환"""
    if settings.environment == "development":
        return MemorySaver()
    else:
        # Supabase PostgreSQL 연결
        return AsyncPostgresSaver.from_conn_string(
            settings.supabase_db_url  # postgresql://...
        )
```

#### 1-2. 그래프 컴파일 시 Checkpointer 적용

```python
# backend/app/graphs/orchestrator_v2.py (수정)
from .checkpointer import get_checkpointer

class ChatOrchestratorV2:
    def __init__(self):
        self.checkpointer = None

    async def initialize(self):
        self.checkpointer = await get_checkpointer()
        # 각 그래프에 checkpointer 적용
        self.collection_graph = InfoCollectionGraph(checkpointer=self.checkpointer)
        self.discovery_graph = DiscoveryGraph(checkpointer=self.checkpointer)
        self.solving_graph = ProblemSolvingGraph(checkpointer=self.checkpointer)
```

#### 1-3. 세션 ID 기반 상태 복원

```python
async def process(self, message: str, session_id: str, ...):
    config = {"configurable": {"thread_id": session_id}}

    # 이전 상태 자동 복원
    result = await self.graph.ainvoke(
        {"message": message, ...},
        config=config
    )
```

### 수정 파일
- `backend/app/graphs/checkpointer.py` (신규)
- `backend/app/graphs/orchestrator_v2.py`
- `backend/app/graphs/collection/graph.py`
- `backend/app/graphs/discovery_graph.py`
- `backend/app/graphs/solving_graph.py`

---

## Phase 2: Interrupt Before + Human-in-the-Loop

### 목표
- 문제 생성 전 사용자 확인 단계 추가
- 힌트 공개 전 확인 (빈칸 마스킹/해제)
- 퍼즐 정답 공개 전 확인

### 구현

#### 2-1. Interrupt Before 패턴

```python
# backend/app/graphs/discovery_graph.py (수정)
from langgraph.graph import StateGraph, END
from langgraph.types import interrupt

def create_discovery_graph():
    workflow = StateGraph(DiscoveryState)

    # ... 노드 추가 ...

    # 문제 생성 노드 전 중단
    workflow.add_node("confirm_generation", confirm_generation_node)
    workflow.add_node("generate_problem", generate_problem_node)

    # interrupt_before로 문제 생성 전 확인
    return workflow.compile(
        checkpointer=checkpointer,
        interrupt_before=["generate_problem"]  # 이 노드 전에 중단
    )
```

#### 2-2. Human-in-the-Loop 확인 노드

```python
# backend/app/graphs/nodes/confirm.py
from langgraph.types import interrupt

async def confirm_generation_node(state: DiscoveryState) -> Dict[str, Any]:
    """문제 생성 전 사용자 확인"""
    collected_info = state.get("collected_info", {})

    # 확인 메시지 구성
    topics = ", ".join(collected_info.get("topics", ["기초"]))
    difficulty = collected_info.get("difficulty", "easy")

    confirm_message = (
        f"**문제 생성 확인**\n\n"
        f"- 주제: {topics}\n"
        f"- 난이도: {difficulty}\n\n"
        f"이 조건으로 새 문제를 생성할까요?"
    )

    # interrupt()로 사용자 응답 대기
    user_response = interrupt({
        "type": "confirmation",
        "message": confirm_message,
        "options": ["예, 생성해주세요", "아니오, 조건 변경"]
    })

    # 사용자 응답에 따라 분기
    if user_response.get("confirmed"):
        return {"proceed_generation": True}
    else:
        return {"proceed_generation": False, "next_node": "route_discovery_intent"}
```

#### 2-3. 프론트엔드 Interrupt 처리

```typescript
// src/lib/api/agent.ts (수정)
interface InterruptResponse {
  type: 'confirmation' | 'selection' | 'input';
  message: string;
  options?: string[];
  session_id: string;
}

async function handleInterrupt(response: InterruptResponse): Promise<void> {
  // 확인 UI 표시
  // 사용자 응답 후 resume API 호출
}

async function resumeGraph(sessionId: string, userResponse: any): Promise<AgentResponse> {
  return await apiClient.post('/agent/resume', {
    session_id: sessionId,
    user_response: userResponse
  });
}
```

### 적용 위치

1. **문제 생성 전** - "이 조건으로 생성할까요?"
2. **힌트 레벨 4 전** - "정답에 가까운 힌트를 보시겠어요?"
3. **퍼즐 정답 공개 전** - "정답 순서를 보시겠어요?"

### 수정 파일
- `backend/app/graphs/discovery_graph.py`
- `backend/app/graphs/solving_graph.py`
- `backend/app/graphs/nodes/confirm.py` (신규)
- `backend/app/routers/agent.py` (resume 엔드포인트 추가)
- `src/lib/api/agent.ts`
- `src/components/chat/PracticeChatPanel.tsx`

---

## Phase 3: Agentic RAG 기반 1대1 대화형 튜터

### 목표
- 문제/정답 코드를 이해하는 지능형 튜터
- 하드코딩 없이 RAG 기반 응답 생성
- 소크라테스식 질문으로 정답 유도

### Agentic RAG 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                    GuidedTutorGraph                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐     ┌─────────────────┐                   │
│  │ AgenticRAG   │────▶│ RetrieveContext │                   │
│  │    State     │     │   (문제/코드)    │                   │
│  └──────────────┘     └────────┬────────┘                   │
│         │                      │                             │
│         ▼                      ▼                             │
│  ┌──────────────┐     ┌─────────────────┐                   │
│  │ AssessStudent│◀────│  GradeContext   │                   │
│  │ Understanding│     │  (관련성 평가)   │                   │
│  └──────────────┘     └─────────────────┘                   │
│         │                                                    │
│         ▼                                                    │
│  ┌──────────────┐     ┌─────────────────┐                   │
│  │DecideAction  │────▶│ GenerateResponse│                   │
│  │ (EXPLAIN/    │     │  (튜터 응답)     │                   │
│  │  ASK/HINT)   │     └─────────────────┘                   │
│  └──────────────┘                                           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 구현

#### 3-1. Agentic RAG State

```python
# backend/app/graphs/guided_tutor/state.py
from typing import TypedDict, Optional, List, Literal
from langgraph.graph import add_messages

class AgenticRAGState(TypedDict, total=False):
    """Agentic RAG State for Guided Tutor"""

    # === 입력 ===
    messages: List[dict]  # add_messages reducer 적용

    # === 문제 컨텍스트 (RAG 검색 대상) ===
    problem_context: dict  # 문제 설명, 핵심 개념
    solution_code: str     # 정답 코드
    key_concepts: List[str]  # 학습해야 할 개념들

    # === RAG 검색 결과 ===
    retrieved_docs: List[dict]  # 관련 문서
    retrieval_grade: Literal["relevant", "not_relevant"]

    # === 학생 상태 ===
    student_understanding: float  # 0.0 ~ 1.0
    concepts_mastered: List[str]  # 이해한 개념
    concepts_struggling: List[str]  # 어려워하는 개념
    current_focus: str  # 현재 다루는 개념

    # === 튜터 행동 ===
    tutor_action: Literal[
        "explain",      # 개념 설명
        "ask_question", # 이해 확인 질문
        "give_hint",    # 힌트 제공
        "give_example", # 예제 제공
        "next_step",    # 다음 단계로
        "celebrate",    # 정답 축하
    ]

    # === 출력 ===
    response: str
    next_node: Optional[str]
```

#### 3-2. Agentic RAG Nodes

```python
# backend/app/graphs/guided_tutor/nodes.py
from langchain_core.prompts import ChatPromptTemplate
from ..services.rag import rag_service
from ..services.openrouter import openrouter_service

async def retrieve_context_node(state: AgenticRAGState) -> dict:
    """문제 관련 컨텍스트 검색 (RAG)"""
    last_message = state["messages"][-1]["content"]
    problem_context = state.get("problem_context", {})

    # 현재 대화에서 관련 개념 검색
    query = f"{last_message} {problem_context.get('description', '')}"

    docs = await rag_service.search_concepts(
        query=query,
        topics=problem_context.get("topics", []),
        limit=3
    )

    return {"retrieved_docs": docs}

async def grade_context_node(state: AgenticRAGState) -> dict:
    """검색 결과 관련성 평가"""
    docs = state.get("retrieved_docs", [])
    last_message = state["messages"][-1]["content"]

    # LLM으로 관련성 평가
    grade_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a grader. Determine if documents are relevant to the student's question."),
        ("human", "Question: {question}\n\nDocuments: {docs}\n\nGrade (relevant/not_relevant):"),
    ])

    # ... LLM 호출 ...

    return {"retrieval_grade": grade}

async def assess_understanding_node(state: AgenticRAGState) -> dict:
    """학생 이해도 평가"""
    messages = state.get("messages", [])
    problem_context = state.get("problem_context", {})
    solution_code = state.get("solution_code", "")

    # 최근 대화에서 이해도 평가
    assess_prompt = f"""
    문제: {problem_context.get('description', '')}
    정답 코드: {solution_code}

    학생의 최근 메시지들을 분석하고:
    1. 전체 이해도 점수 (0.0 ~ 1.0)
    2. 이해한 개념들
    3. 어려워하는 개념들
    4. 현재 집중해야 할 개념

    을 JSON으로 반환해주세요.
    """

    # ... LLM 호출 ...

    return {
        "student_understanding": result["score"],
        "concepts_mastered": result["mastered"],
        "concepts_struggling": result["struggling"],
        "current_focus": result["focus"],
    }

async def decide_action_node(state: AgenticRAGState) -> dict:
    """튜터 행동 결정"""
    understanding = state.get("student_understanding", 0.5)
    struggling = state.get("concepts_struggling", [])
    current_focus = state.get("current_focus", "")

    # 이해도에 따른 행동 결정
    if understanding > 0.8:
        action = "next_step"
    elif understanding > 0.6:
        action = "ask_question"  # 이해 확인
    elif len(struggling) > 0:
        action = "give_hint"  # 어려워하면 힌트
    else:
        action = "explain"  # 기본: 설명

    return {"tutor_action": action}

async def generate_response_node(state: AgenticRAGState) -> dict:
    """튜터 응답 생성 (2줄 이내)"""
    action = state.get("tutor_action", "explain")
    current_focus = state.get("current_focus", "")
    retrieved_docs = state.get("retrieved_docs", [])
    problem_context = state.get("problem_context", {})
    solution_code = state.get("solution_code", "")

    action_prompts = {
        "explain": "간단히 개념을 설명해주세요. 2줄 이내로.",
        "ask_question": "이해도를 확인하는 질문을 하세요. 1줄로.",
        "give_hint": "정답 코드의 관련 부분을 힌트로 주세요. 코드는 보여주지 마세요.",
        "give_example": "관련 예제를 보여주세요.",
        "next_step": "다음 단계로 넘어가세요.",
        "celebrate": "정답을 축하하고 핵심을 요약해주세요.",
    }

    system_prompt = f"""
    당신은 코딩 튜터입니다. 소크라테스식 질문법을 사용하세요.
    직접 정답을 알려주지 마세요. 학생이 스스로 발견하도록 유도하세요.

    === 문제 정보 ===
    {problem_context}

    === 정답 코드 (학생에게 직접 보여주지 마세요) ===
    {solution_code}

    === 현재 집중 개념 ===
    {current_focus}

    === 행동 지시 ===
    {action_prompts.get(action, "도움을 주세요.")}

    응답은 반드시 2줄 이내로 해주세요.
    """

    # ... LLM 호출 ...

    return {"response": response}
```

#### 3-3. Guided Tutor Graph 구성

```python
# backend/app/graphs/guided_tutor/graph.py
from langgraph.graph import StateGraph, END
from .state import AgenticRAGState
from .nodes import (
    retrieve_context_node,
    grade_context_node,
    assess_understanding_node,
    decide_action_node,
    generate_response_node,
)

def create_guided_tutor_graph(checkpointer=None):
    workflow = StateGraph(AgenticRAGState)

    # 노드 추가
    workflow.add_node("retrieve_context", retrieve_context_node)
    workflow.add_node("grade_context", grade_context_node)
    workflow.add_node("assess_understanding", assess_understanding_node)
    workflow.add_node("decide_action", decide_action_node)
    workflow.add_node("generate_response", generate_response_node)

    # 플로우 정의
    workflow.set_entry_point("retrieve_context")

    workflow.add_edge("retrieve_context", "grade_context")

    # 관련성에 따른 분기
    workflow.add_conditional_edges(
        "grade_context",
        lambda s: "assess" if s.get("retrieval_grade") == "relevant" else "retrieve",
        {
            "assess": "assess_understanding",
            "retrieve": "retrieve_context",  # 다시 검색 (다른 쿼리로)
        }
    )

    workflow.add_edge("assess_understanding", "decide_action")
    workflow.add_edge("decide_action", "generate_response")
    workflow.add_edge("generate_response", END)

    return workflow.compile(checkpointer=checkpointer)
```

### 수정/신규 파일
- `backend/app/graphs/guided_tutor/` (신규 디렉토리)
  - `__init__.py`
  - `state.py`
  - `nodes.py`
  - `graph.py`
- `backend/app/services/rag.py` (개념 검색 메서드 추가)
- `backend/app/routers/chat.py` (1대1 대화형 라우트)

---

## Phase 4: 힌트 시스템 개선

### 4-1. 빈칸 힌트 (마스킹 토글)

```python
# backend/app/services/hint_service.py (수정)

async def generate_blank_hint_masked(
    self,
    problem_id: str,
    blank_index: int,
    current_level: int,  # 0=미요청, 1=마스킹, 2=공개
) -> Dict[str, Any]:
    """빈칸 힌트 - 마스킹/해제 토글 방식"""

    blank_problem = self.get_blank_problem(problem_id)
    answers = blank_problem.get("answers", [])
    answer = answers[blank_index] if blank_index < len(answers) else ""

    if current_level == 0:
        # 첫 클릭: 마스킹된 힌트
        masked = "*" * len(answer)
        return {
            "hint_level": 1,
            "hint_content": f"정답: {masked}",
            "hint_type": "masked",
            "can_reveal": True,
        }
    elif current_level == 1:
        # 두 번째 클릭: 힌트 공개
        return {
            "hint_level": 2,
            "hint_content": f"정답: {answer}",
            "hint_type": "revealed",
            "can_reveal": False,
        }

    return {"hint_level": current_level, "hint_content": "이미 공개됨"}
```

### 4-2. 퍼즐 힌트 (첫 틀린 위치 + 이유)

```python
async def generate_puzzle_hint_focused(
    self,
    problem_id: str,
    user_order: List[str],
) -> Dict[str, Any]:
    """퍼즐 힌트 - 첫 번째 틀린 블록 + 이유 (2줄 이내)"""

    puzzle_problem = self.get_puzzle_problem(problem_id)
    blocks = puzzle_problem.get("blocks", [])

    # 정답 순서
    correct_order = [b["id"] for b in sorted(blocks, key=lambda x: x.get("order", 0))]

    # 첫 번째 틀린 위치 찾기
    first_wrong = None
    for i, (user_id, correct_id) in enumerate(zip(user_order, correct_order)):
        if user_id != correct_id:
            first_wrong = {
                "position": i,
                "user_block": user_id,
                "correct_block": correct_id,
            }
            break

    if not first_wrong:
        return {"hint_content": "모두 정답입니다!", "is_correct": True}

    # 정답 블록의 코드
    correct_block = next(b for b in blocks if b["id"] == first_wrong["correct_block"])
    correct_code = correct_block.get("code", "")[:50]

    # 간단한 이유 (2줄 이내)
    hint_prompt = f"""
    위치 {first_wrong['position'] + 1}번이 틀렸습니다.
    정답 블록: `{correct_code}`
    이유를 1줄로 설명해주세요. (예: "반복문이 먼저 와야 합니다")
    """

    # LLM 호출해서 이유 생성
    reason = await self._generate_short_reason(hint_prompt)

    return {
        "hint_content": f"블록 {first_wrong['position'] + 1}번이 틀렸어요.\n정답: `{correct_code}` ({reason})",
        "first_wrong_position": first_wrong["position"],
        "correct_block_id": first_wrong["correct_block"],
    }
```

### 수정 파일
- `backend/app/services/hint_service.py`
- `backend/app/prompts/hint_blank_agent.py`
- `backend/app/prompts/hint_puzzle_agent.py`
- `src/components/practice/UnifiedPractice.tsx` (힌트 UI)

---

## Phase 5: 퍼즐 복수 정답 검증

### 구현

```python
# backend/app/services/puzzle_validator.py (신규)

class PuzzleValidator:
    """퍼즐 문제 복수 정답 검증"""

    async def validate_order(
        self,
        blocks: List[dict],
        user_order: List[str],
        validation_method: str = "smart",  # exact, smart, judge0
    ) -> Dict[str, Any]:
        """
        퍼즐 순서 검증

        validation_method:
        - exact: 정확히 일치해야 정답
        - smart: 함수/클래스 단위 그룹 순서 유연
        - judge0: 실제 실행으로 검증
        """
        if validation_method == "exact":
            return self._validate_exact(blocks, user_order)
        elif validation_method == "smart":
            return self._validate_smart(blocks, user_order)
        elif validation_method == "judge0":
            return await self._validate_with_judge0(blocks, user_order)

    def _validate_smart(
        self,
        blocks: List[dict],
        user_order: List[str],
    ) -> Dict[str, Any]:
        """스마트 검증: 함수/클래스 단위 그룹 순서 유연"""

        # 블록을 그룹으로 분류
        groups = self._identify_groups(blocks)

        # 그룹 내 순서는 고정, 그룹 간 순서는 유연
        user_groups = self._get_user_groups(user_order, groups)
        correct_groups = self._get_correct_groups(blocks, groups)

        # 각 그룹 내 순서 검증
        for group_id, group_blocks in groups.items():
            user_group_order = [b for b in user_order if b in group_blocks]
            correct_group_order = [b["id"] for b in sorted(
                [bl for bl in blocks if bl["id"] in group_blocks],
                key=lambda x: x.get("order", 0)
            )]

            if user_group_order != correct_group_order:
                return {
                    "is_correct": False,
                    "reason": f"그룹 '{group_id}' 내 순서가 틀렸습니다.",
                }

        # 그룹 간 의존성 검증 (import → 함수 정의 → 호출)
        if not self._validate_group_dependencies(user_groups, groups):
            return {
                "is_correct": False,
                "reason": "그룹 간 의존 순서가 틀렸습니다.",
            }

        return {"is_correct": True}

    def _identify_groups(self, blocks: List[dict]) -> Dict[str, List[str]]:
        """블록을 논리적 그룹으로 분류"""
        groups = {}
        current_group = "main"

        for block in blocks:
            code = block.get("code", "")

            # 함수 정의 시작
            if code.strip().startswith("def "):
                func_name = code.split("(")[0].replace("def ", "").strip()
                current_group = f"func_{func_name}"
            # 클래스 정의 시작
            elif code.strip().startswith("class "):
                class_name = code.split("(")[0].split(":")[0].replace("class ", "").strip()
                current_group = f"class_{class_name}"
            # import 구문
            elif code.strip().startswith(("import ", "from ")):
                current_group = "imports"

            if current_group not in groups:
                groups[current_group] = []
            groups[current_group].append(block["id"])

        return groups

    async def _validate_with_judge0(
        self,
        blocks: List[dict],
        user_order: List[str],
    ) -> Dict[str, Any]:
        """Judge0로 실제 실행 검증"""
        from .judge0 import judge0_service

        # 사용자 순서로 코드 조립
        user_code = self._assemble_code(blocks, user_order)

        # 정답 순서로 코드 조립 (테스트 케이스용)
        correct_order = [b["id"] for b in sorted(blocks, key=lambda x: x.get("order", 0))]
        correct_code = self._assemble_code(blocks, correct_order)

        # Judge0 실행
        result = await judge0_service.compare_outputs(
            user_code=user_code,
            correct_code=correct_code,
            language="python",
        )

        return {
            "is_correct": result.get("outputs_match", False),
            "validation_method": "judge0",
            "execution_result": result,
        }
```

### 수정 파일
- `backend/app/services/puzzle_validator.py` (신규)
- `backend/app/routers/practice.py`
- `src/lib/problemLoader.ts`

---

## Phase 6: 개인화 RAG 및 DB 저장 로직 ✅ 완료

### 6-1. PersonalizationService 구현

```python
# backend/app/services/personalization.py (신규)

class PersonalizationService:
    """개인화 서비스 - 학습 데이터 분석 및 추천"""

    async def get_user_profile(self, user_id: str) -> UserLearningProfile:
        """학습 프로필 조회"""
        # attempts 테이블에서 최근 100개 조회
        # 토픽별 성적 분석
        # 강점/약점 파악
        # 선호 난이도 분석

    async def get_recommendations(self, user_id: str, limit: int) -> List[Recommendation]:
        """개인화된 문제 추천"""
        # 40%: 약점 보완 문제
        # 30%: 다음 난이도 도전
        # 30%: 복습 문제 (틀렸던 것)

    async def get_rag_context(self, user_id: str) -> Dict:
        """RAG 검색용 사용자 컨텍스트"""
```

### 6-2. 개인화된 문제 검색

```python
# backend/app/services/rag.py (수정)

async def search_problems_personalized(
    self,
    query: str,
    user_id: str,
    topics: List[str] = None,
    difficulty: str = None,
    limit: int = 5,
) -> Tuple[List[dict], bool]:
    """사용자 맞춤 문제 검색"""

    # 1. 개인화 컨텍스트 조회
    ps = get_personalization_service()
    user_context = await ps.get_rag_context(user_id)

    # 2. 난이도/토픽 자동 조정
    if not difficulty:
        difficulty = user_context.get("preferred_difficulty")
    if user_context.get("weak_topics"):
        topics = (topics or []) + user_context["weak_topics"]

    # 3. 기본 검색 수행
    results, fallback = await self.search_problems_hybrid(...)

    # 4. 개인화 부스팅
    for result in results:
        # 약점 토픽 매칭: +0.15
        # 선호 난이도 매칭: +0.10
        # 다음 난이도 도전: +0.05
        result["similarity"] += personalization_boost

    return sorted(results, by=similarity)[:limit], fallback
```

### 6-3. API 엔드포인트

```python
# backend/app/routers/agent.py (수정)

@router.get("/user/profile")
async def get_user_learning_profile(user_id: UUID):
    """사용자 학습 프로필 조회"""

@router.get("/user/recommendations")
async def get_personalized_recommendations(user_id: UUID, limit: int = 5):
    """개인화된 문제 추천"""

@router.post("/search/personalized")
async def search_problems_personalized(request: RAGSearchRequest, user_id: UUID):
    """개인화된 문제 검색"""
```

### 구현 파일
- `backend/app/services/personalization.py` ✅ 신규
- `backend/app/services/rag.py` ✅ 수정 (search_problems_personalized 추가)
- `backend/app/routers/agent.py` ✅ 수정 (3개 엔드포인트 추가)

---

## 구현 순서

```
Phase 1: PostgresSaver (기반)
    │
    ├── Phase 2: Interrupt + Human-in-Loop
    │
    ├── Phase 3: Agentic RAG 튜터
    │
    ├── Phase 4: 힌트 시스템 개선
    │
    ├── Phase 5: 퍼즐 복수 정답
    │
    └── Phase 6: 개인화 RAG + DB 저장
```

---

## 예상 효과

| Phase | 개선 내용 | 사용자 경험 |
|-------|----------|-----------|
| 1 | 상태 영속화 | 새로고침해도 대화 유지 |
| 2 | 확인 단계 | 문제 생성 전 조건 확인 가능 |
| 3 | Agentic RAG 튜터 | 정답 유도하는 지능형 대화 |
| 4 | 힌트 개선 | 빈칸별 토글 힌트, 퍼즐 첫 오답 안내 |
| 5 | 복수 정답 | 함수 순서 바뀌어도 정답 인정 |
| 6 | 개인화 | 약점 기반 문제 추천 |

---

## 구현 현황 (2025-01-05)

| Phase | 상태 | 주요 구현 파일 |
|-------|------|---------------|
| 1 | ✅ 완료 | `checkpointer.py`, `orchestrator_v2.py`, `main.py` |
| 2 | ✅ 완료 | `nodes/confirm.py`, `discovery_graph.py`, `/resume` API |
| 3 | ✅ 완료 | `guided_tutor/graph.py`, `nodes.py`, `state.py` |
| 4 | ✅ 완료 | `hint_service.py` (masked toggle, focused hint) |
| 5 | ✅ 완료 | `puzzle_validator.py`, `solving.py` (smart validation) |
| 6 | ✅ 완료 | `personalization.py`, `rag.py`, `/user/*` API |

### 신규 생성 파일
- `backend/app/graphs/checkpointer.py`
- `backend/app/graphs/nodes/confirm.py`
- `backend/app/graphs/guided_tutor/` (디렉토리)
- `backend/app/services/puzzle_validator.py`
- `backend/app/services/personalization.py`

### 수정 파일
- `backend/app/config.py` (Supabase DB URL, environment 설정)
- `backend/app/main.py` (orchestrator 초기화, checkpointer 정리)
- `backend/requirements.txt` (langgraph-checkpoint 패키지)
- `backend/app/graphs/orchestrator_v2.py` (checkpointer 연동)
- `backend/app/graphs/discovery_graph.py` (confirm 노드 추가)
- `backend/app/routers/agent.py` (session_id, /resume, 개인화 API)
- `backend/app/services/rag.py` (search_concepts, search_personalized)
- `backend/app/services/hint_service.py` (masked toggle, focused puzzle)
- `backend/app/graphs/nodes/solving.py` (async puzzle validation)
