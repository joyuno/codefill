'use client';

import { useState, useEffect, useCallback } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ArrowLeft, Loader2, Users, UserPlus, Search, MessageCircle, Wifi, WifiOff } from 'lucide-react';
import { friendsApi, type Friend } from '@/lib/api';
import { useWebSocketContext } from '@/contexts/WebSocketContext';
import { FriendList } from './FriendList';
import { FriendRequests } from './FriendRequests';
import { UserSearch } from './UserSearch';
import { Conversation } from './Conversation';
import { cn } from '@/lib/utils';

interface FriendModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

type TabType = 'friends' | 'requests' | 'search';

const tabs: { id: TabType; label: string; icon: React.ReactNode }[] = [
  { id: 'friends', label: '친구', icon: <Users className="h-4 w-4" /> },
  { id: 'requests', label: '요청', icon: <UserPlus className="h-4 w-4" /> },
  { id: 'search', label: '검색', icon: <Search className="h-4 w-4" /> },
];

export function FriendModal({ open, onOpenChange }: FriendModalProps) {
  const [activeTab, setActiveTab] = useState<TabType>('friends');
  const [selectedFriend, setSelectedFriend] = useState<Friend | null>(null);

  // WebSocket 연결 상태
  const { isConnected } = useWebSocketContext();

  // 데이터
  const [friends, setFriends] = useState<Friend[]>([]);
  const [requestCount, setRequestCount] = useState(0);
  const [loading, setLoading] = useState(false);

  // 데이터 로드
  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [friendsRes, countsRes] = await Promise.all([
        friendsApi.listFriends(),
        friendsApi.getUnreadCounts(),
      ]);
      setFriends(friendsRes.friends);
      setRequestCount(countsRes.pending_requests);
    } catch (err) {
      console.error('Failed to fetch friends data:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (open) {
      fetchData();
      setSelectedFriend(null);
    }
  }, [open, fetchData]);

  // 친구 선택
  const handleSelectFriend = (friend: Friend) => {
    setSelectedFriend(friend);
  };

  // 대화에서 뒤로가기
  const handleBackFromConversation = () => {
    setSelectedFriend(null);
    fetchData();
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[480px] h-[70vh] max-h-[650px] flex flex-col p-0 gap-0 overflow-hidden">
        {selectedFriend ? (
          // 대화 화면
          <>
            <DialogHeader className="px-4 py-3 border-b bg-muted/30 shrink-0">
              <div className="flex items-center gap-3">
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-8 w-8 rounded-full hover:bg-background"
                  onClick={handleBackFromConversation}
                >
                  <ArrowLeft className="h-4 w-4" />
                </Button>
                <div className="flex items-center gap-2">
                  <MessageCircle className="h-4 w-4 text-primary" />
                  <DialogTitle className="text-base font-medium">
                    {selectedFriend.name || '익명'}
                  </DialogTitle>
                  {/* 연결 상태 - 닉네임 옆 */}
                  <div className={cn(
                    'flex items-center gap-1 text-xs',
                    isConnected ? 'text-green-500' : 'text-muted-foreground'
                  )}>
                    {isConnected ? (
                      <Wifi className="h-3 w-3" />
                    ) : (
                      <WifiOff className="h-3 w-3" />
                    )}
                  </div>
                </div>
              </div>
            </DialogHeader>
            <div className="flex-1 overflow-hidden">
              <Conversation friend={selectedFriend} />
            </div>
          </>
        ) : (
          // 친구 목록/요청/검색 탭
          <>
            <DialogHeader className="px-5 pt-5 pb-4 shrink-0">
              <DialogTitle className="text-xl font-semibold flex items-center gap-2">
                <Users className="h-5 w-5 text-primary" />
                친구
              </DialogTitle>
            </DialogHeader>

            {/* 커스텀 탭 네비게이션 */}
            <div className="px-4 pb-3 shrink-0">
              <div className="flex gap-1 p-1 bg-muted/50 rounded-lg">
                {tabs.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={cn(
                      'flex-1 flex items-center justify-center gap-1.5 px-3 py-2 rounded-md text-sm font-medium transition-all focus:outline-none',
                      activeTab === tab.id
                        ? 'bg-background text-foreground shadow-sm'
                        : 'text-muted-foreground hover:text-foreground hover:bg-background/50'
                    )}
                  >
                    {tab.icon}
                    <span>{tab.label}</span>
                    {tab.id === 'requests' && requestCount > 0 && (
                      <Badge variant="destructive" className="h-5 min-w-[20px] px-1.5 text-[10px]">
                        {requestCount}
                      </Badge>
                    )}
                    {tab.id === 'friends' && friends.length > 0 && (
                      <span className="text-xs text-muted-foreground">
                        {friends.length}
                      </span>
                    )}
                  </button>
                ))}
              </div>
            </div>

            {/* 컨텐츠 영역 */}
            <div className="flex-1 overflow-auto">
              {loading ? (
                <div className="flex items-center justify-center h-full">
                  <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
                </div>
              ) : (
                <div className="px-4 pb-4">
                  {activeTab === 'friends' && (
                    <FriendList
                      friends={friends}
                      onSelectFriend={handleSelectFriend}
                      onRefresh={fetchData}
                    />
                  )}
                  {activeTab === 'requests' && (
                    <FriendRequests onRefresh={fetchData} />
                  )}
                  {activeTab === 'search' && (
                    <UserSearch onRequestSent={fetchData} />
                  )}
                </div>
              )}
            </div>
          </>
        )}
      </DialogContent>
    </Dialog>
  );
}
