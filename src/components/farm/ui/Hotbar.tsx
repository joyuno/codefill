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
// 시간당 골드: Common ~50G/h, Uncommon ~150G/h, Rare ~400G/h, Epic ~800G/h
export const CROP_INFO: Record<CropVariety, { name: string; icon: string; sellPrice: number; rarity: string; growTime: number }> = {
  // Common (6종) - 10~30분 재배, ~50G/hour
  carrot: { name: '당근', icon: '/farm/icons/crops/Carrot/icon.png', sellPrice: 8, rarity: 'common', growTime: 600 },          // 10분
  radish: { name: '무', icon: '/farm/icons/crops/Radish/icon.png', sellPrice: 8, rarity: 'common', growTime: 600 },            // 10분
  turnip: { name: '순무', icon: '/farm/icons/crops/Turnip/icon.png', sellPrice: 12, rarity: 'common', growTime: 900 },         // 15분
  onion: { name: '양파', icon: '/farm/icons/crops/Onion/icon.png', sellPrice: 17, rarity: 'common', growTime: 1200 },          // 20분
  tomato: { name: '토마토', icon: '/farm/icons/crops/Tomato/icon.png', sellPrice: 21, rarity: 'common', growTime: 1500 },      // 25분
  grain: { name: '밀', icon: '/farm/icons/crops/Grain/icon.png', sellPrice: 25, rarity: 'common', growTime: 1800 },            // 30분
  // Uncommon (6종) - 30분~1시간 재배, ~150G/hour
  cauliflower: { name: '콜리플라워', icon: '/farm/icons/crops/Cauliflower/icon.png', sellPrice: 75, rarity: 'uncommon', growTime: 1800 },   // 30분
  corn: { name: '옥수수', icon: '/farm/icons/crops/Corn/icon.png', sellPrice: 100, rarity: 'uncommon', growTime: 2400 },                    // 40분
  chili_pepper: { name: '고추', icon: '/farm/icons/crops/Chili_Pepper/icon.png', sellPrice: 112, rarity: 'uncommon', growTime: 2700 },      // 45분
  strawberry: { name: '딸기', icon: '/farm/icons/crops/Strawberry/icon.png', sellPrice: 125, rarity: 'uncommon', growTime: 3000 },          // 50분
  zucchini: { name: '주키니', icon: '/farm/icons/crops/Zucchini/icon.png', sellPrice: 138, rarity: 'uncommon', growTime: 3300 },            // 55분
  cotton: { name: '목화', icon: '/farm/icons/crops/Cotton/icon.png', sellPrice: 150, rarity: 'uncommon', growTime: 3600 },                  // 1시간
  // Rare (4종) - 1~3시간 재배, ~400G/hour
  pumpkin: { name: '호박', icon: '/farm/icons/crops/Pumpkin/icon.png', sellPrice: 400, rarity: 'rare', growTime: 3600 },              // 1시간
  grape: { name: '포도', icon: '/farm/icons/crops/Grape/icon.png', sellPrice: 600, rarity: 'rare', growTime: 5400 },                  // 1.5시간
  coffee: { name: '커피', icon: '/farm/icons/crops/Coffee/icon.png', sellPrice: 800, rarity: 'rare', growTime: 7200 },                // 2시간
  prickly_pear: { name: '백년초', icon: '/farm/icons/crops/Prickly_Pear/icon.png', sellPrice: 1200, rarity: 'rare', growTime: 10800 }, // 3시간
  // Epic (2종) - 4~5시간 재배, ~800G/hour
  watermelon: { name: '수박', icon: '/farm/icons/crops/Watermelon/icon.png', sellPrice: 3200, rarity: 'epic', growTime: 14400 },      // 4시간
  pineapple: { name: '파인애플', icon: '/farm/icons/crops/Pineapple/icon.png', sellPrice: 4000, rarity: 'epic', growTime: 18000 },    // 5시간
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
