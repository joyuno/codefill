-- ============================================================
-- add_chat_message 함수 수정 (기존 chat_messages 스키마에 맞춤)
-- 기존 컬럼: id, session_id, role, content, message_meta, chips, created_at
-- ============================================================

-- 기존 함수 삭제 후 재생성
DROP FUNCTION IF EXISTS public.add_chat_message(UUID, TEXT, TEXT, TEXT, JSONB);

-- add_chat_message 함수 (기존 스키마에 맞춤)
CREATE OR REPLACE FUNCTION public.add_chat_message(
    p_session_id UUID,
    p_role TEXT,
    p_content TEXT,
    p_message_type TEXT DEFAULT 'text',
    p_metadata JSONB DEFAULT NULL
)
RETURNS UUID
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_message_id UUID;
BEGIN
    -- message_type은 message_meta에 포함
    INSERT INTO public.chat_messages (session_id, role, content, message_meta)
    VALUES (
        p_session_id,
        p_role,
        p_content,
        COALESCE(p_metadata, '{}'::jsonb) || jsonb_build_object('message_type', p_message_type)
    )
    RETURNING id INTO v_message_id;

    -- 세션 업데이트 시간 갱신
    UPDATE public.chat_sessions
    SET updated_at = NOW()
    WHERE id = p_session_id;

    RETURN v_message_id;
END;
$$;

-- 권한 부여
GRANT EXECUTE ON FUNCTION public.add_chat_message TO authenticated;
GRANT EXECUTE ON FUNCTION public.add_chat_message TO service_role;
