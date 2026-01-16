'use client';

/**
 * UnifiedShopModal - 통합 상점 모달
 * 건물, 밭, 나무, 장식, 울타리 등 모든 구매 가능 아이템
 */

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Store, X, Coins, Check, Home, TreeDeciduous, Flower2, Fence, MapPin } from 'lucide-react';
import { Button } from '@/components/ui/button';
import type { UnifiedShopItem } from '@/lib/api/farm';

type CategoryType = 'building' | 'tree' | 'decoration' | 'fence';

interface UnifiedShopModalProps {
  isOpen: boolean;
  onClose: () => void;
  gold: number;
  items: UnifiedShopItem[];
  onPurchase: (itemCode: string) => void;
  onPurchaseAndPlace?: (itemCode: string) => void;
  isLoading?: boolean;
}

// 카테고리별 아이콘/색상
const CATEGORY_CONFIG: Record<CategoryType, { icon: React.ReactNode; label: string; color: string }> = {
  building: { icon: <Home className="w-4 h-4" />, label: '건물', color: 'text-amber-400' },
  tree: { icon: <TreeDeciduous className="w-4 h-4" />, label: '나무', color: 'text-emerald-400' },
  decoration: { icon: <Flower2 className="w-4 h-4" />, label: '장식', color: 'text-pink-400' },
  fence: { icon: <Fence className="w-4 h-4" />, label: '울타리', color: 'text-stone-400' },
};

// 희귀도별 색상
const RARITY_COLORS: Record<string, string> = {
  common: 'text-gray-300',
  uncommon: 'text-green-400',
  rare: 'text-blue-400',
  epic: 'text-purple-400',
};

const RARITY_LABELS: Record<string, string> = {
  common: '일반',
  uncommon: '고급',
  rare: '희귀',
  epic: '에픽',
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

export function UnifiedShopModal({
  isOpen,
  onClose,
  gold,
  items,
  onPurchase,
  onPurchaseAndPlace,
  isLoading,
}: UnifiedShopModalProps) {
  const [activeCategory, setActiveCategory] = useState<CategoryType>('building');

  // 카테고리별 아이템 필터링
  const filteredItems = items.filter(item => item.category === activeCategory);

  // 모달이 열릴 때 첫 번째 카테고리로 리셋
  useEffect(() => {
    if (isOpen) {
      setActiveCategory('building');
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const categories = Object.entries(CATEGORY_CONFIG) as [CategoryType, typeof CATEGORY_CONFIG[CategoryType]][];

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/60 z-[100] flex items-center justify-center p-4"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.9, y: 20 }}
        animate={{ scale: 1, y: 0 }}
        exit={{ scale: 0.9, y: 20 }}
        onClick={e => e.stopPropagation()}
        className="w-full max-w-lg max-h-[80vh] overflow-hidden rounded-2xl"
        style={{
          background: 'linear-gradient(to bottom, #8D6E63 0%, #6D4C41 100%)',
          border: '6px solid #4E342E',
          boxShadow: '0 10px 40px rgba(0,0,0,0.5)',
        }}
      >
        {/* 헤더 */}
        <div
          className="p-4 flex items-center justify-between"
          style={{
            background: 'linear-gradient(to bottom, #5D4037 0%, #4E342E 100%)',
            borderBottom: '4px solid #3E2723',
          }}
        >
          <h2 className="text-xl font-bold text-amber-200 flex items-center gap-2">
            <Store className="w-6 h-6" />
            상점
          </h2>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 text-yellow-300">
              <Coins className="w-5 h-5" />
              <span className="font-bold">{gold.toLocaleString()}G</span>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={onClose}
              className="text-amber-200 hover:text-white hover:bg-amber-800"
            >
              <X className="w-5 h-5" />
            </Button>
          </div>
        </div>

        {/* 카테고리 탭 */}
        <div className="flex border-b-2 border-amber-900 overflow-x-auto">
          {categories.map(([key, config]) => (
            <button
              key={key}
              onClick={() => setActiveCategory(key)}
              className={`flex-1 min-w-[80px] py-3 px-2 flex items-center justify-center gap-1.5 font-medium transition-colors text-sm ${
                activeCategory === key
                  ? 'bg-amber-700 text-amber-100 border-b-2 border-amber-400'
                  : 'text-amber-300 hover:bg-amber-800'
              }`}
            >
              <span className={config.color}>{config.icon}</span>
              <span className="hidden sm:inline">{config.label}</span>
            </button>
          ))}
        </div>

        {/* 상품 목록 */}
        <div className="p-4 overflow-y-auto max-h-[50vh] space-y-3">
          {filteredItems.length === 0 ? (
            <div className="text-center py-8 text-amber-300">
              이 카테고리에 아이템이 없습니다
            </div>
          ) : (
            filteredItems.map(item => {
              const icon = ITEM_ICONS[item.code] || '📦';
              const rarityColor = RARITY_COLORS[item.rarity] || 'text-gray-300';
              const rarityLabel = RARITY_LABELS[item.rarity] || item.rarity;
              const canAfford = gold >= item.price;
              const isOwned = item.placed > 0 || item.owned > 0;
              const isFree = item.price === 0;
              const atMaxQuantity = item.maxQuantity !== null && (item.owned + item.placed) >= item.maxQuantity;

              return (
                <div
                  key={item.code}
                  className="flex items-center justify-between p-3 rounded-lg"
                  style={{
                    background: isOwned
                      ? 'rgba(34,197,94,0.15)'
                      : 'rgba(0,0,0,0.2)',
                    border: isOwned
                      ? '2px solid rgba(34,197,94,0.4)'
                      : '2px solid rgba(255,255,255,0.1)',
                  }}
                >
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">{icon}</span>
                    <div>
                      <p className="font-bold text-amber-100">{item.nameKo}</p>
                      <div className="flex items-center gap-2 text-sm">
                        <span className={rarityColor}>{rarityLabel}</span>
                        {!isFree && (
                          <span className="text-amber-300">
                            • {item.price.toLocaleString()}G
                          </span>
                        )}
                        {item.maxQuantity !== null && (
                          <span className="text-gray-400">
                            • {item.owned + item.placed}/{item.maxQuantity}
                          </span>
                        )}
                        {item.owned > 0 && (
                          <span className="text-blue-300">
                            • 인벤토리: {item.owned}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {isFree && isOwned ? (
                      <div className="flex items-center gap-1 text-green-400 px-3 py-1.5">
                        <Check className="w-4 h-4" />
                        <span className="font-medium">기본 제공</span>
                      </div>
                    ) : atMaxQuantity ? (
                      <div className="flex items-center gap-1 text-yellow-400 px-3 py-1.5">
                        <Check className="w-4 h-4" />
                        <span className="font-medium">최대 보유</span>
                      </div>
                    ) : (
                      <>
                        <Button
                          size="sm"
                          onClick={() => onPurchase(item.code)}
                          disabled={!canAfford || isLoading || !item.canBuy}
                          className={`border-2 ${
                            canAfford && item.canBuy
                              ? 'bg-green-600 hover:bg-green-500 text-white border-green-400'
                              : 'bg-gray-600 text-gray-400 border-gray-500 cursor-not-allowed'
                          }`}
                        >
                          {isLoading ? '...' : '구매'}
                        </Button>
                        {onPurchaseAndPlace && (
                          <Button
                            size="sm"
                            onClick={() => onPurchaseAndPlace(item.code)}
                            disabled={!canAfford || isLoading || !item.canBuy}
                            className={`border-2 flex items-center gap-1 ${
                              canAfford && item.canBuy
                                ? 'bg-purple-600 hover:bg-purple-500 text-white border-purple-400'
                                : 'bg-gray-600 text-gray-400 border-gray-500 cursor-not-allowed'
                            }`}
                            title="구매 후 바로 배치"
                          >
                            <MapPin className="w-3 h-3" />
                            배치
                          </Button>
                        )}
                      </>
                    )}
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* 하단 안내 */}
        <div
          className="p-3 text-center text-sm text-amber-300"
          style={{
            background: 'rgba(0,0,0,0.2)',
            borderTop: '2px solid rgba(255,255,255,0.1)',
          }}
        >
          구매한 아이템은 인벤토리에 저장됩니다. 배치 모드에서 맵에 배치하세요.
        </div>
      </motion.div>
    </motion.div>
  );
}
