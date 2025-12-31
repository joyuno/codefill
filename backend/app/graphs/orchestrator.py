"""
LangGraph Orchestrator - 3단계 그래프 연결

3개의 LangGraph를 연결하여 전체 플로우를 관리합니다.

[1단계: Intent Graph]     [2단계: Discovery Graph]    [3단계: Solving Graph]
       │                          │                          │
   의도 파악                   문제 탐색                    문제 풀이
       │                          │                          │
       ▼                          ▼                          ▼
┌───────────────┐         ┌───────────────┐         ┌───────────────┐
│classify_intent│         │search_problems│         │ provide_hint  │
│ collect_info  │   ──▶   │filter_results │   ──▶   │ review_code   │
│ route_request │         │handle_selection│        │ check_answer  │
└───────────────┘         │confirm_problem │         │give_feedback  │
                          └───────────────┘         └───────────────┘

사용 예시:
```python
orchestrator = ChatOrchestrator()

# 새로운 대화
result = await orchestrator.process(
    message="DP 문제 풀고 싶어",
    conversation_history=[],
    user_context={}
)

# 결과: route_to="discovery", response_message="어떤 난이도를 원하시나요?"
```
"""
from typing import Dict, Any, Optional, List
import time

from .intent_graph import IntentGraph
from .discovery_graph import DiscoveryGraph
from .solving_graph import ProblemSolvingGraph
from .evaluation import evaluate_stage, evaluation_logger, EvaluationResult


class ChatOrchestrator:
    """
    3단계 LangGraph 오케스트레이터

    1단계 (Intent) → 2단계 (Discovery) → 3단계 (Solving)
    각 단계의 결과에 따라 자동으로 다음 단계로 라우팅합니다.

    평가 모드 활성화 시 각 단계별 성능을 LLM으로 평가합니다.
    """

    def __init__(self, enable_evaluation: bool = False):
        self.intent_graph = IntentGraph()
        self.discovery_graph = DiscoveryGraph()
        self.solving_graph = ProblemSolvingGraph()
        self.enable_evaluation = enable_evaluation
        self.last_evaluation: Optional[EvaluationResult] = None

    async def process(
        self,
        message: str,
        conversation_history: list = None,
        user_context: dict = None,
        session_state: dict = None,
    ) -> Dict[str, Any]:
        """
        메시지를 처리하고 적절한 응답을 반환합니다.

        Args:
            message: 사용자 메시지
            conversation_history: 대화 히스토리
            user_context: 사용자 컨텍스트 (온보딩 데이터, 현재 상태 등)
            session_state: 세션 상태 (이전 검색 결과, 선택된 문제 등)

        Returns:
            {
                stage: 현재 단계 (intent, discovery, solving),
                intent_result: 의도 분류 결과,
                collected_info: 수집된 정보,
                search_results: 검색된 문제 (discovery 단계),
                selected_problem: 선택된 문제,
                response_message: 응답 메시지,
                action_trigger: 액션 트리거,
                action_data: 액션 데이터,
                next_stage: 다음 단계 (discovery, solving, respond),
                is_complete: 현재 플로우 완료 여부,
            }
        """
        conversation_history = conversation_history or []
        user_context = user_context or {}
        session_state = session_state or {}

        # 세션에서 이전 상태 복원
        collected_info = session_state.get("collected_info", {})
        search_results = session_state.get("search_results", [])
        selected_problem = session_state.get("selected_problem")
        current_stage = session_state.get("current_stage", "intent")

        # 입력 데이터 저장 (평가용)
        input_data = {
            "message": message,
            "conversation_history": conversation_history,
            "user_context": user_context,
            "session_state": session_state,
        }

        # 현재 문제가 있고 풀이 중이면 바로 Solving Graph로
        if user_context.get("current_problem") and current_stage == "solving":
            start_time = time.time()
            result = await self._process_solving(
                message=message,
                problem_context=user_context.get("current_problem"),
                user_progress=user_context.get("user_progress", {}),
                conversation_history=conversation_history,
                previous_hints=session_state.get("previous_hints", []),
            )
            latency_ms = (time.time() - start_time) * 1000

            # 평가 수행
            if self.enable_evaluation:
                await self._evaluate_and_log("solving", input_data, result, latency_ms)

            return result

        # 1단계: Intent Graph
        start_time = time.time()
        intent_result = await self.intent_graph.invoke(
            message=message,
            conversation_history=conversation_history,
            user_context=user_context,
            collected_info=collected_info,
        )
        intent_latency = (time.time() - start_time) * 1000

        # Intent 평가
        if self.enable_evaluation:
            await self._evaluate_and_log("intent", input_data, intent_result, intent_latency)

        route_to = intent_result.get("route_to", "respond")
        updated_collected_info = intent_result.get("collected_info", collected_info)

        # route_to에 따라 분기
        if route_to == "discovery":
            # 2단계: Discovery Graph
            start_time = time.time()
            discovery_result = await self._process_discovery(
                message=message,
                intent=intent_result.get("intent_result", {}).get("intent", "new_problem"),
                collected_info=updated_collected_info,
                conversation_history=conversation_history,
                user_context=user_context,
                search_results=search_results,
            )
            discovery_latency = (time.time() - start_time) * 1000

            # Discovery 평가
            if self.enable_evaluation:
                discovery_input = {**input_data, "collected_info": updated_collected_info}
                await self._evaluate_and_log("discovery", discovery_input, discovery_result, discovery_latency)

            return self._merge_results(
                stage="discovery",
                intent_result=intent_result,
                stage_result=discovery_result,
            )

        elif route_to == "solving":
            # 3단계: Solving Graph (문제가 선택된 경우)
            if selected_problem or user_context.get("current_problem"):
                problem_context = selected_problem or user_context.get("current_problem")
                solving_result = await self._process_solving(
                    message=message,
                    problem_context=problem_context,
                    user_progress=user_context.get("user_progress", {}),
                    conversation_history=conversation_history,
                    previous_hints=session_state.get("previous_hints", []),
                )
                return self._merge_results(
                    stage="solving",
                    intent_result=intent_result,
                    stage_result=solving_result,
                )
            else:
                # 문제가 없으면 Discovery로 리다이렉트
                return {
                    "stage": "intent",
                    "intent_result": intent_result.get("intent_result"),
                    "collected_info": updated_collected_info,
                    "response_message": "먼저 문제를 선택해주세요! 어떤 문제를 풀어볼까요?",
                    "next_stage": "discovery",
                    "is_complete": False,
                }

        else:
            # 직접 응답 (greeting, thanks 등)
            return {
                "stage": "intent",
                "intent_result": intent_result.get("intent_result"),
                "collected_info": updated_collected_info,
                "response_message": intent_result.get("response_message", "무엇을 도와드릴까요?"),
                "next_stage": "respond",
                "is_complete": True,
            }

    async def _process_discovery(
        self,
        message: str,
        intent: str,
        collected_info: dict,
        conversation_history: list,
        user_context: dict,
        search_results: list,
    ) -> Dict[str, Any]:
        """Discovery 그래프 실행"""
        return await self.discovery_graph.invoke(
            message=message,
            collected_info=collected_info,
            intent=intent,
            conversation_history=conversation_history,
            user_context=user_context,
            search_results=search_results,
        )

    async def _process_solving(
        self,
        message: str,
        problem_context: dict,
        user_progress: dict,
        conversation_history: list,
        previous_hints: list,
    ) -> Dict[str, Any]:
        """Solving 그래프 실행"""
        return await self.solving_graph.invoke(
            message=message,
            problem_context=problem_context,
            user_progress=user_progress,
            conversation_history=conversation_history,
            previous_hints=previous_hints,
        )

    def _merge_results(
        self,
        stage: str,
        intent_result: Dict[str, Any],
        stage_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Intent 결과와 단계별 결과를 병합"""
        result = {
            "stage": stage,
            "intent_result": intent_result.get("intent_result"),
            "collected_info": stage_result.get("collected_info") or intent_result.get("collected_info"),
            "search_results": stage_result.get("search_results") or stage_result.get("filtered_results"),
            "selected_problem": stage_result.get("selected_problem"),
            "generated_problem": stage_result.get("generated_problem"),
            "response_message": stage_result.get("response_message", ""),
            "action_trigger": stage_result.get("action_trigger"),
            "action_data": stage_result.get("action_data"),
            "next_stage": stage_result.get("route_to", "respond"),
            "is_complete": stage_result.get("is_confirmed", False),
            # Solving 결과
            "hint_level": stage_result.get("hint_level"),
            "is_correct": stage_result.get("is_correct"),
        }

        # 평가 결과 추가
        if self.last_evaluation:
            result["evaluation"] = self.last_evaluation.to_dict()

        return result

    async def _evaluate_and_log(
        self,
        stage: str,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        latency_ms: float,
    ):
        """평가 수행 및 로깅"""
        try:
            eval_result = await evaluate_stage(stage, input_data, output_data, latency_ms)
            evaluation_logger.log(eval_result)
            self.last_evaluation = eval_result
        except Exception as e:
            print(f"[Orchestrator] Evaluation error: {e}")

    def get_evaluation_summary(self) -> Dict[str, Any]:
        """평가 요약 반환"""
        return evaluation_logger.get_summary()

    def get_improvement_suggestions(self) -> List[Dict[str, Any]]:
        """개선 제안 반환"""
        return evaluation_logger.get_improvement_suggestions()


# ============================================================
# Singleton Instance
# ============================================================

_orchestrator = None


def get_orchestrator() -> ChatOrchestrator:
    """오케스트레이터 싱글톤 반환"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = ChatOrchestrator()
    return _orchestrator


# ============================================================
# Convenience Functions
# ============================================================

async def process_message(
    message: str,
    conversation_history: list = None,
    user_context: dict = None,
    session_state: dict = None,
) -> Dict[str, Any]:
    """
    편의 함수: 메시지 처리

    Usage:
        result = await process_message(
            message="DP 문제 풀고 싶어",
            user_context={"level": "intermediate"}
        )
    """
    orchestrator = get_orchestrator()
    return await orchestrator.process(
        message=message,
        conversation_history=conversation_history,
        user_context=user_context,
        session_state=session_state,
    )
