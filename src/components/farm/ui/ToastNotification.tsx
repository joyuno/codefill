'use client';

/**
 * ToastNotification - 픽셀 RPG 스타일 토스트 알림
 * 우하단에 스택되는 게임 알림
 */

import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle, XCircle, Info, Sparkles } from 'lucide-react';
import type { Toast, ToastType } from '@/hooks/useToast';

interface ToastNotificationProps {
  toasts: Toast[];
  onDismiss: (id: string) => void;
}

// 타입별 스타일
const TOAST_STYLES: Record<ToastType, {
  bg: string;
  border: string;
  accent: string;
  icon: React.ReactNode;
  shadow: string;
}> = {
  success: {
    bg: 'linear-gradient(180deg, #2A5D2A 0%, #1A3D1A 100%)',
    border: '#4ADE4A',
    accent: '#90EE90',
    icon: <CheckCircle className="w-5 h-5" />,
    shadow: '0 0 20px rgba(74,222,74,0.3)',
  },
  error: {
    bg: 'linear-gradient(180deg, #5D2A2A 0%, #3D1A1A 100%)',
    border: '#DE4A4A',
    accent: '#FF6B6B',
    icon: <XCircle className="w-5 h-5" />,
    shadow: '0 0 20px rgba(222,74,74,0.3)',
  },
  info: {
    bg: 'linear-gradient(180deg, #2A3D5D 0%, #1A2A3D 100%)',
    border: '#4A8ADE',
    accent: '#6BB5FF',
    icon: <Info className="w-5 h-5" />,
    shadow: '0 0 20px rgba(74,138,222,0.3)',
  },
};

// 반짝임 이펙트 컴포넌트
function ToastSparkle({ delay = 0 }: { delay?: number }) {
  return (
    <motion.div
      className="absolute w-2 h-2"
      initial={{ scale: 0, opacity: 0 }}
      animate={{
        scale: [0, 1, 0],
        opacity: [0, 1, 0],
        rotate: [0, 180, 360],
      }}
      transition={{
        duration: 1.5,
        delay,
        repeat: Infinity,
        ease: 'easeInOut',
      }}
    >
      <Sparkles className="w-full h-full text-yellow-300" />
    </motion.div>
  );
}

export function ToastNotification({ toasts, onDismiss }: ToastNotificationProps) {
  return (
    <div className="fixed bottom-20 right-4 z-50 flex flex-col-reverse gap-2 pointer-events-none">
      <AnimatePresence mode="popLayout">
        {toasts.map((toast, index) => {
          const style = TOAST_STYLES[toast.type];

          return (
            <motion.div
              key={toast.id}
              layout
              initial={{ opacity: 0, x: 100, scale: 0.8 }}
              animate={{ opacity: 1, x: 0, scale: 1 }}
              exit={{ opacity: 0, x: 100, scale: 0.8 }}
              transition={{ type: 'spring', stiffness: 400, damping: 25 }}
              onClick={() => onDismiss(toast.id)}
              className="pointer-events-auto cursor-pointer relative"
            >
              {/* 메인 프레임 */}
              <div
                className="relative flex items-center gap-3 px-4 py-3 rounded-lg min-w-[200px]"
                style={{
                  background: style.bg,
                  border: `3px solid ${style.border}`,
                  boxShadow: `
                    inset 0 1px 0 rgba(255,255,255,0.15),
                    inset 0 -1px 0 rgba(0,0,0,0.2),
                    0 6px 16px rgba(0,0,0,0.5),
                    ${style.shadow}
                  `,
                }}
              >
                {/* 상단 장식 라인 */}
                <div
                  className="absolute top-0 left-3 right-3 h-[2px]"
                  style={{
                    background: `linear-gradient(90deg, transparent 0%, ${style.accent} 50%, transparent 100%)`,
                  }}
                />

                {/* 아이콘 */}
                <div
                  className="flex-shrink-0 w-8 h-8 rounded flex items-center justify-center"
                  style={{
                    background: 'rgba(0,0,0,0.3)',
                    border: `2px solid ${style.border}`,
                    boxShadow: 'inset 2px 2px 4px rgba(0,0,0,0.3)',
                    color: style.accent,
                  }}
                >
                  {style.icon}
                </div>

                {/* 메시지 */}
                <span
                  className="text-sm font-bold flex-1"
                  style={{
                    color: '#E8D5B7',
                    textShadow: '0 1px 2px rgba(0,0,0,0.5)',
                  }}
                >
                  {toast.message}
                </span>

                {/* 코너 장식 */}
                <div
                  className="absolute -top-1 -left-1 w-2 h-2"
                  style={{ background: style.border }}
                />
                <div
                  className="absolute -top-1 -right-1 w-2 h-2"
                  style={{ background: style.border }}
                />
                <div
                  className="absolute -bottom-1 -left-1 w-2 h-2"
                  style={{ background: style.border }}
                />
                <div
                  className="absolute -bottom-1 -right-1 w-2 h-2"
                  style={{ background: style.border }}
                />

                {/* 성공 시 반짝임 이펙트 */}
                {toast.type === 'success' && (
                  <>
                    <ToastSparkle delay={0} />
                    <ToastSparkle delay={0.5} />
                  </>
                )}
              </div>

              {/* 진행 바 (자동 dismiss 표시) */}
              <motion.div
                className="absolute bottom-0 left-1 right-1 h-[3px] rounded-full overflow-hidden"
                style={{ background: 'rgba(0,0,0,0.3)' }}
              >
                <motion.div
                  className="h-full"
                  style={{ background: style.accent }}
                  initial={{ width: '100%' }}
                  animate={{ width: '0%' }}
                  transition={{ duration: 3, ease: 'linear' }}
                />
              </motion.div>
            </motion.div>
          );
        })}
      </AnimatePresence>
    </div>
  );
}

export default ToastNotification;
