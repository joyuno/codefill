import { motion } from 'framer-motion';
import { Badge } from '@/components/ui/badge';
import { Problem } from '@/lib/types';
import { ExternalLink, BookOpen, Lightbulb } from 'lucide-react';
import { cn } from '@/lib/utils';

interface PracticeDescriptionProps {
  problem: Problem;
}

const difficultyColors = {
  easy: 'bg-primary/20 text-primary border-primary/30',
  medium: 'bg-warning/20 text-warning border-warning/30',
  hard: 'bg-destructive/20 text-destructive border-destructive/30',
};

export function PracticeDescription({ problem }: PracticeDescriptionProps) {
  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      className="space-y-6 overflow-auto p-6"
    >
      {/* Description */}
      <div>
        <h2 className="mb-3 flex items-center gap-2 text-lg font-semibold">
          <BookOpen className="h-5 w-5 text-primary" />
          Description
        </h2>
        <p className="leading-relaxed text-muted-foreground">{problem.description}</p>
      </div>

      {/* Tags & Difficulty */}
      <div className="flex flex-wrap gap-2">
        <Badge
          variant="outline"
          className={cn('capitalize', difficultyColors[problem.difficulty])}
        >
          {problem.difficulty}
        </Badge>
        {problem.topics.map((topic) => (
          <Badge key={topic} variant="secondary">
            {topic}
          </Badge>
        ))}
      </div>

      {/* Key Concepts */}
      <div>
        <h3 className="mb-3 flex items-center gap-2 font-semibold">
          <Lightbulb className="h-4 w-4 text-warning" />
          Key Concepts
        </h3>
        <ul className="space-y-2">
          {problem.keyConcepts.map((concept, i) => (
            <motion.li
              key={concept}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.1 }}
              className="flex items-center gap-2 text-sm"
            >
              <span className="h-1.5 w-1.5 rounded-full bg-primary" />
              <code className="rounded bg-secondary px-2 py-0.5 font-mono text-xs">
                {concept}
              </code>
            </motion.li>
          ))}
        </ul>
      </div>

      {/* Related Docs */}
      <div>
        <h3 className="mb-3 font-semibold">Related Documentation</h3>
        <div className="space-y-2">
          {problem.relatedDocs.map((doc) => (
            <a
              key={doc.url}
              href={doc.url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 text-sm text-primary transition-colors hover:underline"
            >
              <ExternalLink className="h-3.5 w-3.5" />
              {doc.title}
            </a>
          ))}
        </div>
      </div>
    </motion.div>
  );
}
