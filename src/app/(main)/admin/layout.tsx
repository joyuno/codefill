'use client';

import { useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { Shield, Users, FileText, PlusCircle, LayoutDashboard } from 'lucide-react';
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
      <div className="relative z-10 space-y-6">
        {/* Admin Header with Navigation */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center justify-between pt-2"
        >
          {/* Left: Admin Badge */}
          <div className="flex items-center gap-3">
            <div className="relative">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-primary/20 to-primary/5 border border-primary/20">
                <Shield className="h-5 w-5 text-primary" />
              </div>
              <div className="absolute -top-0.5 -right-0.5 h-2 w-2 rounded-full bg-primary" />
            </div>
            <div className="flex flex-col">
              <span className="text-sm font-medium tracking-tight">관리자</span>
              <span className="text-[10px] text-muted-foreground/60 uppercase tracking-wider">Admin Console</span>
            </div>
          </div>

          {/* Right: Navigation */}
          <nav className="flex items-center">
            {adminNavItems.map((item, index) => {
              const isActive = item.exact
                ? pathname === item.href
                : pathname.startsWith(item.href) && (item.href !== '/admin' || pathname === '/admin');
              const Icon = item.icon;

              return (
                <motion.div
                  key={item.href}
                  initial={{ opacity: 0, x: 10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.05 + index * 0.03 }}
                >
                  <Link
                    href={item.href}
                    className={cn(
                      'group relative flex items-center gap-1.5 px-3 py-2 text-sm font-medium transition-all duration-200',
                      isActive
                        ? 'text-primary'
                        : 'text-muted-foreground/70 hover:text-foreground'
                    )}
                  >
                    <Icon className={cn(
                      'h-4 w-4 transition-transform duration-200',
                      isActive ? 'text-primary' : 'group-hover:scale-110'
                    )} />
                    <span>{item.label}</span>

                    {/* Active indicator - minimal line */}
                    {isActive && (
                      <motion.div
                        layoutId="admin-nav-indicator"
                        className="absolute -bottom-0.5 left-3 right-3 h-[2px] bg-primary rounded-full"
                        transition={{ type: 'spring', stiffness: 500, damping: 35 }}
                      />
                    )}
                  </Link>
                </motion.div>
              );
            })}
          </nav>
        </motion.div>

        {/* Subtle divider */}
        <div className="h-px bg-gradient-to-r from-transparent via-border/50 to-transparent" />

        {/* Content */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15 }}
        >
          {children}
        </motion.div>
      </div>
    </div>
  );
}
