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
 * - farm 페이지 PlayerController 구조 기반
 * - idle/walk: Farmer_1_32x32.png (24열 x 3행)
 * - harvest/farm: Farmer_1_Harvesting_36_frames_32x32.png (36열 x 1행)
 * - 방향 순서: idle/walk = right(0), up(1), left(2), down(3)
 * - 방향 순서: harvest = down(0), left(1), right(2), up(3)
 */
export function FarmerSprite({
  action = 'idle',
  direction = 'down',
  size = 32,
  className,
  animated = true,
}: FarmerSpriteProps) {
  const [frame, setFrame] = useState(0);

  // harvest/farm 액션 여부
  const isHarvesting = action === 'farm' || action === 'harvest';

  // 스프라이트별 프레임 크기
  // idle/walk: 32x64, dig: 64x64
  const FRAME_WIDTH = isHarvesting ? 64 : 32;
  const FRAME_HEIGHT = isHarvesting ? 64 : 64;

  // 스프라이트시트별 설정
  // idle: 24열 x 3행
  // dig: 36열 x 1행 (마지막 8프레임 = down 방향)
  const IDLE_COLUMNS = 24;
  const IDLE_FRAMES_PER_DIR = 6;
  const FARM_COLUMNS = 36;
  const FARM_FRAMES_PER_DIR = 8;

  // idle/walk 방향 인덱스: right(0), up(1), left(2), down(3)
  const idleDirectionIndex: Record<Direction, number> = {
    right: 0,
    up: 1,
    left: 2,
    down: 3,
  };

  // watering(farm) 방향 인덱스: right(0), up(1), left(2), down(3)
  const farmDirectionIndex: Record<Direction, number> = {
    right: 0,
    up: 1,
    left: 2,
    down: 3,
  };

  // 현재 설정 계산
  const columns = isHarvesting ? FARM_COLUMNS : IDLE_COLUMNS;
  const framesPerDir = isHarvesting ? FARM_FRAMES_PER_DIR : IDLE_FRAMES_PER_DIR;
  const dirIdx = isHarvesting ? farmDirectionIndex[direction] : idleDirectionIndex[direction];

  // 시작 프레임 계산
  let startFrame: number;
  if (isHarvesting) {
    // dig: 마지막 8프레임 (28-35)
    startFrame = 28;
  } else {
    // idle/walk: Row 1 = idle, Row 2 = walk
    const row = action === 'walk' ? 2 : 1;
    startFrame = (row * IDLE_COLUMNS) + (dirIdx * IDLE_FRAMES_PER_DIR);
  }

  // action 변경 시 프레임 리셋
  useEffect(() => {
    setFrame(0);
  }, [action]);

  // 애니메이션 프레임 업데이트
  // dig: 8프레임 x 3번 = 24프레임 사이클
  const totalFrames = isHarvesting ? 24 : framesPerDir;

  useEffect(() => {
    if (!animated) return;

    // fps 설정: farm=12, walk=10, idle=4
    const fps = isHarvesting ? 12 : (action === 'walk' ? 10 : 4);
    const interval = setInterval(() => {
      setFrame(prev => (prev + 1) % totalFrames);
    }, 1000 / fps);

    return () => clearInterval(interval);
  }, [action, animated, totalFrames, isHarvesting]);

  // 현재 프레임의 X, Y 위치 계산
  // dig: frame이 0-23을 돌지만, 실제 스프라이트는 8프레임이므로 % 연산
  const actualFrame = isHarvesting ? frame % framesPerDir : frame;
  const currentFrameIndex = startFrame + actualFrame;
  const frameX = (currentFrameIndex % columns) * FRAME_WIDTH;
  const frameY = Math.floor(currentFrameIndex / columns) * FRAME_HEIGHT;

  // 스프라이트시트 파일 선택
  const spriteFile = isHarvesting
    ? 'Farmer_1_Dig_36_frames_32x32.png'
    : 'Farmer_1_32x32.png';

  // 캐릭터 크기는 항상 32x64 기준으로 scale 계산
  const scale = size / 32;
  // watering은 프레임이 크므로 부모 div도 크게
  const displayWidth = isHarvesting ? FRAME_WIDTH * scale : size;
  const displayHeight = isHarvesting ? FRAME_HEIGHT * scale : 64 * scale;

  return (
    <div
      className={cn('relative', className)}
      style={{
        width: displayWidth,
        height: displayHeight,
        overflow: 'visible',
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
          width: FRAME_WIDTH,
          height: FRAME_HEIGHT,
          backgroundImage: `url(${FARM_ASSETS.characters}/${spriteFile})`,
          backgroundRepeat: 'no-repeat',
          backgroundPosition: `-${frameX}px -${frameY}px`,
          transform: `scale(${scale})`,
          transformOrigin: 'top left',
          imageRendering: 'pixelated',
        }}
      />
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
// 농장 미니맵 (사이드바용) - 리뉴얼 버전
// ============================================

// 미니맵용 슬롯 타입 (본인/타인 프로필 모두 지원)
export interface MinimapSlot {
  cropCode: string | null;
  stage: number;
  // 정렬용 추가 필드 (optional)
  plantedAt?: string | null;
  growTimeSeconds?: number | null;
}

interface FarmMinimapProps {
  level?: number;
  /** 실제 농장 슬롯 데이터 */
  farmSlots?: MinimapSlot[];
  /** 농장 그리드 크기 (예: 9 = 3x3, 16 = 4x4) */
  farmSize?: number;
  className?: string;
}

// 밭 칸 좌표 (시계방향 순서)
// 밭 영역: left 6%, bottom 18%, width 48%, height 45%
// 그리드 inset: 12% → 실제 그리드 X: 11.76%~48.24%, Y: 42.4%~76.6%
// 셀 중심: 열(18%, 30%, 42%), 행(51%, 68%)
// 그리드 (3x2): [0][1][2] / [3][4][5]
// 시계방향: 0 → 1 → 2 → 5 → 4 → 3 → 0
const FARM_CELL_POSITIONS = [
  { x: 18, y: 48 },  // 칸 0 (좌상)
  { x: 30, y: 48 },  // 칸 1 (중상)
  { x: 42, y: 48 },  // 칸 2 (우상)
  { x: 42, y: 65 },  // 칸 5 (우하)
  { x: 30, y: 65 },  // 칸 4 (중하)
  { x: 18, y: 65 },  // 칸 3 (좌하)
];

// 이동 방향 계산
function getDirection(from: { x: number; y: number }, to: { x: number; y: number }): Direction {
  const dx = to.x - from.x;
  const dy = to.y - from.y;
  if (Math.abs(dx) > Math.abs(dy)) {
    return dx > 0 ? 'right' : 'left';
  }
  return dy > 0 ? 'down' : 'up';
}

// 타이밍 설정 (ms)
const MOVE_DURATION = 2000;   // 이동 시간
const IDLE_BEFORE_FARM = 1500; // 농사 전 대기 (숨쉬기)
const WATER_DURATION = 2500;   // 물뿌리기 시간
const IDLE_AFTER_FARM = 1500;  // 농사 후 대기 (숨쉬기)

/**
 * 농장 미니맵 컴포넌트 (리뉴얼)
 * - 실제 farmSlots 데이터 연동
 * - 상태 머신 기반 농부 움직임
 * - 세련된 픽셀아트 스타일
 */
export function FarmMinimap({
  level = 1,
  farmSlots = [],
  farmSize = 9,
  className,
}: FarmMinimapProps) {
  // 농부 위치를 직접 관리 (x, y 좌표)
  const [farmerPos, setFarmerPos] = useState(FARM_CELL_POSITIONS[0]);
  const [cellIndex, setCellIndex] = useState(0);
  // phase: idle_before → watering → idle_after → moving → idle_before...
  const [phase, setPhase] = useState<'idle_before' | 'watering' | 'idle_after' | 'moving'>('idle_before');
  // 초기 마운트 시 transition 비활성화
  const [isReady, setIsReady] = useState(false);

  // 컴포넌트 마운트 시 초기화
  useEffect(() => {
    // 즉시 첫 번째 위치로 설정 (transition 없이)
    setFarmerPos({ x: 18, y: 48 });
    setCellIndex(0);
    setPhase('idle_before');
    setIsReady(false);

    // 약간의 딜레이 후 애니메이션 활성화
    const readyTimer = setTimeout(() => {
      setIsReady(true);
    }, 100);

    return () => clearTimeout(readyTimer);
  }, []); // 마운트 시 한 번만 실행

  // 상태 머신: idle_before → watering → idle_after → moving → idle_before...
  useEffect(() => {
    if (!isReady) return;

    let timer: NodeJS.Timeout;

    switch (phase) {
      case 'idle_before':
        // 대기 후 물뿌리기 시작
        timer = setTimeout(() => {
          setPhase('watering');
        }, IDLE_BEFORE_FARM);
        break;

      case 'watering':
        // 물뿌리기 후 대기
        timer = setTimeout(() => {
          setPhase('idle_after');
        }, WATER_DURATION);
        break;

      case 'idle_after':
        // 대기 후 이동 시작
        timer = setTimeout(() => {
          setPhase('moving');
          // 다음 위치로 이동 시작
          const nextIdx = (cellIndex + 1) % FARM_CELL_POSITIONS.length;
          setFarmerPos(FARM_CELL_POSITIONS[nextIdx]);
        }, IDLE_AFTER_FARM);
        break;

      case 'moving':
        // 이동 완료 후 다음 칸에서 대기
        timer = setTimeout(() => {
          setCellIndex((prev) => (prev + 1) % FARM_CELL_POSITIONS.length);
          setPhase('idle_before');
        }, MOVE_DURATION);
        break;
    }

    return () => clearTimeout(timer);
  }, [phase, isReady, cellIndex]);

  // 현재 상태에 따른 액션과 방향
  const currentPos = FARM_CELL_POSITIONS[cellIndex];
  const nextIndex = (cellIndex + 1) % FARM_CELL_POSITIONS.length;
  const nextPos = FARM_CELL_POSITIONS[nextIndex];

  // phase에 따른 action 결정
  let action: FarmerAction;
  if (phase === 'moving') {
    action = 'walk';
  } else if (phase === 'watering') {
    action = 'farm';
  } else {
    action = 'idle';
  }

  const direction: Direction = phase === 'moving'
    ? getDirection(currentPos, nextPos)
    : 'down';

  // 그리드 크기 계산 (3x3, 4x4, 5x5 등)
  const gridCols = Math.ceil(Math.sqrt(farmSize));

  // 슬롯 데이터를 작물 정보로 변환
  const displaySlots = farmSlots.slice(0, Math.min(farmSlots.length, 6));
  const hasAnyCrops = displaySlots.some(s => s.cropCode);
  const readyCrops = displaySlots.filter(s => s.stage >= 6).length;

  return (
    <div
      className={cn(
        'relative w-full overflow-hidden select-none',
        'rounded-lg',
        className
      )}
      style={{
        aspectRatio: '16/12',
        background: `
          linear-gradient(180deg,
            #7EC8E3 0%,
            #98D1E8 25%,
            #58A65C 25%,
            #4A9150 60%,
            #3D7A42 100%
          )
        `,
        boxShadow: `
          inset 0 0 0 3px #2D5A30,
          inset 0 0 0 5px #1A3A1C,
          0 4px 12px rgba(0,0,0,0.3)
        `,
      }}
    >
      {/* === 하늘 레이어 === */}
      <div className="absolute inset-0 h-[25%] overflow-hidden">
        {/* 태양 */}
        <div
          className="absolute top-2 right-4 w-8 h-8 rounded-full"
          style={{
            background: 'radial-gradient(circle, #FFE566 30%, #FFB833 70%, transparent 100%)',
            boxShadow: '0 0 20px 8px rgba(255,200,50,0.4)',
            animation: 'pulse 4s ease-in-out infinite',
          }}
        />

        {/* 구름들 */}
        <motion.div
          className="absolute top-3 left-3"
          animate={{ x: [0, 6, 0] }}
          transition={{ duration: 12, repeat: Infinity, ease: 'easeInOut' }}
        >
          <div
            className="w-10 h-4 rounded-full opacity-80"
            style={{
              background: 'linear-gradient(180deg, #fff 0%, #e8f4f8 100%)',
              boxShadow: '6px 0 0 -1px #fff, 12px 2px 0 -2px rgba(255,255,255,0.8)',
            }}
          />
        </motion.div>

        <motion.div
          className="absolute top-5 left-[40%]"
          animate={{ x: [0, 4, 0] }}
          transition={{ duration: 10, repeat: Infinity, ease: 'easeInOut', delay: 2 }}
        >
          <div
            className="w-6 h-3 rounded-full opacity-60"
            style={{
              background: 'linear-gradient(180deg, #fff 0%, #e8f4f8 100%)',
              boxShadow: '4px 0 0 -1px rgba(255,255,255,0.9)',
            }}
          />
        </motion.div>
      </div>

      {/* === 잔디 패턴 (텍스처) === */}
      <div
        className="absolute inset-0 top-[25%] opacity-30 pointer-events-none"
        style={{
          backgroundImage: `
            radial-gradient(circle at 20% 40%, #2D5A30 1px, transparent 1px),
            radial-gradient(circle at 60% 60%, #2D5A30 1px, transparent 1px),
            radial-gradient(circle at 80% 30%, #2D5A30 1px, transparent 1px)
          `,
          backgroundSize: '20px 20px',
        }}
      />

      {/* === 밭 영역 === */}
      <div
        className="absolute left-[6%] bottom-[18%] w-[48%] h-[45%] rounded-sm overflow-hidden"
        style={{
          background: 'linear-gradient(180deg, #8B6B4A 0%, #6B4D32 100%)',
          boxShadow: `
            inset 0 2px 4px rgba(0,0,0,0.4),
            inset 0 -1px 2px rgba(255,255,255,0.1),
            2px 3px 6px rgba(0,0,0,0.3)
          `,
          border: '2px solid #4A3728',
        }}
      >
        {/* 밭 고랑 패턴 */}
        <div
          className="absolute inset-0 opacity-40"
          style={{
            backgroundImage: 'repeating-linear-gradient(0deg, transparent, transparent 8px, rgba(0,0,0,0.2) 8px, rgba(0,0,0,0.2) 9px)',
          }}
        />

        {/* 작물 그리드 - 항상 6칸 (3x2) 표시 */}
        <div
          className="absolute grid grid-cols-3 grid-rows-2 gap-1"
          style={{ inset: '12%' }}
        >
          {Array.from({ length: 6 }).map((_, i) => {
            const slot = displaySlots[i];
            const hasCrop = slot?.cropCode;
            const isReady = slot?.stage >= 6;

            return (
              <div
                key={i}
                className="flex items-center justify-center"
                style={{
                  background: 'linear-gradient(180deg, #6B5540 0%, #584435 100%)',
                  borderRadius: '4px',
                  boxShadow: 'inset 0 1px 2px rgba(255,255,255,0.1), inset 0 -1px 2px rgba(0,0,0,0.2)',
                }}
              >
                {hasCrop && (
                  <div className="relative">
                    <CropSprite
                      type={slot.cropCode as CropVariety}
                      stage={slot.stage as CropStage}
                      size={14}
                    />
                    {isReady && (
                      <motion.div
                        className="absolute -top-0.5 -right-0.5 w-1.5 h-1.5 rounded-full bg-yellow-400"
                        animate={{ scale: [1, 1.3, 1], opacity: [1, 0.7, 1] }}
                        transition={{ duration: 1, repeat: Infinity }}
                        style={{ boxShadow: '0 0 3px #FFD700' }}
                      />
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* === 집 === */}
      <div className="absolute right-[8%] top-[28%]">
        <div className="relative">
          <Image
            src={`${FARM_ASSETS.houses}/${HOUSE_IMAGE_MAP[Math.min(level, 4)]?.src || 'Farmer_House_1_32x32.png'}`}
            alt="House"
            width={56}
            height={64}
            className="drop-shadow-lg"
            style={{
              imageRendering: 'pixelated',
              filter: 'drop-shadow(2px 3px 2px rgba(0,0,0,0.3))',
            }}
            unoptimized
          />
          {/* 레벨 4: 반짝임 */}
          {level >= 4 && (
            <motion.div
              className="absolute -top-1 -right-1 text-xs"
              animate={{ scale: [1, 1.2, 1], rotate: [0, 10, -10, 0] }}
              transition={{ duration: 2, repeat: Infinity }}
            >
              ✨
            </motion.div>
          )}
        </div>
      </div>

      {/* === 농부 (밭 위에서 시계방향 순찰) === */}
      {/* CSS transition 사용 - Framer Motion 내부 상태 문제 방지 */}
      <div
        className="absolute z-10"
        style={{
          left: `${farmerPos.x}%`,
          top: `${farmerPos.y}%`,
          transform: 'translate(-50%, -50%)',
          // 초기화 전에는 transition 없음, 이동 중에만 transition 적용
          transitionProperty: 'left, top',
          transitionDuration: isReady && phase === 'moving' ? `${MOVE_DURATION}ms` : '0ms',
          transitionTimingFunction: 'linear',
        }}
      >
        <FarmerSprite
          action={action}
          direction={direction}
          size={18}
        />
      </div>

      {/* === 장식 요소들 === */}
      {/* 잔디 터프트 */}
      <Image
        src={`${FARM_ASSETS.terrains}/Grass_Tufts_Flowers_32x32_1.png`}
        alt=""
        width={16}
        height={16}
        className="absolute bottom-[8%] right-[35%] opacity-80"
        style={{ imageRendering: 'pixelated' }}
        unoptimized
      />
      <Image
        src={`${FARM_ASSETS.terrains}/Grass_Tufts_Flowers_32x32_3.png`}
        alt=""
        width={14}
        height={14}
        className="absolute bottom-[18%] left-[56%] opacity-70"
        style={{ imageRendering: 'pixelated' }}
        unoptimized
      />

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
