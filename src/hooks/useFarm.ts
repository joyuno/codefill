'use client';

/**
 * useFarm Hook
 * 통합 배치 시스템 리팩토링 - 레거시 상태/함수 제거됨
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { farmApi, type UserFarm, type FarmItem, type InventoryItem, type UnifiedShopItem, type PlacedItem, type FarmSlot } from '@/lib/api';

interface UseFarmReturn {
  // State
  farm: UserFarm | null;
  items: FarmItem[];
  inventory: InventoryItem[];
  isLoading: boolean;
  error: string | null;

  // Unified Placement State
  placedItems: PlacedItem[];
  unifiedShopItems: UnifiedShopItem[];

  // Actions
  createCharacter: (data: {
    name: string;
    hair?: string;
    hairColor?: string;
    face?: string;
    outfit?: string;
    outfitColor?: string;
    farmName?: string;
  }) => Promise<void>;
  buySeed: (cropCode: string, quantity?: number) => Promise<void>;
  expand: (targetSize: number) => Promise<void>;
  refresh: () => Promise<void>;

  // Slot-based Farm Actions (신규)
  plantOnSlot: (slot: number, cropCode: string) => Promise<FarmSlot | null>;
  harvestFromSlot: (slot: number) => Promise<{ gold: number; xp: number; slot: FarmSlot } | null>;

  // Unified Placement Actions
  loadUnifiedShop: (category?: string) => Promise<void>;
  buyUnifiedItem: (itemCode: string, quantity?: number) => Promise<void>;
  loadPlacedItems: () => Promise<void>;
  placeItem: (itemCode: string, tileX: number, tileY: number) => Promise<PlacedItem>;
  moveItem: (itemId: string, tileX: number, tileY: number) => Promise<void>;
  removeItem: (itemId: string) => Promise<void>;

  /** @deprecated Use plantOnSlot instead */
  plantOnPlot: (plotId: string, cropCode: string) => Promise<void>;
  /** @deprecated Use harvestFromSlot instead */
  harvestFromPlot: (plotId: string) => Promise<{ gold: number; xp: number }>;
}

export function useFarm(): UseFarmReturn {
  const [farm, setFarm] = useState<UserFarm | null>(null);
  const [items, setItems] = useState<FarmItem[]>([]);
  const [inventory, setInventory] = useState<InventoryItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Unified Placement State
  const [placedItems, setPlacedItems] = useState<PlacedItem[]>([]);
  const [unifiedShopItems, setUnifiedShopItems] = useState<UnifiedShopItem[]>([]);

  const initializedRef = useRef(false);

  // placedItems의 최신 상태를 ref로 유지 (클로저 문제 방지)
  const placedItemsRef = useRef<PlacedItem[]>([]);
  useEffect(() => {
    placedItemsRef.current = placedItems;
  }, [placedItems]);

  // Load initial data (통합 API 사용 - 4 HTTP → 1 HTTP)
  const loadFarmData = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);

      // 통합 API로 모든 데이터를 한 번에 가져옴
      const initData = await farmApi.getInit();

      setFarm(initData.farm);
      setItems(initData.items);
      setInventory(initData.inventory);
      setPlacedItems(initData.placedItems);
    } catch (err) {
      console.error('Farm data load error:', err);
      setError(err instanceof Error ? err.message : '농장 데이터를 불러오는데 실패했습니다');
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Initialize on mount
  useEffect(() => {
    if (initializedRef.current) return;
    initializedRef.current = true;

    // Check if user is authenticated
    const token = localStorage.getItem('access_token');
    if (!token) {
      setIsLoading(false);
      setError('로그인이 필요합니다');
      return;
    }

    loadFarmData();
  }, [loadFarmData]);

  // Create character
  const createCharacter = useCallback(async (data: {
    name: string;
    hair?: string;
    hairColor?: string;
    face?: string;
    outfit?: string;
    outfitColor?: string;
    farmName?: string;
  }) => {
    try {
      setError(null);
      const updatedFarm = await farmApi.createCharacter(data);
      setFarm(updatedFarm);

      // Reload inventory and placed items (initial items are granted)
      const [inventoryData, placedItemsData] = await Promise.all([
        farmApi.getInventory(),
        farmApi.getPlacedItems(),
      ]);
      setInventory(inventoryData);
      setPlacedItems(placedItemsData);
    } catch (err) {
      const message = err instanceof Error ? err.message : '캐릭터 생성에 실패했습니다';
      setError(message);
      throw err;
    }
  }, []);

  // Buy seeds (legacy method, still works via /farm/shop/buy)
  // 주의: 액션 에러 시 setError 사용 안함 (호출자가 토스트로 처리)
  const buySeed = useCallback(async (cropCode: string, quantity: number = 1) => {
    const result = await farmApi.buySeed(cropCode, quantity);
    setFarm(prev => prev ? { ...prev, gold: result.gold } : null);
    setInventory(result.inventory);
  }, []);

  // Expand farm (그리드 확장 + farmSlots 배열 확장)
  // 주의: 액션 에러 시 setError 사용 안함 (호출자가 토스트로 처리)
  const expand = useCallback(async (targetSize: number) => {
    const result = await farmApi.expand(targetSize);
    setFarm(prev => prev ? {
      ...prev,
      farmSize: result.farmSize,
      gold: result.gold,
      farmSlots: result.farmSlots,
    } : null);
  }, []);

  // Refresh all data
  const refresh = useCallback(async () => {
    await loadFarmData();
  }, [loadFarmData]);

  // ====== Unified Placement Actions ======

  // Load unified shop items
  // 주의: 액션 에러 시 setError 사용 안함 (호출자가 토스트로 처리)
  const loadUnifiedShop = useCallback(async (category?: string) => {
    console.log('[useFarm] loadUnifiedShop called, category:', category);
    try {
      const result = await farmApi.getUnifiedShopItems(category);
      console.log('[useFarm] loadUnifiedShop result:', result);
      console.log('[useFarm] items count:', result.items?.length);
      setUnifiedShopItems(result.items);
      setFarm(prev => prev ? { ...prev, gold: result.gold } : null);
    } catch (err) {
      console.error('[useFarm] loadUnifiedShop error:', err);
    }
  }, []);

  // Buy item from unified shop
  // 주의: 액션 에러 시 setError 사용 안함 (호출자가 토스트로 처리)
  const buyUnifiedItem = useCallback(async (itemCode: string, quantity: number = 1) => {
    const result = await farmApi.buyShopItem(itemCode, quantity);
    setFarm(prev => prev ? { ...prev, gold: result.gold } : null);

    // Update inventory from response
    const inventoryArray: InventoryItem[] = Object.entries(result.inventory).map(
      ([code, qty]) => ({ itemCode: code, quantity: qty })
    );
    setInventory(inventoryArray);

    // Reload shop to update counts
    await loadUnifiedShop();
  }, [loadUnifiedShop]);

  // Load placed items
  // 주의: 액션 에러 시 setError 사용 안함 (호출자가 토스트로 처리)
  const loadPlacedItems = useCallback(async () => {
    const items = await farmApi.getPlacedItems();
    setPlacedItems(items);
  }, []);

  // Place item on map
  // 주의: 액션 에러 시 setError 사용 안함 (호출자가 토스트로 처리)
  const placeItem = useCallback(async (itemCode: string, tileX: number, tileY: number): Promise<PlacedItem> => {
    const response = await farmApi.placeItem(itemCode, tileX, tileY);
    setPlacedItems(prev => [...prev, response.item]);

    // Update shop inventory
    setUnifiedShopItems(prev => prev.map(item =>
      item.code === itemCode
        ? { ...item, owned: item.owned - 1, placed: item.placed + 1 }
        : item
    ));

    // Update inventory
    const inventoryArray: InventoryItem[] = Object.entries(response.inventory).map(
      ([code, qty]) => ({ itemCode: code, quantity: qty })
    );
    setInventory(inventoryArray);

    return response.item;
  }, []);

  // Move placed item
  // 주의: 액션 에러 시 setError 사용 안함 (호출자가 토스트로 처리)
  const moveItem = useCallback(async (itemId: string, tileX: number, tileY: number) => {
    await farmApi.moveItem(itemId, tileX, tileY);
    setPlacedItems(prev => prev.map(item =>
      item.id === itemId ? { ...item, tileX, tileY } : item
    ));
  }, []);

  // Remove placed item (return to inventory)
  // 주의: 에러 시 setError 대신 throw만 함 (호출자가 토스트로 처리)
  const removeItem = useCallback(async (itemId: string) => {
    // placedItemsRef로 최신 상태 접근 (클로저 문제 방지)
    const removedItem = placedItemsRef.current.find(item => item.id === itemId);

    const response = await farmApi.removeItem(itemId);

    setPlacedItems(prev => prev.filter(item => item.id !== itemId));

    // Update shop inventory
    if (removedItem) {
      setUnifiedShopItems(prev => prev.map(item =>
        item.code === removedItem.itemCode
          ? { ...item, owned: item.owned + 1, placed: item.placed - 1 }
          : item
      ));
    }

    // Update inventory
    const inventoryArray: InventoryItem[] = Object.entries(response.inventory).map(
      ([code, qty]) => ({ itemCode: code, quantity: qty })
    );
    setInventory(inventoryArray);
  }, []);

  // ====== Slot-based Farm Actions (신규) ======

  // Plant crop on farm slot
  // 주의: 액션 에러 시 setError 사용 안함 (호출자가 토스트로 처리)
  const plantOnSlot = useCallback(async (slot: number, cropCode: string): Promise<FarmSlot | null> => {
    console.log('[useFarm] plantOnSlot called:', { slot, cropCode });
    const result = await farmApi.plantOnSlot(slot, cropCode);
    console.log('[useFarm] plantOnSlot result:', result);

    // Update farmSlots in farm state
    setFarm(prev => {
      if (!prev) return null;
      console.log('[useFarm] Updating farm with farmSlots:', result.farmSlots);
      return {
        ...prev,
        farmSlots: result.farmSlots,
      };
    });

    // Update inventory
    const inventoryArray: InventoryItem[] = Object.entries(result.inventory).map(
      ([code, qty]) => ({ itemCode: code, quantity: qty })
    );
    setInventory(inventoryArray);

    console.log('[useFarm] Returning slot:', result.slot);
    return result.slot;
  }, []);

  // Harvest crop from farm slot
  // 주의: 액션 에러 시 setError 사용 안함 (호출자가 토스트로 처리)
  const harvestFromSlot = useCallback(async (slot: number): Promise<{ gold: number; xp: number; slot: FarmSlot } | null> => {
    const result = await farmApi.harvestFromSlot(slot);

    // Update farmSlots in farm state
    setFarm(prev => {
      if (!prev) return null;
      return {
        ...prev,
        gold: result.gold,
        farmSlots: result.farmSlots,
      };
    });

    return {
      gold: result.rewards.gold,
      xp: result.rewards.xp,
      slot: result.slot,
    };
  }, []);

  // ====== Legacy Placement-based Farm Actions (deprecated) ======

  // Plant crop on farm plot
  // 주의: 액션 에러 시 setError 사용 안함 (호출자가 토스트로 처리)
  const plantOnPlot = useCallback(async (plotId: string, cropCode: string) => {
    const result = await farmApi.plantOnPlot(plotId, cropCode);

    // Update the placed item with crop data
    setPlacedItems(prev => prev.map(item =>
      item.id === plotId
        ? { ...item, data: { cropCode, plantedAt: new Date().toISOString(), stage: 1 } }
        : item
    ));

    // Update inventory
    const inventoryArray: InventoryItem[] = Object.entries(result.inventory).map(
      ([code, qty]) => ({ itemCode: code, quantity: qty })
    );
    setInventory(inventoryArray);
  }, []);

  // Harvest crop from farm plot
  // 주의: 액션 에러 시 setError 사용 안함 (호출자가 토스트로 처리)
  const harvestFromPlot = useCallback(async (plotId: string): Promise<{ gold: number; xp: number }> => {
    const result = await farmApi.harvestFromPlot(plotId);

    // Clear the plot's crop data
    setPlacedItems(prev => prev.map(item =>
      item.id === plotId
        ? { ...item, data: {} }
        : item
    ));

    // Update gold
    setFarm(prev => prev ? { ...prev, gold: result.gold } : null);

    return result.rewards;
  }, []);

  return {
    // State
    farm,
    items,
    inventory,
    isLoading,
    error,

    // Unified Placement State
    placedItems,
    unifiedShopItems,

    // Actions
    createCharacter,
    buySeed,
    expand,
    refresh,

    // Slot-based Farm Actions (신규)
    plantOnSlot,
    harvestFromSlot,

    // Unified Placement Actions
    loadUnifiedShop,
    buyUnifiedItem,
    loadPlacedItems,
    placeItem,
    moveItem,
    removeItem,

    // Legacy (deprecated)
    plantOnPlot,
    harvestFromPlot,
  };
}

// Helper: Get seed count for a crop
export function getSeedCount(inventory: InventoryItem[], cropCode: string): number {
  const seedItem = inventory.find(item => item.itemCode === `seed_${cropCode}`);
  return seedItem?.quantity || 0;
}

// Helper: Get crop info by code
export function getCropInfo(items: FarmItem[], cropCode: string): FarmItem | undefined {
  return items.find(item => item.code === cropCode);
}

// Helper: Calculate crop stage from planted time
export function calculateCropStage(
  plantedAt: string | null,
  growTimeSeconds: number
): 0 | 1 | 2 | 3 | 4 {
  if (!plantedAt) return 0;

  const planted = new Date(plantedAt).getTime();
  const now = Date.now();
  const elapsed = (now - planted) / 1000; // seconds
  const progress = elapsed / growTimeSeconds;

  if (progress >= 1.0) return 4;
  if (progress >= 0.75) return 3;
  if (progress >= 0.5) return 2;
  if (progress >= 0.25) return 1;
  return 1;
}

// Helper: Get remaining time for a crop
export function getRemainingTime(
  plantedAt: string | null,
  growTimeSeconds: number
): number {
  if (!plantedAt) return 0;

  const planted = new Date(plantedAt).getTime();
  const now = Date.now();
  const elapsed = (now - planted) / 1000;
  const remaining = growTimeSeconds - elapsed;

  return Math.max(0, Math.ceil(remaining));
}
