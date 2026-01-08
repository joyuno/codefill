-- =====================================================
-- Badge Icons URL 업데이트
-- Supabase Storage badges 버킷의 아이콘 URL 설정
-- =====================================================

-- Base URL: https://qukgaiwdusuxcswsqhjo.supabase.co/storage/v1/object/public/badges/

-- 마일스톤 - 문제 해결 (6개)
UPDATE badges SET icon_url = 'https://qukgaiwdusuxcswsqhjo.supabase.co/storage/v1/object/public/badges/01_first_solve.svg' WHERE code = 'first_solve';
UPDATE badges SET icon_url = 'https://qukgaiwdusuxcswsqhjo.supabase.co/storage/v1/object/public/badges/02_solve_10.svg' WHERE code = 'solve_10';
UPDATE badges SET icon_url = 'https://qukgaiwdusuxcswsqhjo.supabase.co/storage/v1/object/public/badges/03_solve_50.svg' WHERE code = 'solve_50';
UPDATE badges SET icon_url = 'https://qukgaiwdusuxcswsqhjo.supabase.co/storage/v1/object/public/badges/04_solve_100.svg' WHERE code = 'solve_100';
UPDATE badges SET icon_url = 'https://qukgaiwdusuxcswsqhjo.supabase.co/storage/v1/object/public/badges/05_solve_250.svg' WHERE code = 'solve_250';
UPDATE badges SET icon_url = 'https://qukgaiwdusuxcswsqhjo.supabase.co/storage/v1/object/public/badges/06_solve_500.svg' WHERE code = 'solve_500';

-- 마일스톤 - 스트릭 (5개)
UPDATE badges SET icon_url = 'https://qukgaiwdusuxcswsqhjo.supabase.co/storage/v1/object/public/badges/07_streak_7.svg' WHERE code = 'streak_7';
UPDATE badges SET icon_url = 'https://qukgaiwdusuxcswsqhjo.supabase.co/storage/v1/object/public/badges/08_streak_14.svg' WHERE code = 'streak_14';
UPDATE badges SET icon_url = 'https://qukgaiwdusuxcswsqhjo.supabase.co/storage/v1/object/public/badges/09_streak_30.svg' WHERE code = 'streak_30';
UPDATE badges SET icon_url = 'https://qukgaiwdusuxcswsqhjo.supabase.co/storage/v1/object/public/badges/10_streak_90.svg' WHERE code = 'streak_90';
UPDATE badges SET icon_url = 'https://qukgaiwdusuxcswsqhjo.supabase.co/storage/v1/object/public/badges/11_streak_365.svg' WHERE code = 'streak_365';

-- 마일스톤 - 레벨 (5개)
UPDATE badges SET icon_url = 'https://qukgaiwdusuxcswsqhjo.supabase.co/storage/v1/object/public/badges/12_level_5.svg' WHERE code = 'level_5';
UPDATE badges SET icon_url = 'https://qukgaiwdusuxcswsqhjo.supabase.co/storage/v1/object/public/badges/13_level_10.svg' WHERE code = 'level_10';
UPDATE badges SET icon_url = 'https://qukgaiwdusuxcswsqhjo.supabase.co/storage/v1/object/public/badges/14_level_25.svg' WHERE code = 'level_25';
UPDATE badges SET icon_url = 'https://qukgaiwdusuxcswsqhjo.supabase.co/storage/v1/object/public/badges/15_level_50.svg' WHERE code = 'level_50';
UPDATE badges SET icon_url = 'https://qukgaiwdusuxcswsqhjo.supabase.co/storage/v1/object/public/badges/16_level_100.svg' WHERE code = 'level_100';

-- 문제유형 - 빈칸 (4개)
UPDATE badges SET icon_url = 'https://qukgaiwdusuxcswsqhjo.supabase.co/storage/v1/object/public/badges/17_blank_10.svg' WHERE code = 'blank_10';
UPDATE badges SET icon_url = 'https://qukgaiwdusuxcswsqhjo.supabase.co/storage/v1/object/public/badges/18_blank_30.svg' WHERE code = 'blank_30';
UPDATE badges SET icon_url = 'https://qukgaiwdusuxcswsqhjo.supabase.co/storage/v1/object/public/badges/19_blank_50.svg' WHERE code = 'blank_50';
UPDATE badges SET icon_url = 'https://qukgaiwdusuxcswsqhjo.supabase.co/storage/v1/object/public/badges/20_blank_100.svg' WHERE code = 'blank_100';

-- 문제유형 - 퍼즐 (4개)
UPDATE badges SET icon_url = 'https://qukgaiwdusuxcswsqhjo.supabase.co/storage/v1/object/public/badges/21_puzzle_10.svg' WHERE code = 'puzzle_10';
UPDATE badges SET icon_url = 'https://qukgaiwdusuxcswsqhjo.supabase.co/storage/v1/object/public/badges/22_puzzle_30.svg' WHERE code = 'puzzle_30';
UPDATE badges SET icon_url = 'https://qukgaiwdusuxcswsqhjo.supabase.co/storage/v1/object/public/badges/23_puzzle_50.svg' WHERE code = 'puzzle_50';
UPDATE badges SET icon_url = 'https://qukgaiwdusuxcswsqhjo.supabase.co/storage/v1/object/public/badges/24_puzzle_100.svg' WHERE code = 'puzzle_100';

-- 문제유형 - 대화형 (4개)
UPDATE badges SET icon_url = 'https://qukgaiwdusuxcswsqhjo.supabase.co/storage/v1/object/public/badges/25_guided_10.svg' WHERE code = 'guided_10';
UPDATE badges SET icon_url = 'https://qukgaiwdusuxcswsqhjo.supabase.co/storage/v1/object/public/badges/26_guided_30.svg' WHERE code = 'guided_30';
UPDATE badges SET icon_url = 'https://qukgaiwdusuxcswsqhjo.supabase.co/storage/v1/object/public/badges/27_guided_50.svg' WHERE code = 'guided_50';
UPDATE badges SET icon_url = 'https://qukgaiwdusuxcswsqhjo.supabase.co/storage/v1/object/public/badges/28_guided_100.svg' WHERE code = 'guided_100';

-- 문제유형 - 구현 (4개)
UPDATE badges SET icon_url = 'https://qukgaiwdusuxcswsqhjo.supabase.co/storage/v1/object/public/badges/29_impl_10.svg' WHERE code = 'impl_10';
UPDATE badges SET icon_url = 'https://qukgaiwdusuxcswsqhjo.supabase.co/storage/v1/object/public/badges/30_impl_30.svg' WHERE code = 'impl_30';
UPDATE badges SET icon_url = 'https://qukgaiwdusuxcswsqhjo.supabase.co/storage/v1/object/public/badges/31_impl_50.svg' WHERE code = 'impl_50';
UPDATE badges SET icon_url = 'https://qukgaiwdusuxcswsqhjo.supabase.co/storage/v1/object/public/badges/32_impl_100.svg' WHERE code = 'impl_100';

-- 난이도 - Easy (3개)
UPDATE badges SET icon_url = 'https://qukgaiwdusuxcswsqhjo.supabase.co/storage/v1/object/public/badges/33_easy_10.svg' WHERE code = 'easy_10';
UPDATE badges SET icon_url = 'https://qukgaiwdusuxcswsqhjo.supabase.co/storage/v1/object/public/badges/34_easy_30.svg' WHERE code = 'easy_30';
UPDATE badges SET icon_url = 'https://qukgaiwdusuxcswsqhjo.supabase.co/storage/v1/object/public/badges/35_easy_50.svg' WHERE code = 'easy_50';

-- 난이도 - Medium (3개)
UPDATE badges SET icon_url = 'https://qukgaiwdusuxcswsqhjo.supabase.co/storage/v1/object/public/badges/36_medium_10.svg' WHERE code = 'medium_10';
UPDATE badges SET icon_url = 'https://qukgaiwdusuxcswsqhjo.supabase.co/storage/v1/object/public/badges/37_medium_30.svg' WHERE code = 'medium_30';
UPDATE badges SET icon_url = 'https://qukgaiwdusuxcswsqhjo.supabase.co/storage/v1/object/public/badges/38_medium_50.svg' WHERE code = 'medium_50';

-- 난이도 - Hard (4개)
UPDATE badges SET icon_url = 'https://qukgaiwdusuxcswsqhjo.supabase.co/storage/v1/object/public/badges/39_hard_5.svg' WHERE code = 'hard_5';
UPDATE badges SET icon_url = 'https://qukgaiwdusuxcswsqhjo.supabase.co/storage/v1/object/public/badges/40_hard_10.svg' WHERE code = 'hard_10';
UPDATE badges SET icon_url = 'https://qukgaiwdusuxcswsqhjo.supabase.co/storage/v1/object/public/badges/41_hard_30.svg' WHERE code = 'hard_30';
UPDATE badges SET icon_url = 'https://qukgaiwdusuxcswsqhjo.supabase.co/storage/v1/object/public/badges/42_hard_50.svg' WHERE code = 'hard_50';

-- 난이도 - 복합 (2개)
UPDATE badges SET icon_url = 'https://qukgaiwdusuxcswsqhjo.supabase.co/storage/v1/object/public/badges/43_all_difficulty.svg' WHERE code = 'all_difficulty';
UPDATE badges SET icon_url = 'https://qukgaiwdusuxcswsqhjo.supabase.co/storage/v1/object/public/badges/44_all_difficulty_master.svg' WHERE code = 'all_difficulty_master';

-- 특별활동 - 시간대 (3개)
UPDATE badges SET icon_url = 'https://qukgaiwdusuxcswsqhjo.supabase.co/storage/v1/object/public/badges/45_night_owl.svg' WHERE code = 'night_owl';
UPDATE badges SET icon_url = 'https://qukgaiwdusuxcswsqhjo.supabase.co/storage/v1/object/public/badges/46_early_bird.svg' WHERE code = 'early_bird';
UPDATE badges SET icon_url = 'https://qukgaiwdusuxcswsqhjo.supabase.co/storage/v1/object/public/badges/47_weekend_coder.svg' WHERE code = 'weekend_coder';

-- 특별활동 - 하루집중 (4개)
UPDATE badges SET icon_url = 'https://qukgaiwdusuxcswsqhjo.supabase.co/storage/v1/object/public/badges/48_daily_3.svg' WHERE code = 'daily_3';
UPDATE badges SET icon_url = 'https://qukgaiwdusuxcswsqhjo.supabase.co/storage/v1/object/public/badges/49_daily_5.svg' WHERE code = 'daily_5';
UPDATE badges SET icon_url = 'https://qukgaiwdusuxcswsqhjo.supabase.co/storage/v1/object/public/badges/50_daily_10.svg' WHERE code = 'daily_10';
UPDATE badges SET icon_url = 'https://qukgaiwdusuxcswsqhjo.supabase.co/storage/v1/object/public/badges/51_daily_20.svg' WHERE code = 'daily_20';

-- 특별활동 - 정확도 (5개)
UPDATE badges SET icon_url = 'https://qukgaiwdusuxcswsqhjo.supabase.co/storage/v1/object/public/badges/52_first_try_10.svg' WHERE code = 'first_try_10';
UPDATE badges SET icon_url = 'https://qukgaiwdusuxcswsqhjo.supabase.co/storage/v1/object/public/badges/53_first_try_50.svg' WHERE code = 'first_try_50';
UPDATE badges SET icon_url = 'https://qukgaiwdusuxcswsqhjo.supabase.co/storage/v1/object/public/badges/54_first_try_100.svg' WHERE code = 'first_try_100';
UPDATE badges SET icon_url = 'https://qukgaiwdusuxcswsqhjo.supabase.co/storage/v1/object/public/badges/55_no_hint_50.svg' WHERE code = 'no_hint_50';
UPDATE badges SET icon_url = 'https://qukgaiwdusuxcswsqhjo.supabase.co/storage/v1/object/public/badges/56_no_hint_100.svg' WHERE code = 'no_hint_100';

-- 특별활동 - 도전 (2개)
UPDATE badges SET icon_url = 'https://qukgaiwdusuxcswsqhjo.supabase.co/storage/v1/object/public/badges/57_perfect_week.svg' WHERE code = 'perfect_week';
UPDATE badges SET icon_url = 'https://qukgaiwdusuxcswsqhjo.supabase.co/storage/v1/object/public/badges/58_perfect_month.svg' WHERE code = 'perfect_month';

-- 최고 달성 (2개)
UPDATE badges SET icon_url = 'https://qukgaiwdusuxcswsqhjo.supabase.co/storage/v1/object/public/badges/59_thousand.svg' WHERE code = 'thousand';
UPDATE badges SET icon_url = 'https://qukgaiwdusuxcswsqhjo.supabase.co/storage/v1/object/public/badges/60_all_rounder.svg' WHERE code = 'all_rounder';

-- 검증: icon_url이 설정된 뱃지 수 확인
DO $$
DECLARE
    icon_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO icon_count FROM badges WHERE icon_url IS NOT NULL;
    IF icon_count != 60 THEN
        RAISE WARNING 'Expected 60 badges with icon_url, but found %', icon_count;
    ELSE
        RAISE NOTICE 'Badge icons update complete: % badges updated', icon_count;
    END IF;
END $$;
