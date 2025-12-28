/**
 * Farm API Functions
 */

import { api } from './client';

// =====================================================
// Types
// =====================================================

export interface CharacterData {
  name: string;
  hair: string;
  hairColor: string;
  face: string;
  outfit: string;
  outfitColor: string;
  farmName: string;
}

export interface FarmSlot {
  slot: number;
  cropCode: string | null;
  plantedAt: string | null;
  stage: 0 | 1 | 2 | 3 | 4;
}

export interface UserFarm {
  id: string;
  userId: string;
  characterCreated: boolean;
  characterData: CharacterData | null;
  farmUnlocked: boolean;
  farmLevel: number;
  gold: number;
  farmSize: number;
  farmSlots: FarmSlot[];
  houseLevel: number;
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

export interface PlantResponse {
  success: boolean;
  message: string;
  farmSlots: FarmSlot[];
  inventory: InventoryItem[];
}

export interface HarvestResponse {
  success: boolean;
  message: string;
  rewards: { gold: number; xp: number };
  farmSlots: FarmSlot[];
  gold: number;
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
}

// =====================================================
// Backend Response Types (for transformation)
// =====================================================

interface BackendUserFarm {
  id: string;
  user_id: string;
  character_created: boolean;
  character_data: {
    name: string;
    hair: string;
    hair_color: string;
    face: string;
    outfit: string;
    outfit_color: string;
    farm_name: string;
  } | null;
  farm_unlocked: boolean;
  farm_level: number;
  gold: number;
  farm_size: number;
  farm_slots: Array<{
    slot: number;
    crop_code: string | null;
    planted_at: string | null;
    stage: number;
  }>;
  house_level: number;
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

interface BackendPlantResponse {
  success: boolean;
  message: string;
  farm_slots: Array<{
    slot: number;
    crop_code: string | null;
    planted_at: string | null;
    stage: number;
  }>;
  inventory: BackendInventoryItem[];
}

interface BackendHarvestResponse {
  success: boolean;
  message: string;
  rewards: { gold: number; xp: number };
  farm_slots: Array<{
    slot: number;
    crop_code: string | null;
    planted_at: string | null;
    stage: number;
  }>;
  gold: number;
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
          hair: data.character_data.hair,
          hairColor: data.character_data.hair_color,
          face: data.character_data.face,
          outfit: data.character_data.outfit,
          outfitColor: data.character_data.outfit_color,
          farmName: data.character_data.farm_name,
        }
      : null,
    farmUnlocked: data.farm_unlocked,
    farmLevel: data.farm_level,
    gold: data.gold,
    farmSize: data.farm_size,
    farmSlots: data.farm_slots.map((slot) => ({
      slot: slot.slot,
      cropCode: slot.crop_code,
      plantedAt: slot.planted_at,
      stage: slot.stage as 0 | 1 | 2 | 3 | 4,
    })),
    houseLevel: data.house_level,
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

function transformFarmSlots(
  slots: Array<{ slot: number; crop_code: string | null; planted_at: string | null; stage: number }>
): FarmSlot[] {
  return slots.map((slot) => ({
    slot: slot.slot,
    cropCode: slot.crop_code,
    plantedAt: slot.planted_at,
    stage: slot.stage as 0 | 1 | 2 | 3 | 4,
  }));
}

// =====================================================
// API Functions
// =====================================================

export const farmApi = {
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
    hair?: string;
    hairColor?: string;
    face?: string;
    outfit?: string;
    outfitColor?: string;
    farmName?: string;
  }): Promise<UserFarm> {
    const response = await api.post<BackendUserFarm>('/farm/character', {
      name: data.name,
      hair: data.hair || 'style_01',
      hair_color: data.hairColor || '#8B4513',
      face: data.face || 'face_01',
      outfit: data.outfit || 'outfit_casual',
      outfit_color: data.outfitColor || '#4169E1',
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

  /**
   * Plant a seed
   */
  async plant(slot: number, cropCode: string): Promise<PlantResponse> {
    const response = await api.post<BackendPlantResponse>('/farm/plant', {
      slot,
      crop_code: cropCode,
    });
    if (response.error) throw new Error(response.error.message);
    const data = response.data!;
    return {
      success: data.success,
      message: data.message,
      farmSlots: transformFarmSlots(data.farm_slots),
      inventory: data.inventory.map(transformInventoryItem),
    };
  },

  /**
   * Harvest a crop
   */
  async harvest(slot: number): Promise<HarvestResponse> {
    const response = await api.post<BackendHarvestResponse>('/farm/harvest', { slot });
    if (response.error) throw new Error(response.error.message);
    const data = response.data!;
    return {
      success: data.success,
      message: data.message,
      rewards: data.rewards,
      farmSlots: transformFarmSlots(data.farm_slots),
      gold: data.gold,
    };
  },

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
    };
  },
};
