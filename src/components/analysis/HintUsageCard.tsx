'use client';

import { motion } from 'framer-motion';
import { Lightbulb, HelpCircle, ThumbsUp, TrendingUp } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';

interface HintUsageData {
  total_requested: number;
  helpful_count: number;
  helpful_rate: number;
  avg_hint_level: number;
}

interface HintUsageCardProps {
  hintUsage?: HintUsageData;
}

export function HintUsageCard({ hintUsage }: HintUsageCardProps) {
  if (!hintUsage || hintUsage.total_requested === 0) {
    return (
      <motion.div
        className="flex flex-col h-full p-4 rounded-xl bg-zinc-800/30 border border-zinc-700/50"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <h3 className="text-sm font-medium text-zinc-400 uppercase tracking-wider mb-4">
          Hint Usage
        </h3>
        <div className="flex-1 flex items-center justify-center text-zinc-600 text-sm">
          <div className="text-center">
            <Lightbulb className="w-8 h-8 mx-auto mb-2 opacity-50" />
            <p>아직 힌트 사용 기록이 없습니다</p>
          </div>
        </div>
      </motion.div>
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
    <motion.div
      className="flex flex-col h-full p-4 rounded-xl bg-zinc-800/30 border border-zinc-700/50"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3 }}
    >
      <h3 className="text-sm font-medium text-zinc-400 uppercase tracking-wider mb-4">
        Hint Usage
      </h3>

      <div className="flex-1 flex flex-col gap-4">
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
    </motion.div>
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
