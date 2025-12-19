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
} from '@/components/farm/PixelSprites';
import {
  Leaf,
  Sprout,
  Sparkles,
  ShoppingBag,
  Package,
  ChevronRight,
  ArrowLeft,
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
  type: 'tomato' | 'wheat' | 'corn' | 'carrot' | 'turnip';
  harvestXp?: number;
}

// Farm state
interface FarmState {
  character: CharacterData | null;
  crops: Crop[];
  houseLevel: 1 | 2 | 3 | 4;
  totalXp: number;
  level: number;
  inventory: {
    seeds: number;
    fertilizer: number;
    harvested: number;
    coins: number;
  };
}

const HOUSE_LEVELS = [
  { level: 1, name: '초가집', xpRequired: 0 },
  { level: 2, name: '나무집', xpRequired: 500 },
  { level: 3, name: '벽돌집', xpRequired: 1500 },
  { level: 4, name: '황금 저택', xpRequired: 5000 },
];

const STAGE_LABELS = ['빈 땅', '씨앗', '새싹', '성장 중', '수확!'];

const CROP_TYPES: Array<'tomato' | 'wheat' | 'corn' | 'carrot' | 'turnip'> = [
  'tomato', 'wheat', 'corn', 'carrot', 'turnip'
];

const initialCrops: Crop[] = Array(9)
  .fill(null)
  .map((_, i) => ({
    id: `crop-${i}`,
    stage: (i < 3 ? 4 : i < 5 ? 3 : i < 7 ? 2 : 0) as 0 | 1 | 2 | 3 | 4,
    type: CROP_TYPES[i % CROP_TYPES.length],
    harvestXp: i < 3 ? 50 : undefined,
  }));

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

export default function FarmPage() {
  const router = useRouter();
  const [farmState, setFarmState] = useState<FarmState>({
    character: null,
    crops: initialCrops,
    houseLevel: 1,
    totalXp: 450,
    level: 5,
    inventory: {
      seeds: 10,
      fertilizer: 3,
      harvested: 25,
      coins: 150,
    },
  });
  const [harvestAnimation, setHarvestAnimation] = useState<string | null>(null);
  const [selectedCrop, setSelectedCrop] = useState<string | null>(null);

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

    setHarvestAnimation(cropId);
    setTimeout(() => {
      setHarvestAnimation(null);
      setFarmState((prev) => ({
        ...prev,
        crops: prev.crops.map((c) =>
          c.id === cropId ? { ...c, stage: 0 as const } : c
        ),
        totalXp: prev.totalXp + (crop.harvestXp || 50),
        inventory: {
          ...prev.inventory,
          harvested: prev.inventory.harvested + 1,
          coins: prev.inventory.coins + 10,
        },
      }));
    }, 600);
  };

  const handlePlant = (cropId: string) => {
    if (farmState.inventory.seeds <= 0) return;

    setFarmState((prev) => ({
      ...prev,
      crops: prev.crops.map((c) =>
        c.id === cropId && c.stage === 0
          ? { ...c, stage: 1 as const, type: CROP_TYPES[Math.floor(Math.random() * CROP_TYPES.length)] }
          : c
      ),
      inventory: {
        ...prev.inventory,
        seeds: prev.inventory.seeds - 1,
      },
    }));
  };

  const currentHouse = HOUSE_LEVELS.find((h) => h.level === farmState.houseLevel) || HOUSE_LEVELS[0];
  const nextHouse = HOUSE_LEVELS.find((h) => h.level === farmState.houseLevel + 1);
  const xpProgress = nextHouse
    ? ((farmState.totalXp - currentHouse.xpRequired) /
        (nextHouse.xpRequired - currentHouse.xpRequired)) *
      100
    : 100;

  const readyCrops = farmState.crops.filter((c) => c.stage === 4).length;

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

  return (
    <div className="min-h-screen bg-[#5a9f4a]">
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

        <div className="container mx-auto max-w-5xl p-4 md:p-6 relative z-10">
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
                    hairStyle={farmState.character.appearance.hair as any}
                    hairColor={hairColor}
                    clothesColor={clothesColor}
                    size={56}
                  />
                </motion.div>
                <div>
                  <h1 className="text-xl md:text-2xl font-bold text-amber-900">
                    {farmState.character.farmName}
                  </h1>
                  <div className="flex items-center gap-3 text-sm text-amber-800">
                    <span className="flex items-center gap-1 font-medium">
                      <Leaf className="h-4 w-4 text-green-600" />
                      Lv.{farmState.level} 농부
                    </span>
                    <span className="text-amber-600">|</span>
                    <span className="flex items-center gap-1">
                      <ItemPixel type="coin" size={16} />
                      <span className="font-bold text-yellow-700">{farmState.inventory.coins}</span>
                    </span>
                    <span className="text-amber-600">|</span>
                    <span className="flex items-center gap-1">
                      <Sparkles className="h-4 w-4 text-purple-500" />
                      <span className="font-bold text-purple-700">{farmState.totalXp} XP</span>
                    </span>
                  </div>
                </div>
              </div>

              {/* Quick Actions */}
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  className={cn(
                    'bg-green-100 hover:bg-green-200 text-green-900',
                    'border-3 border-green-700 shadow-[2px_2px_0_0_#166534]',
                    'transition-transform hover:translate-y-[-1px]'
                  )}
                >
                  <ShoppingBag className="h-4 w-4 mr-1" />
                  상점
                </Button>
              </div>
            </div>
          </motion.div>

          <div className="grid gap-6 lg:grid-cols-3">
            {/* Main Farm Area */}
            <div className="lg:col-span-2 space-y-6">
              {/* House Display */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                className={cn(
                  'p-6 rounded-lg text-center',
                  'bg-gradient-to-b from-sky-300 to-sky-400',
                  'border-4 border-sky-700',
                  'shadow-[4px_4px_0_0_#0369a1]'
                )}
              >
                {/* Sky background decoration */}
                <div className="absolute top-2 left-4 w-8 h-4 bg-white/50 rounded-full" />
                <div className="absolute top-4 right-8 w-12 h-5 bg-white/40 rounded-full" />

                <motion.div
                  initial={{ scale: 0, rotate: -10 }}
                  animate={{ scale: 1, rotate: 0 }}
                  transition={{ delay: 0.3, type: 'spring', stiffness: 200 }}
                  className="mb-4 flex justify-center"
                >
                  <HousePixel level={farmState.houseLevel} size={120} />
                </motion.div>
                <p className="font-bold text-sky-900 text-lg">{currentHouse.name}</p>

                {/* Upgrade Progress */}
                {nextHouse && (
                  <div className="mt-4 mx-auto max-w-xs">
                    <div className="flex items-center justify-between text-xs text-sky-800 mb-1 font-medium">
                      <span>다음: {nextHouse.name}</span>
                      <span>
                        {farmState.totalXp} / {nextHouse.xpRequired} XP
                      </span>
                    </div>
                    <div className="h-4 bg-sky-200 rounded-lg border-2 border-sky-600 overflow-hidden">
                      <motion.div
                        className="h-full bg-gradient-to-r from-yellow-400 to-yellow-500"
                        initial={{ width: 0 }}
                        animate={{ width: `${xpProgress}%` }}
                        transition={{ duration: 0.5, delay: 0.5 }}
                      />
                    </div>
                  </div>
                )}
              </motion.div>

              {/* Crop Grid */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className={cn(
                  'p-4 rounded-lg',
                  'bg-gradient-to-b from-amber-700 to-amber-800',
                  'border-4 border-amber-900',
                  'shadow-[4px_4px_0_0_#451a03]'
                )}
              >
                <div className="flex items-center justify-between mb-4">
                  <h2 className="flex items-center gap-2 font-bold text-amber-100 text-lg">
                    <Sprout className="h-5 w-5" />
                    농작물
                  </h2>
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
                </div>

                <div className="grid grid-cols-3 gap-3">
                  {farmState.crops.map((crop, index) => (
                    <motion.div
                      key={crop.id}
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: 0.05 * index }}
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
                          'w-full aspect-square rounded-lg flex flex-col items-center justify-center gap-1',
                          'border-4 transition-all',
                          crop.stage === 4
                            ? 'bg-gradient-to-b from-yellow-200 to-yellow-300 border-yellow-500 cursor-pointer shadow-[3px_3px_0_0_#854d0e]'
                            : crop.stage === 0
                              ? 'bg-amber-600/80 border-amber-700 border-dashed hover:bg-amber-500 cursor-pointer'
                              : 'bg-amber-600 border-amber-700'
                        )}
                      >
                        <CropPixel
                          stage={crop.stage}
                          type={crop.type}
                          size={48}
                        />
                        <span className={cn(
                          'text-xs font-bold',
                          crop.stage === 4 ? 'text-yellow-800' : 'text-amber-200'
                        )}>
                          {STAGE_LABELS[crop.stage]}
                        </span>
                        {crop.stage === 4 && (
                          <span className="text-xs font-bold text-green-700 flex items-center gap-1">
                            +50 XP
                          </span>
                        )}
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
                              +50!
                            </span>
                          </motion.div>
                        )}
                      </AnimatePresence>
                    </motion.div>
                  ))}
                </div>

                <p className="mt-4 text-xs text-center text-amber-200">
                  문제를 풀면 작물이 자라요! 수확하면 XP와 코인을 얻을 수 있어요.
                </p>
              </motion.div>
            </div>

            {/* Sidebar */}
            <div className="space-y-6">
              {/* Inventory */}
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.3 }}
                className={cn(
                  'p-4 rounded-lg',
                  'bg-stone-100 border-4 border-stone-600',
                  'shadow-[4px_4px_0_0_#44403c]'
                )}
              >
                <h3 className="flex items-center gap-2 font-bold text-stone-800 mb-3">
                  <Package className="h-4 w-4" />
                  인벤토리
                </h3>
                <div className="space-y-2">
                  {[
                    { type: 'seed' as const, label: '씨앗', count: farmState.inventory.seeds },
                    { type: 'fertilizer' as const, label: '비료', count: farmState.inventory.fertilizer },
                    { type: 'harvest' as const, label: '수확물', count: farmState.inventory.harvested },
                    { type: 'coin' as const, label: '코인', count: farmState.inventory.coins },
                  ].map((item) => (
                    <div
                      key={item.type}
                      className="flex items-center justify-between p-2 bg-white rounded-lg border-2 border-stone-300"
                    >
                      <span className="flex items-center gap-2">
                        <ItemPixel type={item.type} size={24} />
                        <span className="text-sm font-medium text-stone-700">{item.label}</span>
                      </span>
                      <span className="font-bold text-stone-800 bg-stone-200 px-2 py-0.5 rounded">
                        {item.count}
                      </span>
                    </div>
                  ))}
                </div>
              </motion.div>

              {/* Quick Actions */}
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.4 }}
                className={cn(
                  'p-4 rounded-lg',
                  'bg-green-100 border-4 border-green-700',
                  'shadow-[4px_4px_0_0_#166534]'
                )}
              >
                <h3 className="font-bold text-green-900 mb-3">빠른 행동</h3>
                <Link href="/chat">
                  <Button
                    className={cn(
                      'w-full justify-between',
                      'bg-green-500 hover:bg-green-600 text-white',
                      'border-4 border-green-700 shadow-[3px_3px_0_0_#15803d]',
                      'transition-transform hover:translate-y-[-2px]'
                    )}
                  >
                    <span className="flex items-center gap-2">
                      <Sparkles className="h-4 w-4" />
                      문제 풀러 가기
                    </span>
                    <ChevronRight className="h-4 w-4" />
                  </Button>
                </Link>
              </motion.div>

              {/* Tips */}
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.5 }}
                className={cn(
                  'p-4 rounded-lg',
                  'bg-blue-100 border-4 border-blue-600',
                  'shadow-[4px_4px_0_0_#1d4ed8]'
                )}
              >
                <p className="text-sm font-bold mb-2 flex items-center gap-2 text-blue-900">
                  <Leaf className="h-4 w-4" />
                  농장 팁
                </p>
                <ul className="text-xs text-blue-800 space-y-1">
                  <li>• 문제를 풀면 작물이 한 단계씩 성장해요</li>
                  <li>• 연속으로 문제를 풀면 보너스 성장!</li>
                  <li>• XP를 모아 집을 업그레이드하세요</li>
                </ul>
              </motion.div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
