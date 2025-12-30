'use client';

/**
 * Farm Page - Phaser.js 기반 스타듀밸리 스타일 농장 게임
 */

import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import dynamic from 'next/dynamic';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import {
  useFarm,
  getSeedCount,
  calculateCropStage,
} from '@/hooks/useFarm';
import {
  ShoppingBag,
  Loader2,
  AlertCircle,
  Sprout,
  ChevronLeft,
  Expand,
} from 'lucide-react';

// UI 컴포넌트
import { Hotbar, ShopModal, ControlsGuide, ExpandModal, CROP_INFO, type CropVariety } from '@/components/farm/ui';

// Phaser 게임 컴포넌트 (SSR 비활성화)
const FarmGame = dynamic(() => import('@/components/farm/FarmGame'), {
  ssr: false,
  loading: () => (
    <div className="w-full h-full flex items-center justify-center bg-green-800">
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
      >
        <Loader2 className="w-12 h-12 text-white" />
      </motion.div>
    </div>
  ),
});

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
  } = useFarm();

  // UI 상태
  const [selectedSeed, setSelectedSeed] = useState<CropVariety>('carrot');
  const [showShop, setShowShop] = useState(false);
  const [showExpand, setShowExpand] = useState(false);
  const [notification, setNotification] = useState<{ message: string; type: 'success' | 'error' } | null>(null);

  // 작물 스테이지 계산 (1초마다 업데이트)
  const [farmSlots, setFarmSlots] = useState(farm?.farmSlots || []);

  useEffect(() => {
    if (farm) {
      setFarmSlots(farm.farmSlots.map(slot => {
        if (slot.cropCode && slot.plantedAt) {
          const cropInfo = items.find(item => item.code === slot.cropCode);
          const growTime = cropInfo?.growTimeSeconds || 120;
          const stage = calculateCropStage(slot.plantedAt, growTime);
          return { ...slot, stage };
        }
        return slot;
      }));
    }
  }, [farm, items]);

  // 1초마다 스테이지 업데이트
  useEffect(() => {
    if (!farm || items.length === 0) return;

    const interval = setInterval(() => {
      setFarmSlots(prev => prev.map(slot => {
        if (slot.cropCode && slot.plantedAt) {
          const cropInfo = items.find(item => item.code === slot.cropCode);
          const growTime = cropInfo?.growTimeSeconds || 120;
          const stage = calculateCropStage(slot.plantedAt, growTime);
          return { ...slot, stage };
        }
        return slot;
      }));
    }, 1000);

    return () => clearInterval(interval);
  }, [farm, items]);

  // 캐릭터 미생성 시 리다이렉트
  useEffect(() => {
    if (!isLoading && farm && !farm.characterCreated) {
      router.push('/');
    }
  }, [isLoading, farm, router]);

  // 씨앗 심기
  const handlePlant = useCallback(async (slot: number, cropCode: string) => {
    const seedCount = getSeedCount(inventory, cropCode);
    if (seedCount <= 0) {
      setNotification({ message: '씨앗이 부족합니다!', type: 'error' });
      setTimeout(() => setNotification(null), 2000);
      return;
    }

    try {
      await plant(slot, cropCode);
      setNotification({ message: '씨앗을 심었습니다!', type: 'success' });
      setTimeout(() => setNotification(null), 2000);
    } catch (err) {
      console.error('Plant failed:', err);
      setNotification({ message: '심기 실패', type: 'error' });
      setTimeout(() => setNotification(null), 2000);
    }
  }, [plant, inventory]);

  // 수확
  const handleHarvest = useCallback(async (slot: number) => {
    try {
      const result = await harvest(slot);
      if (result) {
        setNotification({ message: `+${result.gold}G 획득!`, type: 'success' });
        setTimeout(() => setNotification(null), 2000);
      }
    } catch (err) {
      console.error('Harvest failed:', err);
      setNotification({ message: '수확 실패', type: 'error' });
      setTimeout(() => setNotification(null), 2000);
    }
  }, [harvest]);

  // 씨앗 구매
  const handleBuySeed = useCallback(async (cropCode: CropVariety, quantity: number) => {
    try {
      await buySeed(cropCode, quantity);
      setNotification({ message: `${CROP_INFO[cropCode].name} 씨앗 ${quantity}개 구매!`, type: 'success' });
      setTimeout(() => setNotification(null), 2000);
    } catch (err) {
      console.error('Buy failed:', err);
      setNotification({ message: '구매 실패', type: 'error' });
      setTimeout(() => setNotification(null), 2000);
    }
  }, [buySeed]);

  // 농장 확장
  const handleExpand = useCallback(async (targetSize: number) => {
    try {
      await expand(targetSize);
      setNotification({ message: '농장이 확장되었습니다!', type: 'success' });
      setTimeout(() => setNotification(null), 2000);
    } catch (err) {
      console.error('Expand failed:', err);
      setNotification({ message: err instanceof Error ? err.message : '확장 실패', type: 'error' });
      setTimeout(() => setNotification(null), 2000);
      throw err;  // ExpandModal에서 에러 처리하도록
    }
  }, [expand]);

  // Phaser에서 알림 표시 (씨앗 부족, 수확 불가 등)
  const handleNotify = useCallback((message: string, type: 'success' | 'error') => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 2000);
  }, []);

  // 계산된 값들
  const gold = farm?.gold || 0;
  const farmLevel = farm?.farmLevel || 1;
  const farmName = farm?.characterData?.farmName || '나의 농장';
  // 실제 DB farm_size 사용 (farm_size=4 → 2x2, farm_size=9 → 3x3)
  const dbFarmSize = farm?.farmSize || 4;
  // DB farm_size를 NxN 형태로 변환 (4→2, 9→3, 16→4, 25→5)
  const farmSize = Math.sqrt(dbFarmSize);

  // 로딩 상태
  if (isLoading) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center gap-4 bg-green-800">
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
      <div className="min-h-screen flex flex-col items-center justify-center gap-4 p-4 bg-green-800">
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
      <div className="min-h-screen flex flex-col items-center justify-center gap-4 bg-green-800">
        <Sprout className="w-12 h-12 text-white animate-bounce" />
        <p className="text-white font-bold">리다이렉트 중...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen w-full relative overflow-hidden bg-green-800">
      {/* Phaser 게임 캔버스 */}
      <div className="absolute inset-0">
        <FarmGame
          farmSlots={farmSlots}
          farmSize={farmSize}
          gold={gold}
          items={items}
          inventory={inventory}
          selectedSeed={selectedSeed}
          onPlant={handlePlant}
          onHarvest={handleHarvest}
          onNotify={handleNotify}
        />
      </div>

      {/* 상단 UI 오버레이 */}
      <div className="absolute top-0 left-0 right-0 z-40 p-4 pointer-events-none">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          {/* 뒤로가기 */}
          <Link href="/" className="pointer-events-auto">
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
            className="px-6 py-2 rounded-xl pointer-events-none"
            style={{
              background: 'linear-gradient(to bottom, #5D4037 0%, #4E342E 100%)',
              border: '4px solid #3E2723',
              boxShadow: '0 4px 8px rgba(0,0,0,0.3)',
            }}
          >
            <h1 className="text-amber-200 font-bold text-lg">{farmName}</h1>
            <p className="text-amber-400 text-sm text-center">Lv.{farmLevel}</p>
          </div>

          {/* 확장 & 상점 버튼 */}
          <div className="flex items-center gap-2 pointer-events-auto">
            <Button
              onClick={() => setShowExpand(true)}
              className="bg-amber-600 hover:bg-amber-500 border-4 border-amber-800 shadow-[3px_3px_0_0_#78350f] text-white font-bold"
            >
              <Expand className="w-4 h-4 mr-1" />
              확장
            </Button>
            <Button
              onClick={() => setShowShop(true)}
              className="bg-green-600 hover:bg-green-500 border-4 border-green-800 shadow-[3px_3px_0_0_#166534] text-white font-bold"
            >
              <ShoppingBag className="w-4 h-4 mr-1" />
              상점
            </Button>
          </div>
        </div>
      </div>

      {/* 조작 가이드 */}
      <ControlsGuide />

      {/* 알림 메시지 */}
      <AnimatePresence>
        {notification && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className={cn(
              'fixed top-20 left-1/2 -translate-x-1/2 z-50 px-6 py-3 rounded-xl font-bold text-lg',
              notification.type === 'success'
                ? 'bg-green-600 text-white'
                : 'bg-red-600 text-white'
            )}
            style={{
              boxShadow: '0 4px 20px rgba(0,0,0,0.3)',
            }}
          >
            {notification.message}
          </motion.div>
        )}
      </AnimatePresence>

      {/* 선택된 씨앗 표시 */}
      <div className="fixed top-20 right-4 z-40 pointer-events-none">
        <div
          className="px-4 py-2 rounded-lg"
          style={{
            background: 'rgba(0,0,0,0.7)',
            backdropFilter: 'blur(4px)',
          }}
        >
          <p className="text-amber-200 text-sm">
            선택: {CROP_INFO[selectedSeed].emoji} {CROP_INFO[selectedSeed].name}
          </p>
          <p className="text-amber-400 text-xs">
            보유: {getSeedCount(inventory, selectedSeed)}개
          </p>
        </div>
      </div>

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

      {/* 농장 확장 모달 */}
      <AnimatePresence>
        {showExpand && (
          <ExpandModal
            isOpen={showExpand}
            onClose={() => setShowExpand(false)}
            gold={gold}
            currentSize={dbFarmSize}
            onExpand={handleExpand}
          />
        )}
      </AnimatePresence>
    </div>
  );
}
