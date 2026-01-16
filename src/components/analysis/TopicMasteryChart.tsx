'use client';

import { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { TrendingUp, TrendingDown, X, Quote, BarChart3 } from 'lucide-react';
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
  Tooltip,
} from 'recharts';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import type { BKTMastery, TopicScore } from '@/lib/api/analysis';

interface TopicMasteryChartProps {
  bktMastery: BKTMastery;
  strengths?: TopicScore[];
  weaknesses?: TopicScore[];
  summaryText?: string;
}

// 토픽 이름 축약
function shortenTopic(topic: string): string {
  const shortNames: Record<string, string> = {
    'Dynamic Programming': 'DP',
    'Binary Search': 'BS',
    'Two Pointers': '2P',
    'Divide and Conquer': 'D&C',
    'Breadth First Search': 'BFS',
    'Depth First Search': 'DFS',
  };
  return shortNames[topic] || (topic.length > 10 ? topic.slice(0, 8) + '..' : topic);
}

export function TopicMasteryChart({
  bktMastery,
  strengths = [],
  weaknesses = [],
  summaryText,
}: TopicMasteryChartProps) {
  const [selectedTopic, setSelectedTopic] = useState<{
    topic: string;
    type: 'strength' | 'weakness';
    mastery: number;
    insight: string;
    attemptCount: number;
    correctCount: number;
  } | null>(null);

  // BKT 데이터를 절대적 기준으로 강점/약점 분류
  const { topTopics, bottomTopics, topChartData, bottomChartData, allTopicsSorted } = useMemo(() => {
    const STRENGTH_THRESHOLD = 0.7;  // 70% 이상이면 강점
    const WEAKNESS_THRESHOLD = 0.5;  // 50% 미만이면 약점

    const allTopics = Object.entries(bktMastery)
      .map(([topic, data]) => ({
        topic,
        mastery: data.mastery,
        attemptCount: data.attempt_count,
        correctCount: data.correct_count,
        isMastered: data.is_mastered,
      }));

    // 전체 토픽 (숙련도 높은 순으로 정렬)
    const sortedAll = [...allTopics].sort((a, b) => b.mastery - a.mastery);

    // 강점: 70% 이상, 숙련도 높은 순으로 최대 6개
    const top = allTopics
      .filter(t => t.mastery >= STRENGTH_THRESHOLD)
      .sort((a, b) => b.mastery - a.mastery)
      .slice(0, 6);

    // 약점: 50% 미만, 숙련도 낮은 순으로 최대 6개
    const bottom = allTopics
      .filter(t => t.mastery < WEAKNESS_THRESHOLD)
      .sort((a, b) => a.mastery - b.mastery)
      .slice(0, 6);

    // 레이더 차트용 데이터 변환
    const topData = top.map(t => ({
      topic: shortenTopic(t.topic),
      fullTopic: t.topic,
      value: Math.round(t.mastery * 100),
      attemptCount: t.attemptCount,
      correctCount: t.correctCount,
      fullMark: 100,
    }));

    // 약점은 반전: 숙련도가 낮을수록 차트가 크게 표시 (부족한 정도를 시각화)
    const bottomData = bottom.map(t => ({
      topic: shortenTopic(t.topic),
      fullTopic: t.topic,
      value: Math.round((1 - t.mastery) * 100), // 반전!
      originalValue: Math.round(t.mastery * 100), // 원본 값 보존
      attemptCount: t.attemptCount,
      correctCount: t.correctCount,
      fullMark: 100,
    }));

    return {
      topTopics: top,
      bottomTopics: bottom,
      topChartData: topData,
      bottomChartData: bottomData,
      allTopicsSorted: sortedAll,
    };
  }, [bktMastery]);

  // 토픽 클릭 핸들러
  const handleTopicClick = (
    fullTopic: string,
    type: 'strength' | 'weakness',
    mastery: number,
    attemptCount: number,
    correctCount: number
  ) => {
    if (selectedTopic?.topic === fullTopic) {
      setSelectedTopic(null);
      return;
    }

    const list = type === 'strength' ? strengths : weaknesses;
    const item = list.find(s => s.topic === fullTopic);

    setSelectedTopic({
      topic: fullTopic,
      type,
      mastery,
      insight: item?.insight || '이 토픽에 대한 상세 분석이 없습니다.',
      attemptCount,
      correctCount,
    });
  };

  const totalTopics = Object.keys(bktMastery).length;

  if (totalTopics === 0) {
    return (
      <div className="p-8 text-center text-zinc-500">
        토픽 데이터가 없습니다.
      </div>
    );
  }

  // 레이더 차트가 최소 3개 필요
  const canShowStrengthRadar = topChartData.length >= 3;
  const canShowWeaknessRadar = bottomChartData.length >= 3;
  const canShowAnyRadar = canShowStrengthRadar || canShowWeaknessRadar;

  // 숙련도 색상 결정
  const getMasteryColor = (mastery: number) => {
    if (mastery >= 0.7) return 'text-emerald-400';
    if (mastery >= 0.5) return 'text-yellow-400';
    return 'text-orange-400';
  };

  const getMasteryBgColor = (mastery: number) => {
    if (mastery >= 0.7) return 'bg-emerald-500';
    if (mastery >= 0.5) return 'bg-yellow-500';
    return 'bg-orange-500';
  };

  return (
    <div className="p-5">
      {/* AI Summary Quote + 전체 보기 버튼 */}
      <div className="flex items-start justify-between gap-4 mb-5">
        {summaryText && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="relative flex-1"
          >
            <div className="absolute -left-1 -top-1 text-primary/30">
              <Quote className="w-6 h-6" />
            </div>
            <p className="text-sm text-zinc-300 leading-relaxed italic pl-6 pr-4">
              {summaryText}
            </p>
          </motion.div>
        )}

        {/* 전체 토픽 보기 Popover */}
        <Popover>
          <PopoverTrigger asChild>
            <button className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-zinc-800 hover:bg-zinc-700 border border-zinc-700 text-xs text-zinc-300 hover:text-zinc-100 transition-colors flex-shrink-0">
              <BarChart3 className="w-3.5 h-3.5" />
              <span>전체 보기</span>
              <span className="text-zinc-500 ml-0.5">{allTopicsSorted.length}</span>
            </button>
          </PopoverTrigger>
          <PopoverContent
            align="end"
            className="w-72 p-0 bg-zinc-900 border-zinc-700"
          >
            <div className="px-3 py-2.5 border-b border-zinc-800">
              <h4 className="text-sm font-semibold text-zinc-100">전체 토픽 숙련도</h4>
              <p className="text-[10px] text-zinc-500 mt-0.5">BKT 기반 · 총 {allTopicsSorted.length}개 토픽</p>
            </div>
            <div className="max-h-64 overflow-y-auto">
              {allTopicsSorted.map((item, index) => {
                const percent = Math.round(item.mastery * 100);
                return (
                  <div
                    key={item.topic}
                    className={`px-3 py-2 flex items-center gap-3 ${
                      index !== allTopicsSorted.length - 1 ? 'border-b border-zinc-800/50' : ''
                    }`}
                  >
                    <div className="flex-1 min-w-0">
                      <p className="text-xs text-zinc-200 truncate">{item.topic}</p>
                      <p className="text-[10px] text-zinc-500">
                        {item.correctCount}/{item.attemptCount} 정답
                      </p>
                    </div>
                    <div className="flex items-center gap-2 flex-shrink-0">
                      <div className="w-16 h-1.5 bg-zinc-800 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full ${getMasteryBgColor(item.mastery)}`}
                          style={{ width: `${percent}%` }}
                        />
                      </div>
                      <span className={`text-xs font-medium w-9 text-right ${getMasteryColor(item.mastery)}`}>
                        {percent}%
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
            <div className="px-3 py-2 border-t border-zinc-800 bg-zinc-900/50">
              <div className="flex items-center justify-center gap-4 text-[10px]">
                <div className="flex items-center gap-1">
                  <div className="w-2 h-2 rounded-full bg-emerald-500" />
                  <span className="text-zinc-500">70%↑</span>
                </div>
                <div className="flex items-center gap-1">
                  <div className="w-2 h-2 rounded-full bg-yellow-500" />
                  <span className="text-zinc-500">50-70%</span>
                </div>
                <div className="flex items-center gap-1">
                  <div className="w-2 h-2 rounded-full bg-orange-500" />
                  <span className="text-zinc-500">50%↓</span>
                </div>
              </div>
            </div>
          </PopoverContent>
        </Popover>
      </div>

      {canShowAnyRadar ? (
        /* Dual Radar Charts */
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* 강점 레이더 */}
          {canShowStrengthRadar ? (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="bg-emerald-500/5 rounded-xl border border-emerald-500/10 p-4"
            >
              <div className="flex items-center gap-2 mb-3">
                <div className="w-6 h-6 rounded-md bg-emerald-500/15 flex items-center justify-center">
                  <TrendingUp className="w-3.5 h-3.5 text-emerald-400" />
                </div>
                <div>
                  <h4 className="text-sm font-semibold text-emerald-300">강점 토픽</h4>
                  <p className="text-[10px] text-zinc-500">숙련도 70% 이상</p>
                </div>
              </div>

              <div className="flex gap-3">
                {/* 레이더 차트 */}
                <div className="w-[180px] h-[180px] flex-shrink-0">
                  <ResponsiveContainer width="100%" height="100%">
                    <RadarChart data={topChartData} margin={{ top: 15, right: 25, bottom: 15, left: 25 }}>
                      <PolarGrid stroke="#3f3f46" strokeDasharray="3 3" />
                      <PolarAngleAxis
                        dataKey="topic"
                        tick={{ fill: '#a1a1aa', fontSize: 9 }}
                        tickLine={false}
                      />
                      <PolarRadiusAxis
                        angle={90}
                        domain={[0, 100]}
                        tick={false}
                        axisLine={false}
                      />
                      <Radar
                        name="숙련도"
                        dataKey="value"
                        stroke="#22c55e"
                        fill="#22c55e"
                        fillOpacity={0.3}
                        strokeWidth={2}
                        dot={{ r: 2, fill: '#22c55e', strokeWidth: 0 }}
                        animationBegin={200}
                        animationDuration={800}
                      />
                      <Tooltip
                        content={({ active, payload }) => {
                          if (!active || !payload || payload.length === 0) return null;
                          const data = payload[0].payload;
                          return (
                            <div className="bg-zinc-900 border border-zinc-700 rounded-lg px-3 py-2 shadow-lg">
                              <p className="text-sm font-medium text-zinc-200">{data.fullTopic}</p>
                              <p className="text-xs text-emerald-400 mt-1">
                                숙련도: <span className="font-bold">{data.value}%</span>
                              </p>
                              <p className="text-[10px] text-zinc-500">
                                {data.correctCount}/{data.attemptCount} 정답
                              </p>
                            </div>
                          );
                        }}
                      />
                    </RadarChart>
                  </ResponsiveContainer>
                </div>

                {/* 토픽 리스트 */}
                <div className="flex-1 space-y-1.5">
                  {topChartData.map((item) => (
                    <button
                      key={item.fullTopic}
                      onClick={() => handleTopicClick(item.fullTopic, 'strength', item.value / 100, item.attemptCount, item.correctCount)}
                      className={`
                        w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-left transition-all
                        ${selectedTopic?.topic === item.fullTopic
                          ? 'bg-emerald-500/20 ring-1 ring-emerald-500/30'
                          : 'bg-zinc-800/30 hover:bg-emerald-500/10'
                        }
                      `}
                    >
                      <span className="text-xs text-zinc-300 truncate">{item.fullTopic}</span>
                      <span className="text-xs font-semibold text-emerald-400 ml-2">{item.value}%</span>
                    </button>
                  ))}
                </div>
              </div>
            </motion.div>
          ) : (
            <div className="bg-zinc-800/30 rounded-xl border border-zinc-700/30 p-6 flex items-center justify-center">
              <div className="text-center">
                <TrendingUp className="w-8 h-8 text-zinc-600 mx-auto mb-2" />
                <p className="text-sm text-zinc-500">70% 이상 토픽이 부족합니다</p>
                <p className="text-xs text-zinc-600 mt-1">{topChartData.length}개 해당</p>
              </div>
            </div>
          )}

          {/* 약점 레이더 */}
          {canShowWeaknessRadar ? (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.1 }}
              className="bg-orange-500/5 rounded-xl border border-orange-500/10 p-4"
            >
              <div className="flex items-center gap-2 mb-3">
                <div className="w-6 h-6 rounded-md bg-orange-500/15 flex items-center justify-center">
                  <TrendingDown className="w-3.5 h-3.5 text-orange-400" />
                </div>
                <div>
                  <h4 className="text-sm font-semibold text-orange-300">약점 토픽</h4>
                  <p className="text-[10px] text-zinc-500">숙련도 50% 미만</p>
                </div>
              </div>

              <div className="flex gap-3">
                {/* 레이더 차트 */}
                <div className="w-[180px] h-[180px] flex-shrink-0">
                  <ResponsiveContainer width="100%" height="100%">
                    <RadarChart data={bottomChartData} margin={{ top: 15, right: 25, bottom: 15, left: 25 }}>
                      <PolarGrid stroke="#3f3f46" strokeDasharray="3 3" />
                      <PolarAngleAxis
                        dataKey="topic"
                        tick={{ fill: '#a1a1aa', fontSize: 9 }}
                        tickLine={false}
                      />
                      <PolarRadiusAxis
                        angle={90}
                        domain={[0, 100]}
                        tick={false}
                        axisLine={false}
                      />
                      <Radar
                        name="부족도"
                        dataKey="value"
                        stroke="#f97316"
                        fill="#f97316"
                        fillOpacity={0.3}
                        strokeWidth={2}
                        dot={{ r: 2, fill: '#f97316', strokeWidth: 0 }}
                        animationBegin={200}
                        animationDuration={800}
                      />
                      <Tooltip
                        content={({ active, payload }) => {
                          if (!active || !payload || payload.length === 0) return null;
                          const data = payload[0].payload;
                          return (
                            <div className="bg-zinc-900 border border-zinc-700 rounded-lg px-3 py-2 shadow-lg">
                              <p className="text-sm font-medium text-zinc-200">{data.fullTopic}</p>
                              <p className="text-xs text-orange-400 mt-1">
                                숙련도: <span className="font-bold">{data.originalValue}%</span>
                              </p>
                              <p className="text-[10px] text-zinc-500">
                                {data.correctCount}/{data.attemptCount} 정답
                              </p>
                            </div>
                          );
                        }}
                      />
                    </RadarChart>
                  </ResponsiveContainer>
                </div>

                {/* 토픽 리스트 */}
                <div className="flex-1 space-y-1.5">
                  {bottomChartData.map((item) => (
                    <button
                      key={item.fullTopic}
                      onClick={() => handleTopicClick(item.fullTopic, 'weakness', item.originalValue / 100, item.attemptCount, item.correctCount)}
                      className={`
                        w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-left transition-all
                        ${selectedTopic?.topic === item.fullTopic
                          ? 'bg-orange-500/20 ring-1 ring-orange-500/30'
                          : 'bg-zinc-800/30 hover:bg-orange-500/10'
                        }
                      `}
                    >
                      <span className="text-xs text-zinc-300 truncate">{item.fullTopic}</span>
                      <span className="text-xs font-semibold text-orange-400 ml-2">{item.originalValue}%</span>
                    </button>
                  ))}
                </div>
              </div>
            </motion.div>
          ) : (
            <div className="bg-zinc-800/30 rounded-xl border border-zinc-700/30 p-6 flex items-center justify-center">
              <div className="text-center">
                <TrendingDown className="w-8 h-8 text-zinc-600 mx-auto mb-2" />
                <p className="text-sm text-zinc-500">50% 미만 토픽이 없습니다</p>
                <p className="text-xs text-emerald-500 mt-1">잘하고 있어요!</p>
              </div>
            </div>
          )}
        </div>
      ) : (
        /* 기준에 맞는 토픽이 없을 때 */
        <div className="text-center py-8">
          <p className="text-sm text-zinc-500">분석할 강점/약점 토픽이 부족합니다</p>
          <p className="text-xs text-zinc-600 mt-2">
            강점: 70% 이상 {topChartData.length}개 · 약점: 50% 미만 {bottomChartData.length}개
          </p>
          <p className="text-xs text-zinc-600">레이더 차트는 최소 3개 토픽이 필요합니다</p>
        </div>
      )}

      {/* 선택된 토픽 상세 정보 */}
      <AnimatePresence>
        {selectedTopic && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="mt-4"
          >
            <div
              className={`
                p-4 rounded-xl border
                ${selectedTopic.type === 'strength'
                  ? 'bg-emerald-500/5 border-emerald-500/20'
                  : 'bg-orange-500/5 border-orange-500/20'
                }
              `}
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-center gap-2">
                  <div
                    className={`w-7 h-7 rounded-lg flex items-center justify-center ${
                      selectedTopic.type === 'strength' ? 'bg-emerald-500/20' : 'bg-orange-500/20'
                    }`}
                  >
                    {selectedTopic.type === 'strength' ? (
                      <TrendingUp className="w-4 h-4 text-emerald-400" />
                    ) : (
                      <TrendingDown className="w-4 h-4 text-orange-400" />
                    )}
                  </div>
                  <div>
                    <span
                      className={`text-sm font-semibold ${
                        selectedTopic.type === 'strength' ? 'text-emerald-300' : 'text-orange-300'
                      }`}
                    >
                      {selectedTopic.topic}
                    </span>
                    <div className="flex items-center gap-2 mt-0.5">
                      <span className="text-xs text-zinc-400">
                        숙련도 {Math.round(selectedTopic.mastery * 100)}%
                      </span>
                      <span className="text-[10px] text-zinc-600">•</span>
                      <span className="text-[10px] text-zinc-500">
                        {selectedTopic.correctCount}/{selectedTopic.attemptCount} 정답
                      </span>
                    </div>
                  </div>
                </div>
                <button
                  onClick={() => setSelectedTopic(null)}
                  className="text-zinc-500 hover:text-zinc-300 transition-colors p-1"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
              <p className="text-sm text-zinc-400 leading-relaxed mt-3 pl-9">
                {selectedTopic.insight}
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
