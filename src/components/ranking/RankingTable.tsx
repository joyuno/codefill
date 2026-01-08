'use client';

import {
  Table,
  TableBody,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { RankingRow } from './RankingRow';
import { Loader2, Users } from 'lucide-react';
import type { RankingItem, RankingType } from '@/lib/api/ranking';

interface RankingTableProps {
  items: RankingItem[];
  type: RankingType;
  isLoading?: boolean;
  currentUserId?: string;
}

function getValueHeader(type: RankingType) {
  switch (type) {
    case 'xp':
      return '경험치';
    case 'problems':
      return '문제 풀이';
    case 'streak':
      return '최장 스트릭';
    default:
      return '값';
  }
}

export function RankingTable({
  items,
  type,
  isLoading,
  currentUserId,
}: RankingTableProps) {
  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-muted-foreground">
        <Users className="h-12 w-12 mb-4 opacity-50" />
        <p className="text-lg font-medium">랭킹 데이터가 없습니다</p>
        <p className="text-sm">아직 활동한 사용자가 없습니다.</p>
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-border/50 overflow-hidden">
      <Table>
        <TableHeader>
          <TableRow className="bg-muted/30 hover:bg-muted/30">
            <TableHead className="w-16">순위</TableHead>
            <TableHead>사용자</TableHead>
            <TableHead className="text-right w-32">{getValueHeader(type)}</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {items.map((item, index) => (
            <RankingRow
              key={item.user_id}
              item={item}
              index={index}
              type={type}
              isMe={item.user_id === currentUserId}
            />
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
