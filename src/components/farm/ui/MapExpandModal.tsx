'use client';

/**
 * MapExpandModal - 맵 확장 모달
 */

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Map, X, Coins, Loader2, Check, Lock } from 'lucide-react';
import { Button } from '@/components/ui/button';
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

  // 확장 옵션 로드
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

  // 확장 실행
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
          background: 'linear-gradient(to bottom, #4A7C59 0%, #2E5339 100%)',
          border: '6px solid #1E3B28',
          boxShadow: '0 10px 40px rgba(0,0,0,0.5)',
        }}
      >
        {/* 헤더 */}
        <div
          className="p-4 flex items-center justify-between"
          style={{
            background: 'linear-gradient(to bottom, #2E5339 0%, #1E3B28 100%)',
            borderBottom: '4px solid #0F1F14',
          }}
        >
          <h2 className="text-xl font-bold text-green-200 flex items-center gap-2">
            <Map className="w-6 h-6" />
            맵 확장
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
              className="text-green-200 hover:text-white hover:bg-green-800"
            >
              <X className="w-5 h-5" />
            </Button>
          </div>
        </div>

        {/* 컨텐츠 */}
        <div className="p-4 space-y-3">
          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="w-8 h-8 text-green-200 animate-spin" />
            </div>
          ) : error ? (
            <div className="text-center py-8 text-red-300">{error}</div>
          ) : (
            options.map((option, index) => {
              const isCurrent = option.level === currentLevel;
              const isPast = option.level < currentLevel;

              // 순차적 확장: 바로 다음 단계만 확장 가능
              const currentIndex = options.findIndex(o => o.level === currentLevel);
              const isNextStep = index === currentIndex + 1;
              const isLocked = !isCurrent && !isPast && !isNextStep;

              const canUpgrade = isNextStep && gold >= option.cost;

              return (
                <div
                  key={option.level}
                  className={cn(
                    'flex items-center justify-between p-3 rounded-lg transition-all',
                    isCurrent
                      ? 'bg-green-600/50 border-2 border-green-300'
                      : isPast
                        ? 'bg-gray-700/30 border-2 border-gray-600 opacity-50'
                        : isLocked
                          ? 'bg-gray-800/40 border-2 border-gray-700 opacity-60'
                          : 'bg-black/20 border-2 border-transparent hover:border-green-500/50'
                  )}
                >
                  <div className="flex items-center gap-3">
                    {/* 맵 크기 미리보기 */}
                    <div
                      className={cn(
                        'w-12 h-8 rounded flex items-center justify-center text-xs font-bold',
                        isLocked ? 'bg-gray-800/50 text-gray-500' : 'bg-green-800/50 text-green-200'
                      )}
                    >
                      {option.cols}x{option.rows}
                    </div>

                    <div>
                      <p className={cn(
                        'font-bold',
                        isLocked ? 'text-gray-400' : 'text-green-100'
                      )}>
                        {option.name}
                        {isCurrent && (
                          <span className="ml-2 text-xs text-green-200 bg-green-700/50 px-2 py-0.5 rounded">
                            현재
                          </span>
                        )}
                        {isLocked && (
                          <span className="ml-2 text-xs text-gray-400 bg-gray-700/50 px-2 py-0.5 rounded inline-flex items-center gap-1">
                            <Lock className="w-3 h-3" />
                            잠김
                          </span>
                        )}
                      </p>
                      <p className={cn(
                        'text-sm',
                        isLocked ? 'text-gray-500' : 'text-green-300'
                      )}>
                        Lv.{option.level} - {option.cols * option.rows} 타일
                      </p>
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
                    ) : isLocked ? (
                      <div className="flex items-center gap-1 text-gray-500">
                        <Lock className="w-5 h-5" />
                      </div>
                    ) : (
                      <Button
                        size="sm"
                        onClick={() => handleExpand(option.level)}
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
          <p className="text-xs text-green-300/70 text-center">
            맵을 확장하면 더 넓은 공간에 건물과 장식을 배치할 수 있습니다
          </p>
        </div>
      </motion.div>
    </motion.div>
  );
}
