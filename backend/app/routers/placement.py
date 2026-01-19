"""
Unified Placement API Router
통합 배치 시스템 API
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import Optional
from uuid import UUID
from datetime import datetime, timezone
import json

from ..database import get_db
from ..dependencies import get_current_user_id
from ..models.placement import (
    ItemMetadata,
    PlacedItemResponse,
    PlacedItemsListResponse,
    PlaceItemRequest,
    PlaceItemResponse,
    MoveItemRequest,
    MoveItemResponse,
    RemoveItemResponse,
    PlantCropRequest,
    PlantCropResponse,
    HarvestCropResponse,
    MAP_WIDTH_TILES,
    MAP_HEIGHT_TILES,
)
from ..services.farm_service import FarmService

router = APIRouter()


# =====================================================
# Helper Functions (로컬 전용)
# =====================================================

def parse_placed_item(item_data: dict, metadata: ItemMetadata) -> PlacedItemResponse:
    """DB 데이터를 PlacedItemResponse로 변환"""
    data = item_data.get("data", {})
    if isinstance(data, str):
        data = json.loads(data) if data else {}

    return PlacedItemResponse(
        id=str(item_data["id"]),
        itemCode=item_data["item_code"],
        tileX=item_data["tile_x"],
        tileY=item_data["tile_y"],
        rotation=item_data.get("rotation", 0),
        data=data,
        metadata=metadata,
        placedAt=item_data.get("placed_at"),
    )


def get_placed_item(db, item_id: str, user_id: UUID) -> dict:
    """배치된 아이템 조회 (소유권 확인 포함)"""
    result = db.table("user_placed_items").select("*").eq("id", item_id).execute()

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="배치된 아이템을 찾을 수 없습니다"
        )

    item = result.data[0]
    if item["user_id"] != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="이 아이템에 대한 권한이 없습니다"
        )

    return item


def check_placement_valid(db, user_id: UUID, tile_x: int, tile_y: int, width: int, height: int, exclude_id: Optional[str] = None) -> bool:
    """
    배치 위치가 유효한지 확인 (AABB 충돌 감지) - 최적화됨

    Args:
        db: 데이터베이스 연결
        user_id: 사용자 ID
        tile_x, tile_y: 배치 시작 좌표 (좌상단)
        width, height: 아이템 크기 (타일 단위)
        exclude_id: 충돌 검사에서 제외할 아이템 ID (이동 시 사용)

    Returns:
        bool: 배치 가능 여부
    """
    # 맵 범위 체크
    if tile_x < 0 or tile_y < 0 or tile_x + width > MAP_WIDTH_TILES or tile_y + height > MAP_HEIGHT_TILES:
        return False

    # 기존 배치된 아이템 조회
    placed_result = db.table("user_placed_items")\
        .select("id, item_code, tile_x, tile_y")\
        .eq("user_id", str(user_id))\
        .execute()

    if not placed_result.data:
        return True

    # 배치 쿼리로 모든 메타데이터 한 번에 조회 (N+1 방지)
    item_codes = list(set(p["item_code"] for p in placed_result.data))
    metadata_map = FarmService.get_shop_items_metadata(db, item_codes)

    # 배치할 아이템의 충돌 영역
    new_left = tile_x
    new_right = tile_x + width
    new_top = tile_y
    new_bottom = tile_y + height

    # 각 기존 아이템과 AABB 충돌 검사
    for placed in placed_result.data:
        # 자기 자신은 제외 (이동 시)
        if exclude_id and str(placed["id"]) == exclude_id:
            continue

        # 캐시된 메타데이터에서 크기 가져오기
        item_code = placed["item_code"]
        meta = metadata_map.get(item_code)
        other_width = meta.width if meta else 1
        other_height = meta.height if meta else 1

        # 기존 아이템의 충돌 영역
        other_left = placed["tile_x"]
        other_right = placed["tile_x"] + other_width
        other_top = placed["tile_y"]
        other_bottom = placed["tile_y"] + other_height

        # AABB 충돌 검사
        if (new_left < other_right and
            new_right > other_left and
            new_top < other_bottom and
            new_bottom > other_top):
            return False  # 충돌 발생

    return True


def calculate_crop_stage(planted_at: datetime, grow_time_seconds: int) -> int:
    """작물 성장 단계 계산"""
    if not planted_at:
        return 0

    now = datetime.now(timezone.utc)
    if planted_at.tzinfo is None:
        planted_at = planted_at.replace(tzinfo=timezone.utc)

    elapsed = (now - planted_at).total_seconds()
    progress = elapsed / grow_time_seconds

    # 7단계 성장 (0~6)
    if progress >= 1.0:
        return 6  # 수확 가능
    elif progress >= 0.833:
        return 5
    elif progress >= 0.667:
        return 4
    elif progress >= 0.5:
        return 3
    elif progress >= 0.333:
        return 2
    elif progress >= 0.167:
        return 1
    else:
        return 0  # 씨앗


# =====================================================
# Placement Endpoints
# =====================================================

@router.get("/items", response_model=PlacedItemsListResponse)
async def get_placed_items(
    user_id: UUID = Depends(get_current_user_id),
    db=Depends(get_db)
):
    """
    배치된 아이템 목록 조회

    - 모든 배치된 아이템과 메타데이터 반환
    - 밭의 경우 작물 정보(data) 포함
    """
    # 배치된 아이템 조회 (shop_items와 JOIN)
    placed_result = db.table("user_placed_items").select("*").eq("user_id", str(user_id)).execute()

    if not placed_result.data:
        return PlacedItemsListResponse(success=True, items=[])

    # 아이템 코드 목록
    item_codes = list(set(item["item_code"] for item in placed_result.data))

    # 상점 아이템 메타데이터 조회
    shop_result = db.table("shop_items").select("code, metadata").in_("code", item_codes).execute()
    metadata_map = {item["code"]: FarmService.parse_metadata(item.get("metadata", {})) for item in (shop_result.data or [])}

    # 작물 성장 정보 조회 (밭에 심은 작물용)
    crop_result = db.table("farm_items").select("code, grow_time_seconds").eq("type", "crop").execute()
    crop_grow_times = {item["code"]: item["grow_time_seconds"] for item in (crop_result.data or [])}

    items = []
    for placed in placed_result.data:
        item_code = placed["item_code"]
        metadata = metadata_map.get(item_code, ItemMetadata(sprite="default"))

        # 데이터 파싱
        data = placed.get("data", {})
        if isinstance(data, str):
            data = json.loads(data) if data else {}

        # 밭인 경우 성장 단계 업데이트
        if item_code == "farm_plot" and data.get("cropCode"):
            crop_code = data["cropCode"]
            planted_at_str = data.get("plantedAt")
            if planted_at_str:
                planted_at = datetime.fromisoformat(planted_at_str.replace("Z", "+00:00"))
                grow_time = crop_grow_times.get(crop_code, 120)
                data["stage"] = calculate_crop_stage(planted_at, grow_time)

        items.append(PlacedItemResponse(
            id=str(placed["id"]),
            itemCode=item_code,
            tileX=placed["tile_x"],
            tileY=placed["tile_y"],
            rotation=placed.get("rotation", 0),
            data=data,
            metadata=metadata,
            placedAt=placed.get("placed_at"),
        ))

    return PlacedItemsListResponse(success=True, items=items)


@router.post("/place", response_model=PlaceItemResponse)
async def place_item(
    request: PlaceItemRequest,
    user_id: UUID = Depends(get_current_user_id),
    db=Depends(get_db)
):
    """
    아이템 배치

    - 인벤토리에서 차감
    - user_placed_items에 추가
    """
    inventory = FarmService.get_user_inventory(db, user_id)

    # 인벤토리 확인
    if inventory.get(request.item_code, 0) < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="인벤토리에 아이템이 없습니다"
        )

    # 상점 아이템 정보 조회
    shop_item = FarmService.get_shop_item(db, request.item_code)
    metadata = FarmService.parse_metadata(shop_item.get("metadata", {}))

    # 배치 위치 유효성 확인
    if not check_placement_valid(db, user_id, request.tile_x, request.tile_y, metadata.width, metadata.height):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이 위치에는 배치할 수 없습니다"
        )

    # 인벤토리 차감
    FarmService.update_inventory(db, user_id, request.item_code, -1)

    # 배치
    insert_result = db.table("user_placed_items").insert({
        "user_id": str(user_id),
        "item_code": request.item_code,
        "tile_x": request.tile_x,
        "tile_y": request.tile_y,
        "rotation": 0,
        "data": json.dumps({}),
    }).execute()

    placed_item = insert_result.data[0]

    return PlaceItemResponse(
        success=True,
        message=f"{shop_item['name_ko']}을(를) 배치했습니다",
        item=parse_placed_item(placed_item, metadata),
        inventory=FarmService.get_user_inventory(db, user_id),
    )


@router.patch("/items/{item_id}", response_model=MoveItemResponse)
async def move_item(
    item_id: str,
    request: MoveItemRequest,
    user_id: UUID = Depends(get_current_user_id),
    db=Depends(get_db)
):
    """
    아이템 이동

    - canMove가 true인 아이템만 이동 가능
    """
    placed_item = get_placed_item(db, item_id, user_id)
    shop_item = FarmService.get_shop_item(db, placed_item["item_code"])
    metadata = FarmService.parse_metadata(shop_item.get("metadata", {}))

    # 이동 가능 확인
    if not metadata.canMove:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이 아이템은 이동할 수 없습니다"
        )

    # 새 위치 유효성 확인
    if not check_placement_valid(db, user_id, request.tile_x, request.tile_y, metadata.width, metadata.height, exclude_id=item_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이 위치에는 이동할 수 없습니다"
        )

    # 위치 업데이트
    db.table("user_placed_items").update({
        "tile_x": request.tile_x,
        "tile_y": request.tile_y,
    }).eq("id", item_id).execute()

    # 업데이트된 아이템 조회
    updated = db.table("user_placed_items").select("*").eq("id", item_id).execute()
    updated_item = updated.data[0]

    return MoveItemResponse(
        success=True,
        message="아이템을 이동했습니다",
        item=parse_placed_item(updated_item, metadata),
    )


@router.delete("/items/{item_id}", response_model=RemoveItemResponse)
async def remove_item(
    item_id: str,
    user_id: UUID = Depends(get_current_user_id),
    db=Depends(get_db)
):
    """
    아이템 제거

    - canDelete가 true인 아이템만 삭제 가능
    - 인벤토리로 반환
    """
    placed_item = get_placed_item(db, item_id, user_id)
    shop_item = FarmService.get_shop_item(db, placed_item["item_code"])
    metadata = FarmService.parse_metadata(shop_item.get("metadata", {}))

    # 삭제 가능 확인
    if not metadata.canDelete:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이 아이템은 삭제할 수 없습니다"
        )

    # 밭에 작물이 심어져 있으면 삭제 불가
    data = placed_item.get("data", {})
    if isinstance(data, str):
        data = json.loads(data) if data else {}
    if placed_item["item_code"] == "farm_plot" and data.get("cropCode"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="작물이 심어진 밭은 삭제할 수 없습니다. 먼저 수확하세요."
        )

    # 삭제
    db.table("user_placed_items").delete().eq("id", item_id).execute()

    # 인벤토리에 반환
    FarmService.update_inventory(db, user_id, placed_item["item_code"], 1)

    return RemoveItemResponse(
        success=True,
        message=f"{shop_item['name_ko']}을(를) 인벤토리로 반환했습니다",
        inventory=FarmService.get_user_inventory(db, user_id),
    )


# =====================================================
# Farm Plot Actions (작물 심기/수확)
# =====================================================

@router.post("/items/{item_id}/plant", response_model=PlantCropResponse)
async def plant_crop(
    item_id: str,
    request: PlantCropRequest,
    user_id: UUID = Depends(get_current_user_id),
    db=Depends(get_db)
):
    """
    밭에 작물 심기

    - farm_plot 아이템에만 가능
    - 씨앗 인벤토리 차감
    """
    placed_item = get_placed_item(db, item_id, user_id)

    # farm_plot 확인
    if placed_item["item_code"] != "farm_plot":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="밭에만 작물을 심을 수 있습니다"
        )

    # 이미 작물이 있는지 확인
    data = placed_item.get("data", {})
    if isinstance(data, str):
        data = json.loads(data) if data else {}
    if data.get("cropCode"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 작물이 심어져 있습니다"
        )

    # 작물 정보 확인
    crop_result = db.table("farm_items").select("*").eq("code", request.crop_code).eq("type", "crop").execute()
    if not crop_result.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="존재하지 않는 작물입니다"
        )
    crop_info = crop_result.data[0]

    # 씨앗 확인
    seed_code = f"seed_{request.crop_code}"
    inventory = FarmService.get_user_inventory(db, user_id)
    if inventory.get(seed_code, 0) < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="씨앗이 부족합니다"
        )

    # 씨앗 차감
    FarmService.update_inventory(db, user_id, seed_code, -1)

    # 작물 심기
    now = datetime.now(timezone.utc)
    new_data = {
        "cropCode": request.crop_code,
        "plantedAt": now.isoformat(),
        "stage": 1,
    }

    db.table("user_placed_items").update({
        "data": json.dumps(new_data),
    }).eq("id", item_id).execute()

    # 메타데이터 조회
    shop_item = FarmService.get_shop_item(db, "farm_plot")
    metadata = FarmService.parse_metadata(shop_item.get("metadata", {}))

    # 업데이트된 아이템 조회
    updated = db.table("user_placed_items").select("*").eq("id", item_id).execute()
    updated_item = updated.data[0]

    return PlantCropResponse(
        success=True,
        message=f"{crop_info['name_ko']} 씨앗을 심었습니다",
        item=parse_placed_item(updated_item, metadata),
        inventory=FarmService.get_user_inventory(db, user_id),
    )


@router.post("/items/{item_id}/harvest", response_model=HarvestCropResponse)
async def harvest_crop(
    item_id: str,
    user_id: UUID = Depends(get_current_user_id),
    db=Depends(get_db)
):
    """
    작물 수확

    - 성장 완료된 작물만 수확 가능
    - 골드/XP 보상
    """
    farm = FarmService.get_user_farm(db, user_id)
    placed_item = get_placed_item(db, item_id, user_id)

    # farm_plot 확인
    if placed_item["item_code"] != "farm_plot":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="밭에서만 수확할 수 있습니다"
        )

    # 작물 확인
    data = placed_item.get("data", {})
    if isinstance(data, str):
        data = json.loads(data) if data else {}

    crop_code = data.get("cropCode")
    if not crop_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="수확할 작물이 없습니다"
        )

    # 작물 정보 조회
    crop_result = db.table("farm_items").select("*").eq("code", crop_code).eq("type", "crop").execute()
    if not crop_result.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="작물 정보를 찾을 수 없습니다"
        )
    crop_info = crop_result.data[0]

    # 성장 완료 확인 (stage 6)
    planted_at_str = data.get("plantedAt")
    if planted_at_str:
        planted_at = datetime.fromisoformat(planted_at_str.replace("Z", "+00:00"))
        stage = calculate_crop_stage(planted_at, crop_info["grow_time_seconds"])
        if stage < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="아직 수확할 수 없습니다"
            )

    # 보상 계산
    gold_reward = crop_info["sell_price"]
    xp_reward = crop_info["xp_reward"]
    new_gold = farm.get("gold", 0) + gold_reward

    # 골드 지급
    db.table("user_farm").update({"gold": new_gold}).eq("user_id", str(user_id)).execute()

    # 밭 초기화
    db.table("user_placed_items").update({
        "data": json.dumps({}),
    }).eq("id", item_id).execute()

    # 메타데이터 조회
    shop_item = FarmService.get_shop_item(db, "farm_plot")
    metadata = FarmService.parse_metadata(shop_item.get("metadata", {}))

    # 업데이트된 아이템 조회
    updated = db.table("user_placed_items").select("*").eq("id", item_id).execute()
    updated_item = updated.data[0]

    return HarvestCropResponse(
        success=True,
        message=f"{crop_info['name_ko']}를 수확했습니다! +{gold_reward}G +{xp_reward}XP",
        rewards={"gold": gold_reward, "xp": xp_reward},
        item=parse_placed_item(updated_item, metadata),
        gold=new_gold,
    )
