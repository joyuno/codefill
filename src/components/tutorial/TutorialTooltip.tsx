'use client';

import { motion } from 'framer-motion';
import type { TooltipRenderProps } from 'react-joyride';
import { Button } from '@/components/ui/button';
import { X, ChevronLeft, ChevronRight } from 'lucide-react';

interface TutorialTooltipProps extends TooltipRenderProps {
  // 추가 props가 필요하면 여기에 정의
}

export function TutorialTooltip({
  continuous,
  index,
  step,
  size,
  backProps,
  closeProps,
  primaryProps,
  skipProps,
  tooltipProps,
  isLastStep,
}: TutorialTooltipProps) {
  const progress = ((index + 1) / size) * 100;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9, y: 10 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.9, y: 10 }}
      transition={{
        type: 'spring',
        stiffness: 300,
        damping: 25,
      }}
      {...tooltipProps}
      className="bg-card border border-border rounded-xl shadow-2xl max-w-sm overflow-hidden"
    >
      {/* Progress Bar */}
      <div className="h-1 bg-muted">
        <motion.div
          className="h-full bg-primary"
          initial={{ width: 0 }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.3 }}
        />
      </div>

      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-border">
        <span className="text-xs font-medium text-muted-foreground">
          {index + 1} / {size}
        </span>
        <button
          {...closeProps}
          className="text-muted-foreground hover:text-foreground transition-colors"
        >
          <X className="h-4 w-4" />
        </button>
      </div>

      {/* Content */}
      <div className="px-4 py-4">
        {step.title && (
          <h3 className="text-base font-semibold text-foreground mb-2">
            {step.title}
          </h3>
        )}
        <div className="text-sm text-muted-foreground leading-relaxed">
          {step.content}
        </div>
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between px-4 py-3 bg-muted/30 border-t border-border">
        <Button
          variant="ghost"
          size="sm"
          {...skipProps}
          className="text-muted-foreground hover:text-foreground text-xs"
        >
          건너뛰기
        </Button>

        <div className="flex items-center gap-2">
          {index > 0 && (
            <Button
              variant="outline"
              size="sm"
              {...backProps}
              className="h-8 px-3"
            >
              <ChevronLeft className="h-4 w-4 mr-1" />
              이전
            </Button>
          )}
          <Button
            size="sm"
            {...primaryProps}
            className="h-8 px-4"
          >
            {isLastStep ? (
              '완료'
            ) : (
              <>
                다음
                <ChevronRight className="h-4 w-4 ml-1" />
              </>
            )}
          </Button>
        </div>
      </div>
    </motion.div>
  );
}
