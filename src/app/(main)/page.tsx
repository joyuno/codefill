'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { StatCards } from '@/components/dashboard/StatCards';
import { GrassHeatmap } from '@/components/dashboard/GrassHeatmap';
import { Button } from '@/components/ui/button';
import { Play, Sparkles } from 'lucide-react';
import { WelcomeModal } from '@/components/modals/WelcomeModal';

export default function HomePage() {
  const [showWelcomeModal, setShowWelcomeModal] = useState(false);
  const [welcomeUsername, setWelcomeUsername] = useState('');

  // 회원가입 후 환영 모달 표시 체크
  useEffect(() => {
    const shouldShow = localStorage.getItem('showWelcomeModal');
    if (shouldShow === 'true') {
      const username = localStorage.getItem('welcomeUsername') || '';
      setWelcomeUsername(username);
      setShowWelcomeModal(true);
      // 플래그 제거
      localStorage.removeItem('showWelcomeModal');
      localStorage.removeItem('welcomeUsername');
    }
  }, []);

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <StatCards />

      {/* CTA Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="rounded-xl border border-primary/30 bg-gradient-to-r from-primary/10 to-transparent p-6"
      >
        <div className="flex flex-col items-center gap-4 sm:flex-row sm:justify-between">
          <div>
            <h3 className="text-xl font-semibold">오늘의 학습을 시작해보세요!</h3>
            <p className="text-muted-foreground">문제를 풀고 XP를 얻어 레벨업하세요</p>
          </div>
          <Link href="/problems">
            <Button size="lg" className="gap-2">
              <Play className="h-4 w-4" />
              문제 풀기
              <Sparkles className="h-4 w-4" />
            </Button>
          </Link>
        </div>
      </motion.div>

      {/* Grass Heatmap */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
      >
        <GrassHeatmap />
      </motion.div>

      {/* 회원가입 환영 모달 */}
      <WelcomeModal
        open={showWelcomeModal}
        onClose={() => setShowWelcomeModal(false)}
        username={welcomeUsername}
      />
    </div>
  );
}
