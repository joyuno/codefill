-- ============================================================
-- 피드백 결과 저장 및 활용 테이블
-- 피드백 에이전트의 상세 결과를 저장하여 다른 곳에서 활용
-- ============================================================

-- 1. attempts 테이블에 피드백 관련 컬럼 추가
ALTER TABLE attempts
ADD COLUMN IF NOT EXISTS feedback_grade VARCHAR(20),
ADD COLUMN IF NOT EXISTS feedback_data JSONB DEFAULT '{}',
ADD COLUMN IF NOT EXISTS difficulty_bonus INTEGER DEFAULT 0;

-- 2. 피드백 히스토리 테이블 (상세 피드백 저장)
CREATE TABLE IF NOT EXISTS feedback_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    attempt_id UUID REFERENCES attempts(id) ON DELETE CASCADE,
    problem_id UUID,

    -- 등급 정보
    grade VARCHAR(20) NOT NULL,       -- perfect, excellent, good, keep_going, learning
    grade_emoji VARCHAR(10),
    grade_message TEXT,

    -- 점수 (난이도별 차등 적용된)
    efficiency_score INTEGER,
    speed_score INTEGER,
    understanding_score INTEGER,
    difficulty_bonus INTEGER DEFAULT 0,
    avg_score INTEGER,                 -- (efficiency + speed + understanding) / 3

    -- 피드백 상세 (LLM 생성)
    summary_title TEXT,
    summary_highlight TEXT,
    learning_points JSONB DEFAULT '[]',    -- ["배운 점 1", "배운 점 2"]
    improvements JSONB DEFAULT '[]',       -- ["개선 제안 1", "개선 제안 2"]
    encouragement TEXT,

    -- 메타데이터
    problem_type VARCHAR(20),          -- blank, puzzle, guided
    difficulty VARCHAR(20),
    topics JSONB DEFAULT '[]',

    -- 타임스탬프
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. 학습 인사이트 집계 뷰 (피드백 활용)
CREATE OR REPLACE VIEW user_learning_insights AS
SELECT
    fh.user_id,
    -- 전체 통계
    COUNT(*) AS total_problems,
    COUNT(*) FILTER (WHERE fh.grade = 'perfect') AS perfect_count,
    COUNT(*) FILTER (WHERE fh.grade = 'excellent') AS excellent_count,
    COUNT(*) FILTER (WHERE fh.grade = 'good') AS good_count,
    COUNT(*) FILTER (WHERE fh.grade IN ('keep_going', 'learning')) AS needs_improvement_count,

    -- 평균 점수
    ROUND(AVG(fh.avg_score)::numeric, 1) AS avg_overall_score,
    ROUND(AVG(fh.efficiency_score)::numeric, 1) AS avg_efficiency,
    ROUND(AVG(fh.speed_score)::numeric, 1) AS avg_speed,
    ROUND(AVG(fh.understanding_score)::numeric, 1) AS avg_understanding,

    -- 난이도별 분포
    COUNT(*) FILTER (WHERE fh.difficulty = 'easy') AS easy_count,
    COUNT(*) FILTER (WHERE fh.difficulty = 'medium') AS medium_count,
    COUNT(*) FILTER (WHERE fh.difficulty = 'hard') AS hard_count,

    -- 문제 유형별 분포
    COUNT(*) FILTER (WHERE fh.problem_type = 'blank') AS blank_count,
    COUNT(*) FILTER (WHERE fh.problem_type = 'puzzle') AS puzzle_count,
    COUNT(*) FILTER (WHERE fh.problem_type = 'guided') AS guided_count,

    -- 최근 트렌드 (최근 10문제)
    (
        SELECT ROUND(AVG(sub.avg_score)::numeric, 1)
        FROM (
            SELECT avg_score
            FROM feedback_history
            WHERE user_id = fh.user_id
            ORDER BY created_at DESC
            LIMIT 10
        ) sub
    ) AS recent_avg_score
FROM feedback_history fh
GROUP BY fh.user_id;

-- 4. 개선 필요 영역 분석 함수
CREATE OR REPLACE FUNCTION get_improvement_areas(p_user_id UUID)
RETURNS TABLE (
    area VARCHAR,
    current_score FLOAT,
    suggestion TEXT
) AS $$
BEGIN
    RETURN QUERY
    WITH user_scores AS (
        SELECT
            AVG(efficiency_score) AS avg_efficiency,
            AVG(speed_score) AS avg_speed,
            AVG(understanding_score) AS avg_understanding
        FROM feedback_history
        WHERE user_id = p_user_id
        AND created_at > NOW() - INTERVAL '30 days'
    )
    SELECT
        area_name::varchar,
        score::float,
        advice::text
    FROM (
        SELECT 'efficiency' AS area_name, avg_efficiency AS score,
            CASE
                WHEN avg_efficiency < 50 THEN '힌트 사용을 줄이고 스스로 생각하는 시간을 가져보세요'
                WHEN avg_efficiency < 70 THEN '힌트는 마지막 수단으로 사용해보세요'
                ELSE '효율적으로 문제를 풀고 있어요!'
            END AS advice
        FROM user_scores
        UNION ALL
        SELECT 'speed', avg_speed,
            CASE
                WHEN avg_speed < 50 THEN '시간 제한을 두고 연습해보세요'
                WHEN avg_speed < 70 THEN '자주 사용하는 패턴을 암기하면 속도가 빨라져요'
                ELSE '빠른 문제 해결 능력을 가지고 있어요!'
            END
        FROM user_scores
        UNION ALL
        SELECT 'understanding', avg_understanding,
            CASE
                WHEN avg_understanding < 50 THEN '개념 복습 후 다시 도전해보세요'
                WHEN avg_understanding < 70 THEN '비슷한 유형의 문제를 더 풀어보세요'
                ELSE '개념을 잘 이해하고 있어요!'
            END
        FROM user_scores
    ) areas
    WHERE score < 70
    ORDER BY score ASC;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 5. 주간 학습 리포트 함수
CREATE OR REPLACE FUNCTION get_weekly_learning_report(p_user_id UUID)
RETURNS TABLE (
    week_start DATE,
    problems_solved INTEGER,
    avg_score FLOAT,
    perfect_rate FLOAT,
    most_practiced_topic TEXT,
    improvement_trend FLOAT
) AS $$
BEGIN
    RETURN QUERY
    WITH weekly_data AS (
        SELECT
            DATE_TRUNC('week', created_at)::date AS week_start,
            COUNT(*) AS problems_solved,
            AVG(avg_score) AS avg_score,
            COUNT(*) FILTER (WHERE grade = 'perfect')::float / NULLIF(COUNT(*), 0) AS perfect_rate,
            MODE() WITHIN GROUP (ORDER BY topics->0) AS most_practiced_topic
        FROM feedback_history
        WHERE user_id = p_user_id
        AND created_at > NOW() - INTERVAL '8 weeks'
        GROUP BY DATE_TRUNC('week', created_at)
    ),
    with_trend AS (
        SELECT
            *,
            avg_score - LAG(avg_score) OVER (ORDER BY week_start) AS improvement
        FROM weekly_data
    )
    SELECT
        week_start,
        problems_solved::integer,
        ROUND(avg_score::numeric, 1)::float,
        ROUND(perfect_rate::numeric, 2)::float,
        most_practiced_topic::text,
        COALESCE(ROUND(improvement::numeric, 1), 0)::float
    FROM with_trend
    ORDER BY week_start DESC
    LIMIT 8;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 인덱스
CREATE INDEX IF NOT EXISTS feedback_history_user_idx ON feedback_history(user_id);
CREATE INDEX IF NOT EXISTS feedback_history_attempt_idx ON feedback_history(attempt_id);
CREATE INDEX IF NOT EXISTS feedback_history_grade_idx ON feedback_history(grade);
CREATE INDEX IF NOT EXISTS feedback_history_created_idx ON feedback_history(created_at DESC);
CREATE INDEX IF NOT EXISTS feedback_history_difficulty_idx ON feedback_history(difficulty);

-- RLS 정책
ALTER TABLE feedback_history ENABLE ROW LEVEL SECURITY;

DO $$ BEGIN
    CREATE POLICY "Users can view own feedback"
        ON feedback_history FOR SELECT TO authenticated USING (user_id = auth.uid());
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE POLICY "Service role full access to feedback"
        ON feedback_history FOR ALL TO service_role USING (true);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- 권한 부여
GRANT SELECT ON feedback_history TO authenticated;
GRANT ALL ON feedback_history TO service_role;
GRANT SELECT ON user_learning_insights TO authenticated;
GRANT EXECUTE ON FUNCTION get_improvement_areas(UUID) TO authenticated;
GRANT EXECUTE ON FUNCTION get_improvement_areas(UUID) TO service_role;
GRANT EXECUTE ON FUNCTION get_weekly_learning_report(UUID) TO authenticated;
GRANT EXECUTE ON FUNCTION get_weekly_learning_report(UUID) TO service_role;

DO $$ BEGIN RAISE NOTICE 'Feedback storage tables and functions created successfully'; END $$;
