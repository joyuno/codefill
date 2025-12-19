'use client';

import { useState, useEffect } from 'react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { HelpCircle, CheckCircle, XCircle } from 'lucide-react';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';

interface Blank {
  id: string;
  position: number;
  answer: string;
  hints: string[];
}

interface BlankPracticeProps {
  code: string;
  blanks: Blank[];
  onSubmit: (answers: Record<string, string>) => void;
  onHintRequest: (blankId: string, level: number) => void;
  results?: Record<string, boolean>;
  isSubmitted?: boolean;
}

export function BlankPractice({
  code,
  blanks,
  onSubmit,
  onHintRequest,
  results,
  isSubmitted = false,
}: BlankPracticeProps) {
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [hintLevels, setHintLevels] = useState<Record<string, number>>({});

  // Parse code and replace blanks with input fields
  const renderCodeWithBlanks = () => {
    const parts: JSX.Element[] = [];
    let lastIndex = 0;
    let blankIndex = 0;

    // Find all ___ patterns
    const blankPattern = /___/g;
    let match;

    while ((match = blankPattern.exec(code)) !== null) {
      // Add code before blank
      if (match.index > lastIndex) {
        parts.push(
          <span key={`code-${lastIndex}`} className="text-code-variable">
            {code.slice(lastIndex, match.index)}
          </span>
        );
      }

      // Get corresponding blank info
      const blank = blanks[blankIndex];
      if (blank) {
        const isCorrect = results?.[blank.id];
        const currentHintLevel = hintLevels[blank.id] || 0;

        parts.push(
          <span key={`blank-${blank.id}`} className="inline-flex items-center gap-1">
            <span className="relative inline-flex items-center">
              <Input
                value={answers[blank.id] || ''}
                onChange={(e) =>
                  setAnswers((prev) => ({ ...prev, [blank.id]: e.target.value }))
                }
                className={`inline-block h-7 w-32 rounded border px-2 py-0 font-mono text-sm ${
                  isSubmitted
                    ? isCorrect
                      ? 'border-green-500 bg-green-500/10'
                      : 'border-red-500 bg-red-500/10'
                    : 'border-primary/50 bg-code-bg'
                }`}
                placeholder="___"
                disabled={isSubmitted}
              />
              {isSubmitted && (
                <span className="absolute -right-6 top-1/2 -translate-y-1/2">
                  {isCorrect ? (
                    <CheckCircle className="h-4 w-4 text-green-500" />
                  ) : (
                    <XCircle className="h-4 w-4 text-red-500" />
                  )}
                </span>
              )}
            </span>
            {!isSubmitted && (
              <Popover>
                <PopoverTrigger asChild>
                  <button className="text-muted-foreground hover:text-primary">
                    <HelpCircle className="h-4 w-4" />
                  </button>
                </PopoverTrigger>
                <PopoverContent className="w-64 p-3">
                  <div className="space-y-2">
                    <p className="text-sm font-medium">힌트 보기</p>
                    {blank.hints.slice(0, currentHintLevel + 1).map((hint, i) => (
                      <p key={i} className="text-sm text-muted-foreground">
                        Level {i + 1}: {hint}
                      </p>
                    ))}
                    {currentHintLevel < blank.hints.length - 1 && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => {
                          const newLevel = currentHintLevel + 1;
                          setHintLevels((prev) => ({ ...prev, [blank.id]: newLevel }));
                          onHintRequest(blank.id, newLevel);
                        }}
                      >
                        다음 힌트 (-10 XP)
                      </Button>
                    )}
                  </div>
                </PopoverContent>
              </Popover>
            )}
          </span>
        );
      }

      lastIndex = match.index + 3; // "___".length
      blankIndex++;
    }

    // Add remaining code
    if (lastIndex < code.length) {
      parts.push(
        <span key={`code-end`} className="text-code-variable">
          {code.slice(lastIndex)}
        </span>
      );
    }

    return parts;
  };

  const handleSubmit = () => {
    onSubmit(answers);
  };

  const filledCount = Object.values(answers).filter((a) => a.trim()).length;

  return (
    <div className="flex h-full flex-col">
      <div className="flex-1 overflow-auto rounded-lg border border-border bg-code-bg p-4">
        <pre className="font-mono text-sm leading-relaxed whitespace-pre-wrap">
          {renderCodeWithBlanks()}
        </pre>
      </div>

      <div className="mt-4 flex items-center justify-between">
        <p className="text-sm text-muted-foreground">
          {filledCount} / {blanks.length} 빈칸 채움
        </p>
        {!isSubmitted && (
          <Button onClick={handleSubmit} disabled={filledCount < blanks.length}>
            제출하기
          </Button>
        )}
      </div>
    </div>
  );
}
