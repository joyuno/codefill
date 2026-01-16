'use client';

import { useState, useEffect, useMemo } from 'react';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { Brain, RefreshCw, Loader2, Sparkles, FileCode, HelpCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { ScoreOverview } from '@/components/analysis/ScoreOverview';
import { TopicMasteryChart } from '@/components/analysis/TopicMasteryChart';
import { RecommendedProblems } from '@/components/analysis/RecommendedProblems';
import { AICoachingSection } from '@/components/analysis/AICoachingSection';
import { RecentAttemptsCard } from '@/components/analysis/RecentAttemptsCard';
import { HintIndependenceCard } from '@/components/analysis/HintIndependenceCard';
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
      console.log('📊 [DEBUG] getReport response:', response);
      console.log('📊 [DEBUG] report data:', response.data?.report);
      console.log('📊 [DEBUG] problemTypeStats:', response.data?.report?.problemTypeStats);
      console.log('📊 [DEBUG] recent10Attempts:', response.data?.report?.recent10Attempts);
      console.log('📊 [DEBUG] hintIndependence:', response.data?.report?.hintIndependence);
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
      console.log('📊 [DEBUG] generateAnalysis response:', response);
      console.log('📊 [DEBUG] problemTypeStats:', response.data?.problemTypeStats);
      console.log('📊 [DEBUG] recent10Attempts:', response.data?.recent10Attempts);
      console.log('📊 [DEBUG] hintIndependence:', response.data?.hintIndependence);
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

      {/* Row 1: ScoreRing + HintUsage */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="grid grid-cols-1 md:grid-cols-2 gap-4"
      >
        {/* 종합 점수 + 스탯 + 난이도별/유형별 정답률 */}
        <div className="min-h-[280px]">
          <ScoreOverview
            score={overallScore}
            stats={report.statsSnapshot}
            difficultySnapshot={report.difficultySnapshot}
            problemTypeStats={report.problemTypeStats}
          />
        </div>

        {/* 빈 카드 - TODO: 새로운 콘텐츠 추가 예정 */}
        <div className="rounded-2xl bg-zinc-900/80 border border-zinc-800 min-h-[280px] flex items-center justify-center">
          <p className="text-zinc-600 text-sm">새로운 콘텐츠 예정</p>
        </div>
      </motion.div>

      {/* Row 2: BKT Mastery + AI Coach 통합 */}
      {report.bktMastery && Object.keys(report.bktMastery).length >= 3 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.06 }}
          className="rounded-2xl bg-zinc-900/80 border border-zinc-800 overflow-hidden"
        >
          <div className="px-4 py-3 border-b border-zinc-800">
            <h3 className="text-sm font-bold text-zinc-100">토픽별 숙련도 & AI 분석</h3>
            <div className="flex items-center gap-1 mt-0.5">
              <p className="text-[10px] text-zinc-500">
                BKT 기반 실력 분석 · 토픽을 클릭하면 상세 피드백을 볼 수 있습니다
              </p>
              <Popover>
                <PopoverTrigger asChild>
                  <button className="text-zinc-500 hover:text-zinc-300 transition-colors p-0.5">
                    <HelpCircle className="w-3.5 h-3.5" />
                  </button>
                </PopoverTrigger>
                <PopoverContent
                  align="start"
                  className="w-80 p-0 bg-zinc-900 border-zinc-700"
                >
                  <div className="px-4 py-3 border-b border-zinc-800">
                    <h4 className="text-sm font-semibold text-zinc-100">BKT란?</h4>
                    <p className="text-[10px] text-zinc-500 mt-0.5">Bayesian Knowledge Tracing</p>
                  </div>
                  <div className="px-4 py-3 space-y-3 text-xs text-zinc-400">
                    <p>
                      <span className="text-zinc-200 font-medium">단순 정답률과 다릅니다.</span>{' '}
                      BKT는 정답/오답의 <span className="text-primary">순서와 패턴</span>을 분석하여
                      실제 이해도를 측정합니다.
                    </p>
                    <div className="bg-zinc-800/50 rounded-lg p-3 space-y-2">
                      <p className="text-zinc-300 font-medium text-[11px]">예시: 10문제 중 5문제 정답 (50%)</p>
                      <div className="space-y-1.5 text-[11px]">
                        <div className="flex items-center gap-2">
                          <span className="text-emerald-400">●●●●●</span>
                          <span className="text-zinc-500">○○○○○</span>
                          <span className="text-zinc-400">→ BKT 낮음 (최근 연속 오답)</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-zinc-500">○○○○○</span>
                          <span className="text-emerald-400">●●●●●</span>
                          <span className="text-zinc-400">→ BKT 높음 (최근 연속 정답)</span>
                        </div>
                      </div>
                    </div>
                    <p className="text-zinc-500 text-[11px]">
                      최근 정답을 맞추면 숙련도가 올라가고, 최근 오답이 많으면 내려갑니다.
                      꾸준히 정답을 맞추면 점수가 안정적으로 상승합니다.
                    </p>
                  </div>
                </PopoverContent>
              </Popover>
            </div>
          </div>
          <TopicMasteryChart
            bktMastery={report.bktMastery}
            strengths={report.strengths}
            weaknesses={report.weaknesses}
            summaryText={report.summaryText}
          />
        </motion.div>
      )}

      {/* Row 3: 최근 풀이 기록 + 힌트 독립률 */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.10 }}
        className="grid grid-cols-1 md:grid-cols-2 gap-4"
      >
        {/* 최근 10문제 결과 */}
        {report.recent10Attempts && report.recent10Attempts.length > 0 && (
          <div className="rounded-2xl bg-zinc-900/80 border border-zinc-800 overflow-hidden">
            <div className="px-4 py-3 border-b border-zinc-800">
              <h3 className="text-sm font-bold text-zinc-100">최근 풀이 기록</h3>
              <p className="text-[10px] text-zinc-500 mt-0.5">
                최근 10문제 결과 분석
              </p>
            </div>
            <RecentAttemptsCard
              attempts={report.recent10Attempts}
              analysis={report.recent10Analysis}
            />
          </div>
        )}

        {/* 힌트 독립률 (도넛 차트) */}
        {report.hintIndependence && report.hintIndependence.total > 0 && (
          <div className="rounded-2xl bg-zinc-900/80 border border-zinc-800 overflow-hidden">
            <div className="px-4 py-3 border-b border-zinc-800">
              <h3 className="text-sm font-bold text-zinc-100">힌트 독립률</h3>
              <p className="text-[10px] text-zinc-500 mt-0.5">
                힌트 없이 해결한 문제 비율
              </p>
            </div>
            <HintIndependenceCard data={report.hintIndependence} />
          </div>
        )}
      </motion.div>

      {/* Row 4: AI Coach (모든 AI 분석 통합) */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.14 }}
      >
        <AICoachingSection
          detailedFeedback={report.detailedFeedback}
          commonErrorPatterns={report.commonErrorPatterns}
        />
      </motion.div>

      {/* Row 5: RecommendedProblems */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.18 }}
        className="rounded-2xl bg-zinc-900/80 border border-zinc-800"
      >
        <RecommendedProblems initialProblems={report.recommendedProblems} />
      </motion.div>
    </div>
  );
}
