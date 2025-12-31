'use client';

import { useState } from 'react';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
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
import { MoreHorizontal, UserX, Ban, MessageCircle, Loader2, Users, ExternalLink } from 'lucide-react';
import { friendsApi, type Friend } from '@/lib/api';
import { useWebSocketContext } from '@/contexts/WebSocketContext';
import { cn } from '@/lib/utils';
import Link from 'next/link';

interface FriendListProps {
  friends: Friend[];
  onSelectFriend: (friend: Friend) => void;
  onRefresh: () => void;
}

export function FriendList({ friends, onSelectFriend, onRefresh }: FriendListProps) {
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [showBlockDialog, setShowBlockDialog] = useState(false);
  const [targetFriend, setTargetFriend] = useState<Friend | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);

  // WebSocket 컨텍스트에서 실시간 읽지 않은 메시지 수 가져오기
  const { unreadCounts } = useWebSocketContext();

  // 읽지 않은 메시지 수 계산
  const getUnreadCount = (friend: Friend) => {
    const wsUnread = unreadCounts[friend.user_id] || 0;
    return friend.unread_count + wsUnread;
  };

  const handleDelete = async () => {
    if (!targetFriend) return;
    setIsProcessing(true);
    try {
      await friendsApi.deleteFriendship(targetFriend.friendship_id);
      setShowDeleteDialog(false);
      onRefresh();
    } catch (err) {
      console.error('Failed to delete friendship:', err);
    } finally {
      setIsProcessing(false);
      setTargetFriend(null);
    }
  };

  const handleBlock = async () => {
    if (!targetFriend) return;
    setIsProcessing(true);
    try {
      await friendsApi.blockUser(targetFriend.user_id);
      setShowBlockDialog(false);
      onRefresh();
    } catch (err) {
      console.error('Failed to block user:', err);
    } finally {
      setIsProcessing(false);
      setTargetFriend(null);
    }
  };

  if (friends.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center">
        <div className="w-16 h-16 rounded-full bg-muted/50 flex items-center justify-center mb-4">
          <Users className="h-8 w-8 text-muted-foreground/50" />
        </div>
        <p className="text-muted-foreground font-medium">아직 친구가 없어요</p>
        <p className="text-sm text-muted-foreground/70 mt-1">
          검색 탭에서 친구를 추가해보세요
        </p>
      </div>
    );
  }

  return (
    <>
      <div className="space-y-2">
        {friends.map((friend) => {
          const unreadCount = getUnreadCount(friend);
          return (
            <div
              key={friend.user_id}
              className={cn(
                'group flex items-center gap-3 p-3 rounded-xl transition-all cursor-pointer',
                'hover:bg-muted/50 active:scale-[0.99]',
                unreadCount > 0 && 'bg-primary/5'
              )}
              onClick={() => onSelectFriend(friend)}
            >
              {/* 아바타 */}
              <div className="relative">
                <Avatar className="h-11 w-11 ring-2 ring-background">
                  <AvatarImage src={friend.avatar_url || undefined} />
                  <AvatarFallback className="bg-gradient-to-br from-primary/20 to-primary/10 text-primary font-medium">
                    {friend.name?.charAt(0).toUpperCase() || 'U'}
                  </AvatarFallback>
                </Avatar>
                {unreadCount > 0 && (
                  <div className="absolute -top-1 -right-1">
                    <Badge
                      variant="destructive"
                      className="h-5 min-w-[20px] px-1.5 text-[10px] font-bold animate-pulse"
                    >
                      {unreadCount > 99 ? '99+' : unreadCount}
                    </Badge>
                  </div>
                )}
              </div>

              {/* 정보 */}
              <div className="flex-1 min-w-0">
                <p className="font-medium truncate">
                  {friend.name || '익명'}
                </p>
                <p className="text-xs text-muted-foreground truncate">
                  {friend.last_message ? (
                    <>
                      {friend.last_message_is_mine && <span className="text-muted-foreground/70">나: </span>}
                      {friend.last_message}
                    </>
                  ) : (
                    '메시지를 보내보세요'
                  )}
                </p>
              </div>

              {/* 액션 버튼들 */}
              <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-8 w-8 rounded-full"
                  onClick={(e) => {
                    e.stopPropagation();
                    onSelectFriend(friend);
                  }}
                >
                  <MessageCircle className="h-4 w-4" />
                </Button>

                <DropdownMenu>
                  <DropdownMenuTrigger asChild onClick={(e) => e.stopPropagation()}>
                    <Button variant="ghost" size="icon" className="h-8 w-8 rounded-full">
                      <MoreHorizontal className="h-4 w-4" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end" className="w-40">
                    <DropdownMenuItem asChild>
                      <Link href={`/u/${encodeURIComponent(friend.name || '')}`} className="gap-2">
                        <ExternalLink className="h-4 w-4" />
                        프로필 보기
                      </Link>
                    </DropdownMenuItem>
                    <DropdownMenuItem
                      onSelect={() => {
                        setTargetFriend(friend);
                        setShowDeleteDialog(true);
                      }}
                      className="gap-2"
                    >
                      <UserX className="h-4 w-4" />
                      친구 삭제
                    </DropdownMenuItem>
                    <DropdownMenuItem
                      onSelect={() => {
                        setTargetFriend(friend);
                        setShowBlockDialog(true);
                      }}
                      className="gap-2 text-destructive focus:text-destructive"
                    >
                      <Ban className="h-4 w-4" />
                      차단하기
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
            </div>
          );
        })}
      </div>

      {/* 친구 삭제 확인 */}
      <AlertDialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>친구를 삭제하시겠습니까?</AlertDialogTitle>
            <AlertDialogDescription>
              <span className="font-medium text-foreground">{targetFriend?.name || '이 사용자'}</span>님과의
              친구 관계가 해제됩니다. 대화 내역은 유지됩니다.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={isProcessing}>취소</AlertDialogCancel>
            <AlertDialogAction onClick={handleDelete} disabled={isProcessing}>
              {isProcessing && <Loader2 className="h-4 w-4 animate-spin mr-2" />}
              삭제
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* 차단 확인 */}
      <AlertDialog open={showBlockDialog} onOpenChange={setShowBlockDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>사용자를 차단하시겠습니까?</AlertDialogTitle>
            <AlertDialogDescription>
              <span className="font-medium text-foreground">{targetFriend?.name || '이 사용자'}</span>님을
              차단하면 서로 검색되지 않고 메시지를 주고받을 수 없습니다.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={isProcessing}>취소</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleBlock}
              disabled={isProcessing}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              {isProcessing && <Loader2 className="h-4 w-4 animate-spin mr-2" />}
              차단
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}
