#!/usr/bin/env python3
"""
백준 이미지를 Supabase Storage에 업로드하고 DB의 question 컬럼 업데이트

사용법:
    python scripts/upload_images_to_supabase.py

필요 환경변수:
    SUPABASE_URL
    SUPABASE_SERVICE_ROLE_KEY
"""

import os
import re
import sys
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client
import mimetypes

# 버퍼링 없이 즉시 출력
sys.stdout.reconfigure(line_buffering=True)
print = lambda *args, **kwargs: __builtins__.print(*args, **kwargs, flush=True)

# .env 파일 로드
load_dotenv(Path(__file__).parent.parent / "backend" / ".env")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
BUCKET_NAME = "baekjoon-images"
IMAGES_DIR = Path(__file__).parent.parent / "data" / "baekjoon" / "images"

def get_supabase_client() -> Client:
    """Supabase 클라이언트 생성"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("SUPABASE_URL과 SUPABASE_SERVICE_ROLE_KEY 환경변수가 필요합니다")
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def create_bucket_if_not_exists(supabase: Client):
    """버킷이 없으면 생성"""
    try:
        # 버킷 목록 확인
        buckets = supabase.storage.list_buckets()
        bucket_names = [b.name for b in buckets]

        if BUCKET_NAME not in bucket_names:
            print(f"버킷 '{BUCKET_NAME}' 생성 중...")
            supabase.storage.create_bucket(
                BUCKET_NAME,
                options={
                    "public": True,  # 공개 접근 허용
                    "file_size_limit": 10485760,  # 10MB
                    "allowed_mime_types": ["image/png", "image/jpeg", "image/gif", "image/webp"]
                }
            )
            print(f"버킷 '{BUCKET_NAME}' 생성 완료")
        else:
            print(f"버킷 '{BUCKET_NAME}' 이미 존재")
    except Exception as e:
        print(f"버킷 생성 오류: {e}")
        # 이미 존재하면 무시
        pass

def upload_images(supabase: Client):
    """이미지 파일들을 Supabase Storage에 업로드"""
    if not IMAGES_DIR.exists():
        print(f"이미지 디렉토리가 없습니다: {IMAGES_DIR}")
        return

    # 이미 업로드된 파일 목록 (캐싱용)
    uploaded_files = set()

    # 모든 이미지 파일 찾기
    image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.webp'}
    total_uploaded = 0
    total_skipped = 0
    total_errors = 0

    for problem_dir in IMAGES_DIR.iterdir():
        if not problem_dir.is_dir():
            continue

        problem_id = problem_dir.name

        for image_file in problem_dir.iterdir():
            if image_file.suffix.lower() not in image_extensions:
                continue

            # Storage 경로: {문제번호}/{파일명}
            storage_path = f"{problem_id}/{image_file.name}"

            try:
                # 파일 읽기
                with open(image_file, 'rb') as f:
                    file_data = f.read()

                # MIME 타입 결정
                mime_type, _ = mimetypes.guess_type(str(image_file))
                if not mime_type:
                    mime_type = 'image/png'

                # 업로드 (upsert로 덮어쓰기)
                result = supabase.storage.from_(BUCKET_NAME).upload(
                    storage_path,
                    file_data,
                    file_options={"content-type": mime_type, "upsert": "true"}
                )

                total_uploaded += 1
                if total_uploaded % 100 == 0:
                    print(f"업로드 진행: {total_uploaded}개 완료...")

            except Exception as e:
                error_msg = str(e)
                if "Duplicate" in error_msg or "already exists" in error_msg.lower():
                    total_skipped += 1
                else:
                    print(f"업로드 오류 ({storage_path}): {e}")
                    total_errors += 1

    print(f"\n업로드 완료: {total_uploaded}개")
    print(f"스킵 (이미 존재): {total_skipped}개")
    print(f"오류: {total_errors}개")

def get_public_url(problem_id: str, filename: str) -> str:
    """Supabase Storage 공개 URL 생성"""
    return f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET_NAME}/{problem_id}/{filename}"

def update_question_urls(supabase: Client):
    """DB의 question 컬럼에서 백준 이미지 URL을 Supabase URL로 변경"""
    print("\nDB question 컬럼 업데이트 중...")

    # 백준 이미지 URL 패턴
    # ![alt](https://www.acmicpc.net/images/{번호}/{파일명}.png)
    # 또는 ![](https://www.acmicpc.net/...)
    pattern = r'!\[([^\]]*)\]\(https?://(?:www\.)?acmicpc\.net/(?:upload/)?images/(\d+)/([^)]+)\)'

    # 모든 문제 조회 (이미지 URL이 포함된 것만)
    result = supabase.table("base_problems").select("id, original_id, question").ilike("question", "%acmicpc.net%").execute()

    if not result.data:
        print("업데이트할 문제가 없습니다.")
        return

    print(f"업데이트 대상: {len(result.data)}개 문제")

    updated_count = 0
    for problem in result.data:
        question = problem.get("question", "")
        if not question:
            continue

        # 이미지 URL 치환
        def replace_url(match):
            alt_text = match.group(1)
            img_problem_id = match.group(2)
            filename = match.group(3)
            new_url = get_public_url(img_problem_id, filename)
            return f"![{alt_text}]({new_url})"

        new_question = re.sub(pattern, replace_url, question)

        if new_question != question:
            # DB 업데이트
            try:
                supabase.table("base_problems").update({
                    "question": new_question
                }).eq("id", problem["id"]).execute()
                updated_count += 1

                if updated_count % 50 == 0:
                    print(f"DB 업데이트 진행: {updated_count}개 완료...")
            except Exception as e:
                print(f"DB 업데이트 오류 (original_id={problem.get('original_id')}): {e}")

    print(f"DB 업데이트 완료: {updated_count}개 문제")

def main():
    print("=" * 50)
    print("백준 이미지 Supabase Storage 업로드")
    print("=" * 50)

    # Supabase 클라이언트 생성
    supabase = get_supabase_client()
    print(f"Supabase 연결: {SUPABASE_URL}")

    # 1. 버킷 생성
    create_bucket_if_not_exists(supabase)

    # 2. 이미지 업로드
    print(f"\n이미지 디렉토리: {IMAGES_DIR}")
    upload_images(supabase)

    # 3. DB URL 업데이트
    update_question_urls(supabase)

    print("\n완료!")

if __name__ == "__main__":
    main()
