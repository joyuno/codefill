/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,

  // Docker 배포를 위한 standalone 모드
  output: 'standalone',

  // 이미지 최적화 설정
  images: {
    unoptimized: true,
  },

  // SWC 최소화 (더 빠른 빌드)
  swcMinify: true,
};

module.exports = nextConfig;
