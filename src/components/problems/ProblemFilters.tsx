import { useState } from 'react';
import { motion } from 'framer-motion';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Search } from 'lucide-react';

export function ProblemFilters() {
  const [framework, setFramework] = useState<string>('');
  const [difficulty, setDifficulty] = useState<string>('');
  const [search, setSearch] = useState('');

  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex flex-wrap gap-3 rounded-xl border border-border bg-card p-4"
    >
      <Select value={framework} onValueChange={setFramework}>
        <SelectTrigger className="w-[160px] bg-secondary">
          <SelectValue placeholder="Framework" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All Frameworks</SelectItem>
          <SelectItem value="react">React</SelectItem>
          <SelectItem value="vue">Vue</SelectItem>
          <SelectItem value="angular">Angular</SelectItem>
          <SelectItem value="svelte">Svelte</SelectItem>
        </SelectContent>
      </Select>

      <Select value={difficulty} onValueChange={setDifficulty}>
        <SelectTrigger className="w-[140px] bg-secondary">
          <SelectValue placeholder="Difficulty" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All Levels</SelectItem>
          <SelectItem value="easy">Easy</SelectItem>
          <SelectItem value="medium">Medium</SelectItem>
          <SelectItem value="hard">Hard</SelectItem>
        </SelectContent>
      </Select>

      <div className="relative flex-1 min-w-[200px]">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search topics..."
          className="bg-secondary pl-10"
        />
      </div>
    </motion.div>
  );
}
