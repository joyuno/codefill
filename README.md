# CodeFill

AI 기반 인터랙티브 코딩 학습 플랫폼

[![Deploy to AWS](https://github.com/joyuno/codefill/actions/workflows/deploy.yml/badge.svg)](https://github.com/joyuno/codefill/actions/workflows/deploy.yml)

## Overview

CodeFill은 AI 튜터와 함께 알고리즘 문제를 풀며 실력을 키울 수 있는 학습 플랫폼입니다. 단순한 문제 풀이가 아닌, AI와의 대화를 통해 개념을 이해하고 점진적으로 실력을 향상시킬 수 있습니다.

**Live Demo**: [https://codefill.co.kr](https://codefill.co.kr)

## Features

### 문제 유형
- **빈칸 채우기**: 핵심 로직을 직접 완성하며 알고리즘 이해
- **퍼즐 (코드 정렬)**: 섞인 코드 블록을 올바른 순서로 배치
- **1대1 대화형 튜터**: AI 튜터와 소크라틱 대화로 문제 해결

### AI 기능
- **RAG 기반 문제 검색**: 백준, 프로그래머스 문제 DB에서 조건에 맞는 문제 검색
- **맞춤형 힌트 시스템**: 막힌 부분에 대한 단계별 힌트 제공
- **코드 리뷰**: 작성한 코드에 대한 피드백
- **문제 자동 생성**: 원하는 주제/난이도에 맞는 새 문제 생성

### 티어 시스템
| 티어 | 난이도 |
|------|--------|
| 실버 | 기본 개념 연습 |
| 골드 | 응용 문제 |
| 플래티넘 | 도전적인 난이도 |
| 다이아 | 고난이도 문제 |
| 마스터 | 최고 난이도 |

## Tech Stack

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS, shadcn/ui
- **Animation**: Framer Motion
- **State**: React Context, Zustand

### Backend
- **Framework**: FastAPI (Python)
- **AI Orchestration**: LangGraph, LangChain
- **Database**: Supabase (PostgreSQL)
- **Vector DB**: Supabase pgvector (RAG)

### AI/LLM
- **OpenRouter**: GPT-4o-mini (기본 모델)
- **Google Gemini**: gemini-2.0-flash (3개 키 로테이션)

### Infrastructure
- **Cloud**: AWS (EC2, ECR)
- **CI/CD**: GitHub Actions
- **Container**: Docker

## Project Structure

```
codefill/
├── src/                    # Next.js Frontend
│   ├── app/               # App Router pages
│   ├── components/        # React components
│   │   ├── chat/         # 채팅 UI
│   │   ├── problem/      # 문제 풀이 UI
│   │   └── ui/           # shadcn/ui components
│   ├── hooks/            # Custom hooks
│   └── lib/              # Utilities, API clients
│
├── backend/               # FastAPI Backend
│   └── app/
│       ├── routers/      # API endpoints
│       ├── services/     # Business logic
│       ├── graphs/       # LangGraph workflows
│       │   ├── collection/   # 정보 수집 그래프
│       │   └── discovery/    # 문제 탐색 그래프
│       ├── prompts/      # LLM prompts
│       └── tools/        # LangChain tools
│
└── .github/workflows/     # CI/CD
```

## Getting Started

### Prerequisites
- Node.js 18+
- Python 3.11+
- Docker (optional)

### Frontend Setup

```bash
# Install dependencies
npm install

# Set environment variables
cp .env.example .env.local
# Edit .env.local with your values

# Run development server
npm run dev
```

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your values

# Run development server
uvicorn app.main:app --reload --port 8000
```

### Environment Variables

#### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
```

#### Backend (.env)
```env
# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

# LLM
OPENROUTER_API_KEY=your_openrouter_key
GEMINI_API_KEYS=key1,key2,key3

# JWT
JWT_SECRET=your_jwt_secret
```

## Deployment

GitHub Actions를 통해 `deploy` 브랜치에 push하면 자동 배포됩니다.

```bash
# Deploy
git checkout deploy
git merge main
git push origin deploy
```

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Next.js   │────▶│   FastAPI   │────▶│  Supabase   │
│  Frontend   │     │   Backend   │     │  Database   │
└─────────────┘     └──────┬──────┘     └─────────────┘
                           │
                    ┌──────▼──────┐
                    │  LangGraph  │
                    │ Orchestrator│
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
        ┌─────▼─────┐ ┌────▼────┐ ┌─────▼─────┐
        │  OpenAI   │ │ Gemini  │ │  pgvector │
        │  (GPT-4o) │ │  Flash  │ │   (RAG)   │
        └───────────┘ └─────────┘ └───────────┘
```

## License

This project is private and proprietary.

## Contact

- Website: [codefill.co.kr](https://codefill.co.kr)
