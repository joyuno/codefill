import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Problem } from '@/lib/types';
import { Clock, Users, Eye, Play } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { cn } from '@/lib/utils';

interface ProblemCardProps {
  problem: Problem;
  index: number;
}

const difficultyColors = {
  easy: 'bg-primary/20 text-primary border-primary/30',
  medium: 'bg-warning/20 text-warning border-warning/30',
  hard: 'bg-destructive/20 text-destructive border-destructive/30',
};

const frameworkIcons: Record<string, string> = {
  react: '⚛️',
  vue: '💚',
  angular: '🅰️',
  svelte: '🔥',
  vanilla: '📦',
};

export function ProblemCard({ problem, index }: ProblemCardProps) {
  const { toast } = useToast();

  const handlePreview = () => {
    toast({
      title: 'Prototype Only',
      description: 'Preview functionality is not available in this prototype.',
    });
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
      whileHover={{ scale: 1.01 }}
      className="rounded-xl border border-border bg-card p-5 transition-colors hover:border-primary/50"
    >
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex-1 space-y-2">
          <div className="flex items-center gap-2">
            <span className="text-lg">{frameworkIcons[problem.framework]}</span>
            <h3 className="font-semibold">{problem.title}</h3>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <Badge
              variant="outline"
              className={cn('capitalize', difficultyColors[problem.difficulty])}
            >
              {problem.difficulty}
            </Badge>
            {problem.topics.slice(0, 3).map((topic) => (
              <Badge key={topic} variant="secondary" className="text-xs">
                {topic}
              </Badge>
            ))}
          </div>

          <div className="flex items-center gap-4 text-sm text-muted-foreground">
            <span className="flex items-center gap-1">
              <Clock className="h-3.5 w-3.5" />
              {problem.estimatedTime} min
            </span>
            <span className="flex items-center gap-1">
              <Users className="h-3.5 w-3.5" />
              {problem.solvedCount.toLocaleString()} solved
            </span>
          </div>
        </div>

        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={handlePreview}>
            <Eye className="mr-1.5 h-3.5 w-3.5" />
            Preview
          </Button>
          <Link to={`/practice?id=${problem.id}`}>
            <Button size="sm">
              <Play className="mr-1.5 h-3.5 w-3.5" />
              Start
            </Button>
          </Link>
        </div>
      </div>
    </motion.div>
  );
}
