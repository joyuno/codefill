'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Trophy, Sparkles, X } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from './button';

interface NewBadge {
  code: string;
  name: string;
  iconUrl?: string | null;
  rarity: string;
}

interface BadgePopupProps {
  badges: NewBadge[];
  onClose: () => void;
}

// 희귀도별 색상 및 이펙트
const RARITY_CONFIG: Record<string, {
  bg: string;
  border: string;
  glow: string;
  text: string;
  label: string;
  particles: string;
}> = {
  common: {
    bg: 'from-gray-900 to-gray-800',
    border: 'border-gray-500',
    glow: 'shadow-gray-500/50',
    text: 'text-gray-300',
    label: '일반',
    particles: '#9CA3AF',
  },
  uncommon: {
    bg: 'from-green-900 to-green-800',
    border: 'border-green-500',
    glow: 'shadow-green-500/50',
    text: 'text-green-400',
    label: '고급',
    particles: '#22C55E',
  },
  rare: {
    bg: 'from-blue-900 to-blue-800',
    border: 'border-blue-500',
    glow: 'shadow-blue-500/50',
    text: 'text-blue-400',
    label: '희귀',
    particles: '#3B82F6',
  },
  epic: {
    bg: 'from-purple-900 to-purple-800',
    border: 'border-purple-500',
    glow: 'shadow-purple-500/50',
    text: 'text-purple-400',
    label: '영웅',
    particles: '#A855F7',
  },
  legendary: {
    bg: 'from-yellow-900 to-amber-800',
    border: 'border-yellow-500',
    glow: 'shadow-yellow-500/50',
    text: 'text-yellow-400',
    label: '전설',
    particles: '#EAB308',
  },
};

// 파티클 컴포넌트
function Particles({ color, count = 20 }: { color: string; count?: number }) {
  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      {Array.from({ length: count }).map((_, i) => (
        <motion.div
          key={i}
          className="absolute w-2 h-2 rounded-full"
          style={{ backgroundColor: color }}
          initial={{
            x: '50%',
            y: '50%',
            scale: 0,
            opacity: 1,
          }}
          animate={{
            x: `${Math.random() * 100}%`,
            y: `${Math.random() * 100}%`,
            scale: [0, 1, 0],
            opacity: [1, 1, 0],
          }}
          transition={{
            duration: 1.5,
            delay: Math.random() * 0.5,
            ease: 'easeOut',
          }}
        />
      ))}
    </div>
  );
}

// 반짝이는 별 컴포넌트
function SparkleStars({ color }: { color: string }) {
  return (
    <>
      {Array.from({ length: 6 }).map((_, i) => (
        <motion.div
          key={i}
          className="absolute"
          style={{
            left: `${15 + Math.random() * 70}%`,
            top: `${15 + Math.random() * 70}%`,
          }}
          initial={{ scale: 0, rotate: 0 }}
          animate={{
            scale: [0, 1, 0],
            rotate: [0, 180, 360],
          }}
          transition={{
            duration: 2,
            delay: i * 0.2,
            repeat: Infinity,
            repeatDelay: 1,
          }}
        >
          <Sparkles className="h-4 w-4" style={{ color }} />
        </motion.div>
      ))}
    </>
  );
}

export function BadgePopup({ badges, onClose }: BadgePopupProps) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const currentBadge = badges[currentIndex];
  const config = RARITY_CONFIG[currentBadge?.rarity || 'common'];

  const handleNext = () => {
    if (currentIndex < badges.length - 1) {
      setCurrentIndex(currentIndex + 1);
    } else {
      onClose();
    }
  };

  // ESC 키로 닫기
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
      if (e.key === 'Enter' || e.key === ' ') handleNext();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [currentIndex, badges.length]);

  if (!currentBadge) return null;

  return (
    <AnimatePresence>
      <motion.div
        className="fixed inset-0 z-50 flex items-center justify-center"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
      >
        {/* 배경 오버레이 */}
        <motion.div
          className="absolute inset-0 bg-black/80 backdrop-blur-sm"
          onClick={onClose}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        />

        {/* 메인 카드 */}
        <motion.div
          className={cn(
            'relative w-[340px] rounded-2xl border-2 p-8 text-center',
            'bg-gradient-to-b shadow-2xl',
            config.bg,
            config.border,
            config.glow
          )}
          initial={{ scale: 0, rotate: -10 }}
          animate={{ scale: 1, rotate: 0 }}
          exit={{ scale: 0, rotate: 10 }}
          transition={{ type: 'spring', damping: 15, stiffness: 300 }}
        >
          {/* 파티클 이펙트 */}
          <Particles color={config.particles} count={30} />
          <SparkleStars color={config.particles} />

          {/* 닫기 버튼 */}
          <button
            onClick={onClose}
            className="absolute top-3 right-3 p-1 rounded-full hover:bg-white/10 transition-colors"
          >
            <X className="h-5 w-5 text-white/60" />
          </button>

          {/* 타이틀 */}
          <motion.div
            className="flex items-center justify-center gap-2 mb-6"
            initial={{ y: -20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.2 }}
          >
            <Trophy className="h-6 w-6 text-yellow-400" />
            <h2 className="text-2xl font-bold text-white">뱃지 획득!</h2>
            <Trophy className="h-6 w-6 text-yellow-400" />
          </motion.div>

          {/* 뱃지 아이콘 */}
          <motion.div
            className="relative mx-auto mb-6"
            initial={{ scale: 0, rotate: -180 }}
            animate={{ scale: 1, rotate: 0 }}
            transition={{ delay: 0.3, type: 'spring', damping: 10 }}
          >
            <div className={cn(
              'w-28 h-28 mx-auto rounded-full flex items-center justify-center',
              'bg-gradient-to-br from-white/20 to-white/5',
              'border-4',
              config.border
            )}>
              {currentBadge.iconUrl ? (
                <img
                  src={currentBadge.iconUrl}
                  alt={currentBadge.name}
                  className="w-20 h-20 object-contain"
                />
              ) : (
                <Trophy className={cn('w-16 h-16', config.text)} />
              )}
            </div>

            {/* 글로우 이펙트 */}
            <motion.div
              className={cn(
                'absolute inset-0 rounded-full blur-xl opacity-50',
                'bg-gradient-to-br',
                config.bg
              )}
              animate={{
                scale: [1, 1.2, 1],
                opacity: [0.3, 0.5, 0.3],
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
              }}
              style={{ zIndex: -1 }}
            />
          </motion.div>

          {/* 뱃지 이름 */}
          <motion.h3
            className="text-xl font-bold text-white mb-2"
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.4 }}
          >
            {currentBadge.name}
          </motion.h3>

          {/* 희귀도 라벨 */}
          <motion.div
            className={cn(
              'inline-block px-4 py-1 rounded-full text-sm font-semibold mb-6',
              'bg-white/10',
              config.text
            )}
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.5 }}
          >
            {config.label} 등급
          </motion.div>

          {/* 버튼 */}
          <motion.div
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.6 }}
          >
            <Button
              onClick={handleNext}
              className={cn(
                'w-full py-3 text-lg font-semibold',
                'bg-white/20 hover:bg-white/30 text-white border-0'
              )}
            >
              {currentIndex < badges.length - 1
                ? `다음 (${currentIndex + 1}/${badges.length})`
                : '확인'}
            </Button>
          </motion.div>

          {/* 진행 표시 */}
          {badges.length > 1 && (
            <div className="flex justify-center gap-1 mt-4">
              {badges.map((_, i) => (
                <div
                  key={i}
                  className={cn(
                    'w-2 h-2 rounded-full transition-colors',
                    i === currentIndex ? 'bg-white' : 'bg-white/30'
                  )}
                />
              ))}
            </div>
          )}
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}
