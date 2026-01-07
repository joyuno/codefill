-- ============================================================
-- Attempt Details 관련 함수들
-- ============================================================

-- 1. increment_attempt_hints: 힌트 사용 횟수 증가
CREATE OR REPLACE FUNCTION increment_attempt_hints(p_attempt_id UUID)
RETURNS VOID AS $$
BEGIN
    UPDATE attempts
    SET
        hints_used = COALESCE(hints_used, 0) + 1,
        total_hints_requested = COALESCE(total_hints_requested, 0) + 1
    WHERE id = p_attempt_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 2. complete_attempt: 시도 완료 처리 (is_correct 업데이트)
CREATE OR REPLACE FUNCTION complete_attempt(
    p_attempt_id UUID,
    p_is_correct BOOLEAN,
    p_xp_earned INTEGER DEFAULT 0,
    p_score INTEGER DEFAULT NULL,
    p_submitted_answer TEXT DEFAULT NULL
)
RETURNS VOID AS $$
DECLARE
    v_started_at TIMESTAMPTZ;
    v_time_spent INTEGER;
BEGIN
    -- 시작 시간 조회
    SELECT created_at INTO v_started_at
    FROM attempts
    WHERE id = p_attempt_id;

    -- 풀이 시간 계산 (초)
    IF v_started_at IS NOT NULL THEN
        v_time_spent := EXTRACT(EPOCH FROM (NOW() - v_started_at))::INTEGER;
    END IF;

    -- 시도 완료 업데이트
    UPDATE attempts
    SET
        is_correct = p_is_correct,
        xp_earned = p_xp_earned,
        score = COALESCE(p_score, score),
        submitted_answer = COALESCE(p_submitted_answer, submitted_answer),
        time_spent = COALESCE(v_time_spent, time_spent),
        submitted_at = NOW()
    WHERE id = p_attempt_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 3. get_attempt_step_count: 현재 step_number 조회 (다음 step 계산용)
CREATE OR REPLACE FUNCTION get_attempt_step_count(p_attempt_id UUID)
RETURNS INTEGER AS $$
DECLARE
    v_count INTEGER;
BEGIN
    SELECT COALESCE(MAX(step_number), 0) INTO v_count
    FROM attempt_details
    WHERE attempt_id = p_attempt_id;

    RETURN v_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 권한 부여
GRANT EXECUTE ON FUNCTION increment_attempt_hints(UUID) TO authenticated;
GRANT EXECUTE ON FUNCTION increment_attempt_hints(UUID) TO service_role;
GRANT EXECUTE ON FUNCTION complete_attempt(UUID, BOOLEAN, INTEGER, INTEGER, TEXT) TO authenticated;
GRANT EXECUTE ON FUNCTION complete_attempt(UUID, BOOLEAN, INTEGER, INTEGER, TEXT) TO service_role;
GRANT EXECUTE ON FUNCTION get_attempt_step_count(UUID) TO authenticated;
GRANT EXECUTE ON FUNCTION get_attempt_step_count(UUID) TO service_role;

-- RLS Policy for attempt_details (INSERT 허용)
DO $$
BEGIN
    -- 기존 정책 삭제 후 재생성
    DROP POLICY IF EXISTS "Users can insert their own attempt details" ON attempt_details;

    CREATE POLICY "Users can insert their own attempt details"
        ON attempt_details FOR INSERT
        TO authenticated
        WITH CHECK (
            EXISTS (
                SELECT 1 FROM attempts a
                WHERE a.id = attempt_details.attempt_id
                AND a.user_id = auth.uid()
            )
        );
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE 'attempt_details table does not exist yet';
END $$;

-- Success message (log only)
DO $$ BEGIN RAISE NOTICE 'Attempt details functions created successfully'; END $$;
