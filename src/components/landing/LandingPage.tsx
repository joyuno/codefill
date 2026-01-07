'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import { Header } from '@/components/layout/Header';
import { Button } from '@/components/ui/button';
import {
  Sparkles,
  Code2,
  BookOpen,
  Trophy,
  Zap,
  ArrowRight,
  Leaf,
} from 'lucide-react';
import { cn } from '@/lib/utils';

export function LandingPage() {
  const features = [
    {
      icon: BookOpen,
      title: '단계별 학습',
      description: '빈칸 채우기, 퍼즐, 구현까지 점진적으로 실력을 키워요',
    },
    {
      icon: Zap,
      title: 'AI 튜터',
      description: '막힐 때 힌트를 주고, 코드를 분석해 피드백을 줘요',
    },
    {
      icon: Trophy,
      title: '게이미피케이션',
      description: 'XP, 레벨, 뱃지로 성취감을 느끼며 학습해요',
    },
    {
      icon: Leaf,
      title: '나만의 농장',
      description: '문제를 풀면 농작물이 자라요. 농장을 키워보세요!',
    },
  ];

  const stats = [
    { value: '1,000+', label: '문제' },
    { value: '3가지', label: '언어 지원' },
    { value: '4단계', label: '학습 방식' },
    { value: '무료', label: '시작 가능' },
  ];

  return (
    <div className="min-h-screen bg-background">
      <Header />

      {/* 히어로 섹션 */}
      <section className="relative overflow-hidden">
        {/* 배경 그라데이션 */}
        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-primary/10" />

        <div className="container mx-auto max-w-6xl px-6 py-20 relative">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center space-y-6"
          >
            <h1 className="text-4xl md:text-6xl font-bold tracking-tight">
              코딩은 <span className="text-primary">채우는 것</span>부터
              <br />
              시작합니다
            </h1>

            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              빈칸 채우기로 시작해서, 퍼즐 맞추기, 대화형 학습,
              직접 구현까지. 단계별로 코딩 실력을 키워보세요.
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
              <Link href="/onboarding">
                <Button size="lg" className="gap-2 px-8">
                  무료로 시작하기
                  <ArrowRight className="h-4 w-4" />
                </Button>
              </Link>
              <Link href="/login">
                <Button size="lg" variant="outline" className="gap-2">
                  로그인
                </Button>
              </Link>
            </div>
          </motion.div>

          {/* 통계 */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="grid grid-cols-2 md:grid-cols-4 gap-6 mt-16"
          >
            {stats.map((stat, i) => (
              <div key={i} className="text-center">
                <p className="text-3xl md:text-4xl font-bold text-primary">{stat.value}</p>
                <p className="text-muted-foreground">{stat.label}</p>
              </div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* 기능 섹션 */}
      <section className="py-20 bg-secondary/30">
        <div className="container mx-auto max-w-6xl px-6">
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            className="text-center mb-12"
          >
            <h2 className="text-3xl font-bold mb-4">왜 CodeFill인가요?</h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              처음부터 코드를 작성하는 건 어려워요.
              빈칸을 채우면서 자연스럽게 문법과 로직을 익히세요.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className="p-6 rounded-xl bg-card border border-border hover:border-primary/50 transition-colors"
              >
                <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                  <feature.icon className="h-6 w-6 text-primary" />
                </div>
                <h3 className="font-semibold mb-2">{feature.title}</h3>
                <p className="text-sm text-muted-foreground">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* 학습 단계 섹션 */}
      <section className="py-20">
        <div className="container mx-auto max-w-6xl px-6">
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            className="text-center mb-12"
          >
            <h2 className="text-3xl font-bold mb-4">4단계 학습 시스템</h2>
            <p className="text-muted-foreground">
              쉬운 것부터 시작해서 점점 난이도를 높여가요
            </p>
          </motion.div>

          <div className="grid md:grid-cols-4 gap-4">
            {[
              { step: 1, name: '빈칸 채우기', desc: '핵심 문법만 채워요', color: 'bg-green-500' },
              { step: 2, name: '퍼즐 맞추기', desc: '코드 순서를 배워요', color: 'bg-blue-500' },
              { step: 3, name: '대화형 학습', desc: 'AI와 함께 풀어요', color: 'bg-purple-500' },
              { step: 4, name: '직접 구현', desc: '처음부터 작성해요', color: 'bg-orange-500' },
            ].map((item, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className="relative"
              >
                <div className={cn(
                  'p-6 rounded-xl border border-border bg-card',
                  'hover:shadow-lg transition-shadow'
                )}>
                  <div className={cn(
                    'h-10 w-10 rounded-full flex items-center justify-center text-white font-bold mb-4',
                    item.color
                  )}>
                    {item.step}
                  </div>
                  <h3 className="font-semibold mb-1">{item.name}</h3>
                  <p className="text-sm text-muted-foreground">{item.desc}</p>
                </div>
                {i < 3 && (
                  <div className="hidden md:block absolute top-1/2 -right-2 transform -translate-y-1/2">
                    <ArrowRight className="h-4 w-4 text-muted-foreground" />
                  </div>
                )}
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA 섹션 */}
      <section className="py-20 bg-primary text-primary-foreground">
        <div className="container mx-auto max-w-4xl px-6 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              지금 바로 시작하세요
            </h2>
            <p className="text-primary-foreground/80 mb-8 text-lg">
              무료로 가입하고 첫 문제를 풀어보세요.
              <br />
              5분이면 시작할 수 있어요.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link href="/onboarding">
                <Button size="lg" variant="secondary" className="gap-2 px-8">
                  무료 회원가입
                  <Sparkles className="h-4 w-4" />
                </Button>
              </Link>
            </div>
          </motion.div>
        </div>
      </section>

      {/* 푸터 */}
      <footer className="py-8 border-t border-border">
        <div className="container mx-auto max-w-6xl px-6">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <Code2 className="h-5 w-5 text-primary" />
              <span className="font-bold">CodeFill</span>
            </div>
            <p className="text-sm text-muted-foreground">
              © 2024 CodeFill. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
