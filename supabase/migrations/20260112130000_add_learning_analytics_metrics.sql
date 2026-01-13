-- =====================================================
-- Add learning analytics metrics columns to user_analysis_reports
-- BKT (Bayesian Knowledge Tracing), Bloom's Taxonomy, SRK Error Analysis
-- =====================================================

-- BKT 마스터리 데이터 (토픽별 마스터리 확률)
ALTER TABLE user_analysis_reports
ADD COLUMN IF NOT EXISTS bkt_mastery JSONB DEFAULT '{}';

-- Bloom's Taxonomy 메트릭 (난이도별 달성률 및 현재 레벨)
ALTER TABLE user_analysis_reports
ADD COLUMN IF NOT EXISTS bloom_metrics JSONB DEFAULT '{}';

-- SRK 에러 분석 (Skill/Rule/Knowledge 에러 패턴)
ALTER TABLE user_analysis_reports
ADD COLUMN IF NOT EXISTS error_analysis JSONB DEFAULT '{}';

-- 컬럼 설명 추가
COMMENT ON COLUMN user_analysis_reports.bkt_mastery IS 'BKT (Bayesian Knowledge Tracing) 토픽별 마스터리 확률 (0.0~1.0, 80%=마스터)';
COMMENT ON COLUMN user_analysis_reports.bloom_metrics IS 'Bloom Taxonomy 메트릭 (Apply/Analyze/Create 달성률 및 현재 레벨)';
COMMENT ON COLUMN user_analysis_reports.error_analysis IS 'SRK 에러 패턴 분석 (Skill:오타, Rule:경계값, Knowledge:개념부족)';
