'use client';

import { useState, useEffect, useCallback, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Image from 'next/image';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import {
  useFarm,
  getSeedCount,
  getCropInfo,
  calculateCropStage,
  getRemainingTime
} from '@/hooks/useFarm';
import type { FarmSlot, FarmItem, InventoryItem } from '@/lib/api/farm';
import {
  Coins,
  ShoppingBag,
  X,
  Loader2,
  AlertCircle,
  Sprout,
  Home,
  Settings,
  Volume2,
  VolumeX,
  ChevronLeft,
} from 'lucide-react';

// ============================================
// 타입 정의
// ============================================

type CropVariety = 'carrot' | 'tomato' | 'corn' | 'strawberry' | 'potato' | 'wheat' | 'pumpkin' | 'cabbage' | 'onion' | 'radish';
type CropStage = 0 | 1 | 2 | 3 | 4;

interface CropDisplay {
  id: string;
  slot: number;
  stage: CropStage;
  type: CropVariety;
  plantedAt: string | null;
  remainingTime: number;
  growTimeSeconds: number;
}

// ============================================
// 에셋 경로 상수
// ============================================

const ASSETS = {
  crops: '/farm/crops',
  houses: '/farm/houses',
  characters: '/farm/characters',
  terrains: '/farm/terrains',
  tools: '/farm/tools',
};

// 작물 이미지 매핑
const CROP_IMAGES: Record<CropVariety, Record<CropStage, string>> = {
  carrot: {
    0: '', 1: 'Crop_Carrot_Sprout_32x32.png', 2: 'Crop_Carrot_Stage_1_32x32.png',
    3: 'Crop_Carrot_Stage_1_32x32.png', 4: 'Crop_Carrot_Ripe_1_32x32.png',
  },
  tomato: {
    0: '', 1: 'Crop_Tomato_Sprout_32x32.png', 2: 'Crop_Tomato_Stage_1_32x32.png',
    3: 'Crop_Tomato_Fruitless_32x32.png', 4: 'Crop_Tomato_Ripe_32x32.png',
  },
  corn: {
    0: '', 1: 'Crop_Corn_Sprout_32x32.png', 2: 'Crop_Corn_Stage_1_32x32.png',
    3: 'Crop_Corn_Fruitless_32x32.png', 4: 'Crop_Corn_Ripe_32x32.png',
  },
  strawberry: {
    0: '', 1: 'Crop_Strawberry_Sprout_32x32.png', 2: 'Crop_Strawberry_Stage_1_32x32.png',
    3: 'Crop_Strawberry_Fruitless_32x32.png', 4: 'Crop_Strawberry_Ripe_32x32.png',
  },
  potato: {
    0: '', 1: 'Crop_Radish_Sprout_32x32.png', 2: 'Crop_Radish_Stage_1_32x32.png',
    3: 'Crop_Radish_Stage_2_32x32.png', 4: 'Crop_Radish_Ripe_1_32x32.png',
  },
  wheat: {
    0: '', 1: 'Crop_Grain_Sprout_32x32.png', 2: 'Crop_Grain_Stage_1_32x32.png',
    3: 'Crop_Grain_Stage_2_32x32.png', 4: 'Crop_Grain_Ripe_32x32.png',
  },
  pumpkin: {
    0: '', 1: 'Crop_Pumpkin_Sprout_32x32.png', 2: 'Crop_Pumpkin_Stage_1_32x32.png',
    3: 'Crop_Pumpkin_Fruitless_32x32.png', 4: 'Crop_Pumpkin_Ripe_32x32.png',
  },
  cabbage: {
    0: '', 1: 'Crop_Cabbage_Sprout_32x32.png', 2: 'Crop_Cabbage_Stage_1_32x32.png',
    3: 'Crop_Cabbage_Stage_1_32x32.png', 4: 'Crop_Cabbage_Ripe_32x32.png',
  },
  onion: {
    0: '', 1: 'Crop_Onion_Sprout_32x32.png', 2: 'Crop_Onion_Stage_1_32x32.png',
    3: 'Crop_Onion_Stage_1_32x32.png', 4: 'Crop_Onion_Ripe_32x32.png',
  },
  radish: {
    0: '', 1: 'Crop_Radish_Sprout_32x32.png', 2: 'Crop_Radish_Stage_1_32x32.png',
    3: 'Crop_Radish_Stage_2_32x32.png', 4: 'Crop_Radish_Ripe_1_32x32.png',
  },
};

const CROP_INFO: Record<CropVariety, { name: string; emoji: string; sellPrice: number; seedCost: number }> = {
  carrot: { name: '당근', emoji: '🥕', sellPrice: 25, seedCost: 10 },
  tomato: { name: '토마토', emoji: '🍅', sellPrice: 35, seedCost: 15 },
  corn: { name: '옥수수', emoji: '🌽', sellPrice: 50, seedCost: 20 },
  strawberry: { name: '딸기', emoji: '🍓', sellPrice: 60, seedCost: 25 },
  potato: { name: '감자', emoji: '🥔', sellPrice: 30, seedCost: 12 },
  wheat: { name: '밀', emoji: '🌾', sellPrice: 20, seedCost: 8 },
  pumpkin: { name: '호박', emoji: '🎃', sellPrice: 120, seedCost: 50 },
  cabbage: { name: '양배추', emoji: '🥬', sellPrice: 45, seedCost: 18 },
  onion: { name: '양파', emoji: '🧅', sellPrice: 35, seedCost: 14 },
  radish: { name: '무', emoji: '🥕', sellPrice: 22, seedCost: 10 },
};

const ALL_CROPS: CropVariety[] = ['carrot', 'tomato', 'corn', 'strawberry', 'potato', 'wheat', 'pumpkin', 'cabbage', 'onion', 'radish'];

// FarmSlot을 CropDisplay로 변환
const transformSlotToCrop = (slot: FarmSlot, items: FarmItem[]): CropDisplay => {
  const cropInfo = items.find(item => item.code === slot.cropCode);
  const growTimeSeconds = cropInfo?.growTimeSeconds || 120;
  const remaining = slot.plantedAt ? getRemainingTime(slot.plantedAt, growTimeSeconds) : 0;
  const calculatedStage = slot.cropCode ? calculateCropStage(slot.plantedAt, growTimeSeconds) : 0;

  return {
    id: `crop-${slot.slot}`,
    slot: slot.slot,
    stage: calculatedStage,
    type: (slot.cropCode || 'carrot') as CropVariety,
    plantedAt: slot.plantedAt,
    remainingTime: remaining,
    growTimeSeconds,
  };
};

// 시간 포맷
const formatTime = (seconds: number): string => {
  if (seconds <= 0) return '완료!';
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}:${secs.toString().padStart(2, '0')}`;
};

// ============================================
// 타일 컴포넌트
// ============================================

interface FarmTileProps {
  crop: CropDisplay;
  isSelected: boolean;
  onClick: () => void;
  tileSize: number;
}

function FarmTile({ crop, isSelected, onClick, tileSize }: FarmTileProps) {
  const imagePath = crop.stage > 0
    ? `${ASSETS.crops}/${CROP_IMAGES[crop.type][crop.stage]}`
    : null;

  return (
    <motion.button
      onClick={onClick}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      className={cn(
        'relative transition-all duration-150',
        isSelected && 'ring-2 ring-yellow-400 ring-offset-2 ring-offset-amber-900',
        crop.stage === 4 && 'animate-pulse'
      )}
      style={{ width: tileSize, height: tileSize }}
    >
      {/* 흙 배경 */}
      <div
        className="absolute inset-0 rounded-sm"
        style={{
          background: crop.stage === 0
            ? 'linear-gradient(135deg, #8B5A2B 0%, #6B4423 50%, #5D3A1F 100%)'
            : 'linear-gradient(135deg, #5D3A1F 0%, #4A2E19 100%)',
          boxShadow: 'inset 0 2px 4px rgba(0,0,0,0.3)',
        }}
      />

      {/* 작물 이미지 */}
      {imagePath && (
        <div className="absolute inset-0 flex items-center justify-center p-1">
          <Image
            src={imagePath}
            alt={crop.type}
            width={tileSize - 8}
            height={tileSize - 8}
            className="object-contain drop-shadow-md"
            style={{ imageRendering: 'pixelated' }}
            unoptimized
          />
        </div>
      )}

      {/* 빈 땅 표시 */}
      {crop.stage === 0 && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-3 h-3 rounded-full bg-amber-600/50" />
        </div>
      )}

      {/* 수확 가능 표시 */}
      {crop.stage === 4 && (
        <motion.div
          className="absolute -top-1 -right-1 w-4 h-4 bg-yellow-400 rounded-full flex items-center justify-center shadow-lg"
          animate={{ scale: [1, 1.2, 1] }}
          transition={{ duration: 0.8, repeat: Infinity }}
        >
          <span className="text-[8px]">!</span>
        </motion.div>
      )}

      {/* 성장 타이머 */}
      {crop.stage > 0 && crop.stage < 4 && crop.remainingTime > 0 && (
        <div className="absolute bottom-0 left-0 right-0 bg-black/70 text-center py-0.5 rounded-b-sm">
          <span className="text-[8px] text-amber-300 font-mono">
            {formatTime(crop.remainingTime)}
          </span>
        </div>
      )}
    </motion.button>
  );
}

// ============================================
// 인벤토리 핫바
// ============================================

interface HotbarProps {
  inventory: InventoryItem[];
  selectedSeed: CropVariety;
  onSelectSeed: (seed: CropVariety) => void;
  gold: number;
}

function Hotbar({ inventory, selectedSeed, onSelectSeed, gold }: HotbarProps) {
  return (
    <div className="fixed bottom-0 left-0 right-0 z-50">
      {/* 메인 핫바 */}
      <div
        className="mx-auto max-w-2xl px-4 pb-4"
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
          {ALL_CROPS.slice(0, 8).map((cropType) => {
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

// ============================================
// 상점 모달
// ============================================

interface ShopModalProps {
  isOpen: boolean;
  onClose: () => void;
  items: FarmItem[];
  gold: number;
  onBuy: (cropCode: CropVariety, quantity: number) => void;
}

function ShopModal({ isOpen, onClose, items, gold, onBuy }: ShopModalProps) {
  if (!isOpen) return null;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.9, y: 20 }}
        animate={{ scale: 1, y: 0 }}
        exit={{ scale: 0.9, y: 20 }}
        onClick={e => e.stopPropagation()}
        className="w-full max-w-lg max-h-[80vh] overflow-hidden rounded-2xl"
        style={{
          background: 'linear-gradient(to bottom, #8D6E63 0%, #6D4C41 100%)',
          border: '6px solid #4E342E',
          boxShadow: '0 10px 40px rgba(0,0,0,0.5)',
        }}
      >
        {/* 헤더 */}
        <div
          className="p-4 flex items-center justify-between"
          style={{
            background: 'linear-gradient(to bottom, #5D4037 0%, #4E342E 100%)',
            borderBottom: '4px solid #3E2723',
          }}
        >
          <h2 className="text-xl font-bold text-amber-200 flex items-center gap-2">
            <ShoppingBag className="w-6 h-6" />
            씨앗 상점
          </h2>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 text-yellow-300">
              <Coins className="w-5 h-5" />
              <span className="font-bold">{gold.toLocaleString()}G</span>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={onClose}
              className="text-amber-200 hover:text-white hover:bg-amber-800"
            >
              <X className="w-5 h-5" />
            </Button>
          </div>
        </div>

        {/* 상품 목록 */}
        <div className="p-4 overflow-y-auto max-h-[60vh] space-y-3">
          {items.filter(item => item.type === 'crop').map(item => {
            const info = CROP_INFO[item.code as CropVariety];
            if (!info) return null;

            return (
              <div
                key={item.code}
                className="flex items-center justify-between p-3 rounded-lg"
                style={{
                  background: 'rgba(0,0,0,0.2)',
                  border: '2px solid rgba(255,255,255,0.1)',
                }}
              >
                <div className="flex items-center gap-3">
                  <span className="text-2xl">{info.emoji}</span>
                  <div>
                    <p className="font-bold text-amber-100">{info.name} 씨앗</p>
                    <p className="text-sm text-amber-300">{item.seedCost}G / 개</p>
                  </div>
                </div>
                <div className="flex gap-2">
                  <Button
                    size="sm"
                    onClick={() => onBuy(item.code as CropVariety, 1)}
                    disabled={gold < item.seedCost}
                    className="bg-green-600 hover:bg-green-500 text-white border-2 border-green-400"
                  >
                    1개
                  </Button>
                  <Button
                    size="sm"
                    onClick={() => onBuy(item.code as CropVariety, 5)}
                    disabled={gold < item.seedCost * 5}
                    className="bg-green-600 hover:bg-green-500 text-white border-2 border-green-400"
                  >
                    5개
                  </Button>
                </div>
              </div>
            );
          })}
        </div>
      </motion.div>
    </motion.div>
  );
}

// ============================================
// 메인 Farm 페이지
// ============================================

export default function FarmPage() {
  const router = useRouter();

  // useFarm 훅
  const {
    farm,
    items,
    inventory,
    isLoading,
    error,
    plant,
    harvest,
    buySeed,
    expand,
    refresh,
  } = useFarm();

  // UI 상태
  const [selectedSeed, setSelectedSeed] = useState<CropVariety>('carrot');
  const [cropDisplays, setCropDisplays] = useState<CropDisplay[]>([]);
  const [isPlanting, setIsPlanting] = useState(false);
  const [isHarvesting, setIsHarvesting] = useState(false);
  const [showShop, setShowShop] = useState(false);
  const [harvestEffect, setHarvestEffect] = useState<{ id: string; gold: number } | null>(null);
  const [soundEnabled, setSoundEnabled] = useState(true);

  // farm 데이터가 변경되면 cropDisplays 업데이트
  useEffect(() => {
    if (farm && items.length > 0) {
      const displays = farm.farmSlots.map(slot => transformSlotToCrop(slot, items));
      setCropDisplays(displays);
    }
  }, [farm, items]);

  // 1초마다 작물 상태 업데이트
  useEffect(() => {
    if (!farm || items.length === 0) return;

    const timerInterval = setInterval(() => {
      setCropDisplays(prev =>
        prev.map(crop => {
          if (crop.plantedAt && crop.stage > 0 && crop.stage < 4) {
            const newRemaining = getRemainingTime(crop.plantedAt, crop.growTimeSeconds);
            const newStage = calculateCropStage(crop.plantedAt, crop.growTimeSeconds);
            return { ...crop, remainingTime: newRemaining, stage: newStage };
          }
          return crop;
        })
      );
    }, 1000);

    return () => clearInterval(timerInterval);
  }, [farm, items]);

  // 캐릭터 미생성 시 리다이렉트
  useEffect(() => {
    if (!isLoading && farm && !farm.characterCreated) {
      router.push('/');
    }
  }, [isLoading, farm, router]);

  // 그리드 컬럼 수 계산
  const getGridCols = useCallback(() => {
    const farmSize = farm?.farmSize || 4;
    if (farmSize <= 4) return 2;
    if (farmSize <= 9) return 3;
    if (farmSize <= 16) return 4;
    if (farmSize <= 25) return 5;
    return 6;
  }, [farm?.farmSize]);

  // 타일 클릭 핸들러
  const handleTileClick = useCallback(async (crop: CropDisplay) => {
    if (crop.stage === 4) {
      // 수확
      if (isHarvesting) return;
      setIsHarvesting(true);
      try {
        const result = await harvest(crop.slot);
        if (result) {
          setHarvestEffect({ id: crop.id, gold: result.gold });
          setTimeout(() => setHarvestEffect(null), 1000);
        }
      } catch (err) {
        console.error('수확 실패:', err);
      } finally {
        setIsHarvesting(false);
      }
    } else if (crop.stage === 0) {
      // 심기
      if (isPlanting) return;
      const seedCount = getSeedCount(inventory, selectedSeed);
      if (seedCount <= 0) return;

      setIsPlanting(true);
      try {
        await plant(crop.slot, selectedSeed);
      } catch (err) {
        console.error('심기 실패:', err);
      } finally {
        setIsPlanting(false);
      }
    }
  }, [harvest, plant, inventory, selectedSeed, isPlanting, isHarvesting]);

  // 씨앗 구매
  const handleBuySeed = useCallback(async (cropCode: CropVariety, quantity: number) => {
    try {
      await buySeed(cropCode, quantity);
    } catch (err) {
      console.error('구매 실패:', err);
    }
  }, [buySeed]);

  // 타일 크기 (클라이언트 사이드에서만 계산)
  const [tileSize, setTileSize] = useState(56);

  useEffect(() => {
    const calculateTileSize = () => {
      const cols = farm?.farmSize ? (farm.farmSize <= 4 ? 2 : farm.farmSize <= 9 ? 3 : farm.farmSize <= 16 ? 4 : farm.farmSize <= 25 ? 5 : 6) : 2;
      const size = Math.min(64, Math.floor((window.innerWidth - 200) / cols / 1.5));
      setTileSize(Math.max(48, size));
    };

    calculateTileSize();
    window.addEventListener('resize', calculateTileSize);
    return () => window.removeEventListener('resize', calculateTileSize);
  }, [farm?.farmSize]);

  // 계산된 값들
  const gold = farm?.gold || 0;
  const farmLevel = farm?.farmLevel || 1;
  const farmName = farm?.characterData?.farmName || '나의 농장';
  const gridCols = getGridCols();

  // 로딩 상태
  if (isLoading) {
    return (
      <div
        className="min-h-screen flex flex-col items-center justify-center gap-4"
        style={{ background: 'linear-gradient(to bottom, #87CEEB 0%, #7CBA5F 40%, #5A9F4A 100%)' }}
      >
        <motion.div animate={{ rotate: 360 }} transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}>
          <Loader2 className="w-12 h-12 text-white" />
        </motion.div>
        <p className="text-white font-bold text-lg">농장 불러오는 중...</p>
      </div>
    );
  }

  // 에러 상태
  if (error) {
    return (
      <div
        className="min-h-screen flex flex-col items-center justify-center gap-4 p-4"
        style={{ background: 'linear-gradient(to bottom, #87CEEB 0%, #7CBA5F 40%, #5A9F4A 100%)' }}
      >
        <AlertCircle className="w-12 h-12 text-red-400" />
        <p className="text-white font-bold text-center">{error}</p>
        <Button onClick={() => router.push('/')} variant="outline" className="bg-white">
          홈으로 돌아가기
        </Button>
      </div>
    );
  }

  // 캐릭터 미생성
  if (!farm?.characterCreated) {
    return (
      <div
        className="min-h-screen flex flex-col items-center justify-center gap-4"
        style={{ background: 'linear-gradient(to bottom, #87CEEB 0%, #7CBA5F 40%, #5A9F4A 100%)' }}
      >
        <Sprout className="w-12 h-12 text-white animate-bounce" />
        <p className="text-white font-bold">리다이렉트 중...</p>
      </div>
    );
  }

  return (
    <div
      className="min-h-screen relative overflow-hidden"
      style={{
        background: `
          linear-gradient(to bottom,
            #87CEEB 0%,
            #B0E2FF 15%,
            #7CBA5F 20%,
            #5A9F4A 100%
          )
        `,
      }}
    >
      {/* 배경 장식 - 구름 */}
      <motion.div
        className="absolute top-8 left-[10%] text-4xl opacity-80"
        animate={{ x: [0, 30, 0] }}
        transition={{ duration: 20, repeat: Infinity }}
      >
        ☁️
      </motion.div>
      <motion.div
        className="absolute top-16 right-[20%] text-3xl opacity-60"
        animate={{ x: [0, -20, 0] }}
        transition={{ duration: 25, repeat: Infinity }}
      >
        ☁️
      </motion.div>

      {/* 태양 */}
      <motion.div
        className="absolute top-4 right-8 text-5xl"
        animate={{ rotate: [0, 5, -5, 0] }}
        transition={{ duration: 8, repeat: Infinity }}
      >
        ☀️
      </motion.div>

      {/* 상단 UI */}
      <div className="relative z-20 p-4">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          {/* 뒤로가기 */}
          <Link href="/">
            <Button
              variant="outline"
              size="sm"
              className="bg-amber-100 hover:bg-amber-200 border-4 border-amber-700 shadow-[3px_3px_0_0_#78350f] text-amber-900 font-bold"
            >
              <ChevronLeft className="w-4 h-4 mr-1" />
              돌아가기
            </Button>
          </Link>

          {/* 농장 이름 & 레벨 */}
          <div
            className="px-6 py-2 rounded-xl"
            style={{
              background: 'linear-gradient(to bottom, #5D4037 0%, #4E342E 100%)',
              border: '4px solid #3E2723',
              boxShadow: '0 4px 8px rgba(0,0,0,0.3)',
            }}
          >
            <h1 className="text-amber-200 font-bold text-lg">{farmName}</h1>
            <p className="text-amber-400 text-sm text-center">Lv.{farmLevel}</p>
          </div>

          {/* 오른쪽 버튼들 */}
          <div className="flex items-center gap-2">
            <Button
              onClick={() => setShowShop(true)}
              className="bg-green-600 hover:bg-green-500 border-4 border-green-800 shadow-[3px_3px_0_0_#166534] text-white font-bold"
            >
              <ShoppingBag className="w-4 h-4 mr-1" />
              상점
            </Button>
            <Button
              variant="outline"
              size="icon"
              onClick={() => setSoundEnabled(!soundEnabled)}
              className="bg-amber-100 border-4 border-amber-700 shadow-[2px_2px_0_0_#78350f]"
            >
              {soundEnabled ? <Volume2 className="w-4 h-4" /> : <VolumeX className="w-4 h-4" />}
            </Button>
          </div>
        </div>
      </div>

      {/* 메인 농장 영역 */}
      <div className="relative z-10 flex items-center justify-center min-h-[60vh] p-4">
        <div className="relative">
          {/* 집 */}
          <motion.div
            className="absolute -right-32 -top-20"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <Image
              src={`${ASSETS.houses}/Farmer_House_1_32x32.png`}
              alt="Farmhouse"
              width={120}
              height={140}
              style={{ imageRendering: 'pixelated' }}
              unoptimized
            />
          </motion.div>

          {/* 밭 영역 */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="relative p-4 rounded-2xl"
            style={{
              background: 'linear-gradient(135deg, #8B5A2B 0%, #6B4423 50%, #5D3A1F 100%)',
              border: '6px solid #4E342E',
              boxShadow: '0 8px 32px rgba(0,0,0,0.4), inset 0 2px 4px rgba(255,255,255,0.1)',
            }}
          >
            {/* 작물 그리드 */}
            <div
              className="grid gap-2"
              style={{ gridTemplateColumns: `repeat(${gridCols}, 1fr)` }}
            >
              {cropDisplays.map(crop => (
                <FarmTile
                  key={crop.id}
                  crop={crop}
                  isSelected={false}
                  onClick={() => handleTileClick(crop)}
                  tileSize={tileSize}
                />
              ))}
            </div>

            {/* 선택된 씨앗 표시 */}
            <div className="mt-4 text-center">
              <p className="text-amber-200 text-sm">
                선택: {CROP_INFO[selectedSeed].emoji} {CROP_INFO[selectedSeed].name}
                <span className="text-amber-400 ml-2">
                  ({getSeedCount(inventory, selectedSeed)}개)
                </span>
              </p>
            </div>
          </motion.div>

          {/* 허수아비 */}
          <motion.div
            className="absolute -left-20 top-1/2 -translate-y-1/2"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.5 }}
          >
            <Image
              src={`${ASSETS.houses}/Scarecrow_32x32.png`}
              alt="Scarecrow"
              width={48}
              height={64}
              style={{ imageRendering: 'pixelated' }}
              unoptimized
            />
          </motion.div>

          {/* 우물 */}
          <motion.div
            className="absolute -right-16 bottom-0"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.6 }}
          >
            <Image
              src={`${ASSETS.houses}/Well_Usable_Bucket_Full_32x32.png`}
              alt="Well"
              width={48}
              height={64}
              style={{ imageRendering: 'pixelated' }}
              unoptimized
            />
          </motion.div>
        </div>
      </div>

      {/* 수확 이펙트 */}
      <AnimatePresence>
        {harvestEffect && (
          <motion.div
            initial={{ opacity: 1, y: 0 }}
            animate={{ opacity: 0, y: -50 }}
            exit={{ opacity: 0 }}
            className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-50 pointer-events-none"
          >
            <div className="text-2xl font-bold text-yellow-400 drop-shadow-lg">
              +{harvestEffect.gold}G!
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* 인벤토리 핫바 */}
      <Hotbar
        inventory={inventory}
        selectedSeed={selectedSeed}
        onSelectSeed={setSelectedSeed}
        gold={gold}
      />

      {/* 상점 모달 */}
      <AnimatePresence>
        {showShop && (
          <ShopModal
            isOpen={showShop}
            onClose={() => setShowShop(false)}
            items={items}
            gold={gold}
            onBuy={handleBuySeed}
          />
        )}
      </AnimatePresence>
    </div>
  );
}
