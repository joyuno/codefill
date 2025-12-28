'use client';

import {
  Footprints,
  Flame,
  CalendarCheck,
  Crown,
  Target,
  Medal,
  Star,
  Trophy,
  Award,
  type LucideIcon
} from 'lucide-react';
import { cn } from '@/lib/utils';

// 뱃지 이름 → Lucide 아이콘 매핑
const BADGE_ICON_MAP: Record<string, LucideIcon> = {
  // DB 뱃지 (영어 이름)
  'first step': Footprints,
  'week warrior': Flame,
  'monthly master': CalendarCheck,
  'legendary learner': Crown,
  'half century': Target,
  'centurion': Medal,
  'rising star': Star,
  'expert': Trophy,

  // 한글 이름도 지원
  '첫 발걸음': Footprints,
  '주간 전사': Flame,
  '월간 마스터': CalendarCheck,
  '전설의 학습자': Crown,
  '하프 센츄리': Target,
  '센츄리온': Medal,
  '떠오르는 별': Star,
  '전문가': Trophy,

  // Mock 데이터 호환
  'first steps': Footprints,
  'algorithm master': Medal,
  'speed demon': Flame,
  'perfectionist': Crown,
};

// 뱃지 색상 (희귀도별)
const RARITY_COLORS: Record<string, string> = {
  common: 'text-gray-500 bg-gray-500/20',
  rare: 'text-blue-500 bg-blue-500/20',
  epic: 'text-purple-500 bg-purple-500/20',
  legendary: 'text-yellow-500 bg-yellow-500/20',
};

// 뱃지 이름별 기본 색상
const BADGE_COLORS: Record<string, string> = {
  'first step': 'text-cyan-500 bg-cyan-500/20',
  'first steps': 'text-cyan-500 bg-cyan-500/20',
  'week warrior': 'text-orange-500 bg-orange-500/20',
  'monthly master': 'text-purple-500 bg-purple-500/20',
  'legendary learner': 'text-yellow-500 bg-yellow-500/20',
  'half century': 'text-blue-500 bg-blue-500/20',
  'centurion': 'text-gray-400 bg-gray-400/20',
  'rising star': 'text-yellow-400 bg-yellow-400/20',
  'expert': 'text-amber-500 bg-amber-500/20',
  'algorithm master': 'text-green-500 bg-green-500/20',
  'speed demon': 'text-red-500 bg-red-500/20',
  'perfectionist': 'text-pink-500 bg-pink-500/20',
};

interface BadgeIconProps {
  name: string;
  rarity?: 'common' | 'rare' | 'epic' | 'legendary';
  size?: 'sm' | 'md' | 'lg';
  showBackground?: boolean;
  className?: string;
}

export function BadgeIcon({
  name,
  rarity,
  size = 'md',
  showBackground = true,
  className
}: BadgeIconProps) {
  const normalizedName = name.toLowerCase();
  const Icon = BADGE_ICON_MAP[normalizedName] || Award;

  // 색상 결정: rarity가 있으면 rarity 색상, 없으면 뱃지별 색상
  const colorClass = rarity
    ? RARITY_COLORS[rarity]
    : BADGE_COLORS[normalizedName] || 'text-primary bg-primary/20';

  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-5 w-5',
    lg: 'h-6 w-6',
  };

  const containerSizes = {
    sm: 'h-8 w-8',
    md: 'h-10 w-10',
    lg: 'h-12 w-12',
  };

  if (showBackground) {
    return (
      <div className={cn(
        'flex items-center justify-center rounded-lg',
        containerSizes[size],
        colorClass,
        className
      )}>
        <Icon className={sizeClasses[size]} />
      </div>
    );
  }

  return (
    <Icon className={cn(
      sizeClasses[size],
      colorClass.split(' ')[0], // text color only
      className
    )} />
  );
}

// 뱃지 정보와 함께 아이콘을 반환하는 유틸리티
export function getBadgeIconInfo(name: string) {
  const normalizedName = name.toLowerCase();
  return {
    Icon: BADGE_ICON_MAP[normalizedName] || Award,
    color: BADGE_COLORS[normalizedName] || 'text-primary bg-primary/20',
  };
}
