'use client';

/**
 * Farm Page - Phaser.js 기반 스타듀밸리 스타일 농장 게임
 * 통합 배치 시스템 리팩토링 - 레거시 코드 제거됨
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import dynamic from 'next/dynamic';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { useFarm, getSeedCount } from '@/hooks/useFarm';
import { useToast } from '@/hooks/useToast';
import {
  Loader2,
  AlertCircle,
  Sprout,
} from 'lucide-react';

// UI 컴포넌트
import { ExpandModal, CROP_INFO, type CropVariety } from '@/components/farm/ui';
import { UnifiedShopModal } from '@/components/farm/ui/UnifiedShopModal';
import { ToastNotification } from '@/components/farm/ui/ToastNotification';
import { GameTopBar } from '@/components/farm/ui/GameTopBar';
import { UnifiedHotbar, type HotbarMode } from '@/components/farm/ui/UnifiedHotbar';
import type { PlacedItem } from '@/lib/api/farm';
import type { FarmGameHandle } from '@/components/farm/FarmGame';

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
    buySeed,
    expand,
    // 통합 배치 시스템
    placedItems,
    unifiedShopItems,
    loadUnifiedShop,
    buyUnifiedItem,
    placeItem,
    moveItem,
    removeItem,
    plantOnPlot,
    harvestFromPlot,
  } = useFarm();

  // 토스트 알림
  const { toasts, addToast, removeToast } = useToast();

  // UI 상태
  const [showUnifiedShop, setShowUnifiedShop] = useState(false);
  const [showExpand, setShowExpand] = useState(false);
  const [isPurchasing, setIsPurchasing] = useState(false);
  const [isSavingPlacement, setIsSavingPlacement] = useState(false);

  // 통합 핫바 상태
  const [hotbarMode, setHotbarMode] = useState<HotbarMode>('seed');
  const [selectedItem, setSelectedItem] = useState<string | null>(null);

  // FarmGame 핸들 (배치 저장/취소용) - dynamic import라서 콜백으로 받음
  const [farmGameHandle, setFarmGameHandle] = useState<FarmGameHandle | null>(null);

  // FarmGame ready 콜백
  const handleFarmGameReady = useCallback((handle: FarmGameHandle) => {
    setFarmGameHandle(handle);
  }, []);

  // 캐릭터 미생성 시 리다이렉트
  useEffect(() => {
    if (!isLoading && farm && !farm.characterCreated) {
      router.push('/');
    }
  }, [isLoading, farm, router]);

  // 파생 상태 - 레거시 호환성
  const placementMode = hotbarMode === 'placement';
  const selectedSeed = hotbarMode === 'seed' && selectedItem
    ? selectedItem.replace('seed_', '') as CropVariety
    : null;
  const selectedPlacementItem = hotbarMode === 'placement' ? selectedItem : null;

  // 농장 확장
  const handleExpand = useCallback(async (targetSize: number) => {
    try {
      await expand(targetSize);
      addToast('농장이 확장되었습니다!', 'success');
    } catch (err) {
      console.error('Expand failed:', err);
      addToast(err instanceof Error ? err.message : '확장 실패', 'error');
      throw err;
    }
  }, [expand, addToast]);

  // 통합 상점 열기
  const handleOpenUnifiedShop = useCallback(async () => {
    setShowUnifiedShop(true);
    try {
      await loadUnifiedShop();
    } catch (err) {
      console.error('Failed to load unified shop:', err);
    }
  }, [loadUnifiedShop]);

  // 통합 상점에서 아이템 구매
  const handleBuyUnifiedItem = useCallback(async (itemCode: string) => {
    setIsPurchasing(true);
    try {
      await buyUnifiedItem(itemCode);
      addToast('구매 완료! 인벤토리에 추가되었습니다.', 'success');
    } catch (err) {
      console.error('Unified purchase failed:', err);
      addToast(err instanceof Error ? err.message : '구매 실패', 'error');
    } finally {
      setIsPurchasing(false);
    }
  }, [buyUnifiedItem, addToast]);

  // 구매 후 바로 배치 모드로 전환
  const handlePurchaseAndPlace = useCallback(async (itemCode: string) => {
    setIsPurchasing(true);
    try {
      await buyUnifiedItem(itemCode);
      // 구매 성공 시: 모달 닫기 → 배치 모드 → 아이템 선택
      setShowUnifiedShop(false);
      setHotbarMode('placement');
      setSelectedItem(itemCode);
      addToast('배치 모드로 전환! 맵에서 클릭하여 배치하세요.', 'success');
    } catch (err) {
      console.error('Purchase and place failed:', err);
      addToast(err instanceof Error ? err.message : '구매 실패', 'error');
    } finally {
      setIsPurchasing(false);
    }
  }, [buyUnifiedItem, addToast]);

  // 아이템 로컬 배치 (API 호출 없음, 모드 전환 시 저장)
  const handlePlaceItemLocally = useCallback((itemCode: string, tileX: number, tileY: number): string | null => {
    if (!farmGameHandle) return null;

    // 상점 데이터에서 아이템 메타데이터 가져오기
    const shopItem = unifiedShopItems.find(item => item.code === itemCode);
    if (!shopItem) {
      console.error('Item not found in shop:', itemCode);
      return null;
    }

    // 핸들을 통해 로컬 배치 수행 (상점 아이템의 메타데이터 사용)
    const tempId = farmGameHandle.placeItemLocally(itemCode, tileX, tileY, shopItem.metadata);
    return tempId;
  }, [farmGameHandle, unifiedShopItems]);

  // Phaser에서 알림 표시
  const handleNotify = useCallback((message: string, type: 'success' | 'error') => {
    addToast(message, type);
  }, [addToast]);

  // 배치 변경 저장 (내부 함수)
  const savePlacementChanges = useCallback(async (): Promise<boolean> => {
    if (!farmGameHandle) return true;

    const changes = farmGameHandle.getPlacementChanges();

    // 변경 사항이 없으면 스킵
    if (changes.moved.length === 0 && changes.deleted.length === 0 && changes.created.length === 0) {
      farmGameHandle.confirmPlacementChanges();
      return true;
    }

    setIsSavingPlacement(true);
    try {
      // 새로 생성된 아이템들 저장
      for (const item of changes.created) {
        await placeItem(item.itemCode, item.tileX, item.tileY);
      }

      // 이동된 아이템들 저장
      for (const item of changes.moved) {
        await moveItem(item.id, item.tileX, item.tileY);
      }

      // 삭제된 아이템들 저장
      for (const itemId of changes.deleted) {
        await removeItem(itemId);
      }

      // 변경 확정
      farmGameHandle.confirmPlacementChanges();
      addToast('배치가 저장되었습니다!', 'success');
      return true;
    } catch (err) {
      console.error('Save placement failed:', err);
      addToast(err instanceof Error ? err.message : '저장 실패', 'error');
      return false;
    } finally {
      setIsSavingPlacement(false);
    }
  }, [farmGameHandle, placeItem, moveItem, removeItem, addToast]);

  // 핫바 모드 변경 (배치 모드에서 나갈 때 자동 저장)
  const handleModeChange = useCallback(async (mode: HotbarMode) => {
    // 배치 모드에서 나가는 경우 자동 저장
    if (hotbarMode === 'placement' && mode === 'seed') {
      const saved = await savePlacementChanges();
      if (!saved) {
        // 저장 실패 시 모드 유지
        return;
      }
    }

    setHotbarMode(mode);
    setSelectedItem(null);

    // 배치 모드 진입 시 상점 데이터 로드
    if (mode === 'placement') {
      try {
        await loadUnifiedShop();
      } catch (err) {
        console.error('Failed to load unified shop:', err);
      }
    }
  }, [hotbarMode, savePlacementChanges, loadUnifiedShop]);

  // 배치 변경 취소
  const handleCancelPlacement = useCallback(() => {
    if (!farmGameHandle) return;

    farmGameHandle.revertPlacementChanges();
    addToast('변경 사항이 취소되었습니다', 'success');
  }, [farmGameHandle, addToast]);

  // 계산된 값들
  const gold = farm?.gold || 0;
  const dbFarmSize = farm?.farmSize || 4;
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
          onReady={handleFarmGameReady}
          farmSize={farmSize}
          gold={gold}
          inventory={inventory}
          selectedSeed={selectedSeed}
          onNotify={handleNotify}
          placementMode={placementMode}
          selectedPlacementItem={selectedPlacementItem}
          placedItems={placedItems}
          onPlaceItemLocally={handlePlaceItemLocally}
          onMoveItem={moveItem}
          onRemoveItem={removeItem}
          onPlantOnPlot={plantOnPlot}
          onHarvestFromPlot={harvestFromPlot}
        />
      </div>

      {/* 상단 UI - 미니멀 HUD */}
      <GameTopBar
        gold={gold}
        onOpenShop={handleOpenUnifiedShop}
        onOpenExpand={() => setShowExpand(true)}
      />

      {/* 토스트 알림 (우하단) */}
      <ToastNotification toasts={toasts} onDismiss={removeToast} />

      {/* 통합 핫바 */}
      <UnifiedHotbar
        inventory={inventory}
        placeableItems={unifiedShopItems}
        mode={hotbarMode}
        onModeChange={handleModeChange}
        selectedItem={selectedItem}
        onSelectItem={setSelectedItem}
        onCancelPlacement={handleCancelPlacement}
        isSaving={isSavingPlacement}
      />

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

      {/* 통합 상점 모달 */}
      <AnimatePresence>
        {showUnifiedShop && (
          <UnifiedShopModal
            isOpen={showUnifiedShop}
            onClose={() => setShowUnifiedShop(false)}
            gold={gold}
            items={unifiedShopItems}
            onPurchase={handleBuyUnifiedItem}
            onPurchaseAndPlace={handlePurchaseAndPlace}
            isLoading={isPurchasing}
          />
        )}
      </AnimatePresence>

    </div>
  );
}
