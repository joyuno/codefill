import { useState } from 'react';
import { motion } from 'framer-motion';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Button } from '@/components/ui/button';
import { HelpCircle, ChevronRight, AlertTriangle } from 'lucide-react';
import { cn } from '@/lib/utils';

interface HintPopoverProps {
  hints: string[];
  blankNumber: number;
}

export function HintPopover({ hints, blankNumber }: HintPopoverProps) {
  const [revealedLevel, setRevealedLevel] = useState(0);

  const revealNextHint = () => {
    if (revealedLevel < hints.length) {
      setRevealedLevel((prev) => prev + 1);
    }
  };

  return (
    <Popover>
      <PopoverTrigger asChild>
        <button className="inline-flex items-center justify-center rounded-full bg-secondary p-1 transition-colors hover:bg-primary/20">
          <HelpCircle className="h-4 w-4 text-muted-foreground" />
        </button>
      </PopoverTrigger>
      <PopoverContent className="w-72" align="start">
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h4 className="font-semibold">Hints for Blank #{blankNumber}</h4>
            <span className="flex items-center gap-1 text-xs text-destructive">
              <AlertTriangle className="h-3 w-3" />
              -10 XP per hint
            </span>
          </div>

          <div className="space-y-2">
            {hints.map((hint, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0 }}
                animate={{ opacity: index < revealedLevel ? 1 : 0.3 }}
                className={cn(
                  'rounded-lg border p-3 text-sm',
                  index < revealedLevel
                    ? 'border-primary/30 bg-primary/5'
                    : 'border-border bg-secondary'
                )}
              >
                <div className="flex items-center gap-2">
                  <span className="flex h-5 w-5 items-center justify-center rounded-full bg-secondary text-xs font-medium">
                    {index + 1}
                  </span>
                  <span className="text-xs text-muted-foreground">Level {index + 1} Hint</span>
                </div>
                {index < revealedLevel ? (
                  <p className="mt-2">{hint}</p>
                ) : (
                  <p className="mt-2 text-muted-foreground">Click reveal to see hint</p>
                )}
              </motion.div>
            ))}
          </div>

          {revealedLevel < hints.length && (
            <Button
              variant="outline"
              size="sm"
              className="w-full"
              onClick={revealNextHint}
            >
              <ChevronRight className="mr-1.5 h-3.5 w-3.5" />
              Reveal Level {revealedLevel + 1} Hint (-10 XP)
            </Button>
          )}
        </div>
      </PopoverContent>
    </Popover>
  );
}
