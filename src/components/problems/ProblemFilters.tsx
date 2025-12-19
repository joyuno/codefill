'use client';

import { motion } from 'framer-motion';
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
import type { Framework, Difficulty, ProblemType } from '@/lib/types';

export interface ProblemFiltersState {
  search: string;
  language: string;
  difficulty: string;
  type: string;
  topic: string;
}

interface ProblemFiltersProps {
  filters: ProblemFiltersState;
  onFiltersChange: (filters: ProblemFiltersState) => void;
  resultCount: number;
}

const LANGUAGE_OPTIONS = [
  { value: 'all', label: '모든 언어' },
  { value: 'python', label: 'Python' },
  { value: 'javascript', label: 'JavaScript' },
  { value: 'java', label: 'Java' },
  { value: 'cpp', label: 'C++' },
];

const DIFFICULTY_OPTIONS = [
  { value: 'all', label: '모든 난이도' },
  { value: 'easy', label: 'Easy', color: 'text-green-500' },
  { value: 'medium', label: 'Medium', color: 'text-yellow-500' },
  { value: 'hard', label: 'Hard', color: 'text-red-500' },
];

const TYPE_OPTIONS = [
  { value: 'all', label: '모든 유형' },
  { value: 'blank', label: '빈칸 채우기' },
  { value: 'puzzle', label: '퍼즐' },
  { value: 'guided', label: '1대1 대화형' },
  { value: 'implementation', label: '구현' },
];

const TOPIC_OPTIONS = [
  { value: 'all', label: '모든 토픽' },
  { value: 'array', label: '배열' },
  { value: 'hash-map', label: '해시맵' },
  { value: 'binary-search', label: '이진탐색' },
  { value: 'dp', label: 'DP' },
  { value: 'sorting', label: '정렬' },
  { value: 'linked-list', label: '연결리스트' },
  { value: 'stack', label: '스택' },
  { value: 'string', label: '문자열' },
];

export function ProblemFilters({
  filters,
  onFiltersChange,
  resultCount,
}: ProblemFiltersProps) {
  const updateFilter = (key: keyof ProblemFiltersState, value: string) => {
    onFiltersChange({ ...filters, [key]: value });
  };

  const clearFilters = () => {
    onFiltersChange({
      search: '',
      language: 'all',
      difficulty: 'all',
      type: 'all',
      topic: 'all',
    });
  };

  const hasActiveFilters =
    filters.search ||
    filters.language !== 'all' ||
    filters.difficulty !== 'all' ||
    filters.type !== 'all' ||
    filters.topic !== 'all';

  const activeFilterCount = [
    filters.language !== 'all',
    filters.difficulty !== 'all',
    filters.type !== 'all',
    filters.topic !== 'all',
  ].filter(Boolean).length;

  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-3"
    >
      {/* Search Bar */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          value={filters.search}
          onChange={(e) => updateFilter('search', e.target.value)}
          placeholder="문제 제목, 토픽으로 검색..."
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
          value={filters.language}
          onValueChange={(v) => updateFilter('language', v)}
        >
          <SelectTrigger className="w-[130px] bg-secondary h-9">
            <SelectValue placeholder="언어" />
          </SelectTrigger>
          <SelectContent>
            {LANGUAGE_OPTIONS.map((opt) => (
              <SelectItem key={opt.value} value={opt.value}>
                {opt.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Select
          value={filters.difficulty}
          onValueChange={(v) => updateFilter('difficulty', v)}
        >
          <SelectTrigger className="w-[130px] bg-secondary h-9">
            <SelectValue placeholder="난이도" />
          </SelectTrigger>
          <SelectContent>
            {DIFFICULTY_OPTIONS.map((opt) => (
              <SelectItem key={opt.value} value={opt.value}>
                <span className={opt.color}>{opt.label}</span>
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Select
          value={filters.type}
          onValueChange={(v) => updateFilter('type', v)}
        >
          <SelectTrigger className="w-[140px] bg-secondary h-9">
            <SelectValue placeholder="유형" />
          </SelectTrigger>
          <SelectContent>
            {TYPE_OPTIONS.map((opt) => (
              <SelectItem key={opt.value} value={opt.value}>
                {opt.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Select
          value={filters.topic}
          onValueChange={(v) => updateFilter('topic', v)}
        >
          <SelectTrigger className="w-[130px] bg-secondary h-9">
            <SelectValue placeholder="토픽" />
          </SelectTrigger>
          <SelectContent>
            {TOPIC_OPTIONS.map((opt) => (
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
            {resultCount}개의 문제
          </span>
        </div>
      </div>
    </motion.div>
  );
}
