"""
Discovery Embeddings Service

문제 탐색 단계에서 사용할 임베딩 기반 유사도 매칭 서비스
- 문제 선택 의도 인식 (시맨틱 매칭)
- 검색 결과 재순위
- 액션 의도 인식 (더 찾기, 새 문제 생성 등)

기존 패턴 매칭 + 임베딩 유사도 하이브리드 방식
"""
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import asyncio
import re

from .embedding import embedding_service


@dataclass
class SelectionMatch:
    """문제 선택 매칭 결과"""
    problem_index: int          # 선택된 문제 인덱스 (0-based)
    problem_info: Dict          # 선택된 문제 정보
    similarity: float           # 유사도 점수
    match_type: str             # 매칭 타입 (number, ordinal, semantic, name)


@dataclass
class ActionMatch:
    """액션 의도 매칭 결과"""
    action: str                 # 액션 타입 (more_search, generate_new, select, none)
    confidence: float           # 신뢰도
    matched_pattern: str        # 매칭된 패턴


# ============================================================
# 액션 의도 정의 (정규화된 액션 → 변형 리스트)
# ============================================================

ACTION_VARIANTS: Dict[str, List[str]] = {
    "more_search": [
        "더 찾아줘", "더 보여줘", "다른 거 더", "비슷한 거 더",
        "추가로 찾아", "더 검색해줘", "다른 문제 더", "5개 더",
        "more", "다음", "다음 문제들", "더 많이", "계속 찾아",
        "비슷한 문제 더", "같은 유형 더", "이거 말고 더",
    ],
    "generate_new": [
        "새로 만들어줘", "새 문제 생성", "생성해줘", "만들어줘",
        "새로운 문제 만들어", "직접 만들어", "커스텀 문제",
        "generate", "create", "없으면 만들어", "비슷한 거 만들어",
        "새로운 유형", "안 푼 거 만들어",
    ],
    "change_filter": [
        "난이도 바꿔", "주제 바꿔", "언어 바꿔", "다른 주제로",
        "쉬운 걸로", "어려운 걸로", "파이썬으로", "자바로",
        "DP로 바꿔", "그래프로", "필터 변경", "조건 바꿔",
    ],
    "select_problem": [
        "이거 할게", "이거 풀게", "선택할게", "고를게",
        "해볼게", "풀어볼게", "시작할게", "도전할게",
        "이걸로", "그걸로", "저거", "첫번째", "두번째",
    ],
}

# 숫자/서수 패턴 (빠른 매칭용)
NUMBER_PATTERNS = {
    "1번": 1, "2번": 2, "3번": 3, "4번": 4, "5번": 5,
    "일번": 1, "이번": 2, "삼번": 3, "사번": 4, "오번": 5,
    "1": 1, "2": 2, "3": 3, "4": 4, "5": 5,
}

ORDINAL_PATTERNS = {
    "첫번째": 1, "두번째": 2, "세번째": 3, "네번째": 4, "다섯번째": 5,
    "첫 번째": 1, "두 번째": 2, "세 번째": 3, "네 번째": 4, "다섯 번째": 5,
    "첫": 1, "두": 2, "세": 3, "네": 4, "다섯": 5,
    "first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5,
    "처음": 1, "마지막": 5,  # 마지막은 5개 기준
    # 추가: 위치 기반 표현
    "맨 위": 1, "맨위": 1, "제일 위": 1, "제일위": 1,
    "위에 거": 1, "위에거": 1, "위에 있는 거": 1,
    "맨 아래": 5, "맨아래": 5, "제일 아래": 5,
    "아래 거": 5, "아래거": 5, "아래에 있는 거": 5,
    # 추가: 순서 표현 변형
    "첫째": 1, "둘째": 2, "셋째": 3, "넷째": 4, "다섯째": 5,
    "1번째": 1, "2번째": 2, "3번째": 3, "4번째": 4, "5번째": 5,
}


class DiscoveryEmbeddingsService:
    """
    문제 탐색용 임베딩 서비스

    싱글톤으로 관리되며, 앱 시작 시 초기화
    """

    def __init__(self):
        self._initialized = False
        self._action_embeddings: Dict[str, Tuple[str, np.ndarray]] = {}  # variant → (action, embedding)
        self._action_canonical_embeddings: Dict[str, np.ndarray] = {}    # action → mean embedding

        # 임계값
        self.HIGH_CONFIDENCE = 0.85
        self.MEDIUM_CONFIDENCE = 0.70
        self.LOW_CONFIDENCE = 0.55

    async def initialize(self) -> bool:
        """임베딩 사전 계산 및 초기화"""
        if self._initialized:
            return True

        try:
            print("[DiscoveryEmbeddings] Initializing embeddings...")

            # 액션 임베딩 초기화
            all_variants = []
            variant_to_action = {}

            for action, variants in ACTION_VARIANTS.items():
                for variant in variants:
                    all_variants.append(variant)
                    variant_to_action[variant] = action

            # 배치로 임베딩 생성
            embeddings = await embedding_service.generate_embeddings_batch(all_variants)

            # 변형별 임베딩 저장
            action_vectors: Dict[str, List[np.ndarray]] = {k: [] for k in ACTION_VARIANTS.keys()}

            for variant, embedding in zip(all_variants, embeddings):
                action = variant_to_action[variant]
                emb_array = np.array(embedding)
                self._action_embeddings[variant.lower()] = (action, emb_array)
                action_vectors[action].append(emb_array)

            # 액션별 평균 임베딩 계산
            for action, vectors in action_vectors.items():
                if vectors:
                    self._action_canonical_embeddings[action] = np.mean(vectors, axis=0)

            self._initialized = True
            print(f"[DiscoveryEmbeddings] Initialized: {len(all_variants)} action variants")
            return True

        except Exception as e:
            print(f"[DiscoveryEmbeddings] Initialization failed: {e}")
            return False

    def _compute_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """코사인 유사도 계산"""
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return float(np.dot(vec1, vec2) / (norm1 * norm2))

    async def match_action(self, message: str) -> Optional[ActionMatch]:
        """
        메시지에서 액션 의도 매칭

        Args:
            message: 사용자 메시지

        Returns:
            ActionMatch or None
        """
        message_lower = message.lower().strip()

        # 1. 정확한 키워드 매칭 (O(1))
        if message_lower in self._action_embeddings:
            action, _ = self._action_embeddings[message_lower]
            return ActionMatch(
                action=action,
                confidence=1.0,
                matched_pattern=message_lower,
            )

        # 2. 키워드 포함 확인
        for variant, (action, _) in self._action_embeddings.items():
            if variant in message_lower:
                return ActionMatch(
                    action=action,
                    confidence=0.90,
                    matched_pattern=variant,
                )

        # 3. 임베딩 유사도 비교
        if not self._initialized:
            return None

        try:
            message_embedding = await embedding_service.generate_embedding(message)
            message_vec = np.array(message_embedding)

            best_match: Optional[ActionMatch] = None
            best_similarity = 0.0

            for action, canonical_vec in self._action_canonical_embeddings.items():
                similarity = self._compute_similarity(message_vec, canonical_vec)
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = ActionMatch(
                        action=action,
                        confidence=similarity,
                        matched_pattern=action,
                    )

            if best_match and best_match.confidence >= self.LOW_CONFIDENCE:
                return best_match

            return None

        except Exception as e:
            print(f"[DiscoveryEmbeddings] Action match failed: {e}")
            return None

    async def match_problem_selection(
        self,
        message: str,
        available_problems: List[Dict],
    ) -> Optional[SelectionMatch]:
        """
        메시지에서 문제 선택 매칭

        하이브리드 방식:
        1. 숫자/서수 패턴 (가장 빠름)
        2. 문제 이름 직접 언급
        3. 임베딩 유사도 (문제 제목/설명과 비교)

        Args:
            message: 사용자 메시지
            available_problems: 선택 가능한 문제 목록

        Returns:
            SelectionMatch or None
        """
        if not available_problems:
            return None

        message_lower = message.lower().strip()

        # 1. 숫자 패턴 매칭 ("1번", "2번" 등)
        for pattern, index in NUMBER_PATTERNS.items():
            if pattern in message_lower:
                if 0 < index <= len(available_problems):
                    return SelectionMatch(
                        problem_index=index - 1,
                        problem_info=available_problems[index - 1],
                        similarity=1.0,
                        match_type="number",
                    )

        # 2. 서수 패턴 매칭 ("첫번째", "두번째" 등)
        for pattern, index in ORDINAL_PATTERNS.items():
            if pattern in message_lower:
                if 0 < index <= len(available_problems):
                    return SelectionMatch(
                        problem_index=index - 1,
                        problem_info=available_problems[index - 1],
                        similarity=1.0,
                        match_type="ordinal",
                    )

        # 3. 정규식으로 숫자 추출
        num_match = re.search(r'(\d+)\s*번', message)
        if num_match:
            index = int(num_match.group(1))
            if 0 < index <= len(available_problems):
                return SelectionMatch(
                    problem_index=index - 1,
                    problem_info=available_problems[index - 1],
                    similarity=1.0,
                    match_type="number",
                )

        # 4. 문제 이름 직접 언급 확인
        for i, problem in enumerate(available_problems):
            name = problem.get("name", "").lower()
            title = problem.get("title", "").lower()
            if name and name in message_lower:
                return SelectionMatch(
                    problem_index=i,
                    problem_info=problem,
                    similarity=0.95,
                    match_type="name",
                )
            if title and len(title) > 3 and title in message_lower:
                return SelectionMatch(
                    problem_index=i,
                    problem_info=problem,
                    similarity=0.95,
                    match_type="name",
                )

        # 5. 임베딩 유사도 (문제 제목/설명과 비교)
        # 선택 의도가 있는지 먼저 확인
        selection_keywords = ["할게", "풀게", "선택", "고를", "이거", "그거", "저거", "해볼"]
        has_selection_intent = any(kw in message_lower for kw in selection_keywords)

        if has_selection_intent and self._initialized:
            try:
                message_embedding = await embedding_service.generate_embedding(message)
                message_vec = np.array(message_embedding)

                best_match: Optional[SelectionMatch] = None
                best_similarity = 0.0

                for i, problem in enumerate(available_problems):
                    # 문제 정보로 텍스트 생성
                    problem_text = self._create_problem_text(problem)
                    problem_embedding = await embedding_service.generate_embedding(problem_text)
                    problem_vec = np.array(problem_embedding)

                    similarity = self._compute_similarity(message_vec, problem_vec)
                    if similarity > best_similarity:
                        best_similarity = similarity
                        best_match = SelectionMatch(
                            problem_index=i,
                            problem_info=problem,
                            similarity=similarity,
                            match_type="semantic",
                        )

                if best_match and best_match.similarity >= self.MEDIUM_CONFIDENCE:
                    print(f"[DiscoveryEmbeddings] Semantic selection: {best_match.problem_info.get('title')} (sim={best_match.similarity:.2f})")
                    return best_match

            except Exception as e:
                print(f"[DiscoveryEmbeddings] Selection match failed: {e}")

        # 6. 단순 긍정 응답 + 첫 번째 문제 선택
        affirmation_keywords = ["응", "어", "네", "좋아", "그래", "할게", "풀게", "ㅇㅇ"]
        if any(kw in message_lower for kw in affirmation_keywords):
            return SelectionMatch(
                problem_index=0,
                problem_info=available_problems[0],
                similarity=0.60,
                match_type="affirmation",
            )

        return None

    def _create_problem_text(self, problem: Dict) -> str:
        """문제 정보로 임베딩용 텍스트 생성"""
        parts = []

        if problem.get("title"):
            parts.append(problem["title"])
        if problem.get("name"):
            parts.append(problem["name"])
        if problem.get("description"):
            parts.append(problem["description"][:200])
        if problem.get("question"):
            parts.append(problem["question"][:200])
        if problem.get("topics"):
            parts.extend(problem["topics"][:3])
        if problem.get("tags"):
            parts.extend(problem["tags"][:3])
        if problem.get("difficulty"):
            parts.append(problem["difficulty"])

        return " ".join(parts)

    async def rerank_problems(
        self,
        query: str,
        problems: List[Dict],
        top_k: int = 5,
    ) -> List[Dict]:
        """
        사용자 쿼리와 문제 간 유사도로 재순위

        Args:
            query: 사용자 검색 쿼리
            problems: 검색된 문제 목록
            top_k: 반환할 상위 문제 수

        Returns:
            재순위된 문제 목록
        """
        if not problems or not self._initialized:
            return problems[:top_k]

        try:
            query_embedding = await embedding_service.generate_embedding(query)
            query_vec = np.array(query_embedding)

            # 각 문제에 유사도 점수 추가
            scored_problems = []
            for problem in problems:
                problem_text = self._create_problem_text(problem)
                problem_embedding = await embedding_service.generate_embedding(problem_text)
                problem_vec = np.array(problem_embedding)

                similarity = self._compute_similarity(query_vec, problem_vec)
                scored_problems.append({
                    **problem,
                    "_query_similarity": similarity,
                })

            # 유사도 기준 정렬
            scored_problems.sort(key=lambda x: x.get("_query_similarity", 0), reverse=True)

            # 상위 k개 반환 (유사도 점수 제거)
            result = []
            for p in scored_problems[:top_k]:
                p_copy = {k: v for k, v in p.items() if not k.startswith("_")}
                result.append(p_copy)

            return result

        except Exception as e:
            print(f"[DiscoveryEmbeddings] Rerank failed: {e}")
            return problems[:top_k]

    def is_initialized(self) -> bool:
        """초기화 상태 확인"""
        return self._initialized


# ============================================================
# 싱글톤 인스턴스
# ============================================================

_discovery_embeddings_service: Optional[DiscoveryEmbeddingsService] = None


def get_discovery_embeddings_service() -> DiscoveryEmbeddingsService:
    """싱글톤 인스턴스 반환"""
    global _discovery_embeddings_service
    if _discovery_embeddings_service is None:
        _discovery_embeddings_service = DiscoveryEmbeddingsService()
    return _discovery_embeddings_service


async def initialize_discovery_embeddings() -> bool:
    """앱 시작 시 호출하여 임베딩 초기화"""
    service = get_discovery_embeddings_service()
    return await service.initialize()
