'use client';

import { useState, useEffect, useMemo } from 'react';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { Brain, RefreshCw, Loader2, Sparkles, FileCode } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ScoreOverview } from '@/components/analysis/ScoreOverview';
import { SkillRadar } from '@/components/analysis/SkillRadar';
import { HintUsageCard } from '@/components/analysis/HintUsageCard';
import { LearningStyleCard } from '@/components/analysis/LearningStyleCard';
import { RecommendedProblems } from '@/components/analysis/RecommendedProblems';
import { AICoachingSection } from '@/components/analysis/AICoachingSection';
import { analysisApi, type AnalysisReport } from '@/lib/api';

// 종합 점수 계산 (0-100)
function calculateOverallScore(report: AnalysisReport): number {
  const { statsSnapshot, skillSnapshot, difficultySnapshot } = report;

  // 1. 정확도 점수 (40% 가중치)
  const accuracyScore = statsSnapshot.accuracy * 100;

  // 2. 스킬 평균 점수 (30% 가중치)
  const skillValues = Object.values(skillSnapshot || {});
  const skillAvg = skillValues.length > 0
    ? (skillValues.reduce((a, b) => a + b, 0) / skillValues.length) * 100
    : 50;

  // 3. 난이도 가중 점수 (30% 가중치)
  const diffValues = difficultySnapshot || {};
  const easyScore = (diffValues.easy || 0) * 20;
  const mediumScore = (diffValues.medium || 0) * 40;
  const hardScore = (diffValues.hard || diffValues.medium_hard || 0) * 40;
  const difficultyScore = easyScore + mediumScore + hardScore;

  // 종합
  const overall = (accuracyScore * 0.4) + (skillAvg * 0.3) + (difficultyScore * 0.3);
  return Math.round(Math.min(100, Math.max(0, overall)));
}

export default function AnalysisPage() {
  const [report, setReport] = useState<AnalysisReport | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [insufficientData, setInsufficientData] = useState(false);

  useEffect(() => {
    fetchReport();
  }, []);

  const fetchReport = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await analysisApi.getReport();
      if (response.data?.hasReport && response.data.report) {
        setReport(response.data.report);
      } else {
        setReport(null);
      }
    } catch (err) {
      setError('분석 결과를 불러오지 못했습니다');
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerate = async () => {
    setIsGenerating(true);
    setError(null);
    setInsufficientData(false);

    try {
      const response = await analysisApi.generateAnalysis();
      if (response.data) {
        setReport(response.data);
      } else {
        const errorMsg = response.error?.message || '분석 생성에 실패했습니다';
        if (errorMsg.includes('최소') || errorMsg.includes('문제를 풀어')) {
          setInsufficientData(true);
        }
        setError(errorMsg);
      }
    } catch (err) {
      setError('분석 생성 중 오류가 발생했습니다');
    } finally {
      setIsGenerating(false);
    }
  };

  // 계산된 값들
  const overallScore = useMemo(() =>
    report ? calculateOverallScore(report) : 0
  , [report]);

  // ===== 로딩 =====
  if (isLoading) {
    return (
      <div className="flex h-[70vh] items-center justify-center">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center"
        >
          <div className="relative mx-auto w-16 h-16">
            <div className="absolute inset-0 bg-primary/30 rounded-full blur-xl animate-pulse" />
            <div className="relative flex items-center justify-center h-full">
              <Brain className="h-8 w-8 text-primary animate-pulse" />
            </div>
          </div>
          <p className="mt-4 text-zinc-500">분석 데이터 로딩 중...</p>
        </motion.div>
      </div>
    );
  }

  // ===== 리포트 없음 =====
  if (!report) {
    return (
      <div className="flex h-[70vh] items-center justify-center px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center max-w-md"
        >
          <div className="relative mx-auto w-24 h-24 mb-6">
            <div className="absolute inset-0 bg-primary/20 rounded-full blur-2xl" />
            <div className="relative flex items-center justify-center h-full rounded-full bg-zinc-900 border border-zinc-800">
              <Brain className="h-12 w-12 text-primary" />
            </div>
          </div>

          <h1 className="text-2xl font-bold mb-2">Developer Stats</h1>
          <p className="text-zinc-500 mb-6">
            AI가 당신의 코딩 실력을 분석합니다
          </p>

          {insufficientData ? (
            <>
              <div className="mb-6 p-4 rounded-xl bg-orange-500/10 border border-orange-500/30">
                <p className="text-sm text-orange-400">{error}</p>
              </div>
              <Link href="/problems">
                <Button size="lg" className="gap-2">
                  <FileCode className="h-5 w-5" />
                  문제 풀러 가기
                </Button>
              </Link>
            </>
          ) : (
            <>
              <Button
                size="lg"
                onClick={handleGenerate}
                disabled={isGenerating}
                className="gap-2"
              >
                {isGenerating ? (
                  <>
                    <Loader2 className="h-5 w-5 animate-spin" />
                    분석 중...
                  </>
                ) : (
                  <>
                    <Sparkles className="h-5 w-5" />
                    분석 시작
                  </>
                )}
              </Button>
              {error && <p className="mt-4 text-sm text-red-400">{error}</p>}
            </>
          )}
        </motion.div>
      </div>
    );
  }

  // ===== 대시보드 (새로운 레이아웃) =====
  return (
    <div className="max-w-7xl mx-auto px-4 py-6 space-y-5">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Brain className="h-6 w-6 text-primary" />
          <h1 className="text-xl font-bold">Developer Stats</h1>
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={handleGenerate}
          disabled={isGenerating}
          className="text-zinc-400 hover:text-zinc-200"
        >
          {isGenerating ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <RefreshCw className="h-4 w-4" />
          )}
        </Button>
      </div>

      {error && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="p-3 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-sm text-center"
        >
          {error}
        </motion.div>
      )}

      {/* Row 1: ScoreRing + HintUsage + LearningStyle */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
      >
        {/* 종합 점수 + 스탯 + 난이도별 정답률 */}
        <div className="min-h-[280px]">
          <ScoreOverview
            score={overallScore}
            stats={report.statsSnapshot}
            difficultySnapshot={report.difficultySnapshot}
          />
        </div>

        {/* 힌트 사용 패턴 */}
        <div className="rounded-2xl bg-zinc-900/80 border border-zinc-800 min-h-[280px]">
          <HintUsageCard hintUsage={report.hintUsage} />
        </div>

        {/* 학습 스타일 */}
        <div className="rounded-2xl bg-zinc-900/80 border border-zinc-800 min-h-[280px]">
          <LearningStyleCard learningStyle={report.learningStyle} />
        </div>
      </motion.div>

      {/* Row 2: 스킬 분석 (레이더 오른쪽 플로팅) */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.08 }}
        className="rounded-2xl bg-zinc-900/80 border border-zinc-800 overflow-hidden"
      >
        <div className="p-6">
          {/* 상단: 강점/약점 + 레이더 */}
          <div className="flex gap-6">
            {/* 왼쪽: 강점/약점 텍스트 */}
            <div className="flex-1 space-y-5">
              {/* 강점 영역 */}
              <div>
                <div className="flex items-center gap-2 mb-3">
                  <div className="w-2 h-2 rounded-full bg-emerald-500" />
                  <h4 className="text-sm font-semibold text-zinc-200">강점 영역</h4>
                </div>
                <div className="space-y-2">
                  {report.strengths.slice(0, 3).map((s, i) => (
                    <div key={i} className="flex items-start gap-3 p-2.5 rounded-lg bg-emerald-500/5 border border-emerald-500/10">
                      <span className="text-xs font-mono text-emerald-400 bg-emerald-500/10 px-1.5 py-0.5 rounded">
                        {Math.round(s.score * 100)}%
                      </span>
                      <div className="flex-1 min-w-0">
                        <span className="text-sm font-medium text-zinc-100">{s.topic}</span>
                        {s.insight && (
                          <p className="text-xs text-zinc-500 mt-0.5 line-clamp-1">{s.insight}</p>
                        )}
                      </div>
                    </div>
                  ))}
                  {report.strengths.length === 0 && (
                    <p className="text-xs text-zinc-600">아직 데이터가 부족합니다</p>
                  )}
                </div>
              </div>

              {/* 보완 필요 */}
              <div>
                <div className="flex items-center gap-2 mb-3">
                  <div className="w-2 h-2 rounded-full bg-amber-500" />
                  <h4 className="text-sm font-semibold text-zinc-200">보완 필요</h4>
                </div>
                <div className="space-y-2">
                  {report.weaknesses.slice(0, 3).map((w, i) => (
                    <div key={i} className="flex items-start gap-3 p-2.5 rounded-lg bg-amber-500/5 border border-amber-500/10">
                      <span className="text-xs font-mono text-amber-400 bg-amber-500/10 px-1.5 py-0.5 rounded">
                        {Math.round(w.score * 100)}%
                      </span>
                      <div className="flex-1 min-w-0">
                        <span className="text-sm font-medium text-zinc-100">{w.topic}</span>
                        {w.insight && (
                          <p className="text-xs text-zinc-500 mt-0.5 line-clamp-1">{w.insight}</p>
                        )}
                      </div>
                    </div>
                  ))}
                  {report.weaknesses.length === 0 && (
                    <p className="text-xs text-zinc-600">모든 영역에서 잘하고 있어요!</p>
                  )}
                </div>
              </div>
            </div>

            {/* 오른쪽: 레이더 차트 */}
            <div className="hidden md:flex flex-shrink-0 items-center justify-center">
              <div className="relative">
                <div className="absolute inset-0 bg-primary/5 rounded-full blur-2xl" />
                <SkillRadar
                  skills={Object.entries(report.skillSnapshot || {}).map(([topic, score]) => ({
                    topic,
                    score: score as number,
                  }))}
                  size={200}
                />
              </div>
            </div>
          </div>

          {/* 하단: AI 추천 */}
          <div className="mt-6 pt-5 border-t border-zinc-800">
            <div className="flex items-center gap-2 mb-3">
              <div className="w-2 h-2 rounded-full bg-blue-500" />
              <h4 className="text-sm font-semibold text-zinc-200">AI 추천</h4>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
              {report.recommendations.slice(0, 3).map((rec, i) => (
                <div
                  key={i}
                  className="p-3 rounded-lg bg-zinc-800/50 border border-zinc-700/50 hover:border-blue-500/30 transition-colors"
                >
                  <p className="text-sm text-zinc-300 leading-relaxed line-clamp-2">{rec}</p>
                </div>
              ))}
              {report.recommendations.length === 0 && (
                <p className="text-xs text-zinc-600">추천 사항이 없습니다</p>
              )}
            </div>
          </div>
        </div>
      </motion.div>

      {/* Row 3: AI Coaching Section (with error analysis) */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.12 }}
      >
        <AICoachingSection
          summaryText={report.summaryText || ""}
          studyPlan={report.studyPlan}
          detailedFeedback={report.detailedFeedback}
          breakthroughMoments={report.breakthroughMoments}
          commonErrorPatterns={report.commonErrorPatterns}
          errorAnalysis={report.errorAnalysis}
        />
      </motion.div>

      {/* Row 4: RecommendedProblems */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.16 }}
        className="rounded-2xl bg-zinc-900/80 border border-zinc-800"
      >
        <RecommendedProblems initialProblems={report.recommendedProblems} />
      </motion.div>
    </div>
  );
}
