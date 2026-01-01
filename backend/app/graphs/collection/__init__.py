"""
Stage 1: Info Collection Graph

사용자로부터 문제 검색에 필요한 정보를 수집하는 LangGraph

Flow:
    START → parse_input
              ↓
         [is_question?]
              ├─ Yes → handle_question → END (awaiting_confirmation)
              ↓ No
         [current_step?]
              ├─ topic → choose_topic → END
              ├─ difficulty → choose_difficulty → END
              ├─ language → choose_language → END
              └─ complete → complete_collection → END

노드 설명:
- parse_input: collection_tool로 값 추출/확인 분석
- handle_question: 질문일 경우 LLM으로 답변 생성 + 추천값 제안
- choose_*: 직접 선택 확정 + 다음 단계 질문
- complete_collection: 수집 완료, Discovery로 라우팅
"""

from .graph import InfoCollectionGraph, create_info_collection_graph
from .state import CollectionState, get_initial_state

__all__ = [
    "InfoCollectionGraph",
    "create_info_collection_graph",
    "CollectionState",
    "get_initial_state",
]
