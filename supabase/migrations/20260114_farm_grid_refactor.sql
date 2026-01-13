-- =====================================================
-- Farm Grid System Refactoring
-- farm_plot 개별 배치 방식 -> farm_slots 그리드 방식으로 전환
-- 확장 단계: 1x1 -> 2x2 -> 3x3 -> 4x4 -> 5x5 (1, 4, 9, 16, 25칸)
-- =====================================================

-- =====================================================
-- 1. farm_slots 컬럼 구조 확인 및 업데이트
-- =====================================================
-- farm_slots 구조:
-- [
--   {"slot": 0, "cropCode": "carrot", "plantedAt": "2025-01-01T10:00:00Z", "growTimeSeconds": 120},
--   {"slot": 1, "cropCode": null, "plantedAt": null, "growTimeSeconds": null}
-- ]

-- =====================================================
-- 2. farm_slots 초기화 함수
-- =====================================================
CREATE OR REPLACE FUNCTION initialize_farm_slots(size INTEGER)
RETURNS JSONB AS $$
DECLARE
    slots JSONB := '[]'::jsonb;
    i INTEGER;
BEGIN
    FOR i IN 0..(size - 1) LOOP
        slots := slots || jsonb_build_object(
            'slot', i,
            'cropCode', NULL,
            'plantedAt', NULL,
            'growTimeSeconds', NULL
        );
    END LOOP;
    RETURN slots;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- 3. 기존 farm_plot 데이터를 farm_slots로 마이그레이션
-- =====================================================
-- 기존 유저의 farm_plot 작물 데이터를 farm_slots로 이관
WITH farm_plot_data AS (
    SELECT
        upi.user_id,
        ROW_NUMBER() OVER (PARTITION BY upi.user_id ORDER BY upi.tile_y, upi.tile_x) - 1 as slot,
        upi.data->>'cropCode' as crop_code,
        upi.data->>'plantedAt' as planted_at,
        COALESCE(fi.grow_time_seconds, 120) as grow_time_seconds
    FROM user_placed_items upi
    LEFT JOIN farm_items fi ON fi.code = upi.data->>'cropCode'
    WHERE upi.item_code = 'farm_plot'
),
aggregated AS (
    SELECT
        user_id,
        jsonb_agg(
            jsonb_build_object(
                'slot', slot,
                'cropCode', crop_code,
                'plantedAt', planted_at,
                'growTimeSeconds', CASE WHEN crop_code IS NOT NULL THEN grow_time_seconds ELSE NULL END
            ) ORDER BY slot
        ) as slots
    FROM farm_plot_data
    GROUP BY user_id
)
UPDATE user_farm uf
SET farm_slots = a.slots,
    farm_size = jsonb_array_length(a.slots)
FROM aggregated a
WHERE uf.user_id = a.user_id;

-- farm_plot이 없는 신규 유저는 초기 farm_slots 설정 (1칸)
UPDATE user_farm
SET farm_slots = initialize_farm_slots(1),
    farm_size = 1
WHERE (farm_slots IS NULL OR farm_slots = '[]'::jsonb)
  AND character_created = true;

-- 캐릭터 미생성 유저는 빈 상태 유지
UPDATE user_farm
SET farm_slots = '[]'::jsonb,
    farm_size = 1
WHERE character_created = false;

-- =====================================================
-- 4. farm_plot 관련 데이터 정리
-- =====================================================
-- user_placed_items에서 farm_plot 항목 삭제
DELETE FROM user_placed_items WHERE item_code = 'farm_plot';

-- shop_items에서 farm_plot 항목 삭제
DELETE FROM shop_items WHERE code = 'farm_plot';

-- =====================================================
-- 5. 신규 유저용 트리거 업데이트
-- =====================================================
CREATE OR REPLACE FUNCTION initialize_user_farm_items()
RETURNS TRIGGER AS $$
BEGIN
    -- 새 캐릭터 생성 시 기본 아이템 배치
    IF NEW.character_created = true AND (OLD.character_created = false OR OLD.character_created IS NULL) THEN
        -- 집만 배치 (farm_plot 제거됨)
        INSERT INTO user_placed_items (user_id, item_code, tile_x, tile_y)
        VALUES (NEW.user_id, 'house', 23, 2)
        ON CONFLICT DO NOTHING;

        -- farm_slots 초기화 (1x1 = 1칸으로 시작)
        UPDATE user_farm
        SET farm_slots = initialize_farm_slots(1),
            farm_size = 1
        WHERE user_id = NEW.user_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 기존 트리거 재생성
DROP TRIGGER IF EXISTS trigger_initialize_farm_items ON user_farm;
CREATE TRIGGER trigger_initialize_farm_items
    AFTER INSERT OR UPDATE ON user_farm
    FOR EACH ROW
    EXECUTE FUNCTION initialize_user_farm_items();

-- =====================================================
-- 6. farm_slots 확장 헬퍼 함수
-- =====================================================
CREATE OR REPLACE FUNCTION expand_farm_slots(current_slots JSONB, new_size INTEGER)
RETURNS JSONB AS $$
DECLARE
    current_size INTEGER;
    result JSONB;
    i INTEGER;
BEGIN
    current_size := jsonb_array_length(current_slots);
    result := current_slots;

    -- 새 슬롯 추가
    FOR i IN current_size..(new_size - 1) LOOP
        result := result || jsonb_build_object(
            'slot', i,
            'cropCode', NULL,
            'plantedAt', NULL,
            'growTimeSeconds', NULL
        );
    END LOOP;

    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- 7. 작물 심기/수확 헬퍼 함수
-- =====================================================
-- 특정 슬롯에 작물 심기
CREATE OR REPLACE FUNCTION plant_crop_on_slot(
    slots JSONB,
    slot_index INTEGER,
    crop_code VARCHAR,
    grow_time INTEGER
)
RETURNS JSONB AS $$
DECLARE
    result JSONB := '[]'::jsonb;
    slot JSONB;
    i INTEGER;
BEGIN
    FOR i IN 0..(jsonb_array_length(slots) - 1) LOOP
        slot := slots->i;
        IF i = slot_index THEN
            slot := jsonb_set(slot, '{cropCode}', to_jsonb(crop_code));
            slot := jsonb_set(slot, '{plantedAt}', to_jsonb(NOW()::TEXT));
            slot := jsonb_set(slot, '{growTimeSeconds}', to_jsonb(grow_time));
        END IF;
        result := result || slot;
    END LOOP;
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- 특정 슬롯 수확 (초기화)
CREATE OR REPLACE FUNCTION harvest_slot(slots JSONB, slot_index INTEGER)
RETURNS JSONB AS $$
DECLARE
    result JSONB := '[]'::jsonb;
    slot JSONB;
    i INTEGER;
BEGIN
    FOR i IN 0..(jsonb_array_length(slots) - 1) LOOP
        slot := slots->i;
        IF i = slot_index THEN
            slot := jsonb_set(slot, '{cropCode}', 'null'::jsonb);
            slot := jsonb_set(slot, '{plantedAt}', 'null'::jsonb);
            slot := jsonb_set(slot, '{growTimeSeconds}', 'null'::jsonb);
        END IF;
        result := result || slot;
    END LOOP;
    RETURN result;
END;
$$ LANGUAGE plpgsql;
