-- ============================================================
-- get_or_create_chat_session 함수 생성
-- 기존 세션 ID가 있으면 사용, 없으면 새로 생성
-- ============================================================

CREATE OR REPLACE FUNCTION public.get_or_create_chat_session(
    p_user_id UUID,
    p_session_id UUID DEFAULT NULL
)
RETURNS UUID
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_session_id UUID;
BEGIN
    -- 세션 ID가 제공되면 해당 세션이 존재하는지 확인
    IF p_session_id IS NOT NULL THEN
        SELECT id INTO v_session_id
        FROM public.chat_sessions
        WHERE id = p_session_id AND user_id = p_user_id;

        -- 세션이 존재하면 해당 ID 반환
        IF v_session_id IS NOT NULL THEN
            -- 업데이트 시간 갱신
            UPDATE public.chat_sessions
            SET updated_at = NOW()
            WHERE id = v_session_id;

            RETURN v_session_id;
        END IF;
    END IF;

    -- 세션이 없으면 새로 생성
    INSERT INTO public.chat_sessions (user_id, session_type, current_stage, collected_info, session_state)
    VALUES (p_user_id, 'exploration', 'intent', '{}'::jsonb, '{}'::jsonb)
    RETURNING id INTO v_session_id;

    RETURN v_session_id;
END;
$$;

-- 권한 부여
GRANT EXECUTE ON FUNCTION public.get_or_create_chat_session TO authenticated;
GRANT EXECUTE ON FUNCTION public.get_or_create_chat_session TO service_role;
