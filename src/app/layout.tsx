import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { Providers } from './providers';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'CodeFill - AI 기반 능동적 코딩 학습 플랫폼',
  description: '4가지 문제 유형으로 능동적으로 추론하며 코드 패턴을 체화하고, AI 튜터의 개인 맞춤 코칭으로 지속 성장하는 게이미피케이션 기반 학습 서비스',
  keywords: ['코딩 학습', '개발자 교육', 'AI 튜터', '코딩테스트', '프론트엔드', '백엔드'],
  icons: {
    icon: '/favicon.png',
    apple: '/favicon.png',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ko" className="dark">
      <body className={inter.className}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
