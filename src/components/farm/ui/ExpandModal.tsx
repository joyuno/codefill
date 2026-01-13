'use client';

/**
 * ExpandModal - 농장 확장 모달
 */

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Expand, X, Coins, Loader2, Check } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { farmApi, type ExpansionOption } from '@/lib/api/farm';
import { cn } from '@/lib/utils';

interface ExpandModalProps {
  isOpen: boolean;
  onClose: () => void;
  gold: number;
  currentSize: number; // 밭 슬롯 개수 (1, 4, 9, 16, 25)
  onExpand: (targetSize: number) => Promise<void>;
}

export function ExpandModal({ isOpen, onClose, gold, currentSize, onExpand }: ExpandModalProps) {
  const [options, setOptions] = useState<ExpansionOption[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isExpanding, setIsExpanding] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 확장 옵션 로드
  useEffect(() => {
    if (!isOpen) return;

    const loadOptions = async () => {
      try {
        setIsLoading(true);
        setError(null);
        const data = await farmApi.getExpansionCosts();
        setOptions(data.options);
      } catch (err) {
        setError('확장 정보를 불러오는데 실패했습니다');
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };

    loadOptions();
  }, [isOpen]);

  // 확장 실행
  const handleExpand = async (targetSize: number) => {
    try {
      setIsExpanding(true);
      setError(null);
      await onExpand(targetSize);
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : '확장에 실패했습니다');
    } finally {
      setIsExpanding(false);
    }
  };

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
        className="w-full max-w-md overflow-hidden rounded-2xl"
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
            <Expand className="w-6 h-6" />
            농장 확장
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

        {/* 컨텐츠 */}
        <div className="p-4 space-y-3">
          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="w-8 h-8 text-amber-200 animate-spin" />
            </div>
          ) : error ? (
            <div className="text-center py-8 text-red-300">{error}</div>
          ) : (
            options.map(option => {
              const isCurrent = option.size === currentSize;
              const canUpgrade = !isCurrent && gold >= option.cost;
              const isPast = option.size < currentSize;

              return (
                <div
                  key={option.size}
                  className={cn(
                    'flex items-center justify-between p-3 rounded-lg transition-all',
                    isCurrent
                      ? 'bg-green-700/50 border-2 border-green-400'
                      : isPast
                        ? 'bg-gray-700/30 border-2 border-gray-600 opacity-50'
                        : 'bg-black/20 border-2 border-transparent hover:border-amber-600/50'
                  )}
                >
                  <div className="flex items-center gap-3">
                    {/* 그리드 미리보기 */}
                    <div
                      className="w-10 h-10 grid gap-0.5 bg-amber-900/50 rounded p-1"
                      style={{
                        gridTemplateColumns: `repeat(${Math.sqrt(option.size)}, 1fr)`,
                      }}
                    >
                      {Array.from({ length: option.size }).map((_, i) => (
                        <div key={i} className="bg-amber-600/80 rounded-sm" />
                      ))}
                    </div>

                    <div>
                      <p className="font-bold text-amber-100">
                        {option.name}
                        {isCurrent && (
                          <span className="ml-2 text-xs text-green-300 bg-green-800/50 px-2 py-0.5 rounded">
                            현재
                          </span>
                        )}
                      </p>
                      <p className="text-sm text-amber-300">{option.grid}</p>
                    </div>
                  </div>

                  {/* 액션 버튼 */}
                  <div className="flex items-center gap-2">
                    {isCurrent ? (
                      <div className="flex items-center gap-1 text-green-300">
                        <Check className="w-5 h-5" />
                      </div>
                    ) : isPast ? (
                      <span className="text-gray-400 text-sm">완료</span>
                    ) : (
                      <Button
                        size="sm"
                        onClick={() => handleExpand(option.size)}
                        disabled={!canUpgrade || isExpanding}
                        className={cn(
                          'border-2 font-bold',
                          canUpgrade
                            ? 'bg-green-600 hover:bg-green-500 text-white border-green-400'
                            : 'bg-gray-600 text-gray-300 border-gray-500 cursor-not-allowed'
                        )}
                      >
                        {isExpanding ? (
                          <Loader2 className="w-4 h-4 animate-spin" />
                        ) : (
                          <>
                            <Coins className="w-4 h-4 mr-1" />
                            {option.cost.toLocaleString()}G
                          </>
                        )}
                      </Button>
                    )}
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* 안내 문구 */}
        <div className="p-4 pt-0">
          <p className="text-xs text-amber-300/70 text-center">
            밭을 확장하면 더 많은 슬롯에 작물을 심을 수 있습니다
          </p>
        </div>
      </motion.div>
    </motion.div>
  );
}
