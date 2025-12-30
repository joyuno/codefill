# 배치 솔루션 생성 시스템 설정

import os

# 경로 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data", "baekjoon")
BATCH_DIR = os.path.join(BASE_DIR, "scripts", "batch_solution_system", "batches")
LOCK_DIR = os.path.join(BASE_DIR, "scripts", "batch_solution_system", "locks")
CHECKPOINT_FILE = os.path.join(BASE_DIR, "scripts", "batch_solution_system", "checkpoint.json")

# 메인 데이터 파일
MAIN_FILE = os.path.join(DATA_DIR, "problems_with_github_solutions.json")

# 배치 설정
BATCH_SIZE = 10  # 한 번에 처리할 문제 수
MAX_RETRIES = 3  # 솔루션 생성 실패 시 재시도 횟수

# 디렉토리 생성
os.makedirs(BATCH_DIR, exist_ok=True)
os.makedirs(LOCK_DIR, exist_ok=True)
