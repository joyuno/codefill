-- ============================================================
-- chat_sessions 테이블에 세션 상태 컬럼들 추가
-- 대화 상태 (stage, collected_info 등) 저장용
-- ============================================================

-- 현재 단계 (intent, collection, discovery, solving 등)
ALTER TABLE public.chat_sessions
ADD COLUMN IF NOT EXISTS current_stage TEXT DEFAULT 'intent';

-- 수집된 정보 (주제, 난이도, 언어 등)
ALTER TABLE public.chat_sessions
ADD COLUMN IF NOT EXISTS collected_info JSONB DEFAULT '{}';

-- 세션 상태 (추가 상태 정보)
ALTER TABLE public.chat_sessions
ADD COLUMN IF NOT EXISTS session_state JSONB DEFAULT '{}';

-- 현재 문제 데이터
ALTER TABLE public.chat_sessions
ADD COLUMN IF NOT EXISTS current_problem_data JSONB;

-- attempt 참조 (현재 풀이 중인 문제)
ALTER TABLE public.chat_sessions
ADD COLUMN IF NOT EXISTS attempt_id UUID REFERENCES public.attempts(id) ON DELETE SET NULL;

-- 힌트 사용 횟수
ALTER TABLE public.chat_sessions
ADD COLUMN IF NOT EXISTS hints_used INTEGER DEFAULT 0;

-- 인덱스 추가
CREATE INDEX IF NOT EXISTS idx_chat_sessions_current_stage ON public.chat_sessions(current_stage);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_attempt_id ON public.chat_sessions(attempt_id);

COMMENT ON COLUMN public.chat_sessions.current_stage IS '현재 대화 단계 (intent, collection, discovery, solving)';
COMMENT ON COLUMN public.chat_sessions.collected_info IS '수집된 정보 (주제, 난이도, 언어 등)';
COMMENT ON COLUMN public.chat_sessions.session_state IS '추가 세션 상태';
COMMENT ON COLUMN public.chat_sessions.current_problem_data IS '현재 문제 데이터';
COMMENT ON COLUMN public.chat_sessions.attempt_id IS '현재 풀이 중인 attempt 참조';
COMMENT ON COLUMN public.chat_sessions.hints_used IS '힌트 사용 횟수';
