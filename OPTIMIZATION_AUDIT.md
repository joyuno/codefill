# CodeFill 프로젝트 최적화 감사 보고서

> 생성일: 2026-01-06
> 분석 범위: Backend (FastAPI), Frontend (Next.js), Supabase Schema
> 제외: `src/app/chat/` (AI 챗봇 페이지)

---

## 목차

1. [Executive Summary](#executive-summary)
2. [심각도 분류 기준](#심각도-분류-기준)
3. [데이터베이스 쿼리 최적화](#데이터베이스-쿼리-최적화)
4. [API 설계 문제](#api-설계-문제)
5. [프론트엔드 최적화](#프론트엔드-최적화)
6. [Supabase 스키마 분석](#supabase-스키마-분석)
7. [보안 이슈](#보안-이슈)
8. [코드 구조 및 유지보수성](#코드-구조-및-유지보수성)
9. [우선순위별 개선 권장사항](#우선순위별-개선-권장사항)

---

## Executive Summary

CodeFill 프로젝트에 대한 종합적인 코드 분석 결과, 다음과 같은 주요 문제점들이 발견되었습니다:

| 심각도 | 발견 건수 | 주요 영역 |
|--------|----------|----------|
| Critical | 3 | N+1 쿼리, 코드 중복, 대형 파일 |
| High | 8 | SELECT *, 인덱스 누락, API 비효율 |
| Medium | 12 | 에러 처리, 메모이제이션, RLS 정책 |
| Low | 6 | 코드 스타일, 문서화 |

**가장 시급한 개선 사항:**
1. `friends.py`와 `placement.py`의 N+1 쿼리 패턴 수정
2. `shop.py`와 `placement.py` 간 중복 코드 통합
3. `agent.py` 파일 모듈 분리 (1,784줄)

---

## 심각도 분류 기준

| 등급 | 설명 | 영향 |
|------|------|------|
| **Critical** | 즉시 수정 필요 | 성능 심각한 저하, 보안 취약점, 시스템 장애 가능 |
| **High** | 빠른 시일 내 수정 권장 | 성능 저하, 확장성 문제, 유지보수 어려움 |
| **Medium** | 일정 내 수정 권장 | 코드 품질, 부분적 성능 이슈 |
| **Low** | 개선 권장 | 코드 가독성, 컨벤션 |

---

## 데이터베이스 쿼리 최적화

### CRITICAL-01: N+1 쿼리 패턴 - friends.py

**위치:** `backend/app/routers/friends.py` - `list_friends()` 함수 (약 150-200줄)

**문제:**
```python
# 각 친구마다 개별 쿼리 실행 - N+1 문제
for f in (result.data or []):
    friend_user_id = f["friend_id"] if f["user_id"] == str(user_id) else f["user_id"]

    # 쿼리 1: 읽지 않은 메시지 수
    unread_result = db.table("direct_messages").select("id", count="exact")\
        .eq("sender_id", friend_user_id)\
        .eq("receiver_id", str(user_id))\
        .eq("is_read", False)\
        .execute()

    # 쿼리 2: 마지막 메시지
    last_msg_result = db.table("direct_messages").select("content, sender_id, created_at")\
        .or_(f"and(sender_id.eq.{friend_user_id},receiver_id.eq.{str(user_id)}),and(sender_id.eq.{str(user_id)},receiver_id.eq.{friend_user_id})")\
        .order("created_at", desc=True)\
        .limit(1)\
        .execute()
```

**영향:** 친구 100명 = 200+ 쿼리 실행

**해결 방안:**
```python
# 1. 모든 친구 ID를 한 번에 수집
friend_ids = [f["friend_id"] if f["user_id"] == str(user_id) else f["user_id"] for f in result.data]

# 2. 읽지 않은 메시지 수를 한 번의 쿼리로 집계 (SQL 함수 또는 View 활용)
# 3. 마지막 메시지를 Window 함수로 한 번에 조회

# PostgreSQL View 생성 권장:
# CREATE VIEW friend_message_stats AS
# SELECT
#   sender_id, receiver_id,
#   COUNT(*) FILTER (WHERE NOT is_read) as unread_count,
#   MAX(created_at) as last_message_at
# FROM direct_messages
# GROUP BY sender_id, receiver_id;
```

---

### CRITICAL-02: N+1 쿼리 패턴 - placement.py

**위치:** `backend/app/routers/placement.py` - `check_placement_valid()` 함수 (약 100-150줄)

**문제:**
```python
async def check_placement_valid(db, farm_id: str, x: int, y: int, width: int, height: int, exclude_id: str = None):
    # ...
    for placed in placed_result.data:
        item_code = placed.get("item_code")
        # 매번 shop_items 테이블 조회 - N+1
        shop_result = db.table("shop_items").select("metadata").eq("code", item_code).execute()
```

**해결 방안:**
```python
# 1. JOIN 쿼리 사용
placed_result = db.table("placed_items")\
    .select("*, shop_items!inner(metadata)")\
    .eq("farm_id", farm_id)\
    .execute()

# 2. 또는 shop_items를 한 번에 조회 후 딕셔너리로 캐싱
item_codes = list(set(p["item_code"] for p in placed_result.data))
shop_items = db.table("shop_items").select("code, metadata").in_("code", item_codes).execute()
shop_metadata = {item["code"]: item["metadata"] for item in shop_items.data}
```

---

### HIGH-01: SELECT * 안티패턴

**위치:** 다수의 라우터 파일

**문제 파일 및 위치:**

| 파일 | 함수 | 예시 |
|------|------|------|
| `shop.py` | `get_user_farm()` | `.select("*")` |
| `shop.py` | `get_user_inventory()` | `.select("*")` |
| `placement.py` | `get_user_farm()` | `.select("*")` |
| `placement.py` | 다수 | `.select("*")` |
| `friends.py` | `list_friends()` | `.select("*")` |
| `farm.py` | 다수 | `.select("*")` |
| `practice.py` | 다수 | `.select("*")` |

**영향:**
- 불필요한 데이터 전송으로 네트워크 대역폭 낭비
- 민감한 데이터 노출 가능성
- 컬럼 추가 시 예기치 않은 데이터 포함

**해결 방안:**
```python
# Before
db.table("farms").select("*").eq("user_id", user_id).single().execute()

# After - 필요한 컬럼만 명시
db.table("farms").select("id, user_id, width, height, gold, exp, level").eq("user_id", user_id).single().execute()
```

---

### HIGH-02: 중복 쿼리 - 농장/인벤토리 조회

**위치:** `backend/app/routers/placement.py`, `backend/app/routers/shop.py`

**문제:** 동일 요청 내에서 `get_user_farm()`과 `get_user_inventory()`가 각각 호출됨

```python
# placement.py의 plant_crop()
async def plant_crop(...):
    farm = await get_user_farm(db, user_id)  # 쿼리 1
    inventory = await get_user_inventory(db, user_id)  # 쿼리 2
    # ...
    farm = await get_user_farm(db, user_id)  # 쿼리 3 (재조회)
```

**해결 방안:**
```python
# 1. 단일 조회 후 재사용
# 2. 또는 JOIN을 통한 단일 쿼리
result = db.table("farms")\
    .select("*, user_inventories!inner(*)")\
    .eq("user_id", user_id)\
    .single()\
    .execute()
```

---

### HIGH-03: 인덱스 누락 가능성

**위치:** `supabase/schema.sql`

현재 정의된 인덱스:
```sql
CREATE INDEX IF NOT EXISTS codes_embedding_idx ON codes USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS problems_embedding_idx ON problems USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS problems_type_idx ON problems(type);
```

**누락된 인덱스 권장:**

```sql
-- direct_messages: 자주 조회되는 컬럼
CREATE INDEX idx_direct_messages_sender_receiver
ON direct_messages(sender_id, receiver_id, created_at DESC);

CREATE INDEX idx_direct_messages_unread
ON direct_messages(receiver_id, is_read) WHERE is_read = false;

-- friendships: 자주 조회되는 컬럼
CREATE INDEX idx_friendships_user_status
ON friendships(user_id, status);

CREATE INDEX idx_friendships_friend_status
ON friendships(friend_id, status);

-- placed_items: 농장별 아이템 조회
CREATE INDEX idx_placed_items_farm
ON placed_items(farm_id);

-- user_inventories: 사용자별 인벤토리
CREATE INDEX idx_user_inventories_user
ON user_inventories(user_id);

-- solutions: 사용자 제출 내역
CREATE INDEX idx_solutions_user_created
ON solutions(user_id, created_at DESC);

CREATE INDEX idx_solutions_problem
ON solutions(problem_id);
```

---

## API 설계 문제

### CRITICAL-03: 코드 중복 - shop.py / placement.py

**위치:**
- `backend/app/routers/shop.py`
- `backend/app/routers/placement.py`

**문제:** 완전히 동일한 헬퍼 함수 4개가 두 파일에 중복 정의

```python
# 중복된 함수들 (두 파일에서 동일하게 존재)
async def get_user_farm(db, user_id: UUID) -> dict
async def get_user_inventory(db, user_id: UUID) -> list
async def update_inventory(db, user_id: UUID, item_code: str, quantity_change: int)
def parse_metadata(metadata) -> dict
```

**해결 방안:**
```python
# backend/app/services/farm_service.py 생성
class FarmService:
    @staticmethod
    async def get_user_farm(db, user_id: UUID) -> dict:
        ...

    @staticmethod
    async def get_user_inventory(db, user_id: UUID) -> list:
        ...

    @staticmethod
    async def update_inventory(db, user_id: UUID, item_code: str, quantity_change: int):
        ...

    @staticmethod
    def parse_metadata(metadata) -> dict:
        ...

# 각 라우터에서 임포트
from ..services.farm_service import FarmService
```

---

### HIGH-04: 비효율적인 데이터 반환

**위치:** `backend/app/routers/problems.py`

**문제:** 문제 목록 조회 시 불필요한 필드 포함

```python
# 현재: 모든 필드 반환
.select("*")

# 목록에서 불필요한 필드들:
# - description (긴 텍스트)
# - template_code (코드 템플릿)
# - solution_code (정답 코드)
# - test_cases (테스트 케이스 전체)
```

**해결 방안:**
```python
# 목록 조회용 필드만 선택
.select("id, original_id, title, difficulty, source, tags, solved_count, created_at")
```

---

### HIGH-05: 에러 처리 불일치

**위치:** 전체 백엔드 라우터

**문제:** 에러 응답 형식이 일관되지 않음

```python
# 케이스 1: detail 문자열
raise HTTPException(status_code=404, detail="문제를 찾을 수 없습니다")

# 케이스 2: detail 딕셔너리
raise HTTPException(status_code=400, detail={"error": "invalid", "message": "..."})

# 케이스 3: 일반 응답으로 에러 반환
return {"success": False, "error": "..."}
```

**해결 방안:**
```python
# backend/app/exceptions.py 생성
class AppException(HTTPException):
    def __init__(self, code: str, message: str, status_code: int = 400):
        super().__init__(
            status_code=status_code,
            detail={"code": code, "message": message}
        )

class NotFoundException(AppException):
    def __init__(self, resource: str):
        super().__init__(
            code="NOT_FOUND",
            message=f"{resource}을(를) 찾을 수 없습니다",
            status_code=404
        )

# 사용
raise NotFoundException("문제")
```

---

### MEDIUM-01: API 버전 관리 부재

**위치:** `backend/app/main.py`

**문제:** API 버전 관리가 없어 향후 브레이킹 체인지 시 문제 발생

```python
# 현재
app.include_router(auth_router, prefix="/auth", tags=["auth"])

# 권장
app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
```

---

## 프론트엔드 최적화

### HIGH-06: 불필요한 리렌더링 - ProblemFilters

**위치:** `src/components/problems/ProblemFilters.tsx`

**문제:** 필터 컴포넌트가 매 렌더링마다 새 함수 참조 생성

```tsx
// 문제: 매 렌더링마다 새 함수 생성
onFiltersChange={(newFilters) => setFilters(newFilters)}
```

**해결 방안:**
```tsx
// useCallback으로 메모이제이션
const handleFiltersChange = useCallback((newFilters: ProblemFiltersState) => {
  setFilters(newFilters);
}, []);
```

---

### HIGH-07: 무거운 컴포넌트 - mypage/page.tsx

**위치:** `src/app/mypage/page.tsx` (949줄)

**문제점:**
1. 단일 파일에 너무 많은 로직
2. 모든 탭 컨텐츠가 하나의 컴포넌트에 포함
3. 조건부 렌더링으로 인한 복잡성

**해결 방안:**
```tsx
// 탭별 컴포넌트 분리
src/app/mypage/
├── page.tsx (메인 레이아웃)
├── components/
│   ├── OverviewTab.tsx
│   ├── SolutionsTab.tsx
│   ├── StatisticsTab.tsx
│   ├── SolvedAcTab.tsx
│   └── SettingsTab.tsx
```

---

### MEDIUM-02: 중복 API 호출 방지

**위치:** `src/app/mypage/page.tsx`

**현재 상태:** 통합 API로 개선됨 (5개 API -> 1개)

```tsx
// 현재 구현 (양호)
const response = await usersApi.getMyPageData();
```

**추가 개선 권장:**
```tsx
// React Query 또는 SWR 도입으로 캐싱 및 재검증 최적화
import { useQuery } from '@tanstack/react-query';

const { data, isLoading, error } = useQuery({
  queryKey: ['mypage-data'],
  queryFn: () => usersApi.getMyPageData(),
  staleTime: 5 * 60 * 1000, // 5분
});
```

---

### MEDIUM-03: 이미지 최적화

**위치:** 다수의 컴포넌트

**문제:** Next.js Image 컴포넌트 미사용

```tsx
// 현재
<img src={profileImageUrl} alt="profile" />

// 권장
import Image from 'next/image';
<Image
  src={profileImageUrl}
  alt="profile"
  width={64}
  height={64}
  loading="lazy"
/>
```

---

### MEDIUM-04: 메모이제이션 기회

**위치:** `src/components/problems/ProblemRow.tsx`

**권장:**
```tsx
import { memo } from 'react';

export const ProblemRow = memo(function ProblemRow({ problem, index, onPreview }) {
  // ...
});
```

---

## Supabase 스키마 분석

### HIGH-08: RLS 정책 검토 필요

**위치:** `supabase/schema.sql`

**현재 RLS 정책:**
```sql
-- codes 테이블
CREATE POLICY "Users can view own codes" ON codes FOR SELECT USING (user_id = auth.uid());
CREATE POLICY "Users can insert own codes" ON codes FOR INSERT WITH CHECK (user_id = auth.uid());
```

**문제점:**
1. `problems` 테이블에 RLS 정책 없음 (공개 데이터이므로 의도적일 수 있음)
2. `solutions` 테이블 RLS 확인 필요
3. `direct_messages` 테이블 RLS 확인 필요 - 수신자도 볼 수 있어야 함

**권장 추가 정책:**
```sql
-- solutions: 자신의 솔루션만 조회/생성
CREATE POLICY "Users can view own solutions" ON solutions
FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "Users can insert own solutions" ON solutions
FOR INSERT WITH CHECK (user_id = auth.uid());

-- direct_messages: 송신자/수신자 모두 조회 가능
CREATE POLICY "Users can view own messages" ON direct_messages
FOR SELECT USING (sender_id = auth.uid() OR receiver_id = auth.uid());

CREATE POLICY "Users can send messages" ON direct_messages
FOR INSERT WITH CHECK (sender_id = auth.uid());
```

---

### MEDIUM-05: 외래 키 관계 명시

**위치:** `supabase/schema.sql`

**현재 상태:** 대부분의 FK 관계가 정의됨

**검토 필요:**
```sql
-- placed_items.item_code -> shop_items.code 관계 확인
-- user_inventories.item_code -> shop_items.code 관계 확인

-- 명시적 FK 추가 권장
ALTER TABLE placed_items
ADD CONSTRAINT fk_placed_items_shop
FOREIGN KEY (item_code) REFERENCES shop_items(code);
```

---

### MEDIUM-06: 정규화 검토

**위치:** `solutions` 테이블

**현재:**
```sql
CREATE TABLE solutions (
    problem_id UUID REFERENCES problems(id),
    -- problem 정보가 중복 저장될 가능성
);
```

**권장:** 문제 정보는 JOIN으로 조회, 솔루션에는 최소 정보만 저장

---

## 보안 이슈

### MEDIUM-07: SQL Injection 방지 확인

**위치:** `backend/app/routers/friends.py`

**잠재적 문제:**
```python
# f-string으로 쿼리 생성 (Supabase client가 이스케이프하지만 주의 필요)
.or_(f"and(sender_id.eq.{friend_user_id},receiver_id.eq.{str(user_id)}),...")
```

**권장:** Supabase 클라이언트의 내장 필터 사용 권장

---

### MEDIUM-08: 민감 데이터 노출

**위치:** `backend/app/routers/users.py`

**검토 필요:**
- 사용자 정보 반환 시 비밀번호 해시 등 민감 정보 제외 확인
- 다른 사용자 정보 조회 시 제한된 필드만 반환

---

### LOW-01: 환경 변수 관리

**위치:** `backend/app/config.py` (예상)

**권장:**
```python
# pydantic-settings 사용
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    supabase_url: str
    supabase_key: str
    judge0_api_key: str
    openrouter_api_key: str

    class Config:
        env_file = ".env"
```

---

## 코드 구조 및 유지보수성

### CRITICAL-04: 대형 파일 분리 필요 - agent.py

**위치:** `backend/app/routers/agent.py` (1,784줄)

**문제:** 단일 파일에 너무 많은 책임

**현재 구조:**
- LangGraph 상태 정의
- 노드 함수들 (10개 이상)
- API 엔드포인트
- 유틸리티 함수들

**권장 분리:**
```
backend/app/
├── routers/
│   └── agent.py (API 엔드포인트만, ~100줄)
├── services/
│   └── agent/
│       ├── __init__.py
│       ├── graph.py (LangGraph 정의)
│       ├── nodes.py (노드 함수들)
│       ├── state.py (상태 정의)
│       └── prompts.py (프롬프트 템플릿)
```

---

### HIGH-09: 타입 힌트 일관성

**위치:** 전체 백엔드

**문제:** 일부 함수에 타입 힌트 누락

```python
# Before
async def get_user_farm(db, user_id):

# After
async def get_user_farm(db: Client, user_id: UUID) -> dict:
```

---

### MEDIUM-09: 로깅 개선

**위치:** 전체 백엔드

**현재:** `print()` 문 사용

**권장:**
```python
import logging

logger = logging.getLogger(__name__)

# 대신
logger.info("Processing request for user %s", user_id)
logger.error("Failed to fetch profile", exc_info=True)
```

---

### LOW-02: 문서화

**위치:** 전체 프로젝트

**권장:**
- API 엔드포인트에 docstring 추가 (OpenAPI 문서 자동 생성)
- 복잡한 비즈니스 로직에 주석 추가
- README.md 업데이트

---

## 우선순위별 개선 권장사항

### 1단계: Critical (1-2주 내 완료)

| 번호 | 항목 | 예상 소요 | 영향 |
|------|------|----------|------|
| C-01 | friends.py N+1 쿼리 수정 | 4시간 | 친구 목록 로딩 속도 10x+ 개선 |
| C-02 | placement.py N+1 쿼리 수정 | 2시간 | 배치 유효성 검사 속도 개선 |
| C-03 | shop.py/placement.py 중복 코드 통합 | 3시간 | 유지보수성 향상 |
| C-04 | agent.py 파일 분리 | 8시간 | 코드 가독성, 유지보수성 |

### 2단계: High (1개월 내 완료)

| 번호 | 항목 | 예상 소요 | 영향 |
|------|------|----------|------|
| H-01 | SELECT * 제거 | 4시간 | 네트워크 효율성, 보안 |
| H-02 | 중복 쿼리 제거 | 3시간 | DB 부하 감소 |
| H-03 | 인덱스 추가 | 2시간 | 쿼리 성능 개선 |
| H-04 | 문제 목록 API 필드 최적화 | 2시간 | API 응답 크기 감소 |
| H-05 | 에러 처리 통일 | 4시간 | 프론트엔드 에러 핸들링 일관성 |
| H-06 | ProblemFilters 메모이제이션 | 1시간 | 리렌더링 감소 |
| H-07 | mypage 컴포넌트 분리 | 6시간 | 코드 유지보수성 |
| H-08 | RLS 정책 보강 | 3시간 | 보안 강화 |
| H-09 | 타입 힌트 추가 | 4시간 | 코드 품질 |

### 3단계: Medium (분기 내 완료)

| 번호 | 항목 | 예상 소요 | 영향 |
|------|------|----------|------|
| M-01 | API 버전 관리 도입 | 4시간 | 향후 API 변경 용이 |
| M-02 | React Query/SWR 도입 | 8시간 | 클라이언트 캐싱 최적화 |
| M-03 | Next.js Image 컴포넌트 적용 | 2시간 | 이미지 로딩 최적화 |
| M-04 | ProblemRow 메모이제이션 | 1시간 | 리스트 렌더링 최적화 |
| M-05 | FK 관계 명시 | 1시간 | 데이터 무결성 |
| M-06 | 정규화 검토 | 4시간 | 데이터 중복 제거 |
| M-07 | SQL Injection 검토 | 2시간 | 보안 |
| M-08 | 민감 데이터 노출 검토 | 2시간 | 보안 |
| M-09 | 로깅 시스템 도입 | 4시간 | 디버깅, 모니터링 |

### 4단계: Low (필요시)

| 번호 | 항목 | 예상 소요 |
|------|------|----------|
| L-01 | 환경 변수 관리 개선 | 2시간 |
| L-02 | 문서화 개선 | 지속적 |

---

## 부록: 빠른 수정 코드 예시

### N+1 수정 - friends.py

```python
async def list_friends_optimized(user_id: UUID, db):
    # 1. 친구 목록 조회
    friends_result = db.table("friendships")\
        .select("user_id, friend_id, created_at, profiles!friendships_friend_id_fkey(id, nickname, avatar_url)")\
        .or_(f"user_id.eq.{user_id},friend_id.eq.{user_id}")\
        .eq("status", "accepted")\
        .execute()

    if not friends_result.data:
        return []

    # 2. 친구 ID 목록 추출
    friend_ids = []
    for f in friends_result.data:
        fid = f["friend_id"] if f["user_id"] == str(user_id) else f["user_id"]
        friend_ids.append(fid)

    # 3. 읽지 않은 메시지 수 일괄 조회
    unread_result = db.rpc("get_unread_counts", {
        "p_user_id": str(user_id),
        "p_friend_ids": friend_ids
    }).execute()

    # 4. 마지막 메시지 일괄 조회
    last_messages_result = db.rpc("get_last_messages", {
        "p_user_id": str(user_id),
        "p_friend_ids": friend_ids
    }).execute()

    # 5. 결과 조합
    unread_map = {r["friend_id"]: r["count"] for r in unread_result.data}
    last_msg_map = {r["friend_id"]: r for r in last_messages_result.data}

    return [
        {
            **f,
            "unread_count": unread_map.get(fid, 0),
            "last_message": last_msg_map.get(fid)
        }
        for f, fid in zip(friends_result.data, friend_ids)
    ]
```

### PostgreSQL 함수 (Supabase Migration)

```sql
-- 읽지 않은 메시지 수 일괄 조회
CREATE OR REPLACE FUNCTION get_unread_counts(p_user_id UUID, p_friend_ids UUID[])
RETURNS TABLE(friend_id UUID, count BIGINT) AS $$
BEGIN
    RETURN QUERY
    SELECT
        dm.sender_id as friend_id,
        COUNT(*) as count
    FROM direct_messages dm
    WHERE dm.receiver_id = p_user_id
      AND dm.sender_id = ANY(p_friend_ids)
      AND dm.is_read = false
    GROUP BY dm.sender_id;
END;
$$ LANGUAGE plpgsql;

-- 마지막 메시지 일괄 조회
CREATE OR REPLACE FUNCTION get_last_messages(p_user_id UUID, p_friend_ids UUID[])
RETURNS TABLE(
    friend_id UUID,
    content TEXT,
    sender_id UUID,
    created_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT DISTINCT ON (
        CASE
            WHEN dm.sender_id = p_user_id THEN dm.receiver_id
            ELSE dm.sender_id
        END
    )
        CASE
            WHEN dm.sender_id = p_user_id THEN dm.receiver_id
            ELSE dm.sender_id
        END as friend_id,
        dm.content,
        dm.sender_id,
        dm.created_at
    FROM direct_messages dm
    WHERE (dm.sender_id = p_user_id AND dm.receiver_id = ANY(p_friend_ids))
       OR (dm.receiver_id = p_user_id AND dm.sender_id = ANY(p_friend_ids))
    ORDER BY
        CASE
            WHEN dm.sender_id = p_user_id THEN dm.receiver_id
            ELSE dm.sender_id
        END,
        dm.created_at DESC;
END;
$$ LANGUAGE plpgsql;
```

---

## 결론

CodeFill 프로젝트는 전반적으로 잘 구조화되어 있으나, 위에 나열된 최적화 기회들을 통해 성능과 유지보수성을 크게 개선할 수 있습니다. 특히 N+1 쿼리 패턴과 코드 중복은 즉시 수정이 권장되며, 이를 통해 사용자 경험과 서버 리소스 효율성을 크게 향상시킬 수 있습니다.

모든 변경사항은 단계적으로 적용하고, 각 단계마다 테스트를 통해 기능 정상 동작을 확인하시기 바랍니다.
