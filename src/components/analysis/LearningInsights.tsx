'use client';

import { motion } from 'framer-motion';
import {
  BookOpen,
  Zap,
  Gauge,
  Code2,
  Smile,
  Frown,
  Meh,
  HelpCircle,
  Sparkles,
  Coffee,
} from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Tooltip, Cell } from 'recharts';

interface LearningStyleData {
  prefers_examples?: boolean;
  prefers_analogies?: boolean;
  hint_sensitivity?: string;
  pace?: string;
}

interface LearningInsightsProps {
  learningStyle?: LearningStyleData;
  moodDistribution: Record<string, number>;
  teachingNotes?: string[];
}

// 감정에 따른 아이콘과 색상
const moodConfig: Record<string, { icon: React.ReactNode; color: string; label: string }> = {
  curious: { icon: <Sparkles className="w-4 h-4" />, color: '#3b82f6', label: '호기심' },
  confident: { icon: <Smile className="w-4 h-4" />, color: '#22c55e', label: '자신감' },
  frustrated: { icon: <Frown className="w-4 h-4" />, color: '#ef4444', label: '좌절' },
  confused: { icon: <HelpCircle className="w-4 h-4" />, color: '#f97316', label: '혼란' },
  neutral: { icon: <Meh className="w-4 h-4" />, color: '#71717a', label: '보통' },
  tired: { icon: <Coffee className="w-4 h-4" />, color: '#a855f7', label: '피로' },
};

export function LearningInsights({
  learningStyle,
  moodDistribution,
  teachingNotes = [],
}: LearningInsightsProps) {
  const hasMoodData = Object.keys(moodDistribution).length > 0;
  const hasLearningStyle = learningStyle && Object.keys(learningStyle).length > 0;

  if (!hasMoodData && !hasLearningStyle) {
    return (
      <motion.div
        className="p-4 rounded-xl bg-zinc-800/30 border border-zinc-700/50"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
      >
        <h3 className="text-sm font-medium text-zinc-400 uppercase tracking-wider mb-4">
          Learning Insights
        </h3>
        <div className="flex items-center justify-center py-8 text-zinc-600 text-sm">
          <p>학습 스타일 분석 데이터가 없습니다</p>
        </div>
      </motion.div>
    );
  }

  // 감정 분포 차트 데이터
  const moodChartData = Object.entries(moodDistribution).map(([mood, count]) => ({
    mood,
    count,
    label: moodConfig[mood]?.label || mood,
    color: moodConfig[mood]?.color || '#71717a',
  })).sort((a, b) => b.count - a.count);

  // 학습 스타일 항목들
  const styleItems = [];
  if (learningStyle?.prefers_examples) {
    styleItems.push({ icon: <Code2 className="w-4 h-4" />, label: '예시 코드 선호', active: true });
  }
  if (learningStyle?.prefers_analogies) {
    styleItems.push({ icon: <BookOpen className="w-4 h-4" />, label: '비유 설명 선호', active: true });
  }
  if (learningStyle?.hint_sensitivity) {
    const sensitivityLabels: Record<string, string> = {
      low: '힌트 적게 사용',
      medium: '적절한 힌트 사용',
      high: '힌트 많이 사용',
    };
    styleItems.push({
      icon: <Zap className="w-4 h-4" />,
      label: sensitivityLabels[learningStyle.hint_sensitivity] || '힌트 사용',
      active: true,
    });
  }
  if (learningStyle?.pace) {
    const paceLabels: Record<string, string> = {
      slow: '천천히 꼼꼼하게',
      medium: '적당한 속도',
      fast: '빠르게 진행',
    };
    styleItems.push({
      icon: <Gauge className="w-4 h-4" />,
      label: paceLabels[learningStyle.pace] || '학습 속도',
      active: true,
    });
  }

  return (
    <motion.div
      className="p-4 rounded-xl bg-zinc-800/30 border border-zinc-700/50"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.5 }}
    >
      <h3 className="text-sm font-medium text-zinc-400 uppercase tracking-wider mb-4">
        Learning Insights
      </h3>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 학습 스타일 */}
        {styleItems.length > 0 && (
          <div>
            <h4 className="text-xs text-zinc-500 mb-3">학습 스타일</h4>
            <div className="grid grid-cols-2 gap-2">
              {styleItems.map((item, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.1 * index }}
                  className="flex items-center gap-2 p-2.5 rounded-lg bg-zinc-900/50 border border-zinc-700/50"
                >
                  <div className="text-primary">{item.icon}</div>
                  <span className="text-xs text-zinc-300">{item.label}</span>
                </motion.div>
              ))}
            </div>
          </div>
        )}

        {/* 감정 분포 */}
        {hasMoodData && (
          <div>
            <h4 className="text-xs text-zinc-500 mb-3">학습 중 감정 분포</h4>
            <div className="h-32">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={moodChartData} layout="vertical">
                  <XAxis type="number" hide />
                  <YAxis
                    type="category"
                    dataKey="label"
                    tick={{ fill: '#a1a1aa', fontSize: 11 }}
                    width={60}
                    axisLine={false}
                    tickLine={false}
                  />
                  <Tooltip
                    content={({ active, payload }) => {
                      if (!active || !payload?.length) return null;
                      const data = payload[0].payload;
                      return (
                        <div className="bg-zinc-800 border border-zinc-700 rounded-lg px-2 py-1 text-xs">
                          {data.label}: {data.count}회
                        </div>
                      );
                    }}
                  />
                  <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                    {moodChartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}
      </div>

      {/* 효과적이었던 교육 노트 */}
      {teachingNotes.length > 0 && (
        <div className="mt-4 pt-4 border-t border-zinc-700/50">
          <h4 className="text-xs text-zinc-500 mb-3">효과적이었던 설명 방식</h4>
          <div className="space-y-2">
            {teachingNotes.slice(0, 3).map((note, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.2 + 0.1 * index }}
                className="flex items-start gap-2 text-xs text-zinc-400"
              >
                <span className="text-primary mt-0.5">-</span>
                <span className="line-clamp-2">{note}</span>
              </motion.div>
            ))}
          </div>
        </div>
      )}
    </motion.div>
  );
}
