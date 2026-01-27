'use client';

/**
 * MapExpandModal - 픽셀 RPG 스타일 맵 확장 모달
 */

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Map, X, Loader2, Check, Lock } from 'lucide-react';
import { farmApi, type MapExpansionOption } from '@/lib/api/farm';
import { cn } from '@/lib/utils';

interface MapExpandModalProps {
  isOpen: boolean;
  onClose: () => void;
  gold: number;
  currentLevel: number;
  onExpand: (targetLevel: number) => Promise<void>;
}

export function MapExpandModal({ isOpen, onClose, gold, currentLevel, onExpand }: MapExpandModalProps) {
  const [options, setOptions] = useState<MapExpansionOption[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isExpanding, setIsExpanding] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isOpen) return;

    const loadOptions = async () => {
      try {
        setIsLoading(true);
        setError(null);
        const data = await farmApi.getMapExpansionCosts();
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

  const handleExpand = async (targetLevel: number) => {
    try {
      setIsExpanding(true);
      setError(null);
      await onExpand(targetLevel);
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
              background: 'linear-gradient(180deg, #1A3D3D 0%, #0F2A2A 100%)',
              border: '4px solid #2A5D5D',
              boxShadow: `
                inset 0 2px 0 #3D6B6B,
                inset 0 -2px 0 #0A1F1F,
                0 12px 40px rgba(0,0,0,0.7)
              `,
            }}
          >
            {/* 상단 장식 라인 */}
            <div
              className="absolute top-0 left-6 right-6 h-[2px]"
              style={{
                background: 'linear-gradient(90deg, transparent 0%, #4ADEDE 50%, transparent 100%)',
              }}
            />

            {/* 코너 장식 */}
            <div className="absolute -top-1 -left-1 w-4 h-4" style={{ background: '#2A5D5D' }} />
            <div className="absolute -top-1 -right-1 w-4 h-4" style={{ background: '#2A5D5D' }} />
            <div className="absolute -bottom-1 -left-1 w-4 h-4" style={{ background: '#2A5D5D' }} />
            <div className="absolute -bottom-1 -right-1 w-4 h-4" style={{ background: '#2A5D5D' }} />

            {/* 헤더 */}
            <div
              className="relative p-4 flex items-center justify-between"
              style={{
                background: 'linear-gradient(180deg, #2A4A4A 0%, #1A3D3D 100%)',
                borderBottom: '3px solid #2A5D5D',
              }}
            >
              <h2
                className="text-xl font-black flex items-center gap-2"
                style={{
                  color: '#4ADEDE',
                  textShadow: '0 2px 4px rgba(0,0,0,0.8), 0 0 10px rgba(74,222,222,0.3)',
                }}
              >
                <Map className="w-6 h-6" />
                맵 확장
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
                  <Loader2 className="w-8 h-8 text-cyan-400 animate-spin" />
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
                  const isCurrent = option.level === currentLevel;
                  const isPast = option.level < currentLevel;
                  const currentIndex = options.findIndex(o => o.level === currentLevel);
                  const isNextStep = index === currentIndex + 1;
                  const isLocked = !isCurrent && !isPast && !isNextStep;
                  const canUpgrade = isNextStep && gold >= option.cost;

                  return (
                    <motion.div
                      key={option.level}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.05 }}
                      className={cn(
                        'relative flex items-center justify-between p-3 rounded-lg transition-all',
                        isLocked && 'opacity-60'
                      )}
                      style={{
                        background: isCurrent
                          ? 'linear-gradient(180deg, rgba(42,93,93,0.4) 0%, rgba(26,61,61,0.4) 100%)'
                          : isPast
                          ? 'rgba(0,0,0,0.2)'
                          : 'rgba(0,0,0,0.3)',
                        border: isCurrent
                          ? '2px solid #4ADEDE'
                          : isPast
                          ? '2px solid #2A5D5D40'
                          : isLocked
                          ? '2px solid #1A3D3D40'
                          : '2px solid #2A5D5D80',
                      }}
                    >
                      <div className="flex items-center gap-3">
                        {/* 맵 크기 미리보기 */}
                        <div
                          className="w-14 h-10 rounded flex items-center justify-center font-black text-sm"
                          style={{
                            background: isLocked ? 'rgba(0,0,0,0.3)' : 'rgba(0,0,0,0.4)',
                            border: `2px solid ${isLocked ? '#1A3D3D' : '#2A5D5D'}`,
                            color: isLocked ? '#2A5D5D' : isCurrent ? '#4ADEDE' : '#5BAEAE',
                            textShadow: '0 1px 2px #000',
                          }}
                        >
                          {option.cols}x{option.rows}
                        </div>

                        <div>
                          <p
                            className="font-bold flex items-center gap-2"
                            style={{
                              color: isLocked ? '#3D6B6B' : '#B8E8E8',
                              textShadow: '0 1px 2px #000',
                            }}
                          >
                            {option.name}
                            {isCurrent && (
                              <span
                                className="text-xs px-2 py-0.5 rounded font-bold"
                                style={{
                                  background: 'rgba(74,222,222,0.3)',
                                  color: '#4ADEDE',
                                  border: '1px solid #4ADEDE60',
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
                              color: isLocked ? '#2A5D5D' : '#5BAEAE',
                              textShadow: '0 1px 2px #000',
                            }}
                          >
                            Lv.{option.level} - {option.cols * option.rows} 타일
                          </p>
                        </div>
                      </div>

                      {/* 액션 버튼 */}
                      <div className="flex items-center gap-2">
                        {isCurrent ? (
                          <div style={{ color: '#4ADEDE' }}>
                            <Check className="w-5 h-5" />
                          </div>
                        ) : isPast ? (
                          <span
                            className="text-sm font-medium"
                            style={{ color: '#3D6B6B' }}
                          >
                            완료
                          </span>
                        ) : isLocked ? (
                          <Lock className="w-5 h-5" style={{ color: '#2A5D5D' }} />
                        ) : (
                          <motion.button
                            onClick={() => handleExpand(option.level)}
                            disabled={!canUpgrade || isExpanding}
                            whileHover={canUpgrade ? { scale: 1.03, y: -1 } : undefined}
                            whileTap={canUpgrade ? { scale: 0.97 } : undefined}
                            className={cn(
                              'px-3 py-1.5 rounded font-bold text-sm flex items-center gap-1',
                              !canUpgrade && 'opacity-50 cursor-not-allowed'
                            )}
                            style={{
                              background: canUpgrade
                                ? 'linear-gradient(180deg, #2A5D5D 0%, #1A3D3D 100%)'
                                : 'linear-gradient(180deg, #1A3D3D 0%, #0F2A2A 100%)',
                              border: `2px solid ${canUpgrade ? '#4ADEDE' : '#2A5D5D'}`,
                              color: canUpgrade ? '#90EEEE' : '#3D6B6B',
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
                borderTop: '2px solid #2A5D5D',
                color: '#5BAEAE',
                textShadow: '0 1px 2px #000',
              }}
            >
              맵을 확장하면 더 넓은 공간에 건물과 장식을 배치할 수 있습니다
            </div>

            {/* 하단 장식 */}
            <div className="absolute -bottom-1 left-1/2 -translate-x-1/2 flex gap-1">
              {[...Array(5)].map((_, i) => (
                <div
                  key={i}
                  className="w-2 h-2 rotate-45"
                  style={{ background: '#2A5D5D' }}
                />
              ))}
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
