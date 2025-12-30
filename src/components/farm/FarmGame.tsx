'use client';

/**
 * FarmGame - Phaser 게임 React 래퍼 컴포넌트
 * 스타듀밸리 스타일 농장 게임
 * 고정 크기 960x640 (30x20 타일)
 */

import { useEffect, useRef, useState } from 'react';
import Phaser from 'phaser';
import { FarmScene } from './scenes/FarmScene';
import type { FarmSlot, FarmItem, InventoryItem } from '@/lib/api/farm';

// 게임 크기 상수 (config와 동일)
const GAME_WIDTH = 960;
const GAME_HEIGHT = 640;

interface FarmGameProps {
  farmSlots: FarmSlot[];
  farmSize: number;
  gold: number;
  items: FarmItem[];
  inventory: InventoryItem[];
  selectedSeed: string;
  onPlant: (slot: number, cropCode: string) => Promise<void>;
  onHarvest: (slot: number) => Promise<void>;
  onNotify: (message: string, type: 'success' | 'error') => void;
}

export function FarmGame({
  farmSlots,
  farmSize,
  gold,
  items,
  inventory,
  selectedSeed,
  onPlant,
  onHarvest,
  onNotify,
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
        mode: Phaser.Scale.FIT,  // 비율 유지하며 맞춤
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
          farmSlots: farmSlots.map(slot => {
            // 작물별 성장 시간 찾기
            const cropItem = slot.cropCode
              ? items.find(item => item.code === slot.cropCode)
              : null;
            return {
              slot: slot.slot,
              cropCode: slot.cropCode,
              plantedAt: slot.plantedAt,
              stage: slot.stage,
              growTimeSeconds: cropItem?.growTimeSeconds,
            };
          }),
          inventory,
          onPlant,
          onHarvest,
          onNotify,
          selectedSeed,
        });
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
      sceneRef.current.updateFarmData(
        farmSlots.map(slot => {
          // 작물별 성장 시간 찾기
          const cropItem = slot.cropCode
            ? items.find(item => item.code === slot.cropCode)
            : null;
          return {
            slot: slot.slot,
            cropCode: slot.cropCode,
            plantedAt: slot.plantedAt,
            stage: slot.stage,
            growTimeSeconds: cropItem?.growTimeSeconds,
          };
        }),
        selectedSeed,
        inventory
      );
    }
  }, [farmSlots, selectedSeed, inventory, items, isLoaded]);

  // 농장 크기 변경 시 씬 업데이트
  useEffect(() => {
    if (sceneRef.current && isLoaded) {
      sceneRef.current.updateFarmSize(farmSize);
    }
  }, [farmSize, isLoaded]);

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
