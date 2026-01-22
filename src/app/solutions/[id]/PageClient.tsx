'use client';


import { useState, useEffect, useCallback } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { Header } from '@/components/layout/Header';
import { TopNav } from '@/components/layout/TopNav';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { CommentSection } from '@/components/solutions/CommentSection';
import {
  solutionsApi,
  type SolutionDetail,
  type CommentItem,
} from '@/lib/api';
import {
  ArrowLeft,
  Loader2,
  RefreshCw,
  ThumbsUp,
  ThumbsDown,
  Play,
  Edit,
  Trash2,
  MessageCircle,
  Eye,
} from 'lucide-react';
import { Skeleton } from '@/components/ui/skeleton';
import { cn } from '@/lib/utils';
import { formatDistanceToNow } from 'date-fns';
import { ko } from 'date-fns/locale';
import { CodeBlock } from '@/components/ui/code-block';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const languageLabels: Record<string, string> = {
  python: 'Python',
  java: 'Java',
  cpp: 'C++',
  javascript: 'JavaScript',
  typescript: 'TypeScript',
};

export default function SolutionDetailPageClient() {
  const params = useParams();
  const router = useRouter();
  const solutionId = params.id as string;

  const [solution, setSolution] = useState<SolutionDetail | null>(null);
  const [comments, setComments] = useState<CommentItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    if (!solutionId) return;

    setLoading(true);
    setError(null);

    try {
      const [solutionData, commentsData] = await Promise.all([
        solutionsApi.getSolution(solutionId),
        solutionsApi.listComments(solutionId),
      ]);
      setSolution(solutionData);
      setComments(commentsData.items);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load solution');
    } finally {
      setLoading(false);
    }
  }, [solutionId]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleVote = async (voteType: 'up' | 'down') => {
    if (!solution) return;
    try {
      const result = await solutionsApi.voteSolution(solution.id, voteType);
      setSolution((prev) =>
        prev
          ? {
              ...prev,
              upvotes: result.upvotes,
              downvotes: result.downvotes,
              my_vote: result.my_vote,
            }
          : null
      );
    } catch (err) {
      console.error('Vote failed:', err);
    }
  };

  const handleCommentCreated = () => {
    fetchData();
  };

  if (loading && !solution) {
    return (
      <div className="min-h-screen bg-background">
        <Header />
        <TopNav />
        <main className="container max-w-4xl mx-auto px-4 py-6">
          {/* Back button skeleton */}
          <Skeleton className="h-5 w-40 mb-6" />

          {/* Solution Header Skeleton */}
          <div className="border border-border rounded-lg overflow-hidden bg-card mb-6">
            {/* Author Info */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-border">
              <div className="flex items-center gap-3">
                <Skeleton className="h-10 w-10 rounded-full" />
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <Skeleton className="h-4 w-24" />
                    <Skeleton className="h-5 w-16" />
                  </div>
                  <Skeleton className="h-3 w-32" />
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Skeleton className="h-9 w-16" />
                <Skeleton className="h-9 w-16" />
              </div>
            </div>

            {/* Title */}
            <div className="px-6 py-3 border-b border-border">
              <Skeleton className="h-6 w-2/3" />
            </div>

            {/* Description */}
            <div className="px-6 py-4 border-b border-border space-y-2">
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-5/6" />
              <Skeleton className="h-4 w-4/5" />
            </div>

            {/* Code */}
            <Skeleton className="h-64 w-full rounded-none" />
          </div>

          {/* Comments Section Skeleton */}
          <div className="border border-border rounded-lg bg-card">
            <div className="px-6 py-4 border-b border-border">
              <Skeleton className="h-5 w-24" />
            </div>
            <div className="p-6 space-y-4">
              {[1, 2].map((i) => (
                <div key={i} className="flex gap-3">
                  <Skeleton className="h-8 w-8 rounded-full" />
                  <div className="flex-1 space-y-2">
                    <Skeleton className="h-4 w-32" />
                    <Skeleton className="h-4 w-full" />
                    <Skeleton className="h-4 w-3/4" />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </main>
      </div>
    );
  }

  if (error && !solution) {
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

  if (!solution) return null;

  const authorInitial = solution.author_name?.charAt(0).toUpperCase() || 'U';
  const timeAgo = formatDistanceToNow(new Date(solution.created_at), {
    addSuffix: true,
    locale: ko,
  });

  return (
    <div className="min-h-screen bg-background">
      <Header />
      <TopNav />

      <main className="container max-w-4xl mx-auto px-4 py-6">
        {/* Back button */}
        {solution.problem_original_id && (
          <Link
            href={`/problems/${solution.problem_original_id}`}
            className="inline-flex items-center text-muted-foreground hover:text-foreground mb-6"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            {solution.problem_name || '문제로 돌아가기'}
          </Link>
        )}

        {/* Solution Header */}
        <div className="border border-border rounded-lg overflow-hidden bg-card mb-6">
          {/* Author Info */}
          <div className="flex items-center justify-between px-6 py-4 border-b border-border">
            <div className="flex items-center gap-3">
              <Avatar className="h-10 w-10">
                <AvatarImage src={solution.author_avatar || undefined} />
                <AvatarFallback>{authorInitial}</AvatarFallback>
              </Avatar>
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-medium">
                    {solution.author_name || '익명'}
                  </span>
                  <Badge variant="outline" className="text-xs">
                    {languageLabels[solution.language] || solution.language}
                  </Badge>
                </div>
                <div className="flex items-center gap-3 text-sm text-muted-foreground">
                  <span>{timeAgo}</span>
                  <span className="flex items-center gap-1">
                    <Eye className="h-3.5 w-3.5" />
                    {solution.view_count}
                  </span>
                </div>
              </div>
            </div>

            {/* Vote Buttons */}
            <div className="flex items-center gap-2">
              <Button
                variant={solution.my_vote === 'up' ? 'default' : 'outline'}
                size="sm"
                className="gap-1"
                onClick={() => handleVote('up')}
              >
                <ThumbsUp className="h-4 w-4" />
                {solution.upvotes}
              </Button>
              <Button
                variant={solution.my_vote === 'down' ? 'destructive' : 'outline'}
                size="sm"
                className="gap-1"
                onClick={() => handleVote('down')}
              >
                <ThumbsDown className="h-4 w-4" />
                {solution.downvotes}
              </Button>
            </div>
          </div>

          {/* Title */}
          {solution.title && (
            <div className="px-6 py-3 border-b border-border">
              <h1 className="text-xl font-bold">{solution.title}</h1>
            </div>
          )}

          {/* Description */}
          {solution.description && (
            <div className="px-6 py-4 border-b border-border">
              <div className="prose prose-sm dark:prose-invert max-w-none">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {solution.description}
                </ReactMarkdown>
              </div>
            </div>
          )}

          {/* Code */}
          <div>
            <CodeBlock code={solution.code} language={solution.language} />
          </div>
        </div>

        {/* Comments Section */}
        <div className="border border-border rounded-lg bg-card">
          <div className="px-6 py-4 border-b border-border">
            <h2 className="font-semibold flex items-center gap-2">
              <MessageCircle className="h-5 w-5" />
              댓글 ({solution.comment_count})
            </h2>
          </div>
          <CommentSection
            solutionId={solution.id}
            comments={comments}
            onCommentCreated={handleCommentCreated}
          />
        </div>
      </main>
    </div>
  );
}
