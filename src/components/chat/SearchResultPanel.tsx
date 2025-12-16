import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { mockCodePreview } from '@/lib/mockData';
import { Play, Search, CheckCircle } from 'lucide-react';

export function SearchResultPanel() {
  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      className="flex h-full flex-col rounded-xl border border-border bg-card"
    >
      {/* Status indicator */}
      <div className="flex items-center gap-2 border-b border-border px-4 py-3">
        <div className="flex items-center gap-2 rounded-full bg-primary/10 px-3 py-1 text-sm">
          <CheckCircle className="h-4 w-4 text-primary" />
          <span className="font-medium text-primary">Problem Found</span>
        </div>
        <Badge variant="secondary" className="ml-auto">
          <Search className="mr-1 h-3 w-3" />
          RAG Match
        </Badge>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-4">
        <h3 className="mb-2 text-lg font-semibold">{mockCodePreview.title}</h3>
        <p className="mb-4 text-sm text-muted-foreground">{mockCodePreview.description}</p>

        {/* Code preview */}
        <div className="rounded-lg bg-code-bg p-4">
          <pre className="overflow-x-auto text-xs leading-relaxed">
            <code className="font-mono text-foreground">
              {mockCodePreview.code.split('\n').map((line, i) => (
                <div key={i} className="flex">
                  <span className="mr-4 w-6 select-none text-right text-code-comment">
                    {i + 1}
                  </span>
                  <span>
                    {line.includes('_____') ? (
                      <>
                        {line.split('_____').map((part, j, arr) => (
                          <span key={j}>
                            {part}
                            {j < arr.length - 1 && (
                              <span className="mx-1 rounded bg-primary/20 px-2 py-0.5 text-primary">
                                ___
                              </span>
                            )}
                          </span>
                        ))}
                      </>
                    ) : (
                      line
                    )}
                  </span>
                </div>
              ))}
            </code>
          </pre>
        </div>
      </div>

      {/* Action */}
      <div className="border-t border-border p-4">
        <Link to="/practice">
          <Button className="w-full" size="lg">
            <Play className="mr-2 h-4 w-4" />
            Start Practice
          </Button>
        </Link>
      </div>
    </motion.div>
  );
}
