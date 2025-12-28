'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { Progress } from '@/components/ui/progress';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';
import { usersApi } from '@/lib/api/users';
import { farmApi } from '@/lib/api/farm';
import type { Badge as BadgeType } from '@/lib/types';
import { Sparkles, Lock, Leaf, UserPlus, Home, Coins, TrendingUp, Loader2 } from 'lucide-react';
import { BadgeIcon } from '@/components/ui/badge-icon';
import { Button } from '@/components/ui/button';
import {
  CharacterCreationModal,
  type CharacterData,
} from '@/components/character/CharacterCreationModal';
import {
  FarmMinimap,
  FarmerSprite,
  CropSprite,
  HouseSprite,
  type CropVariety,
  type CropStage,
} from '@/components/farm/GameSprites';
import { useAuth, SUBSCRIPTION_FEATURES } from '@/hooks/useAuth';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import type { UserFarm, FarmSlot } from '@/lib/api/farm';

// Color mapping
const COLOR_MAP: Record<string, string> = {
  brown: '#8B4513',
  black: '#2d2d2d',
  blonde: '#f4d03f',
  red: '#c0392b',
  blue: '#3498db',
  pink: '#e91e8a',
};

// 샘플 작물 데이터 (Modern Farm 에셋 기반)
const SAMPLE_CROPS: Array<{ type: CropVariety; stage: CropStage }> = [
  { type: 'tomato', stage: 4 },
  { type: 'carrot', stage: 3 },
  { type: 'corn', stage: 4 },
  { type: 'strawberry', stage: 2 },
  { type: 'cabbage', stage: 4 },
  { type: 'pumpkin', stage: 3 },
];

export function SidebarProfile() {
  const { user, profile, isLoading, isAuthenticated } = useAuth();
  const [showCharacterModal, setShowCharacterModal] = useState(false);
  const [farm, setFarm] = useState<UserFarm | null>(null);
  const [farmLoading, setFarmLoading] = useState(false);
  const [farmError, setFarmError] = useState<string | null>(null);
  const [badges, setBadges] = useState<BadgeType[]>([]);

  // 사용자 XP 및 레벨 계산
  const level = profile?.level || 1;
  const currentXP = profile?.current_xp || 0;
  const requiredXP = profile?.required_xp || 100;
  const xpProgress = (currentXP / requiredXP) * 100;

  // Load farm data from API
  const loadFarmData = async () => {
    if (!isAuthenticated) return;

    setFarmLoading(true);
    setFarmError(null);

    try {
      const data = await farmApi.getFarm();
      setFarm(data);
    } catch (err) {
      console.error('농장 데이터 로드 실패:', err);
      setFarmError('농장 데이터를 불러올 수 없습니다');
      setFarm(null);
    } finally {
      setFarmLoading(false);
    }
  };

  useEffect(() => {
    loadFarmData();
  }, [isAuthenticated]);

  // Fetch user badges from API
  useEffect(() => {
    if (isAuthenticated) {
      usersApi.getBadges()
        .then(setBadges)
        .catch(() => setBadges([]));
    }
  }, [isAuthenticated]);

  const handleCharacterCreate = async (newCharacter: CharacterData) => {
    try {
      // API 호출로 캐릭터 생성
      const updatedFarm = await farmApi.createCharacter({
        name: newCharacter.name,
        hair: newCharacter.appearance.hair,
        hairColor: COLOR_MAP[newCharacter.appearance.color] || '#8B4513',
        face: newCharacter.appearance.face,
        outfit: newCharacter.appearance.clothes,
        outfitColor: COLOR_MAP[newCharacter.appearance.color] || '#8B4513',
        farmName: newCharacter.farmName,
      });
      setFarm(updatedFarm);
      setShowCharacterModal(false);
    } catch (error) {
      console.error('캐릭터 생성 실패:', error);
      // Fallback: localStorage에도 저장 (오프라인 지원)
      localStorage.setItem('codefill_character', JSON.stringify(newCharacter));
      setShowCharacterModal(false);
    }
  };

  // farm 데이터에서 캐릭터 정보 추출
  const character = farm?.characterData ? {
    name: farm.characterData.name,
    appearance: {
      hair: farm.characterData.hair,
      face: farm.characterData.face,
      clothes: farm.characterData.outfit,
      color: Object.entries(COLOR_MAP).find(([_, v]) => v === farm.characterData?.hairColor)?.[0] || 'brown',
    },
    farmName: farm.characterData.farmName,
  } : null;

  const farmLevel = farm?.farmLevel || 1;
  const gold = farm?.gold || 0;

  const characterColor = character ? COLOR_MAP[character.appearance.color] || COLOR_MAP.brown : COLOR_MAP.brown;

  // 로딩 중
  if (isLoading) {
    return (
      <div className="space-y-4 p-4">
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      </div>
    );
  }

  // 비로그인 상태
  if (!isAuthenticated || !user) {
    return (
      <div className="space-y-4 p-4">
        <div className={cn(
          'rounded-xl p-6 text-center',
          'bg-gradient-to-b from-secondary to-secondary/50',
          'border border-border'
        )}>
          <div className="mb-4">
            <FarmerSprite size={64} action="idle" className="mx-auto" />
          </div>
          <h3 className="font-semibold mb-2">로그인이 필요해요</h3>
          <p className="text-sm text-muted-foreground mb-4">
            문제를 풀고 농장을 키워보세요!
          </p>
          <div className="space-y-2">
            <Link href="/login">
              <Button className="w-full">로그인</Button>
            </Link>
            <Link href="/onboarding">
              <Button variant="outline" className="w-full">회원가입</Button>
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4 p-4">
      {/* Character Creation Modal */}
      <CharacterCreationModal
        open={showCharacterModal}
        onClose={() => setShowCharacterModal(false)}
        onComplete={handleCharacterCreate}
      />

      {/* 농장 미니맵 섹션 */}
      <div className="space-y-3">
        {farmLoading ? (
          <div className={cn(
            'rounded-xl p-6 text-center',
            'bg-gradient-to-b from-amber-100 to-amber-50',
            'border-4 border-amber-600'
          )}>
            <Loader2 className="h-8 w-8 animate-spin text-amber-600 mx-auto mb-2" />
            <p className="text-sm text-amber-800">농장 불러오는 중...</p>
          </div>
        ) : farmError ? (
          <div className={cn(
            'rounded-xl p-4',
            'bg-gradient-to-b from-red-50 to-red-100',
            'border-4 border-red-300'
          )}>
            <p className="text-sm text-red-700 mb-3 text-center">{farmError}</p>
            <Button
              onClick={loadFarmData}
              size="sm"
              variant="outline"
              className="w-full border-red-400 text-red-700 hover:bg-red-50"
            >
              다시 시도
            </Button>
          </div>
        ) : character ? (
          <>
            {/* 농장 미니맵 */}
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="relative"
            >
              {/* 농장 이름 헤더 */}
              <div className={cn(
                'flex items-center justify-between px-3 py-2 rounded-t-xl',
                'bg-amber-600 border-4 border-b-0 border-amber-800'
              )}>
                <div className="flex items-center gap-2">
                  <Home className="h-4 w-4 text-amber-100" />
                  <span className="font-bold text-sm text-amber-100">
                    {character.farmName || '나의 농장'}
                  </span>
                </div>
                <div className="flex items-center gap-1 text-xs text-amber-200">
                  <Coins className="h-3 w-3" />
                  <span>{gold.toLocaleString()}G</span>
                </div>
              </div>
              
              {/* 농장 미니맵 */}
              <FarmMinimap 
                level={farmLevel}
                crops={SAMPLE_CROPS}
                className="rounded-t-none h-48"
              />
              
              {/* 캐릭터 정보 오버레이 */}
              <div className={cn(
                'absolute bottom-2 left-2 right-2',
                'flex items-center gap-2 p-2 rounded-lg',
                'bg-black/60 backdrop-blur-sm'
              )}>
                <div className="shrink-0">
                  <FarmerSprite
                    hairColor={characterColor}
                    clothesColor={characterColor}
                    size={32}
                    action="idle"
                  />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-bold text-sm text-white truncate">{character.name}</p>
                  <p className="text-xs text-amber-300">Lv.{level} 농부</p>
                </div>
                <div className="text-right">
                  <div className="text-xs text-green-400 flex items-center gap-1">
                    <TrendingUp className="h-3 w-3" />
                    <span>{SAMPLE_CROPS.filter(c => c.stage === 4).length} 수확</span>
                  </div>
                </div>
              </div>
            </motion.div>
            
            {/* 농장 가기 버튼 */}
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
                농장 관리하기
              </Button>
            </Link>
            
            {/* 빠른 작물 현황 */}
            <div className={cn(
              'p-3 rounded-xl',
              'bg-gradient-to-b from-amber-100 to-amber-50',
              'border-3 border-amber-600 shadow-[2px_2px_0_0_#92400e]'
            )}>
              <h4 className="text-xs font-bold text-amber-800 mb-2 flex items-center gap-1">
                <Leaf className="h-3 w-3" />
                작물 현황
              </h4>
              <div className="grid grid-cols-6 gap-1">
                {SAMPLE_CROPS.map((crop, i) => (
                  <motion.div 
                    key={i}
                    whileHover={{ scale: 1.1 }}
                    className="flex items-center justify-center"
                  >
                    <CropSprite type={crop.type} stage={crop.stage} size={24} />
                  </motion.div>
                ))}
              </div>
            </div>
          </>
        ) : (
          /* 캐릭터 없을 때 */
          <motion.div
            className={cn(
              'rounded-xl p-4 space-y-4',
              'bg-gradient-to-b from-amber-100 to-amber-50',
              'border-4 border-amber-600 shadow-[4px_4px_0_0_#92400e]'
            )}
            whileHover={{ y: -2 }}
          >
            <h4 className="text-sm font-bold text-amber-900 flex items-center gap-2">
              <Leaf className="h-4 w-4" />
              나의 농장
            </h4>
            
            {/* 미리보기 */}
            <div className={cn(
              'relative rounded-lg overflow-hidden',
              'bg-gradient-to-b from-sky-200 to-green-200',
              'border-2 border-amber-400'
            )}
            style={{ height: '120px' }}
            >
              <div className="absolute inset-0 flex items-center justify-center">
                <motion.div
                  animate={{ y: [0, -5, 0] }}
                  transition={{ repeat: Infinity, duration: 2 }}
                >
                  <FarmerSprite size={48} action="idle" />
                </motion.div>
              </div>
              
              <div className="absolute top-2 right-2">
                <HouseSprite level={1} gridSize={12} />
              </div>
              
              <div className="absolute bottom-2 left-2 flex gap-1">
                <CropSprite type="tomato" stage={3} size={20} />
                <CropSprite type="carrot" stage={2} size={20} />
                <CropSprite type="wheat" stage={4} size={20} />
              </div>
              
              <div className="absolute inset-0 bg-black/30 flex items-center justify-center">
                <div className="bg-white/90 rounded-lg px-3 py-2 text-center">
                  <Lock className="h-5 w-5 text-amber-600 mx-auto mb-1" />
                  <p className="text-xs text-amber-800 font-medium">캐릭터를 만들어<br/>농장을 시작하세요!</p>
                </div>
              </div>
            </div>

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
          </motion.div>
        )}
      </div>

      {/* Level & XP */}
      <div className="rounded-xl border border-border bg-card p-4">
        <div className="mb-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-2xl font-bold text-primary">Lv.{level}</span>
            {profile?.subscription_tier && profile.subscription_tier !== 'free' && (
              <Badge className={cn(
                'text-xs',
                profile.subscription_tier === 'pro' 
                  ? 'bg-gradient-to-r from-yellow-400 to-amber-500 text-amber-900'
                  : 'bg-blue-500 text-white'
              )}>
                {SUBSCRIPTION_FEATURES[profile.subscription_tier].name}
              </Badge>
            )}
          </div>
          <span className="text-sm text-muted-foreground">
            {currentXP.toLocaleString()} / {requiredXP.toLocaleString()} XP
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
          {requiredXP - currentXP} XP to next level
        </p>
      </div>

      {/* Badges */}
      <div className="rounded-xl border border-border bg-card p-4">
        <h4 className="mb-3 text-sm font-medium text-muted-foreground">획득한 뱃지</h4>
        {badges.length > 0 ? (
          <div className="flex flex-wrap gap-2">
            {badges.map((badge) => (
              <Tooltip key={badge.id}>
                <TooltipTrigger asChild>
                  <motion.div
                    whileHover={{ scale: 1.1 }}
                    className="cursor-pointer"
                  >
                    {badge.iconUrl ? (
                      <img
                        src={badge.iconUrl}
                        alt={badge.name}
                        className="h-10 w-10 object-contain"
                      />
                    ) : (
                      <BadgeIcon name={badge.name} rarity={badge.rarity} size="md" />
                    )}
                  </motion.div>
                </TooltipTrigger>
                <TooltipContent side="top" className="max-w-[200px]">
                  <p className="font-medium">{badge.name}</p>
                  <p className="text-xs text-muted-foreground">{badge.description}</p>
                </TooltipContent>
              </Tooltip>
            ))}
          </div>
        ) : (
          <p className="text-sm text-muted-foreground">아직 획득한 뱃지가 없습니다</p>
        )}
      </div>
    </div>
  );
}
