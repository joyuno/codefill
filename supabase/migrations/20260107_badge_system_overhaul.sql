-- =====================================================
-- Badge System Overhaul
-- 기존 뱃지 시스템을 60개 뱃지로 전면 개편
-- =====================================================

-- 1. 기존 데이터 삭제 (user_badges 먼저, 그 다음 badges)
TRUNCATE TABLE user_badges CASCADE;
TRUNCATE TABLE badges CASCADE;

-- 2. 60개 뱃지 INSERT
-- xp_reward는 모두 0 (뱃지 획득 시 XP 미지급)

-- =====================================================
-- 마일스톤 - 문제 해결 (6개)
-- =====================================================
INSERT INTO badges (code, name, description, condition_type, condition_value, rarity, xp_reward) VALUES
('first_solve', 'First Step', '첫 번째 문제를 해결하세요', 'problems', 1, 'common', 0),
('solve_10', 'Getting Started', '문제 10개를 해결하세요', 'problems', 10, 'common', 0),
('solve_50', 'Half Century', '문제 50개를 해결하세요', 'problems', 50, 'uncommon', 0),
('solve_100', 'Centurion', '문제 100개를 해결하세요', 'problems', 100, 'rare', 0),
('solve_250', 'Problem Solver', '문제 250개를 해결하세요', 'problems', 250, 'epic', 0),
('solve_500', 'Code Master', '문제 500개를 해결하세요', 'problems', 500, 'legendary', 0);

-- =====================================================
-- 마일스톤 - 스트릭 (5개)
-- =====================================================
INSERT INTO badges (code, name, description, condition_type, condition_value, rarity, xp_reward) VALUES
('streak_7', 'Week Warrior', '7일 연속으로 학습하세요', 'streak', 7, 'common', 0),
('streak_14', 'Two Weeks', '14일 연속으로 학습하세요', 'streak', 14, 'uncommon', 0),
('streak_30', 'Monthly Master', '30일 연속으로 학습하세요', 'streak', 30, 'rare', 0),
('streak_90', 'Quarterly Champion', '90일 연속으로 학습하세요', 'streak', 90, 'epic', 0),
('streak_365', 'Year Legend', '365일 연속으로 학습하세요', 'streak', 365, 'legendary', 0);

-- =====================================================
-- 마일스톤 - 레벨 (5개)
-- =====================================================
INSERT INTO badges (code, name, description, condition_type, condition_value, rarity, xp_reward) VALUES
('level_5', 'Rising Star', '레벨 5에 도달하세요', 'level', 5, 'common', 0),
('level_10', 'Intermediate', '레벨 10에 도달하세요', 'level', 10, 'uncommon', 0),
('level_25', 'Advanced', '레벨 25에 도달하세요', 'level', 25, 'rare', 0),
('level_50', 'Expert', '레벨 50에 도달하세요', 'level', 50, 'epic', 0),
('level_100', 'Grandmaster', '레벨 100에 도달하세요', 'level', 100, 'legendary', 0);

-- =====================================================
-- 문제 유형별 - 빈칸 채우기 (4개)
-- =====================================================
INSERT INTO badges (code, name, description, condition_type, condition_value, rarity, xp_reward) VALUES
('blank_10', 'Blank Beginner', '빈칸 채우기 문제 10개를 해결하세요', 'blank', 10, 'common', 0),
('blank_30', 'Blank Intermediate', '빈칸 채우기 문제 30개를 해결하세요', 'blank', 30, 'uncommon', 0),
('blank_50', 'Blank Expert', '빈칸 채우기 문제 50개를 해결하세요', 'blank', 50, 'rare', 0),
('blank_100', 'Blank Master', '빈칸 채우기 문제 100개를 해결하세요', 'blank', 100, 'epic', 0);

-- =====================================================
-- 문제 유형별 - 퍼즐 (4개)
-- =====================================================
INSERT INTO badges (code, name, description, condition_type, condition_value, rarity, xp_reward) VALUES
('puzzle_10', 'Puzzle Beginner', '퍼즐 문제 10개를 해결하세요', 'puzzle', 10, 'common', 0),
('puzzle_30', 'Puzzle Intermediate', '퍼즐 문제 30개를 해결하세요', 'puzzle', 30, 'uncommon', 0),
('puzzle_50', 'Puzzle Expert', '퍼즐 문제 50개를 해결하세요', 'puzzle', 50, 'rare', 0),
('puzzle_100', 'Puzzle Master', '퍼즐 문제 100개를 해결하세요', 'puzzle', 100, 'epic', 0);

-- =====================================================
-- 문제 유형별 - 1대1 대화형 (4개)
-- =====================================================
INSERT INTO badges (code, name, description, condition_type, condition_value, rarity, xp_reward) VALUES
('guided_10', 'Guided Beginner', '1대1 대화형 문제 10개를 해결하세요', 'guided', 10, 'common', 0),
('guided_30', 'Guided Intermediate', '1대1 대화형 문제 30개를 해결하세요', 'guided', 30, 'uncommon', 0),
('guided_50', 'Guided Expert', '1대1 대화형 문제 50개를 해결하세요', 'guided', 50, 'rare', 0),
('guided_100', 'Guided Master', '1대1 대화형 문제 100개를 해결하세요', 'guided', 100, 'epic', 0);

-- =====================================================
-- 문제 유형별 - 구현 (4개)
-- =====================================================
INSERT INTO badges (code, name, description, condition_type, condition_value, rarity, xp_reward) VALUES
('impl_10', 'Builder Beginner', '구현 문제 10개를 해결하세요', 'implementation', 10, 'common', 0),
('impl_30', 'Builder Intermediate', '구현 문제 30개를 해결하세요', 'implementation', 30, 'uncommon', 0),
('impl_50', 'Builder Expert', '구현 문제 50개를 해결하세요', 'implementation', 50, 'rare', 0),
('impl_100', 'Builder Master', '구현 문제 100개를 해결하세요', 'implementation', 100, 'epic', 0);

-- =====================================================
-- 난이도별 - Easy (3개)
-- =====================================================
INSERT INTO badges (code, name, description, condition_type, condition_value, rarity, xp_reward) VALUES
('easy_10', 'Easy Start', 'Easy 난이도 문제 10개를 해결하세요', 'easy', 10, 'common', 0),
('easy_30', 'Easy Going', 'Easy 난이도 문제 30개를 해결하세요', 'easy', 30, 'uncommon', 0),
('easy_50', 'Easy Expert', 'Easy 난이도 문제 50개를 해결하세요', 'easy', 50, 'rare', 0);

-- =====================================================
-- 난이도별 - Medium (3개)
-- =====================================================
INSERT INTO badges (code, name, description, condition_type, condition_value, rarity, xp_reward) VALUES
('medium_10', 'Medium Start', 'Medium 난이도 문제 10개를 해결하세요', 'medium', 10, 'uncommon', 0),
('medium_30', 'Medium Grinder', 'Medium 난이도 문제 30개를 해결하세요', 'medium', 30, 'rare', 0),
('medium_50', 'Medium Expert', 'Medium 난이도 문제 50개를 해결하세요', 'medium', 50, 'epic', 0);

-- =====================================================
-- 난이도별 - Hard (4개)
-- =====================================================
INSERT INTO badges (code, name, description, condition_type, condition_value, rarity, xp_reward) VALUES
('hard_5', 'Hard Start', 'Hard 난이도 문제 5개를 해결하세요', 'hard', 5, 'uncommon', 0),
('hard_10', 'Hard Crusher', 'Hard 난이도 문제 10개를 해결하세요', 'hard', 10, 'rare', 0),
('hard_30', 'Hard Expert', 'Hard 난이도 문제 30개를 해결하세요', 'hard', 30, 'epic', 0),
('hard_50', 'Hard Master', 'Hard 난이도 문제 50개를 해결하세요', 'hard', 50, 'legendary', 0);

-- =====================================================
-- 난이도별 - 복합 (2개)
-- =====================================================
INSERT INTO badges (code, name, description, condition_type, condition_value, rarity, xp_reward) VALUES
('all_difficulty', 'Difficulty Explorer', '각 난이도별 문제 10개씩 해결하세요', 'special', 10, 'rare', 0),
('all_difficulty_master', 'Difficulty Conqueror', '각 난이도별 문제 50개씩 해결하세요', 'special', 50, 'legendary', 0);

-- =====================================================
-- 특별 활동 - 시간대별 (3개)
-- =====================================================
INSERT INTO badges (code, name, description, condition_type, condition_value, rarity, xp_reward) VALUES
('night_owl', 'Night Owl', '자정~6시 사이에 문제를 풀어보세요', 'time', 1, 'common', 0),
('early_bird', 'Early Bird', '6시~9시 사이에 문제를 풀어보세요', 'time', 1, 'common', 0),
('weekend_coder', 'Weekend Coder', '주말에 문제를 풀어보세요', 'time', 1, 'common', 0);

-- =====================================================
-- 특별 활동 - 하루 집중 (4개)
-- =====================================================
INSERT INTO badges (code, name, description, condition_type, condition_value, rarity, xp_reward) VALUES
('daily_3', 'Daily Learner', '하루에 문제 3개를 해결하세요', 'daily', 3, 'common', 0),
('daily_5', 'Daily Achiever', '하루에 문제 5개를 해결하세요', 'daily', 5, 'uncommon', 0),
('daily_10', 'Daily Champion', '하루에 문제 10개를 해결하세요', 'daily', 10, 'rare', 0),
('daily_20', 'Daily Legend', '하루에 문제 20개를 해결하세요', 'daily', 20, 'epic', 0);

-- =====================================================
-- 특별 활동 - 정확도 (5개)
-- =====================================================
INSERT INTO badges (code, name, description, condition_type, condition_value, rarity, xp_reward) VALUES
('first_try_10', 'Accurate', '첫 시도에 정답 10회를 달성하세요', 'accuracy', 10, 'common', 0),
('first_try_50', 'Sharpshooter', '첫 시도에 정답 50회를 달성하세요', 'accuracy', 50, 'rare', 0),
('first_try_100', 'Perfectionist', '첫 시도에 정답 100회를 달성하세요', 'accuracy', 100, 'epic', 0),
('no_hint_50', 'Independent', '힌트 없이 문제 50개를 해결하세요', 'no_hint', 50, 'rare', 0),
('no_hint_100', 'Self-Reliant', '힌트 없이 문제 100개를 해결하세요', 'no_hint', 100, 'epic', 0);

-- =====================================================
-- 특별 활동 - 도전 (2개)
-- =====================================================
INSERT INTO badges (code, name, description, condition_type, condition_value, rarity, xp_reward) VALUES
('perfect_week', 'Perfect Week', '일주일간 매일 5문제 이상 해결하세요', 'special', 7, 'rare', 0),
('perfect_month', 'Perfect Month', '한 달간 매일 3문제 이상 해결하세요', 'special', 30, 'epic', 0);

-- =====================================================
-- 특별 활동 - 최고 달성 (2개)
-- =====================================================
INSERT INTO badges (code, name, description, condition_type, condition_value, rarity, xp_reward) VALUES
('thousand', 'Thousand Club', '문제 1000개를 해결하세요', 'problems', 1000, 'legendary', 0),
('all_rounder', 'All Rounder', '모든 카테고리의 뱃지를 획득하세요', 'special', 1, 'legendary', 0);

-- =====================================================
-- 검증: 60개 뱃지가 정확히 들어갔는지 확인
-- =====================================================
DO $$
DECLARE
    badge_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO badge_count FROM badges;
    IF badge_count != 60 THEN
        RAISE EXCEPTION 'Expected 60 badges, but found %', badge_count;
    END IF;
    RAISE NOTICE 'Badge system overhaul complete: % badges inserted', badge_count;
END $$;
