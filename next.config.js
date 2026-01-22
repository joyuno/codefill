/** @type {import('next').NextConfig} */
const nextConfig = {
  // 정적 HTML 내보내기 - 동적 라우트 때문에 비활성화
  // S3 정적 배포 대신 EC2에서 Next.js 서버로 실행
  // output: 'export',

  // S3 호환을 위한 trailing slash
  trailingSlash: true,

  reactStrictMode: true,

  // Docker 배포를 위한 standalone 모드
  output: 'standalone',

  // 이미지 최적화 설정
  images: {
    unoptimized: true,  // 정적 export 시 필수
  },

  // SWC 최소화 (더 빠른 빌드)
  swcMinify: true,
};

module.exports = nextConfig;
