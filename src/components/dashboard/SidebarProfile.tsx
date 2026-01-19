'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { Progress } from '@/components/ui/progress';
import { usersApi, publicProfileApi, type PublicFarm, type PublicBadge } from '@/lib/api/users';
import { farmApi, type InventoryItem } from '@/lib/api/farm';
import type { Badge as BadgeType } from '@/lib/types';
import { Sparkles, Lock, Leaf, UserPlus, Home, Coins, TrendingUp, Loader2, UserCheck, Sprout, Package, Settings } from 'lucide-react';
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
  type MinimapSlot,
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

// 농장 슬롯을 미니맵용 슬롯으로 변환
function convertToMinimapSlots(
  farmSlots?: Array<{ cropCode?: string | null; slot?: number; stage?: number; plantedAt?: string | null; growTimeSeconds?: number | null }>,
  publicSlots?: Array<{ cropType?: string | null; slotIndex?: number; stage?: number }>
): MinimapSlot[] {
  // 본인 프로필 (farmSlots)
  if (farmSlots && farmSlots.length > 0) {
    return farmSlots.map(s => ({
      cropCode: s.cropCode || null,
      stage: s.stage || 0,
      plantedAt: s.plantedAt || null,
      growTimeSeconds: s.growTimeSeconds || null,
    }));
  }
  // 타인 프로필 (publicSlots)
  if (publicSlots && publicSlots.length > 0) {
    return publicSlots.map(s => ({
      cropCode: s.cropType || null,
      stage: s.stage || 0,
    }));
  }
  return [];
}

// 남은 시간 계산 (초 단위)
function calculateRemainingSeconds(slot: MinimapSlot): number {
  if (!slot.plantedAt || !slot.growTimeSeconds) return Infinity;
  const plantedTime = new Date(slot.plantedAt).getTime();
  const now = Date.now();
  const elapsedSeconds = Math.floor((now - plantedTime) / 1000);
  const remaining = slot.growTimeSeconds - elapsedSeconds;
  return Math.max(0, remaining);
}

// 실시간 stage 계산 (plantedAt, growTimeSeconds 기반) - 7단계 (0~6)
function calculateStage(slot: MinimapSlot): number {
  if (!slot.cropCode) return 0;
  if (!slot.plantedAt || !slot.growTimeSeconds) return slot.stage;

  const plantedTime = new Date(slot.plantedAt).getTime();
  const now = Date.now();
  const elapsedSeconds = Math.floor((now - plantedTime) / 1000);
  const progress = elapsedSeconds / slot.growTimeSeconds;

  if (progress >= 1) return 6; // 수확 가능
  if (progress >= 0.833) return 5;
  if (progress >= 0.667) return 4;
  if (progress >= 0.5) return 3;
  if (progress >= 0.333) return 2;
  if (progress >= 0.167) return 1;
  return 0; // 씨앗
}

// 작물 슬롯 정렬 (수확 가능 우선 → 남은 시간 짧은 순)
function sortCropSlots(slots: MinimapSlot[]): MinimapSlot[] {
  return [...slots].sort((a, b) => {
    // 1. 수확 가능(실시간 stage >= 6)한 작물 우선
    const aReady = calculateStage(a) >= 6;
    const bReady = calculateStage(b) >= 6;
    if (aReady && !bReady) return -1;
    if (!aReady && bReady) return 1;

    // 2. 둘 다 수확 가능하면 순서 유지
    if (aReady && bReady) return 0;

    // 3. 남은 시간 짧은 순
    const aRemaining = calculateRemainingSeconds(a);
    const bRemaining = calculateRemainingSeconds(b);
    return aRemaining - bRemaining;
  });
}

// 남은 시간 포맷팅 (초 → "M:SS" 또는 "H:MM")
function formatRemainingTime(seconds: number): string {
  if (seconds <= 0 || seconds === Infinity) return '';

  if (seconds < 60) {
    return `${seconds}s`;
  } else if (seconds < 3600) {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return secs > 0 ? `${mins}:${secs.toString().padStart(2, '0')}` : `${mins}m`;
  } else {
    const hours = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    return mins > 0 ? `${hours}h${mins}m` : `${hours}h`;
  }
}

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
  const [isEditingCharacter, setIsEditingCharacter] = useState(false);
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

  // 씨앗/작물 탭 상태
  const [farmTabActive, setFarmTabActive] = useState<'seeds' | 'crops'>('crops');
  // 인벤토리 (씨앗용)
  const [inventory, setInventory] = useState<InventoryItem[]>([]);

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

  // 인벤토리 로드 (씨앗 표시용)
  useEffect(() => {
    if (isAuthenticated && isOwnProfile) {
      farmApi.getInventory()
        .then(setInventory)
        .catch(() => setInventory([]));
    }
  }, [isAuthenticated, isOwnProfile]);

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

      // 헤어스타일 파일명 조합: Hairstyle_Short_Brown_Dark 형태
      const hairStyleFull = `${newCharacter.appearance.hair}_${newCharacter.appearance.hairColor}`;

      const updatedFarm = await farmApi.createCharacter({
        name: newCharacter.name,
        body: newCharacter.appearance.body,
        hair: hairStyleFull,
        hairColor,
        face: newCharacter.appearance.face,
        outfit: newCharacter.appearance.clothes,
        outfitColor: hairColor,
        accessory: newCharacter.appearance.accessory,
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

  // 캐릭터 수정 핸들러
  const handleCharacterUpdate = async (updatedCharacter: CharacterData) => {
    try {
      const hairColor = updatedCharacter.appearance.color.startsWith('#')
        ? updatedCharacter.appearance.color
        : COLOR_MAP[updatedCharacter.appearance.color] || '#8B4513';

      const hairStyleFull = `${updatedCharacter.appearance.hair}_${updatedCharacter.appearance.hairColor}`;

      const updatedFarm = await farmApi.updateCharacter({
        name: updatedCharacter.name,
        body: updatedCharacter.appearance.body,
        hair: hairStyleFull,
        hairColor,
        face: updatedCharacter.appearance.face,
        outfit: updatedCharacter.appearance.clothes,
        outfitColor: hairColor,
        accessory: updatedCharacter.appearance.accessory,
        farmName: updatedCharacter.farmName,
      });
      setFarm(updatedFarm);
      setFarmToCache(updatedFarm);
      setShowCharacterModal(false);
      setIsEditingCharacter(false);
    } catch (error) {
      console.error('캐릭터 수정 실패:', error);
    }
  };

  // 캐릭터 수정 모달 열기
  const handleOpenEditCharacter = () => {
    setIsEditingCharacter(true);
    setShowCharacterModal(true);
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

  // 수정 모달용 초기 데이터 (CharacterData 형식)
  const editInitialData: CharacterData | null = farm?.characterData ? (() => {
    // hair가 "Short_Brown_Dark" 형태 → "Short"와 "Brown_Dark"로 분리
    const hairParts = farm.characterData.hair?.split('_') || ['Short', 'Brown', 'Dark'];
    const hairStyle = hairParts[0] || 'Short'; // Short, Long, Tuft 등
    const hairColorId = hairParts.slice(1).join('_') || 'Brown_Dark'; // Brown_Dark 등

    return {
      name: farm.characterData.name,
      appearance: {
        body: farm.characterData.body || 'Body_1',
        hair: hairStyle,
        hairColor: hairColorId,
        face: farm.characterData.face,
        clothes: farm.characterData.outfit,
        accessory: farm.characterData.accessory || 'none',
        color: farm.characterData.hairColor || '#3d2314',
      },
      farmName: farm.characterData.farmName,
    };
  })() : null;

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
      {/* Character Creation/Edit Modal */}
      <CharacterCreationModal
        open={showCharacterModal}
        onClose={() => {
          setShowCharacterModal(false);
          setIsEditingCharacter(false);
        }}
        onComplete={isEditingCharacter ? handleCharacterUpdate : handleCharacterCreate}
        initialData={isEditingCharacter ? editInitialData : null}
        isEditing={isEditingCharacter}
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
              onClick={() => loadFarmData(true)}
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
                'flex items-center justify-between px-3 py-1.5 rounded-t-xl',
                'bg-amber-600 border-4 border-b-0 border-amber-800'
              )}>
                <div className="flex items-center gap-2">
                  <Home className="h-4 w-4 text-amber-100" />
                  <span className="font-bold text-sm text-amber-100">
                    {character.farmName || '나의 농장'}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="flex items-center gap-1 text-xs text-amber-200">
                    <Coins className="h-3 w-3" />
                    <span>{gold.toLocaleString()}G</span>
                  </div>
                  {/* 캐릭터 수정 버튼 (본인 프로필만) */}
                  {isOwnProfile && (
                    <button
                      onClick={handleOpenEditCharacter}
                      className={cn(
                        'p-1 rounded hover:bg-amber-500/50 transition-colors',
                        'text-amber-200 hover:text-amber-100'
                      )}
                      title="캐릭터 수정"
                    >
                      <Settings className="h-4 w-4" />
                    </button>
                  )}
                </div>
              </div>
              
              {/* 농장 미니맵 - 실제 데이터 연동 */}
              <FarmMinimap
                level={farmLevel}
                farmSlots={convertToMinimapSlots(
                  isOwnProfile ? farm?.farmSlots : undefined,
                  !isOwnProfile ? publicFarm?.slots : undefined
                )}
                farmSize={isOwnProfile ? (farm?.farmSize || 9) : 9}
                className="rounded-t-none"
              />

              {/* 캐릭터 정보 오버레이 (한 줄) */}
              <div className={cn(
                'absolute bottom-4 left-2 right-2 z-20',
                'flex items-center justify-between px-3 py-1.5 rounded-lg',
                'bg-black/40 backdrop-blur-sm'
              )}>
                <span className="font-bold text-sm text-white truncate">{character.name}</span>
                <span className="text-xs text-amber-300">Lv.{displayLevel} 농부</span>
                {(() => {
                  const slots = convertToMinimapSlots(
                    isOwnProfile ? farm?.farmSlots : undefined,
                    !isOwnProfile ? publicFarm?.slots : undefined
                  );
                  const readyCount = slots.filter(s => calculateStage(s) >= 6).length;
                  return readyCount > 0 ? (
                    <div className="text-xs text-green-400 flex items-center gap-1">
                      <TrendingUp className="h-3 w-3" />
                      <span>{readyCount} 수확</span>
                    </div>
                  ) : (
                    <div className="text-xs text-amber-200/70">
                      농장 Lv.{farmLevel}
                    </div>
                  );
                })()}
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
            
            {/* 씨앗/작물 탭 UI */}
            {(() => {
              const slots = convertToMinimapSlots(
                isOwnProfile ? farm?.farmSlots : undefined,
                !isOwnProfile ? publicFarm?.slots : undefined
              );
              const cropsWithData = sortCropSlots(slots.filter(s => s.cropCode));

              // 씨앗 인벤토리 필터링 (seed_ 또는 _seed로 시작하는 아이템)
              const seedItems = inventory.filter(item =>
                item.itemCode.startsWith('seed_') || item.itemCode.includes('_seed')
              );

              return (
                <div className={cn(
                  'rounded-xl overflow-hidden',
                  'bg-gradient-to-b from-amber-100 to-amber-50',
                  'border-2 border-amber-500'
                )}>
                  {/* 탭 헤더 */}
                  <div className="flex border-b border-amber-300">
                    <button
                      onClick={() => setFarmTabActive('crops')}
                      className={cn(
                        'flex-1 px-3 py-2 text-xs font-bold flex items-center justify-center gap-1 transition-colors',
                        farmTabActive === 'crops'
                          ? 'bg-amber-200 text-amber-900'
                          : 'bg-amber-50 text-amber-600 hover:bg-amber-100'
                      )}
                    >
                      <Leaf className="h-3 w-3" />
                      작물 ({cropsWithData.length})
                    </button>
                    <button
                      onClick={() => setFarmTabActive('seeds')}
                      className={cn(
                        'flex-1 px-3 py-2 text-xs font-bold flex items-center justify-center gap-1 transition-colors',
                        farmTabActive === 'seeds'
                          ? 'bg-green-200 text-green-900'
                          : 'bg-amber-50 text-amber-600 hover:bg-amber-100'
                      )}
                    >
                      <Sprout className="h-3 w-3" />
                      씨앗 ({seedItems.reduce((sum, i) => sum + i.quantity, 0)})
                    </button>
                  </div>

                  {/* 탭 컨텐츠 */}
                  <div className="p-3">
                    {farmTabActive === 'crops' ? (
                      // 작물 현황 탭
                      cropsWithData.length === 0 ? (
                        <p className="text-xs text-amber-600 text-center py-2">아직 심은 작물이 없어요</p>
                      ) : (
                        <div
                          className="flex gap-2 overflow-x-auto pb-1"
                          style={{ scrollbarWidth: 'thin', scrollbarColor: '#fcd34d #fef3c7' }}
                        >
                          {cropsWithData.map((slot, i) => {
                            const cropInfo = slot.cropCode ? CROP_INFO[slot.cropCode as keyof typeof CROP_INFO] : null;
                            const currentStage = calculateStage(slot);
                            const isReady = currentStage >= 6;
                            const remaining = calculateRemainingSeconds(slot);
                            const timeText = isReady ? '완료' : formatRemainingTime(remaining);
                            return (
                              <motion.div
                                key={i}
                                whileHover={{ scale: 1.05 }}
                                title={cropInfo?.name || '작물'}
                                className={cn(
                                  'flex flex-col items-center cursor-default flex-shrink-0',
                                  isReady && 'animate-pulse'
                                )}
                              >
                                <div className="relative w-8 h-8">
                                  {cropInfo?.icon ? (
                                    <img
                                      src={cropInfo.icon}
                                      alt={cropInfo.name}
                                      className="w-8 h-8 object-contain"
                                      style={{ imageRendering: 'pixelated' }}
                                    />
                                  ) : (
                                    <span className="text-lg">🌱</span>
                                  )}
                                  {isReady && (
                                    <span className="absolute -top-1 -right-2 text-[8px]">✨</span>
                                  )}
                                </div>
                                <span className={cn(
                                  'text-[9px] font-medium leading-none mt-0.5',
                                  isReady ? 'text-green-600' : 'text-amber-700'
                                )}>
                                  {timeText}
                                </span>
                              </motion.div>
                            );
                          })}
                        </div>
                      )
                    ) : (
                      // 씨앗 현황 탭
                      seedItems.length === 0 ? (
                        <p className="text-xs text-green-600 text-center py-2">보유한 씨앗이 없어요</p>
                      ) : (
                        <div
                          className="space-y-1 max-h-[140px] overflow-y-auto overflow-x-hidden pr-1"
                          style={{ scrollbarWidth: 'thin', scrollbarColor: '#86efac #dcfce7' }}
                        >
                          {seedItems.map((item) => {
                            // seed_tomato → tomato 형태로 변환하여 CROP_INFO 조회
                            const cropCode = item.itemCode.replace('seed_', '').replace('_seed', '');
                            const cropInfo = CROP_INFO[cropCode as keyof typeof CROP_INFO];
                            return (
                              <div
                                key={item.itemCode}
                                className="flex items-center justify-between px-2 py-1 bg-green-100 rounded-lg"
                              >
                                <div className="flex items-center gap-2">
                                  {cropInfo?.icon ? (
                                    <img
                                      src={cropInfo.icon}
                                      alt={cropInfo.name}
                                      className="w-5 h-5 object-contain"
                                      style={{ imageRendering: 'pixelated' }}
                                    />
                                  ) : (
                                    <span className="text-lg">🌱</span>
                                  )}
                                  <span className="text-xs font-medium text-green-800">
                                    {cropInfo?.name || item.itemCode} 씨앗
                                  </span>
                                </div>
                                <span className="text-xs font-bold text-green-700 bg-green-200 px-2 py-0.5 rounded-full">
                                  x{item.quantity}
                                </span>
                              </div>
                            );
                          })}
                        </div>
                      )
                    )}
                  </div>
                </div>
              );
            })()}
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
