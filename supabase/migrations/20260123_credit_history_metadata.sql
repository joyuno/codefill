-- 크레딧 사용 시 내역 기록 함수 (metadata 파라미터 추가)
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
