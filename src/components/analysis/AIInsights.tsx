'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Link from 'next/link';
import {
  Sparkles,
  ChevronDown,
  ChevronUp,
  CheckCircle2,
  AlertTriangle,
  Lightbulb,
  BookOpen,
  ArrowRight,
  Target,
} from 'lucide-react';

interface TopicScore {
  topic: string;
  score: number;
  insight?: string;
}

interface RecommendedProblem {
  id: string;
  originalId?: string;
  name: string;
  difficulty: string;
  topic: string;
  reason: string;
}

interface AIInsightsProps {
  summary: string;
  strengths: TopicScore[];
  weaknesses: TopicScore[];
  recommendations: string[];
  studyPlan?: string;
  recommendedProblems: RecommendedProblem[];
}

// 난이도 색상
function getDifficultyColor(difficulty: string): string {
  const lower = difficulty.toLowerCase();
  if (lower.includes('easy') || lower === '하') return '#22c55e';
  if (lower.includes('medium') || lower === '중') return '#eab308';
  if (lower.includes('hard') || lower === '상') return '#ef4444';
  return '#71717a';
}

export function AIInsights({
  summary,
  strengths,
  weaknesses,
  recommendations,
  studyPlan,
  recommendedProblems,
}: AIInsightsProps) {
  const [expandedSection, setExpandedSection] = useState<string | null>('summary');

  const toggleSection = (section: string) => {
    setExpandedSection(expandedSection === section ? null : section);
  };

  const hasContent =
    summary ||
    strengths.length > 0 ||
    weaknesses.length > 0 ||
    recommendations.length > 0 ||
    recommendedProblems.length > 0;

  if (!hasContent) {
    return (
      <div className="rounded-2xl bg-zinc-900/80 border border-zinc-800 p-6">
        <div className="flex items-center gap-2 mb-4">
          <Sparkles className="h-5 w-5 text-primary" />
          <h3 className="text-sm font-medium text-zinc-400 uppercase tracking-wider">
            AI Insights
          </h3>
        </div>
        <div className="flex items-center justify-center h-32 text-zinc-600 text-sm">
          분석 결과가 없습니다
        </div>
      </div>
    );
  }

  return (
    <motion.div
      className="rounded-2xl bg-gradient-to-br from-zinc-900 to-zinc-900/50 border border-zinc-800 overflow-hidden"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.5 }}
    >
      {/* 헤더 */}
      <div className="flex items-center gap-2 px-6 py-4 border-b border-zinc-800/50">
        <div className="p-1.5 rounded-lg bg-primary/20">
          <Sparkles className="h-4 w-4 text-primary" />
        </div>
        <h3 className="text-sm font-medium text-zinc-300 uppercase tracking-wider">
          AI Insights
        </h3>
      </div>

      {/* 종합 평가 */}
      {summary && (
        <Section
          id="summary"
          icon={<Target className="h-4 w-4" />}
          title="종합 평가"
          isExpanded={expandedSection === 'summary'}
          onToggle={() => toggleSection('summary')}
        >
          <p className="text-sm text-zinc-300 leading-relaxed whitespace-pre-wrap">
            {summary}
          </p>
        </Section>
      )}

      {/* 강점 & 약점 */}
      <div className="grid md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-zinc-800/50">
        {/* 강점 */}
        {strengths.length > 0 && (
          <Section
            id="strengths"
            icon={<CheckCircle2 className="h-4 w-4 text-green-500" />}
            title="강점"
            isExpanded={expandedSection === 'strengths'}
            onToggle={() => toggleSection('strengths')}
            className="md:border-r-0"
          >
            <div className="space-y-3">
              {strengths.slice(0, 3).map((item, index) => (
                <motion.div
                  key={item.topic}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="flex items-start gap-3"
                >
                  <div className="flex-shrink-0 w-10 h-10 rounded-lg bg-green-500/10 border border-green-500/30 flex items-center justify-center">
                    <span className="text-sm font-bold text-green-500">
                      {Math.round(item.score * 100)}
                    </span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-zinc-200">{item.topic}</p>
                    {item.insight && (
                      <p className="text-xs text-zinc-500 mt-0.5 line-clamp-2">
                        {item.insight}
                      </p>
                    )}
                  </div>
                </motion.div>
              ))}
            </div>
          </Section>
        )}

        {/* 약점 */}
        {weaknesses.length > 0 && (
          <Section
            id="weaknesses"
            icon={<AlertTriangle className="h-4 w-4 text-orange-500" />}
            title="개선 필요"
            isExpanded={expandedSection === 'weaknesses'}
            onToggle={() => toggleSection('weaknesses')}
          >
            <div className="space-y-3">
              {weaknesses.slice(0, 3).map((item, index) => (
                <motion.div
                  key={item.topic}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="flex items-start gap-3"
                >
                  <div className="flex-shrink-0 w-10 h-10 rounded-lg bg-orange-500/10 border border-orange-500/30 flex items-center justify-center">
                    <span className="text-sm font-bold text-orange-500">
                      {Math.round(item.score * 100)}
                    </span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <p className="text-sm font-medium text-zinc-200">{item.topic}</p>
                      <Link
                        href={`/practice?topic=${encodeURIComponent(item.topic)}`}
                        className="text-[10px] px-1.5 py-0.5 rounded bg-primary/10 text-primary hover:bg-primary/20 transition-colors"
                      >
                        연습
                      </Link>
                    </div>
                    {item.insight && (
                      <p className="text-xs text-zinc-500 mt-0.5 line-clamp-2">
                        {item.insight}
                      </p>
                    )}
                  </div>
                </motion.div>
              ))}
            </div>
          </Section>
        )}
      </div>

      {/* 학습 가이드 */}
      {recommendations.length > 0 && (
        <Section
          id="recommendations"
          icon={<Lightbulb className="h-4 w-4 text-yellow-500" />}
          title="맞춤 학습 가이드"
          isExpanded={expandedSection === 'recommendations'}
          onToggle={() => toggleSection('recommendations')}
        >
          <ul className="space-y-2">
            {recommendations.map((rec, index) => (
              <motion.li
                key={index}
                initial={{ opacity: 0, y: 5 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="flex items-start gap-2.5 text-sm text-zinc-300"
              >
                <span className="flex-shrink-0 w-5 h-5 rounded-full bg-yellow-500/10 border border-yellow-500/30 flex items-center justify-center text-[10px] font-bold text-yellow-500">
                  {index + 1}
                </span>
                <span className="flex-1 leading-relaxed">{rec}</span>
              </motion.li>
            ))}
          </ul>

          {studyPlan && (
            <div className="mt-4 p-3 rounded-lg bg-zinc-800/50 border border-zinc-700">
              <p className="text-xs text-zinc-400 mb-1">추천 학습 경로</p>
              <p className="text-sm text-zinc-300">{studyPlan}</p>
            </div>
          )}
        </Section>
      )}

      {/* 추천 문제 */}
      {recommendedProblems.length > 0 && (
        <Section
          id="problems"
          icon={<BookOpen className="h-4 w-4 text-blue-500" />}
          title="추천 연습 문제"
          isExpanded={expandedSection === 'problems'}
          onToggle={() => toggleSection('problems')}
          defaultExpanded={false}
        >
          <div className="space-y-2">
            {recommendedProblems.slice(0, 5).map((problem, index) => (
              <motion.div
                key={problem.id}
                initial={{ opacity: 0, y: 5 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
              >
                <Link
                  href={`/problems/${problem.originalId || problem.id}`}
                  className="flex items-center justify-between p-3 rounded-lg bg-zinc-800/30 border border-zinc-800 hover:border-zinc-700 hover:bg-zinc-800/50 transition-all group"
                >
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span
                        className="text-[10px] px-1.5 py-0.5 rounded font-medium"
                        style={{
                          backgroundColor: `${getDifficultyColor(problem.difficulty)}20`,
                          color: getDifficultyColor(problem.difficulty),
                        }}
                      >
                        {problem.difficulty}
                      </span>
                      <span className="text-[10px] px-1.5 py-0.5 rounded bg-zinc-700 text-zinc-400">
                        {problem.topic}
                      </span>
                    </div>
                    <p className="text-sm text-zinc-200 mt-1 truncate">
                      {problem.name}
                    </p>
                    <p className="text-xs text-zinc-500 mt-0.5 truncate">
                      {problem.reason}
                    </p>
                  </div>
                  <ArrowRight className="h-4 w-4 text-zinc-600 group-hover:text-primary transition-colors ml-2 flex-shrink-0" />
                </Link>
              </motion.div>
            ))}
          </div>

          {recommendedProblems.length > 5 && (
            <p className="mt-3 text-center text-xs text-zinc-500">
              +{recommendedProblems.length - 5}개 더 있음
            </p>
          )}
        </Section>
      )}
    </motion.div>
  );
}

// 섹션 컴포넌트
interface SectionProps {
  id: string;
  icon: React.ReactNode;
  title: string;
  children: React.ReactNode;
  isExpanded: boolean;
  onToggle: () => void;
  className?: string;
  defaultExpanded?: boolean;
}

function Section({
  id,
  icon,
  title,
  children,
  isExpanded,
  onToggle,
  className = '',
}: SectionProps) {
  return (
    <div className={`border-t border-zinc-800/50 first:border-t-0 ${className}`}>
      <button
        onClick={onToggle}
        className="w-full flex items-center justify-between px-6 py-3 hover:bg-zinc-800/30 transition-colors"
      >
        <div className="flex items-center gap-2">
          {icon}
          <span className="text-sm font-medium text-zinc-300">{title}</span>
        </div>
        {isExpanded ? (
          <ChevronUp className="h-4 w-4 text-zinc-500" />
        ) : (
          <ChevronDown className="h-4 w-4 text-zinc-500" />
        )}
      </button>

      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="px-6 pb-4">{children}</div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
