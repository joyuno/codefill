'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { Gift, Coins, Sparkles, X, ArrowRight } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface WelcomeModalProps {
  open: boolean;
  onClose: () => void;
  username?: string;
}

export function WelcomeModal({ open, onClose, username }: WelcomeModalProps) {
  return (
    <AnimatePresence>
      {open && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm"
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            transition={{ type: 'spring', duration: 0.5 }}
            className="fixed left-1/2 top-1/2 z-50 w-full max-w-sm -translate-x-1/2 -translate-y-1/2 p-4"
          >
            <div className="relative overflow-hidden rounded-2xl bg-card border border-border shadow-2xl">
              {/* Close button */}
              <button
                onClick={onClose}
                className="absolute right-3 top-3 z-10 p-1 rounded-full hover:bg-secondary transition-colors"
              >
                <X className="h-4 w-4 text-muted-foreground" />
              </button>

              {/* Background decoration */}
              <div className="absolute inset-0 overflow-hidden">
                <div className="absolute -top-20 -right-20 w-40 h-40 bg-amber-500/20 rounded-full blur-3xl" />
                <div className="absolute -bottom-20 -left-20 w-40 h-40 bg-violet-500/20 rounded-full blur-3xl" />
              </div>

              {/* Content */}
              <div className="relative p-6 text-center">
                {/* Gift icon with animation */}
                <motion.div
                  initial={{ scale: 0, rotate: -20 }}
                  animate={{ scale: 1, rotate: 0 }}
                  transition={{ type: 'spring', delay: 0.2, duration: 0.6 }}
                  className="mx-auto mb-4 w-20 h-20 rounded-2xl bg-gradient-to-br from-amber-500 to-orange-500 flex items-center justify-center shadow-lg shadow-amber-500/30"
                >
                  <Gift className="h-10 w-10 text-white" />
                </motion.div>

                {/* Welcome text */}
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3 }}
                >
                  <h2 className="text-xl font-bold mb-1">
                    환영합니다{username ? `, ${username}님` : ''}! 🎉
                  </h2>
                  <p className="text-sm text-muted-foreground">
                    CodeFill과 함께 코딩 실력을 키워보세요
                  </p>
                </motion.div>

                {/* Credit gift box */}
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.4 }}
                  className="mt-6 p-4 rounded-xl bg-gradient-to-r from-amber-500/10 to-orange-500/10 border border-amber-500/20"
                >
                  <div className="flex items-center justify-center gap-2 mb-2">
                    <Sparkles className="h-4 w-4 text-amber-500" />
                    <span className="text-sm font-medium text-amber-600 dark:text-amber-400">
                      가입 축하 선물
                    </span>
                  </div>
                  <div className="flex items-center justify-center gap-2">
                    <Coins className="h-6 w-6 text-amber-500" />
                    <span className="text-3xl font-bold bg-gradient-to-r from-amber-500 to-orange-500 bg-clip-text text-transparent">
                      10,000
                    </span>
                    <span className="text-lg font-medium text-muted-foreground">크레딧</span>
                  </div>
                  <p className="mt-2 text-xs text-muted-foreground">
                    AI 문제 생성에 사용할 수 있어요
                  </p>
                </motion.div>

                {/* Info list */}
                <motion.ul
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.5 }}
                  className="mt-4 text-left text-sm text-muted-foreground space-y-1.5"
                >
                  <li className="flex items-start gap-2">
                    <span className="text-amber-500">•</span>
                    <span>문제 1개 생성 시 <strong className="text-foreground">10 크레딧</strong> 사용</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-amber-500">•</span>
                    <span>구현 문제는 <strong className="text-foreground">무료</strong>로 이용 가능</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-amber-500">•</span>
                    <span>크레딧은 언제든 충전할 수 있어요</span>
                  </li>
                </motion.ul>

                {/* CTA Button */}
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.6 }}
                  className="mt-6"
                >
                  <Button
                    onClick={onClose}
                    className="w-full bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 text-white"
                  >
                    시작하기
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                </motion.div>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
