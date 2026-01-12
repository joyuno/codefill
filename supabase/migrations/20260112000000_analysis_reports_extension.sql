-- =====================================================
-- Analysis Reports Extension Migration
-- 약점 분석 리포트에 추가 데이터 컬럼 확장
-- =====================================================

-- user_analysis_reports 테이블 확장
ALTER TABLE user_analysis_reports
ADD COLUMN IF NOT EXISTS concepts_struggling TEXT[] DEFAULT '{}',
ADD COLUMN IF NOT EXISTS concepts_learned TEXT[] DEFAULT '{}',
ADD COLUMN IF NOT EXISTS hint_usage JSONB DEFAULT '{}',
ADD COLUMN IF NOT EXISTS learning_style JSONB DEFAULT '{}',
ADD COLUMN IF NOT EXISTS common_error_patterns JSONB DEFAULT '{}',
ADD COLUMN IF NOT EXISTS mood_distribution JSONB DEFAULT '{}',
ADD COLUMN IF NOT EXISTS breakthrough_moments TEXT[] DEFAULT '{}',
ADD COLUMN IF NOT EXISTS teaching_notes TEXT[] DEFAULT '{}';

-- 컬럼 설명 추가
COMMENT ON COLUMN user_analysis_reports.concepts_struggling IS '어려워한 개념 목록 (user_memories에서 집계)';
COMMENT ON COLUMN user_analysis_reports.concepts_learned IS '이해한 개념 목록 (user_memories에서 집계)';
COMMENT ON COLUMN user_analysis_reports.hint_usage IS '힌트 사용 패턴 {total_requested, helpful_count, helpful_rate, avg_hint_level}';
COMMENT ON COLUMN user_analysis_reports.learning_style IS '학습 스타일 {prefers_examples, prefers_analogies, hint_sensitivity, pace}';
COMMENT ON COLUMN user_analysis_reports.common_error_patterns IS '자주 하는 실수 패턴';
COMMENT ON COLUMN user_analysis_reports.mood_distribution IS '학습 중 감정 분포 {curious: 5, frustrated: 2, confident: 3}';
COMMENT ON COLUMN user_analysis_reports.breakthrough_moments IS '돌파 순간 목록 (깨달음 순간)';
COMMENT ON COLUMN user_analysis_reports.teaching_notes IS '효과적이었던 교육 노트';

-- 인덱스 추가 (JSONB 검색 최적화)
CREATE INDEX IF NOT EXISTS idx_analysis_reports_hint_usage ON user_analysis_reports USING GIN (hint_usage);
CREATE INDEX IF NOT EXISTS idx_analysis_reports_learning_style ON user_analysis_reports USING GIN (learning_style);
