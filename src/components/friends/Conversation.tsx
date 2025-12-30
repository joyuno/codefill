'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Send, Loader2, Smile } from 'lucide-react';
import { friendsApi, type Friend, type Message } from '@/lib/api';
import { format, isToday, isYesterday } from 'date-fns';
import { ko } from 'date-fns/locale';
import { cn } from '@/lib/utils';
import { useWebSocketContext } from '@/contexts/WebSocketContext';

interface ConversationProps {
  friend: Friend;
}

export function Conversation({ friend }: ConversationProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // WebSocket 컨텍스트
  const {
    isConnected,
    sendMessage: wsSendMessage,
    markAsRead,
    addMessageListener,
    removeMessageListener,
  } = useWebSocketContext();

  // 메시지 로드 및 읽음 처리
  useEffect(() => {
    let isMounted = true;

    const loadAndMarkRead = async () => {
      try {
        // 1. 메시지 로드
        const response = await friendsApi.getConversation(friend.user_id);
        if (isMounted) {
          setMessages(response.messages);
        }

        // 2. 읽음 처리 (REST API - 서버 DB 업데이트)
        await friendsApi.markAsRead(friend.user_id);

        // 3. WebSocket 로컬 카운트 초기화
        markAsRead(friend.user_id);
      } catch (err) {
        console.error('Failed to fetch messages:', err);
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    loadAndMarkRead();
    // 인풋 포커스
    setTimeout(() => inputRef.current?.focus(), 100);

    return () => {
      isMounted = false;
    };
  }, [friend.user_id, markAsRead]);

  // WebSocket 메시지 수신 리스너
  useEffect(() => {
    const handleNewMessage = async (message: Message & { sender_id: string; receiver_id: string }) => {
      if (message.sender_id === friend.user_id || message.receiver_id === friend.user_id) {
        setMessages((prev) => {
          if (prev.some((m) => m.id === message.id)) {
            return prev;
          }
          return [...prev, message as Message];
        });
        // 상대방이 보낸 메시지면 즉시 읽음 처리
        if (message.sender_id === friend.user_id) {
          try {
            await friendsApi.markAsRead(friend.user_id);
            markAsRead(friend.user_id);
          } catch (err) {
            console.error('Failed to mark as read:', err);
          }
        }
      }
    };

    addMessageListener(handleNewMessage);
    return () => removeMessageListener(handleNewMessage);
  }, [friend.user_id, addMessageListener, removeMessageListener, markAsRead]);

  // 스크롤 to bottom (로딩 완료 후에만)
  useEffect(() => {
    if (!loading) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, loading]);

  // 메시지 전송
  const handleSend = async () => {
    const content = inputValue.trim();
    if (!content) return;

    setSending(true);
    setInputValue('');

    try {
      if (isConnected) {
        wsSendMessage(friend.user_id, content);
        setSending(false);
        inputRef.current?.focus();
      } else {
        const newMessage = await friendsApi.sendMessage(friend.user_id, content);
        setMessages((prev) => [...prev, newMessage]);
        setSending(false);
        inputRef.current?.focus();
      }
    } catch (err) {
      console.error('Failed to send message:', err);
      setInputValue(content);
      setSending(false);
    }
  };

  // Enter 키로 전송
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // 날짜 포맷
  const formatMessageDate = (dateStr: string) => {
    const date = new Date(dateStr);
    if (isToday(date)) {
      return format(date, 'a h:mm', { locale: ko });
    }
    if (isYesterday(date)) {
      return `어제 ${format(date, 'a h:mm', { locale: ko })}`;
    }
    return format(date, 'M/d a h:mm', { locale: ko });
  };

  // 메시지 그룹화
  const groupMessages = (msgs: Message[]) => {
    const groups: { senderId: string; messages: Message[]; isMine: boolean }[] = [];

    msgs.forEach((msg) => {
      const lastGroup = groups[groups.length - 1];
      if (lastGroup && lastGroup.senderId === msg.sender_id) {
        lastGroup.messages.push(msg);
      } else {
        groups.push({
          senderId: msg.sender_id,
          messages: [msg],
          isMine: msg.is_mine,
        });
      }
    });

    return groups;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    );
  }

  const messageGroups = groupMessages(messages);

  return (
    <div className="flex flex-col h-full">
      {/* 메시지 영역 */}
      <div className="flex-1 overflow-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="w-16 h-16 rounded-full bg-muted/50 flex items-center justify-center mb-4">
              <Smile className="h-8 w-8 text-muted-foreground/50" />
            </div>
            <p className="text-muted-foreground">
              <span className="font-medium text-foreground">{friend.name || '익명'}</span>님과
            </p>
            <p className="text-muted-foreground">대화를 시작해보세요!</p>
          </div>
        ) : (
          messageGroups.map((group, groupIndex) => (
            <div
              key={groupIndex}
              className={cn(
                'flex gap-2',
                group.isMine ? 'flex-row-reverse' : 'flex-row'
              )}
            >
              {/* 아바타 (상대방만) */}
              {!group.isMine && (
                <Avatar className="h-8 w-8 mt-1 shrink-0">
                  <AvatarImage src={friend.avatar_url || undefined} />
                  <AvatarFallback className="text-xs bg-gradient-to-br from-primary/20 to-primary/10 text-primary">
                    {friend.name?.charAt(0).toUpperCase() || 'U'}
                  </AvatarFallback>
                </Avatar>
              )}

              {/* 메시지 버블들 */}
              <div
                className={cn(
                  'flex flex-col gap-1 max-w-[75%]',
                  group.isMine ? 'items-end' : 'items-start'
                )}
              >
                {group.messages.map((msg, msgIndex) => (
                  <div
                    key={msg.id}
                    className={cn(
                      'flex items-end gap-1.5',
                      group.isMine ? 'flex-row-reverse' : 'flex-row'
                    )}
                  >
                    <div
                      className={cn(
                        'px-3.5 py-2 text-sm whitespace-pre-wrap break-words',
                        group.isMine
                          ? 'bg-primary text-primary-foreground rounded-2xl rounded-br-md'
                          : 'bg-muted rounded-2xl rounded-bl-md'
                      )}
                    >
                      {msg.content}
                    </div>
                    {/* 마지막 메시지에만 시간 표시 */}
                    {msgIndex === group.messages.length - 1 && (
                      <span className="text-[10px] text-muted-foreground/70 shrink-0 pb-0.5">
                        {formatMessageDate(msg.created_at)}
                      </span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* 입력 영역 */}
      <div className="border-t bg-muted/20 p-3">
        <div className="flex gap-2 items-end">
          <div className="flex-1 relative">
            <textarea
              ref={inputRef}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="메시지 입력..."
              className={cn(
                'w-full min-h-[44px] max-h-[120px] px-4 py-3 text-sm',
                'bg-background border rounded-2xl resize-none',
                'focus:outline-none focus:ring-1 focus:ring-primary',
                'placeholder:text-muted-foreground/60'
              )}
              rows={1}
              disabled={sending}
            />
          </div>
          <Button
            size="icon"
            className="h-11 w-11 rounded-full shrink-0"
            onClick={handleSend}
            disabled={!inputValue.trim() || sending}
          >
            {sending ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}
