'use client';

/**
 * PlacementModeUI - 배치 모드 전용 UI
 * - 상단: ESC 나가기, 제목, 저장/취소 버튼
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
  // 기존 건물
  house: '🏠',
  chicken_coop: '🐔',
  water_well: '🪣',
  well: '🪣',
  barn: '🏚️',
  scarecrow: '🎃',
  farm_plot: '🌱',

  // 새 건물
  farmer_house_1: '🏡',
  farmer_house_2: '🏘️',
  barn_small: '🏚️',
  stable: '🐴',
  silos: '🗼',
  doghouse: '🐕',

  // 작업대
  stone_oven: '🔥',
  cheese_machine: '🧀',
  diy_crafting_table: '🔨',
  tailor_table: '🧵',
  woodwork_table: '🪓',

  // 마켓 가판대
  market_stand_blue: '🛒',
  market_stand_green: '🛍️',
  market_stand_yellow: '🏪',
  market_stand_pink: '🎪',

  // 나무
  tree_oak: '🌳',
  tree_pine: '🌲',
  tree_cherry: '🌸',
  tree_apple: '🍎',
  tree_maple: '🍁',

  // 장식
  flower_red: '🌹',
  flower_yellow: '🌻',
  flower_blue: '💐',
  grass_patch: '🌿',
  grass_tuft: '🌿',
  hay_pile: '🌾',
  rock_small: '🪨',
  rock_large: '⛰️',
  pond_small: '💧',

  // 울타리
  fence_wood: '🪵',
  fence_stone: '🧱',
  fence_iron: '⛓️',
};

const SLOTS_PER_PAGE = 9;

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

  // 보유한 아이템만 필터링
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

  // 페이지네이션
  const totalPages = Math.max(1, Math.ceil(placementItems.length / SLOTS_PER_PAGE));
  const startIndex = page * SLOTS_PER_PAGE;
  const visibleItems = placementItems.slice(startIndex, startIndex + SLOTS_PER_PAGE);
  const emptySlots = SLOTS_PER_PAGE - visibleItems.length;

  // 키보드 단축키
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
        return;
      }

      // ESC: 나가기
      if (e.key === 'Escape') {
        onExit();
        return;
      }

      // 1-9: 아이템 선택
      if (e.key >= '1' && e.key <= '9') {
        const index = parseInt(e.key) - 1;
        if (index < visibleItems.length) {
          const item = visibleItems[index];
          onSelectItem(selectedItem === item.code ? null : item.code);
        }
        return;
      }

      // Q: 이전 페이지
      if ((e.key === 'q' || e.key === 'Q' || e.key === 'ㅂ') && page > 0) {
        setPage(p => p - 1);
        return;
      }

      // E: 다음 페이지 (배치모드에서는 E가 페이지 이동)
      if ((e.key === 'e' || e.key === 'E' || e.key === 'ㄷ') && page < totalPages - 1) {
        setPage(p => p + 1);
        return;
      }

      // S: 저장 (Ctrl 없이)
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
      {/* 상단 바 - 배치 모드 전용 */}
      <div className="fixed top-0 left-0 right-0 z-50 pointer-events-none p-4">
        <div className="max-w-4xl mx-auto">
          <div
            className="pointer-events-auto flex items-center justify-between px-4 py-3 rounded-xl"
            style={{
              background: 'linear-gradient(to bottom, #4A148C 0%, #311B92 100%)',
              border: '3px solid #7C4DFF',
              boxShadow: '0 4px 12px rgba(103, 58, 183, 0.4)',
            }}
          >
            {/* 나가기 버튼 */}
            <motion.button
              onClick={onExit}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="flex items-center gap-2 px-3 py-2 rounded-lg bg-white/10 hover:bg-white/20 text-white"
            >
              <X className="w-4 h-4" />
              <span className="font-bold">나가기</span>
              <kbd className="px-1.5 py-0.5 bg-black/30 rounded text-xs">ESC</kbd>
            </motion.button>

            {/* 제목 */}
            <div className="flex items-center gap-2 text-white">
              <Hammer className="w-5 h-5" />
              <span className="font-bold text-lg">배치 모드</span>
              <span className="text-purple-200 text-sm">(드래그 이동, 우클릭 삭제)</span>
            </div>

            {/* 저장/취소 버튼 */}
            <div className="flex items-center gap-2">
              {hasChanges && (
                <motion.button
                  onClick={onCancel}
                  disabled={isSaving}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className={cn(
                    'flex items-center gap-2 px-3 py-2 rounded-lg text-white',
                    'bg-red-500/50 hover:bg-red-500/70',
                    isSaving && 'opacity-50 cursor-not-allowed'
                  )}
                >
                  <Undo2 className="w-4 h-4" />
                  <span className="font-bold">취소</span>
                </motion.button>
              )}

              <motion.button
                onClick={onSave}
                disabled={isSaving || !hasChanges}
                whileHover={hasChanges && !isSaving ? { scale: 1.05 } : {}}
                whileTap={hasChanges && !isSaving ? { scale: 0.95 } : {}}
                className={cn(
                  'flex items-center gap-2 px-4 py-2 rounded-lg text-white transition-all',
                  hasChanges && !isSaving
                    ? 'bg-green-500 hover:bg-green-400'
                    : 'bg-gray-500/50 cursor-not-allowed',
                  isSaving && 'opacity-70'
                )}
              >
                {isSaving ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Save className="w-4 h-4" />
                )}
                <span className="font-bold">{isSaving ? '저장 중...' : '저장'}</span>
                {hasChanges && !isSaving && <kbd className="px-1.5 py-0.5 bg-black/30 rounded text-xs">S</kbd>}
              </motion.button>
            </div>
          </div>
        </div>
      </div>

      {/* 하단 핫바 - 배치 아이템 */}
      <div className="fixed bottom-0 left-0 right-0 z-50 pointer-events-none pb-4">
        <div className="flex justify-center">
          <div
            className="pointer-events-auto flex items-center gap-2 px-3 py-2 rounded-xl"
            style={{
              background: 'linear-gradient(to bottom, #4A148C 0%, #311B92 100%)',
              border: '3px solid #7C4DFF',
              boxShadow: '0 4px 12px rgba(103, 58, 183, 0.4)',
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
                  'w-8 h-8 rounded-lg flex items-center justify-center',
                  page === 0
                    ? 'bg-purple-900/30 text-purple-500 cursor-not-allowed'
                    : 'bg-purple-800/50 text-purple-200 hover:bg-purple-700/50'
                )}
                title="이전 (Q)"
              >
                <ChevronLeft className="w-4 h-4" />
              </motion.button>
            )}

            {/* 아이템 슬롯 */}
            <div className="flex items-center gap-1">
              <AnimatePresence mode="popLayout">
                {visibleItems.map((item, index) => {
                  const isSelected = selectedItem === item.code;
                  const shortcutKey = index + 1;
                  return (
                    <motion.button
                      key={item.code}
                      layout
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, scale: 0.8 }}
                      onClick={() => onSelectItem(isSelected ? null : item.code)}
                      whileHover={{ y: -4 }}
                      whileTap={{ scale: 0.95 }}
                      className={cn(
                        'relative w-12 h-12 rounded-lg flex flex-col items-center justify-center transition-all',
                        isSelected
                          ? 'bg-purple-400 border-2 border-purple-200 shadow-lg shadow-purple-500/30'
                          : 'bg-purple-900/50 border-2 border-purple-600 hover:bg-purple-800/50'
                      )}
                      title={`${item.name} (${item.quantity}개) - ${shortcutKey}키`}
                    >
                      {/* 단축키 표시 */}
                      <span className="absolute -top-1 -left-1 w-4 h-4 bg-gray-800 rounded text-[10px] font-bold text-white flex items-center justify-center">
                        {shortcutKey}
                      </span>

                      <span className="text-xl">{item.emoji}</span>
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
                    className="w-12 h-12 rounded-lg bg-purple-900/30 border-2 border-purple-800/50"
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
                  'w-8 h-8 rounded-lg flex items-center justify-center',
                  page >= totalPages - 1
                    ? 'bg-purple-900/30 text-purple-500 cursor-not-allowed'
                    : 'bg-purple-800/50 text-purple-200 hover:bg-purple-700/50'
                )}
                title="다음 (E)"
              >
                <ChevronRight className="w-4 h-4" />
              </motion.button>
            )}

            {/* 페이지 표시 */}
            {totalPages > 1 && (
              <span className="text-purple-300 text-xs font-bold px-1">
                {page + 1}/{totalPages}
              </span>
            )}
          </div>
        </div>
      </div>
    </>
  );
}

export default PlacementModeUI;
