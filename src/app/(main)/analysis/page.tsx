'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { Brain, RefreshCw, Loader2, Sparkles, FileCode } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { AnalysisHero } from '@/components/analysis/AnalysisHero';
import { StrengthWeaknessCards } from '@/components/analysis/StrengthWeaknessCards';
import { DifficultyProgress } from '@/components/analysis/DifficultyProgress';
import { AIRecommendations } from '@/components/analysis/AIRecommendations';
import { LearningAdvice } from '@/components/analysis/LearningAdvice';
import { analysisApi, type AnalysisReport } from '@/lib/api';

export default function AnalysisPage() {
  const [report, setReport] = useState<AnalysisReport | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [insufficientData, setInsufficientData] = useState(false);

  // Fetch latest report on mount
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
        // Check if it's an insufficient data error (400)
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

  // Format date
  const formatDate = (dateStr?: string) => {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    return date.toLocaleString('ko-KR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="flex h-[60vh] items-center justify-center">
        <div className="text-center">
          <Loader2 className="mx-auto h-10 w-10 animate-spin text-primary" />
          <p className="mt-4 text-muted-foreground">분석 결과를 불러오는 중...</p>
        </div>
      </div>
    );
  }

  // No report - show CTA
  if (!report) {
    return (
      <div className="mx-auto max-w-2xl py-20">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center"
        >
          <div className="mx-auto mb-6 flex h-20 w-20 items-center justify-center rounded-full bg-primary/10">
            <Brain className="h-10 w-10 text-primary" />
          </div>
          <h1 className="mb-3 text-2xl font-bold">AI 학습 분석</h1>

          {insufficientData ? (
            // 데이터 부족 상태
            <>
              <p className="mb-4 text-muted-foreground">
                분석을 위해 먼저 문제를 풀어주세요
              </p>
              <div className="mb-6 rounded-lg border border-orange-500/30 bg-orange-500/10 p-4">
                <p className="text-sm text-orange-500">
                  {error}
                </p>
              </div>
              <Link href="/problems">
                <Button size="lg" className="gap-2">
                  <FileCode className="h-5 w-5" />
                  문제 풀러 가기
                </Button>
              </Link>
            </>
          ) : (
            // 일반 상태 - 분석 시작 버튼
            <>
              <p className="mb-8 text-muted-foreground">
                AI가 당신의 학습 패턴을 분석하고<br />
                맞춤형 학습 조언을 제공합니다
              </p>
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
                    분석 시작하기
                  </>
                )}
              </Button>
              {error && !insufficientData && (
                <p className="mt-4 text-sm text-red-500">{error}</p>
              )}
            </>
          )}
        </motion.div>
      </div>
    );
  }

  // Has report - show dashboard
  return (
    <div className="mx-auto max-w-5xl space-y-6 pb-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div className="flex items-center gap-3">
          <div className="rounded-lg bg-purple-500/10 p-2">
            <Brain className="h-6 w-6 text-purple-500" />
          </div>
          <div>
            <h1 className="text-2xl font-bold">AI 학습 분석</h1>
            {report.createdAt && (
              <p className="text-sm text-muted-foreground">
                마지막 분석: {formatDate(report.createdAt)}
              </p>
            )}
          </div>
        </div>
        <Button
          variant="outline"
          onClick={handleGenerate}
          disabled={isGenerating}
          className="gap-2"
        >
          {isGenerating ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              분석 중...
            </>
          ) : (
            <>
              <RefreshCw className="h-4 w-4" />
              새로 분석하기
            </>
          )}
        </Button>
      </motion.div>

      {error && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="rounded-lg border border-red-500/20 bg-red-500/10 p-4 text-center text-red-500"
        >
          {error}
        </motion.div>
      )}

      {/* Hero Section */}
      <AnalysisHero report={report} />

      {/* Strength & Weakness */}
      <StrengthWeaknessCards
        strengths={report.strengths}
        weaknesses={report.weaknesses}
      />

      {/* Difficulty Progress */}
      <DifficultyProgress difficultySnapshot={report.difficultySnapshot} />

      {/* AI Recommendations & Learning Advice */}
      <div className="grid gap-6 lg:grid-cols-2">
        <AIRecommendations
          studyPlan={report.studyPlan}
          problems={report.recommendedProblems}
        />
        <LearningAdvice recommendations={report.recommendations} />
      </div>
    </div>
  );
}
