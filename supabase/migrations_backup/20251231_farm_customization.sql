-- =====================================================
-- Farm Customization System
-- 농장 커스터마이징 데이터 저장 (장식, 건물 위치/스킨, 지형)
-- =====================================================

-- user_farm 테이블에 customization_data 컬럼 추가
ALTER TABLE user_farm
ADD COLUMN IF NOT EXISTS customization_data JSONB DEFAULT '{}';

-- 컬럼 설명 추가
COMMENT ON COLUMN user_farm.customization_data IS
'농장 커스터마이징 데이터: decorations(장식), buildings(건물 위치/스킨), terrain(지형)';

-- customization_data 구조:
-- {
--   "decorations": [
--     { "id": "flower_blue_5_10_1234", "item_key": "flower_blue", "tile_x": 5, "tile_y": 10 }
--   ],
--   "buildings": {
--     "house": { "x": 22, "y": 2, "skin": "default" },
--     "coop": { "x": 22, "y": 10, "skin": "default" },
--     "well": { "x": 26, "y": 6, "skin": "default" }
--   },
--   "terrain": []
-- }
