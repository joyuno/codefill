'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
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
import { solutionsApi, type CommentItem } from '@/lib/api';
import { useAuth } from '@/hooks/useAuth';
import {
  ThumbsUp,
  ThumbsDown,
  Reply,
  Edit,
  Trash2,
  Loader2,
  MoreVertical,
  X,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { formatDistanceToNow } from 'date-fns';
import { ko } from 'date-fns/locale';

interface CommentSectionProps {
  solutionId: string;
  comments: CommentItem[];
  onCommentCreated: () => void;
}

export function CommentSection({
  solutionId,
  comments,
  onCommentCreated,
}: CommentSectionProps) {
  const [newComment, setNewComment] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newComment.trim()) return;

    setSubmitting(true);
    setError(null);

    try {
      await solutionsApi.createComment(solutionId, { content: newComment.trim() });
      setNewComment('');
      onCommentCreated();
    } catch (err) {
      setError(err instanceof Error ? err.message : '댓글 작성에 실패했습니다.');
    } finally {
      setSubmitting(false);
    }
  };

  // Build comment tree (top-level + replies)
  const topLevelComments = comments.filter((c) => !c.parent_id);
  const repliesMap = new Map<string, CommentItem[]>();
  comments.forEach((c) => {
    if (c.parent_id) {
      const existing = repliesMap.get(c.parent_id) || [];
      repliesMap.set(c.parent_id, [...existing, c]);
    }
  });

  return (
    <div className="p-6 space-y-6">
      {/* New Comment Form */}
      <form onSubmit={handleSubmit} className="space-y-3">
        <Textarea
          value={newComment}
          onChange={(e) => setNewComment(e.target.value)}
          placeholder="댓글을 작성하세요..."
          className="min-h-[80px]"
        />
        {error && (
          <p className="text-sm text-destructive">{error}</p>
        )}
        <div className="flex justify-end">
          <Button type="submit" disabled={submitting || !newComment.trim()}>
            {submitting && <Loader2 className="h-4 w-4 animate-spin mr-2" />}
            댓글 작성
          </Button>
        </div>
      </form>

      {/* Comments List */}
      {topLevelComments.length === 0 ? (
        <div className="text-center py-8 text-muted-foreground">
          <p>아직 댓글이 없습니다.</p>
          <p className="text-sm mt-1">첫 번째 댓글을 작성해보세요!</p>
        </div>
      ) : (
        <div className="space-y-4">
          {topLevelComments.map((comment) => (
            <CommentCard
              key={comment.id}
              comment={comment}
              replies={comment.replies || repliesMap.get(comment.id) || []}
              solutionId={solutionId}
              onCommentCreated={onCommentCreated}
            />
          ))}
        </div>
      )}
    </div>
  );
}

interface CommentCardProps {
  comment: CommentItem;
  replies: CommentItem[];
  solutionId: string;
  onCommentCreated: () => void;
  isReply?: boolean;
}

function CommentCard({
  comment,
  replies,
  solutionId,
  onCommentCreated,
  isReply = false,
}: CommentCardProps) {
  const { user } = useAuth();
  const [showReplyForm, setShowReplyForm] = useState(false);
  const [replyContent, setReplyContent] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [localVotes, setLocalVotes] = useState({
    upvotes: comment.upvotes,
    downvotes: comment.downvotes,
    my_vote: comment.my_vote,
  });

  // 수정 상태
  const [isEditing, setIsEditing] = useState(false);
  const [editContent, setEditContent] = useState(comment.content);
  const [isSaving, setIsSaving] = useState(false);

  // 삭제 상태
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  const isOwner = user?.id === comment.user_id;
  const authorInitial = comment.author_name?.charAt(0).toUpperCase() || 'U';
  const timeAgo = formatDistanceToNow(new Date(comment.created_at), {
    addSuffix: true,
    locale: ko,
  });

  const handleVote = async (voteType: 'up' | 'down') => {
    try {
      const result = await solutionsApi.voteComment(comment.id, voteType);
      setLocalVotes({
        upvotes: result.upvotes,
        downvotes: result.downvotes,
        my_vote: result.my_vote,
      });
    } catch (err) {
      console.error('Vote failed:', err);
    }
  };

  const handleReply = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!replyContent.trim()) return;

    setSubmitting(true);
    try {
      await solutionsApi.createComment(solutionId, {
        content: replyContent.trim(),
        parent_id: comment.id,
      });
      setReplyContent('');
      setShowReplyForm(false);
      onCommentCreated();
    } catch (err) {
      console.error('Reply failed:', err);
    } finally {
      setSubmitting(false);
    }
  };

  const handleEdit = () => {
    setEditContent(comment.content);
    setIsEditing(true);
  };

  const handleCancelEdit = () => {
    setIsEditing(false);
    setEditContent(comment.content);
  };

  const handleSaveEdit = async () => {
    if (!editContent.trim()) return;

    setIsSaving(true);
    try {
      await solutionsApi.updateComment(comment.id, editContent.trim());
      setIsEditing(false);
      onCommentCreated();
    } catch (err) {
      console.error('Failed to update comment:', err);
    } finally {
      setIsSaving(false);
    }
  };

  const handleDelete = async () => {
    setIsDeleting(true);
    try {
      await solutionsApi.deleteComment(comment.id);
      setShowDeleteDialog(false);
      onCommentCreated();
    } catch (err) {
      console.error('Failed to delete comment:', err);
    } finally {
      setIsDeleting(false);
    }
  };

  if (comment.is_deleted) {
    return (
      <div className={cn('py-3', isReply && 'ml-8 pl-4 border-l-2 border-border')}>
        <p className="text-sm text-muted-foreground italic">삭제된 댓글입니다.</p>
        {/* Still show replies if any */}
        {replies.length > 0 && (
          <div className="mt-4 space-y-4">
            {replies.map((reply) => (
              <CommentCard
                key={reply.id}
                comment={reply}
                replies={[]}
                solutionId={solutionId}
                onCommentCreated={onCommentCreated}
                isReply
              />
            ))}
          </div>
        )}
      </div>
    );
  }

  return (
    <>
      <div className={cn(isReply && 'ml-8 pl-4 border-l-2 border-border')}>
        <div className="flex gap-3">
          <Avatar className="h-8 w-8 shrink-0">
            <AvatarImage src={comment.author_avatar || undefined} />
            <AvatarFallback className="text-xs">{authorInitial}</AvatarFallback>
          </Avatar>
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between mb-1">
              <div className="flex items-center gap-2">
                <span className="font-medium text-sm">
                  {comment.author_name || '익명'}
                </span>
                <span className="text-xs text-muted-foreground">{timeAgo}</span>
              </div>

              {/* Owner Actions */}
              {isOwner && !comment.is_deleted && (
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" size="sm" className="h-6 w-6 p-0">
                      <MoreVertical className="h-3.5 w-3.5" />
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
            </div>

            {isEditing ? (
              /* 수정 모드 */
              <div className="space-y-2">
                <Textarea
                  value={editContent}
                  onChange={(e) => setEditContent(e.target.value)}
                  className="min-h-[60px] text-sm"
                />
                <div className="flex justify-end gap-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleCancelEdit}
                    disabled={isSaving}
                  >
                    취소
                  </Button>
                  <Button
                    size="sm"
                    onClick={handleSaveEdit}
                    disabled={isSaving || !editContent.trim()}
                  >
                    {isSaving && <Loader2 className="h-3 w-3 animate-spin mr-1" />}
                    저장
                  </Button>
                </div>
              </div>
            ) : (
              /* 보기 모드 */
              <>
                <p className="text-sm whitespace-pre-wrap">{comment.content}</p>

                {/* Actions */}
                <div className="flex items-center gap-2 mt-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    className={cn(
                      'h-7 px-2 gap-1',
                      localVotes.my_vote === 'up' && 'text-primary'
                    )}
                    onClick={() => handleVote('up')}
                  >
                    <ThumbsUp className="h-3.5 w-3.5" />
                    {localVotes.upvotes > 0 && localVotes.upvotes}
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    className={cn(
                      'h-7 px-2 gap-1',
                      localVotes.my_vote === 'down' && 'text-destructive'
                    )}
                    onClick={() => handleVote('down')}
                  >
                    <ThumbsDown className="h-3.5 w-3.5" />
                    {localVotes.downvotes > 0 && localVotes.downvotes}
                  </Button>
                  {!isReply && (
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-7 px-2 gap-1"
                      onClick={() => setShowReplyForm(!showReplyForm)}
                    >
                      <Reply className="h-3.5 w-3.5" />
                      답글
                    </Button>
                  )}
                </div>
              </>
            )}

            {/* Reply Form */}
            {showReplyForm && (
              <form onSubmit={handleReply} className="mt-3 space-y-2">
                <Textarea
                  value={replyContent}
                  onChange={(e) => setReplyContent(e.target.value)}
                  placeholder="답글을 작성하세요..."
                  className="min-h-[60px] text-sm"
                />
                <div className="flex justify-end gap-2">
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={() => setShowReplyForm(false)}
                  >
                    취소
                  </Button>
                  <Button
                    type="submit"
                    size="sm"
                    disabled={submitting || !replyContent.trim()}
                  >
                    {submitting && <Loader2 className="h-3 w-3 animate-spin mr-1" />}
                    답글 작성
                  </Button>
                </div>
              </form>
            )}
          </div>
        </div>

        {/* Replies */}
        {replies.length > 0 && (
          <div className="mt-4 space-y-4">
            {replies.map((reply) => (
              <CommentCard
                key={reply.id}
                comment={reply}
                replies={[]}
                solutionId={solutionId}
                onCommentCreated={onCommentCreated}
                isReply
              />
            ))}
          </div>
        )}
      </div>

      {/* 삭제 확인 다이얼로그 */}
      <AlertDialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>댓글을 삭제하시겠습니까?</AlertDialogTitle>
            <AlertDialogDescription>
              {replies.length > 0
                ? '대댓글이 있어 내용만 삭제됩니다.'
                : '이 작업은 되돌릴 수 없습니다.'}
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
