-- 크레딧 사용 내역 테이블
CREATE TABLE IF NOT EXISTS credit_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(20) NOT NULL CHECK (type IN ('use', 'charge', 'bonus', 'refund')),
    amount INTEGER NOT NULL,  -- 양수: 충전/보너스/환불, 음수: 사용
    balance INTEGER NOT NULL,  -- 변경 후 잔액
    description TEXT,
    metadata JSONB DEFAULT '{}',  -- 추가 정보 (문제 ID, 결제 ID 등)
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스
CREATE INDEX IF NOT EXISTS idx_credit_history_user_id ON credit_history(user_id);
CREATE INDEX IF NOT EXISTS idx_credit_history_created_at ON credit_history(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_credit_history_type ON credit_history(type);

-- 크레딧 사용 시 내역 기록 함수 (deduct_credits 업데이트)
CREATE OR REPLACE FUNCTION deduct_credits_with_history(
    p_user_id UUID,
    p_amount INTEGER DEFAULT 10,
    p_description TEXT DEFAULT '문제 생성',
    p_metadata JSONB DEFAULT '{}'
)
RETURNS TABLE (success BOOLEAN, remaining_credits INTEGER, message TEXT)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_current_credits INTEGER;
    v_new_credits INTEGER;
BEGIN
    -- 현재 크레딧 조회 (FOR UPDATE로 락)
    SELECT credits INTO v_current_credits
    FROM users
    WHERE id = p_user_id
    FOR UPDATE;

    IF v_current_credits IS NULL THEN
        RETURN QUERY SELECT FALSE, 0, '사용자를 찾을 수 없습니다.'::TEXT;
        RETURN;
    END IF;

    IF v_current_credits < p_amount THEN
        RETURN QUERY SELECT FALSE, v_current_credits, '크레딧이 부족합니다.'::TEXT;
        RETURN;
    END IF;

    -- 크레딧 차감
    v_new_credits := v_current_credits - p_amount;

    UPDATE users
    SET credits = v_new_credits
    WHERE id = p_user_id;

    -- 사용 내역 기록 (metadata 포함)
    INSERT INTO credit_history (user_id, type, amount, balance, description, metadata)
    VALUES (p_user_id, 'use', -p_amount, v_new_credits, p_description, p_metadata);

    RETURN QUERY SELECT TRUE, v_new_credits, '크레딧이 차감되었습니다.'::TEXT;
END;
$$;

-- 크레딧 충전 함수 (내역 기록 포함)
CREATE OR REPLACE FUNCTION charge_credits(
    p_user_id UUID,
    p_amount INTEGER,
    p_bonus INTEGER DEFAULT 0,
    p_description TEXT DEFAULT '크레딧 충전'
)
RETURNS TABLE (success BOOLEAN, new_credits INTEGER, message TEXT)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_current_credits INTEGER;
    v_new_credits INTEGER;
    v_total_amount INTEGER;
BEGIN
    v_total_amount := p_amount + p_bonus;

    -- 현재 크레딧 조회 (FOR UPDATE로 락)
    SELECT credits INTO v_current_credits
    FROM users
    WHERE id = p_user_id
    FOR UPDATE;

    IF v_current_credits IS NULL THEN
        RETURN QUERY SELECT FALSE, 0, '사용자를 찾을 수 없습니다.'::TEXT;
        RETURN;
    END IF;

    -- 크레딧 추가
    v_new_credits := v_current_credits + v_total_amount;

    UPDATE users
    SET credits = v_new_credits
    WHERE id = p_user_id;

    -- 충전 내역 기록
    INSERT INTO credit_history (user_id, type, amount, balance, description)
    VALUES (p_user_id, 'charge', p_amount, v_current_credits + p_amount, p_description);

    -- 보너스가 있으면 별도 기록
    IF p_bonus > 0 THEN
        INSERT INTO credit_history (user_id, type, amount, balance, description)
        VALUES (p_user_id, 'bonus', p_bonus, v_new_credits, '충전 보너스');
    END IF;

    RETURN QUERY SELECT TRUE, v_new_credits, '크레딧이 충전되었습니다.'::TEXT;
END;
$$;

-- 회원가입 시 초기 크레딧 지급 내역 기록 함수
CREATE OR REPLACE FUNCTION record_initial_credits(p_user_id UUID)
RETURNS VOID
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_credits INTEGER;
BEGIN
    SELECT credits INTO v_credits FROM users WHERE id = p_user_id;

    IF v_credits IS NOT NULL THEN
        INSERT INTO credit_history (user_id, type, amount, balance, description)
        VALUES (p_user_id, 'bonus', v_credits, v_credits, '회원가입 보너스');
    END IF;
END;
$$;
