'use client';

import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import remarkBreaks from 'remark-breaks';
import rehypeKatex from 'rehype-katex';
import Image from 'next/image';
import { useState } from 'react';
import { preprocessLatex } from '@/lib/utils';
import 'katex/dist/katex.min.css';

interface MarkdownRendererProps {
  content: string;
  className?: string;
}

/**
 * 마크다운 + KaTeX + 이미지 렌더링 컴포넌트
 *
 * - LaTeX 수식: $...$ 또는 $$...$$ 형식 지원 (KaTeX)
 * - 이미지: Next.js Image 최적화 적용
 * - GFM: 테이블, 체크리스트 등 지원
 */
export function MarkdownRenderer({ content, className = '' }: MarkdownRendererProps) {
  return (
    <div
      className={`prose prose-sm dark:prose-invert max-w-none
        [&_pre]:bg-background/50 [&_pre]:p-3 [&_pre]:rounded-md
        [&_code]:text-primary [&_code]:bg-background/50 [&_code]:px-1 [&_code]:py-0.5 [&_code]:rounded
        [&_p]:text-[13px] [&_li]:text-[13px]
        [&_h1]:text-base [&_h2]:text-sm [&_h3]:text-sm
        [&_table]:text-[12px] [&_th]:p-2 [&_td]:p-2
        ${className}`}
    >
      <ReactMarkdown
        remarkPlugins={[remarkGfm, remarkMath, remarkBreaks]}
        rehypePlugins={[rehypeKatex]}
        components={{
          img: MarkdownImage,
        }}
      >
        {preprocessLatex(content)}
      </ReactMarkdown>
    </div>
  );
}

/**
 * 마크다운 이미지를 Next.js Image로 렌더링
 */
function MarkdownImage({
  src,
  alt,
  ...props
}: React.ImgHTMLAttributes<HTMLImageElement>) {
  const [error, setError] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  if (!src) return null;

  // 에러 발생 시 일반 img 태그로 폴백
  if (error) {
    return (
      <img
        src={src}
        alt={alt || '이미지'}
        className="max-w-full h-auto rounded-md my-4"
        loading="lazy"
        {...props}
      />
    );
  }

  // data URI는 next/image에서 지원하지 않음
  if (src.startsWith('data:')) {
    return (
      <img
        src={src}
        alt={alt || '이미지'}
        className="max-w-full h-auto rounded-md my-4"
        {...props}
      />
    );
  }

  return (
    <span className="block relative my-4">
      {isLoading && (
        <span className="absolute inset-0 bg-muted/50 animate-pulse rounded-md" />
      )}
      <Image
        src={src}
        alt={alt || '이미지'}
        width={800}
        height={600}
        className="max-w-full h-auto rounded-md"
        style={{ width: 'auto', height: 'auto', maxWidth: '100%' }}
        onError={() => setError(true)}
        onLoad={() => setIsLoading(false)}
        unoptimized // 외부 이미지는 최적화 비활성화 (크기 다양)
      />
    </span>
  );
}

export default MarkdownRenderer;
