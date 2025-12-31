"""
Collection Embeddings Service

정보 수집 단계에서 사용할 임베딩 기반 유사도 매칭 서비스
- 주제(topic), 난이도(difficulty), 언어(language) 임베딩 사전 계산
- 유저 입력과 유사도 비교로 가장 적합한 값 반환

기존 키워드 매칭 대신 임베딩 유사도로 분기 결정
"""
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import asyncio

from .embedding import embedding_service


@dataclass
class EmbeddingMatch:
    """임베딩 매칭 결과"""
    value: str              # 정규화된 값 (예: "DP", "easy", "python")
    similarity: float       # 유사도 점수 (0~1)
    matched_variant: str    # 매칭된 변형 (예: "다이나믹 프로그래밍")


# ============================================================
# 정규화된 값과 변형 정의
# ============================================================

# 주제: 정규화된 값 → 변형 리스트 (한글/영어/약어 등)
TOPIC_VARIANTS: Dict[str, List[str]] = {
    "DP": [
        "DP", "dp", "Dynamic Programming", "다이나믹 프로그래밍",
        "동적 프로그래밍", "동적계획법", "다이나믹", "동적", "메모이제이션",
        "Memoization", "탑다운", "바텀업", "점화식"
    ],
    "그래프": [
        "그래프", "Graph", "graph", "그래프 탐색", "그래프 알고리즘",
        "Graph traversal", "노드", "간선", "정점", "edge", "vertex"
    ],
    "BFS/DFS": [
        "BFS", "DFS", "bfs", "dfs", "너비우선탐색", "깊이우선탐색",
        "너비 우선", "깊이 우선", "Breadth First", "Depth First",
        "탐색", "search", "트리 탐색"
    ],
    "정렬": [
        "정렬", "Sort", "sort", "Sorting", "sorting", "소팅",
        "버블정렬", "퀵정렬", "병합정렬", "힙정렬", "삽입정렬",
        "Bubble sort", "Quick sort", "Merge sort", "Heap sort"
    ],
    "이분탐색": [
        "이분탐색", "이진탐색", "Binary Search", "binary search",
        "이분 탐색", "이진 탐색", "바이너리 서치", "parametric search",
        "파라메트릭"
    ],
    "그리디": [
        "그리디", "Greedy", "greedy", "탐욕", "탐욕법", "탐욕 알고리즘",
        "Greedy algorithm", "욕심쟁이"
    ],
    "구현": [
        "구현", "Implementation", "implementation", "시뮬레이션",
        "Simulation", "simulation", "브루트포스", "Brute force",
        "완전탐색", "완전 탐색"
    ],
    "문자열": [
        "문자열", "String", "string", "스트링", "문자열 처리",
        "String manipulation", "정규표현식", "regex", "파싱", "parsing"
    ],
    "기초": [
        "기초", "Basic", "basic", "기본", "입문", "쉬운 문제",
        "beginner", "Beginner", "초급", "초보", "입문자용"
    ],
    "수학": [
        "수학", "Math", "math", "Mathematics", "수론", "정수론",
        "Number theory", "소수", "Prime", "GCD", "LCM", "조합", "순열"
    ],
    "스택/큐": [
        "스택", "큐", "Stack", "Queue", "stack", "queue",
        "자료구조", "Data structure", "LIFO", "FIFO", "덱", "Deque"
    ],
    "트리": [
        "트리", "Tree", "tree", "이진트리", "Binary tree",
        "BST", "세그먼트 트리", "Segment tree", "트라이", "Trie"
    ],
    "해시": [
        "해시", "Hash", "hash", "해시맵", "HashMap", "딕셔너리",
        "Dictionary", "해시테이블", "Hash table", "Set", "집합"
    ],
    "백트래킹": [
        "백트래킹", "Backtracking", "backtracking", "되추적",
        "가지치기", "Pruning", "N-Queen", "순열 생성"
    ],
}

# 난이도: 정규화된 값 → 변형 리스트 (5단계 티어 시스템)
# 실버=easy, 골드=medium, 플래티넘=medium_hard, 다이아=hard, 마스터=very_hard
DIFFICULTY_VARIANTS: Dict[str, List[str]] = {
    "easy": [
        "easy", "Easy", "실버", "Silver", "silver",
        "쉬움", "쉬운", "쉽", "쉬운 문제", "쉬운거",
        "초급", "초보", "입문", "beginner", "Beginner",
        "간단한", "simple", "Simple", "기본 개념"
    ],
    "medium": [
        "medium", "Medium", "골드", "Gold", "gold",
        "중간", "보통", "중급", "적당한",
        "intermediate", "Intermediate",
        "normal", "Normal", "평범한", "응용"
    ],
    "medium_hard": [
        "medium_hard", "플래티넘", "플레티넘", "Platinum", "platinum",
        "심화", "심화 응용", "상급", "advanced"
    ],
    "hard": [
        "hard", "Hard", "다이아", "다이아몬드", "Diamond", "diamond",
        "어려움", "어려운", "어렵", "어려운 문제",
        "고급", "challenging", "Challenging", "도전적인"
    ],
    "very_hard": [
        "very_hard", "마스터", "Master", "master",
        "최상위", "최고", "극한", "expert", "Expert",
        "전문가", "최상급"
    ],
}

# 언어: 정규화된 값 → 변형 리스트
LANGUAGE_VARIANTS: Dict[str, List[str]] = {
    "python": [
        "python", "Python", "파이썬", "파이선", "파이톤", "py", "Py",
        "Python3", "python3", "파이썬3", "🐍"
    ],
    "java": [
        "java", "Java", "JAVA", "자바", "자바스크립트 아님",
        "JDK", "jdk", "OpenJDK"
    ],
    "cpp": [
        "cpp", "c++", "C++", "CPP", "씨플플", "씨쁠쁠", "시플플",
        "C plus plus", "씨쁠", "시쁠"
    ],
}

# ============================================================
# 긍정/부정 응답 변형 정의 (확인 응답용)
# ============================================================

# 긍정 응답: "yes" → 변형 리스트
POSITIVE_VARIANTS: Dict[str, List[str]] = {
    "yes": [
        # 기본 긍정
        "네", "예", "응", "넵", "넹", "ㅇㅇ", "ㅇㅋ", "ok", "OK", "yes", "Yes",
        "그래", "그래요", "알겠어", "알겠어요",
        # 좋다 계열
        "좋아", "좋아요", "좋지", "좋네", "좋다", "좋음", "좋습니다",
        "괜찮아", "괜찮아요", "괜찮네", "괜찮다",
        # 선택/동의 표현
        "그걸로", "그거", "그거로", "그걸로 해", "그걸로 할게",
        "할게", "할래", "하자", "해줘", "해주세요",
        "그렇게 해", "그렇게 할게", "그렇게 해줘",
        # 확인/수락
        "맞아", "맞아요", "맞음", "동의", "확인",
        "오케이", "오키", "오게이", "ㅇㅋㅇㅋ", "ㄱㄱ",
        # 추천 수락
        "그거 좋다", "그거 좋아", "그거 괜찮네",
        "정렬 좋지", "DP 좋아", "그래프 좋다",  # 주제 + 긍정 패턴
        # 짧은 긍정
        "ㅇ", "웅", "응응", "넵넵", "당연", "당연하지",
        # 추가: 슬랭/비표준 표현
        "굳", "굿", "ㄱㄱㄱ", "ㅇㅇㅇ", "good", "Good",
        "해봐", "해봐봐", "가보자", "가보자고", "해보자", "시작해",
        "그래 해볼게", "해볼래", "해볼게", "도전", "도전할게",
        "물론", "물론이지", "당근", "당근이지",
    ],
}

# 부정 응답: "no" → 변형 리스트
NEGATIVE_VARIANTS: Dict[str, List[str]] = {
    "no": [
        # 기본 부정
        "아니", "아니요", "아니오", "아뇨", "ㄴㄴ", "no", "No", "NO",
        "아닌데", "아닌데요", "아님",
        # 거부/다른 것 요청
        "다른거", "다른 거", "다른걸로", "다른 걸로",
        "다르게", "다른 거로", "딴거", "딴 거",
        "말고", "그거 말고", "그건 말고",
        # 싫다 계열
        "싫어", "싫어요", "싫음", "별로", "별로야", "별로예요",
        "안 좋아", "안좋아", "안 괜찮아",
        # 재요청
        "다시", "다시 추천", "다시 해줘", "다른 거 추천",
        "바꿔", "바꿔줘", "바꿀래", "변경", "변경해줘",
        # 거절 표현
        "됐어", "됐어요", "패스", "스킵",
        "글쎄", "글쎄요", "음...", "흠...",
    ],
}

# ============================================================
# 거절 이유 임베딩 변형 정의
# ============================================================

REJECTION_REASON_VARIANTS: Dict[str, List[str]] = {
    "too_hard": [
        "어려워", "어렵다", "어려운데", "어려울 것 같아", "어려울거같아",
        "힘들어", "힘들다", "힘들 것 같아", "힘들거같아",
        "복잡해", "복잡하다", "복잡한데",
        "못하겠어", "못할 것 같아", "자신없어",
        "이해 못해", "이해가 안돼", "무슨 말인지 모르겠어",
    ],
    "too_easy": [
        "쉬워", "쉽다", "쉬운데", "너무 쉬워",
        "심심해", "심심하다", "재미없어", "지루해",
        "다 아는 거야", "이미 알아", "뻔해",
        "도전적인 거", "더 어려운 거", "실력에 안 맞아",
    ],
    "already_done": [
        "했어", "해봤어", "풀었어", "풀어봤어",
        "이미 했어", "전에 했어", "예전에 했어",
        "아는 거야", "알고 있어", "배웠어",
    ],
    "not_interested": [
        "관심없어", "관심 없어", "흥미없어", "흥미 없어",
        "재미없어", "재미 없어", "별로야", "싫어",
        "안 좋아", "좋아하지 않아", "선호하지 않아",
    ],
    "want_choose": [
        "직접 고를래", "직접 선택할래", "내가 고를게",
        "목록 보여줘", "다 보여줘", "선택지 보여줘",
        "뭐 있어?", "어떤 게 있어?", "옵션 뭐 있어?",
    ],
    "unknown": [
        "몰라", "모르겠어", "모르는데", "잘 몰라",
        "처음이야", "처음인데", "입문자야", "초보야",
        "배운 적 없어", "해본 적 없어",
    ],
}


class CollectionEmbeddingsService:
    """
    정보 수집용 임베딩 서비스

    싱글톤으로 관리되며, 앱 시작 시 한 번 초기화
    """

    def __init__(self):
        self._initialized = False
        self._topic_embeddings: Dict[str, Tuple[str, np.ndarray]] = {}  # variant → (canonical, embedding)
        self._difficulty_embeddings: Dict[str, Tuple[str, np.ndarray]] = {}
        self._language_embeddings: Dict[str, Tuple[str, np.ndarray]] = {}

        # 정규화된 값별 평균 임베딩 (빠른 매칭용)
        self._topic_canonical_embeddings: Dict[str, np.ndarray] = {}
        self._difficulty_canonical_embeddings: Dict[str, np.ndarray] = {}
        self._language_canonical_embeddings: Dict[str, np.ndarray] = {}

        # 긍정/부정 응답 임베딩
        self._positive_embeddings: Dict[str, Tuple[str, np.ndarray]] = {}
        self._negative_embeddings: Dict[str, Tuple[str, np.ndarray]] = {}
        self._positive_canonical_embeddings: Dict[str, np.ndarray] = {}
        self._negative_canonical_embeddings: Dict[str, np.ndarray] = {}

        # 거절 이유 임베딩
        self._rejection_reason_embeddings: Dict[str, Tuple[str, np.ndarray]] = {}
        self._rejection_reason_canonical_embeddings: Dict[str, np.ndarray] = {}

        # 임계값
        self.HIGH_CONFIDENCE = 0.85
        self.MEDIUM_CONFIDENCE = 0.70
        self.LOW_CONFIDENCE = 0.50
        self.CONFIRMATION_THRESHOLD = 0.65  # 긍정/부정 응답용 임계값 (좀 더 관대하게)
        self.REJECTION_REASON_THRESHOLD = 0.60  # 거절 이유 감지 임계값

    async def initialize(self) -> bool:
        """
        임베딩 사전 계산 및 초기화

        앱 시작 시 한 번만 호출됨
        """
        if self._initialized:
            return True

        try:
            print("[CollectionEmbeddings] Initializing embeddings...")

            # 모든 변형에 대한 임베딩 생성
            await self._initialize_category(
                TOPIC_VARIANTS,
                self._topic_embeddings,
                self._topic_canonical_embeddings,
                "topic"
            )
            await self._initialize_category(
                DIFFICULTY_VARIANTS,
                self._difficulty_embeddings,
                self._difficulty_canonical_embeddings,
                "difficulty"
            )
            await self._initialize_category(
                LANGUAGE_VARIANTS,
                self._language_embeddings,
                self._language_canonical_embeddings,
                "language"
            )

            # 긍정/부정 응답 임베딩 초기화
            await self._initialize_category(
                POSITIVE_VARIANTS,
                self._positive_embeddings,
                self._positive_canonical_embeddings,
                "positive"
            )
            await self._initialize_category(
                NEGATIVE_VARIANTS,
                self._negative_embeddings,
                self._negative_canonical_embeddings,
                "negative"
            )

            # 거절 이유 임베딩 초기화
            await self._initialize_category(
                REJECTION_REASON_VARIANTS,
                self._rejection_reason_embeddings,
                self._rejection_reason_canonical_embeddings,
                "rejection_reason"
            )

            self._initialized = True
            print(f"[CollectionEmbeddings] Initialized: {len(self._topic_embeddings)} topics, "
                  f"{len(self._difficulty_embeddings)} difficulties, "
                  f"{len(self._language_embeddings)} languages, "
                  f"{len(self._positive_embeddings)} positive, "
                  f"{len(self._negative_embeddings)} negative, "
                  f"{len(self._rejection_reason_embeddings)} rejection_reasons")
            return True

        except Exception as e:
            print(f"[CollectionEmbeddings] Initialization failed: {e}")
            return False

    async def _initialize_category(
        self,
        variants_dict: Dict[str, List[str]],
        variant_embeddings: Dict[str, Tuple[str, np.ndarray]],
        canonical_embeddings: Dict[str, np.ndarray],
        category_name: str,
    ) -> None:
        """카테고리별 임베딩 초기화"""
        all_variants = []
        variant_to_canonical = {}

        # 모든 변형 수집
        for canonical, variants in variants_dict.items():
            for variant in variants:
                all_variants.append(variant)
                variant_to_canonical[variant] = canonical

        # 배치로 임베딩 생성
        embeddings = await embedding_service.generate_embeddings_batch(all_variants)

        # 변형별 임베딩 저장
        canonical_vectors: Dict[str, List[np.ndarray]] = {k: [] for k in variants_dict.keys()}

        for variant, embedding in zip(all_variants, embeddings):
            canonical = variant_to_canonical[variant]
            emb_array = np.array(embedding)
            variant_embeddings[variant.lower()] = (canonical, emb_array)
            canonical_vectors[canonical].append(emb_array)

        # 정규화된 값별 평균 임베딩 계산
        for canonical, vectors in canonical_vectors.items():
            if vectors:
                canonical_embeddings[canonical] = np.mean(vectors, axis=0)

        print(f"[CollectionEmbeddings] {category_name}: {len(all_variants)} variants embedded")

    def _compute_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """코사인 유사도 계산"""
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return float(np.dot(vec1, vec2) / (norm1 * norm2))

    async def match_topic(self, message: str) -> Optional[EmbeddingMatch]:
        """
        메시지에서 주제 매칭

        Args:
            message: 사용자 메시지

        Returns:
            EmbeddingMatch or None (임계값 미달 시)
        """
        return await self._match_value(
            message,
            self._topic_embeddings,
            self._topic_canonical_embeddings,
            "topic"
        )

    async def match_difficulty(self, message: str) -> Optional[EmbeddingMatch]:
        """메시지에서 난이도 매칭"""
        return await self._match_value(
            message,
            self._difficulty_embeddings,
            self._difficulty_canonical_embeddings,
            "difficulty"
        )

    async def match_language(self, message: str) -> Optional[EmbeddingMatch]:
        """메시지에서 언어 매칭"""
        return await self._match_value(
            message,
            self._language_embeddings,
            self._language_canonical_embeddings,
            "language"
        )

    async def _match_value(
        self,
        message: str,
        variant_embeddings: Dict[str, Tuple[str, np.ndarray]],
        canonical_embeddings: Dict[str, np.ndarray],
        category: str,
    ) -> Optional[EmbeddingMatch]:
        """
        임베딩 기반 값 매칭

        1. 먼저 정확한 키워드 매칭 시도 (빠름)
        2. 실패 시 임베딩 유사도 비교
        """
        message_lower = message.lower().strip()

        # 1. 정확한 키워드 매칭 (O(1))
        if message_lower in variant_embeddings:
            canonical, _ = variant_embeddings[message_lower]
            return EmbeddingMatch(
                value=canonical,
                similarity=1.0,
                matched_variant=message_lower,
            )

        # 2. 짧은 메시지에서 키워드 포함 확인
        for variant, (canonical, _) in variant_embeddings.items():
            if len(message_lower) <= 20 and variant in message_lower:
                return EmbeddingMatch(
                    value=canonical,
                    similarity=0.95,
                    matched_variant=variant,
                )

        # 3. 임베딩 유사도 비교
        try:
            message_embedding = await embedding_service.generate_embedding(message)
            message_vec = np.array(message_embedding)

            best_match: Optional[EmbeddingMatch] = None
            best_similarity = 0.0

            # 정규화된 값의 평균 임베딩과 비교
            for canonical, canonical_vec in canonical_embeddings.items():
                similarity = self._compute_similarity(message_vec, canonical_vec)
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = EmbeddingMatch(
                        value=canonical,
                        similarity=similarity,
                        matched_variant=canonical,
                    )

            # 임계값 확인
            if best_match and best_match.similarity >= self.LOW_CONFIDENCE:
                return best_match

            return None

        except Exception as e:
            print(f"[CollectionEmbeddings] Embedding match failed for {category}: {e}")
            return None

    async def match_all(self, message: str) -> Dict[str, Optional[EmbeddingMatch]]:
        """
        한 메시지에서 주제/난이도/언어 모두 매칭 시도

        "파이썬으로 쉬운 DP 문제" 같은 복합 요청 처리
        """
        results = await asyncio.gather(
            self.match_topic(message),
            self.match_difficulty(message),
            self.match_language(message),
        )

        return {
            "topic": results[0],
            "difficulty": results[1],
            "language": results[2],
        }

    async def match_confirmation(self, message: str) -> Tuple[bool, bool, float]:
        """
        긍정/부정 응답 감지 (임베딩 기반)

        Args:
            message: 사용자 메시지

        Returns:
            (is_positive, is_negative, confidence):
            - is_positive: 긍정 응답인지
            - is_negative: 부정 응답인지
            - confidence: 매칭 신뢰도 (0~1)

        사용 예:
            "정렬 좋지" → (True, False, 0.85)
            "다른거로 해줘" → (False, True, 0.90)
            "DP 문제" → (False, False, 0.3)  # 선택 아님
        """
        message_lower = message.lower().strip()

        # 1. 빠른 키워드 체크 (정확한 매칭은 높은 신뢰도)
        for variant in self._positive_embeddings.keys():
            if variant in message_lower or message_lower == variant:
                return (True, False, 1.0)

        for variant in self._negative_embeddings.keys():
            if variant in message_lower or message_lower == variant:
                return (False, True, 1.0)

        # 2. 임베딩 유사도 기반 매칭
        try:
            message_embedding = await embedding_service.generate_embedding(message)
            message_vec = np.array(message_embedding)

            # 긍정 유사도 계산
            positive_similarity = 0.0
            for canonical, canonical_vec in self._positive_canonical_embeddings.items():
                sim = self._compute_similarity(message_vec, canonical_vec)
                positive_similarity = max(positive_similarity, sim)

            # 부정 유사도 계산
            negative_similarity = 0.0
            for canonical, canonical_vec in self._negative_canonical_embeddings.items():
                sim = self._compute_similarity(message_vec, canonical_vec)
                negative_similarity = max(negative_similarity, sim)

            print(f"[match_confirmation] message='{message}', positive={positive_similarity:.2f}, negative={negative_similarity:.2f}")

            # 둘 다 임계값 이상이면 더 높은 쪽 선택
            if positive_similarity >= self.CONFIRMATION_THRESHOLD and negative_similarity >= self.CONFIRMATION_THRESHOLD:
                if positive_similarity > negative_similarity:
                    return (True, False, positive_similarity)
                else:
                    return (False, True, negative_similarity)

            # 긍정만 임계값 이상
            if positive_similarity >= self.CONFIRMATION_THRESHOLD:
                return (True, False, positive_similarity)

            # 부정만 임계값 이상
            if negative_similarity >= self.CONFIRMATION_THRESHOLD:
                return (False, True, negative_similarity)

            # 둘 다 임계값 미달 → 긍정도 부정도 아님
            return (False, False, max(positive_similarity, negative_similarity))

        except Exception as e:
            print(f"[match_confirmation] Embedding failed: {e}")
            return (False, False, 0.0)

    async def is_positive_response(self, message: str) -> Tuple[bool, float]:
        """긍정 응답인지 확인 (간편 메서드)"""
        is_pos, is_neg, conf = await self.match_confirmation(message)
        return (is_pos, conf)

    async def is_negative_response(self, message: str) -> Tuple[bool, float]:
        """부정 응답인지 확인 (간편 메서드)"""
        is_pos, is_neg, conf = await self.match_confirmation(message)
        return (is_neg, conf)

    async def analyze_rejection_reason(self, message: str) -> Optional[Tuple[str, float]]:
        """
        거절 메시지에서 이유 분석 (임베딩 기반)

        Args:
            message: 사용자 거절 메시지

        Returns:
            (reason, confidence) 또는 None
            reason: "too_hard", "too_easy", "already_done", "not_interested", "want_choose", "unknown"

        사용 예:
            "그건 너무 어려워" → ("too_hard", 0.85)
            "이미 풀어봤어" → ("already_done", 0.90)
            "목록 보여줘" → ("want_choose", 0.88)
        """
        message_lower = message.lower().strip()

        # 1. 빠른 키워드 체크
        for reason, variants in REJECTION_REASON_VARIANTS.items():
            for variant in variants:
                if variant.lower() in message_lower:
                    return (reason, 1.0)

        # 2. 임베딩 유사도 기반 매칭
        try:
            message_embedding = await embedding_service.generate_embedding(message)
            message_vec = np.array(message_embedding)

            best_reason = None
            best_similarity = 0.0

            for reason, canonical_vec in self._rejection_reason_canonical_embeddings.items():
                sim = self._compute_similarity(message_vec, canonical_vec)
                if sim > best_similarity:
                    best_similarity = sim
                    best_reason = reason

            print(f"[analyze_rejection_reason] message='{message}', reason={best_reason}, sim={best_similarity:.2f}")

            if best_similarity >= self.REJECTION_REASON_THRESHOLD:
                return (best_reason, best_similarity)

            return None

        except Exception as e:
            print(f"[analyze_rejection_reason] Error: {e}")
            return None

    async def get_rejection_context(self, message: str) -> Dict[str, Any]:
        """
        거절 메시지에서 전체 컨텍스트 추출

        Returns:
            {
                "is_negative": bool,
                "reason": str | None,
                "reason_confidence": float,
                "suggested_action": str | None,
                "alternative_value": EmbeddingMatch | None,
            }
        """
        result = {
            "is_negative": False,
            "reason": None,
            "reason_confidence": 0.0,
            "suggested_action": None,
            "alternative_value": None,
        }

        # 부정 응답 확인
        is_pos, is_neg, conf = await self.match_confirmation(message)
        result["is_negative"] = is_neg

        if not is_neg:
            return result

        # 거절 이유 분석
        reason_result = await self.analyze_rejection_reason(message)
        if reason_result:
            result["reason"] = reason_result[0]
            result["reason_confidence"] = reason_result[1]

            # 이유에 따른 추천 액션
            action_map = {
                "too_hard": "suggest_easier",
                "too_easy": "suggest_harder",
                "already_done": "suggest_different",
                "not_interested": "suggest_different",
                "want_choose": "show_options",
                "unknown": "suggest_basic",
            }
            result["suggested_action"] = action_map.get(result["reason"])

        # 대안 값 추출 시도
        matches = await self.match_all(message)
        for category in ["topic", "difficulty", "language"]:
            if matches.get(category) and matches[category].similarity >= 0.60:
                result["alternative_value"] = matches[category]
                break

        return result

    def is_initialized(self) -> bool:
        """초기화 상태 확인"""
        return self._initialized

    def get_all_topics(self) -> List[str]:
        """모든 유효한 주제 반환"""
        return list(TOPIC_VARIANTS.keys())

    def get_all_difficulties(self) -> List[str]:
        """모든 유효한 난이도 반환"""
        return list(DIFFICULTY_VARIANTS.keys())

    def get_all_languages(self) -> List[str]:
        """모든 유효한 언어 반환"""
        return list(LANGUAGE_VARIANTS.keys())


# ============================================================
# 싱글톤 인스턴스
# ============================================================

_collection_embeddings_service: Optional[CollectionEmbeddingsService] = None


def get_collection_embeddings_service() -> CollectionEmbeddingsService:
    """싱글톤 인스턴스 반환"""
    global _collection_embeddings_service
    if _collection_embeddings_service is None:
        _collection_embeddings_service = CollectionEmbeddingsService()
    return _collection_embeddings_service


async def initialize_collection_embeddings() -> bool:
    """앱 시작 시 호출하여 임베딩 초기화"""
    service = get_collection_embeddings_service()
    return await service.initialize()
