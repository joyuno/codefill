# CodeFill TRD v2

## 목차

1. [Technical Overview](#1-technical-overview)
2. [System Architecture](#2-system-architecture)
3. [Database Schema](#3-database-schema)
4. [API Specification](#4-api-specification)
5. [Agent Implementation](#5-agent-implementation)
6. [Infrastructure](#6-infrastructure)
7. [Security & Performance](#7-security--performance)
8. [Migration Guide](#8-migration-guide)

---

## 1. Technical Overview

### 1.1 Tech Stack

| Layer | Technology |
| --- | --- |
| **Frontend** | Next.js 14+ (App Router), React 19, TailwindCSS, shadcn/ui, Monaco Editor |
| **Backend** | FastAPI (Python) |
| **Database** | PostgreSQL + pgvector (Supabase) |
| **Cache** | Redis |
| **LLM Router** | OpenRouter |
| **Embedding** | OpenAI text-embedding-3-small |
| **Code Execution** | Sandpack (JS/React), Judge0 (Python/Java/C++) |
| **Infra** | Vercel (Frontend), GCP Cloud Run (Backend), Supabase (DB) |

### 1.2 LLM 모델 배정

| 컴포넌트 | 모델 | OpenRouter ID | 선정 이유 |
| --- | --- | --- | --- |
| **Orchestrator** | GPT-4o-mini | `openai/gpt-4o-mini` | 의도 파악만, 비용 효율 |
| **Practice Chatbot** | GPT-4o-mini | `openai/gpt-4o-mini` | 정보 수집, 빠른 응답 |
| **Path Chatbot** | GPT-4o-mini | `openai/gpt-4o-mini` | 정보 수집, 빠른 응답 |
| **Tutor Chatbot** | GPT-4o-mini | `openai/gpt-4o-mini` | 정보 수집, 빠른 응답 |
| **Code Gen** | Claude Sonnet | `anthropic/claude-3.5-sonnet` | 고품질 코드 생성 |
| **Problem Gen (4종)** | GPT-4o-mini | `openai/gpt-4o-mini` | 빠른 생성, 비용 효율 |
| **Hint Agent** | Gemini Flash | `google/gemini-flash-1.5` | 빠른 응답, Docs RAG |
| **Code Review** | Claude Sonnet | `anthropic/claude-3.5-sonnet` | 정확한 품질 평가 |
| **AI Tutor Agent** | Qwen 2.5 72B | `qwen/qwen-2.5-72b-instruct` | 한국어 강점, 비용 효율 |
| **Learning Path Agent** | DeepSeek V3 | `deepseek/deepseek-chat` | 코딩 도메인 강점, 1회성 |
| **Practice Agent** | GPT-4o-mini | `openai/gpt-4o-mini` | 스케줄링 단순 |

### 1.3 아키텍처 핵심 원칙

| 원칙 | 설명 |
| --- | --- |
| **Orchestrator = 의도만** | Context 수집 없이 `[READY_TO_ROUTE: {intent}]`만 출력 |
| **분기별 전용 Chatbot** | 각 도메인에 맞는 정보만 수집 |
| **RAG First** | 생성 전 항상 검색 먼저 |
| **Type-Specific** | 4개 Generator + 4개 Checker 분리 |
| **Background Processing** | Learning Agents는 비동기 실행 |

---

## 2. System Architecture

### 2.1 전체 구조

```
┌──────────────────────────────────────────────────────────────────────────┐
│                              User Request                                 │
└─────────────────────────────────┬────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                     Orchestrator (GPT-4o-mini)                            │
│                                                                           │
│                     대화하며 의도만 파악                                    │
│                     → [READY_TO_ROUTE: {intent}]                          │
└─────────────────────────────────┬────────────────────────────────────────┘
                                  │
        ┌─────────────────────────┼─────────────────────────────┐
        │                         │                             │
        ▼                         ▼                             ▼
   PRACTICE                     PATH                         TUTOR
     Flow                       Flow                          Flow
```

### 2.2 PRACTICE Flow

```
[READY_TO_ROUTE: PRACTICE]
              │
              ▼
┌─────────────────────────────────┐
│     Practice Chatbot            │
│     (GPT-4o-mini)               │
│                                 │
│  수집: Framework, Difficulty,   │
│        Topic, Problem Type      │
└───────────────┬─────────────────┘
                │
                ▼
┌─────────────────────────────────┐
│     RAG Search (pgvector)       │
│                                 │
│  Query Embedding → Vector 검색  │
│  → Re-ranker                    │
└───────────────┬─────────────────┘
                │
        ┌───────┴───────┐
        │ Found         │ Not Found
        ▼               ▼
┌──────────────┐  ┌──────────────┐
│ 기존 문제    │  │  Code Gen    │
│ 반환         │  │ (Claude)     │
└──────┬───────┘  └──────┬───────┘
       │                 │
       └────────┬────────┘
                │
                ▼
┌─────────────────────────────────┐
│     Type Router (규칙 기반)      │
└───────────────┬─────────────────┘
                │
    ┌───────┬───┴───┬───────┐
    ▼       ▼       ▼       ▼
┌───────┐┌───────┐┌───────┐┌───────┐
│Blank  ││Bug    ││Output ││Refactor│
│Gen    ││Gen    ││Gen    ││Gen     │
└───┬───┘└───┬───┘└───┬───┘└───┬───┘
    └────────┴────┬───┴────────┘
                  │
                  ▼
┌─────────────────────────────────┐
│     Practice Page               │
│     (4 Type UIs)                │
│                                 │
│  ├─ Hint → Hint Agent (Gemini) │
│  ├─ Run → Sandbox              │
│  └─ Submit → Answer Checker    │
└───────────────┬─────────────────┘
                │
                ▼
┌─────────────────────────────────┐
│     Answer Checker              │
│                                 │
│  Blank: String Match            │
│  Bug: Test Cases                │
│  Output: Choice Match           │
│  Refactor: Test + Code Review   │
└───────────────┬─────────────────┘
                │
                ▼
┌─────────────────────────────────┐
│     DB Save                     │
│                                 │
│  attempts, attempt_details,     │
│  user_stats, daily_activity,    │
│  review_schedule (오답 시)       │
└─────────────────────────────────┘
```

### 2.3 PATH Flow

```
[READY_TO_ROUTE: PATH]
              │
              ▼
┌─────────────────────────────────┐
│     Path Chatbot                │
│     (GPT-4o-mini)               │
│                                 │
│  수집: Goal, Target Company,    │
│        Period, Current Level    │
└───────────────┬─────────────────┘
                │
                ▼
┌─────────────────────────────────┐
│   Learning Path Agent           │
│   (DeepSeek V3)                 │
│                                 │
│  Input: 수집된 정보 + 기존 풀이  │
└───────────────┬─────────────────┘
                │
                ▼
┌─────────────────────────────────┐
│     Output                      │
│                                 │
│  • Weekly Curriculum            │
│  • Problem List                 │
│  • Milestones                   │
└───────────────┬─────────────────┘
                │
                ▼
┌─────────────────────────────────┐
│     DB Save                     │
│                                 │
│  learning_goals, learning_path, │
│  recommended_problems           │
└───────────────┬─────────────────┘
                │
                ▼
┌─────────────────────────────────┐
│     Path Page                   │
│     (Roadmap Timeline)          │
└─────────────────────────────────┘
```

### 2.4 TUTOR Flow

```
[READY_TO_ROUTE: TUTOR]
              │
              ▼
┌─────────────────────────────────┐
│     Tutor Chatbot               │
│     (GPT-4o-mini)               │
│                                 │
│  수집: Scope, Focus Area,       │
│        Analysis Type            │
└───────────────┬─────────────────┘
                │
                ▼
┌─────────────────────────────────┐
│   Data Aggregation (규칙 기반)   │
│                                 │
│  DB 조회:                        │
│  • user_weaknesses              │
│  • attempts                     │
│  • attempt_details              │
│  • hint_logs                    │
└───────────────┬─────────────────┘
                │
                ▼
┌─────────────────────────────────┐
│   AI Tutor Agent                │
│   (Qwen 2.5 72B)                │
│                                 │
│  Input: 집계된 데이터 + Focus    │
└───────────────┬─────────────────┘
                │
                ▼
┌─────────────────────────────────┐
│     Output                      │
│                                 │
│  • Weakness Report (Top 5)      │
│  • Trend (↑/→/↓)                │
│  • Coaching Message             │
│  • Recommended Problems         │
└───────────────┬─────────────────┘
                │
                ▼
┌─────────────────────────────────┐
│     DB Save                     │
│                                 │
│  user_weaknesses,               │
│  tutor_sessions                 │
└───────────────┬─────────────────┘
                │
                ▼
┌─────────────────────────────────┐
│     Tutor Page                  │
│     (Radar Chart + Trend)       │
└─────────────────────────────────┘
```

### 2.5 보조 Flow

#### REVIEW Flow

```
[READY_TO_ROUTE: REVIEW]
              │
              ▼
┌─────────────────────────────────┐
│   Practice Agent (GPT-4o-mini)  │
│                                 │
│  DB 조회: review_schedule       │
│  WHERE next_review_at <= NOW()  │
└───────────────┬─────────────────┘
                │
                ▼
        오늘 복습할 문제 리스트
                │
                ▼
        PRACTICE Flow로 연결
```

#### HINT Flow (문제 풀이 중)

```
[힌트 요청]
      │
      ▼
┌─────────────────────────────────┐
│   Hint Agent (Gemini Flash)     │
│                                 │
│  Input: 문제 정보, 유형, 레벨    │
│  + Docs RAG (MDN, React Docs)   │
│                                 │
│  Output: Level 1/2/3 힌트       │
└───────────────┬─────────────────┘
                │
                ▼
┌─────────────────────────────────┐
│     DB Save                     │
│                                 │
│  hint_logs, XP 차감 (-10)       │
└─────────────────────────────────┘
```

### 2.6 컴포넌트 요약

| 컴포넌트 | 역할 | 모델/기술 |
| --- | --- | --- |
| **Orchestrator** | 의도 파악 → 라우팅 | GPT-4o-mini |
| **Practice Chatbot** | 문제 조건 수집 | GPT-4o-mini |
| **Path Chatbot** | 커리큘럼 조건 수집 | GPT-4o-mini |
| **Tutor Chatbot** | 분석 조건 수집 | GPT-4o-mini |
| **RAG Search** | 코드/문제 검색 | pgvector + Re-ranker |
| **Code Gen** | 코드 생성 | Claude Sonnet |
| **Problem Gen (4종)** | 문제 생성 | GPT-4o-mini |
| **Hint Agent** | 힌트 + Docs RAG | Gemini Flash |
| **Answer Checker** | 정답 체크 | 규칙 기반 + Test |
| **Code Review** | Refactor 채점 | Claude Sonnet |
| **AI Tutor Agent** | 약점 분석 + 코칭 | Qwen 2.5 72B |
| **Learning Path Agent** | 커리큘럼 생성 | DeepSeek V3 |
| **Practice Agent** | 복습 스케줄 | GPT-4o-mini |

---

## 3. Database Schema

### 3.1 테이블 개요

| 카테고리 | 테이블 | 설명 |
| --- | --- | --- |
| **User** | users, user_stats, user_preferences | 사용자 정보 |
| **Problem** | codes, problems | 코드 및 문제 |
| **Practice** | attempts, attempt_details, hint_logs | 풀이 기록 |
| **Gamification** | daily_activity, badges, user_badges | 게이미피케이션 |
| **Farm** | farm_items, user_farm, user_inventory | 농장 미니게임 |
| **Learning** | user_weaknesses, review_schedule, learning_goals, learning_path, tutor_sessions | 학습 관련 |
| **Subscription** | plans, subscriptions, payments | 결제 |

### 3.2 ERD 개요

```
users ─────┬───── user_stats
           ├───── user_preferences
           ├───── attempts ─────── attempt_details
           ├───── hint_logs
           ├───── daily_activity
           ├───── user_badges ───── badges
           ├───── user_farm ─────── farm_items
           ├───── user_inventory
           ├───── user_weaknesses
           ├───── review_schedule
           ├───── learning_goals ── learning_path
           ├───── tutor_sessions
           └───── subscriptions ─── plans

codes ─────────── problems
```

### 3.3 SQL Schema

```sql
-- =====================================================
-- 1. USER 관련 테이블
-- =====================================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    name VARCHAR(100),
    avatar_url TEXT,
    provider VARCHAR(20) DEFAULT 'email',
    provider_id VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE TABLE user_stats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    total_xp INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,
    problems_solved INTEGER DEFAULT 0,
    problems_attempted INTEGER DEFAULT 0,
    blank_solved INTEGER DEFAULT 0,
    bug_solved INTEGER DEFAULT 0,
    output_solved INTEGER DEFAULT 0,
    refactor_solved INTEGER DEFAULT 0,
    current_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    last_activity_date DATE,
    seeds INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE user_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    preferred_language VARCHAR(20) DEFAULT 'javascript',
    preferred_difficulty VARCHAR(10) DEFAULT 'medium',
    daily_goal INTEGER DEFAULT 5,
    email_notifications BOOLEAN DEFAULT TRUE,
    push_notifications BOOLEAN DEFAULT TRUE,
    review_reminders BOOLEAN DEFAULT TRUE,
    theme VARCHAR(10) DEFAULT 'light',
    editor_font_size INTEGER DEFAULT 14,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- 2. PROBLEM 관련 테이블
-- =====================================================

CREATE TABLE codes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    framework VARCHAR(50) NOT NULL,
    category VARCHAR(100),
    tags TEXT[],
    title VARCHAR(255) NOT NULL,
    description TEXT,
    code TEXT NOT NULL,
    difficulty VARCHAR(10) DEFAULT 'medium',
    source VARCHAR(50),
    source_url TEXT,
    embedding vector(1536),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX codes_embedding_idx ON codes 
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

CREATE TABLE problems (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code_id UUID REFERENCES codes(id) ON DELETE CASCADE,
    problem_type VARCHAR(20) NOT NULL,
    problem_code TEXT NOT NULL,
    answer_data JSONB NOT NULL,
    test_cases JSONB,
    hints JSONB,
    difficulty VARCHAR(10) DEFAULT 'medium',
    times_attempted INTEGER DEFAULT 0,
    times_solved INTEGER DEFAULT 0,
    avg_solve_time INTEGER,
    embedding vector(1536),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX problems_embedding_idx ON problems 
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX problems_type_idx ON problems(problem_type);
CREATE INDEX problems_difficulty_idx ON problems(difficulty);

-- =====================================================
-- 3. PRACTICE 관련 테이블
-- =====================================================

CREATE TABLE attempts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    problem_id UUID REFERENCES problems(id) ON DELETE CASCADE,
    is_correct BOOLEAN NOT NULL,
    score INTEGER,
    submitted_code TEXT,
    submitted_answer VARCHAR(10),
    started_at TIMESTAMPTZ,
    submitted_at TIMESTAMPTZ DEFAULT NOW(),
    time_spent INTEGER,
    hints_used INTEGER DEFAULT 0,
    xp_earned INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX attempts_user_idx ON attempts(user_id);
CREATE INDEX attempts_problem_idx ON attempts(problem_id);
CREATE INDEX attempts_date_idx ON attempts(created_at);

CREATE TABLE attempt_details (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    attempt_id UUID REFERENCES attempts(id) ON DELETE CASCADE,
    error_type VARCHAR(50),
    error_location INTEGER,
    error_description TEXT,
    test_results JSONB,
    review_feedback JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE hint_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    problem_id UUID REFERENCES problems(id) ON DELETE CASCADE,
    attempt_id UUID REFERENCES attempts(id) ON DELETE SET NULL,
    hint_level INTEGER NOT NULL,
    hint_content TEXT,
    xp_cost INTEGER DEFAULT 10,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX hint_logs_user_idx ON hint_logs(user_id);

-- =====================================================
-- 4. GAMIFICATION 관련 테이블
-- =====================================================

CREATE TABLE daily_activity (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    activity_date DATE NOT NULL,
    problems_solved INTEGER DEFAULT 0,
    xp_earned INTEGER DEFAULT 0,
    time_spent INTEGER DEFAULT 0,
    blank_count INTEGER DEFAULT 0,
    bug_count INTEGER DEFAULT 0,
    output_count INTEGER DEFAULT 0,
    refactor_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, activity_date)
);

CREATE INDEX daily_activity_user_date_idx ON daily_activity(user_id, activity_date);

CREATE TABLE badges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    icon_url TEXT,
    condition_type VARCHAR(50) NOT NULL,
    condition_value INTEGER,
    condition_data JSONB,
    rarity VARCHAR(20) DEFAULT 'common',
    xp_reward INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE user_badges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    badge_id UUID REFERENCES badges(id) ON DELETE CASCADE,
    earned_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, badge_id)
);

-- =====================================================
-- 5. FARM 관련 테이블
-- =====================================================

CREATE TABLE farm_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    item_type VARCHAR(20) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    image_url TEXT,
    seed_cost INTEGER DEFAULT 0,
    required_level INTEGER DEFAULT 1,
    required_items JSONB,
    grow_time INTEGER,
    harvest_xp INTEGER,
    harvest_seeds INTEGER,
    house_level INTEGER,
    effect_type VARCHAR(50),
    effect_value INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE user_farm (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    house_level INTEGER DEFAULT 1,
    equipped_costume UUID REFERENCES farm_items(id),
    equipped_tool UUID REFERENCES farm_items(id),
    equipped_pet UUID REFERENCES farm_items(id),
    farm_slots JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE user_inventory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    item_id UUID REFERENCES farm_items(id) ON DELETE CASCADE,
    quantity INTEGER DEFAULT 1,
    acquired_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, item_id)
);

-- =====================================================
-- 6. LEARNING 관련 테이블
-- =====================================================

CREATE TABLE user_weaknesses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    category VARCHAR(100) NOT NULL,
    score DECIMAL(5,2) DEFAULT 50.0,
    total_attempts INTEGER DEFAULT 0,
    correct_attempts INTEGER DEFAULT 0,
    trend VARCHAR(20) DEFAULT 'stable',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, category)
);

CREATE INDEX user_weaknesses_user_idx ON user_weaknesses(user_id);

CREATE TABLE review_schedule (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    problem_id UUID REFERENCES problems(id) ON DELETE CASCADE,
    easiness_factor DECIMAL(3,2) DEFAULT 2.5,
    interval INTEGER DEFAULT 1,
    repetitions INTEGER DEFAULT 0,
    next_review_at TIMESTAMPTZ NOT NULL,
    last_reviewed_at TIMESTAMPTZ,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX review_schedule_user_next_idx ON review_schedule(user_id, next_review_at);

CREATE TABLE learning_goals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    goal_type VARCHAR(50) NOT NULL,
    target_company VARCHAR(100),
    target_period INTEGER,
    current_level VARCHAR(50),
    progress DECIMAL(5,2) DEFAULT 0.0,
    status VARCHAR(20) DEFAULT 'active',
    started_at TIMESTAMPTZ DEFAULT NOW(),
    target_date TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE learning_path (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    goal_id UUID REFERENCES learning_goals(id) ON DELETE CASCADE,
    week_number INTEGER NOT NULL,
    title VARCHAR(255),
    description TEXT,
    recommended_problems JSONB,
    problems_total INTEGER DEFAULT 0,
    problems_completed INTEGER DEFAULT 0,
    milestone_badge_id UUID REFERENCES badges(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE tutor_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    session_type VARCHAR(50) NOT NULL,
    analysis_data JSONB,
    recommended_problems JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX tutor_sessions_user_idx ON tutor_sessions(user_id);

-- =====================================================
-- 7. SUBSCRIPTION 관련 테이블
-- =====================================================

CREATE TABLE plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(50) NOT NULL,
    price_monthly INTEGER DEFAULT 0,
    price_yearly INTEGER DEFAULT 0,
    daily_problem_limit INTEGER,
    ai_tutor_access BOOLEAN DEFAULT FALSE,
    learning_path_access BOOLEAN DEFAULT FALSE,
    interview_prep_access BOOLEAN DEFAULT FALSE,
    features JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    plan_id UUID REFERENCES plans(id),
    started_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    status VARCHAR(20) DEFAULT 'active',
    billing_cycle VARCHAR(20),
    next_billing_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    subscription_id UUID REFERENCES subscriptions(id),
    amount INTEGER NOT NULL,
    currency VARCHAR(3) DEFAULT 'KRW',
    pg_provider VARCHAR(50),
    pg_transaction_id VARCHAR(255),
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- 8. 초기 데이터
-- =====================================================

INSERT INTO plans (code, name, price_monthly, price_yearly, daily_problem_limit, ai_tutor_access, learning_path_access) VALUES
('free', 'Free', 0, 0, 5, FALSE, FALSE),
('pro', 'Pro', 9900, 99000, NULL, TRUE, TRUE),
('max', 'Max', 19900, 199000, NULL, TRUE, TRUE);

INSERT INTO badges (code, name, description, condition_type, condition_value, rarity) VALUES
('first_problem', 'First Step', '첫 문제 풀이', 'problems', 1, 'common'),
('streak_7', 'Week Warrior', '7일 연속 출석', 'streak', 7, 'common'),
('streak_30', 'Monthly Master', '30일 연속 출석', 'streak', 30, 'rare'),
('streak_100', 'Legendary Learner', '100일 연속 출석', 'streak', 100, 'legendary'),
('problems_50', 'Half Century', '50문제 해결', 'problems', 50, 'common'),
('problems_100', 'Centurion', '100문제 해결', 'problems', 100, 'rare'),
('level_10', 'Rising Star', '레벨 10 달성', 'level', 10, 'common'),
('level_50', 'Expert', '레벨 50 달성', 'level', 50, 'epic');
```

---

## 4. API Specification

### 4.1 API 개요

| 항목 | 내용 |
| --- | --- |
| **Base URL** | `https://api.codefill.io/v1` |
| **인증** | Bearer Token (JWT) |
| **Content-Type** | `application/json` |
| **Rate Limit** | Free: 100/hour, Pro: 1000/hour, Max: Unlimited |

### 4.2 Auth API

```
POST   /auth/signup              회원가입
POST   /auth/login               로그인
POST   /auth/logout              로그아웃
POST   /auth/refresh             토큰 갱신
POST   /auth/oauth/{provider}    소셜 로그인 (google, github, kakao)
POST   /auth/password/reset      비밀번호 재설정 요청
PUT    /auth/password/reset      비밀번호 재설정 완료
```

### 4.3 User API

```
GET    /users/me                 내 정보 조회
PUT    /users/me                 내 정보 수정
GET    /users/me/stats           내 통계 조회
GET    /users/me/preferences     설정 조회
PUT    /users/me/preferences     설정 수정
GET    /users/me/badges          내 뱃지 목록
GET    /users/me/activity        활동 내역 (잔디)
```

### 4.4 Chat API

```
POST   /chat                     메시지 전송 (Orchestrator)
POST   /chat/practice            Practice Chatbot
POST   /chat/path                Path Chatbot
POST   /chat/tutor               Tutor Chatbot
```

### 4.5 Problem API

```
POST   /problems/generate        문제 생성 요청
GET    /problems/{id}            문제 조회
POST   /problems/{id}/submit     정답 제출
POST   /problems/{id}/run        코드 실행
POST   /problems/{id}/hint       힌트 요청
GET    /problems/search          문제 검색 (RAG)
GET    /problems/recommended     추천 문제
```

### 4.6 Learning API

```
POST   /tutor/analyze            약점 분석 요청
GET    /tutor/sessions           튜터 세션 목록
GET    /tutor/sessions/{id}      세션 상세
GET    /review/today             오늘의 복습 문제
POST   /review/{id}/complete     복습 완료 처리
GET    /review/schedule          복습 스케줄 조회
POST   /path/generate            커리큘럼 생성
GET    /path/current             현재 커리큘럼 조회
PUT    /path/{id}/progress       진행률 업데이트
```

### 4.7 Farm API

```
GET    /farm                     농장 상태 조회
POST   /farm/plant               심기
POST   /farm/harvest             수확
GET    /farm/inventory           인벤토리 조회
POST   /farm/equip               장착
GET    /farm/shop                상점 아이템 목록
POST   /farm/shop/buy            구매
```

### 4.8 Subscription API

```
GET    /subscription             현재 구독 조회
GET    /subscription/plans       요금제 목록
POST   /subscription/subscribe   구독 시작
POST   /subscription/cancel      구독 취소
GET    /subscription/payments    결제 내역
```

### 4.9 Error Response

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid email format",
    "details": {
      "field": "email",
      "constraint": "email"
    }
  }
}
```

| Code | HTTP Status | 설명 |
| --- | --- | --- |
| `VALIDATION_ERROR` | 400 | 요청 데이터 검증 실패 |
| `UNAUTHORIZED` | 401 | 인증 필요 |
| `FORBIDDEN` | 403 | 권한 없음 |
| `NOT_FOUND` | 404 | 리소스 없음 |
| `RATE_LIMITED` | 429 | 요청 제한 초과 |
| `INTERNAL_ERROR` | 500 | 서버 오류 |

---

## 5. Agent Implementation

### 5.1 Agent 개요

| Agent | 역할 | 모델 | 호출 빈도 |
| --- | --- | --- | --- |
| **Orchestrator** | 의도 파악 → 라우팅 | GPT-4o-mini | 매 대화 |
| **Practice Chatbot** | 문제 조건 수집 | GPT-4o-mini | PRACTICE 진입 시 |
| **Path Chatbot** | 커리큘럼 조건 수집 | GPT-4o-mini | PATH 진입 시 |
| **Tutor Chatbot** | 분석 조건 수집 | GPT-4o-mini | TUTOR 진입 시 |
| **Code Gen** | 코드 생성 | Claude Sonnet | RAG 미스 시 |
| **Blank Gen** | 빈칸 문제 생성 | GPT-4o-mini | 문제 생성 시 |
| **Bug Gen** | 버그 문제 생성 | GPT-4o-mini | 문제 생성 시 |
| **Output Gen** | 출력 문제 생성 | GPT-4o-mini | 문제 생성 시 |
| **Refactor Gen** | 리팩토링 문제 생성 | GPT-4o-mini | 문제 생성 시 |
| **Hint Agent** | 힌트 + Docs RAG | Gemini Flash | 힌트 요청 시 |
| **Code Review** | Refactor 채점 | Claude Sonnet | Refactor 제출 시 |
| **AI Tutor** | 약점 분석 + 코칭 | Qwen 2.5 72B | 분석 요청 시 |
| **Learning Path** | 커리큘럼 생성 | DeepSeek V3 | 1회성 |
| **Practice Agent** | 복습 스케줄 | GPT-4o-mini | 복습 요청 시 |

### 5.2 Orchestrator

**역할**: 사용자와 대화하며 의도만 파악. 세부 정보는 수집하지 않음.

```markdown
# Role
당신은 코딩 학습 플랫폼 CodeFill의 안내 AI입니다.
사용자와 자연스럽게 대화하며 의도를 파악하세요.

# Intent 분류
1. PRACTICE - 문제 풀이 원할 때
2. PATH - 커리큘럼/로드맵 원할 때
3. TUTOR - 약점 분석/코칭 원할 때
4. REVIEW - 복습 문제 원할 때
5. GENERAL - 일반 대화/질문

# 규칙
- 세부 정보(난이도, 유형 등)는 수집하지 마세요
- 의도가 불명확하면 자연스럽게 질문하세요
- 의도가 명확해지면 아래 형식으로 출력:

[READY_TO_ROUTE: {INTENT}]
```

### 5.3 Practice Chatbot

**역할**: PRACTICE 분기에서 문제 생성에 필요한 정보 수집.

```markdown
# Role
문제 생성에 필요한 정보를 수집하는 챗봇입니다.

# 수집 정보
1. framework (필수): react, vue, python, java, javascript 등
2. difficulty (필수): easy, medium, hard
3. topic (선택): 구체적인 주제
4. problem_type (필수): blank, bug, output, refactor

# 규칙
- 이미 알고 있는 정보는 다시 묻지 마세요
- 모든 필수 정보가 수집되면:

[READY_TO_GENERATE]
{ "framework": "...", "difficulty": "...", "topic": "...", "problem_type": "..." }
```

### 5.4 Path Chatbot

**역할**: 커리큘럼 생성에 필요한 정보 수집.

```markdown
# 수집 정보
1. goal (필수): coding_test, work_skills, framework
2. target_company (선택): kakao, naver, samsung, google 등
3. period (필수): 주 단위
4. current_level (필수): 현재 실력 수준

# 출력
[READY_TO_GENERATE]
{ "goal": "...", "target_company": "...", "period": ..., "current_level": "..." }
```

### 5.5 Tutor Chatbot

**역할**: 약점 분석/코칭에 필요한 정보 수집.

```markdown
# 수집 정보
1. scope (필수): full | specific
2. focus_area (scope=specific일 때): 집중 분석할 분야
3. analysis_type (필수): weakness | coaching

# 출력
[READY_TO_ANALYZE]
{ "scope": "...", "focus_area": "...", "analysis_type": "..." }
```

### 5.6 Problem Gen Agents

#### Blank Gen
- 코드에서 핵심 부분을 빈칸으로 변환
- Output: problem_code, blanks[], hints

#### Bug Gen
- 정상 코드에 현실적인 버그 삽입
- Output: problem_code, bug_info, correct_code, test_cases, hints

#### Output Gen
- 코드 실행 결과 예측 문제 생성
- Output: problem_code, options[], explanation, hints

#### Refactor Gen
- 스파게티 코드 생성
- Output: problem_code, model_answer, test_cases, evaluation_criteria, hints

### 5.7 Hint Agent

- 단계별 힌트 제공 (Level 1/2/3)
- Docs RAG (MDN, React Docs 등) 연동
- Output: hint, docs_reference

### 5.8 Code Review Agent

- Refactor 문제 채점
- 평가 항목: Functionality, Readability, DRY, Best Practices
- Output: score, breakdown, strengths, improvements

### 5.9 AI Tutor Agent

- 약점 분석 + 코칭 메시지 생성
- Output: analysis (top_weaknesses, trend), coaching (message, action_items, recommended_problems)

### 5.10 Learning Path Agent

- 개인 맞춤 커리큘럼 생성
- Output: summary, weeks[], final_goal

### 5.11 Practice Agent

- SM-2 알고리즘 기반 복습 스케줄 관리
- Output: today_reviews[], estimated_time, message

---

## 6. Infrastructure

### 6.1 아키텍처 개요

```
Client (Web/Mobile)
        │
        ▼
Vercel (Frontend) ─── Next.js, Edge Runtime, Vercel KV
        │
        ▼
GCP Cloud Run (Backend) ─── FastAPI, LangChain, Workers
        │
        ├──▶ Supabase (PostgreSQL + pgvector + Redis)
        ├──▶ OpenRouter (LLM)
        └──▶ External (Sandpack, Judge0, Resend, Sentry)
```

### 6.2 서비스별 상세

| 서비스 | 기술 | Region |
| --- | --- | --- |
| **Frontend** | Vercel Pro, Next.js 14+ | icn1 (서울) |
| **Backend** | GCP Cloud Run, FastAPI | asia-northeast3 (서울) |
| **Database** | Supabase Pro | ap-northeast-2 (서울) |
| **Cache** | Supabase Redis / Upstash | - |
| **LLM** | OpenRouter | - |
| **Code Execution** | Sandpack (JS), Judge0 (Python/Java) | - |

### 6.3 비용 추정 (월간, 1만 MAU)

| 서비스 | 예상 비용 |
| --- | --- |
| Vercel Pro | $20 |
| GCP Cloud Run | $50 |
| Supabase Pro | $25 |
| OpenRouter LLM | ~$40 |
| Judge0 (Self-hosted) | $30 |
| 기타 | $20 |
| **합계** | **~$185/월** |

### 6.4 환경 변수

```bash
# Frontend
NEXT_PUBLIC_API_URL=https://api.codefill.io
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=xxx

# Backend
DATABASE_URL=postgresql://...
SUPABASE_URL=https://xxx.supabase.co
REDIS_URL=redis://...
OPENROUTER_API_KEY=xxx
OPENAI_API_KEY=xxx
JUDGE0_URL=https://judge0.xxx.com
JWT_SECRET=xxx
SENTRY_DSN=xxx
```

---

## 7. Security & Performance

### 7.1 인증 & 인가

- JWT 기반 인증 (Access + Refresh Token)
- 역할 기반 접근 제어 (RBAC): Free, Pro, Max

### 7.2 Rate Limiting

| Plan | Limit |
| --- | --- |
| Free | 100/hour |
| Pro | 1000/hour |
| Max | 10000/hour |

### 7.3 입력 검증

- Pydantic 스키마 검증
- SQL Injection 방지 (파라미터화)
- XSS 방지 (DOMPurify)

### 7.4 코드 실행 보안

- Sandpack: 브라우저 샌드박스
- Judge0: 리소스 제한 (CPU 5s, Memory 128MB, Network 차단)

### 7.5 성능 최적화

- LLM 응답 캐싱
- 문제/사용자 통계 캐싱
- DB 인덱스 최적화
- 페이지네이션
- React Query 캐싱

### 7.6 SLA 목표

| 메트릭 | 목표 |
| --- | --- |
| API 응답 시간 (P95) | < 500ms |
| LLM 응답 시간 (P95) | < 5s |
| 에러율 | < 0.1% |
| 가용성 | 99.9% |

---

## 8. Migration Guide (v1 → v2)

### 8.1 마이그레이션 개요

| 항목 | v1 | v2 |
| --- | --- | --- |
| 문제 유형 | Blank 1개 | 4개 |
| Agent 구조 | 단일 LLM | 15+ Agents |
| 게이미피케이션 | 잔디/뱃지/레벨 | + 농장 미니게임 |
| 학습 기능 | ❌ | AI Tutor/Path/Review |
| 결제 | ❌ | Free/Pro/Max |

### 8.2 마이그레이션 단계

| Phase | 기간 | 주요 작업 |
| --- | --- | --- |
| **Phase 1** | Week 1 | DB 스키마 확장, 신규 테이블 |
| **Phase 2** | Week 2 | 데이터 마이그레이션 (blanks → problems) |
| **Phase 3** | Week 3-4 | API v2 배포 (v1 병행) |
| **Phase 4** | Week 5-6 | Frontend 롤아웃 (Feature Flag) |
| **Phase 5** | Week 7 | Cleanup (v1 종료) |

### 8.3 롤아웃 스케줄

| 주차 | 기능 | 롤아웃 % |
| --- | --- | --- |
| Week 1 | V2_PROBLEM_TYPES | 5% (Beta) |
| Week 2 | V2_PROBLEM_TYPES | 25% |
| Week 3 | V2_PROBLEM_TYPES | 100% |
| Week 3 | V2_CHAT_INTERFACE | 10% |
| Week 4 | V2_CHAT_INTERFACE | 50% |
| Week 5 | V2_CHAT_INTERFACE | 100% |
| Week 5 | V2_FARM_GAME | 100% |
| Week 6 | V2_AI_TUTOR | Pro 사용자 |
| Week 6 | V2_LEARNING_PATH | Pro 사용자 |

### 8.4 롤백 계획

- Feature Flags 즉시 비활성화
- v1 API 유지 (v2 병행 기간)
- 레거시 데이터 30일 보관

---

## 문서 이력

| 버전 | 날짜 | 작성자 | 변경 사항 |
| --- | --- | --- | --- |
| v2.0 | 2025-12-17 | - | 초안 작성 |
