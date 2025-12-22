'use client';

import { useState, useEffect, useMemo, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Resizer } from '@/components/ui/resizer';
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
  Plus,
  Trash2,
  ChevronDown,
  ChevronUp,
  Copy,
  RotateCcw,
  Zap,
  Eye,
  EyeOff,
} from 'lucide-react';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@/components/ui/collapsible';
import type { ConvertedProblem, ConvertedProblemType, ConvertedTestCase, ConvertedBlank, ConvertedPuzzleBlock } from '@/lib/dataTypes';
import { checkBlankAnswers, checkPuzzleOrder } from '@/lib/problemLoader';
import { CodeEditor } from './CodeEditor';

// UI에서 사용하는 퍼즐 블록 (indentation 포함)
interface UIPuzzleBlock {
  id: string;
  code: string;
  indentation: number;
  correctOrder: number;
}

// API Base URL
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// 코드 실행 API 호출
async function executeCode(sourceCode: string, language: string, stdin: string = ''): Promise<{
  success: boolean;
  stdout: string;
  stderr: string;
  compile_output: string;
  time: string | null;
  memory: number | null;
  status: { id: number; description: string };
  error?: string;
}> {
  const response = await fetch(`${API_BASE_URL}/execute/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      source_code: sourceCode,
      language,
      stdin,
    }),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`API Error: ${response.status} - ${error}`);
  }

  return response.json();
}

interface TestResult {
  testCase: ConvertedTestCase;
  passed: boolean;
  actual?: any;
  error?: string;
  time?: number;
}

interface CustomTestCase extends ConvertedTestCase {
  id: string;
  isCustom: true;
}

interface UnifiedPracticeProps {
  problem: ConvertedProblem;
  problemType: ConvertedProblemType;
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
  const [runningTestId, setRunningTestId] = useState<string | null>(null);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [hintsUsed, setHintsUsed] = useState(0);
  const [output, setOutput] = useState<string>('');
  const [showSidebar, setShowSidebar] = useState(true);
  const [sidebarWidth, setSidebarWidth] = useState(360);
  const [activeTab, setActiveTab] = useState<'problem' | 'testcases'>('problem');

  // 테스트 케이스 UI 상태
  const [expandedTests, setExpandedTests] = useState<Set<number>>(new Set([0]));
  const [customTestCases, setCustomTestCases] = useState<CustomTestCase[]>([]);
  const [showCustomOnly, setShowCustomOnly] = useState(false);

  // 사이드바 리사이즈 핸들러
  const handleSidebarResize = useCallback((delta: number) => {
    setSidebarWidth((prev) => {
      const minWidth = 280;
      const maxWidth = 550;
      return Math.min(Math.max(prev + delta, minWidth), maxWidth);
    });
  }, []);

  // Blank 모드 상태
  const [blankAnswers, setBlankAnswers] = useState<Record<string, string>>({});
  const [blankResults, setBlankResults] = useState<Record<string, boolean>>({});

  // Puzzle 모드 상태
  const [blocks, setBlocks] = useState<UIPuzzleBlock[]>([]);
  const [draggedBlock, setDraggedBlock] = useState<string | null>(null);
  const [puzzleResults, setPuzzleResults] = useState<Record<string, boolean>>({});

  // 문제/타입 변경 시 초기화
  useEffect(() => {
    setTestResults([]);
    setIsSubmitted(false);
    setHintsUsed(0);
    setOutput('');
    setBlankAnswers({});
    setBlankResults({});
    setPuzzleResults({});
    setCustomTestCases([]);
    setExpandedTests(new Set([0]));

    if (problemType === 'blank') {
      setCode(problem.codeSnippet || '');
    } else if (problemType === 'puzzle') {
      // ConvertedPuzzleBlock을 UIPuzzleBlock으로 변환
      const uiBlocks: UIPuzzleBlock[] = (problem.puzzleBlocks || []).map(b => ({
        id: b.id,
        code: b.code,
        indentation: 0, // 기본 indentation
        correctOrder: b.correctOrder,
      }));
      // 랜덤 셔플
      const shuffled = [...uiBlocks].sort(() => Math.random() - 0.5);
      setBlocks(shuffled);
      setCode('# 블록을 올바른 순서로 정렬하세요');
    } else if (problemType === 'implementation') {
      // implementation 문제는 빈 코드로 시작
      setCode('# 여기에 코드를 작성하세요\n');
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
  const baseTestCases = useMemo((): ConvertedTestCase[] => {
    if (problemType === 'implementation') {
      return problem.testCases || [];
    }
    // blank, puzzle은 테스트 케이스가 있으면 사용, 없으면 더미
    return problem.testCases?.length ? problem.testCases : [{ input: 'test', expected: 'test' }];
  }, [problem, problemType]);

  const allTestCases = useMemo(() => {
    if (showCustomOnly) {
      return customTestCases;
    }
    return [...baseTestCases, ...customTestCases];
  }, [baseTestCases, customTestCases, showCustomOnly]);

  const visibleTestCases = allTestCases.filter((tc) => !tc.isHidden);
  const hiddenTestCases = baseTestCases.filter((tc) => tc.isHidden);

  // 테스트 케이스 토글
  const toggleTestExpand = (idx: number) => {
    setExpandedTests(prev => {
      const newSet = new Set(prev);
      if (newSet.has(idx)) {
        newSet.delete(idx);
      } else {
        newSet.add(idx);
      }
      return newSet;
    });
  };

  // 커스텀 테스트 케이스 추가
  const addCustomTestCase = () => {
    const newTestCase: CustomTestCase = {
      id: `custom-${Date.now()}`,
      input: '',
      expected: '',
      isCustom: true,
    };
    setCustomTestCases(prev => [...prev, newTestCase]);
    setExpandedTests(prev => new Set([...Array.from(prev), visibleTestCases.length]));
  };

  // 커스텀 테스트 케이스 업데이트
  const updateCustomTestCase = (id: string, field: 'input' | 'expected', value: string) => {
    setCustomTestCases(prev => prev.map(tc => {
      if (tc.id !== id) return tc;
      // 문자열로 저장
      return { ...tc, [field]: value };
    }));
  };

  // 커스텀 테스트 케이스 삭제
  const deleteCustomTestCase = (id: string) => {
    setCustomTestCases(prev => prev.filter(tc => tc.id !== id));
  };

  // 실행 가능한 코드 조립
  const getExecutableCode = (): string => {
    if (problemType === 'blank') {
      let execCode = problem.codeSnippet || '';
      (problem.blanks || []).forEach((blank) => {
        const answer = blankAnswers[blank.id] || '___';
        execCode = execCode.replace('___', answer);
      });
      return execCode;
    } else if (problemType === 'puzzle') {
      return blocks.map(b => '    '.repeat(b.indentation) + b.code).join('\n');
    }
    return code;
  };

  // 단일 테스트 실행
  const runSingleTest = async (testCase: ConvertedTestCase, idx: number) => {
    setRunningTestId(`test-${idx}`);

    const executableCode = getExecutableCode();
    const language = problem.framework || 'python';

    // input을 stdin으로 변환
    let stdin = '';
    if (Array.isArray(testCase.input)) {
      stdin = testCase.input.map(v => JSON.stringify(v)).join('\n');
    } else if (testCase.input !== undefined) {
      stdin = String(testCase.input);
    }

    try {
      const apiResult = await executeCode(executableCode, language, stdin);

      const actualOutput = apiResult.stdout?.trim() || '';
      const expectedStr = String(testCase.expected).trim();
      const passed = actualOutput === expectedStr;

      const result: TestResult = {
        testCase,
        passed,
        actual: actualOutput || apiResult.stderr || apiResult.compile_output || '(출력 없음)',
        error: apiResult.stderr || apiResult.compile_output || undefined,
        time: apiResult.time ? parseFloat(apiResult.time) * 1000 : undefined,
      };

      setTestResults(prev => {
        const existing = prev.findIndex(r => JSON.stringify(r.testCase) === JSON.stringify(testCase));
        if (existing >= 0) {
          const newResults = [...prev];
          newResults[existing] = result;
          return newResults;
        }
        return [...prev, result];
      });

      // 단일 테스트 결과도 Output에 표시
      let outputText = `[Test ${idx + 1}] ${passed ? '✓ PASS' : '✗ FAIL'}`;
      if (apiResult.stdout) outputText += `\n출력: ${apiResult.stdout}`;
      if (apiResult.stderr) outputText += `\n에러: ${apiResult.stderr}`;
      if (apiResult.time) outputText += `\n시간: ${apiResult.time}s`;
      setOutput(outputText);

      return result;

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '실행 오류';
      const result: TestResult = {
        testCase,
        passed: false,
        actual: errorMessage,
        error: errorMessage,
      };

      setTestResults(prev => [...prev, result]);
      setOutput(`[Test ${idx + 1}] ✗ ERROR\n${errorMessage}`);
      return result;

    } finally {
      setRunningTestId(null);
    }
  };

  // 테스트 실행 / 정답 체크
  const runTests = async (isSubmit: boolean = false) => {
    setIsRunning(true);
    setOutput('');

    try {
      // Blank: 코드 실행 없이 정답만 체크
      if (problemType === 'blank') {
        const userAnswers = (problem.blanks || []).map(blank => blankAnswers[blank.id] || '');
        const { correct, results } = checkBlankAnswers(problem, userAnswers);

        const newBlankResults: Record<string, boolean> = {};
        (problem.blanks || []).forEach((blank, idx) => {
          newBlankResults[blank.id] = results[idx] || false;
        });
        setBlankResults(newBlankResults);

        const correctCount = results.filter(r => r).length;
        const totalCount = results.length;

        if (isSubmit) {
          setOutput(correct
            ? `✓ 정답입니다! (${correctCount}/${totalCount})`
            : `✗ 오답입니다. (${correctCount}/${totalCount}) - 다시 시도해주세요.`
          );
          const testResults: TestResult[] = [{
            testCase: { input: '', expected: 'correct', isHidden: false },
            passed: correct,
            actual: correct ? 'correct' : 'incorrect',
          }];
          onSubmit(getExecutableCode(), testResults);
          // 정답일 때만 수정 불가 상태로 전환
          if (correct) {
            setIsSubmitted(true);
          }
        } else {
          // 실행 버튼 - 현재 상태만 보여줌
          setOutput(`현재 입력 상태: ${correctCount}/${totalCount} 정답`);
        }
        return;
      }

      // Puzzle: 코드 실행 없이 순서만 체크
      if (problemType === 'puzzle') {
        const userOrder = blocks.map(b => b.id);
        const { correct, results } = checkPuzzleOrder(problem, userOrder);

        // 각 블록별 결과 저장
        const newPuzzleResults: Record<string, boolean> = {};
        blocks.forEach((block, idx) => {
          newPuzzleResults[block.id] = results[idx] || false;
        });
        setPuzzleResults(newPuzzleResults);

        const correctCount = results.filter(r => r).length;

        if (isSubmit) {
          setOutput(correct
            ? '✓ 정답입니다! 올바른 순서입니다.'
            : `✗ 오답입니다. (${correctCount}/${blocks.length}) - 순서를 다시 확인해주세요.`
          );
          const testResults: TestResult[] = [{
            testCase: { input: '', expected: 'correct order', isHidden: false },
            passed: correct,
            actual: correct ? 'correct order' : 'wrong order',
          }];
          onSubmit(getExecutableCode(), testResults);
          // 정답일 때만 수정 불가 상태로 전환
          if (correct) {
            setIsSubmitted(true);
          }
        } else {
          setOutput('블록을 올바른 순서로 정렬하고 제출해주세요.');
        }
        return;
      }

      // Implementation: 실제 코드 실행
      const executableCode = getExecutableCode();
      const language = problem.framework || 'python';

      const result = await executeCode(executableCode, language, '');

      let outputText = '';

      if (result.compile_output) {
        outputText += `[Compile]\n${result.compile_output}\n\n`;
      }

      if (result.stderr) {
        outputText += `[Error]\n${result.stderr}\n\n`;
      }

      if (result.stdout) {
        outputText += `[Output]\n${result.stdout}`;
      }

      if (!result.stdout && !result.stderr && !result.compile_output) {
        outputText = '(실행 완료 - 출력 없음)';
      }

      if (result.time || result.memory) {
        outputText += `\n\n--- 실행 정보 ---`;
        if (result.time) outputText += `\n시간: ${result.time}s`;
        if (result.memory) outputText += `\n메모리: ${Math.round(result.memory / 1024)}MB`;
        outputText += `\n상태: ${result.status.description}`;
      }

      setOutput(outputText);

      if (isSubmit) {
        onSubmit(executableCode, []);
        setIsSubmitted(true);
      } else {
        onRun(executableCode);
      }

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '알 수 없는 오류';
      setOutput(`[오류]\n${errorMessage}`);
    } finally {
      setIsRunning(false);
    }
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

  // 결과 리셋
  const resetResults = () => {
    setTestResults([]);
    setOutput('');
  };

  const passedCount = testResults.filter((r) => r.passed).length;
  const totalTests = baseTestCases.length;
  const testedCount = testResults.length;
  const allPassed = testedCount > 0 && passedCount === testedCount;

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
        if (match.index > lastIndex) {
          parts.push(
            <span key={`text-${lineIdx}-${lastIndex}`} className="text-[#d4d4d4]">
              {line.slice(lastIndex, match.index)}
            </span>
          );
        }

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
              {/* 힌트 버튼 - problem.keyConcepts 사용 */}
              {!isSubmitted && problem.keyConcepts?.length > 0 && (
                <Popover>
                  <PopoverTrigger asChild>
                    <button className="text-muted-foreground hover:text-primary">
                      <HelpCircle className="h-4 w-4" />
                    </button>
                  </PopoverTrigger>
                  <PopoverContent className="w-48 p-2">
                    <p className="text-xs text-muted-foreground">{problem.keyConcepts[0]}</p>
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

  const filledCount = Object.values(blankAnswers).filter((a) => a?.trim()).length;
  const totalBlanks = problem.blanks?.length || 0;

  // 테스트 케이스 카드 렌더링
  const renderTestCaseCard = (tc: ConvertedTestCase | CustomTestCase, idx: number) => {
    const result = testResults.find(
      (r) => JSON.stringify(r.testCase) === JSON.stringify(tc)
    );
    const isExpanded = expandedTests.has(idx);
    const isRunningThis = runningTestId === `test-${idx}`;
    const isCustom = 'isCustom' in tc && tc.isCustom;
    const customTc = isCustom ? (tc as CustomTestCase) : null;

    return (
      <Collapsible
        key={customTc?.id || idx}
        open={isExpanded}
        onOpenChange={() => toggleTestExpand(idx)}
      >
        <div
          className={`rounded-lg border transition-all ${
            result
              ? result.passed
                ? 'bg-green-500/5 border-green-500/30'
                : 'bg-red-500/5 border-red-500/30'
              : 'bg-card border-border hover:border-primary/30'
          }`}
        >
          {/* Header */}
          <CollapsibleTrigger asChild>
            <div className="flex items-center justify-between p-3 cursor-pointer group">
              <div className="flex items-center gap-2">
                {isExpanded ? (
                  <ChevronDown className="h-4 w-4 text-muted-foreground" />
                ) : (
                  <ChevronRight className="h-4 w-4 text-muted-foreground" />
                )}
                <span className="text-sm font-medium">
                  {isCustom ? (
                    <span className="text-primary">Custom {idx - baseTestCases.filter(t => !t.isHidden).length + 1}</span>
                  ) : (
                    `Case ${idx + 1}`
                  )}
                </span>
                {isCustom && (
                  <Badge variant="outline" className="text-[10px] px-1.5 py-0">
                    사용자
                  </Badge>
                )}
              </div>
              <div className="flex items-center gap-2">
                {isRunningThis && (
                  <Clock className="h-3.5 w-3.5 text-primary animate-spin" />
                )}
                {result && !isRunningThis && (
                  <>
                    {result.passed ? (
                      <div className="flex items-center gap-1.5 text-green-500">
                        <CheckCircle2 className="h-4 w-4" />
                        <span className="text-xs font-medium">{result.time}ms</span>
                      </div>
                    ) : (
                      <div className="flex items-center gap-1.5 text-red-500">
                        <XCircle className="h-4 w-4" />
                        <span className="text-xs font-medium">{result.time}ms</span>
                      </div>
                    )}
                  </>
                )}
                {!result && !isRunningThis && (
                  <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-6 w-6"
                      onClick={(e) => {
                        e.stopPropagation();
                        runSingleTest(tc, idx);
                      }}
                      disabled={isRunning || isSubmitted}
                    >
                      <Zap className="h-3.5 w-3.5" />
                    </Button>
                  </div>
                )}
              </div>
            </div>
          </CollapsibleTrigger>

          {/* Content */}
          <CollapsibleContent>
            <div className="px-3 pb-3 pt-0 space-y-2">
              {/* Input */}
              <div className="rounded-md bg-secondary/50 p-2">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-[10px] uppercase tracking-wider text-muted-foreground font-medium">
                    Input
                  </span>
                  {!isCustom && (
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-5 w-5"
                      onClick={() => navigator.clipboard.writeText(JSON.stringify(tc.input))}
                    >
                      <Copy className="h-3 w-3" />
                    </Button>
                  )}
                </div>
                {isCustom ? (
                  <Input
                    value={JSON.stringify(customTc!.input)}
                    onChange={(e) => updateCustomTestCase(customTc!.id, 'input', e.target.value)}
                    className="h-7 text-xs font-mono bg-background"
                    placeholder='예: [[1,2,3], 5]'
                  />
                ) : (
                  <code className="text-xs font-mono text-foreground block break-all">
                    {JSON.stringify(tc.input)}
                  </code>
                )}
              </div>

              {/* Expected */}
              <div className="rounded-md bg-secondary/50 p-2">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-[10px] uppercase tracking-wider text-muted-foreground font-medium">
                    Expected
                  </span>
                </div>
                {isCustom ? (
                  <Input
                    value={JSON.stringify(customTc!.expected)}
                    onChange={(e) => updateCustomTestCase(customTc!.id, 'expected', e.target.value)}
                    className="h-7 text-xs font-mono bg-background"
                    placeholder='예: [0, 1]'
                  />
                ) : (
                  <code className="text-xs font-mono text-foreground block">
                    {JSON.stringify(tc.expected)}
                  </code>
                )}
              </div>

              {/* Actual (only if result exists and failed) */}
              {result && !result.passed && (
                <div className="rounded-md bg-red-500/10 border border-red-500/20 p-2">
                  <span className="text-[10px] uppercase tracking-wider text-red-400 font-medium block mb-1">
                    Actual
                  </span>
                  <code className="text-xs font-mono text-red-500 block">
                    {JSON.stringify(result.actual)}
                  </code>
                  {result.error && (
                    <p className="text-xs text-red-400 mt-1.5 whitespace-pre-wrap">
                      {result.error}
                    </p>
                  )}
                </div>
              )}

              {/* Actions for custom test case */}
              {isCustom && (
                <div className="flex justify-between pt-1">
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-7 text-xs text-red-500 hover:text-red-400 hover:bg-red-500/10"
                    onClick={() => deleteCustomTestCase(customTc!.id)}
                  >
                    <Trash2 className="h-3.5 w-3.5 mr-1" />
                    삭제
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    className="h-7 text-xs"
                    onClick={() => runSingleTest(tc, idx)}
                    disabled={isRunning || isSubmitted}
                  >
                    <Play className="h-3.5 w-3.5 mr-1" />
                    실행
                  </Button>
                </div>
              )}
            </div>
          </CollapsibleContent>
        </div>
      </Collapsible>
    );
  };

  return (
    <div className="flex h-full gap-0">
      {/* Left Sidebar */}
      <AnimatePresence>
        {showSidebar && (
          <motion.div
            initial={{ width: 0, opacity: 0 }}
            animate={{ width: sidebarWidth, opacity: 1 }}
            exit={{ width: 0, opacity: 0 }}
            transition={{ duration: 0.15 }}
            className="shrink-0 flex flex-col bg-card overflow-hidden"
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
                {testedCount > 0 && (
                  <Badge
                    variant={allPassed ? 'default' : 'destructive'}
                    className="ml-1 text-[10px] px-1.5"
                  >
                    {passedCount}/{testedCount}
                  </Badge>
                )}
              </button>
              <button
                onClick={() => setShowSidebar(false)}
                className="shrink-0 px-2 text-muted-foreground hover:text-foreground hover:bg-secondary/50 transition-colors"
                title="사이드바 닫기"
              >
                <ChevronLeft className="h-4 w-4" />
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
                          공개 {visibleTestCases.length - customTestCases.length}개
                        </Badge>
                        <Badge variant="outline" className="text-xs">
                          숨김 {hiddenTestCases.length}개
                        </Badge>
                        {customTestCases.length > 0 && (
                          <Badge variant="outline" className="text-xs text-primary border-primary/50">
                            커스텀 {customTestCases.length}개
                          </Badge>
                        )}
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {/* Test Cases Header */}
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-7 text-xs gap-1.5"
                          onClick={() => setShowCustomOnly(!showCustomOnly)}
                        >
                          {showCustomOnly ? <Eye className="h-3.5 w-3.5" /> : <EyeOff className="h-3.5 w-3.5" />}
                          {showCustomOnly ? '전체 보기' : '커스텀만'}
                        </Button>
                        {testResults.length > 0 && (
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-7 text-xs gap-1.5"
                            onClick={resetResults}
                          >
                            <RotateCcw className="h-3.5 w-3.5" />
                            초기화
                          </Button>
                        )}
                      </div>
                      <Button
                        variant="outline"
                        size="sm"
                        className="h-7 text-xs gap-1.5"
                        onClick={addCustomTestCase}
                      >
                        <Plus className="h-3.5 w-3.5" />
                        추가
                      </Button>
                    </div>

                    {/* Test Cases List */}
                    <div className="space-y-2">
                      {visibleTestCases.map((tc, idx) => renderTestCaseCard(tc, idx))}
                    </div>

                    {/* Hidden Test Cases */}
                    {hiddenTestCases.length > 0 && !showCustomOnly && (
                      <div className="rounded-lg p-3 bg-secondary/30 border border-dashed border-border text-center">
                        <p className="text-xs text-muted-foreground">
                          + {hiddenTestCases.length}개의 숨겨진 테스트 (제출 시 실행)
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

      {/* Resize Handle / Toggle Button */}
      {showSidebar ? (
        <Resizer
          direction="horizontal"
          onResize={handleSidebarResize}
          className="bg-border hover:bg-primary/50"
        />
      ) : (
        <button
          onClick={() => setShowSidebar(true)}
          className="shrink-0 w-6 flex items-center justify-center bg-secondary/50 hover:bg-secondary border-r border-border transition-colors"
        >
          <ChevronRight className="h-4 w-4 text-muted-foreground" />
        </button>
      )}

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
              {blocks.map((block) => {
                const hasResult = Object.keys(puzzleResults).length > 0;
                const isCorrect = puzzleResults[block.id];

                return (
                  <div
                    key={block.id}
                    draggable={!isSubmitted}
                    onDragStart={() => !isSubmitted && handleDragStart(block.id)}
                    onDragOver={(e) => !isSubmitted && handleDragOver(e, block.id)}
                    onDragEnd={handleDragEnd}
                    className={`flex items-center gap-2 p-2 rounded border transition-all ${
                      isSubmitted
                        ? 'cursor-default'
                        : 'cursor-move'
                    } ${
                      draggedBlock === block.id
                        ? 'bg-primary/20 border-primary'
                        : hasResult
                          ? isCorrect
                            ? 'bg-green-500/10 border-green-500/50'
                            : 'bg-red-500/10 border-red-500/50 animate-pulse'
                          : 'bg-card border-border hover:border-primary/50'
                    }`}
                    style={{ marginLeft: block.indentation * 24 }}
                  >
                    <GripVertical className={`h-4 w-4 shrink-0 ${
                      hasResult
                        ? isCorrect
                          ? 'text-green-500'
                          : 'text-red-500'
                        : 'text-muted-foreground'
                    }`} />
                    <code className={`text-sm font-mono flex-1 ${
                      hasResult
                        ? isCorrect
                          ? 'text-green-400'
                          : 'text-red-400'
                        : ''
                    }`}>{block.code}</code>
                    {hasResult && (
                      isCorrect ? (
                        <CheckCircle2 className="h-4 w-4 text-green-500 shrink-0" />
                      ) : (
                        <XCircle className="h-4 w-4 text-red-500 shrink-0" />
                      )
                    )}
                  </div>
                );
              })}
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

        {/* Output Console - implementation에서만 표시 */}
        {problemType === 'implementation' && (
          <div className="shrink-0 border-t border-border bg-[#1e1e1e]">
            <div className="flex items-center justify-between px-4 py-2 border-b border-[#333]">
              <div className="flex items-center gap-2">
                <Terminal className="h-4 w-4 text-[#808080]" />
                <span className="text-sm font-medium text-[#cccccc]">Output</span>
              </div>
              {testedCount > 0 && (
                <Badge
                  variant={allPassed ? 'default' : 'destructive'}
                  className="text-xs"
                >
                  {passedCount}/{testedCount} Passed
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
        )}

        {/* Result Banner - 문제 타입별 결과 표시 */}
        {/* blank/puzzle: 결과가 있을 때 표시, implementation: 제출 후 표시 */}
        <AnimatePresence>
          {((problemType === 'blank' && Object.keys(blankResults).length > 0) ||
            (problemType === 'puzzle' && Object.keys(puzzleResults).length > 0) ||
            (problemType === 'implementation' && isSubmitted)) && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className={`shrink-0 px-4 py-3 ${
                problemType === 'blank'
                  ? Object.values(blankResults).every(r => r)
                    ? 'bg-green-500/20'
                    : 'bg-red-500/20'
                  : problemType === 'puzzle'
                    ? Object.values(puzzleResults).every(r => r)
                      ? 'bg-green-500/20'
                      : 'bg-red-500/20'
                    : allPassed
                      ? 'bg-green-500/20'
                      : 'bg-red-500/20'
              }`}
            >
              <div className="flex items-center gap-3">
                {/* Blank 결과 */}
                {problemType === 'blank' && (
                  <>
                    {Object.values(blankResults).every(r => r) ? (
                      <CheckCircle2 className="h-5 w-5 text-green-500" />
                    ) : (
                      <XCircle className="h-5 w-5 text-red-500" />
                    )}
                    <div className="flex flex-col">
                      <span className={`font-medium ${
                        Object.values(blankResults).every(r => r) ? 'text-green-500' : 'text-red-500'
                      }`}>
                        {Object.values(blankResults).every(r => r)
                          ? '정답입니다!'
                          : '오답입니다. 다시 확인해주세요.'
                        }
                      </span>
                      <span className="text-xs text-muted-foreground">
                        {Object.values(blankResults).filter(r => r).length} / {Object.values(blankResults).length} 빈칸 정답
                      </span>
                    </div>
                  </>
                )}

                {/* Puzzle 결과 */}
                {problemType === 'puzzle' && (
                  <>
                    {Object.values(puzzleResults).every(r => r) ? (
                      <CheckCircle2 className="h-5 w-5 text-green-500" />
                    ) : (
                      <XCircle className="h-5 w-5 text-red-500" />
                    )}
                    <div className="flex flex-col">
                      <span className={`font-medium ${
                        Object.values(puzzleResults).every(r => r) ? 'text-green-500' : 'text-red-500'
                      }`}>
                        {Object.values(puzzleResults).every(r => r)
                          ? '정답입니다! 올바른 순서입니다.'
                          : '오답입니다. 순서를 다시 확인해주세요.'
                        }
                      </span>
                      <span className="text-xs text-muted-foreground">
                        {Object.values(puzzleResults).filter(r => r).length} / {blocks.length} 블록 정답
                      </span>
                    </div>
                  </>
                )}

                {/* Implementation 결과 */}
                {problemType === 'implementation' && (
                  <>
                    {allPassed ? (
                      <CheckCircle2 className="h-5 w-5 text-green-500" />
                    ) : (
                      <XCircle className="h-5 w-5 text-red-500" />
                    )}
                    <span className={`font-medium ${allPassed ? 'text-green-500' : 'text-red-500'}`}>
                      {allPassed ? '모든 테스트 통과!' : '일부 테스트 실패'}
                    </span>
                  </>
                )}
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
            {/* 실행 버튼 - implementation에서만 표시 */}
            {problemType === 'implementation' && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => runTests(false)}
                disabled={isRunning || isSubmitted}
              >
                <Play className="mr-2 h-4 w-4" />
                실행
              </Button>
            )}
            <Button
              size="sm"
              onClick={() => runTests(true)}
              disabled={isRunning || isSubmitted || (problemType === 'blank' && filledCount < totalBlanks)}
            >
              {problemType === 'implementation' ? (
                <>
                  <Send className="mr-2 h-4 w-4" />
                  제출
                </>
              ) : (
                <>
                  <CheckCircle2 className="mr-2 h-4 w-4" />
                  정답 확인
                </>
              )}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
