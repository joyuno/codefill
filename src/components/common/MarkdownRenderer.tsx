'use client';

import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import remarkBreaks from 'remark-breaks';
import rehypeKatex from 'rehype-katex';
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
 * - 이미지: 외부 도메인 지원을 위해 일반 img 태그 사용
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
        [&_img]:max-w-full [&_img]:h-auto [&_img]:my-4 [&_img]:rounded-md
        ${className}`}
    >
      <ReactMarkdown
        remarkPlugins={[remarkGfm, remarkMath, remarkBreaks]}
        rehypePlugins={[rehypeKatex]}
        components={{
          // 외부 도메인 이미지 지원을 위해 일반 img 태그 사용
          img: ({ src, alt }) => (
            <span className="inline-block my-4 p-2 bg-white rounded-md">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={src}
                alt={alt || ''}
                loading="lazy"
                className="max-w-full h-auto rounded"
              />
            </span>
          ),
        }}
      >
        {preprocessLatex(content)}
      </ReactMarkdown>
    </div>
  );
}

export default MarkdownRenderer;
