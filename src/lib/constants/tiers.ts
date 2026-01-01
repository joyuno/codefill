/**
 * 티어 시스템 상수
 *
 * DB 난이도 값과 티어 UI를 매핑합니다.
 * DB 값: easy, medium, medium_hard, hard, very_hard
 * 티어: 실버, 골드, 플래티넘, 다이아, 마스터
 */

import { ComponentType } from 'react';
import {
  SilverIcon,
  GoldIcon,
  PlatinumIcon,
  DiamondIcon,
  MasterIcon,
} from '@/components/icons/tiers';

// DB 난이도 타입
export type DifficultyDB = 'easy' | 'medium' | 'medium_hard' | 'hard' | 'very_hard';

// 티어 이름 타입
export type TierName = '실버' | '골드' | '플래티넘' | '다이아' | '마스터';

// 티어 정보 인터페이스
export interface TierInfo {
  name: TierName;
  nameEn: string;
  description: string;
  color: string;           // 텍스트 색상 (Tailwind)
  bgColor: string;         // 배경 색상 (Tailwind)
  borderColor: string;     // 테두리 색상 (Tailwind)
  dotColor: string;        // 점 색상 (Tailwind)
  Icon: ComponentType<{ size?: number; className?: string }>;
}

// DB 난이도 → 티어 매핑
export const DIFFICULTY_TO_TIER: Record<DifficultyDB, TierInfo> = {
  easy: {
    name: '실버',
    nameEn: 'Silver',
    description: '기본 개념 연습',
    color: 'text-gray-500',
    bgColor: 'bg-gray-500/10',
    borderColor: 'border-gray-500/30',
    dotColor: 'bg-gray-400',
    Icon: SilverIcon,
  },
  medium: {
    name: '골드',
    nameEn: 'Gold',
    description: '응용 문제',
    color: 'text-amber-500',
    bgColor: 'bg-amber-500/10',
    borderColor: 'border-amber-500/30',
    dotColor: 'bg-amber-400',
    Icon: GoldIcon,
  },
  medium_hard: {
    name: '플래티넘',
    nameEn: 'Platinum',
    description: '심화 응용',
    color: 'text-cyan-500',
    bgColor: 'bg-cyan-500/10',
    borderColor: 'border-cyan-500/30',
    dotColor: 'bg-cyan-400',
    Icon: PlatinumIcon,
  },
  hard: {
    name: '다이아',
    nameEn: 'Diamond',
    description: '도전적인 문제',
    color: 'text-violet-500',
    bgColor: 'bg-violet-500/10',
    borderColor: 'border-violet-500/30',
    dotColor: 'bg-violet-400',
    Icon: DiamondIcon,
  },
  very_hard: {
    name: '마스터',
    nameEn: 'Master',
    description: '최상위 난이도',
    color: 'text-rose-500',
    bgColor: 'bg-rose-500/10',
    borderColor: 'border-rose-500/30',
    dotColor: 'bg-rose-400',
    Icon: MasterIcon,
  },
};

// 티어 이름 → DB 난이도 역매핑 (사용자 입력 파싱용)
export const TIER_TO_DIFFICULTY: Record<string, DifficultyDB> = {
  // 한글
  '실버': 'easy',
  '골드': 'medium',
  '플래티넘': 'medium_hard',
  '플레티넘': 'medium_hard',  // 오타 대응
  '다이아': 'hard',
  '다이아몬드': 'hard',
  '마스터': 'very_hard',

  // 영어
  'silver': 'easy',
  'gold': 'medium',
  'platinum': 'medium_hard',
  'diamond': 'hard',
  'master': 'very_hard',

  // 기존 호환성 (기존 3단계)
  '쉬움': 'easy',
  '쉬운': 'easy',
  'easy': 'easy',
  '중간': 'medium',
  'medium': 'medium',
  '어려움': 'hard',
  '어려운': 'hard',
  'hard': 'hard',
};

// 티어 순서 (낮은 것 → 높은 것)
export const TIER_ORDER: DifficultyDB[] = [
  'easy',
  'medium',
  'medium_hard',
  'hard',
  'very_hard',
];

// 티어 칩 데이터 (챗봇용)
export const TIER_CHIPS = TIER_ORDER.map((difficulty) => {
  const tier = DIFFICULTY_TO_TIER[difficulty];
  return {
    label: tier.name,
    value: difficulty,
    category: 'difficulty',
  };
});

/**
 * DB 난이도 값으로 티어 정보 가져오기
 */
export function getTierInfo(difficulty: string): TierInfo {
  const normalizedDifficulty = difficulty.toLowerCase() as DifficultyDB;
  return DIFFICULTY_TO_TIER[normalizedDifficulty] || DIFFICULTY_TO_TIER.easy;
}

/**
 * 사용자 입력을 DB 난이도 값으로 변환
 */
export function parseTierInput(input: string): DifficultyDB | null {
  const normalized = input.toLowerCase().trim();
  return TIER_TO_DIFFICULTY[normalized] || null;
}

/**
 * 티어 비교 (a가 b보다 높으면 양수, 같으면 0, 낮으면 음수)
 */
export function compareTiers(a: DifficultyDB, b: DifficultyDB): number {
  return TIER_ORDER.indexOf(a) - TIER_ORDER.indexOf(b);
}
