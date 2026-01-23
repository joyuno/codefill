'use client';

/**
 * SeedHotbar - 픽셀 RPG 스타일 씨앗 핫바
 * 클래식 RPG 인벤토리 슬롯 디자인
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

// 픽셀 슬롯 컴포넌트
function PixelSlot({
  children,
  isSelected,
  isEmpty,
  onClick,
  shortcutKey,
  title,
}: {
  children?: React.ReactNode;
  isSelected?: boolean;
  isEmpty?: boolean;
  onClick?: () => void;
  shortcutKey?: number;
  title?: string;
}) {
  return (
    <motion.button
      onClick={onClick}
      disabled={isEmpty}
      whileHover={!isEmpty ? { y: -3, scale: 1.05 } : undefined}
      whileTap={!isEmpty ? { scale: 0.95 } : undefined}
      className={cn(
        'relative w-14 h-14 transition-all',
        isEmpty && 'cursor-default'
      )}
      title={title}
    >
      {/* 슬롯 외곽 */}
      <div
        className={cn(
          'absolute inset-0 rounded-sm transition-all',
          isSelected
            ? 'bg-[#2A5D2A]'
            : isEmpty
            ? 'bg-[#1A1209]'
            : 'bg-[#2D1B0E]'
        )}
        style={{
          boxShadow: isSelected
            ? 'inset 0 0 0 2px #4ADE4A, inset 0 0 8px #4ADE4A40, 0 0 12px #4ADE4A60'
            : isEmpty
            ? 'inset 0 0 0 2px #3D2E24, inset 2px 2px 4px #0A0705'
            : 'inset 0 0 0 2px #5C3D2E, inset 2px 2px 4px #0A0705',
        }}
      />

      {/* 내부 배경 */}
      <div
        className={cn(
          'absolute inset-[3px] rounded-sm',
          isSelected
            ? 'bg-gradient-to-b from-[#3D7A3D] to-[#2A5D2A]'
            : isEmpty
            ? 'bg-gradient-to-b from-[#2A1F14] to-[#1A1209]'
            : 'bg-gradient-to-b from-[#4A3628] to-[#2D1B0E]'
        )}
        style={{
          boxShadow: isSelected
            ? 'inset 1px 1px 0 #5AEE5A40'
            : 'inset 1px 1px 0 #FFFFFF10',
        }}
      />

      {/* 슬롯 하이라이트 */}
      {!isEmpty && (
        <div
          className="absolute top-[4px] left-[4px] right-[4px] h-[6px] rounded-sm opacity-30"
          style={{
            background: 'linear-gradient(to bottom, #FFFFFF40 0%, transparent 100%)',
          }}
        />
      )}

      {/* 단축키 표시 */}
      {shortcutKey && (
        <div
          className="absolute -top-1 -left-1 w-5 h-5 flex items-center justify-center z-20"
          style={{
            background: 'linear-gradient(135deg, #1A1209 0%, #2D1B0E 100%)',
            border: '1px solid #5C3D2E',
            borderRadius: '3px',
            fontSize: '10px',
            fontWeight: 'bold',
            color: '#C9A227',
            textShadow: '0 1px 2px #000',
          }}
        >
          {shortcutKey}
        </div>
      )}

      {/* 컨텐츠 */}
      <div className="relative z-10 h-full flex flex-col items-center justify-center">
        {children}
      </div>

      {/* 선택 시 반짝임 효과 */}
      {isSelected && (
        <>
          <motion.div
            className="absolute inset-0 pointer-events-none"
            initial={{ opacity: 0 }}
            animate={{ opacity: [0, 0.5, 0] }}
            transition={{ duration: 1.5, repeat: Infinity }}
            style={{
              background: 'radial-gradient(circle, #4ADE4A40 0%, transparent 70%)',
            }}
          />
          {/* 반짝이는 별 */}
          <Sparkle className="absolute top-1 right-1" delay={0} />
          <Sparkle className="absolute bottom-2 left-2" delay={0.5} />
        </>
      )}
    </motion.button>
  );
}

// 반짝이는 별 이펙트
function Sparkle({ className, delay = 0 }: { className?: string; delay?: number }) {
  return (
    <motion.div
      className={cn('w-2 h-2 pointer-events-none z-30', className)}
      initial={{ scale: 0, rotate: 0 }}
      animate={{
        scale: [0, 1, 0],
        rotate: [0, 180, 360],
        opacity: [0, 1, 0],
      }}
      transition={{
        duration: 1.5,
        repeat: Infinity,
        delay,
        ease: 'easeInOut',
      }}
    >
      <svg viewBox="0 0 24 24" fill="#FFD700" className="w-full h-full drop-shadow-[0_0_4px_#FFD700]">
        <path d="M12 0L14.5 9.5L24 12L14.5 14.5L12 24L9.5 14.5L0 12L9.5 9.5L12 0Z" />
      </svg>
    </motion.div>
  );
}

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
  const emptySlots = SLOTS_PER_PAGE - visibleItems.length;

  // 키보드 단축키
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
        return;
      }

      if (e.key >= '1' && e.key <= '9') {
        const index = parseInt(e.key) - 1;
        if (index < visibleItems.length) {
          const item = visibleItems[index];
          onSelectSeed(selectedSeed === item.code ? null : item.code);
        }
        return;
      }

      if (e.key === 'e' || e.key === 'E' || e.key === 'ㄷ') {
        onEnterPlacementMode();
        return;
      }

      if ((e.key === 'q' || e.key === 'Q' || e.key === 'ㅂ') && page > 0) {
        setPage(p => p - 1);
        return;
      }

      if ((e.key === 'r' || e.key === 'R' || e.key === 'ㄱ') && page < totalPages - 1) {
        setPage(p => p + 1);
        return;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [visibleItems, selectedSeed, onSelectSeed, onEnterPlacementMode, page, totalPages]);

  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 pointer-events-none pb-3">
      <div className="flex justify-center">
        {/* 메인 핫바 프레임 */}
        <motion.div
          initial={{ y: 100, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ type: 'spring', stiffness: 200, damping: 20 }}
          className="pointer-events-auto relative"
        >
          {/* 프레임 배경 */}
          <div
            className="absolute inset-0 rounded-lg"
            style={{
              background: 'linear-gradient(180deg, #3D2A1A 0%, #2D1B0E 100%)',
              border: '3px solid #5C3D2E',
              boxShadow: `
                inset 0 2px 0 #6B4A35,
                inset 0 -2px 0 #1A0F08,
                0 8px 24px rgba(0,0,0,0.6),
                0 0 0 1px #1A0F08
              `,
            }}
          />

          {/* 장식용 상단 라인 */}
          <div
            className="absolute top-0 left-4 right-4 h-[2px]"
            style={{
              background: 'linear-gradient(90deg, transparent 0%, #C9A227 50%, transparent 100%)',
            }}
          />

          {/* 컨텐츠 */}
          <div className="relative z-10 flex items-center gap-2 px-3 py-2">
            {/* 이전 페이지 */}
            {totalPages > 1 && (
              <motion.button
                onClick={() => setPage(p => Math.max(0, p - 1))}
                disabled={page === 0}
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                className={cn(
                  'w-8 h-8 rounded flex items-center justify-center transition-all',
                  page === 0
                    ? 'bg-[#1A1209] text-[#4A3628] cursor-not-allowed'
                    : 'bg-[#2D1B0E] text-[#C9A227] hover:bg-[#3D2A1A] border border-[#5C3D2E]'
                )}
              >
                <ChevronLeft className="w-5 h-5" />
              </motion.button>
            )}

            {/* 씨앗 슬롯 */}
            <div className="flex items-center gap-1">
              <AnimatePresence mode="popLayout">
                {visibleItems.map((item, index) => {
                  const isSelected = selectedSeed === item.code;
                  return (
                    <motion.div
                      key={item.code}
                      layout
                      initial={{ opacity: 0, scale: 0.8, y: 20 }}
                      animate={{ opacity: 1, scale: 1, y: 0 }}
                      exit={{ opacity: 0, scale: 0.8 }}
                      transition={{ delay: index * 0.03 }}
                    >
                      <PixelSlot
                        isSelected={isSelected}
                        onClick={() => onSelectSeed(isSelected ? null : item.code)}
                        shortcutKey={index + 1}
                        title={`${item.name} (${item.quantity}개)`}
                      >
                        <img
                          src={item.icon}
                          alt={item.name}
                          className="w-8 h-8 object-contain drop-shadow-[0_2px_2px_rgba(0,0,0,0.5)]"
                          style={{ imageRendering: 'pixelated' }}
                        />
                        <span
                          className="text-[10px] font-bold mt-0.5"
                          style={{
                            color: isSelected ? '#90EE90' : '#C9A227',
                            textShadow: '0 1px 2px #000',
                          }}
                        >
                          {item.quantity}
                        </span>
                      </PixelSlot>
                    </motion.div>
                  );
                })}

                {/* 빈 슬롯 */}
                {Array.from({ length: emptySlots }).map((_, i) => (
                  <motion.div
                    key={`empty-${i}`}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: (visibleItems.length + i) * 0.03 }}
                  >
                    <PixelSlot isEmpty shortcutKey={visibleItems.length + i + 1} />
                  </motion.div>
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
                  'w-8 h-8 rounded flex items-center justify-center transition-all',
                  page >= totalPages - 1
                    ? 'bg-[#1A1209] text-[#4A3628] cursor-not-allowed'
                    : 'bg-[#2D1B0E] text-[#C9A227] hover:bg-[#3D2A1A] border border-[#5C3D2E]'
                )}
              >
                <ChevronRight className="w-5 h-5" />
              </motion.button>
            )}

            {/* 페이지 표시 */}
            {totalPages > 1 && (
              <span
                className="text-xs font-bold px-2"
                style={{ color: '#8B7355', textShadow: '0 1px 2px #000' }}
              >
                {page + 1}/{totalPages}
              </span>
            )}

            {/* 구분선 */}
            <div
              className="w-[2px] h-12 mx-1"
              style={{
                background: 'linear-gradient(180deg, transparent 0%, #5C3D2E 20%, #5C3D2E 80%, transparent 100%)',
              }}
            />

            {/* 배치 모드 버튼 */}
            <motion.button
              onClick={onEnterPlacementMode}
              whileHover={{ scale: 1.05, y: -2 }}
              whileTap={{ scale: 0.95 }}
              className="relative flex items-center gap-2 px-4 py-2.5 rounded"
              style={{
                background: 'linear-gradient(180deg, #6B3FA0 0%, #4A2C6A 100%)',
                border: '2px solid #9B6DD0',
                boxShadow: `
                  inset 0 1px 0 #8B5DC0,
                  inset 0 -1px 0 #3A1C5A,
                  0 4px 8px rgba(0,0,0,0.4)
                `,
              }}
            >
              <Hammer className="w-4 h-4 text-purple-200" />
              <span className="text-sm font-bold text-purple-100">배치</span>
              <kbd
                className="px-1.5 py-0.5 rounded text-xs font-bold"
                style={{
                  background: '#3A1C5A',
                  color: '#C9A0FF',
                  border: '1px solid #6B3FA0',
                }}
              >
                E
              </kbd>
            </motion.button>
          </div>

          {/* 하단 장식 */}
          <div className="absolute -bottom-1 left-1/2 -translate-x-1/2 flex gap-1">
            {[...Array(3)].map((_, i) => (
              <div
                key={i}
                className="w-2 h-2 rotate-45"
                style={{
                  background: '#5C3D2E',
                  border: '1px solid #3D2A1A',
                }}
              />
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  );
}

export default SeedHotbar;
