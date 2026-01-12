'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { Progress } from '@/components/ui/progress';
import { usersApi, publicProfileApi, type PublicFarm, type PublicBadge } from '@/lib/api/users';
import { farmApi } from '@/lib/api/farm';
import type { Badge as BadgeType } from '@/lib/types';
import { Sparkles, Lock, Leaf, UserPlus, Home, Coins, TrendingUp, Loader2, UserCheck } from 'lucide-react';
import { BadgeIcon } from '@/components/ui/badge-icon';
import { BadgeDetailModal, type BadgeRarity } from '@/components/ui/badge-detail-modal';
import { Button } from '@/components/ui/button';
import {
  CharacterCreationModal,
  type CharacterData,
} from '@/components/character/CharacterCreationModal';
import {
  FarmMinimap,
  FarmerSprite,
  HouseSprite,
  type CropVariety,
  type CropStage,
} from '@/components/farm/GameSprites';
import { CROP_INFO } from '@/components/farm/ui/Hotbar';
import { useAuth, SUBSCRIPTION_FEATURES } from '@/hooks/useAuth';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import type { UserFarm } from '@/lib/api/farm';
import { friendsApi } from '@/lib/api/friends';

// Color mapping
const COLOR_MAP: Record<string, string> = {
  brown: '#8B4513',
  black: '#2d2d2d',
  blonde: '#f4d03f',
  red: '#c0392b',
  blue: '#3498db',
  pink: '#e91e8a',
};

// 농장 캐시 관리
const FARM_CACHE_KEY = 'codefill_farm_cache';
const FARM_CACHE_TTL = 1000 * 60 * 30; // 30분 (농장 페이지 방문 시 갱신되므로 넉넉하게)

interface FarmCache {
  data: UserFarm;
  timestamp: number;
}

function getFarmFromCache(): UserFarm | null {
  try {
    const cached = localStorage.getItem(FARM_CACHE_KEY);
    if (!cached) return null;

    const parsed: FarmCache = JSON.parse(cached);
    const now = Date.now();

    // TTL 체크 (기본 30분, 하지만 농장 페이지 방문 시 갱신됨)
    if (now - parsed.timestamp > FARM_CACHE_TTL) {
      localStorage.removeItem(FARM_CACHE_KEY);
      return null;
    }

    return parsed.data;
  } catch {
    return null;
  }
}

function setFarmToCache(data: UserFarm): void {
  try {
    const cache: FarmCache = {
      data,
      timestamp: Date.now(),
    };
    localStorage.setItem(FARM_CACHE_KEY, JSON.stringify(cache));
  } catch {
    // localStorage 쓰기 실패 무시
  }
}

// 농장 페이지 방문 플래그 (sessionStorage로 세션 내 추적)
const FARM_VISITED_KEY = 'codefill_farm_visited';

export function markFarmVisited(): void {
  sessionStorage.setItem(FARM_VISITED_KEY, Date.now().toString());
}

export function checkAndClearFarmVisited(): boolean {
  const visited = sessionStorage.getItem(FARM_VISITED_KEY);
  if (visited) {
    sessionStorage.removeItem(FARM_VISITED_KEY);
    return true;
  }
  return false;
}

// 외부에서 캐시 갱신용 (농장 페이지에서 호출)
export function updateFarmCache(data: UserFarm): void {
  setFarmToCache(data);
}

// 샘플 작물 데이터 (Modern Farm 에셋 기반)
const SAMPLE_CROPS: Array<{ type: CropVariety; stage: CropStage }> = [
  { type: 'tomato', stage: 4 },
  { type: 'carrot', stage: 3 },
  { type: 'corn', stage: 4 },
  { type: 'strawberry', stage: 2 },
  { type: 'cabbage', stage: 4 },
  { type: 'pumpkin', stage: 3 },
];

interface SidebarProfileProps {
  /** 조회할 사용자 username. 없으면 본인 프로필 */
  username?: string;
  /** 부모에서 전달받은 공개 프로필 데이터 (있으면 API 호출 안 함) */
  publicData?: {
    profile: {
      id: string;
      username: string;
      avatarColor: string;
      level: number;
      currentXP: number;
      requiredXP: number;
    };
    badges: PublicBadge[];
    farm: PublicFarm;
  };
  /** 부모에서 전달받은 뱃지 배열 (있으면 API 호출 안 함) */
  badges?: BadgeType[];
}

// 뱃지 희귀도 순서 (내림차순 정렬용)
const RARITY_ORDER: Record<string, number> = {
  legendary: 5,
  epic: 4,
  rare: 3,
  uncommon: 2,
  common: 1,
};

export function SidebarProfile({ username, publicData, badges: propBadges }: SidebarProfileProps) {
  const { user, profile, isLoading, isAuthenticated } = useAuth();
  const [showCharacterModal, setShowCharacterModal] = useState(false);
  // 본인 프로필: 캐시에서 초기값 로드 (즉시 표시)
  const [farm, setFarm] = useState<UserFarm | null>(() => {
    if (typeof window === 'undefined') return null;
    // 타인 프로필이면 캐시 사용 안함
    if (username) return null;
    return getFarmFromCache();
  });
  const [publicFarm, setPublicFarm] = useState<PublicFarm | null>(null);
  // 캐시가 있으면 로딩 상태 false로 시작
  const [farmLoading, setFarmLoading] = useState(() => {
    if (typeof window === 'undefined') return false;
    if (username) return false;
    return !getFarmFromCache();
  });
  const [farmError, setFarmError] = useState<string | null>(null);
  const [badges, setBadges] = useState<BadgeType[]>([]);
  const [publicBadges, setPublicBadges] = useState<PublicBadge[]>([]);
  const [showAllBadges, setShowAllBadges] = useState(false);
  const [selectedBadge, setSelectedBadge] = useState<{
    id: string;
    name: string;
    description: string;
    rarity: BadgeRarity;
    iconUrl?: string;
    earnedAt?: string;
  } | null>(null);

  // 공개 프로필 데이터
  const [publicProfile, setPublicProfile] = useState<{
    id: string;
    username: string;
    avatarColor: string;
    level: number;
    currentXP: number;
    requiredXP: number;
  } | null>(null);
  const [publicLoading, setPublicLoading] = useState(false);

  // 친구 추가 상태
  const [isFriend, setIsFriend] = useState(false);
  const [friendRequestSent, setFriendRequestSent] = useState(false);
  const [addingFriend, setAddingFriend] = useState(false);

  // 본인 프로필인지 확인
  const isOwnProfile = !username || (profile?.username === username);

  // 사용자 XP 및 레벨 계산
  const level = profile?.level || 1;
  const currentXP = profile?.current_xp || 0;
  const requiredXP = profile?.required_xp || 100;
  const xpProgress = (currentXP / requiredXP) * 100;

  // Load farm data from API (with caching for own profile)
  const loadFarmData = async (forceRefresh = false) => {
    setFarmError(null);

    try {
      if (isOwnProfile) {
        // 본인 프로필: 캐시 우선 사용
        if (!isAuthenticated) {
          setFarmLoading(false);
          return;
        }

        // 1. 이미 farm 데이터가 있으면 (초기 캐시 로딩) 백그라운드 갱신만 체크
        if (farm && !forceRefresh) {
          // 농장 페이지 방문 후면 백그라운드 갱신
          const shouldRefresh = checkAndClearFarmVisited();
          if (shouldRefresh) {
            farmApi.getFarm().then((data) => {
              setFarm(data);
              setFarmToCache(data);
            }).catch(() => {
              // 백그라운드 갱신 실패는 무시
            });
          }
          return;
        }

        // 2. farm이 없으면 캐시 확인 (초기 로딩 이후 재마운트 시)
        if (!forceRefresh) {
          const cached = getFarmFromCache();
          if (cached) {
            setFarm(cached);
            setFarmLoading(false);
            return;
          }
        }

        // 3. 캐시도 없으면 API 호출
        setFarmLoading(true);
        const data = await farmApi.getFarm();
        setFarm(data);
        setFarmToCache(data);
      } else if (username) {
        // 타인 프로필: 공개 API 사용 (캐싱 없음)
        setFarmLoading(true);
        const data = await publicProfileApi.getFarm(username);
        setPublicFarm(data);
      }
    } catch (err) {
      console.error('농장 데이터 로드 실패:', err);
      setFarmError('농장 데이터를 불러올 수 없습니다');
      setFarm(null);
      setPublicFarm(null);
    } finally {
      setFarmLoading(false);
    }
  };

  // publicData prop이 있으면 사용, 없으면 API 호출
  useEffect(() => {
    if (!username) return; // 본인 프로필은 스킵

    // props로 데이터가 전달되면 그걸 사용
    if (publicData) {
      setPublicProfile({
        id: publicData.profile.id,
        username: publicData.profile.username,
        avatarColor: publicData.profile.avatarColor,
        level: publicData.profile.level,
        currentXP: publicData.profile.currentXP,
        requiredXP: publicData.profile.requiredXP,
      });
      setPublicBadges(publicData.badges);
      setPublicFarm(publicData.farm);
      setPublicLoading(false);
      return;
    }

    // props가 없으면 API 호출 (fallback)
    setPublicLoading(true);
    Promise.all([
      publicProfileApi.getProfile(username),
      publicProfileApi.getBadges(username),
      publicProfileApi.getFarm(username),
    ])
      .then(([profileData, badgesData, farmData]) => {
        setPublicProfile({
          id: profileData.id,
          username: profileData.username,
          avatarColor: profileData.avatarColor,
          level: profileData.level,
          currentXP: profileData.currentXP,
          requiredXP: profileData.requiredXP,
        });
        setPublicBadges(badgesData);
        setPublicFarm(farmData);
      })
      .catch((err) => {
        console.error('공개 프로필 로드 실패:', err);
      })
      .finally(() => {
        setPublicLoading(false);
      });
  }, [username, publicData]);

  // 본인 프로필일 때 농장 데이터 로드
  useEffect(() => {
    if (!username && isAuthenticated) {
      loadFarmData();
    }
  }, [isAuthenticated, username]);

  // Fetch user badges from API (본인 프로필) - propBadges가 있으면 API 호출 안 함
  useEffect(() => {
    // propBadges가 전달되었으면 그 값 사용 (page.tsx에서 이미 호출함)
    if (propBadges !== undefined) {
      setBadges(propBadges);
      return;
    }

    if (isAuthenticated && isOwnProfile) {
      usersApi.getBadges()
        .then(setBadges)
        .catch(() => setBadges([]));
    }
  }, [isAuthenticated, isOwnProfile, propBadges]);

  // 친구 추가 핸들러
  const handleAddFriend = async () => {
    if (!publicProfile?.id || !isAuthenticated) return;

    setAddingFriend(true);
    try {
      await friendsApi.sendRequest(publicProfile.id);
      setFriendRequestSent(true);
    } catch (err) {
      console.error('친구 요청 실패:', err);
    } finally {
      setAddingFriend(false);
    }
  };

  const handleCharacterCreate = async (newCharacter: CharacterData) => {
    try {
      // API 호출로 캐릭터 생성
      // 새 형식: color가 직접 hex 값 (예: '#3d2314')
      // 레거시 형식: color가 키 (예: 'brown') - COLOR_MAP으로 변환 필요
      const hairColor = newCharacter.appearance.color.startsWith('#')
        ? newCharacter.appearance.color
        : COLOR_MAP[newCharacter.appearance.color] || '#8B4513';

      const updatedFarm = await farmApi.createCharacter({
        name: newCharacter.name,
        hair: newCharacter.appearance.hair,
        hairColor,
        face: newCharacter.appearance.face,
        outfit: newCharacter.appearance.clothes,
        outfitColor: hairColor,
        farmName: newCharacter.farmName,
      });
      setFarm(updatedFarm);
      setFarmToCache(updatedFarm); // 캐시도 업데이트
      setShowCharacterModal(false);
    } catch (error) {
      console.error('캐릭터 생성 실패:', error);
      // Fallback: localStorage에도 저장 (오프라인 지원)
      localStorage.setItem('codefill_character', JSON.stringify(newCharacter));
      setShowCharacterModal(false);
    }
  };

  // farm 데이터에서 캐릭터 정보 추출 (본인 또는 타인)
  const character = isOwnProfile
    ? (farm?.characterData ? {
        name: farm.characterData.name,
        appearance: {
          hair: farm.characterData.hair,
          face: farm.characterData.face,
          clothes: farm.characterData.outfit,
          color: Object.entries(COLOR_MAP).find(([_, v]) => v === farm.characterData?.hairColor)?.[0] || 'brown',
        },
        farmName: farm.characterData.farmName,
      } : null)
    : (publicFarm?.hasCharacter && publicFarm.character ? {
        name: publicFarm.character.name,
        appearance: {
          hair: publicFarm.character.hair,
          face: publicFarm.character.face,
          clothes: publicFarm.character.outfit,
          color: Object.entries(COLOR_MAP).find(([_, v]) => v === publicFarm.character?.hairColor)?.[0] || 'brown',
        },
        farmName: publicFarm.character.farmName,
      } : null);

  const farmLevel = isOwnProfile ? (farm?.farmLevel || 1) : (publicFarm?.farmLevel || 1);
  const gold = isOwnProfile ? (farm?.gold || 0) : (publicFarm?.gold || 0);

  const characterColor = character ? COLOR_MAP[character.appearance.color] || COLOR_MAP.brown : COLOR_MAP.brown;

  // 표시할 레벨/XP (본인 또는 타인)
  const displayLevel = isOwnProfile ? level : (publicProfile?.level || 1);
  const displayCurrentXP = isOwnProfile ? currentXP : (publicProfile?.currentXP || 0);
  const displayRequiredXP = isOwnProfile ? requiredXP : (publicProfile?.requiredXP || 100);
  const displayXpProgress = (displayCurrentXP / displayRequiredXP) * 100;

  // 표시할 뱃지 (본인 또는 타인) - 희귀도 내림차순 정렬
  const displayBadges = (isOwnProfile ? badges : publicBadges.map(b => ({
    id: b.id,
    name: b.name,
    icon: b.icon,
    iconUrl: b.iconUrl,
    description: b.description,
    rarity: b.rarity as 'common' | 'uncommon' | 'rare' | 'epic' | 'legendary',
  }))).sort((a, b) => (RARITY_ORDER[b.rarity] || 0) - (RARITY_ORDER[a.rarity] || 0));

  // 사이드바에 표시할 뱃지 (12개 제한 또는 전체)
  const BADGE_DISPLAY_LIMIT = 12;
  const visibleBadges = showAllBadges ? displayBadges : displayBadges.slice(0, BADGE_DISPLAY_LIMIT);
  const hasMoreBadges = displayBadges.length > BADGE_DISPLAY_LIMIT;

  // 로딩 중
  if (isLoading || publicLoading) {
    return (
      <div className="space-y-4 p-4">
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      </div>
    );
  }

  // 비로그인 상태 (본인 프로필일 때만)
  if (isOwnProfile && (!isAuthenticated || !user)) {
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
              
              {/* 캐릭터 정보 오버레이 (한 줄) */}
              <div className={cn(
                'absolute bottom-2 left-2 right-2 z-20',
                'flex items-center justify-between px-3 py-1.5 rounded-lg',
                'bg-black/40 backdrop-blur-sm'
              )}>
                <span className="font-bold text-sm text-white truncate">{character.name}</span>
                <span className="text-xs text-amber-300">Lv.{displayLevel} 농부</span>
                <div className="text-xs text-green-400 flex items-center gap-1">
                  <TrendingUp className="h-3 w-3" />
                  <span>{SAMPLE_CROPS.filter(c => c.stage === 4).length} 수확</span>
                </div>
              </div>
            </motion.div>
            
            {/* 농장 가기 버튼 (본인만) / 친구 추가 버튼 (타인) */}
            {isOwnProfile ? (
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
            ) : (
              <Button
                onClick={handleAddFriend}
                disabled={addingFriend || friendRequestSent || isFriend}
                className={cn(
                  'w-full gap-2',
                  friendRequestSent || isFriend
                    ? 'bg-gray-400 text-white'
                    : 'bg-blue-500 hover:bg-blue-600 text-white font-bold',
                  'border-4',
                  friendRequestSent || isFriend ? 'border-gray-500' : 'border-blue-700 shadow-[3px_3px_0_0_#1e40af]',
                  'transition-transform hover:translate-y-[-2px]'
                )}
              >
                {addingFriend ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : friendRequestSent ? (
                  <>
                    <UserCheck className="h-4 w-4" />
                    요청 보냄
                  </>
                ) : isFriend ? (
                  <>
                    <UserCheck className="h-4 w-4" />
                    친구
                  </>
                ) : (
                  <>
                    <UserPlus className="h-4 w-4" />
                    친구 추가
                  </>
                )}
              </Button>
            )}
            
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
                    className="flex items-center justify-center text-xl cursor-default"
                    style={{
                      textShadow: `
                        -1px -1px 0 #78350f,
                        1px -1px 0 #78350f,
                        -1px 1px 0 #78350f,
                        1px 1px 0 #78350f
                      `,
                    }}
                  >
                    {CROP_INFO[crop.type]?.emoji || '🌱'}
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
              {isOwnProfile ? '나의 농장' : `${username}님의 농장`}
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

              <div
                className="absolute bottom-2 left-2 flex gap-1 text-lg"
                style={{
                  textShadow: `
                    -1px -1px 0 #78350f,
                    1px -1px 0 #78350f,
                    -1px 1px 0 #78350f,
                    1px 1px 0 #78350f
                  `,
                }}
              >
                <span>🍅</span>
                <span>🥕</span>
                <span>🌾</span>
              </div>

              <div className="absolute inset-0 bg-black/30 flex items-center justify-center">
                <div className="bg-white/90 rounded-lg px-3 py-2 text-center">
                  <Lock className="h-5 w-5 text-amber-600 mx-auto mb-1" />
                  <p className="text-xs text-amber-800 font-medium">
                    {isOwnProfile ? '캐릭터를 만들어\n농장을 시작하세요!' : '아직 농장이 없습니다'}
                  </p>
                </div>
              </div>
            </div>

            {/* 본인 프로필일 때만 캐릭터 생성 버튼 표시 */}
            {isOwnProfile ? (
              <>
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
              </>
            ) : (
              /* 타인 프로필일 때 친구 추가 버튼 */
              <Button
                onClick={handleAddFriend}
                disabled={addingFriend || friendRequestSent || isFriend}
                className={cn(
                  'w-full gap-2',
                  friendRequestSent || isFriend
                    ? 'bg-gray-400 text-white'
                    : 'bg-blue-500 hover:bg-blue-600 text-white font-bold',
                  'border-4',
                  friendRequestSent || isFriend ? 'border-gray-500' : 'border-blue-700 shadow-[3px_3px_0_0_#1e40af]',
                  'transition-transform hover:translate-y-[-2px]'
                )}
              >
                {addingFriend ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : friendRequestSent ? (
                  <>
                    <UserCheck className="h-4 w-4" />
                    요청 보냄
                  </>
                ) : isFriend ? (
                  <>
                    <UserCheck className="h-4 w-4" />
                    친구
                  </>
                ) : (
                  <>
                    <UserPlus className="h-4 w-4" />
                    친구 추가
                  </>
                )}
              </Button>
            )}
          </motion.div>
        )}
      </div>

      {/* Level & XP */}
      <div className="rounded-xl border border-border bg-card p-4">
        <div className="mb-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-2xl font-bold text-primary">Lv.{displayLevel}</span>
            {isOwnProfile && profile?.subscription_tier && profile.subscription_tier !== 'free' && (
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
            {displayCurrentXP.toLocaleString()} / {displayRequiredXP.toLocaleString()} XP
          </span>
        </div>
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: '100%' }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <Progress value={displayXpProgress} className="h-3" />
        </motion.div>
        <p className="mt-2 text-xs text-muted-foreground">
          {displayRequiredXP - displayCurrentXP} XP to next level
        </p>
      </div>

      {/* Badges */}
      <div className="rounded-xl border border-border bg-card p-4">
        <div className="mb-3 flex items-center justify-between">
          <h4 className="text-sm font-medium text-muted-foreground">획득한 뱃지</h4>
          {displayBadges.length > 0 && (
            <span className="text-xs text-muted-foreground">{displayBadges.length}개</span>
          )}
        </div>
        {displayBadges.length > 0 ? (
          <div className="space-y-3">
            <div className="flex flex-wrap gap-2">
              {visibleBadges.map((badge) => (
                <motion.button
                  key={badge.id}
                  whileHover={{ scale: 1.15 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => setSelectedBadge({
                    id: badge.id,
                    name: badge.name,
                    description: badge.description,
                    rarity: badge.rarity as BadgeRarity,
                    iconUrl: 'iconUrl' in badge ? (badge as { iconUrl?: string }).iconUrl : undefined,
                    earnedAt: 'earnedAt' in badge ? (badge as { earnedAt?: string }).earnedAt : undefined,
                  })}
                  className={cn(
                    'rounded-lg p-1 transition-all',
                    'hover:bg-muted/50',
                    badge.rarity === 'legendary' && 'hover:shadow-[0_0_12px_rgba(251,191,36,0.5)]',
                    badge.rarity === 'epic' && 'hover:shadow-[0_0_10px_rgba(168,85,247,0.4)]',
                    badge.rarity === 'rare' && 'hover:shadow-[0_0_8px_rgba(59,130,246,0.3)]'
                  )}
                >
                  {'iconUrl' in badge && (badge as { iconUrl?: string }).iconUrl ? (
                    <img
                      src={(badge as { iconUrl?: string }).iconUrl}
                      alt={badge.name}
                      className="h-10 w-10 object-contain"
                    />
                  ) : (
                    <BadgeIcon name={badge.name} rarity={badge.rarity} size="md" />
                  )}
                </motion.button>
              ))}
            </div>
            {hasMoreBadges && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowAllBadges(!showAllBadges)}
                className="w-full text-xs text-muted-foreground hover:text-foreground"
              >
                {showAllBadges
                  ? '접기'
                  : `더보기 (+${displayBadges.length - BADGE_DISPLAY_LIMIT}개)`}
              </Button>
            )}
          </div>
        ) : (
          <p className="text-sm text-muted-foreground">아직 획득한 뱃지가 없습니다</p>
        )}
      </div>

      {/* Badge Detail Modal */}
      <BadgeDetailModal
        open={!!selectedBadge}
        onClose={() => setSelectedBadge(null)}
        badge={selectedBadge}
      />
    </div>
  );
}
