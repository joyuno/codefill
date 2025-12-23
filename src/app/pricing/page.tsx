'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { Header } from '@/components/layout/Header';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Check,
  Crown,
  Zap,
  Star,
  ArrowLeft,
  CreditCard,
  Shield,
  RefreshCcw,
  HelpCircle,
  MessageCircle,
} from 'lucide-react';
import { useAuth, SUBSCRIPTION_FEATURES } from '@/hooks/useAuth';
import { useToast } from '@/hooks/use-toast';
import { cn } from '@/lib/utils';

// ============================================
// 가격 플랜 정의
// ============================================

interface PricingPlan {
  id: string;
  name: string;
  description: string;
  monthlyPrice: number;
  yearlyPrice: number;
  features: string[];
  highlighted?: boolean;
  icon: React.ReactNode;
  badge?: string;
}

const PRICING_PLANS: PricingPlan[] = [
  {
    id: 'free',
    name: '무료',
    description: '코딩 학습을 시작하는 분께',
    monthlyPrice: 0,
    yearlyPrice: 0,
    features: [
      '하루 5문제 풀이',
      '기본 힌트 3회/일',
      '빈칸 채우기 모드',
      '기본 진도 확인',
      '커뮤니티 접근',
    ],
    icon: <Zap className="h-6 w-6" />,
  },
  {
    id: 'basic',
    name: '베이직',
    description: '본격적으로 실력을 키우고 싶은 분께',
    monthlyPrice: 9900,
    yearlyPrice: 99000,
    features: [
      '하루 20문제 풀이',
      '무제한 힌트',
      '모든 학습 모드',
      'AI 튜터 기본 기능',
      '상세 진도 분석',
      '코드 실행 무제한',
    ],
    highlighted: true,
    icon: <Star className="h-6 w-6" />,
    badge: '인기',
  },
  {
    id: 'pro',
    name: '프로',
    description: '최고의 학습 경험을 원하는 분께',
    monthlyPrice: 19900,
    yearlyPrice: 199000,
    features: [
      '무제한 문제 풀이',
      '무제한 힌트',
      'AI 튜터 고급 기능',
      '1:1 코드 리뷰',
      '우선 지원',
      '모든 뱃지 언락',
      '광고 제거',
      '베타 기능 우선 접근',
    ],
    icon: <Crown className="h-6 w-6" />,
  },
];

// ============================================
// 결제 컴포넌트
// ============================================

function PaymentButton({ 
  plan, 
  billingCycle 
}: { 
  plan: PricingPlan; 
  billingCycle: 'monthly' | 'yearly';
}) {
  const { isAuthenticated, profile } = useAuth();
  const { toast } = useToast();
  const [isProcessing, setIsProcessing] = useState(false);
  
  const price = billingCycle === 'yearly' ? plan.yearlyPrice : plan.monthlyPrice;
  const currentTier = profile?.subscription_tier || 'free';
  const isCurrentPlan = currentTier === plan.id;
  const isUpgrade = !isCurrentPlan && (
    (plan.id === 'basic' && currentTier === 'free') ||
    (plan.id === 'pro' && (currentTier === 'free' || currentTier === 'basic'))
  );
  
  // 결제 처리 (테스트 모드)
  const handlePayment = async () => {
    if (!isAuthenticated) {
      toast({
        title: '로그인이 필요합니다',
        description: '결제를 진행하려면 먼저 로그인해주세요.',
        variant: 'destructive',
      });
      return;
    }
    
    if (plan.id === 'free') {
      toast({
        title: '무료 플랜입니다',
        description: '이미 무료 플랜을 사용 중입니다.',
      });
      return;
    }
    
    setIsProcessing(true);
    
    // 테스트 모드: 포트원(아임포트) SDK 로드
    // 실제 결제 연동 시 아래 코드를 활성화
    try {
      // 포트원 결제 모듈 로드 (테스트용)
      const IMP = (window as any).IMP;
      
      if (!IMP) {
        // SDK가 없으면 테스트 모드로 동작
        toast({
          title: '테스트 모드',
          description: '실제 결제는 사업자 등록 후 연동됩니다. 구독이 활성화된 것으로 처리합니다.',
        });
        
        // 테스트용: 로컬 스토리지에 구독 정보 저장
        localStorage.setItem('codefill_subscription', JSON.stringify({
          tier: plan.id,
          billingCycle,
          startedAt: new Date().toISOString(),
          expiresAt: new Date(Date.now() + (billingCycle === 'yearly' ? 365 : 30) * 24 * 60 * 60 * 1000).toISOString(),
        }));
        
        setTimeout(() => {
          setIsProcessing(false);
          window.location.reload();
        }, 1500);
        return;
      }
      
      // 포트원 결제 요청
      IMP.init('imp00000000'); // 테스트 가맹점 코드
      
      IMP.request_pay({
        pg: 'tosspayments', // 토스페이먼츠
        pay_method: 'card',
        merchant_uid: `order_${Date.now()}`,
        name: `CodeFill ${plan.name} (${billingCycle === 'yearly' ? '연간' : '월간'})`,
        amount: price,
        buyer_email: profile?.email,
        buyer_name: profile?.username,
      }, (response: any) => {
        if (response.success) {
          toast({
            title: '결제 완료',
            description: `${plan.name} 구독이 시작되었습니다!`,
          });
          // TODO: 서버에 결제 정보 전송
        } else {
          toast({
            title: '결제 실패',
            description: response.error_msg,
            variant: 'destructive',
          });
        }
        setIsProcessing(false);
      });
    } catch (error) {
      console.error('결제 오류:', error);
      toast({
        title: '오류 발생',
        description: '결제 처리 중 문제가 발생했습니다.',
        variant: 'destructive',
      });
      setIsProcessing(false);
    }
  };
  
  if (isCurrentPlan) {
    return (
      <Button disabled className="w-full">
        현재 이용 중
      </Button>
    );
  }
  
  if (plan.id === 'free') {
    return (
      <Button variant="outline" className="w-full" asChild>
        <Link href="/onboarding">무료로 시작</Link>
      </Button>
    );
  }
  
  return (
    <Button 
      className={cn(
        'w-full',
        plan.highlighted && 'bg-primary hover:bg-primary/90'
      )}
      onClick={handlePayment}
      disabled={isProcessing}
    >
      {isProcessing ? '처리 중...' : isUpgrade ? '업그레이드' : '구독하기'}
    </Button>
  );
}

// ============================================
// 가격 카드 컴포넌트
// ============================================

function PricingCard({ 
  plan, 
  billingCycle 
}: { 
  plan: PricingPlan; 
  billingCycle: 'monthly' | 'yearly';
}) {
  const price = billingCycle === 'yearly' ? plan.yearlyPrice : plan.monthlyPrice;
  const monthlyEquivalent = billingCycle === 'yearly' ? Math.round(plan.yearlyPrice / 12) : plan.monthlyPrice;
  const savings = billingCycle === 'yearly' ? plan.monthlyPrice * 12 - plan.yearlyPrice : 0;
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -5 }}
      transition={{ duration: 0.2 }}
    >
      <Card className={cn(
        'relative h-full',
        plan.highlighted && 'border-primary shadow-lg shadow-primary/20'
      )}>
        {plan.badge && (
          <Badge className="absolute -top-3 left-1/2 -translate-x-1/2 bg-primary">
            {plan.badge}
          </Badge>
        )}
        
        <CardHeader>
          <div className={cn(
            'h-12 w-12 rounded-lg flex items-center justify-center mb-4',
            plan.highlighted ? 'bg-primary text-primary-foreground' : 'bg-secondary'
          )}>
            {plan.icon}
          </div>
          <CardTitle className="text-2xl">{plan.name}</CardTitle>
          <CardDescription>{plan.description}</CardDescription>
        </CardHeader>
        
        <CardContent className="space-y-6">
          {/* 가격 */}
          <div>
            <div className="flex items-baseline gap-1">
              <span className="text-4xl font-bold">
                {price === 0 ? '무료' : `₩${monthlyEquivalent.toLocaleString()}`}
              </span>
              {price > 0 && (
                <span className="text-muted-foreground">/월</span>
              )}
            </div>
            {billingCycle === 'yearly' && price > 0 && (
              <div className="mt-1 space-y-1">
                <p className="text-sm text-muted-foreground">
                  연간 ₩{price.toLocaleString()} 결제
                </p>
                {savings > 0 && (
                  <Badge variant="secondary" className="text-green-600 bg-green-100">
                    ₩{savings.toLocaleString()} 절약
                  </Badge>
                )}
              </div>
            )}
          </div>
          
          {/* 기능 목록 */}
          <ul className="space-y-3">
            {plan.features.map((feature, i) => (
              <li key={i} className="flex items-start gap-2">
                <Check className="h-5 w-5 text-green-500 shrink-0 mt-0.5" />
                <span className="text-sm">{feature}</span>
              </li>
            ))}
          </ul>
        </CardContent>
        
        <CardFooter>
          <PaymentButton plan={plan} billingCycle={billingCycle} />
        </CardFooter>
      </Card>
    </motion.div>
  );
}

// ============================================
// 메인 가격 페이지
// ============================================

export default function PricingPage() {
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'yearly'>('monthly');
  const { isAuthenticated, profile } = useAuth();
  
  return (
    <div className="min-h-screen bg-background">
      <Header />
      
      <main className="container mx-auto max-w-6xl px-6 py-12">
        {/* 뒤로가기 */}
        <Link href="/">
          <Button variant="ghost" size="sm" className="mb-8 gap-2">
            <ArrowLeft className="h-4 w-4" />
            돌아가기
          </Button>
        </Link>
        
        {/* 헤더 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <h1 className="text-4xl font-bold mb-4">
            나에게 맞는 플랜을 선택하세요
          </h1>
          <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
            모든 플랜은 7일 내 전액 환불이 가능합니다.
            <br />
            부담 없이 시작해보세요.
          </p>
        </motion.div>
        
        {/* 결제 주기 선택 */}
        <div className="flex justify-center mb-8">
          <Tabs 
            value={billingCycle} 
            onValueChange={(v) => setBillingCycle(v as 'monthly' | 'yearly')}
          >
            <TabsList className="grid w-64 grid-cols-2">
              <TabsTrigger value="monthly">월간</TabsTrigger>
              <TabsTrigger value="yearly" className="relative">
                연간
                <Badge 
                  variant="secondary" 
                  className="absolute -top-3 -right-3 text-xs bg-green-100 text-green-700"
                >
                  -17%
                </Badge>
              </TabsTrigger>
            </TabsList>
          </Tabs>
        </div>
        
        {/* 현재 구독 상태 (로그인 시) */}
        {isAuthenticated && profile && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mb-8 p-4 rounded-xl bg-secondary/50 text-center"
          >
            <p className="text-sm text-muted-foreground">
              현재 <span className="font-bold text-foreground">
                {SUBSCRIPTION_FEATURES[profile.subscription_tier || 'free'].name}
              </span> 플랜을 이용 중입니다
            </p>
          </motion.div>
        )}
        
        {/* 가격 카드 */}
        <div className="grid md:grid-cols-3 gap-6 mb-16">
          {PRICING_PLANS.map((plan) => (
            <PricingCard 
              key={plan.id} 
              plan={plan} 
              billingCycle={billingCycle}
            />
          ))}
        </div>
        
        {/* 결제 안내 */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="grid md:grid-cols-3 gap-6 py-12 border-t border-border"
        >
          <div className="flex items-start gap-4">
            <div className="h-10 w-10 rounded-lg bg-blue-100 flex items-center justify-center shrink-0">
              <CreditCard className="h-5 w-5 text-blue-600" />
            </div>
            <div>
              <h3 className="font-semibold mb-1">다양한 결제 수단</h3>
              <p className="text-sm text-muted-foreground">
                신용카드, 카카오페이, 네이버페이 등 편한 방법으로 결제하세요
              </p>
            </div>
          </div>
          
          <div className="flex items-start gap-4">
            <div className="h-10 w-10 rounded-lg bg-green-100 flex items-center justify-center shrink-0">
              <RefreshCcw className="h-5 w-5 text-green-600" />
            </div>
            <div>
              <h3 className="font-semibold mb-1">7일 환불 보장</h3>
              <p className="text-sm text-muted-foreground">
                구독 시작 후 7일 내에는 이유 불문 전액 환불해드립니다
              </p>
            </div>
          </div>
          
          <div className="flex items-start gap-4">
            <div className="h-10 w-10 rounded-lg bg-purple-100 flex items-center justify-center shrink-0">
              <Shield className="h-5 w-5 text-purple-600" />
            </div>
            <div>
              <h3 className="font-semibold mb-1">언제든 해지 가능</h3>
              <p className="text-sm text-muted-foreground">
                약정 없이 원할 때 언제든 구독을 취소할 수 있어요
              </p>
            </div>
          </div>
        </motion.div>
        
        {/* FAQ */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
          className="py-12 border-t border-border"
        >
          <h2 className="text-2xl font-bold text-center mb-8">자주 묻는 질문</h2>
          
          <div className="grid md:grid-cols-2 gap-6 max-w-4xl mx-auto">
            {[
              {
                q: '무료 플랜으로도 충분한가요?',
                a: '기본적인 학습에는 충분합니다. 하지만 하루 5문제 제한이 있어서, 더 많이 풀고 싶다면 업그레이드를 추천드려요.',
              },
              {
                q: '환불은 어떻게 하나요?',
                a: '결제일로부터 7일 이내에 고객센터로 연락주시면 전액 환불해드립니다. 7일 이후에는 남은 기간에 대해 일할 계산됩니다.',
              },
              {
                q: '플랜을 변경할 수 있나요?',
                a: '네, 언제든 업그레이드하거나 다운그레이드할 수 있습니다. 차액은 자동으로 계산됩니다.',
              },
              {
                q: '결제 수단은 뭐가 있나요?',
                a: '신용카드, 체크카드, 카카오페이, 네이버페이를 지원합니다. 계좌이체는 연간 결제 시에만 가능합니다.',
              },
            ].map((faq, i) => (
              <div key={i} className="p-4 rounded-lg bg-secondary/50">
                <h3 className="font-semibold flex items-center gap-2 mb-2">
                  <HelpCircle className="h-4 w-4 text-primary" />
                  {faq.q}
                </h3>
                <p className="text-sm text-muted-foreground">{faq.a}</p>
              </div>
            ))}
          </div>
        </motion.div>
        
        {/* 문의 */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="py-12 text-center"
        >
          <p className="text-muted-foreground mb-4">
            더 궁금한 점이 있으신가요?
          </p>
          <Button variant="outline" className="gap-2">
            <MessageCircle className="h-4 w-4" />
            문의하기
          </Button>
        </motion.div>
      </main>
    </div>
  );
}

