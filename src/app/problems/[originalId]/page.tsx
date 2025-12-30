'use client';

import { useState, useEffect, useCallback } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { Header } from '@/components/layout/Header';
import { TopNav } from '@/components/layout/TopNav';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  solutionsApi,
  type ProblemDiscussionResponse,
  type SolutionListItem,
} from '@/lib/api';
import { SolutionList } from '@/components/solutions/SolutionList';
import { SolutionForm } from '@/components/solutions/SolutionForm';
import { OfficialSolutions } from '@/components/solutions/OfficialSolutions';
import {
  ArrowLeft,
  Loader2,
  RefreshCw,
  ExternalLink,
  Play,
  PenLine,
  MessageSquare,
  Globe,
  FileText,
  TestTube,
} from 'lucide-react';
import { translateText, type LanguageCode } from '@/lib/api/translate';
import { cn } from '@/lib/utils';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import remarkBreaks from 'remark-breaks';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';

const difficultyColors: Record<string, string> = {
  easy: 'bg-primary/20 text-primary border-primary/30',
  medium: 'bg-warning/20 text-warning border-warning/30',
  hard: 'bg-destructive/20 text-destructive border-destructive/30',
};

export default function ProblemDiscussionPage() {
  const params = useParams();
  const router = useRouter();
  const originalId = params.originalId as string;

  const [data, setData] = useState<ProblemDiscussionResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [activeTab, setActiveTab] = useState<'official' | 'community'>('community');
  const [leftTab, setLeftTab] = useState<'problem' | 'testcases'>('problem');
  const [showForm, setShowForm] = useState(false);
  const [sortBy, setSortBy] = useState<'upvotes' | 'newest' | 'oldest'>('upvotes');
  const [page, setPage] = useState(1);

  // 번역 상태
  const [translatedQuestion, setTranslatedQuestion] = useState<string | null>(null);
  const [isTranslating, setIsTranslating] = useState(false);
  const [showTranslated, setShowTranslated] = useState(false);

  const fetchData = useCallback(async () => {
    if (!originalId) return;

    setLoading(true);
    setError(null);

    try {
      const response = await solutionsApi.getProblemDiscussion(originalId, {
        page,
        limit: 10,
        sort: sortBy,
      });
      setData(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load discussion');
    } finally {
      setLoading(false);
    }
  }, [originalId, page, sortBy]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleSolutionCreated = () => {
    setShowForm(false);
    fetchData();
  };

  const handleVote = async (solutionId: string, voteType: 'up' | 'down') => {
    try {
      await solutionsApi.voteSolution(solutionId, voteType);
      fetchData();
    } catch (err) {
      console.error('Vote failed:', err);
    }
  };

  const handleTranslate = async () => {
    if (!data?.problem?.question) return;

    // 이미 번역된 경우 토글
    if (translatedQuestion) {
      setShowTranslated(!showTranslated);
      return;
    }

    setIsTranslating(true);
    try {
      const result = await translateText(data.problem.question, 'ko' as LanguageCode);
      if (result.success && result.translated_text) {
        setTranslatedQuestion(result.translated_text);
        setShowTranslated(true);
      }
    } catch (err) {
      console.error('Translation failed:', err);
    } finally {
      setIsTranslating(false);
    }
  };

  const displayQuestion = showTranslated && translatedQuestion ? translatedQuestion : data?.problem?.question;

  if (loading && !data) {
    return (
      <div className="min-h-screen bg-background">
        <Header />
        <TopNav />
        <div className="flex items-center justify-center py-32">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      </div>
    );
  }

  if (error && !data) {
    return (
      <div className="min-h-screen bg-background">
        <Header />
        <TopNav />
        <div className="flex flex-col items-center justify-center py-32">
          <p className="text-destructive mb-4">{error}</p>
          <Button variant="outline" onClick={fetchData}>
            <RefreshCw className="mr-2 h-4 w-4" />
            다시 시도
          </Button>
        </div>
      </div>
    );
  }

  const problem = data?.problem;

  return (
    <div className="min-h-screen bg-background">
      <Header />
      <TopNav />

      {/* Back button */}
      <div className="border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-20">
        <div className="container max-w-7xl mx-auto px-4 py-3">
          <Link href="/problems" className="inline-flex items-center text-muted-foreground hover:text-foreground">
            <ArrowLeft className="h-4 w-4 mr-2" />
            문제 목록으로
          </Link>
        </div>
      </div>

      {problem && (
        <main className="container max-w-7xl mx-auto px-4 py-4">
          {/* 가로 레이아웃 */}
          <div className="flex flex-col lg:flex-row gap-6">

            {/* 왼쪽: 문제 설명 */}
            <div className="lg:w-1/2">
              {/* Problem Header */}
              <div className="flex items-start justify-between gap-4 mb-4">
                <div>
                  <h1 className="text-xl font-bold mb-2">{problem.name}</h1>
                  <div className="flex flex-wrap items-center gap-2">
                    <Badge
                      variant="outline"
                      className={cn('capitalize', difficultyColors[problem.difficulty] || '')}
                    >
                      {problem.difficulty}
                    </Badge>
                    {problem.source && (
                      <Badge variant="secondary">{problem.source}</Badge>
                    )}
                    {problem.tags.slice(0, 3).map((tag) => (
                      <Badge key={tag} variant="outline" className="text-xs">
                        {tag}
                      </Badge>
                    ))}
                    {problem.tags.length > 3 && (
                      <span className="text-xs text-muted-foreground">
                        +{problem.tags.length - 3}
                      </span>
                    )}
                  </div>
                </div>
                <div className="flex gap-2 shrink-0">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleTranslate}
                    disabled={isTranslating}
                    className={cn(showTranslated && 'text-primary')}
                  >
                    {isTranslating ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Globe className="h-4 w-4" />
                    )}
                  </Button>
                  {problem.url && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => window.open(problem.url!, '_blank')}
                    >
                      <ExternalLink className="h-4 w-4" />
                    </Button>
                  )}
                  <Button
                    size="sm"
                    onClick={() => router.push(`/practice?id=${originalId}&type=implementation`)}
                  >
                    <Play className="h-4 w-4 mr-1" />
                    풀기
                  </Button>
                </div>
              </div>

              {/* Problem Content with Tabs */}
              <div className="bg-muted/30 rounded-lg border border-border overflow-hidden">
                {/* Tab Buttons */}
                <div className="flex border-b border-border">
                  <button
                    onClick={() => setLeftTab('problem')}
                    className={cn(
                      'flex-1 flex items-center justify-center gap-2 px-4 py-2.5 text-sm font-medium transition-colors',
                      leftTab === 'problem'
                        ? 'border-b-2 border-primary text-primary bg-primary/5'
                        : 'text-muted-foreground hover:text-foreground hover:bg-secondary/50'
                    )}
                  >
                    <FileText className="h-4 w-4" />
                    문제 설명
                  </button>
                  <button
                    onClick={() => setLeftTab('testcases')}
                    className={cn(
                      'flex-1 flex items-center justify-center gap-2 px-4 py-2.5 text-sm font-medium transition-colors',
                      leftTab === 'testcases'
                        ? 'border-b-2 border-primary text-primary bg-primary/5'
                        : 'text-muted-foreground hover:text-foreground hover:bg-secondary/50'
                    )}
                  >
                    <TestTube className="h-4 w-4" />
                    테스트케이스
                    {(() => {
                      let count = 0;
                      if (problem.input_output) {
                        if (typeof problem.input_output === 'string') {
                          try {
                            const parsed = JSON.parse(problem.input_output);
                            count = parsed?.inputs?.length || 0;
                          } catch {
                            count = 0;
                          }
                        } else {
                          count = (problem.input_output as { inputs?: string[] })?.inputs?.length || 0;
                        }
                      }
                      return count > 0 ? (
                        <Badge variant="secondary" className="text-[10px] px-1.5 py-0">
                          {count}
                        </Badge>
                      ) : null;
                    })()}
                  </button>
                </div>

                {/* Tab Content */}
                <div className="p-4">
                  {leftTab === 'problem' ? (
                    /* 문제 설명 탭 */
                    <div className="prose prose-sm dark:prose-invert max-w-none [&_pre]:bg-background/50 [&_pre]:p-3 [&_pre]:rounded-md [&_code]:text-primary [&_code]:bg-background/50 [&_code]:px-1 [&_code]:py-0.5 [&_code]:rounded [&_p]:text-[13px] [&_li]:text-[13px] [&_h1]:text-base [&_h2]:text-sm [&_h3]:text-sm">
                      <ReactMarkdown
                        remarkPlugins={[remarkGfm, remarkMath, remarkBreaks]}
                        rehypePlugins={[rehypeKatex]}
                      >
                        {displayQuestion || ''}
                      </ReactMarkdown>
                    </div>
                  ) : (
                    /* 테스트케이스 탭 */
                    <div className="space-y-4">
                      {(() => {
                        // Parse input_output (could be JSON string or object)
                        let ioData: { inputs?: string[]; outputs?: string[] } | null = null;
                        if (problem.input_output) {
                          if (typeof problem.input_output === 'string') {
                            try {
                              ioData = JSON.parse(problem.input_output);
                            } catch {
                              ioData = null;
                            }
                          } else {
                            ioData = problem.input_output as { inputs?: string[]; outputs?: string[] };
                          }
                        }

                        if (!ioData?.inputs || ioData.inputs.length === 0) {
                          return (
                            <div className="text-center py-8 text-muted-foreground">
                              <TestTube className="h-8 w-8 mx-auto mb-2 opacity-50" />
                              <p className="text-sm">테스트케이스가 없습니다.</p>
                            </div>
                          );
                        }

                        return ioData.inputs.map((input, idx) => (
                          <div key={idx} className="space-y-2">
                            <h4 className="text-sm font-medium text-muted-foreground">
                              Example {idx + 1}
                            </h4>
                            <div className="grid grid-cols-2 gap-3">
                              <div className="rounded-lg border border-border overflow-hidden">
                                <div className="bg-muted/50 px-3 py-1.5 border-b border-border text-sm font-medium">
                                  Input
                                </div>
                                <pre className="p-3 text-xs font-mono overflow-auto max-h-32 whitespace-pre text-blue-600 dark:text-blue-400">
                                  {input}
                                </pre>
                              </div>
                              <div className="rounded-lg border border-border overflow-hidden">
                                <div className="bg-muted/50 px-3 py-1.5 border-b border-border text-sm font-medium">
                                  Output
                                </div>
                                <pre className="p-3 text-xs font-mono overflow-auto max-h-32 whitespace-pre text-red-600 dark:text-red-400">
                                  {ioData?.outputs?.[idx] || ''}
                                </pre>
                              </div>
                            </div>
                          </div>
                        ));
                      })()}
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* 오른쪽: Solutions */}
            <div className="lg:w-1/2">
              {/* Solutions Header */}
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-bold flex items-center gap-2">
                  <MessageSquare className="h-5 w-5" />
                  Solutions
                </h2>
                <Button size="sm" onClick={() => setShowForm(!showForm)}>
                  <PenLine className="h-4 w-4 mr-1" />
                  {showForm ? '취소' : '내 풀이'}
                </Button>
              </div>

              {/* Solution Form */}
              {showForm && (
                <div className="mb-4">
                  <SolutionForm
                    baseProblemId={problem.id}
                    onSuccess={handleSolutionCreated}
                    onCancel={() => setShowForm(false)}
                  />
                </div>
              )}

              {/* Tabs */}
              <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as 'official' | 'community')}>
                <TabsList className="mb-3">
                  <TabsTrigger value="community">
                    커뮤니티 ({data?.user_solutions.total || 0})
                  </TabsTrigger>
                  <TabsTrigger value="official">
                    공식 ({data?.official_solutions.length || 0})
                  </TabsTrigger>
                </TabsList>

                <TabsContent value="community" className="mt-0">
                  {/* Sort Options */}
                  <div className="flex gap-1 mb-3">
                    <Button
                      variant={sortBy === 'upvotes' ? 'default' : 'ghost'}
                      size="sm"
                      className="h-7 px-2 text-xs"
                      onClick={() => setSortBy('upvotes')}
                    >
                      인기순
                    </Button>
                    <Button
                      variant={sortBy === 'newest' ? 'default' : 'ghost'}
                      size="sm"
                      className="h-7 px-2 text-xs"
                      onClick={() => setSortBy('newest')}
                    >
                      최신순
                    </Button>
                    <Button
                      variant={sortBy === 'oldest' ? 'default' : 'ghost'}
                      size="sm"
                      className="h-7 px-2 text-xs"
                      onClick={() => setSortBy('oldest')}
                    >
                      오래된순
                    </Button>
                  </div>

                  {/* Solution List */}
                  <SolutionList
                    solutions={data?.user_solutions.items || []}
                    onVote={handleVote}
                    onRefresh={fetchData}
                    loading={loading}
                  />

                  {/* Pagination */}
                  {data?.user_solutions && data.user_solutions.has_more && (
                    <div className="flex justify-center mt-4 pb-4">
                      <Button
                        variant="outline"
                        onClick={() => setPage((p) => p + 1)}
                        disabled={loading}
                      >
                        {loading ? (
                          <Loader2 className="h-4 w-4 animate-spin mr-2" />
                        ) : null}
                        더 보기
                      </Button>
                    </div>
                  )}
                </TabsContent>

                <TabsContent value="official" className="mt-0">
                  <OfficialSolutions solutions={data?.official_solutions || []} />
                </TabsContent>
              </Tabs>
            </div>
          </div>
        </main>
      )}
    </div>
  );
}
