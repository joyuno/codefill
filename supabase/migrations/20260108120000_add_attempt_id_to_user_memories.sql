-- ============================================================
-- user_memories 테이블에 attempt_id 컬럼 추가
-- attempts 테이블과 연결하여 풀이 기록 추적
-- ============================================================

-- attempt_id 컬럼 추가
ALTER TABLE public.user_memories
ADD COLUMN IF NOT EXISTS attempt_id UUID REFERENCES public.attempts(id) ON DELETE SET NULL;

-- 인덱스 추가
CREATE INDEX IF NOT EXISTS idx_user_memories_attempt_id ON public.user_memories(attempt_id);

COMMENT ON COLUMN public.user_memories.attempt_id IS 'attempts 테이블 참조 (풀이 기록과 연결)';
