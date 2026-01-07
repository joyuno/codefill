-- =====================================================
-- Badge Stats Columns
-- 뱃지 조건 체크를 위한 user_stats 컬럼 추가
-- =====================================================

-- 문제 유형별 (기존 blank_solved 유지, puzzle_solved 추가)
-- guided_solved, implementation_solved는 향후 모드 추가 대비
ALTER TABLE user_stats ADD COLUMN IF NOT EXISTS puzzle_solved INTEGER DEFAULT 0;
ALTER TABLE user_stats ADD COLUMN IF NOT EXISTS guided_solved INTEGER DEFAULT 0;
ALTER TABLE user_stats ADD COLUMN IF NOT EXISTS implementation_solved INTEGER DEFAULT 0;

-- 난이도별 해결 수
ALTER TABLE user_stats ADD COLUMN IF NOT EXISTS easy_solved INTEGER DEFAULT 0;
ALTER TABLE user_stats ADD COLUMN IF NOT EXISTS medium_solved INTEGER DEFAULT 0;
ALTER TABLE user_stats ADD COLUMN IF NOT EXISTS hard_solved INTEGER DEFAULT 0;

-- 검증
DO $$
DECLARE
    col_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO col_count
    FROM information_schema.columns
    WHERE table_name = 'user_stats'
    AND column_name IN ('puzzle_solved', 'guided_solved', 'implementation_solved', 'easy_solved', 'medium_solved', 'hard_solved');

    IF col_count = 6 THEN
        RAISE NOTICE 'Badge stats columns added successfully: 6 new columns';
    ELSE
        RAISE WARNING 'Expected 6 new columns, found %', col_count;
    END IF;
END $$;
