-- =====================================================
-- CodeFill Database Migration: Add question_html column
-- HTML 형식의 문제 설명 컬럼 추가
-- =====================================================

-- question_html 컬럼 추가
ALTER TABLE base_problems
    ADD COLUMN IF NOT EXISTS question_html TEXT;

-- 코멘트 추가
COMMENT ON COLUMN base_problems.question_html IS 'HTML 형식의 문제 설명 (이미지 태그 포함)';

-- 인덱스는 필요없음 (전문 검색은 question에서)
