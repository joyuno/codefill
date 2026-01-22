-- =====================================================
-- 건물 크기 축소 - 맵에 배치하기 쉽도록
-- 이미지는 스케일링되어 표시됨
-- =====================================================

-- house: 8×10 → 4×4
UPDATE shop_items
SET metadata = '{
  "sprite": "buildings/house",
  "width": 4,
  "height": 4,
  "depth": 100,
  "canMove": true,
  "canDelete": false,
  "collisionWidth": 4,
  "collisionHeight": 4,
  "collisionOffsetX": 0,
  "collisionOffsetY": 0
}'::jsonb
WHERE code = 'house';

-- farmer_house_1: 8×10 → 5×6
UPDATE shop_items
SET metadata = '{
  "sprite": "buildings/farmer_house_1",
  "width": 5,
  "height": 6,
  "depth": 100,
  "canMove": true,
  "canDelete": true,
  "collisionWidth": 4,
  "collisionHeight": 2,
  "collisionOffsetX": 0,
  "collisionOffsetY": 4
}'::jsonb
WHERE code = 'farmer_house_1';

-- farmer_house_2: 10×9 → 6×5
UPDATE shop_items
SET metadata = '{
  "sprite": "buildings/farmer_house_2",
  "width": 6,
  "height": 5,
  "depth": 100,
  "canMove": true,
  "canDelete": true,
  "collisionWidth": 5,
  "collisionHeight": 2,
  "collisionOffsetX": 0,
  "collisionOffsetY": 3
}'::jsonb
WHERE code = 'farmer_house_2';

-- barn: 8×10 → 5×6
UPDATE shop_items
SET metadata = '{
  "sprite": "buildings/barn",
  "width": 5,
  "height": 6,
  "depth": 100,
  "canMove": true,
  "canDelete": true,
  "collisionWidth": 4,
  "collisionHeight": 2,
  "collisionOffsetX": 0,
  "collisionOffsetY": 4
}'::jsonb
WHERE code = 'barn';

-- barn_small: 8×10 → 5×6
UPDATE shop_items
SET metadata = '{
  "sprite": "buildings/barn_small",
  "width": 5,
  "height": 6,
  "depth": 100,
  "canMove": true,
  "canDelete": true,
  "collisionWidth": 4,
  "collisionHeight": 2,
  "collisionOffsetX": 0,
  "collisionOffsetY": 4
}'::jsonb
WHERE code = 'barn_small';

-- chicken_coop: 4×5 → 3×4
UPDATE shop_items
SET metadata = '{
  "sprite": "buildings/chicken_coop",
  "width": 3,
  "height": 4,
  "depth": 100,
  "canMove": true,
  "canDelete": true,
  "collisionWidth": 3,
  "collisionHeight": 2,
  "collisionOffsetX": 0,
  "collisionOffsetY": 2
}'::jsonb
WHERE code = 'chicken_coop';

-- stable: 10×8 → 6×5
UPDATE shop_items
SET metadata = '{
  "sprite": "buildings/stable",
  "width": 6,
  "height": 5,
  "depth": 100,
  "canMove": true,
  "canDelete": true,
  "collisionWidth": 6,
  "collisionHeight": 3,
  "collisionOffsetX": 0,
  "collisionOffsetY": 2
}'::jsonb
WHERE code = 'stable';

-- silos: 7×14 → 4×8
UPDATE shop_items
SET metadata = '{
  "sprite": "buildings/silos",
  "width": 4,
  "height": 8,
  "depth": 100,
  "canMove": true,
  "canDelete": true,
  "collisionWidth": 3,
  "collisionHeight": 2,
  "collisionOffsetX": 0,
  "collisionOffsetY": 6
}'::jsonb
WHERE code = 'silos';

-- well: 2×2 유지 (작은 건물)
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

-- scarecrow: 3×3 → 2×3
UPDATE shop_items
SET metadata = '{
  "sprite": "buildings/scarecrow",
  "width": 2,
  "height": 3,
  "depth": 100,
  "canMove": true,
  "canDelete": true,
  "collisionWidth": 1,
  "collisionHeight": 1,
  "collisionOffsetX": 0,
  "collisionOffsetY": 2
}'::jsonb
WHERE code = 'scarecrow';

-- doghouse: 2×3 유지
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
-- 작업대 (약간 축소)
-- =====================================================

-- stone_oven: 5×4 → 4×3
UPDATE shop_items
SET metadata = '{
  "sprite": "buildings/stone_oven",
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
WHERE code = 'stone_oven';

-- cheese_machine: 4×3 → 3×2
UPDATE shop_items
SET metadata = '{
  "sprite": "buildings/cheese_machine",
  "width": 3,
  "height": 2,
  "depth": 100,
  "canMove": true,
  "canDelete": true,
  "collisionWidth": 3,
  "collisionHeight": 2,
  "collisionOffsetX": 0,
  "collisionOffsetY": 0
}'::jsonb
WHERE code = 'cheese_machine';

-- diy_crafting_table: 3×3 → 2×2
UPDATE shop_items
SET metadata = '{
  "sprite": "buildings/diy_crafting_table",
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
WHERE code = 'diy_crafting_table';

-- tailor_table: 3×3 → 2×2
UPDATE shop_items
SET metadata = '{
  "sprite": "buildings/tailor_table",
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
WHERE code = 'tailor_table';

-- woodwork_table: 5×4 → 4×3
UPDATE shop_items
SET metadata = '{
  "sprite": "buildings/woodwork_table",
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
WHERE code = 'woodwork_table';

-- =====================================================
-- 마켓 가판대 (약간 축소)
-- =====================================================

-- market_stand_blue: 5×2 → 4×2
UPDATE shop_items
SET metadata = '{
  "sprite": "buildings/market_stand_blue",
  "width": 4,
  "height": 2,
  "depth": 100,
  "canMove": true,
  "canDelete": true,
  "collisionWidth": 4,
  "collisionHeight": 2,
  "collisionOffsetX": 0,
  "collisionOffsetY": 0
}'::jsonb
WHERE code = 'market_stand_blue';

-- market_stand_green: 5×2 → 4×2
UPDATE shop_items
SET metadata = '{
  "sprite": "buildings/market_stand_green",
  "width": 4,
  "height": 2,
  "depth": 100,
  "canMove": true,
  "canDelete": true,
  "collisionWidth": 4,
  "collisionHeight": 2,
  "collisionOffsetX": 0,
  "collisionOffsetY": 0
}'::jsonb
WHERE code = 'market_stand_green';

-- market_stand_yellow: 5×4 → 4×3
UPDATE shop_items
SET metadata = '{
  "sprite": "buildings/market_stand_yellow",
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
WHERE code = 'market_stand_yellow';

-- market_stand_pink: 5×2 → 4×2
UPDATE shop_items
SET metadata = '{
  "sprite": "buildings/market_stand_pink",
  "width": 4,
  "height": 2,
  "depth": 100,
  "canMove": true,
  "canDelete": true,
  "collisionWidth": 4,
  "collisionHeight": 2,
  "collisionOffsetX": 0,
  "collisionOffsetY": 0
}'::jsonb
WHERE code = 'market_stand_pink';
