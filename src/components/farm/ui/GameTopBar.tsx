'use client';

/**
 * GameTopBar - 상단 UI 바
 * 스타듀밸리 스타일 미니멀 HUD
 */

import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import {
  ChevronLeft,
  Coins,
  Menu,
  Store,
  Expand,
  Settings,
  X,
} from 'lucide-react';

interface GameTopBarProps {
  gold: number;
  onOpenShop: () => void;
  onOpenExpand: () => void;
}

export function GameTopBar({ gold, onOpenShop, onOpenExpand }: GameTopBarProps) {
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  // 외부 클릭 시 메뉴 닫기
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
    <div className="absolute top-0 left-0 right-0 z-40 p-4 pointer-events-none">
      <div className="max-w-4xl mx-auto flex items-center justify-between">
        {/* 뒤로가기 */}
        <Link href="/" className="pointer-events-auto">
          <Button
            variant="outline"
            size="sm"
            className="bg-amber-100 hover:bg-amber-200 border-4 border-amber-700 shadow-[3px_3px_0_0_#78350f] text-amber-900 font-bold"
          >
            <ChevronLeft className="w-4 h-4 mr-1" />
            뒤로
          </Button>
        </Link>

        {/* 우측: 골드 + 메뉴 */}
        <div className="flex items-center gap-3 pointer-events-auto" ref={menuRef}>
          {/* 골드 표시 */}
          <div
            className="flex items-center gap-2 px-4 py-2 rounded-xl"
            style={{
              background: 'linear-gradient(to bottom, #5D4037 0%, #4E342E 100%)',
              border: '4px solid #3E2723',
              boxShadow: '0 4px 8px rgba(0,0,0,0.3)',
            }}
          >
            <Coins className="w-5 h-5 text-yellow-400" />
            <span className="text-amber-200 font-bold text-lg">
              {gold.toLocaleString()}G
            </span>
          </div>

          {/* 메뉴 버튼 */}
          <div className="relative">
            <Button
              onClick={() => setMenuOpen(!menuOpen)}
              className="bg-amber-600 hover:bg-amber-500 border-4 border-amber-800 shadow-[3px_3px_0_0_#78350f] text-white font-bold w-12 h-12 p-0"
            >
              {menuOpen ? (
                <X className="w-5 h-5" />
              ) : (
                <Menu className="w-5 h-5" />
              )}
            </Button>

            {/* 드롭다운 메뉴 */}
            <AnimatePresence>
              {menuOpen && (
                <motion.div
                  initial={{ opacity: 0, y: -10, scale: 0.95 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: -10, scale: 0.95 }}
                  transition={{ duration: 0.15 }}
                  className="absolute right-0 top-full mt-2 w-48 z-50"
                >
                  <div
                    className="rounded-xl overflow-hidden"
                    style={{
                      background: 'linear-gradient(to bottom, #5D4037 0%, #4E342E 100%)',
                      border: '4px solid #3E2723',
                      boxShadow: '0 8px 24px rgba(0,0,0,0.4)',
                    }}
                  >
                    {/* 상점 */}
                    <button
                      onClick={() => {
                        onOpenShop();
                        setMenuOpen(false);
                      }}
                      className="w-full flex items-center gap-3 px-4 py-3 text-left text-amber-200 hover:bg-amber-900/50 transition-colors"
                    >
                      <Store className="w-5 h-5 text-blue-400" />
                      <span className="font-bold">상점</span>
                    </button>

                    {/* 농장 확장 */}
                    <button
                      onClick={() => {
                        onOpenExpand();
                        setMenuOpen(false);
                      }}
                      className="w-full flex items-center gap-3 px-4 py-3 text-left text-amber-200 hover:bg-amber-900/50 transition-colors border-t border-amber-900/30"
                    >
                      <Expand className="w-5 h-5 text-green-400" />
                      <span className="font-bold">농장 확장</span>
                    </button>
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
