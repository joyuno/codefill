'use client';

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Trophy, Target, Flame, Zap, FileCode, Puzzle, BookOpen, Code2 } from 'lucide-react';

interface StatsData {
  level: number;
  problemsSolved: number;
  accuracy: number;
  streak: number;
}

interface DifficultyData {
  easy?: number;
  medium?: number;
  hard?: number;
}

interface ProblemTypeStat {
  type: string;
  total: number;
  success: number;
  rate: number;
}

interface ScoreOverviewProps {
  score: number;
  stats: StatsData;
  difficultySnapshot?: DifficultyData;
  problemTypeStats?: ProblemTypeStat[];
}

// 점수에 따른 등급 및 색상
function getGradeInfo(score: number) {
  if (score >= 90) return { grade: 'S', label: 'Master', color: '#fbbf24', bg: 'from-amber-500/20 to-amber-600/5' };
  if (score >= 80) return { grade: 'A', label: 'Expert', color: '#22c55e', bg: 'from-emerald-500/20 to-emerald-600/5' };
  if (score >= 70) return { grade: 'B+', label: 'Advanced', color: '#3b82f6', bg: 'from-blue-500/20 to-blue-600/5' };
  if (score >= 60) return { grade: 'B', label: 'Intermediate', color: '#3b82f6', bg: 'from-blue-500/15 to-blue-600/5' };
  if (score >= 50) return { grade: 'C', label: 'Developing', color: '#a855f7', bg: 'from-violet-500/15 to-violet-600/5' };
  if (score >= 30) return { grade: 'D', label: 'Beginner', color: '#6b7280', bg: 'from-zinc-500/15 to-zinc-600/5' };
  return { grade: 'F', label: 'Starting', color: '#6b7280', bg: 'from-zinc-500/10 to-zinc-600/5' };
}

// 난이도 색상
const DIFFICULTY_COLORS = {
  easy: { color: '#22c55e', label: 'Easy' },
  medium: { color: '#eab308', label: 'Medium' },
  hard: { color: '#ef4444', label: 'Hard' },
};

// 문제 유형 설정
const PROBLEM_TYPE_CONFIG: Record<string, { icon: typeof FileCode; label: string; color: string }> = {
  blank: { icon: FileCode, label: '빈칸', color: '#3b82f6' },
  puzzle: { icon: Puzzle, label: '퍼즐', color: '#8b5cf6' },
  guided: { icon: BookOpen, label: '가이드', color: '#10b981' },
  implementation: { icon: Code2, label: '구현', color: '#f59e0b' },
};

function getProblemTypeConfig(type: string) {
  return PROBLEM_TYPE_CONFIG[type] || { icon: FileCode, label: type, color: '#6b7280' };
}

export function ScoreOverview({ score, stats, difficultySnapshot, problemTypeStats }: ScoreOverviewProps) {
  const [animatedScore, setAnimatedScore] = useState(0);
  const gradeInfo = getGradeInfo(score);

  // 점수 애니메이션
  useEffect(() => {
    const duration = 1200;
    const steps = 50;
    const increment = score / steps;
    let current = 0;

    const timer = setInterval(() => {
      current += increment;
      if (current >= score) {
        setAnimatedScore(score);
        clearInterval(timer);
      } else {
        setAnimatedScore(Math.floor(current));
      }
    }, duration / steps);

    return () => clearInterval(timer);
  }, [score]);

  return (
    <div className={`h-full p-6 rounded-2xl bg-gradient-to-br ${gradeInfo.bg} border border-zinc-800`}>
      {/* 상단: 점수 + 등급 */}
      <div className="flex items-start justify-between mb-6">
        <div>
          <motion.div
            className="text-5xl font-bold tabular-nums tracking-tight"
            style={{ color: gradeInfo.color }}
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            {animatedScore}
          </motion.div>
          <div className="text-sm text-zinc-500 mt-1">Overall Score</div>
        </div>

        <motion.div
          className="flex flex-col items-center px-4 py-2 rounded-xl"
          style={{ backgroundColor: `${gradeInfo.color}15` }}
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.3, duration: 0.4 }}
        >
          <span
            className="text-2xl font-black"
            style={{ color: gradeInfo.color }}
          >
            {gradeInfo.grade}
          </span>
          <span className="text-[10px] text-zinc-400 uppercase tracking-wider">
            {gradeInfo.label}
          </span>
        </motion.div>
      </div>

      {/* 중단: 주요 스탯 그리드 */}
      <motion.div
        className="grid grid-cols-4 gap-2 mb-6"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
      >
        <StatCard
          icon={<Trophy className="w-4 h-4" />}
          value={stats.level}
          label="Level"
          color="#fbbf24"
        />
        <StatCard
          icon={<Target className="w-4 h-4" />}
          value={stats.problemsSolved}
          label="Solved"
          color="#3b82f6"
        />
        <StatCard
          icon={<Zap className="w-4 h-4" />}
          value={`${Math.round(stats.accuracy * 100)}%`}
          label="Accuracy"
          color="#22c55e"
        />
        <StatCard
          icon={<Flame className="w-4 h-4" />}
          value={stats.streak}
          label="Streak"
          color="#f97316"
        />
      </motion.div>

      {/* 하단: 난이도별 + 유형별 정답률 (2열 레이아웃) */}
      <motion.div
        className="grid grid-cols-2 gap-4"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
      >
        {/* 난이도별 정답률 */}
        {difficultySnapshot && (
          <div>
            <div className="text-xs text-zinc-500 uppercase tracking-wider mb-2">
              Difficulty
            </div>
            <div className="space-y-2">
              {(['easy', 'medium', 'hard'] as const).map((difficulty) => {
                const rate = difficultySnapshot[difficulty] ?? 0;
                const config = DIFFICULTY_COLORS[difficulty];
                const percentage = Math.round(rate * 100);

                return (
                  <div key={difficulty} className="flex items-center gap-2">
                    <span
                      className="text-[10px] font-medium w-12"
                      style={{ color: config.color }}
                    >
                      {config.label}
                    </span>
                    <div className="flex-1 h-1.5 bg-zinc-800 rounded-full overflow-hidden">
                      <motion.div
                        className="h-full rounded-full"
                        style={{ backgroundColor: config.color }}
                        initial={{ width: 0 }}
                        animate={{ width: `${percentage}%` }}
                        transition={{ delay: 0.8, duration: 0.8, ease: 'easeOut' }}
                      />
                    </div>
                    <span className="text-[10px] font-mono text-zinc-400 w-8 text-right">
                      {percentage}%
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* 문제 유형별 정답률 */}
        {problemTypeStats && problemTypeStats.length > 0 && (
          <div>
            <div className="text-xs text-zinc-500 uppercase tracking-wider mb-2">
              Problem Type
            </div>
            <div className="space-y-2">
              {problemTypeStats.slice(0, 3).map((stat) => {
                const config = getProblemTypeConfig(stat.type);
                const Icon = config.icon;
                const percentage = Math.round(stat.rate * 100);

                return (
                  <div key={stat.type} className="flex items-center gap-2">
                    <Icon className="w-3 h-3 flex-shrink-0" style={{ color: config.color }} />
                    <span
                      className="text-[10px] font-medium w-10 truncate"
                      style={{ color: config.color }}
                    >
                      {config.label}
                    </span>
                    <div className="flex-1 h-1.5 bg-zinc-800 rounded-full overflow-hidden">
                      <motion.div
                        className="h-full rounded-full"
                        style={{ backgroundColor: config.color }}
                        initial={{ width: 0 }}
                        animate={{ width: `${percentage}%` }}
                        transition={{ delay: 1, duration: 0.8, ease: 'easeOut' }}
                      />
                    </div>
                    <span className="text-[10px] font-mono text-zinc-400 w-8 text-right">
                      {percentage}%
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </motion.div>
    </div>
  );
}

function StatCard({
  icon,
  value,
  label,
  color,
}: {
  icon: React.ReactNode;
  value: string | number;
  label: string;
  color: string;
}) {
  return (
    <div className="flex flex-col items-center p-2 rounded-lg bg-zinc-900/50 border border-zinc-800/50">
      <div style={{ color }} className="mb-1 opacity-80">
        {icon}
      </div>
      <span className="text-sm font-bold text-zinc-100 tabular-nums">{value}</span>
      <span className="text-[9px] text-zinc-500 uppercase tracking-wider">{label}</span>
    </div>
  );
}
