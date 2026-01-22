'use client';

import { useState, useEffect, useMemo, useCallback } from 'react';
import dynamic from 'next/dynamic';
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
  Lock,
  Languages,
  Loader2,
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
import { checkBlankAnswers, checkPuzzleOrder } from '@/lib/problemChecker';

// CodeEditor 동적 임포트 (Monaco Editor 번들 분리 - 초기 로딩 성능 향상)
const CodeEditor = dynamic(
  () => import('./CodeEditor').then(mod => mod.CodeEditor),
  {
    ssr: false,
    loading: () => (
      <div className="h-full flex items-center justify-center bg-[#1e1e1e]">
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    ),
  }
);

// GuidedTutorChat 제거됨 - 1대1 대화형은 기존 PracticeChatPanel에서 처리
import { translateText, LANGUAGE_LABELS, type LanguageCode } from '@/lib/api/translate';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

import { preprocessLatex } from '@/lib/utils';

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
  testId: string;  // 'base-0', 'base-1' 또는 CustomTestCase의 id
  passed: boolean | null;  // null = 출력 확인용 (expected 없음)
  actual?: string;
  error?: string;
  time?: number;
}

// 테스트 케이스 ID 생성 (base: 'base-{idx}', custom: 고유 id)
const getTestId = (tc: ConvertedTestCase | CustomTestCase, idx: number): string => {
  if ('isCustom' in tc && tc.isCustom) {
    return (tc as CustomTestCase).id;
  }
  return `base-${idx}`;
};

// stdin 포맷팅 (공통)
const formatStdin = (input: any): string => {
  if (Array.isArray(input)) {
    return input.map(v => JSON.stringify(v)).join('\n');
  }
  return input !== undefined ? String(input) : '';
};

// 테스트 결과 생성 (공통)
const createTestResult = (
  testId: string,
  apiResult: { stdout?: string; stderr?: string; compile_output?: string; time?: string },
  expected: any
): TestResult => {
  const actualOutput = apiResult.stdout?.trim() || '';
  const expectedStr = expected !== undefined && expected !== ''
    ? String(expected).trim()
    : null;
  const passed = expectedStr === null ? null : actualOutput === expectedStr;

  return {
    testId,
    passed,
    actual: actualOutput || apiResult.stderr || apiResult.compile_output || '(출력 없음)',
    error: apiResult.stderr || apiResult.compile_output || undefined,
    time: apiResult.time ? parseFloat(apiResult.time) * 1000 : undefined,
  };
};

interface CustomTestCase extends ConvertedTestCase {
  id: string;
  isCustom: true;
}

interface UnifiedPracticeProps {
  problem: ConvertedProblem;
  problemType: ConvertedProblemType;
  onSubmit: (code: string, results: TestResult[], hintsUsed?: number) => void;
  onRun: (code: string) => void;
  onHintRequest: (level: number) => void;
  onGiveUp?: () => void;  // 포기하기
  attemptId?: string;  // attempt tracking for hint recording
  onCodeChange?: (code: string) => void;  // 코드 변경 콜백 (guided 모드 튜터에게 전달용)
  onBlankHintUsed?: (index: number) => void;  // 빈칸/퍼즐 힌트 사용 시 콜백 (채팅 도움용)
}

export function UnifiedPractice({
  problem,
  problemType,
  onSubmit,
  onRun,
  onHintRequest,
  onGiveUp,
  attemptId,
  onCodeChange,
  onBlankHintUsed,
}: UnifiedPracticeProps) {
  // 공통 상태
  const [code, setCode] = useState('');
  const [testResults, setTestResults] = useState<Record<string, TestResult>>({});
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

  // 코드 변경 시 콜백 호출 (guided 모드 튜터에게 현재 코드 전달용)
  useEffect(() => {
    if (onCodeChange && code) {
      onCodeChange(code);
    }
  }, [code, onCodeChange]);

  // Guided 모드: 별도 채팅 패널 제거됨 - PracticeChatPanel에서 통합 처리

  // Blank 모드 상태
  const [blankAnswers, setBlankAnswers] = useState<Record<string, string>>({});
  const [blankResults, setBlankResults] = useState<Record<string, boolean>>({});

  // Blank 힌트 상태 (빈칸별 역할 설명, 레벨 없음)
  const [blankHints, setBlankHints] = useState<Record<number, string>>({});  // {blankIndex: hintContent}
  const [blankHintLoading, setBlankHintLoading] = useState<number | null>(null);  // 로딩 중인 빈칸 인덱스
  const [blankHintsUsedCount, setBlankHintsUsedCount] = useState<number>(0);  // 사용한 힌트 횟수 (제한 없음, 기록용)

  // Puzzle 모드 상태
  const [blocks, setBlocks] = useState<UIPuzzleBlock[]>([]);
  const [draggedBlock, setDraggedBlock] = useState<string | null>(null);
  const [puzzleResults, setPuzzleResults] = useState<Record<string, boolean>>({});
  const [showPuzzlePulse, setShowPuzzlePulse] = useState(false);

  // Puzzle 힌트 상태 (순차적 힌트 - 틀린 블록 순서대로)
  const [puzzleHintMessages, setPuzzleHintMessages] = useState<string[]>([]);  // 힌트 메시지 목록
  const [puzzleHintLoading, setPuzzleHintLoading] = useState(false);
  const [puzzleHintsUsedCount, setPuzzleHintsUsedCount] = useState<number>(0);  // 사용한 힌트 횟수 (기록용)

  // 번역 상태
  const [targetLanguage, setTargetLanguage] = useState<LanguageCode>('ko');
  const [translatedDescription, setTranslatedDescription] = useState<string | null>(null);
  const [isTranslating, setIsTranslating] = useState(false);
  const [showOriginal, setShowOriginal] = useState(true);

  // 오답 애니메이션: 결과 나온 후 2초만 표시
  useEffect(() => {
    if (Object.keys(puzzleResults).length > 0) {
      setShowPuzzlePulse(true);
      const timer = setTimeout(() => setShowPuzzlePulse(false), 2000);
      return () => clearTimeout(timer);
    }
  }, [puzzleResults]);

  // 문제/타입 변경 시 초기화
  useEffect(() => {
    setTestResults({});
    setIsSubmitted(false);
    setHintsUsed(0);
    setOutput('');
    setBlankAnswers({});
    setBlankResults({});
    setPuzzleResults({});
    setCustomTestCases([]);
    setExpandedTests(new Set([0]));
    // 번역 상태 초기화
    setTranslatedDescription(null);
    setShowOriginal(true);
    // 힌트 상태 초기화
    setBlankHints({});
    setBlankHintLoading(null);
    setBlankHintsUsedCount(0);  // 힌트 사용 횟수 리셋
    setPuzzleHintMessages([]);
    setPuzzleHintLoading(false);
    setPuzzleHintsUsedCount(0);  // 퍼즐 힌트 사용 횟수 리셋

    if (problemType === 'blank') {
      const snippet = problem.codeSnippet || '';
      const blankCount = problem.blanks?.length || 0;
      // 빈칸 패턴 검증 - _N_ 또는 ___ 패턴이 있는지 확인
      const patternCount = (snippet.match(/_\d+_|___/g) || []).length;

      if (blankCount > 0 && patternCount === 0) {
        console.warn('[UnifiedPractice] Warning: blanks exist but no patterns found in codeSnippet');
        console.warn(`  - blanks.length: ${blankCount}`);
        console.warn(`  - codeSnippet (first 200 chars): ${snippet.substring(0, 200)}`);
      }

      setCode(snippet);
    } else if (problemType === 'puzzle') {
      // ConvertedPuzzleBlock을 UIPuzzleBlock으로 변환
      const uiBlocks: UIPuzzleBlock[] = (problem.puzzleBlocks || []).map(b => ({
        id: b.id,
        code: b.code,
        indentation: b.indentation || 0, // 블록의 들여쓰기 레벨 사용
        correctOrder: b.correctOrder,
      }));
      // 랜덤 셔플
      const shuffled = [...uiBlocks].sort(() => Math.random() - 0.5);
      setBlocks(shuffled);
      setCode('# 블록을 올바른 순서로 정렬하세요');
    } else if (problemType === 'implementation') {
      // implementation 문제는 빈 코드로 시작
      setCode('# 여기에 코드를 작성하세요\n');
      // implementation 모드는 테스트 탭으로 자동 전환
      setActiveTab('testcases');
    } else if (problemType === 'guided') {
      // guided 문제는 starter_code(codeSnippet)가 있으면 사용, 없으면 빈 코드
      const starterCode = problem.codeSnippet || '# 여기에 코드를 작성하세요\n';
      setCode(starterCode);
      // guided 모드도 테스트 탭으로 자동 전환
      setActiveTab('testcases');
    }
  }, [problem.id, problemType, problem.codeSnippet]);

  // 블록 순서 변경 시 코드 업데이트 (baseIndentation 적용)
  useEffect(() => {
    if (problemType === 'puzzle' && blocks.length > 0) {
      // baseIndentation은 fixed_start 기준으로 계산됨
      const fixedStartLines = problem.fixedStart?.split('\n') || [];
      const lastLine = fixedStartLines[fixedStartLines.length - 1] || '';
      const leadingSpaces = lastLine.match(/^(\s*)/)?.[1].length || 0;
      let computedBaseIndent = Math.floor(leadingSpaces / 4);
      if (lastLine.trimEnd().endsWith(':')) {
        computedBaseIndent += 1;
      }

      const assembledCode = blocks
        .map(b => '    '.repeat(computedBaseIndent + (b.indentation || 0)) + b.code)
        .join('\n');
      setCode(assembledCode);
    }
  }, [blocks, problemType, problem.fixedStart]);

  // fixed_start의 마지막 줄에서 기본 들여쓰기 레벨 계산
  const baseIndentation = useMemo((): number => {
    if (!problem.fixedStart) return 0;

    const lines = problem.fixedStart.split('\n');
    const lastLine = lines[lines.length - 1];

    // 마지막 줄의 들여쓰기 계산 (4칸 = 1레벨)
    const leadingSpaces = lastLine.match(/^(\s*)/)?.[1].length || 0;
    let baseIndent = Math.floor(leadingSpaces / 4);

    // 마지막 줄이 ':'로 끝나면 (함수/클래스/조건문/반복문), 다음 블록은 +1 레벨
    if (lastLine.trimEnd().endsWith(':')) {
      baseIndent += 1;
    }

    return baseIndent;
  }, [problem.fixedStart]);

  // 테스트 케이스 (타입별로 다름)
  const baseTestCases = useMemo((): ConvertedTestCase[] => {
    // 테스트 케이스가 있으면 사용
    if (problem.testCases && problem.testCases.length > 0) {
      return problem.testCases;
    }
    // implementation/guided 타입은 테스트 케이스가 없으면 빈 배열
    if (problemType === 'implementation' || problemType === 'guided') {
      return [];
    }
    // blank, puzzle은 테스트 케이스가 없으면 빈 배열 (더미 데이터 제거)
    return [];
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
      const blanks = problem.blanks || [];

      // _N_ 패턴을 사용자 답변으로 교체
      blanks.forEach((blank, idx) => {
        const answer = blankAnswers[blank.id] || blank.answer || '';
        // _N_ 패턴 교체 (예: _0_, _1_, _2_)
        const pattern = new RegExp(`_${idx}_`, 'g');
        execCode = execCode.replace(pattern, answer);
      });

      // 레거시 ___ 패턴도 순차적으로 교체 (혹시 남아있는 경우)
      let seqIdx = 0;
      execCode = execCode.replace(/___/g, () => {
        const blank = blanks[seqIdx];
        seqIdx++;
        return blank ? (blankAnswers[blank.id] || blank.answer || '') : '___';
      });

      return execCode;
    } else if (problemType === 'puzzle') {
      return blocks.map(b => {
        // baseIndentation + 블록의 상대적 indentation = 최종 들여쓰기
        const relativeIndent = b.indentation || 0;
        const totalIndent = baseIndentation + relativeIndent;
        return '    '.repeat(totalIndent) + b.code;
      }).join('\n');
    }
    return code;
  };

  // 단일 테스트 실행
  const runSingleTest = async (testCase: ConvertedTestCase, idx: number) => {
    const testId = getTestId(testCase, idx);
    setRunningTestId(testId);

    const executableCode = getExecutableCode();
    const language = problem.framework || 'python';
    const stdin = formatStdin(testCase.input);

    try {
      const apiResult = await executeCode(executableCode, language, stdin);
      const result = createTestResult(testId, apiResult, testCase.expected);

      setTestResults(prev => ({ ...prev, [testId]: result }));

      // 단일 테스트 결과도 Output에 표시
      let outputText = result.passed === null
        ? `[Test ${idx + 1}] 실행 완료`
        : `[Test ${idx + 1}] ${result.passed ? '✓ PASS' : '✗ FAIL'}`;
      if (apiResult.stdout) outputText += `\n출력: ${apiResult.stdout}`;
      if (apiResult.stderr) outputText += `\n에러: ${apiResult.stderr}`;
      if (apiResult.time) outputText += `\n시간: ${apiResult.time}s`;
      setOutput(outputText);

      return result;

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '실행 오류';
      const result: TestResult = {
        testId,
        passed: false,
        actual: errorMessage,
        error: errorMessage,
      };

      setTestResults(prev => ({ ...prev, [testId]: result }));
      setOutput(`[Test ${idx + 1}] ✗ ERROR\n${errorMessage}`);
      return result;

    } finally {
      setRunningTestId(null);
    }
  };

  // 모든 테스트 케이스 실행 (implementation용) - 결과 반환
  // forSubmit=true: 공식 테스트케이스(baseTestCases)만 실행 (최대 3개)
  // forSubmit=false: 화면에 보이는 테스트케이스(visibleTestCases) 실행 (custom 포함)
  const runAllTestCases = async (forSubmit: boolean = false): Promise<Record<string, TestResult>> => {
    // 제출 시: 공식 테스트케이스 최대 3개만, 일반 실행 시: visible 테스트케이스 (custom 포함)
    const targetTestCases = forSubmit ? baseTestCases.slice(0, 3) : visibleTestCases;

    if (targetTestCases.length === 0) {
      setOutput(forSubmit
        ? '실행할 공식 테스트 케이스가 없습니다.'
        : '실행할 테스트 케이스가 없습니다.\n테스트 케이스를 추가해주세요.');
      return {};
    }

    setIsRunning(true);
    // 제출 시에는 기존 결과 유지 (UI에 custom 결과도 보여야 함), 일반 실행 시에만 초기화
    if (!forSubmit) {
      setTestResults({});
    }
    setOutput(forSubmit ? '제출 중... 공식 테스트 실행' : '테스트 실행 중...');

    const results: Record<string, TestResult> = {};
    let passedCount = 0;
    let judgedCount = 0;  // expected가 있는 테스트만 카운트

    const executableCode = getExecutableCode();
    const language = problem.framework || 'python';

    for (let idx = 0; idx < targetTestCases.length; idx++) {
      const tc = targetTestCases[idx];
      // 제출 시에는 base 테스트케이스 인덱스 그대로 사용
      const testId = forSubmit ? `base-${idx}` : getTestId(tc, idx);
      setRunningTestId(testId);

      const stdin = formatStdin(tc.input);

      try {
        const apiResult = await executeCode(executableCode, language, stdin);
        const result = createTestResult(testId, apiResult, tc.expected);

        if (result.passed === true) passedCount++;
        if (result.passed !== null) judgedCount++;

        results[testId] = result;
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : '실행 오류';
        results[testId] = {
          testId,
          passed: false,
          actual: errorMessage,
          error: errorMessage,
        };
        judgedCount++;
      }
    }

    setRunningTestId(null);
    // 제출 시에는 base 결과만 업데이트, 기존 custom 결과 유지
    if (forSubmit) {
      setTestResults(prev => ({ ...prev, ...results }));
    } else {
      setTestResults(results);
    }
    setIsRunning(false);

    // Output에 요약 표시
    const allPassed = judgedCount > 0 && passedCount === judgedCount;
    const testLabel = forSubmit ? '공식 테스트' : '테스트';
    const summary = forSubmit
      ? (allPassed
          ? `✓ 제출 완료! 모든 ${testLabel} 통과 (${passedCount}/${judgedCount})`
          : `제출 완료 (${passedCount}/${judgedCount} 통과)`)
      : (judgedCount > 0
          ? `${testLabel} 완료: ${passedCount}/${judgedCount} 통과`
          : `${testLabel} 완료: ${targetTestCases.length}개 실행`);
    const details = targetTestCases.map((tc, idx) => {
      const testId = forSubmit ? `base-${idx}` : getTestId(tc, idx);
      const r = results[testId];
      const label = forSubmit ? `[공식 ${idx + 1}]` : `[Test ${idx + 1}]`;
      if (!r) return `${label} 미실행`;
      if (r.passed === null) {
        return `${label} 실행 완료${r.time ? ` (${r.time.toFixed(0)}ms)` : ''}`;
      }
      return `${label} ${r.passed ? '✓ PASS' : '✗ FAIL'}${r.time ? ` (${r.time.toFixed(0)}ms)` : ''}`;
    }).join('\n');
    setOutput(`${summary}\n\n${details}`);

    return results;
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
          const blankTestResults: TestResult[] = [{
            testId: 'blank-result',
            passed: correct,
            actual: correct ? 'correct' : 'incorrect',
          }];
          // 빈칸 힌트 사용 횟수 전달
          onSubmit(getExecutableCode(), blankTestResults, blankHintsUsedCount);
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
          const puzzleTestResults: TestResult[] = [{
            testId: 'puzzle-result',
            passed: correct,
            actual: correct ? 'correct order' : 'wrong order',
          }];
          // 퍼즐 힌트 사용 횟수 전달
          onSubmit(getExecutableCode(), puzzleTestResults, puzzleHintsUsedCount);
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

      if (isSubmit) {
        // 제출 시: 모든 테스트 케이스 재실행 후 결과 전달
        const results = await runAllTestCases(true);
        const resultArray = Object.values(results);

        // 테스트 통과 여부 확인 (expected가 있는 테스트만)
        const judgedResults = resultArray.filter(r => r.passed !== null);
        const allPassed = judgedResults.length > 0 && judgedResults.every(r => r.passed);

        onSubmit(executableCode, resultArray);

        // 모든 테스트 통과 시에만 수정 불가 상태로 전환
        if (allPassed) {
          setIsSubmitted(true);
        }
      } else {
        // 실행 시: 단순 코드 실행 (입력 없이)
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

  // 빈칸별 힌트 요청 핸들러 (횟수 제한 없음, 사용 기록만 추적)
  const handleBlankHint = async (blankIndex: number) => {
    if (blankHintLoading !== null) return;  // 이미 로딩 중

    // 이미 힌트가 있으면 무시 (중복 요청 방지)
    if (blankHints[blankIndex]) return;

    setBlankHintLoading(blankIndex);

    try {
      const { practiceApi } = await import('@/lib/api/practice');

      const result = await practiceApi.getBlankHint({
        // baseProblemId 우선 사용 (사전 생성된 힌트 캐시 매칭을 위해)
        problemId: problem.baseProblemId || problem.id,
        blankIndex,
        codeTemplate: problem.codeSnippet || '',
        attemptId,  // attempt tracking
      });

      // 힌트 저장
      setBlankHints(prev => ({ ...prev, [blankIndex]: result.hintContent }));

      // 힌트 사용 횟수 증가 (기록용, 캐시 여부와 관계없이 항상 증가)
      setBlankHintsUsedCount(prev => prev + 1);

      // 상위 컴포넌트에 힌트 사용 알림 (채팅에서 해당 빈칸 답변 가능하도록)
      onBlankHintUsed?.(blankIndex);

      console.log(`[BlankHint] blank=${blankIndex+1}, fromCache=${result.fromCache}, totalUsed=${blankHintsUsedCount + 1}`);

    } catch (error) {
      console.error('[BlankHint] Error:', error);
      setBlankHints(prev => ({
        ...prev,
        [blankIndex]: '힌트를 불러올 수 없습니다.'
      }));
    } finally {
      setBlankHintLoading(null);
    }
  };

  // 퍼즐 힌트 요청 핸들러 (틀린 블록 순서대로 힌트 제공, 횟수 제한 없음)
  const handlePuzzleHint = async () => {
    if (puzzleHintLoading) return;

    // 틀린 블록들 찾기 (현재 위치 기준)
    const wrongBlockIndices: number[] = [];
    blocks.forEach((block, idx) => {
      if (!puzzleResults[block.id]) {
        wrongBlockIndices.push(idx);
      }
    });

    if (wrongBlockIndices.length === 0) {
      setPuzzleHintMessages(prev => [...prev, '모든 블록이 올바른 위치에 있습니다!']);
      return;
    }

    // 아직 힌트 안 준 첫 번째 틀린 블록
    const hintedCount = puzzleHintMessages.length;
    if (hintedCount >= wrongBlockIndices.length) {
      setPuzzleHintMessages(prev => [...prev, '더 이상 힌트가 없습니다. 남은 블록을 직접 배치해보세요.']);
      return;
    }

    const targetBlockIdx = wrongBlockIndices[hintedCount];
    const targetBlock = blocks[targetBlockIdx];

    setPuzzleHintLoading(true);

    try {
      const { practiceApi } = await import('@/lib/api/practice');

      const result = await practiceApi.getPuzzleHint({
        // baseProblemId 우선 사용 (사전 생성된 힌트 캐시 매칭을 위해)
        problemId: problem.baseProblemId || problem.id,
        blockIndex: targetBlockIdx,
        blocks: blocks.map(b => ({ id: b.id, code: b.code })),
        attemptId,  // attempt tracking
      });

      // 힌트 메시지: "N번째 위치: [블록 역할 설명]"
      const correctPosition = targetBlock.correctOrder + 1;
      const hintMessage = `${correctPosition}번째 위치: ${result.hintContent}`;
      setPuzzleHintMessages(prev => [...prev, hintMessage]);

      // 힌트 사용 횟수 증가 (기록용)
      setPuzzleHintsUsedCount(prev => prev + 1);

      // 상위 컴포넌트에 힌트 사용 알림 (채팅에서 해당 블록 답변 가능하도록)
      onBlankHintUsed?.(targetBlockIdx);

      console.log(`[PuzzleHint] blockIdx=${targetBlockIdx}, totalUsed=${puzzleHintsUsedCount + 1}`);

    } catch (error) {
      console.error('[PuzzleHint] Error:', error);
      setPuzzleHintMessages(prev => [...prev, '힌트를 불러올 수 없습니다.']);
    } finally {
      setPuzzleHintLoading(false);
    }
  };

  // 블록 드래그 핸들러
  const handleDragStart = (blockId: string | number) => {
    setDraggedBlock(String(blockId));
  };

  const handleDragOver = (e: React.DragEvent, targetId: string | number) => {
    e.preventDefault();
    const targetIdStr = String(targetId);
    if (!draggedBlock || draggedBlock === targetIdStr) return;

    // 정답 블록 위로는 드래그 불가
    const targetBlock = blocks.find(b => String(b.id) === targetIdStr);
    if (targetBlock && puzzleResults[targetBlock.id]) return;

    // 정답 블록들의 원래 위치를 기억
    const lockedPositions: { index: number; block: typeof blocks[0] }[] = [];
    blocks.forEach((block, index) => {
      if (puzzleResults[block.id]) {
        lockedPositions.push({ index, block });
      }
    });

    // 오답 블록들만 추출
    const unlockedBlocks = blocks.filter(b => !puzzleResults[b.id]);

    // 오답 블록들 내에서 순서 변경
    const dragIndex = unlockedBlocks.findIndex(b => String(b.id) === draggedBlock);
    const targetIndex = unlockedBlocks.findIndex(b => String(b.id) === targetIdStr);

    if (dragIndex === -1 || targetIndex === -1) return;

    const [removed] = unlockedBlocks.splice(dragIndex, 1);
    unlockedBlocks.splice(targetIndex, 0, removed);

    // 정답 블록들을 원래 위치에 다시 삽입
    const newBlocks = [...unlockedBlocks];
    lockedPositions.forEach(({ index, block }) => {
      newBlocks.splice(index, 0, block);
    });

    setBlocks(newBlocks);
  };

  const handleDragEnd = () => {
    setDraggedBlock(null);
  };

  // 결과 리셋
  const resetResults = () => {
    setTestResults({});
    setOutput('');
  };

  // 번역 핸들러
  const handleTranslate = async () => {
    if (!problem.description || isTranslating) return;

    setIsTranslating(true);
    try {
      const result = await translateText(problem.description, targetLanguage);
      if (result.success && result.translated_text) {
        setTranslatedDescription(result.translated_text);
        setShowOriginal(false);
      } else {
        console.error('Translation failed:', result.error);
      }
    } catch (error) {
      console.error('Translation error:', error);
    } finally {
      setIsTranslating(false);
    }
  };

  const judgedResults = Object.values(testResults).filter((r) => r.passed !== null);
  const passedCount = judgedResults.filter((r) => r.passed === true).length;
  const totalTests = baseTestCases.length;
  const testedCount = judgedResults.length;  // 판정된 테스트만 카운트

  // 테스트 케이스 값을 보기 좋게 포맷팅
  const formatTestValue = (value: any): string => {
    if (value === null || value === undefined) return '';
    if (typeof value === 'string') {
      // 문자열은 그대로 반환 (줄바꿈 포함)
      return value;
    }
    // 배열이나 객체는 보기 좋게 포맷팅
    return JSON.stringify(value, null, 2);
  };
  const allPassed = testedCount > 0 && passedCount === testedCount;

  // Blank 코드 렌더링
  const renderBlankCode = () => {
    const codeLines = (problem.codeSnippet || '').split('\n');
    let sequentialBlankIndex = 0;  // Legacy ___ 패턴용 순차 인덱스
    const blanks = problem.blanks || [];

    return codeLines.map((line, lineIdx) => {
      const parts: React.ReactNode[] = [];
      let lastIndex = 0;
      let match;
      // _N_ 패턴 (예: _0_, _1_, _10_) 또는 레거시 ___ 패턴 매칭
      const blankPattern = /_(\d+)_|___/g;

      while ((match = blankPattern.exec(line)) !== null) {
        if (match.index > lastIndex) {
          parts.push(
            <span key={`text-${lineIdx}-${lastIndex}`} className="text-[#d4d4d4]">
              {line.slice(lastIndex, match.index)}
            </span>
          );
        }

        // blankIndex 결정: _N_ 패턴이면 N 사용, ___ 패턴이면 순차 인덱스 사용
        let blankIndex: number;
        if (match[1] !== undefined) {
          // _N_ 패턴 - 숫자를 인덱스로 사용
          blankIndex = parseInt(match[1], 10);
        } else {
          // 레거시 ___ 패턴 - 순차 인덱스 사용
          blankIndex = sequentialBlankIndex;
          sequentialBlankIndex++;
        }

        const blank = blanks[blankIndex];
        if (blank) {
          const isCorrect = blankResults[blank.id];
          const hasResult = Object.keys(blankResults).length > 0;

          // 정답 길이에 맞는 언더스코어 플레이스홀더 생성
          const answerLength = blank.answer?.length || 3;
          const placeholder = '_'.repeat(answerLength);
          // 동적 너비: 정답 길이에 따라 조정 (최소 50px, 최대 200px)
          const inputWidth = Math.min(200, Math.max(50, answerLength * 10 + 20));

          parts.push(
            <span key={`blank-${blank.id}`} className="inline-flex items-center gap-1 mx-1">
              <Input
                value={blankAnswers[blank.id] || ''}
                onChange={(e) =>
                  setBlankAnswers((prev) => ({ ...prev, [blank.id]: e.target.value }))
                }
                style={{ width: `${inputWidth}px` }}
                className={`inline-block h-7 px-2 py-0 font-mono text-sm ${
                  hasResult
                    ? isCorrect
                      ? 'border-green-500 bg-green-500/10 text-green-400'
                      : 'border-red-500 bg-red-500/10 text-red-400'
                    : 'border-primary/50 bg-[#2d2d2d] text-[#d4d4d4]'
                }`}
                placeholder={placeholder}
                disabled={isSubmitted}
              />
              {/* 빈칸별 힌트 버튼 - 팝업 내 버튼 클릭 방식 */}
              {!isSubmitted && (
                <Popover>
                  <PopoverTrigger asChild>
                    <button
                      className={`relative text-muted-foreground hover:text-primary transition-colors ${
                        blankHints[blankIndex] ? 'text-blue-400' : ''
                      }`}
                      title="힌트 보기"
                    >
                      {blankHintLoading === blankIndex ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : blankHints[blankIndex] ? (
                        <Lightbulb className="h-4 w-4" />
                      ) : (
                        <HelpCircle className="h-4 w-4" />
                      )}
                    </button>
                  </PopoverTrigger>
                  <PopoverContent className="w-80 p-4">
                    {blankHints[blankIndex] ? (
                      /* 힌트 내용 표시 (정답 + 이유 설명) */
                      <div className="space-y-2">
                        <div className="flex items-start gap-2">
                          <Lightbulb className="h-4 w-4 mt-0.5 text-blue-400 flex-shrink-0" />
                          <p className="text-sm text-foreground leading-relaxed">
                            {blankHints[blankIndex]}
                          </p>
                        </div>
                        <p className="text-xs text-muted-foreground text-center pt-2 border-t border-border">
                          이해가 됐다면 다음 빈칸도 도전해보세요!
                        </p>
                      </div>
                    ) : (
                      /* 초기 상태: 힌트 요청 버튼 */
                      <div className="space-y-3">
                        <div className="text-center">
                          <HelpCircle className="h-8 w-8 mx-auto text-muted-foreground mb-2" />
                          <p className="text-sm font-medium">빈칸 #{blankIndex + 1} 힌트</p>
                        </div>
                        <Button
                          size="sm"
                          onClick={() => handleBlankHint(blankIndex)}
                          disabled={blankHintLoading === blankIndex}
                          className="w-full"
                        >
                          {blankHintLoading === blankIndex ? (
                            <Loader2 className="h-4 w-4 animate-spin mr-2" />
                          ) : (
                            <Lightbulb className="h-4 w-4 mr-2" />
                          )}
                          힌트 보기
                        </Button>
                        <p className="text-xs text-muted-foreground text-center">
                          정답과 이유를 알려드려요
                        </p>
                      </div>
                    )}
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
        } else {
          // blank이 없으면 원래 텍스트 그대로 표시
          parts.push(
            <span key={`blank-fallback-${lineIdx}-${match.index}`} className="text-yellow-500">
              {match[0]}
            </span>
          );
        }

        // 매칭된 문자열 길이만큼 lastIndex 이동
        lastIndex = match.index + match[0].length;
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
    const isCustom = 'isCustom' in tc && tc.isCustom;
    const customTc = isCustom ? (tc as CustomTestCase) : null;
    const testId = getTestId(tc, idx);

    // O(1) 직접 접근 (ID 기반)
    const result = testResults[testId];
    const isExpanded = expandedTests.has(idx);
    const isRunningThis = runningTestId === testId;

    return (
      <Collapsible
        key={customTc?.id || idx}
        open={isExpanded}
        onOpenChange={() => toggleTestExpand(idx)}
      >
        <div
          className={`rounded-lg border transition-all ${
            result
              ? result.passed === null
                ? 'bg-blue-500/5 border-blue-500/30'  // 출력 확인용 (중립)
                : result.passed
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
                    <span className="text-primary">
                      Custom {showCustomOnly ? idx + 1 : idx - baseTestCases.filter(t => !t.isHidden).length + 1}
                    </span>
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
                {!isRunningThis && (
                  <div className="flex items-center gap-2">
                    {/* 결과 표시 */}
                    {result && (
                      result.passed === null ? (
                        <div className="flex items-center gap-1.5 text-blue-500">
                          <Terminal className="h-4 w-4" />
                          <span className="text-xs font-medium">{result.time ? `${result.time.toFixed(0)}ms` : '완료'}</span>
                        </div>
                      ) : result.passed ? (
                        <div className="flex items-center gap-1.5 text-green-500">
                          <CheckCircle2 className="h-4 w-4" />
                          <span className="text-xs font-medium">{result.time ? `${result.time.toFixed(0)}ms` : ''}</span>
                        </div>
                      ) : (
                        <div className="flex items-center gap-1.5 text-red-500">
                          <XCircle className="h-4 w-4" />
                          <span className="text-xs font-medium">{result.time ? `${result.time.toFixed(0)}ms` : ''}</span>
                        </div>
                      )
                    )}
                    {/* 실행/재실행 버튼 - 항상 표시 */}
                    <Button
                      variant="ghost"
                      size="icon"
                      className={`h-6 w-6 ${!result ? 'opacity-0 group-hover:opacity-100 transition-opacity' : ''}`}
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
                      onClick={() => navigator.clipboard.writeText(formatTestValue(tc.input))}
                    >
                      <Copy className="h-3 w-3" />
                    </Button>
                  )}
                </div>
                {isCustom ? (
                  <textarea
                    value={formatTestValue(customTc!.input)}
                    onChange={(e) => updateCustomTestCase(customTc!.id, 'input', e.target.value)}
                    className="text-xs font-mono text-foreground whitespace-pre-wrap bg-background/50 rounded p-2 min-h-[80px] max-h-[200px] overflow-auto w-full resize-y border-0 focus:outline-none focus:ring-1 focus:ring-primary"
                    placeholder="입력값을 입력하세요 (여러 줄 가능)"
                  />
                ) : (
                  <pre className="text-xs font-mono text-foreground whitespace-pre-wrap break-all bg-background/50 rounded p-2 max-h-32 overflow-auto">
                    {formatTestValue(tc.input)}
                  </pre>
                )}
              </div>

              {/* Expected - 공식 테스트만 표시, 커스텀은 출력 확인용이라 숨김 */}
              {!isCustom && (
                <div className="rounded-md bg-secondary/50 p-2">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-[10px] uppercase tracking-wider text-muted-foreground font-medium">
                      Expected
                    </span>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-5 w-5"
                      onClick={() => navigator.clipboard.writeText(formatTestValue(tc.expected))}
                    >
                      <Copy className="h-3 w-3" />
                    </Button>
                  </div>
                  <pre className="text-xs font-mono text-foreground whitespace-pre-wrap break-all bg-background/50 rounded p-2 max-h-32 overflow-auto">
                    {formatTestValue(tc.expected)}
                  </pre>
                </div>
              )}

              {/* Output - 실행 결과 */}
              {result && (
                <div className={`rounded-md bg-secondary/50 p-2 ${
                  result.passed === false ? 'border border-red-500/30' : ''
                }`}>
                  <span className="text-[10px] uppercase tracking-wider text-muted-foreground font-medium block mb-1">
                    Output
                  </span>
                  <pre className={`text-xs font-mono whitespace-pre-wrap break-all bg-background/50 rounded p-2 max-h-32 overflow-auto ${
                    result.passed === false ? 'text-red-400' : 'text-foreground'
                  }`}>
                    {formatTestValue(result.actual)}
                  </pre>
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
            style={{ maxWidth: sidebarWidth, minWidth: 0 }}
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
            <ScrollArea className="flex-1 min-w-0 w-full">
              <div className="p-4 min-w-0 w-full overflow-hidden">
                {activeTab === 'problem' ? (
                  <div className="space-y-4 w-full overflow-hidden">
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="text-sm font-semibold">문제 설명</h4>
                        <div className="flex items-center gap-2">
                          <Select
                            value={targetLanguage}
                            onValueChange={(value) => setTargetLanguage(value as LanguageCode)}
                          >
                            <SelectTrigger className="h-7 w-24 text-xs">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              {Object.entries(LANGUAGE_LABELS).map(([code, label]) => (
                                <SelectItem key={code} value={code} className="text-xs">
                                  {label}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={handleTranslate}
                            disabled={isTranslating}
                            className="h-7 px-2 text-xs gap-1"
                          >
                            {isTranslating ? (
                              <Loader2 className="h-3.5 w-3.5 animate-spin" />
                            ) : (
                              <Languages className="h-3.5 w-3.5" />
                            )}
                            번역
                          </Button>
                        </div>
                      </div>
                      {/* 원문/번역문 토글 */}
                      {translatedDescription && (
                        <div className="flex gap-1 mb-2">
                          <Button
                            variant={showOriginal ? "default" : "ghost"}
                            size="sm"
                            onClick={() => setShowOriginal(true)}
                            className="h-6 px-2 text-xs"
                          >
                            원문
                          </Button>
                          <Button
                            variant={!showOriginal ? "default" : "ghost"}
                            size="sm"
                            onClick={() => setShowOriginal(false)}
                            className="h-6 px-2 text-xs"
                          >
                            {LANGUAGE_LABELS[targetLanguage]}
                          </Button>
                        </div>
                      )}
                      <div
                        className="text-sm text-muted-foreground leading-relaxed prose prose-sm prose-invert prose-p:my-1 prose-pre:bg-secondary/50 prose-pre:overflow-x-auto prose-code:text-primary [&_img]:max-w-full [&_img]:h-auto [&_img]:my-4 [&_img]:rounded-md"
                        style={{
                          maxWidth: `${sidebarWidth - 32}px`,  // 32px = p-4 양쪽 패딩
                          wordBreak: 'break-word',
                          overflowWrap: 'break-word',
                          whiteSpace: 'pre-wrap'
                        }}
                      >
                        <ReactMarkdown
                          remarkPlugins={[remarkGfm, remarkMath]}
                          rehypePlugins={[rehypeKatex]}
                          components={{
                            img: ({ src, alt }) => (
                              <span className="inline-block my-4 p-2 bg-white rounded-md">
                                {/* eslint-disable-next-line @next/next/no-img-element */}
                                <img
                                  src={src}
                                  alt={alt || ''}
                                  loading="lazy"
                                  className="max-w-full h-auto rounded"
                                />
                              </span>
                            ),
                          }}
                        >
                          {preprocessLatex(showOriginal || !translatedDescription
                            ? problem.description || ''
                            : translatedDescription)}
                        </ReactMarkdown>
                      </div>
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
                        {Object.keys(testResults).length > 0 && (
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

                    {/* Implementation/Guided 모드 안내 */}
                    {(problemType === 'implementation' || problemType === 'guided') && visibleTestCases.length === 0 && (
                      <div className="rounded-lg p-4 bg-primary/5 border border-primary/20 text-center space-y-2">
                        <TestTube className="h-8 w-8 mx-auto text-primary/60" />
                        <p className="text-sm font-medium text-foreground">테스트 케이스를 추가하세요</p>
                        <p className="text-xs text-muted-foreground">
                          위의 &apos;추가&apos; 버튼을 눌러 입력값과 예상 출력값을 설정하고,<br />
                          코드가 올바르게 동작하는지 검증하세요.
                        </p>
                      </div>
                    )}

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
                // 정답 블록은 고정 (드래그 불가)
                const isLocked = hasResult && isCorrect;

                return (
                  <div
                    key={block.id}
                    draggable={!isSubmitted && !isLocked}
                    onDragStart={() => !isSubmitted && !isLocked && handleDragStart(block.id)}
                    onDragOver={(e) => !isSubmitted && !isLocked && handleDragOver(e, block.id)}
                    onDragEnd={handleDragEnd}
                    className={`flex items-center gap-2 p-2 rounded border transition-all ${
                      isSubmitted || isLocked
                        ? 'cursor-default'
                        : 'cursor-move'
                    } ${
                      draggedBlock === block.id
                        ? 'bg-primary/20 border-primary'
                        : hasResult
                          ? isCorrect
                            ? 'bg-green-500/10 border-green-500/50'
                            : `bg-red-500/10 border-red-500/50 ${showPuzzlePulse ? 'animate-[pulse_2s_ease-in-out_1]' : ''}`
                          : 'bg-card border-border hover:border-primary/50'
                    }`}
                    style={{ marginLeft: block.indentation * 24 }}
                  >
                    {isLocked ? (
                      <Lock className="h-4 w-4 shrink-0 text-green-500" />
                    ) : (
                      <GripVertical className={`h-4 w-4 shrink-0 ${
                        hasResult
                          ? isCorrect
                            ? 'text-green-500'
                            : 'text-red-500'
                          : 'text-muted-foreground'
                      }`} />
                    )}
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

        {/* Implementation 모드: 코드 에디터만 */}
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

        {/* Guided 모드: 코드 에디터만 (가이드 채팅은 오른쪽 AI 코딩 튜터에서 처리) */}
        {problemType === 'guided' && (
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
            <div className="flex items-center gap-4 mb-3">
              <p className="text-xs text-[#808080]">조립된 코드:</p>
              <div className="flex items-center gap-3 text-[10px]">
                <span className="flex items-center gap-1">
                  <span className="w-2 h-2 rounded-full bg-[#6A9955]"></span>
                  <span className="text-[#808080]">고정 코드</span>
                </span>
                <span className="flex items-center gap-1">
                  <span className="w-2 h-2 rounded-full bg-[#9CDCFE]"></span>
                  <span className="text-[#808080]">퍼즐 블록</span>
                </span>
              </div>
            </div>
            <pre className="font-mono text-sm whitespace-pre-wrap">
              {/* fixed_start - 녹색 (고정) */}
              {problem.fixedStart && (
                <span className="text-[#6A9955]">{problem.fixedStart}{'\n'}</span>
              )}
              {/* 퍼즐 블록 - 하늘색 (변경 가능) */}
              <span className="text-[#9CDCFE]">
                {blocks.map(b => {
                  // baseIndentation + 블록의 상대적 indentation = 최종 들여쓰기
                  const relativeIndent = b.indentation || 0;
                  const totalIndent = baseIndentation + relativeIndent;
                  return '    '.repeat(totalIndent) + b.code;
                }).join('\n')}
              </span>
              {/* fixed_end - 녹색 (고정) */}
              {problem.fixedEnd && (
                <span className="text-[#6A9955]">{'\n'}{problem.fixedEnd}</span>
              )}
            </pre>
          </div>
        )}

        {/* 테스트 결과 Console - implementation/guided에서 표시 */}
        {(problemType === 'implementation' || problemType === 'guided') && (
          <div className="shrink-0 border-t border-border bg-[#1e1e1e]">
            <div className="flex items-center justify-between px-4 py-2 border-b border-[#333]">
              <div className="flex items-center gap-2">
                <TestTube className="h-4 w-4 text-[#808080]" />
                <span className="text-sm font-medium text-[#cccccc]">테스트 결과</span>
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
                  테스트 실행 중...
                </div>
              ) : output ? (
                <pre className="text-xs font-mono text-[#4ec9b0] whitespace-pre-wrap">
                  {output}
                </pre>
              ) : (
                <p className="text-xs text-[#808080]">
                  왼쪽 테스트 탭에서 테스트 케이스를 추가하고, &apos;테스트 실행&apos; 버튼을 눌러 코드를 검증하세요.
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
            ((problemType === 'implementation' || problemType === 'guided') && isSubmitted)) && (
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

                {/* Implementation/Guided 결과 */}
                {(problemType === 'implementation' || problemType === 'guided') && (
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

        {/* Puzzle 힌트 메시지 표시 */}
        {problemType === 'puzzle' && puzzleHintMessages.length > 0 && (
          <div className="shrink-0 px-4 py-2 bg-blue-500/10 border-t border-blue-500/30">
            <div className="flex items-start gap-2">
              <Lightbulb className="h-4 w-4 text-blue-400 mt-0.5 flex-shrink-0" />
              <div className="flex-1 space-y-1">
                {puzzleHintMessages.map((msg, idx) => (
                  <p key={idx} className="text-sm text-blue-300">
                    {idx + 1}. {msg}
                  </p>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Actions Bar */}
        <div className="shrink-0 flex items-center justify-between px-4 py-3 border-t border-border bg-card">
          {/* 힌트 버튼 (Puzzle 모드) */}
          <div>
            {problemType === 'puzzle' && !isSubmitted && Object.keys(puzzleResults).length > 0 && (
              <Button
                variant="outline"
                size="sm"
                onClick={handlePuzzleHint}
                disabled={puzzleHintLoading}
                className="gap-2"
              >
                {puzzleHintLoading ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Lightbulb className="h-4 w-4" />
                )}
                힌트 {puzzleHintsUsedCount > 0 ? `(${puzzleHintsUsedCount}회 사용)` : ''}
              </Button>
            )}
          </div>
          <div className="flex gap-2">
            {/* 포기 버튼 - 제출 전에만 표시 */}
            {!isSubmitted && onGiveUp && (
              <Button
                variant="ghost"
                size="sm"
                onClick={onGiveUp}
                disabled={isRunning}
                className="text-muted-foreground hover:text-destructive"
              >
                <XCircle className="mr-2 h-4 w-4" />
                포기
              </Button>
            )}
            {/* 테스트 실행 버튼 - implementation/guided에서 표시 */}
            {(problemType === 'implementation' || problemType === 'guided') && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => runAllTestCases()}
                disabled={isRunning || isSubmitted}
              >
                <Play className="mr-2 h-4 w-4" />
                테스트 실행
              </Button>
            )}
            <Button
              size="sm"
              onClick={() => runTests(true)}
              disabled={isRunning || isSubmitted || (problemType === 'blank' && filledCount < totalBlanks)}
            >
              {(problemType === 'implementation' || problemType === 'guided') ? (
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
