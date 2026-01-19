'use client';

import { memo } from 'react';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Search, X, Filter } from 'lucide-react';
import {
  SilverIcon,
  GoldIcon,
  PlatinumIcon,
  DiamondIcon,
  MasterIcon,
} from '@/components/icons/tiers';

export interface ProblemFiltersState {
  search: string;
  difficulty: string;
  source: string;
  tags: string;
}

interface ProblemFiltersProps {
  filters: ProblemFiltersState;
  onFiltersChange: (filters: ProblemFiltersState) => void;
  resultCount: number;
  totalCount: number;
}

// 난이도 옵션 (DB 값 기준)
const DIFFICULTY_OPTIONS = [
  { value: 'all', label: '모든 난이도', Icon: null, color: '' },
  { value: 'easy', label: '실버', Icon: SilverIcon, color: 'text-gray-500' },
  { value: 'medium', label: '골드', Icon: GoldIcon, color: 'text-amber-500' },
  { value: 'medium_hard', label: '플래티넘', Icon: PlatinumIcon, color: 'text-cyan-500' },
  { value: 'hard', label: '다이아', Icon: DiamondIcon, color: 'text-violet-500' },
  { value: 'very_hard', label: '마스터', Icon: MasterIcon, color: 'text-rose-500' },
];

const SOURCE_OPTIONS = [
  { value: 'all', label: '모든 출처' },
  { value: 'baekjoon', label: 'Baekjoon' },
  { value: 'codeforces', label: 'Codeforces' },
  { value: 'leetcode', label: 'LeetCode' },
  { value: 'geeksforgeeks', label: 'GeeksforGeeks' },
  { value: 'hackerrank', label: 'HackerRank' },
];

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
];

export const ProblemFilters = memo(function ProblemFilters({
  filters,
  onFiltersChange,
  resultCount,
  totalCount,
}: ProblemFiltersProps) {
  const updateFilter = (key: keyof ProblemFiltersState, value: string) => {
    onFiltersChange({ ...filters, [key]: value });
  };

  const clearFilters = () => {
    onFiltersChange({
      search: '',
      difficulty: 'all',
      source: 'all',
      tags: 'all',
    });
  };

  const hasActiveFilters =
    filters.search ||
    filters.difficulty !== 'all' ||
    filters.source !== 'all' ||
    filters.tags !== 'all';

  const activeFilterCount = [
    filters.difficulty !== 'all',
    filters.source !== 'all',
    filters.tags !== 'all',
  ].filter(Boolean).length;

  // 현재 선택된 난이도 옵션 찾기
  const selectedTier = DIFFICULTY_OPTIONS.find(opt => opt.value === filters.difficulty);

  return (
    <div className="space-y-3">
      {/* Search Bar */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          value={filters.search}
          onChange={(e) => updateFilter('search', e.target.value)}
          placeholder="문제 이름으로 검색..."
          className="bg-card pl-10 pr-10"
        />
        {filters.search && (
          <button
            onClick={() => updateFilter('search', '')}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </div>

      {/* Filters Row */}
      <div className="flex flex-wrap items-center gap-3 rounded-xl border border-border bg-card p-3">
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Filter className="h-4 w-4" />
          <span>필터</span>
        </div>

        <Select
          value={filters.difficulty}
          onValueChange={(v) => updateFilter('difficulty', v)}
        >
          <SelectTrigger className="w-[140px] bg-secondary h-9">
            <SelectValue>
              {selectedTier && (
                <div className="flex items-center gap-1.5">
                  {selectedTier.Icon && <selectedTier.Icon size={14} />}
                  <span className={selectedTier.color}>{selectedTier.label}</span>
                </div>
              )}
            </SelectValue>
          </SelectTrigger>
          <SelectContent>
            {DIFFICULTY_OPTIONS.map((opt) => (
              <SelectItem key={opt.value} value={opt.value}>
                <div className="flex items-center gap-1.5">
                  {opt.Icon && <opt.Icon size={14} />}
                  <span className={opt.color}>{opt.label}</span>
                </div>
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Select
          value={filters.source}
          onValueChange={(v) => updateFilter('source', v)}
        >
          <SelectTrigger className="w-[140px] bg-secondary h-9">
            <SelectValue placeholder="출처" />
          </SelectTrigger>
          <SelectContent>
            {SOURCE_OPTIONS.map((opt) => (
              <SelectItem key={opt.value} value={opt.value}>
                {opt.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Select
          value={filters.tags}
          onValueChange={(v) => updateFilter('tags', v)}
        >
          <SelectTrigger className="w-[140px] bg-secondary h-9">
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

        {hasActiveFilters && (
          <Button
            variant="ghost"
            size="sm"
            onClick={clearFilters}
            className="h-9 text-muted-foreground"
          >
            <X className="h-3 w-3 mr-1" />
            초기화
          </Button>
        )}

        <div className="ml-auto flex items-center gap-2">
          {activeFilterCount > 0 && (
            <Badge variant="secondary">{activeFilterCount}개 필터 적용</Badge>
          )}
          <span className="text-sm text-muted-foreground">
            {resultCount.toLocaleString()} / {totalCount.toLocaleString()}개
          </span>
        </div>
      </div>
    </div>
  );
});
