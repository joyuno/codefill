"""
LangGraph-based Chat Agents - Tool 기반 구조

[Intent Tool] → [InfoCollectionGraph] → [DiscoveryGraph] → [SolvingGraph]
      │                │                      │                  │
  의도 분류         정보 수집              문제 탐색            문제 풀이
      │                │                      │                  │
      ▼                ▼                      ▼                  ▼
  단일 호출      topic/difficulty/     search/filter/      hint/review/
              language 수집         select               feedback

사용법:
```python
from backend.app.graphs import ChatOrchestratorV2

orchestrator = ChatOrchestratorV2()
result = await orchestrator.process(
    message="DP 문제 풀고 싶어",
    conversation_history=[],
    user_context={}
)
```
"""
# ============================================================
# Main Graphs
# ============================================================

# Discovery Graph (문제 탐색)
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

# Solving Graph (문제 풀이)
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

# Orchestrator V2 (Tool 기반)
from .orchestrator_v2 import (
    ChatOrchestratorV2,
    get_orchestrator_v2,
    process_message_v2,
)

# Info Collection Graph
from .collection import (
    InfoCollectionGraph,
    CollectionState,
    create_info_collection_graph,
)

# ============================================================
# Legacy (호환성 유지)
# ============================================================
from .chat_graph import create_chat_graph, ChatGraph
from .state import ChatState, CONTEXT_REQUIRED_INTENTS, INTENT_TO_NODE

__all__ = [
    # === Main Structure ===
    # Discovery
    "create_discovery_graph",
    "DiscoveryGraph",
    "get_discovery_graph",
    "DiscoveryState",
    "ProblemInfo",
    "DiscoveryCollectedInfo",
    "DISCOVERY_INTENTS",

    # Solving
    "create_solving_graph",
    "ProblemSolvingGraph",
    "get_solving_graph",
    "SolvingState",
    "ProblemContext",
    "UserProgress",
    "SolvingIntentResult",
    "SOLVING_INTENT_TO_NODE",

    # Orchestrator V2
    "ChatOrchestratorV2",
    "get_orchestrator_v2",
    "process_message_v2",

    # Info Collection Graph
    "InfoCollectionGraph",
    "CollectionState",
    "create_info_collection_graph",

    # === Legacy ===
    "create_chat_graph",
    "ChatGraph",
    "ChatState",
    "CONTEXT_REQUIRED_INTENTS",
    "INTENT_TO_NODE",
]
