'use client';

import { useState, useEffect, useCallback } from 'react';
import { Header } from '@/components/layout/Header';
import { TopNav } from '@/components/layout/TopNav';
import { SidebarProfile } from '@/components/dashboard/SidebarProfile';
import {
  ProblemFilters,
  type ProblemFiltersState,
} from '@/components/problems/ProblemFilters';
import { ProblemRow } from '@/components/problems/ProblemRow';
import { PreviewModal } from '@/components/problems/PreviewModal';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { problemsApi, type BaseProblemListItem } from '@/lib/api';
import { Inbox, RefreshCw, Loader2, ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight } from 'lucide-react';

export default function ProblemsPage() {
  const [filters, setFilters] = useState<ProblemFiltersState>({
    search: '',
    difficulty: 'all',
    source: 'all',
    tags: 'all',
  });

  const [problems, setProblems] = useState<BaseProblemListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [pageInput, setPageInput] = useState('1'); // 입력용 상태
  const [total, setTotal] = useState(0);
  const [hasMore, setHasMore] = useState(false);
  const limit = 20;

  // Preview modal state
  const [previewId, setPreviewId] = useState<string | null>(null);

  // Debounced search
  const [debouncedSearch, setDebouncedSearch] = useState('');

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(filters.search);
      setPage(1); // Reset page on search
    }, 300);
    return () => clearTimeout(timer);
  }, [filters.search]);

  // Reset page on filter change
  useEffect(() => {
    setPage(1);
  }, [filters.difficulty, filters.source, filters.tags]);

  // Fetch problems
  const fetchProblems = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await problemsApi.listBase({
        difficulty: filters.difficulty !== 'all' ? filters.difficulty : undefined,
        source: filters.source !== 'all' ? filters.source : undefined,
        tags: filters.tags !== 'all' ? filters.tags : undefined,
        search: debouncedSearch || undefined,
        page,
        limit,
      });

      setProblems(response.items);
      setTotal(response.total);
      setHasMore(response.has_more);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load problems');
    } finally {
      setLoading(false);
    }
  }, [filters.difficulty, filters.source, filters.tags, debouncedSearch, page]);

  useEffect(() => {
    fetchProblems();
  }, [fetchProblems]);

  // page 변경 시 input 동기화
  useEffect(() => {
    setPageInput(String(page));
  }, [page]);

  const handlePreview = (originalId: string) => {
    setPreviewId(originalId);
  };

  const totalPages = Math.ceil(total / limit);

  // 페이지 입력 후 Enter 시 이동
  const handlePageInputSubmit = () => {
    const val = parseInt(pageInput);
    if (!isNaN(val) && val >= 1 && val <= totalPages) {
      setPage(val);
    } else {
      // 유효하지 않으면 현재 페이지로 복원
      setPageInput(String(page));
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Header />
      <TopNav />
      <div className="flex">
        <aside className="hidden w-72 shrink-0 border-r border-border lg:block">
          <SidebarProfile />
        </aside>
        <main className="flex-1 p-6">
          <div className="mx-auto max-w-5xl space-y-6">
            {/* Page Header */}
            <div className="flex items-start justify-between">
              <div>
                <h1 className="text-2xl font-bold">문제 목록</h1>
                <p className="text-muted-foreground">
                  실전 코딩 문제를 풀고 실력을 키워보세요
                </p>
              </div>
            </div>

            {/* Filters */}
            <ProblemFilters
              filters={filters}
              onFiltersChange={setFilters}
              resultCount={problems.length}
              totalCount={total}
            />

            {/* Error State */}
            {error && !loading && (
              <div className="flex flex-col items-center justify-center py-16 text-center">
                <p className="text-destructive mb-4">{error}</p>
                <Button variant="outline" onClick={fetchProblems}>
                  <RefreshCw className="mr-2 h-4 w-4" />
                  다시 시도
                </Button>
              </div>
            )}

            {/* Problem List - 로딩 중에도 영역 유지 */}
            {!error && (
              <div className="relative">
                {/* 로딩 오버레이 */}
                {loading && (
                  <div className="absolute inset-0 z-10 flex items-center justify-center bg-background/80 backdrop-blur-sm rounded-lg">
                    <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
                  </div>
                )}

                {problems.length > 0 ? (
                  <div className={`rounded-lg border border-border overflow-hidden ${loading ? 'opacity-50' : ''}`}>
                    <table className="w-full">
                      <thead className="bg-muted/50">
                        <tr className="text-left text-xs text-muted-foreground uppercase tracking-wider">
                          <th className="w-10 py-3 pl-4 pr-2"></th>
                          <th className="py-3 px-2">제목</th>
                          <th className="w-24 py-3 px-2">난이도</th>
                          <th className="w-20 py-3 px-2">출처</th>
                          <th className="py-3 px-2 hidden lg:table-cell">태그</th>
                          <th className="w-24 py-3 px-2 pr-4"></th>
                        </tr>
                      </thead>
                      <tbody>
                        {problems.map((problem, i) => (
                          <ProblemRow
                            key={problem.id}
                            problem={problem}
                            index={i}
                            onPreview={handlePreview}
                          />
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div className="flex flex-col items-center justify-center py-16 text-center">
                    <div className="rounded-full bg-secondary p-4 mb-4">
                      <Inbox className="h-8 w-8 text-muted-foreground" />
                    </div>
                    <h3 className="text-lg font-medium">검색 결과가 없습니다</h3>
                    <p className="text-sm text-muted-foreground mt-1">
                      다른 필터를 선택하거나 검색어를 변경해보세요
                    </p>
                    <Button
                      variant="outline"
                      className="mt-4"
                      onClick={() =>
                        setFilters({
                          search: '',
                          difficulty: 'all',
                          source: 'all',
                          tags: 'all',
                        })
                      }
                    >
                      <RefreshCw className="mr-2 h-4 w-4" />
                      필터 초기화
                    </Button>
                  </div>
                )}
              </div>
            )}

            {/* Pagination */}
            {!error && problems.length > 0 && (
              <div className="flex items-center justify-center gap-2 pt-4">
                {/* 처음 */}
                <Button
                  variant="outline"
                  size="icon"
                  className="h-8 w-8"
                  onClick={() => setPage(1)}
                  disabled={page === 1}
                  title="처음"
                >
                  <ChevronsLeft className="h-4 w-4" />
                </Button>
                {/* 이전 */}
                <Button
                  variant="outline"
                  size="icon"
                  className="h-8 w-8"
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page === 1}
                  title="이전"
                >
                  <ChevronLeft className="h-4 w-4" />
                </Button>

                {/* 페이지 입력 */}
                <div className="flex items-center gap-2">
                  <Input
                    type="number"
                    min={1}
                    max={totalPages}
                    value={pageInput}
                    onChange={(e) => setPageInput(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        handlePageInputSubmit();
                        (e.target as HTMLInputElement).blur();
                      }
                    }}
                    onBlur={handlePageInputSubmit}
                    className="w-16 h-8 text-center text-sm border-2 border-muted-foreground/50 focus:border-primary focus:ring-0 focus-visible:ring-0 [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
                  />
                  <span className="text-sm text-muted-foreground">
                    / {totalPages}
                  </span>
                </div>

                {/* 다음 */}
                <Button
                  variant="outline"
                  size="icon"
                  className="h-8 w-8"
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  disabled={page >= totalPages}
                  title="다음"
                >
                  <ChevronRight className="h-4 w-4" />
                </Button>
                {/* 마지막 */}
                <Button
                  variant="outline"
                  size="icon"
                  className="h-8 w-8"
                  onClick={() => setPage(totalPages)}
                  disabled={page >= totalPages}
                  title="마지막"
                >
                  <ChevronsRight className="h-4 w-4" />
                </Button>
              </div>
            )}
          </div>
        </main>
      </div>

      {/* Preview Modal */}
      <PreviewModal
        originalId={previewId}
        onClose={() => setPreviewId(null)}
      />
    </div>
  );
}
