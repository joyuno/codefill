import { motion } from 'framer-motion';
import { Problem } from '@/lib/types';
import { HintPopover } from './HintPopover';

interface EditorMockProps {
  problem: Problem;
}

export function EditorMock({ problem }: EditorMockProps) {
  const lines = problem.codeSnippet.split('\n');
  let blankIndex = 0;

  const renderLine = (line: string, lineNumber: number) => {
    // Check for blanks (simplified detection)
    const parts: React.ReactNode[] = [];
    let lastIndex = 0;
    
    // Look for patterns that should be blanks based on the problem's blanks
    problem.blanks.forEach((blank) => {
      const answer = blank.answer;
      const idx = line.indexOf(answer);
      if (idx !== -1 && blankIndex < problem.blanks.length) {
        const currentBlankIndex = blankIndex;
        blankIndex++;
        
        parts.push(
          <span key={`text-${lastIndex}`} className="text-foreground">
            {line.substring(lastIndex, idx)}
          </span>,
          <span key={`blank-${currentBlankIndex}`} className="inline-flex items-center gap-1">
            <span className="rounded bg-primary/20 px-3 py-0.5 font-mono text-primary">
              ___________
            </span>
            <HintPopover hints={blank.hints} blankNumber={currentBlankIndex + 1} />
          </span>
        );
        lastIndex = idx + answer.length;
      }
    });

    if (parts.length === 0) {
      return <span className="text-foreground">{line}</span>;
    }

    parts.push(
      <span key={`end-${lineNumber}`} className="text-foreground">
        {line.substring(lastIndex)}
      </span>
    );

    return <>{parts}</>;
  };

  // Reset blank index for rendering
  blankIndex = 0;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="h-full overflow-auto rounded-lg bg-code-bg"
    >
      {/* Editor header */}
      <div className="sticky top-0 flex items-center gap-2 border-b border-border bg-code-bg px-4 py-2">
        <div className="flex gap-1.5">
          <div className="h-3 w-3 rounded-full bg-destructive/80" />
          <div className="h-3 w-3 rounded-full bg-warning/80" />
          <div className="h-3 w-3 rounded-full bg-primary/80" />
        </div>
        <span className="ml-2 text-xs text-muted-foreground">solution.tsx</span>
      </div>

      {/* Code content */}
      <div className="p-4">
        <pre className="text-sm leading-relaxed">
          <code>
            {lines.map((line, i) => {
              const currentBlankIndex = blankIndex;
              return (
                <div
                  key={i}
                  className="flex hover:bg-code-line/50"
                >
                  <span className="mr-4 w-8 select-none text-right font-mono text-code-comment">
                    {i + 1}
                  </span>
                  <span className="flex-1 font-mono">
                    {renderLine(line, i)}
                  </span>
                </div>
              );
            })}
          </code>
        </pre>
      </div>

      {/* Instruction */}
      <div className="sticky bottom-0 border-t border-border bg-code-bg px-4 py-2">
        <p className="text-xs text-muted-foreground">
          💡 Click the hint icon next to each blank for help. Type <code className="rounded bg-secondary px-1">hint</code> + Enter for quick hints.
        </p>
      </div>
    </motion.div>
  );
}
