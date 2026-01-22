'use client';

/**
 * ActionPrompt - 액션 프롬프트 UI
 * 핫바 위에 표시되는 미니멀 라인 스타일
 * 현재 상호작용 가능한 액션을 보여줌
 */

import { motion, AnimatePresence } from 'framer-motion';
import { CROP_INFO, type CropVariety } from './Hotbar';
import type { InteractionState } from '../FarmGame';

interface ActionPromptProps {
  /** 현재 상호작용 상태 (null이면 숨김) */
  interaction: InteractionState | null;
  /** 현재 선택된 씨앗 코드 (seed_carrot 형식) */
  selectedSeed: string | null;
}

export function ActionPrompt({ interaction, selectedSeed }: ActionPromptProps) {
  // 표시할 내용 결정
  const getPromptContent = () => {
    if (!interaction) return null;

    const { type, cropCode, stage } = interaction;

    if (type === 'harvest' && cropCode) {
      // 수확 가능한 작물
      const cropInfo = CROP_INFO[cropCode as CropVariety];
      const cropName = cropInfo?.name || cropCode;
      const cropIcon = cropInfo?.icon;

      return {
        icon: cropIcon,
        text: `${cropName} (수확 가능)`,
        action: '수확',
        actionColor: 'text-amber-300',
        bgColor: 'from-amber-900/90 to-amber-800/90',
        borderColor: 'border-amber-600/50',
      };
    }

    if (type === 'plant' && selectedSeed) {
      // 심기 가능 (씨앗 선택됨)
      const cropCode = selectedSeed.replace('seed_', '');
      const cropInfo = CROP_INFO[cropCode as CropVariety];
      const cropName = cropInfo?.name || cropCode;
      const cropIcon = cropInfo?.icon;

      return {
        icon: cropIcon,
        text: `${cropName} 씨앗`,
        action: '심기',
        actionColor: 'text-green-300',
        bgColor: 'from-green-900/90 to-green-800/90',
        borderColor: 'border-green-600/50',
      };
    }

    return null;
  };

  const content = getPromptContent();

  return (
    <AnimatePresence>
      {content && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 10 }}
          transition={{ duration: 0.15 }}
          className="fixed bottom-24 left-1/2 -translate-x-1/2 z-40"
        >
          <div
            className={`
              flex items-center gap-3 px-4 py-2.5 rounded-lg
              bg-gradient-to-r ${content.bgColor}
              border ${content.borderColor}
              backdrop-blur-sm
              shadow-lg shadow-black/30
            `}
          >
            {/* 아이콘 */}
            {content.icon && (
              <img
                src={content.icon}
                alt=""
                className="w-6 h-6 object-contain"
                style={{ imageRendering: 'pixelated' }}
              />
            )}

            {/* 텍스트 */}
            <span className="text-white/90 text-sm font-medium">
              {content.text}
            </span>

            {/* 구분점 */}
            <span className="text-white/40">·</span>

            {/* 액션 */}
            <div className="flex items-center gap-1.5">
              <kbd
                className="
                  px-1.5 py-0.5 rounded text-xs font-bold
                  bg-white/20 text-white/90
                  border border-white/30
                "
              >
                SPACE
              </kbd>
              <span className={`text-sm font-semibold ${content.actionColor}`}>
                {content.action}
              </span>
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

export default ActionPrompt;
