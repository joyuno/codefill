'use client';

import { useMemo } from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, Minus, Zap, Target } from 'lucide-react';
import type { EloHistoryEntry } from '@/lib/api/analysis';

interface EloGrowthCardProps {
  eloHistory: EloHistoryEntry[];
  eloOverall?: number;
}

// 토픽별 총 변화량 계산
interface TopicGrowth {
  topic: string;
  totalChange: number;
  currentElo: number;
  attempts: number;
}

export function EloGrowthCard({ eloHistory, eloOverall }: EloGrowthCardProps) {
  // 데이터 처리
  const { topicGrowths, eloTimeline, stats } = useMemo(() => {
    if (!eloHistory || eloHistory.length === 0) {
      return { topicGrowths: [], eloTimeline: [], stats: null };
    }

    // 토픽별 성장량 집계
    const topicMap = new Map<string, { total: number; current: number; count: number }>();

    // 시간순 ELO 변화
    const timeline: { date: string; elo: number; isCorrect: boolean }[] = [];

    let correctCount = 0;

    eloHistory.forEach((entry) => {
      // DB 형식: { date, topic, before, after, change, problem_elo, expected }
      const existing = topicMap.get(entry.topic);
      if (existing) {
        existing.total += entry.change;
        existing.current = entry.after;
        existing.count += 1;
      } else {
        topicMap.set(entry.topic, {
          total: entry.change,
          current: entry.after,
          count: 1,
        });
      }

      // 정답/오답 추론: change >= 0 이면 정답
      const isCorrect = entry.change >= 0;
      if (isCorrect) correctCount++;

      // 타임라인
      timeline.push({
        date: entry.date,
        elo: entry.after,
        isCorrect,
      });
    });

    // 토픽 성장량 배열로 변환 및 정렬
    const growths: TopicGrowth[] = Array.from(topicMap.entries())
      .map(([topic, data]) => ({
        topic,
        totalChange: data.total,
        currentElo: data.current,
        attempts: data.count,
      }))
      .sort((a, b) => b.totalChange - a.totalChange);

    // 통계 계산
    const totalGain = growths.filter(g => g.totalChange > 0).reduce((sum, g) => sum + g.totalChange, 0);
    const totalLoss = growths.filter(g => g.totalChange < 0).reduce((sum, g) => sum + Math.abs(g.totalChange), 0);
    const netChange = totalGain - totalLoss;

    return {
      topicGrowths: growths,
      eloTimeline: timeline,
      stats: {
        totalGain,
        totalLoss,
        netChange,
        totalAttempts: eloHistory.length,
        correctCount,
      },
    };
  }, [eloHistory]);

  // 데이터 없음
  if (!eloHistory || eloHistory.length === 0) {
    return (
      <div className="p-6 text-center text-zinc-500 text-sm">
        <Zap className="w-8 h-8 mx-auto mb-2 opacity-30" />
        ELO 기록이 없습니다.
        <br />
        <span className="text-xs">문제를 풀면 성장 기록이 표시됩니다.</span>
      </div>
    );
  }

  // 막대 차트용 최대값
  const maxAbsChange = Math.max(
    ...topicGrowths.map(g => Math.abs(g.totalChange)),
    1
  );

  // 라인 차트 계산
  const chartWidth = 320;
  const chartHeight = 120;
  const padding = { left: 12, right: 12, top: 16, bottom: 16 };

  const eloValues = eloTimeline.map(t => t.elo);
  const minElo = Math.min(...eloValues) - 15;
  const maxElo = Math.max(...eloValues) + 15;
  const eloRange = maxElo - minElo || 1;

  const points = eloTimeline.map((entry, idx) => {
    const x = padding.left + (idx / Math.max(eloTimeline.length - 1, 1)) * (chartWidth - padding.left - padding.right);
    const y = padding.top + (1 - (entry.elo - minElo) / eloRange) * (chartHeight - padding.top - padding.bottom);
    return { x, y, ...entry };
  });

  // SVG 경로 생성
  const linePath = points.length > 1
    ? `M ${points.map(p => `${p.x},${p.y}`).join(' L ')}`
    : '';

  // 그라데이션 영역 경로
  const areaPath = points.length > 1
    ? `M ${points[0].x},${chartHeight - padding.bottom} L ${points.map(p => `${p.x},${p.y}`).join(' L ')} L ${points[points.length - 1].x},${chartHeight - padding.bottom} Z`
    : '';

  const currentElo = eloOverall || topicGrowths[0]?.currentElo || 1000;
  const isPositive = stats && stats.netChange >= 0;

  return (
    <div className="p-4 space-y-4">
      {/* 상단: 현재 ELO + 통계 */}
      <div className="flex items-center justify-between">
        <div className="flex items-baseline gap-2">
          <span className="text-3xl font-bold text-zinc-100 tabular-nums tracking-tight">
            {currentElo}
          </span>
          {stats && (
            <span className={`text-sm font-semibold flex items-center gap-0.5 ${
              stats.netChange > 0 ? 'text-emerald-400' :
              stats.netChange < 0 ? 'text-rose-400' : 'text-zinc-500'
            }`}>
              {stats.netChange > 0 ? <TrendingUp className="w-4 h-4" /> :
               stats.netChange < 0 ? <TrendingDown className="w-4 h-4" /> :
               <Minus className="w-4 h-4" />}
              {stats.netChange > 0 ? '+' : ''}{stats.netChange}
            </span>
          )}
        </div>
        <div className="flex items-center gap-3 text-xs text-zinc-500">
          <div className="flex items-center gap-1">
            <div className="w-2 h-2 rounded-full bg-emerald-400" />
            <span>{stats?.correctCount} 정답</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-2 h-2 rounded-full bg-rose-400" />
            <span>{(stats?.totalAttempts || 0) - (stats?.correctCount || 0)} 오답</span>
          </div>
        </div>
      </div>

      {/* 메인 라인 차트 */}
      {points.length > 1 && (
        <div className="relative rounded-xl bg-zinc-800/30 p-3">
          {/* Y축 라벨 */}
          <div className="absolute left-1 top-3 bottom-3 flex flex-col justify-between text-[9px] text-zinc-600 tabular-nums">
            <span>{maxElo}</span>
            <span>{Math.round((maxElo + minElo) / 2)}</span>
            <span>{minElo}</span>
          </div>

          <svg
            viewBox={`0 0 ${chartWidth} ${chartHeight}`}
            className="w-full h-28"
            preserveAspectRatio="xMidYMid meet"
          >
            <defs>
              <linearGradient id="eloAreaGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stopColor={isPositive ? '#10b981' : '#f43f5e'} stopOpacity="0.25" />
                <stop offset="100%" stopColor={isPositive ? '#10b981' : '#f43f5e'} stopOpacity="0.02" />
              </linearGradient>
              <filter id="glow">
                <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
                <feMerge>
                  <feMergeNode in="coloredBlur"/>
                  <feMergeNode in="SourceGraphic"/>
                </feMerge>
              </filter>
            </defs>

            {/* 가로 그리드 라인 */}
            {[0, 0.5, 1].map((ratio, i) => (
              <line
                key={i}
                x1={padding.left}
                y1={padding.top + ratio * (chartHeight - padding.top - padding.bottom)}
                x2={chartWidth - padding.right}
                y2={padding.top + ratio * (chartHeight - padding.top - padding.bottom)}
                stroke="#3f3f46"
                strokeWidth="0.5"
                strokeDasharray="4 4"
              />
            ))}

            {/* 영역 */}
            <motion.path
              d={areaPath}
              fill="url(#eloAreaGradient)"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.8 }}
            />

            {/* 라인 */}
            <motion.path
              d={linePath}
              fill="none"
              stroke={isPositive ? '#10b981' : '#f43f5e'}
              strokeWidth="2.5"
              strokeLinecap="round"
              strokeLinejoin="round"
              filter="url(#glow)"
              initial={{ pathLength: 0 }}
              animate={{ pathLength: 1 }}
              transition={{ duration: 1.2, ease: "easeOut" }}
            />

            {/* 포인트들 */}
            {points.map((point, idx) => (
              <motion.g key={idx}>
                {/* 외부 링 */}
                <motion.circle
                  cx={point.x}
                  cy={point.y}
                  r="6"
                  fill={point.isCorrect ? '#10b981' : '#f43f5e'}
                  fillOpacity="0.2"
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: 0.8 + idx * 0.08 }}
                />
                {/* 내부 점 */}
                <motion.circle
                  cx={point.x}
                  cy={point.y}
                  r="3.5"
                  fill={point.isCorrect ? '#10b981' : '#f43f5e'}
                  stroke="#18181b"
                  strokeWidth="1.5"
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: 0.8 + idx * 0.08, type: "spring" }}
                />
              </motion.g>
            ))}
          </svg>
        </div>
      )}

      {/* 하단: 토픽별 성장량 */}
      {topicGrowths.length > 0 && (
        <div className="space-y-2">
          <div className="flex items-center gap-1.5">
            <Target className="w-3.5 h-3.5 text-zinc-500" />
            <span className="text-[11px] font-medium text-zinc-400">토픽별 성장</span>
          </div>

          <div className="grid gap-1.5">
            {topicGrowths.slice(0, 4).map((growth, idx) => (
              <motion.div
                key={growth.topic}
                className="flex items-center gap-2"
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 1 + idx * 0.05 }}
              >
                {/* 토픽명 */}
                <span className="text-[11px] text-zinc-400 w-20 truncate" title={growth.topic}>
                  {growth.topic}
                </span>

                {/* 막대 그래프 */}
                <div className="flex-1 h-3 flex items-center">
                  <div className="relative w-full h-full flex items-center">
                    <div className="absolute inset-0 bg-zinc-800/50 rounded-full" />
                    <div className="absolute left-1/2 top-0 bottom-0 w-px bg-zinc-700/50" />

                    <motion.div
                      className={`absolute h-2 rounded-full ${
                        growth.totalChange >= 0
                          ? 'left-1/2 bg-gradient-to-r from-emerald-500 to-emerald-400'
                          : 'right-1/2 bg-gradient-to-l from-rose-500 to-rose-400'
                      }`}
                      style={{
                        width: `${(Math.abs(growth.totalChange) / maxAbsChange) * 48}%`,
                      }}
                      initial={{ width: 0 }}
                      animate={{
                        width: `${(Math.abs(growth.totalChange) / maxAbsChange) * 48}%`
                      }}
                      transition={{ duration: 0.5, delay: 1.2 + idx * 0.05 }}
                    />
                  </div>
                </div>

                {/* 변화량 */}
                <span className={`text-[11px] font-semibold w-9 text-right tabular-nums ${
                  growth.totalChange > 0 ? 'text-emerald-400' :
                  growth.totalChange < 0 ? 'text-rose-400' : 'text-zinc-500'
                }`}>
                  {growth.totalChange > 0 ? '+' : ''}{growth.totalChange}
                </span>
              </motion.div>
            ))}

            {topicGrowths.length > 4 && (
              <div className="text-[10px] text-zinc-600 text-center">
                +{topicGrowths.length - 4}개 토픽
              </div>
            )}
          </div>
        </div>
      )}

      {/* 하단 요약 메시지 */}
      {stats && (
        <motion.div
          className={`text-[11px] px-3 py-2 rounded-lg ${
            stats.netChange > 20
              ? 'bg-emerald-500/10 text-emerald-400/90 border border-emerald-500/20'
              : stats.netChange > 0
              ? 'bg-blue-500/10 text-blue-400/90 border border-blue-500/20'
              : stats.netChange < -20
              ? 'bg-rose-500/10 text-rose-400/90 border border-rose-500/20'
              : 'bg-zinc-800/50 text-zinc-400 border border-zinc-700/30'
          }`}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.5 }}
        >
          {stats.netChange > 20
            ? '🔥 빠르게 성장하고 있습니다! 이 페이스를 유지하세요.'
            : stats.netChange > 0
            ? '📈 꾸준히 성장 중입니다. 계속 화이팅!'
            : stats.netChange < -20
            ? '💪 최근 어려운 문제에 도전했네요. 복습이 필요해 보입니다.'
            : '⚡ 실력을 유지하고 있습니다. 새로운 도전을 시도해보세요.'
          }
        </motion.div>
      )}
    </div>
  );
}
