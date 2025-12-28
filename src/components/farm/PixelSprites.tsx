'use client';

import { cn } from '@/lib/utils';

/**
 * SVG 기반 픽셀 아트 스프라이트
 *
 * PNG 에셋 다운로드 전에 사용할 수 있는 플레이스홀더입니다.
 * Stardew Valley 스타일의 픽셀 아트를 SVG로 구현했습니다.
 */

interface PixelSpriteProps {
  className?: string;
  size?: number;
  onClick?: () => void;
}

// ============================================
// 작물 스프라이트 (Crop Sprites)
// ============================================

interface CropPixelProps extends PixelSpriteProps {
  stage: 0 | 1 | 2 | 3 | 4; // 빈땅, 씨앗, 새싹, 성장, 수확
  type?: CropType;
}

export type CropType = 'tomato' | 'wheat' | 'corn' | 'carrot' | 'turnip' | 'strawberry' | 'grape' | 'potato' | 'pumpkin' | 'watermelon' | 'cabbage' | 'onion' | 'radish';

export const CROP_INFO: Record<CropType, { name: string; emoji: string; growTime: number; sellPrice: number; buyPrice: number }> = {
  tomato: { name: '토마토', emoji: '🍅', growTime: 4, sellPrice: 25, buyPrice: 10 },
  wheat: { name: '밀', emoji: '🌾', growTime: 3, sellPrice: 15, buyPrice: 5 },
  corn: { name: '옥수수', emoji: '🌽', growTime: 5, sellPrice: 35, buyPrice: 15 },
  carrot: { name: '당근', emoji: '🥕', growTime: 3, sellPrice: 20, buyPrice: 8 },
  turnip: { name: '순무', emoji: '🥔', growTime: 2, sellPrice: 12, buyPrice: 4 },
  strawberry: { name: '딸기', emoji: '🍓', growTime: 4, sellPrice: 30, buyPrice: 12 },
  grape: { name: '포도', emoji: '🍇', growTime: 6, sellPrice: 50, buyPrice: 25 },
  potato: { name: '감자', emoji: '🥔', growTime: 3, sellPrice: 18, buyPrice: 6 },
  pumpkin: { name: '호박', emoji: '🎃', growTime: 7, sellPrice: 60, buyPrice: 30 },
  watermelon: { name: '수박', emoji: '🍉', growTime: 8, sellPrice: 80, buyPrice: 40 },
  cabbage: { name: '양배추', emoji: '🥬', growTime: 4, sellPrice: 22, buyPrice: 9 },
  onion: { name: '양파', emoji: '🧅', growTime: 3, sellPrice: 16, buyPrice: 6 },
  radish: { name: '무', emoji: '🥕', growTime: 2, sellPrice: 14, buyPrice: 5 },
};

const CROP_COLORS: Record<CropType, { fruit: string; leaf: string }> = {
  tomato: { fruit: '#e74c3c', leaf: '#27ae60' },
  wheat: { fruit: '#f1c40f', leaf: '#8b7355' },
  corn: { fruit: '#f39c12', leaf: '#27ae60' },
  carrot: { fruit: '#e67e22', leaf: '#27ae60' },
  turnip: { fruit: '#ecf0f1', leaf: '#27ae60' },
  strawberry: { fruit: '#ff6b6b', leaf: '#27ae60' },
  grape: { fruit: '#8e44ad', leaf: '#27ae60' },
  potato: { fruit: '#d4a574', leaf: '#27ae60' },
  pumpkin: { fruit: '#ff8c00', leaf: '#27ae60' },
  watermelon: { fruit: '#2ecc71', leaf: '#27ae60' },
  cabbage: { fruit: '#90EE90', leaf: '#27ae60' },
  onion: { fruit: '#FFFACD', leaf: '#27ae60' },
  radish: { fruit: '#FF69B4', leaf: '#27ae60' },
};

export function CropPixel({ stage, type = 'tomato', size = 48, className, onClick }: CropPixelProps) {
  const colors = CROP_COLORS[type];
  const px = size / 16; // 16x16 기준 픽셀 크기

  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 16 16"
      className={cn('', onClick && 'cursor-pointer hover:brightness-110', className)}
      onClick={onClick}
      style={{ imageRendering: 'pixelated' }}
    >
      {/* 흙 배경 */}
      <rect x="0" y="12" width="16" height="4" fill="#8B5A2B" />
      <rect x="1" y="13" width="2" height="1" fill="#6B4423" />
      <rect x="6" y="14" width="3" height="1" fill="#6B4423" />
      <rect x="12" y="13" width="2" height="1" fill="#6B4423" />

      {stage === 0 && (
        /* 빈 땅 */
        <>
          <rect x="4" y="10" width="8" height="2" fill="#8B5A2B" />
          <rect x="6" y="9" width="4" height="1" fill="#7a4a1b" />
        </>
      )}

      {stage === 1 && (
        /* 씨앗 */
        <>
          <rect x="7" y="10" width="2" height="2" fill="#5D4037" />
          <rect x="7" y="11" width="2" height="1" fill="#4E342E" />
        </>
      )}

      {stage === 2 && (
        /* 새싹 */
        <>
          <rect x="7" y="8" width="2" height="4" fill="#27ae60" />
          <rect x="6" y="6" width="1" height="2" fill="#2ecc71" />
          <rect x="9" y="6" width="1" height="2" fill="#2ecc71" />
          <rect x="7" y="5" width="2" height="1" fill="#2ecc71" />
        </>
      )}

      {stage === 3 && (
        /* 성장 중 */
        <>
          <rect x="7" y="6" width="2" height="6" fill="#27ae60" />
          <rect x="5" y="4" width="2" height="3" fill="#2ecc71" />
          <rect x="9" y="4" width="2" height="3" fill="#2ecc71" />
          <rect x="6" y="2" width="4" height="2" fill="#2ecc71" />
          <rect x="4" y="3" width="2" height="2" fill={colors.leaf} />
          <rect x="10" y="3" width="2" height="2" fill={colors.leaf} />
        </>
      )}

      {stage === 4 && (
        /* 수확 가능 */
        <>
          {/* 줄기 */}
          <rect x="7" y="8" width="2" height="4" fill="#27ae60" />
          {/* 잎 */}
          <rect x="4" y="6" width="3" height="2" fill={colors.leaf} />
          <rect x="9" y="6" width="3" height="2" fill={colors.leaf} />
          <rect x="5" y="4" width="2" height="2" fill={colors.leaf} />
          <rect x="9" y="4" width="2" height="2" fill={colors.leaf} />
          {/* 열매 */}
          <rect x="5" y="1" width="6" height="5" fill={colors.fruit} />
          <rect x="6" y="0" width="4" height="1" fill={colors.fruit} />
          <rect x="7" y="0" width="2" height="1" fill="#2ecc71" />
          {/* 하이라이트 */}
          <rect x="6" y="2" width="2" height="2" fill="rgba(255,255,255,0.3)" />
        </>
      )}
    </svg>
  );
}

// ============================================
// 집 스프라이트 (House Sprites)
// ============================================

interface HousePixelProps extends PixelSpriteProps {
  level: 1 | 2 | 3 | 4;
}

const HOUSE_COLORS = {
  1: { roof: '#8B4513', wall: '#DEB887', door: '#654321' }, // 초가집
  2: { roof: '#A0522D', wall: '#D2B48C', door: '#8B4513' }, // 나무집
  3: { roof: '#708090', wall: '#A9A9A9', door: '#654321' }, // 벽돌집
  4: { roof: '#DAA520', wall: '#FFD700', door: '#8B4513' }, // 황금 저택
};

export function HousePixel({ level, size = 96, className, onClick }: HousePixelProps) {
  const colors = HOUSE_COLORS[level];

  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      className={cn('', onClick && 'cursor-pointer', className)}
      onClick={onClick}
      style={{ imageRendering: 'pixelated' }}
    >
      {/* 지붕 */}
      <polygon points="12,2 2,10 22,10" fill={colors.roof} />
      <polygon points="12,2 4,9 20,9" fill={level === 4 ? '#FFE55C' : '#A0522D'} />

      {/* 굴뚝 */}
      {level >= 2 && (
        <>
          <rect x="17" y="3" width="3" height="5" fill="#696969" />
          <rect x="17" y="2" width="3" height="1" fill="#808080" />
        </>
      )}

      {/* 벽 */}
      <rect x="4" y="10" width="16" height="12" fill={colors.wall} />

      {/* 문 */}
      <rect x="10" y="14" width="4" height="8" fill={colors.door} />
      <rect x="13" y="17" width="1" height="1" fill="#FFD700" /> {/* 손잡이 */}

      {/* 창문 */}
      <rect x="5" y="12" width="3" height="3" fill="#87CEEB" />
      <rect x="16" y="12" width="3" height="3" fill="#87CEEB" />
      {/* 창문 프레임 */}
      <rect x="6" y="12" width="1" height="3" fill={colors.wall} />
      <rect x="5" y="13" width="3" height="1" fill={colors.wall} />
      <rect x="17" y="12" width="1" height="3" fill={colors.wall} />
      <rect x="16" y="13" width="3" height="1" fill={colors.wall} />

      {/* 레벨 4 장식 */}
      {level === 4 && (
        <>
          <rect x="11" y="1" width="2" height="2" fill="#FF0000" /> {/* 깃발 */}
          <rect x="4" y="10" width="1" height="12" fill="#B8860B" />
          <rect x="19" y="10" width="1" height="12" fill="#B8860B" />
        </>
      )}
    </svg>
  );
}

// ============================================
// 캐릭터 스프라이트 (Character Sprites)
// ============================================

interface CharacterPixelProps extends PixelSpriteProps {
  hairStyle?: 'short' | 'long' | 'curly' | 'spiky';
  hairColor?: string;
  skinColor?: string;
  clothesColor?: string;
  direction?: 'down' | 'left' | 'right' | 'up';
}

export function CharacterPixel({
  hairStyle = 'short',
  hairColor = '#8B4513',
  skinColor = '#FFDAB9',
  clothesColor = '#3498db',
  direction = 'down',
  size = 64,
  className,
  onClick,
}: CharacterPixelProps) {
  const showFace = direction === 'down';
  const showBack = direction === 'up';

  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 16 20"
      className={cn('', onClick && 'cursor-pointer', className)}
      onClick={onClick}
      style={{ imageRendering: 'pixelated' }}
    >
      {/* 머리카락 */}
      {hairStyle === 'short' && (
        <>
          <rect x="5" y="1" width="6" height="2" fill={hairColor} />
          <rect x="4" y="2" width="8" height="2" fill={hairColor} />
        </>
      )}
      {hairStyle === 'long' && (
        <>
          <rect x="5" y="1" width="6" height="2" fill={hairColor} />
          <rect x="4" y="2" width="8" height="3" fill={hairColor} />
          <rect x="4" y="5" width="2" height="5" fill={hairColor} />
          <rect x="10" y="5" width="2" height="5" fill={hairColor} />
        </>
      )}
      {hairStyle === 'curly' && (
        <>
          <rect x="4" y="1" width="8" height="3" fill={hairColor} />
          <rect x="3" y="2" width="2" height="3" fill={hairColor} />
          <rect x="11" y="2" width="2" height="3" fill={hairColor} />
        </>
      )}
      {hairStyle === 'spiky' && (
        <>
          <rect x="5" y="0" width="2" height="2" fill={hairColor} />
          <rect x="7" y="1" width="2" height="1" fill={hairColor} />
          <rect x="9" y="0" width="2" height="2" fill={hairColor} />
          <rect x="4" y="2" width="8" height="2" fill={hairColor} />
        </>
      )}

      {/* 얼굴 */}
      <rect x="5" y="4" width="6" height="5" fill={skinColor} />

      {showFace && (
        <>
          {/* 눈 */}
          <rect x="6" y="5" width="1" height="2" fill="#2d2d2d" />
          <rect x="9" y="5" width="1" height="2" fill="#2d2d2d" />
          {/* 입 */}
          <rect x="7" y="8" width="2" height="1" fill="#e74c3c" />
        </>
      )}

      {showBack && (
        <>
          {/* 뒷머리 */}
          <rect x="5" y="4" width="6" height="5" fill={hairColor} />
        </>
      )}

      {/* 몸 */}
      <rect x="4" y="9" width="8" height="7" fill={clothesColor} />
      <rect x="3" y="9" width="2" height="5" fill={clothesColor} /> {/* 왼팔 */}
      <rect x="11" y="9" width="2" height="5" fill={clothesColor} /> {/* 오른팔 */}

      {/* 손 */}
      <rect x="3" y="14" width="2" height="1" fill={skinColor} />
      <rect x="11" y="14" width="2" height="1" fill={skinColor} />

      {/* 다리 */}
      <rect x="5" y="16" width="2" height="4" fill="#34495e" />
      <rect x="9" y="16" width="2" height="4" fill="#34495e" />

      {/* 신발 */}
      <rect x="4" y="19" width="3" height="1" fill="#8B4513" />
      <rect x="9" y="19" width="3" height="1" fill="#8B4513" />
    </svg>
  );
}

// ============================================
// 아이템 스프라이트 (Item Sprites)
// ============================================

interface ItemPixelProps extends PixelSpriteProps {
  type: 'seed' | 'fertilizer' | 'harvest' | 'coin' | 'water';
}

export function ItemPixel({ type, size = 32, className, onClick }: ItemPixelProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 16 16"
      className={cn('', onClick && 'cursor-pointer', className)}
      onClick={onClick}
      style={{ imageRendering: 'pixelated' }}
    >
      {type === 'seed' && (
        <>
          <ellipse cx="8" cy="10" rx="4" ry="3" fill="#8B4513" />
          <ellipse cx="8" cy="9" rx="3" ry="2" fill="#A0522D" />
          <rect x="7" y="5" width="2" height="3" fill="#27ae60" />
          <rect x="6" y="4" width="1" height="2" fill="#2ecc71" />
          <rect x="9" y="4" width="1" height="2" fill="#2ecc71" />
        </>
      )}

      {type === 'fertilizer' && (
        <>
          <rect x="4" y="6" width="8" height="8" fill="#8B4513" />
          <rect x="5" y="7" width="6" height="6" fill="#654321" />
          <rect x="6" y="4" width="4" height="3" fill="#8B4513" />
          <rect x="6" y="8" width="4" height="2" fill="#27ae60" />
        </>
      )}

      {type === 'harvest' && (
        <>
          <rect x="3" y="8" width="10" height="6" fill="#DEB887" />
          <rect x="4" y="9" width="8" height="4" fill="#F4D03F" />
          <rect x="5" y="4" width="6" height="5" fill="#e74c3c" />
          <rect x="6" y="3" width="4" height="2" fill="#c0392b" />
          <rect x="7" y="2" width="2" height="2" fill="#27ae60" />
        </>
      )}

      {type === 'coin' && (
        <>
          <circle cx="8" cy="8" r="6" fill="#FFD700" />
          <circle cx="8" cy="8" r="4" fill="#FFA500" />
          <rect x="7" y="5" width="2" height="6" fill="#FFD700" />
          <rect x="6" y="6" width="4" height="1" fill="#FFD700" />
          <rect x="6" y="9" width="4" height="1" fill="#FFD700" />
        </>
      )}

      {type === 'water' && (
        <>
          <ellipse cx="8" cy="10" rx="5" ry="4" fill="#3498db" />
          <ellipse cx="8" cy="9" rx="4" ry="3" fill="#5dade2" />
          <rect x="6" y="3" width="4" height="5" fill="#3498db" />
          <rect x="5" y="5" width="2" height="3" fill="#5dade2" />
        </>
      )}
    </svg>
  );
}

// ============================================
// 타일 스프라이트 (Tile Sprites)
// ============================================

interface TilePixelProps extends PixelSpriteProps {
  type: 'grass' | 'dirt' | 'water' | 'path' | 'fence';
}

export function TilePixel({ type, size = 32, className, onClick }: TilePixelProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 16 16"
      className={cn('', onClick && 'cursor-pointer', className)}
      onClick={onClick}
      style={{ imageRendering: 'pixelated' }}
    >
      {type === 'grass' && (
        <>
          <rect x="0" y="0" width="16" height="16" fill="#7cba5f" />
          <rect x="2" y="3" width="1" height="2" fill="#6aa84f" />
          <rect x="7" y="1" width="1" height="2" fill="#8fce73" />
          <rect x="12" y="5" width="1" height="2" fill="#6aa84f" />
          <rect x="4" y="10" width="1" height="2" fill="#8fce73" />
          <rect x="10" y="12" width="1" height="2" fill="#6aa84f" />
        </>
      )}

      {type === 'dirt' && (
        <>
          <rect x="0" y="0" width="16" height="16" fill="#8B5A2B" />
          <rect x="2" y="2" width="2" height="1" fill="#6B4423" />
          <rect x="8" y="5" width="3" height="1" fill="#6B4423" />
          <rect x="4" y="10" width="2" height="1" fill="#9B6A3B" />
          <rect x="11" y="12" width="2" height="1" fill="#6B4423" />
        </>
      )}

      {type === 'water' && (
        <>
          <rect x="0" y="0" width="16" height="16" fill="#3498db" />
          <rect x="2" y="3" width="4" height="1" fill="#5dade2" />
          <rect x="8" y="7" width="5" height="1" fill="#5dade2" />
          <rect x="3" y="11" width="3" height="1" fill="#2980b9" />
        </>
      )}

      {type === 'path' && (
        <>
          <rect x="0" y="0" width="16" height="16" fill="#D2B48C" />
          <rect x="3" y="2" width="2" height="2" fill="#C4A57B" />
          <rect x="9" y="6" width="2" height="2" fill="#BFA16B" />
          <rect x="5" y="11" width="2" height="2" fill="#C4A57B" />
        </>
      )}

      {type === 'fence' && (
        <>
          <rect x="0" y="0" width="16" height="16" fill="#7cba5f" />
          <rect x="6" y="4" width="4" height="10" fill="#8B4513" />
          <rect x="2" y="6" width="12" height="2" fill="#A0522D" />
          <rect x="2" y="10" width="12" height="2" fill="#A0522D" />
        </>
      )}
    </svg>
  );
}
