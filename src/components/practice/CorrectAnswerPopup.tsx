'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Trophy, Sparkles, Target, Clock, Lightbulb, TrendingUp, ArrowRight, RotateCcw } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { FeedbackResponse } from '@/lib/api/agent';
import type { SeedAwarded } from '@/lib/api/practice';
import { CROPS } from '@/components/farm/config/cropConfig';

interface CorrectAnswerPopupProps {
  isOpen: boolean;
  onClose: () => void;
  onNextProblem: () => void;
  feedback: FeedbackResponse | null;
  xpEarned: number;
  isLoading?: boolean;
  seedAwarded?: SeedAwarded | null;  // 씨앗 보상 정보
}

const gradeColors: Record<string, string> = {
  perfect: 'text-yellow-500',
  excellent: 'text-purple-500',
  good: 'text-blue-500',
  keep_going: 'text-green-500',
  learning: 'text-emerald-500',
};

const gradeBgColors: Record<string, string> = {
  perfect: 'bg-yellow-500/10 border-yellow-500/30',
  excellent: 'bg-purple-500/10 border-purple-500/30',
  good: 'bg-blue-500/10 border-blue-500/30',
  keep_going: 'bg-green-500/10 border-green-500/30',
  learning: 'bg-emerald-500/10 border-emerald-500/30',
};

// 씨앗 등급별 스타일 설정
const seedRarityConfig: Record<string, {
  gradient: string;
  glow: string;
  border: string;
  text: string;
  label: string;
  labelColor: string;
}> = {
  common: {
    gradient: 'from-blue-600/30 via-sky-500/20 to-blue-600/30',
    glow: 'shadow-blue-500/20',
    border: 'border-blue-400/40',
    text: 'text-blue-300',
    label: '일반',
    labelColor: 'bg-blue-500/30 text-blue-300',
  },
  uncommon: {
    gradient: 'from-purple-600/30 via-violet-500/20 to-purple-600/30',
    glow: 'shadow-purple-500/30',
    border: 'border-purple-400/50',
    text: 'text-purple-300',
    label: '고급',
    labelColor: 'bg-purple-500/30 text-purple-300',
  },
  rare: {
    gradient: 'from-red-600/30 via-rose-500/20 to-red-600/30',
    glow: 'shadow-red-500/40',
    border: 'border-red-400/60',
    text: 'text-red-300',
    label: '희귀',
    labelColor: 'bg-red-500/30 text-red-300',
  },
  epic: {
    gradient: 'from-amber-600/30 via-yellow-500/20 to-amber-600/30',
    glow: 'shadow-amber-500/50',
    border: 'border-amber-400/70',
    text: 'text-amber-300',
    label: '전설',
    labelColor: 'bg-amber-500/30 text-amber-300',
  },
};

// 작물 이미지 경로 가져오기
function getCropImage(cropCode: string): string | null {
  const crop = CROPS[cropCode];
  return crop?.ripeSprite || null;
}

export function CorrectAnswerPopup({
  isOpen,
  onClose,
  onNextProblem,
  feedback,
  xpEarned,
  isLoading = false,
  seedAwarded,
}: CorrectAnswerPopupProps) {
  const [showDetails, setShowDetails] = useState(false);

  // Show details after a short delay for animation
  useEffect(() => {
    if (isOpen && feedback) {
      const timer = setTimeout(() => setShowDetails(true), 500);
      return () => clearTimeout(timer);
    } else {
      setShowDetails(false);
    }
  }, [isOpen, feedback]);

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="max-w-md sm:max-w-lg overflow-hidden">
        <DialogHeader className="text-center">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: 'spring', duration: 0.5 }}
            className="mx-auto mb-4"
          >
            {isLoading ? (
              <div className="w-20 h-20 rounded-full bg-muted animate-pulse flex items-center justify-center">
                <Sparkles className="h-8 w-8 text-muted-foreground animate-spin" />
              </div>
            ) : (
              <div className={cn(
                'w-20 h-20 rounded-full border-2 flex items-center justify-center',
                feedback ? gradeBgColors[feedback.grade] : 'bg-primary/10 border-primary/30'
              )}>
                <span className="text-4xl">{feedback?.grade_emoji || '🎉'}</span>
              </div>
            )}
          </motion.div>

          <DialogTitle className="text-2xl font-bold">
            {isLoading ? '분석 중...' : '정답입니다!'}
          </DialogTitle>

          <DialogDescription className="text-base">
            {isLoading ? (
              '풀이 과정을 분석하고 있습니다...'
            ) : (
              feedback?.grade_message || '훌륭해요!'
            )}
          </DialogDescription>
        </DialogHeader>

        {/* XP Badge + Seed Badge (compact) */}
        <motion.div
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="flex justify-center items-center gap-3 flex-wrap"
        >
          {/* XP Badge */}
          <Badge
            variant="outline"
            className="px-4 py-2 text-lg bg-primary/10 text-primary border-primary/30"
          >
            <Trophy className="w-5 h-5 mr-2" />
            +{xpEarned} XP
          </Badge>

          {/* Seed Badge (compact version) */}
          {seedAwarded && (() => {
            const config = seedRarityConfig[seedAwarded.rarity] || seedRarityConfig.common;
            const cropImage = getCropImage(seedAwarded.cropCode);

            return (
              <motion.div
                initial={{ scale: 0, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ delay: 0.4, type: 'spring', stiffness: 300, damping: 20 }}
                className={cn(
                  "relative flex items-center gap-2 px-3 py-1.5 rounded-full border",
                  "bg-gradient-to-r",
                  config.gradient,
                  config.border
                )}
              >
                {/* Glow effect for rare+ */}
                {(seedAwarded.rarity === 'rare' || seedAwarded.rarity === 'epic') && (
                  <motion.div
                    className={cn(
                      "absolute inset-0 rounded-full",
                      seedAwarded.rarity === 'epic'
                        ? "bg-gradient-to-r from-amber-500/10 via-yellow-500/10 to-amber-500/10"
                        : "bg-gradient-to-r from-red-500/10 via-rose-500/10 to-red-500/10"
                    )}
                    animate={{ opacity: [0.5, 1, 0.5] }}
                    transition={{ duration: 1.5, repeat: Infinity, ease: "easeInOut" }}
                  />
                )}

                {/* Crop image */}
                <div className={cn(
                  "relative w-7 h-7 rounded-md flex items-center justify-center",
                  "bg-black/30 border",
                  config.border
                )}>
                  {cropImage ? (
                    <img
                      src={cropImage}
                      alt={seedAwarded.cropNameKo}
                      className="w-5 h-5"
                      style={{ imageRendering: 'pixelated' }}
                    />
                  ) : (
                    <span className="text-sm">🌱</span>
                  )}
                </div>

                {/* Seed name */}
                <span className={cn("text-sm font-medium relative z-10", config.text)}>
                  {seedAwarded.cropNameKo} 씨앗
                </span>

                {/* Rarity indicator dot */}
                <span className={cn(
                  "w-1.5 h-1.5 rounded-full relative z-10",
                  seedAwarded.rarity === 'epic' ? 'bg-amber-400' :
                  seedAwarded.rarity === 'rare' ? 'bg-red-400' :
                  seedAwarded.rarity === 'uncommon' ? 'bg-purple-400' : 'bg-blue-400'
                )} />
              </motion.div>
            );
          })()}
        </motion.div>

        <AnimatePresence>
          {showDetails && feedback && !isLoading && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.3 }}
              className="space-y-4 overflow-hidden"
            >
              <Separator />

              {/* Performance Summary */}
              <div className="bg-muted/30 rounded-lg p-4 space-y-3">
                <h4 className="font-medium text-sm flex items-center gap-2">
                  <Target className="w-4 h-4 text-primary" />
                  성과 분석
                </h4>

                {/* Score Bars */}
                <div className="space-y-3">
                  <div className="space-y-1">
                    <div className="flex justify-between text-xs">
                      <span className="text-muted-foreground">효율성</span>
                      <span className="font-medium">{feedback.visualization.efficiency_score}%</span>
                    </div>
                    <Progress value={feedback.visualization.efficiency_score} className="h-2" />
                  </div>

                  <div className="space-y-1">
                    <div className="flex justify-between text-xs">
                      <span className="text-muted-foreground">속도</span>
                      <span className="font-medium">{feedback.visualization.speed_score}%</span>
                    </div>
                    <Progress value={feedback.visualization.speed_score} className="h-2" />
                  </div>

                  <div className="space-y-1">
                    <div className="flex justify-between text-xs">
                      <span className="text-muted-foreground">이해도</span>
                      <span className="font-medium">{feedback.visualization.understanding_score}%</span>
                    </div>
                    <Progress value={feedback.visualization.understanding_score} className="h-2" />
                  </div>
                </div>

                {/* Time Comparison */}
                {feedback.visualization.time_comparison && (
                  <div className="flex items-center gap-2 text-xs text-muted-foreground mt-2">
                    <Clock className="w-3 h-3" />
                    <span>
                      풀이 시간: {Math.floor(feedback.visualization.time_comparison.user_time / 60)}분
                      {feedback.visualization.time_comparison.user_time % 60}초
                      ({feedback.visualization.time_comparison.percentile})
                    </span>
                  </div>
                )}
              </div>

              {/* Performance Feedback */}
              <div className="grid grid-cols-3 gap-2 text-center">
                <div className="bg-muted/20 rounded-lg p-2">
                  <Clock className="w-4 h-4 mx-auto mb-1 text-blue-500" />
                  <p className="text-xs text-muted-foreground">시간</p>
                  <p className="text-xs font-medium truncate" title={feedback.performance_analysis.time_feedback}>
                    {feedback.performance_analysis.time_feedback.slice(0, 15)}
                    {feedback.performance_analysis.time_feedback.length > 15 ? '...' : ''}
                  </p>
                </div>
                <div className="bg-muted/20 rounded-lg p-2">
                  <Lightbulb className="w-4 h-4 mx-auto mb-1 text-yellow-500" />
                  <p className="text-xs text-muted-foreground">힌트</p>
                  <p className="text-xs font-medium truncate" title={feedback.performance_analysis.hint_feedback}>
                    {feedback.performance_analysis.hint_feedback.slice(0, 15)}
                    {feedback.performance_analysis.hint_feedback.length > 15 ? '...' : ''}
                  </p>
                </div>
                <div className="bg-muted/20 rounded-lg p-2">
                  <TrendingUp className="w-4 h-4 mx-auto mb-1 text-green-500" />
                  <p className="text-xs text-muted-foreground">시도</p>
                  <p className="text-xs font-medium truncate" title={feedback.performance_analysis.attempt_feedback}>
                    {feedback.performance_analysis.attempt_feedback.slice(0, 15)}
                    {feedback.performance_analysis.attempt_feedback.length > 15 ? '...' : ''}
                  </p>
                </div>
              </div>

              {/* Learning Points */}
              {feedback.learning_points.length > 0 && (
                <div className="space-y-2">
                  <h4 className="font-medium text-sm flex items-center gap-2">
                    <Sparkles className="w-4 h-4 text-primary" />
                    배운 점
                  </h4>
                  <ul className="text-sm text-muted-foreground space-y-1">
                    {feedback.learning_points.slice(0, 2).map((point, i) => (
                      <li key={i} className="flex items-start gap-2">
                        <span className="text-primary mt-0.5">•</span>
                        <span>{point}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Encouragement */}
              <div className={cn(
                'rounded-lg p-3 text-center text-sm',
                feedback ? gradeBgColors[feedback.grade] : ''
              )}>
                <p className={cn('font-medium', feedback ? gradeColors[feedback.grade] : '')}>
                  {feedback.encouragement}
                </p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-2 mt-4">
          <Button
            variant="outline"
            className="flex-1"
            onClick={onClose}
            disabled={isLoading}
          >
            <RotateCcw className="w-4 h-4 mr-2" />
            문제풀이로 돌아가기
          </Button>
          <Button
            className="flex-1"
            onClick={onNextProblem}
            disabled={isLoading}
          >
            다음문제 풀기
            <ArrowRight className="w-4 h-4 ml-2" />
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
