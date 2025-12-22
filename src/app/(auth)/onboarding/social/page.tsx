'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
import {
  Code2,
  Loader2,
  ChevronRight,
  ChevronLeft,
  GraduationCap,
  Briefcase,
  Building2,
  RefreshCw,
  Target,
  Building,
  TrendingUp,
  HelpCircle,
  Sprout,
  Leaf,
  TreeDeciduous,
  Trophy,
  Link as LinkIcon,
} from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { apiClient } from '@/lib/api/client';

// Onboarding data type
interface SocialOnboardingData {
  status: 'student' | 'job_seeker' | 'employed' | 'career_change' | null;
  goal: 'big_tech' | 'mid_startup' | 'skill_up' | 'unknown' | null;
  level: 'beginner' | 'elementary' | 'intermediate' | 'advanced' | 'unknown' | null;
  solvedAcId?: string;
  strongAlgorithms: string[];
}

// Step 1 options
const STATUS_OPTIONS = [
  { value: 'student', label: '학생', icon: GraduationCap, emoji: '🎓' },
  { value: 'job_seeker', label: '취준생', icon: Briefcase, emoji: '💼' },
  { value: 'employed', label: '현직자', icon: Building2, emoji: '👔' },
  { value: 'career_change', label: '전환', icon: RefreshCw, emoji: '🔄' },
];

// Step 2 options
const GOAL_OPTIONS = [
  { value: 'big_tech', label: '대기업 코딩테스트', sublabel: '카카오, 네이버 등', icon: Target },
  { value: 'mid_startup', label: '중견/스타트업 코딩테스트', sublabel: '', icon: Building },
  { value: 'skill_up', label: '코딩 실력 향상', sublabel: '', icon: TrendingUp },
  { value: 'unknown', label: '아직 잘 모르겠어요', sublabel: '', icon: HelpCircle },
];

// Step 3 options
const LEVEL_OPTIONS = [
  { value: 'beginner', label: '입문', sublabel: '거의 안 풀어봄', icon: Sprout, emoji: '🌱' },
  { value: 'elementary', label: '초급', sublabel: '백준 브론즈~실버 / 프로그래머스 Lv.1', icon: Leaf, emoji: '🌿' },
  { value: 'intermediate', label: '중급', sublabel: '백준 골드 / 프로그래머스 Lv.2', icon: TreeDeciduous, emoji: '🌳' },
  { value: 'advanced', label: '고급', sublabel: '백준 플래티넘+ / 프로그래머스 Lv.3+', icon: Trophy, emoji: '🏆' },
  { value: 'unknown', label: '잘 모르겠어요', sublabel: '간단한 테스트로 확인', icon: HelpCircle, emoji: '❓' },
];

// Step 4 options
const ALGORITHM_OPTIONS = [
  { value: 'implementation', label: '구현' },
  { value: 'dfs_bfs', label: 'DFS/BFS' },
  { value: 'dp', label: 'DP' },
  { value: 'graph', label: '그래프' },
  { value: 'greedy', label: '그리디' },
  { value: 'binary_search', label: '이분탐색' },
  { value: 'sorting', label: '정렬' },
  { value: 'string', label: '문자열' },
];

export default function SocialOnboardingPage() {
  const router = useRouter();
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(false);
  const [step, setStep] = useState(1);
  const totalSteps = 4;

  const [formData, setFormData] = useState<SocialOnboardingData>({
    status: null,
    goal: null,
    level: null,
    solvedAcId: '',
    strongAlgorithms: [],
  });

  // Check if user is authenticated
  useEffect(() => {
    if (!apiClient.isAuthenticated()) {
      router.push('/login');
    }
  }, [router]);

  const canProceed = () => {
    switch (step) {
      case 1:
        return !!formData.status;
      case 2:
        return !!formData.goal;
      case 3:
        return !!formData.level;
      case 4:
        return true; // Optional step
      default:
        return false;
    }
  };

  const handleNext = async () => {
    if (step === totalSteps) {
      await handleComplete();
      return;
    }

    if (canProceed()) {
      setStep((s) => Math.min(s + 1, totalSteps));
    }
  };

  const handleBack = () => {
    setStep((s) => Math.max(s - 1, 1));
  };

  const toggleAlgorithm = (algo: string) => {
    const current = formData.strongAlgorithms;
    if (current.includes(algo)) {
      setFormData({ ...formData, strongAlgorithms: current.filter((a) => a !== algo) });
    } else {
      setFormData({ ...formData, strongAlgorithms: [...current, algo] });
    }
  };

  const handleComplete = async () => {
    setIsLoading(true);

    try {
      // Update user preferences with onboarding data
      const response = await apiClient.request('/users/me/preferences', {
        method: 'PUT',
        body: {
          // Map onboarding data to preferences
          preferred_difficulty: formData.level === 'beginner' ? 'easy' :
                               formData.level === 'elementary' ? 'easy' :
                               formData.level === 'intermediate' ? 'medium' :
                               formData.level === 'advanced' ? 'hard' : 'medium',
        },
      });

      if (response.error) {
        console.warn('Failed to update preferences:', response.error);
      }

      toast({
        title: '설정 완료!',
        description: 'CodeFill에 오신 것을 환영합니다!',
      });

      router.push('/');
      router.refresh();
    } catch (error) {
      toast({
        title: '오류 발생',
        description: '설정 저장 중 문제가 발생했습니다.',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const renderStepContent = () => {
    switch (step) {
      case 1:
        return (
          <motion.div
            key="step1"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="space-y-6"
          >
            <div className="text-center">
              <h2 className="text-xl font-semibold">현재 상태가 어떻게 되세요?</h2>
              <p className="mt-1 text-sm text-muted-foreground">맞춤 학습을 위해 알려주세요</p>
            </div>

            <div className="grid grid-cols-2 gap-3">
              {STATUS_OPTIONS.map((option) => {
                const isSelected = formData.status === option.value;
                return (
                  <button
                    key={option.value}
                    type="button"
                    onClick={() => setFormData({ ...formData, status: option.value as SocialOnboardingData['status'] })}
                    className={`flex flex-col items-center gap-2 rounded-xl border-2 p-4 transition-all ${
                      isSelected
                        ? 'border-primary bg-primary/10 shadow-md'
                        : 'border-border bg-card hover:border-primary/50 hover:bg-secondary'
                    }`}
                  >
                    <span className="text-2xl">{option.emoji}</span>
                    <span className={`font-medium ${isSelected ? 'text-primary' : ''}`}>
                      {option.label}
                    </span>
                  </button>
                );
              })}
            </div>
          </motion.div>
        );

      case 2:
        return (
          <motion.div
            key="step2"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="space-y-6"
          >
            <div className="text-center">
              <h2 className="text-xl font-semibold">CodeFill로 무엇을 준비하시나요?</h2>
              <p className="mt-1 text-sm text-muted-foreground">목표에 맞는 문제를 추천해드려요</p>
            </div>

            <div className="space-y-3">
              {GOAL_OPTIONS.map((option) => {
                const Icon = option.icon;
                const isSelected = formData.goal === option.value;
                return (
                  <button
                    key={option.value}
                    type="button"
                    onClick={() => setFormData({ ...formData, goal: option.value as SocialOnboardingData['goal'] })}
                    className={`flex w-full items-center gap-4 rounded-xl border-2 p-4 text-left transition-all ${
                      isSelected
                        ? 'border-primary bg-primary/10 shadow-md'
                        : 'border-border bg-card hover:border-primary/50 hover:bg-secondary'
                    }`}
                  >
                    <div className={`rounded-full p-2 ${isSelected ? 'bg-primary/20' : 'bg-secondary'}`}>
                      <Icon className={`h-5 w-5 ${isSelected ? 'text-primary' : 'text-muted-foreground'}`} />
                    </div>
                    <div>
                      <div className={`font-medium ${isSelected ? 'text-primary' : ''}`}>
                        {option.label}
                      </div>
                      {option.sublabel && (
                        <div className="text-sm text-muted-foreground">{option.sublabel}</div>
                      )}
                    </div>
                  </button>
                );
              })}
            </div>
          </motion.div>
        );

      case 3:
        return (
          <motion.div
            key="step3"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="space-y-6"
          >
            <div className="text-center">
              <h2 className="text-xl font-semibold">현재 코딩테스트 경험이 어느 정도인가요?</h2>
              <p className="mt-1 text-sm text-muted-foreground">수준에 맞는 문제부터 시작해요</p>
            </div>

            <div className="space-y-3">
              {LEVEL_OPTIONS.map((option) => {
                const isSelected = formData.level === option.value;
                return (
                  <button
                    key={option.value}
                    type="button"
                    onClick={() => setFormData({ ...formData, level: option.value as SocialOnboardingData['level'] })}
                    className={`flex w-full items-center gap-4 rounded-xl border-2 p-4 text-left transition-all ${
                      isSelected
                        ? 'border-primary bg-primary/10 shadow-md'
                        : 'border-border bg-card hover:border-primary/50 hover:bg-secondary'
                    }`}
                  >
                    <span className="text-2xl">{option.emoji}</span>
                    <div className="flex-1">
                      <div className={`font-medium ${isSelected ? 'text-primary' : ''}`}>
                        {option.label}
                      </div>
                      <div className="text-sm text-muted-foreground">{option.sublabel}</div>
                    </div>
                  </button>
                );
              })}
            </div>
          </motion.div>
        );

      case 4:
        return (
          <motion.div
            key="step4"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="space-y-6"
          >
            <div className="text-center">
              <h2 className="text-xl font-semibold">더 정확한 추천을 위해</h2>
              <p className="mt-1 text-sm text-muted-foreground">선택사항이에요</p>
            </div>

            <div className="space-y-4">
              {/* solved.ac 연동 */}
              <div className="space-y-2">
                <Label className="flex items-center gap-2">
                  <LinkIcon className="h-4 w-4" />
                  백준 아이디 (solved.ac)
                </Label>
                <div className="flex gap-2">
                  <Input
                    placeholder="백준 아이디 입력"
                    className="bg-secondary"
                    value={formData.solvedAcId}
                    onChange={(e) => setFormData({ ...formData, solvedAcId: e.target.value })}
                  />
                  <Button type="button" variant="outline" disabled>
                    연동하기
                  </Button>
                </div>
                <p className="text-xs text-muted-foreground">
                  연동하면 풀이 기록을 기반으로 더 정확한 추천을 받을 수 있어요
                </p>
              </div>

              {/* 자신있는 알고리즘 */}
              <div className="space-y-2">
                <Label>자신있는 알고리즘 (다중선택)</Label>
                <div className="grid grid-cols-2 gap-2">
                  {ALGORITHM_OPTIONS.map((algo) => {
                    const isSelected = formData.strongAlgorithms.includes(algo.value);
                    return (
                      <button
                        key={algo.value}
                        type="button"
                        onClick={() => toggleAlgorithm(algo.value)}
                        className={`flex items-center gap-2 rounded-lg border p-3 text-sm transition-all ${
                          isSelected
                            ? 'border-primary bg-primary/10'
                            : 'border-border bg-secondary hover:border-primary/50'
                        }`}
                      >
                        <Checkbox checked={isSelected} className="pointer-events-none" />
                        <span>{algo.label}</span>
                      </button>
                    );
                  })}
                </div>
              </div>
            </div>
          </motion.div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-background p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md space-y-6"
      >
        {/* Logo */}
        <div className="text-center">
          <Link href="/" className="inline-flex items-center gap-2">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary">
              <Code2 className="h-5 w-5 text-primary-foreground" />
            </div>
            <span className="text-2xl font-bold">
              Code<span className="text-primary">Fill</span>
            </span>
          </Link>
          <p className="mt-2 text-muted-foreground">맞춤 학습을 위한 설정</p>
        </div>

        {/* Progress indicator */}
        <div className="flex items-center justify-center gap-2">
          {Array.from({ length: totalSteps }).map((_, i) => (
            <div
              key={i}
              className={`h-2 rounded-full transition-all ${
                i + 1 <= step ? 'w-8 bg-primary' : 'w-2 bg-muted'
              }`}
            />
          ))}
        </div>

        {/* Step indicator */}
        <p className="text-center text-sm text-muted-foreground">
          {step} / {totalSteps}
        </p>

        {/* Content */}
        <div className="rounded-xl border border-border bg-card p-6">
          <AnimatePresence mode="wait">{renderStepContent()}</AnimatePresence>
        </div>

        {/* Navigation */}
        <div className="flex gap-2">
          {step > 1 && (
            <Button
              type="button"
              variant="outline"
              className="flex-1"
              onClick={handleBack}
              disabled={isLoading}
            >
              <ChevronLeft className="mr-2 h-4 w-4" />
              이전
            </Button>
          )}
          <Button
            type="button"
            className="flex-1"
            onClick={handleNext}
            disabled={!canProceed() || isLoading}
          >
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                저장 중...
              </>
            ) : step === totalSteps ? (
              '시작하기'
            ) : (
              <>
                다음
                <ChevronRight className="ml-2 h-4 w-4" />
              </>
            )}
          </Button>
        </div>

        {/* Skip link */}
        <button
          type="button"
          onClick={() => {
            router.push('/');
            router.refresh();
          }}
          className="w-full text-center text-sm text-muted-foreground hover:text-primary"
        >
          나중에 설정하기
        </button>
      </motion.div>
    </div>
  );
}
