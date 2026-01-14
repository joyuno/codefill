'use client';

import { motion } from 'framer-motion';
import { Trophy, Lightbulb, AlertTriangle, HelpCircle } from 'lucide-react';
import type { HintIndependence } from '@/lib/api/analysis';

interface HintIndependenceCardProps {
  data: HintIndependence;
}

// 도넛 차트 세그먼트 컴포넌트
function DonutSegment({
  percentage,
  offset,
  color,
  delay,
}: {
  percentage: number;
  offset: number;
  color: string;
  delay: number;
}) {
  const radius = 45;
  const circumference = 2 * Math.PI * radius;
  const strokeDasharray = (percentage / 100) * circumference;

  return (
    <motion.circle
      cx="50"
      cy="50"
      r={radius}
      fill="none"
      stroke={color}
      strokeWidth="10"
      strokeLinecap="round"
      strokeDasharray={`${strokeDasharray} ${circumference}`}
      strokeDashoffset={-(offset / 100) * circumference}
      transform="rotate(-90 50 50)"
      initial={{ strokeDasharray: `0 ${circumference}` }}
      animate={{ strokeDasharray: `${strokeDasharray} ${circumference}` }}
      transition={{ duration: 0.8, delay, ease: 'easeOut' }}
    />
  );
}

export function HintIndependenceCard({ data }: HintIndependenceCardProps) {
  if (!data || data.total === 0) {
    return (
      <div className="p-6 text-center text-zinc-500 text-sm">
        풀이 기록이 없습니다.
      </div>
    );
  }

  const {
    solved_without_hint,
    solved_with_hint,
    failed_with_hint,
    failed_without_hint,
    total,
    independence_rate
  } = data;

  // 각 카테고리의 비율 계산
  const segments = [
    {
      key: 'solved_without_hint',
      label: '힌트 없이 성공',
      value: solved_without_hint,
      percent: Math.round((solved_without_hint / total) * 100),
      color: '#22c55e',
      icon: Trophy,
    },
    {
      key: 'solved_with_hint',
      label: '힌트로 성공',
      value: solved_with_hint,
      percent: Math.round((solved_with_hint / total) * 100),
      color: '#3b82f6',
      icon: Lightbulb,
    },
    {
      key: 'failed_with_hint',
      label: '힌트에도 실패',
      value: failed_with_hint,
      percent: Math.round((failed_with_hint / total) * 100),
      color: '#ef4444',
      icon: AlertTriangle,
    },
    {
      key: 'failed_without_hint',
      label: '힌트 없이 실패',
      value: failed_without_hint,
      percent: Math.round((failed_without_hint / total) * 100),
      color: '#6b7280',
      icon: HelpCircle,
    },
  ].filter(s => s.value > 0);

  // 누적 offset 계산
  let currentOffset = 0;
  const segmentsWithOffset = segments.map((segment) => {
    const result = { ...segment, offset: currentOffset };
    currentOffset += segment.percent;
    return result;
  });

  // 독립률에 따른 메시지
  const getIndependenceMessage = (rate: number): { text: string; type: 'good' | 'warn' | 'bad' } => {
    if (rate >= 0.5) return { text: '스스로 해결하는 능력이 좋습니다!', type: 'good' };
    if (rate >= 0.3) return { text: '힌트 의존도를 줄여보세요.', type: 'warn' };
    return { text: '힌트 없이 먼저 시도해보세요.', type: 'bad' };
  };

  const message = getIndependenceMessage(independence_rate);

  return (
    <div className="p-4 flex flex-col items-center">
      {/* 도넛 차트 */}
      <div className="relative w-36 h-36 mb-4">
        <svg viewBox="0 0 100 100" className="w-full h-full">
          {/* 배경 원 */}
          <circle
            cx="50"
            cy="50"
            r="45"
            fill="none"
            stroke="#27272a"
            strokeWidth="10"
          />
          {/* 데이터 세그먼트 */}
          {segmentsWithOffset.map((segment, index) => (
            <DonutSegment
              key={segment.key}
              percentage={segment.percent}
              offset={segment.offset}
              color={segment.color}
              delay={index * 0.1}
            />
          ))}
        </svg>
        {/* 중앙 텍스트 */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <motion.span
            className="text-2xl font-bold text-zinc-100"
            initial={{ opacity: 0, scale: 0.5 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.5 }}
          >
            {Math.round(independence_rate * 100)}%
          </motion.span>
          <span className="text-[10px] text-zinc-500">독립 해결률</span>
        </div>
      </div>

      {/* 범례 */}
      <div className="grid grid-cols-2 gap-x-4 gap-y-1.5 w-full">
        {segments.map((segment) => {
          const Icon = segment.icon;
          return (
            <div
              key={segment.key}
              className="flex items-center gap-1.5"
            >
              <div
                className="w-2 h-2 rounded-full flex-shrink-0"
                style={{ backgroundColor: segment.color }}
              />
              <span className="text-[10px] text-zinc-400 truncate">
                {segment.label}
              </span>
              <span className="text-[10px] font-medium text-zinc-300 ml-auto">
                {segment.percent}%
              </span>
            </div>
          );
        })}
      </div>

      {/* 메시지 */}
      <div
        className={`mt-3 text-center text-xs py-1.5 px-3 rounded-lg w-full ${
          message.type === 'good'
            ? 'bg-emerald-500/10 text-emerald-400'
            : message.type === 'warn'
            ? 'bg-amber-500/10 text-amber-400'
            : 'bg-red-500/10 text-red-400'
        }`}
      >
        {message.text}
      </div>
    </div>
  );
}
