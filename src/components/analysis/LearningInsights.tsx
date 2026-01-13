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
  Brain,
  MessageCircle,
} from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';

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

  if (!hasMoodData && !hasLearningStyle && teachingNotes.length === 0) {
    return (
      <div className="p-6">
        <div className="flex items-center gap-2 mb-6">
          <Brain className="w-5 h-5 text-violet-400" />
          <h3 className="text-base font-semibold text-zinc-100">Learning Insights</h3>
        </div>
        <div className="flex items-center justify-center py-12 text-zinc-600 text-sm">
          <p>학습 스타일 분석 데이터가 없습니다</p>
        </div>
      </div>
    );
  }

  // 감정 분포 차트 데이터
  const moodChartData = Object.entries(moodDistribution).map(([mood, count]) => ({
    mood,
    count,
    label: moodConfig[mood]?.label || mood,
    color: moodConfig[mood]?.color || '#71717a',
  })).sort((a, b) => b.count - a.count);

  const totalMoodCount = moodChartData.reduce((sum, item) => sum + item.count, 0);

  // 가장 많은 감정 (안전한 접근)
  const dominantMood = moodChartData.length > 0 ? moodChartData[0] : null;

  // 학습 스타일 항목들
  const styleItems = [];
  if (learningStyle?.prefers_examples) {
    styleItems.push({
      icon: <Code2 className="w-5 h-5" />,
      label: '예시 코드 선호',
      description: '코드 예제를 통해 학습할 때 효과적',
      color: 'text-blue-400',
      bgColor: 'bg-blue-500/10',
      borderColor: 'border-blue-500/20',
    });
  }
  if (learningStyle?.prefers_analogies) {
    styleItems.push({
      icon: <BookOpen className="w-5 h-5" />,
      label: '비유 설명 선호',
      description: '실생활 비유로 개념을 이해',
      color: 'text-emerald-400',
      bgColor: 'bg-emerald-500/10',
      borderColor: 'border-emerald-500/20',
    });
  }
  if (learningStyle?.hint_sensitivity) {
    const sensitivityConfig: Record<string, {
      label: string;
      description: string;
      color: string;
      bgColor: string;
      borderColor: string;
    }> = {
      low: {
        label: '힌트 적게 사용',
        description: '독립적으로 문제 해결 선호',
        color: 'text-amber-400',
        bgColor: 'bg-amber-500/10',
        borderColor: 'border-amber-500/20',
      },
      medium: {
        label: '적절한 힌트 사용',
        description: '필요시 힌트 활용',
        color: 'text-cyan-400',
        bgColor: 'bg-cyan-500/10',
        borderColor: 'border-cyan-500/20',
      },
      high: {
        label: '힌트 적극 활용',
        description: '단계별 가이드 선호',
        color: 'text-violet-400',
        bgColor: 'bg-violet-500/10',
        borderColor: 'border-violet-500/20',
      },
    };
    const config = sensitivityConfig[learningStyle.hint_sensitivity] || sensitivityConfig.medium;
    styleItems.push({
      icon: <Zap className="w-5 h-5" />,
      label: config.label,
      description: config.description,
      color: config.color,
      bgColor: config.bgColor,
      borderColor: config.borderColor,
    });
  }
  if (learningStyle?.pace) {
    const paceConfig: Record<string, {
      label: string;
      description: string;
      color: string;
      bgColor: string;
      borderColor: string;
    }> = {
      slow: {
        label: '천천히 꼼꼼하게',
        description: '깊이 있는 이해 추구',
        color: 'text-rose-400',
        bgColor: 'bg-rose-500/10',
        borderColor: 'border-rose-500/20',
      },
      medium: {
        label: '적당한 속도',
        description: '균형 잡힌 학습 패턴',
        color: 'text-sky-400',
        bgColor: 'bg-sky-500/10',
        borderColor: 'border-sky-500/20',
      },
      fast: {
        label: '빠르게 진행',
        description: '효율적인 학습 선호',
        color: 'text-lime-400',
        bgColor: 'bg-lime-500/10',
        borderColor: 'border-lime-500/20',
      },
    };
    const config = paceConfig[learningStyle.pace] || paceConfig.medium;
    styleItems.push({
      icon: <Gauge className="w-5 h-5" />,
      label: config.label,
      description: config.description,
      color: config.color,
      bgColor: config.bgColor,
      borderColor: config.borderColor,
    });
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex items-center gap-2 mb-6">
        <Brain className="w-5 h-5 text-violet-400" />
        <h3 className="text-base font-semibold text-zinc-100">Learning Insights</h3>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 감정 분포 도넛 차트 */}
        {hasMoodData && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.1 }}
            className="lg:col-span-1"
          >
            <h4 className="text-xs text-zinc-500 uppercase tracking-wide mb-3">학습 중 감정</h4>
            <div className="relative">
              <div className="h-48">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={moodChartData}
                      cx="50%"
                      cy="50%"
                      innerRadius={50}
                      outerRadius={70}
                      paddingAngle={3}
                      dataKey="count"
                    >
                      {moodChartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip
                      content={({ active, payload }) => {
                        if (!active || !payload?.length) return null;
                        const data = payload[0].payload;
                        const percentage = Math.round((data.count / totalMoodCount) * 100);
                        return (
                          <div className="bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-2 text-xs shadow-lg">
                            <div className="font-medium text-zinc-200">{data.label}</div>
                            <div className="text-zinc-400">{data.count}회 ({percentage}%)</div>
                          </div>
                        );
                      }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>

              {/* 중앙 텍스트 */}
              {dominantMood && (
                <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                  <div className="text-center">
                    <div className="flex justify-center mb-1" style={{ color: dominantMood.color }}>
                      {moodConfig[dominantMood.mood]?.icon}
                    </div>
                    <div className="text-xs text-zinc-400">{dominantMood.label}</div>
                  </div>
                </div>
              )}
            </div>

            {/* 감정 레전드 */}
            <div className="mt-4 grid grid-cols-2 gap-2">
              {moodChartData.slice(0, 4).map((item, index) => (
                <motion.div
                  key={item.mood}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.2 + index * 0.05 }}
                  className="flex items-center gap-2"
                >
                  <div
                    className="w-2.5 h-2.5 rounded-full"
                    style={{ backgroundColor: item.color }}
                  />
                  <span className="text-xs text-zinc-400">
                    {item.label} ({Math.round((item.count / totalMoodCount) * 100)}%)
                  </span>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}

        {/* 학습 스타일 카드들 */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15 }}
          className={`${hasMoodData ? 'lg:col-span-2' : 'lg:col-span-3'}`}
        >
          <h4 className="text-xs text-zinc-500 uppercase tracking-wide mb-3">학습 스타일</h4>
          {styleItems.length > 0 ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {styleItems.map((item, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2 + index * 0.08 }}
                  className={`p-4 rounded-xl ${item.bgColor} border ${item.borderColor} hover:scale-[1.02] transition-transform`}
                >
                  <div className="flex items-start gap-3">
                    <div className={`${item.color} mt-0.5`}>{item.icon}</div>
                    <div>
                      <div className="font-medium text-zinc-200 text-sm">{item.label}</div>
                      <div className="text-xs text-zinc-500 mt-0.5">{item.description}</div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          ) : (
            <div className="p-8 rounded-xl bg-zinc-800/30 border border-zinc-700/50 text-center">
              <p className="text-sm text-zinc-500">더 많은 문제를 풀면 학습 스타일이 분석됩니다</p>
            </div>
          )}

          {/* 효과적이었던 교육 노트 */}
          {teachingNotes.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.35 }}
              className="mt-4"
            >
              <div className="flex items-center gap-2 mb-3">
                <MessageCircle className="w-4 h-4 text-zinc-500" />
                <h4 className="text-xs text-zinc-500 uppercase tracking-wide">효과적이었던 설명</h4>
              </div>
              <div className="space-y-2">
                {teachingNotes.slice(0, 3).map((note, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.4 + index * 0.05 }}
                    className="p-3 rounded-lg bg-zinc-800/40 border border-zinc-700/30"
                  >
                    <p className="text-xs text-zinc-400 leading-relaxed line-clamp-2">{note}</p>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          )}
        </motion.div>
      </div>
    </div>
  );
}
