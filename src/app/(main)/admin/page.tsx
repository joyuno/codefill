'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Users, FileText, Activity, TrendingUp, ArrowRight, ArrowUpRight, UserPlus } from 'lucide-react';
import Link from 'next/link';
import { adminApi, type AdminDashboardStats } from '@/lib/api/admin';

export default function AdminDashboardPage() {
  const [stats, setStats] = useState<AdminDashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const data = await adminApi.getDashboardStats();
        setStats(data);
      } catch (error) {
        console.error('Failed to fetch dashboard stats:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  const statCards = [
    {
      title: '전체 사용자',
      value: stats?.total_users ?? 0,
      icon: Users,
      href: '/admin/users',
      color: 'hsl(199 89% 48%)',
      gradient: 'from-blue-500/20 to-blue-600/5',
    },
    {
      title: '전체 문제',
      value: stats?.total_problems ?? 0,
      icon: FileText,
      href: '/admin/problems',
      color: 'hsl(142 71% 45%)',
      gradient: 'from-emerald-500/20 to-emerald-600/5',
    },
    {
      title: '전체 제출',
      value: stats?.total_submissions ?? 0,
      icon: Activity,
      href: null,
      color: 'hsl(280 100% 70%)',
      gradient: 'from-purple-500/20 to-purple-600/5',
    },
    {
      title: '오늘 활성 사용자',
      value: stats?.active_users_today ?? 0,
      icon: TrendingUp,
      href: null,
      color: 'hsl(38 92% 50%)',
      gradient: 'from-orange-500/20 to-orange-600/5',
    },
  ];

  return (
    <div className="space-y-8">
      {/* Stats Grid */}
      <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {statCards.map((stat, i) => {
          const Icon = stat.icon;
          const content = (
            <div
              className="admin-glass-card admin-stat-card group rounded-2xl p-5 transition-all duration-300"
              style={{
                '--stat-color': stat.color,
                '--stat-glow': stat.color.replace(')', ' / 0.1)'),
              } as React.CSSProperties}
            >
              <div className="relative z-10 flex items-start justify-between">
                <div
                  className={`flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br ${stat.gradient}`}
                >
                  <Icon className="h-5 w-5" style={{ color: stat.color }} />
                </div>
                {stat.href && (
                  <ArrowUpRight
                    className="h-4 w-4 text-muted-foreground/40 transition-all group-hover:text-foreground group-hover:translate-x-0.5 group-hover:-translate-y-0.5"
                  />
                )}
              </div>
              <div className="relative z-10 mt-4">
                {loading ? (
                  <div className="h-9 w-24 animate-pulse rounded-lg bg-white/5" />
                ) : (
                  <p className="admin-stat-value text-3xl font-bold tracking-tight">
                    {stat.value.toLocaleString()}
                  </p>
                )}
                <p className="mt-1 text-sm text-muted-foreground/80">{stat.title}</p>
              </div>
            </div>
          );

          return (
            <motion.div
              key={stat.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1, duration: 0.4 }}
            >
              {stat.href ? (
                <Link href={stat.href} className="block">
                  {content}
                </Link>
              ) : (
                content
              )}
            </motion.div>
          );
        })}
      </div>

      {/* New Users This Week - Highlight Card */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4, duration: 0.4 }}
        className="admin-glass-card rounded-2xl p-6"
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-primary/20 to-primary/5">
              <UserPlus className="h-6 w-6 text-primary" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground/80">이번 주 신규 가입</p>
              {loading ? (
                <div className="h-8 w-16 animate-pulse rounded-lg bg-white/5 mt-1" />
              ) : (
                <p className="text-2xl font-bold tracking-tight">
                  +{stats?.new_users_this_week ?? 0}
                  <span className="text-sm font-normal text-muted-foreground ml-1">명</span>
                </p>
              )}
            </div>
          </div>
          <Link
            href="/admin/users"
            className="flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground transition-colors"
          >
            자세히 보기
            <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      </motion.div>

      {/* Divider */}
      <div className="admin-divider" />

      {/* Quick Actions */}
      <div>
        <div className="admin-section-header">
          <h2 className="text-lg font-semibold">빠른 작업</h2>
        </div>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="grid gap-4 sm:grid-cols-2"
        >
          <Link href="/admin/users">
            <div className="admin-list-item group">
              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500/20 to-blue-600/5">
                <Users className="h-6 w-6 text-blue-400" />
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="font-semibold text-foreground/90">사용자 관리</h3>
                <p className="text-sm text-muted-foreground/70 truncate">
                  사용자 목록 조회, 역할 변경, 계정 정지
                </p>
              </div>
              <ArrowRight className="h-5 w-5 text-muted-foreground/40 transition-all group-hover:text-foreground group-hover:translate-x-1" />
            </div>
          </Link>

          <Link href="/admin/problems">
            <div className="admin-list-item group">
              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-emerald-500/20 to-emerald-600/5">
                <FileText className="h-6 w-6 text-emerald-400" />
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="font-semibold text-foreground/90">문제 관리</h3>
                <p className="text-sm text-muted-foreground/70 truncate">
                  문제 목록 조회, 수정, 삭제 및 새 문제 생성
                </p>
              </div>
              <ArrowRight className="h-5 w-5 text-muted-foreground/40 transition-all group-hover:text-foreground group-hover:translate-x-1" />
            </div>
          </Link>
        </motion.div>
      </div>
    </div>
  );
}
