'use client';

import { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { ArrowRight } from 'lucide-react';

interface TopicData {
  topic: string;
  score: number; // 0-1
  problemCount?: number;
  insight?: string;
}

interface WeaknessBubblesProps {
  weaknesses: TopicData[];
  allSkills?: Record<string, number>;
  maxBubbles?: number;
}

// 점수에 따른 색상 (약할수록 빨강, 강할수록 초록)
function getScoreColor(score: number): { fill: string; stroke: string; glow: string } {
  if (score >= 0.7) {
    return { fill: '#22c55e', stroke: '#16a34a', glow: 'rgba(34, 197, 94, 0.3)' };
  }
  if (score >= 0.5) {
    return { fill: '#eab308', stroke: '#ca8a04', glow: 'rgba(234, 179, 8, 0.3)' };
  }
  if (score >= 0.3) {
    return { fill: '#f97316', stroke: '#ea580c', glow: 'rgba(249, 115, 22, 0.3)' };
  }
  return { fill: '#ef4444', stroke: '#dc2626', glow: 'rgba(239, 68, 68, 0.4)' };
}

export function WeaknessBubbles({
  weaknesses,
  allSkills,
  maxBubbles = 6,
}: WeaknessBubblesProps) {
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);
  const [selectedTopic, setSelectedTopic] = useState<string | null>(null);

  // 약점 데이터 정렬 (점수 낮은 순)
  const sortedWeaknesses = useMemo(() => {
    return [...weaknesses]
      .sort((a, b) => a.score - b.score)
      .slice(0, maxBubbles);
  }, [weaknesses, maxBubbles]);

  if (sortedWeaknesses.length === 0) {
    return (
      <div className="flex flex-col h-full">
        <h3 className="text-sm font-medium text-zinc-400 uppercase tracking-wider mb-4">
          Weakness Map
        </h3>
        <div className="flex-1 flex items-center justify-center text-zinc-600 text-sm">
          분석된 약점이 없습니다
        </div>
      </div>
    );
  }

  const selectedData = selectedTopic
    ? sortedWeaknesses.find((w) => w.topic === selectedTopic)
    : null;

  // 가로 레이아웃용 - 버블 크기 계산 (점수 낮을수록 큰 버블)
  const getBubbleSize = (score: number, index: number) => {
    const baseSize = 90;
    const scoreBonus = (1 - score) * 30; // 점수 낮을수록 +30px
    const indexBonus = (sortedWeaknesses.length - index - 1) * 5; // 앞쪽일수록 약간 더 큼
    return baseSize + scoreBonus + indexBonus;
  };

  return (
    <motion.div
      className="flex flex-col h-full"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: 0.3 }}
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-medium text-zinc-400 uppercase tracking-wider">
          Weakness Map
        </h3>
        <div className="flex items-center gap-2 text-[10px] text-zinc-500">
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-red-500" />
            약함
          </span>
          <span className="text-zinc-700">→</span>
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-green-500" />
            강함
          </span>
        </div>
      </div>

      {/* 가로 버블 레이아웃 */}
      <div className="flex-1 flex items-center justify-center gap-4 flex-wrap py-4">
        {sortedWeaknesses.map((weakness, index) => {
          const size = getBubbleSize(weakness.score, index);
          const colors = getScoreColor(weakness.score);
          const isHovered = hoveredIndex === index;
          const isSelected = selectedTopic === weakness.topic;

          return (
            <motion.div
              key={weakness.topic}
              initial={{ opacity: 0, scale: 0 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.1 * index, duration: 0.4 }}
              className="relative cursor-pointer"
              style={{ width: size, height: size }}
              onMouseEnter={() => setHoveredIndex(index)}
              onMouseLeave={() => setHoveredIndex(null)}
              onClick={() => setSelectedTopic(
                selectedTopic === weakness.topic ? null : weakness.topic
              )}
            >
              {/* 글로우 효과 */}
              {(isHovered || isSelected) && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="absolute inset-0 rounded-full blur-xl"
                  style={{ backgroundColor: colors.glow }}
                />
              )}

              {/* 메인 버블 */}
              <motion.div
                className="absolute inset-0 rounded-full flex flex-col items-center justify-center border-2 transition-all duration-200"
                style={{
                  backgroundColor: colors.fill,
                  borderColor: colors.stroke,
                  opacity: isHovered || isSelected ? 1 : 0.85,
                  boxShadow: isHovered || isSelected
                    ? `0 0 20px ${colors.fill}80`
                    : 'none',
                }}
                whileHover={{ scale: 1.08 }}
                whileTap={{ scale: 0.95 }}
              >
                {/* 토픽 이름 */}
                <span className="text-white text-xs font-medium text-center px-2 leading-tight">
                  {weakness.topic.length > 12
                    ? weakness.topic.slice(0, 10) + '..'
                    : weakness.topic}
                </span>

                {/* 점수 */}
                <span className="text-white/90 text-sm font-bold mt-1">
                  {Math.round(weakness.score * 100)}%
                </span>
              </motion.div>

              {/* 랭킹 뱃지 */}
              {index < 3 && (
                <div
                  className="absolute -top-1 -right-1 w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold border-2 border-zinc-900"
                  style={{
                    backgroundColor: index === 0 ? '#ef4444' : index === 1 ? '#f97316' : '#eab308',
                    color: 'white',
                  }}
                >
                  {index + 1}
                </div>
              )}
            </motion.div>
          );
        })}
      </div>

      {/* 선택된 토픽 상세 정보 */}
      {selectedData && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-4 p-4 rounded-xl bg-zinc-800/50 border border-zinc-700"
        >
          <div className="flex items-center justify-between">
            <div>
              <span className="text-base font-medium text-zinc-200">
                {selectedData.topic}
              </span>
              <span
                className="ml-2 text-sm font-bold"
                style={{ color: getScoreColor(selectedData.score).fill }}
              >
                {Math.round(selectedData.score * 100)}%
              </span>
            </div>
            <Link
              href={`/problems?topic=${encodeURIComponent(selectedData.topic)}`}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-primary/10 text-primary text-sm font-medium hover:bg-primary/20 transition-colors"
            >
              연습하기
              <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
          {selectedData.insight && (
            <p className="mt-2 text-sm text-zinc-400 leading-relaxed">
              {selectedData.insight}
            </p>
          )}
        </motion.div>
      )}

      {/* 안내 텍스트 */}
      {!selectedData && sortedWeaknesses.length > 0 && (
        <p className="mt-2 text-center text-xs text-zinc-600">
          버블을 클릭하면 상세 정보와 연습 링크를 볼 수 있어요
        </p>
      )}
    </motion.div>
  );
}
