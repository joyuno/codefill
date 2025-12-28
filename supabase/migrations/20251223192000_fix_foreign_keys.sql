-- =====================================================
-- CodeFill Database Migration: Fix Foreign Keys
-- 1. user_generated_problems.user_id → users.id 연결
-- 2. problems_blank/puzzle/guided.original_id → base_problems.original_id 연결
-- =====================================================

-- =====================================================
-- 1. user_generated_problems.user_id FK 변경
-- auth.users → users 테이블로 변경
-- =====================================================

-- 기존 FK 제거
ALTER TABLE user_generated_problems
    DROP CONSTRAINT IF EXISTS user_generated_problems_user_id_fkey;

-- users 테이블로 새 FK 추가
ALTER TABLE user_generated_problems
    ADD CONSTRAINT user_generated_problems_user_id_fkey
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- =====================================================
-- 2. problems_blank/puzzle/guided.creator_id FK 변경
-- auth.users → users 테이블로 변경
-- =====================================================

-- problems_blank
ALTER TABLE problems_blank
    DROP CONSTRAINT IF EXISTS problems_blank_creator_id_fkey;
ALTER TABLE problems_blank
    ADD CONSTRAINT problems_blank_creator_id_fkey
    FOREIGN KEY (creator_id) REFERENCES users(id) ON DELETE SET NULL;

-- problems_puzzle
ALTER TABLE problems_puzzle
    DROP CONSTRAINT IF EXISTS problems_puzzle_creator_id_fkey;
ALTER TABLE problems_puzzle
    ADD CONSTRAINT problems_puzzle_creator_id_fkey
    FOREIGN KEY (creator_id) REFERENCES users(id) ON DELETE SET NULL;

-- problems_guided
ALTER TABLE problems_guided
    DROP CONSTRAINT IF EXISTS problems_guided_creator_id_fkey;
ALTER TABLE problems_guided
    ADD CONSTRAINT problems_guided_creator_id_fkey
    FOREIGN KEY (creator_id) REFERENCES users(id) ON DELETE SET NULL;

-- =====================================================
-- 3. original_id FK 연결
-- problems_blank/puzzle/guided.original_id → base_problems.original_id
-- =====================================================

-- problems_blank.original_id → base_problems.original_id
ALTER TABLE problems_blank
    DROP CONSTRAINT IF EXISTS problems_blank_original_id_fkey;
ALTER TABLE problems_blank
    ADD CONSTRAINT problems_blank_original_id_fkey
    FOREIGN KEY (original_id) REFERENCES base_problems(original_id) ON DELETE CASCADE;

-- problems_puzzle.original_id → base_problems.original_id
ALTER TABLE problems_puzzle
    DROP CONSTRAINT IF EXISTS problems_puzzle_original_id_fkey;
ALTER TABLE problems_puzzle
    ADD CONSTRAINT problems_puzzle_original_id_fkey
    FOREIGN KEY (original_id) REFERENCES base_problems(original_id) ON DELETE CASCADE;

-- problems_guided.original_id → base_problems.original_id
ALTER TABLE problems_guided
    DROP CONSTRAINT IF EXISTS problems_guided_original_id_fkey;
ALTER TABLE problems_guided
    ADD CONSTRAINT problems_guided_original_id_fkey
    FOREIGN KEY (original_id) REFERENCES base_problems(original_id) ON DELETE CASCADE;

-- user_generated_problems.original_id → base_problems.original_id
ALTER TABLE user_generated_problems
    DROP CONSTRAINT IF EXISTS user_generated_problems_original_id_fkey;
ALTER TABLE user_generated_problems
    ADD CONSTRAINT user_generated_problems_original_id_fkey
    FOREIGN KEY (original_id) REFERENCES base_problems(original_id) ON DELETE CASCADE;

-- =====================================================
-- 4. RLS 정책 업데이트 (users 테이블 기준)
-- =====================================================

-- 기존 정책 삭제 후 재생성
DROP POLICY IF EXISTS "Users can view own generated problems" ON user_generated_problems;
DROP POLICY IF EXISTS "Users can create own generated problems" ON user_generated_problems;
DROP POLICY IF EXISTS "Users can update own generated problems" ON user_generated_problems;
DROP POLICY IF EXISTS "Users can delete own generated problems" ON user_generated_problems;

-- users 테이블 기준으로 정책 재생성
-- 주의: auth.uid()는 auth.users의 id를 반환하므로,
-- users 테이블과 auth.users가 동기화되어 있어야 함

CREATE POLICY "Users can view own generated problems"
    ON user_generated_problems FOR SELECT
    USING (user_id IN (SELECT id FROM users WHERE id = auth.uid()));

CREATE POLICY "Users can create own generated problems"
    ON user_generated_problems FOR INSERT
    WITH CHECK (user_id IN (SELECT id FROM users WHERE id = auth.uid()));

CREATE POLICY "Users can update own generated problems"
    ON user_generated_problems FOR UPDATE
    USING (user_id IN (SELECT id FROM users WHERE id = auth.uid()));

CREATE POLICY "Users can delete own generated problems"
    ON user_generated_problems FOR DELETE
    USING (user_id IN (SELECT id FROM users WHERE id = auth.uid()));

-- =====================================================
-- 5. 코멘트 업데이트
-- =====================================================

COMMENT ON CONSTRAINT user_generated_problems_user_id_fkey ON user_generated_problems
    IS 'users 테이블의 id 참조';
COMMENT ON CONSTRAINT problems_blank_original_id_fkey ON problems_blank
    IS 'base_problems.original_id 참조';
COMMENT ON CONSTRAINT problems_puzzle_original_id_fkey ON problems_puzzle
    IS 'base_problems.original_id 참조';
COMMENT ON CONSTRAINT problems_guided_original_id_fkey ON problems_guided
    IS 'base_problems.original_id 참조';
