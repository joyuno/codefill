/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,

  // Docker 배포를 위한 standalone 모드
  output: 'standalone',

  // 이미지 최적화 설정
  images: {
    domains: ['localhost'],
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**.supabase.co',
      },
      // 백준 문제 이미지
      {
        protocol: 'https',
        hostname: 'www.acmicpc.net',
      },
      {
        protocol: 'https',
        hostname: 'upload.acmicpc.net',
      },
      {
        protocol: 'https',
        hostname: 'onlinejudgeimages.s3-ap-northeast-1.amazonaws.com',
      },
      // 외부 이미지 (위키피디아 등)
      {
        protocol: 'https',
        hostname: 'upload.wikimedia.org',
      },
    ],
    // 최신 이미지 포맷 지원 (성능 최적화)
    formats: ['image/avif', 'image/webp'],
    // 디바이스별 최적화 크기
    deviceSizes: [640, 750, 828, 1080, 1200, 1920],
  },

  experimental: {
    serverActions: {
      bodySizeLimit: '2mb',
    },
  },

  // 프로덕션 빌드 최적화
  compiler: {
    // 프로덕션에서 console.log 제거
    removeConsole: process.env.NODE_ENV === 'production',
  },

  // SWC 최소화 (더 빠른 빌드)
  swcMinify: true,
};

module.exports = nextConfig;
