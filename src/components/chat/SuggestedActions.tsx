'use client';

import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Sparkles, Star, Zap, BookOpen, Target } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { SuggestedAction } from '@/lib/api/agent';

interface SuggestedActionsProps {
  actions: SuggestedAction[];
  onSelect: (action: SuggestedAction) => void;
  disabled?: boolean;
}

/**
 * 아이콘 매핑 (value 기반)
 */
const getActionIcon = (value: string) => {
  const lower = value.toLowerCase();
  if (lower.includes('dp') || lower.includes('dynamic')) return <Zap className="h-3.5 w-3.5" />;
  if (lower.includes('graph')) return <Target className="h-3.5 w-3.5" />;
  if (lower.includes('easy') || lower.includes('beginner')) return <BookOpen className="h-3.5 w-3.5" />;
  if (lower.includes('recommend') || lower.includes('retry')) return <Star className="h-3.5 w-3.5" />;
  return <Sparkles className="h-3.5 w-3.5" />;
};

/**
 * 🚀 Agentic 동적 선택지 UI
 * LLM이 생성한 개인화된 추천 버튼을 렌더링
 */
export function SuggestedActions({ actions, onSelect, disabled }: SuggestedActionsProps) {
  if (!actions || actions.length === 0) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      className="flex flex-wrap gap-2 mt-3"
    >
      {actions.map((action, index) => (
        <motion.div
          key={`${action.value}-${index}`}
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: index * 0.05 }}
        >
          <Button
            variant={action.recommended ? "default" : "outline"}
            size="sm"
            className={cn(
              "gap-1.5 transition-all",
              action.recommended && "bg-primary/90 hover:bg-primary shadow-sm",
              action.description && "flex-col h-auto py-2 px-3"
            )}
            onClick={() => onSelect(action)}
            disabled={disabled}
          >
            <div className="flex items-center gap-1.5">
              {action.recommended && getActionIcon(action.value)}
              <span className={cn(
                "text-sm",
                action.recommended && "font-medium"
              )}>
                {action.label}
              </span>
              {action.recommended && (
                <Badge
                  variant="secondary"
                  className="ml-1 px-1.5 py-0 text-[10px] bg-white/20 text-white"
                >
                  추천
                </Badge>
              )}
            </div>
            {action.description && (
              <span className={cn(
                "text-[11px] opacity-70",
                action.recommended ? "text-white/80" : "text-muted-foreground"
              )}>
                {action.description}
              </span>
            )}
          </Button>
        </motion.div>
      ))}
    </motion.div>
  );
}

/**
 * 메시지 버블 내에서 사용하는 인라인 버전
 */
export function InlineSuggestedActions({ actions, onSelect, disabled }: SuggestedActionsProps) {
  if (!actions || actions.length === 0) return null;

  return (
    <div className="flex flex-wrap gap-1.5 mt-2 pt-2 border-t border-border/50">
      {actions.map((action, index) => (
        <button
          key={`${action.value}-${index}`}
          className={cn(
            "inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium transition-colors",
            action.recommended
              ? "bg-primary text-primary-foreground hover:bg-primary/90"
              : "bg-muted hover:bg-muted/80 text-foreground"
          )}
          onClick={() => onSelect(action)}
          disabled={disabled}
        >
          {action.recommended && <Star className="h-3 w-3" />}
          {action.label}
        </button>
      ))}
    </div>
  );
}
