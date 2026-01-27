"""
LangGraph Orchestrator V2 (Tool-based Refactored)

Tool/Function Calling 기반으로 리팩토링:
- intent_tool: 통합 의도 분류 (4단계 → 1단계)
- 중복 분기 로직 제거
- 단순한 라우팅
- Checkpointer 기반 상태 영속화 (PostgresSaver/MemorySaver)

Flow:
    Message → intent_tool.classify() → suggested_route 기반 분기
                ↓
           [category/action에 따라]
                ├─ info_collection → InfoCollectionGraph
                ├─ discovery → DiscoveryGraph
                ├─ solving → SolvingGraph
                └─ general → 직접 응답

============================================================
가드레일 (Guardrails)
============================================================
1. 다중 의도 제한:
   - MAX_INTENTS = 3 (intent_tools.py)
   - 3개 초과 시 사용자에게 안내 메시지 표시
   - Primary 충돌 시 선택 요청 (_process_multi_intents)

2. Moderation API:
   - 유해 콘텐츠 필터링 (별도 미들웨어에서 처리)

============================================================
엣지케이스 목록 (Edge Cases)
============================================================
[Discovery - 문제 탐색]
- EC-D01: 의도 파악 실패 → fallback_clarify_node
- EC-D02: 검색 결과 없음 → search_problems_node에서 "결과 없음" 안내
- EC-D03: 선택 인덱스 범위 초과 → handle_selection_node에서 범위 확인
- EC-D04: 문제 유형 생성 실패 → _process_problem_type_selection에서 에러 처리

[Collection - 정보 수집]
- EC-C01: 입력 파싱 실패 → handle_question_node로 폴백
- EC-C02: 유효하지 않은 주제/난이도/언어 → 임베딩 매칭 실패 시 clarify
- EC-C03: 빈 입력 → 기본 안내 메시지

[Solving - 문제 풀이]
- EC-S01: 의도 파악 실패 → respond_node의 solving_fallback
- EC-S02: 코드 없이 제출 → check_answer에서 검증
- EC-S03: 문제 컨텍스트 없음 → 현재 문제 없음 안내

[Multi-Intent - 다중 의도]
- EC-M01: Primary 충돌 → 선택 요청 메시지
- EC-M02: 의도 초과 → 제한 안내 메시지
- EC-M03: Secondary 응답 생성 실패 → 무시하고 메인만 처리
"""
from typing import Dict, Any, Optional, List
import logging

from .collection import InfoCollectionGraph
from .discovery_graph import DiscoveryGraph
from .solving_graph import ProblemSolvingGraph
from .checkpointer import get_checkpointer, create_thread_config
from ..services.problem_save import get_problem_save_service
from ..services.history_refiner import get_history_refiner
from ..services.edge_case_logger import edge_case_logger
from ..tools.intent_tools import intent_tool, IntentCategory, ActionType, MultiIntentResult
from ..services.langsmith_tracker import track_orchestrator_method

logger = logging.getLogger(__name__)


def normalize_code_newlines(code: str) -> str:
    """DB에 저장된 코드의 이스케이프된 줄바꿈을 실제 줄바꿈으로 변환"""
    if not code:
        return code
    code = code.replace('\\n', '\n')
    code = code.replace('\\t', '\t')
    return code


def extract_problem_name(inquiry_target: str) -> str:
    """
    inquiry_target에서 문제 이름만 추출

    LLM이 파싱을 잘못했을 경우를 대비한 후처리
    예: "시식코너는 나의 것이라는 문제 찾아줘" → "시식코너는 나의 것"

    Note: 검색 결과에 없는 문제를 찾을 때만 적용됨
    """
    import re

    if not inquiry_target:
        return inquiry_target

    # 이미 깨끗한 경우 (숫자만 또는 짧은 문자열)
    if inquiry_target.isdigit() or len(inquiry_target) <= 3:
        return inquiry_target

    # 불필요한 접미사 패턴 제거
    suffix_patterns = [
        r'이?라는\s*문제.*$',  # "~이라는 문제 찾아줘"
        r'\s*문제\s*(찾아줘|알려줘|설명해줘|풀어볼래|있어\??|어때\??).*$',
        r'\s*(찾아줘|알려줘|설명해줘|풀어볼래|보여줘).*$',
        r'\s*에\s*대해.*$',  # "~에 대해 알려줘"
        r'\s*좀\s*(알려줘|찾아줘|설명해줘).*$',
    ]

    result = inquiry_target.strip()
    for pattern in suffix_patterns:
        result = re.sub(pattern, '', result, flags=re.IGNORECASE)

    # 앞뒤 공백 및 따옴표 제거
    result = result.strip().strip('"\'""''')

    return result if result else inquiry_target


def is_target_in_search_results(inquiry_target: str, search_results: list) -> bool:
    """
    inquiry_target이 검색 결과 안에 있는지 확인

    - 숫자/숫자+번 패턴이면 인덱스로 확인 (1-based)
    - 문자열이면 name/title과 부분 매칭
    """
    import re

    if not inquiry_target or not search_results:
        return False

    target = inquiry_target.strip()

    # 숫자 또는 "N번" 패턴 (인덱스)
    num_match = re.match(r'^(\d+)\s*번?$', target)
    if num_match:
        idx = int(num_match.group(1))
        return 1 <= idx <= len(search_results)

    # 문자열인 경우 (문제 이름)
    target_lower = target.lower()
    for result in search_results:
        name = (result.get("name") or "").lower()
        title = (result.get("title") or "").lower()
        # 부분 매칭 허용
        if target_lower in name or target_lower in title or name in target_lower or title in target_lower:
            return True

    return False


class ChatOrchestratorV2:
    """
    Tool 기반 LangGraph 오케스트레이터

    intent_tool.classify() → 단일 호출로 의도/액션 분류
    각 그래프가 명확한 단일 책임을 가짐:
    - InfoCollectionGraph: 정보 수집 (주제/난이도/언어)
    - DiscoveryGraph: 문제 검색/선택
    - SolvingGraph: 문제 풀이 지원

    Checkpointer를 통한 상태 영속화:
    - development: MemorySaver (인메모리)
    - production: PostgresSaver (Supabase PostgreSQL)
    """

    def __init__(self):
        self.collection_graph = InfoCollectionGraph()
        self.discovery_graph = DiscoveryGraph()
        self.solving_graph = ProblemSolvingGraph()
        self.checkpointer = None
        self._initialized = False

    async def initialize(self):
        """
        비동기 초기화 - Checkpointer 설정

        Note: __init__은 동기이므로 별도 초기화 메서드 필요
        """
        if self._initialized:
            return

        try:
            self.checkpointer = await get_checkpointer()
            logger.info("[Orchestrator] Checkpointer initialized")
            self._initialized = True
        except Exception as e:
            logger.error(f"[Orchestrator] Failed to initialize checkpointer: {e}")
            self._initialized = True  # 실패해도 진행 (fallback)

    @track_orchestrator_method("process", tags=["main", "entry"])
    async def process(
        self,
        message: str,
        conversation_history: list = None,
        user_context: dict = None,
        session_state: dict = None,
        session_id: str = None,
    ) -> Dict[str, Any]:
        """
        메시지 처리

        Args:
            message: 사용자 메시지
            conversation_history: 대화 히스토리
            user_context: 사용자 컨텍스트 (온보딩 데이터, 현재 상태 등)
            session_state: 세션 상태 (이전 검색 결과, 수집된 정보 등)
            session_id: 세션 식별자 (Checkpointer용 thread_id)

        Returns:
            {
                stage: 현재 단계,
                intent: 분류된 의도,
                collected_info: 수집된 정보,
                search_results: 검색된 문제,
                response_message: 응답 메시지,
                is_complete: 정보 수집 완료 여부,
                action_trigger: 액션 트리거,
                session_id: 세션 ID (상태 추적용),
            }
        """
        # Checkpointer 초기화 (필요시)
        if not self._initialized:
            await self.initialize()

        conversation_history = conversation_history or []
        user_context = user_context or {}
        session_state = session_state or {}

        # session_id가 없으면 생성
        if not session_id:
            import uuid
            session_id = str(uuid.uuid4())
            logger.debug(f"[Orchestrator] Generated new session_id: {session_id}")

        # 세션에서 이전 상태 복원
        collected_info = session_state.get("collected_info", {})
        search_results = session_state.get("search_results", [])
        selected_problem = session_state.get("selected_problem")
        current_stage = session_state.get("current_stage", "intent")

        # session_state 내부에서 추가 상태 복원 (agent.py에서 저장된 것)
        inner_state = session_state.get("session_state", {}) or {}
        if not search_results and inner_state:
            search_results = inner_state.get("search_results", [])
        pending_action = inner_state.get("action_trigger")  # 이전 응답의 action_trigger (문제 유형 선택 대기 등)

        # ============================================================
        # 🚀 히스토리 정제 (의도 분류 전)
        # - 긴 히스토리를 의도에 맞게 필터링
        # - 중요 컨텍스트 추출
        # ============================================================
        refined_history = None
        history_context = {}
        if len(conversation_history) > 5:
            try:
                history_refiner = get_history_refiner()
                # 의도 분류 전이므로 general로 정제
                refined = await history_refiner.refine(
                    history=conversation_history,
                    intent="general",
                    max_messages=10,
                )
                refined_history = refined.messages
                history_context = refined.context_summary
                logger.debug(
                    f"[Orchestrator] History refined: {refined.original_count} → {refined.refined_count}"
                )
            except Exception as e:
                logger.warning(f"[Orchestrator] History refinement failed: {e}")
                refined_history = conversation_history[-10:]  # fallback

        # 정제된 히스토리 또는 원본 사용 (이후 모든 그래프에서 사용)
        conversation_history = refined_history if refined_history else conversation_history

        # 히스토리에서 추출된 컨텍스트를 collected_info에 병합
        if history_context:
            if history_context.get("topics") and not collected_info.get("topics"):
                collected_info["topics"] = history_context["topics"]
            if history_context.get("difficulty") and not collected_info.get("difficulty"):
                collected_info["difficulty"] = history_context["difficulty"]

        # ============================================================
        # 🚀 Ultra Fast-Path: 칩 클릭 감지 (Intent Classifier 전)
        # - 정확한 키워드 매칭 시 LLM 호출 없이 바로 InfoCollectionGraph로
        # - "?"가 포함되면 질문이므로 LLM 호출 필요
        # ============================================================
        message_stripped = message.strip()
        message_lower = message_stripped.lower()
        is_question_mark = "?" in message

        CHIP_TOPIC_KEYWORDS = {
            "구현": "구현", "정렬": "정렬", "dp": "DP", "DP": "DP",
            "그리디": "그리디", "이분탐색": "이분탐색", "문자열": "문자열",
            "그래프": "그래프", "bfs/dfs": "BFS/DFS", "BFS/DFS": "BFS/DFS",
            "트리": "트리", "수학": "수학", "자료구조": "자료구조",
            "완전탐색": "완전탐색", "백트래킹": "백트래킹", "분할정복": "분할정복",
            "시뮬레이션": "시뮬레이션", "기초": "기초", "최단경로": "최단경로",
            "투포인터": "투포인터", "스택": "스택", "큐": "큐", "힙": "힙",
        }
        CHIP_DIFFICULTY_KEYWORDS = {
            "실버": "easy", "silver": "easy", "easy": "easy", "쉬움": "easy",
            "골드": "medium", "gold": "medium", "medium": "medium", "보통": "medium",
            "플래티넘": "medium_hard", "platinum": "medium_hard",
            "다이아": "hard", "diamond": "hard", "hard": "hard",
            "마스터": "very_hard", "master": "very_hard",
        }
        CHIP_LANGUAGE_KEYWORDS = {
            "파이썬": "python", "python": "python", "Python": "python",
            "자바": "java", "java": "java", "Java": "java",
            "c++": "cpp", "cpp": "cpp", "C++": "cpp",
        }

        # collected_info에서 기존 값 추출
        topics_list = collected_info.get("topics", [])
        existing_topic = topics_list[0] if topics_list and isinstance(topics_list, list) and len(topics_list) > 0 else collected_info.get("topic")
        existing_difficulty = collected_info.get("difficulty")
        existing_language = collected_info.get("language")

        chip_matched_value = None
        chip_matched_step = None

        # "?"가 없을 때만 키워드 매칭 시도
        if not is_question_mark:
            # topic 매칭 (기존 값 없을 때)
            if not existing_topic:
                chip_matched_value = CHIP_TOPIC_KEYWORDS.get(message_stripped) or CHIP_TOPIC_KEYWORDS.get(message_lower)
                if chip_matched_value:
                    chip_matched_step = "topic"

            # difficulty 매칭 (기존 값 없을 때)
            if not chip_matched_value and not existing_difficulty:
                chip_matched_value = CHIP_DIFFICULTY_KEYWORDS.get(message_stripped) or CHIP_DIFFICULTY_KEYWORDS.get(message_lower)
                if chip_matched_value:
                    chip_matched_step = "difficulty"

            # language 매칭 (기존 값 없을 때)
            if not chip_matched_value and not existing_language:
                chip_matched_value = CHIP_LANGUAGE_KEYWORDS.get(message_stripped) or CHIP_LANGUAGE_KEYWORDS.get(message_lower)
                if chip_matched_value:
                    chip_matched_step = "language"

        # 키워드 매칭 성공 → Intent Classifier 건너뛰고 바로 InfoCollectionGraph로
        if chip_matched_value and chip_matched_step:
            logger.info(f"[Orchestrator] ⚡ ULTRA FAST-PATH: {chip_matched_step}={chip_matched_value} (no LLM)")

            # extracted_values 구성
            fast_extracted = {chip_matched_step: chip_matched_value}

            return await self._process_info_collection(
                message=message,
                conversation_history=conversation_history,
                user_context=user_context,
                collected_info=collected_info,
                intent="set_" + chip_matched_step,
                session_state=session_state,
                extracted_values=fast_extracted,
            )

        # ============================================================
        # 통합 Intent Tool로 의도 분류 (다중 의도 지원)
        # ============================================================

        intent_session_state = {
            "current_step": collected_info.get("current_step"),
            "topic": existing_topic,  # topics 배열에서 추출
            "difficulty": collected_info.get("difficulty"),
            "language": collected_info.get("language"),
            "awaiting_confirmation": session_state.get("awaiting_confirmation"),
            "suggested_value": session_state.get("suggested_value"),
            "search_results": search_results,
            "current_problem": user_context.get("current_problem"),
            # 현재 문제 풀이 상황 (빈칸/퍼즐 질문 vs 문제 선택 구분용)
            "current_practice_state": session_state.get("current_practice_state"),
        }

        # ============================================================
        # 🚀 다중 의도 분류 (Multi-Intent Classification)
        # ============================================================
        multi_intent_result = await intent_tool.classify_multi(
            message=message,
            session_state=intent_session_state,
        )

        logger.debug(
            f"MultiIntent: is_multi={multi_intent_result.is_multi_intent}, "
            f"count={multi_intent_result.intent_count}, exceeded={multi_intent_result.exceeded_limit}"
        )

        # ============================================================
        # 다중 의도 제한 초과 시 안내 (가드레일)
        # ============================================================
        if multi_intent_result.exceeded_limit:
            logger.warning(
                f"[Guardrail] Intent limit exceeded: {multi_intent_result.original_intent_count} > MAX_INTENTS"
            )
            # EC-M02: 엣지케이스 로깅
            await edge_case_logger.log(
                code="EC-M02",
                user_id=user_context.get("user_id") if user_context else None,
                session_id=session_id,
                current_node="process",
                user_message=message,
                state_snapshot={
                    "original_intent_count": multi_intent_result.original_intent_count,
                    "processed_count": multi_intent_result.intent_count,
                },
                was_recovered=True,  # 제한된 의도만 처리하므로 복구됨
            )
            # 제한 초과 안내를 포함하여 처리 계속 (제한된 의도만 처리)

        # 다중 의도인 경우 순차 처리
        if multi_intent_result.is_multi_intent and multi_intent_result.intent_count > 1:
            return await self._process_multi_intents(
                multi_intent_result=multi_intent_result,
                message=message,
                conversation_history=conversation_history,
                user_context=user_context,
                session_state=session_state,
                collected_info=collected_info,
                search_results=search_results,
                selected_problem=selected_problem,
            )

        # 단일 의도 처리 (기존 로직)
        intent_result = multi_intent_result.primary_intent
        if not intent_result:
            # fallback: 직접 분류
            intent_result = await intent_tool.classify(message, intent_session_state)

        logger.debug(f"IntentTool: category={intent_result.category}, action={intent_result.action}, route={intent_result.suggested_route}")

        # ============================================================
        # 0. QUICK_START 처리 - 정보 수집 스킵하고 바로 문제 유형 선택
        # ============================================================
        if intent_result.action == ActionType.QUICK_START:
            logger.info("[Orchestrator] QUICK_START detected - skipping info collection")
            return await self._process_quick_start(
                message=message,
                user_context=user_context,
                conversation_history=conversation_history,
            )

        # ============================================================
        # 0-1. 이전 action_trigger 기반 라우팅 (세션 컨텍스트 우선)
        # - select_problem_type: 문제 유형 선택 대기 중
        # ============================================================
        if pending_action == "select_problem_type" and selected_problem:
            # 이전 응답에서 문제 유형 선택을 요청했으므로, 현재 메시지는 유형 선택
            problem_type = await intent_tool.detect_problem_type(message)
            if problem_type:
                logger.info(f"[Orchestrator] Processing problem type selection (from pending_action): {problem_type}")
                return await self._process_problem_type_selection(
                    problem_type=problem_type,
                    selected_problem=selected_problem,
                    user_context=user_context,
                )

        # ============================================================
        # 1. 문제 유형 선택 처리 (빈칸/퍼즐/대화형) - Intent 기반
        # ============================================================
        if intent_result.action == ActionType.SELECT_PROBLEM_TYPE and selected_problem:
            problem_type = await intent_tool.detect_problem_type(message)
            if problem_type:
                return await self._process_problem_type_selection(
                    problem_type=problem_type,
                    selected_problem=selected_problem,
                    user_context=user_context,
                )

        # ============================================================
        # 2. 풀이 중이면 Solving Graph로
        # ============================================================
        if intent_result.category == IntentCategory.SOLVING:
            if user_context.get("current_problem"):
                return await self._process_solving(
                    message=message,
                    problem_context=user_context.get("current_problem"),
                    user_progress=user_context.get("user_progress", {}),
                    conversation_history=conversation_history,
                    previous_hints=session_state.get("previous_hints", []),
                    solving_intent=intent_result.action.value,  # LLM이 분류한 의도 전달
                )

        # ============================================================
        # 3. 확인 응답 (긍정/부정) → InfoCollectionGraph
        # ============================================================
        if intent_result.category == IntentCategory.CONFIRMATION:
            # awaiting_confirmation 상태가 아니어도 확인 응답 처리 시도
            # (프론트엔드에서 상태 전달 누락 대비)
            return await self._process_info_collection(
                message=message,
                conversation_history=conversation_history,
                user_context=user_context,
                collected_info=collected_info,
                intent=intent_result.action.value,
                session_state=session_state,
                extracted_values=intent_result.extracted_values,  # 확인 시 추출된 값 전달
            )

        # ============================================================
        # 4. 문제 선택 → Discovery Graph
        # ============================================================
        if intent_result.action == ActionType.SELECT_PROBLEM and search_results:
            return await self._process_discovery(
                message=message,
                intent="problem_selection",
                collected_info=collected_info,
                conversation_history=conversation_history,
                user_context=user_context,
                search_results=search_results,
                selection_index=intent_result.selection_index,
            )

        # ============================================================
        # 4. INQUIRE_PROBLEM 처리
        # - 파싱을 먼저 적용 (LLM이 전체 문장을 넣었을 수 있음)
        # - 파싱된 결과로 검색 결과 매칭
        # - 검색 결과에 있으면 → 내용 설명 (4-1)
        # - 검색 결과에 없으면 → DB에서 검색 (4-2)
        # ============================================================
        if intent_result.action == ActionType.INQUIRE_PROBLEM and intent_result.inquiry_target:
            # 먼저 파싱 적용 (항상)
            raw_target = intent_result.inquiry_target
            parsed_target = extract_problem_name(raw_target)
            print(f"[Orchestrator] INQUIRE_PROBLEM: parsed='{parsed_target}' (raw='{raw_target}')")

            # 파싱된 결과로 검색 결과 매칭
            target_in_results = is_target_in_search_results(parsed_target, search_results)

            if search_results and target_in_results:
                # 4-1. 검색 결과 안에 있음 → 문제 내용 설명
                print(f"[Orchestrator] Target '{parsed_target}' found in search results → explain content")
                return await self._process_discovery(
                    message=message,
                    intent="inquire_problem",
                    collected_info=collected_info,
                    conversation_history=conversation_history,
                    user_context=user_context,
                    search_results=search_results,
                    inquiry_target=parsed_target,  # 파싱된 값 전달
                    inquiry_question=message,
                )

            # 4-2. 검색 결과에 없음 → DB에서 새로 검색
            print(f"[Orchestrator] Target '{parsed_target}' NOT in search results → search DB")
            from ..services.rag import rag_service

            try:
                results, found_exact = await rag_service.search_problems_by_name(
                    problem_name=parsed_target,  # 이미 파싱된 값 사용
                    similarity_threshold=0.40,
                    limit=5,
                )

                if results:
                    top_result = results[0]
                    similarity = top_result.get("similarity", 0)

                    if similarity >= 0.92:
                        response_msg = f"**{top_result['name']}** 문제를 찾았어요!\n\n난이도: {top_result['difficulty']}\n태그: {', '.join(top_result.get('tags', [])[:3])}\n\n이 문제를 풀어볼까요?"
                        action_trigger = "problem_found"
                    else:
                        response_msg = f"'{parsed_target}'과(와) 비슷한 문제를 찾았어요:\n\n"
                        for i, r in enumerate(results[:3], 1):
                            response_msg += f"{i}. **{r['name']}** ({r['difficulty']})\n"
                        response_msg += "\n원하는 문제가 있으면 선택해주세요!"
                        action_trigger = "problems_searched"

                    return {
                        "stage": "discovery",
                        "intent": "inquire_problem",
                        "collected_info": collected_info,
                        "search_results": results,
                        "response_message": response_msg,
                        "action_trigger": action_trigger,
                        "action_data": {
                            "problems": results,
                            "search_query": parsed_target,
                            "found_exact_match": found_exact,
                        },
                        "next_stage": "respond",
                        "is_complete": True,
                    }
                else:
                    return {
                        "stage": "discovery",
                        "intent": "inquire_problem",
                        "collected_info": collected_info,
                        "response_message": f"'{parsed_target}' 문제를 찾지 못했어요. 다른 이름이나 주제로 검색해볼까요?",
                        "action_trigger": "problem_not_found",
                        "next_stage": "respond",
                        "is_complete": True,
                    }
            except Exception as e:
                print(f"[Orchestrator] Problem name search error: {e}")
                return {
                    "stage": "discovery",
                    "intent": "inquire_problem",
                    "collected_info": collected_info,
                    "response_message": "문제 검색 중 오류가 발생했어요. 다시 시도해주세요.",
                    "action_trigger": "error",
                    "next_stage": "respond",
                    "is_complete": True,
                }

        # ============================================================
        # 5. 정보 수집 필요
        # ============================================================
        if intent_result.category == IntentCategory.INFO_COLLECTION:
            return await self._process_info_collection(
                message=message,
                conversation_history=conversation_history,
                user_context=user_context,
                collected_info=collected_info,
                intent=intent_result.action.value,
                session_state=session_state,
                extracted_values=intent_result.extracted_values,
            )

        # ============================================================
        # 6. Discovery 라우팅 (정보 수집 완료 후)
        # ============================================================
        if intent_result.suggested_route == "discovery":
            # 이미 검색 결과가 있고 더 찾기/새 생성 액션이면 바로 Discovery로
            is_discovery_action = intent_result.action in [ActionType.GENERATE_NEW, ActionType.SHOW_MORE]
            has_search_results = bool(search_results)

            if self._has_sufficient_info(collected_info) or (has_search_results and is_discovery_action):
                return await self._process_discovery(
                    message=message,
                    intent=intent_result.action.value,
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
                    intent=intent_result.action.value,
                    session_state=session_state,
                )

        # ============================================================
        # 6-1. 개념 질문 (검색 결과가 있을 때)
        # 검색 단계에서 알고리즘/자료구조 개념 질문 처리
        # ============================================================
        if intent_result.action == ActionType.FREE_CHAT and search_results:
            # 개념 질문 패턴 감지
            concept_keywords = ["뭐야", "뭐지", "뭔가", "설명", "알려", "차이", "언제", "어떻게", "왜"]
            is_concept_question = any(kw in message for kw in concept_keywords)

            if is_concept_question:
                print(f"[Orchestrator] Concept question detected during discovery: {message}")
                return await self._process_discovery(
                    message=message,
                    intent="concept_explain",
                    collected_info=collected_info,
                    conversation_history=conversation_history,
                    user_context=user_context,
                    search_results=search_results,
                )

        # ============================================================
        # 7. General (인사, 감사, 일반 대화) - LLM 기반 동적 응답
        # ============================================================
        if intent_result.category == IntentCategory.GENERAL:
            from ..services.dynamic_response import dynamic_response_generator

            # 현재 문제 풀이 상황을 user_context에 추가 (dynamic_response에서 활용)
            enriched_user_context = dict(user_context) if user_context else {}
            current_practice_state = session_state.get("current_practice_state", {})
            if current_practice_state:
                enriched_user_context["current_practice_state"] = current_practice_state

            # LLM 기반 동적 응답 생성 (하드코딩 제거)
            dynamic_response = await dynamic_response_generator.generate(
                message=message,
                intent=intent_result.action.value if intent_result.action else "general",
                conversation_history=conversation_history,
                user_context=enriched_user_context,
            )

            return {
                "stage": "intent",
                "intent": intent_result.action.value,
                "collected_info": collected_info,
                "response_message": dynamic_response.message,
                "next_stage": "respond",
                "is_complete": True,
            }

        # ============================================================
        # 8. Fallback: 정보 수집 시작
        # ============================================================
        return await self._process_info_collection(
            message=message,
            conversation_history=conversation_history,
            user_context=user_context,
            collected_info=collected_info,
            intent=intent_result.action.value if intent_result.action else "ask_recommendation",
            session_state=session_state,
        )

    @track_orchestrator_method("_process_quick_start", tags=["quick-start", "skip"])
    async def _process_quick_start(
        self,
        message: str,
        user_context: dict,
        conversation_history: list,
    ) -> Dict[str, Any]:
        """
        QUICK_START 처리 - 정보 수집 단계를 스킵하고 바로 랜덤 문제 검색 후 문제 유형 선택

        사용자가 "빨리 시작하자", "스킵", "귀찮아" 등의 의도를 가질 때
        주제/난이도/언어 선택을 건너뛰고 랜덤으로 문제를 선택함
        """
        from ..tools.user_tools import get_user_tools
        import random

        user_tools = get_user_tools()
        user_id = user_context.get("user_id")

        # 사용자 프로필에서 기본값 가져오기
        experience_level = user_context.get("experience_level", "unknown")
        learning_goal = user_context.get("learning_goal", "unknown")
        preferred_language = user_context.get("preferred_language", "python")

        # 레벨에 따른 기본 난이도
        LEVEL_TO_DIFFICULTY = {
            "beginner": "easy",
            "elementary": "easy",
            "intermediate": "medium",
            "advanced": "hard",
            "unknown": "easy",
        }
        default_difficulty = LEVEL_TO_DIFFICULTY.get(experience_level, "easy")

        # 추천 주제 가져오기 (히스토리 기반 또는 기본)
        recommended_topic = "구현"  # 기본값
        try:
            if user_id:
                history_rec = await user_tools.get_history_based_recommendation(user_id)
                if history_rec.get("success"):
                    recommended_topic = history_rec.get("recommended_topic", "구현")
            else:
                # 비로그인 사용자 → 랜덤 주제
                available_topics = ["구현", "정렬", "문자열", "그리디", "BFS/DFS", "DP"]
                recommended_topic = random.choice(available_topics)
        except Exception as e:
            logger.warning(f"[QuickStart] Failed to get recommendation: {e}")

        # 자동 설정된 정보로 Discovery 호출
        collected_info = {
            "topics": [recommended_topic],
            "difficulty": default_difficulty,
            "language": preferred_language or "python",
        }

        logger.info(f"[QuickStart] Auto-selected: topic={recommended_topic}, difficulty={default_difficulty}, language={preferred_language}")

        # Discovery 그래프로 문제 검색
        result = await self._process_discovery(
            message=message,
            intent="quick_start",
            collected_info=collected_info,
            conversation_history=conversation_history,
            user_context=user_context,
            search_results=[],
        )

        # 응답 메시지에 스킵 안내 추가
        original_message = result.get("response_message", "")
        quick_start_notice = "빠르게 시작할게요! 문제를 찾았어요.\n\n"

        result["response_message"] = quick_start_notice + original_message
        result["is_quick_start"] = True

        return result

    @track_orchestrator_method("_process_info_collection", tags=["collection", "graph"])
    async def _process_info_collection(
        self,
        message: str,
        conversation_history: list,
        user_context: dict,
        collected_info: dict,
        intent: str,
        session_state: dict = None,
        extracted_values: dict = None,
    ) -> Dict[str, Any]:
        """
        InfoCollectionGraph 실행

        topic → difficulty → language 순서로 수집
        네/아니오 응답 대기 상태 지원
        """
        session_state = session_state or {}
        extracted_values = extracted_values or {}

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

        # ============================================================
        # extracted_values 적용 (intent_tool에서 추출한 값 우선 적용)
        # ============================================================
        if extracted_values.get("topic"):
            existing_topic = extracted_values["topic"]
        if extracted_values.get("difficulty"):
            existing_difficulty = extracted_values["difficulty"]
        if extracted_values.get("language"):
            existing_language = extracted_values["language"]

        # 출처 및 생성 관련 필드 추출
        existing_source = collected_info.get("source") or extracted_values.get("source")
        existing_wants_generation = collected_info.get("wants_generation", False) or extracted_values.get("wants_generation", False)
        existing_generation_details = collected_info.get("generation_details") or extracted_values.get("generation_details")
        existing_is_corporate_test = collected_info.get("is_corporate_test", False) or extracted_values.get("is_corporate_test", False)

        if existing_source:
            logger.info(f"[InfoCollection] Source filter detected: {existing_source}")
        if existing_wants_generation:
            logger.info(f"[InfoCollection] Generation requested: details={existing_generation_details}")
        if existing_is_corporate_test:
            logger.info(f"[InfoCollection] Corporate test mode enabled")

        # ============================================================
        # 대화 중 언급된 goal/level 정보를 user_context에 반영
        # "대기업 코테 목표" 같은 메시지에서 추출된 정보
        # ============================================================
        if extracted_values.get("learning_goal"):
            user_context = user_context.copy() if user_context else {}
            user_context["learning_goal"] = extracted_values["learning_goal"]
            logger.debug(f"Updated user_context.learning_goal: {extracted_values['learning_goal']}")

        if extracted_values.get("experience_level"):
            user_context = user_context.copy() if user_context else {}
            user_context["experience_level"] = extracted_values["experience_level"]
            logger.debug(f"Updated user_context.experience_level: {extracted_values['experience_level']}")

        # 디버깅 로그
        logger.debug(f"_process_info_collection: message={message[:50]}...")
        logger.debug(f"collected_info={collected_info}, extracted={extracted_values}")
        logger.debug(f"existing: topic={existing_topic}, difficulty={existing_difficulty}, language={existing_language}")

        # 세션에서 awaiting_confirmation, suggested_value, rejected_values 가져오기
        existing_awaiting_confirmation = session_state.get("awaiting_confirmation", False)
        existing_suggested_value = session_state.get("suggested_value")
        existing_rejected_values = session_state.get("rejected_values", [])

        if existing_rejected_values:
            logger.debug(f"Restoring rejected_values from session: {existing_rejected_values}")

        # InfoCollectionGraph 실행
        result = await self.collection_graph.invoke(
            message=message,
            conversation_history=conversation_history,
            user_context=user_context,
            existing_topic=existing_topic,
            existing_difficulty=existing_difficulty,
            existing_language=existing_language,
            existing_awaiting_confirmation=existing_awaiting_confirmation,
            existing_suggested_value=existing_suggested_value,
            existing_rejected_values=existing_rejected_values,
            # 출처 및 생성 관련 필드
            existing_source=existing_source,
            existing_wants_generation=existing_wants_generation,
            existing_generation_details=existing_generation_details,
            existing_is_corporate_test=existing_is_corporate_test,
        )

        # 수집된 정보 병합
        new_collected = result.get("collected_info", {})
        merged_info = {
            "topics": [new_collected.get("topic")] if new_collected.get("topic") else collected_info.get("topics", []),
            "difficulty": new_collected.get("difficulty") or collected_info.get("difficulty"),
            "language": new_collected.get("language") or collected_info.get("language"),
            # 출처 및 생성 관련 필드
            "source": new_collected.get("source") or existing_source,
            "wants_generation": new_collected.get("wants_generation", False) or existing_wants_generation,
            "generation_details": new_collected.get("generation_details") or existing_generation_details,
            "is_corporate_test": new_collected.get("is_corporate_test", False) or existing_is_corporate_test,
        }
        logger.debug(f"Info merge: new={new_collected}, original={collected_info}, merged={merged_info}")

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

        # 응답에 awaiting_confirmation, suggested_value, rejected_values 포함
        return {
            "stage": "collection",
            "intent": intent,
            "collected_info": merged_info,
            "response_message": result.get("message", ""),
            "next_stage": "collection",
            "is_complete": False,
            # 네/아니오 칩용 정보
            "awaiting_confirmation": result.get("awaiting_confirmation", False),
            "suggested_value": result.get("suggested_value"),
            "action_data": result.get("action_data"),
            # 거절된 값 추적 (다음 턴에서 재추천 방지)
            "rejected_values": result.get("rejected_values", []),
        }

    @track_orchestrator_method("_process_discovery", tags=["discovery", "graph"])
    async def _process_discovery(
        self,
        message: str,
        intent: str,
        collected_info: dict,
        conversation_history: list,
        user_context: dict,
        search_results: list,
        selection_index: int = None,
        inquiry_target: str = None,
        inquiry_question: str = None,
    ) -> Dict[str, Any]:
        """Discovery 그래프 실행"""
        # ============================================================
        # difficulty가 None일 때 사용자 레벨 기반으로 자동 설정
        # 이를 통해 검색 시 difficulty=None 문제 방지
        # ============================================================
        if not collected_info.get("difficulty"):
            experience_level = user_context.get("experience_level", "unknown")
            LEVEL_TO_DIFFICULTY = {
                "beginner": "easy",
                "elementary": "easy",
                "intermediate": "medium",
                "advanced": "hard",
                "unknown": "easy",
            }
            auto_difficulty = LEVEL_TO_DIFFICULTY.get(experience_level, "easy")
            collected_info["difficulty"] = auto_difficulty
            logger.info(f"[Discovery] Auto-set difficulty: {experience_level} → {auto_difficulty}")

        result = await self.discovery_graph.invoke(
            message=message,
            collected_info=collected_info,
            intent=intent,
            conversation_history=conversation_history,
            user_context=user_context,
            search_results=search_results,
            selection_index=selection_index,
            inquiry_target=inquiry_target,
            inquiry_question=inquiry_question,
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
            "chips": result.get("chips"),  # 문제 유형 선택 칩 등
            "next_stage": result.get("route_to", "respond"),
            "is_complete": result.get("is_confirmed", False),
        }

    @track_orchestrator_method("_process_solving", tags=["solving", "graph"])
    async def _process_solving(
        self,
        message: str,
        problem_context: dict,
        user_progress: dict,
        conversation_history: list,
        previous_hints: list,
        solving_intent: str = None,
    ) -> Dict[str, Any]:
        """Solving 그래프 실행"""
        result = await self.solving_graph.invoke(
            message=message,
            problem_context=problem_context,
            user_progress=user_progress,
            conversation_history=conversation_history,
            previous_hints=previous_hints,
            solving_intent=solving_intent,  # orchestrator에서 분류한 의도
        )

        return {
            "stage": "solving",
            "response_message": result.get("response_message", ""),
            "hint_level": result.get("hint_level"),
            "is_correct": result.get("is_correct"),
            "next_stage": result.get("route_to", "solving"),
            "is_complete": result.get("is_complete", False),
        }

    # ============================================================
    # 다중 의도 병합 처리 (Multi-Intent Merged Processing)
    # ============================================================

    # Primary 의도: 메인 분기를 결정하는 의도
    PRIMARY_ACTIONS = {
        # info_collection
        "set_topic", "set_difficulty", "set_language", "ask_recommendation", "quick_start",
        # discovery
        "select_problem", "show_more", "generate_new", "select_problem_type", "inquire_problem",
        # solving
        "request_hint", "submit_code", "give_up", "chat_assist", "concept_explain",
        "approach_hint", "code_review", "ask_question",
    }

    # Secondary 의도: 메인 분기에 병합 가능한 의도
    SECONDARY_ACTIONS = {
        "greeting", "thanks", "help", "free_chat",
        "progress_check", "weak_point", "study_plan",
        "affirm", "negate",
    }

    @track_orchestrator_method("_process_multi_intents", tags=["multi-intent", "router"])
    async def _process_multi_intents(
        self,
        multi_intent_result: MultiIntentResult,
        message: str,
        conversation_history: list,
        user_context: dict,
        session_state: dict,
        collected_info: dict,
        search_results: list,
        selected_problem: dict,
    ) -> Dict[str, Any]:
        """
        다중 의도 병합 처리

        여러 의도가 감지된 경우:
        1. Primary/Secondary 분류
        2. Primary가 1개 → 메인 분기로 처리, Secondary는 응답에 병합
        3. Primary가 2개 이상 → 충돌 안내 (한 번에 하나씩)
        4. Primary 없음 → Secondary 순차 병합

        Args:
            multi_intent_result: 다중 의도 분류 결과
            기타: 컨텍스트 정보

        Returns:
            병합된 처리 결과
        """
        intents = multi_intent_result.intents
        logger.info(f"[MultiIntent] Processing {len(intents)} intents with merge strategy")

        # ============================================================
        # 1. Primary / Secondary 분류
        # ============================================================
        primary_intents = []
        secondary_intents = []

        for intent in intents:
            action = intent.action.value if intent.action else "free_chat"
            if action in self.PRIMARY_ACTIONS:
                primary_intents.append(intent)
            else:
                secondary_intents.append(intent)

        logger.info(
            f"[MultiIntent] Classified: primary={len(primary_intents)}, "
            f"secondary={len(secondary_intents)}"
        )

        # ============================================================
        # 2. Primary 충돌 체크 (2개 이상의 다른 분기)
        # ============================================================
        if len(primary_intents) >= 2:
            # 같은 카테고리인지 확인
            categories = set(i.category.value for i in primary_intents)
            if len(categories) > 1:
                # 다른 분기로 가는 primary가 2개 이상 → 충돌 안내
                actions_str = ", ".join([i.action.value for i in primary_intents])

                # EC-M01: Primary 충돌 로깅
                await edge_case_logger.log(
                    code="EC-M01",
                    user_id=user_context.get("user_id") if user_context else None,
                    session_id=session_state.get("session_id") if session_state else None,
                    current_node="_process_multi_intents",
                    user_message=message,
                    state_snapshot={
                        "primary_count": len(primary_intents),
                        "categories": list(categories),
                        "actions": actions_str,
                    },
                    fallback_triggered=True,
                    response_message="충돌 안내 메시지 표시",
                )

                return {
                    "stage": "intent",
                    "response_message": (
                        f"여러 요청이 감지됐어요: **{actions_str}**\n\n"
                        "한 번에 하나씩 처리할게요! 먼저 어떤 걸 도와드릴까요?\n"
                        "1. 문제 검색/추천\n"
                        "2. 진행 상황/통계 확인"
                    ),
                    "is_multi_intent": True,
                    "multi_intent_conflict": True,
                    "detected_intents": [
                        {"action": i.action.value, "category": i.category.value}
                        for i in intents
                    ],
                    "is_complete": False,
                }

        # ============================================================
        # 3. 메인 분기 결정 및 처리
        # ============================================================
        main_intent = primary_intents[0] if primary_intents else (secondary_intents[0] if secondary_intents else intents[0])

        # 메인 의도 처리
        main_result = await self._process_single_intent(
            intent_result=main_intent,
            message=message,
            conversation_history=conversation_history,
            user_context=user_context,
            session_state=session_state,
            collected_info=collected_info,
            search_results=search_results,
            selected_problem=selected_problem,
        )

        # ============================================================
        # 4. Secondary 의도 응답 병합
        # ============================================================
        if secondary_intents:
            merged_responses = await self._generate_secondary_responses(
                secondary_intents=secondary_intents,
                user_context=user_context,
                conversation_history=conversation_history,
            )

            if merged_responses:
                # 메인 응답 앞에 secondary 응답 추가
                original_response = main_result.get("response_message", "")
                merged_text = "\n".join(merged_responses)
                main_result["response_message"] = f"{merged_text}\n\n---\n\n{original_response}"

        # ============================================================
        # 5. 다중 의도 메타데이터 추가
        # ============================================================
        main_result["is_multi_intent"] = True
        main_result["total_intents"] = len(intents)
        main_result["processed_intents"] = [
            {"action": i.action.value, "category": i.category.value}
            for i in intents
        ]

        # ============================================================
        # 6. 의도 제한 초과 시 안내 메시지 추가 (가드레일)
        # ============================================================
        if multi_intent_result.exceeded_limit:
            exceeded_count = multi_intent_result.original_intent_count
            processed_count = multi_intent_result.intent_count
            limit_notice = (
                f"\n\n---\n💡 **참고**: {exceeded_count}개의 요청이 감지되었지만, "
                f"한 번에 {processed_count}개까지만 처리할 수 있어요. "
                f"나머지는 다음에 말씀해주세요!"
            )
            main_result["response_message"] = main_result.get("response_message", "") + limit_notice
            main_result["exceeded_intent_limit"] = True
            main_result["original_intent_count"] = exceeded_count

        logger.info(
            f"[MultiIntent] Merged response: main={main_intent.action.value}, "
            f"secondary_merged={len(secondary_intents)}, exceeded={multi_intent_result.exceeded_limit}"
        )

        return main_result

    async def _generate_secondary_responses(
        self,
        secondary_intents: list,
        user_context: dict,
        conversation_history: list,
    ) -> list:
        """
        Secondary 의도들에 대한 간단한 응답 생성

        메인 응답에 병합될 짧은 응답들
        실제 user_stats 테이블 조회하여 정확한 레벨/통계 정보 제공
        """
        from ..services.dynamic_response import dynamic_response_generator
        from ..tools.user_tools import get_user_tools

        responses = []
        user_id = user_context.get("user_id")

        # user_stats 조회 (progress_check, weak_point에서 사용)
        user_profile = None
        if user_id:
            try:
                user_tools = get_user_tools()
                profile_result = await user_tools.get_user_profile(user_id)
                if profile_result.success:
                    user_profile = profile_result
                    logger.debug(f"[MultiIntent] User profile loaded: level={user_profile.level}, solved={user_profile.problems_solved}")
            except Exception as e:
                logger.warning(f"[MultiIntent] Failed to fetch user profile: {e}")

        for intent in secondary_intents:
            action = intent.action.value if intent.action else "free_chat"

            try:
                if action == "progress_check":
                    # 실제 user_stats 테이블에서 조회한 데이터 사용
                    if user_profile:
                        level = user_profile.level
                        total_xp = user_profile.total_xp
                        solved = user_profile.problems_solved
                        exp_level = user_profile.experience_level

                        # 경험 레벨 한글 표시
                        exp_display = {
                            "beginner": "입문자",
                            "elementary": "초급자",
                            "intermediate": "중급자",
                            "advanced": "고급자",
                        }.get(exp_level, "")

                        if exp_display:
                            responses.append(
                                f"📊 **현재 레벨**: Lv.{level} ({exp_display}) | "
                                f"{solved}문제 풀이 | {total_xp:,} XP"
                            )
                        else:
                            responses.append(
                                f"📊 **현재 레벨**: Lv.{level} | "
                                f"{solved}문제 풀이 | {total_xp:,} XP"
                            )
                    else:
                        responses.append("📊 **진행 상황**: 로그인하면 상세 통계를 볼 수 있어요!")

                elif action == "weak_point":
                    # 약점 분석 - personalization 컨텍스트에서 가져오거나 안내
                    personalization = user_context.get("personalization", {})
                    skill_summary = personalization.get("skill_summary", {})
                    weak = skill_summary.get("weak_topics", [])

                    if weak:
                        responses.append(f"📈 **약점 분석**: {', '.join(weak[:3])} 연습이 필요해요!")
                    elif user_profile and user_profile.problems_solved >= 5:
                        responses.append("📈 **약점 분석**: 분석 페이지에서 상세 내용을 확인해보세요!")
                    else:
                        responses.append("📈 **약점 분석**: 5문제 이상 풀면 약점을 분석해드릴게요!")

                elif action == "greeting":
                    responses.append("안녕하세요! 👋")

                elif action == "thanks":
                    responses.append("천만에요! 😊")

                elif action == "study_plan":
                    # 학습 계획은 분석 페이지로 안내
                    if user_profile:
                        goal = user_profile.learning_goal
                        goal_display = {
                            "big_tech": "대기업 코테",
                            "mid_startup": "스타트업 취업",
                            "skill_up": "실력 향상",
                        }.get(goal, "")

                        if goal_display:
                            responses.append(f"📚 **학습 목표**: {goal_display} 준비 중! 분석 페이지에서 맞춤 계획을 확인해보세요.")
                        else:
                            responses.append("📚 **학습 계획**: 프로필에서 학습 목표를 설정하면 맞춤 계획을 제공해드려요!")
                    else:
                        responses.append("📚 **학습 계획**: 로그인하면 맞춤 학습 계획을 받을 수 있어요!")

                else:
                    # 기타 secondary는 동적 응답 생성
                    dynamic_resp = await dynamic_response_generator.generate(
                        message="",
                        intent=action,
                        conversation_history=conversation_history[-3:],
                        user_context=user_context,
                    )
                    if dynamic_resp.message:
                        responses.append(dynamic_resp.message)

            except Exception as e:
                logger.warning(f"[MultiIntent] Failed to generate secondary response for {action}: {e}")
                continue

        return responses

    async def _process_single_intent(
        self,
        intent_result,
        message: str,
        conversation_history: list,
        user_context: dict,
        session_state: dict,
        collected_info: dict,
        search_results: list,
        selected_problem: dict,
    ) -> Dict[str, Any]:
        """
        단일 의도 처리 (기존 라우팅 로직 재사용)

        다중 의도 처리에서 각 의도를 개별 처리할 때 사용
        """
        from ..services.dynamic_response import dynamic_response_generator

        # ============================================================
        # 카테고리별 라우팅
        # ============================================================

        # 0. Quick Start (정보 수집 스킵)
        if intent_result.action == ActionType.QUICK_START:
            return await self._process_quick_start(
                message=message,
                user_context=user_context,
                conversation_history=conversation_history,
            )

        # 1. Solving
        if intent_result.category == IntentCategory.SOLVING:
            if user_context.get("current_problem"):
                return await self._process_solving(
                    message=message,
                    problem_context=user_context.get("current_problem"),
                    user_progress=user_context.get("user_progress", {}),
                    conversation_history=conversation_history,
                    previous_hints=session_state.get("previous_hints", []),
                    solving_intent=intent_result.action.value,
                )
            # 문제 없으면 안내
            return {
                "stage": "respond",
                "response_message": "이 기능을 사용하려면 먼저 문제를 선택해주세요!",
                "is_complete": False,
            }

        # 2. Confirmation
        if intent_result.category == IntentCategory.CONFIRMATION:
            return await self._process_info_collection(
                message=message,
                conversation_history=conversation_history,
                user_context=user_context,
                collected_info=collected_info,
                intent=intent_result.action.value,
                session_state=session_state,
                extracted_values=intent_result.extracted_values,
            )

        # 3. Discovery - 문제 선택
        if intent_result.action == ActionType.SELECT_PROBLEM and search_results:
            return await self._process_discovery(
                message=message,
                intent="problem_selection",
                collected_info=collected_info,
                conversation_history=conversation_history,
                user_context=user_context,
                search_results=search_results,
                selection_index=intent_result.selection_index,
            )

        # 4. Discovery - 문제 질문
        if intent_result.action == ActionType.INQUIRE_PROBLEM and search_results:
            return await self._process_discovery(
                message=message,
                intent="inquire_problem",
                collected_info=collected_info,
                conversation_history=conversation_history,
                user_context=user_context,
                search_results=search_results,
                inquiry_target=intent_result.inquiry_target,
                inquiry_question=message,
            )

        # 5. Info Collection
        if intent_result.category == IntentCategory.INFO_COLLECTION:
            return await self._process_info_collection(
                message=message,
                conversation_history=conversation_history,
                user_context=user_context,
                collected_info=collected_info,
                intent=intent_result.action.value,
                session_state=session_state,
                extracted_values=intent_result.extracted_values,
            )

        # 6. Discovery 라우팅
        if intent_result.suggested_route == "discovery":
            if self._has_sufficient_info(collected_info):
                return await self._process_discovery(
                    message=message,
                    intent=intent_result.action.value,
                    collected_info=collected_info,
                    conversation_history=conversation_history,
                    user_context=user_context,
                    search_results=search_results,
                )
            else:
                return await self._process_info_collection(
                    message=message,
                    conversation_history=conversation_history,
                    user_context=user_context,
                    collected_info=collected_info,
                    intent=intent_result.action.value,
                    session_state=session_state,
                )

        # 7. General (인사, 감사, 진행상황 등)
        if intent_result.category == IntentCategory.GENERAL:
            dynamic_response = await dynamic_response_generator.generate(
                message=message,
                intent=intent_result.action.value if intent_result.action else "general",
                conversation_history=conversation_history,
                user_context=user_context,
            )

            return {
                "stage": "intent",
                "intent": intent_result.action.value,
                "collected_info": collected_info,
                "response_message": dynamic_response.message,
                "next_stage": "respond",
                "is_complete": True,
            }

        # 8. Fallback
        return await self._process_info_collection(
            message=message,
            conversation_history=conversation_history,
            user_context=user_context,
            collected_info=collected_info,
            intent=intent_result.action.value if intent_result.action else "ask_recommendation",
            session_state=session_state,
        )

    async def process_pending_intent(
        self,
        pending_intent: dict,
        conversation_history: list = None,
        user_context: dict = None,
        session_state: dict = None,
    ) -> Dict[str, Any]:
        """
        대기 중인 의도 처리

        클라이언트에서 pending_intents를 받아 순차적으로 처리할 때 호출

        Args:
            pending_intent: 직렬화된 의도 정보
            conversation_history: 대화 히스토리
            user_context: 사용자 컨텍스트
            session_state: 세션 상태

        Returns:
            처리 결과
        """
        from ..tools.intent_tools import IntentResult, IntentCategory, ActionType

        conversation_history = conversation_history or []
        user_context = user_context or {}
        session_state = session_state or {}

        # 직렬화된 의도를 IntentResult로 복원
        try:
            intent_result = IntentResult(
                category=IntentCategory(pending_intent.get("category", "general")),
                action=ActionType(pending_intent.get("action", "free_chat")),
                confidence=pending_intent.get("confidence", 0.7),
                extracted_values=pending_intent.get("extracted_values", {}),
                suggested_route=pending_intent.get("suggested_route"),
            )
        except (ValueError, KeyError) as e:
            logger.error(f"[MultiIntent] Failed to restore pending intent: {e}")
            return {
                "stage": "error",
                "response_message": "대기 중인 요청을 처리하는데 실패했습니다.",
                "is_complete": False,
            }

        # 세션 상태에서 정보 추출
        collected_info = session_state.get("collected_info", {})
        search_results = session_state.get("search_results", [])
        selected_problem = session_state.get("selected_problem")

        # 의도 처리
        result = await self._process_single_intent(
            intent_result=intent_result,
            message=f"[자동 처리] {intent_result.action.value}",
            conversation_history=conversation_history,
            user_context=user_context,
            session_state=session_state,
            collected_info=collected_info,
            search_results=search_results,
            selected_problem=selected_problem,
        )

        # pending intent 처리 표시
        result["from_pending_intent"] = True
        result["processed_action"] = pending_intent.get("action")

        return result

    def _has_sufficient_info(self, collected_info: dict) -> bool:
        """정보 수집이 충분한지 확인"""
        topics = collected_info.get("topics")
        difficulty = collected_info.get("difficulty")
        language = collected_info.get("language")

        has_topic = topics and isinstance(topics, list) and len(topics) > 0
        has_difficulty = bool(difficulty)
        has_language = bool(language)

        return has_topic and has_difficulty and has_language

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
            # 새 스키마 (2026-01-12 리팩토링)
            base_data.update({
                "concept_explanation": cached_data.get("concept_explanation", ""),
                "variables_guide": cached_data.get("variables_guide", {}),
                "approach_guide": cached_data.get("approach_guide", ""),
                "starter_code": cached_data.get("starter_code", ""),
                "final_code": final_code,
            })

        return base_data

    @track_orchestrator_method("_process_problem_type_selection", tags=["problem-gen", "llm"])
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

        # input_output이 JSON 문자열인 경우 파싱
        input_output = selected_problem.get("input_output")
        if isinstance(input_output, str):
            try:
                input_output = json.loads(input_output)
            except (json.JSONDecodeError, TypeError):
                input_output = None

        # tags가 JSON 문자열인 경우 파싱
        if isinstance(topics, str):
            try:
                topics = json.loads(topics)
            except (json.JSONDecodeError, TypeError):
                topics = []

        # 코드 추출
        language = "python"
        code = selected_problem.get("code")
        if not code:
            solutions = selected_problem.get("solutions", [])
            if solutions:
                # python 우선, 없으면 첫 번째
                python_sol = next((s for s in solutions if s.get("language") == "python"), None)
                if python_sol:
                    code = normalize_code_newlines(python_sol.get("code", ""))
                    language = "python"
                elif solutions:
                    code = normalize_code_newlines(solutions[0].get("code", ""))
                    language = solutions[0].get("language", "python")

        # code 필드에서 직접 가져온 경우도 정규화
        if code:
            code = normalize_code_newlines(code)

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
            logger.warning(f"No base_problem_id found for {original_id}")
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
                logger.debug(f"User already has {problem_type}: {original_id} ({language})")

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
                logger.debug(f"Cache hit! Copying {problem_type} for user: {original_id} ({language})")

                # 현재 유저용으로 복사
                if creator_id:
                    copy_result = await problem_save_service.copy_problem_for_user(
                        problem_type=problem_type,
                        source_problem=existing_problem,
                        creator_id=creator_id,
                    )
                    if copy_result.get("success"):
                        logger.debug(f"Problem copied for user {creator_id[:8]}...")

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
        logger.info(f"Cache miss. Generating new {problem_type}: {original_id} ({language})")

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

                # 새 스키마 (2026-01-12 리팩토링)
                generated_data = {
                    "problem_type": "guided",
                    "original_id": result.get("original_id") or selected_problem.get("id") or selected_problem.get("name"),
                    "language": result.get("language") or language,
                    # 새 스키마 필드
                    "concept_explanation": result.get("concept_explanation", ""),
                    "variables_guide": result.get("variables_guide", {}),
                    "approach_guide": result.get("approach_guide", ""),
                    "starter_code": result.get("starter_code", ""),
                    # 추가 정보
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
                        logger.debug(f"Problem saved: {problem_type} - {generated_data.get('original_id')}")
                    else:
                        logger.warning(f"Failed to save problem: {save_result.get('error')}")
                else:
                    logger.debug("Skipping DB save (no base_problem_id or creator_id)")
            except Exception as save_error:
                logger.warning(f"DB save error (non-blocking): {save_error}")

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


async def initialize_orchestrator():
    """오케스트레이터 비동기 초기화 (앱 시작 시 호출)"""
    orchestrator = get_orchestrator_v2()
    await orchestrator.initialize()
    return orchestrator


async def process_message_v2(
    message: str,
    conversation_history: list = None,
    user_context: dict = None,
    session_state: dict = None,
    session_id: str = None,
) -> Dict[str, Any]:
    """
    편의 함수: 메시지 처리 V2

    Usage:
        result = await process_message_v2(
            message="DP 문제 풀고 싶어",
            user_context={"level": "intermediate"},
            session_id="user-123-session-456"
        )
    """
    orchestrator = get_orchestrator_v2()
    return await orchestrator.process(
        message=message,
        conversation_history=conversation_history,
        user_context=user_context,
        session_state=session_state,
        session_id=session_id,
    )
