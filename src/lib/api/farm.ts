/**
 * Farm API Functions
 * 통합 배치 시스템 리팩토링 - 레거시 타입/함수 제거됨
 */

import { api } from './client';

// =====================================================
// Types
// =====================================================

export interface CharacterData {
  name: string;
  body: string;           // Body_1 ~ Body_9 (피부색)
  hair: string;           // Hairstyle_Short_Brown_Dark 형태
  hairColor: string;      // hex color (#3d2314)
  face: string;           // Eyes_Brown 등 (눈)
  outfit: string;         // Outfit_Dungarees_Green 등
  outfitColor: string;
  accessory: string;      // Accessory_Straw_Hat_Green 등 또는 'none'
  farmName: string;
}

/**
 * CharacterCreationModal에서 반환하는 형식
 * API 호출 전 transformCharacterInput으로 변환 필요
 */
export interface CharacterModalInput {
  name: string;
  appearance: {
    body: string;       // Body_1 ~ Body_9
    hair: string;       // 헤어스타일 ID (Short, Long 등)
    hairColor: string;  // 헤어 색상 ID (Brown_Dark 등)
    face: string;       // Eyes_Brown 등
    clothes: string;    // Outfit_Dungarees_Green 등
    accessory: string;  // Accessory 코드 또는 'none'
    color: string;      // hex color (#3d2314)
  };
  farmName: string;
}

// 레거시 색상 키 → hex 매핑 (이전 버전 호환용)
const COLOR_MAP: Record<string, string> = {
  brown: '#8B4513',
  black: '#2d2d2d',
  blonde: '#f4d03f',
  red: '#c0392b',
  blue: '#3498db',
  pink: '#e91e8a',
};

/**
 * CharacterCreationModal의 데이터를 API 형식으로 변환
 */
export function transformCharacterInput(input: CharacterModalInput): {
  name: string;
  body: string;
  hair: string;
  hairColor: string;
  face: string;
  outfit: string;
  outfitColor: string;
  accessory: string;
  farmName: string;
} {
  // hex 색상 변환 (레거시 키 형식 지원)
  const hairColorHex = input.appearance.color.startsWith('#')
    ? input.appearance.color
    : COLOR_MAP[input.appearance.color] || '#8B4513';

  // 헤어스타일 파일명 조합: Short_Brown_Dark 형태
  const hairStyleFull = `${input.appearance.hair}_${input.appearance.hairColor}`;

  return {
    name: input.name,
    body: input.appearance.body,
    hair: hairStyleFull,
    hairColor: hairColorHex,
    face: input.appearance.face,
    outfit: input.appearance.clothes,
    outfitColor: hairColorHex,
    accessory: input.appearance.accessory,
    farmName: input.farmName || `${input.name}의 농장`,
  };
}

export interface UserFarm {
  id: string;
  userId: string;
  characterCreated: boolean;
  characterData: CharacterData | null;
  farmUnlocked: boolean;
  farmLevel: number;
  gold: number;
  farmSize: number;  // 밭 슬롯 개수 (1, 4, 9, 16, 25)
  houseLevel: number;
  farmSlots: FarmSlot[];  // 밭 그리드 슬롯 데이터
  createdAt: string;
  updatedAt: string;
}

export interface FarmItem {
  id: string;
  code: string;
  name: string;
  nameKo: string;
  type: string;
  rarity: 'common' | 'uncommon' | 'rare' | 'epic';
  imageUrl: string | null;
  seedCost: number;
  sellPrice: number;
  xpReward: number;
  growTimeSeconds: number;
}

export interface InventoryItem {
  itemCode: string;
  quantity: number;
}

export interface BuyResponse {
  success: boolean;
  message: string;
  inventory: InventoryItem[];
  gold: number;
}

export interface SellResponse {
  success: boolean;
  message: string;
  goldEarned: number;
  inventory: InventoryItem[];
  gold: number;
}

export interface ExpansionOption {
  size: number;
  grid: string;
  name: string;
  cost: number;
  isCurrent: boolean;
  canAfford: boolean;
}

export interface ExpansionCostsResponse {
  currentSize: number;
  gold: number;
  options: ExpansionOption[];
}

export interface ExpandResponse {
  success: boolean;
  message: string;
  farmSize: number;
  gold: number;
  farmSlots: FarmSlot[];
}

// =====================================================
// 레거시 Customization/ShopItem 타입 제거됨
// 통합 배치 시스템 타입(UnifiedShopItem, PlacedItem) 사용
// =====================================================

// =====================================================
// Unified Placement System Types (신규)
// =====================================================

export interface ItemMetadata {
  sprite: string;
  width: number;
  height: number;
  depth: number;
  canMove: boolean;
  canDelete: boolean;
  anchor?: number[];
  collision?: boolean;
  // 충돌 영역 (이미지와 별도로 정의, 없으면 width/height 사용)
  collisionWidth?: number;
  collisionHeight?: number;
  collisionOffsetX?: number;  // 타일 기준 X 오프셋
  collisionOffsetY?: number;  // 타일 기준 Y 오프셋
}

export interface UnifiedShopItem {
  code: string;
  name: string;
  nameKo: string;
  category: 'building' | 'tree' | 'decoration' | 'fence' | 'farm';
  rarity: string;
  price: number;
  maxQuantity: number | null;
  owned: number;      // 인벤토리 보유량
  placed: number;     // 배치된 개수
  canBuy: boolean;
  metadata: ItemMetadata;
}

export interface PlacedItem {
  id: string;
  itemCode: string;
  tileX: number;
  tileY: number;
  rotation: number;
  data: Record<string, unknown>;
  metadata: ItemMetadata;
  placedAt?: string;
}

export interface FarmPlotData {
  cropCode?: string;
  plantedAt?: string;
  stage?: number;
}

// =====================================================
// Slot-based Farm System Types (신규)
// =====================================================

export interface FarmSlot {
  slot: number;
  cropCode: string | null;
  plantedAt: string | null;
  growTimeSeconds: number | null;
  stage: number;
}

// Backend response types (snake_case)
interface BackendPlantSlotResponse {
  success: boolean;
  message: string;
  slot: FarmSlot;
  farm_slots: FarmSlot[];
  inventory: Record<string, number>;
}

interface BackendHarvestSlotResponse {
  success: boolean;
  message: string;
  slot: FarmSlot;
  farm_slots: FarmSlot[];
  rewards: { gold: number; xp: number };
  gold: number;
}

// Frontend types (camelCase)
export interface PlantSlotResponse {
  success: boolean;
  message: string;
  slot: FarmSlot;
  farmSlots: FarmSlot[];
  inventory: Record<string, number>;
}

export interface HarvestSlotResponse {
  success: boolean;
  message: string;
  slot: FarmSlot;
  farmSlots: FarmSlot[];
  rewards: { gold: number; xp: number };
  gold: number;
}

export interface UnifiedShopResponse {
  success: boolean;
  items: UnifiedShopItem[];
  gold: number;
}

export interface PlacedItemsResponse {
  success: boolean;
  items: PlacedItem[];
}

export interface PlaceItemResponse {
  success: boolean;
  message: string;
  item: PlacedItem;
  inventory: Record<string, number>;
}

export interface MoveItemResponse {
  success: boolean;
  message: string;
  item: PlacedItem;
}

export interface RemoveItemResponse {
  success: boolean;
  message: string;
  inventory: Record<string, number>;
}

// =====================================================
// Farm Init Response (통합 API)
// =====================================================

export interface FarmInitResponse {
  farm: UserFarm;
  items: FarmItem[];
  inventory: InventoryItem[];
  placedItems: PlacedItem[];
}

interface BackendFarmInitResponse {
  farm: BackendUserFarm;
  items: BackendFarmItem[];
  inventory: BackendInventoryItem[];
  placedItems: PlacedItem[];  // 이미 camelCase로 반환됨
}

export interface PlantCropResponse {
  success: boolean;
  message: string;
  item: PlacedItem;
  inventory: Record<string, number>;
}

export interface HarvestCropResponse {
  success: boolean;
  message: string;
  rewards: { gold: number; xp: number };
  item: PlacedItem;
  gold: number;
}

// 레거시 ShopResponse, PurchaseResponse, CustomizationResponse 제거됨

// =====================================================
// Backend Response Types (for transformation)
// =====================================================

interface BackendFarmSlot {
  slot: number;
  cropCode: string | null;
  plantedAt: string | null;
  growTimeSeconds: number | null;
  stage: number;
}

interface BackendUserFarm {
  id: string;
  user_id: string;
  character_created: boolean;
  character_data: {
    name: string;
    body: string;
    hair: string;
    hair_color: string;
    face: string;
    outfit: string;
    outfit_color: string;
    accessory: string;
    farm_name: string;
  } | null;
  farm_unlocked: boolean;
  farm_level: number;
  gold: number;
  farm_size: number;
  house_level: number;
  farm_slots: BackendFarmSlot[];
  created_at: string;
  updated_at: string;
}

interface BackendFarmItem {
  id: string;
  code: string;
  name: string;
  name_ko: string;
  type: string;
  rarity: string;
  image_url: string | null;
  seed_cost: number;
  sell_price: number;
  xp_reward: number;
  grow_time_seconds: number;
}

interface BackendInventoryItem {
  item_code: string;
  quantity: number;
}

interface BackendBuyResponse {
  success: boolean;
  message: string;
  inventory: BackendInventoryItem[];
  gold: number;
}

interface BackendExpansionOption {
  size: number;
  grid: string;
  name: string;
  cost: number;
  is_current: boolean;
  can_afford: boolean;
}

interface BackendExpansionCostsResponse {
  current_size: number;
  gold: number;
  options: BackendExpansionOption[];
}

interface BackendExpandResponse {
  success: boolean;
  message: string;
  farm_size: number;
  gold: number;
  farm_slots: BackendFarmSlot[];
}

// =====================================================
// Transform Functions
// =====================================================

function transformUserFarm(data: BackendUserFarm): UserFarm {
  return {
    id: data.id,
    userId: data.user_id,
    characterCreated: data.character_created,
    characterData: data.character_data
      ? {
          name: data.character_data.name,
          body: data.character_data.body || 'Body_1',
          hair: data.character_data.hair,
          hairColor: data.character_data.hair_color,
          face: data.character_data.face,
          outfit: data.character_data.outfit,
          outfitColor: data.character_data.outfit_color,
          accessory: data.character_data.accessory || 'none',
          farmName: data.character_data.farm_name,
        }
      : null,
    farmUnlocked: data.farm_unlocked,
    farmLevel: data.farm_level,
    gold: data.gold,
    farmSize: data.farm_size,
    houseLevel: data.house_level,
    farmSlots: (data.farm_slots || []).map(slot => ({
      slot: slot.slot,
      cropCode: slot.cropCode,
      plantedAt: slot.plantedAt,
      growTimeSeconds: slot.growTimeSeconds,
      stage: slot.stage,
    })),
    createdAt: data.created_at,
    updatedAt: data.updated_at,
  };
}

function transformFarmItem(data: BackendFarmItem): FarmItem {
  return {
    id: data.id,
    code: data.code,
    name: data.name,
    nameKo: data.name_ko,
    type: data.type,
    rarity: data.rarity as 'common' | 'uncommon' | 'rare' | 'epic',
    imageUrl: data.image_url,
    seedCost: data.seed_cost,
    sellPrice: data.sell_price,
    xpReward: data.xp_reward,
    growTimeSeconds: data.grow_time_seconds,
  };
}

function transformInventoryItem(data: BackendInventoryItem): InventoryItem {
  return {
    itemCode: data.item_code,
    quantity: data.quantity,
  };
}

// =====================================================
// API Functions
// =====================================================

export const farmApi = {
  /**
   * Get farm initialization data (통합 API - 권장)
   * 4개 API 호출을 1개로 통합하여 성능 개선
   */
  async getInit(): Promise<FarmInitResponse> {
    const response = await api.get<BackendFarmInitResponse>('/farm/init');
    if (response.error) throw new Error(response.error.message);
    const data = response.data!;
    return {
      farm: transformUserFarm(data.farm),
      items: (data.items || []).map(transformFarmItem),
      inventory: (data.inventory || []).map(transformInventoryItem),
      placedItems: data.placedItems || [],
    };
  },

  /**
   * Get farm status
   */
  async getFarm(): Promise<UserFarm> {
    const response = await api.get<BackendUserFarm>('/farm');
    if (response.error) throw new Error(response.error.message);
    return transformUserFarm(response.data!);
  },

  /**
   * Create character (unlocks farm)
   */
  async createCharacter(data: {
    name: string;
    body?: string;
    hair?: string;
    hairColor?: string;
    face?: string;
    outfit?: string;
    outfitColor?: string;
    accessory?: string;
    farmName?: string;
  }): Promise<UserFarm> {
    const response = await api.post<BackendUserFarm>('/farm/character', {
      name: data.name,
      body: data.body || 'Body_1',
      hair: data.hair || 'Short_Brown_Dark',
      hair_color: data.hairColor || '#3d2314',
      face: data.face || 'Eyes_Brown',
      outfit: data.outfit || 'Outfit_Dungarees_Green',
      outfit_color: data.outfitColor || '#27ae60',
      accessory: data.accessory || 'none',
      farm_name: data.farmName || '나의 농장',
    });
    if (response.error) throw new Error(response.error.message);
    return transformUserFarm(response.data!);
  },

  /**
   * Update character appearance
   */
  async updateCharacter(data: {
    name: string;
    body?: string;
    hair?: string;
    hairColor?: string;
    face?: string;
    outfit?: string;
    outfitColor?: string;
    accessory?: string;
    farmName?: string;
  }): Promise<UserFarm> {
    const response = await api.patch<BackendUserFarm>('/farm/character', {
      name: data.name,
      body: data.body || 'Body_1',
      hair: data.hair || 'Short_Brown_Dark',
      hair_color: data.hairColor || '#3d2314',
      face: data.face || 'Eyes_Brown',
      outfit: data.outfit || 'Outfit_Dungarees_Green',
      outfit_color: data.outfitColor || '#27ae60',
      accessory: data.accessory || 'none',
      farm_name: data.farmName || '나의 농장',
    });
    if (response.error) throw new Error(response.error.message);
    return transformUserFarm(response.data!);
  },

  /**
   * Get all farm items (crops)
   */
  async getItems(): Promise<FarmItem[]> {
    const response = await api.get<BackendFarmItem[]>('/farm/items');
    if (response.error) throw new Error(response.error.message);
    return (response.data || []).map(transformFarmItem);
  },

  /**
   * Get user inventory
   */
  async getInventory(): Promise<InventoryItem[]> {
    const response = await api.get<{ items: BackendInventoryItem[] }>('/farm/inventory');
    if (response.error) throw new Error(response.error.message);
    return (response.data?.items || []).map(transformInventoryItem);
  },

  // 레거시 plant(), harvest() 함수 제거됨
  // 통합 배치 시스템의 plantOnPlot(), harvestFromPlot() 사용

  /**
   * Buy seeds
   */
  async buySeed(cropCode: string, quantity: number = 1): Promise<BuyResponse> {
    const response = await api.post<BackendBuyResponse>('/farm/shop/buy', {
      crop_code: cropCode,
      quantity,
    });
    if (response.error) throw new Error(response.error.message);
    const data = response.data!;
    return {
      success: data.success,
      message: data.message,
      inventory: data.inventory.map(transformInventoryItem),
      gold: data.gold,
    };
  },

  /**
   * Sell harvested crops
   */
  async sellCrop(cropCode: string, quantity: number = 1): Promise<SellResponse> {
    const response = await api.post<BackendBuyResponse>('/farm/shop/sell', {
      crop_code: cropCode,
      quantity,
    });
    if (response.error) throw new Error(response.error.message);
    const data = response.data!;
    return {
      success: data.success,
      message: data.message,
      goldEarned: 0, // Not in backend response
      inventory: data.inventory.map(transformInventoryItem),
      gold: data.gold,
    };
  },

  /**
   * Get expansion costs
   */
  async getExpansionCosts(): Promise<ExpansionCostsResponse> {
    const response = await api.get<BackendExpansionCostsResponse>('/farm/expansion-costs');
    if (response.error) throw new Error(response.error.message);
    const data = response.data!;
    return {
      currentSize: data.current_size,
      gold: data.gold,
      options: data.options.map((opt) => ({
        size: opt.size,
        grid: opt.grid,
        name: opt.name,
        cost: opt.cost,
        isCurrent: opt.is_current,
        canAfford: opt.can_afford,
      })),
    };
  },

  /**
   * Expand farm
   */
  async expand(targetSize: number): Promise<ExpandResponse> {
    const response = await api.post<BackendExpandResponse>('/farm/expand', {
      target_size: targetSize,
    });
    if (response.error) throw new Error(response.error.message);
    const data = response.data!;
    return {
      success: data.success,
      message: data.message,
      farmSize: data.farm_size,
      gold: data.gold,
      farmSlots: (data.farm_slots || []).map(slot => ({
        slot: slot.slot,
        cropCode: slot.cropCode,
        plantedAt: slot.plantedAt,
        growTimeSeconds: slot.growTimeSeconds,
        stage: slot.stage,
      })),
    };
  },

  // 레거시 getCustomization, updateCustomization, getBuildingShop, purchaseBuilding 함수 제거됨
  // 통합 배치 시스템(placement API, shop API) 사용

  // =====================================================
  // Unified Placement System API
  // =====================================================

  /**
   * Get unified shop items
   */
  async getUnifiedShopItems(category?: string): Promise<UnifiedShopResponse> {
    const url = category ? `/shop/items?category=${category}` : '/shop/items';
    console.log('[farmApi] getUnifiedShopItems - url:', url);
    const response = await api.get<UnifiedShopResponse>(url);
    console.log('[farmApi] getUnifiedShopItems - response:', response);
    if (response.error) throw new Error(response.error.message);
    console.log('[farmApi] getUnifiedShopItems - data:', response.data);
    return response.data!;
  },

  /**
   * Buy item from unified shop
   */
  async buyShopItem(itemCode: string, quantity: number = 1): Promise<{ success: boolean; message: string; gold: number; inventory: Record<string, number> }> {
    const response = await api.post<{ success: boolean; message: string; gold: number; inventory: Record<string, number> }>('/shop/buy', {
      item_code: itemCode,
      quantity,
    });
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  /**
   * Get all placed items
   */
  async getPlacedItems(): Promise<PlacedItem[]> {
    const response = await api.get<PlacedItemsResponse>('/placement/items');
    if (response.error) throw new Error(response.error.message);
    return response.data!.items;
  },

  /**
   * Place an item from inventory
   */
  async placeItem(itemCode: string, tileX: number, tileY: number): Promise<PlaceItemResponse> {
    const response = await api.post<PlaceItemResponse>('/placement/place', {
      item_code: itemCode,
      tile_x: tileX,
      tile_y: tileY,
    });
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  /**
   * Move a placed item
   */
  async moveItem(itemId: string, tileX: number, tileY: number): Promise<MoveItemResponse> {
    const response = await api.patch<MoveItemResponse>(`/placement/items/${itemId}`, {
      tile_x: tileX,
      tile_y: tileY,
    });
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  /**
   * Remove a placed item (return to inventory)
   */
  async removeItem(itemId: string): Promise<RemoveItemResponse> {
    const response = await api.delete<RemoveItemResponse>(`/placement/items/${itemId}`);
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  // =====================================================
  // Slot-based Farm System API (신규)
  // =====================================================

  /**
   * Plant a crop on a farm slot
   */
  async plantOnSlot(slot: number, cropCode: string): Promise<PlantSlotResponse> {
    const response = await api.post<BackendPlantSlotResponse>(`/farm/slots/${slot}/plant`, {
      crop_code: cropCode,
    });
    if (response.error) throw new Error(response.error.message);
    const data = response.data!;
    // Transform snake_case to camelCase
    return {
      success: data.success,
      message: data.message,
      slot: data.slot,
      farmSlots: data.farm_slots,
      inventory: data.inventory,
    };
  },

  /**
   * Harvest a crop from a farm slot
   */
  async harvestFromSlot(slot: number): Promise<HarvestSlotResponse> {
    const response = await api.post<BackendHarvestSlotResponse>(`/farm/slots/${slot}/harvest`, {});
    if (response.error) throw new Error(response.error.message);
    const data = response.data!;
    // Transform snake_case to camelCase
    return {
      success: data.success,
      message: data.message,
      slot: data.slot,
      farmSlots: data.farm_slots,
      rewards: data.rewards,
      gold: data.gold,
    };
  },

  // =====================================================
  // Legacy Placement-based Farm API (deprecated)
  // Use slot-based API instead
  // =====================================================

  /**
   * @deprecated Use plantOnSlot instead
   */
  async plantOnPlot(plotId: string, cropCode: string): Promise<PlantCropResponse> {
    const response = await api.post<PlantCropResponse>(`/placement/items/${plotId}/plant`, {
      crop_code: cropCode,
    });
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  /**
   * @deprecated Use harvestFromSlot instead
   */
  async harvestFromPlot(plotId: string): Promise<HarvestCropResponse> {
    const response = await api.post<HarvestCropResponse>(`/placement/items/${plotId}/harvest`, {});
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },
};
