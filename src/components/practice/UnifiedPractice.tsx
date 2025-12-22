'use client';

import { useState, useEffect, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  Play,
  Send,
  CheckCircle2,
  XCircle,
  Clock,
  Lightbulb,
  Terminal,
  FileText,
  TestTube,
  ChevronLeft,
  ChevronRight,
  GripVertical,
  HelpCircle,
} from 'lucide-react';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import type { Problem, ProblemType, TestCase, Blank, PuzzleBlock } from '@/lib/types';
import { CodeEditor } from './CodeEditor';

interface TestResult {
  testCase: TestCase;
  passed: boolean;
  actual?: any;
  error?: string;
  time?: number;
}

interface UnifiedPracticeProps {
  problem: Problem;
  problemType: ProblemType;
  onSubmit: (code: string, results: TestResult[]) => void;
  onRun: (code: string) => void;
  onHintRequest: (level: number) => void;
}

export function UnifiedPractice({
  problem,
  problemType,
  onSubmit,
  onRun,
  onHintRequest,
}: UnifiedPracticeProps) {
  // 공통 상태
  const [code, setCode] = useState('');
  const [testResults, setTestResults] = useState<TestResult[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [hintsUsed, setHintsUsed] = useState(0);
  const [output, setOutput] = useState<string>('');
  const [showSidebar, setShowSidebar] = useState(true);
  const [activeTab, setActiveTab] = useState<'problem' | 'testcases'>('problem');

  // Blank 모드 상태
  const [blankAnswers, setBlankAnswers] = useState<Record<string, string>>({});
  const [blankResults, setBlankResults] = useState<Record<string, boolean>>({});

  // Puzzle 모드 상태
  const [blocks, setBlocks] = useState<PuzzleBlock[]>([]);
  const [draggedBlock, setDraggedBlock] = useState<string | null>(null);

  // 문제/타입 변경 시 초기화
  useEffect(() => {
    setTestResults([]);
    setIsSubmitted(false);
    setHintsUsed(0);
    setOutput('');
    setBlankAnswers({});
    setBlankResults({});

    if (problemType === 'blank') {
      setCode(problem.codeSnippet || '');
    } else if (problemType === 'puzzle') {
      // 블록 섞기
      const shuffled = [...(problem.puzzleBlocks || [])].sort(() => Math.random() - 0.5);
      setBlocks(shuffled);
      setCode('# 블록을 올바른 순서로 정렬하세요');
    } else if (problemType === 'implementation') {
      const signature = problem.implementationData?.functionSignature || 'def solution():';
      setCode(signature + '\n    # 여기에 코드를 작성하세요\n    pass');
    }
  }, [problem.id, problemType]);

  // 블록 순서 변경 시 코드 업데이트
  useEffect(() => {
    if (problemType === 'puzzle' && blocks.length > 0) {
      const assembledCode = blocks
        .map(b => '    '.repeat(b.indentation) + b.code)
        .join('\n');
      setCode(assembledCode);
    }
  }, [blocks, problemType]);

  // 테스트 케이스 (타입별로 다름)
  const testCases = useMemo(() => {
    if (problemType === 'implementation') {
      return problem.implementationData?.testCases || [];
    }
    // blank/puzzle은 mock 테스트 케이스
    return [
      { input: ['test'], expected: true },
    ];
  }, [problem, problemType]);

  const visibleTestCases = testCases.filter((tc) => !tc.isHidden);
  const hiddenTestCases = testCases.filter((tc) => tc.isHidden);

  // 실행 가능한 코드 조립
  const getExecutableCode = (): string => {
    if (problemType === 'blank') {
      let execCode = problem.codeSnippet || '';
      (problem.blanks || []).forEach((blank, idx) => {
        const answer = blankAnswers[blank.id] || '___';
        execCode = execCode.replace('___', answer);
      });
      return execCode;
    } else if (problemType === 'puzzle') {
      return blocks.map(b => '    '.repeat(b.indentation) + b.code).join('\n');
    }
    return code;
  };

  // 테스트 실행
  const runTests = async (isSubmit: boolean = false) => {
    setIsRunning(true);
    setOutput('');

    const executableCode = getExecutableCode();
    await new Promise((resolve) => setTimeout(resolve, 1500));

    const casesToTest = isSubmit ? testCases : visibleTestCases;
    const results: TestResult[] = [];

    for (const testCase of casesToTest) {
      const passed = Math.random() > 0.3;
      results.push({
        testCase,
        passed,
        actual: passed ? testCase.expected : 'Wrong answer',
        time: Math.floor(Math.random() * 100) + 10,
      });
    }

    setTestResults(results);
    setIsRunning(false);

    // Blank 결과 업데이트
    if (problemType === 'blank' && isSubmit) {
      const newBlankResults: Record<string, boolean> = {};
      (problem.blanks || []).forEach((blank) => {
        newBlankResults[blank.id] = blankAnswers[blank.id]?.trim() === blank.answer;
      });
      setBlankResults(newBlankResults);
    }

    if (isSubmit) {
      setIsSubmitted(true);
      onSubmit(executableCode, results);
    } else {
      onRun(executableCode);
    }

    const outputLines = results.map((r, i) => {
      const status = r.passed ? '✓ PASS' : '✗ FAIL';
      return `Test ${i + 1}: ${status} (${r.time}ms)`;
    });
    setOutput(outputLines.join('\n'));
  };

  const handleHint = () => {
    const newLevel = hintsUsed + 1;
    setHintsUsed(newLevel);
    onHintRequest(newLevel);
  };

  // 블록 드래그 핸들러
  const handleDragStart = (blockId: string) => {
    setDraggedBlock(blockId);
  };

  const handleDragOver = (e: React.DragEvent, targetId: string) => {
    e.preventDefault();
    if (!draggedBlock || draggedBlock === targetId) return;

    const dragIndex = blocks.findIndex(b => b.id === draggedBlock);
    const targetIndex = blocks.findIndex(b => b.id === targetId);

    const newBlocks = [...blocks];
    const [removed] = newBlocks.splice(dragIndex, 1);
    newBlocks.splice(targetIndex, 0, removed);
    setBlocks(newBlocks);
  };

  const handleDragEnd = () => {
    setDraggedBlock(null);
  };

  const passedCount = testResults.filter((r) => r.passed).length;
  const totalTests = testCases.length;
  const allPassed = testResults.length > 0 && passedCount === totalTests;

  // Blank 코드 렌더링
  const renderBlankCode = () => {
    const codeLines = (problem.codeSnippet || '').split('\n');
    let blankIndex = 0;
    const blanks = problem.blanks || [];

    return codeLines.map((line, lineIdx) => {
      const parts: React.ReactNode[] = [];
      let lastIndex = 0;
      let match;
      const blankPattern = /___/g;

      while ((match = blankPattern.exec(line)) !== null) {
        // 빈칸 앞 텍스트
        if (match.index > lastIndex) {
          parts.push(
            <span key={`text-${lineIdx}-${lastIndex}`} className="text-[#d4d4d4]">
              {line.slice(lastIndex, match.index)}
            </span>
          );
        }

        // 빈칸 입력
        const blank = blanks[blankIndex];
        if (blank) {
          const isCorrect = blankResults[blank.id];
          const hasResult = Object.keys(blankResults).length > 0;

          parts.push(
            <span key={`blank-${blank.id}`} className="inline-flex items-center gap-1 mx-1">
              <Input
                value={blankAnswers[blank.id] || ''}
                onChange={(e) =>
                  setBlankAnswers((prev) => ({ ...prev, [blank.id]: e.target.value }))
                }
                className={`inline-block h-7 w-24 px-2 py-0 font-mono text-sm ${
                  hasResult
                    ? isCorrect
                      ? 'border-green-500 bg-green-500/10 text-green-400'
                      : 'border-red-500 bg-red-500/10 text-red-400'
                    : 'border-primary/50 bg-[#2d2d2d] text-[#d4d4d4]'
                }`}
                placeholder="___"
                disabled={isSubmitted}
              />
              {!isSubmitted && blank.hints && blank.hints.length > 0 && (
                <Popover>
                  <PopoverTrigger asChild>
                    <button className="text-muted-foreground hover:text-primary">
                      <HelpCircle className="h-4 w-4" />
                    </button>
                  </PopoverTrigger>
                  <PopoverContent className="w-48 p-2">
                    <p className="text-xs text-muted-foreground">{blank.hints[0]}</p>
                  </PopoverContent>
                </Popover>
              )}
              {hasResult && (
                isCorrect ? (
                  <CheckCircle2 className="h-4 w-4 text-green-500" />
                ) : (
                  <XCircle className="h-4 w-4 text-red-500" />
                )
              )}
            </span>
          );
          blankIndex++;
        }

        lastIndex = match.index + 3;
      }

      // 나머지 텍스트
      if (lastIndex < line.length) {
        parts.push(
          <span key={`text-${lineIdx}-end`} className="text-[#d4d4d4]">
            {line.slice(lastIndex)}
          </span>
        );
      }

      return (
        <div key={lineIdx} className="flex">
          <span className="mr-4 w-8 select-none text-right text-[#858585]">
            {lineIdx + 1}
          </span>
          <span className="flex-1">{parts.length > 0 ? parts : line}</span>
        </div>
      );
    });
  };

  // 채워진 빈칸 수
  const filledCount = Object.values(blankAnswers).filter((a) => a?.trim()).length;
  const totalBlanks = problem.blanks?.length || 0;

  return (
    <div className="flex h-full gap-0">
      {/* Left Sidebar */}
      <AnimatePresence>
        {showSidebar && (
          <motion.div
            initial={{ width: 0, opacity: 0 }}
            animate={{ width: 320, opacity: 1 }}
            exit={{ width: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="shrink-0 flex flex-col border-r border-border bg-card overflow-hidden"
          >
            {/* Tabs */}
            <div className="flex border-b border-border">
              <button
                onClick={() => setActiveTab('problem')}
                className={`flex-1 flex items-center justify-center gap-2 px-4 py-3 text-sm font-medium transition-colors ${
                  activeTab === 'problem'
                    ? 'border-b-2 border-primary text-primary bg-primary/5'
                    : 'text-muted-foreground hover:text-foreground hover:bg-secondary/50'
                }`}
              >
                <FileText className="h-4 w-4" />
                문제
              </button>
              <button
                onClick={() => setActiveTab('testcases')}
                className={`flex-1 flex items-center justify-center gap-2 px-4 py-3 text-sm font-medium transition-colors ${
                  activeTab === 'testcases'
                    ? 'border-b-2 border-primary text-primary bg-primary/5'
                    : 'text-muted-foreground hover:text-foreground hover:bg-secondary/50'
                }`}
              >
                <TestTube className="h-4 w-4" />
                테스트
                <Badge variant="secondary" className="ml-1 text-xs">
                  {visibleTestCases.length}
                </Badge>
              </button>
            </div>

            {/* Tab Content */}
            <ScrollArea className="flex-1">
              <div className="p-4">
                {activeTab === 'problem' ? (
                  <div className="space-y-4">
                    <div>
                      <h4 className="text-sm font-semibold mb-2">문제 설명</h4>
                      <p className="text-sm text-muted-foreground whitespace-pre-wrap leading-relaxed">
                        {problem.description}
                      </p>
                    </div>

                    {problem.keyConcepts && problem.keyConcepts.length > 0 && (
                      <div className="pt-2">
                        <h4 className="text-sm font-semibold mb-2">핵심 개념</h4>
                        <div className="flex flex-wrap gap-1">
                          {problem.keyConcepts.map((concept, idx) => (
                            <Badge key={idx} variant="secondary" className="text-xs">
                              {concept}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}

                    <div className="pt-2">
                      <div className="flex items-center gap-2 text-xs text-muted-foreground">
                        <Badge variant="outline" className="text-xs">
                          공개 {visibleTestCases.length}개
                        </Badge>
                        <Badge variant="outline" className="text-xs">
                          숨김 {hiddenTestCases.length}개
                        </Badge>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {visibleTestCases.map((tc, idx) => {
                      const result = testResults.find(
                        (r) => JSON.stringify(r.testCase) === JSON.stringify(tc)
                      );
                      return (
                        <div
                          key={idx}
                          className={`rounded-lg p-3 text-xs font-mono border ${
                            result
                              ? result.passed
                                ? 'bg-green-500/10 border-green-500/30'
                                : 'bg-red-500/10 border-red-500/30'
                              : 'bg-secondary/50 border-border'
                          }`}
                        >
                          <div className="flex items-center justify-between mb-2">
                            <span className="font-semibold text-foreground">
                              Case {idx + 1}
                            </span>
                            {result && (
                              result.passed ? (
                                <div className="flex items-center gap-1 text-green-500">
                                  <CheckCircle2 className="h-3.5 w-3.5" />
                                  <span className="text-xs">PASS</span>
                                </div>
                              ) : (
                                <div className="flex items-center gap-1 text-red-500">
                                  <XCircle className="h-3.5 w-3.5" />
                                  <span className="text-xs">FAIL</span>
                                </div>
                              )
                            )}
                          </div>
                          <div className="space-y-1.5">
                            <div>
                              <span className="text-muted-foreground">Input: </span>
                              <code className="text-foreground break-all">
                                {JSON.stringify(tc.input)}
                              </code>
                            </div>
                            <div>
                              <span className="text-muted-foreground">Expected: </span>
                              <code className="text-foreground">
                                {JSON.stringify(tc.expected)}
                              </code>
                            </div>
                            {result && !result.passed && (
                              <div className="pt-1.5 border-t border-red-500/20">
                                <span className="text-red-400">Actual: </span>
                                <code className="text-red-500">
                                  {JSON.stringify(result.actual)}
                                </code>
                              </div>
                            )}
                          </div>
                        </div>
                      );
                    })}
                    {hiddenTestCases.length > 0 && (
                      <div className="rounded-lg p-3 bg-secondary/30 border border-dashed border-border text-center">
                        <p className="text-xs text-muted-foreground">
                          + {hiddenTestCases.length}개의 숨겨진 테스트 케이스
                        </p>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </ScrollArea>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Toggle Button */}
      <button
        onClick={() => setShowSidebar(!showSidebar)}
        className="shrink-0 w-6 flex items-center justify-center bg-secondary/50 hover:bg-secondary border-r border-border transition-colors"
      >
        {showSidebar ? (
          <ChevronLeft className="h-4 w-4 text-muted-foreground" />
        ) : (
          <ChevronRight className="h-4 w-4 text-muted-foreground" />
        )}
      </button>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Puzzle 모드: 블록 드래그 영역 */}
        {problemType === 'puzzle' && (
          <div className="shrink-0 border-b border-border bg-secondary/30 p-4 max-h-[50%] overflow-auto">
            <div className="flex items-center justify-between mb-3">
              <p className="text-xs text-muted-foreground">블록을 드래그하여 올바른 순서로 정렬하세요</p>
              <Badge variant="secondary" className="text-xs">
                {blocks.length}개 블록
              </Badge>
            </div>
            <div className="space-y-2">
              {blocks.map((block) => (
                <div
                  key={block.id}
                  draggable
                  onDragStart={() => handleDragStart(block.id)}
                  onDragOver={(e) => handleDragOver(e, block.id)}
                  onDragEnd={handleDragEnd}
                  className={`flex items-center gap-2 p-2 rounded border cursor-move transition-colors ${
                    draggedBlock === block.id
                      ? 'bg-primary/20 border-primary'
                      : 'bg-card border-border hover:border-primary/50'
                  }`}
                  style={{ marginLeft: block.indentation * 24 }}
                >
                  <GripVertical className="h-4 w-4 text-muted-foreground shrink-0" />
                  <code className="text-sm font-mono">{block.code}</code>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Blank 모드: 빈칸 채우기 */}
        {problemType === 'blank' && (
          <div className="flex-1 min-h-0 overflow-auto bg-[#1e1e1e] p-4">
            <div className="mb-3 flex items-center justify-between">
              <p className="text-xs text-[#808080]">빈칸을 채워 코드를 완성하세요</p>
              <Badge variant="secondary" className="text-xs">
                {filledCount} / {totalBlanks} 채움
              </Badge>
            </div>
            <pre className="font-mono text-sm leading-relaxed">
              <code>{renderBlankCode()}</code>
            </pre>
          </div>
        )}

        {/* Implementation 모드: 코드 에디터 */}
        {problemType === 'implementation' && (
          <div className="flex-1 min-h-0 overflow-hidden">
            <CodeEditor
              initialCode={code}
              language="python"
              onChange={setCode}
              readOnly={isSubmitted}
            />
          </div>
        )}

        {/* Puzzle 모드: 조립된 코드 미리보기 */}
        {problemType === 'puzzle' && (
          <div className="flex-1 min-h-0 overflow-auto bg-[#1e1e1e] p-4">
            <p className="text-xs text-[#808080] mb-2">조립된 코드:</p>
            <pre className="font-mono text-sm text-[#d4d4d4] whitespace-pre-wrap">
              {code}
            </pre>
          </div>
        )}

        {/* Output Console */}
        <div className="shrink-0 border-t border-border bg-[#1e1e1e]">
          <div className="flex items-center justify-between px-4 py-2 border-b border-[#333]">
            <div className="flex items-center gap-2">
              <Terminal className="h-4 w-4 text-[#808080]" />
              <span className="text-sm font-medium text-[#cccccc]">Output</span>
            </div>
            {testResults.length > 0 && (
              <Badge
                variant={allPassed ? 'default' : 'destructive'}
                className="text-xs"
              >
                {passedCount}/{totalTests} Passed
              </Badge>
            )}
          </div>
          <div className="h-28 overflow-y-auto p-3">
            {isRunning ? (
              <div className="flex items-center gap-2 text-sm text-[#808080]">
                <Clock className="h-4 w-4 animate-spin" />
                실행 중...
              </div>
            ) : output ? (
              <pre className="text-xs font-mono text-[#4ec9b0] whitespace-pre-wrap">
                {output}
              </pre>
            ) : (
              <p className="text-xs text-[#808080]">
                코드를 실행하면 결과가 여기에 표시됩니다.
              </p>
            )}
          </div>
        </div>

        {/* Result Banner */}
        <AnimatePresence>
          {isSubmitted && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className={`shrink-0 px-4 py-3 ${
                allPassed ? 'bg-green-500/20' : 'bg-red-500/20'
              }`}
            >
              <div className="flex items-center gap-3">
                {allPassed ? (
                  <CheckCircle2 className="h-5 w-5 text-green-500" />
                ) : (
                  <XCircle className="h-5 w-5 text-red-500" />
                )}
                <span className={`font-medium ${allPassed ? 'text-green-500' : 'text-red-500'}`}>
                  {allPassed ? '모든 테스트 통과!' : '일부 테스트 실패'}
                </span>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Actions Bar */}
        <div className="shrink-0 flex items-center justify-between px-4 py-3 border-t border-border bg-card">
          <Button
            variant="ghost"
            size="sm"
            onClick={handleHint}
            disabled={isSubmitted || hintsUsed >= 3}
            className="text-yellow-600 hover:text-yellow-500"
          >
            <Lightbulb className="mr-2 h-4 w-4" />
            힌트 ({3 - hintsUsed}회 남음)
          </Button>

          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => runTests(false)}
              disabled={isRunning || isSubmitted}
            >
              <Play className="mr-2 h-4 w-4" />
              실행
            </Button>
            <Button
              size="sm"
              onClick={() => runTests(true)}
              disabled={isRunning || isSubmitted || (problemType === 'blank' && filledCount < totalBlanks)}
            >
              <Send className="mr-2 h-4 w-4" />
              제출
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
