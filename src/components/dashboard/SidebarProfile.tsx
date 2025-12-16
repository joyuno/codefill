import { motion } from 'framer-motion';
import { Progress } from '@/components/ui/progress';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';
import { mockUser, mockBadges } from '@/lib/mockData';
import { useState } from 'react';
import { Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';

const avatarShapes = {
  hexagon: 'polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%)',
  circle: 'circle(50% at 50% 50%)',
  diamond: 'polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%)',
  pentagon: 'polygon(50% 0%, 100% 38%, 82% 100%, 18% 100%, 0% 38%)',
};

export function SidebarProfile() {
  const [isLevelingUp, setIsLevelingUp] = useState(false);
  const xpProgress = (mockUser.currentXP / mockUser.requiredXP) * 100;

  const handleLevelUp = () => {
    setIsLevelingUp(true);
    setTimeout(() => setIsLevelingUp(false), 600);
  };

  return (
    <div className="space-y-6 p-4">
      {/* Avatar Card */}
      <div className="rounded-xl border border-border bg-card p-4">
        <div className="flex flex-col items-center gap-4">
          <motion.div
            animate={isLevelingUp ? { scale: [1, 1.2, 1], filter: ['brightness(1)', 'brightness(1.5)', 'brightness(1)'] } : {}}
            transition={{ duration: 0.6 }}
            className="relative"
          >
            <div
              className="flex h-24 w-24 items-center justify-center bg-gradient-to-br from-primary/80 to-primary"
              style={{ clipPath: avatarShapes[mockUser.avatarShape] }}
            >
              <span className="text-3xl font-bold text-primary-foreground">
                {mockUser.username.slice(0, 2).toUpperCase()}
              </span>
            </div>
            {isLevelingUp && (
              <motion.div
                initial={{ scale: 0, opacity: 0 }}
                animate={{ scale: 2, opacity: [0, 1, 0] }}
                transition={{ duration: 0.6 }}
                className="absolute inset-0 flex items-center justify-center"
              >
                <Sparkles className="h-12 w-12 text-primary" />
              </motion.div>
            )}
          </motion.div>

          <div className="text-center">
            <h3 className="font-semibold">{mockUser.username}</h3>
            <p className="text-sm text-muted-foreground">@{mockUser.username.toLowerCase()}</p>
          </div>

          <Button
            variant="outline"
            size="sm"
            onClick={handleLevelUp}
            className="w-full"
          >
            <Sparkles className="mr-2 h-4 w-4" />
            Preview Level Up
          </Button>
        </div>
      </div>

      {/* Level & XP */}
      <div className="rounded-xl border border-border bg-card p-4">
        <div className="mb-3 flex items-center justify-between">
          <span className="text-2xl font-bold text-primary">Lv.{mockUser.level}</span>
          <span className="text-sm text-muted-foreground">
            {mockUser.currentXP.toLocaleString()} / {mockUser.requiredXP.toLocaleString()} XP
          </span>
        </div>
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: '100%' }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <Progress value={xpProgress} className="h-3" />
        </motion.div>
        <p className="mt-2 text-xs text-muted-foreground">
          {mockUser.requiredXP - mockUser.currentXP} XP to next level
        </p>
      </div>

      {/* Badges */}
      <div className="rounded-xl border border-border bg-card p-4">
        <h4 className="mb-3 text-sm font-medium text-muted-foreground">Badges</h4>
        <div className="flex flex-wrap gap-2">
          {mockBadges.slice(0, 5).map((badge) => (
            <Tooltip key={badge.id}>
              <TooltipTrigger asChild>
                <motion.div
                  whileHover={{ scale: 1.1 }}
                  className="flex h-10 w-10 cursor-pointer items-center justify-center rounded-lg bg-secondary text-lg"
                >
                  {badge.icon}
                </motion.div>
              </TooltipTrigger>
              <TooltipContent side="top" className="max-w-[200px]">
                <p className="font-medium">{badge.name}</p>
                <p className="text-xs text-muted-foreground">{badge.description}</p>
              </TooltipContent>
            </Tooltip>
          ))}
        </div>
      </div>
    </div>
  );
}
