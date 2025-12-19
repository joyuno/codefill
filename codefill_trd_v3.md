# CodeFill TRD v3 (Technical Requirements Document)

## 문서 정보

| 항목 | 내용 |
| --- | --- |
| **문서명** | CodeFill v3 기술 요구사항 정의서 |
| **버전** | 3.0 |
| **작성일** | 2025년 12월 19일 |
| **상태** | 최종 |

---

## 1. 기술 스택

### 1.1 Frontend

| 기술 | 버전 | 용도 |
| --- | --- | --- |
| **Next.js** | 14+ | 프레임워크 (App Router) |
| **React** | 19 | UI 라이브러리 |
| **TypeScript** | 5+ | 타입 안정성 |
| **TailwindCSS** | 3+ | 스타일링 |
| **shadcn/ui** | latest | UI 컴포넌트 |
| **Monaco Editor** | latest | 코드 에디터 |
| **react-dnd** | latest | 드래그 앤 드롭 (퍼즐) |
| **Zustand** | latest | 상태 관리 |
| **React Query** | 5+ | 서버 상태 관리 |

### 1.2 Backend

| 기술 | 버전 | 용도 |
| --- | --- | --- |
| **Python** | 3.11+ | 언어 |
| **FastAPI** | 0.100+ | 웹 프레임워크 |
| **LangChain** | 0.1+ | LLM 오케스트레이션 |
| **SQLAlchemy** | 2+ | ORM |
| **Pydantic** | 2+ | 데이터 검증 |
| **asyncio** | - | 비동기 처리 |

### 1.3 Database & Infrastructure

| 기술 | 용도 |
| --- | --- |
| **Supabase** | PostgreSQL + Auth + Storage |
| **pgvector** | 벡터 검색 (RAG) |
| **Redis** | 캐싱, Rate Limiting |
| **Vercel** | Frontend 배포 |
| **GCP Cloud Run** | Backend 배포 |
| **GitHub Actions** | CI/CD |

### 1.4 External Services

| 서비스 | 용도 |
| --- | --- |
| **OpenRouter** | LLM 라우팅 (다중 모델) |
| **OpenAI** | 임베딩 (text-embedding-3-small) |
| **Sandpack** | 브라우저 코드 실행 (JS/React) |
| **Judge0** | 서버 코드 실행 (Python/Java/C++) |
| **토스페이먼츠** | 결제 |
| **Resend** | 이메일 발송 |
| **Sentry** | 에러 추적 |

---

## 2. 시스템 아키텍처

### 2.1 전체 구조

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                 Client                                       │
│                          (Browser/Mobile)                                    │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Frontend (Next.js)                                   │
│                            Vercel Edge                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│  • SSR/SSG 페이지 렌더링                                                     │
│  • 정적 자산 CDN 배포                                                        │
│  • API Route (프록시)                                                        │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │ REST API
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Backend (FastAPI)                                    │
│                          GCP Cloud Run                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ Auth API    │  │ Problem API │  │ Chat API    │  │ Farm API    │        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
│         │                │                │                │                │
│         └────────────────┴────────────────┴────────────────┘                │
│                                   │                                          │
│                          ┌────────▼────────┐                                │
│                          │  Agent System   │                                │
│                          │  (6 Agents)     │                                │
│                          └────────┬────────┘                                │
└───────────────────────────────────┼─────────────────────────────────────────┘
                                    │
          ┌─────────────────────────┼─────────────────────────┐
          │                         │                         │
          ▼                         ▼                         ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────────────┐
│    Supabase     │     │   OpenRouter    │     │   External Services     │
│  PostgreSQL     │     │   (LLM API)     │     │  Sandpack, Judge0       │
│  + pgvector     │     │                 │     │  토스페이먼츠, Resend   │
└─────────────────┘     └─────────────────┘     └─────────────────────────┘
```

### 2.2 Agent 시스템 구조

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Agent System (6개)                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        Chat Agent                                    │   │
│  │                      (GPT-4o-mini)                                   │   │
│  │              사용자 의도 파악 + 정보 수집 통합                         │   │
│  └───────────────────────────┬─────────────────────────────────────────┘   │
│                              │                                              │
│          ┌───────────────────┼───────────────────┐                         │
│          │                   │                   │                         │
│          ▼                   ▼                   ▼                         │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐                   │
│  │  Code Gen    │   │ Problem Gen  │   │ Guided Agent │                   │
│  │ (Claude      │   │ (GPT-4o-mini)│   │ (GPT-4o-mini)│                   │
│  │  Sonnet)     │   │              │   │              │                   │
│  │              │   │ 3가지 유형     │   │ 1대1 대화형  │                   │
│  │코드 및 답 생성  │   │ 문제 유형별 변환 │   │ 진행         │                   │
│  └──────────────┘   └──────────────┘   └──────────────┘                   │
│                              │                                              │
│          ┌───────────────────┼───────────────────┐                         │
│          │                   │                   │                         │
│          ▼                   ▼                   ▼                         │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐                   │
│  │ Hint Agent   │   │   Answer     │   │   (보류)     │                   │
│  │ (Gemini      │   │   Checker    │   │              │                   │
│  │  Flash)      │   │ (규칙)   │   │              │                   │
│  │              │   │              │   │              │                   │
│  │ 힌트 + RAG   │   │ 채점         │   │              │                   │
│  └──────────────┘   └──────────────┘   └──────────────┘                   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.3 Agent 상세

| Agent | 모델 | 역할 | 입력 | 출력 |
| --- | --- | --- | --- | --- |
| **Chat Agent** | GPT-4o-mini | 의도 파악, 정보 수집 | 사용자 메시지 | 라우팅 결정, 수집된 정보 |
| **Code Gen** | Claude Sonnet | 교육용 코드 생성 | 주제, 난이도, 언어 | 완성된 코드 |
| **Problem Gen** | GPT-4o-mini | 3가지 유형 문제 변환 | 코드, 유형 | 문제 데이터 |
| **Guided Agent** | GPT-4o-mini | 1대1 대화형 진행 | 문제, 사용자 응답 | 다음 단계 메시지 |
| **Hint Agent** | Gemini Flash | 힌트 생성 + Docs RAG | 문제, 힌트 레벨 | 힌트 텍스트 |


---

## 3. 데이터베이스 스키마

### 3.1 ERD 개요

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│    users     │────<│   attempts   │>────│   problems   │
└──────────────┘     └──────────────┘     └──────────────┘
       │                    │                    │
       │             ┌──────┴──────┐             │
       │             │             │             │
       ▼             ▼             ▼             │
┌──────────────┐ ┌──────────┐ ┌──────────┐      │
│  user_stats  │ │hint_logs │ │ puzzle_  │      │
└──────────────┘ └──────────┘ │ attempts │      │
       │                      └──────────┘      │
       │                                        │
       ▼                                        ▼
┌──────────────┐                        ┌──────────────┐
│daily_activity│                        │    codes     │
└──────────────┘                        └──────────────┘
       │
       │         ┌──────────────┐     ┌──────────────┐
       │         │  user_farm   │────<│ user_inventory│
       │         └──────────────┘     └──────────────┘
       │                │
       │                ▼
       │         ┌──────────────┐
       │         │  farm_items  │
       │         └──────────────┘
       │
       ▼
┌──────────────┐     ┌──────────────┐
│    badges    │────<│ user_badges  │
└──────────────┘     └──────────────┘
       
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│    plans     │────<│subscriptions │>────│   payments   │
└──────────────┘     └──────────────┘     └──────────────┘
```

### 3.2 테이블 상세

#### users (사용자)

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    nickname VARCHAR(50) NOT NULL,
    profile_image_url TEXT,
    
    -- 온보딩 데이터
    onboarding_data JSONB DEFAULT '{}',
    onboarding_completed BOOLEAN DEFAULT FALSE,
    
    -- solved.ac 연동
    solved_ac_id VARCHAR(50),
    solved_ac_tier INTEGER,
    solved_ac_data JSONB DEFAULT '{}',
    
    -- 소셜 로그인
    provider VARCHAR(20),
    provider_id VARCHAR(255),
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_login_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT TRUE
);

-- onboarding_data 구조
-- {
--   "status": "job_seeker",
--   "goal": "big_tech",
--   "self_level": "intermediate",
--   "interests": ["dp", "graph"],
--   "diagnostic_score": 75,
--   "completed_at": "2025-01-15T10:30:00Z"
-- }

-- solved_ac_data 구조
-- {
--   "tier_name": "Gold III",
--   "solved_count": 342,
--   "rating": 1523,
--   "class": 4,
--   "strong_tags": ["dp", "graphs"],
--   "weak_tags": ["geometry", "string"],
--   "synced_at": "2025-01-15T10:30:00Z"
-- }
```

#### user_stats (사용자 통계)

```sql
CREATE TABLE user_stats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    
    -- 레벨/XP
    level INTEGER DEFAULT 1,
    xp INTEGER DEFAULT 0,
    
    -- 통계
    problems_solved INTEGER DEFAULT 0,
    total_attempts INTEGER DEFAULT 0,
    current_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    last_activity_date DATE,
    
    -- 계산된 레벨
    calculated_level VARCHAR(20) DEFAULT 'beginner',
    level_confidence DECIMAL(3,2) DEFAULT 0.5,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### codes (생성된 코드)

```sql
CREATE TABLE codes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- 메타데이터
    language VARCHAR(20) NOT NULL,
    framework VARCHAR(50),
    topic VARCHAR(100) NOT NULL,
    difficulty VARCHAR(20) NOT NULL,
    
    -- 코드 내용
    code TEXT NOT NULL,
    description TEXT,
    
    -- 임베딩 (RAG용)
    embedding VECTOR(1536),
    
    -- 통계
    times_used INTEGER DEFAULT 0,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX codes_embedding_idx ON codes 
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
```

#### problems (문제)

```sql
CREATE TABLE problems (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code_id UUID REFERENCES codes(id) ON DELETE CASCADE,
    
    -- 문제 유형
    problem_type VARCHAR(20) NOT NULL 
        CHECK (problem_type IN ('blank', 'puzzle', 'guided', 'implementation')),
    
    -- 문제 내용
    title VARCHAR(200) NOT NULL,
    description TEXT,
    
    -- 유형별 데이터 (JSONB)
    problem_data JSONB NOT NULL,
    
    -- 메타데이터
    difficulty VARCHAR(20) NOT NULL,
    language VARCHAR(20) NOT NULL,
    tags TEXT[],
    
    -- 통계
    times_attempted INTEGER DEFAULT 0,
    times_solved INTEGER DEFAULT 0,
    avg_time_seconds INTEGER,
    
    -- 임베딩
    embedding VECTOR(1536),
    
    is_public BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- problem_data 구조 (유형별)

-- blank:
-- {
--   "blanks": [
--     {"index": 0, "answer": "{}", "hint": "빈 딕셔너리"},
--     {"index": 1, "answer": "num", "hint": "현재 숫자"}
--   ],
--   "code_with_blanks": "hash_map = ___\nfor i, num in enumerate(nums):\n    complement = target - ___"
-- }

-- puzzle:
-- {
--   "blocks": [
--     {"id": "b1", "code": "def sum_array(arr):", "indentation": 0},
--     {"id": "b2", "code": "result = 0", "indentation": 1}
--   ],
--   "correct_order": ["b1", "b2", "b3", "b4", "b5"],
--   "distractors": [
--     {"id": "d1", "code": "return arr", "indentation": 1}
--   ]
-- }

-- guided:
-- {
--   "steps": [
--     {
--       "step_number": 1,
--       "ai_message": "Two Sum 문제를 풀어볼까요?",
--       "response_type": "text",
--       "hint": "배열을 생각해보세요"
--     },
--     {
--       "step_number": 2,
--       "ai_message": "어떤 자료구조를 사용할까요?",
--       "response_type": "choice",
--       "choices": ["배열", "해시맵", "스택"],
--       "correct_choice": 1
--     }
--   ],
--   "final_code": "def solution(nums, target):\n    ..."
-- }

-- implementation:
-- {
--   "function_signature": "def solution(nums: list[int], target: int) -> list[int]:",
--   "test_cases": [
--     {"input": [[2,7,11,15], 9], "expected": [0,1]},
--     {"input": [[3,2,4], 6], "expected": [1,2]}
--   ]
-- }

CREATE INDEX problems_type_idx ON problems(problem_type);
CREATE INDEX problems_difficulty_idx ON problems(difficulty);
CREATE INDEX problems_language_idx ON problems(language);
CREATE INDEX problems_embedding_idx ON problems 
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
```

#### attempts (풀이 시도)

```sql
CREATE TABLE attempts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    problem_id UUID REFERENCES problems(id) ON DELETE CASCADE,
    
    -- 제출 내용
    submission JSONB NOT NULL,
    
    -- 결과
    is_correct BOOLEAN NOT NULL,
    score INTEGER,
    
    -- 메타데이터
    hints_used INTEGER DEFAULT 0,
    time_spent_seconds INTEGER,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX attempts_user_idx ON attempts(user_id);
CREATE INDEX attempts_problem_idx ON attempts(problem_id);
CREATE INDEX attempts_created_idx ON attempts(created_at DESC);
```

#### puzzle_attempts (퍼즐 시도 상세)

```sql
CREATE TABLE puzzle_attempts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    attempt_id UUID REFERENCES attempts(id) ON DELETE CASCADE,
    
    submitted_order TEXT[],
    submitted_indentations INTEGER[],
    is_order_correct BOOLEAN,
    is_indentation_correct BOOLEAN,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### guided_sessions (1대1 대화형 세션)

```sql
CREATE TABLE guided_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    problem_id UUID REFERENCES problems(id) ON DELETE CASCADE,
    
    current_step INTEGER DEFAULT 1,
    responses JSONB DEFAULT '[]',
    
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    is_completed BOOLEAN DEFAULT FALSE,
    
    hints_used INTEGER DEFAULT 0,
    skips_used INTEGER DEFAULT 0
);

-- responses 구조
-- [
--   {"step": 1, "response": "이중 for문", "correct": true, "time": 15},
--   {"step": 2, "response": "O(n²)", "correct": true, "time": 8}
-- ]
```

#### hint_logs (힌트 사용 로그)

```sql
CREATE TABLE hint_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    problem_id UUID REFERENCES problems(id) ON DELETE CASCADE,
    attempt_id UUID REFERENCES attempts(id) ON DELETE CASCADE,
    
    hint_level INTEGER NOT NULL,
    hint_content TEXT NOT NULL,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### daily_activity (일일 활동)

```sql
CREATE TABLE daily_activity (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    activity_date DATE NOT NULL,
    
    problems_attempted INTEGER DEFAULT 0,
    problems_solved INTEGER DEFAULT 0,
    xp_earned INTEGER DEFAULT 0,
    time_spent_minutes INTEGER DEFAULT 0,
    
    UNIQUE(user_id, activity_date)
);

CREATE INDEX daily_activity_user_date_idx ON daily_activity(user_id, activity_date DESC);
```

#### badges (뱃지)

```sql
CREATE TABLE badges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    image_url TEXT,
    condition JSONB NOT NULL,
    xp_reward INTEGER DEFAULT 0,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- condition 예시
-- {"type": "streak", "value": 7}
-- {"type": "problems_solved", "value": 100}
-- {"type": "level", "value": 10}
```

#### user_badges (사용자 뱃지)

```sql
CREATE TABLE user_badges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    badge_id UUID REFERENCES badges(id) ON DELETE CASCADE,
    
    earned_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(user_id, badge_id)
);
```

#### user_farm (농장)

```sql
CREATE TABLE user_farm (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    
    -- 캐릭터
    character_created BOOLEAN DEFAULT FALSE,
    character_data JSONB DEFAULT '{}',
    farm_unlocked BOOLEAN DEFAULT FALSE,
    
    -- 농장 상태
    farm_level INTEGER DEFAULT 1,
    seeds INTEGER DEFAULT 10,
    farm_slots JSONB DEFAULT '[]',
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- character_data 구조
-- {
--   "hair": "style_02",
--   "hair_color": "#8B4513",
--   "face": "face_01",
--   "outfit": "outfit_casual",
--   "outfit_color": "#4169E1",
--   "created_at": "2025-01-15T10:30:00Z"
-- }

-- farm_slots 구조
-- [
--   {"slot": 0, "item_id": "crop_001", "planted_at": "...", "status": "growing"},
--   {"slot": 1, "item_id": null, "status": "empty"}
-- ]
```

#### farm_items (농장 아이템)

```sql
CREATE TABLE farm_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL,
    description TEXT,
    image_url TEXT,
    
    -- 가격/보상
    seed_cost INTEGER,
    xp_reward INTEGER,
    seed_reward INTEGER,
    
    -- 성장 시간 (분)
    grow_time_minutes INTEGER,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### user_inventory (인벤토리)

```sql
CREATE TABLE user_inventory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    item_id UUID REFERENCES farm_items(id) ON DELETE CASCADE,
    quantity INTEGER DEFAULT 0,
    
    UNIQUE(user_id, item_id)
);
```

#### plans (요금제)

```sql
CREATE TABLE plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) NOT NULL,
    price INTEGER NOT NULL,
    currency VARCHAR(10) DEFAULT 'KRW',
    interval VARCHAR(20) DEFAULT 'month',
    
    features JSONB NOT NULL,
    
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- features 구조
-- {
--   "daily_problems": -1,      -- -1 = 무제한
--   "daily_hints": -1,
--   "daily_chat": -1,
--   "problem_types": ["blank", "puzzle", "guided", "implementation"],
--   "ad_free": true,
--   "farm_full": true
-- }
```

#### subscriptions (구독)

```sql
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    plan_id UUID REFERENCES plans(id),
    
    status VARCHAR(20) DEFAULT 'active',
    current_period_start TIMESTAMPTZ,
    current_period_end TIMESTAMPTZ,
    
    canceled_at TIMESTAMPTZ,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### payments (결제)

```sql
CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    subscription_id UUID REFERENCES subscriptions(id),
    
    amount INTEGER NOT NULL,
    currency VARCHAR(10) DEFAULT 'KRW',
    status VARCHAR(20) NOT NULL,
    
    pg_provider VARCHAR(50),
    pg_transaction_id VARCHAR(255),
    
    paid_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 4. API 명세

### 4.1 인증 API

```yaml
POST /auth/signup
  Description: 회원가입 (온보딩 완료 후)
  Request:
    email: string
    password: string
    nickname: string
    onboarding_data: object
  Response:
    user: User
    access_token: string
    refresh_token: string

POST /auth/login
  Description: 로그인
  Request:
    email: string
    password: string
  Response:
    user: User
    access_token: string
    refresh_token: string

POST /auth/logout
  Description: 로그아웃
  Headers: Authorization: Bearer {token}
  Response:
    success: boolean

POST /auth/refresh
  Description: 토큰 갱신
  Request:
    refresh_token: string
  Response:
    access_token: string
    refresh_token: string

POST /auth/social/{provider}
  Description: 소셜 로그인 (google, kakao, github)
  Request:
    code: string
  Response:
    user: User
    access_token: string
    is_new_user: boolean

POST /auth/onboarding
  Description: 온보딩 단계별 저장
  Request:
    step: number
    data: object
  Response:
    next_step: number
    progress: number
```

### 4.2 사용자 API

```yaml
GET /users/me
  Description: 내 정보 조회
  Response:
    user: User
    stats: UserStats
    subscription: Subscription | null

PATCH /users/me
  Description: 내 정보 수정
  Request:
    nickname?: string
    profile_image_url?: string
  Response:
    user: User

POST /users/me/solved-ac
  Description: solved.ac 연동
  Request:
    username: string
  Response:
    success: boolean
    data: SolvedAcData

GET /users/me/stats
  Description: 내 통계 조회
  Response:
    stats: UserStats
    daily_activity: DailyActivity[]
    badges: Badge[]

GET /users/me/activity
  Description: 잔디 데이터 조회
  Query:
    start_date: string (YYYY-MM-DD)
    end_date: string (YYYY-MM-DD)
  Response:
    activity: DailyActivity[]
```

### 4.3 문제 API

```yaml
GET /problems
  Description: 문제 목록 조회
  Query:
    search?: string
    language?: string
    difficulty?: string
    type?: string (blank, puzzle, guided, implementation)
    sort?: string (views, difficulty, solved_count)
    order?: string (asc, desc)
    page?: number
    limit?: number
  Response:
    problems: Problem[]
    total: number
    page: number
    total_pages: number

GET /problems/{id}
  Description: 문제 상세 조회
  Response:
    problem: Problem
    code: Code
    user_attempts?: Attempt[]

POST /problems/generate
  Description: 문제 생성 (Chat에서 호출)
  Request:
    topic: string
    language: string
    difficulty: string
    problem_type: string
  Response:
    problem: Problem

POST /problems/{id}/submit
  Description: 답안 제출
  Request:
    submission: object (유형별 다름)
  Response:
    is_correct: boolean
    score: number
    feedback: string
    xp_earned: number

POST /problems/{id}/hint
  Description: 힌트 요청
  Request:
    level: number (1, 2, 3)
  Response:
    hint: string
    hints_remaining: number
```

### 4.4 채팅 API

```yaml
POST /chat/message
  Description: 채팅 메시지 전송
  Request:
    message: string
    context?: object
  Response:
    reply: string
    action?: object (문제 생성, 페이지 이동 등)

POST /chat/guided/{problem_id}/respond
  Description: 1대1 대화형 응답
  Request:
    step: number
    response: string | number
  Response:
    is_correct: boolean
    feedback: string
    next_step?: GuidedStep
    is_completed: boolean

GET /chat/guided/{problem_id}/session
  Description: 1대1 대화형 세션 조회
  Response:
    session: GuidedSession
    current_step: GuidedStep
```

### 4.5 농장 API

```yaml
GET /farm
  Description: 농장 상태 조회
  Response:
    farm: UserFarm
    inventory: UserInventory[]

POST /farm/character
  Description: 캐릭터 생성
  Request:
    hair: string
    hair_color: string
    face: string
    outfit: string
    outfit_color: string
  Response:
    character: CharacterData
    farm_unlocked: boolean

GET /farm/character/options
  Description: 캐릭터 옵션 목록
  Response:
    hair_styles: string[]
    faces: string[]
    outfits: string[]
    colors: string[]

POST /farm/plant
  Description: 농작물 심기
  Request:
    slot: number
    item_id: string
  Response:
    farm: UserFarm
    seeds_remaining: number

POST /farm/harvest
  Description: 농작물 수확
  Request:
    slot: number
  Response:
    farm: UserFarm
    rewards: { xp: number, seeds: number }

GET /farm/shop
  Description: 상점 아이템 목록
  Response:
    items: FarmItem[]

POST /farm/shop/buy
  Description: 아이템 구매
  Request:
    item_id: string
    quantity: number
  Response:
    inventory: UserInventory
    seeds_remaining: number
```

### 4.6 구독 API

```yaml
GET /subscriptions/plans
  Description: 요금제 목록
  Response:
    plans: Plan[]

GET /subscriptions/me
  Description: 내 구독 정보
  Response:
    subscription: Subscription | null
    usage: { problems_today, hints_today, chat_today }

POST /subscriptions/subscribe
  Description: 구독 시작
  Request:
    plan_id: string
    payment_method: string
  Response:
    subscription: Subscription
    payment_url: string

POST /subscriptions/cancel
  Description: 구독 취소
  Response:
    subscription: Subscription

POST /subscriptions/webhook
  Description: 결제 웹훅 (PG사에서 호출)
  Request:
    (PG사별 상이)
  Response:
    success: boolean
```

---

## 5. Agent 구현

### 5.1 Chat Agent

```python
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from pydantic import BaseModel

class ChatIntent(BaseModel):
    intent: str  # "generate_problem", "ask_question", "navigate", "other"
    problem_info: dict | None
    confidence: float

CHAT_AGENT_PROMPT = """
# Role
당신은 CodeFill의 AI 어시스턴트입니다. 사용자가 코딩 학습을 할 수 있도록 도와주세요.

# Tasks
1. 사용자의 의도 파악 (문제 풀기, 질문, 탐색 등)
2. 문제 생성에 필요한 정보 수집 (언어, 유형, 난이도, 주제)
3. 친근하고 격려하는 톤 유지

# Information to Collect (for problem generation)
- language: python, java, cpp, javascript
- problem_type: blank, puzzle, guided, implementation
- topic: 알고리즘/자료구조 주제
- difficulty: easy, medium, hard

# Rules
- 한국어로 대화
- 정보가 부족하면 자연스럽게 질문
- 모든 정보가 모이면 문제 생성 제안

# User Message
{user_message}

# Conversation History
{history}

# Output Format (JSON)
{{
  "reply": "사용자에게 보낼 메시지",
  "intent": "generate_problem | ask_question | navigate | other",
  "collected_info": {{
    "language": "python",
    "problem_type": "blank",
    "topic": "two sum",
    "difficulty": "easy"
  }},
  "ready_to_generate": true | false
}}
"""

class ChatAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.7
        )
        self.prompt = ChatPromptTemplate.from_template(CHAT_AGENT_PROMPT)
    
    async def process(self, message: str, history: list) -> dict:
        response = await self.llm.ainvoke(
            self.prompt.format(
                user_message=message,
                history=self._format_history(history)
            )
        )
        return self._parse_response(response.content)
```

### 5.2 Problem Gen Agent

```python
PROBLEM_GEN_PROMPTS = {
    "blank": """
# Task
주어진 코드를 빈칸 채우기 문제로 변환하세요.

# Input Code
{code}

# Difficulty: {difficulty}
# 빈칸 수: Easy=1-2개, Medium=3-4개, Hard=5-6개

# Output Format (JSON)
{{
  "blanks": [
    {{"index": 0, "answer": "정답", "hint": "힌트 텍스트"}},
    ...
  ],
  "code_with_blanks": "빈칸이 ___로 표시된 코드"
}}
""",
    
    "puzzle": """
# Task
주어진 코드를 블록 정렬 문제로 변환하세요.

# Input Code
{code}

# Rules
1. 코드를 논리적 단위로 분리
2. 각 블록의 들여쓰기 레벨 명시
3. 1-2개의 함정 블록 추가

# Output Format (JSON)
{{
  "blocks": [
    {{"id": "b1", "code": "코드 라인", "indentation": 0}},
    ...
  ],
  "correct_order": ["b1", "b2", "b3"],
  "distractors": [
    {{"id": "d1", "code": "함정 코드", "indentation": 0}}
  ]
}}
""",
    
    "guided": """
# Task
주어진 문제를 1대1 대화형 학습 시나리오로 변환하세요.

# Input
Topic: {topic}
Code: {code}
Difficulty: {difficulty}

# Rules
1. 5-10 단계로 구성
2. 각 단계에서 사고를 유도하는 질문
3. 정답을 바로 주지 않기
4. 중간에 빈칸 채우기나 선택지 삽입

# Output Format (JSON)
{{
  "steps": [
    {{
      "step_number": 1,
      "ai_message": "AI 메시지",
      "response_type": "text | choice | code",
      "choices": ["선택지1", "선택지2"],  // choice인 경우
      "correct_choice": 0,                 // choice인 경우
      "code_template": "hash_map = ___",   // code인 경우
      "correct_code": "{{}}",               // code인 경우
      "hint": "힌트"
    }},
    ...
  ],
  "final_code": "최종 완성 코드"
}}
""",
    
    "implementation": """
# Task
주어진 코드를 구현 문제로 변환하세요.

# Input Code
{code}

# Output Format (JSON)
{{
  "function_signature": "def solution(nums: list[int]) -> int:",
  "test_cases": [
    {{"input": [[1,2,3]], "expected": 6}},
    {{"input": [[]], "expected": 0}}
  ],
  "hidden_test_cases": [
    {{"input": [[1,2,3,4,5]], "expected": 15}}
  ]
}}
"""
}

class ProblemGenAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
    
    async def generate(self, code: str, problem_type: str, difficulty: str) -> dict:
        prompt = PROBLEM_GEN_PROMPTS[problem_type].format(
            code=code,
            difficulty=difficulty,
            topic=self._extract_topic(code)
        )
        
        response = await self.llm.ainvoke(prompt)
        return json.loads(response.content)
```

### 5.3 Guided Agent

```python
GUIDED_AGENT_PROMPT = """
# Role
당신은 1대1 코딩 튜터입니다. 학습자가 스스로 문제를 풀 수 있도록 유도하세요.

# Rules
1. 정답을 직접 알려주지 마세요
2. 질문으로 사고를 유도하세요
3. 틀려도 격려하며 힌트를 주세요
4. 한국어로 친근하게 대화하세요

# Problem
{problem_description}

# Current Step
{current_step}

# User Response
{user_response}

# Expected Answer
{expected_answer}

# Task
사용자 응답을 평가하고 다음 메시지를 생성하세요.

# Output Format (JSON)
{{
  "is_correct": true | false,
  "feedback": "피드백 메시지",
  "next_message": "다음 단계 메시지 (정답인 경우)",
  "hint": "힌트 (오답인 경우)"
}}
"""

class GuidedAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
    
    async def evaluate_response(
        self, 
        problem: dict,
        step: dict,
        user_response: str
    ) -> dict:
        prompt = GUIDED_AGENT_PROMPT.format(
            problem_description=problem["description"],
            current_step=json.dumps(step, ensure_ascii=False),
            user_response=user_response,
            expected_answer=step.get("correct_answer", step.get("correct_choice"))
        )
        
        response = await self.llm.ainvoke(prompt)
        return json.loads(response.content)
```

### 5.4 Answer Checker

```python
class AnswerChecker:
    """유형별 채점 로직"""
    
    def check_blank(self, submission: dict, problem_data: dict) -> dict:
        """빈칸 채점 - 문자열 비교"""
        blanks = problem_data["blanks"]
        answers = submission["answers"]
        
        correct_count = 0
        results = []
        
        for i, blank in enumerate(blanks):
            user_answer = self._normalize(answers.get(str(i), ""))
            correct_answer = self._normalize(blank["answer"])
            
            is_correct = user_answer == correct_answer
            if is_correct:
                correct_count += 1
            
            results.append({
                "index": i,
                "is_correct": is_correct,
                "user_answer": user_answer,
                "correct_answer": correct_answer if not is_correct else None
            })
        
        return {
            "is_correct": correct_count == len(blanks),
            "score": int(correct_count / len(blanks) * 100),
            "results": results
        }
    
    def check_puzzle(self, submission: dict, problem_data: dict) -> dict:
        """퍼즐 채점 - 순서 + 들여쓰기"""
        correct_order = problem_data["correct_order"]
        blocks = {b["id"]: b for b in problem_data["blocks"]}
        
        submitted_order = submission["order"]
        submitted_indents = submission["indentations"]
        
        # 순서 체크
        order_correct = submitted_order == correct_order
        
        # 들여쓰기 체크
        correct_indents = [blocks[bid]["indentation"] for bid in correct_order]
        indent_correct = submitted_indents == correct_indents
        
        # 부분 점수
        order_score = self._calculate_lcs_score(submitted_order, correct_order)
        indent_score = sum(
            1 for a, b in zip(submitted_indents, correct_indents) if a == b
        ) / len(correct_indents) if correct_indents else 0
        
        return {
            "is_correct": order_correct and indent_correct,
            "score": int((order_score * 0.7 + indent_score * 0.3) * 100),
            "order_correct": order_correct,
            "indent_correct": indent_correct
        }
    
    def check_implementation(self, submission: dict, problem_data: dict) -> dict:
        """구현 채점 - 테스트 케이스 실행"""
        code = submission["code"]
        test_cases = problem_data["test_cases"]
        
        results = []
        passed = 0
        
        for tc in test_cases:
            try:
                result = self._execute_code(code, tc["input"])
                is_correct = result == tc["expected"]
                if is_correct:
                    passed += 1
                results.append({
                    "input": tc["input"],
                    "expected": tc["expected"],
                    "actual": result,
                    "is_correct": is_correct
                })
            except Exception as e:
                results.append({
                    "input": tc["input"],
                    "error": str(e),
                    "is_correct": False
                })
        
        return {
            "is_correct": passed == len(test_cases),
            "score": int(passed / len(test_cases) * 100),
            "passed": passed,
            "total": len(test_cases),
            "results": results
        }
    
    def _normalize(self, s: str) -> str:
        """문자열 정규화 (공백, 대소문자)"""
        return s.strip().lower().replace(" ", "")
    
    def _calculate_lcs_score(self, a: list, b: list) -> float:
        """LCS 기반 유사도 점수"""
        # ... LCS 알고리즘 구현
        pass
    
    def _execute_code(self, code: str, inputs: list) -> any:
        """코드 실행 (Judge0 또는 Sandpack)"""
        # ... 코드 실행 구현
        pass
```

---

## 6. Frontend 컴포넌트

### 6.1 문제 유형별 컴포넌트 구조

```
components/
├── problems/
│   ├── ProblemRenderer.tsx       # 유형별 분기
│   ├── BlankProblem.tsx          # 빈칸 채우기
│   ├── PuzzleProblem.tsx         # 드래그 앤 드롭
│   ├── GuidedProblem.tsx         # 1대1 대화형
│   ├── ImplementationProblem.tsx # 전체 구현
│   └── shared/
│       ├── CodeEditor.tsx        # Monaco Editor 래퍼
│       ├── TestResults.tsx       # 테스트 결과 표시
│       └── HintButton.tsx        # 힌트 버튼
```

### 6.2 PuzzleProblem 컴포넌트

```tsx
// components/problems/PuzzleProblem.tsx
import { DndContext, closestCenter } from '@dnd-kit/core';
import { SortableContext, verticalListSortingStrategy } from '@dnd-kit/sortable';
import { useState } from 'react';

interface Block {
  id: string;
  code: string;
  indentation: number;
}

interface PuzzleProblemProps {
  problem: {
    blocks: Block[];
    distractors?: Block[];
  };
  onSubmit: (submission: { order: string[]; indentations: number[] }) => void;
}

export function PuzzleProblem({ problem, onSubmit }: PuzzleProblemProps) {
  const [availableBlocks, setAvailableBlocks] = useState([
    ...problem.blocks,
    ...(problem.distractors || [])
  ].sort(() => Math.random() - 0.5));
  
  const [answerBlocks, setAnswerBlocks] = useState<Block[]>([]);
  const [selectedBlock, setSelectedBlock] = useState<string | null>(null);

  const handleDragEnd = (event: any) => {
    const { active, over } = event;
    // 드래그 앤 드롭 로직
  };

  const adjustIndentation = (blockId: string, delta: number) => {
    setAnswerBlocks(blocks =>
      blocks.map(b =>
        b.id === blockId
          ? { ...b, indentation: Math.max(0, Math.min(4, b.indentation + delta)) }
          : b
      )
    );
  };

  const handleSubmit = () => {
    onSubmit({
      order: answerBlocks.map(b => b.id),
      indentations: answerBlocks.map(b => b.indentation)
    });
  };

  return (
    <div className="flex gap-4 h-full">
      {/* 사용 가능한 블록 */}
      <div className="w-1/2 p-4 bg-gray-50 rounded-lg">
        <h3 className="font-semibold mb-4">사용 가능한 블록</h3>
        <DndContext collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
          <SortableContext items={availableBlocks} strategy={verticalListSortingStrategy}>
            {availableBlocks.map(block => (
              <SortableBlock key={block.id} block={block} />
            ))}
          </SortableContext>
        </DndContext>
      </div>

      {/* 정답 영역 */}
      <div className="w-1/2 p-4 bg-white border rounded-lg">
        <h3 className="font-semibold mb-4">정답 영역</h3>
        <DndContext collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
          <SortableContext items={answerBlocks} strategy={verticalListSortingStrategy}>
            {answerBlocks.length === 0 ? (
              <div className="h-32 border-2 border-dashed rounded flex items-center justify-center text-gray-400">
                블록을 여기로 드래그하세요
              </div>
            ) : (
              answerBlocks.map(block => (
                <SortableBlock
                  key={block.id}
                  block={block}
                  showIndentControls
                  onIndentChange={(delta) => adjustIndentation(block.id, delta)}
                />
              ))
            )}
          </SortableContext>
        </DndContext>

        {/* 들여쓰기 조절 */}
        {selectedBlock && (
          <div className="mt-4 flex gap-2">
            <button onClick={() => adjustIndentation(selectedBlock, -1)}>
              ← 들여쓰기 감소
            </button>
            <button onClick={() => adjustIndentation(selectedBlock, 1)}>
              들여쓰기 증가 →
            </button>
          </div>
        )}
      </div>

      {/* 제출 버튼 */}
      <div className="fixed bottom-4 right-4 flex gap-2">
        <button onClick={handleSubmit} className="btn-primary">
          제출하기
        </button>
      </div>
    </div>
  );
}
```

### 6.3 문제풀이 페이지 레이아웃

```tsx
// app/problem/[id]/page.tsx
'use client';

import { useState } from 'react';
import { cn } from '@/lib/utils';
import { ChatBot } from '@/components/chat/ChatBot';
import { ProblemRenderer } from '@/components/problems/ProblemRenderer';
import { ProblemDescription } from '@/components/problems/ProblemDescription';

export default function ProblemPage({ params }: { params: { id: string } }) {
  const [isDescriptionOpen, setIsDescriptionOpen] = useState(false);
  const { data: problem } = useProblem(params.id);

  return (
    <div className="flex h-screen">
      {/* 챗봇 영역 */}
      <div
        className={cn(
          'transition-all duration-300 border-r flex flex-col',
          isDescriptionOpen ? 'w-[25%]' : 'w-[40%]'
        )}
      >
        <ChatBot problem={problem} />
      </div>

      {/* 문제 풀이 영역 */}
      <div
        className={cn(
          'transition-all duration-300 flex flex-col',
          isDescriptionOpen ? 'w-[45%]' : 'w-[60%]'
        )}
      >
        <ProblemRenderer problem={problem} />
      </div>

      {/* 토글 버튼 */}
      <button
        onClick={() => setIsDescriptionOpen(!isDescriptionOpen)}
        className={cn(
          'w-10 bg-gray-100 hover:bg-gray-200',
          'flex items-center justify-center',
          'border-l transition-colors'
        )}
      >
        {isDescriptionOpen ? '→' : '📖'}
      </button>

      {/* 문제 설명 패널 */}
      <div
        className={cn(
          'transition-all duration-300 border-l overflow-hidden',
          isDescriptionOpen ? 'w-[30%]' : 'w-0'
        )}
      >
        {isDescriptionOpen && (
          <ProblemDescription
            problem={problem}
            onClose={() => setIsDescriptionOpen(false)}
          />
        )}
      </div>
    </div>
  );
}
```

---

## 7. 인프라 구성

### 7.1 배포 구조

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Production                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐       │
│  │   Cloudflare    │     │     Vercel      │     │   Cloud Run     │       │
│  │      CDN        │────▶│    Frontend     │────▶│    Backend      │       │
│  │                 │     │   (Next.js)     │     │   (FastAPI)     │       │
│  └─────────────────┘     └─────────────────┘     └────────┬────────┘       │
│                                                           │                 │
│          ┌────────────────────────────────────────────────┤                 │
│          │                    │                           │                 │
│          ▼                    ▼                           ▼                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────┐    │
│  │    Supabase     │  │     Redis       │  │      OpenRouter         │    │
│  │   PostgreSQL    │  │   (Upstash)     │  │     (LLM API)           │    │
│  └─────────────────┘  └─────────────────┘  └─────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 7.2 환경 변수

```bash
# Frontend (.env.local)
NEXT_PUBLIC_API_URL=https://api.codefill.io
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=xxx

# Backend (.env)
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
OPENROUTER_API_KEY=xxx
OPENAI_API_KEY=xxx
SUPABASE_SERVICE_KEY=xxx
JUDGE0_API_KEY=xxx
TOSS_CLIENT_KEY=xxx
TOSS_SECRET_KEY=xxx
RESEND_API_KEY=xxx
SENTRY_DSN=xxx
```

### 7.3 CI/CD (GitHub Actions)

```yaml
# .github/workflows/deploy-frontend.yml
name: Deploy Frontend

on:
  push:
    branches: [main]
    paths:
      - 'frontend/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          vercel-args: '--prod'

---
# .github/workflows/deploy-backend.yml
name: Deploy Backend

on:
  push:
    branches: [main]
    paths:
      - 'backend/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Run Tests
        run: |
          cd backend
          pip install -r requirements.txt
          pytest
      
      - name: Deploy to Cloud Run
        uses: google-github-actions/deploy-cloudrun@v2
        with:
          service: codefill-api
          region: asia-northeast3
          source: ./backend
```

---

## 8. 보안

### 8.1 인증/인가

```python
# JWT 설정
JWT_SECRET = os.environ["JWT_SECRET"]
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE = timedelta(hours=1)
REFRESH_TOKEN_EXPIRE = timedelta(days=30)

# 미들웨어
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    if request.url.path in PUBLIC_PATHS:
        return await call_next(request)
    
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        request.state.user_id = payload["sub"]
    except jwt.InvalidTokenError:
        return JSONResponse(status_code=401, content={"error": "Invalid token"})
    
    return await call_next(request)
```

### 8.2 Rate Limiting

```python
# 요금제별 Rate Limit
RATE_LIMITS = {
    "free": {
        "problems_per_day": 5,
        "hints_per_day": 3,
        "chat_per_day": 10
    },
    "pro": {
        "problems_per_day": -1,  # 무제한
        "hints_per_day": -1,
        "chat_per_day": -1
    }
}

async def check_rate_limit(user_id: str, action: str) -> bool:
    user = await get_user(user_id)
    plan = user.subscription.plan if user.subscription else "free"
    
    limit = RATE_LIMITS[plan][f"{action}_per_day"]
    if limit == -1:
        return True
    
    key = f"rate:{user_id}:{action}:{date.today()}"
    current = await redis.get(key) or 0
    
    if current >= limit:
        return False
    
    await redis.incr(key)
    await redis.expire(key, 86400)
    return True
```

### 8.3 코드 실행 보안

```python
# Judge0 설정
JUDGE0_CONFIG = {
    "cpu_time_limit": 5,        # 초
    "wall_time_limit": 10,      # 초
    "memory_limit": 128000,     # KB
    "stack_limit": 64000,       # KB
    "max_processes_and_or_threads": 30,
    "enable_network": False
}

async def execute_code(code: str, language: str, stdin: str = "") -> dict:
    # 위험한 코드 패턴 체크
    if contains_dangerous_patterns(code, language):
        return {"error": "Potentially dangerous code detected"}
    
    # Judge0 실행
    response = await judge0_client.submit(
        source_code=code,
        language_id=LANGUAGE_IDS[language],
        stdin=stdin,
        **JUDGE0_CONFIG
    )
    
    return response
```

---

## 9. 성능 최적화

### 9.1 캐싱 전략

```python
# Redis 캐싱
class CacheService:
    def __init__(self):
        self.redis = redis.Redis.from_url(REDIS_URL)
    
    async def get_or_set(self, key: str, fn: callable, ttl: int = 3600):
        cached = await self.redis.get(key)
        if cached:
            return json.loads(cached)
        
        result = await fn()
        await self.redis.setex(key, ttl, json.dumps(result))
        return result

# 사용 예시
@router.get("/problems/{id}")
async def get_problem(id: str):
    return await cache.get_or_set(
        f"problem:{id}",
        lambda: problem_service.get(id),
        ttl=3600
    )
```

### 9.2 LLM 응답 캐싱

```python
# 문제 생성 캐싱
async def generate_problem(topic: str, difficulty: str, problem_type: str):
    cache_key = f"gen:{topic}:{difficulty}:{problem_type}"
    
    # 캐시 확인
    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # RAG: 유사 문제 검색
    similar = await search_similar_problems(topic, difficulty, problem_type)
    if similar and similar.similarity > 0.9:
        return similar.problem
    
    # LLM 생성
    problem = await llm_generate(topic, difficulty, problem_type)
    
    # 캐싱 (24시간)
    await redis.setex(cache_key, 86400, json.dumps(problem))
    
    # DB 저장
    await save_problem(problem)
    
    return problem
```

---

## 10. 모니터링

### 10.1 로깅

```python
import structlog

logger = structlog.get_logger()

# 요청 로깅
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    
    logger.info(
        "request",
        method=request.method,
        path=request.url.path,
        status=response.status_code,
        duration=duration,
        user_id=getattr(request.state, "user_id", None)
    )
    
    return response
```

### 10.2 에러 추적 (Sentry)

```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=SENTRY_DSN,
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,
    environment="production"
)

# 커스텀 에러 보고
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    sentry_sdk.capture_exception(exc)
    
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )
```

### 10.3 메트릭

```python
# Prometheus 메트릭
from prometheus_client import Counter, Histogram

REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)

LLM_COST = Counter(
    'llm_cost_total',
    'Total LLM API cost',
    ['model', 'agent']
)
```

---

## 11. 보류 기능 (v3.1+)

### 11.1 보류된 Agent

| Agent | 역할 | 예상 버전 |
| --- | --- | --- |
| **Learning Path Agent** | 커리큘럼 생성 | v3.1 |
| **Practice Agent** | 복습 스케줄 관리 | v3.1 |
| **Tutor Dashboard Agent** | 약점 분석 | v3.1 |

### 11.2 보류된 테이블

```sql
-- v3.1에서 추가 예정
CREATE TABLE learning_goals (...);
CREATE TABLE learning_path (...);
CREATE TABLE review_schedule (...);
CREATE TABLE tutor_sessions (...);
```

### 11.3 보류된 API

```yaml
# v3.1에서 추가 예정
POST /path/generate
GET /path/me
POST /review/schedule
GET /tutor/analysis
```

---

## 12. 개발 일정

### 12.1 Sprint 계획

| Sprint | 기간 | 내용 |
| --- | --- | --- |
| **Sprint 1** | 2주 | 온보딩, 인증, 기본 UI |
| **Sprint 2** | 2주 | 빈칸/퍼즐 문제 유형 |
| **Sprint 3** | 2주 | 1대1 대화형/구현 유형 |
| **Sprint 4** | 2주 | Problems 목록, Chat 통합 |
| **Sprint 5** | 2주 | 농장, 캐릭터 생성 |
| **Sprint 6** | 2주 | 결제, QA, 출시 |


---

## 13. 부록

### 13.1 LLM 모델 비용

| Agent | 모델 | 예상 호출/일 | 비용/일 |
| --- | --- | --- | --- |
| Chat | GPT-4o-mini | 1,000 | $0.15 |
| Code Gen | Claude Sonnet | 200 | $0.60 |
| Problem Gen | GPT-4o-mini | 200 | $0.03 |
| Guided | GPT-4o-mini | 500 | $0.075 |
| Hint | Gemini Flash | 300 | $0.02 |
| **Total** | | | **~$0.88/일** |

### 13.2 인프라 비용 (월)

| 서비스 | 예상 비용 |
| --- | --- |
| Vercel (Frontend) | $20 |
| Cloud Run (Backend) | $50 |
| Supabase (DB) | $25 |
| Redis (Upstash) | $10 |
| OpenRouter (LLM) | $30 |
| **Total** | **~$135/월** |

---

**문서 끝**
