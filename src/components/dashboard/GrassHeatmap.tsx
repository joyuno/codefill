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

export function GrassHeatmap() {
  const [viewMode, setViewMode] = useState<ViewMode>('yearly');
  const activityData = useMemo(() => generateMockActivityData(365), []);

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

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="rounded-xl border border-border bg-card p-5"
    >
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-lg font-semibold">Activity</h3>
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
      </div>

      <div className="overflow-x-auto">
        <div
          className="grid gap-1"
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
                    'h-3 w-3 rounded-sm transition-transform hover:scale-125',
                    intensityColors[day.intensity]
                  )}
                />
              </TooltipTrigger>
              <TooltipContent>
                <p className="font-medium">{day.count} contributions</p>
                <p className="text-xs text-muted-foreground">{day.date}</p>
              </TooltipContent>
            </Tooltip>
          ))}
        </div>
      </div>

      <div className="mt-4 flex items-center justify-end gap-2 text-xs text-muted-foreground">
        <span>Less</span>
        {[0, 1, 2, 3, 4].map((i) => (
          <div
            key={i}
            className={cn('h-3 w-3 rounded-sm', intensityColors[i as 0 | 1 | 2 | 3 | 4])}
          />
        ))}
        <span>More</span>
      </div>
    </motion.div>
  );
}
