'use client';

import { useState, useEffect, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';
import { cn } from '@/lib/utils';
import { usersApi, publicProfileApi, type DateActivityDetail } from '@/lib/api';
import { Calendar, Code, Zap, Loader2, X } from 'lucide-react';
import { format } from 'date-fns';
import { ko } from 'date-fns/locale';
import { useAuth } from '@/hooks/useAuth';

interface ActivityDay {
  date: string;
  count: number;
  intensity: 0 | 1 | 2 | 3 | 4;
}

interface GrassHeatmapProps {
  compact?: boolean;
  /** 조회할 사용자 username. 없으면 본인 */
  username?: string;
  /** 부모에서 전달받은 공개 활동 데이터 (있으면 API 호출 안 함) */
  publicActivityData?: {
    days: Array<{ date?: string; activity_date?: string; problems_solved?: number; count?: number }>;
    totalDays?: number;
  };
}

const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

// GitHub 스타일 색상
const intensityColors = {
  0: 'bg-[#ebedf0] dark:bg-[#161b22]',
  1: 'bg-[#9be9a8] dark:bg-[#0e4429]',
  2: 'bg-[#40c463] dark:bg-[#006d32]',
  3: 'bg-[#30a14e] dark:bg-[#26a641]',
  4: 'bg-[#216e39] dark:bg-[#39d353]',
};

function calculateIntensity(count: number): 0 | 1 | 2 | 3 | 4 {
  // 절대적 기준으로 색상 결정
  // 0문제: 검은색 (배경)
  // 1-2문제: 약간 초록
  // 3-4문제: 꽤 초록
  // 5-6문제: 초록
  // 7문제 이상: 진한 초록
  if (count === 0) return 0;
  if (count <= 2) return 1;  // 1-2문제: 약간 초록
  if (count <= 4) return 2;  // 3-4문제: 꽤 초록
  if (count <= 6) return 3;  // 5-6문제: 초록
  return 4;                   // 7문제 이상: 진한 초록
}

function generateEmptyYear(): ActivityDay[] {
  const days: ActivityDay[] = [];
  const today = new Date();
  const oneYearAgo = new Date(today);
  oneYearAgo.setFullYear(today.getFullYear() - 1);

  // 1년 전 날짜가 속한 주의 일요일부터 시작
  const startDate = new Date(oneYearAgo);
  startDate.setDate(startDate.getDate() - startDate.getDay());

  const current = new Date(startDate);
  while (current <= today) {
    days.push({
      date: current.toISOString().split('T')[0],
      count: 0,
      intensity: 0,
    });
    current.setDate(current.getDate() + 1);
  }

  return days;
}

// 난이도 색상
const difficultyColors: Record<string, string> = {
  easy: 'text-green-500',
  medium: 'text-yellow-500',
  hard: 'text-red-500',
};

// 문제 타입 라벨
const problemTypeLabels: Record<string, string> = {
  blank: '빈칸 채우기',
  bug: '버그 찾기',
  output: '출력 예측',
  refactor: '리팩토링',
};

export function GrassHeatmap({ compact = false, username, publicActivityData }: GrassHeatmapProps) {
  const { profile } = useAuth();
  const [activityData, setActivityData] = useState<ActivityDay[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedDate, setSelectedDate] = useState<string | null>(null);
  const [dateDetail, setDateDetail] = useState<DateActivityDetail | null>(null);
  const [isLoadingDetail, setIsLoadingDetail] = useState(false);

  // 본인 프로필인지 확인
  const isOwnProfile = !username || (profile?.username === username);

  // 오늘 날짜 상세 자동 로드 여부 추적
  const [hasAutoLoadedToday, setHasAutoLoadedToday] = useState(false);

  useEffect(() => {
    // 데이터 처리 함수
    function processActivityData(response: { days?: Array<{ date?: string; activity_date?: string; problems_solved?: number; count?: number }> } | Array<{ date?: string; activity_date?: string; problems_solved?: number; count?: number }>) {
      // 빈 1년치 데이터 생성
      const emptyYear = generateEmptyYear();

      // 백엔드 응답을 Map으로 변환 (date -> problems_solved)
      const activityMap = new Map<string, number>();
      const days = (response as { days?: Array<unknown> })?.days || response || [];

      if (Array.isArray(days)) {
        days.forEach((day: { date?: string; activity_date?: string; problems_solved?: number; count?: number }) => {
          const date = day.date || day.activity_date;
          const count = day.problems_solved ?? day.count ?? 0;
          if (date) {
            activityMap.set(date, count);
          }
        });
      }

      // 데이터 채우기 (절대적 기준으로 intensity 계산)
      const filledData = emptyYear.map((day) => {
        const count = activityMap.get(day.date) || 0;
        return {
          ...day,
          count,
          intensity: calculateIntensity(count),
        };
      });

      return filledData;
    }

    // publicActivityData가 있으면 사용
    if (username && publicActivityData) {
      setActivityData(processActivityData(publicActivityData));
      setIsLoading(false);
      return;
    }

    // 없으면 API 호출
    async function fetchActivity() {
      try {
        setIsLoading(true);

        // username이 있으면 타인, 없으면 본인
        const response = username
          ? await publicProfileApi.getActivity(username, 365)
          : await usersApi.getActivity(365);

        setActivityData(processActivityData(response));
      } catch (err) {
        console.error('Failed to load activity data:', err);
        // 에러 시 빈 데이터 사용
        setActivityData(generateEmptyYear());
      } finally {
        setIsLoading(false);
      }
    }

    fetchActivity();
  }, [username, publicActivityData]);

  // 페이지 로드 시 오늘 날짜 상세 자동 로드 (compact 모드 제외, Full 버전에서만)
  useEffect(() => {
    // compact 모드이거나, 아직 로딩 중이거나, 데이터가 없거나, 이미 자동 로드했으면 스킵
    if (compact || isLoading || activityData.length === 0 || hasAutoLoadedToday) return;

    const today = new Date().toISOString().split('T')[0];
    const todayData = activityData.find(day => day.date === today);

    if (todayData) {
      // 오늘 날짜 자동 선택 및 상세 로드
      const loadTodayDetail = async () => {
        setSelectedDate(today);
        setIsLoadingDetail(true);
        setHasAutoLoadedToday(true);

        try {
          const detail = isOwnProfile
            ? await usersApi.getActivityByDate(today)
            : await publicProfileApi.getActivityByDate(username!, today);
          setDateDetail(detail);
        } catch (err) {
          console.error('Failed to load today detail:', err);
        } finally {
          setIsLoadingDetail(false);
        }
      };

      loadTodayDetail();
    }
  }, [isLoading, activityData, compact, isOwnProfile, username, hasAutoLoadedToday]);

  // 날짜 클릭 핸들러
  const handleDateClick = async (day: ActivityDay) => {
    if (selectedDate === day.date) {
      // 같은 날짜 클릭 시 닫기
      setSelectedDate(null);
      setDateDetail(null);
      return;
    }

    setSelectedDate(day.date);
    setIsLoadingDetail(true);
    setDateDetail(null);

    try {
      // 본인 프로필이면 /me/activity/{date}, 타인이면 /{username}/public-activity/{date}
      const detail = isOwnProfile
        ? await usersApi.getActivityByDate(day.date)
        : await publicProfileApi.getActivityByDate(username!, day.date);
      setDateDetail(detail);
    } catch (err) {
      console.error('Failed to load date detail:', err);
    } finally {
      setIsLoadingDetail(false);
    }
  };

  // 선택 닫기
  const handleCloseDetail = () => {
    setSelectedDate(null);
    setDateDetail(null);
  };

  // 총 기여 수
  const totalContributions = useMemo(
    () => activityData.reduce((sum, day) => sum + day.count, 0),
    [activityData]
  );

  // 오늘 푼 문제 수
  const todaySolved = useMemo(() => {
    const today = new Date().toISOString().split('T')[0];
    const todayData = activityData.find(day => day.date === today);
    return todayData?.count || 0;
  }, [activityData]);

  // 현재 연도
  const currentYear = new Date().getFullYear();

  // 주별로 그룹화 (열 = 주, 행 = 요일)
  const weeks = useMemo(() => {
    const result: ActivityDay[][] = [];
    let currentWeek: ActivityDay[] = [];

    activityData.forEach((day) => {
      const dayOfWeek = new Date(day.date).getDay();

      // 일요일(0)이면 새 주 시작
      if (dayOfWeek === 0 && currentWeek.length > 0) {
        result.push(currentWeek);
        currentWeek = [];
      }

      currentWeek.push(day);
    });

    if (currentWeek.length > 0) {
      result.push(currentWeek);
    }

    return result;
  }, [activityData]);

  // 월 라벨 위치 계산
  const monthLabels = useMemo(() => {
    const labels: { month: string; weekIndex: number }[] = [];
    let lastMonth = -1;

    weeks.forEach((week, weekIndex) => {
      const firstDay = week[0];
      if (firstDay) {
        const date = new Date(firstDay.date);
        const month = date.getMonth();

        if (month !== lastMonth) {
          labels.push({
            month: MONTHS[month],
            weekIndex,
          });
          lastMonth = month;
        }
      }
    });

    return labels;
  }, [weeks]);

  // Compact 버전 (사이드바용)
  if (compact) {
    const recentWeeks = weeks.slice(-12);
    const recentContributions = recentWeeks.flat().reduce((sum, day) => sum + day.count, 0);

    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="rounded-xl border border-border bg-card p-4"
      >
        <div className="flex items-center justify-between mb-3">
          <div>
            <h3 className="text-sm font-semibold">학습 활동</h3>
            <p className="text-xs text-muted-foreground mt-0.5">
              최근 {recentContributions}문제 해결
            </p>
          </div>
        </div>

        <div className="overflow-x-auto">
          <div className="flex gap-[3px]">
            {recentWeeks.map((week, weekIndex) => (
              <div key={weekIndex} className="flex flex-col gap-[3px]">
                {week.map((day) => (
                  <Tooltip key={day.date}>
                    <TooltipTrigger asChild>
                      <div
                        className={cn(
                          'h-[10px] w-[10px] rounded-sm',
                          intensityColors[day.intensity]
                        )}
                      />
                    </TooltipTrigger>
                    <TooltipContent>
                      <p className="font-medium">{day.count} 문제 해결</p>
                      <p className="text-xs text-muted-foreground">{day.date}</p>
                    </TooltipContent>
                  </Tooltip>
                ))}
              </div>
            ))}
          </div>
        </div>

        <div className="flex items-center justify-end gap-1 mt-3 text-xs text-muted-foreground">
          <span>Less</span>
          {[0, 1, 2, 3, 4].map((i) => (
            <div
              key={i}
              className={cn('h-[10px] w-[10px] rounded-sm', intensityColors[i as 0 | 1 | 2 | 3 | 4])}
            />
          ))}
          <span>More</span>
        </div>
      </motion.div>
    );
  }

  // Full 버전 (GitHub 스타일)
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="rounded-xl border border-border bg-card p-5"
    >
      {/* 헤더: "Today solved N problems" */}
      <h3 className="text-sm font-medium text-muted-foreground mb-2">
        {isLoading ? (
          'Loading...'
        ) : (
          <>Today solved {todaySolved} problem{todaySolved !== 1 ? 's' : ''}</>
        )}
      </h3>

      {/* 메인 그리드 */}
      <div className="overflow-x-auto">
        <div className="inline-block">
          {/* 월 라벨 */}
          <div className="flex mb-1" style={{ marginLeft: '32px' }}>
            {monthLabels.map((label, index) => {
              const nextLabel = monthLabels[index + 1];
              const width = nextLabel
                ? (nextLabel.weekIndex - label.weekIndex) * 14
                : (weeks.length - label.weekIndex) * 14;

              return (
                <div
                  key={`${label.month}-${index}`}
                  className="text-xs text-muted-foreground"
                  style={{ width: `${Math.max(width, 28)}px` }}
                >
                  {label.month}
                </div>
              );
            })}
          </div>

          {/* 그리드 + 요일 라벨 */}
          <div className="flex">
            {/* 요일 라벨 (Mon, Wed, Fri만 표시) */}
            <div className="flex flex-col gap-[3px] pr-2" style={{ paddingTop: '0px' }}>
              {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((day, index) => (
                <div
                  key={day}
                  className="h-[11px] flex items-center"
                >
                  <span
                    className={cn(
                      'text-xs text-muted-foreground leading-none',
                      // GitHub처럼 Mon, Wed, Fri만 표시
                      index === 1 || index === 3 || index === 5 ? '' : 'invisible'
                    )}
                    style={{ fontSize: '10px' }}
                  >
                    {day}
                  </span>
                </div>
              ))}
            </div>

            {/* 주별 그리드 */}
            <div className="flex gap-[3px]">
              {weeks.map((week, weekIndex) => (
                <div key={weekIndex} className="flex flex-col gap-[3px]">
                  {/* 첫 주가 일요일부터 시작하지 않으면 빈 칸으로 패딩 */}
                  {weekIndex === 0 &&
                    week.length < 7 &&
                    Array(7 - week.length)
                      .fill(null)
                      .map((_, i) => (
                        <div key={`pad-${i}`} className="h-[11px] w-[11px]" />
                      ))}
                  {week.map((day) => (
                    <Tooltip key={day.date}>
                      <TooltipTrigger asChild>
                        <div
                          onClick={() => handleDateClick(day)}
                          className={cn(
                            'h-[11px] w-[11px] rounded-[2px] transition-transform hover:scale-125 cursor-pointer',
                            intensityColors[day.intensity],
                            selectedDate === day.date && 'ring-2 ring-primary ring-offset-1'
                          )}
                        />
                      </TooltipTrigger>
                      <TooltipContent>
                        <p className="font-medium">
                          {day.count === 0
                            ? 'No contributions'
                            : `${day.count} contribution${day.count > 1 ? 's' : ''}`}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {new Date(day.date).toLocaleDateString('en-US', {
                            weekday: 'long',
                            month: 'short',
                            day: 'numeric',
                            year: 'numeric',
                          })}
                        </p>
                      </TooltipContent>
                    </Tooltip>
                  ))}
                </div>
              ))}
            </div>
          </div>

          {/* 범례: Less □□□□□ More */}
          <div className="flex items-center justify-end gap-1 mt-2 text-xs text-muted-foreground">
            <span>Less</span>
            {[0, 1, 2, 3, 4].map((i) => (
              <div
                key={i}
                className={cn(
                  'h-[11px] w-[11px] rounded-[2px]',
                  intensityColors[i as 0 | 1 | 2 | 3 | 4]
                )}
              />
            ))}
            <span>More</span>
          </div>
        </div>
      </div>

      {/* 선택된 날짜 상세 패널 */}
      <AnimatePresence>
        {selectedDate && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="overflow-hidden"
          >
            <div className="mt-4 pt-4 border-t border-border">
              {/* 헤더 */}
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <Calendar className="h-4 w-4 text-primary" />
                  <span className="font-medium">
                    {format(new Date(selectedDate), 'yyyy년 M월 d일 (EEEE)', { locale: ko })}
                  </span>
                </div>
                <button
                  onClick={handleCloseDetail}
                  className="p-1 hover:bg-muted rounded-md transition-colors"
                >
                  <X className="h-4 w-4 text-muted-foreground" />
                </button>
              </div>

              {/* 로딩 */}
              {isLoadingDetail && (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
                </div>
              )}

              {/* 상세 내용 */}
              {!isLoadingDetail && dateDetail && (
                <div className="space-y-3">
                  {/* 요약 통계 */}
                  <div className="flex gap-4 text-sm">
                    <div className="flex items-center gap-1.5">
                      <Code className="h-4 w-4 text-green-500" />
                      <span className="text-muted-foreground">문제 해결:</span>
                      <span className="font-medium">{dateDetail.problems_solved}개</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <Zap className="h-4 w-4 text-yellow-500" />
                      <span className="text-muted-foreground">획득 XP:</span>
                      <span className="font-medium">{dateDetail.xp_earned}</span>
                    </div>
                  </div>

                  {/* 문제 목록 */}
                  {dateDetail.problems.length > 0 ? (
                    <div className="space-y-2">
                      <p className="text-xs text-muted-foreground font-medium">풀이한 문제</p>
                      <div className="space-y-1.5">
                        {dateDetail.problems.map((problem) => (
                          <div
                            key={problem.id}
                            className="flex items-center justify-between p-2.5 bg-muted/50 rounded-lg text-sm"
                          >
                            <div className="flex items-center gap-2">
                              <span className={cn('text-xs font-medium', difficultyColors[problem.difficulty])}>
                                {problem.difficulty.toUpperCase()}
                              </span>
                              <span className="font-medium">{problem.name}</span>
                              <span className="text-xs text-muted-foreground">
                                {problemTypeLabels[problem.problem_type] || problem.problem_type}
                              </span>
                            </div>
                            <div className="flex items-center gap-2 text-xs text-muted-foreground">
                              <span>+{problem.xp_earned} XP</span>
                              <span>{format(new Date(problem.solved_at), 'HH:mm')}</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  ) : (
                    <p className="text-sm text-muted-foreground py-4 text-center">
                      이 날에는 풀이한 문제가 없습니다.
                    </p>
                  )}
                </div>
              )}

              {/* 데이터 없음 */}
              {!isLoadingDetail && !dateDetail && (
                <p className="text-sm text-muted-foreground py-4 text-center">
                  데이터를 불러올 수 없습니다.
                </p>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
