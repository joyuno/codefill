'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { cn } from '@/lib/utils';
import {
  ChevronRight,
  ChevronLeft,
  Sparkles,
  Home,
  Leaf,
  Palette,
} from 'lucide-react';
import { CharacterPixel, CropPixel, HousePixel } from '@/components/farm/PixelSprites';

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

// Hair style options
const HAIR_OPTIONS = [
  { id: 'short', label: '숏컷' },
  { id: 'long', label: '긴머리' },
  { id: 'curly', label: '곱슬' },
  { id: 'spiky', label: '뾰족' },
];

// Face style options (표정은 캐릭터 스프라이트에서 시각적으로 변경)
const FACE_OPTIONS = [
  { id: 'happy', label: '행복' },
  { id: 'cool', label: '쿨' },
  { id: 'cute', label: '귀여움' },
  { id: 'sleepy', label: '졸림' },
];

// Clothes style options
const CLOTHES_OPTIONS = [
  { id: 'tshirt', label: '티셔츠' },
  { id: 'hoodie', label: '후드티' },
  { id: 'overalls', label: '멜빵바지' },
  { id: 'farmer', label: '농부옷' },
];

// Color options
const COLOR_OPTIONS = [
  { id: 'brown', color: '#8B4513', label: '갈색' },
  { id: 'black', color: '#2d2d2d', label: '검정' },
  { id: 'blonde', color: '#f4d03f', label: '금발' },
  { id: 'red', color: '#c0392b', label: '빨강' },
  { id: 'blue', color: '#3498db', label: '파랑' },
  { id: 'pink', color: '#e91e8a', label: '분홍' },
];

export function CharacterCreationModal({
  open,
  onClose,
  onComplete,
}: CharacterCreationModalProps) {
  const [step, setStep] = useState(1);
  const totalSteps = 3;

  // Character data
  const [name, setName] = useState('');
  const [hair, setHair] = useState('short');
  const [face, setFace] = useState('happy');
  const [clothes, setClothes] = useState('tshirt');
  const [color, setColor] = useState('brown');
  const [farmName, setFarmName] = useState('');

  const handleNext = () => {
    if (step < totalSteps) {
      setStep(step + 1);
    } else {
      handleComplete();
    }
  };

  const handleBack = () => {
    if (step > 1) {
      setStep(step - 1);
    }
  };

  const handleComplete = () => {
    const character: CharacterData = {
      name: name || '코드냥',
      appearance: {
        hair,
        face,
        clothes,
        color,
      },
      farmName: farmName || `${name || '코드냥'}의 농장`,
    };
    onComplete(character);
  };

  const canProceed = () => {
    switch (step) {
      case 1:
        return name.length >= 2;
      case 2:
        return true;
      case 3:
        return true;
      default:
        return false;
    }
  };

  const selectedColor = COLOR_OPTIONS.find((c) => c.id === color);

  const renderStep = () => {
    switch (step) {
      case 1:
        return (
          <motion.div
            key="step1"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="space-y-6"
          >
            <div className="text-center">
              <motion.div
                className={cn(
                  'mx-auto mb-4 flex h-24 w-24 items-center justify-center rounded-lg',
                  'bg-amber-100 border-4 border-amber-700 shadow-[4px_4px_0_0_#78350f]'
                )}
                animate={{ rotate: [0, -5, 5, 0] }}
                transition={{ repeat: Infinity, duration: 2 }}
              >
                <CharacterPixel
                  hairStyle={hair as any}
                  hairColor={selectedColor?.color}
                  size={64}
                />
              </motion.div>
              <h3 className="text-lg font-bold text-amber-900">캐릭터 이름을 지어주세요!</h3>
              <p className="mt-1 text-sm text-amber-700">
                농장에서 함께할 캐릭터의 이름이에요
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="characterName" className="text-amber-800 font-medium">캐릭터 이름</Label>
              <Input
                id="characterName"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="예: 코드냥, 버그슬레이어"
                maxLength={10}
                className={cn(
                  'text-center text-lg font-medium',
                  'border-3 border-amber-500 focus:border-amber-600 focus:ring-amber-400',
                  'bg-amber-50'
                )}
              />
              <p className="text-xs text-amber-600 text-center">
                2~10자 이내
              </p>
            </div>
          </motion.div>
        );

      case 2:
        return (
          <motion.div
            key="step2"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="space-y-4"
          >
            <div className="text-center">
              <div className={cn(
                'mx-auto mb-3 flex h-16 w-16 items-center justify-center rounded-lg',
                'bg-green-100 border-4 border-green-700 shadow-[3px_3px_0_0_#166534]'
              )}>
                <Palette className="h-8 w-8 text-green-600" />
              </div>
              <h3 className="text-lg font-bold text-green-900">캐릭터를 꾸며주세요!</h3>
            </div>

            {/* Live Preview */}
            <div className="flex justify-center">
              <motion.div
                className={cn(
                  'p-4 rounded-xl',
                  'bg-gradient-to-b from-sky-200 to-green-200',
                  'border-4 border-amber-600 shadow-[4px_4px_0_0_#92400e]'
                )}
                animate={{ y: [0, -4, 0] }}
                transition={{ repeat: Infinity, duration: 2 }}
              >
                <CharacterPixel
                  hairStyle={hair as any}
                  hairColor={selectedColor?.color}
                  clothesColor={selectedColor?.color}
                  size={80}
                />
              </motion.div>
            </div>

            {/* Hair selection */}
            <div className="space-y-2">
              <Label className="text-amber-800 font-bold text-sm">헤어스타일</Label>
              <div className="grid grid-cols-4 gap-2">
                {HAIR_OPTIONS.map((option) => (
                  <motion.button
                    key={option.id}
                    type="button"
                    onClick={() => setHair(option.id)}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className={cn(
                      'flex flex-col items-center rounded-lg p-2 transition-all',
                      'border-3 text-xs font-bold',
                      hair === option.id
                        ? 'border-amber-600 bg-amber-100 text-amber-900 shadow-[2px_2px_0_0_#92400e]'
                        : 'border-stone-300 bg-white hover:border-amber-400 text-stone-600'
                    )}
                  >
                    <CharacterPixel
                      hairStyle={option.id as any}
                      hairColor={selectedColor?.color}
                      size={32}
                    />
                    <span className="mt-1">{option.label}</span>
                  </motion.button>
                ))}
              </div>
            </div>

            {/* Color selection */}
            <div className="space-y-2">
              <Label className="text-amber-800 font-bold text-sm">색상 (머리 & 옷)</Label>
              <div className="grid grid-cols-6 gap-2">
                {COLOR_OPTIONS.map((option) => (
                  <motion.button
                    key={option.id}
                    type="button"
                    onClick={() => setColor(option.id)}
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                    className={cn(
                      'flex h-10 items-center justify-center rounded-lg transition-all',
                      'border-4',
                      color === option.id
                        ? 'border-stone-900 ring-2 ring-offset-2 ring-amber-400 shadow-[2px_2px_0_0_#1f2937]'
                        : 'border-stone-400 hover:border-stone-600'
                    )}
                    style={{ backgroundColor: option.color }}
                    title={option.label}
                  />
                ))}
              </div>
            </div>

            {/* Clothes selection */}
            <div className="space-y-2">
              <Label className="text-amber-800 font-bold text-sm">의상</Label>
              <div className="grid grid-cols-4 gap-2">
                {CLOTHES_OPTIONS.map((option) => (
                  <motion.button
                    key={option.id}
                    type="button"
                    onClick={() => setClothes(option.id)}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className={cn(
                      'flex flex-col items-center rounded-lg p-2 transition-all',
                      'border-3 text-xs font-bold',
                      clothes === option.id
                        ? 'border-amber-600 bg-amber-100 text-amber-900 shadow-[2px_2px_0_0_#92400e]'
                        : 'border-stone-300 bg-white hover:border-amber-400 text-stone-600'
                    )}
                  >
                    {option.label}
                  </motion.button>
                ))}
              </div>
            </div>
          </motion.div>
        );

      case 3:
        return (
          <motion.div
            key="step3"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="space-y-5"
          >
            <div className="text-center">
              <div className={cn(
                'mx-auto mb-3 flex h-16 w-16 items-center justify-center rounded-lg',
                'bg-sky-100 border-4 border-sky-700 shadow-[3px_3px_0_0_#075985]'
              )}>
                <Home className="h-8 w-8 text-sky-600" />
              </div>
              <h3 className="text-lg font-bold text-sky-900">농장 이름을 지어주세요!</h3>
            </div>

            {/* Farm Preview */}
            <div className={cn(
              'mx-auto max-w-xs rounded-xl p-4',
              'bg-gradient-to-b from-sky-300 via-sky-200 to-green-300',
              'border-4 border-green-700 shadow-[4px_4px_0_0_#166534]'
            )}>
              <div className="flex items-center justify-center gap-4 mb-3">
                <HousePixel level={1} size={64} />
              </div>
              <div className="flex items-center gap-3 p-2 bg-amber-100 rounded-lg border-2 border-amber-600">
                <CharacterPixel
                  hairStyle={hair as any}
                  hairColor={selectedColor?.color}
                  clothesColor={selectedColor?.color}
                  size={40}
                />
                <div>
                  <p className="font-bold text-amber-900 text-sm">{name || '코드냥'}</p>
                  <p className="text-xs text-amber-700 flex items-center gap-1">
                    <Leaf className="h-3 w-3" />
                    Lv.1 새싹 농부
                  </p>
                </div>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="farmName" className="text-sky-800 font-bold">농장 이름</Label>
              <Input
                id="farmName"
                value={farmName}
                onChange={(e) => setFarmName(e.target.value)}
                placeholder={`${name || '코드냥'}의 농장`}
                maxLength={20}
                className={cn(
                  'text-center font-medium',
                  'border-3 border-sky-500 focus:border-sky-600 focus:ring-sky-400',
                  'bg-sky-50'
                )}
              />
              <p className="text-xs text-sky-600 text-center">
                입력하지 않으면 기본 이름이 사용됩니다
              </p>
            </div>

            {/* Features preview */}
            <div className={cn(
              'rounded-lg p-3',
              'bg-amber-50 border-3 border-amber-500'
            )}>
              <p className="text-sm font-bold mb-2 text-amber-900">농장에서 할 수 있는 것들</p>
              <div className="grid grid-cols-2 gap-2 text-xs text-amber-800">
                <div className="flex items-center gap-2">
                  <CropPixel stage={4} type="tomato" size={20} />
                  <span>작물 재배</span>
                </div>
                <div className="flex items-center gap-2">
                  <HousePixel level={2} size={20} />
                  <span>집 업그레이드</span>
                </div>
                <div className="flex items-center gap-2">
                  <Sparkles className="h-4 w-4 text-purple-500" />
                  <span>XP & 레벨업</span>
                </div>
                <div className="flex items-center gap-2">
                  <Leaf className="h-4 w-4 text-green-500" />
                  <span>뱃지 수집</span>
                </div>
              </div>
            </div>
          </motion.div>
        );

      default:
        return null;
    }
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className={cn(
        'sm:max-w-md',
        'border-4 border-amber-700 shadow-[6px_6px_0_0_#78350f]',
        'bg-gradient-to-b from-amber-50 to-orange-50'
      )}>
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-amber-900 text-xl">
            <Leaf className="h-6 w-6 text-green-600" />
            캐릭터 만들기
          </DialogTitle>
          <DialogDescription className="text-amber-700">
            농장에서 함께할 나만의 캐릭터를 만들어보세요
          </DialogDescription>
        </DialogHeader>

        {/* Progress */}
        <div className="flex items-center justify-center gap-2 py-2">
          {Array.from({ length: totalSteps }).map((_, i) => (
            <motion.div
              key={i}
              className={cn(
                'h-3 rounded-full transition-all',
                'border-2',
                i + 1 <= step
                  ? 'w-12 bg-green-500 border-green-700'
                  : 'w-4 bg-stone-200 border-stone-400'
              )}
              animate={i + 1 === step ? { scale: [1, 1.1, 1] } : {}}
              transition={{ repeat: Infinity, duration: 1 }}
            />
          ))}
        </div>

        {/* Content */}
        <AnimatePresence mode="wait">{renderStep()}</AnimatePresence>

        {/* Navigation */}
        <div className="flex justify-between pt-4">
          <Button
            variant="outline"
            onClick={handleBack}
            disabled={step === 1}
            className={cn(
              'border-3 border-stone-400',
              step > 1 && 'hover:bg-stone-100 hover:border-stone-500'
            )}
          >
            <ChevronLeft className="mr-1 h-4 w-4" />
            이전
          </Button>
          <Button
            onClick={handleNext}
            disabled={!canProceed()}
            className={cn(
              'bg-green-500 hover:bg-green-600 text-white font-bold',
              'border-4 border-green-700 shadow-[3px_3px_0_0_#166534]',
              'disabled:opacity-50 disabled:cursor-not-allowed',
              'transition-transform hover:translate-y-[-2px]'
            )}
          >
            {step === totalSteps ? (
              <>
                완료!
                <Sparkles className="ml-1 h-4 w-4" />
              </>
            ) : (
              <>
                다음
                <ChevronRight className="ml-1 h-4 w-4" />
              </>
            )}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
