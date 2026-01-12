-- =====================================================
-- Add detailed_feedback column to user_analysis_reports
-- AI 코칭 피드백을 저장하기 위한 컬럼 추가
-- =====================================================

-- user_analysis_reports 테이블에 detailed_feedback 컬럼 추가
ALTER TABLE user_analysis_reports
ADD COLUMN IF NOT EXISTS detailed_feedback TEXT;

-- 컬럼 설명 추가
COMMENT ON COLUMN user_analysis_reports.detailed_feedback IS 'AI 코칭 피드백 (마크다운 형식의 상세 분석)';
