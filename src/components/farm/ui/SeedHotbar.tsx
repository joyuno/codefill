'use client';

/**
 * SeedHotbar - 씨앗 전용 핫바
 * - 1-9 숫자 단축키로 씨앗 선택
 * - 9개씩 페이지네이션
 * - E키로 배치 모드 진입 버튼
 */

import { useState, useEffect, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronLeft, ChevronRight, Hammer } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { InventoryItem } from '@/lib/api/farm';
import { CROP_INFO, type CropVariety } from './Hotbar';

interface SeedItem {
  code: string;
  cropCode: string;
  name: string;
  icon: string;
  quantity: number;
}

interface SeedHotbarProps {
  inventory: InventoryItem[];
  selectedSeed: string | null;
  onSelectSeed: (seedCode: string | null) => void;
  onEnterPlacementMode: () => void;
}

const SLOTS_PER_PAGE = 9;

export function SeedHotbar({
  inventory,
  selectedSeed,
  onSelectSeed,
  onEnterPlacementMode,
}: SeedHotbarProps) {
  const [page, setPage] = useState(0);

  // 보유한 씨앗만 필터링
  const seedItems = useMemo<SeedItem[]>(() => {
    return Object.entries(CROP_INFO)
      .map(([cropCode, info]) => {
        const seedCode = `seed_${cropCode}`;
        const item = inventory.find(i => i.itemCode === seedCode);
        const quantity = item?.quantity || 0;
        return {
          code: seedCode,
          cropCode,
          name: info.name,
          icon: info.icon,
          quantity,
        };
      })
      .filter(item => item.quantity > 0);
  }, [inventory]);

  // 페이지네이션
  const totalPages = Math.max(1, Math.ceil(seedItems.length / SLOTS_PER_PAGE));
  const startIndex = page * SLOTS_PER_PAGE;
  const visibleItems = seedItems.slice(startIndex, startIndex + SLOTS_PER_PAGE);

  // 빈 슬롯 채우기
  const emptySlots = SLOTS_PER_PAGE - visibleItems.length;

  // 키보드 단축키 (1-9, E, 좌우 화살표)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // 입력 필드에서는 무시
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
        return;
      }

      // 1-9: 씨앗 선택
      if (e.key >= '1' && e.key <= '9') {
        const index = parseInt(e.key) - 1;
        if (index < visibleItems.length) {
          const item = visibleItems[index];
          onSelectSeed(selectedSeed === item.code ? null : item.code);
        }
        return;
      }

      // E: 배치 모드 진입
      if (e.key === 'e' || e.key === 'E' || e.key === 'ㄷ') {
        onEnterPlacementMode();
        return;
      }

      // Q: 이전 페이지
      if ((e.key === 'q' || e.key === 'Q' || e.key === 'ㅂ') && page > 0) {
        setPage(p => p - 1);
        return;
      }

      // R: 다음 페이지 (E가 배치모드라서 R 사용)
      if ((e.key === 'r' || e.key === 'R' || e.key === 'ㄱ') && page < totalPages - 1) {
        setPage(p => p + 1);
        return;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [visibleItems, selectedSeed, onSelectSeed, onEnterPlacementMode, page, totalPages]);

  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 pointer-events-none pb-4">
      <div className="flex justify-center">
        <div
          className="pointer-events-auto flex items-center gap-2 px-3 py-2 rounded-xl"
          style={{
            background: 'linear-gradient(to bottom, #5D4037 0%, #4E342E 100%)',
            border: '3px solid #3E2723',
            boxShadow: '0 4px 12px rgba(0,0,0,0.4)',
          }}
        >
          {/* 이전 페이지 */}
          {totalPages > 1 && (
            <motion.button
              onClick={() => setPage(p => Math.max(0, p - 1))}
              disabled={page === 0}
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              className={cn(
                'w-8 h-8 rounded-lg flex items-center justify-center text-xs',
                page === 0
                  ? 'bg-amber-900/30 text-amber-700 cursor-not-allowed'
                  : 'bg-amber-800/50 text-amber-200 hover:bg-amber-700/50'
              )}
              title="이전 (Q)"
            >
              <ChevronLeft className="w-4 h-4" />
            </motion.button>
          )}

          {/* 씨앗 슬롯 */}
          <div className="flex items-center gap-1">
            <AnimatePresence mode="popLayout">
              {visibleItems.map((item, index) => {
                const isSelected = selectedSeed === item.code;
                const shortcutKey = index + 1;
                return (
                  <motion.button
                    key={item.code}
                    layout
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.8 }}
                    onClick={() => onSelectSeed(isSelected ? null : item.code)}
                    whileHover={{ y: -4 }}
                    whileTap={{ scale: 0.95 }}
                    className={cn(
                      'relative w-12 h-12 rounded-lg flex flex-col items-center justify-center transition-all',
                      isSelected
                        ? 'bg-green-500 border-2 border-green-300 shadow-lg shadow-green-500/30'
                        : 'bg-amber-900/50 border-2 border-amber-700 hover:bg-amber-800/50'
                    )}
                    title={`${item.name} (${item.quantity}개) - ${shortcutKey}키`}
                  >
                    {/* 단축키 표시 */}
                    <span className="absolute -top-1 -left-1 w-4 h-4 bg-gray-800 rounded text-[10px] font-bold text-white flex items-center justify-center">
                      {shortcutKey}
                    </span>

                    <img
                      src={item.icon}
                      alt={item.name}
                      className="w-7 h-7 object-contain"
                      style={{ imageRendering: 'pixelated' }}
                    />
                    <span className="text-[10px] font-bold text-white">
                      {item.quantity}
                    </span>
                  </motion.button>
                );
              })}

              {/* 빈 슬롯 */}
              {Array.from({ length: emptySlots }).map((_, i) => (
                <div
                  key={`empty-${i}`}
                  className="w-12 h-12 rounded-lg bg-amber-900/30 border-2 border-amber-800/50"
                />
              ))}
            </AnimatePresence>
          </div>

          {/* 다음 페이지 */}
          {totalPages > 1 && (
            <motion.button
              onClick={() => setPage(p => Math.min(totalPages - 1, p + 1))}
              disabled={page >= totalPages - 1}
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              className={cn(
                'w-8 h-8 rounded-lg flex items-center justify-center text-xs',
                page >= totalPages - 1
                  ? 'bg-amber-900/30 text-amber-700 cursor-not-allowed'
                  : 'bg-amber-800/50 text-amber-200 hover:bg-amber-700/50'
              )}
              title="다음 (R)"
            >
              <ChevronRight className="w-4 h-4" />
            </motion.button>
          )}

          {/* 페이지 표시 */}
          {totalPages > 1 && (
            <span className="text-amber-400 text-xs font-bold px-1">
              {page + 1}/{totalPages}
            </span>
          )}

          {/* 구분선 */}
          <div className="w-px h-10 bg-amber-700 mx-1" />

          {/* 배치 모드 버튼 */}
          <motion.button
            onClick={onEnterPlacementMode}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="flex items-center gap-2 px-3 py-2 rounded-lg bg-purple-600/80 hover:bg-purple-500/80 border-2 border-purple-400/50 text-white"
            title="배치 모드 (E)"
          >
            <Hammer className="w-4 h-4" />
            <span className="text-sm font-bold">배치</span>
            <kbd className="px-1.5 py-0.5 bg-purple-800/50 rounded text-xs">E</kbd>
          </motion.button>
        </div>
      </div>
    </div>
  );
}

export default SeedHotbar;
