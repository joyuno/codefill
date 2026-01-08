'use client';

import { motion } from 'framer-motion';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Crown, Medal, Award, User } from 'lucide-react';
import { cn } from '@/lib/utils';
import Link from 'next/link';
import type { RankingItem, RankingType } from '@/lib/api/ranking';

interface RankingRowProps {
  item: RankingItem;
  index: number;
  type: RankingType;
  isMe?: boolean;
}

function getRankIcon(rank: number) {
  switch (rank) {
    case 1:
      return <Crown className="h-5 w-5 text-yellow-500" />;
    case 2:
      return <Medal className="h-5 w-5 text-gray-400" />;
    case 3:
      return <Award className="h-5 w-5 text-amber-600" />;
    default:
      return null;
  }
}

function getRankBgClass(rank: number) {
  switch (rank) {
    case 1:
      return 'bg-yellow-500/10 border-yellow-500/30';
    case 2:
      return 'bg-gray-400/10 border-gray-400/30';
    case 3:
      return 'bg-amber-600/10 border-amber-600/30';
    default:
      return 'border-border/50';
  }
}

function getValueLabel(value: number, type: RankingType) {
  switch (type) {
    case 'xp':
      return `${value.toLocaleString()} XP`;
    case 'problems':
      return `${value.toLocaleString()}`;
    case 'streak':
      return `${value}`;
    default:
      return value.toLocaleString();
  }
}

function getValueUnit(type: RankingType) {
  switch (type) {
    case 'problems':
      return '문제';
    case 'streak':
      return '일';
    default:
      return '';
  }
}

export function RankingRow({ item, index, type, isMe }: RankingRowProps) {
  const rankIcon = getRankIcon(item.rank);
  const bgClass = getRankBgClass(item.rank);

  return (
    <motion.tr
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.03 }}
      className={cn(
        'group border-b transition-colors',
        bgClass,
        isMe && 'bg-primary/10 border-primary/30',
        !isMe && 'hover:bg-muted/50'
      )}
    >
      {/* 순위 */}
      <td className="w-16 py-3 pl-4 pr-2">
        <div className="flex items-center gap-2">
          {rankIcon || (
            <span className={cn(
              'text-sm font-medium text-muted-foreground',
              item.rank <= 10 && 'text-foreground font-bold'
            )}>
              {item.rank}
            </span>
          )}
        </div>
      </td>

      {/* 사용자 정보 */}
      <td className="py-3 px-2">
        <Link
          href={item.username ? `/u/${encodeURIComponent(item.username)}` : '#'}
          className={cn(
            'flex items-center gap-3 transition-opacity',
            item.username ? 'hover:opacity-80' : 'cursor-default'
          )}
          onClick={(e) => !item.username && e.preventDefault()}
        >
          <Avatar className="h-8 w-8">
            <AvatarImage src={item.profile_image || undefined} />
            <AvatarFallback>
              <User className="h-4 w-4" />
            </AvatarFallback>
          </Avatar>
          <div className="min-w-0">
            <p className={cn(
              'text-sm font-medium truncate',
              isMe && 'text-primary'
            )}>
              {item.username || '익명'}
              {isMe && <span className="ml-2 text-xs text-primary">(나)</span>}
            </p>
            <p className="text-xs text-muted-foreground">
              Lv.{item.level}
            </p>
          </div>
        </Link>
      </td>

      {/* 값 */}
      <td className="py-3 px-4 text-right">
        <div className="flex items-center justify-end gap-1">
          <span className={cn(
            'text-sm font-bold',
            item.rank <= 3 ? 'text-foreground' : 'text-muted-foreground'
          )}>
            {getValueLabel(item.value, type)}
          </span>
          <span className="text-xs text-muted-foreground">
            {getValueUnit(type)}
          </span>
        </div>
      </td>
    </motion.tr>
  );
}
