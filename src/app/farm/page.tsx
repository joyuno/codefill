'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Header } from '@/components/layout/Header';
import { TopNav } from '@/components/layout/TopNav';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  FarmerSprite,
  CropSprite,
  HouseSprite,
  ToolSprite,
  type FarmerAction,
  type Direction,
  type CropVariety,
  type CropStage,
} from '@/components/farm/GameSprites';
import { CROP_INFO } from '@/components/farm/PixelSprites';
import {
  Leaf,
  Sprout,
  Sparkles,
  ShoppingBag,
  ArrowLeft,
  TrendingUp,
  X,
  Plus,
  Coins,
  Expand,
  Clock,
  Home,
} from 'lucide-react';
import { cn } from '@/lib/utils';

// ============================================
// 타입 정의
// ============================================

interface CharacterData {
  name: string;
  appearance: {
    hair: string;
    face: string;
    clothes: string;
    color: string;
  };
  farmName: string;
}

interface Crop {
  id: string;
  stage: CropStage;
  type: CropVariety;
  harvestXp?: number;
  plantedAt?: number;
  growthTime?: number;
}

interface SeedInventory {
  [key: string]: number;
}

interface FarmState {
  character: CharacterData | null;
  crops: Crop[];
  houseLevel: 1 | 2 | 3 | 4;
  totalXp: number;
  level: number;
  gold: number;
  seeds: SeedInventory;
  farmSize: number;
  harvested: { [key: string]: number };
}

interface FarmerState {
  x: number;
  y: number;
  action: FarmerAction;
  direction: Direction;
  isInHouse: boolean;
  targetCropIndex: number | null;
}

type ModalType = 'none' | 'seeds' | 'market' | 'shop' | 'expand';

// ============================================
// 상수 정의
// ============================================

const HOUSE_LEVELS = [
  { level: 1, name: '초가집', xpRequired: 0, gridSize: 2 },
  { level: 2, name: '나무집', xpRequired: 500, gridSize: 3 },
  { level: 3, name: '벽돌집', xpRequired: 1500, gridSize: 4 },
  { level: 4, name: '황금 저택', xpRequired: 5000, gridSize: 5 },
];

const ALL_CROP_TYPES: CropVariety[] = [
  'carrot', 'tomato', 'corn', 'strawberry', 'potato', 'wheat', 'pumpkin', 'cabbage', 'onion', 'radish'
];

const GROWTH_TIMES: Record<CropVariety, number> = {
  carrot: 30,
  tomato: 45,
  corn: 60,
  strawberry: 50,
  potato: 35,
  wheat: 40,
  pumpkin: 120,
};

const EXPANSION_COSTS = [
  { size: 9, cost: 0, name: '기본 농장' },
  { size: 12, cost: 500, name: '작은 확장' },
  { size: 16, cost: 1500, name: '중간 확장' },
  { size: 20, cost: 3000, name: '큰 확장' },
  { size: 25, cost: 6000, name: '최대 확장' },
];

// ============================================
// 유틸리티 함수
// ============================================

const getMarketMultiplier = () => {
  const multipliers = [0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.5];
  return multipliers[Math.floor(Math.random() * multipliers.length)];
};

const createInitialCrops = (size: number): Crop[] => {
  return Array(size)
    .fill(null)
    .map((_, i) => {
      const type = ALL_CROP_TYPES[i % ALL_CROP_TYPES.length];
      const stage = (i < 3 ? 4 : i < 5 ? 3 : i < 7 ? 2 : 0) as CropStage;
      return {
      id: `crop-${i}`,
        stage,
        type,
        harvestXp: stage === 4 ? 50 : undefined,
        plantedAt: stage > 0 ? Date.now() - (stage * 10000) : undefined,
        growthTime: stage > 0 && stage < 4 ? Math.floor(Math.random() * 30) + 10 : undefined,
      };
    });
};

const createInitialSeeds = (): SeedInventory => {
  const seeds: SeedInventory = {};
  ALL_CROP_TYPES.forEach(type => {
    seeds[type] = Math.floor(Math.random() * 5) + 2;
  });
  return seeds;
};

const formatTime = (seconds: number): string => {
  if (seconds <= 0) return '완료!';
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  if (mins > 0) return `${mins}분 ${secs}초`;
  return `${secs}초`;
};

const HAIR_COLORS: Record<string, string> = {
  brown: '#8B4513',
  black: '#2d2d2d',
  blonde: '#f4d03f',
  red: '#c0392b',
  blue: '#3498db',
  pink: '#e91e8a',
};

// ============================================
// 작물 타일 컴포넌트
// ============================================

interface CropTileProps {
  crop: Crop;
  onClick: () => void;
  isHarvesting: boolean;
  marketPrice: number;
}

function CropTile({ crop, onClick, isHarvesting, marketPrice }: CropTileProps) {
  const cropInfo = CROP_INFO[crop.type as keyof typeof CROP_INFO] || { 
    name: crop.type, 
    emoji: '🌱', 
    sellPrice: 10, 
    buyPrice: 5,
    growTime: 30
  };
  
  return (
    <motion.button
      type="button"
      onClick={onClick}
      whileHover={{ scale: 1.03 }}
      whileTap={{ scale: 0.97 }}
      className={cn(
        'relative w-full aspect-square rounded-lg overflow-hidden',
        'border-4 transition-all',
        crop.stage === 4
          ? 'border-yellow-500 cursor-pointer shadow-[3px_3px_0_0_#854d0e] bg-gradient-to-b from-yellow-100 to-yellow-200'
          : crop.stage === 0
            ? 'border-amber-700 border-dashed hover:border-amber-500 cursor-pointer bg-amber-700'
            : 'border-amber-700 bg-amber-600'
      )}
    >
      {/* 작물 스프라이트 */}
      <div className="absolute inset-0 flex items-center justify-center">
        <CropSprite 
          type={crop.type} 
          stage={crop.stage} 
          size={48}
          withTimer={crop.stage > 0 && crop.stage < 4}
          remainingSeconds={crop.growthTime}
        />
      </div>
      
      {/* 빈 땅 심기 표시 */}
      {crop.stage === 0 && (
        <div className="absolute bottom-1 left-0 right-0 text-center">
          <span className="text-[10px] text-amber-200 font-bold">심기</span>
        </div>
      )}
      
      {/* 수확 가격 표시 */}
      {crop.stage === 4 && (
        <div className="absolute top-0 left-0 right-0 bg-yellow-500/90 px-1 py-0.5">
          <span className="text-[10px] text-yellow-900 font-bold flex items-center justify-center gap-0.5">
            <Coins className="h-2.5 w-2.5" />
            +{marketPrice}G
          </span>
        </div>
      )}
      
      {/* 수확 애니메이션 */}
      <AnimatePresence>
        {isHarvesting && (
          <motion.div
            initial={{ opacity: 1, scale: 1 }}
            animate={{ opacity: 0, y: -30, scale: 1.5 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 flex items-center justify-center pointer-events-none z-20"
          >
            <span className="text-xl font-bold text-yellow-400 drop-shadow-lg">
              +{marketPrice}G!
            </span>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.button>
  );
}

// ============================================
// 메인 농장 페이지
// ============================================

export default function FarmPage() {
  const router = useRouter();
  
  const [farmState, setFarmState] = useState<FarmState>({
    character: null,
    crops: createInitialCrops(9),
    houseLevel: 2,
    totalXp: 450,
    level: 15,
    gold: 1250,
    seeds: createInitialSeeds(),
    farmSize: 9,
    harvested: {},
  });
  
  const [farmerState, setFarmerState] = useState<FarmerState>({
    x: 30,
    y: 50,
    action: 'idle',
    direction: 'down',
    isInHouse: false,
    targetCropIndex: null,
  });
  
  const [harvestAnimation, setHarvestAnimation] = useState<string | null>(null);
  const [activeModal, setActiveModal] = useState<ModalType>('none');
  const [selectedSeedType, setSelectedSeedType] = useState<CropVariety>('carrot');
  const [marketPrices, setMarketPrices] = useState<Record<string, number>>({});

  // 농부 자동 행동 로직
  useEffect(() => {
    const actionInterval = setInterval(() => {
      const random = Math.random();
      
      setFarmerState(prev => {
        if (prev.isInHouse) {
          // 집에서 나오기
          if (Math.random() < 0.3) {
            return {
              ...prev,
              isInHouse: false,
              action: 'walk',
              x: 70,
              y: 30,
            };
          }
          return prev;
        }
        
        if (random < 0.1) {
          // 10% 확률로 집에 들어감
          return {
            ...prev,
            isInHouse: true,
            action: 'sleep',
            x: 85,
            y: 25,
          };
        } else if (random < 0.35) {
          // 25% 확률로 농사 (낫 휘두르기)
          const targetIndex = Math.floor(Math.random() * farmState.crops.length);
          const cropX = 15 + (targetIndex % 3) * 20;
          const cropY = 45 + Math.floor(targetIndex / 3) * 15;
          return {
            ...prev,
            action: 'farm',
            direction: 'down',
            x: cropX,
            y: cropY,
            targetCropIndex: targetIndex,
          };
        } else if (random < 0.5) {
          // 15% 확률로 물주기
          const targetIndex = Math.floor(Math.random() * farmState.crops.length);
          const cropX = 15 + (targetIndex % 3) * 20;
          const cropY = 45 + Math.floor(targetIndex / 3) * 15;
          return {
            ...prev,
            action: 'water',
            direction: 'down',
            x: cropX,
            y: cropY,
          };
        } else {
          // 50% 확률로 걷기
          const newX = Math.max(10, Math.min(85, prev.x + (Math.random() - 0.5) * 25));
          const newY = Math.max(25, Math.min(75, prev.y + (Math.random() - 0.5) * 20));
          
          let newDirection: Direction = prev.direction;
          if (newX > prev.x + 5) newDirection = 'right';
          else if (newX < prev.x - 5) newDirection = 'left';
          else if (newY > prev.y + 5) newDirection = 'down';
          else if (newY < prev.y - 5) newDirection = 'up';
          
          return {
            ...prev,
            action: 'walk',
            direction: newDirection,
            x: newX,
            y: newY,
            targetCropIndex: null,
          };
        }
      });
      
      // 2초 후 idle로
      setTimeout(() => {
        setFarmerState(prev => ({
          ...prev,
          action: prev.isInHouse ? 'sleep' : 'idle',
        }));
      }, 1500);
    }, 3000);
    
    return () => clearInterval(actionInterval);
  }, [farmState.crops.length]);
  
  // 작물 타이머
  useEffect(() => {
    const timerInterval = setInterval(() => {
      setFarmState(prev => ({
        ...prev,
        crops: prev.crops.map(crop => {
          if (crop.stage > 0 && crop.stage < 4 && crop.growthTime !== undefined) {
            const newTime = crop.growthTime - 1;
            if (newTime <= 0) {
              const newStage = Math.min(crop.stage + 1, 4) as CropStage;
              return {
                ...crop,
                stage: newStage,
                growthTime: newStage < 4 ? GROWTH_TIMES[crop.type] / 4 : undefined,
              };
            }
            return { ...crop, growthTime: newTime };
          }
          return crop;
        }),
      }));
    }, 1000);
    
    return () => clearInterval(timerInterval);
  }, []);
  
  // 시장 가격 초기화
  useEffect(() => {
    const prices: Record<string, number> = {};
    ALL_CROP_TYPES.forEach(type => {
      const info = CROP_INFO[type as keyof typeof CROP_INFO];
      if (info) {
        prices[type] = Math.round(info.sellPrice * getMarketMultiplier());
      }
    });
    setMarketPrices(prices);
  }, []);

  // 캐릭터 확인
  useEffect(() => {
    const savedCharacter = localStorage.getItem('codefill_character');
    if (savedCharacter) {
      try {
        const character = JSON.parse(savedCharacter);
        setFarmState(prev => ({ ...prev, character }));
      } catch {
        router.push('/');
      }
    } else {
      router.push('/');
    }
  }, [router]);

  // 수확 처리
  const handleHarvest = (cropId: string) => {
    const crop = farmState.crops.find(c => c.id === cropId);
    if (!crop || crop.stage !== 4) return;

    const sellPrice = marketPrices[crop.type] || 25;

    setHarvestAnimation(cropId);
    setTimeout(() => {
      setHarvestAnimation(null);
      setFarmState(prev => ({
        ...prev,
        crops: prev.crops.map(c =>
          c.id === cropId ? { ...c, stage: 0 as CropStage, growthTime: undefined } : c
        ),
        totalXp: prev.totalXp + (crop.harvestXp || 50),
        gold: prev.gold + sellPrice,
        harvested: {
          ...prev.harvested,
          [crop.type]: (prev.harvested[crop.type] || 0) + 1,
        },
      }));
    }, 600);
  };

  // 심기 처리
  const handlePlant = (cropId: string) => {
    if (!farmState.seeds[selectedSeedType] || farmState.seeds[selectedSeedType] <= 0) return;

    setFarmState(prev => ({
      ...prev,
      crops: prev.crops.map(c =>
        c.id === cropId && c.stage === 0
          ? {
              ...c,
              stage: 1 as CropStage,
              type: selectedSeedType,
              plantedAt: Date.now(),
              growthTime: GROWTH_TIMES[selectedSeedType] / 4,
            }
          : c
      ),
      seeds: {
        ...prev.seeds,
        [selectedSeedType]: prev.seeds[selectedSeedType] - 1,
      },
    }));
  };

  // 씨앗 구매
  const handleBuySeed = (type: CropVariety, quantity: number) => {
    const info = CROP_INFO[type as keyof typeof CROP_INFO];
    if (!info) return;
    const cost = info.buyPrice * quantity;
    if (farmState.gold < cost) return;

    setFarmState(prev => ({
      ...prev,
      gold: prev.gold - cost,
      seeds: {
        ...prev.seeds,
        [type]: (prev.seeds[type] || 0) + quantity,
      },
    }));
  };

  // 농장 확장
  const handleExpandFarm = () => {
    const nextExpansion = EXPANSION_COSTS.find(e => e.size > farmState.farmSize);
    if (!nextExpansion || farmState.gold < nextExpansion.cost) return;

    setFarmState(prev => ({
      ...prev,
      gold: prev.gold - nextExpansion.cost,
      farmSize: nextExpansion.size,
      crops: [
        ...prev.crops,
        ...Array(nextExpansion.size - prev.crops.length)
          .fill(null)
          .map((_, i) => ({
            id: `crop-${prev.crops.length + i}`,
            stage: 0 as CropStage,
            type: ALL_CROP_TYPES[i % ALL_CROP_TYPES.length],
          })),
      ],
    }));
    setActiveModal('none');
  };

  const currentHouse = HOUSE_LEVELS.find(h => h.level === farmState.houseLevel) || HOUSE_LEVELS[0];
  const nextHouse = HOUSE_LEVELS.find(h => h.level === farmState.houseLevel + 1);
  const readyCrops = farmState.crops.filter(c => c.stage === 4).length;
  const totalSeeds = Object.values(farmState.seeds).reduce((a, b) => a + b, 0);
  const nextExpansion = EXPANSION_COSTS.find(e => e.size > farmState.farmSize);

  const getGridCols = () => {
    if (farmState.farmSize <= 9) return 3;
    if (farmState.farmSize <= 16) return 4;
    return 5;
  };
  
  // 로딩 상태
  if (!farmState.character) {
    return (
      <div className="min-h-screen bg-[#7cba5f] flex items-center justify-center">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
        >
          <Leaf className="h-12 w-12 text-white" />
        </motion.div>
      </div>
    );
  }

  const hairColor = HAIR_COLORS[farmState.character.appearance.color] || HAIR_COLORS.brown;
  const xpProgress = nextHouse
    ? ((farmState.totalXp - currentHouse.xpRequired) / (nextHouse.xpRequired - currentHouse.xpRequired)) * 100
    : 100;

  return (
    <div className="min-h-screen bg-[#5a9f4a] pb-24">
      <Header />
      <TopNav />

      {/* 픽셀 아트 배경 */}
      <div
        className="min-h-[calc(100vh-120px)] relative overflow-hidden"
        style={{
          backgroundColor: '#5a9f4a',
          backgroundImage: `
            linear-gradient(90deg, rgba(106, 168, 79, 0.3) 1px, transparent 1px),
            linear-gradient(rgba(106, 168, 79, 0.3) 1px, transparent 1px)
          `,
          backgroundSize: '32px 32px',
        }}
      >
        {/* 하늘 그라데이션 */}
            <div
          className="absolute top-0 left-0 right-0 h-32 pointer-events-none"
              style={{
            background: 'linear-gradient(to bottom, #87CEEB 0%, #B0E2FF 50%, transparent 100%)',
          }}
        />
        
        {/* 태양 */}
        <motion.div
          className="absolute top-8 right-12 text-5xl"
          animate={{ rotate: [0, 5, 0, -5, 0] }}
          transition={{ duration: 8, repeat: Infinity }}
        >
          ☀️
        </motion.div>
        
        {/* 구름 */}
        <motion.div
          className="absolute top-16 left-20 text-3xl opacity-80"
          animate={{ x: [0, 30, 0] }}
          transition={{ duration: 20, repeat: Infinity }}
        >
          ☁️
        </motion.div>
        
        <div className="container mx-auto max-w-6xl p-4 md:p-6 relative z-10">
          {/* 뒤로가기 버튼 */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="mb-4"
          >
            <Link href="/">
              <Button
                variant="outline"
                size="sm"
                className={cn(
                  'bg-amber-100 hover:bg-amber-200 text-amber-900',
                  'border-4 border-amber-800 shadow-[3px_3px_0_0_#78350f]',
                  'font-bold transition-transform hover:translate-y-[-2px]'
                )}
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                돌아가기
              </Button>
            </Link>
          </motion.div>

          {/* 농장 헤더 */}
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className={cn(
              'mb-6 p-4 rounded-xl',
              'bg-gradient-to-r from-amber-100 to-amber-200',
              'border-4 border-amber-800',
              'shadow-[4px_4px_0_0_#78350f]'
            )}
          >
            <div className="flex items-center justify-between flex-wrap gap-4">
              <div className="flex items-center gap-4">
                <FarmerSprite 
                    hairColor={hairColor}
                  clothesColor={hairColor}
                  size={48}
                  action="idle"
                  />
                <div>
                  <h1 className="text-xl md:text-2xl font-bold text-amber-900">
                    {farmState.character.farmName || '나의 농장'}
                  </h1>
                  <div className="flex items-center gap-3 text-sm text-amber-800">
                    <span className="flex items-center gap-1 font-medium">
                      <Coins className="h-4 w-4 text-yellow-600" />
                      <span className="font-bold text-yellow-700">{farmState.gold.toLocaleString()}G</span>
                    </span>
                    <span className="text-amber-600">|</span>
                    <span className="flex items-center gap-1">
                      <Leaf className="h-4 w-4 text-green-600" />
                      <span className="font-bold text-green-700">Lv.{farmState.level}</span>
                    </span>
                  </div>
                </div>
              </div>

              {readyCrops > 0 && (
              <motion.div
                  animate={{ scale: [1, 1.05, 1] }}
                  transition={{ repeat: Infinity, duration: 1.5 }}
                >
                  <Badge className="bg-yellow-400 text-yellow-900 border-2 border-yellow-600 gap-1 font-bold px-3 py-1">
                    <Sparkles className="h-4 w-4" />
                    {readyCrops}개 수확 가능!
                  </Badge>
              </motion.div>
              )}
            </div>
          </motion.div>

          {/* 메인 콘텐츠 - 2컬럼 */}
          <div className="grid grid-cols-1 lg:grid-cols-[1fr_300px] gap-6">
            {/* 왼쪽: 농작물 + 농부 */}
          <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="relative"
            >
              <div
            className={cn(
                  'p-4 rounded-xl relative',
              'bg-gradient-to-b from-amber-700 to-amber-800',
              'border-4 border-amber-900',
                  'shadow-[4px_4px_0_0_#451a03]',
                  'min-h-[450px]'
            )}
          >
                {/* 헤더 */}
            <div className="flex items-center justify-between mb-4">
              <h2 className="flex items-center gap-2 font-bold text-amber-100 text-lg">
                <Sprout className="h-5 w-5" />
                농작물
              </h2>
                {nextExpansion && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setActiveModal('expand')}
                    className="bg-green-100 hover:bg-green-200 text-green-900 border-2 border-green-700"
                  >
                    <Expand className="h-3 w-3 mr-1" />
                    확장
                  </Button>
                )}
            </div>

                {/* 농부 캐릭터 */}
                {!farmerState.isInHouse && (
                  <motion.div
                    className="absolute z-20 pointer-events-none"
                    animate={{
                      left: `${farmerState.x}%`,
                      top: `${farmerState.y}%`,
                    }}
                    transition={{
                      type: 'spring',
                      stiffness: 50,
                      damping: 15,
                    }}
                    style={{ transform: 'translate(-50%, -50%)' }}
                  >
                    <FarmerSprite
                      action={farmerState.action}
                      direction={farmerState.direction}
                      hairColor={hairColor}
                      clothesColor={hairColor}
                      size={40}
                      animated
                    />
                  </motion.div>
                )}
                
                {/* 작물 그리드 */}
                <div
                  className="grid gap-2 relative z-10"
              style={{ gridTemplateColumns: `repeat(${getGridCols()}, 1fr)` }}
            >
                  {farmState.crops.map((crop) => (
                    <CropTile
                  key={crop.id}
                      crop={crop}
                    onClick={() => {
                      if (crop.stage === 4) handleHarvest(crop.id);
                      else if (crop.stage === 0) handlePlant(crop.id);
                    }}
                      isHarvesting={harvestAnimation === crop.id}
                      marketPrice={marketPrices[crop.type] || 25}
                    />
                  ))}
                  
                  {/* 확장 슬롯 */}
                  {nextExpansion && Array(Math.min(3, nextExpansion.size - farmState.farmSize)).fill(null).map((_, i) => (
                <motion.button
                  key={`expand-${i}`}
                  onClick={() => setActiveModal('expand')}
                  className={cn(
                    'w-full aspect-square rounded-lg flex flex-col items-center justify-center',
                    'border-4 border-dashed border-amber-500/50 bg-amber-700/30',
                    'hover:bg-amber-600/50 cursor-pointer transition-all'
                  )}
                  whileHover={{ scale: 1.05 }}
                >
                  <Plus className="h-6 w-6 text-amber-300/70" />
                </motion.button>
              ))}
            </div>

                {/* 선택된 씨앗 */}
            <p className="mt-4 text-xs text-center text-amber-200">
                  선택: <CropSprite type={selectedSeedType} stage={4} size={16} className="inline-block mx-1" />
                  {CROP_INFO[selectedSeedType as keyof typeof CROP_INFO]?.name || selectedSeedType} ({farmState.seeds[selectedSeedType] || 0}개)
            </p>
              </div>
          </motion.div>

            {/* 오른쪽: 집 + 정보 */}
          <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="space-y-4"
            >
              {/* 집 */}
              <div className={cn(
                'p-4 rounded-xl',
                'bg-gradient-to-b from-amber-100 to-amber-200',
                'border-4 border-amber-800',
                'shadow-[4px_4px_0_0_#78350f]'
              )}>
                <div className="flex items-center gap-2 mb-4">
                  <Home className="h-5 w-5 text-amber-800" />
                  <h3 className="font-bold text-amber-900">나의 집</h3>
                  <Badge className="ml-auto bg-amber-600 text-white">Lv.{farmState.houseLevel}</Badge>
                </div>
                
                {/* 집 스프라이트 (레벨별 크기) */}
                <div className="flex justify-center mb-4 relative">
                  <HouseSprite 
                    level={farmState.houseLevel} 
                    gridSize={20}
                    showFarmerInside={farmerState.isInHouse}
                  />
                  {farmerState.isInHouse && (
                    <div className="absolute -bottom-2 left-1/2 -translate-x-1/2 text-xs text-amber-700 bg-amber-100 px-2 py-0.5 rounded">
                      💤 휴식 중
                    </div>
                  )}
                </div>
                
                <p className="text-center font-bold text-amber-900 mb-2">{currentHouse.name}</p>
                <p className="text-center text-xs text-amber-700 mb-3">
                  크기: {currentHouse.gridSize}x{currentHouse.gridSize}
                </p>
                
                {/* 경험치 바 */}
                {nextHouse && (
                  <div>
                    <div className="flex justify-between text-xs text-amber-700 mb-1">
                      <span>경험치</span>
                      <span>{farmState.totalXp} / {nextHouse.xpRequired}</span>
                    </div>
                    <div className="h-3 bg-amber-300 rounded-full overflow-hidden border-2 border-amber-600">
                      <motion.div
                        className="h-full bg-gradient-to-r from-green-400 to-green-500"
                        initial={{ width: 0 }}
                        animate={{ width: `${Math.min(xpProgress, 100)}%` }}
                      />
                    </div>
                  </div>
                )}
              </div>
              
              {/* 골드 */}
              <div className={cn(
                'p-4 rounded-xl',
                'bg-gradient-to-r from-yellow-100 to-amber-100',
                'border-4 border-yellow-600',
                'shadow-[3px_3px_0_0_#a16207]'
              )}>
                <div className="flex items-center justify-center gap-2">
                  <Coins className="h-6 w-6 text-yellow-600" />
                  <span className="font-bold text-yellow-800 text-2xl">
                    {farmState.gold.toLocaleString()}G
                  </span>
                </div>
              </div>
              
              {/* 수확 기록 */}
              <div className={cn(
                'p-4 rounded-xl',
                'bg-gradient-to-b from-green-100 to-green-200',
                'border-4 border-green-700',
                'shadow-[3px_3px_0_0_#166534]'
              )}>
                <h3 className="font-bold text-green-900 mb-3 flex items-center gap-2">
                  <TrendingUp className="h-4 w-4" />
                  수확 기록
                </h3>
                <div className="grid grid-cols-4 gap-2">
                  {ALL_CROP_TYPES.slice(0, 4).map(type => (
                    <div key={type} className="text-center">
                      <CropSprite type={type} stage={4} size={24} />
                      <p className="text-xs font-bold text-green-800 mt-1">
                        {farmState.harvested[type] || 0}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
              
              {/* 도구 */}
              <div className={cn(
                'p-3 rounded-xl',
                'bg-gradient-to-b from-stone-100 to-stone-200',
                'border-3 border-stone-600'
              )}>
                <p className="text-xs font-bold text-stone-700 mb-2">도구</p>
                <div className="flex justify-around">
                  <ToolSprite type="sickle" size={28} />
                  <ToolSprite type="hoe" size={28} />
                  <ToolSprite type="wateringCan" size={28} />
                </div>
              </div>
          </motion.div>
          </div>
        </div>
      </div>

      {/* 하단 탭 바 */}
      <motion.div
        initial={{ y: 100 }}
        animate={{ y: 0 }}
        className={cn(
          'fixed bottom-0 left-0 right-0 z-50',
          'bg-amber-100 border-t-4 border-amber-800',
          'shadow-[0_-4px_0_0_#78350f]'
        )}
      >
        <div className="container mx-auto max-w-4xl">
          <div className="grid grid-cols-3 gap-1 p-2">
            <motion.button
              onClick={() => setActiveModal('seeds')}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className={cn(
                'flex flex-col items-center gap-1 py-3 px-4 rounded-lg',
                'bg-green-100 hover:bg-green-200 border-3 border-green-700',
                'shadow-[2px_2px_0_0_#166534]'
              )}
            >
              <CropSprite type="carrot" stage={1} size={24} />
              <span className="text-xs font-bold text-green-900">씨앗</span>
              <Badge className="text-[10px] bg-green-600 text-white px-1.5">{totalSeeds}</Badge>
            </motion.button>

            <motion.button
              onClick={() => setActiveModal('market')}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className={cn(
                'flex flex-col items-center gap-1 py-3 px-4 rounded-lg',
                'bg-blue-100 hover:bg-blue-200 border-3 border-blue-700',
                'shadow-[2px_2px_0_0_#1d4ed8]'
              )}
            >
              <TrendingUp className="h-5 w-5 text-blue-700" />
              <span className="text-xs font-bold text-blue-900">시세</span>
            </motion.button>

            <motion.button
              onClick={() => setActiveModal('shop')}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className={cn(
                'flex flex-col items-center gap-1 py-3 px-4 rounded-lg',
                'bg-yellow-100 hover:bg-yellow-200 border-3 border-yellow-700',
                'shadow-[2px_2px_0_0_#a16207]'
              )}
            >
              <ShoppingBag className="h-5 w-5 text-yellow-700" />
              <span className="text-xs font-bold text-yellow-900">상점</span>
            </motion.button>
          </div>
        </div>
      </motion.div>

      {/* 모달 */}
      <AnimatePresence>
        {activeModal !== 'none' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 z-50 flex items-end justify-center"
            onClick={() => setActiveModal('none')}
          >
            <motion.div
              initial={{ y: '100%' }}
              animate={{ y: 0 }}
              exit={{ y: '100%' }}
              transition={{ type: 'spring', damping: 25 }}
              onClick={e => e.stopPropagation()}
              className={cn(
                'w-full max-w-2xl max-h-[70vh] overflow-y-auto',
                'bg-amber-50 rounded-t-2xl border-t-4 border-x-4 border-amber-800'
              )}
            >
              {/* 모달 헤더 */}
              <div className="sticky top-0 bg-amber-100 p-4 border-b-2 border-amber-300 flex items-center justify-between">
                <h3 className="text-lg font-bold text-amber-900 flex items-center gap-2">
                  {activeModal === 'seeds' && <><Sprout className="h-5 w-5" /> 씨앗 보관함</>}
                  {activeModal === 'market' && <><TrendingUp className="h-5 w-5" /> 시장 시세</>}
                  {activeModal === 'shop' && <><ShoppingBag className="h-5 w-5" /> 상점</>}
                  {activeModal === 'expand' && <><Expand className="h-5 w-5" /> 농장 확장</>}
                </h3>
                <Button variant="ghost" size="sm" onClick={() => setActiveModal('none')}>
                  <X className="h-5 w-5" />
                </Button>
              </div>

              <div className="p-4">
                {/* 씨앗 모달 */}
                {activeModal === 'seeds' && (
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                    {ALL_CROP_TYPES.map(type => {
                      const info = CROP_INFO[type as keyof typeof CROP_INFO];
                      return (
                      <motion.button
                        key={type}
                        onClick={() => {
                          setSelectedSeedType(type);
                          setActiveModal('none');
                        }}
                        whileHover={{ scale: 1.02 }}
                        className={cn(
                          'p-3 rounded-lg border-3 flex items-center gap-3',
                          selectedSeedType === type
                            ? 'bg-green-100 border-green-600'
                            : 'bg-white border-amber-300 hover:border-amber-500'
                        )}
                      >
                          <CropSprite type={type} stage={4} size={32} />
                        <div className="text-left">
                            <p className="font-bold text-amber-900">{info?.name || type}</p>
                          <p className="text-xs text-amber-600">{farmState.seeds[type] || 0}개</p>
                        </div>
                      </motion.button>
                      );
                    })}
                  </div>
                )}

                {/* 시세 모달 */}
                {activeModal === 'market' && (
                  <div className="space-y-3">
                    <p className="text-sm text-amber-700 mb-4">시장 시세는 매일 변동됩니다!</p>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {ALL_CROP_TYPES.map(type => {
                        const info = CROP_INFO[type as keyof typeof CROP_INFO];
                        if (!info) return null;
                        const currentPrice = marketPrices[type] || info.sellPrice;
                        const change = ((currentPrice - info.sellPrice) / info.sellPrice) * 100;
                        const isUp = change > 0;
                        const isDown = change < 0;

                        return (
                          <div
                            key={type}
                            className={cn(
                              'p-3 rounded-lg border-3 flex items-center justify-between',
                              isUp ? 'bg-red-50 border-red-300' : isDown ? 'bg-blue-50 border-blue-300' : 'bg-white border-amber-300'
                            )}
                          >
                            <div className="flex items-center gap-3">
                              <CropSprite type={type} stage={4} size={32} />
                              <span className="font-bold text-amber-900">{info.name}</span>
                            </div>
                            <div className="text-right">
                              <p className={cn(
                                'font-bold',
                                isUp ? 'text-red-600' : isDown ? 'text-blue-600' : 'text-amber-900'
                              )}>
                                {currentPrice}G
                              </p>
                              {change !== 0 && (
                                <p className={cn('text-xs', isUp ? 'text-red-500' : 'text-blue-500')}>
                                  {isUp ? '▲' : '▼'} {Math.abs(change).toFixed(0)}%
                                </p>
                              )}
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}

                {/* 상점 모달 */}
                {activeModal === 'shop' && (
                  <div className="space-y-4">
                    <div className="flex items-center justify-between p-3 bg-yellow-100 rounded-lg border-2 border-yellow-400">
                      <span className="font-bold text-yellow-900">보유 골드</span>
                      <span className="font-bold text-yellow-700 text-lg">{farmState.gold.toLocaleString()}G</span>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {ALL_CROP_TYPES.map(type => {
                        const info = CROP_INFO[type as keyof typeof CROP_INFO];
                        if (!info) return null;
                        return (
                          <div key={type} className="p-3 rounded-lg border-3 bg-white border-amber-300">
                          <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center gap-2">
                                <CropSprite type={type} stage={4} size={32} />
                              <div>
                                  <p className="font-bold text-amber-900">{info.name} 씨앗</p>
                                  <p className="text-xs text-amber-600">{info.buyPrice}G / 개</p>
                              </div>
                            </div>
                          </div>
                          <div className="flex items-center gap-2">
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleBuySeed(type, 1)}
                                disabled={farmState.gold < info.buyPrice}
                              className="flex-1 border-2 border-green-600 text-green-700 hover:bg-green-100"
                            >
                                1개
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleBuySeed(type, 5)}
                                disabled={farmState.gold < info.buyPrice * 5}
                              className="flex-1 border-2 border-green-600 text-green-700 hover:bg-green-100"
                            >
                                5개
                            </Button>
                          </div>
                        </div>
                        );
                      })}
                    </div>
                  </div>
                )}

                {/* 확장 모달 */}
                {activeModal === 'expand' && nextExpansion && (
                  <div className="space-y-4">
                    <div className="p-4 bg-green-50 rounded-lg border-2 border-green-300">
                      <div className="flex items-center justify-between mb-4">
                        <div>
                          <p className="font-bold text-green-900">{nextExpansion.name}</p>
                          <p className="text-sm text-green-700">{farmState.farmSize} → {nextExpansion.size} 칸</p>
                        </div>
                        <div className="text-right">
                          <p className="font-bold text-yellow-700 text-lg">{nextExpansion.cost.toLocaleString()}G</p>
                        </div>
                      </div>
                      <Button
                        onClick={handleExpandFarm}
                        disabled={farmState.gold < nextExpansion.cost}
                        className={cn(
                          'w-full',
                          farmState.gold >= nextExpansion.cost
                            ? 'bg-green-600 hover:bg-green-700 text-white'
                            : 'bg-gray-300 text-gray-500'
                        )}
                      >
                        {farmState.gold >= nextExpansion.cost ? '확장하기' : '골드 부족'}
                      </Button>
                    </div>

                    <div className="space-y-2">
                      {EXPANSION_COSTS.map(exp => (
                        <div
                          key={exp.size}
                          className={cn(
                            'p-2 rounded-lg border-2 flex items-center justify-between',
                            exp.size <= farmState.farmSize
                              ? 'bg-green-100 border-green-400'
                              : exp.size === nextExpansion.size
                                ? 'bg-yellow-50 border-yellow-400'
                                : 'bg-gray-50 border-gray-300'
                          )}
                        >
                            <span className={cn(
                              'font-medium',
                              exp.size <= farmState.farmSize ? 'text-green-800' : 'text-gray-600'
                            )}>
                            {exp.size <= farmState.farmSize && '✓ '}{exp.name}
                            </span>
                          <span className="text-sm text-amber-600">
                            {exp.size}칸 {exp.cost > 0 && `(${exp.cost.toLocaleString()}G)`}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
