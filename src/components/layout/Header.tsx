'use client';

import Link from 'next/link';
import Image from 'next/image';
import { usePathname } from 'next/navigation';
import { motion } from 'framer-motion';
import { Zap } from 'lucide-react';
import { Button } from '@/components/ui/button';

export function Header() {
  const pathname = usePathname();
  const isAuthPage = pathname === '/login' || pathname === '/signup' || pathname === '/onboarding';

  return (
    <motion.header
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      className="sticky top-0 z-50 w-full border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60"
    >
      <div className="flex h-16 items-center justify-between px-6">
        <Link href="/" className="flex items-center">
          <Image
            src="/logo.png"
            alt="CodeFill"
            width={270}
            height={72}
            className="h-[72px] w-auto"
            priority
          />
        </Link>

        <div className="flex items-center gap-3">
          {!isAuthPage ? (
            <>
              <div className="hidden items-center gap-2 rounded-full bg-secondary px-3 py-1.5 sm:flex">
                <Zap className="h-4 w-4 text-primary" />
                <span className="text-sm font-medium">2,450 XP</span>
              </div>
              <Link href="/mypage">
                <Button variant="outline" size="sm">
                  My Page
                </Button>
              </Link>
            </>
          ) : (
            <>
              <Link href="/login">
                <Button variant="ghost" size="sm">
                  Log In
                </Button>
              </Link>
              <Link href="/onboarding">
                <Button size="sm">Sign Up</Button>
              </Link>
            </>
          )}
        </div>
      </div>
    </motion.header>
  );
}
