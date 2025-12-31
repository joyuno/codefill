import React from 'react';

interface TierIconProps {
  size?: number;
  className?: string;
}

const DiamondIcon: React.FC<TierIconProps> = ({ size = 64, className = '' }) => {
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
        <linearGradient id="diaLeft" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#C4B5FD" />
          <stop offset="50%" stopColor="#8B5CF6" />
          <stop offset="100%" stopColor="#5B21B6" />
        </linearGradient>
        <linearGradient id="diaRight" x1="100%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor="#EDE9FE" />
          <stop offset="50%" stopColor="#A78BFA" />
          <stop offset="100%" stopColor="#7C3AED" />
        </linearGradient>
        <linearGradient id="diaCenter" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor="#DDD6FE" />
          <stop offset="50%" stopColor="#A78BFA" />
          <stop offset="100%" stopColor="#4C1D95" />
        </linearGradient>
        <linearGradient id="diaGem" x1="50%" y1="0%" x2="50%" y2="100%">
          <stop offset="0%" stopColor="#FFFFFF" />
          <stop offset="100%" stopColor="#C4B5FD" />
        </linearGradient>
        <filter id="diaShadow">
          <feDropShadow dx="0" dy="2" stdDeviation="3" floodColor="#5B21B6" floodOpacity="0.5"/>
        </filter>
        <filter id="diaGlow" x="-30%" y="-30%" width="160%" height="160%">
          <feGaussianBlur stdDeviation="3" result="blur"/>
          <feMerge>
            <feMergeNode in="blur"/>
            <feMergeNode in="SourceGraphic"/>
          </feMerge>
        </filter>
      </defs>
      
      {/* Left outer wing */}
      <path
        d="M2 14L22 18L32 50L14 30L2 14Z"
        fill="url(#diaLeft)"
        filter="url(#diaShadow)"
      />
      
      {/* Right outer wing */}
      <path
        d="M62 14L42 18L32 50L50 30L62 14Z"
        fill="url(#diaRight)"
        filter="url(#diaShadow)"
      />
      
      {/* Left inner wing */}
      <path
        d="M10 18L24 20L32 42L18 28L10 18Z"
        fill="url(#diaGem)"
        opacity="0.4"
      />
      
      {/* Right inner wing */}
      <path
        d="M54 18L40 20L32 42L46 28L54 18Z"
        fill="url(#diaGem)"
        opacity="0.4"
      />
      
      {/* Center chevron */}
      <path
        d="M18 10L32 4L46 10L32 58L18 10Z"
        fill="url(#diaCenter)"
        filter="url(#diaGlow)"
      />
      
      {/* Center gem facets */}
      <path
        d="M32 4L46 10L40 14L32 10L24 14L18 10L32 4Z"
        fill="#FFFFFF"
        opacity="0.8"
      />
      <path
        d="M32 20L38 24L32 40L26 24L32 20Z"
        fill="#EDE9FE"
        opacity="0.6"
      />
      
      {/* Wing tips sparkle */}
      <path d="M2 14L8 10L14 16L2 14Z" fill="#FFFFFF" opacity="0.5"/>
      <path d="M62 14L56 10L50 16L62 14Z" fill="#FFFFFF" opacity="0.5"/>
    </svg>
  );
};

export default DiamondIcon;
