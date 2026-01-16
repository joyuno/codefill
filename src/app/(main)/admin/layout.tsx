'use client';

import { useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { Shield, Users, FileText, PlusCircle, LayoutDashboard, Sparkles } from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { cn } from '@/lib/utils';

const adminNavItems = [
  { href: '/admin', label: '대시보드', icon: LayoutDashboard, exact: true },
  { href: '/admin/users', label: '사용자', icon: Users },
  { href: '/admin/problems', label: '문제', icon: FileText, exact: true },
  { href: '/admin/problems/create', label: '새 문제', icon: PlusCircle, exact: true },
];

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const { isLoading, isAuthenticated, profile } = useAuth();

  // 관리자 권한 체크
  useEffect(() => {
    if (!isLoading && (!isAuthenticated || profile?.role !== 'admin')) {
      router.push('/');
    }
  }, [isLoading, isAuthenticated, profile, router]);

  // 로딩 중이거나 권한 없으면 렌더링 안함
  if (isLoading || !isAuthenticated || profile?.role !== 'admin') {
    return null;
  }

  return (
    <div className="admin-container admin-mesh-bg min-h-[calc(100vh-120px)] relative">
      <div className="relative z-10 space-y-8">
        {/* Admin Header */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center justify-between pt-2"
        >
          <div className="flex items-center gap-4">
            <div className="relative">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-primary/20 to-primary/5 border border-primary/20 shadow-lg shadow-primary/10">
                <Shield className="h-6 w-6 text-primary" />
              </div>
              <div className="absolute -top-1 -right-1 h-3 w-3 rounded-full bg-primary animate-pulse" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-xl font-semibold tracking-tight">관리자 모드</h1>
                <Sparkles className="h-4 w-4 text-primary/60" />
              </div>
              <p className="text-sm text-muted-foreground/80">CodeFill 플랫폼 관리</p>
            </div>
          </div>
        </motion.div>

        {/* Admin Navigation - Pill Style */}
        <motion.nav
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="admin-nav-pill inline-flex"
        >
          {adminNavItems.map((item, index) => {
            const isActive = item.exact
              ? pathname === item.href
              : pathname.startsWith(item.href) && (item.href !== '/admin' || pathname === '/admin');
            const Icon = item.icon;

            return (
              <motion.div
                key={item.href}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.1 + index * 0.05 }}
              >
                <Link
                  href={item.href}
                  className={cn(
                    'admin-nav-item flex items-center gap-2',
                    isActive && 'active'
                  )}
                >
                  <Icon className="h-4 w-4" />
                  <span>{item.label}</span>
                </Link>
              </motion.div>
            );
          })}
        </motion.nav>

        {/* Content */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          {children}
        </motion.div>
      </div>
    </div>
  );
}
