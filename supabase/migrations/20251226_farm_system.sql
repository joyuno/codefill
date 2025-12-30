-- =====================================================
-- Farm System Tables
-- =====================================================

-- user_farm: 사용자별 농장 상태
CREATE TABLE IF NOT EXISTS user_farm (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE REFERENCES users(id) ON DELETE CASCADE,

    -- 캐릭터 정보
    character_created BOOLEAN DEFAULT FALSE,
    character_data JSONB DEFAULT '{}',
    -- character_data 구조:
    -- {
    --   "name": "농부이름",
    --   "hair": "style_01",
    --   "hair_color": "#8B4513",
    --   "face": "face_01",
    --   "outfit": "outfit_casual",
    --   "outfit_color": "#4169E1",
    --   "farm_name": "나의 농장"
    -- }

    -- 농장 상태
    farm_unlocked BOOLEAN DEFAULT FALSE,
    farm_level INTEGER DEFAULT 1,
    gold INTEGER DEFAULT 0,
    farm_size INTEGER DEFAULT 4,  -- 2x2 = 4칸
    house_level INTEGER DEFAULT 1,

    -- 농장 슬롯 (작물 심기)
    farm_slots JSONB DEFAULT '[]',
    -- farm_slots 구조:
    -- [
    --   {"slot": 0, "crop_code": "carrot", "planted_at": "2025-01-01T10:00:00Z", "stage": 2},
    --   {"slot": 1, "crop_code": null, "planted_at": null, "stage": 0}
    -- ]

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- farm_items: 작물/아이템 정의 (마스터 테이블)
CREATE TABLE IF NOT EXISTS farm_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    name_ko VARCHAR(100),
    type VARCHAR(50) NOT NULL,  -- 'crop', 'seed', 'decoration'
    rarity VARCHAR(20) DEFAULT 'common',  -- common, uncommon, rare, epic
    image_url TEXT,

    -- 경제 시스템
    seed_cost INTEGER DEFAULT 0,
    sell_price INTEGER DEFAULT 0,
    xp_reward INTEGER DEFAULT 0,

    -- 성장 시간 (초)
    grow_time_seconds INTEGER DEFAULT 120,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- user_inventory: 사용자 인벤토리
CREATE TABLE IF NOT EXISTS user_inventory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    item_code VARCHAR(50) NOT NULL,
    quantity INTEGER DEFAULT 0,

    UNIQUE(user_id, item_code)
);

-- =====================================================
-- Indexes
-- =====================================================
CREATE INDEX IF NOT EXISTS idx_user_farm_user_id ON user_farm(user_id);
CREATE INDEX IF NOT EXISTS idx_user_inventory_user_id ON user_inventory(user_id);
CREATE INDEX IF NOT EXISTS idx_farm_items_code ON farm_items(code);
CREATE INDEX IF NOT EXISTS idx_farm_items_type ON farm_items(type);

-- =====================================================
-- RLS Policies
-- =====================================================
ALTER TABLE user_farm ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_inventory ENABLE ROW LEVEL SECURITY;

-- user_farm policies
CREATE POLICY "Users can view own farm" ON user_farm
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can update own farm" ON user_farm
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own farm" ON user_farm
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- user_inventory policies
CREATE POLICY "Users can view own inventory" ON user_inventory
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can update own inventory" ON user_inventory
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own inventory" ON user_inventory
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own inventory" ON user_inventory
    FOR DELETE USING (auth.uid() = user_id);

-- farm_items은 모든 사용자가 읽기 가능 (마스터 데이터)
ALTER TABLE farm_items ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Anyone can view farm items" ON farm_items
    FOR SELECT USING (true);

-- =====================================================
-- 테이블 권한 부여 (백엔드 service_role 전용)
-- =====================================================
GRANT ALL ON user_farm TO service_role;
GRANT ALL ON user_inventory TO service_role;
GRANT ALL ON farm_items TO service_role;

-- =====================================================
-- Service Role RLS 정책 (백엔드 API에서 접근 가능)
-- =====================================================
CREATE POLICY "Service role can manage user_farm" ON user_farm
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role can manage user_inventory" ON user_inventory
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role can manage farm_items" ON farm_items
    FOR ALL USING (auth.role() = 'service_role');

-- =====================================================
-- 초기 작물 데이터 시딩
-- =====================================================
INSERT INTO farm_items (code, name, name_ko, type, rarity, seed_cost, sell_price, xp_reward, grow_time_seconds) VALUES
    -- Common 작물 (2-3분)
    ('carrot', 'Carrot', '당근', 'crop', 'common', 10, 25, 5, 120),
    ('radish', 'Radish', '무', 'crop', 'common', 10, 22, 5, 120),
    ('potato', 'Potato', '감자', 'crop', 'common', 12, 30, 6, 150),
    ('wheat', 'Wheat', '밀', 'crop', 'common', 8, 20, 4, 180),

    -- Uncommon 작물 (3-4분)
    ('tomato', 'Tomato', '토마토', 'crop', 'uncommon', 15, 35, 8, 180),
    ('onion', 'Onion', '양파', 'crop', 'uncommon', 14, 35, 8, 180),
    ('cabbage', 'Cabbage', '양배추', 'crop', 'uncommon', 18, 45, 10, 240),

    -- Rare 작물 (4-5분)
    ('strawberry', 'Strawberry', '딸기', 'crop', 'rare', 25, 60, 15, 240),
    ('corn', 'Corn', '옥수수', 'crop', 'rare', 20, 50, 12, 300),

    -- Epic 작물 (10분)
    ('pumpkin', 'Pumpkin', '호박', 'crop', 'epic', 50, 120, 30, 600)
ON CONFLICT (code) DO UPDATE SET
    name = EXCLUDED.name,
    name_ko = EXCLUDED.name_ko,
    seed_cost = EXCLUDED.seed_cost,
    sell_price = EXCLUDED.sell_price,
    xp_reward = EXCLUDED.xp_reward,
    grow_time_seconds = EXCLUDED.grow_time_seconds;

-- =====================================================
-- 농장 확장 비용 테이블 (참조용)
-- =====================================================
-- 2x2 (4칸): 기본 (무료)
-- 3x3 (9칸): 500 골드
-- 4x4 (16칸): 1500 골드
-- 5x5 (25칸): 4000 골드
-- 6x6 (36칸): 8000 골드

-- =====================================================
-- Trigger: updated_at 자동 업데이트
-- =====================================================
CREATE OR REPLACE FUNCTION update_farm_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_user_farm_updated_at
    BEFORE UPDATE ON user_farm
    FOR EACH ROW
    EXECUTE FUNCTION update_farm_updated_at();
