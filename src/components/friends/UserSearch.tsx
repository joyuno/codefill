'use client';

import { useState, useCallback, useEffect, useRef } from 'react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Search, UserPlus, Loader2, Check, Clock, SearchX, ExternalLink } from 'lucide-react';
import { friendsApi, type UserSearchResult } from '@/lib/api';
import { cn } from '@/lib/utils';
import Link from 'next/link';

interface UserSearchProps {
  onRequestSent: () => void;
}

export function UserSearch({ onRequestSent }: UserSearchProps) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<UserSearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [sendingTo, setSendingTo] = useState<string | null>(null);
  const [hasSearched, setHasSearched] = useState(false);
  const debounceRef = useRef<NodeJS.Timeout | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // 마운트 시 인풋 포커스
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const searchUsers = useCallback(async (searchQuery: string) => {
    if (searchQuery.length < 2) {
      setResults([]);
      setHasSearched(false);
      return;
    }

    setLoading(true);
    setHasSearched(true);
    try {
      const response = await friendsApi.searchUsers(searchQuery);
      setResults(response.users);
    } catch (err) {
      console.error('Failed to search users:', err);
      setResults([]);
    } finally {
      setLoading(false);
    }
  }, []);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setQuery(value);

    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }
    debounceRef.current = setTimeout(() => {
      searchUsers(value);
    }, 300);
  };

  useEffect(() => {
    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }
    };
  }, []);

  const handleSendRequest = async (userId: string) => {
    setSendingTo(userId);
    try {
      const response = await friendsApi.sendRequest(userId);
      setResults((prev) =>
        prev.map((user) =>
          user.id === userId
            ? { ...user, friendship_status: response.status as 'pending' | 'accepted' }
            : user
        )
      );
      onRequestSent();
    } catch (err) {
      console.error('Failed to send friend request:', err);
    } finally {
      setSendingTo(null);
    }
  };

  return (
    <div className="space-y-4">
      {/* 검색 입력 */}
      <div className="relative pt-1">
        <Search className="absolute left-3 top-1/2 translate-y-[-40%] h-4 w-4 text-muted-foreground" />
        <Input
          ref={inputRef}
          value={query}
          onChange={handleInputChange}
          placeholder="이름으로 검색..."
          className="pl-9 h-11 rounded-xl bg-muted/50 border-0 focus-visible:ring-1 focus-visible:ring-offset-0"
        />
        {query && (
          <button
            onClick={() => {
              setQuery('');
              setResults([]);
              setHasSearched(false);
            }}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
          >
            <span className="text-xs">지우기</span>
          </button>
        )}
      </div>

      {/* 검색 결과 */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
        </div>
      ) : results.length > 0 ? (
        <div className="space-y-2">
          {results.map((user) => (
            <div
              key={user.id}
              className="flex items-center gap-3 p-3 rounded-xl bg-muted/30 hover:bg-muted/50 transition-colors"
            >
              <Avatar className="h-10 w-10">
                <AvatarImage src={user.avatar_url || undefined} />
                <AvatarFallback className="bg-gradient-to-br from-primary/20 to-primary/10 text-primary text-sm font-medium">
                  {user.name?.charAt(0).toUpperCase() || 'U'}
                </AvatarFallback>
              </Avatar>

              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-1.5">
                  <p className="font-medium truncate">{user.name || '익명'}</p>
                  <Link
                    href={`/u/${encodeURIComponent(user.name || '')}`}
                    className="text-muted-foreground hover:text-foreground transition-colors"
                    onClick={(e) => e.stopPropagation()}
                  >
                    <ExternalLink className="h-3.5 w-3.5" />
                  </Link>
                </div>
              </div>

              <div>
                {user.friendship_status === 'accepted' ? (
                  <Badge variant="secondary" className="gap-1 bg-green-500/10 text-green-600 border-0">
                    <Check className="h-3 w-3" />
                    친구
                  </Badge>
                ) : user.friendship_status === 'pending' ? (
                  <Badge variant="outline" className="gap-1">
                    <Clock className="h-3 w-3" />
                    요청중
                  </Badge>
                ) : (
                  <Button
                    size="sm"
                    className="gap-1.5 h-8 rounded-lg"
                    onClick={() => handleSendRequest(user.id)}
                    disabled={sendingTo === user.id}
                  >
                    {sendingTo === user.id ? (
                      <Loader2 className="h-3.5 w-3.5 animate-spin" />
                    ) : (
                      <UserPlus className="h-3.5 w-3.5" />
                    )}
                    추가
                  </Button>
                )}
              </div>
            </div>
          ))}
        </div>
      ) : hasSearched && query.length >= 2 ? (
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <div className="w-14 h-14 rounded-full bg-muted/50 flex items-center justify-center mb-3">
            <SearchX className="h-7 w-7 text-muted-foreground/50" />
          </div>
          <p className="text-muted-foreground">검색 결과가 없어요</p>
          <p className="text-sm text-muted-foreground/70 mt-1">
            다른 이름으로 검색해보세요
          </p>
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <div className="w-14 h-14 rounded-full bg-muted/50 flex items-center justify-center mb-3">
            <Search className="h-7 w-7 text-muted-foreground/50" />
          </div>
          <p className="text-muted-foreground">친구를 검색해보세요</p>
          <p className="text-sm text-muted-foreground/70 mt-1">
            2글자 이상 입력하면 검색됩니다
          </p>
        </div>
      )}
    </div>
  );
}
