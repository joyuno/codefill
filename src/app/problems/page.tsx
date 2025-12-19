'use client';

import { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Header } from '@/components/layout/Header';
import { TopNav } from '@/components/layout/TopNav';
import { SidebarProfile } from '@/components/dashboard/SidebarProfile';
import {
  ProblemFilters,
  type ProblemFiltersState,
} from '@/components/problems/ProblemFilters';
import { ProblemCard } from '@/components/problems/ProblemCard';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { mockProblems } from '@/lib/mockData';
import { Inbox, RefreshCw } from 'lucide-react';
import type { Problem } from '@/lib/types';

const PROBLEM_TYPE_LABELS: Record<string, string> = {
  blank: '빈칸 채우기',
  puzzle: '퍼즐',
  guided: '1대1 대화형',
  implementation: '구현',
};

export default function ProblemsPage() {
  const [filters, setFilters] = useState<ProblemFiltersState>({
    search: '',
    language: 'all',
    difficulty: 'all',
    type: 'all',
    topic: 'all',
  });

  // Filter problems based on current filters
  const filteredProblems = useMemo(() => {
    return mockProblems.filter((problem) => {
      // Search filter
      if (filters.search) {
        const searchLower = filters.search.toLowerCase();
        const matchesTitle = problem.title.toLowerCase().includes(searchLower);
        const matchesTopics = problem.topics.some((t) =>
          t.toLowerCase().includes(searchLower)
        );
        const matchesDescription = problem.description
          .toLowerCase()
          .includes(searchLower);
        if (!matchesTitle && !matchesTopics && !matchesDescription) {
          return false;
        }
      }

      // Language filter
      if (filters.language !== 'all' && problem.framework !== filters.language) {
        return false;
      }

      // Difficulty filter
      if (filters.difficulty !== 'all' && problem.difficulty !== filters.difficulty) {
        return false;
      }

      // Type filter
      if (filters.type !== 'all' && problem.problemType !== filters.type) {
        return false;
      }

      // Topic filter
      if (
        filters.topic !== 'all' &&
        !problem.topics.includes(filters.topic)
      ) {
        return false;
      }

      return true;
    });
  }, [filters]);

  // Group problems by type for summary
  const problemsByType = useMemo(() => {
    const grouped: Record<string, number> = {};
    filteredProblems.forEach((p) => {
      const type = p.problemType || 'unknown';
      grouped[type] = (grouped[type] || 0) + 1;
    });
    return grouped;
  }, [filteredProblems]);

  return (
    <div className="min-h-screen bg-background">
      <Header />
      <TopNav />
      <div className="flex">
        <aside className="hidden w-72 shrink-0 border-r border-border lg:block">
          <SidebarProfile />
        </aside>
        <main className="flex-1 p-6">
          <div className="mx-auto max-w-4xl space-y-6">
            {/* Page Header */}
            <div className="flex items-start justify-between">
              <div>
                <h1 className="text-2xl font-bold">문제 목록</h1>
                <p className="text-muted-foreground">
                  실전 코딩 문제를 풀고 실력을 키워보세요
                </p>
              </div>
              <div className="flex gap-2">
                {Object.entries(problemsByType).map(([type, count]) => (
                  <Badge
                    key={type}
                    variant="outline"
                    className="cursor-pointer hover:bg-secondary"
                    onClick={() =>
                      setFilters((prev) => ({
                        ...prev,
                        type: prev.type === type ? 'all' : type,
                      }))
                    }
                  >
                    {PROBLEM_TYPE_LABELS[type] || type}: {count}
                  </Badge>
                ))}
              </div>
            </div>

            {/* Filters */}
            <ProblemFilters
              filters={filters}
              onFiltersChange={setFilters}
              resultCount={filteredProblems.length}
            />

            {/* Problem List */}
            <AnimatePresence mode="popLayout">
              {filteredProblems.length > 0 ? (
                <motion.div
                  layout
                  className="space-y-4"
                >
                  {filteredProblems.map((problem, i) => (
                    <motion.div
                      key={problem.id}
                      layout
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, scale: 0.95 }}
                      transition={{ delay: i * 0.05 }}
                    >
                      <ProblemCard problem={problem} index={i} />
                    </motion.div>
                  ))}
                </motion.div>
              ) : (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="flex flex-col items-center justify-center py-16 text-center"
                >
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
                        language: 'all',
                        difficulty: 'all',
                        type: 'all',
                        topic: 'all',
                      })
                    }
                  >
                    <RefreshCw className="mr-2 h-4 w-4" />
                    필터 초기화
                  </Button>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Pagination placeholder */}
            {filteredProblems.length > 0 && (
              <div className="flex justify-center pt-4">
                <p className="text-sm text-muted-foreground">
                  {filteredProblems.length}개의 문제 중 {filteredProblems.length}개
                  표시
                </p>
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}
