'use client';

/**
 * ShopModal - 씨앗 상점 모달
 */

import { motion } from 'framer-motion';
import { ShoppingBag, X, Coins } from 'lucide-react';
import { Button } from '@/components/ui/button';
import type { FarmItem } from '@/lib/api/farm';
import { CROP_INFO, ALL_CROPS, type CropVariety } from './Hotbar';

interface ShopModalProps {
  isOpen: boolean;
  onClose: () => void;
  items: FarmItem[];
  gold: number;
  onBuy: (cropCode: CropVariety, quantity: number) => void;
}

export function ShopModal({ isOpen, onClose, items, gold, onBuy }: ShopModalProps) {
  if (!isOpen) return null;

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
            <ShoppingBag className="w-6 h-6" />
            씨앗 상점
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

        {/* 상품 목록 - ALL_CROPS 순서로 정렬 */}
        <div className="p-4 overflow-y-auto max-h-[60vh] space-y-3">
          {ALL_CROPS.map(cropCode => {
            const item = items.find(i => i.code === cropCode && i.type === 'crop');
            if (!item) return null;
            const info = CROP_INFO[cropCode];

            return (
              <div
                key={item.code}
                className="flex items-center justify-between p-3 rounded-lg"
                style={{
                  background: 'rgba(0,0,0,0.2)',
                  border: '2px solid rgba(255,255,255,0.1)',
                }}
              >
                <div className="flex items-center gap-3">
                  <span className="text-2xl">{info.emoji}</span>
                  <div>
                    <p className="font-bold text-amber-100">{info.name} 씨앗</p>
                    <p className="text-sm text-amber-300">{item.seedCost}G / 개</p>
                  </div>
                </div>
                <div className="flex gap-2">
                  <Button
                    size="sm"
                    onClick={() => onBuy(cropCode, 1)}
                    disabled={gold < item.seedCost}
                    className="bg-green-600 hover:bg-green-500 text-white border-2 border-green-400"
                  >
                    1개
                  </Button>
                  <Button
                    size="sm"
                    onClick={() => onBuy(cropCode, 5)}
                    disabled={gold < item.seedCost * 5}
                    className="bg-green-600 hover:bg-green-500 text-white border-2 border-green-400"
                  >
                    5개
                  </Button>
                </div>
              </div>
            );
          })}
        </div>
      </motion.div>
    </motion.div>
  );
}
