-- =====================================================
-- Daily Missions & Weekly Challenges System
-- 통일 미션 시스템 (모든 사용자 동일한 미션)
-- 2026-01-09
-- =====================================================

-- =====================================================
-- 1. 테이블 생성
-- =====================================================

-- 1-1. 미션 정의 (마스터 데이터)
CREATE TABLE IF NOT EXISTS missions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    mission_type VARCHAR(20) NOT NULL,     -- 'daily', 'weekly'
    condition_type VARCHAR(30) NOT NULL,   -- 'problems', 'blank', 'puzzle', 'output', 'bug', 'refactor'
    condition_value INT NOT NULL,          -- 목표 수치
    difficulty VARCHAR(10),                -- NULL=모든 난이도, 'easy', 'medium', 'hard'
    reward_gold INT DEFAULT 0,
    reward_xp INT DEFAULT 0,
    reward_seeds JSONB,                    -- {"seed_carrot": 2}
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 1-2. 날짜별 통일 미션 스케줄
CREATE TABLE IF NOT EXISTS mission_schedule (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    schedule_date DATE NOT NULL,           -- 일일: 해당 날짜, 주간: 월요일
    mission_type VARCHAR(20) NOT NULL,     -- 'daily', 'weekly'
    mission_id UUID NOT NULL REFERENCES missions(id) ON DELETE CASCADE,
    slot_number INT NOT NULL,              -- 순서 (1, 2, 3)
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(schedule_date, mission_type, slot_number)
);

-- 1-3. 사용자별 미션 진행 상황
CREATE TABLE IF NOT EXISTS user_mission_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    schedule_id UUID NOT NULL REFERENCES mission_schedule(id) ON DELETE CASCADE,
    current_progress INT DEFAULT 0,
    status VARCHAR(20) DEFAULT 'active',   -- 'active', 'completed', 'claimed'
    completed_at TIMESTAMPTZ,
    claimed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, schedule_id)
);

-- =====================================================
-- 2. 인덱스
-- =====================================================
CREATE INDEX IF NOT EXISTS idx_missions_type_active ON missions(mission_type, is_active);
CREATE INDEX IF NOT EXISTS idx_schedule_date_type ON mission_schedule(schedule_date, mission_type);
CREATE INDEX IF NOT EXISTS idx_progress_user ON user_mission_progress(user_id);
CREATE INDEX IF NOT EXISTS idx_progress_status ON user_mission_progress(status);

-- =====================================================
-- 3. RLS 설정
-- =====================================================
ALTER TABLE missions ENABLE ROW LEVEL SECURITY;
ALTER TABLE mission_schedule ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_mission_progress ENABLE ROW LEVEL SECURITY;

-- missions: 모두 읽기 가능
CREATE POLICY "missions_select" ON missions FOR SELECT USING (true);
CREATE POLICY "missions_service" ON missions FOR ALL USING (auth.role() = 'service_role');

-- mission_schedule: 모두 읽기 가능
CREATE POLICY "schedule_select" ON mission_schedule FOR SELECT USING (true);
CREATE POLICY "schedule_service" ON mission_schedule FOR ALL USING (auth.role() = 'service_role');

-- user_mission_progress: 본인만
CREATE POLICY "progress_select" ON user_mission_progress FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "progress_insert" ON user_mission_progress FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "progress_update" ON user_mission_progress FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "progress_service" ON user_mission_progress FOR ALL USING (auth.role() = 'service_role');

-- =====================================================
-- 4. 권한 부여
-- =====================================================
GRANT SELECT ON missions TO anon, authenticated;
GRANT ALL ON missions TO service_role;

GRANT SELECT ON mission_schedule TO anon, authenticated;
GRANT ALL ON mission_schedule TO service_role;

GRANT SELECT, INSERT, UPDATE ON user_mission_progress TO authenticated;
GRANT ALL ON user_mission_progress TO service_role;

-- =====================================================
-- 5. 시드 데이터
-- =====================================================

-- 일일 미션 (13개)
INSERT INTO missions (code, name, description, mission_type, condition_type, condition_value, difficulty, reward_gold, reward_xp, reward_seeds)
VALUES
    ('daily_solve_3', '3문제 풀기', '오늘 문제 3개 풀기', 'daily', 'problems', 3, NULL, 50, 30, NULL),
    ('daily_solve_5', '5문제 풀기', '오늘 문제 5개 풀기', 'daily', 'problems', 5, NULL, 100, 50, '{"seed_carrot": 2}'),
    ('daily_solve_10', '10문제 풀기', '오늘 문제 10개 풀기', 'daily', 'problems', 10, NULL, 200, 100, '{"seed_tomato": 1, "seed_carrot": 2}'),
    ('daily_blank_2', '빈칸 채우기 2문제', '빈칸 채우기 문제 2개 풀기', 'daily', 'blank', 2, NULL, 40, 25, NULL),
    ('daily_blank_5', '빈칸 마스터', '빈칸 채우기 문제 5개 풀기', 'daily', 'blank', 5, NULL, 100, 60, '{"seed_carrot": 1}'),
    ('daily_output_2', '출력 예측 2문제', '출력 예측 문제 2개 풀기', 'daily', 'output', 2, NULL, 40, 25, NULL),
    ('daily_bug_2', '버그 헌터', '버그 찾기 문제 2개 풀기', 'daily', 'bug', 2, NULL, 50, 30, NULL),
    ('daily_puzzle_2', '퍼즐 마스터', '코드 퍼즐 2개 풀기', 'daily', 'puzzle', 2, NULL, 50, 30, NULL),
    ('daily_refactor_2', '리팩토링 프로', '리팩토링 문제 2개 풀기', 'daily', 'refactor', 2, NULL, 60, 35, NULL),
    ('daily_easy_5', '쉬운 문제 5개', '쉬운 난이도 문제 5개 풀기', 'daily', 'problems', 5, 'easy', 60, 30, NULL),
    ('daily_medium_3', '중간 난이도 도전', '중간 난이도 문제 3개 풀기', 'daily', 'problems', 3, 'medium', 80, 50, '{"seed_carrot": 1}'),
    ('daily_hard_1', '어려운 문제 도전', '어려운 문제 1개 풀기', 'daily', 'problems', 1, 'hard', 100, 60, '{"seed_tomato": 1}'),
    ('daily_hard_3', '하드코어', '어려운 문제 3개 풀기', 'daily', 'problems', 3, 'hard', 250, 150, '{"seed_tomato": 2, "seed_strawberry": 1}')
ON CONFLICT (code) DO NOTHING;

-- 주간 챌린지 (6개)
INSERT INTO missions (code, name, description, mission_type, condition_type, condition_value, difficulty, reward_gold, reward_xp, reward_seeds)
VALUES
    ('weekly_solve_20', '주간 전사', '이번 주 문제 20개 풀기', 'weekly', 'problems', 20, NULL, 300, 200, '{"seed_carrot": 5}'),
    ('weekly_solve_50', '주간 챔피언', '이번 주 문제 50개 풀기', 'weekly', 'problems', 50, NULL, 800, 500, '{"seed_tomato": 3, "seed_strawberry": 2}'),
    ('weekly_blank_10', '빈칸 주간', '이번 주 빈칸 문제 10개 풀기', 'weekly', 'blank', 10, NULL, 250, 150, '{"seed_carrot": 3}'),
    ('weekly_bug_10', '버그 사냥 주간', '이번 주 버그 찾기 10개 풀기', 'weekly', 'bug', 10, NULL, 300, 180, '{"seed_tomato": 2}'),
    ('weekly_hard_5', '하드코어 주간', '이번 주 어려운 문제 5개 풀기', 'weekly', 'problems', 5, 'hard', 400, 250, '{"seed_strawberry": 2}'),
    ('weekly_medium_15', '균형 잡힌 주간', '이번 주 중간 문제 15개 풀기', 'weekly', 'problems', 15, 'medium', 350, 200, '{"seed_tomato": 2, "seed_carrot": 3}')
ON CONFLICT (code) DO NOTHING;

-- =====================================================
-- 6. RPC 함수
-- =====================================================

-- 6-1. 일일 미션 조회 (스케줄 자동 생성 + 사용자 진행 자동 생성)
CREATE OR REPLACE FUNCTION get_daily_missions(p_user_id UUID)
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_today DATE := CURRENT_DATE;
    v_result JSONB;
BEGIN
    -- 1. 오늘 스케줄이 없으면 생성 (INSERT ... SELECT ... ON CONFLICT)
    INSERT INTO mission_schedule (schedule_date, mission_type, mission_id, slot_number)
    SELECT v_today, 'daily', id, rn
    FROM (
        SELECT id, ROW_NUMBER() OVER (ORDER BY RANDOM()) as rn
        FROM missions
        WHERE mission_type = 'daily' AND is_active = true
        LIMIT 3
    ) sub
    ON CONFLICT (schedule_date, mission_type, slot_number) DO NOTHING;

    -- 2. 사용자 진행 상황 없으면 생성
    INSERT INTO user_mission_progress (user_id, schedule_id)
    SELECT p_user_id, ms.id
    FROM mission_schedule ms
    WHERE ms.schedule_date = v_today AND ms.mission_type = 'daily'
    ON CONFLICT (user_id, schedule_id) DO NOTHING;

    -- 3. 결과 조회
    SELECT COALESCE(jsonb_agg(
        jsonb_build_object(
            'id', ump.id,
            'mission_id', m.id,
            'code', m.code,
            'name', m.name,
            'description', m.description,
            'condition_type', m.condition_type,
            'condition_value', m.condition_value,
            'difficulty', m.difficulty,
            'current_progress', ump.current_progress,
            'target_value', m.condition_value,
            'status', ump.status,
            'reward_gold', m.reward_gold,
            'reward_xp', m.reward_xp,
            'reward_seeds', m.reward_seeds
        ) ORDER BY ms.slot_number
    ), '[]'::JSONB)
    INTO v_result
    FROM user_mission_progress ump
    JOIN mission_schedule ms ON ump.schedule_id = ms.id
    JOIN missions m ON ms.mission_id = m.id
    WHERE ump.user_id = p_user_id
      AND ms.schedule_date = v_today
      AND ms.mission_type = 'daily';

    RETURN v_result;
END;
$$;

-- 6-2. 주간 챌린지 조회
CREATE OR REPLACE FUNCTION get_weekly_challenges(p_user_id UUID)
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_week_start DATE := date_trunc('week', CURRENT_DATE)::DATE;
    v_result JSONB;
BEGIN
    -- 1. 이번 주 스케줄이 없으면 생성
    INSERT INTO mission_schedule (schedule_date, mission_type, mission_id, slot_number)
    SELECT v_week_start, 'weekly', id, rn
    FROM (
        SELECT id, ROW_NUMBER() OVER (ORDER BY RANDOM()) as rn
        FROM missions
        WHERE mission_type = 'weekly' AND is_active = true
        LIMIT 2
    ) sub
    ON CONFLICT (schedule_date, mission_type, slot_number) DO NOTHING;

    -- 2. 사용자 진행 상황 없으면 생성
    INSERT INTO user_mission_progress (user_id, schedule_id)
    SELECT p_user_id, ms.id
    FROM mission_schedule ms
    WHERE ms.schedule_date = v_week_start AND ms.mission_type = 'weekly'
    ON CONFLICT (user_id, schedule_id) DO NOTHING;

    -- 3. 결과 조회
    SELECT COALESCE(jsonb_agg(
        jsonb_build_object(
            'id', ump.id,
            'mission_id', m.id,
            'code', m.code,
            'name', m.name,
            'description', m.description,
            'condition_type', m.condition_type,
            'condition_value', m.condition_value,
            'difficulty', m.difficulty,
            'current_progress', ump.current_progress,
            'target_value', m.condition_value,
            'status', ump.status,
            'reward_gold', m.reward_gold,
            'reward_xp', m.reward_xp,
            'reward_seeds', m.reward_seeds
        ) ORDER BY ms.slot_number
    ), '[]'::JSONB)
    INTO v_result
    FROM user_mission_progress ump
    JOIN mission_schedule ms ON ump.schedule_id = ms.id
    JOIN missions m ON ms.mission_id = m.id
    WHERE ump.user_id = p_user_id
      AND ms.schedule_date = v_week_start
      AND ms.mission_type = 'weekly';

    RETURN v_result;
END;
$$;

-- 6-3. 미션 진행률 업데이트 (문제 풀이 시 호출)
CREATE OR REPLACE FUNCTION update_mission_progress(
    p_user_id UUID,
    p_condition_type VARCHAR(30),
    p_difficulty VARCHAR(10) DEFAULT NULL,
    p_increment INT DEFAULT 1
)
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_today DATE := CURRENT_DATE;
    v_week_start DATE := date_trunc('week', CURRENT_DATE)::DATE;
    v_updated JSONB := '[]'::JSONB;
    v_row RECORD;
BEGIN
    -- 일일 미션 + 주간 챌린지 모두 업데이트
    FOR v_row IN
        UPDATE user_mission_progress ump
        SET
            current_progress = LEAST(ump.current_progress + p_increment, m.condition_value),
            status = CASE
                WHEN ump.current_progress + p_increment >= m.condition_value THEN 'completed'
                ELSE ump.status
            END,
            completed_at = CASE
                WHEN ump.current_progress + p_increment >= m.condition_value AND ump.status = 'active' THEN NOW()
                ELSE ump.completed_at
            END
        FROM mission_schedule ms
        JOIN missions m ON ms.mission_id = m.id
        WHERE ump.schedule_id = ms.id
          AND ump.user_id = p_user_id
          AND ump.status = 'active'
          AND m.condition_type = p_condition_type
          AND (m.difficulty IS NULL OR m.difficulty = p_difficulty)
          AND (
              (ms.mission_type = 'daily' AND ms.schedule_date = v_today)
              OR (ms.mission_type = 'weekly' AND ms.schedule_date = v_week_start)
          )
        RETURNING ump.id, ump.current_progress, m.condition_value as target, ump.status
    LOOP
        v_updated := v_updated || jsonb_build_object(
            'id', v_row.id,
            'progress', v_row.current_progress,
            'target', v_row.target,
            'completed', v_row.status = 'completed'
        );
    END LOOP;

    RETURN v_updated;
END;
$$;

-- 6-4. 미션 보상 수령
DROP FUNCTION IF EXISTS claim_mission_reward(UUID, UUID);
CREATE OR REPLACE FUNCTION claim_mission_reward(p_user_id UUID, p_progress_id UUID)
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_mission RECORD;
    v_new_gold INT;
    v_seed_key TEXT;
    v_seed_amount INT;
BEGIN
    -- 미션 정보 조회 + 상태 확인
    SELECT m.reward_gold, m.reward_xp, m.reward_seeds, ump.status
    INTO v_mission
    FROM user_mission_progress ump
    JOIN mission_schedule ms ON ump.schedule_id = ms.id
    JOIN missions m ON ms.mission_id = m.id
    WHERE ump.id = p_progress_id AND ump.user_id = p_user_id;

    IF NOT FOUND THEN
        RETURN jsonb_build_object('success', false, 'error', '미션을 찾을 수 없습니다');
    END IF;

    IF v_mission.status != 'completed' THEN
        RETURN jsonb_build_object('success', false, 'error', '아직 완료되지 않은 미션입니다');
    END IF;

    -- 상태 변경
    UPDATE user_mission_progress
    SET status = 'claimed', claimed_at = NOW()
    WHERE id = p_progress_id;

    -- 골드 지급
    IF v_mission.reward_gold > 0 THEN
        UPDATE user_farm SET gold = gold + v_mission.reward_gold WHERE user_id = p_user_id;
    END IF;

    -- XP 지급
    IF v_mission.reward_xp > 0 THEN
        UPDATE user_stats SET total_xp = total_xp + v_mission.reward_xp WHERE user_id = p_user_id;
    END IF;

    -- 씨앗 지급
    IF v_mission.reward_seeds IS NOT NULL THEN
        FOR v_seed_key, v_seed_amount IN SELECT * FROM jsonb_each_text(v_mission.reward_seeds)
        LOOP
            INSERT INTO user_inventory (user_id, item_code, quantity)
            VALUES (p_user_id, v_seed_key, v_seed_amount::INT)
            ON CONFLICT (user_id, item_code)
            DO UPDATE SET quantity = user_inventory.quantity + v_seed_amount::INT;
        END LOOP;
    END IF;

    -- 새 골드 잔액
    SELECT gold INTO v_new_gold FROM user_farm WHERE user_id = p_user_id;

    RETURN jsonb_build_object(
        'success', true,
        'gold_earned', v_mission.reward_gold,
        'xp_earned', v_mission.reward_xp,
        'seeds_earned', v_mission.reward_seeds,
        'new_gold_balance', COALESCE(v_new_gold, 0)
    );
END;
$$;

-- =====================================================
-- 7. 함수 권한
-- =====================================================
GRANT EXECUTE ON FUNCTION get_daily_missions(UUID) TO authenticated;
GRANT EXECUTE ON FUNCTION get_weekly_challenges(UUID) TO authenticated;
GRANT EXECUTE ON FUNCTION update_mission_progress(UUID, VARCHAR, VARCHAR, INT) TO authenticated;
GRANT EXECUTE ON FUNCTION claim_mission_reward(UUID, UUID) TO authenticated;
