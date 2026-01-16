'use client';

import { motion } from 'framer-motion';
import type { HintIndependence } from '@/lib/api/analysis';

interface HintIndependenceCardProps {
  data: HintIndependence;
}

// 파이 슬라이스 경로 생성
function createPieSlice(
  cx: number,
  cy: number,
  radius: number,
  startAngle: number,
  endAngle: number
): string {
  const start = polarToCartesian(cx, cy, radius, endAngle);
  const end = polarToCartesian(cx, cy, radius, startAngle);
  const largeArcFlag = endAngle - startAngle <= 180 ? 0 : 1;

  return [
    'M', cx, cy,
    'L', start.x, start.y,
    'A', radius, radius, 0, largeArcFlag, 0, end.x, end.y,
    'Z'
  ].join(' ');
}

function polarToCartesian(cx: number, cy: number, radius: number, angle: number) {
  const rad = (angle - 90) * Math.PI / 180;
  return {
    x: cx + radius * Math.cos(rad),
    y: cy + radius * Math.sin(rad)
  };
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

  const segments = [
    {
      key: 'solved_without_hint',
      label: '스스로 해결',
      desc: '힌트 없이 정답',
      value: solved_without_hint,
      percent: (solved_without_hint / total) * 100,
      color: '#22c55e',
      icon: '✓',
    },
    {
      key: 'solved_with_hint',
      label: '힌트로 해결',
      desc: '힌트 참고 후 정답',
      value: solved_with_hint,
      percent: (solved_with_hint / total) * 100,
      color: '#3b82f6',
      icon: '💡',
    },
    {
      key: 'failed_with_hint',
      label: '힌트 후 실패',
      desc: '힌트 봤지만 오답',
      value: failed_with_hint,
      percent: (failed_with_hint / total) * 100,
      color: '#ef4444',
      icon: '✗',
    },
    {
      key: 'failed_without_hint',
      label: '미해결',
      desc: '힌트 없이 오답/포기',
      value: failed_without_hint,
      percent: (failed_without_hint / total) * 100,
      color: '#71717a',
      icon: '−',
    },
  ].filter(s => s.value > 0);

  // 각도 계산
  let currentAngle = 0;
  const slices = segments.map((segment) => {
    const startAngle = currentAngle;
    const sweepAngle = (segment.percent / 100) * 360;
    currentAngle += sweepAngle;
    return { ...segment, startAngle, endAngle: currentAngle };
  });

  const percentValue = Math.round(independence_rate * 100);

  // 독립률 기반 메시지
  const getMessage = (rate: number) => {
    if (rate >= 0.6) return { text: '스스로 문제를 해결하는 능력이 뛰어납니다.', type: 'good' };
    if (rate >= 0.4) return { text: '힌트 의존도를 조금씩 줄여보세요.', type: 'normal' };
    if (rate >= 0.2) return { text: '힌트 없이 먼저 고민하는 습관을 길러보세요.', type: 'warn' };
    return { text: '스스로 해결하려는 시도가 실력 향상의 지름길입니다.', type: 'bad' };
  };

  const message = getMessage(independence_rate);

  return (
    <div className="p-5">
      <div className="flex items-center gap-5">
        {/* 파이 차트 */}
        <div className="relative flex-shrink-0">
          <svg viewBox="0 0 100 100" className="w-40 h-40">
            {slices.map((slice, index) => (
              <motion.path
                key={slice.key}
                d={createPieSlice(50, 50, 42, slice.startAngle, slice.endAngle)}
                fill={slice.color}
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ duration: 0.4, delay: index * 0.05 }}
                style={{ transformOrigin: '50px 50px' }}
              />
            ))}
            {/* 중앙 원 (도넛 효과) */}
            <circle cx="50" cy="50" r="24" fill="#18181b" />
          </svg>

          {/* 중앙 텍스트 */}
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <motion.span
              className="text-xl font-bold text-zinc-100"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5 }}
            >
              {percentValue}%
            </motion.span>
            <span className="text-[10px] text-zinc-500">독립률</span>
          </div>
        </div>

        {/* 우측 범례 */}
        <div className="flex-1 space-y-2.5">
          {slices.map((slice) => (
            <div key={slice.key} className="flex items-center gap-2">
              <div
                className="w-2.5 h-2.5 rounded-sm flex-shrink-0"
                style={{ backgroundColor: slice.color }}
              />
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-1">
                  <span className="text-xs text-zinc-300">{slice.label}</span>
                  <span className="text-[10px] text-zinc-600">{slice.desc}</span>
                </div>
              </div>
              <span className="text-xs font-semibold text-zinc-200 tabular-nums">
                {slice.value}
              </span>
              <span className="text-[10px] text-zinc-500 w-9 text-right tabular-nums">
                {Math.round(slice.percent)}%
              </span>
            </div>
          ))}

          {/* 총계 */}
          <div className="pt-2 border-t border-zinc-800/50">
            <div className="flex items-center justify-between">
              <span className="text-[10px] text-zinc-500">총 문제</span>
              <span className="text-xs font-medium text-zinc-300">{total}문제</span>
            </div>
          </div>
        </div>
      </div>

      {/* 설명 메시지 */}
      <div
        className={`mt-4 text-xs px-3 py-2 rounded-lg ${
          message.type === 'good'
            ? 'bg-emerald-500/10 text-emerald-400/90'
            : message.type === 'normal'
            ? 'bg-blue-500/10 text-blue-400/90'
            : message.type === 'warn'
            ? 'bg-amber-500/10 text-amber-400/90'
            : 'bg-rose-500/10 text-rose-400/90'
        }`}
      >
        {message.text}
      </div>
    </div>
  );
}
