'use client';

/**
 * FarmGame - Phaser 게임 React 래퍼 컴포넌트
 * 스타듀밸리 스타일 농장 게임
 * 고정 크기 960x640 (30x20 타일)
 *
 * 통합 배치 시스템 리팩토링 - 레거시 Props 제거됨
 */

import { useEffect, useRef, useState } from 'react';
import * as Phaser from 'phaser';
import { FarmScene } from './scenes/FarmScene';
import type { PlacementChanges } from './scenes/UnifiedPlacementManager';
import type { InteractionType } from './scenes/InteractionSystem';
import type { InventoryItem, PlacedItem, ItemMetadata, FarmSlot, CharacterData } from '@/lib/api/farm';

// 상호작용 상태 타입 (React에서 사용)
export interface InteractionState {
  type: InteractionType;
  cropCode: string | null;
  stage: number;
}

// 외부에서 접근 가능한 메서드
export interface FarmGameHandle {
  hasPlacementChanges: () => boolean;
  getPlacementChanges: () => PlacementChanges;
  revertPlacementChanges: () => void;
  confirmPlacementChanges: () => void;
  placeItemLocally: (itemCode: string, tileX: number, tileY: number, metadata: ItemMetadata) => Promise<string | null>;
}

// 게임 크기: 브라우저 전체 화면 사용
const getGameWidth = () => typeof window !== 'undefined' ? window.innerWidth : 960;
const getGameHeight = () => typeof window !== 'undefined' ? window.innerHeight : 640;

interface FarmGameProps {
  farmSize: number;
  mapLevel?: number;  // 맵 확장 레벨 (1-5, 기본값 1)
  gold: number;
  inventory: InventoryItem[];
  selectedSeed: string | null;
  onNotify: (message: string, type: 'success' | 'error') => void;
  // 캐릭터 데이터 (레이어 기반 렌더링용)
  characterData?: CharacterData | null;
  // 배치 시스템 상태
  placementMode: boolean;
  selectedPlacementItem?: string | null;
  // 통합 배치 시스템
  placedItems: PlacedItem[];
  // 로컬 배치 콜백 (API 호출 없이 프론트에서 처리, 모드 전환 시 저장)
  onPlaceItemLocally: (itemCode: string, tileX: number, tileY: number) => Promise<string | null>;
  onMoveItem: (itemId: string, tileX: number, tileY: number) => Promise<void>;
  onRemoveItem: (itemId: string) => Promise<void>;
  // 슬롯 기반 밭 시스템 (신규)
  farmSlots: FarmSlot[];
  onPlantOnSlot: (slot: number, cropCode: string) => Promise<FarmSlot | null>;
  onHarvestFromSlot: (slot: number) => Promise<{ gold: number; xp: number; slot: FarmSlot } | null>;
  // 콜백으로 핸들 전달 (dynamic import 호환용)
  onReady?: (handle: FarmGameHandle) => void;
  // 상호작용 상태 변경 콜백 (액션 프롬프트 UI용)
  onInteractionChange?: (interaction: InteractionState | null) => void;
}

export function FarmGame({
  farmSize,
  mapLevel = 1,
  gold,
  inventory,
  selectedSeed,
  onNotify,
  characterData,
  placementMode,
  selectedPlacementItem,
  placedItems,
  onPlaceItemLocally,
  onMoveItem,
  onRemoveItem,
  farmSlots,
  onPlantOnSlot,
  onHarvestFromSlot,
  onReady,
  onInteractionChange,
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
      width: getGameWidth(),
      height: getGameHeight(),
      backgroundColor: '#3d8b3d',
      pixelArt: true,
      scene: FarmScene,
      scale: {
        mode: Phaser.Scale.RESIZE,
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
          mapLevel,  // 맵 확장 레벨
          inventory,
          onNotify,
          selectedSeed,
          // 캐릭터 데이터 (레이어 기반 렌더링용)
          characterData,
          placementMode,
          deleteMode: false, // 우클릭 삭제로 변경됨
          selectedPlacementItem,
          placedItems,
          onPlaceItemLocally, // 로컬 배치 (API 호출 없음)
          onMoveItem,
          onRemoveItem,
          // 슬롯 기반 밭 시스템
          farmSlots,
          onPlantOnSlot,
          onHarvestFromSlot,
          // 상호작용 상태 변경 콜백
          onInteractionChange,
        });

        // 핸들 생성 및 콜백 호출
        const handle: FarmGameHandle = {
          hasPlacementChanges: () => sceneRef.current?.hasPlacementChanges() ?? false,
          getPlacementChanges: () => sceneRef.current?.getPlacementChanges() ?? { moved: [], deleted: [], created: [] },
          revertPlacementChanges: () => sceneRef.current?.revertPlacementChanges(),
          confirmPlacementChanges: () => sceneRef.current?.confirmPlacementChanges(),
          placeItemLocally: async (itemCode, tileX, tileY, metadata) =>
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

  // 밭 슬롯 변경 시 씬 업데이트
  useEffect(() => {
    if (sceneRef.current && isLoaded && farmSlots) {
      sceneRef.current.updateFarmSlots(farmSize, farmSlots);
    }
  }, [farmSlots, farmSize, isLoaded]);

  // 맵 레벨 변경 시 씬 재시작 (맵 확장)
  const prevMapLevelRef = useRef(mapLevel);
  useEffect(() => {
    if (sceneRef.current && isLoaded && mapLevel !== prevMapLevelRef.current) {
      prevMapLevelRef.current = mapLevel;
      // 씬 재시작으로 맵 크기 업데이트
      sceneRef.current.scene.restart({
        gold,
        farmSize,
        mapLevel,
        inventory,
        onNotify,
        selectedSeed,
        characterData,
        placementMode,
        deleteMode: false,
        selectedPlacementItem,
        placedItems,
        onPlaceItemLocally,
        onMoveItem,
        onRemoveItem,
        farmSlots,
        onPlantOnSlot,
        onHarvestFromSlot,
        onInteractionChange,
      });
    }
  }, [mapLevel, isLoaded, gold, farmSize, inventory, onNotify, selectedSeed, characterData, placementMode, selectedPlacementItem, placedItems, onPlaceItemLocally, onMoveItem, onRemoveItem, farmSlots, onPlantOnSlot, onHarvestFromSlot, onInteractionChange]);

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
