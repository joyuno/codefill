'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { farmApi, type UserFarm, type FarmItem, type InventoryItem, type FarmSlot } from '@/lib/api';

interface UseFarmReturn {
  // State
  farm: UserFarm | null;
  items: FarmItem[];
  inventory: InventoryItem[];
  isLoading: boolean;
  error: string | null;

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
  plant: (slot: number, cropCode: string) => Promise<void>;
  harvest: (slot: number) => Promise<{ gold: number; xp: number } | null>;
  buySeed: (cropCode: string, quantity?: number) => Promise<void>;
  expand: (targetSize: number) => Promise<void>;
  refresh: () => Promise<void>;
}

export function useFarm(): UseFarmReturn {
  const [farm, setFarm] = useState<UserFarm | null>(null);
  const [items, setItems] = useState<FarmItem[]>([]);
  const [inventory, setInventory] = useState<InventoryItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const initializedRef = useRef(false);

  // Load initial data
  const loadFarmData = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);

      const [farmData, itemsData, inventoryData] = await Promise.all([
        farmApi.getFarm(),
        farmApi.getItems(),
        farmApi.getInventory(),
      ]);

      setFarm(farmData);
      setItems(itemsData);
      setInventory(inventoryData);
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

      // Reload inventory (initial seeds are granted)
      const inventoryData = await farmApi.getInventory();
      setInventory(inventoryData);
    } catch (err) {
      const message = err instanceof Error ? err.message : '캐릭터 생성에 실패했습니다';
      setError(message);
      throw err;
    }
  }, []);

  // Plant seed
  const plant = useCallback(async (slot: number, cropCode: string) => {
    try {
      setError(null);
      const result = await farmApi.plant(slot, cropCode);

      // Update local state
      setFarm(prev => prev ? {
        ...prev,
        farmSlots: result.farmSlots,
      } : null);
      setInventory(result.inventory);
    } catch (err) {
      const message = err instanceof Error ? err.message : '씨앗 심기에 실패했습니다';
      setError(message);
      throw err;
    }
  }, []);

  // Harvest crop
  const harvest = useCallback(async (slot: number): Promise<{ gold: number; xp: number } | null> => {
    try {
      setError(null);
      const result = await farmApi.harvest(slot);

      // Update local state
      setFarm(prev => prev ? {
        ...prev,
        farmSlots: result.farmSlots,
        gold: result.gold,
      } : null);

      return result.rewards;
    } catch (err) {
      const message = err instanceof Error ? err.message : '수확에 실패했습니다';
      setError(message);
      return null;
    }
  }, []);

  // Buy seeds
  const buySeed = useCallback(async (cropCode: string, quantity: number = 1) => {
    try {
      setError(null);
      const result = await farmApi.buySeed(cropCode, quantity);

      // Update local state
      setFarm(prev => prev ? {
        ...prev,
        gold: result.gold,
      } : null);
      setInventory(result.inventory);
    } catch (err) {
      const message = err instanceof Error ? err.message : '씨앗 구매에 실패했습니다';
      setError(message);
      throw err;
    }
  }, []);

  // Expand farm
  const expand = useCallback(async (targetSize: number) => {
    try {
      setError(null);
      const result = await farmApi.expand(targetSize);

      // Reload farm to get updated slots
      const farmData = await farmApi.getFarm();
      setFarm(farmData);
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

  return {
    farm,
    items,
    inventory,
    isLoading,
    error,
    createCharacter,
    plant,
    harvest,
    buySeed,
    expand,
    refresh,
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
