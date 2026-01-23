'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Dialog,
  DialogContent,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { cn } from '@/lib/utils';
import {
  ChevronRight,
  ChevronLeft,
  Sparkles,
  Home,
  User,
  Loader2,
} from 'lucide-react';

interface CharacterCreationModalProps {
  open: boolean;
  onClose: () => void;
  onComplete: (character: CharacterData) => void;
  /** 수정 모드 (기존 캐릭터 데이터 전달) */
  initialData?: CharacterData | null;
  /** 수정 모드 여부 */
  isEditing?: boolean;
  /** 생성/수정 중 로딩 상태 */
  isLoading?: boolean;
  /** 에러 메시지 */
  error?: string | null;
}

export interface CharacterData {
  name: string;
  appearance: {
    body: string;       // Body_1 ~ Body_9
    hair: string;       // Hairstyle ID (Short, Long 등)
    hairColor: string;  // Hair color ID (Brown_Dark 등)
    face: string;       // Eyes_Brown 등
    clothes: string;    // Outfit_Dungarees_Green 등
    accessory: string;  // Accessory_Straw_Hat_Green 등 또는 'none'
    color: string;      // hex color (#3d2314)
  };
  farmName: string;
}

// ============================================================
// 에셋 옵션 정의 - Modern Farm 에셋 기반
// ============================================================

// Body (피부색) 옵션 - 실제 스프라이트 색상 기반
const BODY_OPTIONS = [
  { id: 'Body_2', label: '밝은 피부 1' },
  { id: 'Body_3', label: '밝은 피부 2' },
  { id: 'Body_5', label: '페일' },
  { id: 'Body_7', label: '피치' },
  { id: 'Body_1', label: '탄 피부 1' },
  { id: 'Body_4', label: '탄 피부 2' },
  { id: 'Body_6', label: '그레이 베이지' },
  { id: 'Body_8', label: '핑크 (판타지)' },
  { id: 'Body_9', label: '라벤더 (판타지)' },
];

// Eye 옵션
const EYE_OPTIONS = [
  { id: 'Eyes_Brown', label: '갈색', color: '#8B4513' },
  { id: 'Eyes_Blue', label: '파랑', color: '#3498db' },
  { id: 'Eyes_Green', label: '초록', color: '#27ae60' },
  { id: 'Eyes_Gray', label: '회색', color: '#7f8c8d' },
  { id: 'Eyes_Orange', label: '주황', color: '#e67e22' },
];

// Hairstyle 스타일 옵션
const HAIRSTYLE_TYPES = [
  { id: 'Short', label: '숏컷' },
  { id: 'Long', label: '긴머리' },
  { id: 'Tuft', label: '곱슬' },
  { id: 'Unkept', label: '헝클어진' },
  { id: 'Balding', label: '대머리' },
];

// 머리색 옵션
const HAIR_COLORS = [
  { id: 'Brown_Dark', label: '검은 갈색', color: '#3d2314' },
  { id: 'Brown_Hazel', label: '헤이즐', color: '#6b4423' },
  { id: 'Brown_Light', label: '밝은 갈색', color: '#8b6914' },
  { id: 'Brown_Ash', label: '애쉬 브라운', color: '#696969' },
  { id: 'Blonde', label: '금발', color: '#f4d03f' },
  { id: 'Blonde_Ash', label: '애쉬 금발', color: '#c4b998' },
  { id: 'Orange', label: '주황', color: '#d35400' },
  { id: 'Blue', label: '파랑', color: '#3498db' },
  { id: 'Gray', label: '회색', color: '#95a5a6' },
];

// Outfit 옵션
const OUTFIT_OPTIONS = [
  { id: 'Outfit_Dungarees_Green', label: '멜빵바지 (초록)', preview: '🥬' },
  { id: 'Outfit_Dungarees_Red', label: '멜빵바지 (빨강)', preview: '🍎' },
  { id: 'Outfit_Dungarees_Violet', label: '멜빵바지 (보라)', preview: '🍇' },
  { id: 'Outfit_Dungarees_Black', label: '멜빵바지 (검정)', preview: '🖤' },
  { id: 'Outfit_Laborer_Blue', label: '작업복 (파랑)', preview: '💙' },
  { id: 'Outfit_Laborer_Red', label: '작업복 (빨강)', preview: '❤️' },
  { id: 'Outfit_Laborer_Violet', label: '작업복 (보라)', preview: '💜' },
  { id: 'Outfit_Vest_Brown', label: '조끼 (갈색)', preview: '🤎' },
  { id: 'Outfit_Vest_Brown_Light', label: '조끼 (밝은 갈색)', preview: '🧡' },
  { id: 'Outfit_Vest_Yellow', label: '조끼 (노랑)', preview: '💛' },
  { id: 'Outfit_Braces_Brown', label: '멜빵 (갈색)', preview: '🟤' },
  { id: 'Outfit_Braces_Green', label: '멜빵 (초록)', preview: '💚' },
  { id: 'Outfit_Braces_Orange', label: '멜빵 (주황)', preview: '🧡' },
];

// Accessory 옵션
const ACCESSORY_OPTIONS = [
  { id: 'none', label: '없음', preview: '❌' },
  { id: 'Accessory_Straw_Hat_Green', label: '밀짚모자 (초록)', preview: '🎩' },
  { id: 'Accessory_Straw_Hat_Red', label: '밀짚모자 (빨강)', preview: '🎩' },
  { id: 'Accessory_Straw_Hat_Cyan', label: '밀짚모자 (하늘)', preview: '🎩' },
  { id: 'Accessory_Straw_Hat_Violet', label: '밀짚모자 (보라)', preview: '🎩' },
  { id: 'Accessory_Straw_Hat_Black', label: '밀짚모자 (검정)', preview: '🎩' },
  { id: 'Accessory_Bamboo_Hat_Brown', label: '삿갓 (갈색)', preview: '🍃' },
  { id: 'Accessory_Bamboo_Hat_Brown_Dull', label: '삿갓 (회갈색)', preview: '🍃' },
  { id: 'Accessory_Gas_Mask', label: '가스 마스크', preview: '😷' },
];

// ============================================================
// 화살표 버튼 컴포넌트
// ============================================================

interface ArrowButtonProps {
  direction: 'left' | 'right';
  onClick: () => void;
  disabled?: boolean;
}

function ArrowButton({ direction, onClick, disabled }: ArrowButtonProps) {
  return (
    <motion.button
      type="button"
      onClick={onClick}
      disabled={disabled}
      whileHover={{ scale: 1.1 }}
      whileTap={{ scale: 0.9 }}
      className={cn(
        'w-8 h-8 flex items-center justify-center',
        'bg-amber-200 hover:bg-amber-300',
        'border-2 border-amber-600 rounded',
        'shadow-[2px_2px_0_0_#92400e]',
        'disabled:opacity-50 disabled:cursor-not-allowed',
        'transition-colors'
      )}
    >
      {direction === 'left' ? (
        <ChevronLeft className="w-5 h-5 text-amber-800" />
      ) : (
        <ChevronRight className="w-5 h-5 text-amber-800" />
      )}
    </motion.button>
  );
}

// ============================================================
// 옵션 선택 행 컴포넌트
// ============================================================

interface OptionRowProps {
  label: string;
  value: string;
  valueLabel?: string;
  onPrev: () => void;
  onNext: () => void;
  colorPreview?: string;
}

function OptionRow({ label, value, valueLabel, onPrev, onNext, colorPreview }: OptionRowProps) {
  return (
    <div className="flex items-center gap-2">
      <ArrowButton direction="left" onClick={onPrev} />
      <div className="flex-1 flex items-center gap-2 min-w-0">
        <span className="text-amber-800 font-bold text-xs w-16 shrink-0">{label}</span>
        {colorPreview && (
          <div
            className="w-4 h-4 rounded border-2 border-amber-700 shrink-0"
            style={{ backgroundColor: colorPreview }}
          />
        )}
        <span className="text-amber-900 text-xs truncate">
          {valueLabel || value}
        </span>
      </div>
      <ArrowButton direction="right" onClick={onNext} />
    </div>
  );
}

// ============================================================
// 캐릭터 프리뷰 컴포넌트 (Canvas 기반 스프라이트시트 레이어 합성)
// ============================================================

// 스프라이트시트 설정 (1792x704, 32x64 프레임)
const SPRITE_CONFIG = {
  frameWidth: 32,
  frameHeight: 64,
  columns: 56,        // 1792 / 32
  rows: 11,           // 704 / 64
  framesPerDirection: 6,
  // 방향 인덱스: right(0), up(1), left(2), down(3)
  directions: { right: 0, up: 1, left: 2, down: 3 },
  // 행 구조
  rowMap: { static: 0, idle: 1, walk: 2 },
};

interface CharacterPreviewProps {
  body: string;
  eyes: string;
  hairstyle: string;
  hairColor: string;
  outfit: string;
  accessory: string;
  size?: number;
  direction?: 'down' | 'up' | 'left' | 'right';
  animate?: boolean;
}

function CharacterPreview({
  body,
  eyes,
  hairstyle,
  hairColor,
  outfit,
  accessory,
  size = 128,
  direction = 'down',
  animate = true,
}: CharacterPreviewProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const imagesRef = useRef<Map<string, HTMLImageElement>>(new Map());
  const frameRef = useRef(0);
  const animationRef = useRef<number | null>(null);

  // 헤어스타일 파일명 조합
  const hairstyleFile = `Hairstyle_${hairstyle}_${hairColor}`;

  // 레이어 정의 (아래→위 순서)
  const layers = [
    { key: 'body', path: `/farm/character-pieces/bodies/${body}.png` },
    { key: 'eyes', path: `/farm/character-pieces/eyes/${eyes}.png` },
    { key: 'outfit', path: `/farm/character-pieces/outfits/${outfit}.png` },
    { key: 'hair', path: `/farm/character-pieces/hairstyles/${hairstyleFile}.png` },
  ];

  if (accessory !== 'none') {
    layers.push({ key: 'accessory', path: `/farm/character-pieces/accessories/${accessory}.png` });
  }

  // 특정 프레임 좌표 계산 (idle 애니메이션 사용)
  const getFrameCoords = useCallback((frame: number) => {
    const { columns, framesPerDirection, directions, rowMap } = SPRITE_CONFIG;
    const dirIndex = directions[direction];
    // idle row에서 해당 방향의 프레임
    const startCol = dirIndex * framesPerDirection;
    const col = startCol + (frame % framesPerDirection);
    const row = rowMap.idle;

    return {
      sx: col * SPRITE_CONFIG.frameWidth,
      sy: row * SPRITE_CONFIG.frameHeight,
      sw: SPRITE_CONFIG.frameWidth,
      sh: SPRITE_CONFIG.frameHeight,
    };
  }, [direction]);

  // 이미지 로드
  useEffect(() => {
    const loadImage = (src: string): Promise<HTMLImageElement> => {
      return new Promise((resolve, reject) => {
        // 캐시된 이미지 사용
        if (imagesRef.current.has(src)) {
          resolve(imagesRef.current.get(src)!);
          return;
        }

        const img = new Image();
        img.crossOrigin = 'anonymous';
        img.onload = () => {
          imagesRef.current.set(src, img);
          resolve(img);
        };
        img.onerror = () => reject(new Error(`Failed to load ${src}`));
        img.src = src;
      });
    };

    // 모든 레이어 이미지 로드
    Promise.all(layers.map(l => loadImage(l.path).catch(() => null)))
      .then(() => {
        // 첫 프레임 렌더링
        renderFrame(0);
      });
  }, [body, eyes, hairstyle, hairColor, outfit, accessory]);

  // 프레임 렌더링
  const renderFrame = useCallback((frame: number) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // 캔버스 클리어
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // 픽셀아트 설정
    ctx.imageSmoothingEnabled = false;

    const coords = getFrameCoords(frame);

    // 레이어 순서대로 그리기
    layers.forEach(({ path }) => {
      const img = imagesRef.current.get(path);
      if (img && img.complete) {
        ctx.drawImage(
          img,
          coords.sx, coords.sy, coords.sw, coords.sh,  // 소스 (스프라이트시트에서 잘라낼 영역)
          0, 0, canvas.width, canvas.height             // 대상 (캔버스 전체에 그리기)
        );
      }
    });
  }, [layers, getFrameCoords]);

  // 애니메이션 루프
  useEffect(() => {
    if (!animate) {
      renderFrame(0);
      return;
    }

    let lastTime = 0;
    const frameInterval = 150; // 150ms per frame

    const animationLoop = (time: number) => {
      if (time - lastTime >= frameInterval) {
        frameRef.current = (frameRef.current + 1) % SPRITE_CONFIG.framesPerDirection;
        renderFrame(frameRef.current);
        lastTime = time;
      }
      animationRef.current = requestAnimationFrame(animationLoop);
    };

    animationRef.current = requestAnimationFrame(animationLoop);

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [animate, renderFrame]);

  // 방향 변경 시 다시 렌더링
  useEffect(() => {
    renderFrame(frameRef.current);
  }, [direction, renderFrame]);

  // 스케일 계산 (32x64 → size x size*2)
  const scale = size / SPRITE_CONFIG.frameWidth;
  const canvasWidth = SPRITE_CONFIG.frameWidth * scale;
  const canvasHeight = SPRITE_CONFIG.frameHeight * scale;

  return (
    <canvas
      ref={canvasRef}
      width={canvasWidth}
      height={canvasHeight}
      style={{
        width: canvasWidth,
        height: canvasHeight,
        imageRendering: 'pixelated',
      }}
    />
  );
}

// ============================================================
// 메인 모달 컴포넌트
// ============================================================

export function CharacterCreationModal({
  open,
  onClose,
  onComplete,
  initialData,
  isEditing = false,
  isLoading = false,
  error = null,
}: CharacterCreationModalProps) {
  // 입력 상태
  const [name, setName] = useState('');
  const [farmName, setFarmName] = useState('');

  // 외모 상태
  const [bodyIndex, setBodyIndex] = useState(2);
  const [eyeIndex, setEyeIndex] = useState(0);
  const [hairstyleIndex, setHairstyleIndex] = useState(0);
  const [hairColorIndex, setHairColorIndex] = useState(0);
  const [outfitIndex, setOutfitIndex] = useState(0);
  const [accessoryIndex, setAccessoryIndex] = useState(0);

  // 미리보기 방향 상태
  const [previewDirection, setPreviewDirection] = useState<'down' | 'up' | 'left' | 'right'>('down');

  // 수정 모드: 모달 열릴 때 초기값 설정
  useEffect(() => {
    if (open && initialData) {
      setName(initialData.name);
      setFarmName(initialData.farmName);

      // body index 찾기
      const bodyIdx = BODY_OPTIONS.findIndex(b => b.id === initialData.appearance.body);
      if (bodyIdx >= 0) setBodyIndex(bodyIdx);

      // eyes index 찾기
      const eyeIdx = EYE_OPTIONS.findIndex(e => e.id === initialData.appearance.face);
      if (eyeIdx >= 0) setEyeIndex(eyeIdx);

      // hairstyle index 찾기
      const hairIdx = HAIRSTYLE_TYPES.findIndex(h => h.id === initialData.appearance.hair);
      if (hairIdx >= 0) setHairstyleIndex(hairIdx);

      // hairColor index 찾기
      const hairColorIdx = HAIR_COLORS.findIndex(c => c.id === initialData.appearance.hairColor);
      if (hairColorIdx >= 0) setHairColorIndex(hairColorIdx);

      // outfit index 찾기
      const outfitIdx = OUTFIT_OPTIONS.findIndex(o => o.id === initialData.appearance.clothes);
      if (outfitIdx >= 0) setOutfitIndex(outfitIdx);

      // accessory index 찾기
      const accIdx = ACCESSORY_OPTIONS.findIndex(a => a.id === initialData.appearance.accessory);
      if (accIdx >= 0) setAccessoryIndex(accIdx);
    } else if (open && !initialData) {
      // 새 캐릭터 생성 모드: 초기화
      setName('');
      setFarmName('');
      setBodyIndex(2);
      setEyeIndex(0);
      setHairstyleIndex(0);
      setHairColorIndex(0);
      setOutfitIndex(0);
      setAccessoryIndex(0);
    }
  }, [open, initialData]);

  // 현재 선택값
  const currentBody = BODY_OPTIONS[bodyIndex];
  const currentEye = EYE_OPTIONS[eyeIndex];
  const currentHairstyle = HAIRSTYLE_TYPES[hairstyleIndex];
  const currentHairColor = HAIR_COLORS[hairColorIndex];
  const currentOutfit = OUTFIT_OPTIONS[outfitIndex];
  const currentAccessory = ACCESSORY_OPTIONS[accessoryIndex];

  // 순환 함수
  const cycle = (current: number, length: number, direction: 1 | -1) => {
    return (current + direction + length) % length;
  };

  // 완료 가능 여부
  const canComplete = name.length >= 2;

  // 완료 핸들러
  const handleComplete = () => {
    const character: CharacterData = {
      name: name || '코드냥',
      appearance: {
        body: currentBody.id,
        hair: currentHairstyle.id,
        hairColor: currentHairColor.id,
        face: currentEye.id,
        clothes: currentOutfit.id,
        accessory: currentAccessory.id,
        color: currentHairColor.color,
      },
      farmName: farmName || `${name || '코드냥'}의 농장`,
    };
    onComplete(character);
  };

  // 로딩 중에는 모달 닫기 방지
  const handleOpenChange = (newOpen: boolean) => {
    if (!newOpen && isLoading) {
      return; // 로딩 중에는 닫기 방지
    }
    if (!newOpen) {
      onClose();
    }
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className={cn(
        'sm:max-w-lg p-0 overflow-hidden',
        'border-4 border-amber-700',
        'bg-amber-100',
        'shadow-[8px_8px_0_0_#78350f]'
      )}>
        {/* 타이틀 바 - 스타듀밸리 스타일 */}
        <div className={cn(
          'px-4 py-2',
          'bg-gradient-to-b from-amber-600 to-amber-700',
          'border-b-4 border-amber-800'
        )}>
          <h2 className="text-amber-100 font-bold text-lg text-center drop-shadow-md">
            {isEditing ? '캐릭터 수정' : '캐릭터 만들기'}
          </h2>
        </div>

        <div className="p-4 space-y-4">
          {/* 상단 영역: 프리뷰 + 입력 필드 */}
          <div className="flex gap-4">
            {/* 캐릭터 프리뷰 - 나무 프레임 */}
            <div className={cn(
              'shrink-0',
              'p-2 rounded-lg',
              'bg-gradient-to-b from-amber-700 to-amber-800',
              'border-4 border-amber-900',
              'shadow-[inset_0_2px_4px_rgba(0,0,0,0.3)]'
            )}>
              <div className={cn(
                'w-32 h-40',
                'bg-gradient-to-b from-sky-300 to-green-300',
                'border-2 border-amber-600',
                'flex items-center justify-center',
                'rounded'
              )}>
                <CharacterPreview
                  body={currentBody.id}
                  eyes={currentEye.id}
                  hairstyle={currentHairstyle.id}
                  hairColor={currentHairColor.id}
                  outfit={currentOutfit.id}
                  accessory={currentAccessory.id}
                  size={48}
                  direction={previewDirection}
                  animate={true}
                />
              </div>
              {/* 방향 전환 버튼 */}
              <div className="flex justify-center items-center gap-1 mt-2">
                <button
                  type="button"
                  onClick={() => setPreviewDirection('left')}
                  className={cn(
                    'w-7 h-7 rounded border-2 flex items-center justify-center text-xs font-bold transition-colors',
                    previewDirection === 'left'
                      ? 'bg-amber-400 border-amber-700 text-amber-900'
                      : 'bg-amber-200 border-amber-600 text-amber-700 hover:bg-amber-300'
                  )}
                >
                  ←
                </button>
                <div className="flex flex-col gap-1">
                  <button
                    type="button"
                    onClick={() => setPreviewDirection('up')}
                    className={cn(
                      'w-7 h-5 rounded border-2 flex items-center justify-center text-xs font-bold transition-colors',
                      previewDirection === 'up'
                        ? 'bg-amber-400 border-amber-700 text-amber-900'
                        : 'bg-amber-200 border-amber-600 text-amber-700 hover:bg-amber-300'
                    )}
                  >
                    ↑
                  </button>
                  <button
                    type="button"
                    onClick={() => setPreviewDirection('down')}
                    className={cn(
                      'w-7 h-5 rounded border-2 flex items-center justify-center text-xs font-bold transition-colors',
                      previewDirection === 'down'
                        ? 'bg-amber-400 border-amber-700 text-amber-900'
                        : 'bg-amber-200 border-amber-600 text-amber-700 hover:bg-amber-300'
                    )}
                  >
                    ↓
                  </button>
                </div>
                <button
                  type="button"
                  onClick={() => setPreviewDirection('right')}
                  className={cn(
                    'w-7 h-7 rounded border-2 flex items-center justify-center text-xs font-bold transition-colors',
                    previewDirection === 'right'
                      ? 'bg-amber-400 border-amber-700 text-amber-900'
                      : 'bg-amber-200 border-amber-600 text-amber-700 hover:bg-amber-300'
                  )}
                >
                  →
                </button>
              </div>
            </div>

            {/* 입력 필드 */}
            <div className="flex-1 space-y-3">
              {/* 이름 입력 */}
              <div className="space-y-1">
                <label className="text-amber-800 font-bold text-sm flex items-center gap-1">
                  <User className="w-4 h-4" />
                  이름
                </label>
                <Input
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="캐릭터 이름"
                  maxLength={10}
                  className={cn(
                    'h-9 text-sm font-medium',
                    'bg-amber-50 border-2 border-amber-500',
                    'text-amber-900 placeholder:text-amber-400',
                    'focus:border-amber-600 focus:ring-1 focus:ring-amber-400'
                  )}
                />
              </div>

              {/* 농장 이름 입력 */}
              <div className="space-y-1">
                <label className="text-amber-800 font-bold text-sm flex items-center gap-1">
                  <Home className="w-4 h-4" />
                  농장 이름
                </label>
                <div className="flex gap-1 items-center">
                  <Input
                    value={farmName}
                    onChange={(e) => setFarmName(e.target.value)}
                    placeholder={name ? `${name}의` : '나의'}
                    maxLength={15}
                    className={cn(
                      'h-9 text-sm font-medium flex-1',
                      'bg-amber-50 border-2 border-amber-500',
                      'text-amber-900 placeholder:text-amber-400',
                      'focus:border-amber-600 focus:ring-1 focus:ring-amber-400'
                    )}
                  />
                  <span className="text-amber-800 font-bold text-sm">농장</span>
                </div>
              </div>

              {/* 미니 정보 */}
              <div className={cn(
                'p-2 rounded',
                'bg-amber-200/50 border border-amber-400'
              )}>
                <p className="text-xs text-amber-700">
                  🌱 문제를 풀고 농장을 가꿔보세요!
                </p>
              </div>
            </div>
          </div>

          {/* 구분선 */}
          <div className="border-t-2 border-amber-400 border-dashed" />

          {/* 커스터마이징 옵션들 */}
          <div className={cn(
            'p-3 rounded-lg space-y-2',
            'bg-amber-200/50 border-2 border-amber-400'
          )}>
            <h3 className="text-amber-800 font-bold text-xs mb-2">외모 설정</h3>

            {/* 피부색 */}
            <OptionRow
              label="피부색"
              value={currentBody.id}
              valueLabel={currentBody.label}
              onPrev={() => setBodyIndex(cycle(bodyIndex, BODY_OPTIONS.length, -1))}
              onNext={() => setBodyIndex(cycle(bodyIndex, BODY_OPTIONS.length, 1))}
            />

            {/* 눈 색 */}
            <OptionRow
              label="눈 색"
              value={currentEye.id}
              valueLabel={currentEye.label}
              colorPreview={currentEye.color}
              onPrev={() => setEyeIndex(cycle(eyeIndex, EYE_OPTIONS.length, -1))}
              onNext={() => setEyeIndex(cycle(eyeIndex, EYE_OPTIONS.length, 1))}
            />

            {/* 머리 스타일 */}
            <OptionRow
              label="머리"
              value={currentHairstyle.id}
              valueLabel={currentHairstyle.label}
              onPrev={() => setHairstyleIndex(cycle(hairstyleIndex, HAIRSTYLE_TYPES.length, -1))}
              onNext={() => setHairstyleIndex(cycle(hairstyleIndex, HAIRSTYLE_TYPES.length, 1))}
            />

            {/* 머리 색 */}
            <OptionRow
              label="머리 색"
              value={currentHairColor.id}
              valueLabel={currentHairColor.label}
              colorPreview={currentHairColor.color}
              onPrev={() => setHairColorIndex(cycle(hairColorIndex, HAIR_COLORS.length, -1))}
              onNext={() => setHairColorIndex(cycle(hairColorIndex, HAIR_COLORS.length, 1))}
            />

            {/* 의상 */}
            <OptionRow
              label="의상"
              value={currentOutfit.id}
              valueLabel={`${currentOutfit.preview} ${currentOutfit.label}`}
              onPrev={() => setOutfitIndex(cycle(outfitIndex, OUTFIT_OPTIONS.length, -1))}
              onNext={() => setOutfitIndex(cycle(outfitIndex, OUTFIT_OPTIONS.length, 1))}
            />

            {/* 악세서리 */}
            <OptionRow
              label="악세서리"
              value={currentAccessory.id}
              valueLabel={`${currentAccessory.preview} ${currentAccessory.label}`}
              onPrev={() => setAccessoryIndex(cycle(accessoryIndex, ACCESSORY_OPTIONS.length, -1))}
              onNext={() => setAccessoryIndex(cycle(accessoryIndex, ACCESSORY_OPTIONS.length, 1))}
            />
          </div>

          {/* 에러 메시지 */}
          {error && (
            <div className="p-2 rounded bg-red-100 border-2 border-red-400">
              <p className="text-sm text-red-700 text-center">{error}</p>
            </div>
          )}

          {/* 하단 버튼 */}
          <div className="flex justify-end gap-2">
            <Button
              variant="outline"
              onClick={onClose}
              disabled={isLoading}
              className={cn(
                'border-2 border-amber-500 bg-amber-100',
                'hover:bg-amber-200 text-amber-800',
                'disabled:opacity-50 disabled:cursor-not-allowed'
              )}
            >
              취소
            </Button>
            <motion.div whileHover={!isLoading && canComplete ? { scale: 1.02 } : {}} whileTap={!isLoading && canComplete ? { scale: 0.98 } : {}}>
              <Button
                onClick={handleComplete}
                disabled={!canComplete || isLoading}
                className={cn(
                  'bg-green-500 hover:bg-green-600 text-white font-bold',
                  'border-4 border-green-700',
                  'shadow-[3px_3px_0_0_#166534]',
                  'disabled:opacity-50 disabled:cursor-not-allowed',
                  'transition-all min-w-[80px]'
                )}
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-1 animate-spin" />
                    저장중...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4 mr-1" />
                    OK
                  </>
                )}
              </Button>
            </motion.div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
