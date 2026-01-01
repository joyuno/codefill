import React from 'react';

interface TierIconProps {
  size?: number;
  className?: string;
}

const PlatinumIcon: React.FC<TierIconProps> = ({ size = 64, className = '' }) => {
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
        <linearGradient id="platLeft" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#67E8F9" />
          <stop offset="50%" stopColor="#22D3EE" />
          <stop offset="100%" stopColor="#0891B2" />
        </linearGradient>
        <linearGradient id="platRight" x1="100%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor="#ECFEFF" />
          <stop offset="50%" stopColor="#67E8F9" />
          <stop offset="100%" stopColor="#06B6D4" />
        </linearGradient>
        <linearGradient id="platCenter" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor="#CFFAFE" />
          <stop offset="50%" stopColor="#22D3EE" />
          <stop offset="100%" stopColor="#0E7490" />
        </linearGradient>
        <linearGradient id="platCrystal" x1="50%" y1="0%" x2="50%" y2="100%">
          <stop offset="0%" stopColor="#FFFFFF" />
          <stop offset="100%" stopColor="#A5F3FC" />
        </linearGradient>
        <filter id="platShadow">
          <feDropShadow dx="0" dy="2" stdDeviation="3" floodColor="#0E7490" floodOpacity="0.4"/>
        </filter>
        <filter id="platGlow">
          <feGaussianBlur stdDeviation="2" result="blur"/>
          <feMerge>
            <feMergeNode in="blur"/>
            <feMergeNode in="SourceGraphic"/>
          </feMerge>
        </filter>
      </defs>
      
      {/* Left wing */}
      <path
        d="M4 16L24 20L32 48L16 32L4 16Z"
        fill="url(#platLeft)"
        filter="url(#platShadow)"
      />
      
      {/* Right wing */}
      <path
        d="M60 16L40 20L32 48L48 32L60 16Z"
        fill="url(#platRight)"
        filter="url(#platShadow)"
      />
      
      {/* Left crystal facet */}
      <path
        d="M4 16L12 12L20 18L16 32L4 16Z"
        fill="url(#platCrystal)"
        opacity="0.5"
      />
      
      {/* Right crystal facet */}
      <path
        d="M60 16L52 12L44 18L48 32L60 16Z"
        fill="url(#platCrystal)"
        opacity="0.5"
      />
      
      {/* Center chevron */}
      <path
        d="M20 12L32 6L44 12L32 56L20 12Z"
        fill="url(#platCenter)"
        filter="url(#platGlow)"
      />
      
      {/* Center highlight */}
      <path
        d="M32 6L44 12L40 14L32 10L24 14L20 12L32 6Z"
        fill="#FFFFFF"
        opacity="0.8"
      />
      
      {/* Crystal shards */}
      <path d="M12 12L16 10L20 14L12 12Z" fill="#FFFFFF" opacity="0.6"/>
      <path d="M52 12L48 10L44 14L52 12Z" fill="#FFFFFF" opacity="0.6"/>
    </svg>
  );
};

export default PlatinumIcon;
