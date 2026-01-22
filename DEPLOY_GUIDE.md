# 🚀 CodeFill AWS 배포 가이드

이 가이드는 Docker와 CI/CD를 처음 접하는 분도 쉽게 따라할 수 있도록 작성되었습니다.

---

## 📚 목차

1. [개념 이해하기](#1-개념-이해하기)
2. [사전 준비](#2-사전-준비)
3. [AWS 설정](#3-aws-설정)
4. [GitHub 설정](#4-github-설정)
5. [로컬에서 Docker 테스트](#5-로컬에서-docker-테스트)
6. [배포하기](#6-배포하기)
7. [문제 해결](#7-문제-해결)

---

## 1. 개념 이해하기

### Docker란?
- **비유**: 이사할 때 모든 짐을 컨테이너 박스에 담는 것과 같습니다.
- 앱 실행에 필요한 모든 것(코드, 라이브러리, 설정)을 하나의 "박스"에 담습니다.
- 어떤 컴퓨터에서든 이 박스를 열면 똑같이 동작합니다.

```
[내 컴퓨터] ─── Docker 이미지 ───> [AWS 서버]
    ↓                                  ↓
  똑같이 동작!               똑같이 동작!
```

### CI/CD란?
- **CI (Continuous Integration)**: 코드 푸시하면 자동으로 테스트
- **CD (Continuous Deployment)**: 테스트 통과하면 자동으로 배포

```
[코드 수정] → [GitHub Push] → [자동 테스트] → [자동 빌드] → [자동 배포]
                                    ↑
                            GitHub Actions가 처리
```

---

## 2. 사전 준비

### 필요한 계정
- [x] AWS 계정 (이미 있음)
- [ ] GitHub 계정
- [ ] Docker Hub 계정 (선택사항)

### 로컬 설치 (개발/테스트용)
```bash
# Windows: Docker Desktop 설치
# https://www.docker.com/products/docker-desktop/ 에서 다운로드

# 설치 확인
docker --version
docker compose version  # 최신 버전은 'docker compose' (하이픈 없음)
```

---

## 3. AWS 설정

### 3.1 IAM 사용자 생성

> IAM = AWS 리소스에 접근할 수 있는 "계정"을 관리하는 서비스

1. AWS 콘솔 → IAM → 사용자 → 사용자 추가
2. 사용자 이름: `codefill-deploy`
3. 권한 정책 연결:
   - `AmazonEC2FullAccess`
   - `AmazonEC2ContainerRegistryFullAccess`

4. **Access Key 생성** (GitHub Actions에서 사용)
   - 보안 자격 증명 탭 → 액세스 키 만들기
   - `AWS_ACCESS_KEY_ID`와 `AWS_SECRET_ACCESS_KEY` 저장

### 3.2 ECR (컨테이너 저장소) 생성

> ECR = Docker 이미지를 저장하는 AWS의 창고

```bash
# AWS CLI로 생성 (또는 콘솔에서)
aws ecr create-repository --repository-name codefill-backend --region ap-northeast-2
aws ecr create-repository --repository-name codefill-frontend --region ap-northeast-2
```

또는 AWS 콘솔:
1. ECR → 리포지토리 → 리포지토리 생성
2. 이름: `codefill-backend`, `codefill-frontend`

### 3.3 EC2 인스턴스 생성

> EC2 = AWS의 가상 컴퓨터

1. **인스턴스 시작**
   - AMI: `Amazon Linux 2023` 또는 `Ubuntu 22.04`
   - 인스턴스 유형: `t3.medium` (최소 권장)
   - 스토리지: 30GB 이상

2. **보안 그룹 설정**
   ```
   인바운드 규칙:
   - SSH (22): 내 IP만
   - HTTP (80): 0.0.0.0/0
   - HTTPS (443): 0.0.0.0/0
   - Custom TCP (3000): 0.0.0.0/0  ← Frontend
   - Custom TCP (8000): 0.0.0.0/0  ← Backend
   ```

3. **키 페어 생성**
   - 새 키 페어 생성 → `codefill-key.pem` 다운로드
   - **이 파일은 절대 잃어버리면 안 됩니다!**

4. **EC2에 Docker 설치**
   ```bash
   # EC2에 SSH 접속
   ssh -i codefill-key.pem ec2-user@<EC2_PUBLIC_IP>

   # Docker 설치 (Amazon Linux 2023)
   sudo dnf update -y
   sudo dnf install -y docker

   # Docker Compose 플러그인 설치 (최신 방식)
   sudo mkdir -p /usr/local/lib/docker/cli-plugins
   sudo curl -SL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64 \
     -o /usr/local/lib/docker/cli-plugins/docker-compose
   sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose

   # Docker 서비스 시작
   sudo systemctl start docker
   sudo systemctl enable docker
   sudo usermod -aG docker ec2-user

   # 재접속 (그룹 적용)
   exit
   ssh -i codefill-key.pem ec2-user@<EC2_PUBLIC_IP>

   # 확인
   docker --version
   docker compose version
   ```

### 3.4 EC2에 AWS 자격 증명 설정
```bash
# EC2 내에서
aws configure
# AWS Access Key ID: [IAM에서 생성한 키]
# AWS Secret Access Key: [IAM에서 생성한 시크릿]
# Default region name: ap-northeast-2
# Default output format: json
```

---

## 4. GitHub 설정

### 4.1 저장소 생성 및 코드 푸시

```bash
# 프로젝트 폴더에서
cd C:\workspace\fastcampus\finalproject

# Git 초기화 (이미 되어있으면 스킵)
git init

# GitHub 저장소 연결
git remote add origin https://github.com/<YOUR_USERNAME>/codefill.git

# 코드 푸시
git add .
git commit -m "Initial commit with Docker and CI/CD setup"
git push -u origin main
```

### 4.2 GitHub Secrets 설정

> Secrets = 비밀번호, API 키 등을 안전하게 저장하는 곳

GitHub 저장소 → Settings → Secrets and variables → Actions → New repository secret

**필수 Secrets:**

| Secret 이름 | 설명 | 예시 |
|------------|------|------|
| `AWS_ACCESS_KEY_ID` | IAM Access Key | AKIA... |
| `AWS_SECRET_ACCESS_KEY` | IAM Secret Key | wJal... |
| `EC2_HOST` | EC2 퍼블릭 IP | 13.125.xxx.xxx |
| `EC2_USER` | EC2 사용자명 | ec2-user 또는 ubuntu |
| `EC2_SSH_KEY` | EC2 SSH 프라이빗 키 | -----BEGIN RSA... |
| `NEXT_PUBLIC_SUPABASE_URL` | Supabase URL | https://xxx.supabase.co |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Supabase Anon Key | eyJhbG... |
| `NEXT_PUBLIC_API_URL` | Backend API URL | http://13.125.xxx.xxx:8000 |
| `SUPABASE_URL` | Supabase URL (백엔드용) | https://xxx.supabase.co |
| `SUPABASE_ANON_KEY` | Supabase Anon Key | eyJhbG... |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase Service Role Key | eyJhbG... |
| `SUPABASE_DB_URL` | Supabase DB 연결 문자열 | postgresql://... |
| `JWT_SECRET` | JWT 서명 키 | 랜덤 문자열 |
| `OPENROUTER_API_KEY` | OpenRouter API 키 | sk-or-... |
| `OPENAI_API_KEY` | OpenAI API 키 | sk-... |
| `JUDGE0_URL` | Judge0 API URL | https://judge0... |
| `JUDGE0_API_KEY` | Judge0 API 키 | xxx |
| `JUDGE0_API_HOST` | Judge0 Host | judge0-ce... |

**EC2_SSH_KEY 등록 방법:**
```bash
# 로컬에서 키 내용 복사
cat codefill-key.pem
# 출력된 전체 내용을 GitHub Secret에 붙여넣기
# (-----BEGIN RSA PRIVATE KEY----- 부터 -----END RSA PRIVATE KEY----- 까지)
```

---

## 5. 로컬에서 Docker 테스트

배포 전에 로컬에서 먼저 테스트해보세요.

### 5.1 환경변수 파일 생성
```bash
cd codefill

# .env 파일 복사 (이미 있으면 스킵)
cp .env.example .env

# .env 파일 편집하여 실제 값 입력
```

### 5.2 Docker Compose로 실행
```bash
# 이미지 빌드 및 실행 (최신 문법: docker compose)
docker compose up --build

# 백그라운드 실행
docker compose up -d --build

# 로그 확인
docker compose logs -f

# 종료
docker compose down
```

> **참고**: 최신 Docker에서는 `docker-compose` 대신 `docker compose` (하이픈 없음) 사용을 권장합니다. 둘 다 동작하지만 새 프로젝트에서는 `docker compose`를 사용하세요.

### 5.3 접속 확인
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API 문서: http://localhost:8000/docs

---

## 6. 배포하기

### 자동 배포 (추천)
GitHub에 코드를 푸시하면 자동으로 배포됩니다.

```bash
git add .
git commit -m "새 기능 추가"
git push origin main
```

배포 진행 상황: GitHub → Actions 탭에서 확인

### 수동 배포
1. GitHub → Actions → "CD - AWS 배포"
2. "Run workflow" 클릭

### 배포 확인
```
Frontend: http://<EC2_PUBLIC_IP>:3000
Backend:  http://<EC2_PUBLIC_IP>:8000
API Docs: http://<EC2_PUBLIC_IP>:8000/docs
```

---

## 7. 문제 해결

### Docker 빌드 실패
```bash
# 캐시 삭제 후 재빌드
docker compose build --no-cache
```

### EC2 접속 안 됨
```bash
# 보안 그룹 확인 (22번 포트 열려있는지)
# 키 파일 권한 확인
chmod 400 codefill-key.pem
```

### 컨테이너 로그 확인 (EC2에서)
```bash
# 실행 중인 컨테이너 확인
docker ps

# 로그 확인
docker logs codefill-backend
docker logs codefill-frontend

# 컨테이너 내부 접속
docker exec -it codefill-backend /bin/bash
```

### 환경변수 문제
```bash
# EC2에서 환경변수 확인
docker exec codefill-backend env | grep SUPABASE
```

### 디스크 공간 부족
```bash
# EC2에서 Docker 정리
docker system prune -a
```

---

## 📁 생성된 파일 구조

```
codefill/
├── .github/
│   └── workflows/
│       ├── ci.yml          # CI: 테스트 & 빌드 검증
│       └── deploy.yml      # CD: AWS 배포
├── backend/
│   ├── Dockerfile          # 백엔드 Docker 설정
│   └── .dockerignore       # Docker 빌드 제외 파일
├── Dockerfile              # 프론트엔드 Docker 설정
├── docker-compose.yml      # 로컬 개발용 Docker Compose
├── .dockerignore           # Docker 빌드 제외 파일
└── DEPLOY_GUIDE.md         # 이 가이드
```

---

## 🎯 다음 단계 (선택사항)

### 도메인 연결
1. Route 53에서 도메인 구매/이전
2. A 레코드 → EC2 IP 연결
3. ACM에서 SSL 인증서 발급
4. CloudFront CDN 설정

### 로드 밸런서 추가
- 트래픽 분산 및 HTTPS 처리
- ALB (Application Load Balancer) 사용

### 모니터링 설정
- CloudWatch 대시보드
- 알람 설정 (CPU, 메모리, 에러)

---

## 💡 팁

1. **처음엔 수동 배포로 연습**: EC2에 직접 접속해서 docker 명령어 익히기
2. **로그를 자주 확인**: 문제 발생 시 가장 먼저 로그 확인
3. **환경변수 꼼꼼히**: 대부분의 에러는 환경변수 누락/오타
4. **작은 변경부터**: 큰 변경보다 작은 변경을 자주 배포

---

## 📖 참고 문서

이 가이드 작성에 참고한 공식 문서들입니다:

- [Docker 공식 문서 - Compose 파일](https://docs.docker.com/compose/compose-file/)
- [GitHub Actions 공식 문서 - AWS ECS 배포](https://docs.github.com/en/actions/how-tos/deploy/deploy-to-third-party-platforms/amazon-elastic-container-service)
- [Next.js 공식 문서 - Docker 배포](https://nextjs.org/docs/app/guides/self-hosting)
- [AWS ECR 인증 가이드](https://docs.aws.amazon.com/AmazonECR/latest/userguide/registry_auth.html)
- [Amazon Linux 2023에 Docker 설치](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-docker.html)

---

질문이 있으시면 언제든 물어보세요! 🙌
