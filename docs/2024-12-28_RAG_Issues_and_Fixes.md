# RAG 검색 및 문제 선택 플로우 이슈 해결 (2024-12-28)

## 개요
CodeFill 백엔드의 RAG(Retrieval-Augmented Generation) 검색 시스템과 문제 선택 플로우에서 발생한 이슈들과 해결 방안을 정리합니다.

---

## 1. Problem Embeddings 테이블이 비어있는 이슈

### 문제 상황
- RAG 검색이 제대로 작동하지 않음
- `problem_embeddings` 테이블을 확인해보니 0개의 레코드
- 임베딩이 전혀 생성되지 않은 상태

### 원인
- 임베딩 생성 스크립트가 실행되지 않았음
- Intent embeddings (인메모리, 서버 시작 시 생성)와 Problem embeddings (pgvector, DB 저장)이 별도로 관리됨

### 해결 방안
배치 임베딩 생성 스크립트 작성 및 실행:

```python
# backend/scripts/generate_embeddings.py
async def generate_all_embeddings():
    problems = db.table("base_problems").select("*").execute().data

    for batch in batches:
        texts = [create_problem_text_for_embedding(p) for p in batch]
        embeddings = await embedding_service.generate_embeddings_batch(texts)

        for problem, embedding in zip(batch, embeddings):
            db.table("problem_embeddings").upsert({
                "problem_id": problem["id"],
                "embedding": embedding,
                "text_content": text[:5000]
            }).execute()
```

**결과**: 3,898개 문제에 대한 임베딩 100% 생성 완료

---

## 2. 임베딩 텍스트 생성 로직 개선

### 문제 상황
- `solutions[0].code`에 1000자 제한이 걸려있어 코드가 잘림
- 문제의 핵심 정보가 임베딩에 제대로 반영되지 않음

### 원인
- 기존 로직이 단순히 `code[:1000]`으로 잘라서 사용
- solutions 구조가 `{language: "python", code: "..."}` 형태인데 이를 고려하지 않음

### 해결 방안
`embedding.py`의 `create_problem_text_for_embedding` 함수 수정:

```python
def create_problem_text_for_embedding(self, problem: Dict[str, Any]) -> str:
    parts = []

    # Title/Name
    if problem.get("name"):
        parts.append(problem["name"])
    elif problem.get("title"):
        parts.append(problem["title"])

    # Question (3000자 제한)
    if problem.get("question"):
        parts.append(problem["question"][:3000])

    # Tags
    if problem.get("tags"):
        parts.append(f"Tags: {', '.join(problem['tags'])}")

    # Difficulty
    if problem.get("difficulty"):
        parts.append(f"Difficulty: {problem['difficulty']}")

    # Python 코드 전체 포함 (제한 없음)
    solutions = problem.get("solutions", [])
    for sol in solutions:
        if sol.get("language", "").lower() == "python" and sol.get("code"):
            parts.append(f"Python Code:\n{sol['code']}")
            break

    return "\n\n".join(parts)
```

---

## 3. 토픽 매칭 이슈 (한국어 vs 영어)

### 문제 상황
- 사용자가 "DP 문제 풀래"라고 요청
- DB의 tags는 "Dynamic programming"으로 저장됨
- 매칭이 되지 않아 검색 결과 없음

### 해결 방안
`rag.py`에 토픽 매핑 추가:

```python
TOPIC_MAPPING = {
    "DP": ["Dynamic programming", "DP", "Memoization"],
    "동적 프로그래밍": ["Dynamic programming", "DP", "Memoization"],
    "이진 탐색": ["Binary search", "Divide and conquer", "Sorting"],
    "그래프": ["Graph algorithms", "Graph traversal", "BFS", "DFS"],
    "정렬": ["Sorting", "Implementation"],
    "문자열": ["String algorithms", "String"],
    "수학": ["Mathematics", "Number theory", "Math"],
    "그리디": ["Greedy algorithms", "Greedy"],
    "완전 탐색": ["Complete search", "Brute force", "Implementation"],
    "스택": ["Data structures", "Stack"],
    "큐": ["Data structures", "Queue"],
    "해시": ["Data structures", "Hash"],
    "트리": ["Tree algorithms", "Data structures"],
    "재귀": ["Recursion", "Divide and conquer"],
}

def _expand_topics(self, topics: List[str]) -> List[str]:
    expanded = set()
    for topic in topics:
        expanded.add(topic)
        if topic in self.TOPIC_MAPPING:
            expanded.update(self.TOPIC_MAPPING[topic])
    return list(expanded)
```

---

## 4. 벡터 검색 방식 변경 (Vector-first → Filter-first)

### 문제 상황
- "쉬운 DP 문제" 검색 시 medium 난이도 문제가 섞여서 반환
- 벡터 유사도 우선 검색 후 필터링하니 원하는 결과가 안 나옴

### 원인
- 기존: 벡터 검색 → 상위 N개 추출 → 필터 적용 (이미 필터링할 데이터가 없음)
- 벡터 유사도가 높아도 난이도/토픽이 맞지 않는 문제가 선택됨

### 해결 방안
**Filter-first, Vector-rank 방식**으로 변경:

```python
async def search_problems_hybrid(self, query, topics, difficulty, language, limit):
    # Step 1: DB에서 먼저 필터링
    db_query = self.db.table("base_problems").select("*")

    if difficulty:
        db_query = db_query.eq("difficulty", difficulty)

    if topics:
        expanded_topics = self._expand_topics(topics)
        db_query = db_query.overlaps("tags", expanded_topics)

    filtered_problems = db_query.limit(100).execute().data

    # Step 2: 필터된 결과에 대해 벡터 유사도 계산
    query_embedding = await embedding_service.generate_embedding(query)

    # Step 3: 유사도로 정렬
    for problem in filtered_problems:
        similarity = cosine_similarity(query_embedding, problem_embedding)
        problem["similarity"] = similarity

    results.sort(key=lambda x: x["similarity"], reverse=True)

    return results[:limit], should_fallback
```

---

## 5. pgvector 임베딩 파싱 오류

### 문제 상황
```
TypeError: ufunc 'multiply' did not contain a loop with signature matching types
```

### 원인
- pgvector에서 반환된 embedding이 문자열 형태 (`"[0.1, 0.2, ...]"`)
- numpy가 문자열을 처리하지 못함

### 해결 방안
```python
for e in embeddings_response.data:
    emb = e["embedding"]
    if isinstance(emb, str):
        emb = json.loads(emb)  # 문자열 → 리스트 변환
    embeddings_map[e["problem_id"]] = emb
```

---

## 6. 문제 선택 후 플로우 전환 이슈

### 문제 상황
- 문제 리스트 표시 후 사용자가 "taco_139로 할게" 선택
- 예상: 문제 유형 선택 UI (blank/puzzle/guided) 표시
- 실제: 검색이 다시 실행되고, CodeGen도 중복 호출됨

### 원인
1. `PROBLEM_SELECTION` 의도가 정의되지 않음
2. LLM이 문제 선택을 다른 의도(AFFIRMATION 또는 NEW_PROBLEM)로 분류
3. 결과적으로 `search_problems` 액션이 다시 트리거됨

### 해결 방안

#### 6.1 새 의도 정의 추가 (`definitions.py`)
```python
class IntentType(str, Enum):
    # 문제 선택
    PROBLEM_SELECTION = "problem_selection"

INTENT_DEFINITIONS[IntentType.PROBLEM_SELECTION] = {
    "description": "문제 리스트에서 특정 문제 선택",
    "examples": [
        "1번", "1번으로 할래", "첫번째 문제",
        "taco_139로 할게", "그 문제로 할래",
        "그걸로 할게", "이 문제 풀래"
    ],
    "required_context": "problem_list",
    "next_action": "select_problem_type",
}
```

#### 6.2 프롬프트 업데이트 (`free_chat_agent.py`)
```python
### 문제 선택 의도 (중요!)
- **problem_selection**: 문제 리스트에서 문제 선택함 → 바로 문제 유형 선택으로 진행
  - 사용자가 번호(1번, 2번)나 이름(taco_139)으로 문제를 선택하면 이 의도
  - 절대 다시 검색하지 말고, action_trigger="select_problem_type" 설정
```

#### 6.3 핸들러 추가 (`agent.py`)
```python
async def _handle_problem_selection(request, intent_result) -> IntentChatResponse:
    # 선택된 문제 추출
    message = request.message.lower()
    selected_problem = None
    selected_index = None

    # 번호 추출 (1번, 첫번째 등)
    num_match = re.search(r'(\d+)\s*번', message)
    if num_match:
        selected_index = int(num_match.group(1))

    # 이름 추출 (taco_139 등)
    name_match = re.search(r'(taco_\d+|[a-z_\-]+\d*)', message)
    if name_match:
        selected_problem = name_match.group(1)

    return IntentChatResponse(
        message="좋아요! 어떤 방식으로 풀어볼까요?",
        action_data={
            "action_trigger": "select_problem_type",
            "next_action": "show_problem_type_selector",
            "selected_problem": selected_problem,
            "selected_problem_index": selected_index
        }
    )
```

#### 6.4 CollectedInfo 모델 확장 (`models/agent.py`)
```python
class CollectedInfo(BaseModel):
    topics: List[str] = []
    difficulty: Optional[str] = None
    language: Optional[str] = None
    specific_needs: Optional[str] = None
    time_available: Optional[int] = None
    selected_problem: Optional[str] = None      # 추가
    selected_problem_index: Optional[int] = None # 추가
```

---

## 전체 플로우 다이어그램

```
사용자: "쉬운 DP 문제 풀래"
    ↓
[Intent Classification] → topic_specific
    ↓
[FREE_CHAT_SYSTEM_PROMPT] → is_complete=true, action_trigger="search_problems"
    ↓
[_auto_search_problems]
    ├─ Filter: difficulty=easy, tags contains "Dynamic programming"
    ├─ Vector ranking: 유사도순 정렬
    └─ Return: 5개 문제
    ↓
응답: "찾은 문제들이에요: 1. taco_139 (easy) ..."
    ↓
사용자: "taco_139로 할게"
    ↓
[Intent Classification] → problem_selection  ← NEW!
    ↓
[_handle_problem_selection]
    ↓
응답: {
    action_trigger: "select_problem_type",
    next_action: "show_problem_type_selector",
    selected_problem: "taco_139"
}
    ↓
[프론트엔드] → 문제 유형 선택 UI 표시 (Blank/Puzzle/Guided)
```

---

## 7. 초보자 요청이 hint_request로 잘못 분류되는 이슈

### 문제 상황
```
사용자: "문제 풀고싶어 쉬운거로"
봇: "좋아요! 어떤 주제로 문제를 풀고 싶으세요?"
사용자: "그런거 하나도 모르는 사람이야 나는 그냥 제일 기본적인거"
봇: "천천히 문제를 다시 읽어보세요. 힌트가 필요하면 말씀해주세요!"  ← 잘못된 응답!
```

### 원인
- 사용자가 "모르겠어"라고 말하면 LLM이 `hint_request`로 분류
- 하지만 현재 문제가 제공되지 않은 상태에서 힌트를 줄 수 없음
- 이 경우는 "초보자가 기초 문제를 원한다"는 `random_recommend` 의도

### 해결 방안

#### 7.1 RANDOM_RECOMMEND 의도 예시 확장 (`definitions.py`)
```python
IntentType.RANDOM_RECOMMEND: {
    "description": "아무거나 추천 요청 또는 초보자 기본 문제 요청",
    "examples": [
        # 기존 예시들...
        # 초보자/기본 요청 추가
        "기본적인거", "제일 기본적인거", "기초적인거",
        "아무것도 모르는데", "하나도 모르는데",
        "초보인데", "처음인데", "입문자인데",
        "그런거 모르는 사람이야", "알고리즘 뭔지 몰라",
    ],
}
```

#### 7.2 컨텍스트 검증 규칙 추가 (`free_chat_agent.py`)
```python
## 중요: 컨텍스트 검증 규칙

**hint_request로 절대 분류하면 안 되는 경우:**
- 현재 문제가 없을 때 (문제 선택 단계에서 "모르겠어"는 hint가 아님!)
- 문제 검색/추천 대화 중일 때
- 사용자가 알고리즘 주제를 모르겠다고 할 때 → 이건 random_recommend!

**예시:**
- "DP가 뭔지 모르겠어" (문제 선택 중) → random_recommend, NOT hint_request
- "그런거 하나도 모르는 사람이야" → random_recommend, NOT hint_request
- "기본적인거로 해줘" → random_recommend with difficulty=easy

**hint_request는 오직:**
- 문제가 이미 제시된 상태에서
- "힌트 줘", "어떻게 풀어?", "모르겠어 도와줘" 같은 요청일 때만
```

#### 7.3 백엔드 안전장치 추가 (`agent.py`)
```python
# 힌트 요청인데 현재 문제가 없으면 검색으로 리다이렉트
if action_trigger == "generate_hint":
    has_current_problem = (
        request.user_context and
        request.user_context.get("current_problem")
    )
    if not has_current_problem:
        action_trigger = "search_problems"
        final_message = "아직 풀고 있는 문제가 없어요! 먼저 문제를 찾아볼까요?"
        is_complete = False
```

---

## 테스트 결과

### 검색 테스트
```bash
curl -X POST http://localhost:8000/agent/chat \
  -d '{"message":"쉬운 DP 문제 풀래"}'
```
**결과**: 5개 easy DP 문제 정상 반환

### 초보자 기본 문제 요청 테스트
```bash
curl -X POST http://localhost:8000/agent/chat \
  -d '{
    "message": "그런거 하나도 모르는 사람이야 나는 그냥 제일 기본적인거",
    "conversation_history": [
      {"role": "user", "content": "문제 풀고싶어 쉬운거로"},
      {"role": "assistant", "content": "좋아요! 어떤 주제로 문제를 풀고 싶으세요?"}
    ]
  }'
```
**결과**:
```json
{
  "message": "알겠어요! 기초적인 쉬운 문제를 찾아볼게요!",
  "intent_info": {"intent": "random_recommend", "confidence": 0.8},
  "collected_info": {
    "topics": ["기초", "Implementation"],
    "difficulty": "easy"
  },
  "action_data": {
    "status": "found",
    "problems": [
      {"name": "taco_333", "difficulty": "easy"},
      {"name": "taco_33", "difficulty": "easy"},
      {"name": "taco_811", "difficulty": "easy"},
      {"name": "taco_1164", "difficulty": "easy"},
      {"name": "taco_875", "difficulty": "easy"}
    ]
  }
}
```
**확인**: `hint_request`가 아닌 `random_recommend`로 정상 분류, 모두 easy 난이도 반환

### 문제 선택 테스트
```bash
curl -X POST http://localhost:8000/agent/chat \
  -d '{
    "message": "taco_333으로 할게",
    "conversation_history": [...]
  }'
```
**결과**:
```json
{
  "message": "좋아요! taco_333 문제로 할게요. 어떤 방식으로 풀어볼까요?",
  "intent_info": {"intent": "problem_selection"},
  "action_data": {
    "action_trigger": "select_problem_type",
    "next_action": "show_problem_type_selector",
    "selected_problem": "taco_333"
  }
}
```
**확인**: 문제 유형 선택 UI 트리거 정상 작동

---

## 수정된 파일 목록

| 파일 | 변경 내용 |
|------|----------|
| `backend/app/services/embedding.py` | 임베딩 텍스트 생성 로직 개선 |
| `backend/app/services/rag.py` | Filter-first 검색, 토픽 매핑, JSON 파싱 |
| `backend/app/intents/definitions.py` | PROBLEM_SELECTION 의도 추가, RANDOM_RECOMMEND 예시 확장 |
| `backend/app/prompts/free_chat_agent.py` | 문제 선택 가이드, 컨텍스트 검증 규칙 추가 |
| `backend/app/routers/agent.py` | 핸들러 추가, hint 안전장치, CollectedInfo 파싱 수정 |
| `backend/app/models/agent.py` | selected_problem 필드 추가 |
| `backend/scripts/generate_embeddings.py` | 배치 임베딩 생성 스크립트 (신규) |

---

## 향후 개선 사항

1. **토픽 매핑 확장**: 더 많은 한국어-영어 토픽 매핑 추가
2. **캐싱**: 자주 검색되는 쿼리에 대한 임베딩 캐싱
3. **프론트엔드 연동**: `show_problem_type_selector` 액션에 대한 UI 구현
4. **문제 유형별 생성 Agent 연결**: Blank/Puzzle/Guided 선택 후 해당 엔드포인트 호출
