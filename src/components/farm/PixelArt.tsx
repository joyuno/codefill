'use client';

import { cn } from '@/lib/utils';

// Pixel Art CSS utilities for Stardew Valley-style farm
export const pixelBorder = 'border-4 border-[#5c3a21] shadow-[4px_4px_0_0_#3d2314]';
export const pixelBorderLight = 'border-2 border-[#8b6914] shadow-[2px_2px_0_0_#5c4510]';

// Pixel character sprites using CSS
interface PixelCharacterProps {
  hair: string;
  face: string;
  clothes: string;
  color: string;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const HAIR_STYLES: Record<string, string[][]> = {
  short: [
    ['t', 'h', 'h', 'h', 't'],
    ['h', 'h', 'h', 'h', 'h'],
    ['t', 't', 't', 't', 't'],
  ],
  long: [
    ['t', 'h', 'h', 'h', 't'],
    ['h', 'h', 'h', 'h', 'h'],
    ['h', 't', 't', 't', 'h'],
    ['h', 't', 't', 't', 'h'],
  ],
  curly: [
    ['h', 'h', 'h', 'h', 'h'],
    ['h', 'h', 'h', 'h', 'h'],
    ['h', 't', 't', 't', 'h'],
  ],
  spiky: [
    ['h', 't', 'h', 't', 'h'],
    ['t', 'h', 'h', 'h', 't'],
    ['h', 'h', 'h', 'h', 'h'],
  ],
};

const FACE_STYLES: Record<string, string[][]> = {
  happy: [
    ['s', 'e', 't', 'e', 's'],
    ['s', 't', 't', 't', 's'],
    ['t', 't', 'm', 't', 't'],
  ],
  cool: [
    ['g', 'g', 't', 'g', 'g'],
    ['s', 't', 't', 't', 's'],
    ['t', 't', 'm', 't', 't'],
  ],
  cute: [
    ['s', 'e', 't', 'e', 's'],
    ['p', 't', 't', 't', 'p'],
    ['t', 't', 'w', 't', 't'],
  ],
  sleepy: [
    ['s', '-', 't', '-', 's'],
    ['s', 't', 't', 't', 's'],
    ['t', 't', 'o', 't', 't'],
  ],
};

const CLOTHES_STYLES: Record<string, string[][]> = {
  tshirt: [
    ['c', 'c', 'c', 'c', 'c'],
    ['t', 'c', 'c', 'c', 't'],
    ['t', 'c', 'c', 'c', 't'],
  ],
  hoodie: [
    ['c', 'c', 'c', 'c', 'c'],
    ['c', 'c', 'c', 'c', 'c'],
    ['t', 'c', 'c', 'c', 't'],
  ],
  overalls: [
    ['t', 'c', 'c', 'c', 't'],
    ['c', 'c', 'c', 'c', 'c'],
    ['c', 'c', 'c', 'c', 'c'],
  ],
  farmer: [
    ['c', 'c', 'c', 'c', 'c'],
    ['c', 'b', 'c', 'b', 'c'],
    ['c', 'c', 'c', 'c', 'c'],
  ],
};

const HAIR_COLORS: Record<string, string> = {
  brown: '#8B4513',
  black: '#2d2d2d',
  blonde: '#f4d03f',
  red: '#c0392b',
  blue: '#3498db',
  pink: '#e91e8a',
};

const SKIN_COLORS: Record<string, string> = {
  light: '#ffe4c4',
  medium: '#deb887',
  tan: '#d2691e',
  dark: '#8b4513',
};

const CLOTHES_COLORS: Record<string, string> = {
  blue: '#3498db',
  red: '#e74c3c',
  green: '#27ae60',
  purple: '#9b59b6',
  orange: '#e67e22',
  pink: '#e91e8a',
};

export function PixelCharacter({
  hair,
  face,
  clothes,
  color,
  size = 'md',
  className,
}: PixelCharacterProps) {
  const pixelSize = size === 'sm' ? 4 : size === 'md' ? 6 : 8;
  const hairColor = HAIR_COLORS[color] || HAIR_COLORS.brown;
  const skinColor = SKIN_COLORS.light;
  const clothesColor = CLOTHES_COLORS[color] || CLOTHES_COLORS.blue;

  const hairStyle = HAIR_STYLES[hair] || HAIR_STYLES.short;
  const faceStyle = FACE_STYLES[face] || FACE_STYLES.happy;
  const clothesStyle = CLOTHES_STYLES[clothes] || CLOTHES_STYLES.tshirt;

  const getPixelColor = (type: string, char: string) => {
    if (char === 't') return 'transparent';
    if (type === 'hair' && char === 'h') return hairColor;
    if (type === 'face') {
      if (char === 's') return skinColor;
      if (char === 'e') return '#2d2d2d'; // eyes
      if (char === 'm' || char === 'w' || char === 'o') return '#c0392b'; // mouth
      if (char === 'g') return '#2d2d2d'; // glasses
      if (char === 'p') return '#ffb6c1'; // blush
      if (char === '-') return '#2d2d2d'; // closed eyes
    }
    if (type === 'clothes') {
      if (char === 'c') return clothesColor;
      if (char === 'b') return '#f4d03f'; // buttons
    }
    return 'transparent';
  };

  return (
    <div
      className={cn('flex flex-col items-center', className)}
      style={{ imageRendering: 'pixelated' }}
    >
      {/* Hair */}
      {hairStyle.map((row, rowIndex) => (
        <div key={`hair-${rowIndex}`} className="flex">
          {row.map((pixel, colIndex) => (
            <div
              key={`hair-${rowIndex}-${colIndex}`}
              style={{
                width: pixelSize,
                height: pixelSize,
                backgroundColor: getPixelColor('hair', pixel),
              }}
            />
          ))}
        </div>
      ))}
      {/* Face */}
      {faceStyle.map((row, rowIndex) => (
        <div key={`face-${rowIndex}`} className="flex">
          {row.map((pixel, colIndex) => (
            <div
              key={`face-${rowIndex}-${colIndex}`}
              style={{
                width: pixelSize,
                height: pixelSize,
                backgroundColor: getPixelColor('face', pixel),
              }}
            />
          ))}
        </div>
      ))}
      {/* Clothes */}
      {clothesStyle.map((row, rowIndex) => (
        <div key={`clothes-${rowIndex}`} className="flex">
          {row.map((pixel, colIndex) => (
            <div
              key={`clothes-${rowIndex}-${colIndex}`}
              style={{
                width: pixelSize,
                height: pixelSize,
                backgroundColor: getPixelColor('clothes', pixel),
              }}
            />
          ))}
        </div>
      ))}
    </div>
  );
}

// Pixel Crop Component
interface PixelCropProps {
  stage: 'empty' | 'seed' | 'sprout' | 'growing' | 'ready';
  size?: 'sm' | 'md' | 'lg';
  onClick?: () => void;
  className?: string;
}

const CROP_SPRITES: Record<string, string[][]> = {
  empty: [
    ['t', 't', 't', 't', 't'],
    ['t', 'd', 'd', 'd', 't'],
    ['d', 'd', 'd', 'd', 'd'],
    ['d', 'd', 'd', 'd', 'd'],
  ],
  seed: [
    ['t', 't', 't', 't', 't'],
    ['t', 'd', 's', 'd', 't'],
    ['d', 'd', 'd', 'd', 'd'],
    ['d', 'd', 'd', 'd', 'd'],
  ],
  sprout: [
    ['t', 't', 'g', 't', 't'],
    ['t', 'g', 'g', 'g', 't'],
    ['d', 'd', 'g', 'd', 'd'],
    ['d', 'd', 'd', 'd', 'd'],
  ],
  growing: [
    ['t', 'g', 'g', 'g', 't'],
    ['g', 'g', 'g', 'g', 'g'],
    ['d', 'g', 'g', 'g', 'd'],
    ['d', 'd', 'd', 'd', 'd'],
  ],
  ready: [
    ['y', 'y', 'y', 'y', 'y'],
    ['g', 'y', 'y', 'y', 'g'],
    ['d', 'g', 'g', 'g', 'd'],
    ['d', 'd', 'd', 'd', 'd'],
  ],
};

const CROP_COLORS: Record<string, string> = {
  t: 'transparent',
  d: '#8B5A2B', // dirt
  s: '#654321', // seed
  g: '#228B22', // green
  y: '#FFD700', // yellow (ready)
};

export function PixelCrop({ stage, size = 'md', onClick, className }: PixelCropProps) {
  const pixelSize = size === 'sm' ? 6 : size === 'md' ? 8 : 10;
  const sprite = CROP_SPRITES[stage];

  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        'flex flex-col items-center transition-transform hover:scale-105',
        onClick && 'cursor-pointer',
        className
      )}
      style={{ imageRendering: 'pixelated' }}
    >
      {sprite.map((row, rowIndex) => (
        <div key={rowIndex} className="flex">
          {row.map((pixel, colIndex) => (
            <div
              key={colIndex}
              style={{
                width: pixelSize,
                height: pixelSize,
                backgroundColor: CROP_COLORS[pixel] || 'transparent',
              }}
            />
          ))}
        </div>
      ))}
    </button>
  );
}

// Pixel House Component
interface PixelHouseProps {
  level: number;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const HOUSE_SPRITES: Record<number, string[][]> = {
  1: [
    ['t', 't', 'r', 'r', 'r', 't', 't'],
    ['t', 'r', 'r', 'r', 'r', 'r', 't'],
    ['r', 'r', 'r', 'r', 'r', 'r', 'r'],
    ['w', 'w', 'w', 'd', 'w', 'w', 'w'],
    ['w', 'b', 'w', 'd', 'w', 'b', 'w'],
    ['w', 'w', 'w', 'd', 'w', 'w', 'w'],
  ],
  2: [
    ['t', 't', 'r', 'r', 'r', 't', 't'],
    ['t', 'r', 'r', 'r', 'r', 'r', 't'],
    ['r', 'r', 'r', 'c', 'r', 'r', 'r'],
    ['o', 'o', 'o', 'd', 'o', 'o', 'o'],
    ['o', 'b', 'o', 'd', 'o', 'b', 'o'],
    ['o', 'o', 'o', 'd', 'o', 'o', 'o'],
  ],
  3: [
    ['t', 't', 'r', 'r', 'r', 't', 't'],
    ['t', 'r', 'r', 'r', 'r', 'r', 't'],
    ['r', 'r', 'c', 'c', 'c', 'r', 'r'],
    ['s', 's', 's', 'd', 's', 's', 's'],
    ['s', 'b', 's', 'd', 's', 'b', 's'],
    ['s', 's', 's', 'd', 's', 's', 's'],
  ],
  4: [
    ['t', 'f', 't', 't', 't', 'f', 't'],
    ['t', 'r', 'r', 'r', 'r', 'r', 't'],
    ['r', 'r', 'c', 'c', 'c', 'r', 'r'],
    ['g', 'g', 'g', 'd', 'g', 'g', 'g'],
    ['g', 'y', 'g', 'd', 'g', 'y', 'g'],
    ['g', 'g', 'g', 'd', 'g', 'g', 'g'],
  ],
};

const HOUSE_COLORS: Record<string, string> = {
  t: 'transparent',
  r: '#8B0000', // roof (red)
  w: '#DEB887', // wood walls
  o: '#8B4513', // oak wood
  s: '#A9A9A9', // stone
  g: '#D4AF37', // gold
  d: '#654321', // door
  b: '#87CEEB', // window (blue)
  y: '#FFFF00', // yellow window
  c: '#808080', // chimney
  f: '#FFD700', // flag
};

export function PixelHouse({ level, size = 'md', className }: PixelHouseProps) {
  const pixelSize = size === 'sm' ? 6 : size === 'md' ? 10 : 14;
  const sprite = HOUSE_SPRITES[level] || HOUSE_SPRITES[1];

  return (
    <div
      className={cn('flex flex-col items-center', className)}
      style={{ imageRendering: 'pixelated' }}
    >
      {sprite.map((row, rowIndex) => (
        <div key={rowIndex} className="flex">
          {row.map((pixel, colIndex) => (
            <div
              key={colIndex}
              style={{
                width: pixelSize,
                height: pixelSize,
                backgroundColor: HOUSE_COLORS[pixel] || 'transparent',
              }}
            />
          ))}
        </div>
      ))}
    </div>
  );
}

// Pixel Item Component (for inventory)
interface PixelItemProps {
  type: 'seed' | 'fertilizer' | 'harvest' | 'coin';
  size?: 'sm' | 'md';
  className?: string;
}

const ITEM_SPRITES: Record<string, string[][]> = {
  seed: [
    ['t', 'b', 't'],
    ['b', 'b', 'b'],
    ['t', 'b', 't'],
  ],
  fertilizer: [
    ['g', 'g', 'g'],
    ['g', 'w', 'g'],
    ['g', 'g', 'g'],
  ],
  harvest: [
    ['y', 'y', 'y'],
    ['g', 'y', 'g'],
    ['t', 'g', 't'],
  ],
  coin: [
    ['y', 'y', 'y'],
    ['y', 'o', 'y'],
    ['y', 'y', 'y'],
  ],
};

const ITEM_COLORS: Record<string, string> = {
  t: 'transparent',
  b: '#8B4513', // brown
  g: '#228B22', // green
  w: '#FFFFFF', // white
  y: '#FFD700', // yellow
  o: '#FFA500', // orange
};

export function PixelItem({ type, size = 'md', className }: PixelItemProps) {
  const pixelSize = size === 'sm' ? 4 : 6;
  const sprite = ITEM_SPRITES[type];

  return (
    <div
      className={cn('flex flex-col items-center', className)}
      style={{ imageRendering: 'pixelated' }}
    >
      {sprite.map((row, rowIndex) => (
        <div key={rowIndex} className="flex">
          {row.map((pixel, colIndex) => (
            <div
              key={colIndex}
              style={{
                width: pixelSize,
                height: pixelSize,
                backgroundColor: ITEM_COLORS[pixel] || 'transparent',
              }}
            />
          ))}
        </div>
      ))}
    </div>
  );
}

// Farm background grass tile
export function PixelGrass({ className }: { className?: string }) {
  return (
    <div
      className={cn('w-full h-full', className)}
      style={{
        backgroundColor: '#7cba5f',
        backgroundImage: `
          radial-gradient(circle at 20% 30%, #6aa84f 2px, transparent 2px),
          radial-gradient(circle at 60% 70%, #8fce73 2px, transparent 2px),
          radial-gradient(circle at 80% 20%, #6aa84f 1px, transparent 1px)
        `,
        backgroundSize: '40px 40px',
        imageRendering: 'pixelated',
      }}
    />
  );
}
