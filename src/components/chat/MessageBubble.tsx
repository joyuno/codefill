import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';
import { Message, QuickChip, SuggestedAction } from '@/lib/types';
import { Bot, User, Star, Sparkles, Zap, Target, BookOpen } from 'lucide-react';
import {
  SilverIcon,
  GoldIcon,
  PlatinumIcon,
  DiamondIcon,
  MasterIcon,
} from '@/components/icons/tiers';

// 난이도 value에 따른 티어 아이콘 매핑
const TIER_ICONS: Record<string, React.ComponentType<{ size?: number }>> = {
  easy: SilverIcon,
  medium: GoldIcon,
  medium_hard: PlatinumIcon,
  hard: DiamondIcon,
  very_hard: MasterIcon,
};

// 난이도 value에 따른 색상 매핑
const TIER_COLORS: Record<string, string> = {
  easy: 'text-gray-500',
  medium: 'text-amber-500',
  medium_hard: 'text-cyan-500',
  hard: 'text-violet-500',
  very_hard: 'text-rose-500',
};

/**
 * 아이콘 매핑 (suggested action value 기반)
 */
const getActionIcon = (value: string) => {
  const lower = value.toLowerCase();
  if (lower.includes('dp') || lower.includes('dynamic')) return <Zap className="h-3 w-3" />;
  if (lower.includes('graph')) return <Target className="h-3 w-3" />;
  if (lower.includes('easy') || lower.includes('beginner')) return <BookOpen className="h-3 w-3" />;
  if (lower.includes('recommend') || lower.includes('retry')) return <Star className="h-3 w-3" />;
  return <Sparkles className="h-3 w-3" />;
};

/**
 * 힌트 메시지 포맷팅 (마크다운 스타일링)
 * [라벨] 또는 **bold** 형식을 굵은 텍스트 + 색상으로 변환
 */
function formatHintContent(content: string): React.ReactNode {
  // [라벨] 또는 **bold** 패턴 찾기
  const pattern = /\[([^\]]+)\]|\*\*([^*]+)\*\*/g;
  const parts: React.ReactNode[] = [];
  let lastIndex = 0;
  let match;
  let keyIndex = 0;

  while ((match = pattern.exec(content)) !== null) {
    // 패턴 앞의 텍스트
    if (match.index > lastIndex) {
      parts.push(content.slice(lastIndex, match.index));
    }

    // [라벨] 또는 **bold** 스타일링
    const text = match[1] || match[2]; // [라벨]은 group 1, **bold**는 group 2
    parts.push(
      <span key={keyIndex++} className="font-semibold text-primary">
        {text}
      </span>
    );

    lastIndex = match.index + match[0].length;
  }

  // 나머지 텍스트
  if (lastIndex < content.length) {
    parts.push(content.slice(lastIndex));
  }

  return parts.length > 0 ? parts : content;
}

interface MessageBubbleProps {
  message: Message;
  onChipClick?: (chip: QuickChip) => void;
  onSuggestedActionClick?: (action: SuggestedAction) => void;
}

export function MessageBubble({ message, onChipClick, onSuggestedActionClick }: MessageBubbleProps) {
  const isAssistant = message.role === 'assistant';

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={cn('flex gap-3', isAssistant ? 'flex-row' : 'flex-row-reverse')}
    >
      <div
        className={cn(
          'flex h-8 w-8 shrink-0 items-center justify-center rounded-lg',
          isAssistant ? 'bg-primary' : 'bg-secondary'
        )}
      >
        {isAssistant ? (
          <Bot className="h-4 w-4 text-primary-foreground" />
        ) : (
          <User className="h-4 w-4 text-foreground" />
        )}
      </div>

      <div className={cn('max-w-[80%] space-y-2', !isAssistant && 'text-right')}>
        <div
          className={cn(
            'rounded-xl px-4 py-2.5',
            isAssistant ? 'bg-secondary' : 'bg-primary text-primary-foreground'
          )}
        >
          <p className="text-sm whitespace-pre-wrap">{formatHintContent(message.content)}</p>
        </div>

        {/* 기존 chips 렌더링 */}
        {message.chips && message.chips.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {message.chips.map((chip) => {
              // difficulty 카테고리일 때 티어 아이콘 표시
              const TierIcon = chip.category === 'difficulty' ? TIER_ICONS[chip.value] : null;
              const tierColor = chip.category === 'difficulty' ? TIER_COLORS[chip.value] : '';

              return (
                <motion.button
                  key={chip.value}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => onChipClick?.(chip)}
                  className={cn(
                    "rounded-full border border-border bg-card px-3 py-1.5 text-xs font-medium transition-colors hover:border-primary hover:bg-primary/10",
                    "flex items-center gap-1.5",
                    tierColor
                  )}
                >
                  {TierIcon && <TierIcon size={14} />}
                  {chip.label}
                </motion.button>
              );
            })}
          </div>
        )}

        {/* 🚀 Agentic 동적 선택지 렌더링 */}
        {message.suggestedActions && message.suggestedActions.length > 0 && (
          <div className="flex flex-wrap gap-2 mt-1">
            {message.suggestedActions.map((action, idx) => (
              <motion.button
                key={`${action.value}-${idx}`}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: idx * 0.05 }}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => onSuggestedActionClick?.(action)}
                className={cn(
                  "rounded-full px-3 py-1.5 text-xs font-medium transition-all",
                  "flex items-center gap-1.5",
                  action.recommended
                    ? "bg-primary text-primary-foreground hover:bg-primary/90 shadow-sm"
                    : "border border-border bg-card hover:border-primary hover:bg-primary/10"
                )}
              >
                {action.recommended && getActionIcon(action.value)}
                <span>{action.label}</span>
                {action.description && (
                  <span className={cn(
                    "text-[10px] opacity-70",
                    action.recommended ? "text-primary-foreground/70" : "text-muted-foreground"
                  )}>
                    · {action.description}
                  </span>
                )}
              </motion.button>
            ))}
          </div>
        )}
      </div>
    </motion.div>
  );
}
