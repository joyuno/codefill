'use client';

import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Globe, Calendar, CalendarDays } from 'lucide-react';
import type { RankingPeriod } from '@/lib/api/ranking';

interface RankingTabsProps {
  value: RankingPeriod;
  onChange: (value: RankingPeriod) => void;
}

export function RankingTabs({ value, onChange }: RankingTabsProps) {
  return (
    <Tabs value={value} onValueChange={(v) => onChange(v as RankingPeriod)}>
      <TabsList className="grid grid-cols-3 w-full max-w-md">
        <TabsTrigger value="global" className="flex items-center gap-2">
          <Globe className="h-4 w-4" />
          <span className="hidden sm:inline">전체</span>
        </TabsTrigger>
        <TabsTrigger value="weekly" className="flex items-center gap-2">
          <Calendar className="h-4 w-4" />
          <span className="hidden sm:inline">주간</span>
        </TabsTrigger>
        <TabsTrigger value="monthly" className="flex items-center gap-2">
          <CalendarDays className="h-4 w-4" />
          <span className="hidden sm:inline">월간</span>
        </TabsTrigger>
      </TabsList>
    </Tabs>
  );
}
