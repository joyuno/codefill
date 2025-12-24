-- =====================================================
-- 문제 테이블 관계 수정: original_id → base_problem_id (UUID FK)
-- 날짜: 2025-12-24
-- 목적: 표준 관계형 설계로 변경 (PK-FK 연결)
-- =====================================================
--
-- 변경 사항:
--   1. problems_blank, problems_puzzle, problems_guided에 base_problem_id 추가
--   2. FK 제약조건 설정 (ON DELETE CASCADE)
--   3. original_id 컬럼 제거 (더 이상 관계 연결에 사용 안함)
--
-- =====================================================

-- 1. problems_blank 테이블 수정
-- =====================================================
ALTER TABLE problems_blank
ADD COLUMN IF NOT EXISTS base_problem_id uuid;

-- FK 제약조건 추가
ALTER TABLE problems_blank
ADD CONSTRAINT fk_problems_blank_base_problem
FOREIGN KEY (base_problem_id)
REFERENCES base_problems(id)
ON DELETE CASCADE;

-- original_id 컬럼 제거
ALTER TABLE problems_blank
DROP COLUMN IF EXISTS original_id;

-- 인덱스 추가 (조회 성능)
CREATE INDEX IF NOT EXISTS idx_problems_blank_base_problem_id
ON problems_blank(base_problem_id);


-- 2. problems_puzzle 테이블 수정
-- =====================================================
ALTER TABLE problems_puzzle
ADD COLUMN IF NOT EXISTS base_problem_id uuid;

-- FK 제약조건 추가
ALTER TABLE problems_puzzle
ADD CONSTRAINT fk_problems_puzzle_base_problem
FOREIGN KEY (base_problem_id)
REFERENCES base_problems(id)
ON DELETE CASCADE;

-- original_id 컬럼 제거
ALTER TABLE problems_puzzle
DROP COLUMN IF EXISTS original_id;

-- 인덱스 추가
CREATE INDEX IF NOT EXISTS idx_problems_puzzle_base_problem_id
ON problems_puzzle(base_problem_id);


-- 3. problems_guided 테이블 수정
-- =====================================================
ALTER TABLE problems_guided
ADD COLUMN IF NOT EXISTS base_problem_id uuid;

-- FK 제약조건 추가
ALTER TABLE problems_guided
ADD CONSTRAINT fk_problems_guided_base_problem
FOREIGN KEY (base_problem_id)
REFERENCES base_problems(id)
ON DELETE CASCADE;

-- original_id 컬럼 제거
ALTER TABLE problems_guided
DROP COLUMN IF EXISTS original_id;

-- 인덱스 추가
CREATE INDEX IF NOT EXISTS idx_problems_guided_base_problem_id
ON problems_guided(base_problem_id);


-- 4. attempts 테이블도 확인/수정 (base_problem_id FK 추가)
-- =====================================================
-- attempts.base_problem_id가 이미 있지만 FK 제약조건이 없을 수 있음
ALTER TABLE attempts
DROP CONSTRAINT IF EXISTS fk_attempts_base_problem;

ALTER TABLE attempts
ADD CONSTRAINT fk_attempts_base_problem
FOREIGN KEY (base_problem_id)
REFERENCES base_problems(id)
ON DELETE SET NULL;

-- 인덱스 추가
CREATE INDEX IF NOT EXISTS idx_attempts_base_problem_id
ON attempts(base_problem_id);


-- =====================================================
-- 완료 후 구조 확인용 쿼리
-- =====================================================
-- SELECT
--     tc.table_name,
--     kcu.column_name,
--     ccu.table_name AS foreign_table_name,
--     ccu.column_name AS foreign_column_name
-- FROM information_schema.table_constraints AS tc
-- JOIN information_schema.key_column_usage AS kcu
--     ON tc.constraint_name = kcu.constraint_name
-- JOIN information_schema.constraint_column_usage AS ccu
--     ON ccu.constraint_name = tc.constraint_name
-- WHERE tc.constraint_type = 'FOREIGN KEY'
-- AND tc.table_name IN ('problems_blank', 'problems_puzzle', 'problems_guided', 'attempts');
