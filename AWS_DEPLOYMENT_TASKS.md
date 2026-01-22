# AWS 배포 태스크 가이드

> **프로젝트 스택**: Next.js 14 (프론트엔드) + FastAPI (백엔드) + Supabase (DB/Auth)
>
> **배포 구조**: EC2 (프론트) + EC2 (백엔드) + CloudFront (CDN)
>
> **도메인**: `codefill.co.kr` (가비아)
> - 프론트엔드: `https://codefill.co.kr`
> - 백엔드 API: `https://api.codefill.co.kr`

---

## 아키텍처 개요

```
┌─────────────────────────────────────────────────────────────┐
│                         사용자                               │
│         codefill.co.kr    /    api.codefill.co.kr           │
└─────────────────────────┬───────────────────────────────────┘
                          │
          ┌───────────────┴───────────────┐
          │                               │
          ▼                               ▼
┌─────────────────────────┐    ┌───────────────────────────────┐
│    CloudFront (CDN)     │    │      EC2 #2 (Backend)         │
│  - codefill.co.kr       │    │   - api.codefill.co.kr        │
│  - HTTPS (ACM 인증서)    │    │   - FastAPI (Docker)          │
│  - 전세계 캐싱           │    │   - Nginx + Let's Encrypt     │
└────────────┬────────────┘    │   - t3.small (~$15/월)        │
             │                 └───────────────────────────────┘
             ▼
┌────────────────────────┐
│   EC2 #1 (Frontend)    │
│   - Next.js 서버        │
│   - PM2 프로세스 관리    │
│   - t3.small (~$15/월)  │
└────────────────────────┘
                                               ▼
                              ┌───────────────────────────────┐
                              │        Supabase               │
                              │   (이미 사용 중 - 무료 티어)   │
                              └───────────────────────────────┘
```

### 예상 월 비용: **$35-50**

| 서비스 | 비용 |
|--------|------|
| EC2 #1 (Frontend) t3.small | ~$15-20 |
| EC2 #2 (Backend) t3.small | ~$15-20 |
| CloudFront | ~$1-5 |
| Elastic IP x2 | 무료 (연결된 경우) |
| Supabase | 무료 |
| **합계** | **~$35-50** |

---

## Phase 1: 사전 준비

### 1.1 AWS 계정 및 CLI 설정
- [ ] AWS 계정 생성 (없는 경우)
- [ ] IAM 사용자 생성
  ```
  권한 정책 추가:
  - AmazonEC2FullAccess
  - CloudFrontFullAccess
  - AmazonRoute53FullAccess (선택)
  - AWSCertificateManagerFullAccess
  ```
- [ ] AWS CLI 설치
  ```bash
  # macOS
  brew install awscli

  # 또는 공식 설치
  curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
  sudo installer -pkg AWSCLIV2.pkg -target /
  ```
- [ ] AWS CLI 설정
  ```bash
  aws configure
  # AWS Access Key ID: [IAM에서 발급받은 키]
  # AWS Secret Access Key: [IAM에서 발급받은 시크릿]
  # Default region name: ap-northeast-2
  # Default output format: json
  ```

### 1.2 프로젝트 환경변수 정리

**프론트엔드 (.env.production)**
```env
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJxxx...
NEXT_PUBLIC_API_URL=https://api.codefill.co.kr
```

**백엔드 (.env)**
```env
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_KEY=eyJxxx...
OPENROUTER_API_KEY=sk-or-xxx...
CORS_ORIGINS=https://codefill.co.kr,https://www.codefill.co.kr
# 기타 API 키들
```

### 1.3 백엔드 Dockerfile 확인/생성

**backend/Dockerfile**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 시스템 의존성
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드
COPY . .

# 포트 노출
EXPOSE 8000

# 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Phase 2: 백엔드 배포 (EC2 #2)

### 2.1 EC2 인스턴스 생성

1. **AWS Console → EC2 → 인스턴스 시작**

2. **설정값**
   | 항목 | 값 |
   |------|-----|
   | 이름 | codefill-backend |
   | AMI | Ubuntu Server 22.04 LTS |
   | 인스턴스 유형 | t3.small (2vCPU, 2GB) |
   | 키 페어 | 새로 생성: `codefill-key` |
   | 스토리지 | 20GB gp3 |

3. **보안 그룹 설정** (새로 생성: `codefill-backend-sg`)
   | 유형 | 포트 | 소스 | 용도 |
   |------|------|------|------|
   | SSH | 22 | 내 IP | SSH 접속 |
   | HTTP | 80 | 0.0.0.0/0 | 웹 트래픽 |
   | HTTPS | 443 | 0.0.0.0/0 | SSL 트래픽 |

4. **Elastic IP 할당**
   - EC2 → 네트워크 및 보안 → 탄력적 IP
   - 새 주소 할당 → 인스턴스에 연결
   - **이 IP 기록**: `BACKEND_IP = ____________`

### 2.2 서버 초기 설정

```bash
# SSH 접속
ssh -i "codefill-key.pem" ubuntu@<BACKEND_IP>

# 시스템 업데이트
sudo apt update && sudo apt upgrade -y

# Docker 설치
sudo apt install -y docker.io docker-compose
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ubuntu

# 재접속 (docker 그룹 적용)
exit
ssh -i "codefill-key.pem" ubuntu@<BACKEND_IP>

# Docker 확인
docker --version
```

### 2.3 애플리케이션 배포

```bash
# 프로젝트 디렉토리 생성
mkdir -p ~/app
cd ~/app

# === 로컬 터미널에서 실행 ===
# 백엔드 파일 전송
scp -i "codefill-key.pem" -r ./backend ubuntu@<BACKEND_IP>:~/app/

# === EC2에서 실행 ===
cd ~/app/backend

# .env 파일 생성
nano .env
# 환경변수 붙여넣기 후 저장 (Ctrl+X, Y, Enter)

# Docker 이미지 빌드
docker build -t codefill-backend .

# 컨테이너 실행
docker run -d \
  --name backend \
  --restart always \
  -p 8000:8000 \
  --env-file .env \
  codefill-backend

# 확인
docker ps
curl http://localhost:8000/docs
```

### 2.4 Nginx 리버스 프록시 설정

```bash
# Nginx 설치
sudo apt install -y nginx

# Nginx 설정 파일 생성
sudo nano /etc/nginx/sites-available/codefill-backend
```

**Nginx 설정 내용:**
```nginx
server {
    listen 80;
    server_name api.codefill.co.kr;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;

        # WebSocket 지원
        proxy_read_timeout 86400;
    }
}
```

```bash
# 설정 활성화
sudo ln -s /etc/nginx/sites-available/codefill-backend /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Nginx 테스트 및 재시작
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx
```

### 2.5 SSL 인증서 설정 (Phase 4 DNS 설정 후)

> **주의**: 가비아 DNS 설정을 먼저 완료해야 SSL 발급 가능

```bash
# Certbot 설치
sudo apt install -y certbot python3-certbot-nginx

# SSL 인증서 발급 (DNS 설정 후 실행)
sudo certbot --nginx -d api.codefill.co.kr

# 자동 갱신 확인
sudo certbot renew --dry-run
```

---

## Phase 3: 프론트엔드 배포 (EC2 #1)

### 3.1 EC2 인스턴스 생성

1. **AWS Console → EC2 → 인스턴스 시작**

2. **설정값**
   | 항목 | 값 |
   |------|-----|
   | 이름 | codefill-frontend |
   | AMI | Ubuntu Server 22.04 LTS |
   | 인스턴스 유형 | t3.small (2vCPU, 2GB) |
   | 키 페어 | 기존 `codefill-key` 사용 |
   | 스토리지 | 20GB gp3 |

3. **보안 그룹 설정** (새로 생성: `codefill-frontend-sg`)
   | 유형 | 포트 | 소스 | 용도 |
   |------|------|------|------|
   | SSH | 22 | 내 IP | SSH 접속 |
   | HTTP | 80 | 0.0.0.0/0 | 웹 트래픽 |
   | HTTPS | 443 | 0.0.0.0/0 | SSL 트래픽 |
   | Custom TCP | 3000 | 0.0.0.0/0 | Next.js (테스트용) |

4. **Elastic IP 할당**
   - 새 주소 할당 → 인스턴스에 연결
   - **이 IP 기록**: `FRONTEND_IP = ____________`

### 3.2 서버 초기 설정

```bash
# SSH 접속
ssh -i "codefill-key.pem" ubuntu@<FRONTEND_IP>

# 시스템 업데이트
sudo apt update && sudo apt upgrade -y

# Node.js 20 LTS 설치
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# 버전 확인
node --version  # v20.x.x
npm --version

# PM2 설치 (프로세스 관리자)
sudo npm install -g pm2

# Nginx 설치
sudo apt install -y nginx
```

### 3.3 애플리케이션 배포

```bash
# === 로컬 터미널에서 실행 ===
# 프론트엔드 파일 전송 (node_modules 제외)
rsync -avz --exclude 'node_modules' --exclude '.next' --exclude '.git' \
  -e "ssh -i codefill-key.pem" \
  ./ ubuntu@<FRONTEND_IP>:~/app/frontend/

# === EC2에서 실행 ===
cd ~/app/frontend

# .env.production 파일 생성
nano .env.production
# 환경변수 붙여넣기 후 저장

# 의존성 설치
npm install

# 프로덕션 빌드
npm run build

# PM2로 실행
pm2 start npm --name "codefill-frontend" -- start

# PM2 상태 확인
pm2 status

# 시스템 재부팅 시 자동 시작 설정
pm2 startup
pm2 save

# 테스트
curl http://localhost:3000
```

### 3.4 Nginx 리버스 프록시 설정

```bash
# Nginx 설정 파일 생성
sudo nano /etc/nginx/sites-available/codefill-frontend
```

**Nginx 설정 내용:**
```nginx
server {
    listen 80;
    server_name codefill.co.kr www.codefill.co.kr;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

```bash
# 설정 활성화
sudo ln -s /etc/nginx/sites-available/codefill-frontend /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Nginx 테스트 및 재시작
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx
```

### 3.5 SSL 인증서 설정 (Phase 4 DNS 설정 후)

```bash
# Certbot 설치
sudo apt install -y certbot python3-certbot-nginx

# SSL 인증서 발급 (DNS 설정 후 실행)
sudo certbot --nginx -d codefill.co.kr -d www.codefill.co.kr

# 자동 갱신 확인
sudo certbot renew --dry-run
```

---

## Phase 4: 도메인 연결 (가비아 DNS)

> **도메인**: `codefill.co.kr` (가비아에서 구매)

### 4.1 가비아 DNS 설정

1. **가비아 로그인 → My가비아 → 도메인 관리**

2. **DNS 설정 → codefill.co.kr 선택**

3. **레코드 추가**

   | 타입 | 호스트 | 값 | TTL |
   |------|--------|-----|-----|
   | **A** | `@` (또는 빈값) | `<FRONTEND_IP>` | 3600 |
   | **A** | `www` | `<FRONTEND_IP>` | 3600 |
   | **A** | `api` | `<BACKEND_IP>` | 3600 |

   > **IP 주소 대입**:
   > - `<FRONTEND_IP>` → Phase 3에서 기록한 프론트엔드 Elastic IP
   > - `<BACKEND_IP>` → Phase 2에서 기록한 백엔드 Elastic IP

### 4.2 DNS 전파 확인 (10분~24시간 소요)

```bash
# 로컬에서 확인
nslookup codefill.co.kr
nslookup www.codefill.co.kr
nslookup api.codefill.co.kr

# 또는 dig 명령어
dig codefill.co.kr +short
dig api.codefill.co.kr +short
```

**온라인 도구로 확인:**
- https://www.whatsmydns.net/#A/codefill.co.kr
- https://dnschecker.org/

### 4.3 SSL 인증서 발급 (DNS 전파 후)

DNS가 전파되면 각 EC2에서 SSL 발급:

**백엔드 EC2에서:**
```bash
ssh -i "codefill-key.pem" ubuntu@<BACKEND_IP>
sudo certbot --nginx -d api.codefill.co.kr
```

**프론트엔드 EC2에서:**
```bash
ssh -i "codefill-key.pem" ubuntu@<FRONTEND_IP>
sudo certbot --nginx -d codefill.co.kr -d www.codefill.co.kr
```

### 4.4 (선택) CloudFront 추가 - 전세계 캐싱

프론트엔드에 CloudFront를 추가하면 전세계 사용자에게 빠른 응답 가능:

1. **ACM에서 인증서 발급** (us-east-1 리전에서!)
   - 도메인: `codefill.co.kr`, `*.codefill.co.kr`
   - DNS 검증

2. **CloudFront 배포 생성**
   - 원본: `<FRONTEND_IP>` (커스텀 원본)
   - HTTPS 리다이렉트
   - 대체 도메인: `codefill.co.kr`, `www.codefill.co.kr`
   - SSL 인증서: ACM에서 발급받은 것

3. **가비아 DNS 수정**
   - `codefill.co.kr` → CloudFront 도메인 (CNAME)
   - `www.codefill.co.kr` → CloudFront 도메인 (CNAME)

---

## Phase 5: 배포 스크립트 작성

### 5.1 프론트엔드 배포 스크립트

**deploy-frontend.sh**
```bash
#!/bin/bash
set -e

# 설정값 (실제 값으로 변경)
FRONTEND_IP="YOUR_FRONTEND_ELASTIC_IP"
KEY_PATH="~/.ssh/codefill-key.pem"

echo "📤 Uploading frontend files..."
rsync -avz --exclude 'node_modules' --exclude '.next' --exclude '.git' \
  -e "ssh -i $KEY_PATH" \
  ./ ubuntu@$FRONTEND_IP:~/app/frontend/

echo "🔄 Building and restarting..."
ssh -i $KEY_PATH ubuntu@$FRONTEND_IP << 'EOF'
cd ~/app/frontend
npm install
npm run build
pm2 restart codefill-frontend
EOF

echo "✅ Frontend deployed to https://codefill.co.kr"
```

### 5.2 백엔드 배포 스크립트

**deploy-backend.sh**
```bash
#!/bin/bash
set -e

# 설정값 (실제 값으로 변경)
BACKEND_IP="YOUR_BACKEND_ELASTIC_IP"
KEY_PATH="~/.ssh/codefill-key.pem"

echo "📤 Uploading backend files..."
rsync -avz -e "ssh -i $KEY_PATH" \
  --exclude 'venv' \
  --exclude '__pycache__' \
  --exclude '.env' \
  --exclude '.git' \
  ./backend/ ubuntu@$BACKEND_IP:~/app/backend/

echo "🔄 Rebuilding and restarting container..."
ssh -i $KEY_PATH ubuntu@$BACKEND_IP << 'EOF'
cd ~/app/backend
docker build -t codefill-backend .
docker stop backend || true
docker rm backend || true
docker run -d \
  --name backend \
  --restart always \
  -p 8000:8000 \
  --env-file .env \
  codefill-backend
EOF

echo "✅ Backend deployed to https://api.codefill.co.kr"
```

```bash
chmod +x deploy-frontend.sh deploy-backend.sh
```

---

## 체크리스트 요약

```
Phase 1: 사전 준비
  [ ] AWS CLI 설치 및 설정
  [ ] IAM 사용자 생성
  [ ] 환경변수 정리 (.env.production, .env)
  [ ] Dockerfile 확인

Phase 2: 백엔드 배포 (EC2 #2)
  [ ] EC2 인스턴스 생성 (codefill-backend)
  [ ] Elastic IP 할당 → BACKEND_IP 기록
  [ ] Docker 설치
  [ ] 백엔드 코드 업로드
  [ ] Docker 컨테이너 실행
  [ ] Nginx 설정

Phase 3: 프론트엔드 배포 (EC2 #1)
  [ ] EC2 인스턴스 생성 (codefill-frontend)
  [ ] Elastic IP 할당 → FRONTEND_IP 기록
  [ ] Node.js, PM2 설치
  [ ] 프론트엔드 코드 업로드
  [ ] npm install && npm run build
  [ ] PM2로 실행
  [ ] Nginx 설정

Phase 4: 도메인 연결
  [ ] 가비아 DNS 설정:
      - codefill.co.kr → FRONTEND_IP
      - www.codefill.co.kr → FRONTEND_IP
      - api.codefill.co.kr → BACKEND_IP
  [ ] DNS 전파 대기 (10분~24시간)
  [ ] 백엔드 SSL 발급 (certbot)
  [ ] 프론트엔드 SSL 발급 (certbot)

Phase 5: 배포 자동화
  [ ] deploy-frontend.sh 작성
  [ ] deploy-backend.sh 작성
```

---

## 자주 사용하는 명령어

### 프론트엔드 (EC2 #1)

```bash
# SSH 접속
ssh -i "codefill-key.pem" ubuntu@<FRONTEND_IP>

# PM2 관리
pm2 status                 # 상태 확인
pm2 logs codefill-frontend # 로그 확인
pm2 restart codefill-frontend  # 재시작

# 수동 재배포
cd ~/app/frontend
git pull  # 또는 rsync로 업로드
npm install
npm run build
pm2 restart codefill-frontend
```

### 백엔드 (EC2 #2)

```bash
# SSH 접속
ssh -i "codefill-key.pem" ubuntu@<BACKEND_IP>

# Docker 관리
docker ps                    # 실행 중인 컨테이너
docker logs -f backend       # 로그 확인
docker restart backend       # 재시작

# 수동 재배포
cd ~/app/backend
docker build -t codefill-backend .
docker stop backend && docker rm backend
docker run -d --name backend --restart always -p 8000:8000 --env-file .env codefill-backend
```

### Nginx & SSL

```bash
# Nginx 상태
sudo systemctl status nginx
sudo nginx -t
sudo systemctl reload nginx

# SSL 갱신
sudo certbot renew
```

---

## 접속 URL

| 서비스 | URL |
|--------|-----|
| 프론트엔드 | https://codefill.co.kr |
| 백엔드 API | https://api.codefill.co.kr |
| API 문서 | https://api.codefill.co.kr/docs |

---

## 문제 해결

### EC2 접속 안 됨
```bash
# 키 파일 권한 확인
chmod 400 codefill-key.pem

# 보안 그룹에서 22번 포트가 "내 IP"로 설정되어 있는지 확인
```

### Docker 컨테이너 안 뜸
```bash
docker logs backend  # 에러 확인
docker ps -a         # 종료된 컨테이너 확인
```

### PM2 앱이 안 뜸
```bash
pm2 logs codefill-frontend  # 에러 확인
pm2 delete codefill-frontend
pm2 start npm --name "codefill-frontend" -- start
```

### SSL 발급 실패
```bash
# DNS가 제대로 전파되었는지 확인
nslookup api.codefill.co.kr

# 80번 포트가 열려있는지 확인
sudo ufw status
sudo ufw allow 80
```

### 504 Gateway Timeout
```bash
# 백엔드가 실행 중인지 확인
curl http://localhost:8000/docs

# Nginx 설정 확인
sudo nginx -t
sudo systemctl restart nginx
```
