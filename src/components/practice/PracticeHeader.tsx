'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';
import { Play, Send, ArrowLeft } from 'lucide-react';

interface PracticeHeaderProps {
  title: string;
  blanksFileld: number;
  totalBlanks: number;
}

export function PracticeHeader({ title, blanksFileld, totalBlanks }: PracticeHeaderProps) {
  const { toast } = useToast();
  const progress = (blanksFileld / totalBlanks) * 100;

  const handlePrototype = () => {
    toast({
      title: 'Prototype Only',
      description: 'This functionality is not available in the prototype.',
    });
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className="border-b border-border bg-card px-6 py-4"
    >
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <Link href="/problems">
            <Button variant="ghost" size="icon">
              <ArrowLeft className="h-4 w-4" />
            </Button>
          </Link>
          <div>
            <h1 className="text-lg font-semibold">{title}</h1>
            <p className="text-sm text-muted-foreground">
              {blanksFileld}/{totalBlanks} blanks filled
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="w-32">
            <Progress value={progress} className="h-2" />
          </div>
          <Button variant="outline" size="sm" onClick={handlePrototype}>
            <Play className="mr-1.5 h-3.5 w-3.5" />
            Run
          </Button>
          <Button size="sm" onClick={handlePrototype}>
            <Send className="mr-1.5 h-3.5 w-3.5" />
            Submit
          </Button>
        </div>
      </div>
    </motion.div>
  );
}
