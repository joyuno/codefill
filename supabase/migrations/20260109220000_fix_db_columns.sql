-- ============================================================
-- Migration: DB 컬럼 정리 및 FK 관계 추가
--
-- 1. attempts.problem_id 삭제 (더이상 사용 안함, base_problem_id 사용)
-- 2. feedback_history.base_problem_id 추가
-- 3. hint_logs.base_problem_id 추가
-- 4. user_memories.problem_id 삭제
-- ============================================================

-- ============================================================
-- 1. attempts.problem_id 삭제
-- ============================================================
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public'
        AND table_name = 'attempts'
        AND column_name = 'problem_id'
    ) THEN
        ALTER TABLE attempts DROP COLUMN problem_id;
        RAISE NOTICE 'attempts.problem_id 컬럼 삭제 완료';
    ELSE
        RAISE NOTICE 'attempts.problem_id 컬럼이 이미 존재하지 않음';
    END IF;
END $$;

-- ============================================================
-- 2. feedback_history.base_problem_id 추가
-- ============================================================
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public'
        AND table_name = 'feedback_history'
        AND column_name = 'base_problem_id'
    ) THEN
        ALTER TABLE feedback_history ADD COLUMN base_problem_id UUID REFERENCES base_problems(id);
        CREATE INDEX IF NOT EXISTS feedback_history_base_problem_idx ON feedback_history(base_problem_id);
        RAISE NOTICE 'feedback_history.base_problem_id 컬럼 추가 완료';
    ELSE
        RAISE NOTICE 'feedback_history.base_problem_id 컬럼이 이미 존재함';
    END IF;
END $$;

-- ============================================================
-- 3. hint_logs.base_problem_id 추가
-- ============================================================
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public'
        AND table_name = 'hint_logs'
        AND column_name = 'base_problem_id'
    ) THEN
        ALTER TABLE hint_logs ADD COLUMN base_problem_id UUID REFERENCES base_problems(id);
        CREATE INDEX IF NOT EXISTS hint_logs_base_problem_idx ON hint_logs(base_problem_id);
        RAISE NOTICE 'hint_logs.base_problem_id 컬럼 추가 완료';
    ELSE
        RAISE NOTICE 'hint_logs.base_problem_id 컬럼이 이미 존재함';
    END IF;
END $$;

-- ============================================================
-- 4. user_memories.problem_id 삭제
-- ============================================================
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public'
        AND table_name = 'user_memories'
        AND column_name = 'problem_id'
    ) THEN
        ALTER TABLE user_memories DROP COLUMN problem_id;
        RAISE NOTICE 'user_memories.problem_id 컬럼 삭제 완료';
    ELSE
        RAISE NOTICE 'user_memories.problem_id 컬럼이 이미 존재하지 않음';
    END IF;
END $$;

-- ============================================================
-- 5. user_skill_profiles에 누락된 컬럼 기본값 설정
-- ============================================================
DO $$
BEGIN
    -- total_problems_solved
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public'
        AND table_name = 'user_skill_profiles'
        AND column_name = 'total_problems_solved'
    ) THEN
        UPDATE user_skill_profiles SET total_problems_solved = 0 WHERE total_problems_solved IS NULL;
        ALTER TABLE user_skill_profiles ALTER COLUMN total_problems_solved SET DEFAULT 0;
    END IF;

    -- total_problems_attempted
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public'
        AND table_name = 'user_skill_profiles'
        AND column_name = 'total_problems_attempted'
    ) THEN
        UPDATE user_skill_profiles SET total_problems_attempted = 0 WHERE total_problems_attempted IS NULL;
        ALTER TABLE user_skill_profiles ALTER COLUMN total_problems_attempted SET DEFAULT 0;
    END IF;

    -- current_streak
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public'
        AND table_name = 'user_skill_profiles'
        AND column_name = 'current_streak'
    ) THEN
        UPDATE user_skill_profiles SET current_streak = 0 WHERE current_streak IS NULL;
        ALTER TABLE user_skill_profiles ALTER COLUMN current_streak SET DEFAULT 0;
    END IF;

    -- longest_streak
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public'
        AND table_name = 'user_skill_profiles'
        AND column_name = 'longest_streak'
    ) THEN
        UPDATE user_skill_profiles SET longest_streak = 0 WHERE longest_streak IS NULL;
        ALTER TABLE user_skill_profiles ALTER COLUMN longest_streak SET DEFAULT 0;
    END IF;
END $$;

COMMENT ON COLUMN feedback_history.base_problem_id IS 'base_problems 테이블의 ID (문제 식별용)';
COMMENT ON COLUMN hint_logs.base_problem_id IS 'base_problems 테이블의 ID (문제 식별용)';
