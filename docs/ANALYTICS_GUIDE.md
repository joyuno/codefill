# CodeFill 분석 도구 통합 가이드

## 현재 구현된 것

### 1. CF 로그 테이블 (`user_problem_interactions`)
```sql
-- 수집 데이터
- action_type: view, attempt, solve, skip, bookmark, hint_request
- time_spent_seconds: 체류 시간
- is_correct: 정답 여부
- hint_used_count: 힌트 의존도
- source: 유입 경로 (추천 성능 측정)
```

### 2. CF 추천 함수
```sql
-- 유사 유저 찾기
SELECT * FROM find_similar_users('user-uuid', 3, 10);

-- CF 기반 문제 추천
SELECT * FROM recommend_problems_cf('user-uuid', 5);
```

---

## 추가 권장 도구

### 1. Microsoft Clarity (무료, 필수)
**용도**: 사용자 행동 시각화, 히트맵, 세션 리플레이

```bash
# 설치
npm install @microsoft/clarity
```

```typescript
// src/lib/analytics/clarity.ts
export const initClarity = () => {
  if (typeof window === 'undefined') return;

  (function(c,l,a,r,i,t,y){
    c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};
    t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;
    y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
  })(window, document, "clarity", "script", "YOUR_CLARITY_ID");
};

// 사용자 식별 (로그인 후)
export const identifyUser = (userId: string, traits?: Record<string, string>) => {
  if (typeof window !== 'undefined' && window.clarity) {
    window.clarity("identify", userId);
    if (traits) {
      Object.entries(traits).forEach(([key, value]) => {
        window.clarity("set", key, value);
      });
    }
  }
};
```

**추적 포인트**:
- 코드 에디터에서 막히는 부분 (히트맵)
- 힌트 버튼 클릭 전 행동 (세션 리플레이)
- 스크롤 깊이 (문제 설명 읽는지)

---

### 2. Google Analytics 4 (무료, 권장)
**용도**: 전환 퍼널, 유입 경로, 리텐션

```typescript
// src/lib/analytics/ga4.ts
import { gtag } from 'ga-gtag';

export const GA_ID = process.env.NEXT_PUBLIC_GA_ID;

export const pageview = (url: string) => {
  gtag('config', GA_ID, { page_path: url });
};

// 커스텀 이벤트
export const event = (action: string, params: Record<string, unknown>) => {
  gtag('event', action, params);
};

// CodeFill 전용 이벤트
export const trackProblemEvent = (
  action: 'start' | 'submit' | 'solve' | 'skip' | 'hint',
  problemId: string,
  metadata?: Record<string, unknown>
) => {
  event(`problem_${action}`, {
    problem_id: problemId,
    ...metadata,
  });
};
```

**추천 이벤트 설정**:
```
problem_start      → 문제 시작
problem_submit     → 코드 제출
problem_solve      → 정답
problem_skip       → 스킵
problem_hint       → 힌트 사용
onboarding_complete → 온보딩 완료
chat_message       → 챗봇 메시지
```

---

### 3. Mixpanel / Amplitude (유료, 스케일업 시)
**용도**: 고급 코호트 분석, 리텐션 차트, A/B 테스트

필요한 시점:
- MAU 10,000+
- 리텐션 심층 분석 필요 시
- A/B 테스트 본격화 시

---

## 나중에 개발할 때 필요한 데이터

### A. 추천 시스템 고도화

| 데이터 | 용도 | 우선순위 |
|--------|------|---------|
| `user_problem_interactions` | CF 학습 | ✅ 완료 |
| `problem_embeddings` | Content-based 추천 | ✅ 완료 |
| `user_skill_vectors` | 실력 기반 매칭 | 🔜 다음 |
| `problem_difficulty_history` | 동적 난이도 조절 | 🔜 다음 |

### B. 학습 분석 (Learning Analytics)

```sql
-- 추가 테이블 제안
CREATE TABLE user_learning_sessions (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    started_at TIMESTAMPTZ,
    ended_at TIMESTAMPTZ,
    problems_attempted INTEGER,
    problems_solved INTEGER,
    total_hints_used INTEGER,
    topics_practiced TEXT[],
    session_quality_score FLOAT  -- ML로 계산
);

CREATE TABLE user_skill_progression (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    topic TEXT NOT NULL,
    skill_level FLOAT,  -- 0.0 ~ 1.0 (BKT 모델)
    confidence FLOAT,
    updated_at TIMESTAMPTZ
);
```

### C. A/B 테스트 인프라

```sql
CREATE TABLE ab_experiments (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    variants JSONB,  -- {"control": 50, "variant_a": 50}
    start_date TIMESTAMPTZ,
    end_date TIMESTAMPTZ,
    status TEXT  -- 'running', 'completed', 'stopped'
);

CREATE TABLE user_experiment_assignments (
    user_id UUID NOT NULL,
    experiment_id UUID NOT NULL,
    variant TEXT NOT NULL,
    assigned_at TIMESTAMPTZ,
    PRIMARY KEY (user_id, experiment_id)
);
```

---

## 데이터 파이프라인 로드맵

```
Phase 1 (현재)
├── user_problem_interactions → CF 기본
├── problem_embeddings → RAG 검색
└── Clarity + GA4 → 기본 분석

Phase 2 (사용자 1000+)
├── user_skill_vectors → 실력 매칭
├── Mixpanel → 코호트 분석
└── A/B 테스트 인프라

Phase 3 (사용자 10000+)
├── ML Pipeline (Airflow/Dagster)
├── 실시간 추천 (Redis + Model Serving)
└── 자동 난이도 조절
```

---

## 즉시 적용 체크리스트

- [ ] Clarity 프로젝트 생성 및 스크립트 추가
- [ ] GA4 속성 생성 및 이벤트 설정
- [ ] `useInteractionLog` hook 컴포넌트에 연결
- [ ] 페이지 이탈 시 `flush()` 호출 (beforeunload)
- [ ] 주요 버튼에 이벤트 트래킹 추가

---

## 환경 변수 추가

```env
# .env.local
NEXT_PUBLIC_CLARITY_ID=your-clarity-id
NEXT_PUBLIC_GA_ID=G-XXXXXXXXXX
```
