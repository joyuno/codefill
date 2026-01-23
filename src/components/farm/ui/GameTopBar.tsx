'use client';

/**
 * GameTopBar - 픽셀 RPG 스타일 상단 UI 바
 * 장식 프레임과 골드 표시
 */

import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Link from 'next/link';
import {
  ChevronLeft,
  Coins,
  Menu,
  Store,
  Expand,
  Map,
  X,
} from 'lucide-react';

interface GameTopBarProps {
  gold: number;
  onOpenShop: () => void;
  onOpenExpand: () => void;
  onOpenMapExpand?: () => void;
}

// 골드 표시 컴포넌트 (동전 애니메이션 포함)
function GoldDisplay({ amount }: { amount: number }) {
  const [displayAmount, setDisplayAmount] = useState(amount);
  const [isAnimating, setIsAnimating] = useState(false);
  const prevAmount = useRef(amount);

  useEffect(() => {
    if (amount !== prevAmount.current) {
      setIsAnimating(true);
      const diff = amount - prevAmount.current;
      const steps = 20;
      const stepValue = diff / steps;
      let current = prevAmount.current;
      let step = 0;

      const interval = setInterval(() => {
        step++;
        current += stepValue;
        setDisplayAmount(Math.round(current));
        if (step >= steps) {
          clearInterval(interval);
          setDisplayAmount(amount);
          setIsAnimating(false);
        }
      }, 20);

      prevAmount.current = amount;
      return () => clearInterval(interval);
    }
  }, [amount]);

  return (
    <motion.div
      className="relative flex items-center gap-2"
      animate={isAnimating ? { scale: [1, 1.1, 1] } : {}}
      transition={{ duration: 0.3 }}
    >
      {/* 동전 아이콘 */}
      <motion.div
        className="relative"
        animate={isAnimating ? { rotate: [0, 360] } : {}}
        transition={{ duration: 0.5 }}
      >
        <div
          className="w-7 h-7 rounded-full flex items-center justify-center"
          style={{
            background: 'linear-gradient(135deg, #FFD700 0%, #FFA500 50%, #FF8C00 100%)',
            boxShadow: `
              inset -2px -2px 4px rgba(0,0,0,0.3),
              inset 2px 2px 4px rgba(255,255,255,0.4),
              0 2px 4px rgba(0,0,0,0.3)
            `,
            border: '2px solid #B8860B',
          }}
        >
          <span className="text-[10px] font-black text-amber-900">G</span>
        </div>
        {/* 반짝임 */}
        <div
          className="absolute top-0.5 left-0.5 w-2 h-2 rounded-full"
          style={{
            background: 'radial-gradient(circle, rgba(255,255,255,0.8) 0%, transparent 70%)',
          }}
        />
      </motion.div>

      {/* 금액 */}
      <span
        className="text-lg font-black tabular-nums"
        style={{
          color: '#FFD700',
          textShadow: '0 2px 4px rgba(0,0,0,0.8), 0 0 10px rgba(255,215,0,0.3)',
        }}
      >
        {displayAmount.toLocaleString()}
      </span>

      {/* 획득 시 파티클 */}
      <AnimatePresence>
        {isAnimating && (
          <>
            {[...Array(5)].map((_, i) => (
              <motion.div
                key={i}
                className="absolute w-1.5 h-1.5 rounded-full"
                style={{ background: '#FFD700' }}
                initial={{
                  x: 0,
                  y: 0,
                  opacity: 1,
                  scale: 1,
                }}
                animate={{
                  x: (Math.random() - 0.5) * 40,
                  y: -20 - Math.random() * 20,
                  opacity: 0,
                  scale: 0,
                }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.5, delay: i * 0.05 }}
              />
            ))}
          </>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

// 메뉴 아이템 컴포넌트
function MenuItem({
  icon,
  label,
  onClick,
  color,
}: {
  icon: React.ReactNode;
  label: string;
  onClick: () => void;
  color: string;
}) {
  return (
    <motion.button
      onClick={onClick}
      whileHover={{ x: 4, backgroundColor: 'rgba(92, 61, 46, 0.8)' }}
      whileTap={{ scale: 0.98 }}
      className="w-full flex items-center gap-3 px-4 py-3 text-left transition-colors"
    >
      <span className={color}>{icon}</span>
      <span
        className="font-bold"
        style={{ color: '#E8D5B7', textShadow: '0 1px 2px #000' }}
      >
        {label}
      </span>
    </motion.button>
  );
}

export function GameTopBar({ gold, onOpenShop, onOpenExpand, onOpenMapExpand }: GameTopBarProps) {
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setMenuOpen(false);
      }
    }

    if (menuOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [menuOpen]);

  return (
    <div className="absolute top-0 left-0 right-0 z-40 p-3 pointer-events-none">
      <div className="flex items-start justify-between">
        {/* 뒤로가기 버튼 */}
        <Link href="/" className="pointer-events-auto">
          <motion.div
            whileHover={{ scale: 1.05, x: -2 }}
            whileTap={{ scale: 0.95 }}
            className="relative"
          >
            {/* 버튼 배경 */}
            <div
              className="px-4 py-2 rounded-lg flex items-center gap-1.5"
              style={{
                background: 'linear-gradient(180deg, #4A3628 0%, #2D1B0E 100%)',
                border: '2px solid #5C3D2E',
                boxShadow: `
                  inset 0 1px 0 #6B4A35,
                  inset 0 -1px 0 #1A0F08,
                  0 4px 8px rgba(0,0,0,0.4)
                `,
              }}
            >
              <ChevronLeft className="w-4 h-4 text-amber-400" />
              <span
                className="text-sm font-bold"
                style={{ color: '#E8D5B7', textShadow: '0 1px 2px #000' }}
              >
                나가기
              </span>
            </div>
          </motion.div>
        </Link>

        {/* 우측: 골드 + 메뉴 */}
        <div className="flex items-center gap-2 pointer-events-auto" ref={menuRef}>
          {/* 골드 표시 프레임 */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="relative"
          >
            {/* 프레임 */}
            <div
              className="px-4 py-2 rounded-lg"
              style={{
                background: 'linear-gradient(180deg, #3D2A1A 0%, #2D1B0E 100%)',
                border: '2px solid #5C3D2E',
                boxShadow: `
                  inset 0 1px 0 #4A3628,
                  inset 0 -1px 0 #1A0F08,
                  0 4px 12px rgba(0,0,0,0.5)
                `,
              }}
            >
              <GoldDisplay amount={gold} />
            </div>

            {/* 장식 별 */}
            <div
              className="absolute -top-1 -right-1 w-3 h-3"
              style={{
                background: '#C9A227',
                clipPath: 'polygon(50% 0%, 61% 35%, 98% 35%, 68% 57%, 79% 91%, 50% 70%, 21% 91%, 32% 57%, 2% 35%, 39% 35%)',
              }}
            />
          </motion.div>

          {/* 메뉴 버튼 */}
          <div className="relative">
            <motion.button
              onClick={() => setMenuOpen(!menuOpen)}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="w-11 h-11 rounded-lg flex items-center justify-center"
              style={{
                background: menuOpen
                  ? 'linear-gradient(180deg, #6B4A35 0%, #4A3628 100%)'
                  : 'linear-gradient(180deg, #5C3D2E 0%, #3D2A1A 100%)',
                border: '2px solid #6B4A35',
                boxShadow: menuOpen
                  ? 'inset 0 2px 4px rgba(0,0,0,0.4)'
                  : `inset 0 1px 0 #7B5A45, 0 4px 8px rgba(0,0,0,0.4)`,
              }}
            >
              <AnimatePresence mode="wait">
                {menuOpen ? (
                  <motion.div
                    key="close"
                    initial={{ rotate: -90, opacity: 0 }}
                    animate={{ rotate: 0, opacity: 1 }}
                    exit={{ rotate: 90, opacity: 0 }}
                    transition={{ duration: 0.15 }}
                  >
                    <X className="w-5 h-5 text-amber-300" />
                  </motion.div>
                ) : (
                  <motion.div
                    key="menu"
                    initial={{ rotate: 90, opacity: 0 }}
                    animate={{ rotate: 0, opacity: 1 }}
                    exit={{ rotate: -90, opacity: 0 }}
                    transition={{ duration: 0.15 }}
                  >
                    <Menu className="w-5 h-5 text-amber-300" />
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.button>

            {/* 드롭다운 메뉴 */}
            <AnimatePresence>
              {menuOpen && (
                <motion.div
                  initial={{ opacity: 0, y: -10, scale: 0.95 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: -10, scale: 0.95 }}
                  transition={{ type: 'spring', stiffness: 300, damping: 25 }}
                  className="absolute right-0 top-full mt-2 w-48 z-50 overflow-hidden rounded-lg"
                  style={{
                    background: 'linear-gradient(180deg, #3D2A1A 0%, #2D1B0E 100%)',
                    border: '3px solid #5C3D2E',
                    boxShadow: `
                      inset 0 1px 0 #4A3628,
                      0 8px 24px rgba(0,0,0,0.6)
                    `,
                  }}
                >
                  {/* 상단 장식 라인 */}
                  <div
                    className="h-[2px] mx-2"
                    style={{
                      background: 'linear-gradient(90deg, transparent 0%, #C9A227 50%, transparent 100%)',
                    }}
                  />

                  <div className="py-1">
                    <MenuItem
                      icon={<Store className="w-5 h-5" />}
                      label="상점"
                      color="text-blue-400"
                      onClick={() => {
                        onOpenShop();
                        setMenuOpen(false);
                      }}
                    />

                    <div className="h-px mx-3 bg-[#5C3D2E]/50" />

                    <MenuItem
                      icon={<Expand className="w-5 h-5" />}
                      label="밭 확장"
                      color="text-green-400"
                      onClick={() => {
                        onOpenExpand();
                        setMenuOpen(false);
                      }}
                    />

                    {onOpenMapExpand && (
                      <>
                        <div className="h-px mx-3 bg-[#5C3D2E]/50" />
                        <MenuItem
                          icon={<Map className="w-5 h-5" />}
                          label="맵 확장"
                          color="text-cyan-400"
                          onClick={() => {
                            onOpenMapExpand();
                            setMenuOpen(false);
                          }}
                        />
                      </>
                    )}
                  </div>

                  {/* 하단 장식 */}
                  <div className="flex justify-center pb-1">
                    <div className="flex gap-1">
                      {[...Array(3)].map((_, i) => (
                        <div
                          key={i}
                          className="w-1.5 h-1.5 rotate-45"
                          style={{ background: '#5C3D2E' }}
                        />
                      ))}
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>
    </div>
  );
}

export default GameTopBar;
