import React from 'react';

interface TierIconProps {
  size?: number;
  className?: string;
}

const GoldIcon: React.FC<TierIconProps> = ({ size = 64, className = '' }) => {
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
        <linearGradient id="goldLeft" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#FCD34D" />
          <stop offset="50%" stopColor="#F59E0B" />
          <stop offset="100%" stopColor="#B45309" />
        </linearGradient>
        <linearGradient id="goldRight" x1="100%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor="#FEF3C7" />
          <stop offset="50%" stopColor="#FCD34D" />
          <stop offset="100%" stopColor="#D97706" />
        </linearGradient>
        <linearGradient id="goldCenter" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor="#FDE68A" />
          <stop offset="50%" stopColor="#FBBF24" />
          <stop offset="100%" stopColor="#92400E" />
        </linearGradient>
        <filter id="goldShadow">
          <feDropShadow dx="0" dy="2" stdDeviation="2" floodColor="#92400E" floodOpacity="0.4"/>
        </filter>
      </defs>
      
      {/* Left wing */}
      <path
        d="M6 18L26 22L32 46L18 34L6 18Z"
        fill="url(#goldLeft)"
        filter="url(#goldShadow)"
      />
      
      {/* Right wing */}
      <path
        d="M58 18L38 22L32 46L46 34L58 18Z"
        fill="url(#goldRight)"
        filter="url(#goldShadow)"
      />
      
      {/* Center chevron */}
      <path
        d="M22 14L32 8L42 14L32 54L22 14Z"
        fill="url(#goldCenter)"
      />
      
      {/* Wing tips */}
      <path d="M6 18L12 16L18 22L6 18Z" fill="#FEF3C7" opacity="0.7"/>
      <path d="M58 18L52 16L46 22L58 18Z" fill="#FEF3C7" opacity="0.7"/>
      
      {/* Center highlight */}
      <path
        d="M32 8L42 14L38 16L32 12L26 16L22 14L32 8Z"
        fill="#FFFFFF"
        opacity="0.7"
      />
    </svg>
  );
};

export default GoldIcon;
