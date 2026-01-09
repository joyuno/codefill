-- ============================================================
-- Migration: user_memories.problem_id 컬럼 삭제
--
-- 이유:
-- - attempt_id FK를 통해 문제 정보 접근 가능
-- - problem_id 비정규화 불필요
-- ============================================================

-- 1. user_memories 테이블에서 problem_id 컬럼 삭제
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
