import React from 'react';

interface TierIconProps {
  size?: number;
  className?: string;
}

const MasterIcon: React.FC<TierIconProps> = ({ size = 64, className = '' }) => {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 64 64"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      <defs>
        {/* Red/Crimson gradients for Grandmaster style */}
        <linearGradient id="masterLeft" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#FCA5A5" />
          <stop offset="50%" stopColor="#DC2626" />
          <stop offset="100%" stopColor="#7F1D1D" />
        </linearGradient>
        <linearGradient id="masterRight" x1="100%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor="#FECACA" />
          <stop offset="50%" stopColor="#EF4444" />
          <stop offset="100%" stopColor="#991B1B" />
        </linearGradient>
        <linearGradient id="masterCenter" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor="#FEE2E2" />
          <stop offset="30%" stopColor="#F87171" />
          <stop offset="70%" stopColor="#DC2626" />
          <stop offset="100%" stopColor="#450A0A" />
        </linearGradient>
        <linearGradient id="masterCrown" x1="50%" y1="0%" x2="50%" y2="100%">
          <stop offset="0%" stopColor="#FFFFFF" />
          <stop offset="100%" stopColor="#FCA5A5" />
        </linearGradient>
        <linearGradient id="masterWingShine" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#FECACA" />
          <stop offset="50%" stopColor="#F87171" />
          <stop offset="100%" stopColor="#B91C1C" />
        </linearGradient>
        <filter id="masterShadow">
          <feDropShadow dx="0" dy="2" stdDeviation="3" floodColor="#7F1D1D" floodOpacity="0.6"/>
        </filter>
        <filter id="masterGlow" x="-40%" y="-40%" width="180%" height="180%">
          <feGaussianBlur stdDeviation="3" result="blur"/>
          <feMerge>
            <feMergeNode in="blur"/>
            <feMergeNode in="SourceGraphic"/>
          </feMerge>
        </filter>
      </defs>
      
      {/* Left outer wing */}
      <path
        d="M0 12L20 16L32 52L12 28L0 12Z"
        fill="url(#masterLeft)"
        filter="url(#masterShadow)"
      />
      
      {/* Right outer wing */}
      <path
        d="M64 12L44 16L32 52L52 28L64 12Z"
        fill="url(#masterRight)"
        filter="url(#masterShadow)"
      />
      
      {/* Left inner wing */}
      <path
        d="M8 16L22 18L32 44L16 26L8 16Z"
        fill="url(#masterCrown)"
        opacity="0.5"
      />
      
      {/* Right inner wing */}
      <path
        d="M56 16L42 18L32 44L48 26L56 16Z"
        fill="url(#masterCrown)"
        opacity="0.5"
      />
      
      {/* Center chevron */}
      <path
        d="M16 8L32 2L48 8L32 60L16 8Z"
        fill="url(#masterCenter)"
        filter="url(#masterGlow)"
      />
      
      {/* Crown spikes */}
      <path d="M24 8L26 4L28 10L24 8Z" fill="#FEE2E2"/>
      <path d="M32 6L32 2L32 6Z" fill="#FEE2E2"/>
      <path d="M40 8L38 4L36 10L40 8Z" fill="#FEE2E2"/>
      
      {/* Center highlight */}
      <path
        d="M32 2L48 8L44 12L32 8L20 12L16 8L32 2Z"
        fill="#FFFFFF"
        opacity="0.85"
      />
      
      {/* Wing decorations */}
      <path d="M0 12L6 8L12 14L0 12Z" fill="#FECACA" opacity="0.7"/>
      <path d="M64 12L58 8L52 14L64 12Z" fill="#FECACA" opacity="0.7"/>
      
      {/* Center gem */}
      <path
        d="M32 18L38 24L32 38L26 24L32 18Z"
        fill="#FEE2E2"
        opacity="0.7"
      />
      <path
        d="M32 18L38 24L32 24L26 24L32 18Z"
        fill="#FFFFFF"
        opacity="0.5"
      />
    </svg>
  );
};

export default MasterIcon;
