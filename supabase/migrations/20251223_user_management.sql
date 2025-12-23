-- =====================================================
-- User Management Features Migration
-- 2025-12-23
-- =====================================================

-- 1. 닉네임 변경 날짜 추적 컬럼 추가
ALTER TABLE users ADD COLUMN IF NOT EXISTS nickname_last_changed_at TIMESTAMPTZ;

-- 2. 기존 중복 닉네임 처리 (있다면)
DO $$
BEGIN
    -- 중복된 닉네임에 숫자 붙이기
    WITH duplicates AS (
        SELECT id, name,
               ROW_NUMBER() OVER (PARTITION BY LOWER(name) ORDER BY created_at) as rn
        FROM users
        WHERE name IS NOT NULL AND deleted_at IS NULL
    )
    UPDATE users u
    SET name = u.name || '_' || d.rn::text
    FROM duplicates d
    WHERE u.id = d.id AND d.rn > 1;
END $$;

-- 3. 닉네임 UNIQUE 인덱스 생성 (soft-delete 제외, 대소문자 무시)
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_name_unique
ON users(LOWER(name)) WHERE name IS NOT NULL AND deleted_at IS NULL;

-- 4. 이메일 소문자 인덱스 (검색 최적화)
CREATE INDEX IF NOT EXISTS idx_users_email_lower
ON users(LOWER(email)) WHERE deleted_at IS NULL;
