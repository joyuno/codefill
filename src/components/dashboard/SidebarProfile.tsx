'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { Progress } from '@/components/ui/progress';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';
import { mockUser, mockBadges } from '@/lib/mockData';
import { Sparkles, Lock, Leaf, UserPlus } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  CharacterCreationModal,
  type CharacterData,
} from '@/components/character/CharacterCreationModal';
import { CharacterPixel, CropPixel } from '@/components/farm/PixelSprites';
import { cn } from '@/lib/utils';

const avatarShapes = {
  hexagon: 'polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%)',
  circle: 'circle(50% at 50% 50%)',
  diamond: 'polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%)',
  pentagon: 'polygon(50% 0%, 100% 38%, 82% 100%, 18% 100%, 0% 38%)',
};

// Color mapping
const COLOR_MAP: Record<string, string> = {
  brown: '#8B4513',
  black: '#2d2d2d',
  blonde: '#f4d03f',
  red: '#c0392b',
  blue: '#3498db',
  pink: '#e91e8a',
};

export function SidebarProfile() {
  const [isLevelingUp, setIsLevelingUp] = useState(false);
  const [showCharacterModal, setShowCharacterModal] = useState(false);
  const [character, setCharacter] = useState<CharacterData | null>(null);
  const xpProgress = (mockUser.currentXP / mockUser.requiredXP) * 100;

  // Load character from localStorage
  useEffect(() => {
    const savedCharacter = localStorage.getItem('codefill_character');
    if (savedCharacter) {
      try {
        setCharacter(JSON.parse(savedCharacter));
      } catch {
        // Invalid data
      }
    }
  }, []);

  const handleLevelUp = () => {
    setIsLevelingUp(true);
    setTimeout(() => setIsLevelingUp(false), 600);
  };

  const handleCharacterCreate = (newCharacter: CharacterData) => {
    localStorage.setItem('codefill_character', JSON.stringify(newCharacter));
    setCharacter(newCharacter);
    setShowCharacterModal(false);
  };

  const characterColor = character ? COLOR_MAP[character.appearance.color] || COLOR_MAP.brown : COLOR_MAP.brown;

  return (
    <div className="space-y-6 p-4">
      {/* Character Creation Modal */}
      <CharacterCreationModal
        open={showCharacterModal}
        onClose={() => setShowCharacterModal(false)}
        onComplete={handleCharacterCreate}
      />

      {/* Avatar Card */}
      <div className="rounded-xl border border-border bg-card p-4">
        <div className="flex flex-col items-center gap-4">
          <motion.div
            animate={isLevelingUp ? { scale: [1, 1.2, 1], filter: ['brightness(1)', 'brightness(1.5)', 'brightness(1)'] } : {}}
            transition={{ duration: 0.6 }}
            className="relative"
          >
            <div
              className="flex h-24 w-24 items-center justify-center bg-gradient-to-br from-primary/80 to-primary"
              style={{ clipPath: avatarShapes[mockUser.avatarShape] }}
            >
              <span className="text-3xl font-bold text-primary-foreground">
                {mockUser.username.slice(0, 2).toUpperCase()}
              </span>
            </div>
            {isLevelingUp && (
              <motion.div
                initial={{ scale: 0, opacity: 0 }}
                animate={{ scale: 2, opacity: [0, 1, 0] }}
                transition={{ duration: 0.6 }}
                className="absolute inset-0 flex items-center justify-center"
              >
                <Sparkles className="h-12 w-12 text-primary" />
              </motion.div>
            )}
          </motion.div>

          <div className="text-center">
            <h3 className="font-semibold">{mockUser.username}</h3>
            <p className="text-sm text-muted-foreground">@{mockUser.username.toLowerCase()}</p>
          </div>

          <Button
            variant="outline"
            size="sm"
            onClick={handleLevelUp}
            className="w-full"
          >
            <Sparkles className="mr-2 h-4 w-4" />
            Preview Level Up
          </Button>
        </div>
      </div>

      {/* Character & Farm Section - PRD 2.4 (Pixel Art Style) */}
      <motion.div
        className={cn(
          'rounded-xl p-4 space-y-3',
          'bg-gradient-to-b from-green-200 to-green-100',
          'border-4 border-green-700 shadow-[4px_4px_0_0_#166534]'
        )}
        whileHover={{ y: -2 }}
        transition={{ duration: 0.2 }}
      >
        <h4 className="text-sm font-bold text-green-900 flex items-center gap-2">
          <Leaf className="h-4 w-4" />
          나의 농장
        </h4>

        {character ? (
          <>
            {/* Character Display (Pixel Art Style) */}
            <motion.div
              className={cn(
                'flex items-center gap-3 p-3 rounded-lg',
                'bg-amber-50 border-3 border-amber-600 shadow-[2px_2px_0_0_#92400e]'
              )}
              whileHover={{ scale: 1.02 }}
            >
              <div className={cn(
                'p-2 rounded-lg bg-gradient-to-b from-sky-200 to-green-200',
                'border-2 border-amber-500'
              )}>
                <CharacterPixel
                  hairStyle={character.appearance.hair as any}
                  hairColor={characterColor}
                  clothesColor={characterColor}
                  size={48}
                />
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-bold text-sm text-amber-900 truncate">{character.name}</p>
                <p className="text-xs text-amber-700 truncate">{character.farmName}</p>
                <div className="flex items-center gap-1 mt-1">
                  <CropPixel stage={4} type="tomato" size={14} />
                  <CropPixel stage={3} type="wheat" size={14} />
                  <CropPixel stage={2} type="corn" size={14} />
                </div>
              </div>
            </motion.div>

            {/* Farm Entry Button - Unlocked */}
            <Link href="/farm">
              <Button
                className={cn(
                  'w-full gap-2',
                  'bg-green-500 hover:bg-green-600 text-white font-bold',
                  'border-4 border-green-700 shadow-[3px_3px_0_0_#166534]',
                  'transition-transform hover:translate-y-[-2px]'
                )}
              >
                <Leaf className="h-4 w-4" />
                농장 가기
              </Button>
            </Link>
          </>
        ) : (
          <>
            {/* Empty State with Preview */}
            <div className={cn(
              'flex flex-col items-center gap-2 p-4 rounded-lg',
              'bg-amber-50/50 border-2 border-dashed border-amber-400'
            )}>
              <motion.div
                animate={{ y: [0, -4, 0] }}
                transition={{ repeat: Infinity, duration: 2 }}
              >
                <CharacterPixel
                  hairStyle="short"
                  hairColor="#8B4513"
                  clothesColor="#3498db"
                  size={48}
                />
              </motion.div>
              <p className="text-xs text-amber-700 text-center">
                캐릭터를 만들고<br />농장을 시작하세요!
              </p>
            </div>

            {/* Character Creation Button */}
            <Button
              onClick={() => setShowCharacterModal(true)}
              className={cn(
                'w-full gap-2',
                'bg-amber-500 hover:bg-amber-600 text-white font-bold',
                'border-4 border-amber-700 shadow-[3px_3px_0_0_#92400e]',
                'transition-transform hover:translate-y-[-2px]'
              )}
            >
              <UserPlus className="h-4 w-4" />
              캐릭터 생성하기
            </Button>

            {/* Farm Entry Button - Locked */}
            <Button
              className={cn(
                'w-full gap-2',
                'bg-stone-300 text-stone-500',
                'border-3 border-stone-400'
              )}
              disabled
            >
              <Lock className="h-4 w-4" />
              농장 가기
              <span className="ml-auto text-xs">(캐릭터 필요)</span>
            </Button>
          </>
        )}
      </motion.div>

      {/* Level & XP */}
      <div className="rounded-xl border border-border bg-card p-4">
        <div className="mb-3 flex items-center justify-between">
          <span className="text-2xl font-bold text-primary">Lv.{mockUser.level}</span>
          <span className="text-sm text-muted-foreground">
            {mockUser.currentXP.toLocaleString()} / {mockUser.requiredXP.toLocaleString()} XP
          </span>
        </div>
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: '100%' }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <Progress value={xpProgress} className="h-3" />
        </motion.div>
        <p className="mt-2 text-xs text-muted-foreground">
          {mockUser.requiredXP - mockUser.currentXP} XP to next level
        </p>
      </div>

      {/* Badges */}
      <div className="rounded-xl border border-border bg-card p-4">
        <h4 className="mb-3 text-sm font-medium text-muted-foreground">Badges</h4>
        <div className="flex flex-wrap gap-2">
          {mockBadges.slice(0, 5).map((badge) => (
            <Tooltip key={badge.id}>
              <TooltipTrigger asChild>
                <motion.div
                  whileHover={{ scale: 1.1 }}
                  className="flex h-10 w-10 cursor-pointer items-center justify-center rounded-lg bg-secondary text-lg"
                >
                  {badge.icon}
                </motion.div>
              </TooltipTrigger>
              <TooltipContent side="top" className="max-w-[200px]">
                <p className="font-medium">{badge.name}</p>
                <p className="text-xs text-muted-foreground">{badge.description}</p>
              </TooltipContent>
            </Tooltip>
          ))}
        </div>
      </div>
    </div>
  );
}
