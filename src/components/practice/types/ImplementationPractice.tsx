'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
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
} from 'lucide-react';
import type { ImplementationProblemData, TestCase } from '@/lib/types';
import { CodeEditor } from '../CodeEditor';

interface TestResult {
  testCase: TestCase;
  passed: boolean;
  actual?: any;
  error?: string;
  time?: number;
}

interface ImplementationPracticeProps {
  data: ImplementationProblemData;
  description: string;
  onSubmit: (code: string, results: TestResult[]) => void;
  onRun: (code: string) => void;
  onHintRequest: (level: number) => void;
}

export function ImplementationPractice({
  data,
  description,
  onSubmit,
  onRun,
  onHintRequest,
}: ImplementationPracticeProps) {
  const [code, setCode] = useState(data.functionSignature + '\n    # 여기에 코드를 작성하세요\n    pass');
  const [testResults, setTestResults] = useState<TestResult[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [hintsUsed, setHintsUsed] = useState(0);
  const [output, setOutput] = useState<string>('');
  const [showSidebar, setShowSidebar] = useState(true);
  const [activeTab, setActiveTab] = useState<'problem' | 'testcases'>('problem');

  const visibleTestCases = data.testCases.filter((tc) => !tc.isHidden);
  const hiddenTestCases = data.testCases.filter((tc) => tc.isHidden);

  const runTests = async (isSubmit: boolean = false) => {
    setIsRunning(true);
    setOutput('');

    // Simulate running tests (in real app, this would call Judge0/Sandpack)
    await new Promise((resolve) => setTimeout(resolve, 1500));

    const casesToTest = isSubmit ? data.testCases : visibleTestCases;
    const results: TestResult[] = [];

    for (const testCase of casesToTest) {
      // Mock test execution
      // In real implementation, this would execute the code
      const passed = Math.random() > 0.3; // Mock: 70% pass rate

      results.push({
        testCase,
        passed,
        actual: passed ? testCase.expected : 'Wrong answer',
        time: Math.floor(Math.random() * 100) + 10,
      });
    }

    setTestResults(results);
    setIsRunning(false);

    if (isSubmit) {
      setIsSubmitted(true);
      onSubmit(code, results);
    } else {
      onRun(code);
    }

    // Generate output
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

  const passedCount = testResults.filter((r) => r.passed).length;
  const totalTests = data.testCases.length;
  const allPassed = passedCount === totalTests;

  return (
    <div className="flex h-full gap-0">
      {/* Left Sidebar - Problem & Test Cases */}
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
                        {description}
                      </p>
                    </div>
                    <div className="pt-4 border-t border-border">
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

      {/* Main Content - Code Editor & Output */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Code Editor */}
        <div className="flex-1 min-h-0 overflow-hidden">
          <CodeEditor
            initialCode={code}
            language="python"
            onChange={setCode}
            readOnly={isSubmitted}
          />
        </div>

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
              disabled={isRunning || isSubmitted}
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
