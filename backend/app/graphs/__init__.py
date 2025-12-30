"""
LangGraph-based Chat Agents - 3단계 구조

[1단계: Intent Graph]     [2단계: Discovery Graph]    [3단계: Solving Graph]
       │                          │                          │
   의도 파악                   문제 탐색                    문제 풀이
       │                          │                          │
       ▼                          ▼                          ▼
┌───────────────┐         ┌───────────────┐         ┌───────────────┐
│classify_intent│         │route_discovery│         │ provide_hint  │
│ route_request │   ──▶   │     ↓         │   ──▶   │ review_code   │
└───────────────┘         │search_problems│         │ check_answer  │
                          │  ↓         ↓  │         │give_feedback  │
                          │filter  generate│         └───────────────┘
                          │  └─────┬─────┘│
                          │handle_selection│
                          │confirm_problem │
                          └───────────────┘

Discovery Graph Flow:
  route_discovery_intent → search_problems → [유사도↑] filter_results ─┐
                                           → [fallback] generate_problem─┴→ handle_selection
                                                                             ↓ (선택됨)
                                                                        confirm_problem → respond

Note: 정보 수집(collect_info)은 InfoCollectionGraph에서 별도 처리

사용법:
```python
from backend.app.graphs import ChatOrchestrator

orchestrator = ChatOrchestrator()
result = await orchestrator.process(
    message="DP 문제 풀고 싶어",
    conversation_history=[],
    user_context={}
)
```
"""
# ============================================================
# 3단계 그래프 구조
# ============================================================

# 1단계: Intent Graph (의도 파악)
from .intent_graph import (
    create_intent_graph,
    IntentGraph,
    get_intent_graph,
)
from .intent_state import (
    IntentState,
    IntentResult,
    CollectedInfo as IntentCollectedInfo,
    INTENT_TO_ROUTE,
    NEEDS_INFO_COLLECTION,
)

# 2단계: Discovery Graph (문제 탐색)
from .discovery_graph import (
    create_discovery_graph,
    DiscoveryGraph,
    get_discovery_graph,
)
from .discovery_state import (
    DiscoveryState,
    ProblemInfo,
    CollectedInfo as DiscoveryCollectedInfo,
    DISCOVERY_INTENTS,
)

# 3단계: Solving Graph (문제 풀이)
from .solving_graph import (
    create_solving_graph,
    ProblemSolvingGraph,
    get_solving_graph,
)
from .solving_state import (
    SolvingState,
    ProblemContext,
    UserProgress,
    SolvingIntentResult,
    SOLVING_INTENT_TO_NODE,
)

# Orchestrator (3단계 연결)
from .orchestrator import (
    ChatOrchestrator,
    get_orchestrator,
    process_message,
)

# Orchestrator V2 (개선된 노드 분리 구조)
from .orchestrator_v2 import (
    ChatOrchestratorV2,
    get_orchestrator_v2,
    process_message_v2,
)

# Info Collection Graph (Stage 1 개선)
from .collection import (
    InfoCollectionGraph,
    CollectionState,
    create_info_collection_graph,
)

# ============================================================
# Legacy (호환성 유지)
# ============================================================

# 기존 ChatGraph (1+2단계 통합 버전)
from .chat_graph import create_chat_graph, ChatGraph
from .state import ChatState

__all__ = [
    # === 3단계 구조 (신규) ===
    # 1단계: Intent
    "create_intent_graph",
    "IntentGraph",
    "get_intent_graph",
    "IntentState",
    "IntentResult",
    "IntentCollectedInfo",
    "INTENT_TO_ROUTE",
    "NEEDS_INFO_COLLECTION",

    # 2단계: Discovery
    "create_discovery_graph",
    "DiscoveryGraph",
    "get_discovery_graph",
    "DiscoveryState",
    "ProblemInfo",
    "DiscoveryCollectedInfo",
    "DISCOVERY_INTENTS",

    # 3단계: Solving
    "create_solving_graph",
    "ProblemSolvingGraph",
    "get_solving_graph",
    "SolvingState",
    "ProblemContext",
    "UserProgress",
    "SolvingIntentResult",
    "SOLVING_INTENT_TO_NODE",

    # Orchestrator
    "ChatOrchestrator",
    "get_orchestrator",
    "process_message",

    # Orchestrator V2 (개선된 구조)
    "ChatOrchestratorV2",
    "get_orchestrator_v2",
    "process_message_v2",

    # Info Collection Graph
    "InfoCollectionGraph",
    "CollectionState",
    "create_info_collection_graph",

    # === Legacy (호환성) ===
    "create_chat_graph",
    "ChatGraph",
    "ChatState",
]
