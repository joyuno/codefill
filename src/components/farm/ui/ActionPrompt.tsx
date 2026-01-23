'use client';

/**
 * ActionPrompt - 픽셀 RPG 스타일 말풍선 액션 프롬프트
 * 핫바 위에 표시되는 말풍선 UI
 */

import { motion, AnimatePresence } from 'framer-motion';
import { CROP_INFO, type CropVariety } from './Hotbar';
import type { InteractionState } from '../FarmGame';

interface ActionPromptProps {
  interaction: InteractionState | null;
  selectedSeed: string | null;
}

export function ActionPrompt({ interaction, selectedSeed }: ActionPromptProps) {
  const getPromptContent = () => {
    if (!interaction) return null;

    const { type, cropCode } = interaction;

    if (type === 'harvest' && cropCode) {
      const cropInfo = CROP_INFO[cropCode as CropVariety];
      const cropName = cropInfo?.name || cropCode;
      const cropIcon = cropInfo?.icon;

      return {
        icon: cropIcon,
        text: cropName,
        subtext: '수확 가능',
        action: '수확',
        theme: 'harvest',
      };
    }

    if (type === 'plant' && selectedSeed) {
      const seedCropCode = selectedSeed.replace('seed_', '');
      const cropInfo = CROP_INFO[seedCropCode as CropVariety];
      const cropName = cropInfo?.name || seedCropCode;
      const cropIcon = cropInfo?.icon;

      return {
        icon: cropIcon,
        text: `${cropName} 씨앗`,
        subtext: '심기 가능',
        action: '심기',
        theme: 'plant',
      };
    }

    return null;
  };

  const content = getPromptContent();

  // 테마별 색상
  const themeColors = {
    harvest: {
      bg: 'linear-gradient(180deg, #5C4025 0%, #3D2A1A 100%)',
      border: '#C9A227',
      accent: '#FFD700',
      textShadow: '0 1px 2px #2A1F14',
    },
    plant: {
      bg: 'linear-gradient(180deg, #2A5D2A 0%, #1A3D1A 100%)',
      border: '#4ADE4A',
      accent: '#90EE90',
      textShadow: '0 1px 2px #0A200A',
    },
  };

  const colors = content ? themeColors[content.theme as keyof typeof themeColors] : themeColors.harvest;

  return (
    <AnimatePresence>
      {content && (
        <motion.div
          initial={{ opacity: 0, y: 15, scale: 0.9 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: 15, scale: 0.9 }}
          transition={{ type: 'spring', stiffness: 400, damping: 25 }}
          className="fixed bottom-24 left-1/2 -translate-x-1/2 z-40"
        >
          {/* 말풍선 본체 */}
          <div className="relative">
            {/* 메인 프레임 */}
            <div
              className="relative px-5 py-3 rounded-lg"
              style={{
                background: colors.bg,
                border: `3px solid ${colors.border}`,
                boxShadow: `
                  inset 0 1px 0 rgba(255,255,255,0.1),
                  inset 0 -1px 0 rgba(0,0,0,0.2),
                  0 6px 16px rgba(0,0,0,0.5)
                `,
              }}
            >
              {/* 상단 장식 라인 */}
              <div
                className="absolute top-0 left-4 right-4 h-[2px]"
                style={{
                  background: `linear-gradient(90deg, transparent 0%, ${colors.accent} 50%, transparent 100%)`,
                }}
              />

              {/* 컨텐츠 */}
              <div className="flex items-center gap-3">
                {/* 아이콘 프레임 */}
                {content.icon && (
                  <div
                    className="w-10 h-10 rounded flex items-center justify-center"
                    style={{
                      background: 'rgba(0,0,0,0.3)',
                      border: `2px solid ${colors.border}`,
                      boxShadow: 'inset 2px 2px 4px rgba(0,0,0,0.3)',
                    }}
                  >
                    <img
                      src={content.icon}
                      alt=""
                      className="w-7 h-7 object-contain drop-shadow-[0_2px_2px_rgba(0,0,0,0.5)]"
                      style={{ imageRendering: 'pixelated' }}
                    />
                  </div>
                )}

                {/* 텍스트 영역 */}
                <div className="flex flex-col">
                  <span
                    className="text-sm font-bold"
                    style={{
                      color: '#E8D5B7',
                      textShadow: colors.textShadow,
                    }}
                  >
                    {content.text}
                  </span>
                  <span
                    className="text-xs font-medium"
                    style={{
                      color: colors.accent,
                      textShadow: colors.textShadow,
                    }}
                  >
                    {content.subtext}
                  </span>
                </div>

                {/* 구분선 */}
                <div
                  className="w-[2px] h-8"
                  style={{
                    background: `linear-gradient(180deg, transparent 0%, ${colors.border} 20%, ${colors.border} 80%, transparent 100%)`,
                  }}
                />

                {/* 액션 버튼 */}
                <div className="flex items-center gap-2">
                  <kbd
                    className="px-2 py-1 rounded text-xs font-black"
                    style={{
                      background: 'linear-gradient(180deg, #2D1B0E 0%, #1A0F08 100%)',
                      border: '2px solid #5C3D2E',
                      color: '#C9A227',
                      textShadow: '0 1px 2px #000',
                      boxShadow: 'inset 0 1px 0 #3D2A1A, 0 2px 4px rgba(0,0,0,0.3)',
                    }}
                  >
                    SPACE
                  </kbd>
                  <span
                    className="text-sm font-black"
                    style={{
                      color: colors.accent,
                      textShadow: `0 0 8px ${colors.accent}40, ${colors.textShadow}`,
                    }}
                  >
                    {content.action}
                  </span>
                </div>
              </div>

              {/* 코너 장식 */}
              <div
                className="absolute -top-1 -left-1 w-2 h-2"
                style={{ background: colors.border }}
              />
              <div
                className="absolute -top-1 -right-1 w-2 h-2"
                style={{ background: colors.border }}
              />
              <div
                className="absolute -bottom-1 -left-1 w-2 h-2"
                style={{ background: colors.border }}
              />
              <div
                className="absolute -bottom-1 -right-1 w-2 h-2"
                style={{ background: colors.border }}
              />
            </div>

            {/* 말풍선 꼬리 (아래쪽 삼각형) */}
            <div className="absolute left-1/2 -translate-x-1/2 -bottom-3">
              <div
                className="w-4 h-4 rotate-45"
                style={{
                  background: colors.bg.includes('5C4025') ? '#3D2A1A' : '#1A3D1A',
                  border: `3px solid ${colors.border}`,
                  borderTop: 'none',
                  borderLeft: 'none',
                }}
              />
            </div>
          </div>

          {/* 펄스 이펙트 */}
          <motion.div
            className="absolute inset-0 rounded-lg pointer-events-none"
            animate={{
              boxShadow: [
                `0 0 0 0 ${colors.accent}00`,
                `0 0 0 8px ${colors.accent}30`,
                `0 0 0 0 ${colors.accent}00`,
              ],
            }}
            transition={{ duration: 2, repeat: Infinity }}
          />
        </motion.div>
      )}
    </AnimatePresence>
  );
}

export default ActionPrompt;
