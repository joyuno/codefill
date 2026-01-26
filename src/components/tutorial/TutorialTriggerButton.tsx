'use client';

import { HelpCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import { useTutorialContext } from './TutorialProvider';
import type { ProblemType } from '@/lib/tutorial/constants';

interface TutorialTriggerButtonProps {
  problemType: ProblemType;
  className?: string;
}

/**
 * 튜토리얼 다시보기 버튼 ("?" 버튼)
 */
export function TutorialTriggerButton({ problemType, className }: TutorialTriggerButtonProps) {
  const { startTutorial, resetTutorial, isRunning } = useTutorialContext();

  const handleClick = () => {
    if (isRunning) return;
    // 튜토리얼 상태 리셋 후 시작
    resetTutorial(problemType);
    // 약간의 딜레이 후 시작 (DOM 업데이트 대기)
    setTimeout(() => {
      startTutorial(problemType);
    }, 100);
  };

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <Button
            variant="ghost"
            size="icon"
            onClick={handleClick}
            disabled={isRunning}
            className={className}
          >
            <HelpCircle className="h-4 w-4" />
          </Button>
        </TooltipTrigger>
        <TooltipContent>
          <p>튜토리얼 다시보기</p>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}
