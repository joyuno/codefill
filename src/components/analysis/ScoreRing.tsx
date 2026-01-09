'use client';

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';

interface StatsData {
  level: number;
  problemsSolved: number;
  accuracy: number; // 0-1
  streak: number;
}

interface ScoreRingProps {
  score: number; // 0-100
  stats?: StatsData;
  size?: number;
  strokeWidth?: number;
}

// 점수에 따른 등급 및 색상
function getGradeInfo(score: number) {
  if (score >= 90) return { grade: 'S', label: '마스터', color: '#fbbf24', glow: 'rgba(251, 191, 36, 0.4)' };
  if (score >= 80) return { grade: 'A', label: '숙련자', color: '#22c55e', glow: 'rgba(34, 197, 94, 0.4)' };
  if (score >= 70) return { grade: 'B+', label: '중급자', color: '#3b82f6', glow: 'rgba(59, 130, 246, 0.4)' };
  if (score >= 60) return { grade: 'B', label: '중급자', color: '#3b82f6', glow: 'rgba(59, 130, 246, 0.3)' };
  if (score >= 50) return { grade: 'C', label: '초급자', color: '#a855f7', glow: 'rgba(168, 85, 247, 0.3)' };
  if (score >= 30) return { grade: 'D', label: '입문자', color: '#6b7280', glow: 'rgba(107, 114, 128, 0.3)' };
  return { grade: 'F', label: '시작하기', color: '#6b7280', glow: 'rgba(107, 114, 128, 0.2)' };
}

export function ScoreRing({ score, stats, size = 160, strokeWidth = 10 }: ScoreRingProps) {
  const [animatedScore, setAnimatedScore] = useState(0);
  const gradeInfo = getGradeInfo(score);

  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const progress = (animatedScore / 100) * circumference;
  const offset = circumference - progress;

  // 점수 애니메이션
  useEffect(() => {
    const duration = 1500;
    const steps = 60;
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
    <div className="flex flex-col items-center">
      {/* 점수 링 */}
      <div className="relative flex items-center justify-center" style={{ width: size, height: size }}>
        {/* 글로우 효과 */}
        <div
          className="absolute inset-0 rounded-full blur-2xl opacity-60"
          style={{ backgroundColor: gradeInfo.glow }}
        />

        {/* SVG 링 */}
        <svg width={size} height={size} className="relative -rotate-90">
          {/* 배경 링 */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke="#262626"
            strokeWidth={strokeWidth}
          />
          {/* 프로그레스 링 */}
          <motion.circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke={gradeInfo.color}
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset: offset }}
            transition={{ duration: 1.5, ease: 'easeOut' }}
            style={{
              filter: `drop-shadow(0 0 8px ${gradeInfo.color})`,
            }}
          />
        </svg>

        {/* 중앙 텍스트 */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <motion.span
            className="text-4xl font-bold tabular-nums"
            style={{ color: gradeInfo.color }}
            initial={{ opacity: 0, scale: 0.5 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.3, duration: 0.5 }}
          >
            {animatedScore}
          </motion.span>
          <motion.div
            className="flex items-center gap-1.5 mt-0.5"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6, duration: 0.4 }}
          >
            <span
              className="text-lg font-bold"
              style={{ color: gradeInfo.color }}
            >
              {gradeInfo.grade}
            </span>
            <span className="text-xs text-zinc-500">
              {gradeInfo.label}
            </span>
          </motion.div>
        </div>
      </div>

      {/* 기본 스탯 - 하단에 통합 */}
      {stats && (
        <motion.div
          className="mt-4 grid grid-cols-4 gap-2 w-full max-w-[280px]"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
        >
          <StatItem label="Level" value={stats.level} />
          <StatItem label="Solved" value={stats.problemsSolved} />
          <StatItem label="정확도" value={`${Math.round(stats.accuracy * 100)}%`} />
          <StatItem label="연속" value={`${stats.streak}일`} />
        </motion.div>
      )}
    </div>
  );
}

function StatItem({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="flex flex-col items-center px-2 py-1.5 rounded-lg bg-zinc-800/50">
      <span className="text-sm font-bold text-zinc-100 tabular-nums">{value}</span>
      <span className="text-[10px] text-zinc-500 uppercase tracking-wider">{label}</span>
    </div>
  );
}
