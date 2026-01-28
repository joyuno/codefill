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
import { updateFarmCache, markFarmVisited } from '@/components/dashboard/SidebarProfile';
import {
  Loader2,
  AlertCircle,
  Sprout,
} from 'lucide-react';

// UI 컴포넌트
import {
  ExpandModal,
  MapExpandModal,
  CROP_INFO,
  type CropVariety,
  ActionPrompt,
  SeedHotbar,
  PlacementModeUI,
} from '@/components/farm/ui';
import { UnifiedShopModal } from '@/components/farm/ui/UnifiedShopModal';
import { ToastNotification } from '@/components/farm/ui/ToastNotification';
import { GameTopBar } from '@/components/farm/ui/GameTopBar';
import type { PlacedItem } from '@/lib/api/farm';
import type { FarmGameHandle, InteractionState } from '@/components/farm/FarmGame';

// Phaser 게임 컴포넌트 (SSR 비활성화)
const FarmGame = dynamic(() => import('@/components/farm/FarmGame'), {
  ssr: false,
  loading: () => (
    <div
      className="w-full h-full flex flex-col items-center justify-center"
      style={{
        backgroundImage: 'url(/farm/farm_loading_bg.png)',
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        imageRendering: 'pixelated',
      }}
    >
      <div className="bg-black/50 backdrop-blur-sm rounded-xl px-10 py-6 flex flex-col items-center gap-4">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
        >
          <Loader2 className="w-10 h-10 text-yellow-300" />
        </motion.div>
        <p className="text-white font-bold text-lg" style={{ textShadow: '0 1px 3px rgba(0,0,0,0.8)' }}>
          게임 로딩 중...
        </p>
      </div>
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
    getMapExpansionCosts,
    expandMap,
    // 통합 배치 시스템
    placedItems,
    unifiedShopItems,
    loadUnifiedShop,
    buyUnifiedItem,
    placeItem,
    moveItem,
    removeItem,
    // 슬롯 기반 밭 시스템
    plantOnSlot,
    harvestFromSlot,
  } = useFarm();

  // 토스트 알림
  const { toasts, addToast, removeToast } = useToast();

  // UI 상태
  const [showUnifiedShop, setShowUnifiedShop] = useState(false);
  const [showExpand, setShowExpand] = useState(false);
  const [showMapExpand, setShowMapExpand] = useState(false);
  const [isPurchasing, setIsPurchasing] = useState(false);
  const [isSavingPlacement, setIsSavingPlacement] = useState(false);

  // UI 모드 상태 (분리된 모드)
  const [isPlacementMode, setIsPlacementMode] = useState(false);
  const [selectedSeedCode, setSelectedSeedCode] = useState<string | null>(null);
  const [selectedPlacementCode, setSelectedPlacementCode] = useState<string | null>(null);
  const [hasPlacementChanges, setHasPlacementChanges] = useState(false);

  // 상호작용 상태 (Phaser에서 전달받음)
  const [interactionState, setInteractionState] = useState<InteractionState | null>(null);

  // FarmGame 핸들 (배치 저장/취소용) - dynamic import라서 콜백으로 받음
  const [farmGameHandle, setFarmGameHandle] = useState<FarmGameHandle | null>(null);

  // 클로저 문제 방지를 위한 refs
  // Phaser 씬에 전달된 콜백이 항상 최신 상태를 참조하도록 함
  const unifiedShopItemsRef = useRef(unifiedShopItems);
  const farmGameHandleRef = useRef(farmGameHandle);

  useEffect(() => {
    unifiedShopItemsRef.current = unifiedShopItems;
  }, [unifiedShopItems]);

  useEffect(() => {
    farmGameHandleRef.current = farmGameHandle;
  }, [farmGameHandle]);

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

  // 농장 데이터 캐시 업데이트 (farm 변경 시)
  useEffect(() => {
    if (farm) {
      updateFarmCache(farm);
    }
  }, [farm]);

  // 페이지 떠날 때 방문 플래그 설정
  useEffect(() => {
    return () => {
      // 다음에 SidebarProfile이 로드될 때 백그라운드 갱신하도록 플래그 설정
      markFarmVisited();
    };
  }, []);

  // 배치 모드에서 Phaser 상태와 동기화 (폴링 방식)
  useEffect(() => {
    if (!isPlacementMode || !farmGameHandle) return;

    const interval = setInterval(() => {
      const phaserHasChanges = farmGameHandle.hasPlacementChanges();
      setHasPlacementChanges(prev => {
        if (prev !== phaserHasChanges) {
          return phaserHasChanges;
        }
        return prev;
      });
    }, 200); // 200ms 주기로 체크

    return () => clearInterval(interval);
  }, [isPlacementMode, farmGameHandle]);

  // 파생 상태 - Phaser 연동용
  const selectedSeed = !isPlacementMode && selectedSeedCode
    ? selectedSeedCode.replace('seed_', '') as CropVariety
    : null;
  const selectedPlacementItem = isPlacementMode ? selectedPlacementCode : null;

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

  // 맵 확장
  const handleMapExpand = useCallback(async (targetLevel: number) => {
    try {
      await expandMap(targetLevel);
      addToast('맵이 확장되었습니다!', 'success');
    } catch (err) {
      console.error('Map expand failed:', err);
      addToast(err instanceof Error ? err.message : '확장 실패', 'error');
      throw err;
    }
  }, [expandMap, addToast]);

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
      setIsPlacementMode(true);
      setSelectedPlacementCode(itemCode);
      addToast('배치 모드로 전환! 맵에서 클릭하여 배치하세요.', 'success');
    } catch (err) {
      console.error('Purchase and place failed:', err);
      addToast(err instanceof Error ? err.message : '구매 실패', 'error');
    } finally {
      setIsPurchasing(false);
    }
  }, [buyUnifiedItem, addToast]);

  // 아이템 로컬 배치 (API 호출 없음, 모드 전환 시 저장)
  // ref를 사용하여 클로저 문제 방지 - Phaser 씬에 전달된 콜백이 항상 최신 상태 참조
  const handlePlaceItemLocally = useCallback(async (itemCode: string, tileX: number, tileY: number): Promise<string | null> => {
    try {
      // ref에서 최신 핸들 가져오기 (클로저 문제 방지)
      const handle = farmGameHandleRef.current;
      if (!handle) {
        return null;
      }

      // ref에서 최신 상점 데이터 가져오기 (클로저 문제 방지)
      const shopItems = unifiedShopItemsRef.current || [];
      const shopItem = shopItems.find(item => item.code === itemCode);
      if (!shopItem) {
        return null;
      }

      // 핸들을 통해 로컬 배치 수행 (상점 아이템의 메타데이터 사용)
      // await로 에셋 로딩 완료 후 tempId 반환
      const tempId = await handle.placeItemLocally(itemCode, tileX, tileY, shopItem.metadata);

      // 배치 성공 시 변경 사항 추적
      if (tempId) {
        setHasPlacementChanges(true);
      }

      return tempId;
    } catch {
      return null;
    }
  }, []);

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
      // 병렬 처리를 위한 Promise 배열 생성
      const promises: Promise<unknown>[] = [];

      // 새로 생성된 아이템들 (병렬)
      for (const item of changes.created) {
        promises.push(placeItem(item.itemCode, item.tileX, item.tileY));
      }

      // 이동된 아이템들 (병렬)
      for (const item of changes.moved) {
        promises.push(moveItem(item.id, item.tileX, item.tileY));
      }

      // 삭제된 아이템들 (병렬)
      for (const itemId of changes.deleted) {
        promises.push(removeItem(itemId));
      }

      // 모든 변경 사항 병렬 실행
      await Promise.all(promises);

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

  // 배치 모드 진입 (E키)
  const handleEnterPlacementMode = useCallback(async () => {
    setIsPlacementMode(true);
    setSelectedSeedCode(null);
    setHasPlacementChanges(false);

    // 배치 모드 진입 시 상점 데이터 로드
    try {
      await loadUnifiedShop();
    } catch (err) {
      console.error('Failed to load unified shop:', err);
    }
  }, [loadUnifiedShop]);

  // 배치 모드 종료 (ESC키) - 저장하지 않고 변경사항 취소
  const handleExitPlacementMode = useCallback(() => {
    // 변경 사항이 있으면 되돌리기
    if (farmGameHandle) {
      try {
        farmGameHandle.revertPlacementChanges();
      } catch {
        // Silent fail
      }
    }

    setIsPlacementMode(false);
    setSelectedPlacementCode(null);
    setHasPlacementChanges(false);
  }, [farmGameHandle]);

  // 배치 저장 (S키 또는 저장 버튼)
  const handleSavePlacement = useCallback(async () => {
    if (isSavingPlacement) {
      return;
    }

    const saved = await savePlacementChanges();
    if (saved) {
      setHasPlacementChanges(false);
    }
  }, [savePlacementChanges, isSavingPlacement]);

  // 배치 변경 취소 (취소 버튼)
  const handleCancelPlacement = useCallback(() => {
    if (!farmGameHandle) {
      addToast('아직 준비 중입니다. 잠시 후 다시 시도하세요.', 'error');
      return;
    }

    try {
      farmGameHandle.revertPlacementChanges();
      setHasPlacementChanges(false);
      addToast('변경 사항이 취소되었습니다', 'success');
    } catch {
      addToast('취소 중 오류가 발생했습니다', 'error');
    }
  }, [farmGameHandle, addToast]);

  // 계산된 값들
  const gold = farm?.gold || 0;
  const dbFarmSize = farm?.farmSize || 1;

  // 로딩 상태
  if (isLoading) {
    return (
      <div
        className="min-h-screen flex flex-col items-center justify-center gap-4"
        style={{
          backgroundImage: 'url(/farm/farm_loading_bg.png)',
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          imageRendering: 'pixelated',
        }}
      >
        <div className="bg-black/50 backdrop-blur-sm rounded-xl px-10 py-6 flex flex-col items-center gap-4">
          <motion.div animate={{ rotate: 360 }} transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}>
            <Loader2 className="w-10 h-10 text-yellow-300" />
          </motion.div>
          <p className="text-white font-bold text-lg" style={{ textShadow: '0 1px 3px rgba(0,0,0,0.8)' }}>
            농장 불러오는 중...
          </p>
        </div>
      </div>
    );
  }

  // 에러 상태
  if (error) {
    return (
      <div
        className="min-h-screen flex flex-col items-center justify-center gap-4 p-4"
        style={{
          backgroundImage: 'url(/farm/farm_loading_bg.png)',
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          imageRendering: 'pixelated',
        }}
      >
        <div className="bg-black/60 backdrop-blur-sm rounded-xl px-10 py-6 flex flex-col items-center gap-4">
          <AlertCircle className="w-12 h-12 text-red-400" />
          <p className="text-white font-bold text-center" style={{ textShadow: '0 1px 3px rgba(0,0,0,0.8)' }}>{error}</p>
          <Button onClick={() => router.push('/')} variant="outline" className="bg-white">
            홈으로 돌아가기
          </Button>
        </div>
      </div>
    );
  }

  // 캐릭터 미생성
  if (!farm?.characterCreated) {
    return (
      <div
        className="min-h-screen flex flex-col items-center justify-center gap-4"
        style={{
          backgroundImage: 'url(/farm/farm_loading_bg.png)',
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          imageRendering: 'pixelated',
        }}
      >
        <div className="bg-black/50 backdrop-blur-sm rounded-xl px-10 py-6 flex flex-col items-center gap-3">
          <Sprout className="w-12 h-12 text-green-300 animate-bounce" />
          <p className="text-white font-bold" style={{ textShadow: '0 1px 3px rgba(0,0,0,0.8)' }}>리다이렉트 중...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen w-full relative overflow-hidden bg-[#3d8b3d]">
      {/* Phaser 게임 캔버스 */}
      <div className="absolute inset-0">
        <FarmGame
          onReady={handleFarmGameReady}
          farmSize={dbFarmSize}
          mapLevel={farm?.mapLevel || 1}
          gold={gold}
          inventory={inventory}
          selectedSeed={selectedSeed}
          onNotify={handleNotify}
          characterData={farm?.characterData}
          placementMode={isPlacementMode}
          selectedPlacementItem={selectedPlacementItem}
          placedItems={placedItems}
          onPlaceItemLocally={handlePlaceItemLocally}
          onMoveItem={moveItem}
          onRemoveItem={removeItem}
          farmSlots={farm?.farmSlots || []}
          onPlantOnSlot={plantOnSlot}
          onHarvestFromSlot={harvestFromSlot}
          onInteractionChange={setInteractionState}
        />
      </div>

      {/* 상단 UI - 미니멀 HUD (배치 모드가 아닐 때만) */}
      {!isPlacementMode && (
        <GameTopBar
          gold={gold}
          onOpenShop={handleOpenUnifiedShop}
          onOpenExpand={() => setShowExpand(true)}
          onOpenMapExpand={() => setShowMapExpand(true)}
        />
      )}

      {/* 토스트 알림 (우하단) */}
      <ToastNotification toasts={toasts} onDismiss={removeToast} />

      {/* 액션 프롬프트 (핫바 위) - 씨앗 모드에서만 표시 */}
      {!isPlacementMode && (
        <ActionPrompt
          interaction={interactionState}
          selectedSeed={selectedSeedCode}
        />
      )}

      {/* 모드별 UI - 조건부 렌더링 */}
      {isPlacementMode ? (
        <PlacementModeUI
          items={unifiedShopItems}
          selectedItem={selectedPlacementCode}
          onSelectItem={setSelectedPlacementCode}
          onExit={handleExitPlacementMode}
          onSave={handleSavePlacement}
          onCancel={handleCancelPlacement}
          isSaving={isSavingPlacement}
          hasChanges={hasPlacementChanges}
        />
      ) : (
        <SeedHotbar
          inventory={inventory}
          selectedSeed={selectedSeedCode}
          onSelectSeed={setSelectedSeedCode}
          onEnterPlacementMode={handleEnterPlacementMode}
        />
      )}

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

      {/* 맵 확장 모달 */}
      <AnimatePresence>
        {showMapExpand && (
          <MapExpandModal
            isOpen={showMapExpand}
            onClose={() => setShowMapExpand(false)}
            gold={gold}
            currentLevel={farm?.mapLevel || 1}
            onExpand={handleMapExpand}
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
