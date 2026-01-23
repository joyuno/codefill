-- =====================================================
-- 작물 밸런스 대규모 업데이트
-- 시간당 골드 효율 기준 밸런싱
-- Common: 50G/hour, Uncommon: 150G/hour, Rare: 400G/hour, Epic: 800G/hour
-- =====================================================

-- farm_items 작물 데이터 업데이트 (18종)
UPDATE farm_items SET
    sell_price = 8,
    grow_time_seconds = 600,  -- 10분
    xp_reward = 3
WHERE code = 'carrot';

UPDATE farm_items SET
    sell_price = 8,
    grow_time_seconds = 600,  -- 10분
    xp_reward = 3
WHERE code = 'radish';

UPDATE farm_items SET
    sell_price = 12,
    grow_time_seconds = 900,  -- 15분
    xp_reward = 4
WHERE code = 'turnip';

UPDATE farm_items SET
    sell_price = 17,
    grow_time_seconds = 1200,  -- 20분
    xp_reward = 5
WHERE code = 'onion';

UPDATE farm_items SET
    sell_price = 21,
    grow_time_seconds = 1500,  -- 25분
    xp_reward = 6
WHERE code = 'tomato';

UPDATE farm_items SET
    sell_price = 25,
    grow_time_seconds = 1800,  -- 30분
    xp_reward = 7
WHERE code = 'grain';

-- Uncommon (150G/hour)
UPDATE farm_items SET
    sell_price = 75,
    grow_time_seconds = 1800,  -- 30분
    xp_reward = 10
WHERE code = 'cauliflower';

UPDATE farm_items SET
    sell_price = 100,
    grow_time_seconds = 2400,  -- 40분
    xp_reward = 12
WHERE code = 'corn';

UPDATE farm_items SET
    sell_price = 112,
    grow_time_seconds = 2700,  -- 45분
    xp_reward = 13
WHERE code = 'chili_pepper';

UPDATE farm_items SET
    sell_price = 125,
    grow_time_seconds = 3000,  -- 50분
    xp_reward = 14
WHERE code = 'strawberry';

UPDATE farm_items SET
    sell_price = 138,
    grow_time_seconds = 3300,  -- 55분
    xp_reward = 15
WHERE code = 'zucchini';

UPDATE farm_items SET
    sell_price = 150,
    grow_time_seconds = 3600,  -- 1시간
    xp_reward = 16
WHERE code = 'cotton';

-- Rare (400G/hour)
UPDATE farm_items SET
    sell_price = 400,
    grow_time_seconds = 3600,  -- 1시간
    xp_reward = 25
WHERE code = 'pumpkin';

UPDATE farm_items SET
    sell_price = 600,
    grow_time_seconds = 5400,  -- 1.5시간
    xp_reward = 30
WHERE code = 'grape';

UPDATE farm_items SET
    sell_price = 800,
    grow_time_seconds = 7200,  -- 2시간
    xp_reward = 40
WHERE code = 'coffee';

UPDATE farm_items SET
    sell_price = 1200,
    grow_time_seconds = 10800,  -- 3시간
    xp_reward = 50
WHERE code = 'prickly_pear';

-- Epic (800G/hour)
UPDATE farm_items SET
    sell_price = 3200,
    grow_time_seconds = 14400,  -- 4시간
    xp_reward = 80
WHERE code = 'watermelon';

UPDATE farm_items SET
    sell_price = 4000,
    grow_time_seconds = 18000,  -- 5시간
    xp_reward = 100
WHERE code = 'pineapple';

-- =====================================================
-- shop_items 씨앗 메타데이터도 동기화
-- =====================================================
UPDATE shop_items SET
    metadata = jsonb_build_object(
        'cropCode', fi.code,
        'growTimeSeconds', fi.grow_time_seconds,
        'sellPrice', fi.sell_price,
        'xpReward', fi.xp_reward
    )
FROM farm_items fi
WHERE shop_items.code = 'seed_' || fi.code
  AND shop_items.category = 'seed';

-- =====================================================
-- 밸런스 요약 (참조용)
-- =====================================================
-- | 등급      | 작물        | 판매가  | 재배시간 | G/hour |
-- |-----------|-------------|---------|----------|--------|
-- | Common    | 당근        | 8G      | 10분     | 48     |
-- | Common    | 무          | 8G      | 10분     | 48     |
-- | Common    | 순무        | 12G     | 15분     | 48     |
-- | Common    | 양파        | 17G     | 20분     | 51     |
-- | Common    | 토마토      | 21G     | 25분     | 50     |
-- | Common    | 밀          | 25G     | 30분     | 50     |
-- | Uncommon  | 콜리플라워  | 75G     | 30분     | 150    |
-- | Uncommon  | 옥수수      | 100G    | 40분     | 150    |
-- | Uncommon  | 고추        | 112G    | 45분     | 149    |
-- | Uncommon  | 딸기        | 125G    | 50분     | 150    |
-- | Uncommon  | 주키니      | 138G    | 55분     | 150    |
-- | Uncommon  | 목화        | 150G    | 60분     | 150    |
-- | Rare      | 호박        | 400G    | 1시간    | 400    |
-- | Rare      | 포도        | 600G    | 1.5시간  | 400    |
-- | Rare      | 커피        | 800G    | 2시간    | 400    |
-- | Rare      | 백년초      | 1200G   | 3시간    | 400    |
-- | Epic      | 수박        | 3200G   | 4시간    | 800    |
-- | Epic      | 파인애플    | 4000G   | 5시간    | 800    |
