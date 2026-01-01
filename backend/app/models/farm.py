"""
Farm System Models
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from enum import Enum


class CropRarity(str, Enum):
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"


# =====================================================
# Character Models
# =====================================================

class CharacterData(BaseModel):
    """캐릭터 외형 데이터"""
    name: str = Field(..., min_length=1, max_length=20)
    hair: str = Field(default="style_01")
    hair_color: str = Field(default="#8B4513")
    face: str = Field(default="face_01")
    outfit: str = Field(default="outfit_casual")
    outfit_color: str = Field(default="#4169E1")
    farm_name: str = Field(default="나의 농장", max_length=30)


class CharacterCreateRequest(BaseModel):
    """캐릭터 생성 요청"""
    name: str = Field(..., min_length=1, max_length=20)
    hair: str = Field(default="style_01")
    hair_color: str = Field(default="#8B4513")
    face: str = Field(default="face_01")
    outfit: str = Field(default="outfit_casual")
    outfit_color: str = Field(default="#4169E1")
    farm_name: str = Field(default="나의 농장", max_length=30)


# =====================================================
# Farm Slot Models
# =====================================================

class FarmSlot(BaseModel):
    """농장 슬롯 (작물 한 칸)"""
    slot: int
    crop_code: Optional[str] = None
    planted_at: Optional[datetime] = None
    stage: int = Field(default=0, ge=0, le=4)  # 0=empty, 1-3=growing, 4=ready


# =====================================================
# Farm Response Models
# =====================================================

class UserFarmResponse(BaseModel):
    """사용자 농장 상태 응답 (통합 배치 시스템)"""
    id: UUID
    user_id: UUID
    character_created: bool
    character_data: Optional[CharacterData] = None
    farm_unlocked: bool
    farm_level: int
    gold: int
    farm_size: int  # 배치 가능 영역 크기
    house_level: int
    created_at: datetime
    updated_at: datetime
    # 레거시 필드 제거됨:
    # - farm_slots → user_placed_items 사용 (GET /placement/items)
    # - customization_data → user_placed_items 사용


class FarmItemResponse(BaseModel):
    """농장 아이템 (작물) 정보"""
    id: UUID
    code: str
    name: str
    name_ko: str
    type: str
    rarity: str
    image_url: Optional[str] = None
    seed_cost: int
    sell_price: int
    xp_reward: int
    grow_time_seconds: int


class InventoryItem(BaseModel):
    """인벤토리 아이템"""
    item_code: str
    quantity: int


class InventoryResponse(BaseModel):
    """인벤토리 응답"""
    items: List[InventoryItem]


# =====================================================
# Action Request/Response Models
# =====================================================

class PlantRequest(BaseModel):
    """씨앗 심기 요청"""
    slot: int = Field(..., ge=0)
    crop_code: str


class PlantResponse(BaseModel):
    """씨앗 심기 응답"""
    success: bool
    message: str
    farm_slots: List[FarmSlot]
    inventory: List[InventoryItem]


class HarvestRequest(BaseModel):
    """수확 요청"""
    slot: int = Field(..., ge=0)


class HarvestResponse(BaseModel):
    """수확 응답"""
    success: bool
    message: str
    rewards: Dict[str, int]  # {"gold": 25, "xp": 5}
    farm_slots: List[FarmSlot]
    gold: int


class BuyRequest(BaseModel):
    """씨앗 구매 요청"""
    crop_code: str
    quantity: int = Field(default=1, ge=1, le=99)


class BuyResponse(BaseModel):
    """씨앗 구매 응답"""
    success: bool
    message: str
    inventory: List[InventoryItem]
    gold: int


class SellRequest(BaseModel):
    """작물 판매 요청"""
    crop_code: str
    quantity: int = Field(default=1, ge=1, le=99)


class SellResponse(BaseModel):
    """작물 판매 응답"""
    success: bool
    message: str
    gold_earned: int
    inventory: List[InventoryItem]
    gold: int


class ExpandRequest(BaseModel):
    """농장 확장 요청"""
    target_size: int = Field(..., ge=9, le=36)  # 9, 16, 25, 36


class ExpandResponse(BaseModel):
    """농장 확장 응답"""
    success: bool
    message: str
    farm_size: int
    gold: int


class ExpansionCost(BaseModel):
    """확장 비용 정보"""
    size: int
    grid: str  # "3x3"
    name: str
    cost: int
    is_current: bool
    can_afford: bool


class ExpansionCostsResponse(BaseModel):
    """확장 비용 목록 응답"""
    current_size: int
    gold: int
    options: List[ExpansionCost]


# =====================================================
# Customization Models (장식, 건물, 지형)
# =====================================================

class PlacedDecoration(BaseModel):
    """배치된 장식"""
    id: str
    item_key: str
    tile_x: int
    tile_y: int


class BuildingPosition(BaseModel):
    """건물 위치 및 스킨"""
    x: int
    y: int
    skin: str = "default"


class OwnedTree(BaseModel):
    """배치된 나무/건초"""
    id: str
    type: str  # tree_oak_small, hay_pile 등
    tile_x: int
    tile_y: int


class CustomizationData(BaseModel):
    """농장 커스터마이징 데이터"""
    decorations: List[PlacedDecoration] = []
    buildings: Dict[str, BuildingPosition] = {}
    owned_buildings: List[str] = ["house"]  # 소유한 건물 목록
    owned_trees: List[OwnedTree] = []  # 소유한 나무/건초
    terrain: List[Any] = []


class CustomizationUpdateRequest(BaseModel):
    """커스터마이징 업데이트 요청"""
    decorations: Optional[List[PlacedDecoration]] = None
    buildings: Optional[Dict[str, BuildingPosition]] = None
    owned_buildings: Optional[List[str]] = None
    owned_trees: Optional[List[OwnedTree]] = None
    terrain: Optional[List[Any]] = None


class CustomizationResponse(BaseModel):
    """커스터마이징 데이터 응답"""
    success: bool
    message: str
    customization: CustomizationData


# =====================================================
# Constants
# =====================================================

# 농장 확장 비용
EXPANSION_COSTS = {
    4: {"grid": "2x2", "name": "작은 농장", "cost": 0},
    9: {"grid": "3x3", "name": "중간 농장", "cost": 500},
    16: {"grid": "4x4", "name": "큰 농장", "cost": 1500},
    25: {"grid": "5x5", "name": "대형 농장", "cost": 4000},
    36: {"grid": "6x6", "name": "최대 농장", "cost": 8000},
}

# 캐릭터 생성 시 초기 지급
INITIAL_GOLD = 100
INITIAL_SEEDS_COUNT = 5

# 기본 건물 위치 (집만 기본 제공)
DEFAULT_BUILDING_POSITIONS = {
    "house": {"x": 23, "y": 2, "skin": "default"},
    "chickenCoop": {"x": 2, "y": 7, "skin": "default"},
    "scarecrow": {"x": 9, "y": 6, "skin": "default"},
    "well": {"x": 26, "y": 8, "skin": "default"},
    "barn": {"x": 20, "y": 12, "skin": "default"},
}


# =====================================================
# Shop Models (건물/나무/건초 상점)
# =====================================================

class ShopItem(BaseModel):
    """상점 아이템"""
    code: str
    name: str
    name_ko: str
    type: str  # building, tree, hay
    rarity: str
    price: int
    owned: bool = False


class ShopResponse(BaseModel):
    """상점 목록 응답"""
    success: bool
    items: List[ShopItem]
    gold: int


class PurchaseItemRequest(BaseModel):
    """아이템 구매 요청"""
    item_code: str


class PurchaseItemResponse(BaseModel):
    """아이템 구매 응답"""
    success: bool
    message: str
    gold: int
    owned_buildings: List[str]
    buildings: Dict[str, BuildingPosition]
