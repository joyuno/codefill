'use client';

/**
 * PlacementInventory - 배치 모드 인벤토리 UI
 * 인벤토리에 있는 아이템을 선택하여 맵에 배치
 */

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Package, X, ChevronDown, ChevronUp, Home, TreeDeciduous, Flower2, Fence } from 'lucide-react';
import { Button } from '@/components/ui/button';
import type { UnifiedShopItem } from '@/lib/api/farm';

type CategoryType = 'building' | 'tree' | 'decoration' | 'fence';

interface PlacementInventoryProps {
  isOpen: boolean;
  items: UnifiedShopItem[];  // owned > 0 인 아이템만 전달
  selectedItem: string | null;
  onSelectItem: (itemCode: string | null) => void;
  onClose: () => void;
}

// 카테고리별 아이콘
const CATEGORY_ICONS: Record<CategoryType, React.ReactNode> = {
  building: <Home className="w-4 h-4" />,
  tree: <TreeDeciduous className="w-4 h-4" />,
  decoration: <Flower2 className="w-4 h-4" />,
  fence: <Fence className="w-4 h-4" />,
};

const CATEGORY_LABELS: Record<CategoryType, string> = {
  building: '건물',
  tree: '나무',
  decoration: '장식',
  fence: '울타리',
};

// 아이템별 이모지
const ITEM_ICONS: Record<string, string> = {
  house: '🏠',
  well: '🪣',
  chicken_coop: '🐔',
  scarecrow: '🧑‍🌾',
  barn: '🏚️',
  tree_oak: '🌳',
  tree_pine: '🌲',
  tree_apple: '🍎',
  flower_red: '🌹',
  flower_yellow: '🌻',
  flower_purple: '💜',
  grass_tuft: '🌿',
  hay_pile: '🌾',
  rock_small: '🪨',
  fence_wood: '🪵',
  fence_stone: '🧱',
};

export function PlacementInventory({
  isOpen,
  items,
  selectedItem,
  onSelectItem,
  onClose,
}: PlacementInventoryProps) {
  const [isExpanded, setIsExpanded] = useState(true);
  const [activeCategory, setActiveCategory] = useState<CategoryType | 'all'>('all');

  // 인벤토리에 있는 아이템만 필터링 (owned > 0)
  const inventoryItems = items.filter(item => item.owned > 0);

  // 카테고리별 필터링
  const filteredItems = activeCategory === 'all'
    ? inventoryItems
    : inventoryItems.filter(item => item.category === activeCategory);

  // 카테고리별 아이템 개수
  const categoryCounts = inventoryItems.reduce((acc, item) => {
    acc[item.category] = (acc[item.category] || 0) + item.owned;
    return acc;
  }, {} as Record<string, number>);

  if (!isOpen) return null;

  return (
    <motion.div
      initial={{ x: -100, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      exit={{ x: -100, opacity: 0 }}
      className="fixed left-4 top-1/2 -translate-y-1/2 z-50"
    >
      <div
        className="rounded-2xl overflow-hidden"
        style={{
          background: 'linear-gradient(to bottom, #8D6E63 0%, #6D4C41 100%)',
          border: '4px solid #4E342E',
          boxShadow: '0 8px 32px rgba(0,0,0,0.4)',
          width: isExpanded ? '280px' : '60px',
          transition: 'width 0.3s ease',
        }}
      >
        {/* 헤더 */}
        <div
          className="p-3 flex items-center justify-between cursor-pointer"
          onClick={() => setIsExpanded(!isExpanded)}
          style={{
            background: 'linear-gradient(to bottom, #5D4037 0%, #4E342E 100%)',
            borderBottom: '3px solid #3E2723',
          }}
        >
          <div className="flex items-center gap-2">
            <Package className="w-5 h-5 text-amber-200" />
            {isExpanded && (
              <span className="text-amber-200 font-bold">인벤토리</span>
            )}
          </div>
          {isExpanded ? (
            <ChevronDown className="w-4 h-4 text-amber-300" />
          ) : (
            <ChevronUp className="w-4 h-4 text-amber-300" />
          )}
        </div>

        <AnimatePresence>
          {isExpanded && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
            >
              {/* 카테고리 필터 */}
              <div className="p-2 flex flex-wrap gap-1 border-b border-amber-900/50">
                <button
                  onClick={() => setActiveCategory('all')}
                  className={`px-2 py-1 rounded text-xs font-medium transition-colors ${
                    activeCategory === 'all'
                      ? 'bg-amber-600 text-white'
                      : 'bg-amber-900/30 text-amber-300 hover:bg-amber-800/50'
                  }`}
                >
                  전체 ({inventoryItems.reduce((sum, i) => sum + i.owned, 0)})
                </button>
                {(Object.keys(CATEGORY_LABELS) as CategoryType[]).map(cat => {
                  const count = categoryCounts[cat] || 0;
                  if (count === 0) return null;
                  return (
                    <button
                      key={cat}
                      onClick={() => setActiveCategory(cat)}
                      className={`px-2 py-1 rounded text-xs font-medium flex items-center gap-1 transition-colors ${
                        activeCategory === cat
                          ? 'bg-amber-600 text-white'
                          : 'bg-amber-900/30 text-amber-300 hover:bg-amber-800/50'
                      }`}
                    >
                      {CATEGORY_ICONS[cat]}
                      <span>{count}</span>
                    </button>
                  );
                })}
              </div>

              {/* 아이템 목록 */}
              <div className="p-2 max-h-[300px] overflow-y-auto space-y-1">
                {filteredItems.length === 0 ? (
                  <div className="text-center py-6 text-amber-300/70 text-sm">
                    인벤토리가 비어있습니다
                  </div>
                ) : (
                  filteredItems.map(item => {
                    const icon = ITEM_ICONS[item.code] || '📦';
                    const isSelected = selectedItem === item.code;

                    return (
                      <button
                        key={item.code}
                        onClick={() => onSelectItem(isSelected ? null : item.code)}
                        className={`w-full p-2 rounded-lg flex items-center gap-3 transition-all ${
                          isSelected
                            ? 'bg-green-600/50 border-2 border-green-400'
                            : 'bg-black/20 border-2 border-transparent hover:bg-black/30'
                        }`}
                      >
                        <span className="text-2xl">{icon}</span>
                        <div className="flex-1 text-left">
                          <p className="font-medium text-amber-100 text-sm">
                            {item.nameKo}
                          </p>
                          <p className="text-xs text-amber-300">
                            보유: {item.owned}개
                          </p>
                        </div>
                        {isSelected && (
                          <div className="w-6 h-6 rounded-full bg-green-500 flex items-center justify-center">
                            <span className="text-white text-xs">✓</span>
                          </div>
                        )}
                      </button>
                    );
                  })
                )}
              </div>

              {/* 안내 */}
              <div
                className="p-2 text-center text-xs text-amber-300/70"
                style={{
                  background: 'rgba(0,0,0,0.2)',
                  borderTop: '2px solid rgba(255,255,255,0.1)',
                }}
              >
                {selectedItem ? (
                  <span className="text-green-300">맵을 클릭하여 배치하세요</span>
                ) : (
                  <span>아이템을 선택하세요</span>
                )}
              </div>

              {/* 닫기 버튼 */}
              <div className="p-2 border-t border-amber-900/50">
                <Button
                  onClick={onClose}
                  size="sm"
                  className="w-full bg-red-600 hover:bg-red-500 text-white"
                >
                  <X className="w-4 h-4 mr-1" />
                  배치 모드 종료
                </Button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
}
