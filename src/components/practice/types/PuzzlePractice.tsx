'use client';

import { useState, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import {
  GripVertical,
  CheckCircle,
  XCircle,
  RotateCcw,
  HelpCircle,
  Shuffle,
} from 'lucide-react';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import { cn } from '@/lib/utils';
import ReactMarkdown from 'react-markdown';

interface PuzzleBlock {
  id: string;
  code: string;
  indentation: number;
}

interface PuzzlePracticeProps {
  problemDescription: string;
  blocks: PuzzleBlock[];
  onSubmit: (blockOrder: Array<{ id: string; indentation: number }>) => void;
  onHintRequest: (level: number, currentOrder: string[]) => void;  // 현재 배치 순서 추가
  hints: string[];
  results?: Record<string, boolean>;
  isSubmitted?: boolean;
}

export function PuzzlePractice({
  problemDescription,
  blocks: initialBlocks,
  onSubmit,
  onHintRequest,
  hints,
  results,
  isSubmitted = false,
}: PuzzlePracticeProps) {
  // Shuffle blocks initially
  const shuffleArray = <T,>(array: T[]): T[] => {
    const shuffled = [...array];
    for (let i = shuffled.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    return shuffled;
  };

  const [availableBlocks, setAvailableBlocks] = useState<PuzzleBlock[]>(() =>
    shuffleArray(initialBlocks.map((b) => ({ ...b, indentation: 0 })))
  );
  const [arrangedBlocks, setArrangedBlocks] = useState<PuzzleBlock[]>([]);
  const [draggedBlock, setDraggedBlock] = useState<PuzzleBlock | null>(null);
  const [dragSource, setDragSource] = useState<'available' | 'arranged' | null>(null);
  const [hintLevel, setHintLevel] = useState(0);

  // Handle drag start
  const handleDragStart = (block: PuzzleBlock, source: 'available' | 'arranged') => {
    setDraggedBlock(block);
    setDragSource(source);
  };

  // Handle drag over for arranged area
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  // Handle drop on arranged area
  const handleDropOnArranged = (e: React.DragEvent, dropIndex?: number) => {
    e.preventDefault();
    if (!draggedBlock) return;

    if (dragSource === 'available') {
      // Move from available to arranged
      setAvailableBlocks((prev) => prev.filter((b) => b.id !== draggedBlock.id));
      setArrangedBlocks((prev) => {
        const newArranged = [...prev];
        if (dropIndex !== undefined) {
          newArranged.splice(dropIndex, 0, draggedBlock);
        } else {
          newArranged.push(draggedBlock);
        }
        return newArranged;
      });
    } else if (dragSource === 'arranged' && dropIndex !== undefined) {
      // Reorder within arranged
      setArrangedBlocks((prev) => {
        const newArranged = prev.filter((b) => b.id !== draggedBlock.id);
        newArranged.splice(dropIndex, 0, draggedBlock);
        return newArranged;
      });
    }

    setDraggedBlock(null);
    setDragSource(null);
  };

  // Handle drop on available area (return block)
  const handleDropOnAvailable = (e: React.DragEvent) => {
    e.preventDefault();
    if (!draggedBlock || dragSource !== 'arranged') return;

    setArrangedBlocks((prev) => prev.filter((b) => b.id !== draggedBlock.id));
    setAvailableBlocks((prev) => [...prev, draggedBlock]);

    setDraggedBlock(null);
    setDragSource(null);
  };

  // 들여쓰기 조절 기능 제거됨 - 코드 내부에 이미 들여쓰기 포함

  // Reset puzzle
  const handleReset = () => {
    setAvailableBlocks(shuffleArray(initialBlocks.map((b) => ({ ...b, indentation: 0 }))));
    setArrangedBlocks([]);
  };

  // Shuffle available blocks
  const handleShuffle = () => {
    setAvailableBlocks((prev) => shuffleArray(prev));
  };

  // Submit answer
  const handleSubmit = () => {
    const submission = arrangedBlocks.map((block) => ({
      id: block.id,
      indentation: block.indentation,
    }));
    onSubmit(submission);
  };

  // Get hint - 현재 배치 순서와 함께 전달
  const handleGetHint = () => {
    if (hintLevel < hints.length) {
      const currentOrder = arrangedBlocks.map(block => block.id);
      onHintRequest(hintLevel + 1, currentOrder);
      setHintLevel((prev) => prev + 1);
    }
  };

  return (
    <div className="flex h-full flex-col gap-4">
      {/* Problem description */}
      <Card className="border-border bg-card/50 p-4">
        <p className="text-sm text-muted-foreground">{problemDescription}</p>
      </Card>

      <div className="flex flex-1 gap-4 overflow-hidden">
        {/* Available blocks */}
        <div className="flex w-1/2 flex-col">
          <div className="mb-2 flex items-center justify-between">
            <h3 className="text-sm font-medium text-muted-foreground">
              코드 블록 (드래그하여 배열)
            </h3>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleShuffle}
              disabled={isSubmitted}
            >
              <Shuffle className="mr-1 h-3 w-3" />
              섞기
            </Button>
          </div>
          <div
            className={cn(
              'flex-1 overflow-auto rounded-lg border-2 border-dashed p-3',
              draggedBlock && dragSource === 'arranged'
                ? 'border-primary bg-primary/5'
                : 'border-border bg-muted/20'
            )}
            onDragOver={handleDragOver}
            onDrop={handleDropOnAvailable}
          >
            <div className="space-y-2">
              {availableBlocks.map((block) => (
                <div
                  key={block.id}
                  draggable={!isSubmitted}
                  onDragStart={() => handleDragStart(block, 'available')}
                  className={cn(
                    'flex cursor-grab items-center gap-2 rounded-md border bg-card px-3 py-2 font-mono text-sm transition-all',
                    draggedBlock?.id === block.id && 'opacity-50',
                    isSubmitted && 'cursor-default opacity-60'
                  )}
                >
                  <GripVertical className="h-4 w-4 shrink-0 text-muted-foreground" />
                  <code className="flex-1 whitespace-pre">{block.code}</code>
                </div>
              ))}
              {availableBlocks.length === 0 && (
                <p className="py-8 text-center text-sm text-muted-foreground">
                  모든 블록이 배열되었습니다
                </p>
              )}
            </div>
          </div>
        </div>

        {/* Arranged blocks */}
        <div className="flex w-1/2 flex-col">
          <div className="mb-2 flex items-center justify-between">
            <h3 className="text-sm font-medium text-muted-foreground">
              정답 영역 ({arrangedBlocks.length}개 배열됨)
            </h3>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleReset}
              disabled={isSubmitted}
            >
              <RotateCcw className="mr-1 h-3 w-3" />
              초기화
            </Button>
          </div>
          <div
            className={cn(
              'flex-1 overflow-auto rounded-lg border-2 p-3',
              draggedBlock && dragSource === 'available'
                ? 'border-primary bg-primary/5'
                : 'border-border bg-code-bg'
            )}
            onDragOver={handleDragOver}
            onDrop={(e) => handleDropOnArranged(e)}
          >
            <div className="space-y-1">
              {arrangedBlocks.length === 0 && (
                <p className="py-8 text-center text-sm text-muted-foreground">
                  코드 블록을 여기로 드래그하세요
                </p>
              )}
              {arrangedBlocks.map((block, index) => {
                const isCorrect = results?.[block.id];
                return (
                  <div
                    key={block.id}
                    draggable={!isSubmitted}
                    onDragStart={() => handleDragStart(block, 'arranged')}
                    onDragOver={handleDragOver}
                    onDrop={(e) => {
                      e.stopPropagation();
                      handleDropOnArranged(e, index);
                    }}
                    className={cn(
                      'group flex items-center gap-1 rounded-md border px-2 py-1.5 font-mono text-sm transition-all',
                      draggedBlock?.id === block.id && 'opacity-50',
                      isSubmitted
                        ? isCorrect
                          ? 'border-green-500/50 bg-green-500/10'
                          : 'border-red-500/50 bg-red-500/10'
                        : 'cursor-grab border-border bg-card hover:border-primary/50'
                    )}
                    // 코드 내부에 이미 들여쓰기 포함되어 있으므로 CSS margin 제거
                  >
                    <GripVertical className="h-4 w-4 shrink-0 text-muted-foreground" />

                    {/* 들여쓰기 조절 컨트롤 제거 - 코드 내부에 이미 들여쓰기 포함됨 */}

                    <code className="flex-1 whitespace-pre">{block.code}</code>

                    {isSubmitted && (
                      <span className="shrink-0">
                        {isCorrect ? (
                          <CheckCircle className="h-4 w-4 text-green-500" />
                        ) : (
                          <XCircle className="h-4 w-4 text-red-500" />
                        )}
                      </span>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          {/* Hint button */}
          <Popover>
            <PopoverTrigger asChild>
              <Button variant="outline" size="sm" disabled={hintLevel >= 3}>
                <HelpCircle className="mr-1 h-4 w-4" />
                힌트 ({hintLevel}/3)
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-72">
              <div className="space-y-2">
                <p className="text-sm font-medium">힌트</p>
                {hints.slice(0, hintLevel).map((hint, i) => (
                  <div key={i} className="text-sm text-muted-foreground">
                    <span className="font-medium text-foreground">Level {i + 1}:</span>{' '}
                    <ReactMarkdown
                      components={{
                        strong: ({ children }) => (
                          <strong className="font-bold text-primary">{children}</strong>
                        ),
                        p: ({ children }) => <span className="inline">{children}</span>,
                      }}
                    >
                      {hint}
                    </ReactMarkdown>
                  </div>
                ))}
                {hintLevel < 3 && (
                  <Button size="sm" variant="outline" onClick={handleGetHint}>
                    다음 힌트 보기 (-10 XP)
                  </Button>
                )}
              </div>
            </PopoverContent>
          </Popover>

{/* 들여쓰기 조절 기능 제거됨 - 코드 내부에 이미 들여쓰기 포함 */}
        </div>

        {!isSubmitted && (
          <Button
            onClick={handleSubmit}
            disabled={arrangedBlocks.length === 0}
          >
            제출하기
          </Button>
        )}
      </div>
    </div>
  );
}
