'use client';

/**
 * Hotbar - 인벤토리 핫바 (하단 UI)
 * 씨앗 선택 및 골드 표시
 */

import { motion } from 'framer-motion';
import { Coins } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { InventoryItem } from '@/lib/api/farm';
import { getSeedCount } from '@/hooks/useFarm';

// 작물 타입
export type CropVariety = 'carrot' | 'tomato' | 'corn' | 'strawberry' | 'potato' | 'wheat' | 'pumpkin' | 'cabbage' | 'onion' | 'radish';

// 작물 정보 (DB farm_items 순서와 동일하게 정렬: rarity 기준)
export const CROP_INFO: Record<CropVariety, { name: string; emoji: string; sellPrice: number; seedCost: number }> = {
  // Common
  carrot: { name: '당근', emoji: '🥕', sellPrice: 25, seedCost: 10 },
  radish: { name: '무', emoji: '🫚', sellPrice: 22, seedCost: 10 },
  potato: { name: '감자', emoji: '🥔', sellPrice: 30, seedCost: 12 },
  wheat: { name: '밀', emoji: '🌾', sellPrice: 20, seedCost: 8 },
  // Uncommon
  tomato: { name: '토마토', emoji: '🍅', sellPrice: 35, seedCost: 15 },
  onion: { name: '양파', emoji: '🧅', sellPrice: 35, seedCost: 14 },
  cabbage: { name: '양배추', emoji: '🥬', sellPrice: 45, seedCost: 18 },
  // Rare
  strawberry: { name: '딸기', emoji: '🍓', sellPrice: 60, seedCost: 25 },
  corn: { name: '옥수수', emoji: '🌽', sellPrice: 50, seedCost: 20 },
  // Epic
  pumpkin: { name: '호박', emoji: '🎃', sellPrice: 120, seedCost: 50 },
};

// DB farm_items INSERT 순서와 동일 (rarity 기준)
export const ALL_CROPS: CropVariety[] = [
  // Common
  'carrot', 'radish', 'potato', 'wheat',
  // Uncommon
  'tomato', 'onion', 'cabbage',
  // Rare
  'strawberry', 'corn',
  // Epic
  'pumpkin',
];

interface HotbarProps {
  inventory: InventoryItem[];
  selectedSeed: CropVariety;
  onSelectSeed: (seed: CropVariety) => void;
  gold: number;
}

export function Hotbar({ inventory, selectedSeed, onSelectSeed, gold }: HotbarProps) {
  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 pointer-events-none">
      <div
        className="mx-auto max-w-2xl px-4 pb-4 pointer-events-auto"
        style={{ filter: 'drop-shadow(0 -4px 6px rgba(0,0,0,0.3))' }}
      >
        <div
          className="flex items-center justify-center gap-1 p-2 rounded-xl"
          style={{
            background: 'linear-gradient(to bottom, #5D4037 0%, #4E342E 100%)',
            border: '4px solid #3E2723',
            boxShadow: 'inset 0 2px 4px rgba(255,255,255,0.1), inset 0 -2px 4px rgba(0,0,0,0.2)',
          }}
        >
          {ALL_CROPS.map((cropType) => {
            const info = CROP_INFO[cropType];
            const count = getSeedCount(inventory, cropType);
            const isSelected = selectedSeed === cropType;

            return (
              <motion.button
                key={cropType}
                onClick={() => onSelectSeed(cropType)}
                whileHover={{ y: -4 }}
                whileTap={{ scale: 0.95 }}
                className={cn(
                  'relative w-12 h-12 rounded-lg flex flex-col items-center justify-center transition-all',
                  isSelected
                    ? 'bg-amber-400 border-2 border-amber-200'
                    : 'bg-amber-900/50 border-2 border-amber-700 hover:bg-amber-800/50'
                )}
              >
                <span className="text-lg">{info.emoji}</span>
                <span className={cn(
                  'text-[10px] font-bold',
                  count > 0 ? 'text-white' : 'text-red-400'
                )}>
                  {count}
                </span>
                {isSelected && (
                  <motion.div
                    className="absolute -top-1 left-1/2 -translate-x-1/2 w-0 h-0"
                    layoutId="hotbar-indicator"
                    style={{
                      borderLeft: '6px solid transparent',
                      borderRight: '6px solid transparent',
                      borderTop: '6px solid #FCD34D',
                    }}
                  />
                )}
              </motion.button>
            );
          })}

          {/* 구분선 */}
          <div className="w-px h-10 bg-amber-700 mx-2" />

          {/* 골드 표시 */}
          <div className="flex items-center gap-2 px-3 py-2 bg-yellow-400/20 rounded-lg border-2 border-yellow-600">
            <Coins className="w-5 h-5 text-yellow-400" />
            <span className="text-yellow-300 font-bold">{gold.toLocaleString()}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
