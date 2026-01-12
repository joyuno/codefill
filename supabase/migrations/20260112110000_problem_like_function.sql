-- =====================================================
-- 문제 좋아요 토글 RPC 함수
-- =====================================================

-- 문제 좋아요 토글 함수
CREATE OR REPLACE FUNCTION toggle_problem_like(
    p_user_id UUID,
    p_base_problem_id UUID
)
RETURNS jsonb AS $$
DECLARE
    v_existing_like_id UUID;
    v_is_liked BOOLEAN;
    v_new_like_count INTEGER;
BEGIN
    -- 기존 좋아요 확인
    SELECT id INTO v_existing_like_id
    FROM problem_likes
    WHERE user_id = p_user_id AND base_problem_id = p_base_problem_id;

    IF v_existing_like_id IS NOT NULL THEN
        -- 좋아요 취소
        DELETE FROM problem_likes WHERE id = v_existing_like_id;

        -- like_count 감소
        UPDATE base_problems
        SET like_count = GREATEST(0, COALESCE(like_count, 0) - 1)
        WHERE id = p_base_problem_id
        RETURNING like_count INTO v_new_like_count;

        v_is_liked := FALSE;
    ELSE
        -- 좋아요 추가
        INSERT INTO problem_likes (user_id, base_problem_id)
        VALUES (p_user_id, p_base_problem_id);

        -- like_count 증가
        UPDATE base_problems
        SET like_count = COALESCE(like_count, 0) + 1
        WHERE id = p_base_problem_id
        RETURNING like_count INTO v_new_like_count;

        v_is_liked := TRUE;
    END IF;

    RETURN jsonb_build_object(
        'success', TRUE,
        'is_liked', v_is_liked,
        'like_count', COALESCE(v_new_like_count, 0)
    );
EXCEPTION WHEN OTHERS THEN
    RETURN jsonb_build_object(
        'success', FALSE,
        'is_liked', FALSE,
        'like_count', 0,
        'error', SQLERRM
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 문제 조회수 증가 함수
CREATE OR REPLACE FUNCTION increment_problem_view(
    p_base_problem_id UUID
)
RETURNS VOID AS $$
BEGIN
    UPDATE base_problems
    SET view_count = COALESCE(view_count, 0) + 1
    WHERE id = p_base_problem_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 권한 부여
GRANT EXECUTE ON FUNCTION toggle_problem_like(UUID, UUID) TO authenticated;
GRANT EXECUTE ON FUNCTION increment_problem_view(UUID) TO anon;
GRANT EXECUTE ON FUNCTION increment_problem_view(UUID) TO authenticated;
