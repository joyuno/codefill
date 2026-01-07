-- =====================================================
-- CodeFill DB 구조 개선 마이그레이션
-- 날짜: 2025-12-24
-- 목적: 옵션 A 단순 구조 (creator_id 직접 참조)
-- =====================================================
--
-- 변경 사항:
--   1. user_generated_id 컬럼 삭제 (중복 제거)
--   2. user_generated_problems 테이블 삭제
--   3. FK 제약조건 추가 (creator_id → users, original_id → base_problems)
--   4. 인덱스 추가 (조회 최적화)
--
-- 주의: base_problems 테이블은 변경하지 않음 (2,048개 데이터 보존)
-- =====================================================

-- 1. user_generated_id 컬럼 삭제 (중복 제거)
-- 현재 데이터 0개이므로 안전
ALTER TABLE problems_blank DROP COLUMN IF EXISTS user_generated_id;
ALTER TABLE problems_puzzle DROP COLUMN IF EXISTS user_generated_id;
ALTER TABLE problems_guided DROP COLUMN IF EXISTS user_generated_id;

-- 2. user_generated_problems 테이블 삭제
-- 현재 데이터 0개이므로 안전
DROP TABLE IF EXISTS user_generated_problems;

-- 3. FK 제약조건 추가: creator_id → users.id
-- 사용자 삭제 시 creator_id를 NULL로 설정 (문제는 유지)
ALTER TABLE problems_blank
ADD CONSTRAINT fk_blank_creator
FOREIGN KEY (creator_id) REFERENCES users(id) ON DELETE SET NULL;

ALTER TABLE problems_puzzle
ADD CONSTRAINT fk_puzzle_creator
FOREIGN KEY (creator_id) REFERENCES users(id) ON DELETE SET NULL;

ALTER TABLE problems_guided
ADD CONSTRAINT fk_guided_creator
FOREIGN KEY (creator_id) REFERENCES users(id) ON DELETE SET NULL;

-- 4. FK 제약조건 추가: original_id → base_problems.original_id
-- 원본 문제 삭제 시 변형 문제도 삭제
ALTER TABLE problems_blank
ADD CONSTRAINT fk_blank_base
FOREIGN KEY (original_id) REFERENCES base_problems(original_id) ON DELETE CASCADE;

ALTER TABLE problems_puzzle
ADD CONSTRAINT fk_puzzle_base
FOREIGN KEY (original_id) REFERENCES base_problems(original_id) ON DELETE CASCADE;

ALTER TABLE problems_guided
ADD CONSTRAINT fk_guided_base
FOREIGN KEY (original_id) REFERENCES base_problems(original_id) ON DELETE CASCADE;

-- 5. 인덱스 추가 (마이페이지 조회 최적화)
CREATE INDEX IF NOT EXISTS idx_blank_creator ON problems_blank(creator_id);
CREATE INDEX IF NOT EXISTS idx_puzzle_creator ON problems_puzzle(creator_id);
CREATE INDEX IF NOT EXISTS idx_guided_creator ON problems_guided(creator_id);

-- 6. user_generated_problems_detail 뷰도 삭제 (의존성)
DROP VIEW IF EXISTS user_generated_problems_detail;
