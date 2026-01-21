# ========================================
# CodeFill Frontend - Next.js Dockerfile
# ========================================

# Stage 1: 의존성 설치
FROM node:20-alpine AS deps
WORKDIR /app

# 의존성 파일 복사
COPY package.json package-lock.json* bun.lockb* ./

# npm 또는 bun으로 의존성 설치
RUN if [ -f bun.lockb ]; then \
        npm install -g bun && bun install --frozen-lockfile; \
    elif [ -f package-lock.json ]; then \
        npm ci; \
    else \
        npm install; \
    fi

# Stage 2: 빌드
FROM node:20-alpine AS builder
WORKDIR /app

# 의존성 복사
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# 환경변수 설정 (빌드 시 필요)
ARG NEXT_PUBLIC_SUPABASE_URL
ARG NEXT_PUBLIC_SUPABASE_ANON_KEY
ARG NEXT_PUBLIC_API_URL

ENV NEXT_PUBLIC_SUPABASE_URL=$NEXT_PUBLIC_SUPABASE_URL
ENV NEXT_PUBLIC_SUPABASE_ANON_KEY=$NEXT_PUBLIC_SUPABASE_ANON_KEY
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

# Prisma 클라이언트 생성 (필요한 경우)
RUN if [ -f "prisma/schema.prisma" ]; then npx prisma generate; fi

# Next.js 빌드
RUN npm run build

# Stage 3: 프로덕션 실행
FROM node:20-alpine AS runner
WORKDIR /app

# 보안: non-root 사용자로 실행
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# 빌드 결과물 복사
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# Next.js 서버 실행
CMD ["node", "server.js"]
