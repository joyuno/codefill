'use client';

import { useMemo } from 'react';
import { motion } from 'framer-motion';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceDot,
} from 'recharts';
import { TrendingUp, TrendingDown, Minus, Trophy } from 'lucide-react';

interface GrowthDataPoint {
  date: string; // ISO 날짜 또는 라벨
  score: number; // 0-100
  label?: string;
  milestone?: string; // 마일스톤 이벤트 (레벨업 등)
}

interface GrowthCurveProps {
  data: GrowthDataPoint[];
  currentScore: number;
  previousScore?: number;
}

// 날짜 포맷
function formatDate(dateStr: string): string {
  try {
    const date = new Date(dateStr);
    return `${date.getMonth() + 1}/${date.getDate()}`;
  } catch {
    return dateStr;
  }
}

// 트렌드 계산
function calculateTrend(data: GrowthDataPoint[]): {
  direction: 'up' | 'down' | 'stable';
  percentage: number;
} {
  if (data.length < 2) {
    return { direction: 'stable', percentage: 0 };
  }

  const recent = data.slice(-3);
  const older = data.slice(0, Math.max(1, data.length - 3));

  const recentAvg = recent.reduce((sum, d) => sum + d.score, 0) / recent.length;
  const olderAvg = older.reduce((sum, d) => sum + d.score, 0) / older.length;

  const diff = recentAvg - olderAvg;
  const percentage = Math.abs(Math.round(diff));

  if (diff > 2) return { direction: 'up', percentage };
  if (diff < -2) return { direction: 'down', percentage };
  return { direction: 'stable', percentage: 0 };
}

export function GrowthCurve({
  data,
  currentScore,
  previousScore,
}: GrowthCurveProps) {
  // 데이터 처리
  const chartData = useMemo(() => {
    if (data.length === 0) {
      // 데이터가 없으면 현재 점수만 표시
      return [
        {
          date: '현재',
          score: currentScore,
          displayDate: '현재',
        },
      ];
    }

    return data.map((point) => ({
      ...point,
      displayDate: formatDate(point.date),
    }));
  }, [data, currentScore]);

  // 트렌드 계산
  const trend = useMemo(() => {
    if (previousScore !== undefined) {
      const diff = currentScore - previousScore;
      const percentage = Math.abs(Math.round(diff));
      if (diff > 2) return { direction: 'up' as const, percentage };
      if (diff < -2) return { direction: 'down' as const, percentage };
      return { direction: 'stable' as const, percentage: 0 };
    }
    return calculateTrend(data);
  }, [data, currentScore, previousScore]);

  // 트렌드 아이콘 및 색상
  const trendConfig = {
    up: {
      icon: TrendingUp,
      color: '#22c55e',
      text: `+${trend.percentage}% 상승`,
      bgColor: 'bg-green-500/10',
      borderColor: 'border-green-500/30',
    },
    down: {
      icon: TrendingDown,
      color: '#ef4444',
      text: `-${trend.percentage}% 하락`,
      bgColor: 'bg-red-500/10',
      borderColor: 'border-red-500/30',
    },
    stable: {
      icon: Minus,
      color: '#71717a',
      text: '유지 중',
      bgColor: 'bg-zinc-500/10',
      borderColor: 'border-zinc-500/30',
    },
  };

  const TrendIcon = trendConfig[trend.direction].icon;

  // 마일스톤 찾기
  const milestones = chartData.filter((d) => d.milestone);

  const isFirstAnalysis = data.length === 0;

  return (
    <motion.div
      className="flex flex-col h-full"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: 0.4 }}
    >
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-medium text-zinc-400 uppercase tracking-wider">
          Growth Curve
        </h3>
        <div
          className={`flex items-center gap-1.5 px-2 py-1 rounded-full text-xs font-medium ${trendConfig[trend.direction].bgColor} ${trendConfig[trend.direction].borderColor} border`}
          style={{ color: trendConfig[trend.direction].color }}
        >
          <TrendIcon className="h-3 w-3" />
          {trendConfig[trend.direction].text}
        </div>
      </div>

      {isFirstAnalysis ? (
        // 첫 분석인 경우
        <div className="flex-1 flex flex-col items-center justify-center text-center px-4">
          <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center mb-3">
            <Trophy className="h-6 w-6 text-primary" />
          </div>
          <p className="text-sm text-zinc-400 mb-1">첫 분석을 완료했어요!</p>
          <p className="text-2xl font-bold text-zinc-100">
            {currentScore}점
          </p>
          <p className="text-xs text-zinc-500 mt-2">
            다음 분석부터 성장 추이가 표시됩니다
          </p>
        </div>
      ) : (
        // 차트 표시
        <div className="flex-1 min-h-[180px]">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart
              data={chartData}
              margin={{ top: 10, right: 10, left: -20, bottom: 0 }}
            >
              <defs>
                <linearGradient id="scoreGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.4} />
                  <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
                </linearGradient>
              </defs>

              <CartesianGrid
                strokeDasharray="3 3"
                stroke="#27272a"
                vertical={false}
              />

              <XAxis
                dataKey="displayDate"
                tick={{ fill: '#71717a', fontSize: 10 }}
                tickLine={false}
                axisLine={{ stroke: '#3f3f46' }}
              />

              <YAxis
                domain={[0, 100]}
                tick={{ fill: '#71717a', fontSize: 10 }}
                tickLine={false}
                axisLine={false}
                tickCount={5}
              />

              <Tooltip
                content={({ active, payload }) => {
                  if (!active || !payload || payload.length === 0) return null;
                  const data = payload[0].payload;
                  return (
                    <div className="bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-2 shadow-lg">
                      <p className="text-xs text-zinc-400">{data.displayDate}</p>
                      <p className="text-sm font-bold text-zinc-100">
                        {data.score}점
                      </p>
                      {data.milestone && (
                        <p className="text-xs text-primary mt-1 flex items-center gap-1">
                          <Trophy className="h-3 w-3" />
                          {data.milestone}
                        </p>
                      )}
                    </div>
                  );
                }}
              />

              <Area
                type="monotone"
                dataKey="score"
                stroke="#8b5cf6"
                strokeWidth={2}
                fill="url(#scoreGradient)"
                dot={{
                  fill: '#8b5cf6',
                  strokeWidth: 0,
                  r: 3,
                }}
                activeDot={{
                  fill: '#a78bfa',
                  strokeWidth: 2,
                  stroke: '#8b5cf6',
                  r: 5,
                }}
                animationBegin={400}
                animationDuration={1200}
              />

              {/* 마일스톤 표시 */}
              {milestones.map((milestone, i) => (
                <ReferenceDot
                  key={i}
                  x={milestone.displayDate}
                  y={milestone.score}
                  r={6}
                  fill="#fbbf24"
                  stroke="#f59e0b"
                  strokeWidth={2}
                />
              ))}
            </AreaChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* 요약 정보 */}
      {!isFirstAnalysis && data.length >= 2 && (
        <div className="mt-2 flex items-center justify-center gap-4 text-xs text-zinc-500">
          <span>
            시작: <span className="text-zinc-400">{data[0].score}점</span>
          </span>
          <span className="text-zinc-700">→</span>
          <span>
            현재: <span className="text-zinc-200 font-medium">{currentScore}점</span>
          </span>
        </div>
      )}
    </motion.div>
  );
}
