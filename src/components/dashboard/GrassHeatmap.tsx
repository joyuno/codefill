'use client';

import { useState, useEffect, useMemo } from 'react';
import { motion } from 'framer-motion';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';
import { cn } from '@/lib/utils';
import { usersApi } from '@/lib/api';

interface ActivityDay {
  date: string;
  count: number;
  intensity: 0 | 1 | 2 | 3 | 4;
}

interface GrassHeatmapProps {
  compact?: boolean;
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

function calculateIntensity(count: number, maxCount: number): 0 | 1 | 2 | 3 | 4 {
  if (count === 0) return 0;
  if (maxCount === 0) return 0;
  const ratio = count / maxCount;
  if (ratio <= 0.25) return 1;
  if (ratio <= 0.5) return 2;
  if (ratio <= 0.75) return 3;
  return 4;
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

export function GrassHeatmap({ compact = false }: GrassHeatmapProps) {
  const [activityData, setActivityData] = useState<ActivityDay[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function fetchActivity() {
      try {
        setIsLoading(true);
        const response = await usersApi.getActivity(365);

        // 빈 1년치 데이터 생성
        const emptyYear = generateEmptyYear();

        // 백엔드 응답을 Map으로 변환 (date -> problems_solved)
        const activityMap = new Map<string, number>();
        const days = response?.days || response || [];

        if (Array.isArray(days)) {
          days.forEach((day: { date?: string; activity_date?: string; problems_solved?: number; count?: number }) => {
            const date = day.date || day.activity_date;
            const count = day.problems_solved ?? day.count ?? 0;
            if (date) {
              activityMap.set(date, count);
            }
          });
        }

        // 최대값 계산 (intensity 계산용)
        const maxCount = Math.max(...Array.from(activityMap.values()), 1);

        // 데이터 채우기
        const filledData = emptyYear.map((day) => {
          const count = activityMap.get(day.date) || 0;
          return {
            ...day,
            count,
            intensity: calculateIntensity(count, maxCount),
          };
        });

        setActivityData(filledData);
      } catch (err) {
        console.error('Failed to load activity data:', err);
        // 에러 시 빈 데이터 사용
        setActivityData(generateEmptyYear());
      } finally {
        setIsLoading(false);
      }
    }

    fetchActivity();
  }, []);

  // 총 기여 수
  const totalContributions = useMemo(
    () => activityData.reduce((sum, day) => sum + day.count, 0),
    [activityData]
  );

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
      {/* 헤더: "N contributions in YYYY" */}
      <h3 className="text-sm font-medium text-muted-foreground mb-2">
        {isLoading ? (
          'Loading...'
        ) : (
          <>{totalContributions.toLocaleString()} contributions in {currentYear}</>
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
                          className={cn(
                            'h-[11px] w-[11px] rounded-[2px] transition-transform hover:scale-125 cursor-pointer',
                            intensityColors[day.intensity]
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
    </motion.div>
  );
}
