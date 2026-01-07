'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import {
  GraduationCap,
  Target,
  Briefcase,
  Code2,
  Sparkles,
  ChevronRight,
  ChevronLeft,
  Check,
  Zap,
  BookOpen,
  Building2,
  Rocket,
  TrendingUp,
  User,
  Binary,
  Network,
  Layers,
  Search,
  Hash,
} from 'lucide-react';

/**
 * 온보딩 데이터 구조
 */
export interface OnboardingData {
  experience_level: string;
  learning_goal: string;
  current_status: string;
  preferred_topics: string[];
  preferred_difficulty: string;
  preferred_language: string;
  completed_at?: string;
}

interface OnboardingWizardProps {
  onComplete: (data: OnboardingData) => void;
  onSkip?: () => void;
  initialData?: Partial<OnboardingData>;
}

// 단계 정의
const STEPS = [
  { id: 'level', title: '실력', icon: GraduationCap },
  { id: 'goal', title: '목표', icon: Target },
  { id: 'status', title: '현재', icon: Briefcase },
  { id: 'topics', title: '주제', icon: Code2 },
  { id: 'difficulty', title: '난이도', icon: Zap },
];

// 옵션 데이터
const LEVEL_OPTIONS = [
  { value: 'beginner', label: '입문자', description: '프로그래밍을 이제 시작했어요', icon: BookOpen },
  { value: 'elementary', label: '초급', description: '기본 문법은 알지만 알고리즘은 처음', icon: Sparkles },
  { value: 'intermediate', label: '중급', description: 'DP, 그래프 등 기본 알고리즘 학습 중', icon: TrendingUp },
  { value: 'advanced', label: '고급', description: '대회 입상 경험 / 코테 통과 경험 있음', icon: Rocket },
];

const GOAL_OPTIONS = [
  { value: 'big_tech', label: '대기업 취업', description: '네카라쿠배 등 대기업 코딩테스트 준비', icon: Building2 },
  { value: 'mid_startup', label: '중견/스타트업', description: '중견기업 또는 스타트업 취업 준비', icon: Rocket },
  { value: 'skill_up', label: '실력 향상', description: '알고리즘 실력 자체를 키우고 싶어요', icon: TrendingUp },
  { value: 'competition', label: '대회 준비', description: 'ICPC, 코드포스 등 경진대회 준비', icon: Target },
];

const STATUS_OPTIONS = [
  { value: 'student', label: '학생', description: '대학생 / 대학원생', icon: GraduationCap },
  { value: 'job_seeker', label: '취업준비생', description: '취업 준비 중이에요', icon: Search },
  { value: 'employed', label: '직장인', description: '현재 직장에 다니고 있어요', icon: Briefcase },
  { value: 'other', label: '기타', description: '그 외의 상황이에요', icon: User },
];

const TOPIC_OPTIONS = [
  { value: 'dp', label: 'DP', description: '동적 프로그래밍', icon: Layers },
  { value: 'graph', label: '그래프', description: 'BFS, DFS, 최단경로', icon: Network },
  { value: 'data_structure', label: '자료구조', description: '스택, 큐, 트리, 힙', icon: Binary },
  { value: 'sorting', label: '정렬', description: '퀵소트, 머지소트 등', icon: Hash },
  { value: 'greedy', label: '그리디', description: '탐욕 알고리즘', icon: Zap },
  { value: 'binary_search', label: '이분탐색', description: '탐색 알고리즘', icon: Search },
];

const DIFFICULTY_OPTIONS = [
  { value: 'easy', label: '실버', description: '기본기부터 천천히', color: 'text-gray-500' },
  { value: 'medium', label: '골드', description: '적당한 도전 (추천)', color: 'text-amber-500', recommended: true },
  { value: 'medium_hard', label: '플래티넘', description: '도전적인 난이도', color: 'text-cyan-500' },
  { value: 'hard', label: '다이아', description: '고난이도 문제', color: 'text-violet-500' },
];

export function OnboardingWizard({ onComplete, onSkip, initialData }: OnboardingWizardProps) {
  const [step, setStep] = useState(0);
  const [data, setData] = useState<OnboardingData>({
    experience_level: initialData?.experience_level || '',
    learning_goal: initialData?.learning_goal || '',
    current_status: initialData?.current_status || '',
    preferred_topics: initialData?.preferred_topics || [],
    preferred_difficulty: initialData?.preferred_difficulty || 'medium',
    preferred_language: initialData?.preferred_language || 'python',
  });

  const currentStep = STEPS[step];
  const isLastStep = step === STEPS.length - 1;
  const canProceed = () => {
    switch (step) {
      case 0: return !!data.experience_level;
      case 1: return !!data.learning_goal;
      case 2: return !!data.current_status;
      case 3: return data.preferred_topics.length > 0;
      case 4: return !!data.preferred_difficulty;
      default: return true;
    }
  };

  const handleNext = () => {
    if (isLastStep) {
      const completedData = { ...data, completed_at: new Date().toISOString() };
      // localStorage에 저장
      localStorage.setItem('user_profile', JSON.stringify(completedData));
      localStorage.setItem('onboarding_completed', 'true');
      onComplete(completedData);
    } else {
      setStep(step + 1);
    }
  };

  const handleBack = () => {
    if (step > 0) setStep(step - 1);
  };

  const handleSelect = (field: keyof OnboardingData, value: string) => {
    if (field === 'preferred_topics') {
      const topics = data.preferred_topics as string[];
      if (topics.includes(value)) {
        setData({ ...data, preferred_topics: topics.filter(t => t !== value) });
      } else if (topics.length < 3) {
        setData({ ...data, preferred_topics: [...topics, value] });
      }
    } else {
      setData({ ...data, [field]: value });
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="relative w-full max-w-lg mx-4 bg-card border border-border rounded-2xl shadow-2xl overflow-hidden"
      >
        {/* Progress bar */}
        <div className="absolute top-0 left-0 right-0 h-1 bg-muted">
          <motion.div
            className="h-full bg-primary"
            initial={{ width: 0 }}
            animate={{ width: `${((step + 1) / STEPS.length) * 100}%` }}
            transition={{ duration: 0.3 }}
          />
        </div>

        {/* Header */}
        <div className="px-6 pt-8 pb-4">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <div className="h-10 w-10 rounded-xl bg-primary/10 flex items-center justify-center">
                <currentStep.icon className="h-5 w-5 text-primary" />
              </div>
              <div>
                <p className="text-xs text-muted-foreground">Step {step + 1} of {STEPS.length}</p>
                <h2 className="text-lg font-bold">{currentStep.title}</h2>
              </div>
            </div>
            {onSkip && (
              <Button variant="ghost" size="sm" onClick={onSkip} className="text-muted-foreground">
                건너뛰기
              </Button>
            )}
          </div>

          {/* Step indicators */}
          <div className="flex gap-1.5 mb-6">
            {STEPS.map((s, i) => (
              <div
                key={s.id}
                className={cn(
                  "h-1.5 flex-1 rounded-full transition-colors",
                  i <= step ? "bg-primary" : "bg-muted"
                )}
              />
            ))}
          </div>
        </div>

        {/* Content */}
        <div className="px-6 pb-6">
          <AnimatePresence mode="wait">
            <motion.div
              key={step}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.2 }}
            >
              {step === 0 && (
                <StepContent
                  title="현재 알고리즘 실력이 어느 정도인가요?"
                  options={LEVEL_OPTIONS}
                  selectedValue={data.experience_level}
                  onSelect={(v) => handleSelect('experience_level', v)}
                />
              )}
              {step === 1 && (
                <StepContent
                  title="알고리즘 공부의 목표가 무엇인가요?"
                  options={GOAL_OPTIONS}
                  selectedValue={data.learning_goal}
                  onSelect={(v) => handleSelect('learning_goal', v)}
                />
              )}
              {step === 2 && (
                <StepContent
                  title="현재 어떤 상황이신가요?"
                  options={STATUS_OPTIONS}
                  selectedValue={data.current_status}
                  onSelect={(v) => handleSelect('current_status', v)}
                />
              )}
              {step === 3 && (
                <StepContent
                  title="어떤 주제를 연습하고 싶으신가요? (최대 3개)"
                  options={TOPIC_OPTIONS}
                  selectedValues={data.preferred_topics}
                  onSelect={(v) => handleSelect('preferred_topics', v)}
                  multi
                />
              )}
              {step === 4 && (
                <StepContent
                  title="어느 정도 난이도로 시작할까요?"
                  options={DIFFICULTY_OPTIONS}
                  selectedValue={data.preferred_difficulty}
                  onSelect={(v) => handleSelect('preferred_difficulty', v)}
                  showColors
                />
              )}
            </motion.div>
          </AnimatePresence>
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-border flex justify-between">
          <Button
            variant="outline"
            onClick={handleBack}
            disabled={step === 0}
            className="gap-1"
          >
            <ChevronLeft className="h-4 w-4" />
            이전
          </Button>
          <Button
            onClick={handleNext}
            disabled={!canProceed()}
            className="gap-1"
          >
            {isLastStep ? (
              <>
                완료
                <Check className="h-4 w-4" />
              </>
            ) : (
              <>
                다음
                <ChevronRight className="h-4 w-4" />
              </>
            )}
          </Button>
        </div>
      </motion.div>
    </div>
  );
}

interface StepContentProps {
  title: string;
  options: Array<{
    value: string;
    label: string;
    description: string;
    icon?: any;
    color?: string;
    recommended?: boolean;
  }>;
  selectedValue?: string;
  selectedValues?: string[];
  onSelect: (value: string) => void;
  multi?: boolean;
  showColors?: boolean;
}

function StepContent({
  title,
  options,
  selectedValue,
  selectedValues,
  onSelect,
  multi,
  showColors,
}: StepContentProps) {
  const isSelected = (value: string) =>
    multi ? selectedValues?.includes(value) : selectedValue === value;

  return (
    <div>
      <h3 className="text-base font-medium mb-4">{title}</h3>
      <div className="grid grid-cols-2 gap-3">
        {options.map((option) => {
          const Icon = option.icon;
          const selected = isSelected(option.value);

          return (
            <motion.button
              key={option.value}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => onSelect(option.value)}
              className={cn(
                "relative p-4 rounded-xl border-2 text-left transition-all",
                selected
                  ? "border-primary bg-primary/5"
                  : "border-border hover:border-primary/50 bg-card",
                showColors && option.color
              )}
            >
              {selected && (
                <div className="absolute top-2 right-2">
                  <Check className="h-4 w-4 text-primary" />
                </div>
              )}
              {option.recommended && (
                <span className="absolute top-2 right-2 text-[10px] px-1.5 py-0.5 rounded-full bg-primary/10 text-primary font-medium">
                  추천
                </span>
              )}
              <div className="flex items-start gap-3">
                {Icon && (
                  <div className={cn(
                    "h-8 w-8 rounded-lg flex items-center justify-center shrink-0",
                    selected ? "bg-primary/20" : "bg-muted"
                  )}>
                    <Icon className={cn("h-4 w-4", selected ? "text-primary" : "text-muted-foreground")} />
                  </div>
                )}
                <div className="min-w-0">
                  <p className={cn(
                    "font-medium text-sm",
                    showColors && option.color
                  )}>{option.label}</p>
                  <p className="text-xs text-muted-foreground line-clamp-2 mt-0.5">
                    {option.description}
                  </p>
                </div>
              </div>
            </motion.button>
          );
        })}
      </div>
    </div>
  );
}

/**
 * 온보딩 필요 여부 확인 훅
 */
export function useOnboardingCheck() {
  const [needsOnboarding, setNeedsOnboarding] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const completed = localStorage.getItem('onboarding_completed');
    const profile = localStorage.getItem('user_profile');

    // 온보딩 완료 기록이 없거나, 프로필이 불완전하면 온보딩 필요
    if (!completed || !profile) {
      setNeedsOnboarding(true);
    } else {
      try {
        const data = JSON.parse(profile);
        // 필수 필드 확인
        if (!data.experience_level || !data.learning_goal) {
          setNeedsOnboarding(true);
        }
      } catch {
        setNeedsOnboarding(true);
      }
    }
    setIsLoading(false);
  }, []);

  return { needsOnboarding, isLoading, setNeedsOnboarding };
}
