"""
Farm System API Router
통합 배치 시스템 리팩토링 - 레거시 엔드포인트 제거됨
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from datetime import datetime, timezone
from uuid import UUID
import random
import json

from ..database import get_db
from ..dependencies import get_current_user_id
from ..models.farm import (
    CharacterCreateRequest,
    CharacterData,
    UserFarmResponse,
    FarmItemResponse,
    FarmSlot,
    InventoryItem,
    InventoryResponse,
    BuyRequest,
    BuyResponse,
    SellRequest,
    SellResponse,
    ExpandRequest,
    ExpandResponse,
    ExpansionCost,
    ExpansionCostsResponse,
    PlantSlotRequest,
    PlantSlotResponse,
    HarvestSlotResponse,
    EXPANSION_COSTS,
    INITIAL_GOLD,
    INITIAL_SEEDS_COUNT,
)

router = APIRouter()


# =====================================================
# Helper Functions
# =====================================================

def get_or_create_farm(db, user_id: UUID) -> dict:
    """사용자 농장 조회 또는 생성"""
    result = db.table("user_farm").select(
        "id, user_id, character_created, character_data, "
        "farm_unlocked, farm_level, gold, farm_size, house_level, "
        "created_at, updated_at"
    ).eq("user_id", str(user_id)).execute()

    if result.data and len(result.data) > 0:
        return result.data[0]

    # 농장이 없으면 생성 (1x1 그리드로 시작)
    new_farm = {
        "user_id": str(user_id),
        "character_created": False,
        "character_data": {},
        "farm_unlocked": False,
        "farm_level": 1,
        "gold": 0,
        "farm_size": 1,  # 1x1 (1칸)으로 시작
        "house_level": 1,
        "farm_slots": json.dumps([]),  # 빈 슬롯 배열
    }
    insert_result = db.table("user_farm").insert(new_farm).execute()
    return insert_result.data[0] if insert_result.data else new_farm


def get_inventory(db, user_id: UUID) -> List[InventoryItem]:
    """사용자 인벤토리 조회"""
    result = db.table("user_inventory").select("item_code, quantity").eq("user_id", str(user_id)).execute()
    return [InventoryItem(item_code=item["item_code"], quantity=item["quantity"]) for item in (result.data or [])]


def update_inventory(db, user_id: UUID, item_code: str, quantity_change: int):
    """인벤토리 수량 업데이트"""
    existing = db.table("user_inventory").select("quantity").eq("user_id", str(user_id)).eq("item_code", item_code).execute()

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


def get_crop_info(db, crop_code: str) -> Optional[dict]:
    """작물 정보 조회"""
    result = db.table("farm_items").select(
        "id, code, name, name_ko, type, rarity, image_url, "
        "seed_cost, sell_price, xp_reward, grow_time_seconds"
    ).eq("code", crop_code).eq("type", "crop").execute()
    return result.data[0] if result.data else None


def calculate_crop_stage(planted_at_str: str, grow_time_seconds: int) -> int:
    """작물 성장 단계 계산 (0=empty, 1-3=growing, 4=ready)"""
    if not planted_at_str:
        return 0

    try:
        planted_at = datetime.fromisoformat(planted_at_str.replace('Z', '+00:00'))
        now = datetime.now(timezone.utc)
        elapsed = (now - planted_at).total_seconds()
        progress = elapsed / grow_time_seconds if grow_time_seconds > 0 else 1.0

        if progress >= 1.0:
            return 4
        elif progress >= 0.75:
            return 3
        elif progress >= 0.5:
            return 2
        elif progress >= 0.25:
            return 1
        else:
            return 1  # 최소 1단계
    except:
        return 1


def get_farm_slots(db, user_id: UUID) -> List[FarmSlot]:
    """farm_slots 조회 및 stage 계산"""
    result = db.table("user_farm").select("farm_slots").eq("user_id", str(user_id)).execute()

    if not result.data or not result.data[0].get("farm_slots"):
        return []

    raw_slots = result.data[0]["farm_slots"]
    if isinstance(raw_slots, str):
        raw_slots = json.loads(raw_slots)

    slots = []
    for slot_data in raw_slots:
        crop_code = slot_data.get("cropCode")
        planted_at = slot_data.get("plantedAt")
        grow_time = slot_data.get("growTimeSeconds") or 120

        stage = 0
        if crop_code and planted_at:
            stage = calculate_crop_stage(planted_at, grow_time)

        slots.append(FarmSlot(
            slot=slot_data.get("slot", 0),
            cropCode=crop_code,
            plantedAt=planted_at,
            growTimeSeconds=slot_data.get("growTimeSeconds"),
            stage=stage,
        ))

    return slots


def update_farm_slots(db, user_id: UUID, slots: List[FarmSlot]):
    """farm_slots 업데이트"""
    slots_data = [
        {
            "slot": s.slot,
            "cropCode": s.cropCode,
            "plantedAt": s.plantedAt,
            "growTimeSeconds": s.growTimeSeconds,
        }
        for s in slots
    ]
    db.table("user_farm").update({
        "farm_slots": json.dumps(slots_data)
    }).eq("user_id", str(user_id)).execute()


def get_inventory_dict(db, user_id: UUID) -> dict:
    """인벤토리를 딕셔너리로 반환"""
    result = db.table("user_inventory").select("item_code, quantity").eq("user_id", str(user_id)).execute()
    return {item["item_code"]: item["quantity"] for item in (result.data or [])}


# =====================================================
# Farm Endpoints (유지)
# =====================================================

@router.get("", response_model=UserFarmResponse)
async def get_farm(
    user_id: UUID = Depends(get_current_user_id),
    db=Depends(get_db)
):
    """농장 상태 조회 (farm_slots 포함)"""
    farm = get_or_create_farm(db, user_id)

    # character_data 파싱
    char_data = farm.get("character_data", {})
    if isinstance(char_data, str):
        char_data = json.loads(char_data) if char_data else {}

    character_data = None
    if farm.get("character_created") and char_data:
        character_data = CharacterData(**char_data)

    # farm_slots 조회 (stage 계산 포함)
    farm_slots = get_farm_slots(db, user_id)

    return UserFarmResponse(
        id=farm["id"],
        user_id=farm["user_id"],
        character_created=farm.get("character_created", False),
        character_data=character_data,
        farm_unlocked=farm.get("farm_unlocked", False),
        farm_level=farm.get("farm_level", 1),
        gold=farm.get("gold", 0),
        farm_size=farm.get("farm_size", 1),  # 기본값 1 (1x1)
        house_level=farm.get("house_level", 1),
        farm_slots=farm_slots,
        created_at=farm["created_at"],
        updated_at=farm["updated_at"],
    )


@router.post("/character", response_model=UserFarmResponse)
async def create_character(
    request: CharacterCreateRequest,
    user_id: UUID = Depends(get_current_user_id),
    db=Depends(get_db)
):
    """캐릭터 생성 (농장 해금)

    - 캐릭터 데이터 저장
    - 초기 골드 지급
    - 초기 씨앗 지급 (랜덤 5개)
    - farm_slots 1칸 초기화
    - 트리거가 자동으로 house를 user_placed_items에 배치
    """
    farm = get_or_create_farm(db, user_id)

    if farm.get("character_created"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="캐릭터가 이미 생성되어 있습니다"
        )

    # 캐릭터 데이터 저장
    character_data = {
        "name": request.name,
        "hair": request.hair,
        "hair_color": request.hair_color,
        "face": request.face,
        "outfit": request.outfit,
        "outfit_color": request.outfit_color,
        "farm_name": request.farm_name,
    }

    # 초기 farm_slots (1x1 = 1칸)
    initial_slots = [
        {"slot": 0, "cropCode": None, "plantedAt": None, "growTimeSeconds": None}
    ]

    # 농장 업데이트 (트리거가 house 배치)
    db.table("user_farm").update({
        "character_created": True,
        "character_data": json.dumps(character_data),
        "farm_unlocked": True,
        "gold": INITIAL_GOLD,
        "farm_size": 1,
        "farm_slots": json.dumps(initial_slots),
    }).eq("user_id", str(user_id)).execute()

    # 초기 씨앗 지급 (랜덤 5개)
    crops = db.table("farm_items").select("code").eq("type", "crop").execute()
    if crops.data:
        crop_codes = [c["code"] for c in crops.data]
        for _ in range(INITIAL_SEEDS_COUNT):
            random_crop = random.choice(crop_codes)
            update_inventory(db, user_id, f"seed_{random_crop}", 1)

    # 업데이트된 농장 반환
    return await get_farm(user_id, db)


@router.get("/items", response_model=List[FarmItemResponse])
async def get_farm_items(db=Depends(get_db)):
    """작물 목록 조회 (farm_items 테이블)"""
    result = db.table("farm_items").select(
        "id, code, name, name_ko, type, rarity, image_url, "
        "seed_cost, sell_price, xp_reward, grow_time_seconds"
    ).eq("type", "crop").execute()
    return [FarmItemResponse(**item) for item in (result.data or [])]


@router.get("/inventory", response_model=InventoryResponse)
async def get_user_inventory(
    user_id: UUID = Depends(get_current_user_id),
    db=Depends(get_db)
):
    """인벤토리 조회"""
    inventory = get_inventory(db, user_id)
    return InventoryResponse(items=inventory)


@router.post("/shop/buy", response_model=BuyResponse)
async def buy_seeds(
    request: BuyRequest,
    user_id: UUID = Depends(get_current_user_id),
    db=Depends(get_db)
):
    """씨앗 구매"""
    farm = get_or_create_farm(db, user_id)
    crop_info = get_crop_info(db, request.crop_code)

    if not crop_info:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="존재하지 않는 작물입니다")

    total_cost = crop_info["seed_cost"] * request.quantity
    current_gold = farm.get("gold", 0)

    if current_gold < total_cost:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="골드가 부족합니다")

    # 골드 차감
    new_gold = current_gold - total_cost
    db.table("user_farm").update({"gold": new_gold}).eq("user_id", str(user_id)).execute()

    # 씨앗 추가
    seed_code = f"seed_{request.crop_code}"
    update_inventory(db, user_id, seed_code, request.quantity)

    return BuyResponse(
        success=True,
        message=f"{crop_info['name_ko']} 씨앗 {request.quantity}개를 구매했습니다",
        inventory=get_inventory(db, user_id),
        gold=new_gold,
    )


@router.post("/shop/sell", response_model=SellResponse)
async def sell_crops(
    request: SellRequest,
    user_id: UUID = Depends(get_current_user_id),
    db=Depends(get_db)
):
    """작물 판매 (인벤토리에서 판매)"""
    farm = get_or_create_farm(db, user_id)
    crop_info = get_crop_info(db, request.crop_code)

    if not crop_info:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="존재하지 않는 작물입니다")

    # 인벤토리 확인
    crop_code = f"crop_{request.crop_code}"
    inventory = get_inventory(db, user_id)
    crop_item = next((item for item in inventory if item.item_code == crop_code), None)

    if not crop_item or crop_item.quantity < request.quantity:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="판매할 작물이 부족합니다")

    # 골드 지급
    gold_earned = crop_info["sell_price"] * request.quantity
    new_gold = farm.get("gold", 0) + gold_earned
    db.table("user_farm").update({"gold": new_gold}).eq("user_id", str(user_id)).execute()

    # 작물 제거
    update_inventory(db, user_id, crop_code, -request.quantity)

    return SellResponse(
        success=True,
        message=f"{crop_info['name_ko']} {request.quantity}개를 판매했습니다 (+{gold_earned}G)",
        gold_earned=gold_earned,
        inventory=get_inventory(db, user_id),
        gold=new_gold,
    )


@router.get("/expansion-costs", response_model=ExpansionCostsResponse)
async def get_expansion_costs(
    user_id: UUID = Depends(get_current_user_id),
    db=Depends(get_db)
):
    """농장 확장 비용 조회"""
    farm = get_or_create_farm(db, user_id)
    current_size = farm.get("farm_size", 4)
    gold = farm.get("gold", 0)

    options = []
    for size, info in EXPANSION_COSTS.items():
        options.append(ExpansionCost(
            size=size,
            grid=info["grid"],
            name=info["name"],
            cost=info["cost"],
            is_current=(size == current_size),
            can_afford=(gold >= info["cost"] and size > current_size),
        ))

    return ExpansionCostsResponse(
        current_size=current_size,
        gold=gold,
        options=sorted(options, key=lambda x: x.size),
    )


@router.post("/expand", response_model=ExpandResponse)
async def expand_farm(
    request: ExpandRequest,
    user_id: UUID = Depends(get_current_user_id),
    db=Depends(get_db)
):
    """농장 밭 확장

    - farm_size 업데이트
    - farm_slots 배열 자동 확장 (새 슬롯 추가)
    """
    farm = get_or_create_farm(db, user_id)
    current_size = farm.get("farm_size", 1)
    gold = farm.get("gold", 0)

    if request.target_size not in EXPANSION_COSTS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="유효하지 않은 확장 크기입니다")

    if request.target_size <= current_size:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="현재 크기보다 큰 크기로만 확장할 수 있습니다")

    cost = EXPANSION_COSTS[request.target_size]["cost"]

    if gold < cost:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="골드가 부족합니다")

    new_gold = gold - cost

    # 기존 farm_slots 가져오기
    current_slots = get_farm_slots(db, user_id)

    # 새 슬롯 추가
    new_slots = list(current_slots)
    for i in range(len(current_slots), request.target_size):
        new_slots.append(FarmSlot(
            slot=i,
            cropCode=None,
            plantedAt=None,
            growTimeSeconds=None,
            stage=0,
        ))

    # farm_size와 farm_slots 업데이트
    slots_data = [
        {"slot": s.slot, "cropCode": s.cropCode, "plantedAt": s.plantedAt, "growTimeSeconds": s.growTimeSeconds}
        for s in new_slots
    ]
    db.table("user_farm").update({
        "farm_size": request.target_size,
        "gold": new_gold,
        "farm_slots": json.dumps(slots_data),
    }).eq("user_id", str(user_id)).execute()

    return ExpandResponse(
        success=True,
        message=f"밭을 {EXPANSION_COSTS[request.target_size]['name']}으로 확장했습니다!",
        farm_size=request.target_size,
        gold=new_gold,
        farm_slots=new_slots,
    )


# =====================================================
# Farm Slot Endpoints (그리드 기반 심기/수확)
# =====================================================

@router.post("/slots/{slot}/plant", response_model=PlantSlotResponse)
async def plant_on_slot(
    slot: int,
    request: PlantSlotRequest,
    user_id: UUID = Depends(get_current_user_id),
    db=Depends(get_db)
):
    """슬롯에 작물 심기

    - slot: 밭 슬롯 인덱스 (0부터 시작)
    - crop_code: 심을 작물 코드 (예: carrot)
    """
    farm = get_or_create_farm(db, user_id)
    farm_size = farm.get("farm_size", 1)

    # 슬롯 유효성 검사
    if slot < 0 or slot >= farm_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"유효하지 않은 슬롯입니다 (0-{farm_size - 1})"
        )

    # 현재 슬롯 상태 확인
    current_slots = get_farm_slots(db, user_id)
    if slot >= len(current_slots):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="슬롯이 초기화되지 않았습니다"
        )

    target_slot = current_slots[slot]
    if target_slot.cropCode:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 작물이 심어져 있습니다"
        )

    # 작물 정보 확인
    crop_info = get_crop_info(db, request.crop_code)
    if not crop_info:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="존재하지 않는 작물입니다"
        )

    # 씨앗 인벤토리 확인
    seed_code = f"seed_{request.crop_code}"
    inventory = get_inventory_dict(db, user_id)
    if inventory.get(seed_code, 0) < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="씨앗이 부족합니다"
        )

    # 씨앗 차감
    update_inventory(db, user_id, seed_code, -1)

    # 슬롯 업데이트
    now = datetime.now(timezone.utc).isoformat()
    grow_time = crop_info["grow_time_seconds"]

    target_slot.cropCode = request.crop_code
    target_slot.plantedAt = now
    target_slot.growTimeSeconds = grow_time
    target_slot.stage = 1

    # DB 업데이트
    update_farm_slots(db, user_id, current_slots)

    # 업데이트된 인벤토리
    new_inventory = get_inventory_dict(db, user_id)

    return PlantSlotResponse(
        success=True,
        message=f"{crop_info['name_ko']}을(를) 심었습니다!",
        slot=target_slot,
        farm_slots=current_slots,
        inventory=new_inventory,
    )


@router.post("/slots/{slot}/harvest", response_model=HarvestSlotResponse)
async def harvest_from_slot(
    slot: int,
    user_id: UUID = Depends(get_current_user_id),
    db=Depends(get_db)
):
    """슬롯에서 작물 수확

    - slot: 밭 슬롯 인덱스 (0부터 시작)
    - stage가 4일 때만 수확 가능
    """
    farm = get_or_create_farm(db, user_id)
    farm_size = farm.get("farm_size", 1)

    # 슬롯 유효성 검사
    if slot < 0 or slot >= farm_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"유효하지 않은 슬롯입니다 (0-{farm_size - 1})"
        )

    # 현재 슬롯 상태 확인
    current_slots = get_farm_slots(db, user_id)
    if slot >= len(current_slots):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="슬롯이 초기화되지 않았습니다"
        )

    target_slot = current_slots[slot]
    if not target_slot.cropCode:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="수확할 작물이 없습니다"
        )

    # 수확 가능 여부 확인 (stage 4)
    if target_slot.stage < 4:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="아직 수확할 수 없습니다 (성장 중)"
        )

    # 작물 정보 조회
    crop_info = get_crop_info(db, target_slot.cropCode)
    if not crop_info:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="작물 정보를 찾을 수 없습니다"
        )

    # 보상 계산
    gold_reward = crop_info["sell_price"]
    xp_reward = crop_info["xp_reward"]

    # 골드 지급
    current_gold = farm.get("gold", 0)
    new_gold = current_gold + gold_reward
    db.table("user_farm").update({"gold": new_gold}).eq("user_id", str(user_id)).execute()

    # XP 지급 (users 테이블)
    try:
        user_result = db.table("users").select("xp").eq("id", str(user_id)).execute()
        if user_result.data:
            current_xp = user_result.data[0].get("xp", 0)
            db.table("users").update({"xp": current_xp + xp_reward}).eq("id", str(user_id)).execute()
    except:
        pass  # XP 업데이트 실패해도 계속 진행

    # 슬롯 초기화
    target_slot.cropCode = None
    target_slot.plantedAt = None
    target_slot.growTimeSeconds = None
    target_slot.stage = 0

    # DB 업데이트
    update_farm_slots(db, user_id, current_slots)

    return HarvestSlotResponse(
        success=True,
        message=f"{crop_info['name_ko']}을(를) 수확했습니다! (+{gold_reward}G, +{xp_reward}XP)",
        slot=target_slot,
        farm_slots=current_slots,
        rewards={"gold": gold_reward, "xp": xp_reward},
        gold=new_gold,
    )


# =====================================================
# 레거시 엔드포인트 (하위 호환성)
# =====================================================
# - POST /placement/items/{id}/plant - 기존 farm_plot 방식 (deprecated)
# - POST /placement/items/{id}/harvest - 기존 farm_plot 방식 (deprecated)
