-- =====================================================
-- Fix shop_items metadata: 이미지 크기 + 충돌 영역 정확히 설정
-- 이미지 분석 기반 실제 충돌 영역 적용
-- =====================================================

-- house (Farmer_House_1): 이미지 8×5, 충돌 6×3 (하단 벽 부분)
UPDATE shop_items
SET metadata = '{
  "sprite": "buildings/house",
  "width": 8,
  "height": 5,
  "depth": 100,
  "canMove": true,
  "canDelete": false,
  "collisionWidth": 6,
  "collisionHeight": 3,
  "collisionOffsetX": 1,
  "collisionOffsetY": 2
}'::jsonb
WHERE code = 'house';

-- well: 이미지 2×2, 충돌 전체
UPDATE shop_items
SET metadata = '{
  "sprite": "buildings/well",
  "width": 2,
  "height": 2,
  "depth": 100,
  "canMove": true,
  "canDelete": true,
  "collisionWidth": 2,
  "collisionHeight": 2,
  "collisionOffsetX": 0,
  "collisionOffsetY": 0
}'::jsonb
WHERE code = 'well';

-- chicken_coop: 이미지 4×5, 충돌 4×2 (하단)
UPDATE shop_items
SET metadata = '{
  "sprite": "buildings/chicken_coop",
  "width": 4,
  "height": 5,
  "depth": 100,
  "canMove": true,
  "canDelete": true,
  "collisionWidth": 4,
  "collisionHeight": 2,
  "collisionOffsetX": 0,
  "collisionOffsetY": 3
}'::jsonb
WHERE code = 'chicken_coop';

-- scarecrow: 이미지 3×3, 충돌 1×1 (발 부분)
UPDATE shop_items
SET metadata = '{
  "sprite": "buildings/scarecrow",
  "width": 3,
  "height": 3,
  "depth": 100,
  "canMove": true,
  "canDelete": true,
  "collisionWidth": 1,
  "collisionHeight": 1,
  "collisionOffsetX": 1,
  "collisionOffsetY": 2
}'::jsonb
WHERE code = 'scarecrow';

-- barn: 이미지 8×10, 충돌 6×4 (하단)
UPDATE shop_items
SET metadata = '{
  "sprite": "buildings/barn",
  "width": 8,
  "height": 10,
  "depth": 100,
  "canMove": true,
  "canDelete": true,
  "collisionWidth": 6,
  "collisionHeight": 4,
  "collisionOffsetX": 1,
  "collisionOffsetY": 6
}'::jsonb
WHERE code = 'barn';

-- =====================================================
-- 새 건물들
-- =====================================================

-- farmer_house_1: 이미지 8×10, 충돌 6×4
UPDATE shop_items
SET metadata = '{
  "sprite": "buildings/farmer_house_1",
  "width": 8,
  "height": 10,
  "depth": 100,
  "canMove": true,
  "canDelete": true,
  "collisionWidth": 6,
  "collisionHeight": 4,
  "collisionOffsetX": 1,
  "collisionOffsetY": 6
}'::jsonb
WHERE code = 'farmer_house_1';

-- farmer_house_2: 이미지 10×9, 충돌 9×4
UPDATE shop_items
SET metadata = '{
  "sprite": "buildings/farmer_house_2",
  "width": 10,
  "height": 9,
  "depth": 100,
  "canMove": true,
  "canDelete": true,
  "collisionWidth": 9,
  "collisionHeight": 4,
  "collisionOffsetX": 0,
  "collisionOffsetY": 5
}'::jsonb
WHERE code = 'farmer_house_2';

-- barn_small: 이미지 8×10, 충돌 6×4
UPDATE shop_items
SET metadata = '{
  "sprite": "buildings/barn_small",
  "width": 8,
  "height": 10,
  "depth": 100,
  "canMove": true,
  "canDelete": true,
  "collisionWidth": 6,
  "collisionHeight": 4,
  "collisionOffsetX": 1,
  "collisionOffsetY": 6
}'::jsonb
WHERE code = 'barn_small';

-- stable: 이미지 10×8, 충돌 10×6
UPDATE shop_items
SET metadata = '{
  "sprite": "buildings/stable",
  "width": 10,
  "height": 8,
  "depth": 100,
  "canMove": true,
  "canDelete": true,
  "collisionWidth": 10,
  "collisionHeight": 6,
  "collisionOffsetX": 0,
  "collisionOffsetY": 2
}'::jsonb
WHERE code = 'stable';

-- silos: 이미지 7×14, 충돌 5×3 (하단 기초)
UPDATE shop_items
SET metadata = '{
  "sprite": "buildings/silos",
  "width": 7,
  "height": 14,
  "depth": 100,
  "canMove": true,
  "canDelete": true,
  "collisionWidth": 5,
  "collisionHeight": 3,
  "collisionOffsetX": 1,
  "collisionOffsetY": 11
}'::jsonb
WHERE code = 'silos';

-- doghouse: 이미지 2×3, 충돌 2×2
UPDATE shop_items
SET metadata = '{
  "sprite": "buildings/doghouse",
  "width": 2,
  "height": 3,
  "depth": 100,
  "canMove": true,
  "canDelete": true,
  "collisionWidth": 2,
  "collisionHeight": 2,
  "collisionOffsetX": 0,
  "collisionOffsetY": 1
}'::jsonb
WHERE code = 'doghouse';

-- =====================================================
-- 작업대
-- =====================================================

-- stone_oven: 이미지 5×4, 충돌 5×3
UPDATE shop_items
SET metadata = '{
  "sprite": "buildings/stone_oven",
  "width": 5,
  "height": 4,
  "depth": 100,
  "canMove": true,
  "canDelete": true,
  "collisionWidth": 5,
  "collisionHeight": 3,
  "collisionOffsetX": 0,
  "collisionOffsetY": 1
}'::jsonb
WHERE code = 'stone_oven';

-- cheese_machine: 이미지 4×3, 충돌 4×2
UPDATE shop_items
SET metadata = '{
  "sprite": "buildings/cheese_machine",
  "width": 4,
  "height": 3,
  "depth": 100,
  "canMove": true,
  "canDelete": true,
  "collisionWidth": 4,
  "collisionHeight": 2,
  "collisionOffsetX": 0,
  "collisionOffsetY": 1
}'::jsonb
WHERE code = 'cheese_machine';

-- diy_crafting_table: 이미지 3×3, 충돌 3×2
UPDATE shop_items
SET metadata = '{
  "sprite": "buildings/diy_crafting_table",
  "width": 3,
  "height": 3,
  "depth": 100,
  "canMove": true,
  "canDelete": true,
  "collisionWidth": 3,
  "collisionHeight": 2,
  "collisionOffsetX": 0,
  "collisionOffsetY": 1
}'::jsonb
WHERE code = 'diy_crafting_table';

-- tailor_table: 이미지 3×3, 충돌 3×2
UPDATE shop_items
SET metadata = '{
  "sprite": "buildings/tailor_table",
  "width": 3,
  "height": 3,
  "depth": 100,
  "canMove": true,
  "canDelete": true,
  "collisionWidth": 3,
  "collisionHeight": 2,
  "collisionOffsetX": 0,
  "collisionOffsetY": 1
}'::jsonb
WHERE code = 'tailor_table';

-- woodwork_table: 이미지 5×4, 충돌 5×3
UPDATE shop_items
SET metadata = '{
  "sprite": "buildings/woodwork_table",
  "width": 5,
  "height": 4,
  "depth": 100,
  "canMove": true,
  "canDelete": true,
  "collisionWidth": 5,
  "collisionHeight": 3,
  "collisionOffsetX": 0,
  "collisionOffsetY": 1
}'::jsonb
WHERE code = 'woodwork_table';

-- =====================================================
-- 마켓 가판대
-- =====================================================

-- market_stand_blue: 이미지 5×2, 충돌 전체
UPDATE shop_items
SET metadata = '{
  "sprite": "buildings/market_stand_blue",
  "width": 5,
  "height": 2,
  "depth": 100,
  "canMove": true,
  "canDelete": true,
  "collisionWidth": 5,
  "collisionHeight": 2,
  "collisionOffsetX": 0,
  "collisionOffsetY": 0
}'::jsonb
WHERE code = 'market_stand_blue';

-- market_stand_green: 이미지 5×2, 충돌 전체
UPDATE shop_items
SET metadata = '{
  "sprite": "buildings/market_stand_green",
  "width": 5,
  "height": 2,
  "depth": 100,
  "canMove": true,
  "canDelete": true,
  "collisionWidth": 5,
  "collisionHeight": 2,
  "collisionOffsetX": 0,
  "collisionOffsetY": 0
}'::jsonb
WHERE code = 'market_stand_green';

-- market_stand_yellow: 이미지 5×4, 충돌 5×2 (하단 테이블)
UPDATE shop_items
SET metadata = '{
  "sprite": "buildings/market_stand_yellow",
  "width": 5,
  "height": 4,
  "depth": 100,
  "canMove": true,
  "canDelete": true,
  "collisionWidth": 5,
  "collisionHeight": 2,
  "collisionOffsetX": 0,
  "collisionOffsetY": 2
}'::jsonb
WHERE code = 'market_stand_yellow';

-- market_stand_pink: 이미지 5×2, 충돌 전체
UPDATE shop_items
SET metadata = '{
  "sprite": "buildings/market_stand_pink",
  "width": 5,
  "height": 2,
  "depth": 100,
  "canMove": true,
  "canDelete": true,
  "collisionWidth": 5,
  "collisionHeight": 2,
  "collisionOffsetX": 0,
  "collisionOffsetY": 0
}'::jsonb
WHERE code = 'market_stand_pink';
