-- ============================================================
-- Migration: attempts.problem_id 컬럼 삭제
--
-- 이유:
-- - base_problem_id가 문제 추적의 주요 키로 사용됨
-- - problem_id는 더 이상 사용되지 않음 (레거시)
-- - 혼란 방지 및 스키마 정리
-- ============================================================

-- 1. attempts 테이블에서 problem_id 컬럼 삭제
-- (이미 삭제된 경우 에러 방지)
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
