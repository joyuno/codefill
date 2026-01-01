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

router = APIRouter()


# =====================================================
# Helper Functions
# =====================================================

def get_user_farm(db, user_id: UUID) -> dict:
    """사용자 농장 조회"""
    result = db.table("user_farm").select("*").eq("user_id", str(user_id)).execute()
    if result.data and len(result.data) > 0:
        return result.data[0]
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="농장을 찾을 수 없습니다. 캐릭터를 먼저 생성해주세요."
    )


def get_user_inventory(db, user_id: UUID) -> dict:
    """사용자 인벤토리 조회 (딕셔너리 형태)"""
    result = db.table("user_inventory").select("item_code, quantity").eq("user_id", str(user_id)).execute()
    return {item["item_code"]: item["quantity"] for item in (result.data or [])}


def update_inventory(db, user_id: UUID, item_code: str, quantity_change: int):
    """인벤토리 수량 업데이트"""
    existing = db.table("user_inventory").select("*").eq("user_id", str(user_id)).eq("item_code", item_code).execute()

    if existing.data and len(existing.data) > 0:
        new_quantity = existing.data[0]["quantity"] + quantity_change
        if new_quantity <= 0:
            db.table("user_inventory").delete().eq("user_id", str(user_id)).eq("item_code", item_code).execute()
        else:
            db.table("user_inventory").update({"quantity": new_quantity}).eq("user_id", str(user_id)).eq("item_code", item_code).execute()
    elif quantity_change > 0:
        db.table("user_inventory").insert({
            "user_id": str(user_id),
            "item_code": item_code,
            "quantity": quantity_change,
        }).execute()


def parse_metadata(metadata_json) -> ItemMetadata:
    """메타데이터 JSON을 ItemMetadata로 변환"""
    if isinstance(metadata_json, str):
        metadata_json = json.loads(metadata_json) if metadata_json else {}

    return ItemMetadata(
        sprite=metadata_json.get("sprite", "default"),
        width=metadata_json.get("width", 1),
        height=metadata_json.get("height", 1),
        depth=metadata_json.get("depth", 50),
        canMove=metadata_json.get("canMove", True),
        canDelete=metadata_json.get("canDelete", True),
        anchor=metadata_json.get("anchor"),
        collision=metadata_json.get("collision"),
    )


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


def get_shop_item(db, item_code: str) -> dict:
    """상점 아이템 정보 조회"""
    result = db.table("shop_items").select("*").eq("code", item_code).execute()
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="존재하지 않는 아이템입니다"
        )
    return result.data[0]


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
    """배치 위치가 유효한지 확인"""
    # 맵 범위 체크
    if tile_x < 0 or tile_y < 0 or tile_x + width > MAP_WIDTH_TILES or tile_y + height > MAP_HEIGHT_TILES:
        return False

    # TODO: 충돌 체크 (다른 아이템과 겹치는지)
    # 현재는 단순화를 위해 같은 위치에 같은 아이템만 체크

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

    if progress >= 1.0:
        return 4  # 수확 가능
    elif progress >= 0.75:
        return 3
    elif progress >= 0.5:
        return 2
    elif progress >= 0.25:
        return 1
    else:
        return 1  # 최소 1단계


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
    metadata_map = {item["code"]: parse_metadata(item.get("metadata", {})) for item in (shop_result.data or [])}

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
    inventory = get_user_inventory(db, user_id)

    # 인벤토리 확인
    if inventory.get(request.item_code, 0) < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="인벤토리에 아이템이 없습니다"
        )

    # 상점 아이템 정보 조회
    shop_item = get_shop_item(db, request.item_code)
    metadata = parse_metadata(shop_item.get("metadata", {}))

    # 배치 위치 유효성 확인
    if not check_placement_valid(db, user_id, request.tile_x, request.tile_y, metadata.width, metadata.height):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이 위치에는 배치할 수 없습니다"
        )

    # 인벤토리 차감
    update_inventory(db, user_id, request.item_code, -1)

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
        inventory=get_user_inventory(db, user_id),
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
    shop_item = get_shop_item(db, placed_item["item_code"])
    metadata = parse_metadata(shop_item.get("metadata", {}))

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
    shop_item = get_shop_item(db, placed_item["item_code"])
    metadata = parse_metadata(shop_item.get("metadata", {}))

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
    update_inventory(db, user_id, placed_item["item_code"], 1)

    return RemoveItemResponse(
        success=True,
        message=f"{shop_item['name_ko']}을(를) 인벤토리로 반환했습니다",
        inventory=get_user_inventory(db, user_id),
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
    inventory = get_user_inventory(db, user_id)
    if inventory.get(seed_code, 0) < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="씨앗이 부족합니다"
        )

    # 씨앗 차감
    update_inventory(db, user_id, seed_code, -1)

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
    shop_item = get_shop_item(db, "farm_plot")
    metadata = parse_metadata(shop_item.get("metadata", {}))

    # 업데이트된 아이템 조회
    updated = db.table("user_placed_items").select("*").eq("id", item_id).execute()
    updated_item = updated.data[0]

    return PlantCropResponse(
        success=True,
        message=f"{crop_info['name_ko']} 씨앗을 심었습니다",
        item=parse_placed_item(updated_item, metadata),
        inventory=get_user_inventory(db, user_id),
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
    farm = get_user_farm(db, user_id)
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

    # 성장 완료 확인
    planted_at_str = data.get("plantedAt")
    if planted_at_str:
        planted_at = datetime.fromisoformat(planted_at_str.replace("Z", "+00:00"))
        stage = calculate_crop_stage(planted_at, crop_info["grow_time_seconds"])
        if stage < 4:
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
    shop_item = get_shop_item(db, "farm_plot")
    metadata = parse_metadata(shop_item.get("metadata", {}))

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
