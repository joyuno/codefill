'use client';

import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '@/lib/utils';

/**
 * 게임 스타일 픽셀 아트 스프라이트 컴포넌트
 * - SVG 기반 고품질 픽셀 아트
 * - 농부, 작물, 집, 도구 등 게임 에셋
 */

// ============================================
// 색상 팔레트 (스타듀밸리 스타일)
// ============================================

const PALETTE = {
  // 피부톤
  skin: {
    light: '#FFDAB9',
    medium: '#DEB887',
    tan: '#D2B48C',
  },
  // 머리카락
  hair: {
    brown: '#8B4513',
    black: '#2D2D2D',
    blonde: '#F4D03F',
    red: '#C0392B',
    blue: '#3498DB',
    pink: '#E91E8A',
  },
  // 옷
  clothes: {
    blue: '#3498DB',
    red: '#E74C3C',
    green: '#27AE60',
    purple: '#9B59B6',
    orange: '#E67E22',
  },
  // 농장
  farm: {
    dirt: '#8B5A2B',
    dirtDark: '#6B4423',
    grass: '#7CBA5F',
    grassDark: '#5A9F4A',
  },
  // 건물
  building: {
    wood: '#DEB887',
    woodDark: '#A0522D',
    roof: '#8B4513',
    roofDark: '#654321',
    stone: '#A9A9A9',
    gold: '#FFD700',
  },
};

// ============================================
// 농부 스프라이트 (게임 스타일)
// ============================================

export type FarmerAction = 'idle' | 'walk' | 'farm' | 'water' | 'harvest' | 'sleep';
export type Direction = 'down' | 'up' | 'left' | 'right';

interface FarmerSpriteProps {
  action?: FarmerAction;
  direction?: Direction;
  hairColor?: string;
  clothesColor?: string;
  size?: number;
  className?: string;
  animated?: boolean;
}

export function FarmerSprite({
  action = 'idle',
  direction = 'down',
  hairColor = PALETTE.hair.brown,
  clothesColor = PALETTE.clothes.blue,
  size = 32,
  className,
  animated = true,
}: FarmerSpriteProps) {
  const [frame, setFrame] = useState(0);
  
  // 애니메이션 프레임
  useEffect(() => {
    if (!animated) return;
    
    const fps = action === 'walk' ? 8 : action === 'farm' ? 4 : 2;
    const interval = setInterval(() => {
      setFrame(prev => (prev + 1) % 4);
    }, 1000 / fps);
    
    return () => clearInterval(interval);
  }, [action, animated]);
  
  // 방향에 따른 좌우 반전
  const scaleX = direction === 'left' ? -1 : 1;
  const showBack = direction === 'up';
  
  // 걷기 애니메이션 오프셋
  const walkOffset = action === 'walk' ? Math.sin(frame * Math.PI / 2) * 2 : 0;
  
  // 농사 도구 렌더링
  const renderTool = () => {
    if (action === 'farm') {
      // 낫
      return (
        <g transform={`translate(${12 + Math.sin(frame * Math.PI / 2) * 4}, ${8 - Math.abs(Math.sin(frame * Math.PI / 2) * 3)}) rotate(${-30 + Math.sin(frame * Math.PI / 2) * 40})`}>
          <rect x="0" y="0" width="2" height="10" fill="#8B4513" />
          <path d="M0,0 Q-3,-2 -5,3 L-3,4 Q-2,1 0,2 Z" fill="#A9A9A9" />
        </g>
      );
    }
    if (action === 'water') {
      // 물뿌리개
      return (
        <g transform={`translate(12, 10) rotate(${Math.sin(frame * Math.PI / 2) * 15})`}>
          <ellipse cx="0" cy="2" rx="4" ry="3" fill="#3498DB" />
          <rect x="3" y="0" width="6" height="2" fill="#2980B9" />
          <circle cx="9" cy="1" r="1" fill="#5DADE2" />
        </g>
      );
    }
    return null;
  };
  
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 16 20"
      className={cn('', className)}
      style={{ 
        imageRendering: 'pixelated',
        transform: `scaleX(${scaleX})`,
      }}
    >
      {/* 그림자 */}
      <ellipse cx="8" cy="19" rx="5" ry="1.5" fill="rgba(0,0,0,0.2)" />
      
      {/* 다리 (걷기 애니메이션) */}
      <g transform={`translate(0, ${walkOffset})`}>
        <rect x="5" y="14" width="2" height="4" fill="#34495E" />
        <rect x="9" y="14" width="2" height="4" fill="#34495E" />
        {action === 'walk' && (
          <>
            <rect x="5" y="14" width="2" height="4" fill="#34495E" 
              transform={`translate(${Math.sin(frame * Math.PI / 2) * 1}, 0)`} />
            <rect x="9" y="14" width="2" height="4" fill="#34495E"
              transform={`translate(${-Math.sin(frame * Math.PI / 2) * 1}, 0)`} />
          </>
        )}
      </g>
      
      {/* 신발 */}
      <rect x="4" y="17" width="3" height="2" fill="#5D4037" />
      <rect x="9" y="17" width="3" height="2" fill="#5D4037" />
      
      {/* 몸통 */}
      <rect x="4" y="9" width="8" height="6" fill={clothesColor} />
      
      {/* 팔 */}
      <g>
        {/* 왼팔 */}
        <rect x="2" y="9" width="3" height="5" fill={clothesColor} />
        <rect x="2" y="13" width="2" height="2" fill={PALETTE.skin.light} />
        
        {/* 오른팔 */}
        <rect x="11" y="9" width="3" height="5" fill={clothesColor} 
          transform={action === 'farm' ? `rotate(${-20 + Math.sin(frame * Math.PI / 2) * 30}, 12, 9)` : ''} />
        <rect x="12" y="13" width="2" height="2" fill={PALETTE.skin.light} />
      </g>
      
      {/* 머리 */}
      <rect x="4" y="3" width="8" height="7" fill={PALETTE.skin.light} />
      
      {/* 머리카락 */}
      {!showBack ? (
        <>
          <rect x="4" y="1" width="8" height="3" fill={hairColor} />
          <rect x="3" y="2" width="2" height="3" fill={hairColor} />
          <rect x="11" y="2" width="2" height="3" fill={hairColor} />
        </>
      ) : (
        <rect x="3" y="1" width="10" height="8" fill={hairColor} />
      )}
      
      {/* 얼굴 (앞면만) */}
      {!showBack && (
        <>
          {/* 눈 */}
          <rect x="5" y="5" width="2" height="2" fill="#2D2D2D" />
          <rect x="9" y="5" width="2" height="2" fill="#2D2D2D" />
          {/* 눈 하이라이트 */}
          <rect x="5" y="5" width="1" height="1" fill="#FFFFFF" />
          <rect x="9" y="5" width="1" height="1" fill="#FFFFFF" />
          {/* 입 */}
          <rect x="7" y="8" width="2" height="1" fill="#E74C3C" />
        </>
      )}
      
      {/* 농사 도구 */}
      {renderTool()}
      
      {/* 밀짚모자 */}
      <rect x="2" y="0" width="12" height="2" fill="#F4D03F" />
      <rect x="4" y="-1" width="8" height="2" fill="#DAA520" />
      
      {/* 수확 이펙트 */}
      {action === 'harvest' && (
        <motion.g
          initial={{ opacity: 0, y: 0 }}
          animate={{ opacity: [1, 0], y: -10 }}
          transition={{ duration: 0.5, repeat: Infinity }}
        >
          <text x="8" y="-5" textAnchor="middle" fontSize="4" fill="#FFD700">✨</text>
        </motion.g>
      )}
    </svg>
  );
}

// ============================================
// 작물 스프라이트 (땅에 묻힌 스타일)
// ============================================

export type CropStage = 0 | 1 | 2 | 3 | 4;
export type CropVariety = 'carrot' | 'tomato' | 'corn' | 'strawberry' | 'potato' | 'wheat' | 'pumpkin';

interface CropSpriteProps {
  type?: CropVariety;
  stage?: CropStage;
  size?: number;
  withTimer?: boolean;
  remainingSeconds?: number;
  className?: string;
}

const CROP_COLORS: Record<CropVariety, { fruit: string; leaf: string }> = {
  carrot: { fruit: '#E67E22', leaf: '#27AE60' },
  tomato: { fruit: '#E74C3C', leaf: '#27AE60' },
  corn: { fruit: '#F1C40F', leaf: '#27AE60' },
  strawberry: { fruit: '#FF6B6B', leaf: '#27AE60' },
  potato: { fruit: '#D4A574', leaf: '#27AE60' },
  wheat: { fruit: '#DAA520', leaf: '#8B7355' },
  pumpkin: { fruit: '#FF8C00', leaf: '#27AE60' },
};

export function CropSprite({
  type = 'tomato',
  stage = 0,
  size = 32,
  withTimer = false,
  remainingSeconds = 0,
  className,
}: CropSpriteProps) {
  const colors = CROP_COLORS[type];
  
  return (
    <div className={cn('relative', className)} style={{ width: size, height: size }}>
      <svg
        width={size}
        height={size}
        viewBox="0 0 16 16"
        style={{ imageRendering: 'pixelated' }}
      >
        {/* 흙 배경 */}
        <rect x="0" y="10" width="16" height="6" fill={PALETTE.farm.dirt} />
        <rect x="2" y="11" width="3" height="1" fill={PALETTE.farm.dirtDark} />
        <rect x="8" y="12" width="4" height="1" fill={PALETTE.farm.dirtDark} />
        <rect x="12" y="11" width="2" height="1" fill={PALETTE.farm.dirtDark} />
        
        {/* 단계별 작물 */}
        {stage === 0 && (
          // 빈 땅
          <g>
            <rect x="6" y="9" width="4" height="2" fill={PALETTE.farm.dirtDark} />
          </g>
        )}
        
        {stage === 1 && (
          // 씨앗
          <g>
            <rect x="7" y="8" width="2" height="3" fill="#5D4037" />
            <circle cx="8" cy="8" r="1" fill="#8D6E63" />
          </g>
        )}
        
        {stage === 2 && (
          // 새싹
          <g>
            <rect x="7" y="6" width="2" height="5" fill="#27AE60" />
            <rect x="5" y="5" width="2" height="2" fill="#2ECC71" />
            <rect x="9" y="5" width="2" height="2" fill="#2ECC71" />
          </g>
        )}
        
        {stage === 3 && (
          // 성장 중
          <g>
            <rect x="7" y="4" width="2" height="7" fill={colors.leaf} />
            <rect x="4" y="3" width="3" height="3" fill={colors.leaf} />
            <rect x="9" y="3" width="3" height="3" fill={colors.leaf} />
            <rect x="6" y="1" width="4" height="3" fill={colors.leaf} />
          </g>
        )}
        
        {stage === 4 && (
          // 수확 가능
          <g>
            {/* 줄기/잎 */}
            <rect x="7" y="6" width="2" height="5" fill={colors.leaf} />
            <rect x="4" y="5" width="3" height="2" fill={colors.leaf} />
            <rect x="9" y="5" width="3" height="2" fill={colors.leaf} />
            
            {/* 열매 (땅에서 올라온 형태) */}
            <rect x="4" y="0" width="8" height="6" fill={colors.fruit} rx="1" />
            <rect x="5" y="-1" width="6" height="2" fill={colors.fruit} />
            
            {/* 하이라이트 */}
            <rect x="5" y="1" width="2" height="2" fill="rgba(255,255,255,0.4)" />
            
            {/* 꼭지 */}
            <rect x="7" y="-2" width="2" height="2" fill="#27AE60" />
          </g>
        )}
      </svg>
      
      {/* 타이머 표시 */}
      {withTimer && stage > 0 && stage < 4 && remainingSeconds > 0 && (
        <div className="absolute bottom-0 left-0 right-0 bg-black/70 text-[8px] text-center text-amber-300 font-mono py-0.5">
          {Math.floor(remainingSeconds / 60)}:{(remainingSeconds % 60).toString().padStart(2, '0')}
        </div>
      )}
    </div>
  );
}

// ============================================
// 집 스프라이트 (레벨별 크기)
// ============================================

interface HouseSpriteProps {
  level?: 1 | 2 | 3 | 4;
  gridSize?: number; // 기본 그리드 셀 크기
  className?: string;
  showFarmerInside?: boolean;
}

// 레벨별 집 크기 (그리드 셀 단위)
const HOUSE_SIZES: Record<number, { width: number; height: number }> = {
  1: { width: 2, height: 2 }, // 2x2
  2: { width: 3, height: 3 }, // 3x3
  3: { width: 4, height: 4 }, // 4x4
  4: { width: 5, height: 5 }, // 5x5
};

const HOUSE_STYLES: Record<number, { roof: string; wall: string; name: string }> = {
  1: { roof: '#8B4513', wall: '#DEB887', name: '초가집' },
  2: { roof: '#A0522D', wall: '#D2B48C', name: '나무집' },
  3: { roof: '#708090', wall: '#A9A9A9', name: '벽돌집' },
  4: { roof: '#FFD700', wall: '#FFF8DC', name: '황금저택' },
};

export function HouseSprite({
  level = 1,
  gridSize = 24,
  className,
  showFarmerInside = false,
}: HouseSpriteProps) {
  const houseSize = HOUSE_SIZES[level];
  const style = HOUSE_STYLES[level];
  const width = houseSize.width * gridSize;
  const height = houseSize.height * gridSize;
  
  return (
    <div 
      className={cn('relative', className)}
      style={{ width, height }}
    >
      <svg
        width={width}
        height={height}
        viewBox={`0 0 ${houseSize.width * 16} ${houseSize.height * 16}`}
        style={{ imageRendering: 'pixelated' }}
      >
        {/* 지붕 */}
        <polygon
          points={`${houseSize.width * 8},2 ${houseSize.width * 16 - 2},${houseSize.height * 6} 2,${houseSize.height * 6}`}
          fill={style.roof}
        />
        <polygon
          points={`${houseSize.width * 8},4 ${houseSize.width * 16 - 4},${houseSize.height * 6 - 2} 4,${houseSize.height * 6 - 2}`}
          fill={level === 4 ? '#FFEC8B' : '#CD853F'}
        />
        
        {/* 굴뚝 (레벨 2 이상) */}
        {level >= 2 && (
          <g>
            <rect 
              x={houseSize.width * 12} 
              y={houseSize.height * 2} 
              width={houseSize.width * 2} 
              height={houseSize.height * 4} 
              fill="#696969" 
            />
            {/* 연기 */}
            <motion.circle
              cx={houseSize.width * 13}
              cy={houseSize.height}
              r={2}
              fill="rgba(200,200,200,0.6)"
              animate={{ y: [-2, -8], opacity: [0.6, 0] }}
              transition={{ duration: 2, repeat: Infinity }}
            />
          </g>
        )}
        
        {/* 벽 */}
        <rect
          x={2}
          y={houseSize.height * 6}
          width={houseSize.width * 16 - 4}
          height={houseSize.height * 10 - 2}
          fill={style.wall}
        />
        
        {/* 문 */}
        <rect
          x={houseSize.width * 6}
          y={houseSize.height * 10}
          width={houseSize.width * 4}
          height={houseSize.height * 6}
          fill="#654321"
        />
        {/* 문 손잡이 */}
        <circle
          cx={houseSize.width * 9}
          cy={houseSize.height * 13}
          r={1}
          fill="#FFD700"
        />
        
        {/* 창문 */}
        <rect
          x={houseSize.width * 2}
          y={houseSize.height * 8}
          width={houseSize.width * 3}
          height={houseSize.height * 3}
          fill="#87CEEB"
        />
        <rect
          x={houseSize.width * 11}
          y={houseSize.height * 8}
          width={houseSize.width * 3}
          height={houseSize.height * 3}
          fill="#87CEEB"
        />
        {/* 창문 격자 */}
        <line x1={houseSize.width * 3.5} y1={houseSize.height * 8} x2={houseSize.width * 3.5} y2={houseSize.height * 11} stroke={style.wall} strokeWidth="1" />
        <line x1={houseSize.width * 2} y1={houseSize.height * 9.5} x2={houseSize.width * 5} y2={houseSize.height * 9.5} stroke={style.wall} strokeWidth="1" />
        
        {/* 레벨 4 특수 장식 */}
        {level === 4 && (
          <>
            {/* 깃발 */}
            <rect x={houseSize.width * 8 - 1} y={0} width={2} height={4} fill="#8B4513" />
            <polygon 
              points={`${houseSize.width * 8 + 1},0 ${houseSize.width * 8 + 6},2 ${houseSize.width * 8 + 1},4`} 
              fill="#FF0000" 
            />
            {/* 기둥 장식 */}
            <rect x={0} y={houseSize.height * 6} width={3} height={houseSize.height * 10} fill="#DAA520" />
            <rect x={houseSize.width * 16 - 3} y={houseSize.height * 6} width={3} height={houseSize.height * 10} fill="#DAA520" />
          </>
        )}
      </svg>
      
      {/* 집 안의 농부 표시 */}
      {showFarmerInside && (
        <motion.div
          className="absolute"
          style={{
            left: houseSize.width * gridSize / 2 - 8,
            top: houseSize.height * gridSize * 0.7,
          }}
          animate={{ opacity: [1, 0.5, 1] }}
          transition={{ duration: 2, repeat: Infinity }}
        >
          <div className="w-4 h-4 bg-yellow-400 rounded-full" />
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
        setFarmerPos({ x: 20 + Math.random() * 30, y: 40 + Math.random() * 20 });
        setTimeout(() => setFarmerAction('idle'), 2000);
      } else if (random < 0.5) {
        // 20% 확률로 물주기
        setFarmerAction('water');
        setTimeout(() => setFarmerAction('idle'), 1500);
      } else {
        // 50% 확률로 걷기
        setFarmerAction('walk');
        const newX = Math.max(10, Math.min(80, farmerPos.x + (Math.random() - 0.5) * 30));
        const newY = Math.max(30, Math.min(70, farmerPos.y + (Math.random() - 0.5) * 20));
        
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
        'relative rounded-xl overflow-hidden',
        'bg-gradient-to-b from-sky-300 to-sky-200',
        'border-4 border-amber-800',
        'shadow-[4px_4px_0_0_#78350f]',
        className
      )}
      style={{ 
        aspectRatio: '1',
        backgroundImage: `
          radial-gradient(circle at 80% 20%, rgba(255,255,255,0.3) 0%, transparent 30%)
        `,
      }}
    >
      {/* 잔디 바닥 */}
      <div 
        className="absolute bottom-0 left-0 right-0 h-3/4"
        style={{
          background: `
            linear-gradient(to bottom, ${PALETTE.farm.grass} 0%, ${PALETTE.farm.grassDark} 100%)
          `,
          backgroundImage: `
            radial-gradient(circle at 20% 30%, rgba(46, 204, 113, 0.3) 2px, transparent 2px),
            radial-gradient(circle at 60% 70%, rgba(39, 174, 96, 0.3) 2px, transparent 2px),
            radial-gradient(circle at 80% 20%, rgba(46, 204, 113, 0.3) 2px, transparent 2px)
          `,
          backgroundSize: '20px 20px',
        }}
      />
      
      {/* 밭 영역 */}
      <div 
        className="absolute left-[10%] top-[40%] w-[40%] h-[35%] rounded"
        style={{ backgroundColor: PALETTE.farm.dirt }}
      >
        {/* 작물 그리드 */}
        <div className="grid grid-cols-3 gap-0.5 p-1 h-full">
          {crops.slice(0, 6).map((crop, i) => (
            <div key={i} className="flex items-center justify-center">
              <CropSprite type={crop.type} stage={crop.stage} size={16} />
            </div>
          ))}
        </div>
      </div>
      
      {/* 집 */}
      <div 
        className="absolute right-[5%] top-[15%]"
        style={{
          width: `${houseSize.width * 12}%`,
          height: `${houseSize.height * 12}%`,
        }}
      >
        <HouseSprite level={level as 1 | 2 | 3 | 4} gridSize={16} showFarmerInside={isInHouse} />
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
            size={24}
          />
        </motion.div>
      )}
      
      {/* 해/구름 장식 */}
      <motion.div
        className="absolute top-2 right-2 text-2xl"
        animate={{ rotate: [0, 10, 0] }}
        transition={{ duration: 4, repeat: Infinity }}
      >
        ☀️
      </motion.div>
      
      <motion.div
        className="absolute top-4 left-4 text-lg opacity-70"
        animate={{ x: [0, 10, 0] }}
        transition={{ duration: 8, repeat: Infinity }}
      >
        ☁️
      </motion.div>
    </div>
  );
}

// ============================================
// 도구 스프라이트
// ============================================

interface ToolSpriteProps {
  type: 'hoe' | 'sickle' | 'wateringCan' | 'axe' | 'pickaxe';
  size?: number;
  className?: string;
}

export function ToolSprite({ type, size = 24, className }: ToolSpriteProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 16 16"
      className={className}
      style={{ imageRendering: 'pixelated' }}
    >
      {type === 'sickle' && (
        <g>
          <rect x="7" y="8" width="2" height="8" fill="#8B4513" />
          <path d="M3,2 Q1,4 2,7 L5,8 Q4,5 5,3 Z" fill="#A9A9A9" />
          <path d="M4,3 Q3,5 4,6 L5,7 Q4,5 5,4 Z" fill="#C0C0C0" />
        </g>
      )}
      
      {type === 'hoe' && (
        <g>
          <rect x="7" y="4" width="2" height="12" fill="#8B4513" />
          <rect x="4" y="2" width="8" height="3" fill="#A9A9A9" />
        </g>
      )}
      
      {type === 'wateringCan' && (
        <g>
          <ellipse cx="8" cy="10" rx="5" ry="4" fill="#3498DB" />
          <rect x="10" y="6" width="6" height="2" fill="#2980B9" />
          <circle cx="15" cy="7" r="1" fill="#5DADE2" />
          <rect x="6" y="5" width="4" height="2" fill="#2980B9" />
        </g>
      )}
      
      {type === 'axe' && (
        <g>
          <rect x="7" y="4" width="2" height="12" fill="#8B4513" />
          <polygon points="2,2 10,2 10,6 6,8 2,6" fill="#A9A9A9" />
        </g>
      )}
      
      {type === 'pickaxe' && (
        <g>
          <rect x="7" y="6" width="2" height="10" fill="#8B4513" />
          <polygon points="1,4 15,4 13,7 3,7" fill="#A9A9A9" />
        </g>
      )}
    </svg>
  );
}

