'use client';

import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from '@/components/ui/alert-dialog';
import { AlertTriangle } from 'lucide-react';

interface ExitWarningDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirmExit: () => void;
  isLoading?: boolean;
}

/**
 * 문제 풀이 페이지 이탈 경고 팝업
 * - 나가기/포기 시 ELO 감소 경고
 * - "다시 풀어보기" / "나가기" 선택
 */
export function ExitWarningDialog({
  isOpen,
  onClose,
  onConfirmExit,
  isLoading = false,
}: ExitWarningDialogProps) {
  return (
    <AlertDialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <AlertDialogContent className="sm:max-w-md">
        <AlertDialogHeader>
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-warning/20">
              <AlertTriangle className="h-5 w-5 text-warning" />
            </div>
            <AlertDialogTitle>문제를 포기하시겠어요?</AlertDialogTitle>
          </div>
          <AlertDialogDescription className="pt-2 text-left">
            지금 나가면 <strong className="text-foreground">실력 측정(ELO)에 불이익</strong>이 있을 수 있어요.
            <br />
            <span className="text-muted-foreground">포기로 기록되어 ELO 점수가 감소합니다.</span>
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter className="sm:justify-end gap-2">
          <AlertDialogCancel
            onClick={onClose}
            disabled={isLoading}
            className="border-primary/30 hover:bg-primary/10"
          >
            다시 풀어보기
          </AlertDialogCancel>
          <AlertDialogAction
            onClick={onConfirmExit}
            disabled={isLoading}
            className="bg-destructive hover:bg-destructive/90"
          >
            {isLoading ? '처리 중...' : '나가기'}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
