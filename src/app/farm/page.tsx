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
  CropPixel,
  HousePixel,
  CharacterPixel,
  ItemPixel,
  TilePixel,
  CropType,
  CROP_INFO,
} from '@/components/farm/PixelSprites';
import {
  Leaf,
  Sprout,
  Sparkles,
  ShoppingBag,
  Package,
  ChevronRight,
  ArrowLeft,
  TrendingUp,
  X,
  Plus,
  Minus,
  Home,
  Coins,
  Expand,
} from 'lucide-react';
import { cn } from '@/lib/utils';

// Character data from localStorage
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

// Farm crop types
interface Crop {
  id: string;
  stage: 0 | 1 | 2 | 3 | 4;
  type: CropType;
  harvestXp?: number;
  plantedAt?: number;
}

// Seed inventory
interface SeedInventory {
  [key: string]: number;
}

// Farm state
interface FarmState {
  character: CharacterData | null;
  crops: Crop[];
  houseLevel: 1 | 2 | 3 | 4;
  totalXp: number;
  level: number;
  gold: number;
  seeds: SeedInventory;
  farmSize: number; // Number of plots unlocked
  harvested: { [key: string]: number }; // Harvested crops count
}

type BottomTab = 'seeds' | 'market' | 'shop';
type ModalType = 'none' | 'seeds' | 'market' | 'shop' | 'expand';

const HOUSE_LEVELS = [
  { level: 1, name: '초가집', xpRequired: 0 },
  { level: 2, name: '나무집', xpRequired: 500 },
  { level: 3, name: '벽돌집', xpRequired: 1500 },
  { level: 4, name: '황금 저택', xpRequired: 5000 },
];

const STAGE_LABELS = ['빈 땅', '씨앗', '새싹', '성장 중', '수확!'];

const ALL_CROP_TYPES: CropType[] = [
  'carrot', 'tomato', 'corn', 'strawberry', 'grape', 'potato', 'wheat', 'turnip', 'pumpkin', 'watermelon'
];

// Market price fluctuation (random multiplier)
const getMarketMultiplier = () => {
  const multipliers = [0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.5];
  return multipliers[Math.floor(Math.random() * multipliers.length)];
};

// Initial crops setup
const createInitialCrops = (size: number): Crop[] => {
  return Array(size)
    .fill(null)
    .map((_, i) => ({
      id: `crop-${i}`,
      stage: (i < 3 ? 4 : i < 5 ? 3 : i < 7 ? 2 : 0) as 0 | 1 | 2 | 3 | 4,
      type: ALL_CROP_TYPES[i % ALL_CROP_TYPES.length],
      harvestXp: i < 3 ? 50 : undefined,
    }));
};

// Initial seeds
const createInitialSeeds = (): SeedInventory => {
  const seeds: SeedInventory = {};
  ALL_CROP_TYPES.forEach(type => {
    seeds[type] = Math.floor(Math.random() * 5) + 2;
  });
  return seeds;
};

// Hair color mapping
const HAIR_COLORS: Record<string, string> = {
  brown: '#8B4513',
  black: '#2d2d2d',
  blonde: '#f4d03f',
  red: '#c0392b',
  blue: '#3498db',
  pink: '#e91e8a',
};

// Clothes color mapping
const CLOTHES_COLORS: Record<string, string> = {
  brown: '#8B4513',
  black: '#2d2d2d',
  blonde: '#f4d03f',
  red: '#c0392b',
  blue: '#3498db',
  pink: '#e91e8a',
};

// Farm expansion costs
const EXPANSION_COSTS = [
  { size: 9, cost: 0, name: '기본 농장' },
  { size: 12, cost: 500, name: '작은 확장' },
  { size: 16, cost: 1500, name: '중간 확장' },
  { size: 20, cost: 3000, name: '큰 확장' },
  { size: 25, cost: 6000, name: '최대 확장' },
];

export default function FarmPage() {
  const router = useRouter();
  const [farmState, setFarmState] = useState<FarmState>({
    character: null,
    crops: createInitialCrops(9),
    houseLevel: 1,
    totalXp: 450,
    level: 15,
    gold: 1250,
    seeds: createInitialSeeds(),
    farmSize: 9,
    harvested: {},
  });
  const [harvestAnimation, setHarvestAnimation] = useState<string | null>(null);
  const [selectedCrop, setSelectedCrop] = useState<string | null>(null);
  const [activeModal, setActiveModal] = useState<ModalType>('none');
  const [selectedSeedType, setSelectedSeedType] = useState<CropType>('carrot');
  const [marketPrices, setMarketPrices] = useState<Record<CropType, number>>({} as Record<CropType, number>);
  const [shopQuantity, setShopQuantity] = useState(1);

  // Initialize market prices
  useEffect(() => {
    const prices: Record<CropType, number> = {} as Record<CropType, number>;
    ALL_CROP_TYPES.forEach(type => {
      prices[type] = Math.round(CROP_INFO[type].sellPrice * getMarketMultiplier());
    });
    setMarketPrices(prices);
  }, []);

  // Check if character exists
  useEffect(() => {
    const savedCharacter = localStorage.getItem('codefill_character');
    if (savedCharacter) {
      try {
        const character = JSON.parse(savedCharacter);
        setFarmState((prev) => ({ ...prev, character }));
      } catch {
        router.push('/');
      }
    } else {
      router.push('/');
    }
  }, [router]);

  const handleHarvest = (cropId: string) => {
    const crop = farmState.crops.find((c) => c.id === cropId);
    if (!crop || crop.stage !== 4) return;

    const sellPrice = marketPrices[crop.type] || CROP_INFO[crop.type].sellPrice;

    setHarvestAnimation(cropId);
    setTimeout(() => {
      setHarvestAnimation(null);
      setFarmState((prev) => ({
        ...prev,
        crops: prev.crops.map((c) =>
          c.id === cropId ? { ...c, stage: 0 as const } : c
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

  const handlePlant = (cropId: string) => {
    if (!farmState.seeds[selectedSeedType] || farmState.seeds[selectedSeedType] <= 0) return;

    setFarmState((prev) => ({
      ...prev,
      crops: prev.crops.map((c) =>
        c.id === cropId && c.stage === 0
          ? { ...c, stage: 1 as const, type: selectedSeedType, plantedAt: Date.now() }
          : c
      ),
      seeds: {
        ...prev.seeds,
        [selectedSeedType]: prev.seeds[selectedSeedType] - 1,
      },
    }));
  };

  const handleBuySeed = (type: CropType, quantity: number) => {
    const cost = CROP_INFO[type].buyPrice * quantity;
    if (farmState.gold < cost) return;

    setFarmState((prev) => ({
      ...prev,
      gold: prev.gold - cost,
      seeds: {
        ...prev.seeds,
        [type]: (prev.seeds[type] || 0) + quantity,
      },
    }));
  };

  const handleExpandFarm = () => {
    const currentExpansion = EXPANSION_COSTS.find(e => e.size === farmState.farmSize);
    const nextExpansion = EXPANSION_COSTS.find(e => e.size > farmState.farmSize);

    if (!nextExpansion || farmState.gold < nextExpansion.cost) return;

    setFarmState((prev) => ({
      ...prev,
      gold: prev.gold - nextExpansion.cost,
      farmSize: nextExpansion.size,
      crops: [
        ...prev.crops,
        ...Array(nextExpansion.size - prev.crops.length)
          .fill(null)
          .map((_, i) => ({
            id: `crop-${prev.crops.length + i}`,
            stage: 0 as const,
            type: ALL_CROP_TYPES[i % ALL_CROP_TYPES.length],
          })),
      ],
    }));
    setActiveModal('none');
  };

  const currentHouse = HOUSE_LEVELS.find((h) => h.level === farmState.houseLevel) || HOUSE_LEVELS[0];
  const nextHouse = HOUSE_LEVELS.find((h) => h.level === farmState.houseLevel + 1);
  const xpProgress = nextHouse
    ? ((farmState.totalXp - currentHouse.xpRequired) /
        (nextHouse.xpRequired - currentHouse.xpRequired)) *
      100
    : 100;

  const readyCrops = farmState.crops.filter((c) => c.stage === 4).length;
  const totalSeeds = Object.values(farmState.seeds).reduce((a, b) => a + b, 0);
  const nextExpansion = EXPANSION_COSTS.find(e => e.size > farmState.farmSize);

  // Loading state
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
  const clothesColor = CLOTHES_COLORS[farmState.character.appearance.color] || CLOTHES_COLORS.blue;

  // Calculate grid columns based on farm size
  const getGridCols = () => {
    if (farmState.farmSize <= 9) return 3;
    if (farmState.farmSize <= 16) return 4;
    return 5;
  };

  return (
    <div className="min-h-screen bg-[#5a9f4a] pb-24">
      <Header />
      <TopNav />

      {/* Pixel art grass background */}
      <div
        className="min-h-[calc(100vh-120px)] relative"
        style={{
          backgroundColor: '#5a9f4a',
          backgroundImage: `
            linear-gradient(90deg, rgba(106, 168, 79, 0.5) 1px, transparent 1px),
            linear-gradient(rgba(106, 168, 79, 0.5) 1px, transparent 1px)
          `,
          backgroundSize: '32px 32px',
        }}
      >
        {/* Decorative grass tiles */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none opacity-30">
          {Array(20).fill(null).map((_, i) => (
            <div
              key={i}
              className="absolute"
              style={{
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
              }}
            >
              <TilePixel type="grass" size={32} />
            </div>
          ))}
        </div>

        <div className="container mx-auto max-w-4xl p-4 md:p-6 relative z-10">
          {/* Back Button */}
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

          {/* Farm Header */}
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className={cn(
              'mb-6 p-4 rounded-lg',
              'bg-amber-100 border-4 border-amber-800',
              'shadow-[4px_4px_0_0_#78350f]'
            )}
          >
            <div className="flex items-center justify-between flex-wrap gap-4">
              <div className="flex items-center gap-4">
                {/* Character Avatar */}
                <motion.div
                  className={cn(
                    'p-2 rounded-lg bg-amber-50',
                    'border-4 border-amber-700 shadow-[2px_2px_0_0_#92400e]'
                  )}
                  whileHover={{ scale: 1.05 }}
                >
                  <CharacterPixel
                    hairStyle={farmState.character.appearance.hair as 'short' | 'long' | 'curly' | 'spiky'}
                    hairColor={hairColor}
                    clothesColor={clothesColor}
                    size={56}
                  />
                </motion.div>
                <div>
                  <h1 className="text-xl md:text-2xl font-bold text-amber-900">
                    나의 농장
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

              {/* House */}
              <motion.div
                className="flex flex-col items-center"
                whileHover={{ scale: 1.05 }}
              >
                <HousePixel level={farmState.houseLevel} size={64} />
                <span className="text-xs font-bold text-amber-800 mt-1">{currentHouse.name}</span>
              </motion.div>
            </div>
          </motion.div>

          {/* Main Farm Grid */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className={cn(
              'p-4 rounded-lg relative',
              'bg-gradient-to-b from-amber-700 to-amber-800',
              'border-4 border-amber-900',
              'shadow-[4px_4px_0_0_#451a03]'
            )}
          >
            {/* Farm Grid Header */}
            <div className="flex items-center justify-between mb-4">
              <h2 className="flex items-center gap-2 font-bold text-amber-100 text-lg">
                <Sprout className="h-5 w-5" />
                농작물
              </h2>
              <div className="flex gap-2">
                {readyCrops > 0 && (
                  <motion.div
                    animate={{ scale: [1, 1.1, 1] }}
                    transition={{ repeat: Infinity, duration: 1.5 }}
                  >
                    <Badge className="bg-yellow-400 text-yellow-900 border-2 border-yellow-600 gap-1 font-bold">
                      <Sparkles className="h-3 w-3" />
                      {readyCrops}개 수확 가능!
                    </Badge>
                  </motion.div>
                )}
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
            </div>

            {/* Crop Grid */}
            <div
              className="grid gap-2"
              style={{ gridTemplateColumns: `repeat(${getGridCols()}, 1fr)` }}
            >
              {farmState.crops.map((crop, index) => (
                <motion.div
                  key={crop.id}
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.03 * index }}
                  className="relative"
                >
                  <motion.button
                    type="button"
                    onClick={() => {
                      if (crop.stage === 4) handleHarvest(crop.id);
                      else if (crop.stage === 0) handlePlant(crop.id);
                    }}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className={cn(
                      'w-full aspect-square rounded-lg flex flex-col items-center justify-center',
                      'border-4 transition-all relative overflow-hidden',
                      crop.stage === 4
                        ? 'bg-gradient-to-b from-yellow-200 to-yellow-300 border-yellow-500 cursor-pointer shadow-[3px_3px_0_0_#854d0e]'
                        : crop.stage === 0
                          ? 'bg-amber-600/80 border-amber-700 border-dashed hover:bg-amber-500 cursor-pointer'
                          : 'bg-amber-600 border-amber-700'
                    )}
                  >
                    {/* Show emoji for crops */}
                    <span className="text-2xl md:text-3xl">
                      {crop.stage === 0 ? '🌱' : CROP_INFO[crop.type].emoji}
                    </span>
                    <span className={cn(
                      'text-[10px] md:text-xs font-bold mt-1',
                      crop.stage === 4 ? 'text-yellow-800' : 'text-amber-200'
                    )}>
                      {crop.stage === 0 ? '심기' : crop.stage === 4 ? `+${marketPrices[crop.type] || CROP_INFO[crop.type].sellPrice}G` : STAGE_LABELS[crop.stage]}
                    </span>
                  </motion.button>

                  {/* Harvest animation */}
                  <AnimatePresence>
                    {harvestAnimation === crop.id && (
                      <motion.div
                        initial={{ opacity: 1, y: 0, scale: 1 }}
                        animate={{ opacity: 0, y: -40, scale: 1.5 }}
                        exit={{ opacity: 0 }}
                        className="absolute inset-0 flex items-center justify-center pointer-events-none"
                      >
                        <span className="text-2xl font-bold text-yellow-400 drop-shadow-lg">
                          +{marketPrices[crop.type] || CROP_INFO[crop.type].sellPrice}G!
                        </span>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </motion.div>
              ))}

              {/* Expansion placeholder slots */}
              {nextExpansion && Array(Math.min(4, nextExpansion.size - farmState.farmSize)).fill(null).map((_, i) => (
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
                  <span className="text-[10px] text-amber-300/70 mt-1">확장</span>
                </motion.button>
              ))}
            </div>

            <p className="mt-4 text-xs text-center text-amber-200">
              선택된 씨앗: {CROP_INFO[selectedSeedType].emoji} {CROP_INFO[selectedSeedType].name} ({farmState.seeds[selectedSeedType] || 0}개)
            </p>
          </motion.div>

          {/* Character on farm */}
          <motion.div
            className="absolute bottom-32 right-8 md:right-16"
            animate={{ y: [0, -5, 0] }}
            transition={{ repeat: Infinity, duration: 2 }}
          >
            <div className="text-4xl md:text-5xl">👨‍🌾</div>
          </motion.div>
        </div>
      </div>

      {/* Bottom Tab Bar */}
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
            {/* Seeds Tab */}
            <motion.button
              onClick={() => setActiveModal('seeds')}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className={cn(
                'flex flex-col items-center gap-1 py-3 px-4 rounded-lg',
                'bg-green-100 hover:bg-green-200 border-3 border-green-700',
                'shadow-[2px_2px_0_0_#166534] transition-all'
              )}
            >
              <span className="text-xl">🌱</span>
              <span className="text-xs font-bold text-green-900">씨앗</span>
              <Badge className="text-[10px] bg-green-600 text-white px-1.5">{totalSeeds}</Badge>
            </motion.button>

            {/* Market Tab */}
            <motion.button
              onClick={() => setActiveModal('market')}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className={cn(
                'flex flex-col items-center gap-1 py-3 px-4 rounded-lg',
                'bg-blue-100 hover:bg-blue-200 border-3 border-blue-700',
                'shadow-[2px_2px_0_0_#1d4ed8] transition-all'
              )}
            >
              <TrendingUp className="h-5 w-5 text-blue-700" />
              <span className="text-xs font-bold text-blue-900">시세</span>
            </motion.button>

            {/* Shop Tab */}
            <motion.button
              onClick={() => setActiveModal('shop')}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className={cn(
                'flex flex-col items-center gap-1 py-3 px-4 rounded-lg',
                'bg-yellow-100 hover:bg-yellow-200 border-3 border-yellow-700',
                'shadow-[2px_2px_0_0_#a16207] transition-all'
              )}
            >
              <ShoppingBag className="h-5 w-5 text-yellow-700" />
              <span className="text-xs font-bold text-yellow-900">상점</span>
            </motion.button>
          </div>
        </div>
      </motion.div>

      {/* Modal Overlays */}
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
              onClick={(e) => e.stopPropagation()}
              className={cn(
                'w-full max-w-2xl max-h-[70vh] overflow-y-auto',
                'bg-amber-50 rounded-t-2xl border-t-4 border-x-4 border-amber-800',
                'shadow-[0_-4px_0_0_#78350f]'
              )}
            >
              {/* Modal Header */}
              <div className="sticky top-0 bg-amber-100 p-4 border-b-2 border-amber-300 flex items-center justify-between">
                <h3 className="text-lg font-bold text-amber-900 flex items-center gap-2">
                  {activeModal === 'seeds' && <><span className="text-xl">🌱</span> 씨앗 보관함</>}
                  {activeModal === 'market' && <><TrendingUp className="h-5 w-5" /> 시장 시세</>}
                  {activeModal === 'shop' && <><ShoppingBag className="h-5 w-5" /> 상점</>}
                  {activeModal === 'expand' && <><Expand className="h-5 w-5" /> 농장 확장</>}
                </h3>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setActiveModal('none')}
                  className="text-amber-700 hover:text-amber-900"
                >
                  <X className="h-5 w-5" />
                </Button>
              </div>

              {/* Modal Content */}
              <div className="p-4">
                {/* Seeds Modal */}
                {activeModal === 'seeds' && (
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                    {ALL_CROP_TYPES.map((type) => (
                      <motion.button
                        key={type}
                        onClick={() => {
                          setSelectedSeedType(type);
                          setActiveModal('none');
                        }}
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        className={cn(
                          'p-3 rounded-lg border-3 flex items-center gap-3',
                          selectedSeedType === type
                            ? 'bg-green-100 border-green-600'
                            : 'bg-white border-amber-300 hover:border-amber-500'
                        )}
                      >
                        <span className="text-2xl">{CROP_INFO[type].emoji}</span>
                        <div className="text-left">
                          <p className="font-bold text-amber-900">{CROP_INFO[type].name}</p>
                          <p className="text-xs text-amber-600">{farmState.seeds[type] || 0}개</p>
                        </div>
                      </motion.button>
                    ))}
                  </div>
                )}

                {/* Market Modal */}
                {activeModal === 'market' && (
                  <div className="space-y-3">
                    <p className="text-sm text-amber-700 mb-4">시장 시세는 매일 변동됩니다!</p>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {ALL_CROP_TYPES.map((type) => {
                        const basePrice = CROP_INFO[type].sellPrice;
                        const currentPrice = marketPrices[type] || basePrice;
                        const change = ((currentPrice - basePrice) / basePrice) * 100;
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
                              <span className="text-2xl">{CROP_INFO[type].emoji}</span>
                              <span className="font-bold text-amber-900">{CROP_INFO[type].name}</span>
                            </div>
                            <div className="text-right">
                              <p className={cn(
                                'font-bold',
                                isUp ? 'text-red-600' : isDown ? 'text-blue-600' : 'text-amber-900'
                              )}>
                                {currentPrice}G
                              </p>
                              {change !== 0 && (
                                <p className={cn(
                                  'text-xs',
                                  isUp ? 'text-red-500' : 'text-blue-500'
                                )}>
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

                {/* Shop Modal */}
                {activeModal === 'shop' && (
                  <div className="space-y-4">
                    <div className="flex items-center justify-between p-3 bg-yellow-100 rounded-lg border-2 border-yellow-400">
                      <span className="font-bold text-yellow-900">보유 골드</span>
                      <span className="font-bold text-yellow-700 text-lg">{farmState.gold.toLocaleString()}G</span>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {ALL_CROP_TYPES.map((type) => (
                        <div
                          key={type}
                          className="p-3 rounded-lg border-3 bg-white border-amber-300"
                        >
                          <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center gap-2">
                              <span className="text-2xl">{CROP_INFO[type].emoji}</span>
                              <div>
                                <p className="font-bold text-amber-900">{CROP_INFO[type].name} 씨앗</p>
                                <p className="text-xs text-amber-600">{CROP_INFO[type].buyPrice}G / 개</p>
                              </div>
                            </div>
                          </div>
                          <div className="flex items-center gap-2">
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleBuySeed(type, 1)}
                              disabled={farmState.gold < CROP_INFO[type].buyPrice}
                              className="flex-1 border-2 border-green-600 text-green-700 hover:bg-green-100"
                            >
                              1개 구매
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleBuySeed(type, 5)}
                              disabled={farmState.gold < CROP_INFO[type].buyPrice * 5}
                              className="flex-1 border-2 border-green-600 text-green-700 hover:bg-green-100"
                            >
                              5개 구매
                            </Button>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Expand Modal */}
                {activeModal === 'expand' && nextExpansion && (
                  <div className="space-y-4">
                    <div className="p-4 bg-green-50 rounded-lg border-2 border-green-300">
                      <div className="flex items-center justify-between mb-4">
                        <div>
                          <p className="font-bold text-green-900">{nextExpansion.name}</p>
                          <p className="text-sm text-green-700">농장 크기: {farmState.farmSize} → {nextExpansion.size} 칸</p>
                        </div>
                        <div className="text-right">
                          <p className="font-bold text-yellow-700 text-lg">{nextExpansion.cost.toLocaleString()}G</p>
                          <p className="text-xs text-amber-600">필요 골드</p>
                        </div>
                      </div>
                      <Button
                        onClick={handleExpandFarm}
                        disabled={farmState.gold < nextExpansion.cost}
                        className={cn(
                          'w-full',
                          farmState.gold >= nextExpansion.cost
                            ? 'bg-green-600 hover:bg-green-700 text-white'
                            : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                        )}
                      >
                        {farmState.gold >= nextExpansion.cost ? '확장하기' : '골드 부족'}
                      </Button>
                    </div>

                    <div className="space-y-2">
                      <p className="text-sm font-bold text-amber-800">확장 단계</p>
                      {EXPANSION_COSTS.map((exp, i) => (
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
                          <div className="flex items-center gap-2">
                            {exp.size <= farmState.farmSize && <span className="text-green-600">✓</span>}
                            <span className={cn(
                              'font-medium',
                              exp.size <= farmState.farmSize ? 'text-green-800' : 'text-gray-600'
                            )}>
                              {exp.name}
                            </span>
                          </div>
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
