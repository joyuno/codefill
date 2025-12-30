'use client';

import { useState, useEffect } from 'react';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import { Check, X, Loader2, Inbox, Send } from 'lucide-react';
import { friendsApi, type FriendRequest, type SentRequest } from '@/lib/api';
import { formatDistanceToNow } from 'date-fns';
import { ko } from 'date-fns/locale';
import { cn } from '@/lib/utils';

interface FriendRequestsProps {
  onRefresh: () => void;
}

type TabType = 'received' | 'sent';

export function FriendRequests({ onRefresh }: FriendRequestsProps) {
  const [activeTab, setActiveTab] = useState<TabType>('received');
  const [receivedRequests, setReceivedRequests] = useState<FriendRequest[]>([]);
  const [sentRequests, setSentRequests] = useState<SentRequest[]>([]);
  const [loading, setLoading] = useState(false);
  const [processingId, setProcessingId] = useState<string | null>(null);

  const fetchRequests = async () => {
    setLoading(true);
    try {
      const [received, sent] = await Promise.all([
        friendsApi.listRequests(),
        friendsApi.listSentRequests(),
      ]);
      setReceivedRequests(received.requests);
      setSentRequests(sent.requests);
    } catch (err) {
      console.error('Failed to fetch requests:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRequests();
  }, []);

  const handleAccept = async (friendshipId: string) => {
    setProcessingId(friendshipId);
    try {
      await friendsApi.acceptRequest(friendshipId);
      await fetchRequests();
      onRefresh();
    } catch (err) {
      console.error('Failed to accept request:', err);
    } finally {
      setProcessingId(null);
    }
  };

  const handleReject = async (friendshipId: string) => {
    setProcessingId(friendshipId);
    try {
      await friendsApi.deleteFriendship(friendshipId);
      await fetchRequests();
      onRefresh();
    } catch (err) {
      console.error('Failed to reject request:', err);
    } finally {
      setProcessingId(null);
    }
  };

  const handleCancel = async (friendshipId: string) => {
    setProcessingId(friendshipId);
    try {
      await friendsApi.deleteFriendship(friendshipId);
      await fetchRequests();
    } catch (err) {
      console.error('Failed to cancel request:', err);
    } finally {
      setProcessingId(null);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-16">
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* 미니 탭 */}
      <div className="flex gap-1 p-0.5 bg-muted/30 rounded-lg w-fit">
        <button
          onClick={() => setActiveTab('received')}
          className={cn(
            'flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition-all',
            activeTab === 'received'
              ? 'bg-background text-foreground shadow-sm'
              : 'text-muted-foreground hover:text-foreground'
          )}
        >
          <Inbox className="h-3.5 w-3.5" />
          받은 요청
          {receivedRequests.length > 0 && (
            <span className="ml-0.5 text-xs bg-primary text-primary-foreground px-1.5 py-0.5 rounded-full">
              {receivedRequests.length}
            </span>
          )}
        </button>
        <button
          onClick={() => setActiveTab('sent')}
          className={cn(
            'flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition-all',
            activeTab === 'sent'
              ? 'bg-background text-foreground shadow-sm'
              : 'text-muted-foreground hover:text-foreground'
          )}
        >
          <Send className="h-3.5 w-3.5" />
          보낸 요청
          {sentRequests.length > 0 && (
            <span className="ml-0.5 text-xs text-muted-foreground">
              {sentRequests.length}
            </span>
          )}
        </button>
      </div>

      {/* 받은 요청 */}
      {activeTab === 'received' && (
        <>
          {receivedRequests.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <div className="w-14 h-14 rounded-full bg-muted/50 flex items-center justify-center mb-3">
                <Inbox className="h-7 w-7 text-muted-foreground/50" />
              </div>
              <p className="text-muted-foreground">받은 요청이 없어요</p>
            </div>
          ) : (
            <div className="space-y-2">
              {receivedRequests.map((request) => (
                <div
                  key={request.id}
                  className="flex items-center gap-3 p-3 rounded-xl bg-muted/30"
                >
                  <Avatar className="h-10 w-10">
                    <AvatarImage src={request.requester_avatar || undefined} />
                    <AvatarFallback className="bg-gradient-to-br from-primary/20 to-primary/10 text-primary text-sm font-medium">
                      {request.requester_name?.charAt(0).toUpperCase() || 'U'}
                    </AvatarFallback>
                  </Avatar>

                  <div className="flex-1 min-w-0">
                    <p className="font-medium truncate">{request.requester_name || '익명'}</p>
                    <p className="text-xs text-muted-foreground">
                      {formatDistanceToNow(new Date(request.created_at), {
                        addSuffix: true,
                        locale: ko,
                      })}
                    </p>
                  </div>

                  <div className="flex items-center gap-1.5">
                    <Button
                      size="sm"
                      className="h-8 gap-1 rounded-lg"
                      onClick={() => handleAccept(request.id)}
                      disabled={processingId === request.id}
                    >
                      {processingId === request.id ? (
                        <Loader2 className="h-3.5 w-3.5 animate-spin" />
                      ) : (
                        <Check className="h-3.5 w-3.5" />
                      )}
                      수락
                    </Button>
                    <Button
                      variant="outline"
                      size="icon"
                      className="h-8 w-8 rounded-lg"
                      onClick={() => handleReject(request.id)}
                      disabled={processingId === request.id}
                    >
                      <X className="h-3.5 w-3.5" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {/* 보낸 요청 */}
      {activeTab === 'sent' && (
        <>
          {sentRequests.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <div className="w-14 h-14 rounded-full bg-muted/50 flex items-center justify-center mb-3">
                <Send className="h-7 w-7 text-muted-foreground/50" />
              </div>
              <p className="text-muted-foreground">보낸 요청이 없어요</p>
            </div>
          ) : (
            <div className="space-y-2">
              {sentRequests.map((request) => (
                <div
                  key={request.id}
                  className="flex items-center gap-3 p-3 rounded-xl bg-muted/30"
                >
                  <Avatar className="h-10 w-10">
                    <AvatarImage src={request.addressee_avatar || undefined} />
                    <AvatarFallback className="bg-gradient-to-br from-primary/20 to-primary/10 text-primary text-sm font-medium">
                      {request.addressee_name?.charAt(0).toUpperCase() || 'U'}
                    </AvatarFallback>
                  </Avatar>

                  <div className="flex-1 min-w-0">
                    <p className="font-medium truncate">{request.addressee_name || '익명'}</p>
                    <p className="text-xs text-muted-foreground">
                      {formatDistanceToNow(new Date(request.created_at), {
                        addSuffix: true,
                        locale: ko,
                      })}
                      에 요청
                    </p>
                  </div>

                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-8 text-muted-foreground hover:text-destructive"
                    onClick={() => handleCancel(request.id)}
                    disabled={processingId === request.id}
                  >
                    {processingId === request.id ? (
                      <Loader2 className="h-3.5 w-3.5 animate-spin" />
                    ) : (
                      '취소'
                    )}
                  </Button>
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}
