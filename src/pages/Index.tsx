import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { Header } from '@/components/layout/Header';
import { TopNav } from '@/components/layout/TopNav';
import { SidebarProfile } from '@/components/dashboard/SidebarProfile';
import { StatCards } from '@/components/dashboard/StatCards';
import { GrassHeatmap } from '@/components/dashboard/GrassHeatmap';
import { Button } from '@/components/ui/button';
import { Play, Sparkles } from 'lucide-react';

const Index = () => {
  return (
    <div className="min-h-screen bg-background">
      <Header />
      <TopNav />
      <div className="flex">
        <aside className="hidden w-72 shrink-0 border-r border-border lg:block">
          <SidebarProfile />
        </aside>
        <main className="flex-1 p-6">
          <div className="mx-auto max-w-4xl space-y-6">
            <StatCards />
            <GrassHeatmap />
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} className="rounded-xl border border-primary/30 bg-gradient-to-r from-primary/10 to-transparent p-6">
              <div className="flex flex-col items-center gap-4 sm:flex-row sm:justify-between">
                <div><h3 className="text-xl font-semibold">Ready to level up?</h3><p className="text-muted-foreground">Start practicing and earn XP</p></div>
                <Link to="/chat"><Button size="lg" className="gap-2"><Play className="h-4 w-4" />Start Practicing<Sparkles className="h-4 w-4" /></Button></Link>
              </div>
            </motion.div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default Index;
