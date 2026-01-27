'use client';

/**
 * UnifiedShopModal - 픽셀 RPG 스타일 통합 상점 모달
 * 건물, 나무, 장식, 울타리 등 모든 구매 가능 아이템
 */

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Store, X, Check, Home, TreeDeciduous, Flower2, Fence, MapPin, Sparkles } from 'lucide-react';
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

// 카테고리별 설정
const CATEGORY_CONFIG: Record<CategoryType, { icon: React.ReactNode; label: string; color: string }> = {
  building: { icon: <Home className="w-4 h-4" />, label: '건물', color: '#FFB74D' },
  tree: { icon: <TreeDeciduous className="w-4 h-4" />, label: '나무', color: '#81C784' },
  decoration: { icon: <Flower2 className="w-4 h-4" />, label: '장식', color: '#F48FB1' },
  fence: { icon: <Fence className="w-4 h-4" />, label: '울타리', color: '#A1887F' },
};

// 희귀도별 설정
const RARITY_CONFIG: Record<string, { color: string; label: string; glow: string }> = {
  common: { color: '#9E9E9E', label: '일반', glow: 'none' },
  uncommon: { color: '#4CAF50', label: '고급', glow: '0 0 8px rgba(76,175,80,0.4)' },
  rare: { color: '#2196F3', label: '희귀', glow: '0 0 10px rgba(33,150,243,0.5)' },
  epic: { color: '#9C27B0', label: '에픽', glow: '0 0 12px rgba(156,39,176,0.6)' },
};

// 아이템별 이모지
const ITEM_ICONS: Record<string, string> = {
  house: '🏠', well: '🪣', chicken_coop: '🐔', scarecrow: '🧑‍🌾', barn: '🏚️',
  tree_oak: '🌳', tree_pine: '🌲', tree_apple: '🍎', tree_cherry: '🌸', tree_maple: '🍁',
  flower_red: '🌹', flower_yellow: '🌻', flower_purple: '💜', flower_blue: '💐',
  grass_tuft: '🌿', grass_patch: '🌿', hay_pile: '🌾', rock_small: '🪨', rock_large: '⛰️',
  pond_small: '💧', fence_wood: '🪵', fence_stone: '🧱', fence_iron: '⛓️',
  farmer_house_1: '🏡', farmer_house_2: '🏘️', barn_small: '🏚️', stable: '🐴',
  silos: '🗼', doghouse: '🐕', stone_oven: '🔥', cheese_machine: '🧀',
  diy_crafting_table: '🔨', tailor_table: '🧵', woodwork_table: '🪓',
  market_stand_blue: '🛒', market_stand_green: '🛍️', market_stand_yellow: '🏪', market_stand_pink: '🎪',
};

// 픽셀 버튼 컴포넌트
function PixelButton({
  children,
  onClick,
  disabled,
  variant = 'default',
  size = 'md',
}: {
  children: React.ReactNode;
  onClick?: () => void;
  disabled?: boolean;
  variant?: 'default' | 'success' | 'purple';
  size?: 'sm' | 'md';
}) {
  const variants = {
    default: { bg: '#5C3D2E', border: '#8B5A3C' },
    success: { bg: '#2A5D2A', border: '#4ADE4A' },
    purple: { bg: '#4A2C6A', border: '#9B6DD0' },
  };

  const v = variants[variant];
  const padding = size === 'sm' ? 'px-3 py-1.5' : 'px-4 py-2';

  return (
    <motion.button
      onClick={onClick}
      disabled={disabled}
      whileHover={!disabled ? { scale: 1.03, y: -1 } : undefined}
      whileTap={!disabled ? { scale: 0.97 } : undefined}
      className={`relative ${padding} rounded font-bold text-sm transition-all ${
        disabled ? 'opacity-50 cursor-not-allowed' : ''
      }`}
      style={{
        background: `linear-gradient(180deg, ${v.bg} 0%, ${v.bg}CC 100%)`,
        border: `2px solid ${v.border}`,
        color: '#E8D5B7',
        textShadow: '0 1px 2px #000',
        boxShadow: disabled
          ? 'none'
          : `inset 0 1px 0 rgba(255,255,255,0.15), 0 3px 6px rgba(0,0,0,0.3)`,
      }}
    >
      {children}
    </motion.button>
  );
}

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

  const filteredItems = items.filter(item => item.category === activeCategory);

  useEffect(() => {
    if (isOpen) {
      setActiveCategory('building');
    }
  }, [isOpen]);

  const categories = Object.entries(CATEGORY_CONFIG) as [CategoryType, typeof CATEGORY_CONFIG[CategoryType]][];

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black/70 z-[100] flex items-center justify-center p-4"
          onClick={onClose}
        >
          <motion.div
            initial={{ scale: 0.9, y: 30, opacity: 0 }}
            animate={{ scale: 1, y: 0, opacity: 1 }}
            exit={{ scale: 0.9, y: 30, opacity: 0 }}
            transition={{ type: 'spring', stiffness: 300, damping: 25 }}
            onClick={e => e.stopPropagation()}
            className="relative w-full max-w-lg max-h-[85vh] overflow-hidden rounded-lg"
            style={{
              background: 'linear-gradient(180deg, #3D2A1A 0%, #2D1B0E 100%)',
              border: '4px solid #5C3D2E',
              boxShadow: `
                inset 0 2px 0 #4A3628,
                inset 0 -2px 0 #1A0F08,
                0 12px 40px rgba(0,0,0,0.7)
              `,
            }}
          >
            {/* 상단 장식 라인 */}
            <div
              className="absolute top-0 left-6 right-6 h-[2px]"
              style={{
                background: 'linear-gradient(90deg, transparent 0%, #C9A227 50%, transparent 100%)',
              }}
            />

            {/* 코너 장식 */}
            <div className="absolute -top-1 -left-1 w-4 h-4" style={{ background: '#5C3D2E' }} />
            <div className="absolute -top-1 -right-1 w-4 h-4" style={{ background: '#5C3D2E' }} />
            <div className="absolute -bottom-1 -left-1 w-4 h-4" style={{ background: '#5C3D2E' }} />
            <div className="absolute -bottom-1 -right-1 w-4 h-4" style={{ background: '#5C3D2E' }} />

            {/* 헤더 */}
            <div
              className="relative p-4 flex items-center justify-between"
              style={{
                background: 'linear-gradient(180deg, #4A3628 0%, #3D2A1A 100%)',
                borderBottom: '3px solid #5C3D2E',
              }}
            >
              <h2
                className="text-xl font-black flex items-center gap-2"
                style={{
                  color: '#FFD700',
                  textShadow: '0 2px 4px rgba(0,0,0,0.8), 0 0 10px rgba(255,215,0,0.3)',
                }}
              >
                <Store className="w-6 h-6" />
                상점
              </h2>

              <div className="flex items-center gap-4">
                {/* 골드 표시 */}
                <div
                  className="flex items-center gap-2 px-3 py-1.5 rounded"
                  style={{
                    background: 'rgba(0,0,0,0.3)',
                    border: '2px solid #C9A227',
                  }}
                >
                  <img src="/farm/icons/gold_coin.png" alt="gold" className="w-5 h-5" style={{ imageRendering: 'pixelated' }} />
                  <span
                    className="font-black"
                    style={{
                      color: '#FFD700',
                      textShadow: '0 1px 2px rgba(0,0,0,0.8)',
                    }}
                  >
                    {gold.toLocaleString()}
                  </span>
                </div>

                {/* 닫기 버튼 */}
                <motion.button
                  onClick={onClose}
                  whileHover={{ scale: 1.1, rotate: 90 }}
                  whileTap={{ scale: 0.9 }}
                  className="w-8 h-8 rounded flex items-center justify-center"
                  style={{
                    background: 'linear-gradient(180deg, #5D2A2A 0%, #3D1A1A 100%)',
                    border: '2px solid #DE4A4A',
                  }}
                >
                  <X className="w-4 h-4 text-red-300" />
                </motion.button>
              </div>
            </div>

            {/* 카테고리 탭 */}
            <div
              className="flex"
              style={{
                background: 'rgba(0,0,0,0.2)',
                borderBottom: '2px solid #5C3D2E',
              }}
            >
              {categories.map(([key, config]) => {
                const isActive = activeCategory === key;
                return (
                  <motion.button
                    key={key}
                    onClick={() => setActiveCategory(key)}
                    whileHover={{ y: -2 }}
                    className="flex-1 py-3 px-2 flex items-center justify-center gap-1.5 font-bold text-sm transition-all relative"
                    style={{
                      background: isActive
                        ? 'linear-gradient(180deg, #5C3D2E 0%, #4A3628 100%)'
                        : 'transparent',
                      color: isActive ? '#E8D5B7' : '#8B7355',
                      textShadow: '0 1px 2px #000',
                    }}
                  >
                    <span style={{ color: config.color }}>{config.icon}</span>
                    <span className="hidden sm:inline">{config.label}</span>
                    {isActive && (
                      <motion.div
                        layoutId="activeTab"
                        className="absolute bottom-0 left-2 right-2 h-[3px]"
                        style={{ background: '#C9A227' }}
                      />
                    )}
                  </motion.button>
                );
              })}
            </div>

            {/* 상품 목록 */}
            <div className="p-4 overflow-y-auto max-h-[50vh] space-y-2">
              <AnimatePresence mode="popLayout">
                {filteredItems.length === 0 ? (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="text-center py-8"
                    style={{ color: '#8B7355' }}
                  >
                    이 카테고리에 아이템이 없습니다
                  </motion.div>
                ) : (
                  filteredItems.map((item, index) => {
                    const icon = ITEM_ICONS[item.code] || '📦';
                    const rarity = RARITY_CONFIG[item.rarity] || RARITY_CONFIG.common;
                    const canAfford = gold >= item.price;
                    const isOwned = item.placed > 0 || item.owned > 0;
                    const isFree = item.price === 0;
                    const atMaxQuantity = item.maxQuantity !== null && (item.owned + item.placed) >= item.maxQuantity;

                    return (
                      <motion.div
                        key={item.code}
                        layout
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: 20 }}
                        transition={{ delay: index * 0.03 }}
                        className="relative flex items-center justify-between p-3 rounded-lg"
                        style={{
                          background: isOwned
                            ? 'linear-gradient(180deg, rgba(42,93,42,0.3) 0%, rgba(26,61,26,0.3) 100%)'
                            : 'rgba(0,0,0,0.3)',
                          border: isOwned
                            ? '2px solid rgba(74,222,74,0.4)'
                            : '2px solid rgba(92,61,46,0.5)',
                          boxShadow: rarity.glow,
                        }}
                      >
                        <div className="flex items-center gap-3">
                          {/* 아이콘 프레임 */}
                          <div
                            className="w-12 h-12 rounded flex items-center justify-center text-2xl"
                            style={{
                              background: 'rgba(0,0,0,0.3)',
                              border: `2px solid ${rarity.color}`,
                              boxShadow: `inset 2px 2px 4px rgba(0,0,0,0.3), ${rarity.glow}`,
                            }}
                          >
                            {icon}
                          </div>

                          <div>
                            <p
                              className="font-bold"
                              style={{ color: '#E8D5B7', textShadow: '0 1px 2px #000' }}
                            >
                              {item.nameKo}
                            </p>
                            <div className="flex items-center gap-2 text-xs">
                              <span style={{ color: rarity.color }}>{rarity.label}</span>
                              {!isFree && (
                                <span className="inline-flex items-center gap-0.5" style={{ color: '#C9A227' }}>
                                  • <img src="/farm/icons/gold_coin.png" alt="G" className="w-3.5 h-3.5 inline-block" style={{ imageRendering: 'pixelated' }} />{item.price.toLocaleString()}
                                </span>
                              )}
                              {item.maxQuantity !== null && (
                                <span style={{ color: '#8B7355' }}>
                                  • {item.owned + item.placed}/{item.maxQuantity}
                                </span>
                              )}
                              {item.owned > 0 && (
                                <span style={{ color: '#6BB5FF' }}>
                                  • 인벤: {item.owned}
                                </span>
                              )}
                            </div>
                          </div>
                        </div>

                        {/* 버튼 영역 */}
                        <div className="flex items-center gap-2">
                          {isFree && isOwned ? (
                            <div
                              className="flex items-center gap-1 px-3 py-1.5"
                              style={{ color: '#4ADE4A' }}
                            >
                              <Check className="w-4 h-4" />
                              <span className="font-bold text-sm">기본</span>
                            </div>
                          ) : atMaxQuantity ? (
                            <div
                              className="flex items-center gap-1 px-3 py-1.5"
                              style={{ color: '#FFD700' }}
                            >
                              <Sparkles className="w-4 h-4" />
                              <span className="font-bold text-sm">최대</span>
                            </div>
                          ) : (
                            <>
                              <PixelButton
                                size="sm"
                                variant="success"
                                onClick={() => onPurchase(item.code)}
                                disabled={!canAfford || isLoading || !item.canBuy}
                              >
                                {isLoading ? '...' : '구매'}
                              </PixelButton>
                              {onPurchaseAndPlace && (
                                <PixelButton
                                  size="sm"
                                  variant="purple"
                                  onClick={() => onPurchaseAndPlace(item.code)}
                                  disabled={!canAfford || isLoading || !item.canBuy}
                                >
                                  <span className="flex items-center gap-1">
                                    <MapPin className="w-3 h-3" />
                                    배치
                                  </span>
                                </PixelButton>
                              )}
                            </>
                          )}
                        </div>
                      </motion.div>
                    );
                  })
                )}
              </AnimatePresence>
            </div>

            {/* 하단 안내 */}
            <div
              className="p-3 text-center text-sm font-medium"
              style={{
                background: 'rgba(0,0,0,0.3)',
                borderTop: '2px solid #5C3D2E',
                color: '#8B7355',
                textShadow: '0 1px 2px #000',
              }}
            >
              구매한 아이템은 인벤토리에 저장됩니다. 배치 모드에서 맵에 배치하세요.
            </div>

            {/* 하단 장식 */}
            <div className="absolute -bottom-1 left-1/2 -translate-x-1/2 flex gap-1">
              {[...Array(5)].map((_, i) => (
                <div
                  key={i}
                  className="w-2 h-2 rotate-45"
                  style={{ background: '#5C3D2E' }}
                />
              ))}
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
