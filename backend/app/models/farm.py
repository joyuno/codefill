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
    body: str = Field(default="Body_1")  # Body_1 ~ Body_9 (피부색)
    hair: str = Field(default="Short_Brown_Dark")  # Hairstyle_Short_Brown_Dark 형태
    hair_color: str = Field(default="#8B4513")
    face: str = Field(default="Eyes_Brown")  # 눈
    outfit: str = Field(default="Outfit_Dungarees_Green")
    outfit_color: str = Field(default="#4169E1")
    accessory: str = Field(default="none")  # Accessory_Straw_Hat_Green 등 또는 'none'
    farm_name: str = Field(default="나의 농장", max_length=30)


class CharacterCreateRequest(BaseModel):
    """캐릭터 생성 요청"""
    name: str = Field(..., min_length=1, max_length=20)
    body: str = Field(default="Body_1")  # Body_1 ~ Body_9 (피부색)
    hair: str = Field(default="Short_Brown_Dark")
    hair_color: str = Field(default="#8B4513")
    face: str = Field(default="Eyes_Brown")
    outfit: str = Field(default="Outfit_Dungarees_Green")
    outfit_color: str = Field(default="#4169E1")
    accessory: str = Field(default="none")  # Accessory_Straw_Hat_Green 등 또는 'none'
    farm_name: str = Field(default="나의 농장", max_length=30)


# =====================================================
# Farm Slot Models
# =====================================================

class FarmSlot(BaseModel):
    """농장 슬롯 (작물 한 칸) - 프론트엔드용 camelCase"""
    slot: int
    cropCode: Optional[str] = None
    plantedAt: Optional[str] = None  # ISO datetime string
    growTimeSeconds: Optional[int] = None
    stage: int = Field(default=0, ge=0, le=6)  # 0=empty, 1-5=growing, 6=ready

    class Config:
        # DB에서 snake_case로 저장되어도 camelCase로 변환
        populate_by_name = True


# =====================================================
# Farm Response Models
# =====================================================

class UserFarmResponse(BaseModel):
    """사용자 농장 상태 응답 (그리드 기반 밭 시스템)"""
    id: UUID
    user_id: UUID
    character_created: bool
    character_data: Optional[CharacterData] = None
    farm_unlocked: bool
    farm_level: int
    gold: int
    farm_size: int  # 밭 슬롯 개수 (1, 4, 9, 16, 25, 36, 49)
    map_level: int = 1  # 맵 확장 레벨 (1-5)
    house_level: int
    farm_slots: List[FarmSlot] = []  # 밭 그리드 슬롯 데이터
    created_at: datetime
    updated_at: datetime


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

class PlantSlotRequest(BaseModel):
    """슬롯에 씨앗 심기 요청"""
    crop_code: str


class PlantSlotResponse(BaseModel):
    """슬롯에 씨앗 심기 응답"""
    success: bool
    message: str
    slot: FarmSlot  # 업데이트된 슬롯
    farm_slots: List[FarmSlot]  # 전체 슬롯 배열
    inventory: Dict[str, int]  # 업데이트된 인벤토리


class HarvestSlotResponse(BaseModel):
    """슬롯 수확 응답"""
    success: bool
    message: str
    slot: FarmSlot  # 초기화된 슬롯
    farm_slots: List[FarmSlot]  # 전체 슬롯 배열
    rewards: Dict[str, int]  # {"gold": 25, "xp": 5}
    gold: int  # 현재 골드


# Legacy models (하위 호환성)
class PlantRequest(BaseModel):
    """씨앗 심기 요청 (레거시)"""
    slot: int = Field(..., ge=0)
    crop_code: str


class PlantResponse(BaseModel):
    """씨앗 심기 응답 (레거시)"""
    success: bool
    message: str
    farm_slots: List[FarmSlot]
    inventory: List[InventoryItem]


class HarvestRequest(BaseModel):
    """수확 요청 (레거시)"""
    slot: int = Field(..., ge=0)


class HarvestResponse(BaseModel):
    """수확 응답 (레거시)"""
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
    target_size: int = Field(..., ge=1, le=49)  # 1, 4, 9, 16, 25, 36, 49


class ExpandResponse(BaseModel):
    """농장 확장 응답"""
    success: bool
    message: str
    farm_size: int
    gold: int
    farm_slots: List[FarmSlot] = []  # 확장된 슬롯 배열


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
# Map Expansion Models (맵 확장)
# =====================================================

class MapExpandRequest(BaseModel):
    """맵 확장 요청"""
    target_level: int = Field(..., ge=1, le=5)  # 1-5


class MapExpandResponse(BaseModel):
    """맵 확장 응답"""
    success: bool
    message: str
    map_level: int
    gold: int


class MapExpansionCost(BaseModel):
    """맵 확장 비용 정보"""
    level: int
    cols: int
    rows: int
    name: str
    cost: int
    is_current: bool
    can_afford: bool


class MapExpansionCostsResponse(BaseModel):
    """맵 확장 비용 목록 응답"""
    current_level: int
    gold: int
    options: List[MapExpansionCost]


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
# Farm Init Response (통합 API 응답)
# =====================================================

class FarmInitResponse(BaseModel):
    """농장 초기화 통합 응답 (1개 HTTP 요청으로 모든 데이터 반환)"""
    farm: UserFarmResponse
    items: List[FarmItemResponse]  # 작물 목록 (정적 데이터)
    inventory: List[InventoryItem]  # 사용자 인벤토리
    placedItems: List[Any] = []  # 배치된 아이템 (PlacedItemResponse)


# =====================================================
# Constants
# =====================================================

# 농장 확장 비용 (그리드 기반: 1x1 -> 7x7)
EXPANSION_COSTS = {
    1: {"grid": "1x1", "name": "씨앗 밭", "cost": 0},
    4: {"grid": "2x2", "name": "작은 농장", "cost": 200},
    9: {"grid": "3x3", "name": "중간 농장", "cost": 500},
    16: {"grid": "4x4", "name": "큰 농장", "cost": 1500},
    25: {"grid": "5x5", "name": "대형 농장", "cost": 4000},
    36: {"grid": "6x6", "name": "거대 농장", "cost": 8000},
    49: {"grid": "7x7", "name": "전설 농장", "cost": 15000},
}

# 순차적 확장을 위한 크기 순서 정의
EXPANSION_ORDER = [1, 4, 9, 16, 25, 36, 49]

# 캐릭터 생성 시 초기 지급
INITIAL_GOLD = 100000
INITIAL_FARM_SIZE = 9  # 3x3 그리드
INITIAL_SEEDS_QUANTITY = 10  # 모든 씨앗 종류별 10개씩
INITIAL_MAP_LEVEL = 1  # 초기 맵 레벨

# 맵 확장 비용 (레벨 기반: 1 -> 5, 최소 30x20=뷰포트, 최대 60x40)
MAP_EXPANSION_COSTS = {
    1: {"cols": 30, "rows": 20, "name": "작은 땅", "cost": 0},
    2: {"cols": 38, "rows": 25, "name": "넓은 땅", "cost": 5000},
    3: {"cols": 45, "rows": 30, "name": "중간 땅", "cost": 15000},
    4: {"cols": 52, "rows": 35, "name": "큰 땅", "cost": 35000},
    5: {"cols": 60, "rows": 40, "name": "대농장", "cost": 70000},
}

MAP_EXPANSION_ORDER = [1, 2, 3, 4, 5]

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
