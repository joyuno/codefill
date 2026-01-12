'use client';

import { useState, useMemo } from 'react';
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
} from 'lucide-react';

interface CharacterCreationModalProps {
  open: boolean;
  onClose: () => void;
  onComplete: (character: CharacterData) => void;
}

export interface CharacterData {
  name: string;
  appearance: {
    hair: string;
    face: string;
    clothes: string;
    color: string;
  };
  farmName: string;
}

// ============================================================
// 에셋 옵션 정의 - Modern Farm 에셋 기반
// ============================================================

// Body (피부색) 옵션
const BODY_OPTIONS = [
  { id: 'Body_1', label: '밝은 피부 1' },
  { id: 'Body_2', label: '밝은 피부 2' },
  { id: 'Body_3', label: '베이지' },
  { id: 'Body_4', label: '황금빛' },
  { id: 'Body_5', label: '올리브' },
  { id: 'Body_6', label: '카라멜' },
  { id: 'Body_7', label: '브라운' },
  { id: 'Body_8', label: '다크' },
  { id: 'Body_9', label: '딥 다크' },
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
// 캐릭터 프리뷰 컴포넌트 (레이어 합성)
// ============================================================

interface CharacterPreviewProps {
  body: string;
  eyes: string;
  hairstyle: string;
  hairColor: string;
  outfit: string;
  accessory: string;
  size?: number;
}

function CharacterPreview({
  body,
  eyes,
  hairstyle,
  hairColor,
  outfit,
  accessory,
  size = 128,
}: CharacterPreviewProps) {
  // 헤어스타일 파일명 조합
  const hairstyleFile = `Hairstyle_${hairstyle}_${hairColor}`;

  // 레이어 순서: body → outfit → eyes → hair → accessory
  const layers = [
    `/farm/character-pieces/bodies/${body}.png`,
    `/farm/character-pieces/outfits/${outfit}.png`,
    `/farm/character-pieces/eyes/${eyes}.png`,
    `/farm/character-pieces/hairstyles/${hairstyleFile}.png`,
  ];

  if (accessory !== 'none') {
    layers.push(`/farm/character-pieces/accessories/${accessory}.png`);
  }

  return (
    <div
      className="relative"
      style={{
        width: size,
        height: size,
        imageRendering: 'pixelated',
      }}
    >
      {layers.map((src, index) => (
        <img
          key={src}
          src={src}
          alt=""
          className="absolute inset-0 w-full h-full object-contain"
          style={{
            imageRendering: 'pixelated',
            zIndex: index,
          }}
          onError={(e) => {
            // 이미지 로드 실패 시 숨김
            (e.target as HTMLImageElement).style.display = 'none';
          }}
        />
      ))}
    </div>
  );
}

// ============================================================
// 메인 모달 컴포넌트
// ============================================================

export function CharacterCreationModal({
  open,
  onClose,
  onComplete,
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
        hair: `${currentHairstyle.id}_${currentHairColor.id}`,
        face: currentEye.id,
        clothes: currentOutfit.id,
        color: currentHairColor.color,
      },
      farmName: farmName || `${name || '코드냥'}의 농장`,
    };
    onComplete(character);
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
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
            캐릭터 만들기
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
                'w-32 h-32',
                'bg-gradient-to-b from-sky-300 to-green-300',
                'border-2 border-amber-600',
                'flex items-center justify-center',
                'rounded'
              )}>
                <motion.div
                  animate={{ y: [0, -4, 0] }}
                  transition={{ repeat: Infinity, duration: 2, ease: 'easeInOut' }}
                >
                  <CharacterPreview
                    body={currentBody.id}
                    eyes={currentEye.id}
                    hairstyle={currentHairstyle.id}
                    hairColor={currentHairColor.id}
                    outfit={currentOutfit.id}
                    accessory={currentAccessory.id}
                    size={96}
                  />
                </motion.div>
              </div>
              {/* 성별 아이콘 (장식용) */}
              <div className="flex justify-center gap-2 mt-2">
                <div className="w-6 h-6 bg-amber-200 rounded border-2 border-amber-600 flex items-center justify-center">
                  <span className="text-xs">♂</span>
                </div>
                <div className="w-6 h-6 bg-amber-200 rounded border-2 border-amber-600 flex items-center justify-center">
                  <span className="text-xs">♀</span>
                </div>
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

          {/* 하단 버튼 */}
          <div className="flex justify-end gap-2">
            <Button
              variant="outline"
              onClick={onClose}
              className={cn(
                'border-2 border-amber-500 bg-amber-100',
                'hover:bg-amber-200 text-amber-800'
              )}
            >
              취소
            </Button>
            <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
              <Button
                onClick={handleComplete}
                disabled={!canComplete}
                className={cn(
                  'bg-green-500 hover:bg-green-600 text-white font-bold',
                  'border-4 border-green-700',
                  'shadow-[3px_3px_0_0_#166534]',
                  'disabled:opacity-50 disabled:cursor-not-allowed',
                  'transition-all'
                )}
              >
                <Sparkles className="w-4 h-4 mr-1" />
                OK
              </Button>
            </motion.div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
