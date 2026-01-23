-- ============================================================
-- increment_problem_solve RPC 함수
-- 사용자가 문제를 처음 맞췄을 때만 solve_count 증가
--
-- 주의: 이 함수는 attempt INSERT 이후에 호출됨
--       따라서 정답 attempt가 1개일 때 = 처음 맞춤
-- ============================================================

CREATE OR REPLACE FUNCTION increment_problem_solve(
    p_user_id UUID,
    p_base_problem_id UUID
)
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_correct_count INTEGER := 0;
    v_new_count INTEGER;
    v_incremented BOOLEAN := FALSE;
    v_is_first_solve BOOLEAN := FALSE;
BEGIN
    -- 1. 이 사용자가 이 문제를 맞춘 횟수 확인
    -- (이 함수는 attempt INSERT 이후 호출되므로, 1이면 처음 맞춘 것)
    SELECT COUNT(*) INTO v_correct_count
    FROM attempts
    WHERE user_id = p_user_id
      AND base_problem_id = p_base_problem_id
      AND is_correct = TRUE;

    -- 2. 정답 attempt가 정확히 1개 = 처음 맞춘 것
    v_is_first_solve := (v_correct_count = 1);

    -- 3. 처음 맞춘 경우에만 solve_count 증가
    IF v_is_first_solve THEN
        UPDATE base_problems
        SET solve_count = COALESCE(solve_count, 0) + 1,
            updated_at = NOW()
        WHERE id = p_base_problem_id
        RETURNING solve_count INTO v_new_count;

        v_incremented := TRUE;
    ELSE
        -- 이미 푼 경우 현재 값만 반환
        SELECT solve_count INTO v_new_count
        FROM base_problems
        WHERE id = p_base_problem_id;
    END IF;

    RETURN jsonb_build_object(
        'incremented', v_incremented,
        'solve_count', COALESCE(v_new_count, 0),
        'is_first_solve', v_is_first_solve,
        'correct_attempts', v_correct_count
    );
END;
$$;

-- 함수 권한 설정
GRANT EXECUTE ON FUNCTION increment_problem_solve(UUID, UUID) TO authenticated;
GRANT EXECUTE ON FUNCTION increment_problem_solve(UUID, UUID) TO service_role;

-- 주석 추가
COMMENT ON FUNCTION increment_problem_solve IS '사용자가 문제를 처음 맞췄을 때만 base_problems.solve_count를 증가시킵니다.';
