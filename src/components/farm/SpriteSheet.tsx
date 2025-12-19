'use client';

import { useState, useEffect, useMemo } from 'react';
import { cn } from '@/lib/utils';

/**
 * Sprite Sheet Component
 *
 * PNG 스프라이트 시트에서 특정 프레임을 표시합니다.
 *
 * 사용법:
 * <Sprite
 *   src="/sprites/crops/tomato.png"
 *   frameWidth={16}
 *   frameHeight={16}
 *   frame={2}  // 0부터 시작
 *   scale={2}  // 2배 확대
 * />
 */

interface SpriteProps {
  src: string;
  frameWidth: number;
  frameHeight: number;
  frame?: number;
  row?: number;
  scale?: number;
  className?: string;
  alt?: string;
  onClick?: () => void;
}

export function Sprite({
  src,
  frameWidth,
  frameHeight,
  frame = 0,
  row = 0,
  scale = 1,
  className,
  alt = 'sprite',
  onClick,
}: SpriteProps) {
  const width = frameWidth * scale;
  const height = frameHeight * scale;
  const offsetX = frame * frameWidth * scale;
  const offsetY = row * frameHeight * scale;

  return (
    <div
      className={cn('overflow-hidden', onClick && 'cursor-pointer', className)}
      style={{
        width,
        height,
        imageRendering: 'pixelated',
      }}
      onClick={onClick}
      role={onClick ? 'button' : undefined}
      aria-label={alt}
    >
      <div
        style={{
          width: width,
          height: height,
          backgroundImage: `url(${src})`,
          backgroundPosition: `-${offsetX}px -${offsetY}px`,
          backgroundSize: 'auto',
          backgroundRepeat: 'no-repeat',
          transform: `scale(${scale})`,
          transformOrigin: 'top left',
          imageRendering: 'pixelated',
        }}
      />
    </div>
  );
}

/**
 * Animated Sprite Component
 *
 * 애니메이션이 있는 스프라이트를 표시합니다.
 */
interface AnimatedSpriteProps extends Omit<SpriteProps, 'frame'> {
  frames: number[];
  fps?: number;
  loop?: boolean;
  playing?: boolean;
}

export function AnimatedSprite({
  src,
  frameWidth,
  frameHeight,
  frames,
  fps = 8,
  loop = true,
  playing = true,
  row = 0,
  scale = 1,
  className,
  alt = 'animated sprite',
  onClick,
}: AnimatedSpriteProps) {
  const [currentFrameIndex, setCurrentFrameIndex] = useState(0);

  useEffect(() => {
    if (!playing || frames.length <= 1) return;

    const interval = setInterval(() => {
      setCurrentFrameIndex((prev) => {
        const next = prev + 1;
        if (next >= frames.length) {
          return loop ? 0 : prev;
        }
        return next;
      });
    }, 1000 / fps);

    return () => clearInterval(interval);
  }, [playing, frames.length, fps, loop]);

  return (
    <Sprite
      src={src}
      frameWidth={frameWidth}
      frameHeight={frameHeight}
      frame={frames[currentFrameIndex]}
      row={row}
      scale={scale}
      className={className}
      alt={alt}
      onClick={onClick}
    />
  );
}

/**
 * Crop Sprite Component (작물 전용)
 *
 * 작물 성장 단계를 표시합니다.
 * 기본적으로 16x16 스프라이트 시트를 사용합니다.
 */
interface CropSpriteProps {
  crop: string; // 작물 이름 (예: 'tomato', 'wheat')
  stage: number; // 0-4 (5단계)
  scale?: number;
  className?: string;
  onClick?: () => void;
}

// 작물별 스프라이트 시트 매핑
// 실제 PNG 파일 다운로드 후 경로 수정 필요
const CROP_SPRITES: Record<string, string> = {
  tomato: '/sprites/crops/crops.png',
  wheat: '/sprites/crops/crops.png',
  corn: '/sprites/crops/crops.png',
  carrot: '/sprites/crops/crops.png',
  potato: '/sprites/crops/crops.png',
  strawberry: '/sprites/crops/crops.png',
};

const CROP_ROW: Record<string, number> = {
  tomato: 0,
  wheat: 1,
  corn: 2,
  carrot: 3,
  potato: 4,
  strawberry: 5,
};

export function CropSprite({
  crop,
  stage,
  scale = 3,
  className,
  onClick,
}: CropSpriteProps) {
  const src = CROP_SPRITES[crop] || CROP_SPRITES.tomato;
  const row = CROP_ROW[crop] || 0;

  return (
    <Sprite
      src={src}
      frameWidth={16}
      frameHeight={16}
      frame={Math.min(stage, 4)} // 0-4 단계
      row={row}
      scale={scale}
      className={className}
      alt={`${crop} stage ${stage}`}
      onClick={onClick}
    />
  );
}

/**
 * Character Sprite Component (캐릭터 전용)
 *
 * LPC 스타일 캐릭터 스프라이트를 표시합니다.
 * 기본 LPC 캐릭터는 64x64 프레임입니다.
 */
interface CharacterSpriteProps {
  src?: string;
  direction?: 'down' | 'left' | 'right' | 'up';
  animation?: 'idle' | 'walk';
  frame?: number;
  scale?: number;
  className?: string;
}

const DIRECTION_ROW = {
  down: 0,
  left: 1,
  right: 2,
  up: 3,
};

export function CharacterSprite({
  src = '/sprites/characters/farmer.png',
  direction = 'down',
  animation = 'idle',
  frame = 0,
  scale = 1,
  className,
}: CharacterSpriteProps) {
  const row = DIRECTION_ROW[direction] + (animation === 'walk' ? 4 : 0);

  return (
    <Sprite
      src={src}
      frameWidth={64}
      frameHeight={64}
      frame={frame}
      row={row}
      scale={scale}
      className={className}
      alt={`Character ${direction} ${animation}`}
    />
  );
}

/**
 * Building Sprite Component (건물 전용)
 */
interface BuildingSpriteProps {
  type: 'house1' | 'house2' | 'house3' | 'house4' | 'barn' | 'coop';
  scale?: number;
  className?: string;
}

const BUILDING_CONFIG: Record<string, { src: string; width: number; height: number; frame: number }> = {
  house1: { src: '/sprites/buildings/houses.png', width: 48, height: 64, frame: 0 },
  house2: { src: '/sprites/buildings/houses.png', width: 48, height: 64, frame: 1 },
  house3: { src: '/sprites/buildings/houses.png', width: 64, height: 80, frame: 2 },
  house4: { src: '/sprites/buildings/houses.png', width: 80, height: 96, frame: 3 },
  barn: { src: '/sprites/buildings/farm.png', width: 64, height: 64, frame: 0 },
  coop: { src: '/sprites/buildings/farm.png', width: 48, height: 48, frame: 1 },
};

export function BuildingSprite({
  type,
  scale = 2,
  className,
}: BuildingSpriteProps) {
  const config = BUILDING_CONFIG[type] || BUILDING_CONFIG.house1;

  return (
    <Sprite
      src={config.src}
      frameWidth={config.width}
      frameHeight={config.height}
      frame={config.frame}
      scale={scale}
      className={className}
      alt={`Building ${type}`}
    />
  );
}

/**
 * Tile Grid Component
 *
 * 타일 기반 그리드를 렌더링합니다.
 */
interface TileGridProps {
  tiles: string[][]; // 2D 배열의 타일 이름
  tileSize?: number;
  scale?: number;
  className?: string;
}

export function TileGrid({ tiles, tileSize = 16, scale = 2, className }: TileGridProps) {
  const tileMap: Record<string, { row: number; col: number }> = {
    grass: { row: 0, col: 0 },
    dirt: { row: 0, col: 1 },
    water: { row: 1, col: 0 },
    path: { row: 1, col: 1 },
  };

  return (
    <div
      className={cn('grid', className)}
      style={{
        gridTemplateColumns: `repeat(${tiles[0]?.length || 1}, ${tileSize * scale}px)`,
        imageRendering: 'pixelated',
      }}
    >
      {tiles.flat().map((tile, index) => {
        const config = tileMap[tile] || tileMap.grass;
        return (
          <Sprite
            key={index}
            src="/sprites/tiles/terrain.png"
            frameWidth={tileSize}
            frameHeight={tileSize}
            frame={config.col}
            row={config.row}
            scale={scale}
          />
        );
      })}
    </div>
  );
}
