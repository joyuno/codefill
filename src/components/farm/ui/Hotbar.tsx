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

// 작물 타입 (18종)
export type CropVariety =
  | 'carrot' | 'radish' | 'turnip' | 'onion' | 'tomato' | 'grain'  // Common
  | 'cauliflower' | 'corn' | 'chili_pepper' | 'strawberry' | 'zucchini' | 'cotton'  // Uncommon
  | 'pumpkin' | 'grape' | 'coffee' | 'prickly_pear'  // Rare
  | 'watermelon' | 'pineapple';  // Epic

// 작물 정보 (18종, rarity 기준 정렬)
export const CROP_INFO: Record<CropVariety, { name: string; icon: string; sellPrice: number; seedCost: number; rarity: string }> = {
  // Common (6종) - 판매가 30~50
  carrot: { name: '당근', icon: '/farm/icons/crops/Carrot/icon.png', sellPrice: 38, seedCost: 8, rarity: 'common' },
  radish: { name: '무', icon: '/farm/icons/crops/Radish/icon.png', sellPrice: 30, seedCost: 6, rarity: 'common' },
  turnip: { name: '순무', icon: '/farm/icons/crops/Turnip/icon.png', sellPrice: 34, seedCost: 7, rarity: 'common' },
  onion: { name: '양파', icon: '/farm/icons/crops/Onion/icon.png', sellPrice: 42, seedCost: 10, rarity: 'common' },
  tomato: { name: '토마토', icon: '/farm/icons/crops/Tomato/icon.png', sellPrice: 50, seedCost: 12, rarity: 'common' },
  grain: { name: '밀', icon: '/farm/icons/crops/Grain/icon.png', sellPrice: 32, seedCost: 5, rarity: 'common' },
  // Uncommon (6종) - 판매가 150~200
  cauliflower: { name: '콜리플라워', icon: '/farm/icons/crops/Cauliflower/icon.png', sellPrice: 160, seedCost: 18, rarity: 'uncommon' },
  corn: { name: '옥수수', icon: '/farm/icons/crops/Corn/icon.png', sellPrice: 175, seedCost: 22, rarity: 'uncommon' },
  chili_pepper: { name: '고추', icon: '/farm/icons/crops/Chili_Pepper/icon.png', sellPrice: 185, seedCost: 25, rarity: 'uncommon' },
  strawberry: { name: '딸기', icon: '/farm/icons/crops/Strawberry/icon.png', sellPrice: 200, seedCost: 28, rarity: 'uncommon' },
  zucchini: { name: '주키니', icon: '/farm/icons/crops/Zucchini/icon.png', sellPrice: 150, seedCost: 16, rarity: 'uncommon' },
  cotton: { name: '목화', icon: '/farm/icons/crops/Cotton/icon.png', sellPrice: 155, seedCost: 15, rarity: 'uncommon' },
  // Rare (4종) - 판매가 700~900
  pumpkin: { name: '호박', icon: '/farm/icons/crops/Pumpkin/icon.png', sellPrice: 750, seedCost: 45, rarity: 'rare' },
  grape: { name: '포도', icon: '/farm/icons/crops/Grape/icon.png', sellPrice: 820, seedCost: 52, rarity: 'rare' },
  coffee: { name: '커피', icon: '/farm/icons/crops/Coffee/icon.png', sellPrice: 900, seedCost: 60, rarity: 'rare' },
  prickly_pear: { name: '백년초', icon: '/farm/icons/crops/Prickly_Pear/icon.png', sellPrice: 700, seedCost: 40, rarity: 'rare' },
  // Epic (2종) - 판매가 2300~2500
  watermelon: { name: '수박', icon: '/farm/icons/crops/Watermelon/icon.png', sellPrice: 2300, seedCost: 100, rarity: 'epic' },
  pineapple: { name: '파인애플', icon: '/farm/icons/crops/Pineapple/icon.png', sellPrice: 2500, seedCost: 150, rarity: 'epic' },
};

// DB farm_items INSERT 순서와 동일 (rarity 기준)
export const ALL_CROPS: CropVariety[] = [
  // Common
  'carrot', 'radish', 'turnip', 'onion', 'tomato', 'grain',
  // Uncommon
  'cauliflower', 'corn', 'chili_pepper', 'strawberry', 'zucchini', 'cotton',
  // Rare
  'pumpkin', 'grape', 'coffee', 'prickly_pear',
  // Epic
  'watermelon', 'pineapple',
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
                <img
                  src={info.icon}
                  alt={info.name}
                  className="w-7 h-7 object-contain pixelated"
                  style={{ imageRendering: 'pixelated' }}
                />
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
