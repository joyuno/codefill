'use client';

/**
 * useFarm Hook
 * 통합 배치 시스템 리팩토링 - 레거시 상태/함수 제거됨
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { farmApi, type UserFarm, type FarmItem, type InventoryItem, type UnifiedShopItem, type PlacedItem } from '@/lib/api';

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

  // Unified Placement Actions
  loadUnifiedShop: (category?: string) => Promise<void>;
  buyUnifiedItem: (itemCode: string, quantity?: number) => Promise<void>;
  loadPlacedItems: () => Promise<void>;
  placeItem: (itemCode: string, tileX: number, tileY: number) => Promise<PlacedItem | null>;
  moveItem: (itemId: string, tileX: number, tileY: number) => Promise<void>;
  removeItem: (itemId: string) => Promise<void>;
  plantOnPlot: (plotId: string, cropCode: string) => Promise<void>;
  harvestFromPlot: (plotId: string) => Promise<{ gold: number; xp: number } | null>;
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

  // Load initial data
  const loadFarmData = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);

      const [farmData, itemsData, inventoryData, placedItemsData] = await Promise.all([
        farmApi.getFarm(),
        farmApi.getItems(),
        farmApi.getInventory(),
        farmApi.getPlacedItems().catch(() => []),
      ]);

      setFarm(farmData);
      setItems(itemsData);
      setInventory(inventoryData);
      setPlacedItems(placedItemsData);
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
  const buySeed = useCallback(async (cropCode: string, quantity: number = 1) => {
    try {
      setError(null);
      const result = await farmApi.buySeed(cropCode, quantity);

      setFarm(prev => prev ? { ...prev, gold: result.gold } : null);
      setInventory(result.inventory);
    } catch (err) {
      const message = err instanceof Error ? err.message : '씨앗 구매에 실패했습니다';
      setError(message);
      throw err;
    }
  }, []);

  // Expand farm (배치 영역만 확장)
  const expand = useCallback(async (targetSize: number) => {
    try {
      setError(null);
      const result = await farmApi.expand(targetSize);

      setFarm(prev => prev ? { ...prev, farmSize: result.farmSize, gold: result.gold } : null);
    } catch (err) {
      const message = err instanceof Error ? err.message : '농장 확장에 실패했습니다';
      setError(message);
      throw err;
    }
  }, []);

  // Refresh all data
  const refresh = useCallback(async () => {
    await loadFarmData();
  }, [loadFarmData]);

  // ====== Unified Placement Actions ======

  // Load unified shop items
  const loadUnifiedShop = useCallback(async (category?: string) => {
    try {
      setError(null);
      const result = await farmApi.getUnifiedShopItems(category);
      setUnifiedShopItems(result.items);
      setFarm(prev => prev ? { ...prev, gold: result.gold } : null);
    } catch (err) {
      const message = err instanceof Error ? err.message : '상점 정보를 불러오는데 실패했습니다';
      setError(message);
      throw err;
    }
  }, []);

  // Buy item from unified shop
  const buyUnifiedItem = useCallback(async (itemCode: string, quantity: number = 1) => {
    try {
      setError(null);
      const result = await farmApi.buyShopItem(itemCode, quantity);
      setFarm(prev => prev ? { ...prev, gold: result.gold } : null);

      // Update inventory from response
      const inventoryArray: InventoryItem[] = Object.entries(result.inventory).map(
        ([code, qty]) => ({ itemCode: code, quantity: qty })
      );
      setInventory(inventoryArray);

      // Reload shop to update counts
      await loadUnifiedShop();
    } catch (err) {
      const message = err instanceof Error ? err.message : '구매에 실패했습니다';
      setError(message);
      throw err;
    }
  }, [loadUnifiedShop]);

  // Load placed items
  const loadPlacedItems = useCallback(async () => {
    try {
      setError(null);
      const items = await farmApi.getPlacedItems();
      setPlacedItems(items);
    } catch (err) {
      const message = err instanceof Error ? err.message : '배치된 아이템을 불러오는데 실패했습니다';
      setError(message);
      throw err;
    }
  }, []);

  // Place item on map
  const placeItem = useCallback(async (itemCode: string, tileX: number, tileY: number): Promise<PlacedItem | null> => {
    try {
      setError(null);
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
    } catch (err) {
      const message = err instanceof Error ? err.message : '아이템 배치에 실패했습니다';
      setError(message);
      return null;
    }
  }, []);

  // Move placed item
  const moveItem = useCallback(async (itemId: string, tileX: number, tileY: number) => {
    try {
      setError(null);
      await farmApi.moveItem(itemId, tileX, tileY);
      setPlacedItems(prev => prev.map(item =>
        item.id === itemId ? { ...item, tileX, tileY } : item
      ));
    } catch (err) {
      const message = err instanceof Error ? err.message : '아이템 이동에 실패했습니다';
      setError(message);
      throw err;
    }
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

  // Plant crop on farm plot
  const plantOnPlot = useCallback(async (plotId: string, cropCode: string) => {
    try {
      setError(null);
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
    } catch (err) {
      const message = err instanceof Error ? err.message : '씨앗 심기에 실패했습니다';
      setError(message);
      throw err;
    }
  }, []);

  // Harvest crop from farm plot
  const harvestFromPlot = useCallback(async (plotId: string): Promise<{ gold: number; xp: number } | null> => {
    try {
      setError(null);
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
    } catch (err) {
      const message = err instanceof Error ? err.message : '수확에 실패했습니다';
      setError(message);
      return null;
    }
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

    // Unified Placement Actions
    loadUnifiedShop,
    buyUnifiedItem,
    loadPlacedItems,
    placeItem,
    moveItem,
    removeItem,
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
