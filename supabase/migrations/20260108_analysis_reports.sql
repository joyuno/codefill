-- =====================================================
-- Analysis Reports Table
-- AI 분석 결과 저장 (사용자당 1개, 최신 분석만 유지)
-- =====================================================

CREATE TABLE IF NOT EXISTS user_analysis_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- AI 분석 결과
    summary_text TEXT,                    -- "DP와 그래프 영역에서..."
    strengths JSONB DEFAULT '[]',         -- [{"topic": "Array", "score": 0.92}, ...]
    weaknesses JSONB DEFAULT '[]',        -- [{"topic": "DP", "score": 0.32}, ...]
    recommendations TEXT[],               -- ["하루 3문제씩...", ...]
    study_plan TEXT,                      -- "추천 학습 경로: DP → Graph → Tree"

    -- 분석 시점의 스냅샷
    skill_snapshot JSONB,                 -- skill_by_topic 스냅샷
    stats_snapshot JSONB,                 -- {level, problems_solved, accuracy, streak}
    difficulty_snapshot JSONB,            -- success_rate_by_difficulty 스냅샷

    -- 추천 문제 (분석 시점 기준)
    recommended_problems JSONB DEFAULT '[]',  -- [{id, name, topic, reason}, ...]

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT unique_user_analysis UNIQUE(user_id)
);

-- Index for fast user lookup
CREATE INDEX IF NOT EXISTS idx_analysis_reports_user ON user_analysis_reports(user_id);

-- Grant permissions (백엔드 service_role용)
GRANT ALL ON user_analysis_reports TO service_role;

-- RLS Policies
ALTER TABLE user_analysis_reports ENABLE ROW LEVEL SECURITY;

-- Users can read their own analysis
CREATE POLICY "Users can view own analysis"
    ON user_analysis_reports FOR SELECT
    USING (auth.uid() = user_id);

-- Users can insert their own analysis
CREATE POLICY "Users can insert own analysis"
    ON user_analysis_reports FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Users can update their own analysis
CREATE POLICY "Users can update own analysis"
    ON user_analysis_reports FOR UPDATE
    USING (auth.uid() = user_id);

-- Service role has full access
CREATE POLICY "Service role full access"
    ON user_analysis_reports FOR ALL
    USING (auth.role() = 'service_role');

-- Updated_at trigger
CREATE OR REPLACE FUNCTION update_analysis_reports_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_analysis_reports_updated_at
    BEFORE UPDATE ON user_analysis_reports
    FOR EACH ROW
    EXECUTE FUNCTION update_analysis_reports_updated_at();
