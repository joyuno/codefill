'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { X, Sparkles, Star, Crown, Gem, Award } from 'lucide-react';
import { cn } from '@/lib/utils';

export type BadgeRarity = 'common' | 'uncommon' | 'rare' | 'epic' | 'legendary';

interface BadgeDetailModalProps {
  open: boolean;
  onClose: () => void;
  badge: {
    id: string;
    name: string;
    description: string;
    rarity: BadgeRarity;
    icon?: string;
    iconUrl?: string;
    earnedAt?: string;
  } | null;
}

// 등급별 스타일 설정
const RARITY_STYLES: Record<BadgeRarity, {
  bgGradient: string;
  borderColor: string;
  glowColor: string;
  textColor: string;
  iconBg: string;
  label: string;
  labelColor: string;
  Icon: typeof Star;
}> = {
  common: {
    bgGradient: 'from-slate-800 via-slate-700 to-slate-800',
    borderColor: 'border-slate-500',
    glowColor: '',
    textColor: 'text-slate-300',
    iconBg: 'bg-slate-600',
    label: 'Common',
    labelColor: 'text-slate-400',
    Icon: Award,
  },
  uncommon: {
    bgGradient: 'from-green-900 via-green-800 to-green-900',
    borderColor: 'border-green-500',
    glowColor: 'shadow-[0_0_30px_rgba(34,197,94,0.3)]',
    textColor: 'text-green-300',
    iconBg: 'bg-green-700',
    label: 'Uncommon',
    labelColor: 'text-green-400',
    Icon: Star,
  },
  rare: {
    bgGradient: 'from-blue-900 via-blue-800 to-blue-900',
    borderColor: 'border-blue-400',
    glowColor: 'shadow-[0_0_40px_rgba(59,130,246,0.4)]',
    textColor: 'text-blue-300',
    iconBg: 'bg-blue-700',
    label: 'Rare',
    labelColor: 'text-blue-400',
    Icon: Star,
  },
  epic: {
    bgGradient: 'from-purple-900 via-purple-800 to-purple-900',
    borderColor: 'border-purple-400',
    glowColor: 'shadow-[0_0_50px_rgba(168,85,247,0.5)]',
    textColor: 'text-purple-300',
    iconBg: 'bg-purple-700',
    label: 'Epic',
    labelColor: 'text-purple-400',
    Icon: Gem,
  },
  legendary: {
    bgGradient: 'from-amber-900 via-yellow-700 to-amber-900',
    borderColor: 'border-yellow-400',
    glowColor: 'shadow-[0_0_60px_rgba(251,191,36,0.6)]',
    textColor: 'text-yellow-300',
    iconBg: 'bg-gradient-to-br from-yellow-500 to-amber-600',
    label: 'Legendary',
    labelColor: 'text-yellow-400',
    Icon: Crown,
  },
};

export function BadgeDetailModal({ open, onClose, badge }: BadgeDetailModalProps) {
  if (!badge) return null;

  const style = RARITY_STYLES[badge.rarity] || RARITY_STYLES.common;
  const RarityIcon = style.Icon;

  return (
    <AnimatePresence>
      {open && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm"
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.8, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.8, y: 20 }}
            transition={{ type: 'spring', damping: 25, stiffness: 300 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4"
            onClick={onClose}
          >
            <div
              onClick={(e) => e.stopPropagation()}
              className={cn(
                'relative w-full max-w-sm rounded-2xl border-2 p-6',
                'bg-gradient-to-b',
                style.bgGradient,
                style.borderColor,
                style.glowColor
              )}
            >
              {/* Close button */}
              <button
                onClick={onClose}
                className="absolute right-3 top-3 rounded-full p-1 text-white/60 hover:bg-white/10 hover:text-white transition-colors"
              >
                <X className="h-5 w-5" />
              </button>

              {/* Legendary 파티클 효과 */}
              {badge.rarity === 'legendary' && (
                <div className="absolute inset-0 overflow-hidden rounded-2xl pointer-events-none">
                  {[...Array(12)].map((_, i) => (
                    <motion.div
                      key={i}
                      className="absolute w-1 h-1 bg-yellow-400 rounded-full"
                      initial={{
                        x: '50%',
                        y: '50%',
                        opacity: 0,
                      }}
                      animate={{
                        x: `${Math.random() * 100}%`,
                        y: `${Math.random() * 100}%`,
                        opacity: [0, 1, 0],
                      }}
                      transition={{
                        duration: 2 + Math.random() * 2,
                        repeat: Infinity,
                        delay: Math.random() * 2,
                      }}
                    />
                  ))}
                </div>
              )}

              {/* Epic 반짝임 효과 */}
              {badge.rarity === 'epic' && (
                <motion.div
                  className="absolute inset-0 rounded-2xl pointer-events-none"
                  animate={{
                    background: [
                      'radial-gradient(circle at 30% 30%, rgba(168,85,247,0.2) 0%, transparent 50%)',
                      'radial-gradient(circle at 70% 70%, rgba(168,85,247,0.2) 0%, transparent 50%)',
                      'radial-gradient(circle at 30% 30%, rgba(168,85,247,0.2) 0%, transparent 50%)',
                    ],
                  }}
                  transition={{ duration: 3, repeat: Infinity }}
                />
              )}

              {/* 등급 라벨 */}
              <div className="flex items-center justify-center gap-1 mb-4">
                <RarityIcon className={cn('h-4 w-4', style.labelColor)} />
                <span className={cn('text-sm font-bold uppercase tracking-wider', style.labelColor)}>
                  {style.label}
                </span>
                <RarityIcon className={cn('h-4 w-4', style.labelColor)} />
              </div>

              {/* 뱃지 아이콘 */}
              <div className="flex justify-center mb-4">
                <motion.div
                  animate={badge.rarity === 'legendary' ? {
                    rotate: [0, 5, -5, 0],
                    scale: [1, 1.05, 1],
                  } : badge.rarity === 'epic' ? {
                    scale: [1, 1.03, 1],
                  } : {}}
                  transition={{ duration: 2, repeat: Infinity }}
                  className={cn(
                    'relative rounded-2xl p-4',
                    style.iconBg,
                    badge.rarity === 'legendary' && 'ring-4 ring-yellow-400/50',
                    badge.rarity === 'epic' && 'ring-2 ring-purple-400/50'
                  )}
                >
                  {badge.iconUrl ? (
                    <img
                      src={badge.iconUrl}
                      alt={badge.name}
                      className="h-20 w-20 object-contain"
                    />
                  ) : (
                    <div className="h-20 w-20 flex items-center justify-center text-5xl">
                      🏆
                    </div>
                  )}

                  {/* Legendary 빛 효과 */}
                  {badge.rarity === 'legendary' && (
                    <motion.div
                      className="absolute inset-0 rounded-2xl"
                      animate={{
                        boxShadow: [
                          '0 0 20px rgba(251,191,36,0.5)',
                          '0 0 40px rgba(251,191,36,0.8)',
                          '0 0 20px rgba(251,191,36,0.5)',
                        ],
                      }}
                      transition={{ duration: 1.5, repeat: Infinity }}
                    />
                  )}
                </motion.div>
              </div>

              {/* 뱃지 이름 */}
              <h3 className={cn(
                'text-center text-xl font-bold mb-2',
                badge.rarity === 'legendary' ? 'text-yellow-200' : 'text-white'
              )}>
                {badge.name}
              </h3>

              {/* 뱃지 설명 */}
              <p className={cn('text-center text-sm mb-4', style.textColor)}>
                {badge.description}
              </p>

              {/* 획득일 */}
              {badge.earnedAt && (
                <div className="pt-4 border-t border-white/10">
                  <p className="text-center text-xs text-white/50">
                    획득일: {new Date(badge.earnedAt).toLocaleDateString('ko-KR', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric',
                    })}
                  </p>
                </div>
              )}

              {/* 장식 라인 */}
              <div className="absolute bottom-0 left-0 right-0 h-1 rounded-b-2xl overflow-hidden">
                <motion.div
                  className={cn(
                    'h-full',
                    badge.rarity === 'legendary'
                      ? 'bg-gradient-to-r from-yellow-600 via-yellow-400 to-yellow-600'
                      : badge.rarity === 'epic'
                      ? 'bg-gradient-to-r from-purple-600 via-purple-400 to-purple-600'
                      : badge.rarity === 'rare'
                      ? 'bg-gradient-to-r from-blue-600 via-blue-400 to-blue-600'
                      : badge.rarity === 'uncommon'
                      ? 'bg-gradient-to-r from-green-600 via-green-400 to-green-600'
                      : 'bg-gradient-to-r from-slate-600 via-slate-400 to-slate-600'
                  )}
                  animate={{
                    x: ['-100%', '100%'],
                  }}
                  transition={{
                    duration: badge.rarity === 'legendary' ? 2 : 3,
                    repeat: Infinity,
                    ease: 'linear',
                  }}
                />
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
