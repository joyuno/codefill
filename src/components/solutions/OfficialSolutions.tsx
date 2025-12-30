'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Check, Copy, ChevronDown, ChevronUp } from 'lucide-react';
import type { OfficialSolution } from '@/lib/api';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { getLanguageLabel, getLanguageColor } from './constants';

interface OfficialSolutionsProps {
  solutions: OfficialSolution[];
}

export function OfficialSolutions({ solutions }: OfficialSolutionsProps) {
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);

  if (solutions.length === 0) {
    return (
      <div className="text-center py-12 text-muted-foreground">
        <p>공식 풀이가 없습니다.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {solutions.map((solution, index) => (
        <OfficialSolutionCard
          key={index}
          solution={solution}
          index={index}
          expanded={expandedIndex === index}
          onToggle={() => setExpandedIndex(expandedIndex === index ? null : index)}
        />
      ))}
    </div>
  );
}

interface OfficialSolutionCardProps {
  solution: OfficialSolution;
  index: number;
  expanded: boolean;
  onToggle: () => void;
}

function OfficialSolutionCard({ solution, index, expanded, onToggle }: OfficialSolutionCardProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(solution.code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const languageForHighlighter = solution.language === 'cpp' ? 'cpp' : solution.language;

  return (
    <div className="border border-border rounded-lg overflow-hidden bg-card">
      {/* Header */}
      <button
        onClick={onToggle}
        className="w-full flex items-center justify-between px-4 py-3 hover:bg-muted/50 transition-colors"
      >
        <div className="flex items-center gap-3">
          <Badge
            variant="outline"
            className={`text-xs py-0 ${getLanguageColor(solution.language)}`}
          >
            {getLanguageLabel(solution.language)}
          </Badge>
          <span className="text-sm text-muted-foreground">
            공식 풀이 #{index + 1}
          </span>
        </div>
        {expanded ? (
          <ChevronUp className="h-4 w-4 text-muted-foreground" />
        ) : (
          <ChevronDown className="h-4 w-4 text-muted-foreground" />
        )}
      </button>

      {/* Code */}
      {expanded && (
        <div className="border-t border-border">
          <div className="flex justify-end p-2 bg-muted/30">
            <Button
              variant="ghost"
              size="sm"
              className="h-7 px-2 gap-1"
              onClick={handleCopy}
            >
              {copied ? (
                <>
                  <Check className="h-3.5 w-3.5" />
                  Copied
                </>
              ) : (
                <>
                  <Copy className="h-3.5 w-3.5" />
                  Copy
                </>
              )}
            </Button>
          </div>
          <SyntaxHighlighter
            language={languageForHighlighter}
            style={oneDark}
            customStyle={{
              margin: 0,
              borderRadius: 0,
              fontSize: '0.875rem',
            }}
          >
            {solution.code}
          </SyntaxHighlighter>
        </div>
      )}
    </div>
  );
}
