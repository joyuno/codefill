'use client';

import dynamic from 'next/dynamic';
import { Skeleton } from './skeleton';

// SyntaxHighlighter를 동적으로 로드 (번들 분리)
const SyntaxHighlighter = dynamic(
  () => import('react-syntax-highlighter').then((mod) => mod.Prism),
  {
    loading: () => <Skeleton className="h-48 w-full" />,
    ssr: false,
  }
);

// 스타일도 동적으로 로드
const getOneDarkStyle = async () => {
  const { oneDark } = await import('react-syntax-highlighter/dist/esm/styles/prism');
  return oneDark;
};

import { useEffect, useState } from 'react';

interface CodeBlockProps {
  code: string;
  language: string;
  showLineNumbers?: boolean;
  className?: string;
}

export function CodeBlock({ code, language, showLineNumbers = true, className }: CodeBlockProps) {
  const [style, setStyle] = useState<Record<string, React.CSSProperties> | null>(null);

  useEffect(() => {
    getOneDarkStyle().then(setStyle);
  }, []);

  if (!style) {
    return <Skeleton className="h-48 w-full" />;
  }

  const languageForHighlighter = language === 'cpp' ? 'cpp' : language;

  return (
    <SyntaxHighlighter
      language={languageForHighlighter}
      style={style}
      customStyle={{
        margin: 0,
        borderRadius: 0,
        fontSize: '0.875rem',
        ...(className ? {} : {}),
      }}
      showLineNumbers={showLineNumbers}
    >
      {code}
    </SyntaxHighlighter>
  );
}
