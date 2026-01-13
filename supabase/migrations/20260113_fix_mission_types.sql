-- =====================================================
-- Fix Mission System - 다양한 조건 지원
-- 실제 문제 유형: blank, puzzle, guided, implementation
-- 추가 조건: category, difficulty, all_types
-- 2026-01-13
-- =====================================================

-- 1. 기존 데이터 삭제
DELETE FROM user_mission_progress;
DELETE FROM mission_schedule;
DELETE FROM missions;

-- 2. missions 테이블에 새 컬럼 추가 (없으면)
ALTER TABLE missions ADD COLUMN IF NOT EXISTS category VARCHAR(50);      -- 알고리즘 카테고리
ALTER TABLE missions ADD COLUMN IF NOT EXISTS require_all_types BOOLEAN DEFAULT FALSE;  -- 모든 유형 풀기

-- =====================================================
-- 2. 일일 미션 (25개) - 매일 4개 랜덤 선택
-- =====================================================
-- 씨앗 등급: common(carrot,radish,potato,wheat) < uncommon(tomato,onion,cabbage) < rare(strawberry,corn) < epic(pumpkin)
INSERT INTO missions (code, name, description, mission_type, condition_type, condition_value, difficulty, reward_gold, reward_xp, reward_seeds)
VALUES
    -- ========== 전체 문제 풀이 (6개) ==========
    ('daily_solve_1', 'Warm Up', '오늘 문제 1개 풀기', 'daily', 'problems', 1, NULL, 20, 15, NULL),
    ('daily_solve_3', 'Daily Grind', '오늘 문제 3개 풀기', 'daily', 'problems', 3, NULL, 50, 30, '{"seed_radish": 1}'),
    ('daily_solve_5', 'Code Sprint', '오늘 문제 5개 풀기', 'daily', 'problems', 5, NULL, 100, 50, '{"seed_carrot": 1, "seed_wheat": 1}'),
    ('daily_solve_7', 'Power Hour', '오늘 문제 7개 풀기', 'daily', 'problems', 7, NULL, 150, 80, '{"seed_potato": 2, "seed_radish": 1}'),
    ('daily_solve_10', 'Ten Down', '오늘 문제 10개 풀기', 'daily', 'problems', 10, NULL, 200, 100, '{"seed_onion": 1, "seed_carrot": 2}'),
    ('daily_solve_15', 'Code Storm', '오늘 문제 15개 풀기', 'daily', 'problems', 15, NULL, 300, 150, '{"seed_tomato": 1, "seed_cabbage": 1, "seed_carrot": 1}'),

    -- ========== 빈칸 채우기 (5개) ==========
    ('daily_blank_1', 'Fill Starter', '빈칸 채우기 1개 풀기', 'daily', 'blank', 1, NULL, 25, 20, NULL),
    ('daily_blank_2', 'Fill Practice', '빈칸 채우기 2개 풀기', 'daily', 'blank', 2, NULL, 40, 25, '{"seed_wheat": 1}'),
    ('daily_blank_3', 'Fill Challenge', '빈칸 채우기 3개 풀기', 'daily', 'blank', 3, NULL, 60, 35, '{"seed_carrot": 1, "seed_radish": 1}'),
    ('daily_blank_5', 'Fill Expert', '빈칸 채우기 5개 풀기', 'daily', 'blank', 5, NULL, 100, 60, '{"seed_onion": 1, "seed_potato": 1}'),
    ('daily_blank_7', 'Fill Master', '빈칸 채우기 7개 풀기', 'daily', 'blank', 7, NULL, 150, 90, '{"seed_tomato": 1, "seed_carrot": 2}'),

    -- ========== 퍼즐 (5개) ==========
    ('daily_puzzle_1', 'Puzzle Starter', '코드 퍼즐 1개 풀기', 'daily', 'puzzle', 1, NULL, 30, 20, NULL),
    ('daily_puzzle_2', 'Puzzle Practice', '코드 퍼즐 2개 풀기', 'daily', 'puzzle', 2, NULL, 50, 30, '{"seed_potato": 1}'),
    ('daily_puzzle_3', 'Puzzle Challenge', '코드 퍼즐 3개 풀기', 'daily', 'puzzle', 3, NULL, 80, 50, '{"seed_wheat": 1, "seed_radish": 1}'),
    ('daily_puzzle_5', 'Puzzle Expert', '코드 퍼즐 5개 풀기', 'daily', 'puzzle', 5, NULL, 120, 70, '{"seed_cabbage": 1, "seed_carrot": 1}'),
    ('daily_puzzle_7', 'Puzzle Master', '코드 퍼즐 7개 풀기', 'daily', 'puzzle', 7, NULL, 180, 100, '{"seed_corn": 1, "seed_onion": 1}'),

    -- ========== 가이디드 (4개) ==========
    ('daily_guided_1', 'Guided Starter', '가이디드 문제 1개 풀기', 'daily', 'guided', 1, NULL, 40, 30, '{"seed_radish": 1}'),
    ('daily_guided_2', 'Guided Practice', '가이디드 문제 2개 풀기', 'daily', 'guided', 2, NULL, 80, 50, '{"seed_carrot": 1, "seed_potato": 1}'),
    ('daily_guided_3', 'Guided Challenge', '가이디드 문제 3개 풀기', 'daily', 'guided', 3, NULL, 120, 80, '{"seed_tomato": 1, "seed_wheat": 1}'),
    ('daily_guided_5', 'Guided Master', '가이디드 문제 5개 풀기', 'daily', 'guided', 5, NULL, 200, 120, '{"seed_strawberry": 1, "seed_onion": 1}'),

    -- ========== 구현 (5개) ==========
    ('daily_impl_1', 'Build Starter', '구현 문제 1개 풀기', 'daily', 'implementation', 1, NULL, 50, 35, '{"seed_wheat": 1}'),
    ('daily_impl_2', 'Build Practice', '구현 문제 2개 풀기', 'daily', 'implementation', 2, NULL, 100, 60, '{"seed_potato": 1, "seed_radish": 1}'),
    ('daily_impl_3', 'Build Challenge', '구현 문제 3개 풀기', 'daily', 'implementation', 3, NULL, 150, 90, '{"seed_cabbage": 1, "seed_carrot": 1}'),
    ('daily_impl_5', 'Build Expert', '구현 문제 5개 풀기', 'daily', 'implementation', 5, NULL, 250, 150, '{"seed_corn": 1, "seed_tomato": 1}'),
    ('daily_impl_7', 'Build Master', '구현 문제 7개 풀기', 'daily', 'implementation', 7, NULL, 350, 200, '{"seed_strawberry": 1, "seed_cabbage": 1, "seed_onion": 1}');

-- =====================================================
-- 3. 주간 챌린지 (20개) - 매주 5개 랜덤 선택
-- =====================================================
INSERT INTO missions (code, name, description, mission_type, condition_type, condition_value, difficulty, reward_gold, reward_xp, reward_seeds)
VALUES
    -- ========== 전체 문제 풀이 (5개) ==========
    ('weekly_solve_10', 'Weekly Starter', '이번 주 문제 10개 풀기', 'weekly', 'problems', 10, NULL, 150, 100, '{"seed_carrot": 2, "seed_radish": 2}'),
    ('weekly_solve_20', 'Weekly Warrior', '이번 주 문제 20개 풀기', 'weekly', 'problems', 20, NULL, 300, 200, '{"seed_potato": 2, "seed_wheat": 2, "seed_onion": 1}'),
    ('weekly_solve_35', 'Weekly Champion', '이번 주 문제 35개 풀기', 'weekly', 'problems', 35, NULL, 500, 350, '{"seed_tomato": 2, "seed_cabbage": 2, "seed_corn": 1}'),
    ('weekly_solve_50', 'Weekly Legend', '이번 주 문제 50개 풀기', 'weekly', 'problems', 50, NULL, 800, 500, '{"seed_strawberry": 2, "seed_corn": 2, "seed_tomato": 1}'),
    ('weekly_solve_70', 'Weekly Elite', '이번 주 문제 70개 풀기', 'weekly', 'problems', 70, NULL, 1200, 750, '{"seed_pumpkin": 1, "seed_strawberry": 2, "seed_corn": 2}'),

    -- ========== 빈칸 채우기 (4개) ==========
    ('weekly_blank_5', 'Fill Weekly', '이번 주 빈칸 5개 풀기', 'weekly', 'blank', 5, NULL, 150, 100, '{"seed_carrot": 2, "seed_wheat": 2}'),
    ('weekly_blank_10', 'Fill Challenger', '이번 주 빈칸 10개 풀기', 'weekly', 'blank', 10, NULL, 250, 150, '{"seed_onion": 2, "seed_potato": 2}'),
    ('weekly_blank_20', 'Fill Champion', '이번 주 빈칸 20개 풀기', 'weekly', 'blank', 20, NULL, 450, 300, '{"seed_corn": 2, "seed_cabbage": 2}'),
    ('weekly_blank_30', 'Fill Elite', '이번 주 빈칸 30개 풀기', 'weekly', 'blank', 30, NULL, 700, 450, '{"seed_pumpkin": 1, "seed_strawberry": 2}'),

    -- ========== 퍼즐 (4개) ==========
    ('weekly_puzzle_5', 'Puzzle Weekly', '이번 주 퍼즐 5개 풀기', 'weekly', 'puzzle', 5, NULL, 180, 120, '{"seed_radish": 2, "seed_potato": 2}'),
    ('weekly_puzzle_10', 'Puzzle Challenger', '이번 주 퍼즐 10개 풀기', 'weekly', 'puzzle', 10, NULL, 300, 200, '{"seed_tomato": 2, "seed_onion": 2}'),
    ('weekly_puzzle_20', 'Puzzle Champion', '이번 주 퍼즐 20개 풀기', 'weekly', 'puzzle', 20, NULL, 500, 350, '{"seed_strawberry": 2, "seed_cabbage": 2}'),
    ('weekly_puzzle_30', 'Puzzle Elite', '이번 주 퍼즐 30개 풀기', 'weekly', 'puzzle', 30, NULL, 750, 500, '{"seed_pumpkin": 1, "seed_corn": 2}'),

    -- ========== 가이디드 (3개) ==========
    ('weekly_guided_3', 'Guided Weekly', '이번 주 가이디드 3개 풀기', 'weekly', 'guided', 3, NULL, 200, 130, '{"seed_carrot": 2, "seed_radish": 2}'),
    ('weekly_guided_7', 'Guided Challenger', '이번 주 가이디드 7개 풀기', 'weekly', 'guided', 7, NULL, 400, 280, '{"seed_cabbage": 2, "seed_tomato": 2}'),
    ('weekly_guided_15', 'Guided Champion', '이번 주 가이디드 15개 풀기', 'weekly', 'guided', 15, NULL, 700, 500, '{"seed_strawberry": 2, "seed_corn": 2, "seed_onion": 1}'),

    -- ========== 구현 (4개) ==========
    ('weekly_impl_3', 'Build Weekly', '이번 주 구현 3개 풀기', 'weekly', 'implementation', 3, NULL, 220, 150, '{"seed_wheat": 2, "seed_potato": 2}'),
    ('weekly_impl_7', 'Build Challenger', '이번 주 구현 7개 풀기', 'weekly', 'implementation', 7, NULL, 450, 300, '{"seed_onion": 2, "seed_tomato": 2}'),
    ('weekly_impl_15', 'Build Champion', '이번 주 구현 15개 풀기', 'weekly', 'implementation', 15, NULL, 750, 500, '{"seed_corn": 2, "seed_strawberry": 2}'),
    ('weekly_impl_25', 'Build Elite', '이번 주 구현 25개 풀기', 'weekly', 'implementation', 25, NULL, 1000, 700, '{"seed_pumpkin": 1, "seed_strawberry": 2, "seed_corn": 1}');

-- =====================================================
-- 3-2. 추가 일일 미션 - 난이도/복합 조건 (8개 추가 → 총 33개)
-- =====================================================
INSERT INTO missions (code, name, description, mission_type, condition_type, condition_value, difficulty, reward_gold, reward_xp, reward_seeds, category, require_all_types)
VALUES
    -- ========== 난이도별 미션 (6개) ==========
    ('daily_easy_3', 'Easy Mode', '쉬운 난이도 3문제 풀기', 'daily', 'problems', 3, 'easy', 40, 25, '{"seed_carrot": 2}', NULL, FALSE),
    ('daily_easy_5', 'Easy Streak', '쉬운 난이도 5문제 풀기', 'daily', 'problems', 5, 'easy', 70, 40, '{"seed_radish": 2, "seed_wheat": 1}', NULL, FALSE),
    ('daily_medium_3', 'Medium Mode', '보통 난이도 3문제 풀기', 'daily', 'problems', 3, 'medium', 80, 50, '{"seed_potato": 1, "seed_onion": 1}', NULL, FALSE),
    ('daily_medium_5', 'Medium Streak', '보통 난이도 5문제 풀기', 'daily', 'problems', 5, 'medium', 130, 80, '{"seed_tomato": 1, "seed_cabbage": 1}', NULL, FALSE),
    ('daily_hard_2', 'Hard Mode', '어려운 난이도 2문제 풀기', 'daily', 'problems', 2, 'hard', 120, 70, '{"seed_corn": 1, "seed_onion": 1}', NULL, FALSE),
    ('daily_hard_3', 'Hardcore', '어려운 난이도 3문제 풀기', 'daily', 'problems', 3, 'hard', 180, 100, '{"seed_strawberry": 1, "seed_tomato": 1}', NULL, FALSE),

    -- ========== 복합 조건 미션 (2개) ==========
    ('daily_all_types', 'All Rounder', '모든 유형 각각 1문제씩 풀기', 'daily', 'problems', 4, NULL, 200, 120, '{"seed_corn": 1, "seed_strawberry": 1}', NULL, TRUE),
    ('daily_variety_2', 'Variety Pack', '3가지 이상 유형 문제 풀기', 'daily', 'problems', 3, NULL, 100, 60, '{"seed_tomato": 1, "seed_cabbage": 1}', NULL, FALSE);

-- =====================================================
-- 3-3. 추가 주간 미션 - 난이도/복합 조건 (8개 추가 → 총 28개)
-- =====================================================
INSERT INTO missions (code, name, description, mission_type, condition_type, condition_value, difficulty, reward_gold, reward_xp, reward_seeds, category, require_all_types)
VALUES
    -- ========== 난이도별 주간 미션 (5개) ==========
    ('weekly_easy_20', 'Easy Expert', '쉬운 난이도 20문제 풀기', 'weekly', 'problems', 20, 'easy', 300, 200, '{"seed_carrot": 3, "seed_radish": 3, "seed_wheat": 2}', NULL, FALSE),
    ('weekly_medium_15', 'Medium Expert', '보통 난이도 15문제 풀기', 'weekly', 'problems', 15, 'medium', 400, 280, '{"seed_tomato": 2, "seed_onion": 2, "seed_cabbage": 2}', NULL, FALSE),
    ('weekly_medium_25', 'Medium Legend', '보통 난이도 25문제 풀기', 'weekly', 'problems', 25, 'medium', 650, 450, '{"seed_corn": 2, "seed_strawberry": 2, "seed_tomato": 2}', NULL, FALSE),
    ('weekly_hard_10', 'Hard Challenger', '어려운 난이도 10문제 풀기', 'weekly', 'problems', 10, 'hard', 600, 400, '{"seed_strawberry": 2, "seed_corn": 2, "seed_pumpkin": 1}', NULL, FALSE),
    ('weekly_hard_20', 'Hard Legend', '어려운 난이도 20문제 풀기', 'weekly', 'problems', 20, 'hard', 1000, 700, '{"seed_pumpkin": 2, "seed_strawberry": 3, "seed_corn": 2}', NULL, FALSE),

    -- ========== 복합 조건 주간 미션 (3개) ==========
    ('weekly_all_types', 'All Rounder Pro', '모든 유형 각각 5문제씩 풀기', 'weekly', 'problems', 20, NULL, 800, 500, '{"seed_pumpkin": 1, "seed_strawberry": 2, "seed_corn": 2}', NULL, TRUE),
    ('weekly_variety', 'Versatile', '모든 유형 각각 3문제씩 풀기', 'weekly', 'problems', 12, NULL, 450, 300, '{"seed_corn": 2, "seed_strawberry": 2, "seed_tomato": 2}', NULL, TRUE),
    ('weekly_balanced', 'Balanced', '각 난이도별로 5문제씩 풀기', 'weekly', 'problems', 15, NULL, 500, 320, '{"seed_corn": 2, "seed_tomato": 2, "seed_onion": 2}', NULL, FALSE);

-- =====================================================
-- 4. 미션 선택 개수 변경을 위한 함수 업데이트
-- 일일: 3개, 주간: 5개
-- =====================================================

-- 일일 미션 조회 (3개 선택)
CREATE OR REPLACE FUNCTION get_daily_missions(p_user_id UUID)
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_today DATE := CURRENT_DATE;
    v_result JSONB;
BEGIN
    -- 1. 오늘 스케줄이 없으면 생성 (3개 선택)
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
            'reward_seeds', m.reward_seeds,
            'category', m.category,
            'require_all_types', m.require_all_types
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

-- 주간 챌린지 조회 (5개 선택)
CREATE OR REPLACE FUNCTION get_weekly_challenges(p_user_id UUID)
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_week_start DATE := date_trunc('week', CURRENT_DATE)::DATE;
    v_result JSONB;
BEGIN
    -- 1. 이번 주 스케줄이 없으면 생성 (5개 선택)
    INSERT INTO mission_schedule (schedule_date, mission_type, mission_id, slot_number)
    SELECT v_week_start, 'weekly', id, rn
    FROM (
        SELECT id, ROW_NUMBER() OVER (ORDER BY RANDOM()) as rn
        FROM missions
        WHERE mission_type = 'weekly' AND is_active = true
        LIMIT 5  -- 2개 → 5개로 변경
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
            'reward_seeds', m.reward_seeds,
            'category', m.category,
            'require_all_types', m.require_all_types
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

-- =====================================================
-- 5. 미션 진행률 업데이트 함수 (확장 버전)
-- 난이도 필터링 및 require_all_types 지원
-- =====================================================

-- 사용자별 오늘/이번주 유형별 풀이 기록 저장 테이블 (기존에 없으면 생성)
CREATE TABLE IF NOT EXISTS user_daily_type_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    progress_date DATE NOT NULL DEFAULT CURRENT_DATE,
    blank_count INT DEFAULT 0,
    puzzle_count INT DEFAULT 0,
    guided_count INT DEFAULT 0,
    implementation_count INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, progress_date)
);

-- 미션 진행률 업데이트 함수 (확장 버전)
CREATE OR REPLACE FUNCTION update_mission_progress(
    p_user_id UUID,
    p_condition_type VARCHAR(30),        -- 'problems', 'blank', 'puzzle', 'guided', 'implementation'
    p_difficulty VARCHAR(20) DEFAULT NULL,  -- 'easy', 'medium', 'hard' etc.
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
    v_type_progress RECORD;
    v_all_types_complete BOOLEAN;
BEGIN
    -- 1. 유형별 풀이 기록 업데이트 (blank, puzzle, guided, implementation)
    IF p_condition_type IN ('blank', 'puzzle', 'guided', 'implementation') THEN
        INSERT INTO user_daily_type_progress (user_id, progress_date, blank_count, puzzle_count, guided_count, implementation_count)
        VALUES (p_user_id, v_today, 0, 0, 0, 0)
        ON CONFLICT (user_id, progress_date) DO NOTHING;

        -- 유형별 카운트 증가
        EXECUTE format('UPDATE user_daily_type_progress SET %I_count = %I_count + $1, updated_at = NOW() WHERE user_id = $2 AND progress_date = $3',
            p_condition_type, p_condition_type)
        USING p_increment, p_user_id, v_today;
    END IF;

    -- 2. 일반 미션 업데이트 (기존 로직)
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
          AND m.require_all_types = FALSE  -- 복합 조건 미션은 별도 처리
          AND (
              m.condition_type = p_condition_type
              OR (m.condition_type = 'problems' AND p_condition_type IN ('blank', 'puzzle', 'guided', 'implementation'))
          )
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

    -- 3. require_all_types 미션 처리 (모든 유형 각각 풀기)
    -- 오늘/이번 주 유형별 진행 상황 조회
    SELECT blank_count, puzzle_count, guided_count, implementation_count
    INTO v_type_progress
    FROM user_daily_type_progress
    WHERE user_id = p_user_id AND progress_date = v_today;

    IF FOUND THEN
        -- 일일 미션: require_all_types 처리
        FOR v_row IN
            SELECT ump.id, ump.current_progress, m.condition_value as target, ump.status,
                   LEAST(
                       v_type_progress.blank_count,
                       v_type_progress.puzzle_count,
                       v_type_progress.guided_count,
                       v_type_progress.implementation_count
                   ) * 4 as new_progress  -- 4유형 각각 1개씩 = 4문제
            FROM user_mission_progress ump
            JOIN mission_schedule ms ON ump.schedule_id = ms.id
            JOIN missions m ON ms.mission_id = m.id
            WHERE ump.user_id = p_user_id
              AND ump.status = 'active'
              AND m.require_all_types = TRUE
              AND ms.mission_type = 'daily'
              AND ms.schedule_date = v_today
        LOOP
            IF v_row.new_progress > v_row.current_progress THEN
                UPDATE user_mission_progress
                SET current_progress = LEAST(v_row.new_progress, v_row.target),
                    status = CASE WHEN v_row.new_progress >= v_row.target THEN 'completed' ELSE status END,
                    completed_at = CASE WHEN v_row.new_progress >= v_row.target AND status = 'active' THEN NOW() ELSE completed_at END
                WHERE id = v_row.id;

                v_updated := v_updated || jsonb_build_object(
                    'id', v_row.id,
                    'progress', LEAST(v_row.new_progress, v_row.target),
                    'target', v_row.target,
                    'completed', v_row.new_progress >= v_row.target
                );
            END IF;
        END LOOP;
    END IF;

    RETURN v_updated;
END;
$$;

-- 권한 부여
GRANT ALL ON TABLE user_daily_type_progress TO authenticated;
GRANT EXECUTE ON FUNCTION update_mission_progress(UUID, VARCHAR, VARCHAR, INT) TO authenticated;
