'use client';

/**
 * UnifiedHotbar - 통합 핫바
 * 씨앗과 배치 아이템을 탭으로 전환
 * 보유한 아이템만 표시, 6슬롯 페이지네이션
 */

import { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronLeft, ChevronRight, Sprout, Hammer, Undo2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { InventoryItem, UnifiedShopItem } from '@/lib/api/farm';
import { CROP_INFO, type CropVariety } from './Hotbar';

// 핫바 모드
export type HotbarMode = 'seed' | 'placement';

// 슬롯당 아이템
interface HotbarItem {
  code: string;
  name: string;
  icon?: string;  // 이미지 경로 (씨앗용)
  emoji?: string; // 이모지 (배치 아이템용)
  quantity: number;
}

interface UnifiedHotbarProps {
  // 씨앗 데이터
  inventory: InventoryItem[];
  // 배치 아이템 데이터 (보유한 것만)
  placeableItems: UnifiedShopItem[];
  // 현재 모드
  mode: HotbarMode;
  onModeChange: (mode: HotbarMode) => void;
  // 선택된 아이템
  selectedItem: string | null;
  onSelectItem: (itemCode: string | null) => void;
  // 배치 취소 (배치 모드에서만 사용)
  onCancelPlacement?: () => void;
  isSaving?: boolean;
}

// 배치 아이템 이모지 매핑
const ITEM_EMOJI: Record<string, string> = {
  // 건물
  house: '🏠',
  chicken_coop: '🐔',
  water_well: '🪣',
  barn: '🏚️',
  scarecrow: '🎃',
  // 밭
  farm_plot: '🌱',
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
  rock_small: '🪨',
  rock_large: '⛰️',
  pond_small: '💧',
  // 울타리
  fence_wood: '🪵',
  fence_stone: '🧱',
  fence_iron: '⛓️',
};

const SLOTS_PER_PAGE = 6;

export function UnifiedHotbar({
  inventory,
  placeableItems,
  mode,
  onModeChange,
  selectedItem,
  onSelectItem,
  onCancelPlacement,
  isSaving = false,
}: UnifiedHotbarProps) {
  const [page, setPage] = useState(0);

  // 씨앗 아이템 (보유한 것만)
  const seedItems = useMemo<HotbarItem[]>(() => {
    return Object.entries(CROP_INFO)
      .map(([code, info]) => {
        const seedCode = `seed_${code}`;
        const item = inventory.find(i => i.itemCode === seedCode);
        const quantity = item?.quantity || 0;
        return {
          code: seedCode,
          name: info.name,
          icon: info.icon,
          quantity,
        };
      })
      .filter(item => item.quantity > 0);
  }, [inventory]);

  // 배치 아이템 (보유한 것만)
  const placementItems = useMemo<HotbarItem[]>(() => {
    return placeableItems
      .filter(item => item.owned > 0)
      .map(item => ({
        code: item.code,
        name: item.nameKo,
        emoji: ITEM_EMOJI[item.code] || '📦',
        quantity: item.owned,
      }));
  }, [placeableItems]);

  // 현재 모드에 따른 아이템
  const currentItems = mode === 'seed' ? seedItems : placementItems;

  // 페이지네이션
  const totalPages = Math.max(1, Math.ceil(currentItems.length / SLOTS_PER_PAGE));
  const startIndex = page * SLOTS_PER_PAGE;
  const visibleItems = currentItems.slice(startIndex, startIndex + SLOTS_PER_PAGE);

  // 빈 슬롯 채우기
  const emptySlots = SLOTS_PER_PAGE - visibleItems.length;

  // 모드 변경 시 페이지 리셋
  const handleModeChange = (newMode: HotbarMode) => {
    if (newMode !== mode) {
      setPage(0);
      onSelectItem(null);
      onModeChange(newMode);
    }
  };

  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 pointer-events-none">
      <div
        className="mx-auto max-w-xl px-4 pb-4 pointer-events-auto"
        style={{ filter: 'drop-shadow(0 -4px 6px rgba(0,0,0,0.3))' }}
      >
        <div
          className="p-2 rounded-xl"
          style={{
            background: 'linear-gradient(to bottom, #5D4037 0%, #4E342E 100%)',
            border: '4px solid #3E2723',
            boxShadow: 'inset 0 2px 4px rgba(255,255,255,0.1), inset 0 -2px 4px rgba(0,0,0,0.2)',
          }}
        >
          <div className="flex items-center gap-2">
            {/* 모드 탭 */}
            <div className="flex flex-col gap-1">
              <motion.button
                onClick={() => handleModeChange('seed')}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className={cn(
                  'w-10 h-10 rounded-lg flex items-center justify-center transition-all',
                  mode === 'seed'
                    ? 'bg-green-500 border-2 border-green-300'
                    : 'bg-amber-900/50 border-2 border-amber-700 hover:bg-amber-800/50'
                )}
                title="씨앗"
              >
                <Sprout className="w-5 h-5 text-white" />
              </motion.button>
              <motion.button
                onClick={() => handleModeChange('placement')}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className={cn(
                  'w-10 h-10 rounded-lg flex items-center justify-center transition-all',
                  mode === 'placement'
                    ? 'bg-purple-500 border-2 border-purple-300'
                    : 'bg-amber-900/50 border-2 border-amber-700 hover:bg-amber-800/50'
                )}
                title="배치"
              >
                <Hammer className="w-5 h-5 text-white" />
              </motion.button>
            </div>

            {/* 구분선 */}
            <div className="w-px h-20 bg-amber-700" />

            {/* 아이템 슬롯 */}
            <div className="flex items-center gap-1 flex-1">
              <AnimatePresence mode="popLayout">
                {visibleItems.map((item) => {
                  const isSelected = selectedItem === item.code;
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
                        'relative w-14 h-14 rounded-lg flex flex-col items-center justify-center transition-all',
                        isSelected
                          ? 'bg-amber-400 border-2 border-amber-200'
                          : 'bg-amber-900/50 border-2 border-amber-700 hover:bg-amber-800/50'
                      )}
                      title={`${item.name} (${item.quantity}개)`}
                    >
                      {item.icon ? (
                        <img
                          src={item.icon}
                          alt={item.name}
                          className="w-8 h-8 object-contain"
                          style={{ imageRendering: 'pixelated' }}
                        />
                      ) : (
                        <span className="text-xl">{item.emoji}</span>
                      )}
                      <span className="text-[10px] font-bold text-white">
                        {item.quantity}
                      </span>
                      {isSelected && (
                        <motion.div
                          className="absolute -top-1 left-1/2 -translate-x-1/2 w-0 h-0"
                          layoutId="hotbar-indicator"
                          style={{
                            borderLeft: '6px solid transparent',
                            borderRight: '6px solid transparent',
                            borderTop: '6px solid #FCD34D',
                          }}
                        />
                      )}
                    </motion.button>
                  );
                })}

                {/* 빈 슬롯 */}
                {Array.from({ length: emptySlots }).map((_, i) => (
                  <div
                    key={`empty-${i}`}
                    className="w-14 h-14 rounded-lg bg-amber-900/30 border-2 border-amber-800/50"
                  />
                ))}
              </AnimatePresence>
            </div>

            {/* 구분선 */}
            <div className="w-px h-20 bg-amber-700" />

            {/* 페이지네이션 */}
            <div className="flex flex-col items-center gap-1">
              <motion.button
                onClick={() => setPage(p => Math.max(0, p - 1))}
                disabled={page === 0}
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                className={cn(
                  'w-8 h-8 rounded-lg flex items-center justify-center',
                  page === 0
                    ? 'bg-amber-900/30 text-amber-700 cursor-not-allowed'
                    : 'bg-amber-800/50 text-amber-200 hover:bg-amber-700/50'
                )}
              >
                <ChevronLeft className="w-4 h-4" />
              </motion.button>
              <span className="text-amber-400 text-xs font-bold">
                {page + 1}/{totalPages}
              </span>
              <motion.button
                onClick={() => setPage(p => Math.min(totalPages - 1, p + 1))}
                disabled={page >= totalPages - 1}
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                className={cn(
                  'w-8 h-8 rounded-lg flex items-center justify-center',
                  page >= totalPages - 1
                    ? 'bg-amber-900/30 text-amber-700 cursor-not-allowed'
                    : 'bg-amber-800/50 text-amber-200 hover:bg-amber-700/50'
                )}
              >
                <ChevronRight className="w-4 h-4" />
              </motion.button>
            </div>
          </div>

          {/* 현재 모드 표시 + 취소 버튼 */}
          <div className="mt-2 flex items-center justify-center gap-3">
            <span className={cn(
              'text-xs font-bold px-3 py-1 rounded-full',
              mode === 'seed'
                ? 'bg-green-600/50 text-green-200'
                : 'bg-purple-600/50 text-purple-200'
            )}>
              {mode === 'seed'
                ? '씨앗 모드 - 밭에 심기'
                : '배치 모드 - 드래그로 이동, 우클릭 삭제 (씨앗 모드 전환 시 저장)'}
            </span>

            {/* 배치 모드 취소 버튼 */}
            {mode === 'placement' && (
              <motion.button
                onClick={onCancelPlacement}
                disabled={isSaving}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className={cn(
                  'flex items-center gap-1 px-3 py-1 rounded-full text-xs font-bold transition-all',
                  'bg-red-600/50 text-red-200 hover:bg-red-500/50',
                  isSaving && 'opacity-50 cursor-not-allowed'
                )}
                title="변경 취소"
              >
                <Undo2 className="w-3 h-3" />
                {isSaving ? '저장 중...' : '취소'}
              </motion.button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default UnifiedHotbar;
