-- =====================================================
-- base_problems 테이블에 한국어 번역 컬럼 추가
-- 번역 캐싱: 첫 번역 시 저장, 이후 DB에서 조회
-- =====================================================

-- 한국어 번역 컬럼 추가
ALTER TABLE base_problems
ADD COLUMN IF NOT EXISTS question_ko TEXT;

-- 인덱스 추가 (NULL이 아닌 경우만 - 번역된 문제 빠른 조회)
CREATE INDEX IF NOT EXISTS idx_base_problems_question_ko_exists
ON base_problems(id)
WHERE question_ko IS NOT NULL;

-- 코멘트 추가
COMMENT ON COLUMN base_problems.question_ko IS '문제 설명 한국어 번역 (캐싱용)';
