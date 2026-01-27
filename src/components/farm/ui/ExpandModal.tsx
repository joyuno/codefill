'use client';

/**
 * ExpandModal - 픽셀 RPG 스타일 농장 확장 모달
 */

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Expand, X, Loader2, Check, Lock } from 'lucide-react';
import { farmApi, type ExpansionOption } from '@/lib/api/farm';
import { cn } from '@/lib/utils';

interface ExpandModalProps {
  isOpen: boolean;
  onClose: () => void;
  gold: number;
  currentSize: number;
  onExpand: (targetSize: number) => Promise<void>;
}

export function ExpandModal({ isOpen, onClose, gold, currentSize, onExpand }: ExpandModalProps) {
  const [options, setOptions] = useState<ExpansionOption[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isExpanding, setIsExpanding] = useState(false);
  const [error, setError] = useState<string | null>(null);

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
            className="relative w-full max-w-md overflow-hidden rounded-lg"
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
                <Expand className="w-6 h-6" />
                농장 확장
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

            {/* 컨텐츠 */}
            <div className="p-4 space-y-2 max-h-[60vh] overflow-y-auto">
              {isLoading ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="w-8 h-8 text-amber-400 animate-spin" />
                </div>
              ) : error ? (
                <div
                  className="text-center py-8"
                  style={{ color: '#FF6B6B', textShadow: '0 1px 2px #000' }}
                >
                  {error}
                </div>
              ) : (
                options.map((option, index) => {
                  const isCurrent = option.size === currentSize;
                  const isPast = option.size < currentSize;
                  const currentIndex = options.findIndex(o => o.size === currentSize);
                  const isNextStep = index === currentIndex + 1;
                  const isLocked = !isCurrent && !isPast && !isNextStep;
                  const canUpgrade = isNextStep && gold >= option.cost;

                  return (
                    <motion.div
                      key={option.size}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.05 }}
                      className={cn(
                        'relative flex items-center justify-between p-3 rounded-lg transition-all',
                        isLocked && 'opacity-60'
                      )}
                      style={{
                        background: isCurrent
                          ? 'linear-gradient(180deg, rgba(42,93,42,0.4) 0%, rgba(26,61,26,0.4) 100%)'
                          : isPast
                          ? 'rgba(0,0,0,0.2)'
                          : 'rgba(0,0,0,0.3)',
                        border: isCurrent
                          ? '2px solid #4ADE4A'
                          : isPast
                          ? '2px solid #5C3D2E40'
                          : isLocked
                          ? '2px solid #3D2E2440'
                          : '2px solid #5C3D2E80',
                      }}
                    >
                      <div className="flex items-center gap-3">
                        {/* 그리드 미리보기 */}
                        <div
                          className="w-11 h-11 grid gap-0.5 rounded p-1"
                          style={{
                            background: isLocked ? 'rgba(0,0,0,0.3)' : 'rgba(0,0,0,0.4)',
                            border: `2px solid ${isLocked ? '#3D2E24' : '#5C3D2E'}`,
                            gridTemplateColumns: `repeat(${Math.sqrt(option.size)}, 1fr)`,
                          }}
                        >
                          {Array.from({ length: option.size }).map((_, i) => (
                            <div
                              key={i}
                              className="rounded-sm"
                              style={{
                                background: isLocked
                                  ? '#3D2E24'
                                  : isCurrent
                                  ? '#4ADE4A80'
                                  : isPast
                                  ? '#5C3D2E60'
                                  : '#C9A22780',
                              }}
                            />
                          ))}
                        </div>

                        <div>
                          <p
                            className="font-bold flex items-center gap-2"
                            style={{
                              color: isLocked ? '#6B5344' : '#E8D5B7',
                              textShadow: '0 1px 2px #000',
                            }}
                          >
                            {option.name}
                            {isCurrent && (
                              <span
                                className="text-xs px-2 py-0.5 rounded font-bold"
                                style={{
                                  background: 'rgba(74,222,74,0.3)',
                                  color: '#4ADE4A',
                                  border: '1px solid #4ADE4A60',
                                }}
                              >
                                현재
                              </span>
                            )}
                            {isLocked && (
                              <span className="flex items-center gap-1 text-xs">
                                <Lock className="w-3 h-3" />
                              </span>
                            )}
                          </p>
                          <p
                            className="text-sm"
                            style={{
                              color: isLocked ? '#5C4025' : '#8B7355',
                              textShadow: '0 1px 2px #000',
                            }}
                          >
                            {option.grid}
                          </p>
                        </div>
                      </div>

                      {/* 액션 버튼 */}
                      <div className="flex items-center gap-2">
                        {isCurrent ? (
                          <div style={{ color: '#4ADE4A' }}>
                            <Check className="w-5 h-5" />
                          </div>
                        ) : isPast ? (
                          <span
                            className="text-sm font-medium"
                            style={{ color: '#6B5344' }}
                          >
                            완료
                          </span>
                        ) : isLocked ? (
                          <Lock className="w-5 h-5" style={{ color: '#5C4025' }} />
                        ) : (
                          <motion.button
                            onClick={() => handleExpand(option.size)}
                            disabled={!canUpgrade || isExpanding}
                            whileHover={canUpgrade ? { scale: 1.03, y: -1 } : undefined}
                            whileTap={canUpgrade ? { scale: 0.97 } : undefined}
                            className={cn(
                              'px-3 py-1.5 rounded font-bold text-sm flex items-center gap-1',
                              !canUpgrade && 'opacity-50 cursor-not-allowed'
                            )}
                            style={{
                              background: canUpgrade
                                ? 'linear-gradient(180deg, #2A5D2A 0%, #1A3D1A 100%)'
                                : 'linear-gradient(180deg, #3D2A1A 0%, #2D1B0E 100%)',
                              border: `2px solid ${canUpgrade ? '#4ADE4A' : '#5C3D2E'}`,
                              color: canUpgrade ? '#90EE90' : '#6B5344',
                              textShadow: '0 1px 2px #000',
                              boxShadow: canUpgrade
                                ? 'inset 0 1px 0 rgba(255,255,255,0.1), 0 3px 6px rgba(0,0,0,0.3)'
                                : 'none',
                            }}
                          >
                            {isExpanding ? (
                              <Loader2 className="w-4 h-4 animate-spin" />
                            ) : (
                              <>
                                <img src="/farm/icons/gold_coin.png" alt="G" className="w-4 h-4" style={{ imageRendering: 'pixelated' }} />
                                {option.cost.toLocaleString()}
                              </>
                            )}
                          </motion.button>
                        )}
                      </div>
                    </motion.div>
                  );
                })
              )}
            </div>

            {/* 안내 문구 */}
            <div
              className="p-3 text-center text-sm font-medium"
              style={{
                background: 'rgba(0,0,0,0.3)',
                borderTop: '2px solid #5C3D2E',
                color: '#8B7355',
                textShadow: '0 1px 2px #000',
              }}
            >
              밭을 확장하면 더 많은 슬롯에 작물을 심을 수 있습니다
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
