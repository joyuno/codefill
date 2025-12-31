import React from 'react';

interface TierIconProps {
  size?: number;
  className?: string;
}

export const SilverIcon: React.FC<TierIconProps> = ({ size = 24, className = '' }) => {
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
        <linearGradient id="silverLeft" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#D1D5DB" />
          <stop offset="50%" stopColor="#9CA3AF" />
          <stop offset="100%" stopColor="#6B7280" />
        </linearGradient>
        <linearGradient id="silverRight" x1="100%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor="#F3F4F6" />
          <stop offset="50%" stopColor="#D1D5DB" />
          <stop offset="100%" stopColor="#9CA3AF" />
        </linearGradient>
        <linearGradient id="silverCenter" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor="#E5E7EB" />
          <stop offset="100%" stopColor="#6B7280" />
        </linearGradient>
        <filter id="silverShadow">
          <feDropShadow dx="0" dy="2" stdDeviation="2" floodColor="#4B5563" floodOpacity="0.3"/>
        </filter>
      </defs>

      {/* Left wing */}
      <path
        d="M8 20L28 24L32 44L20 36L8 20Z"
        fill="url(#silverLeft)"
        filter="url(#silverShadow)"
      />

      {/* Right wing */}
      <path
        d="M56 20L36 24L32 44L44 36L56 20Z"
        fill="url(#silverRight)"
        filter="url(#silverShadow)"
      />

      {/* Center chevron */}
      <path
        d="M24 18L32 12L40 18L32 52L24 18Z"
        fill="url(#silverCenter)"
      />

      {/* Highlight */}
      <path
        d="M32 12L40 18L36 20L32 16L28 20L24 18L32 12Z"
        fill="#FFFFFF"
        opacity="0.6"
      />
    </svg>
  );
};

export default SilverIcon;
