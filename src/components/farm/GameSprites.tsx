'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Image from 'next/image';
import { cn } from '@/lib/utils';

/**
 * Modern Farm 에셋 기반 스프라이트 컴포넌트
 * - itch.io Modern Farm v1.2 에셋 팩 사용
 * - 32x32 픽셀 아트 이미지 기반
 */

// ============================================
// 에셋 경로 상수
// ============================================

const FARM_ASSETS = {
  crops: '/farm/crops',
  houses: '/farm/houses',
  characters: '/farm/characters',
  terrains: '/farm/terrains',
  tools: '/farm/tools',
  icons: '/farm/icons',
  animals: '/farm/animals',
};

// ============================================
// 타입 정의
// ============================================

export type FarmerAction = 'idle' | 'walk' | 'farm' | 'water' | 'harvest' | 'sleep';
export type Direction = 'down' | 'up' | 'left' | 'right';
export type CropStage = 0 | 1 | 2 | 3 | 4;
export type CropVariety = 'carrot' | 'tomato' | 'corn' | 'strawberry' | 'potato' | 'wheat' | 'pumpkin' | 'cabbage' | 'onion' | 'radish';

// ============================================
// 작물 이미지 매핑
// ============================================

/**
 * 작물별 이미지 파일 매핑
 * - 각 단계별로 적절한 이미지 파일 지정
 */
const CROP_IMAGE_MAP: Record<CropVariety, Record<CropStage, string>> = {
  carrot: {
    0: 'Soil_Wet_1_32x32.png',  // 빈 땅
    1: 'Crop_Carrot_Sprout_32x32.png',
    2: 'Crop_Carrot_Stage_1_32x32.png',
    3: 'Crop_Carrot_Stage_1_32x32.png',
    4: 'Crop_Carrot_Ripe_1_32x32.png',
  },
  tomato: {
    0: 'Soil_Wet_1_32x32.png',
    1: 'Crop_Tomato_Sprout_32x32.png',
    2: 'Crop_Tomato_Stage_1_32x32.png',
    3: 'Crop_Tomato_Fruitless_32x32.png',
    4: 'Crop_Tomato_Ripe_32x32.png',
  },
  corn: {
    0: 'Soil_Wet_1_32x32.png',
    1: 'Crop_Corn_Sprout_32x32.png',
    2: 'Crop_Corn_Stage_1_32x32.png',
    3: 'Crop_Corn_Fruitless_32x32.png',
    4: 'Crop_Corn_Ripe_32x32.png',
  },
  strawberry: {
    0: 'Soil_Wet_1_32x32.png',
    1: 'Crop_Strawberry_Sprout_32x32.png',
    2: 'Crop_Strawberry_Stage_1_32x32.png',
    3: 'Crop_Strawberry_Fruitless_32x32.png',
    4: 'Crop_Strawberry_Ripe_32x32.png',
  },
  potato: {
    0: 'Soil_Wet_1_32x32.png',
    1: 'Crop_Radish_Sprout_32x32.png',  // potato 대신 radish 사용
    2: 'Crop_Radish_Stage_1_32x32.png',
    3: 'Crop_Radish_Stage_2_32x32.png',
    4: 'Crop_Radish_Ripe_1_32x32.png',
  },
  wheat: {
    0: 'Soil_Wet_1_32x32.png',
    1: 'Crop_Grain_Sprout_32x32.png',
    2: 'Crop_Grain_Stage_1_32x32.png',
    3: 'Crop_Grain_Stage_2_32x32.png',
    4: 'Crop_Grain_Ripe_32x32.png',
  },
  pumpkin: {
    0: 'Soil_Wet_1_32x32.png',
    1: 'Crop_Pumpkin_Sprout_32x32.png',
    2: 'Crop_Pumpkin_Stage_1_32x32.png',
    3: 'Crop_Pumpkin_Fruitless_32x32.png',
    4: 'Crop_Pumpkin_Ripe_32x32.png',
  },
  cabbage: {
    0: 'Soil_Wet_1_32x32.png',
    1: 'Crop_Cabbage_Sprout_32x32.png',
    2: 'Crop_Cabbage_Stage_1_32x32.png',
    3: 'Crop_Cabbage_Stage_1_32x32.png',
    4: 'Crop_Cabbage_Ripe_32x32.png',
  },
  onion: {
    0: 'Soil_Wet_1_32x32.png',
    1: 'Crop_Onion_Sprout_32x32.png',
    2: 'Crop_Onion_Stage_1_32x32.png',
    3: 'Crop_Onion_Stage_1_32x32.png',
    4: 'Crop_Onion_Ripe_32x32.png',
  },
  radish: {
    0: 'Soil_Wet_1_32x32.png',
    1: 'Crop_Radish_Sprout_32x32.png',
    2: 'Crop_Radish_Stage_1_32x32.png',
    3: 'Crop_Radish_Stage_2_32x32.png',
    4: 'Crop_Radish_Ripe_1_32x32.png',
  },
};

// ============================================
// 집 이미지 매핑 (레벨별)
// ============================================

const HOUSE_IMAGE_MAP: Record<number, { src: string; width: number; height: number }> = {
  1: { src: 'Farmer_House_1_32x32.png', width: 96, height: 112 },
  2: { src: 'Farmer_House_2_32x32.png', width: 112, height: 100 },
  3: { src: 'Barn_Small_32x32.png', width: 96, height: 112 },
  4: { src: 'Farmer_House_2_32x32.png', width: 140, height: 125 }, // 황금 저택 (확대)
};

// 레벨별 집 크기 (그리드 셀 단위)
const HOUSE_SIZES: Record<number, { width: number; height: number }> = {
  1: { width: 2, height: 2 },
  2: { width: 3, height: 3 },
  3: { width: 4, height: 4 },
  4: { width: 5, height: 5 },
};

const HOUSE_STYLES: Record<number, { name: string }> = {
  1: { name: '초가집' },
  2: { name: '나무집' },
  3: { name: '헛간' },
  4: { name: '황금저택' },
};

// ============================================
// 농부 스프라이트 컴포넌트
// ============================================

interface FarmerSpriteProps {
  action?: FarmerAction;
  direction?: Direction;
  hairColor?: string;
  clothesColor?: string;
  size?: number;
  className?: string;
  animated?: boolean;
}

/**
 * 농부 스프라이트 컴포넌트
 * - 스프라이트 시트 기반 애니메이션
 * - 행동과 방향에 따라 다른 프레임 표시
 */
export function FarmerSprite({
  action = 'idle',
  direction = 'down',
  size = 32,
  className,
  animated = true,
}: FarmerSpriteProps) {
  const [frame, setFrame] = useState(0);
  
  // 스프라이트 시트 정보
  // Farmer_1_32x32.png: 각 캐릭터 32x32, 여러 방향/액션 프레임 포함
  const spriteSheetConfig = {
    idle: {
      src: `${FARM_ASSETS.characters}/Farmer_1_32x32.png`,
      frameCount: 3,
      frameWidth: 32,
      frameHeight: 32,
      row: 0, // 첫 번째 줄: idle
    },
    walk: {
      src: `${FARM_ASSETS.characters}/Farmer_1_32x32.png`,
      frameCount: 24,
      frameWidth: 32,
      frameHeight: 32,
      row: direction === 'down' ? 1 : direction === 'up' ? 2 : 3,
    },
    farm: {
      src: `${FARM_ASSETS.characters}/Farmer_1_Harvesting_36_frames_32x32.png`,
      frameCount: 36,
      frameWidth: 32,
      frameHeight: 32,
      row: 0,
    },
    harvest: {
      src: `${FARM_ASSETS.characters}/Farmer_1_Harvesting_36_frames_32x32.png`,
      frameCount: 36,
      frameWidth: 32,
      frameHeight: 32,
      row: 0,
    },
    water: {
      src: `${FARM_ASSETS.characters}/Farmer_1_Watering_56_frames_32x32.png`,
      frameCount: 56,
      frameWidth: 32,
      frameHeight: 32,
      row: 0,
    },
    sleep: {
      src: `${FARM_ASSETS.characters}/Farmer_1_32x32.png`,
      frameCount: 1,
      frameWidth: 32,
      frameHeight: 32,
      row: 0,
    },
  };

  const config = spriteSheetConfig[action];
  
  // 애니메이션 프레임 업데이트
  useEffect(() => {
    if (!animated) return;
    
    const fps = action === 'walk' ? 12 : action === 'farm' || action === 'harvest' ? 8 : action === 'water' ? 10 : 2;
    const interval = setInterval(() => {
      setFrame(prev => (prev + 1) % config.frameCount);
    }, 1000 / fps);
    
    return () => clearInterval(interval);
  }, [action, animated, config.frameCount]);

  // 방향에 따른 좌우 반전
  const scaleX = direction === 'left' ? -1 : 1;

  // 스프라이트 시트에서 현재 프레임 위치 계산
  const frameX = (frame % config.frameCount) * config.frameWidth;
  const frameY = config.row * config.frameHeight;

  return (
    <div
      className={cn('relative overflow-hidden', className)}
      style={{
        width: size,
        height: size,
        transform: `scaleX(${scaleX})`,
      }}
    >
      {/* 그림자 */}
      <div 
        className="absolute bottom-0 left-1/2 -translate-x-1/2 bg-black/20 rounded-full"
        style={{
          width: size * 0.7,
          height: size * 0.15,
        }}
      />
      
      {/* 스프라이트 시트 이미지 */}
      <div
        style={{
          position: 'absolute',
          width: config.frameWidth * config.frameCount,
          height: config.frameHeight * (config.row + 1),
          backgroundImage: `url(${config.src})`,
          backgroundRepeat: 'no-repeat',
          backgroundPosition: `-${frameX}px -${frameY}px`,
          backgroundSize: 'auto',
          transform: `scale(${size / config.frameWidth})`,
          transformOrigin: 'top left',
          imageRendering: 'pixelated',
        }}
      />
      
      {/* 간단한 픽셀 농부 폴백 (이미지 로드 실패 시) */}
      <noscript>
        <div 
          className="absolute inset-0 bg-amber-600 rounded-full"
          style={{ width: size * 0.6, height: size * 0.6, margin: 'auto' }}
        />
      </noscript>
    </div>
  );
}

// ============================================
// 작물 스프라이트 컴포넌트
// ============================================

interface CropSpriteProps {
  type?: CropVariety;
  stage?: CropStage;
  size?: number;
  withTimer?: boolean;
  remainingSeconds?: number;
  className?: string;
}

/**
 * 작물 스프라이트 컴포넌트
 * - 작물 종류와 성장 단계에 따라 다른 이미지 표시
 * - 선택적으로 남은 시간 타이머 표시
 */
export function CropSprite({
  type = 'tomato',
  stage = 0,
  size = 32,
  withTimer = false,
  remainingSeconds = 0,
  className,
}: CropSpriteProps) {
  // 작물 이미지 경로 결정
  const cropImages = CROP_IMAGE_MAP[type];
  const imageName = cropImages?.[stage] || 'Soil_Wet_1_32x32.png';
  
  // 빈 땅(Stage 0)은 terrains 폴더에서 가져옴
  const imagePath = stage === 0 
    ? `${FARM_ASSETS.terrains}/${imageName}`
    : `${FARM_ASSETS.crops}/${imageName}`;

  return (
    <div 
      className={cn('relative flex items-end justify-center', className)} 
      style={{ width: size, height: size }}
    >
      {/* 작물 이미지 */}
      <div className="relative" style={{ width: size, height: size }}>
        <Image
          src={imagePath}
          alt={`${type} stage ${stage}`}
          width={size}
          height={size}
          className="object-contain"
          style={{ 
            imageRendering: 'pixelated',
            objectPosition: 'bottom center',
          }}
          unoptimized
          onError={(e) => {
            // 이미지 로드 실패 시 기본 이미지로 대체
            const target = e.target as HTMLImageElement;
            target.src = `${FARM_ASSETS.terrains}/Soil_Wet_1_32x32.png`;
          }}
        />
        
        {/* 수확 가능 시 반짝임 효과 */}
        {stage === 4 && (
          <motion.div
            className="absolute inset-0 pointer-events-none"
            animate={{ opacity: [0, 0.3, 0] }}
            transition={{ duration: 1.5, repeat: Infinity }}
          >
            <div className="w-full h-full bg-yellow-300 rounded" />
          </motion.div>
        )}
      </div>
      
      {/* 타이머 표시 */}
      {withTimer && stage > 0 && stage < 4 && remainingSeconds > 0 && (
        <div 
          className="absolute bottom-0 left-0 right-0 bg-black/70 text-center py-0.5 rounded-b"
          style={{ fontSize: size > 32 ? '10px' : '8px' }}
        >
          <span className="text-amber-300 font-mono">
            {Math.floor(remainingSeconds / 60)}:{(remainingSeconds % 60).toString().padStart(2, '0')}
          </span>
        </div>
      )}
    </div>
  );
}

// ============================================
// 집 스프라이트 컴포넌트
// ============================================

interface HouseSpriteProps {
  level?: 1 | 2 | 3 | 4;
  gridSize?: number;
  className?: string;
  showFarmerInside?: boolean;
}

/**
 * 집 스프라이트 컴포넌트
 * - 레벨에 따라 다른 집 이미지 표시
 * - 황금 저택(레벨 4)은 특수 효과 적용
 */
export function HouseSprite({
  level = 1,
  gridSize = 24,
  className,
  showFarmerInside = false,
}: HouseSpriteProps) {
  const houseInfo = HOUSE_IMAGE_MAP[level];
  const houseSize = HOUSE_SIZES[level];
  
  const displayWidth = houseSize.width * gridSize;
  const displayHeight = houseSize.height * gridSize;

  return (
    <div 
      className={cn('relative', className)}
      style={{ 
        width: displayWidth,
        height: displayHeight,
      }}
    >
      {/* 집 이미지 */}
      <div className="relative w-full h-full">
        <Image
          src={`${FARM_ASSETS.houses}/${houseInfo.src}`}
          alt={`Level ${level} house`}
          fill
          className="object-contain"
          style={{ 
            imageRendering: 'pixelated',
            objectPosition: 'bottom center',
          }}
          unoptimized
        />
        
        {/* 레벨 4: 황금 효과 */}
        {level === 4 && (
          <>
            <motion.div
              className="absolute inset-0 pointer-events-none"
              style={{
                background: 'linear-gradient(45deg, transparent 30%, rgba(255,215,0,0.3) 50%, transparent 70%)',
              }}
              animate={{
                backgroundPosition: ['0% 0%', '100% 100%'],
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                repeatType: 'reverse',
              }}
            />
            {/* 반짝이는 별 효과 */}
            <motion.div
              className="absolute top-2 right-2 text-yellow-400"
              animate={{ scale: [1, 1.3, 1], opacity: [1, 0.7, 1] }}
              transition={{ duration: 1.5, repeat: Infinity }}
            >
              ✨
            </motion.div>
          </>
        )}
      </div>
      
      {/* 굴뚝 연기 (레벨 2 이상) */}
      {level >= 2 && (
        <motion.div
          className="absolute text-gray-400 text-sm"
          style={{
            top: level === 3 ? '5%' : '15%',
            right: level === 3 ? '35%' : '25%',
          }}
          animate={{ 
            y: [-5, -15], 
            opacity: [0.7, 0],
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
          }}
        >
          💨
        </motion.div>
      )}
      
      {/* 집 안의 농부 표시 */}
      {showFarmerInside && (
        <motion.div
          className="absolute left-1/2 -translate-x-1/2"
          style={{ bottom: '20%' }}
          animate={{ opacity: [1, 0.5, 1] }}
          transition={{ duration: 2, repeat: Infinity }}
        >
          <div 
            className="bg-yellow-400 rounded-full shadow-lg"
            style={{
              width: displayWidth * 0.15,
              height: displayWidth * 0.15,
            }}
          />
        </motion.div>
      )}
    </div>
  );
}

// ============================================
// 농장 미니맵 (사이드바용)
// ============================================

interface FarmMinimapProps {
  level?: number;
  crops?: Array<{ type: CropVariety; stage: CropStage }>;
  className?: string;
}

/**
 * 농장 미니맵 컴포넌트
 * - 메인 대시보드 사이드바에 표시되는 작은 농장 뷰
 * - 농부 자동 이동 및 행동 애니메이션 포함
 */
export function FarmMinimap({
  level = 1,
  crops = [],
  className,
}: FarmMinimapProps) {
  const [farmerPos, setFarmerPos] = useState({ x: 50, y: 50 });
  const [farmerAction, setFarmerAction] = useState<FarmerAction>('idle');
  const [farmerDirection, setFarmerDirection] = useState<Direction>('down');
  const [isInHouse, setIsInHouse] = useState(false);
  
  // 농부 자동 이동 로직
  useEffect(() => {
    const actionInterval = setInterval(() => {
      const random = Math.random();
      
      if (random < 0.1) {
        // 10% 확률로 집에 들어감
        setIsInHouse(true);
        setFarmerAction('sleep');
        setTimeout(() => {
          setIsInHouse(false);
          setFarmerAction('idle');
        }, 3000);
      } else if (random < 0.3) {
        // 20% 확률로 농사
        setFarmerAction('farm');
        setFarmerPos({ x: 15 + Math.random() * 35, y: 50 + Math.random() * 20 });
        setTimeout(() => setFarmerAction('idle'), 2000);
      } else if (random < 0.5) {
        // 20% 확률로 물주기
        setFarmerAction('water');
        setTimeout(() => setFarmerAction('idle'), 1500);
      } else {
        // 50% 확률로 걷기
        setFarmerAction('walk');
        const newX = Math.max(10, Math.min(75, farmerPos.x + (Math.random() - 0.5) * 30));
        const newY = Math.max(35, Math.min(75, farmerPos.y + (Math.random() - 0.5) * 20));
        
        // 방향 결정
        if (newX > farmerPos.x) setFarmerDirection('right');
        else if (newX < farmerPos.x) setFarmerDirection('left');
        else if (newY > farmerPos.y) setFarmerDirection('down');
        else setFarmerDirection('up');
        
        setFarmerPos({ x: newX, y: newY });
        setTimeout(() => setFarmerAction('idle'), 1000);
      }
    }, 2500);
    
    return () => clearInterval(actionInterval);
  }, [farmerPos]);
  
  const houseSize = HOUSE_SIZES[level as 1 | 2 | 3 | 4] || HOUSE_SIZES[1];
  
  return (
    <div
      className={cn(
        'relative w-full rounded-xl overflow-hidden',
        'border-4 border-amber-800',
        'shadow-[4px_4px_0_0_#78350f]',
        className
      )}
      style={{
        background: `
          linear-gradient(to bottom,
            #87CEEB 0%,
            #B0E2FF 30%,
            #7CBA5F 30%,
            #5A9F4A 100%
          )
        `,
      }}
    >
      {/* 하늘 장식 */}
      <motion.div
        className="absolute top-2 right-3 text-2xl"
        animate={{ rotate: [0, 10, 0] }}
        transition={{ duration: 4, repeat: Infinity }}
      >
        ☀️
      </motion.div>
      
      <motion.div
        className="absolute top-4 left-4 text-base opacity-70"
        animate={{ x: [0, 8, 0] }}
        transition={{ duration: 8, repeat: Infinity }}
      >
        ☁️
      </motion.div>
      
      {/* 밭 영역 */}
      <div 
        className="absolute left-[8%] top-[45%] w-[45%] h-[40%] rounded-lg overflow-hidden"
        style={{ 
          backgroundColor: '#8B5A2B',
          boxShadow: 'inset 0 2px 4px rgba(0,0,0,0.3)',
        }}
      >
        {/* 작물 그리드 */}
        <div className="grid grid-cols-3 gap-0.5 p-1 h-full">
          {crops.slice(0, 6).map((crop, i) => (
            <div key={i} className="flex items-center justify-center">
              <CropSprite type={crop.type} stage={crop.stage} size={20} />
            </div>
          ))}
        </div>
      </div>
      
      {/* 집 */}
      <div 
        className="absolute right-[5%] top-[20%]"
        style={{
          width: `${houseSize.width * 10}%`,
          height: `${houseSize.height * 10}%`,
        }}
      >
        <HouseSprite 
          level={level as 1 | 2 | 3 | 4} 
          gridSize={12} 
          showFarmerInside={isInHouse} 
        />
      </div>
      
      {/* 농부 */}
      {!isInHouse && (
        <motion.div
          className="absolute z-10"
          animate={{
            left: `${farmerPos.x}%`,
            top: `${farmerPos.y}%`,
          }}
          transition={{
            type: 'spring',
            stiffness: 50,
            damping: 15,
          }}
          style={{
            transform: 'translate(-50%, -50%)',
          }}
        >
          <FarmerSprite 
            action={farmerAction} 
            direction={farmerDirection}
            size={28}
          />
        </motion.div>
      )}
      
      {/* 잔디 장식 */}
      <div className="absolute bottom-2 left-2 text-xs opacity-60">🌿</div>
      <div className="absolute bottom-3 right-3 text-xs opacity-60">🌱</div>
    </div>
  );
}

// ============================================
// 도구 스프라이트
// ============================================

interface ToolSpriteProps {
  type: 'hoe' | 'sickle' | 'wateringCan' | 'axe' | 'pickaxe' | 'shovel';
  size?: number;
  className?: string;
}

const TOOL_IMAGE_MAP: Record<string, string> = {
  hoe: 'Tool_Shovel.png',
  sickle: 'Tool_Axe.png',
  wateringCan: 'Tool_Watering_Can.png',
  axe: 'Tool_Axe.png',
  pickaxe: 'Tool_Axe.png',
  shovel: 'Tool_Shovel.png',
};

/**
 * 도구 스프라이트 컴포넌트
 */
export function ToolSprite({ type, size = 24, className }: ToolSpriteProps) {
  const imageName = TOOL_IMAGE_MAP[type] || 'Tool_Shovel.png';
  
  return (
    <div 
      className={cn('relative', className)} 
      style={{ width: size, height: size }}
    >
      <Image
        src={`${FARM_ASSETS.tools}/${imageName}`}
        alt={type}
        width={size}
        height={size}
        className="object-contain"
        style={{ imageRendering: 'pixelated' }}
        unoptimized
      />
    </div>
  );
}

// ============================================
// 동물 스프라이트
// ============================================

interface AnimalSpriteProps {
  type: 'chicken' | 'dog';
  size?: number;
  className?: string;
}

/**
 * 동물 스프라이트 컴포넌트
 */
export function AnimalSprite({ type, size = 32, className }: AnimalSpriteProps) {
  // 동물 이미지는 스프라이트 시트 형태이므로 첫 프레임만 표시
  const animalImages: Record<string, string> = {
    chicken: 'Chicken_Brown.png',
    dog: 'Basenji_Black_Idle.png',
  };
  
  return (
    <div 
      className={cn('relative overflow-hidden', className)} 
      style={{ width: size, height: size }}
    >
      <Image
        src={`${FARM_ASSETS.animals}/${animalImages[type] || 'Chicken_Brown.png'}`}
        alt={type}
        width={size}
        height={size}
        className="object-cover object-left"
        style={{ imageRendering: 'pixelated' }}
        unoptimized
      />
    </div>
  );
}
