'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Play,
  Send,
  CheckCircle2,
  XCircle,
  Clock,
  Lightbulb,
  Terminal,
} from 'lucide-react';
import type { ImplementationProblemData, TestCase } from '@/lib/types';
import { EditorMock } from '../EditorMock';

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
    <div className="flex h-full flex-col">
      {/* Header with problem info */}
      <div className="mb-4 space-y-2">
        <p className="text-sm text-muted-foreground whitespace-pre-wrap">
          {description}
        </p>
        <div className="flex items-center gap-2 text-sm">
          <Badge variant="outline">
            테스트 케이스: {visibleTestCases.length}개 공개 / {hiddenTestCases.length}개 숨김
          </Badge>
        </div>
      </div>

      {/* Code Editor */}
      <div className="flex-1 min-h-0 rounded-lg border border-border overflow-hidden">
        <EditorMock
          initialCode={code}
          language="python"
          onChange={setCode}
          readOnly={isSubmitted}
        />
      </div>

      {/* Test Cases & Output */}
      <div className="mt-4 grid grid-cols-2 gap-4">
        {/* Test Cases */}
        <div className="rounded-lg border border-border p-3">
          <h4 className="text-sm font-medium mb-2">테스트 케이스</h4>
          <div className="space-y-2 max-h-40 overflow-y-auto">
            {visibleTestCases.map((tc, idx) => {
              const result = testResults.find(
                (r) => JSON.stringify(r.testCase) === JSON.stringify(tc)
              );
              return (
                <div
                  key={idx}
                  className={`rounded p-2 text-xs font-mono ${
                    result
                      ? result.passed
                        ? 'bg-green-500/10 border border-green-500/20'
                        : 'bg-red-500/10 border border-red-500/20'
                      : 'bg-secondary'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-muted-foreground">Case {idx + 1}</span>
                    {result && (
                      result.passed ? (
                        <CheckCircle2 className="h-3 w-3 text-green-500" />
                      ) : (
                        <XCircle className="h-3 w-3 text-red-500" />
                      )
                    )}
                  </div>
                  <div className="mt-1">
                    <span className="text-muted-foreground">Input: </span>
                    <span>{JSON.stringify(tc.input)}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Expected: </span>
                    <span>{JSON.stringify(tc.expected)}</span>
                  </div>
                  {result && !result.passed && (
                    <div className="text-red-500">
                      <span className="text-muted-foreground">Actual: </span>
                      <span>{JSON.stringify(result.actual)}</span>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Output Console */}
        <div className="rounded-lg border border-border p-3">
          <div className="flex items-center gap-2 mb-2">
            <Terminal className="h-4 w-4" />
            <h4 className="text-sm font-medium">Output</h4>
          </div>
          <div className="bg-code-bg rounded p-2 h-32 overflow-y-auto">
            {isRunning ? (
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Clock className="h-4 w-4 animate-spin" />
                실행 중...
              </div>
            ) : output ? (
              <pre className="text-xs font-mono text-code-variable whitespace-pre-wrap">
                {output}
              </pre>
            ) : (
              <p className="text-xs text-muted-foreground">
                코드를 실행하면 결과가 여기에 표시됩니다.
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Result summary after submit */}
      {isSubmitted && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className={`mt-4 p-4 rounded-lg ${
            allPassed
              ? 'bg-green-500/10 border border-green-500/20'
              : 'bg-red-500/10 border border-red-500/20'
          }`}
        >
          <div className="flex items-center gap-3">
            {allPassed ? (
              <>
                <CheckCircle2 className="h-6 w-6 text-green-500" />
                <div>
                  <p className="font-medium text-green-600">모든 테스트 통과!</p>
                  <p className="text-sm text-muted-foreground">
                    {passedCount}/{totalTests} 테스트 케이스 통과
                  </p>
                </div>
              </>
            ) : (
              <>
                <XCircle className="h-6 w-6 text-red-500" />
                <div>
                  <p className="font-medium text-red-600">일부 테스트 실패</p>
                  <p className="text-sm text-muted-foreground">
                    {passedCount}/{totalTests} 테스트 케이스 통과
                  </p>
                </div>
              </>
            )}
          </div>
        </motion.div>
      )}

      {/* Actions */}
      <div className="mt-4 flex items-center justify-between">
        <Button
          variant="ghost"
          size="sm"
          onClick={handleHint}
          disabled={isSubmitted || hintsUsed >= 3}
          className="text-yellow-600"
        >
          <Lightbulb className="mr-2 h-4 w-4" />
          힌트 ({3 - hintsUsed}회 남음)
        </Button>

        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={() => runTests(false)}
            disabled={isRunning || isSubmitted}
          >
            <Play className="mr-2 h-4 w-4" />
            실행하기
          </Button>
          <Button
            onClick={() => runTests(true)}
            disabled={isRunning || isSubmitted}
          >
            <Send className="mr-2 h-4 w-4" />
            제출하기
          </Button>
        </div>
      </div>
    </div>
  );
}
