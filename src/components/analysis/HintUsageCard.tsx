'use client';

import { Lightbulb, HelpCircle, ThumbsUp, TrendingUp } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';

interface HintUsageData {
  total_requested: number;
  by_level?: Record<string, number>; // 레벨별 힌트 사용 횟수
  helpful_count: number;
  helpful_rate: number;
  avg_per_problem?: number; // 문제당 평균 힌트 수
  avg_hint_level: number;
}

interface HintUsageCardProps {
  hintUsage?: HintUsageData;
}

export function HintUsageCard({ hintUsage }: HintUsageCardProps) {
  if (!hintUsage || hintUsage.total_requested === 0) {
    return (
      <div className="p-6">
        <div className="flex items-center gap-2 mb-1.5">
          <Lightbulb className="w-5 h-5 text-amber-400" />
          <h3 className="text-base font-semibold text-zinc-100">힌트 사용 패턴</h3>
        </div>
        <p className="text-xs text-zinc-500 mb-4">
          힌트를 언제, 얼마나 사용하는지 분석합니다.
        </p>
        <div className="flex items-center justify-center py-8 text-zinc-600 text-sm">
          <p>힌트 사용 기록이 쌓이면 패턴이 표시됩니다</p>
        </div>
      </div>
    );
  }

  const { total_requested, helpful_count, helpful_rate, avg_hint_level } = hintUsage;
  const notHelpfulCount = total_requested - helpful_count;

  const pieData = [
    { name: '도움됨', value: helpful_count },
    { name: '미도움', value: notHelpfulCount },
  ];

  // 힌트 레벨에 따른 평가
  const getLevelAssessment = (level: number) => {
    if (level <= 1) return { text: '최소 힌트', color: '#22c55e' };
    if (level <= 2) return { text: '적절한 힌트', color: '#3b82f6' };
    return { text: '많은 힌트', color: '#eab308' };
  };

  const levelAssessment = getLevelAssessment(avg_hint_level);

  return (
    <div className="p-6">
      <div className="mb-4">
        <div className="flex items-center gap-2 mb-1.5">
          <Lightbulb className="w-5 h-5 text-amber-400" />
          <h3 className="text-base font-semibold text-zinc-100">힌트 사용 패턴</h3>
        </div>
        <p className="text-xs text-zinc-500">
          힌트 의존도가 낮을수록 스스로 해결하는 능력이 높습니다.
        </p>
      </div>

      <div className="flex flex-col gap-4">
        {/* 파이 차트 */}
        <div className="flex items-center gap-4">
          <div className="w-20 h-20">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={20}
                  outerRadius={35}
                  paddingAngle={2}
                  dataKey="value"
                >
                  {pieData.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={index === 0 ? '#22c55e' : '#52525b'} />
                  ))}
                </Pie>
                <Tooltip
                  content={({ active, payload }) => {
                    if (!active || !payload?.length) return null;
                    const data = payload[0];
                    return (
                      <div className="bg-zinc-800 border border-zinc-700 rounded-lg px-2 py-1 text-xs">
                        {data.name}: {data.value}회
                      </div>
                    );
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="flex-1">
            <div className="text-2xl font-bold text-zinc-100">
              {Math.round(helpful_rate * 100)}%
            </div>
            <div className="text-xs text-zinc-500">힌트 도움률</div>
          </div>
        </div>

        {/* 통계 그리드 */}
        <div className="grid grid-cols-2 gap-2">
          <StatBox
            icon={<HelpCircle className="w-4 h-4" />}
            label="총 요청"
            value={`${total_requested}회`}
            color="#3b82f6"
          />
          <StatBox
            icon={<ThumbsUp className="w-4 h-4" />}
            label="도움됨"
            value={`${helpful_count}회`}
            color="#22c55e"
          />
        </div>

        {/* 평균 힌트 레벨 */}
        <div className="flex items-center justify-between p-2 rounded-lg bg-zinc-900/50">
          <div className="flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-zinc-500" />
            <span className="text-xs text-zinc-400">평균 힌트 레벨</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm font-bold" style={{ color: levelAssessment.color }}>
              {avg_hint_level.toFixed(1)}
            </span>
            <span className="text-xs px-1.5 py-0.5 rounded" style={{ backgroundColor: `${levelAssessment.color}20`, color: levelAssessment.color }}>
              {levelAssessment.text}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatBox({
  icon,
  label,
  value,
  color,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  color: string;
}) {
  return (
    <div className="flex items-center gap-2 p-2 rounded-lg bg-zinc-900/50">
      <div style={{ color }} className="opacity-80">
        {icon}
      </div>
      <div>
        <div className="text-sm font-bold text-zinc-100">{value}</div>
        <div className="text-[10px] text-zinc-500">{label}</div>
      </div>
    </div>
  );
}
