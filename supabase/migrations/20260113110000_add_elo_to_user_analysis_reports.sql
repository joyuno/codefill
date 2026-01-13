-- =====================================================
-- 2단계: user_analysis_reports 테이블에 ELO 컬럼 추가
-- 날짜: 2026-01-13
-- 목적: 사용자 스킬을 ELO 레이팅 시스템으로 확장
-- =====================================================
--
-- 기존 skill_by_topic (0.0~1.0)은 유지
-- 신규 elo_by_topic (600~1600) 추가
--
-- ELO 레이팅 기준:
--   - 600: 매우 초보
--   - 800: 초보
--   - 1000: 중급 (기본값)
--   - 1200: 상급
--   - 1400+: 고수
-- =====================================================

-- =====================================================
-- 1. ELO 관련 컬럼 추가
-- =====================================================

-- 토픽별 ELO 레이팅
-- 예: {"DP": 1050, "그래프": 920, "정렬": 1150}
ALTER TABLE user_analysis_reports
ADD COLUMN IF NOT EXISTS elo_by_topic JSONB DEFAULT '{}';

-- 전체 ELO 레이팅 (토픽별 가중 평균)
ALTER TABLE user_analysis_reports
ADD COLUMN IF NOT EXISTS elo_overall INTEGER DEFAULT 1000;

-- 토픽별 문제 풀이 수 (신뢰도 지표)
-- 예: {"DP": 15, "그래프": 8}
ALTER TABLE user_analysis_reports
ADD COLUMN IF NOT EXISTS elo_problems_by_topic JSONB DEFAULT '{}';

-- ELO 변화 이력 (최근 20개)
-- 예: [{"date": "2026-01-13", "topic": "DP", "before": 1000, "after": 1015, "problem_elo": 1050}, ...]
ALTER TABLE user_analysis_reports
ADD COLUMN IF NOT EXISTS elo_history JSONB DEFAULT '[]';

-- K-factor 설정 (초보자는 높게, 숙련자는 낮게)
-- 기본 32, 50문제 후 24, 100문제 후 16
ALTER TABLE user_analysis_reports
ADD COLUMN IF NOT EXISTS elo_k_factor FLOAT DEFAULT 32;

-- =====================================================
-- 2. 기존 skill_by_topic 데이터를 ELO로 변환
-- =====================================================

-- 변환 공식: elo = 600 + (skill * 800)
-- skill 0.0 → elo 600
-- skill 0.5 → elo 1000
-- skill 1.0 → elo 1400
UPDATE user_analysis_reports
SET elo_by_topic = (
    SELECT COALESCE(
        jsonb_object_agg(
            key,
            ROUND(600 + (value::float * 800))::integer
        ),
        '{}'::jsonb
    )
    FROM jsonb_each_text(skill_by_topic)
)
WHERE skill_by_topic IS NOT NULL
  AND skill_by_topic != '{}'::jsonb
  AND (elo_by_topic IS NULL OR elo_by_topic = '{}'::jsonb);

-- =====================================================
-- 3. 전체 ELO 계산 (토픽별 평균)
-- =====================================================

UPDATE user_analysis_reports
SET elo_overall = (
    SELECT COALESCE(
        ROUND(AVG(value::integer)),
        1000
    )
    FROM jsonb_each_text(elo_by_topic)
)
WHERE elo_by_topic IS NOT NULL
  AND elo_by_topic != '{}'::jsonb;

-- =====================================================
-- 4. attempts 기반 토픽별 문제 수 계산
-- =====================================================

UPDATE user_analysis_reports uar
SET elo_problems_by_topic = subq.topic_counts
FROM (
    SELECT
        user_id,
        jsonb_object_agg(topic, cnt) AS topic_counts
    FROM (
        SELECT
            a.user_id,
            UNNEST(a.topics) AS topic,
            COUNT(*) AS cnt
        FROM attempts a
        WHERE a.topics IS NOT NULL AND array_length(a.topics, 1) > 0
        GROUP BY a.user_id, UNNEST(a.topics)
    ) topic_counts_raw
    GROUP BY user_id
) subq
WHERE uar.user_id = subq.user_id;

-- =====================================================
-- 5. K-factor 조정 (문제 풀이 수 기반)
-- =====================================================

UPDATE user_analysis_reports
SET elo_k_factor = CASE
    WHEN total_problems_attempted < 20 THEN 32   -- 초보: 빠른 변화
    WHEN total_problems_attempted < 50 THEN 28
    WHEN total_problems_attempted < 100 THEN 24
    WHEN total_problems_attempted < 200 THEN 20
    ELSE 16                                       -- 숙련자: 안정적
END
WHERE total_problems_attempted IS NOT NULL;

-- =====================================================
-- 6. 인덱스 추가
-- =====================================================

CREATE INDEX IF NOT EXISTS idx_user_analysis_reports_elo_overall
ON user_analysis_reports(elo_overall);

CREATE INDEX IF NOT EXISTS idx_user_analysis_reports_elo_by_topic
ON user_analysis_reports USING GIN(elo_by_topic);

-- =====================================================
-- 7. 컬럼 설명 추가
-- =====================================================

COMMENT ON COLUMN user_analysis_reports.elo_by_topic IS '토픽별 ELO 레이팅 (600~1600). {"DP": 1050, "그래프": 920}';
COMMENT ON COLUMN user_analysis_reports.elo_overall IS '전체 ELO 레이팅 (토픽별 가중 평균). 기본값 1000';
COMMENT ON COLUMN user_analysis_reports.elo_problems_by_topic IS '토픽별 풀이 문제 수 (ELO 신뢰도 지표)';
COMMENT ON COLUMN user_analysis_reports.elo_history IS 'ELO 변화 이력 (최근 20개). [{date, topic, before, after, problem_elo}]';
COMMENT ON COLUMN user_analysis_reports.elo_k_factor IS 'ELO K-factor (초보 32, 숙련 16). 변화 민감도';

-- =====================================================
-- 8. 사용자 ELO 업데이트 함수
-- =====================================================

CREATE OR REPLACE FUNCTION update_user_elo(
    p_user_id UUID,
    p_topic TEXT,
    p_problem_elo INTEGER,
    p_is_correct BOOLEAN,
    p_time_factor FLOAT DEFAULT 1.0,   -- 시간 보정 (빠르면 >1, 느리면 <1)
    p_hint_factor FLOAT DEFAULT 1.0    -- 힌트 보정 (힌트 없으면 1, 많으면 <1)
)
RETURNS TABLE (
    new_elo INTEGER,
    elo_change INTEGER,
    expected_probability FLOAT
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_current_elo INTEGER;
    v_k_factor FLOAT;
    v_expected FLOAT;
    v_actual FLOAT;
    v_change INTEGER;
    v_new_elo INTEGER;
    v_elo_by_topic JSONB;
    v_elo_history JSONB;
    v_problems_by_topic JSONB;
BEGIN
    -- 현재 사용자 데이터 조회
    SELECT
        COALESCE((elo_by_topic->>p_topic)::integer, 1000),
        COALESCE(elo_k_factor, 32),
        COALESCE(elo_by_topic, '{}'::jsonb),
        COALESCE(elo_history, '[]'::jsonb),
        COALESCE(elo_problems_by_topic, '{}'::jsonb)
    INTO v_current_elo, v_k_factor, v_elo_by_topic, v_elo_history, v_problems_by_topic
    FROM user_analysis_reports
    WHERE user_id = p_user_id;

    -- 새 사용자면 기본값 사용
    IF v_current_elo IS NULL THEN
        v_current_elo := 1000;
        v_k_factor := 32;
        v_elo_by_topic := '{}'::jsonb;
        v_elo_history := '[]'::jsonb;
        v_problems_by_topic := '{}'::jsonb;
    END IF;

    -- 예상 승률 계산
    v_expected := 1.0 / (1.0 + POWER(10, (p_problem_elo - v_current_elo)::FLOAT / 400.0));

    -- 실제 결과 (시간/힌트 보정 적용)
    IF p_is_correct THEN
        v_actual := LEAST(1.0, 1.0 * p_time_factor * p_hint_factor);
    ELSE
        v_actual := 0.0;
    END IF;

    -- ELO 변화량 계산
    v_change := ROUND(v_k_factor * (v_actual - v_expected))::INTEGER;
    v_new_elo := v_current_elo + v_change;

    -- 범위 제한 (600 ~ 1600)
    v_new_elo := GREATEST(600, LEAST(1600, v_new_elo));
    v_change := v_new_elo - v_current_elo;

    -- elo_by_topic 업데이트
    v_elo_by_topic := jsonb_set(v_elo_by_topic, ARRAY[p_topic], to_jsonb(v_new_elo));

    -- problems_by_topic 업데이트
    v_problems_by_topic := jsonb_set(
        v_problems_by_topic,
        ARRAY[p_topic],
        to_jsonb(COALESCE((v_problems_by_topic->>p_topic)::integer, 0) + 1)
    );

    -- 히스토리에 추가 (최근 20개 유지)
    v_elo_history := (
        SELECT jsonb_agg(elem)
        FROM (
            SELECT elem
            FROM (
                SELECT jsonb_build_object(
                    'date', CURRENT_DATE,
                    'topic', p_topic,
                    'before', v_current_elo,
                    'after', v_new_elo,
                    'change', v_change,
                    'problem_elo', p_problem_elo,
                    'expected', ROUND(v_expected::numeric, 3)
                ) AS elem
                UNION ALL
                SELECT elem FROM jsonb_array_elements(v_elo_history) AS elem
            ) all_elems
            LIMIT 20
        ) recent
    );

    -- DB 업데이트 (upsert)
    INSERT INTO user_analysis_reports (user_id, elo_by_topic, elo_problems_by_topic, elo_history, elo_overall)
    VALUES (
        p_user_id,
        v_elo_by_topic,
        v_problems_by_topic,
        v_elo_history,
        (SELECT ROUND(AVG(value::integer)) FROM jsonb_each_text(v_elo_by_topic))::integer
    )
    ON CONFLICT (user_id) DO UPDATE SET
        elo_by_topic = EXCLUDED.elo_by_topic,
        elo_problems_by_topic = EXCLUDED.elo_problems_by_topic,
        elo_history = EXCLUDED.elo_history,
        elo_overall = EXCLUDED.elo_overall,
        updated_at = NOW();

    -- 결과 반환
    RETURN QUERY SELECT v_new_elo, v_change, v_expected;
END;
$$;

-- 함수 권한 부여
GRANT EXECUTE ON FUNCTION update_user_elo(UUID, TEXT, INTEGER, BOOLEAN, FLOAT, FLOAT) TO service_role;

-- =====================================================
-- 9. ELO 랭킹 뷰
-- =====================================================

CREATE OR REPLACE VIEW user_elo_ranking AS
SELECT
    uar.user_id,
    u.name AS user_name,
    uar.elo_overall,
    uar.elo_by_topic,
    uar.total_problems_solved,
    uar.total_problems_attempted,
    RANK() OVER (ORDER BY uar.elo_overall DESC) AS overall_rank,
    uar.updated_at
FROM user_analysis_reports uar
JOIN users u ON uar.user_id = u.id
WHERE uar.elo_overall IS NOT NULL
ORDER BY uar.elo_overall DESC;

GRANT SELECT ON user_elo_ranking TO authenticated;
GRANT SELECT ON user_elo_ranking TO service_role;

-- =====================================================
-- 완료
-- =====================================================

DO $$
DECLARE
    v_total INTEGER;
    v_with_elo INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_total FROM user_analysis_reports;
    SELECT COUNT(*) INTO v_with_elo
    FROM user_analysis_reports
    WHERE elo_by_topic IS NOT NULL AND elo_by_topic != '{}'::jsonb;

    RAISE NOTICE '✅ 사용자 ELO 마이그레이션 완료';
    RAISE NOTICE '   - 전체 사용자 프로필: % 개', v_total;
    RAISE NOTICE '   - ELO 설정됨: % 개', v_with_elo;
END $$;
