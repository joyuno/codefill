# AWS 배포 태스크 가이드

> **프로젝트 스택**: Next.js 14 (프론트엔드) + FastAPI (백엔드) + Supabase (DB/Auth)

---

## Phase 1: 사전 준비

### 1.1 AWS 계정 및 CLI 설정
- [ ] AWS 계정 생성 (없는 경우)
- [ ] IAM 사용자 생성 및 적절한 권한 부여
- [ ] AWS CLI 설치 및 `aws configure` 설정
- [ ] 리전 선택 (예: `ap-northeast-2` 서울)

### 1.2 프로젝트 환경변수 정리
- [ ] `.env.example` 파일 생성 (프론트엔드/백엔드 각각)
- [ ] 프로덕션용 환경변수 목록 정리
  - Supabase URL, API Key
  - OpenAI/LLM API Key
  - 기타 시크릿 키들

### 1.3 Docker 설정 파일 생성
- [ ] `backend/Dockerfile` 생성
- [ ] `Dockerfile` (프론트엔드용) 생성
- [ ] `docker-compose.yml` 생성 (로컬 테스트용)
- [ ] `.dockerignore` 파일 생성

---

## Phase 2: 백엔드 배포 (FastAPI)

### 옵션 A: AWS ECS (Fargate) - 권장
> 컨테이너 기반, 서버리스, 자동 스케일링

#### 2.1 ECR (Elastic Container Registry) 설정
- [ ] ECR 리포지토리 생성 (`codefill-backend`)
- [ ] Docker 이미지 빌드 및 태깅
- [ ] ECR에 이미지 푸시

```bash
# ECR 로그인
aws ecr get-login-password --region ap-northeast-2 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.ap-northeast-2.amazonaws.com

# 이미지 빌드 및 푸시
docker build -t codefill-backend ./backend
docker tag codefill-backend:latest <account-id>.dkr.ecr.ap-northeast-2.amazonaws.com/codefill-backend:latest
docker push <account-id>.dkr.ecr.ap-northeast-2.amazonaws.com/codefill-backend:latest
```

#### 2.2 ECS 클러스터 설정
- [ ] ECS 클러스터 생성 (Fargate 유형)
- [ ] Task Definition 생성
  - CPU/메모리 설정 (최소 0.5vCPU, 1GB 권장)
  - 컨테이너 포트 매핑 (8000)
  - 환경변수 설정 (AWS Secrets Manager 연동)
- [ ] 서비스 생성 및 원하는 태스크 수 설정

#### 2.3 로드 밸런서 설정
- [ ] Application Load Balancer (ALB) 생성
- [ ] Target Group 설정 (HTTP:8000)
- [ ] Health Check 경로 설정 (`/health` 또는 `/docs`)
- [ ] HTTPS 리스너 추가 (ACM 인증서 필요)

#### 2.4 네트워크 설정
- [ ] VPC 설정 (기본 VPC 또는 신규 생성)
- [ ] 보안 그룹 설정
  - 인바운드: 80, 443 (ALB)
  - 아웃바운드: All traffic
- [ ] 퍼블릭/프라이빗 서브넷 구성

---

### 옵션 B: AWS EC2 - 간단한 방법
> 전통적인 VM 방식, 직접 관리 필요

#### 2.1 EC2 인스턴스 생성
- [ ] AMI 선택 (Amazon Linux 2023 또는 Ubuntu 22.04)
- [ ] 인스턴스 타입 선택 (t3.small 이상 권장)
- [ ] 키 페어 생성/선택
- [ ] 보안 그룹 설정 (22, 80, 443, 8000)
- [ ] Elastic IP 할당

#### 2.2 서버 환경 구성
- [ ] SSH 접속 후 필수 패키지 설치
```bash
sudo yum update -y  # Amazon Linux
sudo yum install -y docker git
sudo systemctl start docker
sudo systemctl enable docker
```

- [ ] Docker Compose 설치
- [ ] 애플리케이션 배포 및 실행

#### 2.3 Nginx 리버스 프록시 설정
- [ ] Nginx 설치 및 설정
- [ ] SSL 인증서 설정 (Let's Encrypt / Certbot)

---

## Phase 3: 프론트엔드 배포 (Next.js)

### 옵션 A: AWS Amplify - 권장
> 가장 간단, CI/CD 자동 설정

#### 3.1 Amplify 앱 생성
- [ ] AWS Amplify Console 접속
- [ ] GitHub 리포지토리 연결
- [ ] 빌드 설정 구성

```yaml
# amplify.yml
version: 1
frontend:
  phases:
    preBuild:
      commands:
        - npm ci
    build:
      commands:
        - npm run build
  artifacts:
    baseDirectory: .next
    files:
      - '**/*'
  cache:
    paths:
      - node_modules/**/*
```

#### 3.2 환경변수 설정
- [ ] Amplify Console에서 환경변수 추가
  - `NEXT_PUBLIC_SUPABASE_URL`
  - `NEXT_PUBLIC_SUPABASE_ANON_KEY`
  - `NEXT_PUBLIC_API_URL` (백엔드 URL)

#### 3.3 커스텀 도메인 설정
- [ ] Route 53에서 도메인 등록 (또는 외부 도메인 연결)
- [ ] Amplify에서 커스텀 도메인 추가
- [ ] SSL 인증서 자동 발급 확인

---

### 옵션 B: S3 + CloudFront (정적 내보내기)
> SSR 미사용 시, 가장 저렴

#### 3.1 S3 버킷 설정
- [ ] S3 버킷 생성 (`codefill-frontend`)
- [ ] 정적 웹사이트 호스팅 활성화
- [ ] 버킷 정책 설정 (공개 읽기)

#### 3.2 CloudFront 배포
- [ ] CloudFront 배포 생성
- [ ] S3 버킷을 오리진으로 설정
- [ ] SSL 인증서 연결 (ACM)
- [ ] 캐시 정책 설정

#### 3.3 빌드 및 배포
```bash
npm run build
aws s3 sync out/ s3://codefill-frontend --delete
aws cloudfront create-invalidation --distribution-id <ID> --paths "/*"
```

---

### 옵션 C: ECS (Fargate) - SSR 필요 시
> 백엔드와 동일한 방식으로 컨테이너 배포

- [ ] Next.js용 Dockerfile 생성
- [ ] ECR에 이미지 푸시
- [ ] ECS 서비스 생성 (포트 3000)
- [ ] ALB 연결

---

## Phase 4: 도메인 및 SSL 설정

### 4.1 Route 53 설정
- [ ] 호스팅 영역 생성
- [ ] 네임서버 설정 (도메인 등록기관에서)
- [ ] A/CNAME 레코드 추가
  - `api.yourdomain.com` → 백엔드 ALB
  - `yourdomain.com` → 프론트엔드

### 4.2 ACM (AWS Certificate Manager)
- [ ] SSL 인증서 요청 (도메인 검증)
- [ ] 프론트엔드용 인증서 (us-east-1 리전 - CloudFront용)
- [ ] 백엔드용 인증서 (서비스 리전)

---

## Phase 5: CI/CD 파이프라인 구축

### 5.1 GitHub Actions 설정
- [ ] `.github/workflows/deploy-backend.yml` 생성
- [ ] `.github/workflows/deploy-frontend.yml` 생성
- [ ] GitHub Secrets 설정
  - `AWS_ACCESS_KEY_ID`
  - `AWS_SECRET_ACCESS_KEY`
  - 기타 환경변수

### 5.2 백엔드 CI/CD 예시
```yaml
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

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ap-northeast-2

      - name: Login to ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v2

      - name: Build and push image
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          IMAGE_TAG: ${{ github.sha }}
        run: |
          docker build -t $ECR_REGISTRY/codefill-backend:$IMAGE_TAG ./backend
          docker push $ECR_REGISTRY/codefill-backend:$IMAGE_TAG

      - name: Update ECS service
        run: |
          aws ecs update-service --cluster codefill --service backend --force-new-deployment
```

---

## Phase 6: 모니터링 및 로깅

### 6.1 CloudWatch 설정
- [ ] 로그 그룹 생성 (`/ecs/codefill-backend`)
- [ ] 메트릭 알람 설정
  - CPU 사용률 > 80%
  - 메모리 사용률 > 80%
  - HTTP 5xx 에러 증가
- [ ] 대시보드 생성

### 6.2 X-Ray (선택사항)
- [ ] 분산 트레이싱 설정
- [ ] FastAPI에 X-Ray SDK 통합

---

## Phase 7: 보안 강화

### 7.1 AWS Secrets Manager
- [ ] 시크릿 생성 (API 키, DB 비밀번호 등)
- [ ] ECS Task Definition에서 시크릿 참조 설정

### 7.2 IAM 권한 최소화
- [ ] ECS Task Execution Role 검토
- [ ] 필요한 권한만 부여

### 7.3 WAF (Web Application Firewall)
- [ ] WAF 규칙 생성
- [ ] ALB에 WAF 연결
- [ ] Rate limiting 설정

---

## Phase 8: 비용 최적화

### 8.1 예상 비용 검토
| 서비스 | 예상 월 비용 |
|--------|-------------|
| ECS Fargate (백엔드) | ~$30-50 |
| ALB | ~$20 |
| Amplify (프론트엔드) | ~$0-15 |
| Route 53 | ~$1 |
| CloudWatch | ~$5 |
| **합계** | **~$56-91** |

### 8.2 비용 절감 팁
- [ ] Fargate Spot 사용 고려 (최대 70% 절감)
- [ ] 개발/스테이징 환경은 최소 사양으로
- [ ] 불필요한 리소스 정리 자동화
- [ ] Reserved Capacity 검토 (장기 운영 시)

---

## 체크리스트 요약

```
Phase 1: 사전 준비 ────────────────── □
Phase 2: 백엔드 배포 (ECS/EC2) ────── □
Phase 3: 프론트엔드 배포 (Amplify) ── □
Phase 4: 도메인 및 SSL ────────────── □
Phase 5: CI/CD 파이프라인 ─────────── □
Phase 6: 모니터링 ─────────────────── □
Phase 7: 보안 강화 ────────────────── □
Phase 8: 비용 최적화 ──────────────── □
```

---

## 참고 자료

- [AWS ECS 공식 문서](https://docs.aws.amazon.com/ecs/)
- [AWS Amplify 공식 문서](https://docs.amplify.aws/)
- [Next.js on AWS](https://nextjs.org/docs/deployment)
- [FastAPI 배포 가이드](https://fastapi.tiangolo.com/deployment/)
