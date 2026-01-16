'use client';

import { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import {
  Search,
  ChevronLeft,
  ChevronRight,
  ChevronsLeft,
  ChevronsRight,
  MoreHorizontal,
  Trash2,
  Edit,
  Eye,
  Code2,
  Puzzle,
  BookOpen,
  Calendar,
  Heart,
  Users,
} from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
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
import { adminApi, type AdminProblem } from '@/lib/api/admin';
import { toast } from 'sonner';
import {
  SilverIcon,
  GoldIcon,
  PlatinumIcon,
  DiamondIcon,
  MasterIcon,
} from '@/components/icons/tiers';

const difficultyConfig: Record<string, { label: string; Icon: React.ComponentType<{ className?: string }>; color: string }> = {
  easy: { label: '실버', Icon: SilverIcon, color: 'text-gray-400' },
  medium: { label: '골드', Icon: GoldIcon, color: 'text-amber-500' },
  medium_hard: { label: '플래티넘', Icon: PlatinumIcon, color: 'text-cyan-400' },
  hard: { label: '다이아', Icon: DiamondIcon, color: 'text-violet-400' },
  very_hard: { label: '마스터', Icon: MasterIcon, color: 'text-rose-400' },
};

const TAG_OPTIONS = [
  { value: 'all', label: '모든 태그' },
  { value: 'Dynamic programming', label: 'DP' },
  { value: 'Graph algorithms', label: 'Graph' },
  { value: 'Binary search', label: 'Binary Search' },
  { value: 'Sorting', label: 'Sorting' },
  { value: 'Math', label: 'Math' },
  { value: 'String', label: 'String' },
  { value: 'Implementation', label: 'Implementation' },
  { value: 'Greedy', label: 'Greedy' },
  { value: 'Tree', label: 'Tree' },
  { value: 'Data structures', label: 'Data Structures' },
];

const SORT_OPTIONS = [
  { value: 'created_at', label: '생성일' },
  { value: 'name', label: '이름' },
  { value: 'difficulty', label: '난이도' },
  { value: 'solve_count', label: '풀이 수' },
  { value: 'like_count', label: '좋아요 수' },
];

export default function AdminProblemsPage() {
  const [problems, setProblems] = useState<AdminProblem[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [sourceFilter, setSourceFilter] = useState<string>('all');
  const [difficultyFilter, setDifficultyFilter] = useState<string>('all');
  const [tagFilter, setTagFilter] = useState<string>('all');
  const [sortBy, setSortBy] = useState<string>('created_at');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [pageInput, setPageInput] = useState('1');
  const limit = 20;

  // Dialog state
  const [deleteTarget, setDeleteTarget] = useState<AdminProblem | null>(null);

  const fetchProblems = useCallback(async () => {
    setLoading(true);
    try {
      const response = await adminApi.listProblems({
        search: search || undefined,
        source: sourceFilter !== 'all' ? sourceFilter : undefined,
        difficulty: difficultyFilter !== 'all' ? difficultyFilter : undefined,
        tags: tagFilter !== 'all' ? tagFilter : undefined,
        sort_by: sortBy,
        sort_order: sortOrder,
        page,
        limit,
      });
      setProblems(response.items);
      setTotal(response.total);
    } catch (error) {
      console.error('Failed to fetch problems:', error);
      toast.error('문제 목록을 불러오는데 실패했습니다');
    } finally {
      setLoading(false);
    }
  }, [search, sourceFilter, difficultyFilter, tagFilter, sortBy, sortOrder, page]);

  useEffect(() => {
    fetchProblems();
  }, [fetchProblems]);

  // Debounce search
  useEffect(() => {
    const timer = setTimeout(() => {
      setPage(1);
    }, 300);
    return () => clearTimeout(timer);
  }, [search]);

  const handleDelete = async () => {
    if (!deleteTarget) return;

    try {
      await adminApi.deleteProblem(deleteTarget.original_id);
      toast.success('문제가 삭제되었습니다');
      fetchProblems();
    } catch (error) {
      console.error('Failed to delete problem:', error);
      toast.error('문제 삭제에 실패했습니다');
    } finally {
      setDeleteTarget(null);
    }
  };

  const totalPages = Math.ceil(total / limit);

  // pageInput과 page 동기화
  useEffect(() => {
    setPageInput(String(page));
  }, [page]);

  // 페이지 입력 후 Enter 시 이동
  const handlePageInputSubmit = () => {
    const val = parseInt(pageInput);
    if (!isNaN(val) && val >= 1 && val <= totalPages) {
      setPage(val);
    } else {
      setPageInput(String(page));
    }
  };

  const getVariantBadges = (problem: AdminProblem) => {
    const badges = [];
    if (problem.has_blank) {
      badges.push(
        <span
          key="blank"
          className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs bg-blue-500/10 text-blue-400 border border-blue-500/20"
        >
          <Code2 className="h-3 w-3" />
          빈칸
        </span>
      );
    }
    if (problem.has_puzzle) {
      badges.push(
        <span
          key="puzzle"
          className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs bg-purple-500/10 text-purple-400 border border-purple-500/20"
        >
          <Puzzle className="h-3 w-3" />
          퍼즐
        </span>
      );
    }
    if (problem.has_guided) {
      badges.push(
        <span
          key="guided"
          className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
        >
          <BookOpen className="h-3 w-3" />
          가이드
        </span>
      );
    }
    return badges;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="admin-section-header">
        <h2 className="text-lg font-semibold">문제 목록</h2>
      </div>

      {/* Filters */}
      <div className="admin-glass-card rounded-2xl p-4">
        <div className="flex flex-wrap gap-4">
          <div className="admin-search flex-1 min-w-[240px] max-w-md">
            <Search className="admin-search-icon h-4 w-4" />
            <input
              type="text"
              placeholder="제목으로 검색..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>

          <Select
            value={sourceFilter}
            onValueChange={(v) => {
              setSourceFilter(v);
              setPage(1);
            }}
          >
            <SelectTrigger className="w-[140px] bg-white/5 border-white/10 rounded-xl">
              <SelectValue placeholder="출처" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">모든 출처</SelectItem>
              <SelectItem value="leetcode">LeetCode</SelectItem>
              <SelectItem value="programmers">프로그래머스</SelectItem>
              <SelectItem value="baekjoon">백준</SelectItem>
              <SelectItem value="custom">직접 생성</SelectItem>
            </SelectContent>
          </Select>

          <Select
            value={difficultyFilter}
            onValueChange={(v) => {
              setDifficultyFilter(v);
              setPage(1);
            }}
          >
            <SelectTrigger className="w-[140px] bg-white/5 border-white/10 rounded-xl">
              <SelectValue placeholder="난이도" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">모든 난이도</SelectItem>
              <SelectItem value="easy">
                <span className="flex items-center gap-1.5">
                  <SilverIcon className="h-4 w-4" />
                  실버
                </span>
              </SelectItem>
              <SelectItem value="medium">
                <span className="flex items-center gap-1.5">
                  <GoldIcon className="h-4 w-4" />
                  골드
                </span>
              </SelectItem>
              <SelectItem value="medium_hard">
                <span className="flex items-center gap-1.5">
                  <PlatinumIcon className="h-4 w-4" />
                  플래티넘
                </span>
              </SelectItem>
              <SelectItem value="hard">
                <span className="flex items-center gap-1.5">
                  <DiamondIcon className="h-4 w-4" />
                  다이아
                </span>
              </SelectItem>
              <SelectItem value="very_hard">
                <span className="flex items-center gap-1.5">
                  <MasterIcon className="h-4 w-4" />
                  마스터
                </span>
              </SelectItem>
            </SelectContent>
          </Select>

          <Select
            value={tagFilter}
            onValueChange={(v) => {
              setTagFilter(v);
              setPage(1);
            }}
          >
            <SelectTrigger className="w-[160px] bg-white/5 border-white/10 rounded-xl">
              <SelectValue placeholder="태그" />
            </SelectTrigger>
            <SelectContent>
              {TAG_OPTIONS.map((opt) => (
                <SelectItem key={opt.value} value={opt.value}>
                  {opt.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <div className="flex items-center gap-2 ml-auto">
            <Select
              value={sortBy}
              onValueChange={(v) => {
                setSortBy(v);
                setPage(1);
              }}
            >
              <SelectTrigger className="w-[120px] bg-white/5 border-white/10 rounded-xl">
                <SelectValue placeholder="정렬" />
              </SelectTrigger>
              <SelectContent>
                {SORT_OPTIONS.map((opt) => (
                  <SelectItem key={opt.value} value={opt.value}>
                    {opt.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <Button
              variant="outline"
              size="sm"
              onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
              className="px-3 bg-white/5 border-white/10 hover:bg-white/10 rounded-xl"
            >
              {sortOrder === 'asc' ? '↑ 오름' : '↓ 내림'}
            </Button>
          </div>
        </div>
      </div>

      {/* Problems List */}
      <div className="space-y-3">
        {loading ? (
          Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="admin-list-item animate-pulse">
              <div className="h-10 w-10 rounded-xl bg-white/5" />
              <div className="flex-1 space-y-2">
                <div className="h-4 w-48 rounded bg-white/5" />
                <div className="h-3 w-32 rounded bg-white/5" />
              </div>
            </div>
          ))
        ) : problems.length === 0 ? (
          <div className="admin-glass-card rounded-2xl p-8 text-center">
            <p className="text-muted-foreground">검색 결과가 없습니다</p>
          </div>
        ) : (
          problems.map((problem, i) => (
            <motion.div
              key={problem.original_id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.03 }}
            >
              <Link href={`/admin/problems/${problem.original_id}`}>
                <div className="admin-list-item group">
                  {/* Tier Icon */}
                  {(() => {
                    const config = difficultyConfig[problem.difficulty];
                    const Icon = config?.Icon || SilverIcon;
                    return (
                      <div className={`shrink-0 ${config?.color || 'text-gray-400'}`} title={config?.label || problem.difficulty}>
                        <Icon className="h-6 w-6" />
                      </div>
                    );
                  })()}

                  {/* Main Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <h3 className="text-sm font-medium text-foreground/90 truncate group-hover:text-primary transition-colors">
                        {problem.name}
                      </h3>
                      {/* Tags */}
                      {problem.tags && problem.tags.length > 0 && (
                        <div className="hidden sm:flex items-center gap-1">
                          {problem.tags.slice(0, 2).map((tag) => (
                            <span
                              key={tag}
                              className="px-1.5 py-0.5 rounded text-[10px] bg-white/5 text-muted-foreground/70 border border-white/10"
                            >
                              {tag}
                            </span>
                          ))}
                          {problem.tags.length > 2 && (
                            <span className="text-[10px] text-muted-foreground/50">
                              +{problem.tags.length - 2}
                            </span>
                          )}
                        </div>
                      )}
                    </div>
                    <div className="flex items-center gap-3 mt-0.5">
                      {problem.source && (
                        <span className="text-[11px] text-muted-foreground/60">
                          {problem.source}
                        </span>
                      )}
                      <span className="flex items-center gap-1 text-[11px] text-muted-foreground/60" title="풀이 수">
                        <Users className="h-3 w-3" />
                        {(problem.solve_count ?? 0).toLocaleString()}
                      </span>
                      <span className="flex items-center gap-1 text-[11px] text-muted-foreground/60" title="좋아요">
                        <Heart className="h-3 w-3" />
                        {(problem.like_count ?? 0).toLocaleString()}
                      </span>
                      {problem.created_at && (
                        <span className="hidden md:flex items-center gap-1 text-[11px] text-muted-foreground/60">
                          <Calendar className="h-3 w-3" />
                          {new Date(problem.created_at).toLocaleDateString()}
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Variant Badges */}
                  <div className="hidden md:flex items-center gap-2 shrink-0">
                    {getVariantBadges(problem)}
                    {!problem.has_blank &&
                      !problem.has_puzzle &&
                      !problem.has_guided && (
                        <span className="text-xs text-muted-foreground/40">
                          변형 없음
                        </span>
                      )}
                  </div>

                  {/* Actions */}
                  <DropdownMenu>
                    <DropdownMenuTrigger
                      asChild
                      onClick={(e) => e.preventDefault()}
                    >
                      <Button
                        variant="ghost"
                        size="icon"
                        className="shrink-0 opacity-0 group-hover:opacity-100 transition-opacity"
                      >
                        <MoreHorizontal className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem asChild>
                        <Link href={`/admin/problems/${problem.original_id}`}>
                          <Eye className="h-4 w-4 mr-2" />
                          상세 보기
                        </Link>
                      </DropdownMenuItem>
                      <DropdownMenuItem asChild>
                        <Link
                          href={`/admin/problems/${problem.original_id}?edit=true`}
                        >
                          <Edit className="h-4 w-4 mr-2" />
                          수정
                        </Link>
                      </DropdownMenuItem>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem
                        onClick={(e) => {
                          e.preventDefault();
                          setDeleteTarget(problem);
                        }}
                        className="text-destructive"
                      >
                        <Trash2 className="h-4 w-4 mr-2" />
                        삭제
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              </Link>
            </motion.div>
          ))
        )}
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between pt-2">
        <span className="text-sm text-muted-foreground/70">
          총 <span className="font-medium text-foreground">{total.toLocaleString()}</span>개
        </span>
        <div className="flex items-center gap-1.5">
          {/* 처음 */}
          <Button
            variant="outline"
            size="icon"
            onClick={() => setPage(1)}
            disabled={page === 1}
            className="h-8 w-8 rounded-xl bg-white/5 border-white/10 hover:bg-white/10"
            title="처음"
          >
            <ChevronsLeft className="h-4 w-4" />
          </Button>
          {/* 이전 */}
          <Button
            variant="outline"
            size="icon"
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
            className="h-8 w-8 rounded-xl bg-white/5 border-white/10 hover:bg-white/10"
            title="이전"
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>

          {/* 페이지 입력 */}
          <div className="flex items-center gap-1.5 px-2">
            <input
              type="number"
              min={1}
              max={totalPages || 1}
              value={pageInput}
              onChange={(e) => setPageInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  handlePageInputSubmit();
                  (e.target as HTMLInputElement).blur();
                }
              }}
              onBlur={handlePageInputSubmit}
              className="w-14 h-8 text-center text-sm rounded-lg bg-white/5 border border-white/10 focus:border-primary/50 focus:outline-none focus:ring-1 focus:ring-primary/20 transition-colors [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
            />
            <span className="text-sm text-muted-foreground">
              / {totalPages || 1}
            </span>
          </div>

          {/* 다음 */}
          <Button
            variant="outline"
            size="icon"
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            disabled={page >= totalPages}
            className="h-8 w-8 rounded-xl bg-white/5 border-white/10 hover:bg-white/10"
            title="다음"
          >
            <ChevronRight className="h-4 w-4" />
          </Button>
          {/* 마지막 */}
          <Button
            variant="outline"
            size="icon"
            onClick={() => setPage(totalPages)}
            disabled={page >= totalPages}
            className="h-8 w-8 rounded-xl bg-white/5 border-white/10 hover:bg-white/10"
            title="마지막"
          >
            <ChevronsRight className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Delete Dialog */}
      <AlertDialog
        open={!!deleteTarget}
        onOpenChange={() => setDeleteTarget(null)}
      >
        <AlertDialogContent className="admin-glass-card border-white/10">
          <AlertDialogHeader>
            <AlertDialogTitle>문제 삭제</AlertDialogTitle>
            <AlertDialogDescription>
              &quot;{deleteTarget?.name}&quot; 문제를 삭제하시겠습니까? 이 작업은
              되돌릴 수 없습니다.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel className="rounded-xl">취소</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDelete}
              className="bg-destructive hover:bg-destructive/90 rounded-xl"
            >
              삭제
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
