-- =====================================================
-- Add attempt_number column to attempts table
-- 동일 문제에 대한 시도 순서 (1, 2, 3...)
-- accuracy 뱃지 체크에 사용 (첫 시도 정답)
-- =====================================================

-- 1. 컬럼 추가
ALTER TABLE attempts ADD COLUMN IF NOT EXISTS attempt_number INTEGER DEFAULT 1;

-- 2. 인덱스 추가 (첫 시도 정답 조회 최적화)
CREATE INDEX IF NOT EXISTS idx_attempts_first_try
ON attempts(user_id, is_correct, attempt_number)
WHERE attempt_number = 1 AND is_correct = true;

-- 3. 기존 데이터 백필 (submitted_at 순서로 번호 매기기)
-- CTE로 각 (user_id, problem_id) 그룹별 순서 계산 후 업데이트
WITH numbered AS (
    SELECT
        id,
        ROW_NUMBER() OVER (
            PARTITION BY user_id, problem_id
            ORDER BY submitted_at ASC
        ) as rn
    FROM attempts
)
UPDATE attempts a
SET attempt_number = n.rn
FROM numbered n
WHERE a.id = n.id;

-- 4. 검증
DO $$
DECLARE
    col_exists BOOLEAN;
    idx_exists BOOLEAN;
BEGIN
    -- 컬럼 존재 확인
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'attempts' AND column_name = 'attempt_number'
    ) INTO col_exists;

    -- 인덱스 존재 확인
    SELECT EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE tablename = 'attempts' AND indexname = 'idx_attempts_first_try'
    ) INTO idx_exists;

    IF col_exists AND idx_exists THEN
        RAISE NOTICE 'SUCCESS: attempt_number column and index created';
    ELSE
        RAISE WARNING 'FAILED: column exists=%, index exists=%', col_exists, idx_exists;
    END IF;
END $$;

-- 5. 코멘트 추가
COMMENT ON COLUMN attempts.attempt_number IS '동일 문제에 대한 시도 순서 (1=첫 시도)';
