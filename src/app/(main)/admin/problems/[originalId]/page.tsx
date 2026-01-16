'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { useParams, useRouter, useSearchParams } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ArrowLeft,
  Save,
  Code2,
  Puzzle,
  BookOpen,
  Plus,
  Trash2,
  Edit,
  X,
  CheckCircle,
  XCircle,
  Calendar,
  Hash,
  ExternalLink,
  Clock,
  HardDrive,
  Tag,
  FileCode,
  Sparkles,
  Flame,
  Zap,
  ChevronDown,
  ChevronUp,
  Copy,
  Check,
  Users,
  Heart,
  MessageSquare,
  ThumbsUp,
  ThumbsDown,
  Eye,
  RefreshCw,
  MoreHorizontal,
  FlaskConical,
} from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import { adminApi, type AdminProblemDetail } from '@/lib/api/admin';
import {
  solutionsApi,
  type SolutionListItem,
  type SolutionDetail,
  type CommentItem,
} from '@/lib/api/solutions';
import { problemsApi } from '@/lib/api/problems';
import { toast } from 'sonner';
import { CodeBlock } from '@/components/ui/code-block';
import { getLanguageLabel, getLanguageColor } from '@/components/solutions/constants';
import { formatDistanceToNow } from 'date-fns';
import { ko } from 'date-fns/locale';

// 난이도 설정
const difficultyConfig: Record<string, { label: string; color: string; bgColor: string; borderColor: string; icon: React.ReactNode }> = {
  easy: {
    label: 'Easy',
    color: 'text-emerald-400',
    bgColor: 'bg-emerald-500/10',
    borderColor: 'border-emerald-500/20',
    icon: <Sparkles className="h-3.5 w-3.5" />,
  },
  medium: {
    label: 'Medium',
    color: 'text-amber-400',
    bgColor: 'bg-amber-500/10',
    borderColor: 'border-amber-500/20',
    icon: <Zap className="h-3.5 w-3.5" />,
  },
  hard: {
    label: 'Hard',
    color: 'text-rose-400',
    bgColor: 'bg-rose-500/10',
    borderColor: 'border-rose-500/20',
    icon: <Flame className="h-3.5 w-3.5" />,
  },
};

const difficultyOptions = [
  { value: 'easy', label: 'Easy' },
  { value: 'medium', label: 'Medium' },
  { value: 'hard', label: 'Hard' },
];

const languageOptions = [
  { value: 'python', label: 'Python' },
  { value: 'javascript', label: 'JavaScript' },
  { value: 'typescript', label: 'TypeScript' },
  { value: 'java', label: 'Java' },
  { value: 'cpp', label: 'C++' },
];

export default function AdminProblemDetailPage() {
  const params = useParams();
  const router = useRouter();
  const searchParams = useSearchParams();
  const originalId = params.originalId as string;
  const isEditMode = searchParams.get('edit') === 'true';

  // Problem state
  const [problem, setProblem] = useState<AdminProblemDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [editing, setEditing] = useState(isEditMode);

  // Community state
  const [solutions, setSolutions] = useState<SolutionListItem[]>([]);
  const [solutionsTotal, setSolutionsTotal] = useState(0);
  const [loadingSolutions, setLoadingSolutions] = useState(false);
  const [stats, setStats] = useState({ solve_count: 0, like_count: 0 });

  // Community solution detail (accordion)
  const [expandedCommunitySolution, setExpandedCommunitySolution] = useState<string | null>(null);
  const [communitySolutionDetails, setCommunitySolutionDetails] = useState<Record<string, { detail: SolutionDetail; comments: CommentItem[] }>>({});
  const [loadingCommunitySolution, setLoadingCommunitySolution] = useState<string | null>(null);

  // UI state
  const [deleteVariant, setDeleteVariant] = useState<{ type: 'blank' | 'puzzle' | 'guided'; id: string } | null>(null);
  const [deleteSolution, setDeleteSolution] = useState<{ id: string; title: string | null } | null>(null);
  const [deleteComment, setDeleteComment] = useState<{ id: string; solutionId: string } | null>(null);
  const [expandedSolution, setExpandedSolution] = useState<number | null>(null);
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

  // Form state
  const [formData, setFormData] = useState({
    name: '',
    question: '',
    difficulty: '',
    tags: [] as string[],
    source: '',
    url: '',
    time_limit: '',
    memory_limit: '',
    solutions: [{ language: 'python', code: '' }],
    input_output: { inputs: [] as string[], outputs: [] as string[] },
  });
  const [tagInput, setTagInput] = useState('');
  const [copiedTestCase, setCopiedTestCase] = useState<{ idx: number; type: 'input' | 'output' } | null>(null);

  // Parse input_output helper
  const parseInputOutput = (io: any): { inputs: string[]; outputs: string[] } => {
    if (!io) return { inputs: [], outputs: [] };
    if (typeof io === 'string') {
      try {
        const parsed = JSON.parse(io);
        return {
          inputs: parsed.inputs || [],
          outputs: parsed.outputs || [],
        };
      } catch {
        return { inputs: [], outputs: [] };
      }
    }
    return {
      inputs: io.inputs || [],
      outputs: io.outputs || [],
    };
  };

  // Fetch problem data
  useEffect(() => {
    const fetchProblem = async () => {
      try {
        const data = await adminApi.getProblemDetail(originalId);
        setProblem(data);
        setFormData({
          name: data.name,
          question: data.question,
          difficulty: data.difficulty,
          tags: data.tags || [],
          source: data.source || '',
          url: data.url || '',
          time_limit: data.time_limit || '',
          memory_limit: data.memory_limit || '',
          solutions: data.solutions || [{ language: 'python', code: '' }],
          input_output: parseInputOutput(data.input_output),
        });
      } catch (error) {
        console.error('Failed to fetch problem:', error);
        toast.error('문제 정보를 불러오는데 실패했습니다');
        router.push('/admin/problems');
      } finally {
        setLoading(false);
      }
    };

    fetchProblem();
  }, [originalId, router]);

  // Fetch community solutions
  const fetchSolutions = useCallback(async () => {
    if (!problem?.id) return;

    setLoadingSolutions(true);
    try {
      const response = await solutionsApi.getProblemDiscussion(originalId, {
        page: 1,
        limit: 20,
        sort: 'upvotes',
      });
      setSolutions(response.user_solutions.items);
      setSolutionsTotal(response.user_solutions.total);
    } catch (error) {
      console.error('Failed to fetch solutions:', error);
    } finally {
      setLoadingSolutions(false);
    }
  }, [originalId, problem?.id]);

  // Fetch stats
  const fetchStats = useCallback(async () => {
    if (!problem?.id) return;

    try {
      const statsData = await problemsApi.getStats(problem.id);
      setStats({
        solve_count: statsData.solve_count,
        like_count: statsData.like_count,
      });
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  }, [problem?.id]);

  useEffect(() => {
    if (problem?.id) {
      fetchSolutions();
      fetchStats();
    }
  }, [problem?.id, fetchSolutions, fetchStats]);

  // Toggle community solution accordion
  const handleToggleSolution = async (solutionId: string) => {
    if (expandedCommunitySolution === solutionId) {
      setExpandedCommunitySolution(null);
      return;
    }

    setExpandedCommunitySolution(solutionId);

    // Already fetched
    if (communitySolutionDetails[solutionId]) return;

    setLoadingCommunitySolution(solutionId);
    try {
      const [detail, commentsResponse] = await Promise.all([
        solutionsApi.getSolution(solutionId),
        solutionsApi.listComments(solutionId),
      ]);
      setCommunitySolutionDetails((prev) => ({
        ...prev,
        [solutionId]: { detail, comments: commentsResponse.items },
      }));
    } catch (error) {
      console.error('Failed to fetch solution:', error);
      toast.error('풀이를 불러오는데 실패했습니다');
    } finally {
      setLoadingCommunitySolution(null);
    }
  };

  // Delete community solution
  const handleDeleteSolution = async () => {
    if (!deleteSolution) return;
    try {
      await adminApi.deleteSolution(deleteSolution.id);
      toast.success('풀이가 삭제되었습니다');
      setSolutions((prev) => prev.filter((s) => s.id !== deleteSolution.id));
      setSolutionsTotal((prev) => prev - 1);
      setCommunitySolutionDetails((prev) => {
        const newDetails = { ...prev };
        delete newDetails[deleteSolution.id];
        return newDetails;
      });
      if (expandedCommunitySolution === deleteSolution.id) {
        setExpandedCommunitySolution(null);
      }
    } catch (error) {
      console.error('Failed to delete solution:', error);
      toast.error('풀이 삭제에 실패했습니다');
    } finally {
      setDeleteSolution(null);
    }
  };

  // Delete comment
  const handleDeleteComment = async () => {
    if (!deleteComment) return;
    try {
      await adminApi.deleteComment(deleteComment.id);
      toast.success('댓글이 삭제되었습니다');
      // Update comments in the cached solution details
      setCommunitySolutionDetails((prev) => {
        const solutionData = prev[deleteComment.solutionId];
        if (!solutionData) return prev;
        return {
          ...prev,
          [deleteComment.solutionId]: {
            ...solutionData,
            comments: solutionData.comments.filter((c) => c.id !== deleteComment.id),
          },
        };
      });
    } catch (error) {
      console.error('Failed to delete comment:', error);
      toast.error('댓글 삭제에 실패했습니다');
    } finally {
      setDeleteComment(null);
    }
  };

  const handleSave = async () => {
    if (!problem) return;

    setSaving(true);
    try {
      await adminApi.updateProblem(originalId, {
        name: formData.name,
        question: formData.question,
        difficulty: formData.difficulty,
        tags: formData.tags,
        source: formData.source || undefined,
        url: formData.url || undefined,
        time_limit: formData.time_limit || undefined,
        memory_limit: formData.memory_limit || undefined,
        solutions: formData.solutions.filter(s => s.code.trim()),
        input_output: formData.input_output,
      });
      toast.success('문제가 수정되었습니다');
      setEditing(false);
      const data = await adminApi.getProblemDetail(originalId);
      setProblem(data);
      setFormData(prev => ({
        ...prev,
        input_output: parseInputOutput(data.input_output),
      }));
    } catch (error) {
      console.error('Failed to update problem:', error);
      toast.error('문제 수정에 실패했습니다');
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteVariant = async () => {
    if (!deleteVariant || !problem) return;

    try {
      if (deleteVariant.type === 'blank') {
        await adminApi.deleteBlankProblem(originalId, deleteVariant.id);
      } else if (deleteVariant.type === 'puzzle') {
        await adminApi.deletePuzzleProblem(originalId, deleteVariant.id);
      } else if (deleteVariant.type === 'guided') {
        await adminApi.deleteGuidedProblem(originalId, deleteVariant.id);
      }
      toast.success('변형 문제가 삭제되었습니다');
      const data = await adminApi.getProblemDetail(originalId);
      setProblem(data);
    } catch (error) {
      console.error('Failed to delete variant:', error);
      toast.error('변형 삭제에 실패했습니다');
    } finally {
      setDeleteVariant(null);
    }
  };

  const handleAddTag = () => {
    if (tagInput.trim() && !formData.tags.includes(tagInput.trim())) {
      setFormData({
        ...formData,
        tags: [...formData.tags, tagInput.trim()],
      });
      setTagInput('');
    }
  };

  const handleRemoveTag = (tag: string) => {
    setFormData({
      ...formData,
      tags: formData.tags.filter((t) => t !== tag),
    });
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center gap-4">
          <div className="h-10 w-10 rounded-xl bg-white/5 animate-pulse" />
          <div className="space-y-2">
            <div className="h-6 w-48 bg-white/5 animate-pulse rounded" />
            <div className="h-4 w-32 bg-white/5 animate-pulse rounded" />
          </div>
        </div>
        <div className="grid lg:grid-cols-2 gap-6">
          <div className="h-96 bg-white/5 animate-pulse rounded-2xl" />
          <div className="h-96 bg-white/5 animate-pulse rounded-2xl" />
        </div>
      </div>
    );
  }

  if (!problem) {
    return null;
  }

  const difficulty = difficultyConfig[problem.difficulty] || difficultyConfig.medium;
  const primaryLanguage = problem.solutions?.[0]?.language || 'python';

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start gap-4">
        <Link href="/admin/problems">
          <Button variant="ghost" size="icon" className="rounded-xl bg-white/5 hover:bg-white/10">
            <ArrowLeft className="h-4 w-4" />
          </Button>
        </Link>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <h1 className="text-xl font-bold truncate">
              {editing ? '문제 수정' : problem.name}
            </h1>
            <span className="text-sm text-muted-foreground font-mono">#{problem.original_id}</span>
          </div>
          <div className="flex items-center gap-2 mt-2 flex-wrap">
            <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-medium ${difficulty.bgColor} ${difficulty.color} border ${difficulty.borderColor}`}>
              {difficulty.icon}
              {difficulty.label}
            </span>
            <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-medium border ${getLanguageColor(primaryLanguage)}`}>
              <FileCode className="h-3 w-3" />
              {getLanguageLabel(primaryLanguage)}
            </span>
            {problem.deleted_at ? (
              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-red-500/10 text-red-400 border border-red-500/20">
                <XCircle className="h-3 w-3" />
                삭제됨
              </span>
            ) : (
              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                <CheckCircle className="h-3 w-3" />
                활성
              </span>
            )}
          </div>
        </div>

        <div className="flex gap-2 shrink-0">
          {editing ? (
            <>
              <Button
                variant="outline"
                size="sm"
                className="rounded-xl bg-white/5 border-white/10 hover:bg-white/10"
                onClick={() => {
                  setEditing(false);
                  setFormData({
                    name: problem.name,
                    question: problem.question,
                    difficulty: problem.difficulty,
                    tags: problem.tags || [],
                    source: problem.source || '',
                    url: problem.url || '',
                    time_limit: problem.time_limit || '',
                    memory_limit: problem.memory_limit || '',
                    solutions: problem.solutions || [{ language: 'python', code: '' }],
                    input_output: parseInputOutput(problem.input_output),
                  });
                }}
              >
                <X className="h-4 w-4 mr-1.5" />
                취소
              </Button>
              <Button size="sm" className="rounded-xl" onClick={handleSave} disabled={saving}>
                <Save className="h-4 w-4 mr-1.5" />
                {saving ? '저장 중...' : '저장'}
              </Button>
            </>
          ) : (
            <Button size="sm" className="rounded-xl" onClick={() => setEditing(true)}>
              <Edit className="h-4 w-4 mr-1.5" />
              수정
            </Button>
          )}
        </div>
      </div>

      {/* Two Column Layout */}
      <div className="grid lg:grid-cols-2 gap-6">
        {/* Left Column - Problem Info */}
        <div className="space-y-4">
          {/* Problem Description */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="admin-glass-card rounded-2xl p-5"
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-semibold flex items-center gap-2">
                <Hash className="h-4 w-4 text-primary" />
                문제 정보
              </h3>
              {!editing && (
                <div className="flex items-center gap-3 text-xs text-muted-foreground">
                  {problem.time_limit && (
                    <span className="flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      {problem.time_limit}
                    </span>
                  )}
                  {problem.memory_limit && (
                    <span className="flex items-center gap-1">
                      <HardDrive className="h-3 w-3" />
                      {problem.memory_limit}
                    </span>
                  )}
                </div>
              )}
            </div>

            {editing ? (
              <div className="space-y-4">
                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-2">
                    <label className="text-xs text-muted-foreground">제목</label>
                    <Input
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      className="bg-white/5 border-white/10 rounded-xl"
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-xs text-muted-foreground">난이도</label>
                    <Select
                      value={formData.difficulty}
                      onValueChange={(v) => setFormData({ ...formData, difficulty: v })}
                    >
                      <SelectTrigger className="bg-white/5 border-white/10 rounded-xl">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {difficultyOptions.map((opt) => (
                          <SelectItem key={opt.value} value={opt.value}>
                            {opt.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-2">
                    <label className="text-xs text-muted-foreground">출처</label>
                    <Input
                      value={formData.source}
                      onChange={(e) => setFormData({ ...formData, source: e.target.value })}
                      placeholder="예: 백준, 프로그래머스"
                      className="bg-white/5 border-white/10 rounded-xl"
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-xs text-muted-foreground">원본 URL</label>
                    <Input
                      value={formData.url}
                      onChange={(e) => setFormData({ ...formData, url: e.target.value })}
                      placeholder="https://..."
                      className="bg-white/5 border-white/10 rounded-xl"
                    />
                  </div>
                </div>

                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-2">
                    <label className="text-xs text-muted-foreground">시간 제한</label>
                    <Input
                      value={formData.time_limit}
                      onChange={(e) => setFormData({ ...formData, time_limit: e.target.value })}
                      placeholder="예: 1초, 2초"
                      className="bg-white/5 border-white/10 rounded-xl"
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-xs text-muted-foreground">메모리 제한</label>
                    <Input
                      value={formData.memory_limit}
                      onChange={(e) => setFormData({ ...formData, memory_limit: e.target.value })}
                      placeholder="예: 128MB, 256MB"
                      className="bg-white/5 border-white/10 rounded-xl"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-xs text-muted-foreground">태그</label>
                  <div className="flex gap-2">
                    <Input
                      value={tagInput}
                      onChange={(e) => setTagInput(e.target.value)}
                      onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddTag())}
                      placeholder="태그 입력 후 Enter"
                      className="flex-1 bg-white/5 border-white/10 rounded-xl"
                    />
                    <Button type="button" variant="outline" size="sm" onClick={handleAddTag} className="rounded-xl bg-white/5 border-white/10">
                      추가
                    </Button>
                  </div>
                  {formData.tags.length > 0 && (
                    <div className="flex flex-wrap gap-2 mt-2">
                      {formData.tags.map((tag) => (
                        <span
                          key={tag}
                          className="inline-flex items-center gap-1 px-2 py-1 rounded-lg text-xs bg-primary/10 text-primary border border-primary/20 cursor-pointer hover:bg-primary/20 transition-colors"
                          onClick={() => handleRemoveTag(tag)}
                        >
                          {tag}
                          <X className="h-3 w-3" />
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                <div className="space-y-2">
                  <label className="text-xs text-muted-foreground">문제 설명</label>
                  <Textarea
                    value={formData.question}
                    onChange={(e) => setFormData({ ...formData, question: e.target.value })}
                    rows={10}
                    className="bg-white/5 border-white/10 rounded-xl font-mono text-sm"
                  />
                </div>
              </div>
            ) : (
              <>
                {/* 출처 & URL */}
                {(problem.source || problem.url) && (
                  <div className="flex items-center gap-4 mb-4 text-xs text-muted-foreground">
                    {problem.source && (
                      <span className="flex items-center gap-1.5">
                        <span className="text-muted-foreground/60">출처:</span>
                        <span>{problem.source}</span>
                      </span>
                    )}
                    {problem.url && (
                      <a
                        href={problem.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-1 text-primary hover:underline"
                      >
                        <ExternalLink className="h-3 w-3" />
                        원본 링크
                      </a>
                    )}
                  </div>
                )}

                {problem.tags && problem.tags.length > 0 && (
                  <div className="flex flex-wrap gap-2 mb-4">
                    {problem.tags.map((tag) => (
                      <span key={tag} className="inline-flex items-center gap-1 px-2 py-1 rounded-lg text-xs bg-white/5 text-muted-foreground border border-white/10">
                        <Tag className="h-3 w-3" />
                        {tag}
                      </span>
                    ))}
                  </div>
                )}
                <div className="p-4 rounded-xl bg-white/3 border border-white/5 max-h-[300px] overflow-auto">
                  <pre className="whitespace-pre-wrap text-sm leading-relaxed">
                    {problem.question}
                  </pre>
                </div>
              </>
            )}
          </motion.div>

          {/* Official Solutions */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="admin-glass-card rounded-2xl p-5"
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-semibold flex items-center gap-2">
                <FileCode className="h-4 w-4 text-primary" />
                공식 솔루션
              </h3>
              <span className="text-xs text-muted-foreground">{problem.solutions?.length || 0}개</span>
            </div>

            {editing ? (
              <div className="space-y-3">
                {formData.solutions.map((solution, index) => (
                  <div key={index} className="space-y-2 p-3 rounded-xl bg-white/3 border border-white/5">
                    <div className="flex items-center justify-between">
                      <Select
                        value={solution.language}
                        onValueChange={(v) => {
                          const newSolutions = [...formData.solutions];
                          newSolutions[index] = { ...newSolutions[index], language: v };
                          setFormData({ ...formData, solutions: newSolutions });
                        }}
                      >
                        <SelectTrigger className="w-[120px] bg-white/5 border-white/10 rounded-lg h-8 text-xs">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {languageOptions.map((opt) => (
                            <SelectItem key={opt.value} value={opt.value}>
                              {opt.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                      {formData.solutions.length > 1 && (
                        <Button
                          type="button"
                          variant="ghost"
                          size="icon"
                          className="h-7 w-7 text-destructive hover:bg-red-500/10"
                          onClick={() => {
                            setFormData({
                              ...formData,
                              solutions: formData.solutions.filter((_, i) => i !== index),
                            });
                          }}
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                        </Button>
                      )}
                    </div>
                    <Textarea
                      value={solution.code}
                      onChange={(e) => {
                        const newSolutions = [...formData.solutions];
                        newSolutions[index] = { ...newSolutions[index], code: e.target.value };
                        setFormData({ ...formData, solutions: newSolutions });
                      }}
                      rows={8}
                      className="font-mono text-xs bg-black/20 border-white/10 rounded-xl"
                    />
                  </div>
                ))}
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  className="w-full rounded-xl bg-white/5 border-white/10"
                  onClick={() => {
                    setFormData({
                      ...formData,
                      solutions: [...formData.solutions, { language: 'python', code: '' }],
                    });
                  }}
                >
                  <Plus className="h-4 w-4 mr-1.5" />
                  솔루션 추가
                </Button>
              </div>
            ) : (
              <div className="space-y-2">
                {problem.solutions?.map((solution, index) => {
                  const isExpanded = expandedSolution === index;
                  const handleCopy = async () => {
                    await navigator.clipboard.writeText(solution.code);
                    setCopiedIndex(index);
                    setTimeout(() => setCopiedIndex(null), 2000);
                  };

                  return (
                    <div key={index} className="rounded-xl border border-white/10 overflow-hidden bg-white/3">
                      <button
                        onClick={() => setExpandedSolution(isExpanded ? null : index)}
                        className="w-full flex items-center justify-between px-3 py-2.5 hover:bg-white/5 transition-colors"
                      >
                        <div className="flex items-center gap-2">
                          <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-xs font-medium border ${getLanguageColor(solution.language)}`}>
                            {getLanguageLabel(solution.language)}
                          </span>
                          <span className="text-xs text-muted-foreground">#{index + 1}</span>
                        </div>
                        {isExpanded ? <ChevronUp className="h-4 w-4 text-muted-foreground" /> : <ChevronDown className="h-4 w-4 text-muted-foreground" />}
                      </button>

                      {isExpanded && (
                        <div className="border-t border-white/10">
                          <div className="flex justify-end px-2 py-1.5 bg-black/20">
                            <Button variant="ghost" size="sm" className="h-6 px-2 gap-1 text-xs hover:bg-white/10" onClick={handleCopy}>
                              {copiedIndex === index ? (
                                <><Check className="h-3 w-3 text-emerald-400" /><span className="text-emerald-400">Copied</span></>
                              ) : (
                                <><Copy className="h-3 w-3" />Copy</>
                              )}
                            </Button>
                          </div>
                          <div className="max-h-[250px] overflow-auto">
                            <CodeBlock code={solution.code} language={solution.language} showLineNumbers={true} />
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })}
                {(!problem.solutions || problem.solutions.length === 0) && (
                  <div className="flex flex-col items-center justify-center py-6 text-center">
                    <FileCode className="h-8 w-8 text-muted-foreground/50 mb-2" />
                    <p className="text-xs text-muted-foreground">솔루션이 없습니다</p>
                  </div>
                )}
              </div>
            )}
          </motion.div>

          {/* Test Cases */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.15 }}
            className="admin-glass-card rounded-2xl p-5"
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-semibold flex items-center gap-2">
                <FlaskConical className="h-4 w-4 text-primary" />
                테스트 케이스
              </h3>
              <span className="text-xs text-muted-foreground">
                {Math.max(formData.input_output.inputs.length, formData.input_output.outputs.length)}개
              </span>
            </div>

            {editing ? (
              <div className="space-y-3">
                {/* 케이스 점프 버튼 바 */}
                {formData.input_output.inputs.length > 3 && (
                  <div className="sticky top-0 z-10 bg-background/95 backdrop-blur-sm -mx-1 px-1 py-2 border-b border-white/5">
                    <div className="flex items-center gap-1.5 flex-wrap">
                      <span className="text-[10px] text-muted-foreground mr-1">이동:</span>
                      {formData.input_output.inputs.length <= 10 ? (
                        // 10개 이하: 개별 버튼
                        formData.input_output.inputs.map((_, idx) => (
                          <button
                            key={idx}
                            onClick={() => {
                              const element = document.getElementById(`test-case-edit-${idx}`);
                              element?.scrollIntoView({ behavior: 'smooth', block: 'center' });
                            }}
                            className="h-6 min-w-[28px] px-1.5 text-[10px] font-medium rounded-md bg-white/5 hover:bg-primary/20 hover:text-primary border border-white/10 transition-colors"
                          >
                            #{idx + 1}
                          </button>
                        ))
                      ) : (
                        // 10개 초과: 10개 단위 그룹 버튼
                        Array.from({ length: Math.ceil(formData.input_output.inputs.length / 10) }, (_, groupIdx) => {
                          const start = groupIdx * 10 + 1;
                          const end = Math.min((groupIdx + 1) * 10, formData.input_output.inputs.length);
                          return (
                            <button
                              key={groupIdx}
                              onClick={() => {
                                const element = document.getElementById(`test-case-edit-${groupIdx * 10}`);
                                element?.scrollIntoView({ behavior: 'smooth', block: 'start' });
                              }}
                              className="h-6 px-2 text-[10px] font-medium rounded-md bg-white/5 hover:bg-primary/20 hover:text-primary border border-white/10 transition-colors"
                            >
                              {start}-{end}
                            </button>
                          );
                        })
                      )}
                    </div>
                  </div>
                )}

                {/* 스크롤 영역 */}
                <div className="max-h-[500px] overflow-auto space-y-3 pr-1">
                  {formData.input_output.inputs.map((input, idx) => (
                    <div
                      key={idx}
                      id={`test-case-edit-${idx}`}
                      className="p-3 rounded-xl bg-white/3 border border-white/5 scroll-mt-16"
                    >
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-xs font-medium text-muted-foreground">케이스 #{idx + 1}</span>
                        <Button
                          type="button"
                          variant="ghost"
                          size="icon"
                          className="h-6 w-6 text-muted-foreground hover:text-destructive hover:bg-red-500/10"
                          onClick={() => {
                            const newInputs = formData.input_output.inputs.filter((_, i) => i !== idx);
                            const newOutputs = formData.input_output.outputs.filter((_, i) => i !== idx);
                            setFormData({
                              ...formData,
                              input_output: { inputs: newInputs, outputs: newOutputs },
                            });
                          }}
                        >
                          <Trash2 className="h-3 w-3" />
                        </Button>
                      </div>
                      <div className="grid grid-cols-2 gap-3">
                        <div className="space-y-1">
                          <label className="text-[10px] text-muted-foreground uppercase tracking-wider">Input</label>
                          <Textarea
                            value={input}
                            onChange={(e) => {
                              const newInputs = [...formData.input_output.inputs];
                              newInputs[idx] = e.target.value;
                              setFormData({
                                ...formData,
                                input_output: { ...formData.input_output, inputs: newInputs },
                              });
                            }}
                            rows={3}
                            className="font-mono text-xs bg-black/20 border-white/10 rounded-lg resize-none"
                            placeholder="입력값"
                          />
                        </div>
                        <div className="space-y-1">
                          <label className="text-[10px] text-muted-foreground uppercase tracking-wider">Output</label>
                          <Textarea
                            value={formData.input_output.outputs[idx] || ''}
                            onChange={(e) => {
                              const newOutputs = [...formData.input_output.outputs];
                              newOutputs[idx] = e.target.value;
                              setFormData({
                                ...formData,
                                input_output: { ...formData.input_output, outputs: newOutputs },
                              });
                            }}
                            rows={3}
                            className="font-mono text-xs bg-black/20 border-white/10 rounded-lg resize-none"
                            placeholder="출력값"
                          />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  className="w-full rounded-xl bg-white/5 border-white/10"
                  onClick={() => {
                    setFormData({
                      ...formData,
                      input_output: {
                        inputs: [...formData.input_output.inputs, ''],
                        outputs: [...formData.input_output.outputs, ''],
                      },
                    });
                    // 새로 추가한 케이스로 스크롤
                    setTimeout(() => {
                      const newIdx = formData.input_output.inputs.length;
                      const element = document.getElementById(`test-case-edit-${newIdx}`);
                      element?.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    }, 100);
                  }}
                >
                  <Plus className="h-4 w-4 mr-1.5" />
                  테스트 케이스 추가
                </Button>
              </div>
            ) : (
              <div className="space-y-3">
                {formData.input_output.inputs.length > 0 ? (
                  <>
                    {/* 케이스 점프 버튼 바 (보기 모드) */}
                    {formData.input_output.inputs.length > 3 && (
                      <div className="flex items-center gap-1.5 flex-wrap pb-3 border-b border-white/5">
                        <span className="text-[10px] text-muted-foreground mr-1">이동:</span>
                        {formData.input_output.inputs.length <= 10 ? (
                          // 10개 이하: 개별 버튼
                          formData.input_output.inputs.map((_, idx) => (
                            <button
                              key={idx}
                              onClick={() => {
                                const element = document.getElementById(`test-case-view-${idx}`);
                                element?.scrollIntoView({ behavior: 'smooth', block: 'center' });
                              }}
                              className="h-6 min-w-[28px] px-1.5 text-[10px] font-medium rounded-md bg-white/5 hover:bg-primary/20 hover:text-primary border border-white/10 transition-colors"
                            >
                              #{idx + 1}
                            </button>
                          ))
                        ) : (
                          // 10개 초과: 10개 단위 그룹 버튼
                          Array.from({ length: Math.ceil(formData.input_output.inputs.length / 10) }, (_, groupIdx) => {
                            const start = groupIdx * 10 + 1;
                            const end = Math.min((groupIdx + 1) * 10, formData.input_output.inputs.length);
                            return (
                              <button
                                key={groupIdx}
                                onClick={() => {
                                  const element = document.getElementById(`test-case-view-${groupIdx * 10}`);
                                  element?.scrollIntoView({ behavior: 'smooth', block: 'start' });
                                }}
                                className="h-6 px-2 text-[10px] font-medium rounded-md bg-white/5 hover:bg-primary/20 hover:text-primary border border-white/10 transition-colors"
                              >
                                {start}-{end}
                              </button>
                            );
                          })
                        )}
                      </div>
                    )}

                    {/* 스크롤 영역 */}
                    <div className="max-h-[400px] overflow-auto space-y-3 pr-1">
                      {formData.input_output.inputs.map((input, idx) => (
                        <div
                          key={idx}
                          id={`test-case-view-${idx}`}
                          className="rounded-xl border border-white/10 overflow-hidden bg-white/3 scroll-mt-4"
                        >
                          <div className="flex items-center justify-between px-3 py-1.5 bg-white/3 border-b border-white/10">
                            <span className="text-xs font-medium text-muted-foreground">케이스 #{idx + 1}</span>
                          </div>
                          <div className="grid grid-cols-2 gap-0">
                            {/* Input */}
                            <div className="border-r border-white/10">
                              <div className="flex items-center justify-between px-3 py-1.5 bg-blue-500/5 border-b border-white/10">
                                <span className="text-[10px] font-medium text-blue-400 uppercase tracking-wider">Input</span>
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  className="h-5 px-1.5 gap-1 text-[10px] hover:bg-white/10"
                                  onClick={async () => {
                                    await navigator.clipboard.writeText(input);
                                    setCopiedTestCase({ idx, type: 'input' });
                                    setTimeout(() => setCopiedTestCase(null), 2000);
                                  }}
                                >
                                  {copiedTestCase?.idx === idx && copiedTestCase?.type === 'input' ? (
                                    <><Check className="h-2.5 w-2.5 text-emerald-400" /><span className="text-emerald-400">Copied</span></>
                                  ) : (
                                    <><Copy className="h-2.5 w-2.5" />Copy</>
                                  )}
                                </Button>
                              </div>
                              <pre className="p-3 text-xs font-mono overflow-auto max-h-32 whitespace-pre text-blue-400">
                                {input || '(없음)'}
                              </pre>
                            </div>
                            {/* Output */}
                            <div>
                              <div className="flex items-center justify-between px-3 py-1.5 bg-emerald-500/5 border-b border-white/10">
                                <span className="text-[10px] font-medium text-emerald-400 uppercase tracking-wider">Output</span>
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  className="h-5 px-1.5 gap-1 text-[10px] hover:bg-white/10"
                                  onClick={async () => {
                                    await navigator.clipboard.writeText(formData.input_output.outputs[idx] || '');
                                    setCopiedTestCase({ idx, type: 'output' });
                                    setTimeout(() => setCopiedTestCase(null), 2000);
                                  }}
                                >
                                  {copiedTestCase?.idx === idx && copiedTestCase?.type === 'output' ? (
                                    <><Check className="h-2.5 w-2.5 text-emerald-400" /><span className="text-emerald-400">Copied</span></>
                                  ) : (
                                    <><Copy className="h-2.5 w-2.5" />Copy</>
                                  )}
                                </Button>
                              </div>
                              <pre className="p-3 text-xs font-mono overflow-auto max-h-32 whitespace-pre text-emerald-400">
                                {formData.input_output.outputs[idx] || '(없음)'}
                              </pre>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </>
                ) : (
                  <div className="flex flex-col items-center justify-center py-8 text-center">
                    <FlaskConical className="h-8 w-8 text-muted-foreground/30 mb-2" />
                    <p className="text-xs text-muted-foreground">테스트 케이스가 없습니다</p>
                  </div>
                )}
              </div>
            )}
          </motion.div>

          {/* Variants */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="admin-glass-card rounded-2xl p-5"
          >
            <h3 className="text-sm font-semibold mb-4 flex items-center gap-2">
              <Puzzle className="h-4 w-4 text-primary" />
              변형 문제
            </h3>

            <div className="grid grid-cols-3 gap-3">
              {/* Blank */}
              <div className="p-3 rounded-xl bg-white/3 border border-white/5">
                <div className="flex items-center gap-2 mb-2">
                  <div className="flex h-6 w-6 items-center justify-center rounded-md bg-cyan-500/15">
                    <Code2 className="h-3 w-3 text-cyan-400" />
                  </div>
                  <span className="text-xs font-medium">빈칸</span>
                  <span className="ml-auto text-xs text-muted-foreground">{problem.blanks?.length || 0}</span>
                </div>
                {problem.blanks && problem.blanks.length > 0 ? (
                  <div className="space-y-1">
                    {problem.blanks.slice(0, 2).map((blank) => (
                      <div key={blank.id} className="flex items-center justify-between text-xs p-1.5 rounded-lg bg-white/3">
                        <span className="text-muted-foreground">{getLanguageLabel(blank.language)}</span>
                        <Button
                          size="icon"
                          variant="ghost"
                          className="h-5 w-5 text-muted-foreground hover:text-destructive"
                          onClick={() => setDeleteVariant({ type: 'blank', id: blank.id })}
                        >
                          <Trash2 className="h-3 w-3" />
                        </Button>
                      </div>
                    ))}
                    {problem.blanks.length > 2 && (
                      <p className="text-[10px] text-muted-foreground text-center">+{problem.blanks.length - 2} more</p>
                    )}
                  </div>
                ) : null}
                <Link href={`/admin/problems/create?type=blank&originalId=${originalId}`} className="block mt-2">
                  <Button size="sm" variant="outline" className="w-full h-7 text-xs rounded-lg bg-cyan-500/10 border-cyan-500/20 text-cyan-400 hover:bg-cyan-500/20">
                    <Plus className="h-3 w-3 mr-1" />
                    {problem.blanks?.length ? '추가' : '생성'}
                  </Button>
                </Link>
              </div>

              {/* Puzzle */}
              <div className="p-3 rounded-xl bg-white/3 border border-white/5">
                <div className="flex items-center gap-2 mb-2">
                  <div className="flex h-6 w-6 items-center justify-center rounded-md bg-pink-500/15">
                    <Puzzle className="h-3 w-3 text-pink-400" />
                  </div>
                  <span className="text-xs font-medium">퍼즐</span>
                  <span className="ml-auto text-xs text-muted-foreground">{problem.puzzles?.length || 0}</span>
                </div>
                {problem.puzzles && problem.puzzles.length > 0 ? (
                  <div className="space-y-1">
                    {problem.puzzles.slice(0, 2).map((puzzle) => (
                      <div key={puzzle.id} className="flex items-center justify-between text-xs p-1.5 rounded-lg bg-white/3">
                        <span className="text-muted-foreground">{getLanguageLabel(puzzle.language)}</span>
                        <Button
                          size="icon"
                          variant="ghost"
                          className="h-5 w-5 text-muted-foreground hover:text-destructive"
                          onClick={() => setDeleteVariant({ type: 'puzzle', id: puzzle.id })}
                        >
                          <Trash2 className="h-3 w-3" />
                        </Button>
                      </div>
                    ))}
                    {problem.puzzles.length > 2 && (
                      <p className="text-[10px] text-muted-foreground text-center">+{problem.puzzles.length - 2} more</p>
                    )}
                  </div>
                ) : null}
                <Link href={`/admin/problems/create?type=puzzle&originalId=${originalId}`} className="block mt-2">
                  <Button size="sm" variant="outline" className="w-full h-7 text-xs rounded-lg bg-pink-500/10 border-pink-500/20 text-pink-400 hover:bg-pink-500/20">
                    <Plus className="h-3 w-3 mr-1" />
                    {problem.puzzles?.length ? '추가' : '생성'}
                  </Button>
                </Link>
              </div>

              {/* Guided */}
              <div className="p-3 rounded-xl bg-white/3 border border-white/5">
                <div className="flex items-center gap-2 mb-2">
                  <div className="flex h-6 w-6 items-center justify-center rounded-md bg-amber-500/15">
                    <BookOpen className="h-3 w-3 text-amber-400" />
                  </div>
                  <span className="text-xs font-medium">가이드</span>
                  <span className="ml-auto text-xs text-muted-foreground">{problem.guideds?.length || 0}</span>
                </div>
                {problem.guideds && problem.guideds.length > 0 ? (
                  <div className="space-y-1">
                    {problem.guideds.slice(0, 2).map((guided) => (
                      <div key={guided.id} className="flex items-center justify-between text-xs p-1.5 rounded-lg bg-white/3">
                        <span className="text-muted-foreground">{getLanguageLabel(guided.language)}</span>
                        <Button
                          size="icon"
                          variant="ghost"
                          className="h-5 w-5 text-muted-foreground hover:text-destructive"
                          onClick={() => setDeleteVariant({ type: 'guided', id: guided.id })}
                        >
                          <Trash2 className="h-3 w-3" />
                        </Button>
                      </div>
                    ))}
                    {problem.guideds.length > 2 && (
                      <p className="text-[10px] text-muted-foreground text-center">+{problem.guideds.length - 2} more</p>
                    )}
                  </div>
                ) : null}
                <Link href={`/admin/problems/create?type=guided&originalId=${originalId}`} className="block mt-2">
                  <Button size="sm" variant="outline" className="w-full h-7 text-xs rounded-lg bg-amber-500/10 border-amber-500/20 text-amber-400 hover:bg-amber-500/20">
                    <Plus className="h-3 w-3 mr-1" />
                    {problem.guideds?.length ? '추가' : '생성'}
                  </Button>
                </Link>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Right Column - Community */}
        <div className="space-y-4">
          {/* Community Solutions */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="admin-glass-card rounded-2xl p-5"
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-semibold flex items-center gap-2">
                <MessageSquare className="h-4 w-4 text-primary" />
                커뮤니티 풀이
              </h3>
              <div className="flex items-center gap-3">
                {/* Inline Stats */}
                <div className="flex items-center gap-3 text-xs text-muted-foreground">
                  <span className="flex items-center gap-1" title="풀이 수">
                    <Users className="h-3 w-3" />
                    {stats.solve_count}
                  </span>
                  <span className="flex items-center gap-1 text-rose-400" title="좋아요">
                    <Heart className="h-3 w-3" />
                    {stats.like_count}
                  </span>
                  <span className="flex items-center gap-1 text-sky-400" title="커뮤니티 풀이">
                    <MessageSquare className="h-3 w-3" />
                    {solutionsTotal}
                  </span>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-7 px-2 text-xs"
                  onClick={fetchSolutions}
                  disabled={loadingSolutions}
                >
                  <RefreshCw className={`h-3 w-3 mr-1 ${loadingSolutions ? 'animate-spin' : ''}`} />
                  새로고침
                </Button>
              </div>
            </div>

            {loadingSolutions ? (
              <div className="space-y-3">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="p-3 rounded-xl bg-white/3 animate-pulse">
                    <div className="flex items-center gap-2 mb-2">
                      <div className="h-6 w-6 rounded-full bg-white/10" />
                      <div className="h-3 w-20 bg-white/10 rounded" />
                    </div>
                    <div className="h-12 bg-white/5 rounded" />
                  </div>
                ))}
              </div>
            ) : solutions.length > 0 ? (
              <div className="space-y-2 max-h-[600px] overflow-auto pr-1">
                {solutions.map((solution) => {
                  const isExpanded = expandedCommunitySolution === solution.id;
                  const isLoading = loadingCommunitySolution === solution.id;
                  const solutionData = communitySolutionDetails[solution.id];

                  return (
                    <div
                      key={solution.id}
                      className="rounded-xl bg-white/3 border border-white/5 overflow-hidden"
                    >
                      {/* Header - Clickable */}
                      <button
                        onClick={() => handleToggleSolution(solution.id)}
                        className="w-full p-3 hover:bg-white/5 transition-colors text-left"
                      >
                        <div className="flex items-center gap-2 mb-2">
                          {solution.author_avatar ? (
                            <img src={solution.author_avatar} alt="" className="h-6 w-6 rounded-full" />
                          ) : (
                            <div className="h-6 w-6 rounded-full bg-primary/20 flex items-center justify-center">
                              <span className="text-[10px] font-medium text-primary">
                                {solution.author_name?.charAt(0) || '?'}
                              </span>
                            </div>
                          )}
                          <span className="text-xs font-medium truncate">{solution.author_name || '익명'}</span>
                          <span className={`text-[10px] px-1.5 py-0.5 rounded border ${getLanguageColor(solution.language)}`}>
                            {getLanguageLabel(solution.language)}
                          </span>
                          <div className="ml-auto flex items-center gap-2">
                            <Button
                              variant="ghost"
                              size="icon"
                              className="h-6 w-6 text-muted-foreground hover:text-destructive hover:bg-red-500/10"
                              onClick={(e) => {
                                e.stopPropagation();
                                setDeleteSolution({ id: solution.id, title: solution.title });
                              }}
                            >
                              <Trash2 className="h-3 w-3" />
                            </Button>
                            {isExpanded ? (
                              <ChevronUp className="h-4 w-4 text-muted-foreground" />
                            ) : (
                              <ChevronDown className="h-4 w-4 text-muted-foreground" />
                            )}
                          </div>
                        </div>

                        {solution.title && (
                          <p className="text-xs font-medium mb-1 truncate">{solution.title}</p>
                        )}

                        <div className="flex items-center gap-3 text-[10px] text-muted-foreground">
                          <span className="flex items-center gap-1">
                            <ThumbsUp className="h-3 w-3" />
                            {solution.upvotes}
                          </span>
                          <span className="flex items-center gap-1">
                            <ThumbsDown className="h-3 w-3" />
                            {solution.downvotes}
                          </span>
                          <span className="flex items-center gap-1">
                            <MessageSquare className="h-3 w-3" />
                            {solution.comment_count}
                          </span>
                          <span className="ml-auto">
                            {formatDistanceToNow(new Date(solution.created_at), { addSuffix: true, locale: ko })}
                          </span>
                        </div>
                      </button>

                      {/* Expanded Content */}
                      <AnimatePresence>
                        {isExpanded && (
                          <motion.div
                            initial={{ height: 0, opacity: 0 }}
                            animate={{ height: 'auto', opacity: 1 }}
                            exit={{ height: 0, opacity: 0 }}
                            transition={{ duration: 0.2 }}
                            className="border-t border-white/5"
                          >
                            {isLoading ? (
                              <div className="p-4 space-y-3">
                                <div className="h-32 bg-white/5 animate-pulse rounded-lg" />
                                <div className="h-16 bg-white/5 animate-pulse rounded-lg" />
                              </div>
                            ) : solutionData ? (
                              <div className="p-4 space-y-4">
                                {/* Description */}
                                {solutionData.detail.description && (
                                  <p className="text-xs text-muted-foreground">{solutionData.detail.description}</p>
                                )}

                                {/* Stats */}
                                <div className="flex items-center gap-4 text-xs text-muted-foreground">
                                  <span className="flex items-center gap-1">
                                    <Eye className="h-3 w-3" />
                                    {solutionData.detail.view_count} 조회
                                  </span>
                                </div>

                                {/* Code */}
                                <div className="rounded-lg overflow-hidden border border-white/10">
                                  <div className="max-h-[250px] overflow-auto">
                                    <CodeBlock
                                      code={solutionData.detail.code}
                                      language={solutionData.detail.language}
                                      showLineNumbers={true}
                                    />
                                  </div>
                                </div>

                                {/* Comments */}
                                <div>
                                  <h5 className="text-xs font-semibold mb-2 flex items-center gap-1.5 text-muted-foreground">
                                    <MessageSquare className="h-3 w-3" />
                                    댓글 ({solutionData.comments.length})
                                  </h5>

                                  {solutionData.comments.length > 0 ? (
                                    <div className="space-y-2 max-h-[200px] overflow-auto">
                                      {solutionData.comments.map((comment) => (
                                        <div key={comment.id} className="p-2.5 rounded-lg bg-white/3 border border-white/5">
                                          <div className="flex items-center gap-2 mb-1.5">
                                            {comment.author_avatar ? (
                                              <img src={comment.author_avatar} alt="" className="h-5 w-5 rounded-full" />
                                            ) : (
                                              <div className="h-5 w-5 rounded-full bg-primary/20 flex items-center justify-center">
                                                <span className="text-[8px] font-medium text-primary">
                                                  {comment.author_name?.charAt(0) || '?'}
                                                </span>
                                              </div>
                                            )}
                                            <span className="text-[10px] font-medium">{comment.author_name || '익명'}</span>
                                            <span className="text-[10px] text-muted-foreground ml-auto">
                                              {formatDistanceToNow(new Date(comment.created_at), { addSuffix: true, locale: ko })}
                                            </span>
                                            <Button
                                              variant="ghost"
                                              size="icon"
                                              className="h-5 w-5 text-muted-foreground hover:text-destructive hover:bg-red-500/10"
                                              onClick={() => setDeleteComment({ id: comment.id, solutionId: solution.id })}
                                            >
                                              <Trash2 className="h-2.5 w-2.5" />
                                            </Button>
                                          </div>
                                          <p className="text-[11px] text-muted-foreground leading-relaxed">{comment.content}</p>
                                          <div className="flex items-center gap-2 mt-1.5 text-[10px] text-muted-foreground">
                                            <span className="flex items-center gap-0.5">
                                              <ThumbsUp className="h-2.5 w-2.5" />
                                              {comment.upvotes}
                                            </span>
                                            <span className="flex items-center gap-0.5">
                                              <ThumbsDown className="h-2.5 w-2.5" />
                                              {comment.downvotes}
                                            </span>
                                          </div>
                                        </div>
                                      ))}
                                    </div>
                                  ) : (
                                    <p className="text-[10px] text-muted-foreground/60 text-center py-3">댓글이 없습니다</p>
                                  )}
                                </div>
                              </div>
                            ) : null}
                          </motion.div>
                        )}
                      </AnimatePresence>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center py-12 text-center">
                <MessageSquare className="h-10 w-10 text-muted-foreground/30 mb-3" />
                <p className="text-sm text-muted-foreground">아직 커뮤니티 풀이가 없습니다</p>
              </div>
            )}
          </motion.div>
        </div>
      </div>

      {/* Delete Variant Dialog */}
      <AlertDialog open={!!deleteVariant} onOpenChange={() => setDeleteVariant(null)}>
        <AlertDialogContent className="bg-black/90 border-white/10 rounded-2xl max-w-md">
          <AlertDialogHeader>
            <div className="flex items-center justify-center w-12 h-12 rounded-xl bg-red-500/15 mx-auto mb-3">
              <Trash2 className="h-6 w-6 text-red-400" />
            </div>
            <AlertDialogTitle className="text-center">변형 문제 삭제</AlertDialogTitle>
            <AlertDialogDescription className="text-center">
              이 변형 문제를 삭제하시겠습니까?<br />
              <span className="text-red-400/80">이 작업은 되돌릴 수 없습니다.</span>
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter className="flex-col sm:flex-row gap-2 mt-4">
            <AlertDialogCancel className="rounded-xl bg-white/5 border-white/10 hover:bg-white/10">
              취소
            </AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDeleteVariant}
              className="rounded-xl bg-red-500/20 text-red-400 border border-red-500/30 hover:bg-red-500/30"
            >
              <Trash2 className="h-4 w-4 mr-1.5" />
              삭제
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Delete Solution Dialog */}
      <AlertDialog open={!!deleteSolution} onOpenChange={() => setDeleteSolution(null)}>
        <AlertDialogContent className="bg-black/90 border-white/10 rounded-2xl max-w-md">
          <AlertDialogHeader>
            <div className="flex items-center justify-center w-12 h-12 rounded-xl bg-red-500/15 mx-auto mb-3">
              <Trash2 className="h-6 w-6 text-red-400" />
            </div>
            <AlertDialogTitle className="text-center">커뮤니티 풀이 삭제</AlertDialogTitle>
            <AlertDialogDescription className="text-center">
              {deleteSolution?.title ? (
                <span className="font-medium">&quot;{deleteSolution.title}&quot;</span>
              ) : (
                '이 풀이'
              )}
              를 삭제하시겠습니까?<br />
              <span className="text-red-400/80 text-xs">관련 댓글도 함께 삭제됩니다.</span>
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter className="flex-col sm:flex-row gap-2 mt-4">
            <AlertDialogCancel className="rounded-xl bg-white/5 border-white/10 hover:bg-white/10">
              취소
            </AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDeleteSolution}
              className="rounded-xl bg-red-500/20 text-red-400 border border-red-500/30 hover:bg-red-500/30"
            >
              <Trash2 className="h-4 w-4 mr-1.5" />
              삭제
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Delete Comment Dialog */}
      <AlertDialog open={!!deleteComment} onOpenChange={() => setDeleteComment(null)}>
        <AlertDialogContent className="bg-black/90 border-white/10 rounded-2xl max-w-md">
          <AlertDialogHeader>
            <div className="flex items-center justify-center w-12 h-12 rounded-xl bg-red-500/15 mx-auto mb-3">
              <MessageSquare className="h-6 w-6 text-red-400" />
            </div>
            <AlertDialogTitle className="text-center">댓글 삭제</AlertDialogTitle>
            <AlertDialogDescription className="text-center">
              이 댓글을 삭제하시겠습니까?
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter className="flex-col sm:flex-row gap-2 mt-4">
            <AlertDialogCancel className="rounded-xl bg-white/5 border-white/10 hover:bg-white/10">
              취소
            </AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDeleteComment}
              className="rounded-xl bg-red-500/20 text-red-400 border border-red-500/30 hover:bg-red-500/30"
            >
              <Trash2 className="h-4 w-4 mr-1.5" />
              삭제
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
