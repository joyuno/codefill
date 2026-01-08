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
import { Brain, TrendingUp, Target, Flame } from 'lucide-react';
import type { AnalysisReport } from '@/lib/api';

interface AnalysisHeroProps {
  report: AnalysisReport;
}

export function AnalysisHero({ report }: AnalysisHeroProps) {
  const { summaryText, skillSnapshot, statsSnapshot } = report;

  // Transform skill data for radar chart
  const chartData = Object.entries(skillSnapshot || {}).map(([topic, score]) => ({
    topic,
    score: Math.round(score * 100),
    fullMark: 100,
  }));

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="rounded-2xl border border-border bg-gradient-to-br from-card via-card to-primary/5 p-6"
    >
      <div className="flex flex-col gap-6 lg:flex-row lg:items-center">
        {/* Radar Chart */}
        <div className="flex-shrink-0 lg:w-72">
          {chartData.length > 0 ? (
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart data={chartData} margin={{ top: 20, right: 30, bottom: 20, left: 30 }}>
                  <PolarGrid stroke="hsl(var(--border))" />
                  <PolarAngleAxis
                    dataKey="topic"
                    tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 11 }}
                  />
                  <PolarRadiusAxis
                    angle={30}
                    domain={[0, 100]}
                    tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 10 }}
                  />
                  <Radar
                    name="실력"
                    dataKey="score"
                    stroke="hsl(142, 71%, 45%)"
                    fill="hsl(142, 71%, 45%)"
                    fillOpacity={0.3}
                    strokeWidth={2}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'hsl(var(--card))',
                      border: '1px solid hsl(var(--border))',
                      borderRadius: '8px',
                    }}
                    formatter={(value: number) => [`${value}%`, '실력']}
                  />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="flex h-64 items-center justify-center rounded-xl bg-secondary/30">
              <p className="text-sm text-muted-foreground">분석 데이터 없음</p>
            </div>
          )}
        </div>

        {/* Summary Content */}
        <div className="flex-1 space-y-4">
          {/* AI Summary */}
          <div className="flex items-start gap-3">
            <div className="rounded-lg bg-purple-500/10 p-2">
              <Brain className="h-5 w-5 text-purple-500" />
            </div>
            <div>
              <h3 className="mb-1 text-lg font-semibold">AI 분석 결과</h3>
              <p className="text-muted-foreground leading-relaxed">{summaryText}</p>
            </div>
          </div>

          {/* Stats Row */}
          <div className="grid grid-cols-3 gap-4 pt-2">
            <div className="flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-primary" />
              <div>
                <p className="text-lg font-bold">Lv.{statsSnapshot.level}</p>
                <p className="text-xs text-muted-foreground">현재 레벨</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Target className="h-4 w-4 text-blue-500" />
              <div>
                <p className="text-lg font-bold">{Math.round(statsSnapshot.accuracy * 100)}%</p>
                <p className="text-xs text-muted-foreground">정답률</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Flame className="h-4 w-4 text-orange-500" />
              <div>
                <p className="text-lg font-bold">{statsSnapshot.streak}일</p>
                <p className="text-xs text-muted-foreground">연속 학습</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
