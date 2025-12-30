"""
LangGraph Orchestrator V2 - 개선된 3단계 그래프 구조

기존 구조의 문제점:
- IntentGraph의 collect_info_node가 너무 거대함 (200줄+ if/else)
- LangGraph의 노드 분리 철학을 따르지 않음
- 질문과 선택 구분이 불명확

개선된 구조:
- IntentGraph: 의도 분류만 담당
- InfoCollectionGraph: 정보 수집 (topic → difficulty → language)
- DiscoveryGraph: 문제 검색/선택
- SolvingGraph: 문제 풀이 지원

Flow:
    Message → IntentGraph (의도 분류)
                ↓
           [needs_info_collection?]
                ├─ Yes → InfoCollectionGraph → [is_complete?]
                │                                   ├─ Yes → DiscoveryGraph
                │                                   └─ No → 응답 (추가 정보 요청)
                └─ No → [route_to?]
                            ├─ discovery → DiscoveryGraph
                            ├─ solving → SolvingGraph
                            └─ respond → 직접 응답
"""
from typing import Dict, Any, Optional, List

from .intent_graph import IntentGraph
from .collection import InfoCollectionGraph
from .discovery_graph import DiscoveryGraph
from .solving_graph import ProblemSolvingGraph
from .intent_state import NEEDS_INFO_COLLECTION
from ..services.problem_save import get_problem_save_service


class ChatOrchestratorV2:
    """
    개선된 3단계 LangGraph 오케스트레이터

    각 그래프가 명확한 단일 책임을 가짐:
    - IntentGraph: 의도 분류
    - InfoCollectionGraph: 정보 수집 (주제/난이도/언어)
    - DiscoveryGraph: 문제 검색/선택
    - SolvingGraph: 문제 풀이 지원
    """

    def __init__(self):
        self.intent_graph = IntentGraph()
        self.collection_graph = InfoCollectionGraph()
        self.discovery_graph = DiscoveryGraph()
        self.solving_graph = ProblemSolvingGraph()

    async def process(
        self,
        message: str,
        conversation_history: list = None,
        user_context: dict = None,
        session_state: dict = None,
    ) -> Dict[str, Any]:
        """
        메시지 처리

        Args:
            message: 사용자 메시지
            conversation_history: 대화 히스토리
            user_context: 사용자 컨텍스트 (온보딩 데이터, 현재 상태 등)
            session_state: 세션 상태 (이전 검색 결과, 수집된 정보 등)

        Returns:
            {
                stage: 현재 단계,
                intent: 분류된 의도,
                collected_info: 수집된 정보,
                search_results: 검색된 문제,
                response_message: 응답 메시지,
                is_complete: 정보 수집 완료 여부,
                action_trigger: 액션 트리거,
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

        # ============================================================
        # 0. 문제 유형 선택 처리 (빈칸/퍼즐/대화형)
        # ============================================================
        problem_type = self._detect_problem_type_selection(message)
        if problem_type and selected_problem:
            return await self._process_problem_type_selection(
                problem_type=problem_type,
                selected_problem=selected_problem,
                user_context=user_context,
            )

        # ============================================================
        # 1. 현재 문제가 있고 풀이 중이면 바로 Solving Graph로
        # ============================================================
        if user_context.get("current_problem") and current_stage == "solving":
            return await self._process_solving(
                message=message,
                problem_context=user_context.get("current_problem"),
                user_progress=user_context.get("user_progress", {}),
                conversation_history=conversation_history,
                previous_hints=session_state.get("previous_hints", []),
            )

        # ============================================================
        # 2. Intent Graph - 의도 분류
        # ============================================================
        intent_result = await self.intent_graph.invoke(
            message=message,
            conversation_history=conversation_history,
            user_context=user_context,
            collected_info={},  # V2에서는 IntentGraph가 정보 수집 안함
        )

        intent = intent_result.get("intent_result", {}).get("intent", "unknown")

        # ============================================================
        # 3. 정보 수집이 필요한 의도인지 확인
        # ============================================================
        if intent in NEEDS_INFO_COLLECTION:
            return await self._process_info_collection(
                message=message,
                conversation_history=conversation_history,
                user_context=user_context,
                collected_info=collected_info,
                intent=intent,
            )

        # ============================================================
        # 4. route_to에 따라 분기
        # ============================================================
        route_to = intent_result.get("route_to", "respond")

        if route_to == "discovery":
            # 정보가 충분하면 Discovery로
            if self._has_sufficient_info(collected_info):
                return await self._process_discovery(
                    message=message,
                    intent=intent,
                    collected_info=collected_info,
                    conversation_history=conversation_history,
                    user_context=user_context,
                    search_results=search_results,
                )
            else:
                # 정보 부족 → InfoCollectionGraph
                return await self._process_info_collection(
                    message=message,
                    conversation_history=conversation_history,
                    user_context=user_context,
                    collected_info=collected_info,
                    intent=intent,
                )

        elif route_to == "solving":
            if selected_problem or user_context.get("current_problem"):
                return await self._process_solving(
                    message=message,
                    problem_context=selected_problem or user_context.get("current_problem"),
                    user_progress=user_context.get("user_progress", {}),
                    conversation_history=conversation_history,
                    previous_hints=session_state.get("previous_hints", []),
                )
            else:
                return {
                    "stage": "intent",
                    "intent": intent,
                    "collected_info": collected_info,
                    "response_message": "먼저 문제를 선택해주세요! 어떤 문제를 풀어볼까요?",
                    "next_stage": "discovery",
                    "is_complete": False,
                }

        else:
            # 직접 응답 (greeting, thanks 등)
            return {
                "stage": "intent",
                "intent": intent,
                "collected_info": collected_info,
                "response_message": intent_result.get("response_message", "무엇을 도와드릴까요?"),
                "next_stage": "respond",
                "is_complete": True,
            }

    async def _process_info_collection(
        self,
        message: str,
        conversation_history: list,
        user_context: dict,
        collected_info: dict,
        intent: str,
    ) -> Dict[str, Any]:
        """
        InfoCollectionGraph 실행

        topic → difficulty → language 순서로 수집
        """
        # 기존 수집 정보에서 추출
        existing_topic = None
        existing_difficulty = None
        existing_language = None

        if collected_info:
            topics = collected_info.get("topics")
            if topics and isinstance(topics, list) and len(topics) > 0:
                existing_topic = topics[0]
            existing_difficulty = collected_info.get("difficulty")
            existing_language = collected_info.get("language")

        # InfoCollectionGraph 실행
        result = await self.collection_graph.invoke(
            message=message,
            conversation_history=conversation_history,
            user_context=user_context,
            existing_topic=existing_topic,
            existing_difficulty=existing_difficulty,
            existing_language=existing_language,
        )

        # 수집된 정보 병합
        new_collected = result.get("collected_info", {})
        merged_info = {
            "topics": [new_collected.get("topic")] if new_collected.get("topic") else collected_info.get("topics", []),
            "difficulty": new_collected.get("difficulty") or collected_info.get("difficulty"),
            "language": new_collected.get("language") or collected_info.get("language"),
        }

        # 정보 수집 완료 시 Discovery로
        if result.get("is_complete"):
            return await self._process_discovery(
                message=message,
                intent=intent,
                collected_info=merged_info,
                conversation_history=conversation_history,
                user_context=user_context,
                search_results=[],
            )

        return {
            "stage": "collection",
            "intent": intent,
            "collected_info": merged_info,
            "response_message": result.get("message", ""),
            "next_stage": "collection",
            "is_complete": False,
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
        result = await self.discovery_graph.invoke(
            message=message,
            collected_info=collected_info,
            intent=intent,
            conversation_history=conversation_history,
            user_context=user_context,
            search_results=search_results,
        )

        return {
            "stage": "discovery",
            "intent": intent,
            "collected_info": result.get("collected_info") or collected_info,
            "search_results": result.get("search_results") or result.get("filtered_results"),
            "selected_problem": result.get("selected_problem"),
            "generated_problem": result.get("generated_problem"),
            "response_message": result.get("response_message", ""),
            "action_trigger": result.get("action_trigger"),
            "action_data": result.get("action_data"),
            "next_stage": result.get("route_to", "respond"),
            "is_complete": result.get("is_confirmed", False),
        }

    async def _process_solving(
        self,
        message: str,
        problem_context: dict,
        user_progress: dict,
        conversation_history: list,
        previous_hints: list,
    ) -> Dict[str, Any]:
        """Solving 그래프 실행"""
        result = await self.solving_graph.invoke(
            message=message,
            problem_context=problem_context,
            user_progress=user_progress,
            conversation_history=conversation_history,
            previous_hints=previous_hints,
        )

        return {
            "stage": "solving",
            "response_message": result.get("response_message", ""),
            "hint_level": result.get("hint_level"),
            "is_correct": result.get("is_correct"),
            "next_stage": result.get("route_to", "solving"),
            "is_complete": result.get("is_complete", False),
        }

    def _has_sufficient_info(self, collected_info: dict) -> bool:
        """정보 수집이 충분한지 확인"""
        topics = collected_info.get("topics")
        difficulty = collected_info.get("difficulty")
        language = collected_info.get("language")

        has_topic = topics and isinstance(topics, list) and len(topics) > 0
        has_difficulty = bool(difficulty)
        has_language = bool(language)

        return has_topic and has_difficulty and has_language

    def _detect_problem_type_selection(self, message: str) -> Optional[str]:
        """메시지에서 문제 유형 선택 감지"""
        message_lower = message.lower()

        # 빈칸 채우기
        if any(kw in message_lower for kw in ["빈칸", "blank", "빈 칸"]):
            return "blank"

        # 퍼즐
        if any(kw in message_lower for kw in ["퍼즐", "puzzle", "정렬", "코드 정렬"]):
            return "puzzle"

        # 대화형
        if any(kw in message_lower for kw in ["대화형", "1대1", "guided", "가이드", "1:1"]):
            return "guided"

        return None

    def _convert_cached_to_generated(
        self,
        problem_type: str,
        cached_data: dict,
        title: str,
        description: str,
        difficulty: str,
        topics: list,
        input_output: dict,
        final_code: str = None,
    ) -> dict:
        """
        캐시된 DB 데이터를 generated_data 형식으로 변환

        Args:
            problem_type: 문제 유형 (blank, puzzle, guided)
            cached_data: DB에서 가져온 데이터
            title: 문제 제목
            description: 문제 설명
            difficulty: 난이도
            topics: 주제 목록
            input_output: 입출력 예제
            final_code: 정답 코드 (guided용)

        Returns:
            generated_data 형식의 딕셔너리
        """
        base_data = {
            "problem_type": problem_type,
            "original_id": cached_data.get("original_id"),
            "language": cached_data.get("language"),
            "title": title,
            "description": description,
            "difficulty": difficulty,
            "topics": topics,
            "input_output": input_output,
        }

        if problem_type == "blank":
            base_data.update({
                "code_template": cached_data.get("code_template", ""),
                "answers": cached_data.get("answers", []),
            })

        elif problem_type == "puzzle":
            base_data.update({
                "fixed_start": cached_data.get("fixed_start"),
                "fixed_end": cached_data.get("fixed_end"),
                "blocks": cached_data.get("blocks", []),
            })

        elif problem_type == "guided":
            base_data.update({
                "concepts": cached_data.get("concepts", []),
                "flow": cached_data.get("flow", []),
                "checkpoints": cached_data.get("checkpoints", []),
                "final_code": final_code,
            })

        return base_data

    async def _process_problem_type_selection(
        self,
        problem_type: str,
        selected_problem: dict,
        user_context: dict,
    ) -> Dict[str, Any]:
        """
        문제 유형 선택 처리 - 해당 에이전트 호출하여 문제 생성
        """
        from ..services.openrouter import openrouter_service
        from ..prompts import (
            BLANK_PROBLEM_SYSTEM_PROMPT,
            PUZZLE_PROBLEM_SYSTEM_PROMPT,
            GUIDED_PROBLEM_SYSTEM_PROMPT,
        )
        import json

        # 문제 정보 추출
        title = selected_problem.get("title") or selected_problem.get("name", "Problem")
        description = selected_problem.get("description") or selected_problem.get("question", "")
        difficulty = selected_problem.get("difficulty", "medium")
        topics = selected_problem.get("topics") or selected_problem.get("tags", [])
        input_output = selected_problem.get("input_output")

        # 코드 추출
        language = "python"
        code = selected_problem.get("code")
        if not code:
            solutions = selected_problem.get("solutions", [])
            if solutions:
                # python 우선, 없으면 첫 번째
                python_sol = next((s for s in solutions if s.get("language") == "python"), None)
                if python_sol:
                    code = python_sol.get("code", "")
                    language = "python"
                elif solutions:
                    code = solutions[0].get("code", "")
                    language = solutions[0].get("language", "python")

        if not code:
            return {
                "stage": "discovery",
                "response_message": "이 문제에는 솔루션 코드가 없어요. 다른 문제를 선택해주세요!",
                "is_complete": False,
                "action_trigger": "select_problem",
            }

        # original_id 추출 (문자열 ID)
        original_id = selected_problem.get("original_id") or selected_problem.get("name")

        # base_problem_id 추출 (UUID)
        # selected_problem.id가 UUID이면 사용, 아니면 original_id로 조회
        base_problem_id = selected_problem.get("id")
        problem_save_service = get_problem_save_service()

        # base_problem_id가 없거나 UUID 형식이 아니면 조회
        if not base_problem_id or (isinstance(base_problem_id, str) and len(base_problem_id) < 30):
            base_problem_id = problem_save_service.get_base_problem_id(original_id)

        if not base_problem_id:
            print(f"[Orchestrator] Warning: No base_problem_id found for {original_id}")
            # 그래도 진행 (legacy 지원)

        # creator_id 추출
        creator_id = user_context.get("user_id") or user_context.get("id")

        type_labels = {
            "blank": "빈칸 채우기",
            "puzzle": "퍼즐 (코드 정렬)",
            "guided": "1대1 대화형",
        }

        # ============================================================
        # 1. 현재 유저가 이미 이 문제를 가지고 있는지 확인
        # ============================================================
        if base_problem_id and creator_id:
            user_existing = problem_save_service.check_user_has_problem(
                problem_type=problem_type,
                base_problem_id=base_problem_id,
                language=language,
                creator_id=creator_id,
            )

            if user_existing:
                print(f"[Orchestrator] User already has {problem_type}: {original_id} ({language})")

                generated_data = self._convert_cached_to_generated(
                    problem_type=problem_type,
                    cached_data=user_existing,
                    title=title,
                    description=description,
                    difficulty=difficulty,
                    topics=topics,
                    input_output=input_output,
                    final_code=code,
                )

                return {
                    "stage": "problem_generation",
                    "intent": "problem_type_selected",
                    "selected_problem": selected_problem,
                    "generated_problem_data": generated_data,
                    "response_message": f"**{title}** 문제를 **{type_labels.get(problem_type, problem_type)}** 형식으로 준비했어요!\n\n왼쪽 화면에서 문제를 풀어보세요.",
                    "action_trigger": "problem_generated",
                    "action_data": {
                        "problem_type": problem_type,
                        "generated_data": generated_data,
                        "from_cache": True,
                        "user_owned": True,
                    },
                    "next_stage": "solving",
                    "is_complete": True,
                }

        # ============================================================
        # 2. 다른 유저가 만든 문제가 있는지 확인 → 복사
        # ============================================================
        if base_problem_id:
            existing_problem = problem_save_service.find_existing_problem(
                problem_type=problem_type,
                base_problem_id=base_problem_id,
                language=language,
            )

            if existing_problem:
                print(f"[Orchestrator] Cache hit! Copying {problem_type} for user: {original_id} ({language})")

                # 현재 유저용으로 복사
                if creator_id:
                    copy_result = await problem_save_service.copy_problem_for_user(
                        problem_type=problem_type,
                        source_problem=existing_problem,
                        creator_id=creator_id,
                    )
                    if copy_result.get("success"):
                        print(f"[Orchestrator] Problem copied for user {creator_id[:8]}...")

                generated_data = self._convert_cached_to_generated(
                    problem_type=problem_type,
                    cached_data=existing_problem,
                    title=title,
                    description=description,
                    difficulty=difficulty,
                    topics=topics,
                    input_output=input_output,
                    final_code=code,
                )

                return {
                    "stage": "problem_generation",
                    "intent": "problem_type_selected",
                    "selected_problem": selected_problem,
                    "generated_problem_data": generated_data,
                    "response_message": f"**{title}** 문제를 **{type_labels.get(problem_type, problem_type)}** 형식으로 준비했어요!\n\n왼쪽 화면에서 문제를 풀어보세요.",
                    "action_trigger": "problem_generated",
                    "action_data": {
                        "problem_type": problem_type,
                        "generated_data": generated_data,
                        "from_cache": True,
                        "copied": True,
                    },
                    "next_stage": "solving",
                    "is_complete": True,
                }

        # ============================================================
        # 3. Cache Miss: LLM으로 문제 생성
        # ============================================================
        print(f"[Orchestrator] Cache miss. Generating new {problem_type} problem: {original_id} ({language})")

        # 사용자 레벨 추출
        user_level = user_context.get("level", "intermediate")

        # base_problem JSON 구성
        base_problem_json = json.dumps({
            "title": title,
            "description": description,
            "code": code,
            "difficulty": difficulty,
            "topics": topics,
        }, ensure_ascii=False)

        try:
            if problem_type == "blank":
                system_prompt = BLANK_PROBLEM_SYSTEM_PROMPT \
                    .replace("{base_problem}", base_problem_json) \
                    .replace("{user_level}", user_level) \
                    .replace("{language}", language)

                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": "위 문제를 빈칸 채우기 문제로 변환해주세요."},
                ]

                response = await openrouter_service.chat_completion(
                    model="gpt-4o-mini",
                    messages=messages,
                    temperature=0.7,
                    response_format={"type": "json_object"},
                )

                content = openrouter_service.get_content(response)
                result = openrouter_service.parse_json_response(content)

                # 생성된 문제 데이터 구성
                generated_data = {
                    "problem_type": "blank",
                    "original_id": result.get("original_id") or selected_problem.get("id") or selected_problem.get("name"),
                    "language": result.get("language") or language,
                    "code_template": result.get("code_template", ""),
                    "answers": result.get("answers", []),
                    "title": title,
                    "description": description,
                    "difficulty": difficulty,
                    "topics": topics,
                    "input_output": input_output,
                }

            elif problem_type == "puzzle":
                system_prompt = PUZZLE_PROBLEM_SYSTEM_PROMPT \
                    .replace("{base_problem}", base_problem_json) \
                    .replace("{user_level}", user_level) \
                    .replace("{language}", language)

                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": "위 문제를 퍼즐(Parsons) 문제로 변환해주세요."},
                ]

                response = await openrouter_service.chat_completion(
                    model="gpt-4o-mini",
                    messages=messages,
                    temperature=0.7,
                    response_format={"type": "json_object"},
                )

                content = openrouter_service.get_content(response)
                result = openrouter_service.parse_json_response(content)

                generated_data = {
                    "problem_type": "puzzle",
                    "original_id": result.get("original_id") or selected_problem.get("id") or selected_problem.get("name"),
                    "language": result.get("language") or language,
                    "fixed_start": result.get("fixed_start"),
                    "fixed_end": result.get("fixed_end"),
                    "blocks": result.get("blocks", []),
                    "title": title,
                    "description": description,
                    "difficulty": difficulty,
                    "topics": topics,
                    "input_output": input_output,
                }

            else:  # guided
                system_prompt = GUIDED_PROBLEM_SYSTEM_PROMPT \
                    .replace("{base_problem}", base_problem_json) \
                    .replace("{user_level}", user_level) \
                    .replace("{language}", language)

                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": "위 문제를 1대1 대화형 문제로 변환해주세요."},
                ]

                response = await openrouter_service.chat_completion(
                    model="gpt-4o-mini",
                    messages=messages,
                    temperature=0.7,
                    response_format={"type": "json_object"},
                )

                content = openrouter_service.get_content(response)
                result = openrouter_service.parse_json_response(content)

                generated_data = {
                    "problem_type": "guided",
                    "original_id": result.get("original_id") or selected_problem.get("id") or selected_problem.get("name"),
                    "language": result.get("language") or language,
                    "concepts": result.get("concepts", []),
                    "flow": result.get("flow", []),
                    "checkpoints": result.get("checkpoints", []),
                    "final_code": code,  # 원본 코드 포함
                    "title": title,
                    "description": description,
                    "difficulty": difficulty,
                    "topics": topics,
                    "input_output": input_output,
                }

            type_labels = {
                "blank": "빈칸 채우기",
                "puzzle": "퍼즐 (코드 정렬)",
                "guided": "1대1 대화형",
            }

            # DB에 생성된 문제 저장
            try:
                if base_problem_id and creator_id:
                    save_result = await problem_save_service.save_generated_problem(
                        problem_type=problem_type,
                        generated_data=generated_data,
                        base_problem_id=base_problem_id,
                        creator_id=creator_id,
                    )
                    if save_result.get("success"):
                        print(f"[Orchestrator] Problem saved to DB: {problem_type} - {generated_data.get('original_id')} (user: {creator_id[:8]}...)")
                    else:
                        print(f"[Orchestrator] Failed to save problem: {save_result.get('error')}")
                else:
                    print(f"[Orchestrator] Skipping DB save (no base_problem_id or creator_id)")
            except Exception as save_error:
                print(f"[Orchestrator] DB save error (non-blocking): {save_error}")

            return {
                "stage": "problem_generation",
                "intent": "problem_type_selected",
                "selected_problem": selected_problem,
                "generated_problem_data": generated_data,
                "response_message": f"**{title}** 문제를 **{type_labels.get(problem_type, problem_type)}** 형식으로 준비했어요!\n\n왼쪽 화면에서 문제를 풀어보세요.",
                "action_trigger": "problem_generated",
                "action_data": {
                    "problem_type": problem_type,
                    "generated_data": generated_data,
                },
                "next_stage": "solving",
                "is_complete": True,
            }

        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                "stage": "discovery",
                "response_message": f"문제 생성 중 오류가 발생했어요. 다시 시도해주세요.\n\n오류: {str(e)}",
                "is_complete": False,
                "action_trigger": "error",
            }


# ============================================================
# Singleton Instance
# ============================================================

_orchestrator_v2 = None


def get_orchestrator_v2() -> ChatOrchestratorV2:
    """오케스트레이터 V2 싱글톤 반환"""
    global _orchestrator_v2
    if _orchestrator_v2 is None:
        _orchestrator_v2 = ChatOrchestratorV2()
    return _orchestrator_v2


async def process_message_v2(
    message: str,
    conversation_history: list = None,
    user_context: dict = None,
    session_state: dict = None,
) -> Dict[str, Any]:
    """
    편의 함수: 메시지 처리 V2

    Usage:
        result = await process_message_v2(
            message="DP 문제 풀고 싶어",
            user_context={"level": "intermediate"}
        )
    """
    orchestrator = get_orchestrator_v2()
    return await orchestrator.process(
        message=message,
        conversation_history=conversation_history,
        user_context=user_context,
        session_state=session_state,
    )
