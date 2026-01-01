-- =====================================================
-- 통합 상점 시스템: 씨앗 추가
-- shop_items에 seed 카테고리 아이템 추가
-- =====================================================

-- 1. 씨앗 아이템 추가 (farm_items의 작물 기반)
INSERT INTO shop_items (code, name, name_ko, category, rarity, price, max_quantity, metadata)
SELECT
    'seed_' || code,
    name || ' Seed',
    name_ko || ' 씨앗',
    'seed',
    rarity,
    seed_cost,
    NULL,  -- 무제한 구매 가능
    jsonb_build_object(
        'cropCode', code,
        'growTimeSeconds', grow_time_seconds,
        'sellPrice', sell_price,
        'xpReward', xp_reward
    )
FROM farm_items
WHERE type = 'crop'
ON CONFLICT (code) DO UPDATE SET
    name = EXCLUDED.name,
    name_ko = EXCLUDED.name_ko,
    price = EXCLUDED.price,
    metadata = EXCLUDED.metadata;

-- 2. 씨앗 카테고리 인덱스 추가 (성능 최적화)
CREATE INDEX IF NOT EXISTS idx_shop_items_seed_category
ON shop_items(category) WHERE category = 'seed';

-- =====================================================
-- 참고: 기존 씨앗 데이터 예시
-- =====================================================
-- seed_carrot: 당근 씨앗, 10G, common
-- seed_radish: 무 씨앗, 10G, common
-- seed_potato: 감자 씨앗, 10G, common
-- seed_wheat: 밀 씨앗, 10G, common
-- seed_tomato: 토마토 씨앗, 20G, uncommon
-- seed_onion: 양파 씨앗, 20G, uncommon
-- seed_cabbage: 양배추 씨앗, 20G, uncommon
-- seed_strawberry: 딸기 씨앗, 35G, rare
-- seed_corn: 옥수수 씨앗, 40G, rare
-- seed_pumpkin: 호박 씨앗, 100G, epic
