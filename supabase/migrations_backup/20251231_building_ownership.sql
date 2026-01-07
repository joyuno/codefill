-- =====================================================
-- Building Ownership System
-- 건물/나무/건초 소유 시스템 추가
-- =====================================================

-- farm_items 테이블에 건물, 나무, 건초 아이템 추가
-- seed_cost 필드를 구매 가격으로 활용

INSERT INTO farm_items (code, name, name_ko, type, rarity, seed_cost, sell_price, xp_reward, grow_time_seconds) VALUES
    -- Buildings (type = 'building')
    ('chickenCoop', 'Chicken Coop', '닭장', 'building', 'uncommon', 500, 0, 50, 0),
    ('well', 'Well', '우물', 'building', 'uncommon', 300, 0, 30, 0),
    ('scarecrow', 'Scarecrow', '허수아비', 'building', 'common', 150, 0, 15, 0),
    ('barn', 'Barn', '헛간', 'building', 'rare', 1000, 0, 100, 0),

    -- Trees (type = 'tree')
    ('tree_oak_small', 'Small Oak', '작은 참나무', 'tree', 'common', 100, 0, 10, 0),
    ('tree_oak_medium', 'Medium Oak', '중간 참나무', 'tree', 'uncommon', 200, 0, 20, 0),
    ('tree_pine_small', 'Small Pine', '작은 소나무', 'tree', 'common', 100, 0, 10, 0),
    ('tree_pine_medium', 'Medium Pine', '중간 소나무', 'tree', 'uncommon', 200, 0, 20, 0),
    ('tree_apple', 'Apple Tree', '사과나무', 'tree', 'rare', 300, 0, 30, 0),

    -- Hay/Decorations (type = 'hay')
    ('hay_pile', 'Hay Pile', '건초 더미', 'hay', 'common', 50, 0, 5, 0),
    ('hay_small', 'Small Hay', '작은 건초', 'hay', 'common', 30, 0, 3, 0)
ON CONFLICT (code) DO UPDATE SET
    name = EXCLUDED.name,
    name_ko = EXCLUDED.name_ko,
    type = EXCLUDED.type,
    rarity = EXCLUDED.rarity,
    seed_cost = EXCLUDED.seed_cost,
    xp_reward = EXCLUDED.xp_reward;

-- customization_data 구조 확장 설명:
-- {
--   "decorations": [...],              -- 기존: 꽃/잔디 장식
--   "buildings": {...},                -- 기존: 건물 위치
--   "owned_buildings": ["house", ...], -- 추가: 소유 건물 목록
--   "owned_trees": [                   -- 추가: 소유 나무/건초
--     { "id": "...", "type": "tree_oak_small", "tile_x": 5, "tile_y": 10 }
--   ],
--   "terrain": []
-- }
