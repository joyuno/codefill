import { Header } from '@/components/layout/Header';
import { TopNav } from '@/components/layout/TopNav';
import { SidebarProfile } from '@/components/dashboard/SidebarProfile';
import { ProblemFilters } from '@/components/problems/ProblemFilters';
import { ProblemCard } from '@/components/problems/ProblemCard';
import { mockProblems } from '@/lib/mockData';

const Problems = () => {
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
            <div><h1 className="text-2xl font-bold">Problems</h1><p className="text-muted-foreground">Find real-world coding challenges</p></div>
            <ProblemFilters />
            <div className="space-y-4">{mockProblems.map((problem, i) => (<ProblemCard key={problem.id} problem={problem} index={i} />))}</div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default Problems;
