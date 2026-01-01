'use client';

/**
 * ToastNotification - 우하단 토스트 알림
 * 스타듀밸리 스타일 게임 알림
 */

import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle, XCircle, Info } from 'lucide-react';
import type { Toast, ToastType } from '@/hooks/useToast';

interface ToastNotificationProps {
  toasts: Toast[];
  onDismiss: (id: string) => void;
}

// 타입별 스타일
const TOAST_STYLES: Record<ToastType, {
  bg: string;
  border: string;
  icon: React.ReactNode;
}> = {
  success: {
    bg: 'bg-green-600',
    border: 'border-green-400',
    icon: <CheckCircle className="w-5 h-5" />,
  },
  error: {
    bg: 'bg-red-600',
    border: 'border-red-400',
    icon: <XCircle className="w-5 h-5" />,
  },
  info: {
    bg: 'bg-blue-600',
    border: 'border-blue-400',
    icon: <Info className="w-5 h-5" />,
  },
};

export function ToastNotification({ toasts, onDismiss }: ToastNotificationProps) {
  return (
    <div className="fixed bottom-20 right-4 z-50 flex flex-col-reverse gap-2 pointer-events-none">
      <AnimatePresence mode="popLayout">
        {toasts.map((toast) => {
          const style = TOAST_STYLES[toast.type];

          return (
            <motion.div
              key={toast.id}
              layout
              initial={{ opacity: 0, x: 100, scale: 0.9 }}
              animate={{ opacity: 1, x: 0, scale: 1 }}
              exit={{ opacity: 0, x: 100, scale: 0.9 }}
              transition={{ type: 'spring', stiffness: 500, damping: 30 }}
              onClick={() => onDismiss(toast.id)}
              className="pointer-events-auto cursor-pointer"
            >
              <div
                className={`
                  flex items-center gap-3 px-4 py-3 rounded-xl
                  ${style.bg} ${style.border}
                  border-2 text-white font-bold
                  shadow-lg
                `}
                style={{
                  boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
                }}
              >
                {style.icon}
                <span className="text-sm">{toast.message}</span>
              </div>
            </motion.div>
          );
        })}
      </AnimatePresence>
    </div>
  );
}

export default ToastNotification;
