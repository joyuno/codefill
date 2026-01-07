-- =====================================================
-- Unified Item System
-- 통합 아이템 시스템: 건물, 나무, 장식, 울타리, 밭 등
-- =====================================================

-- =====================================================
-- 1. shop_items 테이블 (상점 아이템 정의)
-- =====================================================
CREATE TABLE IF NOT EXISTS shop_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    name_ko VARCHAR(100) NOT NULL,
    category VARCHAR(20) NOT NULL,  -- 'building', 'tree', 'decoration', 'fence', 'farm'
    rarity VARCHAR(20) DEFAULT 'common',  -- 'common', 'uncommon', 'rare', 'epic'
    price INTEGER NOT NULL DEFAULT 0,
    max_quantity INTEGER DEFAULT NULL,  -- NULL = 무제한
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- 2. user_placed_items 테이블 (배치된 아이템)
-- =====================================================
CREATE TABLE IF NOT EXISTS user_placed_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    item_code VARCHAR(50) NOT NULL REFERENCES shop_items(code) ON DELETE CASCADE,
    tile_x INTEGER NOT NULL,
    tile_y INTEGER NOT NULL,
    rotation INTEGER DEFAULT 0,
    data JSONB DEFAULT '{}',  -- 밭: { cropCode, plantedAt, stage }
    placed_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_shop_items_code ON shop_items(code);
CREATE INDEX IF NOT EXISTS idx_shop_items_category ON shop_items(category);
CREATE INDEX IF NOT EXISTS idx_placed_items_user ON user_placed_items(user_id);
CREATE INDEX IF NOT EXISTS idx_placed_items_code ON user_placed_items(item_code);

-- =====================================================
-- 3. RLS Policies
-- =====================================================
ALTER TABLE shop_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_placed_items ENABLE ROW LEVEL SECURITY;

-- shop_items는 모두 읽기 가능
CREATE POLICY "Anyone can view shop items" ON shop_items
    FOR SELECT USING (true);

CREATE POLICY "Service role can manage shop items" ON shop_items
    FOR ALL USING (auth.role() = 'service_role');

-- user_placed_items는 본인만
CREATE POLICY "Users can view own placed items" ON user_placed_items
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own placed items" ON user_placed_items
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own placed items" ON user_placed_items
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own placed items" ON user_placed_items
    FOR DELETE USING (auth.uid() = user_id);

CREATE POLICY "Service role can manage placed items" ON user_placed_items
    FOR ALL USING (auth.role() = 'service_role');

-- 권한 부여
GRANT ALL ON shop_items TO service_role;
GRANT ALL ON user_placed_items TO service_role;

-- =====================================================
-- 4. 초기 상점 데이터
-- =====================================================
INSERT INTO shop_items (code, name, name_ko, category, rarity, price, max_quantity, metadata) VALUES
    -- === 건물 (building) ===
    ('house', 'House', '집', 'building', 'common', 0, 1,
     '{"sprite":"buildings/house","width":4,"height":3,"depth":100,"canMove":true,"canDelete":false}'),
    ('well', 'Well', '우물', 'building', 'uncommon', 300, 1,
     '{"sprite":"buildings/well","width":2,"height":2,"depth":100,"canMove":true,"canDelete":false}'),
    ('chicken_coop', 'Chicken Coop', '닭장', 'building', 'uncommon', 500, 1,
     '{"sprite":"buildings/chickenCoop","width":3,"height":3,"depth":100,"canMove":true,"canDelete":false}'),
    ('scarecrow', 'Scarecrow', '허수아비', 'building', 'common', 150, 5,
     '{"sprite":"buildings/scarecrow","width":1,"height":2,"depth":100,"canMove":true,"canDelete":true}'),
    ('barn', 'Barn', '헛간', 'building', 'rare', 1000, 1,
     '{"sprite":"buildings/barn","width":5,"height":4,"depth":100,"canMove":true,"canDelete":false}'),

    -- === 밭 (farm) ===
    ('farm_plot', 'Farm Plot', '밭', 'farm', 'common', 50, NULL,
     '{"sprite":"tiles/farmland","width":1,"height":1,"depth":10,"canMove":false,"canDelete":true}'),

    -- === 나무 (tree) ===
    ('tree_oak', 'Oak Tree', '참나무', 'tree', 'common', 100, NULL,
     '{"sprite":"trees/oak","width":2,"height":3,"depth":80,"canMove":true,"canDelete":true}'),
    ('tree_pine', 'Pine Tree', '소나무', 'tree', 'common', 100, NULL,
     '{"sprite":"trees/pine","width":2,"height":3,"depth":80,"canMove":true,"canDelete":true}'),
    ('tree_apple', 'Apple Tree', '사과나무', 'tree', 'rare', 300, NULL,
     '{"sprite":"trees/apple","width":2,"height":3,"depth":80,"canMove":true,"canDelete":true}'),

    -- === 장식 (decoration) ===
    ('flower_red', 'Red Flower', '빨간 꽃', 'decoration', 'common', 20, NULL,
     '{"sprite":"decorations/flower_red","width":1,"height":1,"depth":30,"canMove":true,"canDelete":true}'),
    ('flower_yellow', 'Yellow Flower', '노란 꽃', 'decoration', 'common', 20, NULL,
     '{"sprite":"decorations/flower_yellow","width":1,"height":1,"depth":30,"canMove":true,"canDelete":true}'),
    ('flower_purple', 'Purple Flower', '보라 꽃', 'decoration', 'common', 20, NULL,
     '{"sprite":"decorations/flower_purple","width":1,"height":1,"depth":30,"canMove":true,"canDelete":true}'),
    ('grass_tuft', 'Grass Tuft', '잔디', 'decoration', 'common', 10, NULL,
     '{"sprite":"decorations/grass","width":1,"height":1,"depth":30,"canMove":true,"canDelete":true}'),
    ('hay_pile', 'Hay Pile', '건초 더미', 'decoration', 'common', 50, NULL,
     '{"sprite":"decorations/hay","width":1,"height":1,"depth":30,"canMove":true,"canDelete":true}'),
    ('rock_small', 'Small Rock', '작은 바위', 'decoration', 'common', 30, NULL,
     '{"sprite":"decorations/rock","width":1,"height":1,"depth":30,"canMove":true,"canDelete":true}'),

    -- === 울타리 (fence) ===
    ('fence_wood', 'Wood Fence', '나무 울타리', 'fence', 'common', 10, NULL,
     '{"sprite":"fences/wood","width":1,"height":1,"depth":40,"canMove":false,"canDelete":true}'),
    ('fence_stone', 'Stone Fence', '돌 울타리', 'fence', 'uncommon', 30, NULL,
     '{"sprite":"fences/stone","width":1,"height":1,"depth":40,"canMove":false,"canDelete":true}')
ON CONFLICT (code) DO UPDATE SET
    name = EXCLUDED.name,
    name_ko = EXCLUDED.name_ko,
    category = EXCLUDED.category,
    rarity = EXCLUDED.rarity,
    price = EXCLUDED.price,
    max_quantity = EXCLUDED.max_quantity,
    metadata = EXCLUDED.metadata;

-- =====================================================
-- 5. 기존 데이터 리셋
-- =====================================================
-- customization_data와 farm_slots 초기화
UPDATE user_farm SET
    customization_data = '{}',
    farm_slots = '[]';

-- user_placed_items 비우기 (새 테이블이므로 이미 비어있음)
DELETE FROM user_placed_items;

-- =====================================================
-- 6. 모든 기존 유저에게 기본 아이템 배치
-- =====================================================
-- 집 배치 (위치: 23, 2)
INSERT INTO user_placed_items (user_id, item_code, tile_x, tile_y, data)
SELECT id, 'house', 23, 2, '{}'
FROM users
WHERE id IN (SELECT user_id FROM user_farm WHERE character_created = true)
ON CONFLICT DO NOTHING;

-- 밭 9개 배치 (3x3, 시작 위치: 10, 8)
INSERT INTO user_placed_items (user_id, item_code, tile_x, tile_y, data)
SELECT u.id, 'farm_plot', 10 + (g % 3), 8 + (g / 3), '{}'
FROM users u
CROSS JOIN generate_series(0, 8) AS g
WHERE u.id IN (SELECT user_id FROM user_farm WHERE character_created = true)
ON CONFLICT DO NOTHING;

-- =====================================================
-- 7. 신규 유저 생성 시 자동 배치용 함수
-- =====================================================
CREATE OR REPLACE FUNCTION initialize_user_farm_items()
RETURNS TRIGGER AS $$
BEGIN
    -- 새 캐릭터 생성 시 기본 아이템 배치
    IF NEW.character_created = true AND (OLD.character_created = false OR OLD.character_created IS NULL) THEN
        -- 집 배치
        INSERT INTO user_placed_items (user_id, item_code, tile_x, tile_y)
        VALUES (NEW.user_id, 'house', 23, 2)
        ON CONFLICT DO NOTHING;

        -- 밭 9개 배치
        INSERT INTO user_placed_items (user_id, item_code, tile_x, tile_y)
        SELECT NEW.user_id, 'farm_plot', 10 + (g % 3), 8 + (g / 3)
        FROM generate_series(0, 8) AS g
        ON CONFLICT DO NOTHING;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 기존 트리거가 있으면 삭제
DROP TRIGGER IF EXISTS trigger_initialize_farm_items ON user_farm;

-- 트리거 생성
CREATE TRIGGER trigger_initialize_farm_items
    AFTER INSERT OR UPDATE ON user_farm
    FOR EACH ROW
    EXECUTE FUNCTION initialize_user_farm_items();
