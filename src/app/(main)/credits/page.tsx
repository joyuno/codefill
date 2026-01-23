'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { useToast } from '@/hooks/use-toast';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Coins,
  TrendingUp,
  Clock,
  Gift,
  Zap,
  ChevronDown,
  Receipt,
  MessageCircleQuestion,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { cn } from '@/lib/utils';

// 크레딧 패키지 정의
const CREDIT_PACKAGES = [
  { id: 'pack-5k', price: 5000, credits: 5250, bonus: 5, popular: false },
  { id: 'pack-10k', price: 10000, credits: 10800, bonus: 8, popular: true },
  { id: 'pack-30k', price: 30000, credits: 33000, bonus: 10, popular: false },
  { id: 'pack-50k', price: 50000, credits: 57500, bonus: 15, popular: false },
];


// 크레딧 사용 내역 타입
interface CreditHistoryMetadata {
  problem_type?: string;
  original_id?: string;
  title?: string;
  difficulty?: string;
  language?: string;
}

interface CreditHistory {
  id: string;
  type: 'use' | 'charge' | 'bonus' | 'refund';
  amount: number;
  balance: number;
  description: string;
  metadata?: CreditHistoryMetadata;
  created_at: string;
}

// FAQ 항목
const FAQ_ITEMS = [
  {
    question: '크레딧은 어디에 사용되나요?',
    answer: 'AI가 문제를 생성할 때 크레딧이 소모됩니다. 빈칸 채우기, 퍼즐, 1대1 대화형 문제는 각각 10 크레딧이 필요하며, 구현 문제는 무료입니다.',
  },
  {
    question: '크레딧 유효기간이 있나요?',
    answer: '충전한 크레딧은 유효기간 없이 계속 사용할 수 있습니다.',
  },
  {
    question: '환불이 가능한가요?',
    answer: '미사용 크레딧에 한해 결제일로부터 7일 이내 환불 요청이 가능합니다. 고객센터로 문의해주세요.',
  },
  {
    question: '보너스 크레딧도 환불되나요?',
    answer: '보너스 크레딧은 환불 대상에서 제외됩니다. 환불 시 보너스 크레딧은 자동으로 차감됩니다.',
  },
];

// 애니메이션 variants
const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.1 },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 },
};

export default function CreditsPage() {
  const { profile, isLoading: authLoading } = useAuth();
  const { toast } = useToast();
  const [selectedPackage, setSelectedPackage] = useState<string | null>(null);
  const [creditHistory, setCreditHistory] = useState<CreditHistory[]>([]);
  const [historyLoading, setHistoryLoading] = useState(true);
  const [monthlyUsage, setMonthlyUsage] = useState(0);
  const [activeTab, setActiveTab] = useState<'history' | 'faq'>('history');
  const [expandedFaq, setExpandedFaq] = useState<number | null>(null);

  // 크레딧 사용 내역 조회
  useEffect(() => {
    const fetchCreditHistory = async () => {
      if (!profile?.id) return;

      try {
        const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const token = localStorage.getItem('access_token');

        const response = await fetch(`${API_BASE_URL}/users/me/credits/history`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });

        if (response.ok) {
          const data = await response.json();
          setCreditHistory(data.history || []);
          setMonthlyUsage(data.monthly_usage || 0);
        }
      } catch (error) {
        console.error('Failed to fetch credit history:', error);
      } finally {
        setHistoryLoading(false);
      }
    };

    fetchCreditHistory();
  }, [profile?.id]);

  // 패키지 선택 및 결제 처리
  const handlePurchase = async (packageId: string) => {
    const pkg = CREDIT_PACKAGES.find(p => p.id === packageId);
    if (!pkg) return;

    setSelectedPackage(packageId);

    toast({
      title: '결제 기능 준비 중',
      description: '곧 결제 기능이 추가될 예정입니다.',
    });

    setTimeout(() => setSelectedPackage(null), 1000);
  };

  // 타입별 스타일
  const getHistoryStyle = (type: CreditHistory['type']) => {
    switch (type) {
      case 'charge':
        return { icon: <TrendingUp className="h-4 w-4" />, color: 'text-emerald-400', bg: 'bg-emerald-500/10' };
      case 'bonus':
        return { icon: <Gift className="h-4 w-4" />, color: 'text-violet-400', bg: 'bg-violet-500/10' };
      case 'use':
        return { icon: <Zap className="h-4 w-4" />, color: 'text-amber-400', bg: 'bg-amber-500/10' };
      case 'refund':
        return { icon: <Clock className="h-4 w-4" />, color: 'text-blue-400', bg: 'bg-blue-500/10' };
      default:
        return { icon: <Coins className="h-4 w-4" />, color: 'text-gray-400', bg: 'bg-gray-500/10' };
    }
  };

  const getHistoryLabel = (type: CreditHistory['type']) => {
    switch (type) {
      case 'charge': return '충전';
      case 'bonus': return '보너스';
      case 'use': return '사용';
      case 'refund': return '환불';
      default: return type;
    }
  };

  const credits = profile?.credits ?? 0;

  return (
    <div className="min-h-screen">
      {/* 배경 효과 */}
      <div className="fixed inset-0 -z-10 overflow-hidden">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-amber-500/5 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-violet-500/5 rounded-full blur-3xl" />
      </div>

      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="container max-w-5xl mx-auto py-8 px-4 space-y-10"
      >
        {/* 히어로 섹션 - 크레딧 현황 (컴팩트) */}
        <motion.section variants={itemVariants} className="relative">
          <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-gray-900 via-gray-800 to-gray-900 border border-white/10 p-5">
            {/* 배경 장식 */}
            <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-amber-500/20 to-orange-500/10 rounded-full blur-2xl -translate-y-1/2 translate-x-1/2" />

            <div className="relative flex items-center justify-between gap-6">
              {/* 크레딧 표시 */}
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-amber-500/20 to-orange-500/20 flex items-center justify-center">
                  <Coins className="h-6 w-6 text-amber-500" />
                </div>
                <div>
                  <p className="text-xs text-gray-400 mb-0.5">보유 크레딧</p>
                  {authLoading ? (
                    <Skeleton className="h-8 w-24" />
                  ) : (
                    <div className="flex items-baseline gap-1.5">
                      <motion.span
                        key={credits}
                        initial={{ scale: 1.1, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        className="text-2xl font-bold bg-gradient-to-r from-amber-400 to-orange-400 bg-clip-text text-transparent"
                      >
                        {credits.toLocaleString()}
                      </motion.span>
                      <span className="text-gray-500 text-sm">C</span>
                    </div>
                  )}
                </div>
              </div>

              {/* 이번 달 사용량 & 문제 생성 가능 */}
              <div className="flex items-center gap-6">
                <div className="hidden sm:block text-right">
                  <p className="text-xs text-gray-500">이번 달 사용</p>
                  <p className="text-lg font-semibold text-white">
                    {historyLoading ? '-' : monthlyUsage.toLocaleString()}
                    <span className="text-xs text-gray-500 ml-1">C</span>
                  </p>
                </div>
                <div className="h-8 w-px bg-white/10 hidden sm:block" />
                <div className="text-right">
                  <p className="text-xs text-gray-500">생성 가능</p>
                  <p className="text-lg font-semibold text-white">
                    ~{Math.floor(credits / 10)}
                    <span className="text-xs text-gray-500 ml-1">문제</span>
                  </p>
                </div>
              </div>
            </div>
          </div>
        </motion.section>

        {/* 충전 패키지 */}
        <motion.section variants={itemVariants} className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">크레딧 충전</h2>
            <p className="text-xs text-muted-foreground">
              대량 구매 시 최대 15% 보너스
            </p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {CREDIT_PACKAGES.map((pkg) => (
              <motion.div
                key={pkg.id}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => handlePurchase(pkg.id)}
                className={cn(
                  "relative cursor-pointer rounded-xl p-4 transition-all",
                  "bg-card border hover:shadow-md",
                  pkg.popular
                    ? "border-amber-500/50 ring-1 ring-amber-500/20"
                    : "border-border hover:border-primary/30",
                  selectedPackage === pkg.id && "ring-2 ring-primary"
                )}
              >
                {pkg.popular && (
                  <Badge className="absolute -top-2 right-3 bg-amber-500 text-white text-[10px] px-1.5 py-0">
                    BEST
                  </Badge>
                )}

                {/* 가격 */}
                <p className="text-lg font-bold mb-1">
                  {pkg.price.toLocaleString()}원
                </p>

                {/* 크레딧 */}
                <p className="text-sm text-muted-foreground">
                  {pkg.credits.toLocaleString()} 크레딧
                </p>

                {/* 보너스 */}
                {pkg.bonus > 0 && (
                  <p className="text-xs text-amber-500 mt-1">
                    +{pkg.bonus}% 보너스
                  </p>
                )}
              </motion.div>
            ))}
          </div>
        </motion.section>

        {/* 탭 섹션: 사용 내역 / FAQ */}
        <motion.section variants={itemVariants} className="space-y-4">
          {/* 탭 헤더 */}
          <div className="flex gap-2 border-b border-border">
            <button
              onClick={() => setActiveTab('history')}
              className={cn(
                "flex items-center gap-2 px-4 py-3 text-sm font-medium transition-colors relative",
                activeTab === 'history'
                  ? "text-foreground"
                  : "text-muted-foreground hover:text-foreground"
              )}
            >
              <Receipt className="h-4 w-4" />
              사용 내역
              {activeTab === 'history' && (
                <motion.div
                  layoutId="activeTab"
                  className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary"
                />
              )}
            </button>
            <button
              onClick={() => setActiveTab('faq')}
              className={cn(
                "flex items-center gap-2 px-4 py-3 text-sm font-medium transition-colors relative",
                activeTab === 'faq'
                  ? "text-foreground"
                  : "text-muted-foreground hover:text-foreground"
              )}
            >
              <MessageCircleQuestion className="h-4 w-4" />
              자주 묻는 질문
              {activeTab === 'faq' && (
                <motion.div
                  layoutId="activeTab"
                  className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary"
                />
              )}
            </button>
          </div>

          {/* 탭 컨텐츠 */}
          <AnimatePresence mode="wait">
            {activeTab === 'history' ? (
              <motion.div
                key="history"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="min-h-[300px]"
              >
                {historyLoading ? (
                  <div className="space-y-3">
                    {[...Array(5)].map((_, i) => (
                      <Skeleton key={i} className="h-16 w-full rounded-xl" />
                    ))}
                  </div>
                ) : creditHistory.length === 0 ? (
                  <div className="flex flex-col items-center justify-center py-16 text-muted-foreground">
                    <div className="w-16 h-16 rounded-full bg-muted/50 flex items-center justify-center mb-4">
                      <Receipt className="h-8 w-8 opacity-50" />
                    </div>
                    <p className="font-medium">아직 사용 내역이 없습니다</p>
                    <p className="text-sm mt-1">문제를 생성하면 여기에 기록됩니다</p>
                  </div>
                ) : (
                  <div className="space-y-2">
                    {creditHistory.map((history, index) => {
                      const style = getHistoryStyle(history.type);
                      return (
                        <motion.div
                          key={history.id}
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: index * 0.05 }}
                          className="flex items-center gap-4 p-4 rounded-xl bg-card border border-border hover:border-border/80 transition-colors"
                        >
                          {/* 아이콘 */}
                          <div className={cn(
                            "flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center",
                            style.bg, style.color
                          )}>
                            {style.icon}
                          </div>

                          {/* 내용 */}
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2">
                              <span className="font-medium text-sm">
                                {history.description}
                              </span>
                              <Badge variant="outline" className="text-[10px]">
                                {getHistoryLabel(history.type)}
                              </Badge>
                            </div>
                            {history.metadata?.difficulty && (
                              <div className="flex items-center gap-2 mt-1 text-xs text-muted-foreground">
                                <span>{history.metadata.difficulty}</span>
                                {history.metadata.language && (
                                  <>
                                    <span>·</span>
                                    <span>{history.metadata.language}</span>
                                  </>
                                )}
                              </div>
                            )}
                          </div>

                          {/* 금액 */}
                          <div className="flex-shrink-0 text-right">
                            <div className={cn(
                              "font-semibold",
                              history.amount > 0 ? "text-emerald-500" : "text-red-400"
                            )}>
                              {history.amount > 0 ? '+' : ''}{history.amount.toLocaleString()}
                            </div>
                            <div className="text-xs text-muted-foreground">
                              잔액 {history.balance.toLocaleString()}
                            </div>
                          </div>

                          {/* 시간 */}
                          <div className="flex-shrink-0 text-xs text-muted-foreground w-20 text-right">
                            {new Date(history.created_at).toLocaleDateString('ko-KR', {
                              month: 'short',
                              day: 'numeric',
                            })}
                            <br />
                            {new Date(history.created_at).toLocaleTimeString('ko-KR', {
                              hour: '2-digit',
                              minute: '2-digit',
                            })}
                          </div>
                        </motion.div>
                      );
                    })}
                  </div>
                )}
              </motion.div>
            ) : (
              <motion.div
                key="faq"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="space-y-2"
              >
                {FAQ_ITEMS.map((item, index) => (
                  <div
                    key={index}
                    className="rounded-xl border border-border overflow-hidden"
                  >
                    <button
                      onClick={() => setExpandedFaq(expandedFaq === index ? null : index)}
                      className="w-full flex items-center justify-between p-4 text-left hover:bg-muted/50 transition-colors"
                    >
                      <span className="font-medium">{item.question}</span>
                      <ChevronDown
                        className={cn(
                          "h-4 w-4 text-muted-foreground transition-transform",
                          expandedFaq === index && "rotate-180"
                        )}
                      />
                    </button>
                    <AnimatePresence>
                      {expandedFaq === index && (
                        <motion.div
                          initial={{ height: 0, opacity: 0 }}
                          animate={{ height: 'auto', opacity: 1 }}
                          exit={{ height: 0, opacity: 0 }}
                          transition={{ duration: 0.2 }}
                          className="overflow-hidden"
                        >
                          <div className="px-4 pb-4 text-sm text-muted-foreground">
                            {item.answer}
                          </div>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </div>
                ))}
              </motion.div>
            )}
          </AnimatePresence>
        </motion.section>
      </motion.div>
    </div>
  );
}
