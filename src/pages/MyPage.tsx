import { Header } from '@/components/layout/Header';
import { TopNav } from '@/components/layout/TopNav';
import { mockUser, mockBadges, mockRecentActivity } from '@/lib/mockData';
import { Badge } from '@/components/ui/badge';
import { Trophy, Award, Flame, Calendar } from 'lucide-react';

const MyPage = () => {
  return (
    <div className="min-h-screen bg-background">
      <Header />
      <TopNav />
      <main className="mx-auto max-w-4xl p-6 space-y-6">
        <div className="rounded-xl border border-border bg-card p-6 flex items-center gap-6">
          <div className="flex h-20 w-20 items-center justify-center rounded-full bg-primary text-3xl font-bold text-primary-foreground">{mockUser.username.slice(0, 2).toUpperCase()}</div>
          <div><h1 className="text-2xl font-bold">{mockUser.username}</h1><p className="text-muted-foreground">Level {mockUser.level} • {mockUser.currentXP.toLocaleString()} XP</p><Badge variant="secondary" className="mt-2 capitalize">{mockUser.subscription} Plan</Badge></div>
        </div>
        <div className="grid gap-4 sm:grid-cols-3">
          <div className="rounded-xl border border-border bg-card p-4 flex items-center gap-3"><Trophy className="h-8 w-8 text-primary" /><div><p className="text-2xl font-bold">{mockUser.solvedCount}</p><p className="text-sm text-muted-foreground">Solved</p></div></div>
          <div className="rounded-xl border border-border bg-card p-4 flex items-center gap-3"><Award className="h-8 w-8 text-warning" /><div><p className="text-2xl font-bold">{mockBadges.length}</p><p className="text-sm text-muted-foreground">Badges</p></div></div>
          <div className="rounded-xl border border-border bg-card p-4 flex items-center gap-3"><Flame className="h-8 w-8 text-destructive" /><div><p className="text-2xl font-bold">{mockUser.streak}</p><p className="text-sm text-muted-foreground">Day Streak</p></div></div>
        </div>
        <div className="rounded-xl border border-border bg-card p-6"><h2 className="mb-4 font-semibold">Recent Activity</h2><div className="space-y-3">{mockRecentActivity.map((a) => (<div key={a.id} className="flex items-center justify-between border-b border-border pb-3 last:border-0"><div><p className="font-medium">{a.title}</p><p className="text-sm text-muted-foreground">{a.description}</p></div>{a.xpGained && <Badge variant="secondary">+{a.xpGained} XP</Badge>}</div>))}</div></div>
      </main>
    </div>
  );
};

export default MyPage;
