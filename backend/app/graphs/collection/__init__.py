"""
Stage 1: Info Collection Graph

사용자로부터 문제 검색에 필요한 정보를 수집하는 LangGraph

Flow:
    START → parse_input
              ↓
         [is_question?]
              ├─ Yes → handle_question → (현재 단계 질문으로 돌아감)
              ↓ No
         [current_step?]
              ├─ topic → ask_topic → END
              ├─ difficulty → ask_difficulty → END
              ├─ language → ask_language → END
              └─ complete → complete_collection → END

노드 설명:
- parse_input: 사용자 메시지에서 직접 정보 추출 (LLM 없이 패턴 매칭)
- handle_question: 질문일 경우 LLM으로 답변 생성
- ask_topic: 주제 선택 질문
- ask_difficulty: 난이도 선택 질문
- ask_language: 언어 선택 질문
- complete_collection: 수집 완료, 다음 단계로 라우팅
"""

from .graph import InfoCollectionGraph, create_info_collection_graph
from .state import CollectionState, get_initial_state

__all__ = [
    "InfoCollectionGraph",
    "create_info_collection_graph",
    "CollectionState",
    "get_initial_state",
]
