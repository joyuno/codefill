-- ============================================================
-- chat_messages 테이블 및 add_chat_message 함수 생성
-- 채팅 메시지 저장용
-- ============================================================

-- chat_messages 테이블 (없으면 생성)
CREATE TABLE IF NOT EXISTS public.chat_messages (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    session_id UUID NOT NULL REFERENCES public.chat_sessions(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    message_type TEXT DEFAULT 'text',
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스
CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id ON public.chat_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_created_at ON public.chat_messages(created_at);

-- RLS 정책
ALTER TABLE public.chat_messages ENABLE ROW LEVEL SECURITY;

-- 사용자는 자신의 세션 메시지만 볼 수 있음
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies
        WHERE tablename = 'chat_messages' AND policyname = 'Users can view own messages'
    ) THEN
        CREATE POLICY "Users can view own messages" ON public.chat_messages
            FOR SELECT
            USING (
                session_id IN (
                    SELECT id FROM public.chat_sessions WHERE user_id = auth.uid()
                )
            );
    END IF;
END $$;

-- add_chat_message 함수
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
    INSERT INTO public.chat_messages (session_id, role, content, message_type, metadata)
    VALUES (p_session_id, p_role, p_content, p_message_type, p_metadata)
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
