-- =====================================================
-- problem_hints 테이블 컬럼 이름 변경
-- blank_index → hint_index (모든 유형 지원)
-- =====================================================

-- 1. 컬럼 이름 변경 (존재하는 경우에만)
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'problem_hints' AND column_name = 'blank_index'
    ) THEN
        ALTER TABLE problem_hints RENAME COLUMN blank_index TO hint_index;
    END IF;
END $$;

-- 2. 기존 인덱스 삭제 및 새 인덱스 생성
DROP INDEX IF EXISTS idx_problem_hints_lookup;
CREATE INDEX IF NOT EXISTS idx_problem_hints_lookup
ON problem_hints (problem_id, problem_type, hint_index);

-- 3. 유니크 제약 조건 업데이트
ALTER TABLE problem_hints DROP CONSTRAINT IF EXISTS problem_hints_problem_id_problem_type_blank_index_key;
ALTER TABLE problem_hints DROP CONSTRAINT IF EXISTS problem_hints_problem_id_problem_type_hint_index_key;
ALTER TABLE problem_hints ADD CONSTRAINT problem_hints_problem_id_problem_type_hint_index_key
    UNIQUE (problem_id, problem_type, hint_index);

-- 4. 코멘트 업데이트
COMMENT ON COLUMN problem_hints.hint_index IS '힌트 위치: 빈칸/블록/단계 인덱스';
