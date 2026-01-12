'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { X, Globe, ExternalLink, Loader2, Copy, Check, MessageSquare, LogIn } from 'lucide-react';
import Link from 'next/link';
import { problemsApi, type BaseProblemDetail } from '@/lib/api';
import { apiClient } from '@/lib/api/client';
import { translateText, type LanguageCode } from '@/lib/api/translate';
import { cn, preprocessLatex } from '@/lib/utils';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import remarkBreaks from 'remark-breaks';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';

// Copy button component
function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <button
      onClick={handleCopy}
      className="text-xs text-muted-foreground hover:text-foreground transition-colors flex items-center gap-1"
    >
      {copied ? (
        <>
          <Check className="h-3 w-3" />
          Copied
        </>
      ) : (
        <>
          <Copy className="h-3 w-3" />
          Copy
        </>
      )}
    </button>
  );
}

interface PreviewModalProps {
  originalId: string | null;
  onClose: () => void;
}

const difficultyColors: Record<string, string> = {
  easy: 'bg-primary/20 text-primary border-primary/30',
  medium: 'bg-warning/20 text-warning border-warning/30',
  hard: 'bg-destructive/20 text-destructive border-destructive/30',
};

export function PreviewModal({ originalId, onClose }: PreviewModalProps) {
  const router = useRouter();
  const [problem, setProblem] = useState<BaseProblemDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showLoginDialog, setShowLoginDialog] = useState(false);

  // Translation state
  const [translatedQuestion, setTranslatedQuestion] = useState<string | null>(null);
  const [isTranslating, setIsTranslating] = useState(false);
  const [showTranslated, setShowTranslated] = useState(false);

  const handleStartPractice = () => {
    if (!problem) return;

    // Check if user is logged in
    if (!apiClient.isAuthenticated()) {
      setShowLoginDialog(true);
      return;
    }

    // Navigate to chat page
    router.push(`/chat?problem_id=${problem.original_id}`);
  };

  useEffect(() => {
    if (!originalId) return;

    const fetchProblem = async () => {
      setLoading(true);
      setError(null);
      setProblem(null);
      setTranslatedQuestion(null);
      setShowTranslated(false);

      try {
        const data = await problemsApi.getBase(originalId);
        setProblem(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load problem');
      } finally {
        setLoading(false);
      }
    };

    fetchProblem();
  }, [originalId]);

  const handleTranslate = async () => {
    if (!problem?.question) return;

    // Toggle between original and translated
    if (translatedQuestion) {
      setShowTranslated(!showTranslated);
      return;
    }

    setIsTranslating(true);
    try {
      const result = await translateText(problem.question, 'ko' as LanguageCode);
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

  // Close on escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleEscape);
    return () => window.removeEventListener('keydown', handleEscape);
  }, [onClose]);

  if (!originalId) return null;

  const displayQuestion = showTranslated && translatedQuestion ? translatedQuestion : problem?.question;

  return (
    <>
    <AnimatePresence>
      {originalId && (
      <motion.div
        key="preview-modal-overlay"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
        onClick={onClose}
      >
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          transition={{ type: 'spring', damping: 25, stiffness: 300 }}
          className="relative w-full max-w-3xl max-h-[85vh] overflow-hidden rounded-xl border border-border bg-card shadow-2xl"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="flex items-center justify-between border-b border-border px-6 py-4">
            <div className="flex items-center gap-3 flex-wrap">
              <h2 className="text-lg font-semibold">
                {loading ? 'Loading...' : problem?.name || 'Problem Preview'}
              </h2>
              {problem && (
                <>
                  <Badge
                    variant="outline"
                    className={cn('capitalize', difficultyColors[problem.difficulty] || '')}
                  >
                    {problem.difficulty}
                  </Badge>
                  {problem.source && (
                    <Badge variant="secondary" className="text-xs">
                      {problem.source}
                    </Badge>
                  )}
                </>
              )}
            </div>
            <div className="flex items-center gap-2">
              {/* Translate button */}
              {problem?.question && (
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
                  <span className="ml-1.5">
                    {showTranslated ? '원본' : '번역'}
                  </span>
                </Button>
              )}
              {/* External link */}
              {problem?.url && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => window.open(problem.url!, '_blank')}
                >
                  <ExternalLink className="h-4 w-4" />
                </Button>
              )}
              {/* Close button */}
              <Button variant="ghost" size="icon" onClick={onClose}>
                <X className="h-4 w-4" />
              </Button>
            </div>
          </div>

          {/* Content */}
          <div className="overflow-y-auto p-6" style={{ maxHeight: 'calc(85vh - 140px)' }}>
            {loading && (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
              </div>
            )}

            {error && (
              <div className="text-center py-12 text-destructive">
                <p>{error}</p>
                <Button variant="outline" className="mt-4" onClick={onClose}>
                  Close
                </Button>
              </div>
            )}

            {problem && !loading && (
              <div className="space-y-6">
                {/* Tags */}
                {problem.tags.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {problem.tags
                      .filter((tag) => tag && tag.trim() !== '')
                      .map((tag, idx) => (
                        <Badge key={`${tag}-${idx}`} variant="outline" className="text-xs">
                          {tag}
                        </Badge>
                      ))}
                  </div>
                )}

                {/* Question - Markdown + LaTeX 렌더링 */}
                <div className="space-y-2">
                  <h3 className="text-sm font-medium text-muted-foreground">Problem</h3>
                  <div className="prose prose-sm dark:prose-invert max-w-none bg-muted/30 rounded-lg p-4 [&_pre]:bg-background/50 [&_pre]:p-3 [&_pre]:rounded-md [&_code]:text-primary [&_code]:bg-background/50 [&_code]:px-1 [&_code]:py-0.5 [&_code]:rounded [&_p]:text-[13px] [&_li]:text-[13px] [&_h1]:text-base [&_h2]:text-sm [&_h3]:text-sm">
                    <ReactMarkdown
                      remarkPlugins={[remarkGfm, remarkMath, remarkBreaks]}
                      rehypePlugins={[rehypeKatex]}
                    >
                      {preprocessLatex(displayQuestion || '')}
                    </ReactMarkdown>
                  </div>
                </div>

                {/* Input/Output Examples */}
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
                      ioData = problem.input_output;
                    }
                  }

                  if (!ioData?.inputs || ioData.inputs.length === 0) return null;

                  // Show only first 3 examples
                  const examples = ioData.inputs.slice(0, 3).map((input, idx) => ({
                    input,
                    output: ioData?.outputs?.[idx] || '',
                  }));

                  return (
                    <div className="space-y-4">
                      <h3 className="text-sm font-semibold">Examples</h3>
                      {examples.map((example, idx) => (
                        <div key={idx} className="grid grid-cols-2 gap-3">
                          {/* Input Box */}
                          <div className="rounded-lg border border-border overflow-hidden">
                            <div className="flex items-center justify-between bg-muted/50 px-3 py-1.5 border-b border-border">
                              <span className="text-sm font-medium">input</span>
                              <CopyButton text={example.input} />
                            </div>
                            <pre className="p-3 text-sm font-mono overflow-auto max-h-40 whitespace-pre text-blue-600 dark:text-blue-400">
                              {example.input}
                            </pre>
                          </div>
                          {/* Output Box */}
                          <div className="rounded-lg border border-border overflow-hidden">
                            <div className="flex items-center justify-between bg-muted/50 px-3 py-1.5 border-b border-border">
                              <span className="text-sm font-medium">output</span>
                              <CopyButton text={example.output} />
                            </div>
                            <pre className="p-3 text-sm font-mono overflow-auto max-h-40 whitespace-pre text-red-600 dark:text-red-400">
                              {example.output}
                            </pre>
                          </div>
                        </div>
                      ))}
                    </div>
                  );
                })()}

                {/* Explanation */}
                {problem.explanation && (
                  <div className="space-y-2">
                    <h3 className="text-sm font-medium text-muted-foreground">Explanation</h3>
                    <div className="prose prose-sm dark:prose-invert max-w-none">
                      <ReactMarkdown
                        remarkPlugins={[remarkGfm, remarkMath, remarkBreaks]}
                        rehypePlugins={[rehypeKatex]}
                      >
                        {preprocessLatex(problem.explanation)}
                      </ReactMarkdown>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Footer */}
          {problem && !loading && (
            <div className="flex justify-end gap-2 border-t border-border px-6 py-4">
              <Button variant="outline" onClick={onClose}>
                Close
              </Button>
              <Link href={`/problems/${problem.original_id}`}>
                <Button variant="outline">
                  <MessageSquare className="h-4 w-4 mr-2" />
                  Discussion
                </Button>
              </Link>
              <Button onClick={handleStartPractice}>
                Start Practice
              </Button>
            </div>
          )}
        </motion.div>
      </motion.div>
      )}
    </AnimatePresence>

    {/* Login Required Dialog */}
    <Dialog open={showLoginDialog} onOpenChange={setShowLoginDialog}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <LogIn className="h-5 w-5" />
            로그인이 필요합니다
          </DialogTitle>
          <DialogDescription>
            문제를 풀려면 로그인이 필요합니다.<br />
            로그인하면 XP 획득과 잔디 기록이 저장됩니다.
          </DialogDescription>
        </DialogHeader>
        <DialogFooter className="flex gap-2 sm:justify-end">
          <Button variant="outline" onClick={() => setShowLoginDialog(false)}>
            취소
          </Button>
          <Button onClick={() => router.push('/login')}>
            <LogIn className="mr-2 h-4 w-4" />
            로그인하기
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
    </>
  );
}
