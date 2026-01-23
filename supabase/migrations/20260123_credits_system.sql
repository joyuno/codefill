-- =====================================================
-- Credits System Migration (v2)
-- users 테이블에 크레딧 저장
-- =====================================================

-- =====================================================
-- 1. 기존 user_stats 크레딧 정리 (이미 적용했다면)
-- =====================================================
DROP INDEX IF EXISTS idx_user_stats_credits;
ALTER TABLE user_stats DROP COLUMN IF EXISTS credits;

-- 기존 함수/트리거 정리
DROP TRIGGER IF EXISTS on_auth_user_created_stats ON auth.users;
DROP FUNCTION IF EXISTS handle_new_user_with_credits();
DROP FUNCTION IF EXISTS deduct_credits(UUID, INTEGER);
DROP FUNCTION IF EXISTS get_user_credits(UUID);
DROP FUNCTION IF EXISTS add_credits(UUID, INTEGER);

-- =====================================================
-- 2. users 테이블에 credits 컬럼 추가
-- =====================================================
ALTER TABLE users
ADD COLUMN IF NOT EXISTS credits INTEGER DEFAULT 10000;

-- 기존 유저에게 10000 크레딧 부여
UPDATE users
SET credits = 10000
WHERE credits IS NULL;

-- =====================================================
-- 3. 크레딧 차감 함수 (문제 생성 시 호출)
-- =====================================================
CREATE OR REPLACE FUNCTION deduct_credits(
    p_user_id UUID,
    p_amount INTEGER DEFAULT 10
)
RETURNS TABLE (
    success BOOLEAN,
    remaining_credits INTEGER,
    message TEXT
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_current_credits INTEGER;
BEGIN
    -- 현재 크레딧 조회 (FOR UPDATE로 락)
    SELECT credits INTO v_current_credits
    FROM users
    WHERE id = p_user_id
    FOR UPDATE;

    -- 유저가 없는 경우
    IF v_current_credits IS NULL THEN
        RETURN QUERY SELECT
            FALSE::BOOLEAN,
            0::INTEGER,
            '사용자 정보를 찾을 수 없습니다.'::TEXT;
        RETURN;
    END IF;

    -- 크레딧 부족
    IF v_current_credits < p_amount THEN
        RETURN QUERY SELECT
            FALSE::BOOLEAN,
            v_current_credits::INTEGER,
            '크레딧이 부족합니다. 현재: ' || v_current_credits || ', 필요: ' || p_amount::TEXT;
        RETURN;
    END IF;

    -- 크레딧 차감
    UPDATE users
    SET
        credits = credits - p_amount,
        updated_at = NOW()
    WHERE id = p_user_id;

    -- 성공 반환
    RETURN QUERY SELECT
        TRUE::BOOLEAN,
        (v_current_credits - p_amount)::INTEGER,
        '크레딧이 차감되었습니다.'::TEXT;
END;
$$;

-- =====================================================
-- 4. 크레딧 조회 함수
-- =====================================================
CREATE OR REPLACE FUNCTION get_user_credits(p_user_id UUID)
RETURNS INTEGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_credits INTEGER;
BEGIN
    SELECT credits INTO v_credits
    FROM users
    WHERE id = p_user_id;

    RETURN COALESCE(v_credits, 0);
END;
$$;

-- =====================================================
-- 5. 크레딧 추가 함수 (관리자용 또는 향후 충전용)
-- =====================================================
CREATE OR REPLACE FUNCTION add_credits(
    p_user_id UUID,
    p_amount INTEGER
)
RETURNS TABLE (
    success BOOLEAN,
    new_credits INTEGER,
    message TEXT
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    UPDATE users
    SET
        credits = credits + p_amount,
        updated_at = NOW()
    WHERE id = p_user_id;

    IF NOT FOUND THEN
        RETURN QUERY SELECT
            FALSE::BOOLEAN,
            0::INTEGER,
            '사용자 정보를 찾을 수 없습니다.'::TEXT;
        RETURN;
    END IF;

    RETURN QUERY SELECT
        TRUE::BOOLEAN,
        (SELECT credits FROM users WHERE id = p_user_id)::INTEGER,
        p_amount || ' 크레딧이 추가되었습니다.'::TEXT;
END;
$$;

-- =====================================================
-- 6. 인덱스 추가 (성능 최적화)
-- =====================================================
CREATE INDEX IF NOT EXISTS idx_users_credits ON users(credits);

COMMENT ON COLUMN users.credits IS '문제 생성에 사용되는 크레딧 (기본 10000)';
