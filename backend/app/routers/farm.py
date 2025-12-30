"""
Farm System API Router
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from datetime import datetime, timezone
from uuid import UUID
import random
import json

from ..database import get_db
from ..dependencies import get_current_user_id  # 공통 인증 의존성
from ..models.farm import (
    CharacterCreateRequest,
    CharacterData,
    UserFarmResponse,
    FarmItemResponse,
    FarmSlot,
    InventoryItem,
    InventoryResponse,
    PlantRequest,
    PlantResponse,
    HarvestRequest,
    HarvestResponse,
    BuyRequest,
    BuyResponse,
    SellRequest,
    SellResponse,
    ExpandRequest,
    ExpandResponse,
    ExpansionCost,
    ExpansionCostsResponse,
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
    result = db.table("user_farm").select("*").eq("user_id", str(user_id)).execute()

    if result.data and len(result.data) > 0:
        return result.data[0]

    # 농장이 없으면 생성
    new_farm = {
        "user_id": str(user_id),
        "character_created": False,
        "character_data": {},
        "farm_unlocked": False,
        "farm_level": 1,
        "gold": 0,
        "farm_size": 4,
        "house_level": 1,
        "farm_slots": json.dumps([]),
    }
    insert_result = db.table("user_farm").insert(new_farm).execute()
    return insert_result.data[0] if insert_result.data else new_farm


def parse_farm_slots(farm_data: dict) -> List[FarmSlot]:
    """farm_slots JSON을 FarmSlot 리스트로 변환"""
    slots_data = farm_data.get("farm_slots", [])
    if isinstance(slots_data, str):
        slots_data = json.loads(slots_data)

    slots = []
    for slot_data in slots_data:
        planted_at = slot_data.get("planted_at")
        if planted_at and isinstance(planted_at, str):
            planted_at = datetime.fromisoformat(planted_at.replace("Z", "+00:00"))
        slots.append(FarmSlot(
            slot=slot_data.get("slot", 0),
            crop_code=slot_data.get("crop_code"),
            planted_at=planted_at,
            stage=slot_data.get("stage", 0),
        ))
    return slots


def serialize_farm_slots(slots: List[FarmSlot]) -> str:
    """FarmSlot 리스트를 JSON 문자열로 변환"""
    slots_list = []
    for slot in slots:
        slot_dict = {
            "slot": slot.slot,
            "crop_code": slot.crop_code,
            "planted_at": slot.planted_at.isoformat() if slot.planted_at else None,
            "stage": slot.stage,
        }
        slots_list.append(slot_dict)
    return json.dumps(slots_list)


def get_inventory(db, user_id: UUID) -> List[InventoryItem]:
    """사용자 인벤토리 조회"""
    result = db.table("user_inventory").select("item_code, quantity").eq("user_id", str(user_id)).execute()
    return [InventoryItem(item_code=item["item_code"], quantity=item["quantity"]) for item in (result.data or [])]


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


def get_crop_info(db, crop_code: str) -> Optional[dict]:
    """작물 정보 조회"""
    result = db.table("farm_items").select("*").eq("code", crop_code).eq("type", "crop").execute()
    return result.data[0] if result.data else None


def calculate_crop_stage(planted_at: datetime, grow_time_seconds: int) -> int:
    """현재 작물 성장 단계 계산"""
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
# Farm Endpoints
# =====================================================

@router.get("", response_model=UserFarmResponse)
async def get_farm(
    user_id: UUID = Depends(get_current_user_id),
    db=Depends(get_db)
):
    """농장 상태 조회"""
    farm = get_or_create_farm(db, user_id)
    farm_slots = parse_farm_slots(farm)

    # 작물 성장 단계 업데이트
    items_result = db.table("farm_items").select("code, grow_time_seconds").eq("type", "crop").execute()
    crop_grow_times = {item["code"]: item["grow_time_seconds"] for item in (items_result.data or [])}

    for slot in farm_slots:
        if slot.crop_code and slot.planted_at:
            grow_time = crop_grow_times.get(slot.crop_code, 120)
            slot.stage = calculate_crop_stage(slot.planted_at, grow_time)

    # character_data 파싱
    char_data = farm.get("character_data", {})
    if isinstance(char_data, str):
        char_data = json.loads(char_data) if char_data else {}

    character_data = None
    if farm.get("character_created") and char_data:
        character_data = CharacterData(**char_data)

    return UserFarmResponse(
        id=farm["id"],
        user_id=farm["user_id"],
        character_created=farm.get("character_created", False),
        character_data=character_data,
        farm_unlocked=farm.get("farm_unlocked", False),
        farm_level=farm.get("farm_level", 1),
        gold=farm.get("gold", 0),
        farm_size=farm.get("farm_size", 4),
        farm_slots=farm_slots,
        house_level=farm.get("house_level", 1),
        created_at=farm["created_at"],
        updated_at=farm["updated_at"],
    )


@router.post("/character", response_model=UserFarmResponse)
async def create_character(
    request: CharacterCreateRequest,
    user_id: UUID = Depends(get_current_user_id),
    db=Depends(get_db)
):
    """캐릭터 생성 (농장 해금)"""
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

    # 초기 농장 슬롯 생성 (2x2 = 4칸)
    initial_slots = [{"slot": i, "crop_code": None, "planted_at": None, "stage": 0} for i in range(4)]

    # 농장 업데이트
    db.table("user_farm").update({
        "character_created": True,
        "character_data": json.dumps(character_data),
        "farm_unlocked": True,
        "gold": INITIAL_GOLD,
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
    """작물/아이템 목록 조회"""
    result = db.table("farm_items").select("*").eq("type", "crop").execute()
    return [FarmItemResponse(**item) for item in (result.data or [])]


@router.get("/inventory", response_model=InventoryResponse)
async def get_user_inventory(
    user_id: UUID = Depends(get_current_user_id),
    db=Depends(get_db)
):
    """인벤토리 조회"""
    inventory = get_inventory(db, user_id)
    return InventoryResponse(items=inventory)


@router.post("/plant", response_model=PlantResponse)
async def plant_seed(
    request: PlantRequest,
    user_id: UUID = Depends(get_current_user_id),
    db=Depends(get_db)
):
    """씨앗 심기"""
    farm = get_or_create_farm(db, user_id)

    if not farm.get("farm_unlocked"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="농장이 해금되지 않았습니다")

    # 슬롯 범위 확인
    if request.slot >= farm.get("farm_size", 4):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="유효하지 않은 슬롯입니다")

    # 작물 존재 확인
    crop_info = get_crop_info(db, request.crop_code)
    if not crop_info:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="존재하지 않는 작물입니다")

    # 씨앗 보유 확인
    seed_code = f"seed_{request.crop_code}"
    inventory = get_inventory(db, user_id)
    seed_item = next((item for item in inventory if item.item_code == seed_code), None)

    if not seed_item or seed_item.quantity < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="씨앗이 부족합니다")

    # 슬롯 상태 확인
    farm_slots = parse_farm_slots(farm)
    target_slot = next((s for s in farm_slots if s.slot == request.slot), None)

    if not target_slot:
        # 슬롯이 없으면 생성
        target_slot = FarmSlot(slot=request.slot, crop_code=None, planted_at=None, stage=0)
        farm_slots.append(target_slot)

    if target_slot.crop_code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="이미 작물이 심어져 있습니다")

    # 씨앗 소모
    update_inventory(db, user_id, seed_code, -1)

    # 작물 심기
    target_slot.crop_code = request.crop_code
    target_slot.planted_at = datetime.now(timezone.utc)
    target_slot.stage = 1

    # 농장 업데이트
    db.table("user_farm").update({
        "farm_slots": serialize_farm_slots(farm_slots),
    }).eq("user_id", str(user_id)).execute()

    return PlantResponse(
        success=True,
        message=f"{crop_info['name_ko']} 씨앗을 심었습니다",
        farm_slots=farm_slots,
        inventory=get_inventory(db, user_id),
    )


@router.post("/harvest", response_model=HarvestResponse)
async def harvest_crop(
    request: HarvestRequest,
    user_id: UUID = Depends(get_current_user_id),
    db=Depends(get_db)
):
    """작물 수확"""
    farm = get_or_create_farm(db, user_id)
    farm_slots = parse_farm_slots(farm)

    target_slot = next((s for s in farm_slots if s.slot == request.slot), None)

    if not target_slot or not target_slot.crop_code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="수확할 작물이 없습니다")

    # 작물 정보 조회
    crop_info = get_crop_info(db, target_slot.crop_code)
    if not crop_info:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="작물 정보를 찾을 수 없습니다")

    # 성장 완료 확인
    stage = calculate_crop_stage(target_slot.planted_at, crop_info["grow_time_seconds"])
    if stage < 4:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="아직 수확할 수 없습니다")

    # 보상 지급
    gold_reward = crop_info["sell_price"]
    xp_reward = crop_info["xp_reward"]
    new_gold = farm.get("gold", 0) + gold_reward

    # 슬롯 초기화
    target_slot.crop_code = None
    target_slot.planted_at = None
    target_slot.stage = 0

    # 농장 업데이트
    db.table("user_farm").update({
        "farm_slots": serialize_farm_slots(farm_slots),
        "gold": new_gold,
    }).eq("user_id", str(user_id)).execute()

    # 사용자 XP 증가 (user_stats 테이블이 있는 경우)
    try:
        db.table("user_stats").update({
            "total_xp": db.table("user_stats").select("total_xp").eq("user_id", str(user_id)).single().execute().data["total_xp"] + xp_reward
        }).eq("user_id", str(user_id)).execute()
    except Exception:
        pass  # user_stats가 없어도 계속 진행

    return HarvestResponse(
        success=True,
        message=f"{crop_info['name_ko']}를 수확했습니다! +{gold_reward}G +{xp_reward}XP",
        rewards={"gold": gold_reward, "xp": xp_reward},
        farm_slots=farm_slots,
        gold=new_gold,
    )


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
    """작물 판매 (수확된 작물 인벤토리에서 판매)"""
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
    """농장 확장"""
    farm = get_or_create_farm(db, user_id)
    current_size = farm.get("farm_size", 4)
    gold = farm.get("gold", 0)

    if request.target_size not in EXPANSION_COSTS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="유효하지 않은 확장 크기입니다")

    if request.target_size <= current_size:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="현재 크기보다 큰 크기로만 확장할 수 있습니다")

    cost = EXPANSION_COSTS[request.target_size]["cost"]

    if gold < cost:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="골드가 부족합니다")

    # 기존 슬롯 + 새 슬롯
    farm_slots = parse_farm_slots(farm)
    for i in range(current_size, request.target_size):
        farm_slots.append(FarmSlot(slot=i, crop_code=None, planted_at=None, stage=0))

    new_gold = gold - cost

    db.table("user_farm").update({
        "farm_size": request.target_size,
        "gold": new_gold,
        "farm_slots": serialize_farm_slots(farm_slots),
    }).eq("user_id", str(user_id)).execute()

    return ExpandResponse(
        success=True,
        message=f"농장을 {EXPANSION_COSTS[request.target_size]['name']}으로 확장했습니다!",
        farm_size=request.target_size,
        gold=new_gold,
    )
