'use client';

import { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import {
  Search,
  ChevronLeft,
  ChevronRight,
  ChevronsLeft,
  ChevronsRight,
  Ban,
  Shield,
  User,
  MoreHorizontal,
  Mail,
  Trophy,
  CheckCircle,
  Calendar,
  XCircle,
} from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
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
import { adminApi, type AdminUser } from '@/lib/api/admin';
import { toast } from 'sonner';

export default function AdminUsersPage() {
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [roleFilter, setRoleFilter] = useState<string>('all');
  const [includeBanned, setIncludeBanned] = useState(false);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [pageInput, setPageInput] = useState('1');
  const limit = 20;

  // Dialog state
  const [selectedUser, setSelectedUser] = useState<AdminUser | null>(null);
  const [showBanDialog, setShowBanDialog] = useState(false);
  const [banDuration, setBanDuration] = useState<string>('7');  // 정지 기간 (일)

  // Debounce search
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(search);
      setPage(1);
    }, 300);
    return () => clearTimeout(timer);
  }, [search]);

  const fetchUsers = useCallback(async () => {
    setLoading(true);
    try {
      const response = await adminApi.listUsers({
        search: debouncedSearch || undefined,
        role: roleFilter !== 'all' ? roleFilter : undefined,
        include_banned: includeBanned,
        page,
        limit,
      });
      setUsers(response.items);
      setTotal(response.total);
    } catch (error) {
      console.error('Failed to fetch users:', error);
      toast.error('사용자 목록을 불러오는데 실패했습니다');
    } finally {
      setLoading(false);
    }
  }, [debouncedSearch, roleFilter, includeBanned, page]);

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  const handleBanToggle = async () => {
    if (!selectedUser) return;

    try {
      const isBanned = isUserBanned(selectedUser);
      const newBanState = !isBanned;

      if (newBanState) {
        // 정지할 때: 기간 옵션 전달
        const banDays = banDuration === 'permanent' ? undefined : parseInt(banDuration);
        await adminApi.banUser(selectedUser.id, true, { ban_days: banDays });
        toast.success(
          banDuration === 'permanent'
            ? '사용자가 영구 정지되었습니다'
            : `사용자가 ${banDuration}일간 정지되었습니다`
        );
      } else {
        // 정지 해제
        await adminApi.banUser(selectedUser.id, false);
        toast.success('정지가 해제되었습니다');
      }

      fetchUsers();
    } catch (error) {
      console.error('Failed to ban/unban user:', error);
      toast.error('작업에 실패했습니다');
    } finally {
      setSelectedUser(null);
      setShowBanDialog(false);
      setBanDuration('7');
    }
  };

  // 사용자 정지 여부 체크 (banned_until 기준)
  const isUserBanned = (user: AdminUser): boolean => {
    if (!user.banned_until) return false;
    const bannedUntil = new Date(user.banned_until);
    return bannedUntil > new Date();
  };

  // 정지 만료일 포맷팅
  const formatBannedUntil = (bannedUntil: string): string => {
    const date = new Date(bannedUntil);
    if (date.getFullYear() >= 9999) {
      return '영구 정지';
    }
    return `${date.getFullYear()}.${(date.getMonth() + 1).toString().padStart(2, '0')}.${date.getDate().toString().padStart(2, '0')}까지`;
  };

  const totalPages = Math.ceil(total / limit);

  // pageInput과 page 동기화
  useEffect(() => {
    setPageInput(String(page));
  }, [page]);

  // 페이지 입력 후 Enter 시 이동
  const handlePageInputSubmit = () => {
    const val = parseInt(pageInput);
    if (!isNaN(val) && val >= 1 && val <= totalPages) {
      setPage(val);
    } else {
      setPageInput(String(page));
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="admin-section-header">
        <h2 className="text-lg font-semibold">사용자 목록</h2>
      </div>

      {/* Filters - Compact inline */}
      <div className="flex flex-wrap items-center gap-2">
        <div className="relative flex-1 min-w-[200px] max-w-xs">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground/40" />
          <input
            type="text"
            placeholder="이메일 또는 이름 검색..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full h-8 pl-9 pr-3 text-sm bg-white/5 border border-white/10 rounded-lg placeholder:text-muted-foreground/50 focus:outline-none focus:border-primary/50 transition-colors"
          />
        </div>

        <Select
          value={roleFilter}
          onValueChange={(v) => {
            setRoleFilter(v);
            setPage(1);
          }}
        >
          <SelectTrigger className="h-8 w-auto min-w-[90px] px-3 text-xs bg-white/5 border-white/10 rounded-lg">
            <SelectValue placeholder="역할" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">모든 역할</SelectItem>
            <SelectItem value="admin">관리자</SelectItem>
            <SelectItem value="user">일반 사용자</SelectItem>
          </SelectContent>
        </Select>

        <button
          onClick={() => {
            setIncludeBanned(!includeBanned);
            setPage(1);
          }}
          className={`h-8 px-3 text-xs rounded-lg border transition-colors ${
            includeBanned
              ? 'bg-primary/15 border-primary/30 text-primary'
              : 'bg-white/5 border-white/10 text-muted-foreground hover:text-foreground hover:border-white/20'
          }`}
        >
          정지 포함
        </button>
      </div>

      {/* Users List */}
      <div className="space-y-3">
        {loading ? (
          Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="admin-list-item animate-pulse">
              <div className="h-10 w-10 rounded-full bg-white/5" />
              <div className="flex-1 space-y-2">
                <div className="h-4 w-48 rounded bg-white/5" />
                <div className="h-3 w-32 rounded bg-white/5" />
              </div>
            </div>
          ))
        ) : users.length === 0 ? (
          <div className="admin-glass-card rounded-2xl p-8 text-center">
            <p className="text-muted-foreground">검색 결과가 없습니다</p>
          </div>
        ) : (
          users.map((user, i) => (
            <motion.div
              key={user.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.03 }}
            >
              <Link href={`/admin/users/${user.id}`}>
                <div className="admin-list-item group">
                  {/* Avatar */}
                  <div className="relative shrink-0">
                    {user.avatar_url ? (
                      <img
                        src={user.avatar_url}
                        alt={user.name || 'User'}
                        className="h-8 w-8 rounded-full object-cover"
                      />
                    ) : (
                      <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-primary/20 to-primary/5">
                        <User className="h-4 w-4 text-primary" />
                      </div>
                    )}
                    {user.role === 'admin' && (
                      <div className="absolute -bottom-0.5 -right-0.5 flex h-3.5 w-3.5 items-center justify-center rounded-full bg-primary">
                        <Shield className="h-2 w-2 text-white" />
                      </div>
                    )}
                  </div>

                  {/* Main Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <h3 className="text-sm font-medium text-foreground/90 truncate group-hover:text-primary transition-colors">
                        {user.name || 'Unknown'}
                      </h3>
                      {isUserBanned(user) ? (
                        <span className="inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded-full text-[10px] bg-red-500/10 text-red-400 border border-red-500/20">
                          <XCircle className="h-2.5 w-2.5" />
                          {user.banned_until && formatBannedUntil(user.banned_until)}
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded-full text-[10px] bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                          <CheckCircle className="h-2.5 w-2.5" />
                          정상
                        </span>
                      )}
                    </div>
                    <div className="flex items-center gap-3 mt-0.5">
                      <span className="flex items-center gap-1 text-[11px] text-muted-foreground/60">
                        <Mail className="h-3 w-3" />
                        {user.email}
                      </span>
                      <span className="flex items-center gap-1 text-[11px] text-muted-foreground/60">
                        <Trophy className="h-3 w-3" />
                        Lv. {user.level}
                      </span>
                      <span className="hidden sm:flex items-center gap-1 text-[11px] text-muted-foreground/60">
                        <CheckCircle className="h-3 w-3" />
                        {user.problems_solved} 풀이
                      </span>
                      <span className="hidden md:flex items-center gap-1 text-[11px] text-muted-foreground/60">
                        <Calendar className="h-3 w-3" />
                        {new Date(user.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>

                  {/* Role Badge */}
                  <div className="hidden lg:flex items-center gap-2 shrink-0">
                    <span
                      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium ${
                        user.role === 'admin'
                          ? 'bg-primary/10 text-primary border border-primary/20'
                          : 'bg-white/5 text-muted-foreground border border-white/10'
                      }`}
                    >
                      {user.role === 'admin' ? (
                        <>
                          <Shield className="h-2.5 w-2.5" />
                          관리자
                        </>
                      ) : (
                        <>
                          <User className="h-2.5 w-2.5" />
                          사용자
                        </>
                      )}
                    </span>
                  </div>

                  {/* Actions */}
                  <DropdownMenu>
                    <DropdownMenuTrigger
                      asChild
                      onClick={(e) => e.preventDefault()}
                    >
                      <Button
                        variant="ghost"
                        size="icon"
                        className="shrink-0 opacity-0 group-hover:opacity-100 transition-opacity"
                      >
                        <MoreHorizontal className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem asChild>
                        <Link href={`/admin/users/${user.id}`}>
                          상세 보기
                        </Link>
                      </DropdownMenuItem>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem
                        onClick={(e) => {
                          e.preventDefault();
                          setSelectedUser(user);
                          setShowBanDialog(true);
                        }}
                        className="text-destructive"
                      >
                        <Ban className="h-4 w-4 mr-2" />
                        {isUserBanned(user) ? '정지 해제' : '사용자 정지'}
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              </Link>
            </motion.div>
          ))
        )}
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between pt-2">
        <span className="text-sm text-muted-foreground/70">
          총 <span className="font-medium text-foreground">{total.toLocaleString()}</span>명
        </span>
        <div className="flex items-center gap-1.5">
          {/* 처음 */}
          <Button
            variant="outline"
            size="icon"
            onClick={() => setPage(1)}
            disabled={page === 1}
            className="h-8 w-8 rounded-xl bg-white/5 border-white/10 hover:bg-white/10"
            title="처음"
          >
            <ChevronsLeft className="h-4 w-4" />
          </Button>
          {/* 이전 */}
          <Button
            variant="outline"
            size="icon"
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
            className="h-8 w-8 rounded-xl bg-white/5 border-white/10 hover:bg-white/10"
            title="이전"
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>

          {/* 페이지 입력 */}
          <div className="flex items-center gap-1.5 px-2">
            <input
              type="number"
              min={1}
              max={totalPages || 1}
              value={pageInput}
              onChange={(e) => setPageInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  handlePageInputSubmit();
                  (e.target as HTMLInputElement).blur();
                }
              }}
              onBlur={handlePageInputSubmit}
              className="w-14 h-8 text-center text-sm rounded-lg bg-white/5 border border-white/10 focus:border-primary/50 focus:outline-none focus:ring-1 focus:ring-primary/20 transition-colors [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
            />
            <span className="text-sm text-muted-foreground">
              / {totalPages || 1}
            </span>
          </div>

          {/* 다음 */}
          <Button
            variant="outline"
            size="icon"
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            disabled={page >= totalPages}
            className="h-8 w-8 rounded-xl bg-white/5 border-white/10 hover:bg-white/10"
            title="다음"
          >
            <ChevronRight className="h-4 w-4" />
          </Button>
          {/* 마지막 */}
          <Button
            variant="outline"
            size="icon"
            onClick={() => setPage(totalPages)}
            disabled={page >= totalPages}
            className="h-8 w-8 rounded-xl bg-white/5 border-white/10 hover:bg-white/10"
            title="마지막"
          >
            <ChevronsRight className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Ban Dialog */}
      <AlertDialog
        open={showBanDialog}
        onOpenChange={(open) => {
          if (!open) {
            setShowBanDialog(false);
            setSelectedUser(null);
            setBanDuration('7');
          }
        }}
      >
        <AlertDialogContent className="admin-glass-card border-white/10">
          <AlertDialogHeader>
            <AlertDialogTitle>
              {selectedUser && isUserBanned(selectedUser) ? '정지 해제' : '사용자 정지'}
            </AlertDialogTitle>
            <AlertDialogDescription asChild>
              <div className="space-y-4">
                {selectedUser && isUserBanned(selectedUser) ? (
                  <p>
                    <span className="font-medium text-foreground">{selectedUser?.name || selectedUser?.email}</span>
                    의 정지를 해제하시겠습니까?
                  </p>
                ) : (
                  <>
                    <p>
                      <span className="font-medium text-foreground">{selectedUser?.name || selectedUser?.email}</span>
                      를 정지하시겠습니까? 정지된 사용자는 로그인할 수 없습니다.
                    </p>
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-foreground">정지 기간</label>
                      <Select value={banDuration} onValueChange={setBanDuration}>
                        <SelectTrigger className="w-full bg-white/5 border-white/10 rounded-xl">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="1">1일</SelectItem>
                          <SelectItem value="3">3일</SelectItem>
                          <SelectItem value="7">7일</SelectItem>
                          <SelectItem value="14">14일</SelectItem>
                          <SelectItem value="30">30일</SelectItem>
                          <SelectItem value="90">90일</SelectItem>
                          <SelectItem value="permanent">영구 정지</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </>
                )}
              </div>
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel className="rounded-xl">취소</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleBanToggle}
              className={`rounded-xl ${
                selectedUser && isUserBanned(selectedUser)
                  ? ''
                  : 'bg-destructive hover:bg-destructive/90'
              }`}
            >
              {selectedUser && isUserBanned(selectedUser) ? '해제' : '정지'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
