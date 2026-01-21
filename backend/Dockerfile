# ========================================
# CodeFill Backend - FastAPI Dockerfile
# ========================================

# Python 3.11 slim 이미지 사용 (가볍고 빠름)
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 의존성 설치 (PostgreSQL 클라이언트 등)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# pip 업그레이드
RUN pip install --upgrade pip

# 의존성 파일 복사 및 설치 (캐싱 활용)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 포트 노출
EXPOSE 8000

# 헬스체크 (컨테이너 상태 확인용)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health')" || exit 1

# 서버 실행
# --host 0.0.0.0: 모든 IP에서 접근 가능
# --workers 4: 동시 처리를 위한 워커 수 (CPU 코어 수에 맞게 조정)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
