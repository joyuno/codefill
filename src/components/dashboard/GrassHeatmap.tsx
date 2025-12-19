import { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import { generateMockActivityData } from '@/lib/mockData';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';
import { cn } from '@/lib/utils';

type ViewMode = 'daily' | 'weekly' | 'yearly';

const intensityColors = {
  0: 'bg-grass-0',
  1: 'bg-grass-1',
  2: 'bg-grass-2',
  3: 'bg-grass-3',
  4: 'bg-grass-4',
};

interface GrassHeatmapProps {
  compact?: boolean;
}

export function GrassHeatmap({ compact = false }: GrassHeatmapProps) {
  const [viewMode, setViewMode] = useState<ViewMode>(compact ? 'weekly' : 'yearly');
  const activityData = useMemo(() => generateMockActivityData(compact ? 90 : 365), [compact]);

  const getDisplayData = () => {
    switch (viewMode) {
      case 'daily':
        return activityData.slice(-7);
      case 'weekly':
        return activityData.slice(-28);
      case 'yearly':
      default:
        return activityData;
    }
  };

  const displayData = getDisplayData();
  const weeks = Math.ceil(displayData.length / 7);

  // For compact mode, calculate total contributions
  const totalContributions = displayData.reduce((sum, day) => sum + day.count, 0);
  const streak = displayData.filter(day => day.count > 0).length;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className={cn(
        "rounded-xl border border-border bg-card",
        compact ? "p-4" : "p-5"
      )}
    >
      <div className={cn("flex items-center justify-between", compact ? "mb-3" : "mb-4")}>
        <div>
          <h3 className={cn("font-semibold", compact ? "text-sm" : "text-lg")}>
            {compact ? '학습 활동' : 'Activity'}
          </h3>
          {compact && (
            <p className="text-xs text-muted-foreground mt-0.5">
              최근 {streak}일 연속 학습
            </p>
          )}
        </div>
        {!compact && (
          <div className="flex rounded-lg bg-secondary p-1">
            {(['daily', 'weekly', 'yearly'] as ViewMode[]).map((mode) => (
              <button
                key={mode}
                onClick={() => setViewMode(mode)}
                className={cn(
                  'rounded-md px-3 py-1.5 text-xs font-medium capitalize transition-colors',
                  viewMode === mode
                    ? 'bg-primary text-primary-foreground'
                    : 'text-muted-foreground hover:text-foreground'
                )}
              >
                {mode}
              </button>
            ))}
          </div>
        )}
      </div>

      <div className="overflow-x-auto">
        <div
          className={cn("grid", compact ? "gap-0.5" : "gap-1")}
          style={{
            gridTemplateColumns: `repeat(${weeks}, minmax(0, 1fr))`,
            gridTemplateRows: 'repeat(7, minmax(0, 1fr))',
          }}
        >
          {displayData.map((day, index) => (
            <Tooltip key={day.date}>
              <TooltipTrigger asChild>
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: index * 0.002 }}
                  className={cn(
                    'rounded-sm transition-transform hover:scale-125',
                    compact ? 'h-2.5 w-2.5' : 'h-3 w-3',
                    intensityColors[day.intensity]
                  )}
                />
              </TooltipTrigger>
              <TooltipContent>
                <p className="font-medium">{day.count} 문제 해결</p>
                <p className="text-xs text-muted-foreground">{day.date}</p>
              </TooltipContent>
            </Tooltip>
          ))}
        </div>
      </div>

      <div className={cn(
        "flex items-center justify-between text-xs text-muted-foreground",
        compact ? "mt-3" : "mt-4"
      )}>
        {compact ? (
          <span>총 {totalContributions}문제</span>
        ) : (
          <span />
        )}
        <div className="flex items-center gap-2">
          <span>Less</span>
          {[0, 1, 2, 3, 4].map((i) => (
            <div
              key={i}
              className={cn(
                'rounded-sm',
                compact ? 'h-2.5 w-2.5' : 'h-3 w-3',
                intensityColors[i as 0 | 1 | 2 | 3 | 4]
              )}
            />
          ))}
          <span>More</span>
        </div>
      </div>
    </motion.div>
  );
}
