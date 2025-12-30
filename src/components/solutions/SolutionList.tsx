'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
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
import {
  ThumbsUp,
  ThumbsDown,
  MessageCircle,
  ChevronDown,
  ChevronUp,
  Copy,
  Check,
  Loader2,
  MoreVertical,
  Edit,
  Trash2,
} from 'lucide-react';
import { solutionsApi, type SolutionListItem } from '@/lib/api';
import { useAuth } from '@/hooks/useAuth';
import { formatDistanceToNow } from 'date-fns';
import { ko } from 'date-fns/locale';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { getLanguageLabel, getLanguageColor } from './constants';

interface SolutionListProps {
  solutions: SolutionListItem[];
  onVote: (solutionId: string, voteType: 'up' | 'down') => void;
  onRefresh?: () => void;
  loading?: boolean;
}

export function SolutionList({ solutions, onVote, onRefresh, loading }: SolutionListProps) {
  if (solutions.length === 0) {
    return (
      <div className="text-center py-12 text-muted-foreground">
        <p>아직 등록된 풀이가 없습니다.</p>
        <p className="text-sm mt-1">첫 번째 풀이를 작성해보세요!</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {solutions.map((solution) => (
        <SolutionCard
          key={solution.id}
          solution={solution}
          onVote={onVote}
          onRefresh={onRefresh}
        />
      ))}
      {loading && (
        <div className="flex justify-center py-4">
          <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
        </div>
      )}
    </div>
  );
}

interface SolutionCardProps {
  solution: SolutionListItem;
  onVote: (solutionId: string, voteType: 'up' | 'down') => void;
  onRefresh?: () => void;
}

function SolutionCard({ solution, onVote, onRefresh }: SolutionCardProps) {
  const { user } = useAuth();
  const [expanded, setExpanded] = useState(false);
  const [copied, setCopied] = useState(false);

  // 수정 상태
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(solution.title || '');
  const [editLanguage, setEditLanguage] = useState(solution.language);
  const [editCode, setEditCode] = useState(solution.code);
  const [isSaving, setIsSaving] = useState(false);

  // 삭제 상태
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  const isOwner = user?.id === solution.user_id;
  const authorInitial = solution.author_name?.charAt(0).toUpperCase() || 'U';
  const timeAgo = formatDistanceToNow(new Date(solution.created_at), {
    addSuffix: true,
    locale: ko,
  });

  const handleCopy = async () => {
    await navigator.clipboard.writeText(solution.code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleEdit = () => {
    setEditTitle(solution.title || '');
    setEditLanguage(solution.language);
    setEditCode(solution.code);
    setIsEditing(true);
    setExpanded(true);
  };

  const handleCancelEdit = () => {
    setIsEditing(false);
    setEditTitle(solution.title || '');
    setEditLanguage(solution.language);
    setEditCode(solution.code);
  };

  const handleSaveEdit = async () => {
    setIsSaving(true);
    try {
      await solutionsApi.updateSolution(solution.id, {
        title: editTitle.trim() || undefined,
        language: editLanguage,
        code: editCode.trim(),
      });
      setIsEditing(false);
      onRefresh?.();
    } catch (err) {
      console.error('Failed to update solution:', err);
    } finally {
      setIsSaving(false);
    }
  };

  const handleDelete = async () => {
    setIsDeleting(true);
    try {
      await solutionsApi.deleteSolution(solution.id);
      setShowDeleteDialog(false);
      onRefresh?.();
    } catch (err) {
      console.error('Failed to delete solution:', err);
    } finally {
      setIsDeleting(false);
    }
  };

  const languageForHighlighter = solution.language === 'cpp' ? 'cpp' : solution.language;

  return (
    <>
      <div className="border border-border rounded-lg overflow-hidden bg-card">
        {/* Header - Clickable to expand */}
        <button
          onClick={() => !isEditing && setExpanded(!expanded)}
          className="w-full flex items-center justify-between px-4 py-3 hover:bg-muted/50 transition-colors"
          disabled={isEditing}
        >
          <div className="flex items-center gap-3">
            <Avatar className="h-8 w-8">
              <AvatarImage src={solution.author_avatar || undefined} />
              <AvatarFallback className="text-xs">{authorInitial}</AvatarFallback>
            </Avatar>
            <div className="text-left space-y-1">
              <div className="flex items-center gap-2">
                <span className="font-medium text-sm">
                  {solution.author_name || '익명'}
                </span>
                {solution.title && (
                  <span className="text-sm text-foreground truncate max-w-[200px]">
                    {solution.title}
                  </span>
                )}
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs text-muted-foreground">{timeAgo}</span>
                <Badge
                  variant="outline"
                  className={`text-xs py-0 ${getLanguageColor(solution.language)}`}
                >
                  {getLanguageLabel(solution.language)}
                </Badge>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {/* Vote counts (display only) */}
            <div className="flex items-center gap-1 text-muted-foreground">
              <ThumbsUp className="h-4 w-4" />
              <span className="text-sm">{solution.upvotes}</span>
            </div>
            <div className="flex items-center gap-1 text-muted-foreground">
              <MessageCircle className="h-4 w-4" />
              <span className="text-sm">{solution.comment_count}</span>
            </div>

            {/* Owner Actions */}
            {isOwner && (
              <DropdownMenu>
                <DropdownMenuTrigger asChild onClick={(e) => e.stopPropagation()}>
                  <Button variant="ghost" size="sm" className="h-7 w-7 p-0">
                    <MoreVertical className="h-4 w-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" onClick={(e) => e.stopPropagation()}>
                  <DropdownMenuItem onSelect={handleEdit}>
                    <Edit className="h-4 w-4 mr-2" />
                    수정
                  </DropdownMenuItem>
                  <DropdownMenuItem
                    onSelect={() => setShowDeleteDialog(true)}
                    className="text-destructive focus:text-destructive"
                  >
                    <Trash2 className="h-4 w-4 mr-2" />
                    삭제
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            )}

            {!isEditing && (
              expanded ? (
                <ChevronUp className="h-4 w-4 text-muted-foreground" />
              ) : (
                <ChevronDown className="h-4 w-4 text-muted-foreground" />
              )
            )}
          </div>
        </button>

        {/* Expanded Code Section */}
        {expanded && (
          <div className="border-t border-border">
            {isEditing ? (
              /* 수정 모드 */
              <div className="p-4 space-y-3">
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="text-sm font-medium mb-1 block">제목 (선택)</label>
                    <Input
                      value={editTitle}
                      onChange={(e) => setEditTitle(e.target.value)}
                      placeholder="예: O(n) 풀이"
                    />
                  </div>
                  <div>
                    <label className="text-sm font-medium mb-1 block">언어</label>
                    <Select value={editLanguage} onValueChange={setEditLanguage}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="python">Python</SelectItem>
                        <SelectItem value="java">Java</SelectItem>
                        <SelectItem value="cpp">C++</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div>
                  <label className="text-sm font-medium mb-1 block">코드</label>
                  <Textarea
                    value={editCode}
                    onChange={(e) => setEditCode(e.target.value)}
                    className="font-mono min-h-[300px] text-sm"
                  />
                </div>
                <div className="flex justify-end gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleCancelEdit}
                    disabled={isSaving}
                  >
                    취소
                  </Button>
                  <Button
                    size="sm"
                    onClick={handleSaveEdit}
                    disabled={isSaving || !editCode.trim()}
                  >
                    {isSaving && <Loader2 className="h-4 w-4 animate-spin mr-2" />}
                    저장
                  </Button>
                </div>
              </div>
            ) : (
              /* 보기 모드 */
              <>
                {/* Code */}
                <SyntaxHighlighter
                  language={languageForHighlighter}
                  style={oneDark}
                  customStyle={{
                    margin: 0,
                    borderRadius: 0,
                    fontSize: '0.8rem',
                    maxHeight: '400px',
                  }}
                >
                  {solution.code}
                </SyntaxHighlighter>
                {/* Toolbar */}
                <div className="flex items-center justify-between px-3 py-2 bg-muted/30 border-t border-border/50">
                  <div className="flex items-center gap-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-7 px-2 gap-1"
                      onClick={(e) => {
                        e.stopPropagation();
                        onVote(solution.id, 'up');
                      }}
                    >
                      <ThumbsUp className="h-3.5 w-3.5" />
                      <span className="text-xs">{solution.upvotes}</span>
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-7 px-2 gap-1"
                      onClick={(e) => {
                        e.stopPropagation();
                        onVote(solution.id, 'down');
                      }}
                    >
                      <ThumbsDown className="h-3.5 w-3.5" />
                      <span className="text-xs">{solution.downvotes}</span>
                    </Button>
                    <Link href={`/solutions/${solution.id}`} onClick={(e) => e.stopPropagation()}>
                      <Button variant="ghost" size="sm" className="h-7 px-2 gap-1">
                        <MessageCircle className="h-3.5 w-3.5" />
                        <span className="text-xs">댓글 {solution.comment_count}</span>
                      </Button>
                    </Link>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-7 px-2 gap-1"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleCopy();
                    }}
                  >
                    {copied ? (
                      <>
                        <Check className="h-3.5 w-3.5" />
                        <span className="text-xs">Copied</span>
                      </>
                    ) : (
                      <>
                        <Copy className="h-3.5 w-3.5" />
                        <span className="text-xs">Copy</span>
                      </>
                    )}
                  </Button>
                </div>
              </>
            )}
          </div>
        )}
      </div>

      {/* 삭제 확인 다이얼로그 */}
      <AlertDialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>풀이를 삭제하시겠습니까?</AlertDialogTitle>
            <AlertDialogDescription>
              이 작업은 되돌릴 수 없습니다. 풀이와 관련된 모든 댓글도 함께 삭제됩니다.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={isDeleting}>취소</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDelete}
              disabled={isDeleting}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              {isDeleting && <Loader2 className="h-4 w-4 animate-spin mr-2" />}
              삭제
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}
