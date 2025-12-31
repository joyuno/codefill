'use client';

/**
 * FarmGame - Phaser 게임 React 래퍼 컴포넌트
 * 스타듀밸리 스타일 농장 게임
 * 고정 크기 960x640 (30x20 타일)
 *
 * 통합 배치 시스템 리팩토링 - 레거시 Props 제거됨
 */

import { useEffect, useRef, useState } from 'react';
import Phaser from 'phaser';
import { FarmScene } from './scenes/FarmScene';
import type { PlacementChanges } from './scenes/UnifiedPlacementManager';
import type { InventoryItem, PlacedItem, ItemMetadata } from '@/lib/api/farm';

// 외부에서 접근 가능한 메서드
export interface FarmGameHandle {
  hasPlacementChanges: () => boolean;
  getPlacementChanges: () => PlacementChanges;
  revertPlacementChanges: () => void;
  confirmPlacementChanges: () => void;
  placeItemLocally: (itemCode: string, tileX: number, tileY: number, metadata: ItemMetadata) => string | null;
}

// 게임 크기 상수 (config와 동일)
const GAME_WIDTH = 960;
const GAME_HEIGHT = 640;

interface FarmGameProps {
  farmSize: number;
  gold: number;
  inventory: InventoryItem[];
  selectedSeed: string | null;
  onNotify: (message: string, type: 'success' | 'error') => void;
  // 배치 시스템 상태
  placementMode: boolean;
  selectedPlacementItem?: string | null;
  // 통합 배치 시스템
  placedItems: PlacedItem[];
  // 로컬 배치 콜백 (API 호출 없이 프론트에서 처리, 모드 전환 시 저장)
  onPlaceItemLocally: (itemCode: string, tileX: number, tileY: number) => string | null;
  onMoveItem: (itemId: string, tileX: number, tileY: number) => Promise<void>;
  onRemoveItem: (itemId: string) => Promise<void>;
  onPlantOnPlot: (plotId: string, cropCode: string) => Promise<void>;
  onHarvestFromPlot: (plotId: string) => Promise<{ gold: number; xp: number } | null>;
  // 콜백으로 핸들 전달 (dynamic import 호환용)
  onReady?: (handle: FarmGameHandle) => void;
}

export function FarmGame({
  farmSize,
  gold,
  inventory,
  selectedSeed,
  onNotify,
  placementMode,
  selectedPlacementItem,
  placedItems,
  onPlaceItemLocally,
  onMoveItem,
  onRemoveItem,
  onPlantOnPlot,
  onHarvestFromPlot,
  onReady,
}: FarmGameProps) {
  const gameContainerRef = useRef<HTMLDivElement>(null);
  const gameRef = useRef<Phaser.Game | null>(null);
  const sceneRef = useRef<FarmScene | null>(null);
  const [isLoaded, setIsLoaded] = useState(false);

  // 게임 초기화
  useEffect(() => {
    if (!gameContainerRef.current || gameRef.current) return;

    const container = gameContainerRef.current;

    const config: Phaser.Types.Core.GameConfig = {
      type: Phaser.AUTO,
      parent: container,
      width: GAME_WIDTH,
      height: GAME_HEIGHT,
      backgroundColor: '#3d8b3d',
      pixelArt: true,
      scene: FarmScene,
      scale: {
        mode: Phaser.Scale.FIT,
        autoCenter: Phaser.Scale.CENTER_BOTH,
      },
      input: {
        keyboard: true,
        mouse: true,
        touch: true,
      },
    };

    const game = new Phaser.Game(config);
    gameRef.current = game;

    // 씬 데이터 전달
    game.events.once('ready', () => {
      const scene = game.scene.getScene('FarmScene') as FarmScene;
      if (scene) {
        sceneRef.current = scene;
        // 씬 시작 시 데이터 전달
        scene.scene.restart({
          gold,
          farmSize,
          inventory,
          onNotify,
          selectedSeed,
          placementMode,
          deleteMode: false, // 우클릭 삭제로 변경됨
          selectedPlacementItem,
          placedItems,
          onPlaceItemLocally, // 로컬 배치 (API 호출 없음)
          onMoveItem,
          onRemoveItem,
          onPlantOnPlot,
          onHarvestFromPlot,
        });

        // 핸들 생성 및 콜백 호출
        const handle: FarmGameHandle = {
          hasPlacementChanges: () => sceneRef.current?.hasPlacementChanges() ?? false,
          getPlacementChanges: () => sceneRef.current?.getPlacementChanges() ?? { moved: [], deleted: [], created: [] },
          revertPlacementChanges: () => sceneRef.current?.revertPlacementChanges(),
          confirmPlacementChanges: () => sceneRef.current?.confirmPlacementChanges(),
          placeItemLocally: (itemCode, tileX, tileY, metadata) =>
            sceneRef.current?.placeItemLocally(itemCode, tileX, tileY, metadata) ?? null,
        };
        onReady?.(handle);
      }
      setIsLoaded(true);
    });

    return () => {
      if (gameRef.current) {
        gameRef.current.destroy(true);
        gameRef.current = null;
        sceneRef.current = null;
      }
    };
  }, []);

  // 농장 데이터 변경 시 씬 업데이트
  useEffect(() => {
    if (sceneRef.current && isLoaded) {
      sceneRef.current.updateFarmData(selectedSeed, inventory);
    }
  }, [selectedSeed, inventory, isLoaded]);

  // 배치 모드 변경 시 씬 업데이트
  useEffect(() => {
    if (sceneRef.current && isLoaded) {
      sceneRef.current.updatePlacementMode(placementMode, false);
    }
  }, [placementMode, isLoaded]);

  // 배치 아이템 변경 시 씬 업데이트
  useEffect(() => {
    if (sceneRef.current && isLoaded && placedItems) {
      sceneRef.current.updatePlacedItems(placedItems);
    }
  }, [placedItems, isLoaded]);

  // 선택된 배치 아이템 변경 시 씬 업데이트
  useEffect(() => {
    if (sceneRef.current && isLoaded) {
      sceneRef.current.updateSelectedPlacementItem(selectedPlacementItem || null);
    }
  }, [selectedPlacementItem, isLoaded]);

  return (
    <div
      ref={gameContainerRef}
      className="w-full h-full"
      style={{
        imageRendering: 'pixelated',
      }}
    />
  );
}

export default FarmGame;
