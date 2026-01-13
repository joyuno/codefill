-- =====================================================
-- 1단계: base_problems 테이블에 ELO 레이팅 시스템 추가
-- 날짜: 2026-01-13
-- 목적: 문제 난이도를 ELO 레이팅으로 수치화
-- =====================================================
--
-- ELO 레이팅 기준:
--   - easy: 800
--   - medium: 1000
--   - medium_hard: 1150
--   - hard: 1300
--   - very_hard: 1500
--
-- 기존 difficulty 컬럼은 유지 (UI 표시용)
-- =====================================================

-- =====================================================
-- 1. ELO 관련 컬럼 추가
-- =====================================================

-- 문제 ELO 레이팅 (기본값 1000 = medium 수준)
ALTER TABLE base_problems
ADD COLUMN IF NOT EXISTS elo_rating INTEGER DEFAULT 1000;

-- 문제 정답률 (0.0~1.0, ELO 보정 및 통계용)
ALTER TABLE base_problems
ADD COLUMN IF NOT EXISTS success_rate FLOAT;

-- 평균 풀이 시간 (초 단위, 통계용)
ALTER TABLE base_problems
ADD COLUMN IF NOT EXISTS avg_solve_time_seconds INTEGER;

-- ELO 레이팅 업데이트 횟수 (신뢰도 측정용)
ALTER TABLE base_problems
ADD COLUMN IF NOT EXISTS elo_update_count INTEGER DEFAULT 0;

-- =====================================================
-- 2. 기존 difficulty 기반 초기 ELO 설정
-- =====================================================

UPDATE base_problems
SET elo_rating = CASE LOWER(difficulty)
    WHEN 'easy' THEN 800
    WHEN 'medium' THEN 1000
    WHEN 'medium_hard' THEN 1150
    WHEN 'hard' THEN 1300
    WHEN 'very_hard' THEN 1500
    ELSE 1000  -- 기본값
END
WHERE elo_rating IS NULL OR elo_rating = 1000;

-- =====================================================
-- 3. 기존 풀이 데이터 기반 success_rate 계산
-- =====================================================

-- attempts 테이블에서 문제별 정답률 계산하여 업데이트
UPDATE base_problems bp
SET
    success_rate = subq.rate,
    avg_solve_time_seconds = subq.avg_time
FROM (
    SELECT
        base_problem_id,
        CASE
            WHEN COUNT(*) > 0 THEN
                ROUND(COUNT(*) FILTER (WHERE is_correct = true)::numeric / COUNT(*)::numeric, 3)
            ELSE NULL
        END AS rate,
        ROUND(AVG(time_spent) FILTER (WHERE time_spent > 0 AND time_spent < 7200))::integer AS avg_time
    FROM attempts
    WHERE base_problem_id IS NOT NULL
    GROUP BY base_problem_id
    HAVING COUNT(*) >= 3  -- 최소 3회 이상 시도된 문제만
) subq
WHERE bp.id = subq.base_problem_id;

-- =====================================================
-- 4. 정답률 기반 ELO 미세 조정 (선택적)
-- =====================================================

-- 정답률이 매우 높은 문제는 ELO 하향 조정
UPDATE base_problems
SET elo_rating = GREATEST(600, elo_rating - 100)
WHERE success_rate > 0.85 AND success_rate IS NOT NULL;

-- 정답률이 매우 낮은 문제는 ELO 상향 조정
UPDATE base_problems
SET elo_rating = LEAST(1600, elo_rating + 100)
WHERE success_rate < 0.25 AND success_rate IS NOT NULL;

-- =====================================================
-- 5. 인덱스 추가
-- =====================================================

CREATE INDEX IF NOT EXISTS idx_base_problems_elo_rating
ON base_problems(elo_rating);

CREATE INDEX IF NOT EXISTS idx_base_problems_success_rate
ON base_problems(success_rate)
WHERE success_rate IS NOT NULL;

-- =====================================================
-- 6. 컬럼 설명 추가
-- =====================================================

COMMENT ON COLUMN base_problems.elo_rating IS 'ELO 레이팅 (600~1600, 기본 1000). easy=800, medium=1000, hard=1300, very_hard=1500';
COMMENT ON COLUMN base_problems.success_rate IS '문제 정답률 (0.0~1.0). attempts 테이블 기반 계산';
COMMENT ON COLUMN base_problems.avg_solve_time_seconds IS '평균 풀이 시간 (초). 정답자 기준';
COMMENT ON COLUMN base_problems.elo_update_count IS 'ELO 레이팅 업데이트 횟수 (신뢰도 지표)';

-- =====================================================
-- 7. ELO 업데이트 함수 (문제 레이팅 동적 조정용)
-- =====================================================

CREATE OR REPLACE FUNCTION update_problem_elo(
    p_problem_id UUID,
    p_user_elo INTEGER,
    p_is_correct BOOLEAN,
    p_k_factor FLOAT DEFAULT 4.0  -- 문제는 천천히 변화
)
RETURNS INTEGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_current_elo INTEGER;
    v_expected FLOAT;
    v_actual FLOAT;
    v_new_elo INTEGER;
BEGIN
    -- 현재 문제 ELO 조회
    SELECT elo_rating INTO v_current_elo
    FROM base_problems
    WHERE id = p_problem_id;

    IF v_current_elo IS NULL THEN
        RETURN NULL;
    END IF;

    -- 예상 결과 계산 (문제 관점: 사용자가 틀릴 확률)
    -- 문제가 어려울수록(높은 ELO) 사용자가 틀릴 확률 높음
    v_expected := 1.0 / (1.0 + POWER(10, (p_user_elo - v_current_elo)::FLOAT / 400.0));

    -- 실제 결과 (문제 관점: 사용자가 틀렸으면 1, 맞췄으면 0)
    v_actual := CASE WHEN p_is_correct THEN 0.0 ELSE 1.0 END;

    -- ELO 업데이트
    v_new_elo := v_current_elo + ROUND(p_k_factor * (v_actual - v_expected))::INTEGER;

    -- 범위 제한 (600 ~ 1600)
    v_new_elo := GREATEST(600, LEAST(1600, v_new_elo));

    -- 업데이트
    UPDATE base_problems
    SET
        elo_rating = v_new_elo,
        elo_update_count = COALESCE(elo_update_count, 0) + 1,
        updated_at = NOW()
    WHERE id = p_problem_id;

    RETURN v_new_elo;
END;
$$;

-- 함수 권한 부여
GRANT EXECUTE ON FUNCTION update_problem_elo(UUID, INTEGER, BOOLEAN, FLOAT) TO service_role;

-- =====================================================
-- 8. 난이도별 ELO 통계 뷰
-- =====================================================

CREATE OR REPLACE VIEW problem_elo_stats AS
SELECT
    difficulty,
    COUNT(*) AS problem_count,
    ROUND(AVG(elo_rating)) AS avg_elo,
    MIN(elo_rating) AS min_elo,
    MAX(elo_rating) AS max_elo,
    ROUND(AVG(success_rate)::numeric, 3) AS avg_success_rate,
    ROUND(AVG(avg_solve_time_seconds)) AS avg_solve_time
FROM base_problems
GROUP BY difficulty
ORDER BY avg_elo;

GRANT SELECT ON problem_elo_stats TO authenticated;
GRANT SELECT ON problem_elo_stats TO service_role;

-- =====================================================
-- 완료
-- =====================================================

DO $$
DECLARE
    v_total INTEGER;
    v_with_elo INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_total FROM base_problems;
    SELECT COUNT(*) INTO v_with_elo FROM base_problems WHERE elo_rating IS NOT NULL;

    RAISE NOTICE '✅ ELO 레이팅 마이그레이션 완료';
    RAISE NOTICE '   - 전체 문제: % 개', v_total;
    RAISE NOTICE '   - ELO 설정됨: % 개', v_with_elo;
END $$;
