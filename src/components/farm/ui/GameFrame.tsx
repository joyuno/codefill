'use client';

/**
 * GameFrame - 픽셀 RPG 스타일 UI 프레임
 * 9-slice 스케일링 가능한 장식 프레임
 */

import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

interface GameFrameProps {
  children: React.ReactNode;
  variant?: 'default' | 'gold' | 'wood' | 'dark';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  animate?: boolean;
  glow?: boolean;
}

// 프레임 색상 팔레트
const FRAME_VARIANTS = {
  default: {
    outer: '#2D1B0E',
    border: '#5C3D2E',
    inner: '#8B5A3C',
    bg: 'linear-gradient(180deg, #6B4423 0%, #4A2C17 100%)',
    highlight: '#9B6B4A',
    shadow: '#1A0F08',
  },
  gold: {
    outer: '#4A3728',
    border: '#C9A227',
    inner: '#E8C547',
    bg: 'linear-gradient(180deg, #5C4025 0%, #3D2A1A 100%)',
    highlight: '#FFD700',
    shadow: '#2A1F14',
  },
  wood: {
    outer: '#1E1209',
    border: '#4A3628',
    inner: '#6B5344',
    bg: 'linear-gradient(180deg, #594639 0%, #3D2E24 100%)',
    highlight: '#7A6455',
    shadow: '#0F0905',
  },
  dark: {
    outer: '#0D0D12',
    border: '#2A2A3D',
    inner: '#3D3D5C',
    bg: 'linear-gradient(180deg, #1E1E2E 0%, #141420 100%)',
    highlight: '#4D4D6D',
    shadow: '#050508',
  },
};

const SIZE_CONFIG = {
  sm: { padding: '8px 12px', cornerSize: 6, borderWidth: 2 },
  md: { padding: '12px 16px', cornerSize: 8, borderWidth: 3 },
  lg: { padding: '16px 24px', cornerSize: 10, borderWidth: 4 },
};

export function GameFrame({
  children,
  variant = 'default',
  size = 'md',
  className,
  animate = false,
  glow = false,
}: GameFrameProps) {
  const colors = FRAME_VARIANTS[variant];
  const sizeConfig = SIZE_CONFIG[size];

  const frameStyle = {
    '--frame-outer': colors.outer,
    '--frame-border': colors.border,
    '--frame-inner': colors.inner,
    '--frame-bg': colors.bg,
    '--frame-highlight': colors.highlight,
    '--frame-shadow': colors.shadow,
    '--corner-size': `${sizeConfig.cornerSize}px`,
    '--border-width': `${sizeConfig.borderWidth}px`,
  } as React.CSSProperties;

  const content = (
    <div
      className={cn(
        'game-frame relative',
        glow && 'game-frame-glow',
        className
      )}
      style={frameStyle}
    >
      {/* 외곽 테두리 */}
      <div
        className="absolute inset-0 rounded-lg"
        style={{
          background: colors.outer,
          boxShadow: `
            inset 0 0 0 var(--border-width) var(--frame-border),
            0 4px 12px var(--frame-shadow)
          `,
        }}
      />

      {/* 내부 배경 */}
      <div
        className="absolute rounded-md"
        style={{
          inset: 'var(--border-width)',
          background: colors.bg,
          boxShadow: `
            inset 2px 2px 0 var(--frame-highlight),
            inset -2px -2px 0 var(--frame-shadow)
          `,
        }}
      />

      {/* 코너 장식 - 좌상단 */}
      <div
        className="absolute"
        style={{
          top: '-2px',
          left: '-2px',
          width: 'var(--corner-size)',
          height: 'var(--corner-size)',
          background: colors.border,
          clipPath: 'polygon(0 0, 100% 0, 0 100%)',
        }}
      />

      {/* 코너 장식 - 우상단 */}
      <div
        className="absolute"
        style={{
          top: '-2px',
          right: '-2px',
          width: 'var(--corner-size)',
          height: 'var(--corner-size)',
          background: colors.border,
          clipPath: 'polygon(0 0, 100% 0, 100% 100%)',
        }}
      />

      {/* 코너 장식 - 좌하단 */}
      <div
        className="absolute"
        style={{
          bottom: '-2px',
          left: '-2px',
          width: 'var(--corner-size)',
          height: 'var(--corner-size)',
          background: colors.border,
          clipPath: 'polygon(0 0, 0 100%, 100% 100%)',
        }}
      />

      {/* 코너 장식 - 우하단 */}
      <div
        className="absolute"
        style={{
          bottom: '-2px',
          right: '-2px',
          width: 'var(--corner-size)',
          height: 'var(--corner-size)',
          background: colors.border,
          clipPath: 'polygon(100% 0, 0 100%, 100% 100%)',
        }}
      />

      {/* 컨텐츠 */}
      <div
        className="relative z-10"
        style={{ padding: sizeConfig.padding }}
      >
        {children}
      </div>

      {/* 글로우 이펙트 */}
      {glow && (
        <div
          className="absolute inset-0 rounded-lg pointer-events-none animate-pulse"
          style={{
            boxShadow: `0 0 20px ${colors.highlight}40, 0 0 40px ${colors.highlight}20`,
          }}
        />
      )}

      <style jsx>{`
        .game-frame-glow {
          animation: frame-glow 2s ease-in-out infinite;
        }
        @keyframes frame-glow {
          0%, 100% { filter: brightness(1); }
          50% { filter: brightness(1.1); }
        }
      `}</style>
    </div>
  );

  if (animate) {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ type: 'spring', stiffness: 300, damping: 20 }}
      >
        {content}
      </motion.div>
    );
  }

  return content;
}

export default GameFrame;
