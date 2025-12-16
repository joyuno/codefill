import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';
import { Message, QuickChip } from '@/lib/types';
import { Bot, User } from 'lucide-react';

interface MessageBubbleProps {
  message: Message;
  onChipClick?: (chip: QuickChip) => void;
}

export function MessageBubble({ message, onChipClick }: MessageBubbleProps) {
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
          <p className="text-sm">{message.content}</p>
        </div>

        {message.chips && message.chips.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {message.chips.map((chip) => (
              <motion.button
                key={chip.value}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => onChipClick?.(chip)}
                className="rounded-full border border-border bg-card px-3 py-1.5 text-xs font-medium transition-colors hover:border-primary hover:bg-primary/10"
              >
                {chip.label}
              </motion.button>
            ))}
          </div>
        )}
      </div>
    </motion.div>
  );
}
