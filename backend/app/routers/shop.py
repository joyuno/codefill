"""
Unified Shop API Router
통합 상점 시스템 API
"""

from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import Optional
from uuid import UUID
import json

from ..database import get_db
from ..dependencies import get_current_user_id
from ..models.placement import (
    ItemMetadata,
    ShopItemResponse,
    ShopListResponse,
    BuyItemRequest,
    BuyItemResponse,
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


# =====================================================
# Shop Endpoints
# =====================================================

@router.get("/items", response_model=ShopListResponse)
async def get_shop_items(
    category: Optional[str] = Query(None, description="카테고리 필터 (building, tree, decoration, fence, farm)"),
    user_id: UUID = Depends(get_current_user_id),
    db=Depends(get_db)
):
    """
    상점 아이템 목록 조회

    - category: 카테고리 필터 (선택사항)
    - 인벤토리 보유량, 배치된 개수, 구매 가능 여부 포함
    """
    farm = get_user_farm(db, user_id)
    inventory = get_user_inventory(db, user_id)

    # 배치된 아이템 개수 조회
    placed_result = db.table("user_placed_items").select("item_code").eq("user_id", str(user_id)).execute()
    placed_counts = {}
    for item in (placed_result.data or []):
        code = item["item_code"]
        placed_counts[code] = placed_counts.get(code, 0) + 1

    # 상점 아이템 조회
    query = db.table("shop_items").select("*")
    if category:
        query = query.eq("category", category)

    result = query.execute()

    items = []
    for item in (result.data or []):
        code = item["code"]
        owned = inventory.get(code, 0)
        placed = placed_counts.get(code, 0)
        max_qty = item.get("max_quantity")

        # 구매 가능 여부 판단
        can_buy = True
        if max_qty is not None:
            total_owned = owned + placed
            if total_owned >= max_qty:
                can_buy = False

        # 가격 확인
        if farm.get("gold", 0) < item["price"]:
            can_buy = False

        # 무료 아이템 (기본 제공)은 이미 배치되어 있으면 구매 불가
        if item["price"] == 0 and placed > 0:
            can_buy = False

        items.append(ShopItemResponse(
            code=code,
            name=item["name"],
            nameKo=item["name_ko"],
            category=item["category"],
            rarity=item["rarity"],
            price=item["price"],
            maxQuantity=max_qty,
            owned=owned,
            placed=placed,
            canBuy=can_buy,
            metadata=parse_metadata(item.get("metadata", {})),
        ))

    return ShopListResponse(
        success=True,
        items=items,
        gold=farm.get("gold", 0),
    )


@router.post("/buy", response_model=BuyItemResponse)
async def buy_item(
    request: BuyItemRequest,
    user_id: UUID = Depends(get_current_user_id),
    db=Depends(get_db)
):
    """
    아이템 구매

    - 골드 차감
    - 인벤토리에 추가
    - max_quantity 체크
    """
    farm = get_user_farm(db, user_id)
    inventory = get_user_inventory(db, user_id)

    # 아이템 정보 조회
    item_result = db.table("shop_items").select("*").eq("code", request.item_code).execute()
    if not item_result.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="존재하지 않는 아이템입니다"
        )

    item = item_result.data[0]

    # 무료 아이템은 직접 구매 불가
    if item["price"] == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="기본 제공 아이템은 구매할 수 없습니다"
        )

    # max_quantity 체크
    max_qty = item.get("max_quantity")
    if max_qty is not None:
        # 배치된 개수 조회
        placed_result = db.table("user_placed_items").select("id").eq("user_id", str(user_id)).eq("item_code", request.item_code).execute()
        placed_count = len(placed_result.data or [])
        current_owned = inventory.get(request.item_code, 0)

        if current_owned + placed_count + request.quantity > max_qty:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"이 아이템은 최대 {max_qty}개까지만 보유할 수 있습니다"
            )

    # 골드 확인
    total_cost = item["price"] * request.quantity
    current_gold = farm.get("gold", 0)

    if current_gold < total_cost:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"골드가 부족합니다 (필요: {total_cost}G, 보유: {current_gold}G)"
        )

    # 구매 처리
    new_gold = current_gold - total_cost
    db.table("user_farm").update({"gold": new_gold}).eq("user_id", str(user_id)).execute()

    # 인벤토리에 추가
    update_inventory(db, user_id, request.item_code, request.quantity)

    # 업데이트된 인벤토리 조회
    updated_inventory = get_user_inventory(db, user_id)

    return BuyItemResponse(
        success=True,
        message=f"{item['name_ko']} {request.quantity}개를 구매했습니다",
        gold=new_gold,
        inventory=updated_inventory,
    )
