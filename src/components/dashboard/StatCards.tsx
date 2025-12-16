import { motion } from 'framer-motion';
import { Trophy, Award, Flame } from 'lucide-react';
import { mockUser } from '@/lib/mockData';

const stats = [
  { label: 'Problems Solved', value: mockUser.solvedCount, icon: Trophy, color: 'text-primary' },
  { label: 'Badges Earned', value: 12, icon: Award, color: 'text-warning' },
  { label: 'Day Streak', value: mockUser.streak, icon: Flame, color: 'text-destructive' },
];

export function StatCards() {
  return (
    <div className="grid gap-4 sm:grid-cols-3">
      {stats.map((stat, index) => {
        const Icon = stat.icon;
        return (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            whileHover={{ scale: 1.02 }}
            className="rounded-xl border border-border bg-card p-5"
          >
            <div className="flex items-center gap-3">
              <div className={`rounded-lg bg-secondary p-2.5 ${stat.color}`}>
                <Icon className="h-5 w-5" />
              </div>
              <div>
                <p className="text-2xl font-bold">{stat.value}</p>
                <p className="text-sm text-muted-foreground">{stat.label}</p>
              </div>
            </div>
          </motion.div>
        );
      })}
    </div>
  );
}
