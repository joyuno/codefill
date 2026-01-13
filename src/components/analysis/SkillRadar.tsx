'use client';

import { motion } from 'framer-motion';
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
  Tooltip,
} from 'recharts';

interface SkillData {
  topic: string;
  score: number; // 0-1
  fullMark?: number;
}

interface SkillRadarProps {
  skills: SkillData[];
  previousSkills?: SkillData[]; // 지난주 데이터 (비교용)
  size?: number;
}

// 토픽 이름 축약 (차트에 표시용)
function shortenTopic(topic: string): string {
  const shortNames: Record<string, string> = {
    'Dynamic Programming': 'DP',
    'Binary Search': 'BS',
    'Two Pointers': '2P',
    'Divide and Conquer': 'D&C',
    'Breadth First Search': 'BFS',
    'Depth First Search': 'DFS',
  };
  return shortNames[topic] || (topic.length > 8 ? topic.slice(0, 6) + '..' : topic);
}

// 점수에 따른 색상
function getScoreColor(score: number): string {
  if (score >= 0.8) return '#22c55e'; // green
  if (score >= 0.6) return '#3b82f6'; // blue
  if (score >= 0.4) return '#eab308'; // yellow
  return '#ef4444'; // red
}

export function SkillRadar({ skills, previousSkills, size = 280 }: SkillRadarProps) {
  // 데이터 변환 (recharts 형식) - 중복 토픽 병합
  const chartData = (() => {
    const dataMap = new Map<string, { fullTopic: string; scores: number[]; previous?: number }>();

    skills.forEach((skill) => {
      const shortTopic = shortenTopic(skill.topic);
      const prev = previousSkills?.find((p) => p.topic === skill.topic);
      const existing = dataMap.get(shortTopic);

      if (existing) {
        // 중복 토픽: 점수 누적 (나중에 평균 계산)
        existing.scores.push(skill.score);
        if (prev && existing.previous === undefined) {
          existing.previous = prev.score;
        }
      } else {
        dataMap.set(shortTopic, {
          fullTopic: skill.topic,
          scores: [skill.score],
          previous: prev?.score,
        });
      }
    });

    // Map을 배열로 변환하면서 평균 계산
    return Array.from(dataMap.entries()).map(([topic, data]) => {
      const avgScore = data.scores.reduce((a, b) => a + b, 0) / data.scores.length;
      return {
        topic,
        fullTopic: data.fullTopic,
        current: Math.round(avgScore * 100),
        previous: data.previous !== undefined ? Math.round(data.previous * 100) : undefined,
        fullMark: 100,
      };
    });
  })();

  // 평균 점수 계산
  const avgScore = skills.length > 0
    ? skills.reduce((sum, s) => sum + s.score, 0) / skills.length
    : 0;
  const avgColor = getScoreColor(avgScore);

  if (skills.length === 0) {
    return (
      <div className="flex flex-col h-full">
        <h3 className="text-sm font-medium text-zinc-400 uppercase tracking-wider mb-4">
          Skill Radar
        </h3>
        <div className="flex-1 flex items-center justify-center text-zinc-600 text-sm">
          문제를 풀면 스킬이 표시됩니다
        </div>
      </div>
    );
  }

  // 데이터가 3개 미만이면 레이더 차트가 이상하게 보이므로 최소 3개 필요
  if (skills.length < 3) {
    return (
      <div className="flex flex-col h-full">
        <h3 className="text-sm font-medium text-zinc-400 uppercase tracking-wider mb-4">
          Skill Radar
        </h3>
        <div className="flex-1 flex items-center justify-center text-zinc-600 text-sm text-center px-4">
          다양한 토픽의 문제를 풀어보세요<br />
          (최소 3개 토픽 필요)
        </div>
      </div>
    );
  }

  return (
    <motion.div
      className="flex flex-col h-full"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: 0.2 }}
    >
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-sm font-medium text-zinc-400 uppercase tracking-wider">
          Skill Radar
        </h3>
        <div className="flex items-center gap-3 text-xs">
          <div className="flex items-center gap-1.5">
            <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: avgColor }} />
            <span className="text-zinc-500">현재</span>
          </div>
          {previousSkills && previousSkills.length > 0 && (
            <div className="flex items-center gap-1.5">
              <div className="w-2.5 h-2.5 rounded-full bg-zinc-600" />
              <span className="text-zinc-500">지난주</span>
            </div>
          )}
        </div>
      </div>

      <div className="flex-1 min-h-0" style={{ minHeight: size }}>
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart data={chartData} margin={{ top: 20, right: 30, bottom: 20, left: 30 }}>
            <PolarGrid
              stroke="#3f3f46"
              strokeDasharray="3 3"
            />
            <PolarAngleAxis
              dataKey="topic"
              tick={{ fill: '#a1a1aa', fontSize: 11 }}
              tickLine={false}
            />
            <PolarRadiusAxis
              angle={90}
              domain={[0, 100]}
              tick={{ fill: '#71717a', fontSize: 9 }}
              tickCount={5}
              axisLine={false}
            />

            {/* 지난주 데이터 (있으면) */}
            {previousSkills && previousSkills.length > 0 && (
              <Radar
                name="지난주"
                dataKey="previous"
                stroke="#52525b"
                fill="#52525b"
                fillOpacity={0.2}
                strokeWidth={1}
                dot={false}
              />
            )}

            {/* 현재 데이터 */}
            <Radar
              name="현재"
              dataKey="current"
              stroke={avgColor}
              fill={avgColor}
              fillOpacity={0.3}
              strokeWidth={2}
              dot={{
                r: 3,
                fill: avgColor,
                strokeWidth: 0,
              }}
              animationBegin={300}
              animationDuration={1000}
            />

            <Tooltip
              content={({ active, payload }) => {
                if (!active || !payload || payload.length === 0) return null;
                const data = payload[0].payload;
                return (
                  <div className="bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-2 shadow-lg">
                    <p className="text-sm font-medium text-zinc-200">{data.fullTopic}</p>
                    <p className="text-xs text-zinc-400 mt-1">
                      현재: <span className="text-zinc-200 font-medium">{data.current}%</span>
                    </p>
                    {data.previous !== undefined && (
                      <p className="text-xs text-zinc-500">
                        지난주: {data.previous}%
                        {data.current > data.previous && (
                          <span className="text-green-400 ml-1">+{data.current - data.previous}%</span>
                        )}
                        {data.current < data.previous && (
                          <span className="text-red-400 ml-1">{data.current - data.previous}%</span>
                        )}
                      </p>
                    )}
                  </div>
                );
              }}
            />
          </RadarChart>
        </ResponsiveContainer>
      </div>

      {/* 평균 점수 표시 */}
      <div className="mt-2 text-center">
        <span className="text-xs text-zinc-500">평균 </span>
        <span className="text-sm font-bold" style={{ color: avgColor }}>
          {Math.round(avgScore * 100)}%
        </span>
      </div>
    </motion.div>
  );
}
