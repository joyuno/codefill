'use client';

import { motion } from 'framer-motion';
import {
  Compass,
  Zap,
  Search,
  Shield,
  Sparkles,
} from 'lucide-react';
import type { LearningStyle } from '@/lib/api/analysis';

interface LearningStyleCardProps {
  learningStyle?: LearningStyle;
}

// 학습 스타일별 아이콘과 색상 매핑
const STYLE_CONFIG: Record<string, { icon: typeof Compass; color: string; label: string }> = {
  methodical: {
    icon: Compass,
    color: '#3b82f6', // blue
    label: '체계적 학습자',
  },
  exploratory: {
    icon: Search,
    color: '#8b5cf6', // violet
    label: '탐구형 학습자',
  },
  'hint-dependent': {
    icon: Sparkles,
    color: '#f59e0b', // amber
    label: '힌트 활용형',
  },
  independent: {
    icon: Shield,
    color: '#10b981', // emerald
    label: '독립적 학습자',
  },
};

function getStyleConfig(type: string) {
  const normalizedType = type.toLowerCase().trim();

  for (const [key, config] of Object.entries(STYLE_CONFIG)) {
    if (normalizedType.includes(key)) {
      return config;
    }
  }

  // 기본값
  return {
    icon: Zap,
    color: '#a855f7',
    label: type,
  };
}

export function LearningStyleCard({ learningStyle }: LearningStyleCardProps) {
  if (!learningStyle || !learningStyle.type) {
    return (
      <div className="p-6">
        <div className="flex items-center gap-2 mb-1.5">
          <Zap className="w-5 h-5 text-violet-400" />
          <h3 className="text-base font-semibold text-zinc-100">학습 스타일</h3>
        </div>
        <p className="text-xs text-zinc-500 mb-4">
          AI가 분석한 당신만의 학습 패턴
        </p>
        <div className="flex items-center justify-center py-8 text-zinc-600 text-sm">
          <p>더 많은 문제를 풀면 학습 스타일이 분석됩니다</p>
        </div>
      </div>
    );
  }

  const config = getStyleConfig(learningStyle.type);
  const IconComponent = config.icon;

  return (
    <div className="p-6">
      <div className="mb-4">
        <div className="flex items-center gap-2 mb-1.5">
          <Zap className="w-5 h-5 text-violet-400" />
          <h3 className="text-base font-semibold text-zinc-100">학습 스타일</h3>
        </div>
        <p className="text-xs text-zinc-500">
          AI가 분석한 당신만의 학습 패턴
        </p>
      </div>

      <div className="space-y-4">
        {/* 스타일 배지 */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="flex items-center gap-3 p-3 rounded-xl"
          style={{ backgroundColor: `${config.color}10` }}
        >
          <div
            className="w-10 h-10 rounded-lg flex items-center justify-center"
            style={{ backgroundColor: `${config.color}20` }}
          >
            <IconComponent className="w-5 h-5" style={{ color: config.color }} />
          </div>
          <div>
            <div
              className="text-sm font-semibold"
              style={{ color: config.color }}
            >
              {config.label}
            </div>
          </div>
        </motion.div>

        {/* 설명 */}
        {learningStyle.description && (
          <motion.div
            initial={{ opacity: 0, y: 5 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="p-3 rounded-lg bg-zinc-800/50"
          >
            <p className="text-sm text-zinc-300 leading-relaxed">
              {learningStyle.description}
            </p>
          </motion.div>
        )}

        {/* 전략 */}
        {learningStyle.strategy && (
          <motion.div
            initial={{ opacity: 0, y: 5 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="p-3 rounded-lg bg-violet-500/5 border border-violet-500/20"
          >
            <div className="flex items-center gap-1.5 mb-1.5">
              <Sparkles className="w-3.5 h-3.5 text-violet-400" />
              <span className="text-xs font-medium text-violet-400">추천 전략</span>
            </div>
            <p className="text-sm text-zinc-300 leading-relaxed">
              {learningStyle.strategy}
            </p>
          </motion.div>
        )}
      </div>
    </div>
  );
}
