'use client';

import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  Send,
  Lightbulb,
  SkipForward,
  CheckCircle2,
  XCircle,
  Code,
  Bot,
  User,
  Sparkles,
} from 'lucide-react';
import type { GuidedStep, GuidedProblemData } from '@/lib/types';

interface GuidedResponse {
  step: number;
  response: string | number;
  correct: boolean;
  time: number;
}

interface GuidedPracticeProps {
  data: GuidedProblemData;
  onComplete: (responses: GuidedResponse[]) => void;
  onHintRequest: (step: number) => void;
  onSkip: (step: number) => void;
}

export function GuidedPractice({
  data,
  onComplete,
  onHintRequest,
  onSkip,
}: GuidedPracticeProps) {
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [responses, setResponses] = useState<GuidedResponse[]>([]);
  const [userInput, setUserInput] = useState('');
  const [showHint, setShowHint] = useState(false);
  const [stepStartTime, setStepStartTime] = useState(Date.now());
  const [isCorrect, setIsCorrect] = useState<boolean | null>(null);
  const [showFeedback, setShowFeedback] = useState(false);
  const [isCompleted, setIsCompleted] = useState(false);
  const [hintsUsed, setHintsUsed] = useState(0);
  const [skipsUsed, setSkipsUsed] = useState(0);

  const chatEndRef = useRef<HTMLDivElement>(null);

  const currentStep = data.steps[currentStepIndex];
  const totalSteps = data.steps.length;

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [currentStepIndex, showFeedback]);

  const handleTextSubmit = () => {
    if (!userInput.trim()) return;

    const step = currentStep;
    let correct = false;

    if (step.responseType === 'text') {
      // Simple text comparison (normalize spaces and case)
      const normalizedInput = userInput.trim().toLowerCase().replace(/\s+/g, ' ');
      const normalizedCorrect = (step.correctCode || '').toLowerCase().replace(/\s+/g, ' ');
      correct = normalizedInput === normalizedCorrect ||
                userInput.trim().toLowerCase().includes(normalizedCorrect);
    } else if (step.responseType === 'code') {
      // Code comparison (normalize)
      const normalizedInput = userInput.trim().replace(/\s+/g, '');
      const normalizedCorrect = (step.correctCode || '').replace(/\s+/g, '');
      correct = normalizedInput === normalizedCorrect;
    }

    submitResponse(userInput, correct);
  };

  const handleChoiceSelect = (choiceIndex: number) => {
    const correct = choiceIndex === currentStep.correctChoice;
    submitResponse(choiceIndex.toString(), correct);
  };

  const submitResponse = (response: string | number, correct: boolean) => {
    const elapsedTime = Math.floor((Date.now() - stepStartTime) / 1000);

    const newResponse: GuidedResponse = {
      step: currentStep.stepNumber,
      response: response,
      correct,
      time: elapsedTime,
    };

    setResponses([...responses, newResponse]);
    setIsCorrect(correct);
    setShowFeedback(true);

    // Move to next step after delay
    setTimeout(() => {
      if (currentStepIndex < totalSteps - 1) {
        if (correct) {
          setCurrentStepIndex(currentStepIndex + 1);
        }
        // If not correct, stay on same step but let them try again
      } else if (correct) {
        setIsCompleted(true);
        onComplete([...responses, newResponse]);
      }
      setShowFeedback(false);
      setIsCorrect(null);
      setUserInput('');
      setShowHint(false);
      setStepStartTime(Date.now());
    }, correct ? 1500 : 2500);
  };

  const handleHint = () => {
    setShowHint(true);
    setHintsUsed(hintsUsed + 1);
    onHintRequest(currentStep.stepNumber);
  };

  const handleSkip = () => {
    setSkipsUsed(skipsUsed + 1);
    onSkip(currentStep.stepNumber);

    const newResponse: GuidedResponse = {
      step: currentStep.stepNumber,
      response: 'SKIPPED',
      correct: false,
      time: Math.floor((Date.now() - stepStartTime) / 1000),
    };

    setResponses([...responses, newResponse]);

    if (currentStepIndex < totalSteps - 1) {
      setCurrentStepIndex(currentStepIndex + 1);
      setStepStartTime(Date.now());
      setShowHint(false);
      setUserInput('');
    } else {
      setIsCompleted(true);
      onComplete([...responses, newResponse]);
    }
  };

  const renderChatHistory = () => {
    const elements: JSX.Element[] = [];

    // Render all previous steps
    for (let i = 0; i <= currentStepIndex; i++) {
      const step = data.steps[i];
      const response = responses.find((r) => r.step === step.stepNumber);

      // AI message
      elements.push(
        <motion.div
          key={`ai-${step.stepNumber}`}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex gap-3"
        >
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/10">
            <Bot className="h-4 w-4 text-primary" />
          </div>
          <div className="flex-1 space-y-2">
            <p className="text-sm text-foreground whitespace-pre-wrap">
              {step.aiMessage}
            </p>
            {/* Render choices if applicable and it's current step */}
            {step.responseType === 'choice' && i === currentStepIndex && !showFeedback && (
              <div className="flex flex-wrap gap-2 mt-2">
                {step.choices?.map((choice, idx) => (
                  <Button
                    key={idx}
                    variant="outline"
                    size="sm"
                    onClick={() => handleChoiceSelect(idx)}
                    className="text-sm"
                  >
                    {idx + 1}. {choice}
                  </Button>
                ))}
              </div>
            )}
            {/* Render code template if applicable */}
            {step.responseType === 'code' && i === currentStepIndex && !response && (
              <div className="mt-2 rounded-lg border border-border bg-code-bg p-3">
                <code className="text-sm text-code-variable">
                  {step.codeTemplate}
                </code>
              </div>
            )}
          </div>
        </motion.div>
      );

      // User response (if exists)
      if (response && i < currentStepIndex) {
        elements.push(
          <motion.div
            key={`user-${step.stepNumber}`}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex justify-end gap-3"
          >
            <div className="flex items-start gap-2">
              <div className="rounded-lg bg-primary px-3 py-2">
                <p className="text-sm text-primary-foreground">
                  {response.response === 'SKIPPED'
                    ? '(건너뜀)'
                    : step.responseType === 'choice'
                      ? step.choices?.[Number(response.response)]
                      : response.response}
                </p>
              </div>
              {response.correct ? (
                <CheckCircle2 className="h-5 w-5 text-green-500 shrink-0" />
              ) : (
                <XCircle className="h-5 w-5 text-red-500 shrink-0" />
              )}
            </div>
          </motion.div>
        );
      }
    }

    return elements;
  };

  if (isCompleted) {
    const correctCount = responses.filter((r) => r.correct).length;
    const score = Math.round((correctCount / totalSteps) * 100);

    return (
      <div className="flex h-full flex-col items-center justify-center p-6 text-center">
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          className="mb-4"
        >
          <Sparkles className="h-16 w-16 text-primary" />
        </motion.div>
        <h2 className="text-2xl font-bold mb-2">학습 완료!</h2>
        <p className="text-muted-foreground mb-4">
          {totalSteps}개 단계 중 {correctCount}개 정답
        </p>
        <div className="flex gap-4 mb-6">
          <Badge variant="outline" className="text-lg px-4 py-2">
            점수: {score}%
          </Badge>
          <Badge variant="outline" className="text-lg px-4 py-2">
            힌트 사용: {hintsUsed}회
          </Badge>
        </div>
        <div className="w-full max-w-md rounded-lg border border-border bg-code-bg p-4">
          <p className="text-sm text-muted-foreground mb-2">최종 완성 코드</p>
          <pre className="text-sm text-code-variable whitespace-pre-wrap">
            {data.finalCode}
          </pre>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col">
      {/* Progress */}
      <div className="mb-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Badge variant="secondary">
            Step {currentStepIndex + 1} / {totalSteps}
          </Badge>
          {showHint && (
            <Badge variant="outline" className="text-yellow-600">
              힌트 사용
            </Badge>
          )}
        </div>
        <div className="flex h-2 w-32 overflow-hidden rounded-full bg-secondary">
          <div
            className="bg-primary transition-all"
            style={{ width: `${((currentStepIndex + 1) / totalSteps) * 100}%` }}
          />
        </div>
      </div>

      {/* Chat area */}
      <div className="flex-1 overflow-y-auto space-y-4 pb-4">
        {renderChatHistory()}

        {/* Feedback */}
        <AnimatePresence>
          {showFeedback && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className={`flex items-center gap-2 p-3 rounded-lg ${
                isCorrect
                  ? 'bg-green-500/10 text-green-600'
                  : 'bg-red-500/10 text-red-600'
              }`}
            >
              {isCorrect ? (
                <>
                  <CheckCircle2 className="h-5 w-5" />
                  <span>정답입니다! 다음 단계로 넘어갑니다.</span>
                </>
              ) : (
                <>
                  <XCircle className="h-5 w-5" />
                  <span>다시 한번 생각해보세요. 힌트를 사용해보세요!</span>
                </>
              )}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Hint display */}
        {showHint && currentStep.hint && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex gap-2 items-start p-3 rounded-lg bg-yellow-500/10 border border-yellow-500/20"
          >
            <Lightbulb className="h-5 w-5 text-yellow-600 shrink-0" />
            <p className="text-sm text-yellow-800 dark:text-yellow-200">
              {currentStep.hint}
            </p>
          </motion.div>
        )}

        <div ref={chatEndRef} />
      </div>

      {/* Input area */}
      {currentStep.responseType !== 'choice' && !showFeedback && (
        <div className="border-t border-border pt-4">
          <div className="flex gap-2">
            <div className="flex-1 relative">
              <Input
                value={userInput}
                onChange={(e) => setUserInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleTextSubmit()}
                placeholder={
                  currentStep.responseType === 'code'
                    ? '코드를 입력하세요...'
                    : '답변을 입력하세요...'
                }
                className={`pr-10 ${
                  currentStep.responseType === 'code' ? 'font-mono' : ''
                }`}
              />
              {currentStep.responseType === 'code' && (
                <Code className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              )}
            </div>
            <Button onClick={handleTextSubmit} disabled={!userInput.trim()}>
              <Send className="h-4 w-4" />
            </Button>
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex justify-between pt-4">
        <Button
          variant="ghost"
          size="sm"
          onClick={handleHint}
          disabled={showHint || showFeedback}
          className="text-yellow-600"
        >
          <Lightbulb className="mr-2 h-4 w-4" />
          힌트 (-10 XP)
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={handleSkip}
          disabled={showFeedback}
          className="text-muted-foreground"
        >
          <SkipForward className="mr-2 h-4 w-4" />
          Skip
        </Button>
      </div>
    </div>
  );
}
