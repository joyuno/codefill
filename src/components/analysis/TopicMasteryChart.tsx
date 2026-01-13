'use client';

import { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, ChevronUp, Zap, Target, X, Quote } from 'lucide-react';
import type { BKTMastery, TopicScore } from '@/lib/api/analysis';

interface TopicMasteryChartProps {
  bktMastery: BKTMastery;
  strengths?: TopicScore[];
  weaknesses?: TopicScore[];
  summaryText?: string;
}

interface TopicData {
  topic: string;
  mastery: number;
  attemptCount: number;
  correctCount: number;
  isMastered: boolean;
}

// 숙련도에 따른 색상
function getMasteryColor(mastery: number): { bar: string; text: string; bg: string } {
  if (mastery >= 0.8) return { bar: '#22c55e', text: 'text-emerald-400', bg: 'bg-emerald-500/10' };
  if (mastery >= 0.5) return { bar: '#eab308', text: 'text-yellow-400', bg: 'bg-yellow-500/10' };
  return { bar: '#ef4444', text: 'text-red-400', bg: 'bg-red-500/10' };
}

export function TopicMasteryChart({
  bktMastery,
  strengths = [],
  weaknesses = [],
  summaryText,
}: TopicMasteryChartProps) {
  const [showAll, setShowAll] = useState(false);
  const [selectedTopic, setSelectedTopic] = useState<{
    topic: string;
    type: 'strength' | 'weakness';
    score: number;
    insight: string;
  } | null>(null);

  // 데이터 변환 및 정렬
  const sortedTopics = useMemo(() => {
    return Object.entries(bktMastery)
      .map(([topic, data]) => ({
        topic,
        mastery: data.mastery,
        attemptCount: data.attempt_count,
        correctCount: data.correct_count,
        isMastered: data.is_mastered,
      }))
      .sort((a, b) => b.mastery - a.mastery);
  }, [bktMastery]);

  // 표시할 토픽 (기본 6개, 전체보기 시 전체)
  const displayTopics = showAll ? sortedTopics : sortedTopics.slice(0, 6);
  const hasMore = sortedTopics.length > 6;

  // 통계
  const stats = useMemo(() => {
    const masteredCount = sortedTopics.filter(t => t.mastery >= 0.8).length;
    const learningCount = sortedTopics.filter(t => t.mastery >= 0.5 && t.mastery < 0.8).length;
    const weakCount = sortedTopics.filter(t => t.mastery < 0.5).length;
    const avgMastery = sortedTopics.length > 0
      ? sortedTopics.reduce((sum, t) => sum + t.mastery, 0) / sortedTopics.length
      : 0;
    return { masteredCount, learningCount, weakCount, avgMastery, total: sortedTopics.length };
  }, [sortedTopics]);

  // 토픽 클릭 핸들러
  const handleTopicClick = (topic: string, type: 'strength' | 'weakness') => {
    const list = type === 'strength' ? strengths : weaknesses;
    const item = list.find(s => s.topic === topic);

    if (selectedTopic?.topic === topic) {
      setSelectedTopic(null);
    } else if (item) {
      setSelectedTopic({
        topic: item.topic,
        type,
        score: item.score,
        insight: item.insight || '',
      });
    }
  };

  if (sortedTopics.length === 0) {
    return (
      <div className="p-8 text-center text-zinc-500">
        토픽 데이터가 없습니다.
      </div>
    );
  }

  return (
    <div className="p-5">
      {/* AI Summary Quote */}
      {summaryText && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-5 relative"
        >
          <div className="absolute -left-1 -top-1 text-amber-500/30">
            <Quote className="w-6 h-6" />
          </div>
          <p className="text-sm text-zinc-300 leading-relaxed italic pl-6 pr-4">
            {summaryText}
          </p>
        </motion.div>
      )}

      {/* 메인 컨텐츠 */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        {/* 왼쪽: 토픽 테이블 (8칸) */}
        <div className="lg:col-span-8">
          {/* 헤더 */}
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-4">
              <span className="text-[11px] text-zinc-500 uppercase tracking-wider">Topic Mastery</span>
              <div className="flex items-center gap-3 text-[10px]">
                <span className="flex items-center gap-1">
                  <span className="w-2 h-2 rounded-full bg-emerald-500" />
                  <span className="text-zinc-500">{stats.masteredCount}</span>
                </span>
                <span className="flex items-center gap-1">
                  <span className="w-2 h-2 rounded-full bg-yellow-500" />
                  <span className="text-zinc-500">{stats.learningCount}</span>
                </span>
                <span className="flex items-center gap-1">
                  <span className="w-2 h-2 rounded-full bg-red-500" />
                  <span className="text-zinc-500">{stats.weakCount}</span>
                </span>
              </div>
            </div>
            <span className="text-[11px] text-zinc-600">
              avg <span className="text-zinc-400 font-medium">{Math.round(stats.avgMastery * 100)}%</span>
            </span>
          </div>

          {/* 토픽 리스트 */}
          <div className="space-y-1">
            {displayTopics.map((item, index) => {
              const colors = getMasteryColor(item.mastery);
              const percentage = Math.round(item.mastery * 100);

              return (
                <motion.div
                  key={item.topic}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.03 }}
                  className="group flex items-center gap-3 py-2 px-3 rounded-lg hover:bg-zinc-800/30 transition-colors"
                >
                  {/* 토픽명 */}
                  <div className="w-24 flex-shrink-0">
                    <span className="text-xs text-zinc-300 truncate block font-medium" title={item.topic}>
                      {item.topic}
                    </span>
                  </div>

                  {/* 프로그레스 바 */}
                  <div className="flex-1 h-1.5 bg-zinc-800 rounded-full overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${percentage}%` }}
                      transition={{ duration: 0.6, delay: index * 0.03, ease: "easeOut" }}
                      className="h-full rounded-full"
                      style={{ backgroundColor: colors.bar }}
                    />
                  </div>

                  {/* 정답/시도 */}
                  <div className="w-12 text-right">
                    <span className="text-[10px] text-zinc-500">
                      {item.correctCount}/{item.attemptCount}
                    </span>
                  </div>

                  {/* 퍼센트 */}
                  <div className="w-10 text-right">
                    <span className={`text-xs font-semibold ${colors.text}`}>
                      {percentage}%
                    </span>
                  </div>
                </motion.div>
              );
            })}
          </div>

          {/* 더보기/접기 */}
          {hasMore && (
            <button
              onClick={() => setShowAll(!showAll)}
              className="w-full mt-2 py-2 text-[11px] text-zinc-500 hover:text-zinc-300 flex items-center justify-center gap-1 transition-colors"
            >
              {showAll ? (
                <>
                  <ChevronUp className="w-3 h-3" />
                  Show Less
                </>
              ) : (
                <>
                  <ChevronDown className="w-3 h-3" />
                  Show All ({sortedTopics.length})
                </>
              )}
            </button>
          )}
        </div>

        {/* 오른쪽: AI 분석 키워드 (4칸) */}
        <div className="lg:col-span-4 lg:border-l lg:border-zinc-800 lg:pl-5 space-y-4">
          {/* Strengths */}
          {strengths.length > 0 && (
            <div>
              <div className="flex items-center gap-1.5 mb-2">
                <Zap className="w-3.5 h-3.5 text-emerald-400" />
                <span className="text-[11px] text-zinc-500 uppercase tracking-wider">Strengths</span>
              </div>
              <div className="flex flex-wrap gap-1.5">
                {strengths.map((item) => (
                  <button
                    key={item.topic}
                    onClick={() => handleTopicClick(item.topic, 'strength')}
                    className={`
                      px-2.5 py-1 rounded-md text-[11px] font-medium transition-all border
                      ${selectedTopic?.topic === item.topic
                        ? 'bg-emerald-500/20 border-emerald-500/40 text-emerald-300'
                        : 'bg-zinc-800/50 border-zinc-700/50 text-zinc-400 hover:text-emerald-300 hover:border-emerald-500/30'
                      }
                    `}
                  >
                    {item.topic}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Weaknesses */}
          {weaknesses.length > 0 && (
            <div>
              <div className="flex items-center gap-1.5 mb-2">
                <Target className="w-3.5 h-3.5 text-rose-400" />
                <span className="text-[11px] text-zinc-500 uppercase tracking-wider">Needs Work</span>
              </div>
              <div className="flex flex-wrap gap-1.5">
                {weaknesses.map((item) => (
                  <button
                    key={item.topic}
                    onClick={() => handleTopicClick(item.topic, 'weakness')}
                    className={`
                      px-2.5 py-1 rounded-md text-[11px] font-medium transition-all border
                      ${selectedTopic?.topic === item.topic
                        ? 'bg-rose-500/20 border-rose-500/40 text-rose-300'
                        : 'bg-zinc-800/50 border-zinc-700/50 text-zinc-400 hover:text-rose-300 hover:border-rose-500/30'
                      }
                    `}
                  >
                    {item.topic}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* 선택된 토픽 피드백 */}
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
                p-4 rounded-xl border backdrop-blur-sm
                ${selectedTopic.type === 'strength'
                  ? 'bg-emerald-500/5 border-emerald-500/20'
                  : 'bg-rose-500/5 border-rose-500/20'
                }
              `}
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-center gap-2">
                  {selectedTopic.type === 'strength' ? (
                    <div className="w-6 h-6 rounded-md bg-emerald-500/20 flex items-center justify-center">
                      <Zap className="w-3.5 h-3.5 text-emerald-400" />
                    </div>
                  ) : (
                    <div className="w-6 h-6 rounded-md bg-rose-500/20 flex items-center justify-center">
                      <Target className="w-3.5 h-3.5 text-rose-400" />
                    </div>
                  )}
                  <div>
                    <span
                      className={`text-sm font-semibold ${
                        selectedTopic.type === 'strength' ? 'text-emerald-300' : 'text-rose-300'
                      }`}
                    >
                      {selectedTopic.topic}
                    </span>
                    <span className="text-xs text-zinc-500 ml-2">
                      {Math.round(selectedTopic.score * 100)}%
                    </span>
                  </div>
                </div>
                <button
                  onClick={() => setSelectedTopic(null)}
                  className="text-zinc-500 hover:text-zinc-300 transition-colors p-1"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
              <p className="text-sm text-zinc-400 leading-relaxed mt-3 pl-8">
                {selectedTopic.insight || '상세 분석 정보가 없습니다.'}
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
