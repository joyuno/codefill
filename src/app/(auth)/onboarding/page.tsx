'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
import Image from 'next/image';
import {
  Loader2,
  Eye,
  EyeOff,
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
  Check,
  X,
} from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { useDebounce } from '@/hooks/useDebounce';
import { authApi, solvedacApi, tierToName, getTierColor, type SignupData, type SolvedAcProfile } from '@/lib/api';
import { ga4Events } from '@/lib/analytics';

// Onboarding data schema
const onboardingSchema = z.object({
  // Step 1: 현재 상태
  status: z.enum(['student', 'job_seeker', 'employed', 'career_change']),
  // Step 2: 목표
  goal: z.enum(['big_tech', 'mid_startup', 'skill_up', 'unknown']),
  // Step 3: 수준
  level: z.enum(['beginner', 'elementary', 'intermediate', 'advanced', 'unknown']),
  // Step 4: 추가 정보 (optional)
  solvedAcId: z.string().optional(),
  strongAlgorithms: z.array(z.string()).optional(),
  // Step 5: 회원 정보
  email: z.string().email('올바른 이메일 주소를 입력해주세요'),
  password: z
    .string()
    .min(8, '비밀번호는 최소 8자 이상이어야 합니다')
    .regex(/[a-zA-Z]/, '비밀번호에 영문자가 포함되어야 합니다')
    .regex(/[0-9]/, '비밀번호에 숫자가 포함되어야 합니다'),
  confirmPassword: z.string(),
  nickname: z.string().min(2, '닉네임은 최소 2자 이상이어야 합니다').max(20),
  desiredJob: z.string().max(20, '희망 직무는 20자 이내로 입력해주세요').optional(),
}).refine((data) => data.password === data.confirmPassword, {
  message: '비밀번호가 일치하지 않습니다',
  path: ['confirmPassword'],
});

type OnboardingData = z.infer<typeof onboardingSchema>;

// Step 1 options: 현재 상태
const STATUS_OPTIONS = [
  { value: 'student', label: '학생', icon: GraduationCap, emoji: '🎓' },
  { value: 'job_seeker', label: '취준생', icon: Briefcase, emoji: '💼' },
  { value: 'employed', label: '현직자', icon: Building2, emoji: '👔' },
  { value: 'career_change', label: '전환', icon: RefreshCw, emoji: '🔄' },
];

// Step 2 options: 목표
const GOAL_OPTIONS = [
  { value: 'big_tech', label: '대기업 코딩테스트', sublabel: '카카오, 네이버 등', icon: Target },
  { value: 'mid_startup', label: '중견/스타트업 코딩테스트', sublabel: '', icon: Building },
  { value: 'skill_up', label: '코딩 실력 향상', sublabel: '', icon: TrendingUp },
  { value: 'unknown', label: '아직 잘 모르겠어요', sublabel: '', icon: HelpCircle },
];

// Step 3 options: 수준
const LEVEL_OPTIONS = [
  { value: 'beginner', label: '입문', sublabel: '거의 안 풀어봄', icon: Sprout, emoji: '🌱' },
  { value: 'elementary', label: '초급', sublabel: '백준 브론즈~실버 / 프로그래머스 Lv.1', icon: Leaf, emoji: '🌿' },
  { value: 'intermediate', label: '중급', sublabel: '백준 골드 / 프로그래머스 Lv.2', icon: TreeDeciduous, emoji: '🌳' },
  { value: 'advanced', label: '고급', sublabel: '백준 플래티넘+ / 프로그래머스 Lv.3+', icon: Trophy, emoji: '🏆' },
  { value: 'unknown', label: '잘 모르겠어요', sublabel: '간단한 테스트로 확인', icon: HelpCircle, emoji: '❓' },
];

// Step 4 options: 알고리즘
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

export default function OnboardingPage() {
  const router = useRouter();
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [step, setStep] = useState(1);
  const totalSteps = 5;

  // Email/Nickname availability check states
  const [emailAvailable, setEmailAvailable] = useState<boolean | null>(null);
  const [emailChecking, setEmailChecking] = useState(false);
  const [emailMessage, setEmailMessage] = useState('');
  const [nicknameAvailable, setNicknameAvailable] = useState<boolean | null>(null);
  const [nicknameChecking, setNicknameChecking] = useState(false);
  const [nicknameMessage, setNicknameMessage] = useState('');

  // solved.ac verification states
  const [solvedAcVerifying, setSolvedAcVerifying] = useState(false);
  const [solvedAcProfile, setSolvedAcProfile] = useState<SolvedAcProfile | null>(null);
  const [solvedAcError, setSolvedAcError] = useState('');

  // GA4 온보딩 시작 이벤트
  useEffect(() => {
    ga4Events.onboardingStart();
  }, []);

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
    setValue,
    trigger,
  } = useForm<OnboardingData>({
    resolver: zodResolver(onboardingSchema),
    defaultValues: {
      strongAlgorithms: [],
    },
  });

  const watchedFields = watch();

  // Debounced values for API calls
  const debouncedEmail = useDebounce(watchedFields.email || '', 500);
  const debouncedNickname = useDebounce(watchedFields.nickname || '', 500);

  // Check email availability
  useEffect(() => {
    const checkEmail = async () => {
      if (!debouncedEmail || !debouncedEmail.includes('@')) {
        setEmailAvailable(null);
        setEmailMessage('');
        return;
      }

      setEmailChecking(true);
      try {
        const result = await authApi.checkEmail(debouncedEmail);
        if (result.data) {
          setEmailAvailable(result.data.available);
          setEmailMessage(result.data.message);
        }
      } catch (error) {
        setEmailAvailable(null);
        setEmailMessage('');
      } finally {
        setEmailChecking(false);
      }
    };

    checkEmail();
  }, [debouncedEmail]);

  // Check nickname availability
  useEffect(() => {
    const checkNickname = async () => {
      if (!debouncedNickname || debouncedNickname.length < 2) {
        setNicknameAvailable(null);
        setNicknameMessage('');
        return;
      }

      setNicknameChecking(true);
      try {
        const result = await authApi.checkNickname(debouncedNickname);
        if (result.data) {
          setNicknameAvailable(result.data.available);
          setNicknameMessage(result.data.message);
        }
      } catch (error) {
        setNicknameAvailable(null);
        setNicknameMessage('');
      } finally {
        setNicknameChecking(false);
      }
    };

    checkNickname();
  }, [debouncedNickname]);

  const canProceed = () => {
    switch (step) {
      case 1:
        return !!watchedFields.status;
      case 2:
        return !!watchedFields.goal;
      case 3:
        return !!watchedFields.level;
      case 4:
        return true; // Optional step
      case 5:
        return true; // Form validation handles this
      default:
        return false;
    }
  };

  const handleNext = async () => {
    if (step === 5) {
      const isValid = await trigger(['email', 'password', 'confirmPassword', 'nickname']);
      if (isValid) {
        handleSubmit(onSubmit)();
      }
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
    const current = watchedFields.strongAlgorithms || [];
    if (current.includes(algo)) {
      setValue('strongAlgorithms', current.filter((a) => a !== algo));
    } else {
      setValue('strongAlgorithms', [...current, algo]);
    }
  };

  const verifySolvedAc = async () => {
    const handle = watchedFields.solvedAcId?.trim();
    if (!handle) {
      setSolvedAcError('백준 아이디를 입력해주세요.');
      return;
    }

    setSolvedAcVerifying(true);
    setSolvedAcError('');
    setSolvedAcProfile(null);

    try {
      const result = await solvedacApi.lookup(handle);
      if (result.error) {
        setSolvedAcError(result.error.message);
        return;
      }
      if (result.data) {
        // 이미 다른 사용자가 연동한 경우 에러 표시
        if (result.data.isLinked) {
          setSolvedAcError(`'${result.data.handle}' 아이디는 이미 다른 사용자가 연동 중입니다.`);
          return;
        }
        setSolvedAcProfile(result.data);
        toast({
          title: '확인 완료',
          description: `${result.data.handle}님의 프로필을 확인했어요!`,
        });
      }
    } catch (error) {
      setSolvedAcError('프로필 조회 중 오류가 발생했습니다.');
    } finally {
      setSolvedAcVerifying(false);
    }
  };

  const clearSolvedAc = () => {
    setSolvedAcProfile(null);
    setSolvedAcError('');
    setValue('solvedAcId', '');
  };

  const onSubmit = async (data: OnboardingData) => {
    setIsLoading(true);

    try {
      const signupData: SignupData = {
        email: data.email,
        password: data.password,
        name: data.nickname,
        onboarding_data: {
          status: data.status,
          goal: data.goal,
          level: data.level,
          solved_ac_id: data.solvedAcId,
          strong_algorithms: data.strongAlgorithms,
          desired_job: data.desiredJob,
        },
      };

      const result = await authApi.signup(signupData);

      if (result.error) {
        toast({
          title: '회원가입 실패',
          description: result.error.message,
          variant: 'destructive',
        });
        return;
      }

      // 회원가입 성공 시 토큰이 자동으로 저장됨 (authApi.signup 내부에서 처리)
      if (result.data?.access_token) {
        // GA4 회원가입 이벤트
        ga4Events.signUp('email');
        ga4Events.onboardingComplete(0);

        toast({
          title: '회원가입 완료!',
          description: 'CodeFill에 오신 것을 환영합니다!',
        });

        // 자동 로그인되어 대시보드로 이동
        router.push('/');
      } else {
        // 예외 상황: 토큰이 없는 경우
        toast({
          title: '회원가입 완료',
          description: '로그인 페이지에서 로그인해주세요.',
        });
        router.push('/login');
      }
    } catch (error) {
      toast({
        title: '오류 발생',
        description: '회원가입 중 문제가 발생했습니다. 다시 시도해주세요.',
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
                const Icon = option.icon;
                const isSelected = watchedFields.status === option.value;
                return (
                  <button
                    key={option.value}
                    type="button"
                    onClick={() => setValue('status', option.value as OnboardingData['status'])}
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
                const isSelected = watchedFields.goal === option.value;
                return (
                  <button
                    key={option.value}
                    type="button"
                    onClick={() => setValue('goal', option.value as OnboardingData['goal'])}
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
                const isSelected = watchedFields.level === option.value;
                return (
                  <button
                    key={option.value}
                    type="button"
                    onClick={() => setValue('level', option.value as OnboardingData['level'])}
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
                {solvedAcProfile ? (
                  // 확인된 프로필 표시
                  <div className="rounded-lg border border-primary/30 bg-primary/5 p-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div
                          className="flex h-10 w-10 items-center justify-center rounded-full text-white font-bold text-sm"
                          style={{ backgroundColor: getTierColor(solvedAcProfile.tier) }}
                        >
                          {tierToName(solvedAcProfile.tier).split(' ')[0][0]}
                        </div>
                        <div>
                          <div className="font-medium">{solvedAcProfile.handle}</div>
                          <div className="flex items-center gap-2 text-xs text-muted-foreground">
                            <span style={{ color: getTierColor(solvedAcProfile.tier) }}>
                              {tierToName(solvedAcProfile.tier)}
                            </span>
                            <span>|</span>
                            <span>{solvedAcProfile.solvedCount}문제</span>
                            <span>|</span>
                            <span>Rating {solvedAcProfile.rating}</span>
                          </div>
                        </div>
                      </div>
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={clearSolvedAc}
                        className="text-muted-foreground hover:text-destructive"
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                ) : (
                  // 입력 폼
                  <>
                    <div className="flex gap-2">
                      <Input
                        placeholder="백준 아이디 입력"
                        className={`bg-secondary ${solvedAcError ? 'border-destructive' : ''}`}
                        disabled={solvedAcVerifying}
                        {...register('solvedAcId')}
                      />
                      <Button
                        type="button"
                        variant="outline"
                        onClick={verifySolvedAc}
                        disabled={solvedAcVerifying || !watchedFields.solvedAcId?.trim()}
                      >
                        {solvedAcVerifying ? (
                          <Loader2 className="h-4 w-4 animate-spin" />
                        ) : (
                          '확인'
                        )}
                      </Button>
                    </div>
                    {solvedAcError && (
                      <p className="text-sm text-destructive">{solvedAcError}</p>
                    )}
                  </>
                )}
                <p className="text-xs text-muted-foreground">
                  연동하면 풀이 기록을 기반으로 더 정확한 추천을 받을 수 있어요
                </p>
              </div>

              {/* 자신있는 알고리즘 */}
              <div className="space-y-2">
                <Label>자신있는 알고리즘 (다중선택)</Label>
                <div className="grid grid-cols-2 gap-2">
                  {ALGORITHM_OPTIONS.map((algo) => {
                    const isSelected = (watchedFields.strongAlgorithms || []).includes(algo.value);
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

            <button
              type="button"
              onClick={() => setStep(5)}
              className="w-full text-center text-sm text-muted-foreground hover:text-primary"
            >
              건너뛰기
            </button>
          </motion.div>
        );

      case 5:
        return (
          <motion.div
            key="step5"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="space-y-6"
          >
            <div className="text-center">
              <h2 className="text-xl font-semibold">마지막으로 가입 정보를 입력해주세요</h2>
              <p className="mt-1 text-sm text-muted-foreground">거의 다 왔어요!</p>
            </div>

            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email">이메일</Label>
                <div className="relative">
                  <Input
                    id="email"
                    type="email"
                    placeholder="you@example.com"
                    className={`bg-secondary pr-10 ${
                      emailAvailable === true ? 'border-green-500' :
                      emailAvailable === false ? 'border-destructive' : ''
                    }`}
                    disabled={isLoading}
                    {...register('email')}
                  />
                  <div className="absolute right-3 top-1/2 -translate-y-1/2">
                    {emailChecking ? (
                      <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
                    ) : emailAvailable === true ? (
                      <Check className="h-4 w-4 text-green-500" />
                    ) : emailAvailable === false ? (
                      <X className="h-4 w-4 text-destructive" />
                    ) : null}
                  </div>
                </div>
                {errors.email && (
                  <p className="text-sm text-destructive">{errors.email.message}</p>
                )}
                {!errors.email && emailMessage && (
                  <p className={`text-sm ${emailAvailable ? 'text-green-500' : 'text-destructive'}`}>
                    {emailMessage}
                  </p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="password">비밀번호</Label>
                <div className="relative">
                  <Input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    placeholder="영문, 숫자 포함 8자 이상"
                    className="bg-secondary pr-10"
                    disabled={isLoading}
                    {...register('password')}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                  >
                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
                {errors.password && (
                  <p className="text-sm text-destructive">{errors.password.message}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="confirmPassword">비밀번호 확인</Label>
                <Input
                  id="confirmPassword"
                  type="password"
                  placeholder="비밀번호 재입력"
                  className="bg-secondary"
                  disabled={isLoading}
                  {...register('confirmPassword')}
                />
                {errors.confirmPassword && (
                  <p className="text-sm text-destructive">{errors.confirmPassword.message}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="nickname">닉네임</Label>
                <div className="relative">
                  <Input
                    id="nickname"
                    placeholder="닉네임을 입력해주세요"
                    className={`bg-secondary pr-10 ${
                      nicknameAvailable === true ? 'border-green-500' :
                      nicknameAvailable === false ? 'border-destructive' : ''
                    }`}
                    disabled={isLoading}
                    {...register('nickname')}
                  />
                  <div className="absolute right-3 top-1/2 -translate-y-1/2">
                    {nicknameChecking ? (
                      <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
                    ) : nicknameAvailable === true ? (
                      <Check className="h-4 w-4 text-green-500" />
                    ) : nicknameAvailable === false ? (
                      <X className="h-4 w-4 text-destructive" />
                    ) : null}
                  </div>
                </div>
                {errors.nickname && (
                  <p className="text-sm text-destructive">{errors.nickname.message}</p>
                )}
                {!errors.nickname && nicknameMessage && (
                  <p className={`text-sm ${nicknameAvailable ? 'text-green-500' : 'text-destructive'}`}>
                    {nicknameMessage}
                  </p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="desiredJob">희망 직무 (선택)</Label>
                <Input
                  id="desiredJob"
                  placeholder="예: 백엔드 개발자"
                  className="bg-secondary"
                  disabled={isLoading}
                  {...register('desiredJob')}
                />
                {errors.desiredJob && (
                  <p className="text-sm text-destructive">{errors.desiredJob.message}</p>
                )}
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
          <Link href="/" className="inline-flex items-center justify-center">
            <Image
              src="/logo.png"
              alt="CodeFill"
              width={270}
              height={72}
              className="h-[72px] w-auto"
              priority
            />
          </Link>
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
                가입 중...
              </>
            ) : step === totalSteps ? (
              '가입 완료'
            ) : (
              <>
                다음
                <ChevronRight className="ml-2 h-4 w-4" />
              </>
            )}
          </Button>
        </div>

        {/* Login link */}
        <p className="text-center text-sm text-muted-foreground">
          이미 계정이 있으신가요?{' '}
          <Link href="/login" className="text-primary hover:underline">
            로그인
          </Link>
        </p>
      </motion.div>
    </div>
  );
}
