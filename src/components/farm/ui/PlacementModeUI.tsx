'use client';

/**
 * PlacementModeUI - 픽셀 RPG 스타일 배치 모드 UI
 * - 상단: 나가기, 제목, 저장/취소
 * - 하단: 배치 아이템 핫바 (1-9 단축키)
 */

import { useState, useEffect, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronLeft, ChevronRight, X, Save, Undo2, Hammer, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { UnifiedShopItem } from '@/lib/api/farm';

interface PlacementItem {
  code: string;
  name: string;
  emoji: string;
  quantity: number;
}

interface PlacementModeUIProps {
  items: UnifiedShopItem[];
  selectedItem: string | null;
  onSelectItem: (itemCode: string | null) => void;
  onExit: () => void;
  onSave: () => void;
  onCancel: () => void;
  isSaving: boolean;
  hasChanges: boolean;
}

// 배치 아이템 이모지 매핑
const ITEM_EMOJI: Record<string, string> = {
  house: '🏠',
  chicken_coop: '🐔',
  water_well: '🪣',
  well: '🪣',
  barn: '🏚️',
  scarecrow: '🎃',
  farm_plot: '🌱',
  farmer_house_1: '🏡',
  farmer_house_2: '🏘️',
  barn_small: '🏚️',
  stable: '🐴',
  silos: '🗼',
  doghouse: '🐕',
  stone_oven: '🔥',
  cheese_machine: '🧀',
  diy_crafting_table: '🔨',
  tailor_table: '🧵',
  woodwork_table: '🪓',
  market_stand_blue: '🛒',
  market_stand_green: '🛍️',
  market_stand_yellow: '🏪',
  market_stand_pink: '🎪',
  tree_oak: '🌳',
  tree_pine: '🌲',
  tree_cherry: '🌸',
  tree_apple: '🍎',
  tree_maple: '🍁',
  flower_red: '🌹',
  flower_yellow: '🌻',
  flower_blue: '💐',
  grass_patch: '🌿',
  grass_tuft: '🌿',
  hay_pile: '🌾',
  rock_small: '🪨',
  rock_large: '⛰️',
  pond_small: '💧',
  fence_wood: '🪵',
  fence_stone: '🧱',
  fence_iron: '⛓️',
};

const SLOTS_PER_PAGE = 9;

// 픽셀 스타일 버튼 컴포넌트
function PixelButton({
  children,
  onClick,
  disabled,
  variant = 'default',
  className,
}: {
  children: React.ReactNode;
  onClick?: () => void;
  disabled?: boolean;
  variant?: 'default' | 'success' | 'danger' | 'ghost';
  className?: string;
}) {
  const variants = {
    default: {
      bg: 'linear-gradient(180deg, #5C3D2E 0%, #3D2A1A 100%)',
      border: '#6B4A35',
      hover: 'linear-gradient(180deg, #6B4A35 0%, #4A3628 100%)',
    },
    success: {
      bg: 'linear-gradient(180deg, #2A5D2A 0%, #1A3D1A 100%)',
      border: '#4ADE4A',
      hover: 'linear-gradient(180deg, #3D7A3D 0%, #2A5D2A 100%)',
    },
    danger: {
      bg: 'linear-gradient(180deg, #5D2A2A 0%, #3D1A1A 100%)',
      border: '#DE4A4A',
      hover: 'linear-gradient(180deg, #7A3D3D 0%, #5D2A2A 100%)',
    },
    ghost: {
      bg: 'rgba(0,0,0,0.3)',
      border: '#5C3D2E',
      hover: 'rgba(0,0,0,0.4)',
    },
  };

  const v = variants[variant];

  return (
    <motion.button
      onClick={onClick}
      disabled={disabled}
      whileHover={!disabled ? { scale: 1.02, y: -1 } : undefined}
      whileTap={!disabled ? { scale: 0.98 } : undefined}
      className={cn(
        'relative px-4 py-2 rounded-lg transition-all',
        disabled && 'opacity-50 cursor-not-allowed',
        className
      )}
      style={{
        background: v.bg,
        border: `2px solid ${v.border}`,
        boxShadow: `
          inset 0 1px 0 rgba(255,255,255,0.1),
          inset 0 -1px 0 rgba(0,0,0,0.2),
          0 4px 8px rgba(0,0,0,0.3)
        `,
      }}
    >
      {children}
    </motion.button>
  );
}

// 픽셀 슬롯 컴포넌트
function PlacementSlot({
  item,
  isSelected,
  shortcutKey,
  onClick,
  isEmpty,
}: {
  item?: PlacementItem;
  isSelected?: boolean;
  shortcutKey: number;
  onClick?: () => void;
  isEmpty?: boolean;
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
      title={item ? `${item.name} (${item.quantity}개)` : undefined}
    >
      {/* 슬롯 외곽 */}
      <div
        className={cn(
          'absolute inset-0 rounded-sm transition-all',
          isSelected
            ? 'bg-[#4A2C6A]'
            : isEmpty
            ? 'bg-[#1A1209]'
            : 'bg-[#2D1B0E]'
        )}
        style={{
          boxShadow: isSelected
            ? 'inset 0 0 0 2px #9B6DD0, inset 0 0 8px #9B6DD040, 0 0 12px #9B6DD060'
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
            ? 'bg-gradient-to-b from-[#6B3FA0] to-[#4A2C6A]'
            : isEmpty
            ? 'bg-gradient-to-b from-[#2A1F14] to-[#1A1209]'
            : 'bg-gradient-to-b from-[#4A3628] to-[#2D1B0E]'
        )}
        style={{
          boxShadow: isSelected
            ? 'inset 1px 1px 0 #8B5DC040'
            : 'inset 1px 1px 0 #FFFFFF10',
        }}
      />

      {/* 하이라이트 */}
      {!isEmpty && (
        <div
          className="absolute top-[4px] left-[4px] right-[4px] h-[6px] rounded-sm opacity-30"
          style={{
            background: 'linear-gradient(to bottom, #FFFFFF40 0%, transparent 100%)',
          }}
        />
      )}

      {/* 단축키 표시 */}
      <div
        className="absolute -top-1 -left-1 w-5 h-5 flex items-center justify-center z-20"
        style={{
          background: 'linear-gradient(135deg, #1A1209 0%, #2D1B0E 100%)',
          border: '1px solid #5C3D2E',
          borderRadius: '3px',
          fontSize: '10px',
          fontWeight: 'bold',
          color: isSelected ? '#C9A0FF' : '#C9A227',
          textShadow: '0 1px 2px #000',
        }}
      >
        {shortcutKey}
      </div>

      {/* 컨텐츠 */}
      <div className="relative z-10 h-full flex flex-col items-center justify-center">
        {item && (
          <>
            <span className="text-xl drop-shadow-[0_2px_2px_rgba(0,0,0,0.5)]">
              {item.emoji}
            </span>
            <span
              className="text-[10px] font-bold mt-0.5"
              style={{
                color: isSelected ? '#C9A0FF' : '#C9A227',
                textShadow: '0 1px 2px #000',
              }}
            >
              {item.quantity}
            </span>
          </>
        )}
      </div>

      {/* 선택 시 반짝임 효과 */}
      {isSelected && (
        <motion.div
          className="absolute inset-0 pointer-events-none"
          initial={{ opacity: 0 }}
          animate={{ opacity: [0, 0.5, 0] }}
          transition={{ duration: 1.5, repeat: Infinity }}
          style={{
            background: 'radial-gradient(circle, #9B6DD040 0%, transparent 70%)',
          }}
        />
      )}
    </motion.button>
  );
}

export function PlacementModeUI({
  items,
  selectedItem,
  onSelectItem,
  onExit,
  onSave,
  onCancel,
  isSaving,
  hasChanges,
}: PlacementModeUIProps) {
  const [page, setPage] = useState(0);

  const placementItems = useMemo<PlacementItem[]>(() => {
    return items
      .filter(item => item.owned > 0)
      .map(item => ({
        code: item.code,
        name: item.nameKo,
        emoji: ITEM_EMOJI[item.code] || '📦',
        quantity: item.owned,
      }));
  }, [items]);

  const totalPages = Math.max(1, Math.ceil(placementItems.length / SLOTS_PER_PAGE));
  const startIndex = page * SLOTS_PER_PAGE;
  const visibleItems = placementItems.slice(startIndex, startIndex + SLOTS_PER_PAGE);
  const emptySlots = SLOTS_PER_PAGE - visibleItems.length;

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
        return;
      }

      if (e.key === 'Escape') {
        onExit();
        return;
      }

      if (e.key >= '1' && e.key <= '9') {
        const index = parseInt(e.key) - 1;
        if (index < visibleItems.length) {
          const item = visibleItems[index];
          onSelectItem(selectedItem === item.code ? null : item.code);
        }
        return;
      }

      if ((e.key === 'q' || e.key === 'Q' || e.key === 'ㅂ') && page > 0) {
        setPage(p => p - 1);
        return;
      }

      if ((e.key === 'e' || e.key === 'E' || e.key === 'ㄷ') && page < totalPages - 1) {
        setPage(p => p + 1);
        return;
      }

      if ((e.key === 's' || e.key === 'S' || e.key === 'ㄴ') && !e.ctrlKey && !e.metaKey) {
        e.preventDefault();
        if (!isSaving && hasChanges) {
          onSave();
        }
        return;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [visibleItems, selectedItem, onSelectItem, onExit, onSave, page, totalPages, isSaving, hasChanges]);

  return (
    <>
      {/* 상단 바 */}
      <div className="fixed top-0 left-0 right-0 z-50 pointer-events-none p-3">
        <motion.div
          initial={{ y: -50, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ type: 'spring', stiffness: 200, damping: 20 }}
          className="max-w-4xl mx-auto pointer-events-auto"
        >
          <div
            className="relative flex items-center justify-between px-4 py-3 rounded-lg"
            style={{
              background: 'linear-gradient(180deg, #4A2C6A 0%, #2D1B4A 100%)',
              border: '3px solid #6B3FA0',
              boxShadow: `
                inset 0 1px 0 #8B5DC0,
                inset 0 -1px 0 #1A0F2A,
                0 8px 24px rgba(0,0,0,0.5)
              `,
            }}
          >
            {/* 상단 장식 라인 */}
            <div
              className="absolute top-0 left-4 right-4 h-[2px]"
              style={{
                background: 'linear-gradient(90deg, transparent 0%, #9B6DD0 50%, transparent 100%)',
              }}
            />

            {/* 나가기 버튼 */}
            <PixelButton onClick={onExit} variant="ghost">
              <div className="flex items-center gap-2">
                <X className="w-4 h-4 text-purple-300" />
                <span
                  className="font-bold"
                  style={{ color: '#E8D5B7', textShadow: '0 1px 2px #000' }}
                >
                  나가기
                </span>
                <kbd
                  className="px-1.5 py-0.5 rounded text-xs font-bold"
                  style={{
                    background: '#2D1B4A',
                    color: '#9B6DD0',
                    border: '1px solid #6B3FA0',
                  }}
                >
                  ESC
                </kbd>
              </div>
            </PixelButton>

            {/* 제목 */}
            <div className="flex items-center gap-3">
              <Hammer className="w-5 h-5 text-purple-300" />
              <span
                className="font-black text-lg"
                style={{
                  color: '#E8D5B7',
                  textShadow: '0 2px 4px #000, 0 0 10px rgba(155,109,208,0.3)',
                }}
              >
                배치 모드
              </span>
              <span
                className="text-sm"
                style={{ color: '#9B6DD0', textShadow: '0 1px 2px #000' }}
              >
                드래그 이동 · 우클릭 삭제
              </span>
            </div>

            {/* 저장/취소 버튼 */}
            <div className="flex items-center gap-2">
              {hasChanges && (
                <PixelButton onClick={onCancel} disabled={isSaving} variant="danger">
                  <div className="flex items-center gap-2">
                    <Undo2 className="w-4 h-4 text-red-300" />
                    <span
                      className="font-bold"
                      style={{ color: '#E8D5B7', textShadow: '0 1px 2px #000' }}
                    >
                      취소
                    </span>
                  </div>
                </PixelButton>
              )}

              <PixelButton
                onClick={onSave}
                disabled={isSaving || !hasChanges}
                variant={hasChanges ? 'success' : 'ghost'}
              >
                <div className="flex items-center gap-2">
                  {isSaving ? (
                    <Loader2 className="w-4 h-4 text-green-300 animate-spin" />
                  ) : (
                    <Save className="w-4 h-4 text-green-300" />
                  )}
                  <span
                    className="font-bold"
                    style={{
                      color: hasChanges ? '#E8D5B7' : '#8B7355',
                      textShadow: '0 1px 2px #000',
                    }}
                  >
                    {isSaving ? '저장 중...' : '저장'}
                  </span>
                  {hasChanges && !isSaving && (
                    <kbd
                      className="px-1.5 py-0.5 rounded text-xs font-bold"
                      style={{
                        background: '#1A3D1A',
                        color: '#4ADE4A',
                        border: '1px solid #2A5D2A',
                      }}
                    >
                      S
                    </kbd>
                  )}
                </div>
              </PixelButton>
            </div>

            {/* 코너 장식 */}
            <div className="absolute -top-1 -left-1 w-3 h-3" style={{ background: '#6B3FA0' }} />
            <div className="absolute -top-1 -right-1 w-3 h-3" style={{ background: '#6B3FA0' }} />
            <div className="absolute -bottom-1 -left-1 w-3 h-3" style={{ background: '#6B3FA0' }} />
            <div className="absolute -bottom-1 -right-1 w-3 h-3" style={{ background: '#6B3FA0' }} />
          </div>
        </motion.div>
      </div>

      {/* 하단 핫바 */}
      <div className="fixed bottom-0 left-0 right-0 z-50 pointer-events-none pb-3">
        <div className="flex justify-center">
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
                background: 'linear-gradient(180deg, #4A2C6A 0%, #2D1B4A 100%)',
                border: '3px solid #6B3FA0',
                boxShadow: `
                  inset 0 2px 0 #8B5DC0,
                  inset 0 -2px 0 #1A0F2A,
                  0 8px 24px rgba(0,0,0,0.6),
                  0 0 0 1px #1A0F2A
                `,
              }}
            />

            {/* 상단 장식 라인 */}
            <div
              className="absolute top-0 left-4 right-4 h-[2px]"
              style={{
                background: 'linear-gradient(90deg, transparent 0%, #9B6DD0 50%, transparent 100%)',
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
                      ? 'bg-[#1A0F2A] text-[#4A2C6A] cursor-not-allowed'
                      : 'bg-[#2D1B4A] text-[#9B6DD0] hover:bg-[#4A2C6A] border border-[#6B3FA0]'
                  )}
                >
                  <ChevronLeft className="w-5 h-5" />
                </motion.button>
              )}

              {/* 아이템 슬롯 */}
              <div className="flex items-center gap-1">
                <AnimatePresence mode="popLayout">
                  {visibleItems.map((item, index) => (
                    <motion.div
                      key={item.code}
                      layout
                      initial={{ opacity: 0, scale: 0.8, y: 20 }}
                      animate={{ opacity: 1, scale: 1, y: 0 }}
                      exit={{ opacity: 0, scale: 0.8 }}
                      transition={{ delay: index * 0.03 }}
                    >
                      <PlacementSlot
                        item={item}
                        isSelected={selectedItem === item.code}
                        shortcutKey={index + 1}
                        onClick={() => onSelectItem(selectedItem === item.code ? null : item.code)}
                      />
                    </motion.div>
                  ))}

                  {/* 빈 슬롯 */}
                  {Array.from({ length: emptySlots }).map((_, i) => (
                    <motion.div
                      key={`empty-${i}`}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: (visibleItems.length + i) * 0.03 }}
                    >
                      <PlacementSlot isEmpty shortcutKey={visibleItems.length + i + 1} />
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
                      ? 'bg-[#1A0F2A] text-[#4A2C6A] cursor-not-allowed'
                      : 'bg-[#2D1B4A] text-[#9B6DD0] hover:bg-[#4A2C6A] border border-[#6B3FA0]'
                  )}
                >
                  <ChevronRight className="w-5 h-5" />
                </motion.button>
              )}

              {/* 페이지 표시 */}
              {totalPages > 1 && (
                <span
                  className="text-xs font-bold px-2"
                  style={{ color: '#9B6DD0', textShadow: '0 1px 2px #000' }}
                >
                  {page + 1}/{totalPages}
                </span>
              )}
            </div>

            {/* 하단 장식 */}
            <div className="absolute -bottom-1 left-1/2 -translate-x-1/2 flex gap-1">
              {[...Array(3)].map((_, i) => (
                <div
                  key={i}
                  className="w-2 h-2 rotate-45"
                  style={{
                    background: '#6B3FA0',
                    border: '1px solid #4A2C6A',
                  }}
                />
              ))}
            </div>
          </motion.div>
        </div>
      </div>
    </>
  );
}

export default PlacementModeUI;
