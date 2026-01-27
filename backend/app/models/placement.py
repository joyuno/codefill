"""
Unified Placement System Models
통합 배치 시스템 모델
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from enum import Enum


class ItemCategory(str, Enum):
    """아이템 카테고리"""
    BUILDING = "building"
    TREE = "tree"
    DECORATION = "decoration"
    FENCE = "fence"
    FARM = "farm"


class ItemRarity(str, Enum):
    """아이템 희귀도"""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"


# =====================================================
# Item Metadata (DB에서 로드)
# =====================================================

class ItemMetadata(BaseModel):
    """아이템 메타데이터 (렌더링 정보)"""
    sprite: str
    width: int = 1
    height: int = 1
    depth: int = 50
    canMove: bool = True
    canDelete: bool = True
    anchor: Optional[List[float]] = None
    collision: Optional[bool] = None


# =====================================================
# Shop Item Models
# =====================================================

class ShopItemResponse(BaseModel):
    """상점 아이템 응답"""
    code: str
    name: str
    nameKo: str
    category: str
    rarity: str
    price: int
    maxQuantity: Optional[int] = None
    owned: int = 0        # 인벤토리 보유량
    placed: int = 0       # 배치된 개수
    canBuy: bool = True
    metadata: ItemMetadata


class ShopListResponse(BaseModel):
    """상점 아이템 목록 응답"""
    success: bool
    items: List[ShopItemResponse]
    gold: int


class BuyItemRequest(BaseModel):
    """아이템 구매 요청"""
    item_code: str
    quantity: int = Field(default=1, ge=1, le=99)


class BuyItemResponse(BaseModel):
    """아이템 구매 응답"""
    success: bool
    message: str
    gold: int
    inventory: Dict[str, int]  # { item_code: quantity }


# =====================================================
# Placed Item Models
# =====================================================

class FarmPlotData(BaseModel):
    """밭 아이템 데이터 (작물 정보)"""
    cropCode: Optional[str] = None
    plantedAt: Optional[datetime] = None
    stage: int = 0


class PlacedItemResponse(BaseModel):
    """배치된 아이템 응답"""
    id: str
    itemCode: str
    tileX: int
    tileY: int
    rotation: int = 0
    data: Dict[str, Any] = {}
    metadata: ItemMetadata
    placedAt: Optional[datetime] = None


class PlacedItemsListResponse(BaseModel):
    """배치된 아이템 목록 응답"""
    success: bool
    items: List[PlacedItemResponse]


class PlaceItemRequest(BaseModel):
    """아이템 배치 요청"""
    item_code: str
    tile_x: int = Field(..., ge=0)
    tile_y: int = Field(..., ge=0)


class PlaceItemResponse(BaseModel):
    """아이템 배치 응답"""
    success: bool
    message: str
    item: PlacedItemResponse
    inventory: Dict[str, int]


class MoveItemRequest(BaseModel):
    """아이템 이동 요청"""
    tile_x: int = Field(..., ge=0)
    tile_y: int = Field(..., ge=0)


class MoveItemResponse(BaseModel):
    """아이템 이동 응답"""
    success: bool
    message: str
    item: PlacedItemResponse


class RemoveItemResponse(BaseModel):
    """아이템 제거 응답"""
    success: bool
    message: str
    inventory: Dict[str, int]


# =====================================================
# Farm Plot Action Models (작물 심기/수확)
# =====================================================

class PlantCropRequest(BaseModel):
    """작물 심기 요청"""
    crop_code: str


class PlantCropResponse(BaseModel):
    """작물 심기 응답"""
    success: bool
    message: str
    item: PlacedItemResponse
    inventory: Dict[str, int]


class HarvestCropResponse(BaseModel):
    """작물 수확 응답"""
    success: bool
    message: str
    rewards: Dict[str, int]  # { "gold": 25, "xp": 5 }
    item: PlacedItemResponse
    gold: int


# =====================================================
# Constants
# =====================================================

# 맵 크기 (타일 단위) - 기본값 (레벨 1)
# 동적 맵 확장을 위해 farm.py의 MAP_EXPANSION_COSTS 사용 권장
MAP_WIDTH_TILES = 30
MAP_HEIGHT_TILES = 20

# 맵 확장 레벨별 크기 (farm.py와 동기화 필요)
MAP_EXPANSION_TILES = {
    1: {"cols": 30, "rows": 20},
    2: {"cols": 38, "rows": 25},
    3: {"cols": 45, "rows": 30},
    4: {"cols": 52, "rows": 35},
    5: {"cols": 60, "rows": 40},
}


def get_map_dimensions(map_level: int) -> dict:
    """맵 레벨에 따른 맵 크기 반환"""
    return MAP_EXPANSION_TILES.get(map_level, MAP_EXPANSION_TILES[1])
